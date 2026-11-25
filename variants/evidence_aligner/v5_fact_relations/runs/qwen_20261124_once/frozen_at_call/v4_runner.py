"""Persist one request per case; no retries and no overwrite/resume of a run."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
ALIGNER = HERE.parent
PROJECT = HERE.parents[2]
CASE_NAMES = ('susan', 'promotion', 'career_history', 'transition', 'skydiving')
MODEL = 'qwen-plus-2025-12-01'
SETTINGS = {'model': MODEL, 'temperature': 0, 'response_format': {'type': 'json_object'},
            'max_tokens': 8192, 'automatic_retries': 0}


def _json_bytes(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def _save(path, value):
    """Atomically persist each transition before any irreversible request."""
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _safe_error(exc):
    result = {'type': type(exc).__name__}
    status = getattr(exc, 'status_code', None)
    if isinstance(status, int):
        result['http_status'] = status
    code = getattr(exc, 'code', None)
    if isinstance(code, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', code):
        result['provider_error_code'] = code
    return result


def run_cases(cases, run_dir, *, prepare, analyze, backend_factory, system_prompt):
    """Execute exactly one call for each fixed case, handling each failure separately.

    ``prepare`` is pure and must not call a model; ``analyze(payload, parsed)``
    performs offline validation and planning. backend_factory creates a backend
    with one-call semantics, no retries, and a ``provider_response`` attribute.
    An existing directory is never resumed: an interrupted attempt must never be
    resent automatically. Each request is marked attempted and fsynced first.
    """
    names = [c.get('input', {}).get('case_id') for c in cases]
    if names != list(CASE_NAMES):
        raise ValueError('exactly five fixed case IDs in fixed order are required')
    if not isinstance(system_prompt, str) or not system_prompt.strip():
        raise ValueError('system prompt required')
    prepared = []
    for case in cases:
        payload = prepare(case)
        messages = [{'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, indent=2)}]
        prepared.append((payload, messages))
    run = Path(run_dir).resolve()
    run.mkdir(mode=0o700, parents=True, exist_ok=False)
    prompt_hash = hashlib.sha256(system_prompt.encode('utf-8')).hexdigest()
    manifest = {**SETTINGS, 'maximum_requests': len(CASE_NAMES), 'request_attempts': 0,
                'model_responses': 0, 'status': 'preparing', 'prompt_sha256': prompt_hash,
                'cases': [{'case_id': name, 'status': 'not_started', 'attempts': 0} for name in CASE_NAMES]}
    _save(run / 'manifest.json', manifest)
    for i, name in enumerate(CASE_NAMES):
        payload, messages = prepared[i]
        request = {**SETTINGS, 'messages': messages}
        request['sha256'] = hashlib.sha256(_json_bytes(request)).hexdigest()
        request['messages_sha256'] = hashlib.sha256(_json_bytes(messages)).hexdigest()
        _save(run / f'{name}.json', {'case_id': name, 'prepared_input': payload, 'request': request,
              'call': {'status': 'not_started', 'attempts': 0, 'request_transmitted': False},
              'usage': None, 'raw_response': None, 'provider_response': None, 'result': None})
    try:
        backend = backend_factory()
    except Exception as exc:
        manifest.update(status='configuration_error', error=_safe_error(exc))
        _save(run / 'manifest.json', manifest)
        raise
    manifest['status'] = 'running'
    _save(run / 'manifest.json', manifest)
    try:
        for i, name in enumerate(CASE_NAMES):
            path = run / f'{name}.json'
            artifact = json.loads(path.read_text(encoding='utf-8'))
            messages = artifact['request']['messages']
            request_fields = {k: v for k, v in artifact['request'].items() if k not in ('sha256', 'messages_sha256')}
            if (hashlib.sha256(_json_bytes(request_fields)).hexdigest() != artifact['request']['sha256']
                    or hashlib.sha256(_json_bytes(messages)).hexdigest() != artifact['request']['messages_sha256']):
                raise RuntimeError('prepared request changed before dispatch')
            backend.provider_response = None
            artifact['call'].update(status='started', attempts=1, request_transmitted='unknown')
            manifest['request_attempts'] += 1
            manifest['cases'][i].update(status='started', attempts=1)
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            started = time.monotonic()
            try:
                reply = backend(messages)  # The only network attempt for this case.
            except Exception as exc:
                elapsed = round(time.monotonic() - started, 3)
                provider = backend.provider_response
                http_response = getattr(exc, 'response', None)
                if isinstance(provider, dict):
                    manifest['model_responses'] += 1
                    artifact['provider_response'] = provider
                    if isinstance(provider.get('usage'), dict):
                        artifact['usage'] = provider['usage']
                    choices = provider.get('choices')
                    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
                        msg = choices[0].get('message')
                        if isinstance(msg, dict) and isinstance(msg.get('content'), str):
                            artifact['raw_response'] = msg['content']
                    artifact['call']['request_transmitted'] = True
                elif http_response is not None:
                    try:
                        body = http_response.text
                    except Exception:
                        body = None
                    if isinstance(body, str):
                        artifact['raw_response'] = body
                    artifact['call']['request_transmitted'] = True
                artifact['call'].update(status='request_error', elapsed_seconds=elapsed, error=_safe_error(exc))
                manifest['cases'][i].update(status='request_error', elapsed_seconds=elapsed, error=_safe_error(exc),
                                            usage=artifact['usage'])
                _save(path, artifact)
                _save(run / 'manifest.json', manifest)
                continue
            elapsed = round(time.monotonic() - started, 3)
            provider = backend.provider_response
            if isinstance(provider, dict):
                manifest['model_responses'] += 1
            usage = provider.get('usage') if isinstance(provider, dict) and isinstance(provider.get('usage'), dict) else None
            raw = reply.get('content') if isinstance(reply, dict) else None
            model = reply.get('model') if isinstance(reply, dict) else None
            artifact.update(raw_response=raw, provider_response=provider, usage=usage)
            artifact['call'].update(status='response_received', elapsed_seconds=elapsed, returned_model=model,
                                    finish_reason=reply.get('finish_reason') if isinstance(reply, dict) else None,
                                    request_transmitted=True if provider is not None else 'unknown')
            # Persist the provider reply before parsing/validation: a later
            # failure or process termination must never erase a paid response.
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            try:
                if model != MODEL:
                    status, result = 'model_mismatch', None
                else:
                    try:
                        parsed = json.loads(raw)
                        if not isinstance(parsed, dict):
                            raise TypeError('top-level JSON must be an object')
                    except (TypeError, ValueError):
                        status, result = 'parse_error', None
                    else:
                        result = analyze(prepared[i][0], parsed)
                        status = result.get('status', 'validation_error') if isinstance(result, dict) else 'validation_error'
            except Exception as exc:
                status, result = 'analysis_error', {'error': _safe_error(exc)}
            artifact['call']['status'] = status
            artifact['result'] = result
            manifest['cases'][i].update(status=status, elapsed_seconds=elapsed, returned_model=model, usage=usage)
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            print(f'{name}: {status}; {elapsed}s', flush=True)
        manifest['status'] = 'completed'
    finally:
        try:
            backend.close()
        finally:
            _save(run / 'manifest.json', manifest)
    return manifest


def load_fixed_cases():
    run = ALIGNER / 'runs' / 'fixed_five_20261120'
    return [json.loads((run / f'{name}.json').read_text(encoding='utf-8')) for name in CASE_NAMES]


def main():
    parser = argparse.ArgumentParser(description='One-shot evidence alignment trial')
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='make exactly one model request per case')
    args = parser.parse_args()
    import interface
    prompt = (HERE / 'prompt.txt').read_text(encoding='utf-8')
    cases = load_fixed_cases()
    if not args.execute:
        for case in cases:
            interface.prepare_input(case)
        print(json.dumps({'status': 'offline_preflight', 'cases': list(CASE_NAMES), 'attempts': 0}))
        return
    sys.path.insert(0, str(ALIGNER))
    from qwen_backend import QwenBackend
    planner_path = PROJECT / 'variants/evidence_scope_planner/v2_offline/scope_planner.py'
    spec = importlib.util.spec_from_file_location('v2_offline_scope_planner', planner_path)
    planner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(planner)

    def analyze(payload, parsed):
        validation = interface.validate_output(parsed, payload)
        args = interface.planner_inputs(payload, parsed)
        plan = planner.build_scope_plan(*args)
        return {'status': validation['status'], 'validation': validation, 'parsed': parsed, 'plan': plan}

    run_cases(cases, args.run_dir, prepare=interface.prepare_input, analyze=analyze,
              backend_factory=QwenBackend, system_prompt=prompt)


if __name__ == '__main__':
    main()
