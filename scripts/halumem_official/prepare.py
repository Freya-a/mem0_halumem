#!/usr/bin/env python3
"""Build official HaluMem scorer inputs from the recorded development run."""
import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'results/medium_dev/williams_native_prefix5_20261028_v3'
PREVIOUS = ROOT / 'results/medium_dev/official_eval_development_20261029_v1'
DATA = ROOT / 'HaluMem/data/HaluMem-Medium.jsonl'
OFFICIAL = ROOT / 'HaluMem/eval/evaluation.py'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_records():
    with (PREVIOUS / 'records.jsonl').open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def build_inputs(records=None):
    manifest = read(RUN / 'manifest.json')
    require(sha(DATA) == manifest['dataset_sha256'], 'dataset hash mismatch')
    wanted = set(manifest['selected_users'])
    with DATA.open(encoding='utf-8') as f:
        sources = {u['uuid']: u for line in f if (u := json.loads(line))['uuid'] in wanted}
    require(set(sources) == wanted, 'selected users missing')
    records = read_records() if records is None else records
    indexed = {}
    for rec in records:
        src = rec['source']
        kind = rec['kind']
        require(kind in ('update', 'qa'), 'unknown record kind')
        idx = src['memory_point_index_zero_based'] if kind == 'update' else src['question_index_zero_based']
        key = (src['uuid'], src['session_index_zero_based'], kind, idx)
        require(key not in indexed, 'duplicate record')
        indexed[key] = rec
    used = set()
    users = []
    summary = {'users': 0, 'sessions': 0, 'updates': 0, 'questions': 0,
               'reference_memories': 0, 'extracted_memories': 0, 'interference_memories': 0, 'anomalous_sessions': 0,
               'dataset_sha256': manifest['dataset_sha256'],
               'official_evaluation_sha256': sha(OFFICIAL),
               'previous_records_sha256': sha(PREVIOUS / 'records.jsonl')}
    for prefix in manifest['prefixes']:
        uid = prefix['user_uuid']
        original = sources[uid]
        match = re.search(r'Name:\s*(.*?); Gender:', original.get('persona_info', ''))
        require(bool(original.get('user_name') or match), 'user name missing')
        user = {'uuid': uid, 'user_name': original.get('user_name') or match.group(1).strip(), 'sessions': []}
        checkpoint = read(RUN / 'users' / uid / 'checkpoint.json')
        indices = prefix['original_session_indices_zero_based']
        require(checkpoint['completed_ordinal'] == len(indices) == len(checkpoint['commits']), 'incomplete sessions')
        for ordinal, index in enumerate(indices, 1):
            folder = RUN / 'users' / uid / f'session_{ordinal:03d}'
            commit = checkpoint['commits'][ordinal - 1]
            require(commit['ordinal'] == ordinal, 'checkpoint order mismatch')
            verification = 'verification.json' if (folder / 'verification.json').exists() else 'observed_anomaly.json'
            for filename in ('input.json', 'add_return.json', 'after.json', verification):
                require(sha(folder / filename) == commit['artifacts_sha256'][filename], f'{filename} hash mismatch')
            summary['anomalous_sessions'] += verification == 'observed_anomaly.json'
            session = copy.deepcopy(original['sessions'][index])
            inp = read(folder / 'input.json')
            require(inp['user_uuid'] == uid and inp['original_session_index_zero_based'] == index and inp['raw_dialogue'] == session['dialogue'], 'session mismatch')
            add = read(folder / 'add_return.json')
            require(add['exception'] is None and isinstance(add['return_value']['results'], list), 'add result unavailable')
            session['extracted_memories'] = [item['memory'] for item in add['return_value']['results']]
            session['add_dialogue_duration_ms'] = add['add_elapsed_seconds'] * 1000
            for kind, field in (('update', 'memory_points'), ('qa', 'questions')):
                for i, item in enumerate(session.get(field, [])):
                    if kind == 'update' and not (item['is_update'] == 'True' and item.get('original_memories')):
                        continue
                    key = (uid, index, kind, i)
                    require(key in indexed, f'missing {kind} record {key}')
                    rec = indexed[key]
                    src = rec['source']
                    require(src['session_ordinal_one_based'] == ordinal and src['snapshot_sha256'] == sha(folder / 'after.json'), 'snapshot mismatch')
                    require(src['memory_point' if kind == 'update' else 'question'] == item, f'{kind} source mismatch')
                    require(rec['stages']['retrieval']['status'] == 'ok', f'{kind} retrieval unavailable')
                    hits = rec['stages']['retrieval']['payload']['hits']
                    require(isinstance(hits, list), 'invalid hits')
                    if kind == 'update':
                        item['memories_from_system'] = [f"{h['timestamp']}: {h['memory']}" for h in hits]
                        summary['updates'] += 1
                    else:
                        require(rec['stages']['answer']['status'] == 'ok', 'qa answer unavailable')
                        answer = rec['stages']['answer']['payload']['text']
                        require(isinstance(answer, str), 'invalid qa answer')
                        item['system_response'] = answer
                        summary['questions'] += 1
                    used.add(key)
            summary['sessions'] += 1
            summary['reference_memories'] += len(session['memory_points'])
            summary['interference_memories'] += sum(m['memory_source'] == 'interference' for m in session['memory_points'])
            summary['extracted_memories'] += len(session['extracted_memories'])
            user['sessions'].append(session)
        users.append(user)
    require(used == set(indexed), 'unused or mismatched records')
    summary['users'] = len(users)
    return users, summary


def write_bundle(target, users, summary):
    target.mkdir(parents=True, exist_ok=False)
    dest = target / 'results/memzero-development'
    dest.mkdir(parents=True)
    input_file = dest / 'memzero_eval_results.jsonl'
    with input_file.open('x', encoding='utf-8') as f:
        for user in users:
            f.write(json.dumps(user, ensure_ascii=False) + '\n')
    summary = dict(summary, input_sha256=sha(input_file))
    (target / 'input_manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new output directory')
    parser.add_argument('--run-official', action='store_true', help='run original official scorer; makes model API calls')
    args = parser.parse_args()
    users, summary = build_inputs()
    output = args.output.resolve()
    write_bundle(output, users, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    if args.run_official:
        subprocess.run([sys.executable, str(OFFICIAL), '--frame', 'memzero', '--version', 'development'], cwd=output, check=True)


if __name__ == '__main__':
    main()
