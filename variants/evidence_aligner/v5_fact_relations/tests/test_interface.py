import copy
import unittest
import interface


def example():
    payload={'case_id':'test','old_units':[{'unit_id':'old','source_id':'m','memory_quotes':['closed']}],
             'new_units':[{'unit_id':'new','source_id':'s','memory_quotes':['The room is now open.']}],
             'source_texts':{'memory':{'source_id':'m','text':'The room was closed.','source_ref':'test:old'},
                 'messages':[{'source_id':'s','text':'The room is now open.','source_ref':'test:new','side':'new','speaker':'user'}]}}
    quote={'unit_id':'new','source_id':'s','quote':'The room is now open.'}
    fact={'fact_id':'f1','subject':'room','attribute':'state','value':'open','conditions':{'kind':'unconditional'},
          'modality':'asserted','quotes':[quote],'rationale':'A statement.','uncertainties':[]}
    relation={'relation_id':'r1','fact_id':'f1','unit_id':'old','relation':'change','old_subject':'room',
              'old_attribute':'state','old_value':'closed','old_conditions':{'kind':'unconditional'},
              'old_quotes':[{'unit_id':'old','source_id':'m','quote':'closed'}],
              'affected_part':'closed','temporal_order':{'relation':'unknown','basis':[],'explanation':None},
              'rationale':'Potential change','semantic_basis':[{'side':'new','source_id':'s','quote':'The room is now open.'}],
              'uncertainties':[]}
    return payload,{'facts':[fact],'relations':[relation],'unmatched_old_unit_ids':[]}

class InterfaceTests(unittest.TestCase):
    def test_fact_and_relation_are_independent_and_unreviewed(self):
        payload,out=example();analysis=interface.analyze(payload,out)
        self.assertEqual(analysis['validation']['schema_status'],'passed')
        self.assertEqual(analysis['validation']['quote_status'],'passed')
        self.assertEqual(len(analysis['plan']['candidate_coverage']),2)
        self.assertEqual([a['relation'] for a in analysis['alignments']],['new_information','change'])
        self.assertTrue(all(a['semantic_support']=='unknown' for a in analysis['alignments']))
        self.assertFalse(analysis['plan']['add']);self.assertFalse(analysis['plan']['modify'])
        self.assertTrue(all(j['outputs'] for c in analysis['plan']['candidate_coverage'] for j in c['judgments']))

    def test_missing_or_wrong_new_source_blocks_candidate(self):
        p,o=example();o['facts'][0]['quotes'][0]['source_id']='wrong'
        a=interface.analyze(p,o)
        self.assertEqual(a['validation']['quote_status'],'failed')
        self.assertFalse(a['plan']['add']);self.assertFalse(a['plan']['modify'])

    def test_relation_missing_fact_id_is_not_repaired(self):
        p,o=example();o['relations'][0]['fact_id']='missing'
        a=interface.analyze(p,o)
        self.assertEqual(a['validation']['schema_status'],'failed')
        self.assertFalse(a['plan']['modify']);self.assertTrue(a['plan']['uncertain'])
        self.assertEqual(a['alignments'][1]['new_value'],None)

    def test_duplicate_fact_id_fails_closed(self):
        p,o=example();o['facts'].append(copy.deepcopy(o['facts'][0]))
        a=interface.analyze(p,o)
        self.assertEqual(a['validation']['schema_status'],'failed')
        self.assertTrue(any('duplicate' in e for e in a['validation']['schema_errors']))
        self.assertFalse(a['plan']['add']);self.assertFalse(a['plan']['modify'])

    def test_supplement_does_not_manufacture_another_new_fact(self):
        p,o=example();o['relations'][0]['relation']='supplement'
        a=interface.analyze(p,o)
        self.assertEqual(a['alignments'][1]['relation'],'unknown')
        self.assertEqual(len(a['plan']['candidate_coverage']),2)
        self.assertEqual(a['plan']['candidate_coverage'][1]['judgments'][0]['kind'],'old_relation')

    def test_unknown_conditions_and_time_remain_unknown(self):
        p,o=example();o['facts'][0]['conditions']={'kind':'unknown'}
        a=interface.analyze(p,o)
        self.assertEqual(a['alignments'][0]['new_conditions'],{'kind':'unknown'})
        self.assertEqual(a['alignments'][1]['temporal_order']['relation'],'unknown')
        self.assertFalse(a['plan']['modify'])

    def test_malformed_relation_is_recorded_not_crashed(self):
        p,o=example();o['relations'][0]['relation']=[]
        a=interface.analyze(p,o)
        self.assertEqual(a['validation']['schema_status'],'failed')
        self.assertEqual(len(a['plan']['candidate_coverage']),2)
        self.assertFalse(a['plan']['modify'])

if __name__=='__main__':unittest.main()
