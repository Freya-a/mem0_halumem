"""Replay the five saved v1 inputs exactly once each with the v2 prompt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import time

from aligner_v2 import MODEL, PROMPT_FILE, PROMPT_VERSION, align_evidence_v2, build_messages
from qwen_backend import QwenBackend
from run_alignment_trial import CASE_NAMES, HERE, _read, _save

V1_RUN = HERE / 'runs' / 'fixed_five_20261120'
DEFAULT_RUN = HERE / 'runs' / 'v2_paired_20261120'


def _bytes_hash(value):
    return hashlib.sha256(value).hexdigest()


def _json_hash(value):
    return _bytes_hash(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                  separators=(',', ':')).encode('utf-8'))


def get_usage(provider_response):
    if isinstance(provider_response, dict) and isinstance(provider_response.get('usage'), dict):
        return provider_response['usage']
    return None


def verify_pair(v1, candidate):
    original = v1['input']
    components = {}
    for key in ('old_units', 'new_units', 'source_texts'):
        components[key] = {'v1_sha256': _json_hash(original[key]), 'v2_sha256': _json_hash(candidate[key])}
        components[key]['equal'] = components[key]['v1_sha256'] == components[key]['v2_sha256']
    v1_user = v1['request']['messages'][1]['content']
    v2_user = build_messages(candidate['old_units'], candidate['new_units'], candidate['source_texts'])[1]['content']
    checks = {'v1_input_sha256': _json_hash(original), 'v2_input_sha256': _json_hash(candidate),
              'v1_user_content_sha256': _bytes_hash(v1_user.encode('utf-8')),
              'v2_user_content_sha256': _bytes_hash(v2_user.encode('utf-8')),
              'components': components,
              'old_unit_ids': [u['unit_id'] for u in candidate['old_units']],
              'new_unit_ids': [u['unit_id'] for u in candidate['new_units']]}
    checks['all_equal'] = (checks['v1_input_sha256'] == checks['v2_input_sha256']
                           and checks['v1_user_content_sha256'] == checks['v2_user_content_sha256']
                           and all(c['equal'] for c in components.values()))
    if not checks['all_equal']:
        raise ValueError('v2 input or exact user message differs from saved v1 input')
    return checks


def load_paired_cases():
    manifest = _read(V1_RUN / 'manifest.json')
    if manifest['request_attempts'] != 5 or manifest['model_responses'] != 5:
        raise ValueError('v1 run is incomplete')
    cases = []
    for name in CASE_NAMES:
        path = V1_RUN / (name + '.json')
        original = _read(path)
        case = original['input']
        if case.get('case_id') != name:
            raise ValueError('case ID differs from saved v1 case')
        checks = verify_pair(original, case)
        checks['v1_artifact_sha256'] = _bytes_hash(path.read_bytes())
        cases.append({'input': case, 'v1': original, 'input_validation': checks})
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true')
    parser.add_argument('--run-dir', type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    cases = load_paired_cases()
    prompt_sha = _bytes_hash(PROMPT_FILE.read_bytes())
    if args.preflight:
        print(json.dumps({'prompt_version': PROMPT_VERSION, 'prompt_sha256': prompt_sha,
                          'request_attempts': 0,
                          'cases': [{'case_id': c['input']['case_id'], **c['input_validation']} for c in cases]},
                         ensure_ascii=False, indent=2))
        return
    run = args.run_dir.resolve()
    run.mkdir(mode=0o700, parents=True, exist_ok=False)
    frozen = run / 'frozen_code'
    frozen.mkdir()
    for filename in ('aligner_v2.py', 'aligner.py', 'qwen_backend.py', 'run_alignment_v2.py'):
        shutil.copy2(HERE / filename, frozen / filename)
    shutil.copy2(PROMPT_FILE, frozen / PROMPT_FILE.name)
    manifest = {'prompt_version': PROMPT_VERSION, 'prompt_sha256': prompt_sha,
                'model': MODEL, 'temperature': 0, 'response_format': {'type': 'json_object'},
                'max_tokens': 8192, 'maximum_requests': 5, 'automatic_retries': 0,
                'http_redirects': False, 'trust_env': False, 'request_attempts': 0,
                'model_responses': 0, 'status': 'preparing',
                'v1_run': str(V1_RUN.relative_to(HERE)),
                'cases': [{'case_id': c['input']['case_id'], 'status': 'not_started'} for c in cases]}
    _save(run / 'manifest.json', manifest)
    for pair in cases:
        case = pair['input']
        messages = build_messages(case['old_units'], case['new_units'], case['source_texts'])
        artifact = {'input': case, 'input_validation': pair['input_validation'],
                    'request': {'model': MODEL, 'prompt_version': PROMPT_VERSION, 'prompt_sha256': prompt_sha,
                                'temperature': 0, 'response_format': {'type': 'json_object'},
                                'max_tokens': 8192, 'automatic_retries': 0, 'messages': messages},
                    'call': {'status': 'not_started', 'attempts': 0}, 'usage': None,
                    'raw_response': None, 'provider_response': None, 'result': None}
        _save(run / (case['case_id'] + '.json'), artifact)
    try:
        backend = QwenBackend()
    except Exception as exc:
        manifest.update(status='configuration_error', error={'type': type(exc).__name__})
        _save(run / 'manifest.json', manifest)
        raise
    manifest['status'] = 'running'
    _save(run / 'manifest.json', manifest)
    try:
        for i, pair in enumerate(cases):
            case = pair['input']
            path = run / (case['case_id'] + '.json')
            artifact = _read(path)
            checks = verify_pair(pair['v1'], artifact['input'])
            if any(checks[key] != pair['input_validation'][key] for key in checks):
                raise ValueError('stored input checks differ from preflight')
            if _bytes_hash((V1_RUN / (case['case_id'] + '.json')).read_bytes()) != pair['input_validation']['v1_artifact_sha256']:
                raise ValueError('saved v1 artifact changed after preflight')
            if checks['v2_user_content_sha256'] != _bytes_hash(artifact['request']['messages'][1]['content'].encode('utf-8')):
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
            result = align_evidence_v2(case['old_units'], case['new_units'], case['source_texts'], backend=checked_backend)
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
                                        validation_error_count=len(result.get('validation_errors', [])),
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


if __name__ == '__main__':
    main()
