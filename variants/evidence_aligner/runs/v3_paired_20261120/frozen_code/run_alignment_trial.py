"""Five existing cases: preflight offline; one irreversible API attempt per case."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time

from aligner import MODEL, align_evidence, build_messages
from qwen_backend import QwenBackend

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = HERE.parent / 'evidence_relation_judge/runs/scope_positioning_20261118_v1/cases'
SIMPLEMEM = HERE.parent / 'simplemem_mem0_splitter/offline_entity_recheck_20261119/case_2.json'
CASE_NAMES = ['susan', 'promotion', 'career_history', 'transition', 'skydiving']
DEFAULT_RUN = HERE / 'runs/fixed_five_20261120'


def _read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path):
    return str(path.relative_to(ROOT))


def _save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def load_cases():
    cases = []
    for name in CASE_NAMES:
        path = PRIOR / name / 'input.json'
        prior = _read(path)
        request = prior['request']
        split = request['split_result']
        memory_id, memory_text = split['memory_id'], split['memory_text']
        if name == 'skydiving':
            sm = _read(SIMPLEMEM)
            checked = sm['rechecked_validation']
            if (sm['input']['memory_id'] != memory_id or sm['input']['memory_text'] != memory_text
                    or checked['status'] != 'passed'
                    or len(checked['validated_units']) != len(checked['parsed']['units'])):
                raise ValueError('SimpleMem result does not match skydiving old memory')
            old_units = checked['validated_units']
            old_origin = 'simplemem_prompt_v2'
            old_source_file, old_source_sha = _rel(SIMPLEMEM), _sha(SIMPLEMEM)
        else:
            old_units = []
            for unit in prior['manual_annotations']['old_units']:
                evidence = unit['attribute']['evidence']
                quotes = [q['quote'] for q in evidence if q['source_id'] == memory_id]
                old_units.append({'unit_id': unit['name'], 'raw_statement': unit['attribute']['value'],
                                  'source_id': memory_id, 'memory_quotes': quotes,
                                  'upstream_manual_unit': unit})
            old_origin = 'previous_manual_mapping'
            old_source_file, old_source_sha = _rel(path), _sha(path)

        selected = request['new_evidence']
        refs = {s['source_ref'].split('#')[0] for s in selected}
        if len(refs) != 1:
            raise ValueError(f'{name}: selected messages do not belong to one session')
        session_path = ROOT / next(iter(refs))
        session = _read(session_path)
        messages = [{'source_id': f'new-{i}', 'side': 'new', 'speaker': m['role'],
                     'text': m['content'], 'recorded_at': m.get('timestamp'),
                     'source_ref': f'{_rel(session_path)}#/raw_dialogue/{i}/content'}
                    for i, m in enumerate(session['raw_dialogue'])]
        message_map = {m['source_id']: m for m in messages}
        for source in selected:
            actual = message_map.get(source['source_id'])
            if (not actual or actual['text'] != source['text'] or actual['speaker'] != source['speaker']
                    or actual['recorded_at'] != source['recorded_at']):
                raise ValueError(f'{name}: selected message differs from original session')
        for context in request['source_context']:
            messages.append({**context, 'side': 'old'})

        # Keep the previous fixed manual new unit verbatim as metadata. It covers
        # only one selected source; expose the others as coarse, unsplit units.
        fixed = prior['manual_annotations']['new_unit']
        ev = fixed['attribute']['evidence']
        sids = {e['source_id'] for e in ev}
        if len(sids) != 1:
            raise ValueError(f'{name}: fixed new unit has multiple sources')
        sid = next(iter(sids))
        new_units = [{'unit_id': fixed['name'], 'source_id': sid,
                      'raw_statement': ' '.join(e['quote'] for e in ev),
                      'memory_quotes': [e['quote'] for e in ev], 'upstream_manual_unit': fixed}]
        for source in selected:
            if source['source_id'] != sid:
                new_units.append({'unit_id': 'unsplit-' + source['source_id'], 'source_id': source['source_id'],
                                  'raw_statement': source['text'], 'memory_quotes': [source['text']],
                                  'unit_origin': 'unsplit_selected_source'})
        sources = {'memory': {'source_id': memory_id, 'text': memory_text, 'speaker': 'memory',
                              'source_ref': prior['memory_snapshot']}, 'messages': messages}
        # This also fails before any model request on invalid IDs or upstream quotes.
        build_messages(old_units, new_units, sources)
        cases.append({'case_id': name, 'old_units': old_units, 'new_units': new_units, 'source_texts': sources,
                      'provenance': {'fixed_case_file': _rel(path), 'fixed_case_sha256': _sha(path),
                                     'old_unit_origin': old_origin, 'old_unit_source_file': old_source_file,
                                     'old_unit_source_sha256': old_source_sha,
                                     'new_unit_origin': 'previous_manual_mapping_plus_unsplit_selected_sources',
                                     'selected_new_source_ids': [s['source_id'] for s in selected],
                                     'full_session_file': _rel(session_path), 'full_session_sha256': _sha(session_path),
                                     'limitations': 'Only selected evidence has fixed/unsplit units; remaining session messages are context, not a new-unit split.'}})
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preflight', action='store_true', help='validate and describe inputs without any API request')
    parser.add_argument('--run-dir', type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    cases = load_cases()
    if args.preflight:
        print(json.dumps([{'case_id': c['case_id'], 'old_units': len(c['old_units']), 'new_units': len(c['new_units']),
                           'session_messages': sum(m['side'] == 'new' for m in c['source_texts']['messages']),
                           'old_unit_origin': c['provenance']['old_unit_origin']} for c in cases], ensure_ascii=False, indent=2))
        return
    run = args.run_dir.resolve()
    run.mkdir(mode=0o700, parents=True, exist_ok=False)
    manifest = {'model': MODEL, 'temperature': 0, 'response_format': {'type': 'json_object'},
                'maximum_requests': 5, 'automatic_retries': 0, 'http_redirects': False, 'trust_env': False,
                'request_attempts': 0, 'model_responses': 0, 'status': 'preparing',
                'cases': [{'case_id': c['case_id'], 'status': 'not_started'} for c in cases]}
    _save(run / 'manifest.json', manifest)
    for case in cases:
        messages = build_messages(case['old_units'], case['new_units'], case['source_texts'])
        artifact = {'input': case, 'request': {'model': MODEL, 'temperature': 0,
                    'response_format': {'type': 'json_object'}, 'max_tokens': 8192,
                    'automatic_retries': 0, 'messages': messages},
                    'call': {'status': 'not_started', 'attempts': 0},
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
        for i, case in enumerate(cases):
            path = run / (case['case_id'] + '.json')
            artifact = _read(path)
            backend.provider_response = None
            artifact['call'].update(status='started', attempts=1, request_transmitted='unknown')
            manifest['request_attempts'] += 1
            manifest['cases'][i].update(status='started', attempts=1, file=path.name)
            _save(path, artifact)
            _save(run / 'manifest.json', manifest)
            started = time.monotonic()
            result = align_evidence(case['old_units'], case['new_units'], case['source_texts'], backend=backend)
            elapsed = round(time.monotonic() - started, 3)
            artifact.update(raw_response=result.get('raw_response'), provider_response=backend.provider_response, result=result)
            artifact['call'].update(status=result['status'], elapsed_seconds=elapsed,
                                    returned_model=result.get('returned_model'),
                                    request_transmitted=True if backend.provider_response else 'unknown')
            if backend.provider_response is not None:
                manifest['model_responses'] += 1
            manifest['cases'][i].update(status=result['status'], elapsed_seconds=elapsed,
                                        returned_model=result.get('returned_model'),
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
