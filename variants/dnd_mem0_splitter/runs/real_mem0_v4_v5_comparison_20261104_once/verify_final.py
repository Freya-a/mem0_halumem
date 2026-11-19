"""Read-only final checks; writes only a new verification JSON in this run."""
from datetime import datetime
import hashlib
import html
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE))
from splitter import MockBackend, _read_json, split_memory, ValidationError


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before = _read_json(ROOT / 'source_integrity.before.json')
    changed = [name for name, digest in before.items() if not Path(name).is_file() or sha(Path(name)) != digest]
    assert not changed, changed
    selection = _read_json(ROOT / 'selection.json')['cases']
    completion = _read_json(ROOT / 'batch_completion.json')
    attempt = _read_json(ROOT / 'batch_attempt.json')
    revision_path = BASE / 'prompt_versions/v5_granularity_relations_20261104/revision.json'
    revision = _read_json(revision_path)
    prompt_path = ROOT / 'prompts/v5.txt'
    assert sha(prompt_path) == revision['prompt_sha256'] == attempt['prompt_sha256']
    assert prompt_path.read_bytes() == (revision_path.parent / 'prompt.txt').read_bytes()
    assert datetime.fromisoformat(revision['frozen_at']) < datetime.fromisoformat(attempt['started_at'])
    assert completion['actual_v5_calls'] == 5 and completion['actual_new_v4_calls'] == 0
    assert completion['retries'] == 0 and attempt['sdk_max_retries'] == 0
    assert attempt['http_follow_redirects'] is False
    events = [json.loads(line) for line in (ROOT / 'call_journal.jsonl').read_text().splitlines()]
    assert len(events) == 10
    assert sum(e.get('calls', 0) for e in events if e['event'] == 'finished') == 5
    data = _read_json(ROOT / 'comparison_data.json')['cases']
    reviews = _read_json(ROOT / 'semantic_reviews.json')['cases']
    markdown = (ROOT / 'COMPARISON_REPORT.md').read_text()
    cases, hashes, facts_reviewed, supports_reviewed = [], {}, 0, 0
    for selected, datum, reviewed in zip(selection, data, reviews):
        cid = selected['case_id']
        assert datum['case_id'] == reviewed['case_id'] == cid
        assert len([e for e in events if e['event'] == 'starting' and e['case_id'] == cid]) == 1
        assert len([e for e in events if e['event'] == 'finished' and e['case_id'] == cid]) == 1
        directory = ROOT / 'runs' / cid / 'v5'
        inp = _read_json(directory / 'input.json')
        assert inp == datum['input']
        assert (directory / 'input.json').read_bytes() == (ROOT / 'inputs' / (cid + '.json')).read_bytes()
        assert sha(directory / 'input.json') == selected['input_sha256']
        assert (directory / 'prompt.txt').read_bytes() == prompt_path.read_bytes()
        one_attempt = _read_json(directory / 'attempt.json')
        report = _read_json(directory / 'report.json')
        assert one_attempt['prompt_sha256'] == revision['prompt_sha256']
        assert report['model_call_attempts'] == 1 and report['sdk_max_retries'] == 0
        assert report['response_repaired'] is False
        assert _read_json(directory / 'raw_content.txt') == datum['v5_candidate']
        assert report == datum['v5_program_report']
        try:
            replay = split_memory(inp, MockBackend(datum['v5_candidate']))
        except ValidationError as error:
            assert report['automatic_check'] == 'failed'
            assert error.as_dict() == report['error']
            assert not (directory / 'result.json').exists()
        else:
            assert report['automatic_check'] == 'passed'
            assert replay == _read_json(directory / 'result.json')
        for name, provenance in selected['v4_artifacts'].items():
            assert sha(ROOT / 'baseline_v4' / cid / name) == provenance['sha256']
            assert sha(Path(provenance['source'])) == provenance['sha256']
        assert datum['v4'] == _read_json(ROOT / 'baseline_v4' / cid / 'raw_content.txt')
        for version, response in [('v4', datum['v4']), ('v5', datum['v5_candidate'])]:
            f_reviews = reviewed['versions'][version]['facts']
            assert len(f_reviews) == len(response['facts'])
            for fact, rv in zip(response['facts'], f_reviews):
                assert rv['actual_raw_subfact'] == fact['raw_subfact']
                assert rv['actual_contextualized_subfact'] == fact['contextualized_subfact']
                assert rv['model_pending_confirmations'] == fact['pending_confirmations']
                assert len(rv['supports']) == len(fact['evidence'])
                for e, er in zip(fact['evidence'], rv['supports']):
                    assert er['actual_evidence'] == e
                fields = [fact['raw_subfact'], fact['contextualized_subfact'],
                          json.dumps(fact['pending_confirmations'], ensure_ascii=False, indent=2)]
                fields += [e[k] for e in fact['evidence'] for k in ['quote', 'supports']]
                for field in fields:
                    escaped = html.escape(field, quote=False).replace('|', '&#124;').replace('\n', '<br>')
                    assert escaped in markdown, (cid, version, field)
                facts_reviewed += 1
                supports_reviewed += len(fact['evidence'])
        cases.append({'case_id': cid, 'v5_calls': 1, 'program': report['automatic_check'],
                      'candidate_facts': len(datum['v5_candidate']['facts']),
                      'accepted_result_exists': (directory / 'result.json').exists()})
        hashes[cid] = {'input_sha256': sha(directory / 'input.json'),
                       'v4_raw_sha256': sha(ROOT / 'baseline_v4' / cid / 'raw_content.txt'),
                       'v5_raw_sha256': sha(directory / 'raw_content.txt')}
    assert len(selection) == len(data) == len(reviews) == 5
    assert facts_reviewed == 22 and supports_reviewed == 41
    actual_files = {p for p in BASE.rglob('*') if p.is_file()}
    added = [p for p in actual_files if str(p) not in before]
    allowed_roots = [ROOT, revision_path.parent]
    assert all(any(p.is_relative_to(root) for root in allowed_roots) for p in added)
    result = {'checked_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'protected_existing_files': len(before), 'protected_unchanged': len(before) - len(changed),
        'protected_changed': changed, 'new_files_limited_to_two_new_directories': True,
        'v5_prompt_sha256': revision['prompt_sha256'], 'prompt_frozen_before_requests': True,
        'actual_v5_calls': 5, 'actual_new_v4_calls': 0, 'retries': 0,
        'cases': cases, 'exact_response_and_input_hashes': hashes,
        'reviewed_facts_including_rejected_candidates': facts_reviewed,
        'reviewed_supports_including_rejected_candidates': supports_reviewed,
        'comparison_preserves_all_actual_fields': True, 'offline_existing_unit_tests_passed': 38,
        'offline_new_invocation_tests_passed': 3, 'synthetic_examples_validated': 3,
        'offline_reporting_regression_tests_passed': 1,
        'scope': 'No Mem0 import/call or knowledge-base writes; no full development subset execution.',
        'semantic_status': 'AI preliminary review pending human confirmation; literal match is not semantic proof.',
        'design_protocol_hash_capture': 'Final hashes only; these documents were saved before requests, but no separate pre-request hash marker was recorded.',
        'design_sha256_final': sha(revision_path.parent / 'DESIGN.md'),
        'review_protocol_sha256_final': sha(ROOT / 'REVIEW_PROTOCOL.md')}
    with (ROOT / 'final_verification.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({k: result[k] for k in ['protected_unchanged', 'protected_changed', 'actual_v5_calls',
          'actual_new_v4_calls', 'retries', 'comparison_preserves_all_actual_fields']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
