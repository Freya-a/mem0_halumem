"""Five one-shot v5 calls; historical v4 is copied, never requested again."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE))
from real_backend import OpenAICompatibleBackend, load_model_settings
from splitter import ValidationError, _read_json, split_memory

CASE_IDS = ['case_10_sports_preferences', 'case_11_persian_care',
            'case_09_father_profile', 'case_03_assistant_yoga', 'case_08_partner_profile']


def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, content):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(content)


def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def execute_case(root, case_id, input_bytes, prompt, settings,
                 backend_factory=OpenAICompatibleBackend):
    directory = root / 'runs' / case_id / 'v5'
    directory.mkdir(parents=True, exist_ok=False)
    (directory / 'input.json').write_bytes(input_bytes)
    request = _read_json(directory / 'input.json')
    write(directory / 'prompt.txt', prompt)
    save(directory / 'attempt.json', {
        'case_id': case_id, 'version': 'v5', 'started_at': now(), 'model': settings.model,
        'max_model_calls': 1, 'sdk_max_retries': 0, 'http_follow_redirects': False,
        'generation_parameters': settings.generation, 'response_format': {'type': 'json_object'},
        'timeout_seconds': settings.timeout, 'prompt_sha256': sha(prompt.encode()),
        'input_sha256': sha(input_bytes),
    })
    backend, result, failure = None, None, None
    try:
        backend = backend_factory(settings, prompt)
        result = split_memory(request, backend)
    except ValidationError as error:
        failure = error.as_dict()
    finally:
        if backend is not None:
            backend.close()
    calls = backend.call_count if backend is not None else 0
    assert calls <= 1
    if backend is not None and isinstance(backend.raw_content, str):
        # Never silently modify actual model content to make a candidate pass.
        # Credential echo aborts artifact persistence rather than exposing it.
        if settings.api_key in backend.raw_content:
            raise RuntimeError('Sensitive echo detected; no response content printed or persisted.')
        write(directory / 'raw_content.txt', backend.raw_content)
    save(directory / 'response_metadata.json', backend.response_metadata if backend is not None else {})
    report = {
        'case_id': case_id, 'version': 'v5', 'finished_at': now(), 'model': settings.model,
        'model_call_attempts': calls, 'sdk_max_retries': 0, 'http_follow_redirects': False,
        'automatic_check': 'passed' if result is not None else 'failed', 'error': failure,
        'validation_scope': 'schema, input identity and literal evidence quotes only',
        'semantic_review': 'not determined by program', 'response_repaired': False,
    }
    if result is not None:
        save(directory / 'result.json', result)
    save(directory / 'report.json', report)
    return report


def main():
    selected = _read_json(ROOT / 'selection.json')['cases']
    assert [c['case_id'] for c in selected] == CASE_IDS
    revision = _read_json(BASE / 'prompt_versions/v5_granularity_relations_20261104/revision.json')
    prompt_bytes = (ROOT / 'prompts/v5.txt').read_bytes()
    assert sha(prompt_bytes) == revision['prompt_sha256']
    assert prompt_bytes == (BASE / 'prompt_versions/v5_granularity_relations_20261104/prompt.txt').read_bytes()
    prompt = prompt_bytes.decode('utf-8')
    for name, expected in _read_json(ROOT / 'source_integrity.before.json').items():
        assert sha(Path(name).read_bytes()) == expected, name
    for case in selected:
        assert sha((ROOT / 'inputs' / (case['case_id'] + '.json')).read_bytes()) == case['input_sha256']
    settings = load_model_settings(BASE.parent.parent / '.env.local')
    assert settings.model == 'qwen-plus'
    assert settings.generation == {} and settings.timeout == 180.0
    save(ROOT / 'batch_attempt.json', {
        'started_at': now(), 'max_calls_total': 5, 'max_calls_each': 1,
        'order': CASE_IDS, 'new_v4_calls': 0, 'prompt_sha256': sha(prompt_bytes),
        'model': settings.model, 'generation_parameters': settings.generation,
        'timeout_seconds': settings.timeout, 'sdk_max_retries': 0, 'http_follow_redirects': False,
        'response_format': {'type': 'json_object'},
        'configuration_names_and_sources': settings.provenance,
        'unknown_service_parameters': ['default sampling parameters', 'concrete model revision', 'provider routing'],
        'request_contents': 'Frozen v5 prompt + identical historical input JSON only; no reviews or target evidence.',
        'evaluation_limit': 'Five previously reviewed design-informed regression cases; not independent generalization.',
    })
    journal = ROOT / 'call_journal.jsonl'
    with journal.open('x', encoding='utf-8'):
        pass
    reports = []
    for position, case in enumerate(selected, 1):
        case_id = case['case_id']
        assert sha((ROOT / 'prompts/v5.txt').read_bytes()) == revision['prompt_sha256']
        data = (ROOT / 'inputs' / (case_id + '.json')).read_bytes()
        assert sha(data) == case['input_sha256']
        with journal.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'event': 'starting', 'position': position,
                                     'case_id': case_id, 'at': now()}) + '\n')
            stream.flush()
        report = execute_case(ROOT, case_id, data, prompt, settings)
        reports.append(report)
        with journal.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps({'event': 'finished', 'position': position,
                'case_id': case_id, 'at': now(), 'calls': report['model_call_attempts'],
                'automatic_check': report['automatic_check']}) + '\n')
        print(json.dumps({'position': position, 'case_id': case_id,
                          'calls': report['model_call_attempts'], 'program': report['automatic_check']}), flush=True)
    save(ROOT / 'batch_completion.json', {
        'finished_at': now(), 'run_count': len(reports), 'actual_v5_calls': sum(r['model_call_attempts'] for r in reports),
        'actual_new_v4_calls': 0, 'retries': 0,
        'passed': sum(r['automatic_check'] == 'passed' for r in reports), 'reports': reports,
    })


if __name__ == '__main__':
    main()
