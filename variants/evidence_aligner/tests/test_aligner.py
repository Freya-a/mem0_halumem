import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import aligner
except ModuleNotFoundError as exc:
    if exc.name != 'aligner':
        raise
    aligner = None


def fixture():
    old = [{'unit_id': 'old-1', 'memory_quotes': ['Looking for a new job'],
            'raw_statement': 'Looking for a new job'}]
    new = [{'unit_id': 'new-1', 'source_id': 'msg-1',
            'memory_quotes': ["I've finally transitioned to a new role"],
            'raw_statement': "I've finally transitioned to a new role"}]
    sources = {'memory': {'source_id': 'memory-1', 'text': 'Looking for a new job'},
               'messages': [{'source_id': 'msg-1', 'speaker': 'user', 'side': 'new',
                             'text': "I've finally transitioned to a new role", 'recorded_at': '2026-03-01'}]}
    record = {'old_unit_ids': ['old-1'], 'new_unit_ids': ['new-1'],
              'attribute': 'job transition status', 'change_type': 'state_change',
              'old_value': 'looking for a new job', 'new_claim': 'transitioned to a new role',
              'old_quotes': [{'source_id': 'memory-1', 'quote': 'Looking for a new job'}],
              'new_quotes': [{'source_id': 'msg-1', 'quote': "I've finally transitioned to a new role"}],
              'conditions': [], 'time_expressions': [], 'event_date': None,
              'unknowns': ['exact transition date']}
    return old, new, sources, {'records': [record], 'unmatched_old_unit_ids': []}


class AlignmentTests(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(aligner, 'the evidence aligner module must be implemented')

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_single_call_preserves_input_and_validates(self):
        old, new, sources, response = fixture()
        calls = []
        def backend(messages):
            calls.append(messages)
            return {'content': json.dumps(response), 'model': aligner.MODEL}
        result = aligner.align_evidence(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['parsed'], response)
        payload = json.loads(calls[0][1]['content'])
        self.assertEqual(payload['old_units'], old)
        self.assertEqual(payload['new_units'], new)
        self.assertEqual(payload['source_texts'], sources)

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_malformed_json_is_parse_error_without_retry(self):
        old, new, sources, _ = fixture()
        calls = []
        def backend(messages):
            calls.append(messages)
            return {'content': '{bad', 'model': aligner.MODEL}
        result = aligner.align_evidence(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'parse_error')
        self.assertTrue(result['parse_errors'])
        self.assertEqual(result['coverage']['uncovered_new_unit_ids'], ['new-1'])

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_reports_unknown_ids_and_uncovered_units_separately(self):
        old, new, sources, response = fixture()
        response['records'][0]['new_unit_ids'] = ['invented']
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertTrue(any(e['code'] == 'unknown_unit_id' for e in result['validation_errors']))
        self.assertEqual(result['coverage']['uncovered_new_unit_ids'], ['new-1'])

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_quote_must_belong_to_the_linked_unit_not_just_source(self):
        old, new, sources, response = fixture()
        sources['messages'][0]['text'] += ' Other unrelated words.'
        response['records'][0]['new_quotes'][0]['quote'] = 'Other unrelated words'
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertTrue(any(e['code'] == 'quote_provenance' for e in result['validation_errors']))

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_rejects_wrong_side_and_unsupported_qualifiers(self):
        old, new, sources, response = fixture()
        response['records'][0]['old_quotes'][0] = {'source_id': 'msg-1', 'quote': 'transitioned'}
        response['records'][0]['conditions'] = [{'source_id': 'msg-1', 'quote': 'if hired'}]
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertGreaterEqual(sum(e['code'] == 'quote_provenance' for e in result['validation_errors']), 2)

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_recording_date_does_not_support_an_event_date(self):
        old, new, sources, response = fixture()
        response['records'][0]['event_date'] = '2026-03-01'
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertTrue(any(e['code'] == 'unsupported_event_date' for e in result['validation_errors']))

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_a_bare_number_in_a_quote_is_not_an_event_date(self):
        old, new, sources, response = fixture()
        text = "I've finally transitioned to a new role after 2 interviews"
        sources['messages'][0]['text'] = text
        new[0]['memory_quotes'] = [text]
        response['records'][0]['new_quotes'][0]['quote'] = text
        response['records'][0]['event_date'] = '2'
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertTrue(any(e['code'] == 'unsupported_event_date' for e in result['validation_errors']))

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_explicit_date_quoted_from_new_evidence_is_accepted(self):
        old, new, sources, response = fixture()
        text = "I've finally transitioned to a new role on March 1, 2026"
        sources['messages'][0]['text'] = text
        new[0]['memory_quotes'] = [text]
        response['records'][0]['new_quotes'][0]['quote'] = text
        response['records'][0]['event_date'] = 'March 1, 2026'
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertEqual(result['status'], 'passed')

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_non_string_change_type_is_a_validation_error_not_an_exception(self):
        old, new, sources, response = fixture()
        response['records'][0]['change_type'] = {'unexpected': 'object'}
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertTrue(any(e['code'] == 'schema' for e in result['validation_errors']))

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_independent_new_fact_can_have_no_old_unit(self):
        old, new, sources, response = fixture()
        response['records'][0].update(old_unit_ids=[], old_value=None, old_quotes=[], change_type='new_information')
        response['unmatched_old_unit_ids'] = ['old-1']
        result = aligner.parse_and_validate(json.dumps(response), old, new, sources)
        self.assertEqual(result['status'], 'passed')

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_duplicate_input_ids_fail_before_any_call(self):
        old, new, sources, _ = fixture()
        new.append(copy.deepcopy(new[0]))
        calls = []
        result = aligner.align_evidence(old, new, sources, backend=lambda messages: calls.append(messages))
        self.assertEqual(calls, [])
        self.assertEqual(result['status'], 'input_error')

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_transport_failure_does_not_retry_and_leaves_units_uncovered(self):
        old, new, sources, _ = fixture()
        calls = []
        def backend(messages):
            calls.append(messages)
            raise ConnectionError('sensitive detail should not be logged')
        result = aligner.align_evidence(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'request_error')
        self.assertEqual(result['request_error'], {'type': 'ConnectionError'})
        self.assertEqual(result['coverage']['uncovered_new_unit_ids'], ['new-1'])

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_default_backend_is_closed_after_one_call(self):
        old, new, sources, response = fixture()
        state = {'calls': 0, 'closed': False}
        class Backend:
            def __call__(self, messages):
                state['calls'] += 1
                return {'content': json.dumps(response), 'model': aligner.MODEL}
            def close(self):
                state['closed'] = True
        with patch('qwen_backend.QwenBackend', Backend):
            result = aligner.align_evidence(old, new, sources)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(state, {'calls': 1, 'closed': True})

    @unittest.skipIf(aligner is None, 'implementation not yet available')
    def test_invalid_backend_configuration_is_recorded_before_a_request(self):
        old, new, sources, _ = fixture()
        with patch('qwen_backend.QwenBackend', side_effect=ValueError('secret detail')):
            result = aligner.align_evidence(old, new, sources)
        self.assertEqual(result['status'], 'configuration_error')
        self.assertEqual(result['request_attempts'], 0)
        self.assertEqual(result['configuration_error'], {'type': 'ValueError'})


if __name__ == '__main__':
    unittest.main()
