import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import adapt_aligner_output


def artifact():
    return {
        'input': {
            'old_units': [{'unit_id': 'u', 'memory_quotes': ['old claim']}],
            'new_units': [{'unit_id': 'n', 'source_id': 's', 'memory_quotes': ['new claim']}],
            'source_texts': {'memory': {'source_id': 'm', 'text': 'old claim'},
                             'messages': [{'source_id': 's', 'text': 'new claim', 'side': 'new', 'speaker': 'user'}]},
        },
        'result': {'parsed': {'records': [{
            'old_unit_ids': ['u'], 'new_unit_ids': ['n'], 'attribute': 'role',
            'relation': 'state_change', 'old_quotes': ['old claim'], 'new_quotes': ['new claim'],
            'qualifiers': [], 'missing_evidence': [],
        }], 'unmatched_old_unit_ids': []}, 'structure_errors': [], 'coverage': {}},
    }


class AdapterTests(unittest.TestCase):
    def test_v3_does_not_fabricate_subject_value_or_scope(self):
        rec = adapt_aligner_output(artifact())[0]
        for field in ('old_subject', 'new_subject', 'old_value', 'new_value', 'old_conditions', 'new_conditions'):
            self.assertIsNone(rec[field], field)
        self.assertEqual(rec['relation'], 'change')
        self.assertTrue(any('new_conditions' in reason for reason in rec['missing_reasons']))
        self.assertEqual(rec['raw_record']['qualifiers'], [])

    def test_record_structure_error_is_propagated(self):
        a = artifact()
        a['result']['structure_errors'] = [{'path': 'records[0].qualifiers[0]', 'code': 'bad_source'}]
        rec = adapt_aligner_output(a)[0]
        self.assertEqual(rec['upstream_structure_errors'][0]['code'], 'bad_source')
        self.assertTrue(any('bad_source' in reason for reason in rec['missing_reasons']))

    def test_source_mismatch_is_not_resolved(self):
        a = artifact()
        a['input']['new_units'][0]['source_id'] = 'other'
        rec = adapt_aligner_output(a)[0]
        self.assertIsNone(rec['source_id'])
        self.assertTrue(any('source' in reason for reason in rec['missing_reasons']))

    def test_multiple_quotes_are_retained_but_not_combined(self):
        a = artifact()
        a['input']['new_units'][0]['memory_quotes'] = ['new claim', 'another claim']
        a['input']['source_texts']['messages'][0]['text'] = 'new claim and another claim'
        a['result']['parsed']['records'][0]['new_quotes'] = ['new claim', 'another claim']
        rec = adapt_aligner_output(a)[0]
        self.assertIsNone(rec['new_quote'])
        self.assertEqual([q['quote'] for q in rec['resolved_new_quotes']], ['new claim', 'another claim'])
        self.assertEqual(rec['raw_record']['new_quotes'], ['new claim', 'another claim'])
        self.assertTrue(any('single' in reason for reason in rec['missing_reasons']))

    def test_unmatched_and_unhandled_units_are_explicit(self):
        a = artifact()
        a['input']['old_units'].extend([
            {'unit_id': 'u2', 'memory_quotes': ['second']},
            {'unit_id': 'u3', 'memory_quotes': ['third']},
        ])
        a['result']['parsed']['unmatched_old_unit_ids'] = ['u2']
        a['result']['coverage']['unhandled_old_unit_ids'] = ['u3']
        a['result']['coverage']['unhandled_new_unit_ids'] = ['n2']
        recs = adapt_aligner_output(a)
        self.assertEqual([x['unit_id'] for x in recs], ['u', 'u2', 'u3', None])
        self.assertIn('unmatched', recs[1]['missing_reasons'][0])
        self.assertIn('unhandled', recs[2]['missing_reasons'][0])
        self.assertEqual(recs[3]['unhandled_new_unit_id'], 'n2')

    def test_adapt_does_not_mutate_raw_artifact(self):
        a = artifact()
        before = copy.deepcopy(a)
        adapt_aligner_output(a)
        self.assertEqual(a, before)


if __name__ == '__main__':
    unittest.main()
