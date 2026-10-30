#!/usr/bin/env python3
"""One annotated HaluMem update case; observe unmodified Mem0, never inject labels.

All execution: conda run --no-capture-output -n mem0_halumem python ...
Preparation is offline. --execute is one-shot and refuses repeat ingestion.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
import fcntl
import functools
import importlib.metadata as md
import inspect
import json
import logging
import os
from pathlib import Path
import platform
import shutil
import sqlite3
import sys
import threading
import time
import traceback
import uuid
from zoneinfo import ZoneInfo

import local_smoke as base

ROOT = base.ROOT
TZ = ZoneInfo('Asia/Shanghai')
SOURCE = ROOT / 'results/local_smoke/20261022T203207+0800_a40c12d5'


def now():
    return datetime.now(TZ).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def true_flag(value):
    return value is True or isinstance(value, str) and value.strip().lower() == 'true'


def ordered(user):
    return sorted(enumerate(user['sessions']), key=lambda x: datetime.strptime(x[1]['start_time'], base.DATE_FORMAT))


def session_input(user, line, ordinal, original, session):
    d = session['dialogue']
    times = [datetime.strptime(m['timestamp'], base.DATE_FORMAT) for m in d]
    assert times and times == sorted(times)
    assert len(d) == 2 * session['dialogue_turn_num']
    assert times[0] == datetime.strptime(session['start_time'], base.DATE_FORMAT)
    assert times[-1] == datetime.strptime(session['end_time'], base.DATE_FORMAT)
    assert all(m['role'] in ('user', 'assistant') and isinstance(m['content'], str) for m in d)
    return {'user_uuid': user['uuid'], 'dataset_line_one_based': line,
            'chronological_session_ordinal_one_based': ordinal,
            'original_session_index_zero_based': original,
            'source_json_pointer': f'/sessions/{original}/dialogue',
            'start_time': session['start_time'], 'end_time': session['end_time'],
            'dialogue_turn_num': session['dialogue_turn_num'], 'raw_dialogue': d,
            'messages': [{'role': m['role'], 'content': m['content']} for m in d]}


def manifest(path):
    return {str(p.relative_to(path)): base.sha256(p) for p in sorted(path.rglob('*')) if p.is_file()}


def native_source():
    return {p: base.sha256(ROOT / 'mem0_v0.1.118' / p) for p in read(SOURCE / 'environment.json')['source_sha256']}


def validate_prefix(out, user, line, dataset_hash):
    """Verify copies, leaving every original artifact byte-identical."""
    evidence = out / 'linked_original'
    # Qdrant uses flock; hold the original lock while taking a filesystem copy.
    with (SOURCE / 'qdrant/.lock').open('rb') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        shutil.copytree(SOURCE, evidence)
    summary = read(evidence / 'summary.json')
    assert summary['status'] == 'completed' and summary['completed_sessions'] == 2
    assert summary['user_uuid'] == user['uuid'] == base.EXPECTED_USER
    assert read(evidence / 'data_check.json')['sha256'] == dataset_hash
    assert native_source() == read(evidence / 'environment.json')['source_sha256']
    assert all(e.get('resolved') for e in read(evidence / 'errors.json'))
    selected = read(evidence / 'selected_input.json')
    assert selected['dataset_line_one_based'] == line and selected['user_uuid'] == user['uuid']
    from mem0.memory.utils import get_fact_retrieval_messages, parse_messages
    from qdrant_client import QdrantClient
    calls = [json.loads(x) for x in (evidence / 'api_calls.jsonl').read_text().splitlines()]
    all_ops, origins, previous = [], [], None
    for ordinal, (index, s) in enumerate(ordered(user)[:2], 1):
        expected = session_input(user, line, ordinal, index, s)
        old = selected['sessions'][ordinal - 1]
        assert all(old[k] == expected[k] for k in old)
        folder = evidence / f'session_{ordinal:02d}'
        assert read(folder / 'input.json') == old
        before, after = read(folder / 'before.json'), read(folder / 'after.json')
        assert before['not_truncated'] and after['not_truncated']
        if previous is None:
            assert before['database_count_exact'] == 0
        else:
            base.verify_persistence(previous['database_points_with_vectors'], before['database_points_with_vectors'])
        ops = read(folder / 'actual_operations.json')
        returned = read(folder / 'add_return.json')
        assert returned['error'] is None
        base.reconcile(before, after, ops, returned['return_value'])
        assert len(ops) == (17 if ordinal == 1 else 12) and all(r['event'] == 'ADD' for r in ops)
        llm = [c for c in calls if c['phase'] == f'session_{ordinal:02d}' and c['kind'] == 'llm']
        assert len(llm) == 2 and all(c['status'] == 'ok' and c['response']['choices'][0]['finish_reason'] == 'stop' for c in llm)
        system, prompt = get_fact_retrieval_messages(parse_messages(expected['messages']))
        assert llm[0]['request']['messages'] == [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]
        assert read(folder / 'verification.json')['native_error_count'] == 0
        for row in ops:
            origins.append({'memory_id': row['memory_id'], 'memory': row['new_memory'],
                            'source_session_ordinal': ordinal, 'source_original_session_index': index,
                            'history_sequence': row['sequence'],
                            'evidence': f'linked_original/session_{ordinal:02d}/actual_operations.json'})
        all_ops.extend(ops)
        previous = after
    assert all_ops == base.history_rows(evidence / 'history.db') == read(evidence / 'all_actual_operations.json')
    final = read(evidence / 'final_snapshot.json')
    base.verify_persistence(previous['database_points_with_vectors'], final['database_points_with_vectors'])
    client = QdrantClient(path=str(evidence / 'qdrant'))
    try:
        points, count, _ = base.collect_points(client, 'local_smoke', None)
        disk = base.verify_persistence(final['database_points_with_vectors'], points)
        assert count == 29 == summary['final_memory_count']
    finally:
        client.close()
    with sqlite3.connect(f'file:{evidence / "history.db"}?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    base.write_json(out / 'prefix_memory_origins.json', origins)
    shutil.copytree(evidence / 'qdrant', out / 'qdrant')
    shutil.copy2(evidence / 'history.db', out / 'history.db')
    return {'verified': True, 'completed_sessions': 2, 'memory_count': 29,
            'session_message_counts': [12, 8], 'session_add_counts': [17, 12],
            'input_matches_dataset_and_extraction_requests': True,
            'snapshot_chain_history_returns_and_persistent_db_match': True,
            'persistence_comparison': disk, 'history_integrity_check': 'ok'}


def prepare():
    run_id = datetime.now(TZ).strftime('%Y%m%dT%H%M%S%z') + '_' + uuid.uuid4().hex[:8]
    out = ROOT / 'results/local_update_case' / run_id
    out.mkdir(parents=True)
    out.chmod(0o700)
    os.environ['MEM0_DIR'] = str(out / 'mem0_runtime')
    os.environ['MEM0_TELEMETRY'] = 'False'
    original_manifest = manifest(SOURCE)
    base.write_json(out / 'original_manifest.before.json', original_manifest)
    data, first = base.inspect_data(ROOT / 'HaluMem/data/HaluMem-Medium.jsonl')
    base.write_json(out / 'data_check.json', data)
    users = [(n, json.loads(s)) for n, s in enumerate((ROOT / 'HaluMem/data/HaluMem-Medium.jsonl').open(), 1)]
    preferred = next((pair for pair in users if pair[1]['uuid'] == base.EXPECTED_USER), None)
    assert preferred is not None
    line, user = preferred
    audit_selection = []
    target = None
    for candidate_line, candidate in [preferred] + [p for p in users if p != preferred]:
        start = 2 if candidate['uuid'] == base.EXPECTED_USER else 0
        for ordinal, (index, s) in enumerate(ordered(candidate), 1):
            if ordinal <= start:
                continue
            for point_index, point in enumerate(s['memory_points']):
                qualifies = true_flag(point.get('is_update')) and bool(point.get('original_memories'))
                audit_selection.append({'dataset_line_one_based': candidate_line, 'user_uuid': candidate['uuid'],
                    'session_ordinal': ordinal, 'original_session_index': index, 'memory_point_index': point_index,
                    'is_update_raw': point.get('is_update'), 'original_memories_nonempty': bool(point.get('original_memories')),
                    'qualifies': qualifies})
                if qualifies:
                    line, user = candidate_line, candidate
                    target = {'user_uuid': user['uuid'], 'dataset_line_one_based': line,
                        'chronological_session_ordinal_one_based': ordinal, 'original_session_index_zero_based': index,
                        'memory_point_index_zero_based': point_index, 'annotation': point,
                        'old_propositions': point['original_memories'], 'new_proposition': point['memory_content'],
                        'source_json_pointer': f'/sessions/{index}/memory_points/{point_index}',
                        'session_start': s['start_time'], 'session_end': s['end_time']}
                    break
            if target:
                break
        if target:
            break
    assert target is not None, 'No eligible update target in fixed dataset order'
    base.write_json(out / 'selection_scan.json', audit_selection)
    base.write_json(out / 'target.json', target)
    try:
        assert user['uuid'] == base.EXPECTED_USER, 'Selected another user: build from first session'
        prefix = validate_prefix(out, user, line, data['sha256'])
    except Exception:
        prefix = {'verified': False, 'verification_exception': traceback.format_exc(),
                  'fallback': 'Build all full sessions from first in fresh independent database'}
        for path in (out / 'qdrant', out / 'history.db'):
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
    base.write_json(out / 'prefix_verification.json', prefix)
    start = 3 if prefix['verified'] else 1
    sessions = [session_input(user, line, ordinal, index, s)
                for ordinal, (index, s) in enumerate(ordered(user), 1)
                if start <= ordinal <= target['chronological_session_ordinal_one_based']]
    base.write_json(out / 'selected_input.json', {'user_uuid': user['uuid'], 'sessions': sessions})
    # Persist entire raw prefix as provenance, but labels/questions never enter add().
    base.write_json(out / 'raw_history_prefix.json', {'user_uuid': user['uuid'], 'dataset_line_one_based': line,
        'sessions': [session_input(user, line, ordinal, index, s) for ordinal, (index, s) in enumerate(ordered(user), 1)
                     if ordinal <= target['chronological_session_ordinal_one_based']]})
    base.write_json(out / 'source_integrity.json', {'native_source_sha256': native_source(),
                    'original_run_unchanged': manifest(SOURCE) == original_manifest})
    shutil.copy2(Path(__file__), out / 'local_update_case.py')
    shutil.copy2(Path(base.__file__), out / 'local_smoke.py')
    (out / 'PLAN.md').write_text('''# 单个更新目标诊断计划

Goal: 在原生 Mem0 0.1.118 中完成一个静态选中的更新标注所在完整会话。
Spec: 本轮用户请求；原运行 REPORT.md 保存在 linked_original 中。
Architecture: 离线核验历史后复制数据库续接；失败则新库重建完整历史前缀。包装调用只观察，原响应与异常原样返回。
Constraints: conda mem0_halumem；qwen-plus / text-embedding-v4；不将标注、persona、答案传给系统；不强制 UPDATE；只运行至一个目标会话结束。

- [x] 静态按固定用户、时间、标注顺序查找目标；兼容布尔值与字符串。
- [ ] 核验前两完整会话、API 输入、29 条记忆、历史及磁盘；选择复制续接或新库重建。
- [ ] 记录完整输入/时间、提取事实、top-5 候选 ID/score、更新模型输入输出、含 NONE 的计划、调用执行结果与异常。
- [ ] 每会话全量快照、历史重放；最终重新打开数据库与 SQLite integrity_check。
- [ ] 按目标新旧命题生成原文、ID、日志位置对照；证据不足标未知。

Review focus: 字符串 False 不应判真；历史输入不应重复；Qdrant 浮点容差；NONE 不在 add 返回中；标注不得污染输入。
Decision: 这是用户已授权的诊断运行，直接执行，不变更两个源码仓库或提交代码。原目录非 Git 仓库，使用独立结果目录隔离。
''')
    print(json.dumps({'run_directory': str(out), 'target': target, 'prefix': prefix,
                      'session_ordinals_to_ingest': [s['chronological_session_ordinal_one_based'] for s in sessions]}, ensure_ascii=False, indent=2))
    return out


class Observer:
    def __init__(self, out):
        self.out, self.phase, self.lock = out, 'setup', threading.Lock()
        self.entries = []

    def emit(self, kind, **data):
        with self.lock:
            entry = base.clean({'sequence': len(self.entries) + 1, 'time': now(), 'phase': self.phase, 'kind': kind, **data})
            self.entries.append(entry)
            with (self.out / 'observations.jsonl').open('a') as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + '\n')
            return entry

    def install(self, memory):
        original_generate = memory.llm.generate_response

        @functools.wraps(original_generate)
        def generate(*args, **kwargs):
            caller = inspect.currentframe().f_back
            stage = 'update' if 'temp_uuid_mapping' in caller.f_locals else 'extraction'
            mapping = deepcopy(caller.f_locals.get('temp_uuid_mapping', {}))
            self.emit('model_input', stage=stage, messages=deepcopy(kwargs.get('messages')),
                      response_format=kwargs.get('response_format'), native_temp_uuid_mapping=mapping,
                      native_new_facts=deepcopy(caller.f_locals.get('new_retrieved_facts')),
                      native_retrieved_old_memory=deepcopy(caller.f_locals.get('retrieved_old_memory')))
            del caller
            tick = time.perf_counter()
            try:
                result = original_generate(*args, **kwargs)
                from mem0.memory.utils import remove_code_blocks
                try:
                    parsed, parse_error = json.loads(remove_code_blocks(result)), None
                except Exception:
                    parsed, parse_error = None, traceback.format_exc()
                self.emit('model_output', stage=stage, raw_response=result, parsed=parsed, parse_error=parse_error,
                          native_temp_uuid_mapping=mapping, elapsed_seconds=time.perf_counter() - tick)
                return result
            except Exception:
                self.emit('model_exception', stage=stage, traceback=traceback.format_exc())
                raise
        memory.llm.generate_response = generate

        original_search = memory.vector_store.search

        @functools.wraps(original_search)
        def search(*args, **kwargs):
            tick = time.perf_counter()
            self.emit('recall_input', query=kwargs.get('query'), limit=kwargs.get('limit'),
                      filters=deepcopy(kwargs.get('filters')), vector_dimensions=len(kwargs.get('vectors', [])))
            try:
                result = original_search(*args, **kwargs)
                self.emit('recall_output', query=kwargs.get('query'),
                          candidates=[p.model_dump(mode='json') for p in result], elapsed_seconds=time.perf_counter() - tick)
                return result
            except Exception:
                self.emit('recall_exception', traceback=traceback.format_exc())
                raise
        memory.vector_store.search = search
        for name, event in [('_create_memory', 'ADD'), ('_update_memory', 'UPDATE'), ('_delete_memory', 'DELETE')]:
            original = getattr(memory, name)
            signature = inspect.signature(original)

            def wrap(original=original, signature=signature, event=event):
                @functools.wraps(original)
                def operation(*args, **kwargs):
                    bound = signature.bind(*args, **kwargs).arguments
                    info = {k: deepcopy(v) for k, v in bound.items() if k != 'existing_embeddings'}
                    self.emit('operation_attempt', event=event, arguments=info)
                    try:
                        result = original(*args, **kwargs)
                        self.emit('operation_result', event=event, arguments=info, memory_id=result,
                                  status='ok', native_return=result)
                        return result
                    except Exception:
                        self.emit('operation_result', event=event, arguments=info, status='error', traceback=traceback.format_exc())
                        raise
                return operation
            setattr(memory, name, wrap())


def derived_session(out, folder, observer, log):
    entries = [e for e in observer.entries if e['phase'] == folder.name]
    base.write_json(folder / 'observations.json', entries)
    outputs = [e for e in entries if e['kind'] == 'model_output']
    facts = [e for e in outputs if e['stage'] == 'extraction']
    updates = [e for e in outputs if e['stage'] == 'update']
    base.write_json(folder / 'extracted_facts.json', facts)
    base.write_json(folder / 'recall_candidates.json', [e for e in entries if e['kind'].startswith('recall_')])
    base.write_json(folder / 'update_model_io.json', [e for e in entries if e.get('stage') == 'update'])
    plans = []
    for output in updates:
        for i, action in enumerate((output['parsed'] or {}).get('memory', [])):
            plans.append({'plan_index_zero_based': i, **action,
                          'resolved_existing_memory_id': (output['native_temp_uuid_mapping'].get(action.get('id'))
                                                          if action.get('event') in ('UPDATE', 'DELETE', 'NONE') else None),
                          'observation_sequence': output['sequence']})
    base.write_json(folder / 'full_operation_plan.json', plans)
    base.write_json(folder / 'execution_results.json', [e for e in entries if e['kind'].startswith('operation_')])
    runtime = [json.loads(s) for s in (out / 'runtime.jsonl').read_text().splitlines() if s.strip()]
    none_count = sum(e['phase'] == folder.name and e['message'] == 'NOOP for Memory.' for e in runtime)
    return {'planned_operation_counts_including_NONE': dict(Counter(p.get('event') for p in plans)),
            'native_NONE_dispatch_count': none_count,
            'planned_NONE_matches_native_dispatch': none_count == sum(p.get('event') == 'NONE' and bool(p.get('text')) for p in plans)}


def execute(out):
    out = Path(out).resolve()
    assert out.parent == ROOT / 'results/local_update_case'
    assert not (out / 'execution_started.json').exists(), 'Refusing repeat ingestion; inspect saved state instead'
    os.environ['MEM0_DIR'] = str(out / 'mem0_runtime')
    os.environ['MEM0_TELEMETRY'] = 'False'
    settings, provenance, missing = base.load_settings()
    assert not missing, missing
    os.environ.pop('OPENROUTER_API_KEY', None)
    import mem0
    from mem0 import Memory
    assert md.version('mem0ai') == '0.1.118'
    assert Path(mem0.__file__).resolve() == ROOT / 'mem0_v0.1.118/mem0/__init__.py'
    assert native_source() == read(out / 'source_integrity.json')['native_source_sha256']
    base.save_dependencies(out)
    config = read(SOURCE / 'mem0_config.json')
    actual_llm = {'model': settings['LLM_MODEL'], 'api_key': settings['LLM_API_KEY'],
                  'openai_base_url': settings['LLM_BASE_URL']}
    for key, name, convert in [('OPENAI_MAX_TOKENS', 'max_tokens', int), ('OPENAI_TEMPERATURE', 'temperature', float)]:
        if key in settings:
            actual_llm[name] = convert(settings[key])
    assert base.clean(actual_llm) == config['llm']['config'], 'Validated LLM configuration changed'
    actual_embedder = {'model': settings['EMBEDDING_MODEL'], 'api_key': settings['EMBEDDING_API_KEY'],
                      'openai_base_url': settings['EMBEDDING_BASE_URL'], 'embedding_dims': int(settings['EMBEDDING_DIMS'])}
    assert base.clean(actual_embedder) == config['embedder']['config'], 'Validated embedding configuration changed'
    config['llm']['config'] = actual_llm
    config['embedder']['config'] = actual_embedder
    config['vector_store']['config']['path'] = str(out / 'qdrant')
    config['history_db_path'] = str(out / 'history.db')
    base.write_json(out / 'mem0_config.json', config)
    base.write_json(out / 'configuration.json', {'settings': settings, 'sources': provenance, 'infer': True,
                    'custom_prompts': None, 'graph_enabled': False, 'native_recall_limit': 5,
                    'labels_or_answers_injected': False, 'linked_original_run': str(SOURCE),
                    'timeout_seconds': float(settings.get('OPENAI_TIMEOUT', 180))})
    base.write_json(out / 'environment.json', {'python': sys.version, 'platform': platform.platform(),
        'conda_environment': os.environ['CONDA_DEFAULT_ENV'], 'mem0ai': md.version('mem0ai'),
        'mem0_file': mem0.__file__, 'harness_sha256': base.sha256(Path(__file__)),
        'native_source_sha256': native_source()})
    selected, prefix = read(out / 'selected_input.json'), read(out / 'prefix_verification.json')
    user_id = selected['user_uuid']
    observer, api = Observer(out), base.APIAudit(out / 'api_calls.jsonl')
    log = base.AuditHandler(out / 'runtime.jsonl')
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(log)
    for name in ('httpx', 'httpcore', 'openai'):
        logging.getLogger(name).setLevel(logging.WARNING)
    (out / 'runtime.jsonl').touch()
    report = {'run_id': out.name, 'status': 'started', 'linked_original_run': str(SOURCE),
              'user_uuid': user_id, 'prefix_reused': prefix['verified'],
              'completed_new_session_ordinals': [], 'sessions': []}
    memory = None
    tick = time.perf_counter()
    try:
        memory = Memory.from_config(config)
        assert not memory.enable_graph and memory.custom_fact_extraction_prompt is None and memory.custom_update_memory_prompt is None
        timeout = float(settings.get('OPENAI_TIMEOUT', 180))
        memory.llm.client = memory.llm.client.with_options(timeout=timeout)
        memory.embedding_model.client = memory.embedding_model.client.with_options(timeout=timeout)
        api.wrap(memory.llm.client.chat.completions, 'llm')
        api.wrap(memory.embedding_model.client.embeddings, 'embedding')
        observer.install(memory)
        initial = base.snapshot(memory, user_id)
        assert initial['database_count_exact'] == (29 if prefix['verified'] else 0)
        base.write_json(out / 'initial_snapshot.json', initial)
        base.write_json(out / 'execution_started.json', {'time': now(), 'one_shot': True})
        initial_history_count = len(base.history_rows(out / 'history.db'))
        report['initial_history_count'] = initial_history_count
        for session in selected['sessions']:
            ordinal = session['chronological_session_ordinal_one_based']
            phase = f'session_{ordinal:02d}'
            api.phase = log.phase = observer.phase = phase
            folder = out / phase
            folder.mkdir()
            base.write_json(folder / 'input.json', session)
            before = base.snapshot(memory, user_id)
            base.write_json(folder / 'before.json', before)
            old_history = base.history_rows(out / 'history.db')
            error_start, call_start = len(log.errors), len(api.calls)
            returned, error = None, None
            start = time.perf_counter()
            observer.emit('session_add_input', messages=deepcopy(session['messages']), user_id=user_id,
                          infer=True, raw_dialogue=deepcopy(session['raw_dialogue']))
            try:
                returned = memory.add(session['messages'], user_id=user_id, infer=True)
            except Exception:
                error = traceback.format_exc()
                logging.getLogger(__name__).exception('Native session add raised')
            observer.emit('session_add_result', return_value=returned, exception=error)
            base.write_json(folder / 'add_return.json', {'return_value': returned, 'exception': error,
                            'elapsed_seconds': time.perf_counter() - start})
            after = base.snapshot(memory, user_id)
            base.write_json(folder / 'after.json', after)
            ops = base.history_rows(out / 'history.db')[len(old_history):]
            base.write_json(folder / 'actual_operations.json', ops)
            checks = base.reconcile(before, after, ops, returned)
            checks.update(derived_session(out, folder, observer, log))
            checks.update(session_ordinal=ordinal, before_count=before['database_count_exact'],
                          after_count=after['database_count_exact'], native_error_count=len(log.errors) - error_start,
                          add_exception=error, input_message_count=len(session['messages']))
            calls = api.calls[call_start:]
            checks['all_api_calls_ok'] = all(c['status'] == 'ok' for c in calls)
            checks['all_llm_outputs_untruncated'] = all(c['response']['choices'][0]['finish_reason'] == 'stop' for c in calls if c['kind'] == 'llm')
            base.write_json(folder / 'verification.json', checks)
            report['sessions'].append(checks)
            assert not error and checks['native_error_count'] == 0 and checks['all_api_calls_ok'] and checks['all_llm_outputs_untruncated']
            assert checks['planned_NONE_matches_native_dispatch']
            report['completed_new_session_ordinals'].append(ordinal)
            base.write_json(out / 'summary.json', report)
            print(f'{phase}: {checks["before_count"]} -> {checks["after_count"]}; actual {checks["actual_operation_counts"]}; planned {checks["planned_operation_counts_including_NONE"]}', flush=True)
        report['status'] = 'completed'
    except Exception:
        report.update(status='failed', exception=traceback.format_exc())
        logging.getLogger(__name__).exception('Update case failed')
    finally:
        if memory:
            try:
                final = base.snapshot(memory, user_id)
                base.write_json(out / 'final_snapshot.json', final)
                rows = base.history_rows(out / 'history.db')
                base.write_json(out / 'all_actual_operations.json', rows)
                new_rows = rows[report.get('initial_history_count', 0):]
                base.write_json(out / 'new_actual_operations.json', new_rows)
                report['final_memory_count'] = final['database_count_exact']
                report['new_actual_operation_counts'] = dict(Counter(r['event'] for r in new_rows))
                memory.vector_store.client.close()
                from qdrant_client import QdrantClient
                reopened = QdrantClient(path=str(out / 'qdrant'))
                try:
                    persisted, count, pages = base.collect_points(reopened, 'local_smoke', None)
                finally:
                    reopened.close()
                report['persistence_comparison'] = base.verify_persistence(final['database_points_with_vectors'], persisted)
                base.write_json(out / 'reopened_snapshot.json', {'database_count_exact': count, 'scroll_pages': pages,
                                'database_points_with_vectors': persisted})
                with sqlite3.connect(f'file:{out / "history.db"}?mode=ro', uri=True) as db:
                    report['history_integrity_check'] = db.execute('PRAGMA integrity_check').fetchone()[0]
                    assert report['history_integrity_check'] == 'ok'
            except Exception:
                report.update(status='failed', final_verification_exception=traceback.format_exc())
            finally:
                memory.db.close()
                memory._telemetry_vector_store.client.close()
        report['elapsed_seconds'] = time.perf_counter() - tick
        report['usage'] = api.summary()
        report['original_run_unchanged'] = manifest(SOURCE) == read(out / 'original_manifest.before.json')
        report['native_source_unchanged'] = native_source() == read(out / 'source_integrity.json')['native_source_sha256']
        base.write_json(out / 'original_manifest.after.json', manifest(SOURCE))
        base.write_json(out / 'errors.json', log.errors)
        base.write_json(out / 'summary.json', report)
        print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0 if report['status'] == 'completed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', type=Path, help='Execute an already prepared case once')
    args = parser.parse_args()
    assert os.environ.get('CONDA_DEFAULT_ENV') == 'mem0_halumem'
    if args.execute:
        return execute(args.execute)
    prepare()
    return 0


if __name__ == '__main__':
    sys.exit(main())
