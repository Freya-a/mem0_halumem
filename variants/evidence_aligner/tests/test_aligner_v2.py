import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import aligner_v2
except ModuleNotFoundError as exc:
    if exc.name != 'aligner_v2':
        raise
    aligner_v2 = None


def example():
    old = [{'unit_id': 'o1', 'source_id': 'mem', 'raw_statement': 'looking for work',
            'memory_quotes': ['Looking for a new job']}]
    new_text = "I've finally transitioned to a new role. Work-life balance is much healthier now."
    new = [{'unit_id': 'n1', 'source_id': 'm1', 'raw_statement': new_text, 'memory_quotes': [new_text]}]
    sources = {'memory': {'source_id': 'mem', 'text': 'Previously: Looking for a new job', 'speaker': 'memory'},
               'messages': [{'source_id': 'm1', 'text': new_text, 'speaker': 'user',
                             'side': 'new', 'recorded_at': '2026-03-01'}]}
    rec = {'old_unit_ids': ['o1'], 'new_unit_ids': ['n1'],
           'old_claim': {'subject': 'person', 'object': 'job', 'attribute': 'job search progress',
                         'statement': 'looking for a new job', 'qualifiers': [
                             {'kind': 'time', 'source_id': 'mem', 'quote': 'Previously'}], 'event_date': None},
           'new_claim': {'subject': 'person', 'object': 'job', 'attribute': 'job search progress',
                         'statement': 'transitioned to a new role', 'qualifiers': [], 'event_date': None},
           'target_relation': 'same', 'change_type': 'state_change',
           'old_quotes': [{'source_id': 'mem', 'quote': 'Looking for a new job'}],
           'new_quotes': [{'source_id': 'm1', 'quote': "I've finally transitioned to a new role"}],
           'change_evidence': [{'source_id': 'm1', 'quote': 'transitioned to a new role'}],
           'relation_explanation': 'The new evidence states the transition was completed.',
           'unknowns': ['exact transition date']}
    return old, new, sources, {'records': [rec], 'unmatched_old_unit_ids': []}


class V2Tests(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(aligner_v2, 'v2 evidence aligner must be implemented')

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_one_request_preserves_input_and_returns_quote_offsets(self):
        old, new, sources, response = example()
        calls = []
        def backend(messages):
            calls.append(messages)
            return {'content': json.dumps(response), 'model': aligner_v2.MODEL}
        result = aligner_v2.align_evidence_v2(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(json.loads(calls[0][1]['content']),
                         {'old_units': old, 'new_units': new, 'source_texts': sources})
        self.assertTrue(any(q['path'] == 'records[0].old_claim.qualifiers[0]' and q['spans'] == [[0, 10]]
                            for q in result['quote_locations']))

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_state_change_requires_specific_new_evidence(self):
        old, new, sources, response = example()
        response['records'][0]['change_evidence'] = []
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('missing_change_evidence', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_state_change_requires_an_old_claim_to_compare(self):
        old, new, sources, response = example()
        response['records'][0].update(old_unit_ids=[], old_claim=None, old_quotes=[])
        response['unmatched_old_unit_ids'] = ['o1']
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('missing_old_claim_for_change', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_change_evidence_must_be_within_cited_new_quote(self):
        old, new, sources, response = example()
        response['records'][0]['change_evidence'] = [{'source_id': 'm1', 'quote': 'much healthier now'}]
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('change_evidence_not_in_new_quote', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_old_qualifier_cannot_use_new_side_or_unknown_source(self):
        old, new, sources, response = example()
        response['records'][0]['old_claim']['qualifiers'] = [{'kind': 'time', 'source_id': 'm1', 'quote': 'now'}]
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('quote_provenance', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_missing_and_invented_unit_ids_are_reported_separately(self):
        old, new, sources, response = example()
        response['records'][0]['new_unit_ids'] = ['invented']
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('unknown_unit_id', [e['code'] for e in result['validation_errors']])
        self.assertEqual(result['coverage']['uncovered_new_unit_ids'], ['n1'])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_independent_new_record_does_not_require_old_claim(self):
        old, new, sources, response = example()
        rec = response['records'][0]
        rec.update(old_unit_ids=[], old_claim=None, old_quotes=[], change_evidence=[],
                   target_relation='unknown', change_type='new_information')
        response['unmatched_old_unit_ids'] = ['o1']
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertEqual(result['status'], 'passed')

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_recording_timestamp_cannot_be_used_as_event_date(self):
        old, new, sources, response = example()
        response['records'][0]['new_claim']['event_date'] = '2026-03-01'
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('unsupported_event_date', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_quote_must_belong_to_linked_unit_not_only_source(self):
        old, new, sources, response = example()
        sources['messages'][0]['text'] += ' Unrelated extra sentence.'
        response['records'][0]['new_quotes'] = [{'source_id': 'm1', 'quote': 'Unrelated extra sentence.'}]
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertIn('quote_provenance', [e['code'] for e in result['validation_errors']])

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_malformed_fields_are_errors_not_exceptions(self):
        old, new, sources, response = example()
        response['records'][0]['change_type'] = {'bad': 'value'}
        response['records'][0]['new_claim']['qualifiers'] = ['now']
        result = aligner_v2.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertEqual(result['status'], 'failed')
        self.assertGreaterEqual(len(result['validation_errors']), 2)

    @unittest.skipIf(aligner_v2 is None, 'implementation not yet available')
    def test_bad_json_does_not_retry(self):
        old, new, sources, _ = example()
        calls = []
        def backend(messages):
            calls.append(messages)
            return {'content': '{bad', 'model': aligner_v2.MODEL}
        result = aligner_v2.align_evidence_v2(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'parse_error')
        self.assertEqual(result['coverage']['uncovered_new_unit_ids'], ['n1'])


if __name__ == '__main__':
    unittest.main()
