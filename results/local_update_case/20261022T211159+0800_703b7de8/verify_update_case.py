#!/usr/bin/env python3
"""Offline evidence verification for one local_update_case; no model calls."""
import json
import math
import os
from pathlib import Path
import sys

import local_update_case as case
from local_update_case import base, read


def verify(out):
    out = Path(out).resolve()
    assert os.environ.get('CONDA_DEFAULT_ENV') == 'mem0_halumem'
    assert out.parent == case.ROOT / 'results/local_update_case'
    os.environ['MEM0_DIR'] = str(out / 'mem0_runtime')
    os.environ['MEM0_TELEMETRY'] = 'False'
    from mem0.memory.utils import get_fact_retrieval_messages, parse_messages, remove_code_blocks
    from qdrant_client import QdrantClient
    summary = read(out / 'summary.json')
    # A native action error is an observed outcome, not permission to replay input.
    assert summary['status'] in ('completed', 'failed')
    target = read(out / 'target.json')
    selected = read(out / 'selected_input.json')
    raw = read(out / 'raw_history_prefix.json')
    observations = [json.loads(s) for s in (out / 'observations.jsonl').read_text().splitlines()]
    api = [json.loads(s) for s in (out / 'api_calls.jsonl').read_text().splitlines()]
    runtime = [json.loads(s) for s in (out / 'runtime.jsonl').read_text().splitlines()]
    dataset = case.ROOT / 'HaluMem/data/HaluMem-Medium.jsonl'
    assert base.sha256(dataset) == read(out / 'data_check.json')['sha256']
    with dataset.open() as f:
        u = next(json.loads(s) for s in f if json.loads(s)['uuid'] == target['user_uuid'])
    source_sessions = case.ordered(u)
    for s in raw['sessions']:
        ordinal = s['chronological_session_ordinal_one_based']
        index, source = source_sessions[ordinal - 1]
        assert s == case.session_input(u, target['dataset_line_one_based'], ordinal, index, source)
    scan = read(out / 'selection_scan.json')
    assert scan[-1]['qualifies'] and not any(r['qualifies'] for r in scan[:-1])
    assert case.true_flag(target['annotation']['is_update']) and target['old_propositions']
    initial, final = read(out / 'initial_snapshot.json'), read(out / 'final_snapshot.json')
    rows = base.history_rows(out / 'history.db')
    assert rows == read(out / 'all_actual_operations.json')
    prefix_count = summary['initial_history_count']
    assert rows[prefix_count:] == read(out / 'new_actual_operations.json')
    if summary['prefix_reused']:
        assert rows[:prefix_count] == read(out / 'linked_original/all_actual_operations.json')
        base.verify_persistence(read(out / 'linked_original/final_snapshot.json')['database_points_with_vectors'], initial['database_points_with_vectors'])
    previous = initial
    verified = []
    for s in selected['sessions']:
        ordinal = s['chronological_session_ordinal_one_based']
        phase = f'session_{ordinal:02d}'
        folder = out / phase
        assert read(folder / 'input.json') == s == raw['sessions'][ordinal - 1]
        before, after = read(folder / 'before.json'), read(folder / 'after.json')
        assert before['not_truncated'] and after['not_truncated']
        base.verify_persistence(previous['database_points_with_vectors'], before['database_points_with_vectors'])
        ops = read(folder / 'actual_operations.json')
        returned = read(folder / 'add_return.json')
        assert returned['exception'] is None
        base.reconcile(before, after, ops, returned['return_value'])
        assert rows[prefix_count:prefix_count + len(ops)] == ops
        prefix_count += len(ops)
        obs = [e for e in observations if e['phase'] == phase]
        adds = [e for e in obs if e['kind'] == 'session_add_input']
        assert len(adds) == 1 and adds[0]['messages'] == s['messages'] and adds[0]['infer'] is True
        assert adds[0]['raw_dialogue'] == s['raw_dialogue']
        assert adds[0]['user_id'] == selected['user_uuid']
        models_in = [e for e in obs if e['kind'] == 'model_input']
        models_out = [e for e in obs if e['kind'] == 'model_output']
        assert [e['stage'] for e in models_in] == ['extraction', 'update']
        assert [e['stage'] for e in models_out] == ['extraction', 'update']
        system, prompt = get_fact_retrieval_messages(parse_messages(s['messages']))
        assert models_in[0]['messages'] == [{'role': 'system', 'content': system}, {'role': 'user', 'content': prompt}]
        sdk = [c for c in api if c['phase'] == phase and c['kind'] == 'llm']
        assert len(sdk) == 2
        for a, b, c in zip(models_in, models_out, sdk):
            assert a['messages'] == c['request']['messages']
            assert b['raw_response'] == c['response']['choices'][0]['message']['content']
            assert b['parse_error'] is None and c['status'] == 'ok'
            assert c['response']['choices'][0]['finish_reason'] == 'stop'
        facts = models_out[0]['parsed']['facts']
        recall_in = [e for e in obs if e['kind'] == 'recall_input']
        recalls = [e for e in obs if e['kind'] == 'recall_output']
        assert [r['query'] for r in recalls] == [r['query'] for r in recall_in] == facts
        assert all(r['limit'] == 5 and r['filters'] == {'user_id': selected['user_uuid']} for r in recall_in)
        prior = {str(p['id']): p['payload']['data'] for p in before['database_points_with_vectors']}
        unique = {}
        for recall in recalls:
            assert len(recall['candidates']) <= 5
            for point in recall['candidates']:
                assert prior[str(point['id'])] == point['payload']['data']
                assert math.isfinite(point['score'])
                unique[str(point['id'])] = point['payload']['data']
        mapping = {str(i): key for i, key in enumerate(unique)}
        assert mapping == models_in[1]['native_temp_uuid_mapping'] == models_out[1]['native_temp_uuid_mapping']
        assert models_in[1]['native_retrieved_old_memory'] == [{'id': str(i), 'text': text} for i, text in enumerate(unique.values())]
        assert models_in[1]['native_new_facts'] == facts
        from mem0.configs.prompts import get_update_memory_messages
        expected_prompt = get_update_memory_messages(models_in[1]['native_retrieved_old_memory'], facts, None)
        assert models_in[1]['messages'] == [{'role': 'user', 'content': expected_prompt}]
        plans = read(folder / 'full_operation_plan.json')
        assert [{k: v for k, v in p.items() if k not in ('plan_index_zero_based', 'resolved_existing_memory_id', 'observation_sequence')} for p in plans] == models_out[1]['parsed']['memory']
        successes = [e for e in obs if e['kind'] == 'operation_result' and e['status'] == 'ok']
        assert len(successes) == len(ops)
        for execution, row in zip(successes, ops):
            assert execution['event'] == row['event'] and execution['memory_id'] == row['memory_id']
            assert execution['arguments'].get('data') == row['new_memory']
        actual_iter = iter(successes)
        decisions = []
        none_logs = [e for e in runtime if e['phase'] == phase and e['message'] == 'NOOP for Memory.']
        none_iter = iter(none_logs)
        native_rejections = []
        for p in plans:
            if p['event'] == 'NONE':
                log = next(none_iter)
                decisions.append({**p, 'actual_status': 'native_NONE_no_write', 'native_log_time': log['time']})
            elif p['event'] in ('UPDATE', 'DELETE') and p['id'] not in mapping:
                failures = [e for e in runtime if e['phase'] == phase and e['logger'] == 'mem0.memory.main'
                            and e['level'] == 'ERROR' and e['message'].startswith('Error processing memory action:')
                            and f"'id': '{p['id']}'" in e['message'] and f"Error: '{p['id']}'" in e['message']]
                assert len(failures) == 1
                native_rejections.extend(failures)
                decisions.append({**p, 'actual_status': 'native_action_error_before_method_call',
                    'actual_memory_id': None, 'native_log_time': failures[0]['time'],
                    'native_error': failures[0]['message'],
                    'reason': 'Model temporary ID absent from native temp_uuid_mapping; native lookup raises KeyError before operation method'})
            else:
                event = next(actual_iter)
                assert event['event'] == p['event'] and event['arguments'].get('data') == p.get('text')
                if p['event'] in ('UPDATE', 'DELETE'):
                    assert event['memory_id'] == p['resolved_existing_memory_id']
                decisions.append({**p, 'actual_status': 'executed', 'actual_memory_id': event['memory_id'],
                                  'model_id_ignored_by_native_ADD': p['event'] == 'ADD',
                                  'execution_observation_sequence': event['sequence']})
        assert next(actual_iter, None) is None and next(none_iter, None) is None
        base.write_json(folder / 'plan_execution_correspondence.json', decisions)
        native_errors = [e for e in runtime if e['level'] == 'ERROR' and e['phase'] == phase and e['logger'] == 'mem0.memory.main']
        assert native_errors == native_rejections
        assert all(e['status'] == 'ok' for e in api if e['phase'] == phase)
        verified.append({'ordinal': ordinal, 'message_count': len(s['messages']), 'facts': len(facts),
                         'recall_queries': len(recalls), 'unique_candidates': len(mapping),
                         'plan_entries': len(plans), 'executed_operations': len(ops), 'NONE_dispatches': len(none_logs),
                         'native_rejected_actions': len(native_rejections)})
        previous = after
    assert prefix_count == len(rows)
    base.verify_persistence(previous['database_points_with_vectors'], final['database_points_with_vectors'])
    client = QdrantClient(path=str(out / 'qdrant'))
    try:
        disk, count, _ = base.collect_points(client, 'local_smoke', None)
    finally:
        client.close()
    persistence = base.verify_persistence(final['database_points_with_vectors'], disk)
    assert count == summary['final_memory_count']
    import sqlite3
    with sqlite3.connect(f'file:{out / "history.db"}?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert case.manifest(case.SOURCE) == read(out / 'original_manifest.before.json') == read(out / 'original_manifest.after.json')
    assert case.native_source() == read(out / 'source_integrity.json')['native_source_sha256']
    recorded_errors = read(out / 'errors.json')
    assert recorded_errors == [e for e in runtime if e['level'] == 'ERROR']
    native_error_count = sum(s['native_rejected_actions'] for s in verified)
    if native_error_count:
        assert summary['status'] == 'failed'
        assert len(recorded_errors) == native_error_count + 1
        assert recorded_errors[-1]['message'] == 'Update case failed' and 'AssertionError' in recorded_errors[-1]['traceback']
        assert summary['completed_new_session_ordinals'] == [s['ordinal'] for s in verified if not s['native_rejected_actions']]
    else:
        assert summary['status'] == 'completed' and recorded_errors == []
        assert summary['completed_new_session_ordinals'] == [s['ordinal'] for s in verified]
    assert selected['sessions'][-1]['chronological_session_ordinal_one_based'] == target['chronological_session_ordinal_one_based']
    result = {'status': 'passed', 'additional_model_calls': 0, 'time': case.now(),
        'sessions': verified, 'original_run_byte_identical': True, 'native_source_unchanged': True,
        'input_and_both_native_prompts_exact': True, 'recall_candidates_and_integer_ID_mapping_verified': True,
        'full_plans_including_NONE_and_rejected_actions_match_native_dispatch_and_history': True,
        'native_action_error_count': native_error_count,
        'snapshot_chain_and_history_replay_verified': True, 'history_integrity_check': 'ok',
        'persistence_comparison': persistence, 'single_target_stop_boundary_verified': True}
    base.write_json(out / 'independent_verification.json', result)
    base.write_json(out / 'diagnostic_summary.json', {
        'diagnostic_status': 'completed_with_native_action_error' if native_error_count else 'completed',
        'original_execution_status': summary['status'],
        'all_selected_sessions_fully_submitted_and_returned': True,
        'processed_session_ordinals': [s['ordinal'] for s in verified],
        'sessions_with_no_native_action_errors': summary['completed_new_session_ordinals'],
        'one_target_only': True, 'additional_model_calls_during_verification': 0,
        'native_action_error_count': native_error_count,
        'native_error_corrected_or_retried': False,
        'independent_evidence_verification': 'passed',
        'note': 'summary.json retains the execution harness strict failure status. Diagnostic completion means all planned raw dialogue was submitted once, target session returned, all actions/errors and final state were reconciled; it does not mean every native action succeeded.'})
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    verify(sys.argv[1])
