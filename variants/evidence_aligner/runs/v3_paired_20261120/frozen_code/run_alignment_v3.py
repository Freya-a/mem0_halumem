"""Replay the exact saved v1/v2 inputs once each using the v3 prompt."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import time

from aligner_v3 import MODEL, PROMPT_FILE, PROMPT_VERSION, align_evidence_v3, build_messages
from qwen_backend import QwenBackend
from run_alignment_trial import CASE_NAMES, HERE, _read, _save
from run_alignment_v2 import V1_RUN, _bytes_hash, _json_hash, get_usage

V2_RUN = HERE / 'runs' / 'v2_paired_20261120'
DEFAULT_RUN = HERE / 'runs' / 'v3_paired_20261120'
SETTINGS = {'model': MODEL, 'temperature': 0, 'response_format': {'type': 'json_object'},
            'max_tokens': 8192, 'automatic_retries': 0}


def verify_pair(v1, v2, candidate):
    """Compare both historical inputs, the live input, and all exact user-message bytes."""
    originals = {'v1': v1, 'v2': v2}
    checks = {}
    for version, artifact in originals.items():
        req = artifact['request']
        if any(req.get(key) != value for key, value in SETTINGS.items()):
            raise ValueError(f'{version} request settings differ from v3')
        checks[version + '_input_sha256'] = _json_hash(artifact['input'])
        checks[version + '_user_content_sha256'] = _bytes_hash(req['messages'][1]['content'].encode('utf-8'))
    checks['v3_input_sha256'] = _json_hash(candidate)
    live_user = build_messages(candidate['old_units'], candidate['new_units'], candidate['source_texts'])[1]['content']
    checks['v3_user_content_sha256'] = _bytes_hash(live_user.encode('utf-8'))
    checks['components'] = {}
    for key in ('old_units', 'new_units', 'source_texts'):
        hashes = {version + '_sha256': _json_hash(artifact['input'][key]) for version, artifact in originals.items()}
        hashes['v3_sha256'] = _json_hash(candidate[key])
        hashes['equal'] = len(set(hashes.values())) == 1
        checks['components'][key] = hashes
    checks['old_unit_ids'] = [u['unit_id'] for u in candidate['old_units']]
    checks['new_unit_ids'] = [u['unit_id'] for u in candidate['new_units']]
    checks['all_equal'] = (len({checks[v + '_input_sha256'] for v in ('v1', 'v2', 'v3')}) == 1
                           and len({checks[v + '_user_content_sha256'] for v in ('v1', 'v2', 'v3')}) == 1
                           and all(x['equal'] for x in checks['components'].values()))
    if not checks['all_equal']:
        raise ValueError('v1/v2/v3 input or exact user message differs')
    return checks


def load_paired_cases():
    for run in (V1_RUN, V2_RUN):
        manifest = _read(run / 'manifest.json')
        if manifest['request_attempts'] != 5 or manifest['model_responses'] != 5:
            raise ValueError(f'incomplete historical run: {run}')
    pairs = []
    for name in CASE_NAMES:
        paths = [run / (name + '.json') for run in (V1_RUN, V2_RUN)]
        v1, v2 = [_read(path) for path in paths]
        case = v1['input']
        if case.get('case_id') != name or v2['input'].get('case_id') != name:
            raise ValueError('case ID differs from saved case')
        checks = verify_pair(v1, v2, case)
        checks['v1_artifact_sha256'], checks['v2_artifact_sha256'] = [_bytes_hash(p.read_bytes()) for p in paths]
        pairs.append({'input': case, 'v1': v1, 'v2': v2, 'input_validation': checks})
    return pairs


def run_paired(pairs, run_dir, *, backend_factory=QwenBackend):
    if [pair['input']['case_id'] for pair in pairs] != list(CASE_NAMES):
        raise ValueError('exactly the five fixed cases in order are required')
    for pair in pairs:
        checks = verify_pair(pair['v1'], pair['v2'], pair['input'])
        if any(checks[key] != pair['input_validation'][key] for key in checks):
            raise ValueError('input differs from preflight')
    run = Path(run_dir).resolve()
    run.mkdir(mode=0o700, parents=True, exist_ok=False)
    frozen = run / 'frozen_code'
    frozen.mkdir()
    for filename in ('aligner_v3.py', 'aligner_v2.py', 'aligner.py', 'qwen_backend.py',
                     'run_alignment_v3.py', 'run_alignment_v2.py', 'run_alignment_trial.py'):
        shutil.copy2(HERE / filename, frozen / filename)
    (frozen / 'prompts').mkdir()
    shutil.copy2(PROMPT_FILE, frozen / 'prompts' / PROMPT_FILE.name)
    prompt_sha = _bytes_hash(PROMPT_FILE.read_bytes())
    manifest = {'prompt_version': PROMPT_VERSION, 'prompt_sha256': prompt_sha, **SETTINGS,
                'maximum_requests': 5, 'http_redirects': False, 'trust_env': False,
                'request_attempts': 0, 'model_responses': 0, 'status': 'preparing',
                'v1_run': str(V1_RUN.relative_to(HERE)), 'v2_run': str(V2_RUN.relative_to(HERE)),
                'cases': [{'case_id': p['input']['case_id'], 'status': 'not_started'} for p in pairs]}
    _save(run / 'manifest.json', manifest)
    for pair in pairs:
        case = pair['input']
        messages = build_messages(case['old_units'], case['new_units'], case['source_texts'])
        artifact = {'input': case, 'input_validation': pair['input_validation'],
                    'request': {**SETTINGS, 'prompt_version': PROMPT_VERSION, 'prompt_sha256': prompt_sha,
                                'messages': messages},
                    'call': {'status': 'not_started', 'attempts': 0}, 'usage': None,
                    'raw_response': None, 'provider_response': None, 'result': None}
        _save(run / (case['case_id'] + '.json'), artifact)
    try:
        backend = backend_factory()
    except Exception as exc:
        manifest.update(status='configuration_error', error={'type': type(exc).__name__})
        _save(run / 'manifest.json', manifest)
        raise
    manifest['status'] = 'running'
    _save(run / 'manifest.json', manifest)
    try:
        for i, pair in enumerate(pairs):
            case = pair['input']
            path = run / (case['case_id'] + '.json')
            artifact = _read(path)
            checks = verify_pair(pair['v1'], pair['v2'], artifact['input'])
            if any(checks[key] != pair['input_validation'][key] for key in checks):
                raise ValueError('stored input differs from preflight')
            for version, base in (('v1', V1_RUN), ('v2', V2_RUN)):
                if _bytes_hash((base / path.name).read_bytes()) != pair['input_validation'][version + '_artifact_sha256']:
                    raise ValueError(f'{version} artifact changed after preflight')
            if checks['v3_user_content_sha256'] != _bytes_hash(artifact['request']['messages'][1]['content'].encode('utf-8')):
                raise ValueError('stored user message differs from verified paired input')
            backend.provider_response = None
            artifact['call'].update(status='started', attempts=1, request_transmitted='unknown')
            manifest['request_attempts'] += 1
            manifest['cases'][i].update(status='started', attempts=1, file=path.name)
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            def checked_backend(messages):
                if messages != artifact['request']['messages']:
                    raise ValueError('live messages differ from saved request')
                return backend(messages)
            started = time.monotonic()
            result = align_evidence_v3(case['old_units'], case['new_units'], case['source_texts'], backend=checked_backend)
            elapsed = round(time.monotonic() - started, 3)
            usage = get_usage(backend.provider_response)
            artifact.update(raw_response=result.get('raw_response'), provider_response=backend.provider_response,
                            usage=usage, result=result)
            artifact['call'].update(status=result['status'], elapsed_seconds=elapsed,
                                    returned_model=result.get('returned_model'),
                                    request_transmitted=True if backend.provider_response is not None else 'unknown')
            if backend.provider_response is not None:
                manifest['model_responses'] += 1
            manifest['cases'][i].update(status=result['status'], elapsed_seconds=elapsed,
                                        returned_model=result.get('returned_model'), usage=usage,
                                        parse_error_count=len(result.get('parse_errors', [])),
                                        structure_error_count=len(result.get('structure_errors', [])),
                                        coverage=result.get('coverage'))
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            print(f"{case['case_id']}: {result['status']}; {elapsed}s", flush=True)
            if result['status'] == 'request_error':
                manifest['status'] = 'stopped_request_error'
                break
            if result.get('returned_model') != MODEL:
                manifest['status'] = 'stopped_model_mismatch'
                break
        else:
            manifest['status'] = 'completed'
    finally:
        backend.close()
        _save(run / 'manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--run-dir', type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    pairs = load_paired_cases()
    if args.preflight:
        print(json.dumps({'prompt_version': PROMPT_VERSION, 'prompt_sha256': _bytes_hash(PROMPT_FILE.read_bytes()),
                          'request_attempts': 0,
                          'cases': [{'case_id': p['input']['case_id'], **p['input_validation']} for p in pairs]},
                         ensure_ascii=False, indent=2))
        return
    run_paired(pairs, args.run_dir)


if __name__ == '__main__':
    main()
