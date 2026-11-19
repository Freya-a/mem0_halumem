#!/usr/bin/env python3
"""Prepare a complete Medium run and explicitly invoke the official HaluMem scorer."""
from __future__ import annotations

import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import medium_full as baseline

ROOT = baseline.ROOT
OFFICIAL = ROOT / 'HaluMem/eval/evaluation.py'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def jsonl(path):
    with Path(path).open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]


def prepare_bundle(run, target, dataset):
    run, target, dataset = Path(run), Path(target), Path(dataset)
    if target.exists():
        raise FileExistsError(f'Evaluation directory already exists: {target}')
    status = baseline.read_json(run / 'status.json')
    config = baseline.read_json(run / 'run.json')
    require(status.get('status') == 'completed' and status.get('qa') is True and config.get('with_qa') is True,
            'Run must be complete and contain QA answers')
    require(baseline.digest(dataset) == config['dataset_sha256'], 'Dataset hash differs from the recorded run')
    require(baseline.digest(baseline.PROFILE) == config['profile_sha256'], 'Baseline profile changed since the run')
    require(isinstance(config.get('qa_settings'), dict), 'Run has no recorded QA configuration')
    sources = jsonl(dataset)
    inputs = jsonl(run / 'memzero_eval_results.jsonl')
    require(len(inputs) == len(sources) == status.get('users'), 'Incomplete user results')
    summary = {'users': len(sources), 'sessions': 0, 'questions': 0, 'updates': 0}
    for source, user in zip(sources, inputs):
        uid = source['uuid']
        require(user.get('uuid') == uid, 'User IDs or order do not match the dataset')
        require(len(source['sessions']) == len(user['sessions']), f'Incomplete sessions: {uid}')
        for index, (original, session) in enumerate(zip(source['sessions'], user['sessions']), 1):
            require(session.get('dialogue') == original['dialogue'], f'dialogue mismatch: {uid}:{index}')
            points = session.get('memory_points', [])
            questions = session.get('questions', [])
            require(len(points) == len(original.get('memory_points', [])), 'Memory point count mismatch')
            require(len(questions) == len(original.get('questions', [])), 'Question count mismatch')
            for actual, expected in zip(points, original.get('memory_points', [])):
                original_point = {k: v for k, v in actual.items() if k != 'memories_from_system'}
                require(original_point == expected, 'Reference memory point mismatch')
                if str(expected.get('is_update')) != 'False' and expected.get('original_memories'):
                    require(isinstance(actual.get('memories_from_system'), list), 'Missing update retrieval')
                    summary['updates'] += 1
            for actual, expected in zip(questions, original.get('questions', [])):
                require(isinstance(actual.get('system_response'), str) and bool(actual['system_response'].strip()),
                        f'Missing QA answer: {uid}:{index}')
                require(isinstance(actual.get('context'), str), 'Missing QA context')
                extras = {'system_response', 'context', 'search_duration_ms', 'response_duration_ms'}
                require({k: v for k, v in actual.items() if k not in extras} == expected, 'Question reference mismatch')
                summary['questions'] += 1
            result = session.get('mem0_add_result')
            require(isinstance(result, dict) and isinstance(result.get('results'), list), 'Missing native add result')
            require(session.get('extracted_memories') == [item['memory'] for item in result['results']],
                    'Extracted memories differ from native return')
            recorded = baseline.read_json(run / 'users' / uid / 'sessions' / f'{index:06d}.json')
            require(session == recorded, 'Consolidated output differs from session record')
            summary['sessions'] += 1
    require(not any((run / 'users').glob('*/incomplete.json')), 'Incomplete session marker exists')
    target.mkdir(parents=True, exist_ok=False, mode=0o700)
    destination = target / 'results/memzero-full/memzero_eval_results.jsonl'
    destination.parent.mkdir(parents=True)
    shutil.copyfile(run / 'memzero_eval_results.jsonl', destination)
    summary['input_sha256'] = baseline.digest(destination)
    summary['dataset_sha256'] = baseline.digest(dataset)
    summary['qa_settings'] = config['qa_settings']
    summary['official_source_sha256'] = {name: baseline.digest(ROOT / 'HaluMem/eval' / name)
                                          for name in ('evaluation.py', 'eval_tools.py', 'llms.py', 'prompts.py')}
    baseline.atomic_json(target / 'input_manifest.json', summary)
    return summary


def metric_rows(score):
    rows = []
    for label, group, key in (
        ('R', 'memory_integrity', 'recall'), ('Weighted R', 'memory_integrity', 'weighted_recall'),
        ('Target P', 'memory_accuracy', 'target_accuracy'), ('Acc.', 'memory_accuracy', 'weighted_accuracy'),
        ('FMR', 'memory_accuracy', 'interference_accuracy')):
        rows.append({'stage': 'memory_extraction', 'metric': label,
                     'all': score[group][key + '(all)'], 'valid': score[group][key + '(valid)']})
    rows.append({'stage': 'memory_extraction', 'metric': 'F1', 'all': score['memory_extraction_f1'], 'valid': None})
    for stage, suffix in (('memory_update', 'update_memory'), ('question_answering', 'qa')):
        for label, name in (('C', 'correct'), ('H', 'hallucination'), ('O', 'omission')):
            key = f'{name}_{suffix}_ratio'
            rows.append({'stage': stage, 'metric': label, 'all': score[stage][key + '(all)'],
                         'valid': score[stage][key + '(valid)']})
    return rows


def score_bundle(target, settings, resume=False):
    target = Path(target)
    manifest = baseline.read_json(target / 'input_manifest.json')
    official_input = target / 'results/memzero-full/memzero_eval_results.jsonl'
    require(baseline.digest(official_input) == manifest['input_sha256'], 'Official scorer input changed')
    for name, expected in manifest['official_source_sha256'].items():
        require(baseline.digest(ROOT / 'HaluMem/eval' / name) == expected, f'Official scorer changed: {name}')
    baseline.configure_qa(settings)
    os.environ.pop('OPENROUTER_API_KEY', None)
    config_file = target / 'score_config.json'
    record = {'input_sha256': manifest['input_sha256'], 'official_source_sha256': manifest['official_source_sha256'],
              'judge': {key: os.environ.get(key) for key in ('OPENAI_MODEL', 'OPENAI_BASE_URL', 'OPENAI_TEMPERATURE',
                  'OPENAI_MAX_TOKENS', 'OPENAI_TIMEOUT', 'RETRY_TIMES', 'WAIT_TIME_LOWER', 'WAIT_TIME_UPPER')}}
    require(record['judge'] == manifest['qa_settings'], 'QA and scoring model configuration differs from the run')
    if config_file.exists():
        require(resume, 'Existing scoring run requires --resume')
        require(baseline.read_json(config_file) == record, 'Scoring configuration changed; prepare a new bundle')
    else:
        require(not resume, 'No scoring run to resume')
        require(not (target / 'results/memzero-full/tmp2').exists(), 'Unexpected existing scoring cache')
        baseline.atomic_json(config_file, record)
    subprocess.run([sys.executable, str(OFFICIAL), '--frame', 'memzero', '--version', 'full'],
                   cwd=target, env=os.environ.copy(), check=True)
    scores_path = target / 'results/memzero-full/memzero_eval_stat_result.json'
    rows = metric_rows(baseline.read_json(scores_path)['overall_score'])
    out = target / 'metrics.csv'
    with out.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['stage', 'metric', 'all', 'valid'])
        writer.writeheader()
        writer.writerows(rows)
    baseline.atomic_json(target / 'scoring_status.json', {'status': 'completed', 'official_result_sha256': baseline.digest(scores_path)})
    print(f'Official score: {scores_path}\nMetric table: {out}', flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-id', required=True)
    p.add_argument('--env-file', default=str(ROOT / '.env.server.medium-full'))
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--score', action='store_true')
    p.add_argument('--resume', action='store_true')
    args = p.parse_args()
    require(bool(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}', args.run_id)), 'Invalid run ID')
    run = ROOT / 'results/medium_full' / args.run_id
    require(run.is_dir(), 'Full baseline run does not exist')
    target = run / 'halumem_evaluation'
    with (run / '.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.prepare:
            require(not args.resume, '--resume applies only to scoring')
            profile = baseline.read_json(baseline.PROFILE)
            summary = prepare_bundle(run, target, ROOT / profile['dataset'])
            print(f"Prepared {summary['users']} users, {summary['sessions']} sessions, {summary['questions']} answers; no model calls.")
            print(f'Official scorer input: {target / "results/memzero-full/memzero_eval_results.jsonl"}')
        else:
            settings = baseline.load_environment(args.env_file)
            score_bundle(target, settings, args.resume)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        message = str(exc)
        for name in ('DASHSCOPE_API_KEY', 'EMBEDDING_API_KEY', 'OPENAI_API_KEY'):
            secret = os.environ.get(name)
            if secret: message = message.replace(secret, '<redacted>')
        print(f'Evaluation stopped: {message}', file=sys.stderr, flush=True)
        sys.exit(1)
