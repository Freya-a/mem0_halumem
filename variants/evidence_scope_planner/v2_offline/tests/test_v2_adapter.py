import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from adapter import adapt_aligner_output, load_aligner_case


def artifact():
    return {'input': {'old_units': [
        {'unit_id': 'u1', 'memory_quotes': ['old one']},
        {'unit_id': 'u2', 'memory_quotes': ['old two']}],
        'new_units': [
            {'unit_id': 'n1', 'source_id': 's1', 'memory_quotes': ['new one']},
            {'unit_id': 'n2', 'source_id': 's2', 'memory_quotes': ['new two']}],
        'source_texts': {'memory': {'source_id': 'm', 'text': 'old one; old two'},
                         'messages': [{'source_id': 's1', 'text': 'new one', 'side': 'new', 'speaker': 'user'},
                                      {'source_id': 's2', 'text': 'new two', 'side': 'new', 'speaker': 'user'}]}},
        'result': {'parsed': {'records': [{
            'old_unit_ids': ['u1', 'u2'], 'new_unit_ids': ['n1', 'n2'], 'attribute': 'role',
            'relation': 'state_change', 'old_quotes': ['old one', 'old two'],
            'new_quotes': ['new one', 'new two'], 'qualifiers': [], 'missing_evidence': [],
        }], 'unmatched_old_unit_ids': []}, 'structure_errors': [], 'coverage': {}}}


class AdapterV2Tests(unittest.TestCase):
    def test_multiple_quotes_preserve_source_and_unique_unit_without_cross_pairing(self):
        a = adapt_aligner_output(artifact())[0]
        self.assertEqual(a['old_quotes'], [{'source_id': 'm', 'quote': 'old one', 'unit_id': 'u1'}, {'source_id': 'm', 'quote': 'old two', 'unit_id': 'u2'}])
        self.assertEqual(a['new_quotes'], [{'source_id': 's1', 'quote': 'new one', 'unit_id': 'n1'}, {'source_id': 's2', 'quote': 'new two', 'unit_id': 'n2'}])
        self.assertIsNone(a['unit_id'])
        self.assertIsNone(a['new_quote'])

    def test_ambiguous_unit_binding_not_fabricated(self):
        x = artifact()
        x['input']['old_units'][1]['memory_quotes'] = ['old one']
        x['result']['parsed']['records'][0]['old_quotes'] = ['old one']
        a = adapt_aligner_output(x)[0]
        self.assertNotIn('unit_id', a['old_quotes'][0])
        self.assertTrue(a['validation_errors'])

    def test_unrelated_and_new_information_are_distinct_and_old_link_is_uncertain(self):
        x = artifact(); record = x['result']['parsed']['records'][0]
        record.update(old_unit_ids=[], old_quotes=[], new_unit_ids=['n1'], new_quotes=['new one'], relation='new_information')
        self.assertEqual(adapt_aligner_output(x)[0]['relation'], 'new_information')
        record.update(old_unit_ids=['u1'], old_quotes=['old one'])
        a = adapt_aligner_output(x)[0]
        self.assertEqual(a['relation'], 'unknown')
        self.assertTrue(any('old unit' in str(r) for r in a['missing_reasons']))

    def test_time_and_unknowns_do_not_create_chronology_or_blocking_error(self):
        x = artifact(); record = x['result']['parsed']['records'][0]
        record['qualifiers'] = [{'side': 'new', 'kind': 'time', 'quote': 'recently', 'claim_quote': 'recently new one'}]
        record['missing_evidence'] = ['completion date unavailable']
        a = adapt_aligner_output(x)[0]
        self.assertEqual(a['temporal_order'], {'relation': 'unknown', 'basis': []})
        self.assertEqual(a['qualifiers'], record['qualifiers'])
        self.assertEqual(a['unknowns'], ['completion date unavailable'])
        self.assertFalse(any('completion date' in str(r) for r in a['validation_errors']))

    def test_errors_scoped_to_record_and_sources_checked(self):
        x = artifact(); x['result']['parsed']['records'].append(copy.deepcopy(x['result']['parsed']['records'][0]))
        x['result']['structure_errors'] = [{'path': 'records[0].old_quotes', 'code': 'bad'}]
        a = adapt_aligner_output(x)
        self.assertTrue(any('bad' in str(e) for e in a[0]['validation_errors']))
        self.assertFalse(any('bad' in str(e) for e in a[1]['validation_errors']))
        x['input']['source_texts']['messages'][0]['speaker'] = 'assistant'
        self.assertTrue(any('user' in str(e) for e in adapt_aligner_output(x)[0]['validation_errors']))

    def test_no_values_fabricated_from_v2_claims(self):
        x = artifact(); r = x['result']['parsed']['records'][0]
        r.update(change_type='state_change', old_claim={'subject': 'user','attribute':'role','object':'org','statement':'old'}, new_claim={'subject':'user','attribute':'role','object':'org2','statement':'new'})
        del r['relation']
        a = adapt_aligner_output(x)[0]
        self.assertEqual(a['old_subject'], 'user')
        self.assertIsNone(a['old_value']); self.assertIsNone(a['new_value'])
        self.assertEqual(a['old_claim']['object'], 'org')

    def test_unlinked_old_source_is_not_reassigned(self):
        x = artifact()
        r = x['result']['parsed']['records'][0]
        r.update(old_unit_ids=['u1'], old_quotes=[{'source_id': 'other', 'quote': 'old one'}],
                 new_unit_ids=['n1'], new_quotes=[{'source_id': 's1', 'quote': 'new one'}],
                 change_type='state_change', old_value='x', new_claim='y')
        del r['relation']
        x['input']['source_texts']['messages'].append({'source_id': 'other', 'text': 'old one', 'side': 'old', 'speaker': 'user'})
        a = adapt_aligner_output(x)[0]
        self.assertIsNone(a['old_quotes'][0]['source_id'])
        self.assertEqual(a['old_quotes'][0]['reported_source_id'], 'other')
        self.assertTrue(a['validation_errors'])

    def test_repeated_quote_in_source_is_a_location_error(self):
        x = artifact()
        r = x['result']['parsed']['records'][0]
        r.update(old_unit_ids=['u1'], old_quotes=['old one'], new_unit_ids=['n1'], new_quotes=['new one'])
        x['input']['source_texts']['memory']['text'] = 'old one and old one'
        a = adapt_aligner_output(x)[0]
        self.assertTrue(any('repeated' in str(e) for e in a['validation_errors']))
        self.assertNotIn('position', a['old_quotes'][0])

    def test_global_error_stays_separate_from_records(self):
        x = artifact()
        x['result']['validation_errors'] = [{'path': 'coverage', 'code': 'global_coverage_error'}]
        records = adapt_aligner_output(x)
        self.assertFalse(any('global_coverage_error' in str(e) for e in records[0]['validation_errors']))
        self.assertTrue(any('global_coverage_error' in str(r.get('missing_reasons')) for r in records[1:]))

    def test_v2_qualifiers_preserved_separately(self):
        x = artifact(); r = x['result']['parsed']['records'][0]
        r.update(change_type='state_change', old_claim={'subject':'user', 'attribute':'role', 'qualifiers':[{'kind':'time','quote':'before'}]},
                 new_claim={'subject':'user', 'attribute':'role', 'qualifiers':[{'kind':'time','quote':'recently'}]})
        del r['relation']
        a = adapt_aligner_output(x)[0]
        self.assertEqual(a['old_qualifiers'], r['old_claim']['qualifiers'])
        self.assertEqual(a['new_qualifiers'], r['new_claim']['qualifiers'])
        self.assertEqual(a['temporal_order']['relation'], 'unknown')

    def test_unhandled_units_and_memory_id_are_retained(self):
        x = artifact(); x['input']['source_texts']['memory']['source_ref'] = 'before.json#/memory'
        x['result']['parsed']['unmatched_old_unit_ids'] = ['u2']
        x['result']['coverage']['unhandled_new_unit_ids'] = ['n2']
        records = adapt_aligner_output(x)
        self.assertTrue(any(r.get('unit_id') == 'u2' and r.get('upstream_coverage') for r in records))
        self.assertTrue(any(r.get('unhandled_new_unit_id') == 'n2' for r in records))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'input.json'; p.write_text(json.dumps(x))
            _, units, _, _ = load_aligner_case(p)
        self.assertTrue(all(u['memory_id'] == 'm' and u['source_ref'] == 'before.json#/memory' for u in units))

if __name__ == '__main__':
    unittest.main()
