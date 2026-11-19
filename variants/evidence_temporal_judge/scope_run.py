"""Prepare a reproducible three-case scope rerun; execute only with --execute."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

import judge_scope as scope

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
OLD = HERE / 'runs/scope_check_20261105_v1'
CASES = ('promotion', 'skydiving', 'career_history')
V4_SHA = 'd9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stamp(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def write(path, value):
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def prepare(root):
    root = Path(root)
    config = read(OLD / 'run_config.json')
    if config['prompt_sha256'] != V4_SHA:
        raise ValueError('old run does not record the expected v4 prompt')
    prepared = []
    for name in CASES:
        old = OLD / name
        inputs, split = read(old / 'model_input.json'), read(old / 'split_result.json')
        if split['prompt']['sha256'] != V4_SHA:
            raise ValueError('saved split lacks expected v4 provenance')
        request = inputs['split_request']
        contexts = scope.base._splitter._validate_request(request)
        scope.base._splitter._validate_response(split['result'], request, contexts)
        if len(split['result']['facts']) != 1:
            raise ValueError('unexpected fact count; refusing to expand call scope')
        scope.base._sources(inputs['new_evidence'])
        files = ('model_input.json', 'split_result.json', 'source_provenance.json', 'judge_result.json', 'candidate_stage.json')
        prepared.append((name, {f: (old / f).read_bytes() for f in files}))
    root.mkdir(parents=True, exist_ok=False)
    manifest = {'prepared_at': stamp(), 'source_run': str(OLD), 'v4_prompt_sha256': V4_SHA,
                'prompt_version': scope.PROMPT_VERSION, 'request_limit': 6, 'cases': {}}
    for name, files in prepared:
        folder = root / name; folder.mkdir()
        for filename, content in files.items():
            (folder / filename).write_bytes(content)
        manifest['cases'][name] = {filename: sha(folder / filename) for filename in files}
    write(root / 'prepared_manifest.json', manifest)
    write(root / 'prompts.json', {'version': scope.PROMPT_VERSION, 'fact': scope.FACT_PROMPT, 'candidate': scope.CANDIDATE_PROMPT})
    return manifest


def validate_prepared(root):
    manifest = read(root / 'prepared_manifest.json')
    if tuple(manifest['cases']) != CASES or manifest['v4_prompt_sha256'] != V4_SHA or manifest['request_limit'] != 6:
        raise ValueError('invalid prepared manifest')
    prompts = read(root / 'prompts.json')
    if prompts != {'version': scope.PROMPT_VERSION, 'fact': scope.FACT_PROMPT, 'candidate': scope.CANDIDATE_PROMPT}:
        raise ValueError('prepared prompts differ from implementation')
    for name in CASES:
        for filename, expected in manifest['cases'][name].items():
            if sha(root / name / filename) != expected or sha(OLD / name / filename) != expected:
                raise ValueError('prepared or original saved input differs')
    return manifest


def execute(root, invoke, config):
    root = Path(root)
    manifest = validate_prepared(root)
    with (root / 'RUN_STARTED').open('x', encoding='utf-8') as f: f.write(stamp() + '\n')
    write(root / 'run_config.json', {**config, 'started_at': stamp(), 'request_limit': 6,
          'prompt_version': scope.PROMPT_VERSION, 'v4_split_reused': True, 'v4_prompt_sha256': V4_SHA,
          'prompt_sha256': sha(root / 'prompts.json'), 'prepared_manifest_sha256': sha(root / 'prepared_manifest.json')})
    (root / 'calls').mkdir()
    count = 0
    def call(case, payload):
        nonlocal count
        if count >= 6: raise RuntimeError('request limit reached')
        count += 1
        payload = payload.copy(); prompt = payload.pop('prompt')
        folder = root / 'calls' / f'{count:02d}_{case}_{payload["task"]}'; folder.mkdir()
        write(folder / 'request.json', {'system_prompt': prompt, 'input': payload})
        with (root / 'call_journal.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps({'number': count, 'case': case, 'task': payload['task'], 'event': 'reserved', 'time': stamp()})+'\n'); f.flush(); os.fsync(f.fileno())
        value, info = invoke(prompt, payload)
        if info.get('raw') is not None: (folder / 'raw_content.txt').write_text(info['raw'], encoding='utf-8')
        write(folder / 'response_metadata.json', {k: v for k, v in info.items() if k != 'raw'})
        if info.get('error_type'):
            if info.get('error_code') in ('model_json_error', 'invalid_model_response', 'model_incomplete_response', 'empty_model_response', 'duplicate_json_key'):
                raise scope.BackendParseError()
            raise RuntimeError('model call failed')
        write(folder / 'parsed_response.json', value)
        return value
    for name in CASES:
        folder = root / name
        inputs, split = read(folder / 'model_input.json'), read(folder / 'split_result.json')
        result = scope.judge(split['result'], inputs['split_request']['source_context'], inputs['new_evidence'],
                             inputs['time_info'], lambda p: call(name, p), lambda p: call(name, p))
        write(folder / 'scope_result.json', result)
        write(folder / 'comparison.json', {'case': name, 'human_review_source_for_comparison_only': str(OLD / 'REPORT.md'),
              'v1': {'fact_judgments': read(folder / 'judge_result.json')['facts'], 'new_candidates': read(folder / 'candidate_stage.json')},
              'scope_v2': {'fact_judgments': result['facts'], 'new_candidates': result['new_candidates']},
              'semantic_review': 'pending_user_review'})
    metadata = list((root / 'calls').glob('*/response_metadata.json'))
    summary = {'finished_at': stamp(), 'reserved_count': count, 'actual_sdk_attempts': sum(bool(read(p).get('attempted')) for p in metadata),
               'ambiguous_attempts': count - len(metadata), 'request_limit': 6,
               'case_status': {name: {'facts': [f['status'] for f in read(root / name / 'scope_result.json')['facts']],
                                     'candidates': read(root / name / 'scope_result.json')['new_candidates']['status']} for name in CASES}}
    write(root / 'run_summary.json', summary)
    return summary


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('--prepare', '--execute'):
        print('Usage: scope_run.py --prepare|--execute RUN_DIR'); return 2
    root = Path(sys.argv[2]).resolve()
    if sys.argv[1] == '--prepare':
        prepare(root); print('Prepared offline; no model calls.'); return 0
    validate_prepared(root)
    sys.path.insert(0, str(scope.base.SPLITTER_DIR))
    from real_backend import load_model_settings, OpenAICompatibleBackend
    settings = load_model_settings(PROJECT / '.env.local')
    def invoke(prompt, payload):
        backend = None
        try:
            backend = OpenAICompatibleBackend(settings, prompt)
            value = backend(payload)
            return value, {'attempted': bool(backend.call_count), 'metadata': backend.response_metadata,
                           'raw': backend.raw_content.replace(settings.api_key, '[REDACTED]') if isinstance(backend.raw_content, str) else None}
        except Exception as exc:
            return None, {'attempted': bool(backend and backend.call_count), 'error_type': type(exc).__name__,
                          'error_code': getattr(exc, 'code', None), 'metadata': backend.response_metadata if backend else {},
                          'raw': backend.raw_content.replace(settings.api_key, '[REDACTED]') if backend and isinstance(backend.raw_content, str) else None}
        finally:
            if backend: backend.close()
    config = {'model': settings.model, 'generation_parameters': settings.generation, 'timeout_seconds': settings.timeout,
              'sdk_max_retries': 0, 'http_follow_redirects': False, 'endpoint_host': urlsplit(settings.base_url).hostname,
              'settings_sources': settings.provenance}
    print(json.dumps(execute(root, invoke, config), ensure_ascii=False)); return 0


if __name__ == '__main__': raise SystemExit(main())
