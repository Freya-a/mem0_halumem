"""One call per frozen development memory; no retry or response repair."""
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
HISTORY = ROOT.parent / 'real_mem0_v3_v4_comparison_20261104_once'
V6 = BASE / 'prompt_versions/v6_dnd_paper_aligned'
sys.path.insert(0, str(BASE))
from splitter import ValidationError, _read_json
from real_backend import OpenAICompatibleBackend, load_model_settings
spec = importlib.util.spec_from_file_location('v6_real_dev', V6 / 'v6_splitter.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

CASES = ['case_01_multi_person', 'case_03_assistant_yoga', 'case_04_negative_relative',
         'case_05_relative_time', 'case_06_plan_possibility', 'case_08_partner_profile',
         'case_10_sports_preferences', 'case_11_persian_care']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()

def main():
    # This exclusive marker also prevents accidental repeat calls after interruption.
    with (ROOT / 'started.marker').open('x', encoding='utf-8') as stream:
        stream.write(now() + '\n')
    prompt = (V6 / 'prompt.txt').read_bytes()
    with (ROOT / 'frozen_prompt.txt').open('xb') as stream:
        stream.write(prompt)
    known = {c['case_id']: c for c in _read_json(HISTORY / 'selection.json')['cases']}
    for case in CASES:
        source = HISTORY / 'inputs' / (case + '.json')
        data = source.read_bytes()
        if sha(data) != known[case]['input_sha256']:
            raise RuntimeError('Input hash mismatch: ' + case)
    settings = load_model_settings(BASE.parent.parent / '.env.local')
    save(ROOT / 'attempt.json', {'started_at': now(), 'cases': CASES,
        'model': settings.model, 'generation_parameters': settings.generation,
        'timeout_seconds': settings.timeout, 'sdk_max_retries': 0,
        'prompt_sha256': sha(prompt), 'max_calls_each': 1,
        'provider_defaults_and_model_revision': 'unknown',
        'input_source': str(HISTORY / 'inputs'), 'target_session_new_evidence_sent': False})
    reports = []
    for case in CASES:
        if sha((V6 / 'prompt.txt').read_bytes()) != sha(prompt):
            raise RuntimeError('v6 prompt changed during experiment')
        directory = ROOT / case
        directory.mkdir()
        source = HISTORY / 'inputs' / (case + '.json')
        data = source.read_bytes()
        with (directory / 'input.json').open('xb') as stream:
            stream.write(data)
        request = _read_json(directory / 'input.json')
        save(directory / 'attempt.json', {'case_id': case, 'input_sha256': sha(data),
                                         'prompt_sha256': sha(prompt), 'started_at': now()})
        holder = []
        def factory(text):
            backend = OpenAICompatibleBackend(settings, text)
            holder.append(backend)
            return backend
        result, failure = None, None
        try:
            result = module.split_memory_v6(request, factory)
        except ValidationError as error:
            failure = error.as_dict()
        backend = holder[0] if holder else None
        if backend and isinstance(backend.raw_content, str):
            with (directory / 'raw_content.txt').open('x', encoding='utf-8') as stream:
                stream.write(backend.raw_content.replace(settings.api_key, '[REDACTED]'))
        save(directory / 'response_metadata.json', backend.response_metadata if backend else {})
        if result is not None:
            save(directory / 'result.json', result)
        report = {'case_id': case, 'finished_at': now(), 'model_calls': backend.call_count if backend else 0,
                  'program_status': 'passed' if result is not None else 'failed',
                  'fact_count': len(result['facts']) if result is not None else None,
                  'error': failure, 'semantic_status': 'not evaluated by program'}
        save(directory / 'report.json', report)
        reports.append(report)
        print(json.dumps(report, ensure_ascii=False), flush=True)
    save(ROOT / 'batch_completion.json', {'finished_at': now(), 'reports': reports,
        'total': len(reports), 'calls': sum(r['model_calls'] for r in reports),
        'passed': sum(r['program_status'] == 'passed' for r in reports)})

if __name__ == '__main__':
    main()
