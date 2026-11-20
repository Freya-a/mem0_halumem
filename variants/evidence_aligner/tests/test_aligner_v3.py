import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import aligner_v3
except ModuleNotFoundError as exc:
    if exc.name != 'aligner_v3':
        raise
    aligner_v3 = None


def example():
    old = [{'unit_id': 'o1', 'source_id': 'mem', 'raw_statement': 'search',
            'memory_quotes': ['Looking for a new job']}]
    text = "I've transitioned to a new role. Work-life balance is much healthier now."
    new = [{'unit_id': 'n1', 'source_id': 'm1', 'raw_statement': text, 'memory_quotes': [text]}]
    sources = {'memory': {'source_id': 'mem', 'text': 'Previously: Looking for a new job', 'speaker': 'memory'},
               'messages': [{'source_id': 'm1', 'text': text, 'speaker': 'user', 'side': 'new'}]}
    record = {'old_unit_ids': ['o1'], 'new_unit_ids': ['n1'], 'attribute': 'work',
              'relation': 'state_change', 'old_quotes': ['Looking for a new job'],
              'new_quotes': [text], 'qualifiers': [
                  {'side': 'new', 'kind': 'time', 'quote': 'now',
                   'claim_quote': 'Work-life balance is much healthier now'}],
              'missing_evidence': []}
    return old, new, sources, {'records': [record], 'unmatched_old_unit_ids': []}


def validate(inputs):
    old, new, sources, data = inputs
    return aligner_v3.parse_and_validate(json.dumps(data), old, new, sources)


class AlignerV3Tests(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(aligner_v3, 'v3 aligner has not yet been implemented')

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_prompt_json_example_satisfies_validator_contract(self):
        example_json = aligner_v3.PROMPT_FILE.read_text(encoding='utf-8').splitlines()[-1]
        old = [{'unit_id': 'o1', 'source_id': 'mem', 'raw_statement': 'title',
                'memory_quotes': ['Director']}]
        text = 'I recently got promoted to lead director'
        new = [{'unit_id': 'n1', 'source_id': 'm1', 'raw_statement': text, 'memory_quotes': [text]}]
        sources = {'memory': {'source_id': 'mem', 'text': 'Director'},
                   'messages': [{'source_id': 'm1', 'text': text, 'speaker': 'user', 'side': 'new'}]}
        result = aligner_v3.parse_and_validate(example_json, old, new, sources)
        self.assertEqual(result['status'], 'passed', result['structure_errors'])
        self.assertEqual(result['coverage']['unhandled_new_unit_ids'], [])

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_fills_unique_sources_without_mutating_model_output(self):
        inputs = example()
        original = copy.deepcopy(inputs[3])
        result = validate(inputs)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['parsed'], original)
        mappings = {x['path']: x['source_id'] for x in result['source_completions']}
        self.assertEqual(mappings['records[0].old_quotes[0]'], 'mem')
        self.assertEqual(mappings['records[0].new_quotes[0]'], 'm1')
        self.assertEqual(mappings['records[0].qualifiers[0]'], 'm1')
        self.assertEqual(result['semantic_review']['status'], 'not_reviewed')

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_same_text_in_two_sources_is_ambiguous_and_not_auto_filled(self):
        old, new, sources, data = example()
        new.append({'unit_id': 'n2', 'source_id': 'm2', 'raw_statement': new[0]['raw_statement'],
                    'memory_quotes': new[0]['memory_quotes'][:]})
        sources['messages'].append({'source_id': 'm2', 'text': new[0]['raw_statement'],
                                    'speaker': 'user', 'side': 'new'})
        data['records'][0]['new_unit_ids'] = ['n1', 'n2']
        data['records'][0]['qualifiers'] = []
        result = validate((old, new, sources, data))
        ambiguity = next(x for x in result['ambiguities'] if x['path'] == 'records[0].new_quotes[0]')
        self.assertEqual(ambiguity['candidate_source_ids'], ['m1', 'm2'])
        self.assertFalse(any(x['path'] == ambiguity['path'] for x in result['source_completions']))
        self.assertCountEqual(result['coverage']['unhandled_new_unit_ids'], ['n1', 'n2'])
        self.assertEqual(result['status'], 'failed')

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_qualifier_must_be_in_its_claim_anchor(self):
        inputs = example()
        inputs[3]['records'][0]['qualifiers'][0]['claim_quote'] = "I've transitioned to a new role"
        result = validate(inputs)
        self.assertIn('qualifier_not_in_claim', [e['code'] for e in result['structure_errors']])

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_qualifier_cannot_come_from_an_unlinked_new_source(self):
        inputs = example()
        inputs[2]['messages'].append({'source_id': 'm2', 'text': 'simulated skydiving',
                                      'speaker': 'user', 'side': 'new'})
        inputs[3]['records'][0]['qualifiers'][0] = {
            'side': 'new', 'kind': 'simulation', 'quote': 'simulated',
            'claim_quote': 'simulated skydiving'}
        result = validate(inputs)
        self.assertIn('qualifier_anchor_provenance', [e['code'] for e in result['structure_errors']])

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_qualifier_can_include_same_source_context_outside_short_unit_quote(self):
        inputs = example()
        inputs[3]['records'][0]['qualifiers'].append({
            'side': 'old', 'kind': 'time', 'quote': 'Previously',
            'claim_quote': 'Previously: Looking for a new job'})
        result = validate(inputs)
        self.assertEqual(result['status'], 'passed')
        self.assertTrue(any(x['path'] == 'records[0].qualifiers[1]' for x in result['scope_review']))
        self.assertTrue(any(x['path'] == 'records[0].qualifiers[1]' and x['source_id'] == 'mem'
                            for x in result['source_completions']))

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_bad_quote_does_not_count_as_handled_and_missing_evidence_is_reported(self):
        inputs = example()
        inputs[3]['records'][0]['new_quotes'] = ['not actually in the source']
        inputs[3]['records'][0]['qualifiers'] = []
        result = validate(inputs)
        self.assertEqual(result['coverage']['unhandled_new_unit_ids'], ['n1'])
        self.assertIn('quote_provenance', [e['code'] for e in result['structure_errors']])
        self.assertTrue(any(x.get('unit_id') == 'n1' for x in result['missing_evidence']))

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_multiple_records_can_cover_distinct_claims_in_one_unit(self):
        inputs = example()
        rec = inputs[3]['records'][0]
        rec['new_quotes'] = ["I've transitioned to a new role"]
        rec['qualifiers'] = []
        second = {'old_unit_ids': [], 'new_unit_ids': ['n1'], 'attribute': 'work-life balance',
                  'relation': 'new_information', 'old_quotes': [],
                  'new_quotes': ['Work-life balance is much healthier now'],
                  'qualifiers': [{'side': 'new', 'kind': 'time', 'quote': 'now',
                                  'claim_quote': 'Work-life balance is much healthier now'}],
                  'missing_evidence': ['exact date']}
        inputs[3]['records'].append(second)
        result = validate(inputs)
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['coverage']['unhandled_new_unit_ids'], [])
        self.assertTrue(any(x.get('message') == 'exact date' for x in result['missing_evidence']))

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_explicit_unmatched_old_and_unmentioned_new_are_distinct(self):
        inputs = example()
        inputs[3]['records'] = []
        inputs[3]['unmatched_old_unit_ids'] = ['o1']
        result = validate(inputs)
        self.assertEqual(result['coverage']['unmatched_old_unit_ids'], ['o1'])
        self.assertEqual(result['coverage']['unhandled_old_unit_ids'], [])
        self.assertEqual(result['coverage']['unhandled_new_unit_ids'], ['n1'])

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_state_change_requires_old_evidence(self):
        inputs = example()
        rec = inputs[3]['records'][0]
        rec['old_unit_ids'], rec['old_quotes'] = [], []
        inputs[3]['unmatched_old_unit_ids'] = ['o1']
        result = validate(inputs)
        self.assertIn('missing_old_evidence', [e['code'] for e in result['structure_errors']])

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_malformed_fields_are_errors_and_do_not_raise(self):
        inputs = example()
        rec = inputs[3]['records'][0]
        rec.update(new_unit_ids=[{'bad': 1}], relation={'bad': 1}, qualifiers=['now'])
        result = validate(inputs)
        self.assertEqual(result['status'], 'failed')
        self.assertGreaterEqual(len(result['structure_errors']), 3)

    @unittest.skipIf(aligner_v3 is None, 'v3 missing')
    def test_bad_json_one_call_and_no_retry(self):
        old, new, sources, _ = example()
        calls = []
        def backend(messages):
            calls.append(messages)
            return {'content': '{bad', 'model': aligner_v3.MODEL}
        result = aligner_v3.align_evidence_v3(old, new, sources, backend=backend)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'parse_error')
        self.assertEqual(result['coverage']['unhandled_new_unit_ids'], ['n1'])
        self.assertEqual(json.loads(calls[0][1]['content']),
                         {'old_units': old, 'new_units': new, 'source_texts': sources})


if __name__ == '__main__':
    unittest.main()
