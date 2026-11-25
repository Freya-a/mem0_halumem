import copy
import unittest
import scope_planner


def fixture():
    old='The room was closed.'
    new='The room was closed; now it is open.'
    units=[{'id':'o','quote':'closed','memory_id':'m','source_ref':'test:old'}]
    sources=[{'source_id':'s','text':new,'source_ref':'test:new','side':'new','speaker':'user'}]
    a={'unit_id':'o','relation':'change','old_subject':'room','new_subject':'room',
       'old_attribute':'status','new_attribute':'status','old_value':'closed','new_value':'open',
       'old_conditions':{'kind':'unconditional'},'new_conditions':{'kind':'unconditional'},
       'modality':'asserted','old_quotes':[{'unit_id':'o','source_id':'m','quote':'closed'}],
       'new_quotes':[{'source_id':'s','quote':new}], 'semantic_support':'supported',
       'semantic_basis':[{'side':'new','source_id':'s','quote':new}],
       'temporal_order':{'relation':'after','basis':[{'side':'new','source_id':'s','quote':new}],
                         'explanation':'It was closed and is now open.'}}
    return old,units,sources,a


class CoverageTests(unittest.TestCase):
    def test_overlapping_uncertain_claim_does_not_hide_sibling_change(self):
        old,units,sources,change=fixture()
        supplemental={**copy.deepcopy(change),'relation':'supplement','old_attribute':'purpose',
                      'new_attribute':'purpose','old_value':'safety','new_value':'improved safety'}
        p=scope_planner.build_scope_plan(old,units,sources,[change,supplemental])
        decisions={(x.get('candidate_index'),x.get('judgment_kind')) for x in p['uncertain']}
        self.assertIn((0,'old_relation'),decisions)
        self.assertIn((1,'old_relation'),decisions)
        self.assertIn('blocked',next(x['reason'] for x in p['uncertain'] if x.get('candidate_index')==0))
        self.assertFalse(p['modify'])
        self.assertTrue(all(j['outputs'] for c in p['candidate_coverage'] for j in c['judgments']))

    def test_supplement_has_separate_new_claim_and_old_relation(self):
        old,units,sources,a=fixture();a['relation']='supplement'
        p=scope_planner.build_scope_plan(old,units,sources,[a])
        c=p['candidate_coverage'][0]
        self.assertEqual({j['kind'] for j in c['judgments']},{'new_claim','old_relation'})
        self.assertTrue(all(j['outputs'] for j in c['judgments']))
        self.assertTrue(any(x.get('judgment_kind')=='new_claim' for x in p['add']))
        self.assertTrue(any(x.get('judgment_kind')=='old_relation' for x in p['uncertain']))

    def test_duplicate_supported_candidates_have_distinct_destinations(self):
        old,units,sources,a=fixture()
        p=scope_planner.build_scope_plan(old,units,sources,[a,copy.deepcopy(a)])
        self.assertEqual(len(p['candidate_coverage']),2)
        self.assertTrue(all(j['outputs'] for c in p['candidate_coverage'] for j in c['judgments']))
        self.assertTrue(any(x.get('candidate_index')==1 for x in p['uncertain']))
        self.assertFalse(p['modify'],'unresolved same-scope candidate must block edit')

    def test_unmapped_unit_gets_candidate_uncertain(self):
        old,units,sources,a=fixture();a['unit_id']='absent';a['old_quotes'][0]['unit_id']='absent'
        p=scope_planner.build_scope_plan(old,units,sources,[a])
        self.assertTrue(p['candidate_coverage'][0]['judgments'][0]['outputs'])
        self.assertTrue(any(x.get('candidate_index')==0 for x in p['uncertain']))
        self.assertFalse(p['modify'])

    def test_new_only_does_not_get_fake_old_relation(self):
        old,units,sources,a=fixture();a.update(unit_id=None,relation='new_information',old_quotes=[])
        p=scope_planner.build_scope_plan(old,units,sources,[a])
        self.assertEqual([j['kind'] for j in p['candidate_coverage'][0]['judgments']],['new_claim'])
        self.assertTrue(p['candidate_coverage'][0]['judgments'][0]['outputs'])

    def test_conflicting_candidates_each_receive_an_output(self):
        old,units,sources,a=fixture()
        b=copy.deepcopy(a);b['new_value']='locked'
        p=scope_planner.build_scope_plan(old,units,sources,[a,b])
        self.assertFalse(p['modify'])
        self.assertEqual({x['candidate_index'] for x in p['uncertain'] if 'candidate_index' in x},{0,1})
        for entry in p['candidate_coverage']:
            for judgment in entry['judgments']:
                for ref in judgment['outputs']:
                    item=p[ref['category']][ref['index']]
                    self.assertEqual((item['candidate_index'],item['judgment_kind']),
                                     (entry['candidate_index'],judgment['kind']))

    def test_finite_two_dimension_partition_is_retained(self):
        old,units,sources,a=fixture()
        a['old_conditions']={'kind':'finite','dimensions':{'city':['A','B'],'service':['in','out']}}
        a['new_conditions']={'kind':'finite','dimensions':{'city':['A'],'service':['out']}}
        p=scope_planner.build_scope_plan(old,units,sources,[a])
        self.assertEqual([x['scope'] for x in p['modify']],[{'city':'A','service':'out'}])
        self.assertEqual(len(p['preserve']),3)
        refs=p['candidate_coverage'][0]['judgments'][0]['outputs']
        self.assertEqual({r['category'] for r in refs},{'modify','preserve'})

if __name__=='__main__':unittest.main()
