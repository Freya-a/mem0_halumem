#!/usr/bin/env python3
"""Rejudge exactly the recorded seven missing scores using official functions."""
import copy
import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = HERE.parent / 'native_official_baseline_20261113_v1'
DATA = BASE / 'results/memzero-development/memzero_eval_results.jsonl'
RESULT = BASE / 'results/memzero-development/memzero_eval_stat_result.json'
INVALID = BASE / 'invalid_scores.jsonl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write_atomic(path, obj):
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_cases():
    meta = json.loads((BASE / 'run_metadata.json').read_text())
    require(sha(DATA) == meta['input_sha256'], 'original input fingerprint changed')
    expected = {name: digest for digest, name in (line.split(maxsplit=1) for line in (BASE / 'SHA256SUMS').read_text().splitlines())}
    require(sha(RESULT) == expected['results/memzero-development/memzero_eval_stat_result.json'], 'original scoring result fingerprint changed')
    for filename, expected in meta['file_sha256'].items():
        require(sha(ROOT / filename) == expected, f'original code changed: {filename}')
    require(sha(INVALID) == '82105fdd435b1b61625ff5c10d8b9fa5b7e1797efa484d136d46c143211c03be', 'invalid records changed')
    baseline = json.loads(RESULT.read_text())
    with DATA.open(encoding='utf-8') as f:
        inputs = {u['uuid']: u for line in f if (u := json.loads(line))}
    with INVALID.open(encoding='utf-8') as f:
        invalid = [json.loads(line) for line in f]
    require(len(invalid) == 7 and sum(x['task'] == 'accuracy' for x in invalid) == 6 and sum(x['task'] == 'update' for x in invalid) == 1, 'unexpected invalid set')
    cases = []
    for number, row in enumerate(invalid, 1):
        kind = row['task']
        rec = row['record']
        section = 'memory_accuracy_records' if kind == 'accuracy' else 'memory_update_records'
        matches = [idx for idx, r in enumerate(baseline[section]) if r == rec]
        require(len(matches) == 1, f'baseline record not unique: {number}')
        session = inputs[rec['uuid']]['sessions'][rec['ssession_id']]
        if kind == 'accuracy':
            require(rec['memory_accuracy_score'] is None, 'already valid accuracy')
            indices = [i for i, x in enumerate(session['extracted_memories']) if x == rec['memory_content']]
            dialogue = []
            for turn in session['dialogue']:
                dialogue.append(f"[{turn['timestamp']}]{turn['role']}: {turn['content']}")
                if turn['role'] == 'assistant':
                    dialogue.append('')
            gold = '\n'.join(m['memory_content'] for m in session['memory_points'] if m['memory_source'] != 'interference')
            args = ['\n'.join(dialogue), gold, rec['memory_content']]
        else:
            require(rec['memory_update_type'] not in ('Correct', 'Hallucination', 'Omission', 'Other'), 'already valid update')
            indices = [i for i, m in enumerate(session['memory_points']) if all(rec.get(k) == value for k, value in m.items())]
            args = ['\n'.join(rec['memories_from_system']), rec['memory_content'], '\n'.join(rec['original_memories'])]
        require(len(indices) == 1, f'input record not unique: {number}')
        cases.append({'number': number, 'kind': kind, 'section': section, 'record_index': matches[0],
                      'uuid': rec['uuid'], 'session_index': rec['ssession_id'], 'input_index': indices[0], 'args': args})
    require(len({(c['section'], c['record_index']) for c in cases}) == 7, 'duplicate case')
    return baseline, cases


def merge_results(baseline, cases, results):
    require(len(cases) == len(results), 'case/result count mismatch')
    merged = copy.deepcopy(baseline)
    for case, result in zip(cases, results):
        if result['status'] != 'valid':
            continue
        rec = merged[case['section']][case['record_index']]
        if case['kind'] == 'accuracy':
            rec['memory_accuracy_score'] = result['normalized']['accuracy_score']
            rec['is_included_in_golden_memories'] = result['normalized']['is_included_in_golden_memories']
        else:
            rec['memory_update_type'] = result['normalized']['evaluation_result']
    return merged


def normalize(kind, parsed):
    require(isinstance(parsed, dict), 'parsed response is not a JSON object')
    if kind == 'accuracy':
        score = int(parsed['accuracy_score'])
        flag = parsed['is_included_in_golden_memories']
        require(score in (0, 1, 2), 'accuracy score outside official rubric')
        require(flag in ('true', 'True', 'false', 'False'), 'target inclusion is not an official string')
        return {'accuracy_score': score, 'is_included_in_golden_memories': flag}
    label = parsed.get('evaluation_result')
    require(label in ('Correct', 'Hallucination', 'Omission', 'Other'), 'invalid update label')
    return {'evaluation_result': label}


def main():
    from dotenv import dotenv_values
    baseline, cases = load_cases()
    config = json.loads((BASE / 'run_metadata.json').read_text())
    values = dotenv_values(ROOT / '.env.local')
    require(values['LLM_MODEL'] == config['judge_model_alias'], 'model alias changed')
    from urllib.parse import urlsplit
    require(urlsplit(values['LLM_BASE_URL']).hostname == config['base_url_host'], 'service host changed')
    require(not (HERE / 'run_config.json').exists(), 'run already started; refuse to repeat calls')
    os.environ.update(OPENAI_API_KEY=values['LLM_API_KEY'], OPENAI_BASE_URL=values['LLM_BASE_URL'],
                      OPENAI_MODEL=config['judge_model_alias'], OPENAI_TEMPERATURE='0', OPENAI_MAX_TOKENS='16384',
                      OPENAI_TIMEOUT='180', RETRY_TIMES='1', WAIT_TIME_LOWER='1', WAIT_TIME_UPPER='1',
                      NO_PROXY='dashscope.aliyuncs.com', no_proxy='dashscope.aliyuncs.com')
    sys.path.insert(0, str(ROOT / 'HaluMem/eval'))
    import llms
    import eval_tools
    import evaluation
    require(sys.version.split()[0] == config['python'].split()[0], 'python version differs from baseline')
    import openai
    require(openai.__version__ == config['dependencies']['openai'], 'OpenAI SDK version differs from baseline')
    write_new(HERE / 'run_config.json', {'source_baseline': str(BASE), 'model': config['judge_model_alias'],
        'endpoint_host': config['base_url_host'], 'endpoint_path': urlsplit(values['LLM_BASE_URL']).path,
        'temperature': 0, 'max_tokens': 16384, 'timeout_seconds': 180,
        'official_retry_attempts': 1, 'sdk_retries': 2, 'python': sys.version, 'openai': openai.__version__,
        'official_commit': config['official_commit'], 'official_file_sha256': config['file_sha256'],
        'input_sha256': sha(DATA), 'baseline_result_sha256': sha(RESULT), 'invalid_sha256': sha(INVALID),
        'note': 'Exactly one official scorer invocation per item; SDK may internally retry connection failures. Model alias does not pin weights.'})
    results = []
    for case in cases:
        path = HERE / f"case_{case['number']:02d}.json"
        state = {'case': case, 'status': 'started', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 'request': None, 'raw_response': None, 'parsed': None, 'normalized': None, 'exception': None}
        write_new(path, state)
        create = llms.client.chat.completions.create
        def captured_create(*args, **kwargs):
            state['request'] = kwargs
            write_atomic(path, state)
            response = create(*args, **kwargs)
            state['raw_response'] = response.model_dump(mode='json')
            state['request_id'] = getattr(response, '_request_id', None)
            write_atomic(path, state)
            return response
        llms.client.chat.completions.create = captured_create
        start = time.monotonic()
        try:
            fn = eval_tools.evaluation_for_memory_accuracy if case['kind'] == 'accuracy' else eval_tools.evaluation_for_update_memory
            state['parsed'] = fn(*case['args'])
            state['normalized'] = normalize(case['kind'], state['parsed'])
            state['status'] = 'valid'
        except Exception as exc:
            secret = values['LLM_API_KEY'] or ''
            message = str(exc)
            if secret:
                message = message.replace(secret, '[REDACTED]')
            state['exception'] = {'type': type(exc).__name__, 'message': message,
                                  'status_code': getattr(exc, 'status_code', None),
                                  'request_id': getattr(exc, 'request_id', None),
                                  'cause_type': type(exc.__cause__).__name__ if exc.__cause__ else None}
            state['status'] = 'invalid'
        finally:
            llms.client.chat.completions.create = create
            state['elapsed_seconds'] = round(time.monotonic() - start, 3)
            state['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            write_atomic(path, state)
        results.append(state)
        print(f"case {case['number']}: {state['status']}", flush=True)
    merged = merge_results(baseline, cases, results)
    for counters in merged['overall_score']['memory_type_accuracy'].values():
        counters.update(memory_integrity_acc=0, memory_update_acc=0, total_num=0, memory_acc=0)
    try:
        evaluation.aggregate_eval_results(merged)
        write_new(HERE / 'merged_official_scores.json', merged)
    except Exception as exc:
        write_new(HERE / 'aggregation_error.json', {'type': type(exc).__name__, 'message': str(exc)})
        raise


if __name__ == '__main__':
    main()
