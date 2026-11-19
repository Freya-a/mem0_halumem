"""Offline replay of saved v4/v5 responses; never invokes a real backend."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from splitter import MockBackend, ValidationError, _read_json, split_memory


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def main():
    completion = _read_json(ROOT / 'batch_completion.json')
    assert completion['actual_v5_calls'] == 5 and completion['actual_new_v4_calls'] == 0
    assert completion['retries'] == 0
    audits, quotes = [], []
    checks_dir = ROOT / 'program_checks'
    checks_dir.mkdir(exist_ok=False)
    for case in _read_json(ROOT / 'selection.json')['cases']:
        cid = case['case_id']
        for version in ['v4', 'v5']:
            directory = ROOT / 'baseline_v4' / cid if version == 'v4' else ROOT / 'runs' / cid / 'v5'
            request = _read_json(directory / 'input.json')
            report = _read_json(directory / 'report.json')
            candidate, replay, error = None, None, None
            try:
                candidate = _read_json(directory / 'raw_content.txt')
                replay = split_memory(request, MockBackend(candidate))
            except ValidationError as exc:
                error = exc.as_dict()
            facts = candidate.get('facts', []) if isinstance(candidate, dict) else []
            sources = {('memory', request['memory_id']): request['memory_text']}
            sources.update({('context', c['source_id']): c['text'] for c in request.get('source_context', [])})
            fact_checks = []
            for position, fact in enumerate(facts, 1):
                evidence_checks = []
                for eindex, evidence in enumerate(fact.get('evidence', [])):
                    quote = evidence.get('quote')
                    source = sources.get((evidence.get('source_type'), evidence.get('source_id')))
                    check = {'case_id': cid, 'version': version, 'fact_index': fact.get('fact_index'),
                        'evidence_index': eindex, 'source_type': evidence.get('source_type'),
                        'source_id': evidence.get('source_id'), 'quote': quote,
                        'exact_substring': isinstance(quote, str) and bool(quote.strip()) and source is not None and quote in source}
                    evidence_checks.append(check)
                    quotes.append(check)
                memory = [e for e in evidence_checks if e['source_type'] == 'memory']
                fact_checks.append({'fact_index': fact.get('fact_index'),
                    'consecutive_index': type(fact.get('fact_index')) is int and fact['fact_index'] == position,
                    'source_memory_id_match': fact.get('source_memory_id') == request['memory_id'],
                    'memory_evidence_passed': bool(memory) and all(e['source_id'] == request['memory_id'] and e['exact_substring'] for e in memory),
                    'all_literal_quotes_passed': all(e['exact_substring'] for e in evidence_checks),
                    'evidence_checks': evidence_checks})
            passed = replay is not None
            assert passed == (report['automatic_check'] == 'passed'), (cid, version)
            result_path = directory / 'result.json'
            assert result_path.exists() == passed, (cid, version)
            saved_equals_replay = passed and replay == _read_json(result_path)
            assert not passed or saved_equals_replay
            audit = {'case_id': cid, 'version': version, 'program_status': 'passed' if passed else 'failed',
                'strict_JSON_and_existing_validator_replay': passed, 'replay_error': error,
                'candidate_fact_count': len(facts), 'accepted_fact_count': len(replay['facts']) if passed else 0,
                'saved_result_equals_replay': saved_equals_replay,
                'raw_response_exists': (directory / 'raw_content.txt').exists(), 'facts': fact_checks,
                'semantic_correctness': 'not determined; separate AI preliminary review pending human confirmation',
                'additional_real_model_calls': 0}
            save(checks_dir / (cid + '_' + version + '.json'), audit)
            audits.append(audit)
    versions = {}
    for version in ['v4', 'v5']:
        group = [a for a in audits if a['version'] == version]
        q = [e for e in quotes if e['version'] == version]
        versions[version] = {'case_count': len(group), 'program_passed': sum(a['program_status'] == 'passed' for a in group),
            'accepted_facts': sum(a['accepted_fact_count'] for a in group),
            'candidate_facts': sum(a['candidate_fact_count'] for a in group),
            'literal_quotes_total': len(q), 'literal_quotes_passed': sum(e['exact_substring'] for e in q),
            'memory_quotes': sum(e['source_type'] == 'memory' for e in q),
            'context_quotes': sum(e['source_type'] == 'context' for e in q),
            'facts_with_memory_passed': sum(f['memory_evidence_passed'] for a in group for f in a['facts'])}
    save(ROOT / 'program_summary.json', {'versions': versions, 'runs': audits, 'additional_real_model_calls': 0})
    with (ROOT / 'literal_quote_checks.csv').open('x', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(quotes[0]))
        writer.writeheader(); writer.writerows(quotes)
    print(json.dumps(versions, ensure_ascii=False))


if __name__ == '__main__':
    main()
