import copy
import unittest
from comparison import compare_case, make_new_only


def fixture():
    old='The room was closed.'
    new='The room was closed; now it is open.'
    payload={'case_id':'test', 'old_units':[{'unit_id':'o','source_id':'m','memory_quotes':['closed']}],
             'new_units':[{'unit_id':'n','source_id':'s','memory_quotes':[new]}],
             'source_texts':{'memory':{'source_id':'m','text':old,'source_ref':'synthetic:old'},
                             'messages':[{'source_id':'s','text':new,'source_ref':'synthetic:new','side':'new','speaker':'user'}]}}
    rec={'unit_id':'o','relation':'change','old_subject':'room','new_subject':'room','old_attribute':'status',
         'new_attribute':'status','old_value':'closed','new_value':'open','old_conditions':{'kind':'unconditional'},
         'new_conditions':{'kind':'same_as_old'},'modality':'asserted',
         'old_quotes':[{'unit_id':'o','source_id':'m','quote':'closed'}],
         'new_quotes':[{'unit_id':'n','source_id':'s','quote':new}],
         'semantic_rationale':'Model proposes an update.','semantic_basis':[{'side':'new','source_id':'s','quote':new}],
         'temporal_order':{'relation':'after','basis':[{'side':'new','source_id':'s','quote':new}],'explanation':'It says was closed and now open.'},
         'uncertainties':[]}
    return payload,{'records':[rec],'unmatched_old_unit_ids':[]}


class ComparisonTests(unittest.TestCase):
    def test_candidate_mode_is_separate_from_independent_semantic_review(self):
        payload,raw=fixture();groups=compare_case(payload,raw)
        self.assertFalse(groups['A']['plan']['modify'])
        self.assertEqual(len(groups['B']['plan']['modify']),1)
        self.assertEqual(groups['A']['alignments'][0]['semantic_support'],'unknown')
        self.assertEqual(groups['B']['alignments'][0]['semantic_support'],'supported')
        self.assertEqual(groups['B']['alignments'][0]['authorization_origin'],'model_candidate_only')
        self.assertNotIn('semantic_support',raw['records'][0])

    def test_independent_new_candidate_does_not_authorize_earlier_change(self):
        payload,raw=fixture();raw['records'][0]['temporal_order']={'relation':'unknown','basis':[],'explanation':None}
        plan=compare_case(payload,raw)['B']['plan']
        self.assertFalse(plan['modify']);self.assertTrue(plan['uncertain'])
        self.assertEqual(len(plan['add']),1)
        self.assertEqual(plan['add'][0]['value'],'open')

    def test_unbound_new_quote_cannot_generate_candidate_action(self):
        payload,raw=fixture();raw['records'][0]['new_quotes'][0]['source_id']='invented'
        plan=compare_case(payload,raw)['B']['plan']
        self.assertFalse(plan['modify']);self.assertFalse(plan['add']);self.assertTrue(plan['uncertain'])

    def test_new_only_projection_removes_only_old_relation_not_model_claim(self):
        payload,raw=fixture();r=copy.deepcopy(raw['records'][0]); nr=make_new_only(r)
        self.assertEqual(nr['new_value'],r['new_value']); self.assertEqual(nr['new_quotes'],r['new_quotes'])
        self.assertEqual(nr['new_attribute'],r['new_attribute']);self.assertEqual(nr['semantic_basis'],r['semantic_basis'])
        self.assertEqual(nr['relation'],'new_information');self.assertEqual(nr['temporal_order']['relation'],'unknown')
        self.assertEqual(r['temporal_order']['relation'],'after')

    def test_opaque_scope_never_becomes_unconditional(self):
        payload,raw=fixture();raw['records'][0]['old_conditions']={'kind':'unknown'}
        raw['records'][0]['new_conditions']={'kind':'same_as_old'}
        result=compare_case(payload,raw)
        self.assertFalse(result['B']['plan']['modify'])
        self.assertFalse(result['B']['plan']['add'])
        self.assertTrue(result['B']['plan']['uncertain'])

    def test_independent_new_subfact_does_not_repair_source(self):
        payload,raw=fixture(); raw['records'][0]['semantic_basis'][0]['source_id']='unselected'
        result=compare_case(payload,raw)
        self.assertFalse(result['B']['plan']['modify'])
        self.assertFalse(result['B']['plan']['add'])
        self.assertTrue(result['B']['plan']['uncertain'])

if __name__=='__main__': unittest.main()
