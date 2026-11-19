#!/usr/bin/env python3
"""Execute at most one model request for each frozen v9 input; never retry."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
PROJECT = BASE.parents[1]
PRIOR = BASE / 'runs/v9_vs_v8_reviewed_20261118_01'
RUN = BASE / 'runs/v10_vs_v9_components_20261118_01'
sys.path.insert(0, str(BASE))
from real_backend import OpenAICompatibleBackend, load_model_settings
from splitter import ValidationError
import v10_splitter as v10


def sha(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()


def save(path, value):
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def main():
    prior_manifest = json.loads((PRIOR / 'manifest.json').read_text())
    prior_config = json.loads((PRIOR / 'configuration.json').read_text())
    settings = load_model_settings(PROJECT / '.env.local', environ={**os.environ, 'LLM_MODEL': v10.MODEL})
    settings.generation['extra_body'] = {'enable_thinking': False}
    if (settings.model != prior_config['model'] or settings.generation != prior_config['generation']
            or settings.timeout != prior_config['timeout_seconds'] or prior_config['sdk_max_retries'] != 0):
        raise RuntimeError('Current model settings differ from the recorded v9 configuration; no calls made.')
    prompt = v10.get_prompt()
    prompt_hash = sha(prompt.encode())
    old_prompt_hash = sha(v10.V9_PROMPT.read_bytes())
    if old_prompt_hash != prior_manifest['prompt_sha256']:
        raise RuntimeError('The v9 prompt differs from the recorded prompt; no calls made.')
    entries = []
    for case in prior_manifest['cases']:
        source = PRIOR / case['case']
        data = (source / 'input.json').read_bytes()
        if sha(data) != case['input_sha256']:
            raise RuntimeError('Input hash mismatch; no calls made.')
        entries.append({'case': case['case'], 'target': case['target'], 'input_sha256': sha(data),
                        'v9_result_sha256': sha((source / 'v9_result.json').read_bytes())})
    RUN.mkdir(exist_ok=False)
    (RUN / 'frozen_prompt.txt').write_text(prompt, encoding='utf-8')
    save(RUN / 'manifest.json', {'created_at': now(), 'model': settings.model, 'enable_thinking': False,
        'generation': settings.generation, 'timeout_seconds': settings.timeout, 'sdk_max_retries': 0,
        'max_calls_per_case': 1, 'prompt_sha256': prompt_hash, 'v9_prompt_sha256': old_prompt_hash,
        'v10_code_sha256': sha((HERE / 'v10_splitter.py').read_bytes()), 'cases': entries})
    reports = []
    for entry in entries:
        if sha(v10.get_prompt().encode()) != prompt_hash or sha((HERE / 'v10_splitter.py').read_bytes()) != json.loads((RUN / 'manifest.json').read_text())['v10_code_sha256']:
            save(RUN / 'stopped.json', {'reason': 'frozen_code_or_prompt_changed', 'completed': len(reports)})
            break
        case = entry['case']
        dest = RUN / case
        dest.mkdir()
        source = PRIOR / case
        (dest / 'input.json').write_bytes((source / 'input.json').read_bytes())
        (dest / 'v9_result.json').write_bytes((source / 'v9_result.json').read_bytes())
        (dest / 'provenance.json').write_bytes((source / 'provenance.json').read_bytes())
        request = json.loads((dest / 'input.json').read_text())
        save(dest / 'attempt.json', {'started_at': now(), 'prompt_sha256': prompt_hash, 'max_calls': 1})
        backends = []
        def factory(text):
            backend = OpenAICompatibleBackend(settings, text)
            backends.append(backend)
            def audit(http_request):
                body = json.loads(http_request.content)
                if (body['model'] != settings.model or body['enable_thinking'] is not False
                        or sha(body['messages'][0]['content'].encode()) != prompt_hash
                        or json.loads(body['messages'][1]['content']) != request):
                    raise ValueError('Request differs from frozen configuration.')
                save(dest / 'request_audit.json', {'observed_at': now(), 'model': body['model'],
                     'enable_thinking': body['enable_thinking'], 'prompt_sha256': prompt_hash,
                     'input_matches': True, 'response_format': body.get('response_format')})
            backend.client._client.event_hooks['request'].append(audit)
            return backend
        result, error = None, None
        try:
            result = v10.split_memory_v10(request, factory)
        except ValidationError as exc:
            error = exc.as_dict()
        except Exception as exc:
            error = {'code': 'unexpected_local_error', 'type': type(exc).__name__, 'message': 'Details hidden.'}
        backend = backends[0] if backends else None
        metadata = backend.response_metadata if backend else {}
        if backend and isinstance(backend.raw_content, str):
            (dest / 'raw_content.txt').write_text(backend.raw_content.replace(settings.api_key, '[REDACTED]'), encoding='utf-8')
        save(dest / 'response_metadata.json', metadata)
        if result is not None:
            save(dest / 'v10_result.json', result)
        report = {'case': case, 'reviewed_main_target': entry['target'], 'finished_at': now(),
                  'model_calls': backend.call_count if backend else 0, 'status': 'accepted' if result is not None else 'error',
                  'error': error, 'returned_model': metadata.get('returned_model'),
                  'request_audit_present': (dest / 'request_audit.json').exists()}
        save(dest / 'report.json', report)
        reports.append(report)
        print(json.dumps(report, ensure_ascii=False), flush=True)
        if error and (metadata.get('http_status') in (400, 401, 403, 404, 422) or not (dest / 'request_audit.json').exists()):
            save(RUN / 'stopped.json', {'reason': 'configuration_or_request_rejected', 'case': case, 'error': error})
            break
    save(RUN / 'batch_completion.json', {'finished_at': now(), 'completed_cases': len(reports),
        'calls': sum(row['model_calls'] for row in reports), 'reports': reports})


if __name__ == '__main__':
    main()
