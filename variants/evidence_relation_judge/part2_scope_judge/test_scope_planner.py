import copy
import unittest
from pathlib import Path
import json

import scope_planner as s

HERE = Path(__file__).resolve().parent.parent

def sample():
    req = json.loads((HERE/'runs/real_cases_20261106/promotion_input.json').read_text())
    rel = json.loads((HERE/'runs/controlled_v2_20261106/promotion_run.json').read_text())['result']
    return req, rel

class ScopeTests(unittest.TestCase):
    def test_original_predicate_is_extracted_and_known_limitation(self):
        self.assertTrue(s.facttrack_overlap(0, 3, 1, 4, True))
        self.assertFalse(s.facttrack_overlap(0, 4, 1, 3, True))
        self.assertEqual(s.compare_intervals((0, 4, True, True), (1, 3, True, True)), 'contains')

    def test_interval_edges_and_unknown(self):
        self.assertEqual(s.compare_intervals((0,1,True,False),(1,2,True,True)), 'before')
        self.assertEqual(s.compare_intervals((0,1,True,True),(1,2,True,True)), 'touches')
        self.assertEqual(s.compare_intervals((0,1,True,True),(0,1,True,True)), 'equal')
        self.assertEqual(s.compare_intervals(None, (0,1,True,True)), 'unknown')

    def test_upstream_error_and_record_time_never_expire(self):
        req, rel = sample(); rel['results'][0]['status']='error'; rel['results'][0]['errors']=[{'message':'bad'}]
        result=s.plan_scope(req,rel)
        row=result['results'][0]
        self.assertEqual(row['status'], 'upstream_error')
        self.assertEqual(row['boundary']['kind'], 'unknown')
        self.assertEqual(row['upstream']['errors'][0]['message'], 'bad')
        self.assertFalse(row['modifications'])
        self.assertTrue(row['additions'])

    def test_ambiguous_fragment_never_locates_or_modifies(self):
        req, rel = sample(); text=req['split_result']['memory_text']; req['split_result']['memory_text']=text+'; '+text
        row=s.plan_scope(req,rel)['results'][0]
        self.assertIn('fragment_not_unique', [x['code'] for x in row['pending']])
        self.assertFalse(row['modifications'])

    def test_duplicate_or_missing_upstream_rows(self):
        req, rel=sample(); rel['results'].append(copy.deepcopy(rel['results'][0]))
        self.assertEqual(s.plan_scope(req,rel)['results'][0]['status'],'upstream_error')
        rel['results']=[]
        self.assertEqual(s.plan_scope(req,rel)['results'][0]['status'],'upstream_error')

    def test_bad_quote_or_candidate_identity_is_error(self):
        req, rel=sample(); rel['results'][0]['candidate']['new_quote']['quote']='fabricated'
        rel['results'][0]['located_candidate']['new_quote']['quote']='fabricated'
        self.assertEqual(s.plan_scope(req,rel)['results'][0]['status'],'upstream_error')

    def test_all_evidence_preserved_without_inventing_semantics(self):
        req,rel=sample(); out=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(out['upstream']['semantic_correctness'],'not_checked')
        self.assertEqual(out['relation']['classification'],'unknown')
        self.assertEqual(out['additions'][0]['text'],req['new_evidence'][0]['text'])
        self.assertEqual(out['nli']['status'],'disabled')
        self.assertEqual(out['protected'][0]['text'],req['split_result']['memory_text'])

    def test_failed_nli_is_reported(self):
        req,rel=sample()
        def broken(a,b): raise RuntimeError('no model')
        nli=s.plan_scope(req,rel,nli=broken)['results'][0]['nli']
        self.assertEqual(nli['status'],'error'); self.assertIn('no model', nli['error'])

if __name__=='__main__': unittest.main()

class SourcedTimeTests(unittest.TestCase):
    def test_sourced_periods_call_facttrack_and_create_window_candidate(self):
        req, rel = sample()
        req['source_context'][0]['text'] += ' The old role held from 2024-01-01 through 2024-12-31.'
        req['new_evidence'][0]['text'] += ' The new role held from 2025-01-01 through 2025-12-31.'
        req['time_info']=[
            {'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-12-31','source_id':'old-context-1','quote':'The old role held from 2024-01-01 through 2024-12-31.'},
            {'side':'new','kind':'valid_period','start':'2025-01-01','end':'2025-12-31','source_id':'dialogue-0','quote':'The new role held from 2025-01-01 through 2025-12-31.'}]
        row=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(row['time']['interval_relation'],'before')
        self.assertEqual(row['boundary']['kind'],'window_candidate')
        self.assertEqual(row['facttrack']['status'],'called')
        self.assertFalse(row['modifications'])

    def test_invalid_time_quote_does_not_become_validity(self):
        req, rel=sample()
        req['time_info']=[{'side':'new','kind':'valid_period','start':'2025-01-01','end':'2025-12-31','source_id':'dialogue-0','quote':'fabricated 2025-01-01 2025-12-31'}]
        row=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(row['time']['interval_relation'],'unknown')
        self.assertTrue(row['time']['errors'])

class OriginalExecutionTests(unittest.TestCase):
    def test_original_three_methods_run_on_isolated_known_nonblocking_interval(self):
        result=s.facttrack_original_probe((10, 20), (30, 40), block_verdict=False)
        self.assertEqual(result['status'], 'called')
        self.assertEqual(result['calls'], ['interval_blockCheck', 'interval_contradictCheck', 'interval_insert'])
        self.assertEqual(result['inserted_fact_count'], 2)
        self.assertEqual(result['existing_interval_after'], [10,20])

    def test_probe_declines_semantically_unassessed_pairs(self):
        self.assertEqual(s.facttrack_original_probe((10,20),(30,40),block_verdict=None)['status'],'not_called')

class ProvenanceTests(unittest.TestCase):
    def test_time_side_must_match_source_collection(self):
        req,rel=sample()
        req['new_evidence'][0]['text']+=' 2025-01-01 2025-12-31'
        req['time_info']=[{'side':'old','kind':'valid_period','start':'2025-01-01','end':'2025-12-31','source_id':'dialogue-0','quote':'2025-01-01 2025-12-31'}]
        row=s.plan_scope(req,rel)['results'][0]
        self.assertFalse(row['time']['period_candidates']['old'])
        self.assertTrue(row['time']['errors'])

    def test_failed_nli_adds_pending_issue(self):
        req,rel=sample()
        def broken(a,b): raise RuntimeError('no model')
        row=s.plan_scope(req,rel,nli=broken)['results'][0]
        self.assertIn('nli_error',[p['code'] for p in row['pending']])

class ExtractionTests(unittest.TestCase):
    def test_extractor_candidates_are_sourced_and_not_accepted_as_truth(self):
        req,rel=sample()
        def extract(payload):
            return {'comparability':'comparable', 'reason':'candidate only', 'old':{'object':'user','attribute':'position','conditions':'at company'},
                    'new':{'object':'user','attribute':'position','conditions':'at company'},
                    'new_facts':[{'text':'promotion candidate','source_id':'dialogue-0','quote':'I recently got promoted'}]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['extraction']['status'],'ok')
        self.assertEqual(row['relation']['classification'],'unknown')
        self.assertEqual(row['extraction']['result']['comparability'],'comparable')
        self.assertEqual(row['extraction']['semantic_correctness'],'not_checked')
        self.assertEqual(row['extraction']['new_fact_candidates'][0]['source_id'],'dialogue-0')

    def test_extractor_bad_citation_is_recorded(self):
        req,rel=sample()
        def extract(payload): return {'new_facts':[{'text':'fabrication','source_id':'dialogue-0','quote':'missing'}]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['extraction']['status'],'error')
        self.assertIn('extraction_error',[p['code'] for p in row['pending']])

class MultiFactTimeTests(unittest.TestCase):
    def test_unassigned_time_not_applied_to_all_facts(self):
        req, rel=sample()
        fact=copy.deepcopy(req['split_result']['facts'][0]); fact['fact_index']=2
        req['split_result']['facts'].append(fact)
        req['new_evidence'][0]['text']+=' 2025-01-01 2025-12-31'
        req['time_info']=[{'side':'new','kind':'valid_period','start':'2025-01-01','end':'2025-12-31','source_id':'dialogue-0','quote':'2025-01-01 2025-12-31'}]
        rows=s.plan_scope(req,rel)['results']
        for row in rows:
            self.assertFalse(row['time']['period_candidates']['new'])
            self.assertTrue(row['time']['errors'])

class CandidateComparisonTests(unittest.TestCase):
    def test_same_extracted_fields_are_candidates_not_verified_facts(self):
        req,rel=sample()
        def extract(payload):
            return {'comparability':'different','old':{'subject':'User','object':'Company','attribute':'position','value':'Director','conditions':'at Company'},
                    'new':{'subject':'User','object':'Company','attribute':'position','value':'Lead Director','conditions':'at Company'},'new_facts':[]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['scope_assessment']['status'],'same_scope_candidate')
        self.assertEqual(row['scope_assessment']['value_relation'],'different_text')
        self.assertFalse(row['scope_assessment']['semantic_verified'])
        self.assertIn('extractor_comparison_disagreement',[p['code'] for p in row['pending']])
        self.assertEqual(row['relation']['classification'],'unknown')

    def test_missing_conditions_remain_unknown(self):
        req,rel=sample()
        def extract(payload):
            return {'old':{'subject':'User','object':'x','attribute':'x','conditions':''}, 'new':{'subject':'User','object':'x','attribute':'x','conditions':''},'new_facts':[]}
        self.assertEqual(s.plan_scope(req,rel,extractor=extract)['results'][0]['scope_assessment']['status'],'unknown')


def correction_sample(memory='My favorite color is blue; I enjoy hiking.',
                      evidence='Correction: my favorite color is green, not blue.'):
    req,rel=sample()
    split=req['split_result']; mid='synthetic-memory-1'; fact=split['facts'][0]
    split['memory_id']=mid; fact['source_memory_id']=mid
    split['memory_text']=memory
    fact.update(raw_subfact=memory,contextualized_subfact=memory,
                evidence=[{'source_type':'memory','source_id':mid,'quote':memory,'supports':'memory'}],pending_confirmations=[])
    req['source_context']=[]; req['time_info']=None
    req['new_evidence']=[{'source_id':'new-1','text':evidence,'speaker':'user'}]
    row=rel['results'][0]; row['memory_id']=mid; row['old_subfact']=memory
    c=copy.deepcopy(row['candidate']); c.update(memory_id=mid,old_subfact=memory,relation='historical_correction',object='user',attribute='favorite color',conditions='',candidate_impact_fragment=memory,old_quote=memory,new_quote={'source_id':'new-1','quote':evidence},reason='candidate',confirmation_questions=[])
    row['candidate']=copy.deepcopy(c); row['located_candidate']=copy.deepcopy(c)
    row['fragment_match']={'raw':memory,'located':memory,'method':'exact','start':0,'end':len(memory)}
    row['status']='ok'; row['validation']={'passed':True,'semantic_correctness':'not_checked'}
    return req,rel

class LocalCorrectionTests(unittest.TestCase):
    def test_explicit_correction_produces_local_review_candidate_and_protects_rest(self):
        req,rel=correction_sample(); row=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(len(row['modifications']),1)
        patch=row['modifications'][0]
        self.assertEqual((patch['old_text'],patch['proposed_text']),('blue','green'))
        self.assertEqual(req['split_result']['memory_text'][patch['span']['start']:patch['span']['end']],'blue')
        self.assertEqual(patch['time_effect']['state'],'unknown')
        self.assertEqual(patch['status'],'needs_review')
        self.assertTrue(any('I enjoy hiking' in x['text'] for x in row['protected']))
        self.assertEqual(patch['evidence_refs'][1]['source_id'],'new-1')

    def test_conflicting_corrections_must_not_produce_modification(self):
        req,rel=correction_sample(); req['new_evidence'].append({'source_id':'new-2','text':'Correction: my favorite color is red, not blue.','speaker':'user'})
        row=s.plan_scope(req,rel)['results'][0]
        self.assertFalse(row['modifications'])
        self.assertIn('conflicting_corrections',[p['code'] for p in row['pending']])

    def test_duplicate_old_fragment_or_negated_context_not_modified(self):
        for memory in ['My favorite color is blue; My favorite color is blue.', 'Not my favorite color is blue; I enjoy hiking.', 'If my favorite color is blue; I enjoy hiking.']:
            with self.subTest(memory=memory):
                req,rel=correction_sample(memory=memory)
                self.assertFalse(s.plan_scope(req,rel)['results'][0]['modifications'])

    def test_unreliable_v2_prevents_even_explicit_correction(self):
        req,rel=correction_sample(); rel['results'][0]['status']='error'
        self.assertFalse(s.plan_scope(req,rel)['results'][0]['modifications'])

    def test_mismatched_attribute_never_replaces_value(self):
        req,rel=correction_sample(evidence='Correction: my work city is green, not blue.')
        self.assertFalse(s.plan_scope(req,rel)['results'][0]['modifications'])

    def test_duplicate_additions_merge_source_provenance(self):
        req,rel=correction_sample(); text=req['new_evidence'][0]['text']
        req['new_evidence'].append({'source_id':'new-2','text':text,'speaker':'user'})
        def extract(payload): return {'new_facts':[{'text':text,'source_id':'new-1','quote':text}]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(len(row['additions']),1)
        self.assertEqual({r['source_id'] for r in row['additions'][0]['evidence_refs']},{'new-1','new-2'})
        self.assertIn('extracted_candidate',row['additions'][0]['kinds'])

class LocalCorrectionEdgeTests(unittest.TestCase):
    def test_conflicting_corrections_in_one_source_are_not_ignored(self):
        req,rel=correction_sample(evidence='Correction: my favorite color is green, not blue. Correction: my favorite color is red, not blue.')
        row=s.plan_scope(req,rel)['results'][0]
        self.assertFalse(row['modifications'])
        self.assertIn('conflicting_corrections',[p['code'] for p in row['pending']])

    def test_nearby_correction_does_not_modify_a_different_subfact(self):
        req,rel=correction_sample(memory='My favorite color is blue; My hobby is hiking.')
        f=req['split_result']['facts'][0]; f['raw_subfact']='My hobby is hiking.'; f['contextualized_subfact']=f['raw_subfact']
        r=rel['results'][0]; r['old_subfact']=f['raw_subfact']
        for key in ('candidate','located_candidate'):
            r[key]['old_subfact']=f['raw_subfact']; r[key]['candidate_impact_fragment']='My hobby is hiking.'
        row=s.plan_scope(req,rel)['results'][0]
        self.assertFalse(row['modifications'])

    def test_case_difference_is_not_collapsed_as_identical_evidence(self):
        req,rel=correction_sample(); req['new_evidence'].append({'source_id':'new-2','text':req['new_evidence'][0]['text'].upper(),'speaker':'user'})
        row=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(len(row['additions']),2)

class FieldEvidenceTests(unittest.TestCase):
    def test_field_citations_are_checked_without_claiming_semantic_truth(self):
        req,rel=sample()
        def extractor(payload):
            return {'old':{'attribute':'position'}, 'new':{'attribute':'position'}, 'new_facts':[],
              'field_evidence':{'old':{'attribute':[{'source_id':'old-context-1','quote':'as a Director'}]},
                                'new':{'attribute':[{'source_id':'dialogue-0','quote':'promoted to lead director'}]}}}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        refs=row['extraction']['field_evidence']
        self.assertEqual(refs['old']['attribute']['status'],'literal_quote_verified')
        self.assertEqual(refs['new']['attribute']['status'],'literal_quote_verified')
        self.assertFalse(refs['old']['attribute']['semantic_verified'])
        self.assertEqual(refs['old']['attribute']['refs'][0]['source_id'],'old-context-1')

    def test_bad_field_citation_is_exposed_and_not_used(self):
        req,rel=sample()
        def extractor(payload):
            return {'old':{'attribute':'position'},'new':{},'new_facts':[],
                    'field_evidence':{'old':{'attribute':[{'source_id':'dialogue-0','quote':'not a quote'}]}}}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['extraction']['field_evidence']['old']['attribute']['status'],'invalid')
        self.assertIn('field_evidence_invalid',[p['code'] for p in row['pending']])

class ExclusivityAndTemporalFlowTests(unittest.TestCase):
    def test_exclusivity_candidate_needs_valid_quote_and_stays_unverified(self):
        req,rel=sample()
        def extractor(payload):
            return {'new_facts':[],'exclusivity':{'candidate':'mutually_exclusive','reason':'candidate',
                'evidence':[{'source_id':'dialogue-0','quote':'promoted to lead director'}]}}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['relation']['exclusivity']['candidate'],'mutually_exclusive')
        self.assertEqual(row['relation']['exclusivity']['evidence_status'],'literal_quote_verified')
        self.assertFalse(row['relation']['exclusivity']['semantic_verified'])
        self.assertEqual(row['relation']['classification'],'unknown')

    def test_unsupported_exclusivity_is_unknown(self):
        req,rel=sample()
        def extractor(payload): return {'new_facts':[],'exclusivity':{'candidate':'mutually_exclusive','evidence':[{'source_id':'dialogue-0','quote':'absent'}]}}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['relation']['exclusivity']['candidate'],'unknown')
        self.assertIn('exclusivity_evidence_invalid',[p['code'] for p in row['pending']])

    def test_facttrack_predicate_participates_in_overlap_path(self):
        req,rel=sample()
        req['source_context'][0]['text']+=' Old period 2024-01-01 through 2024-08-01.'
        req['new_evidence'][0]['text']+=' New period 2024-05-01 through 2024-12-01.'
        req['time_info']=[{'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-08-01','source_id':'old-context-1','quote':'Old period 2024-01-01 through 2024-08-01.'},
                          {'side':'new','kind':'valid_period','start':'2024-05-01','end':'2024-12-01','source_id':'dialogue-0','quote':'New period 2024-05-01 through 2024-12-01.'}]
        row=s.plan_scope(req,rel)['results'][0]
        self.assertEqual(row['time']['interval_relation'],'overlap')
        self.assertEqual(row['facttrack']['decision_path'],'original_overlap_true')
        self.assertTrue(row['facttrack']['original_pre_overlap'])
        self.assertEqual(row['relation']['classification'],'unknown')

class PlanDedupTests(unittest.TestCase):
    def test_top_level_additions_are_deduplicated_across_facts(self):
        req,rel=sample()
        fact=copy.deepcopy(req['split_result']['facts'][0]); fact['fact_index']=2; req['split_result']['facts'].append(fact)
        row=copy.deepcopy(rel['results'][0]); row['fact_index']=2
        row['candidate']['fact_index']=2; row['located_candidate']['fact_index']=2
        rel['results'].append(row)
        out=s.plan_scope(req,rel)
        self.assertEqual(len(out['additions']),1)
        self.assertEqual(out['additions'][0]['fact_indices'],[1,2])

    def test_global_dedup_keeps_all_source_references(self):
        req,rel=correction_sample(); req['new_evidence'].append({'source_id':'new-2','text':req['new_evidence'][0]['text'],'speaker':'user'})
        out=s.plan_scope(req,rel)
        self.assertEqual({x['source_id'] for x in out['additions'][0]['evidence_refs']},{'new-1','new-2'})

class RelationCandidateTests(unittest.TestCase):
    def test_cited_exclusivity_and_overlap_form_only_unverified_conflict_candidate(self):
        req,rel=sample()
        req['source_context'][0]['text']+=' Old period 2024-01-01 through 2024-08-01.'
        req['new_evidence'][0]['text']+=' New period 2024-05-01 through 2024-12-01.'
        req['time_info']=[{'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-08-01','source_id':'old-context-1','quote':'Old period 2024-01-01 through 2024-08-01.'},
                          {'side':'new','kind':'valid_period','start':'2024-05-01','end':'2024-12-01','source_id':'dialogue-0','quote':'New period 2024-05-01 through 2024-12-01.'}]
        def extractor(payload):
            return {'old':{'subject':'user','object':'company','attribute':'position','conditions':'same company','value':'Director'},
                    'new':{'subject':'user','object':'company','attribute':'position','conditions':'same company','value':'lead director'},
                    'new_facts':[], 'field_evidence':{side:{field:[{'source_id':sid,'quote':quote}] for field in ('subject','object','attribute','conditions','value')} for side,sid,quote in [('old','old-context-1','I work at Historical Productions Ltd. as a Director.'),('new','dialogue-0','promoted to lead director')]},
                    'exclusivity':{'candidate':'mutually_exclusive','reason':'model candidate','evidence':[{'source_id':'dialogue-0','quote':'promoted to lead director'}]}}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['relation']['candidate_assessment']['kind'],'conflict_candidate')
        self.assertFalse(row['relation']['candidate_assessment']['semantic_verified'])
        self.assertEqual(row['relation']['classification'],'unknown')
        self.assertFalse(row['modifications'])

class MissingProvenanceGateTests(unittest.TestCase):
    def test_uncited_model_fields_cannot_yield_conflict_candidate(self):
        req,rel=sample()
        req['source_context'][0]['text']+=' Old period 2024-01-01 through 2024-08-01.'
        req['new_evidence'][0]['text']+=' New period 2024-05-01 through 2024-12-01.'
        req['time_info']=[{'side':'old','kind':'valid_period','start':'2024-01-01','end':'2024-08-01','source_id':'old-context-1','quote':'Old period 2024-01-01 through 2024-08-01.'},
                          {'side':'new','kind':'valid_period','start':'2024-05-01','end':'2024-12-01','source_id':'dialogue-0','quote':'New period 2024-05-01 through 2024-12-01.'}]
        def extract(payload):
            dimensions={'subject':'user','object':'company','attribute':'position','conditions':'at company','value':'director'}
            return {'old':dimensions,'new':dimensions,'new_facts':[], 'exclusivity':{'candidate':'mutually_exclusive','evidence':[{'source_id':'dialogue-0','quote':'promoted to lead director'}]}}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['relation']['candidate_assessment']['kind'],'unknown')
        self.assertIn('field_evidence_missing',[p['code'] for p in row['pending']])

class CrossFactModificationTests(unittest.TestCase):
    def test_duplicate_cross_fact_patch_is_single_plan_candidate(self):
        req,rel=correction_sample()
        fact=copy.deepcopy(req['split_result']['facts'][0]); fact['fact_index']=2; req['split_result']['facts'].append(fact)
        row=copy.deepcopy(rel['results'][0]); row['fact_index']=2
        row['candidate']['fact_index']=2; row['located_candidate']['fact_index']=2
        rel['results'].append(row)
        out=s.plan_scope(req,rel)
        self.assertEqual(len(out['modifications']),1)
        self.assertEqual(out['modifications'][0]['fact_indices'],[1,2])
        self.assertEqual(out['modifications'][0]['proposed_text'],'green')

class NewQuoteRecoveryTests(unittest.TestCase):
    def test_unique_case_only_new_quote_recovery_preserves_raw(self):
        req,rel=sample()
        def extractor(payload):
            return {'new_facts':[{'text':'candidate','source_id':'dialogue-0','quote':'i recently got promoted'}]}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['extraction']['status'],'ok')
        self.assertEqual(row['extraction']['result']['new_facts'][0]['quote'],'i recently got promoted')
        found=row['extraction']['new_fact_candidates'][0]
        self.assertEqual(found['quote'],'I recently got promoted')
        self.assertEqual(found['quote_match']['method'],'unique_casefold')

    def test_ambiguous_case_recovery_still_fails(self):
        req,rel=sample(); req['new_evidence'][0]['text']+=' I recently got promoted'
        def extractor(payload): return {'new_facts':[{'text':'candidate','source_id':'dialogue-0','quote':'i recently got promoted'}]}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(row['extraction']['status'],'error')

class GreetingDedupTests(unittest.TestCase):
    def test_exact_source_with_leading_greeting_and_extracted_fact_are_merged(self):
        req,rel=sample()
        original=req['new_evidence'][0]['text']; req['new_evidence'][0]['text']='Hey, '+original
        # Existing new_quote remains an exact substring of the longer source.
        def extractor(payload): return {'new_facts':[{'text':original,'source_id':'dialogue-0','quote':original}]}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(len(row['additions']),1)
        self.assertIn('extracted_candidate',row['additions'][0]['kinds'])
        self.assertEqual(row['additions'][0]['text'],'Hey, '+original)

    def test_substring_with_substantive_extra_context_is_not_collapsed(self):
        req,rel=sample(); original=req['new_evidence'][0]['text']
        def extractor(payload): return {'new_facts':[{'text':'I recently got promoted','source_id':'dialogue-0','quote':'I recently got promoted'}]}
        row=s.plan_scope(req,rel,extractor=extractor)['results'][0]
        self.assertEqual(len(row['additions']),2)

class AdditionSupportTests(unittest.TestCase):
    def test_partial_quote_does_not_claim_support_for_full_candidate(self):
        req,rel=sample(); whole=req['new_evidence'][0]['text']
        def extract(payload): return {'new_facts':[{'text':whole,'source_id':'dialogue-0','quote':'promoted to lead director'}]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['extraction']['new_fact_candidates'][0]['support_status'],'quote_partial_for_literal_text')
        self.assertIn('new_fact_quote_partial',[p['code'] for p in row['pending']])

    def test_paraphrase_is_not_verified_by_literal_quote(self):
        req,rel=sample()
        def extract(payload): return {'new_facts':[{'text':'They own a company','source_id':'dialogue-0','quote':'promoted to lead director'}]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertEqual(row['extraction']['new_fact_candidates'][0]['support_status'],'paraphrase_unverified')
        self.assertIn('new_fact_semantics_unverified',[p['code'] for p in row['pending']])

class LocalProtectionTests(unittest.TestCase):
    def test_matching_source_backed_employer_is_local_protection_candidate(self):
        req,rel=sample()
        def extract(payload):
            return {'old':{'object':'Historical Productions Ltd.'},'new':{'object':'Historical Productions Ltd.'},'new_facts':[],
                'field_evidence':{'old':{'object':[{'source_id':req['split_result']['memory_id'],'quote':'Historical Productions Ltd.'}]},
                                  'new':{'object':[{'source_id':'dialogue-0','quote':'Historical Productions Ltd.'}]}}}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        local=[p for p in row['protected'] if p.get('kind')=='protected_candidate']
        self.assertEqual(len(local),1)
        self.assertEqual(local[0]['text'],'Historical Productions Ltd.')
        self.assertEqual(local[0]['semantic_correctness'],'not_checked')
        self.assertFalse(row['modifications'])

    def test_unverified_or_missing_field_quotes_do_not_create_local_protection(self):
        req,rel=sample()
        def extract(payload):return {'old':{'object':'Historical Productions Ltd.'},'new':{'object':'Historical Productions Ltd.'},'new_facts':[]}
        row=s.plan_scope(req,rel,extractor=extract)['results'][0]
        self.assertFalse([p for p in row['protected'] if p.get('kind')=='protected_candidate'])

class PlanConflictSafetyTests(unittest.TestCase):
    def test_overlapping_candidates_are_removed_and_whole_memory_protected(self):
        from scope_actions import combine_modifications
        req,rel=correction_sample(); base=s.plan_scope(req,rel)['results'][0]
        left=copy.deepcopy(base); right=copy.deepcopy(base); right['fact_index']=2
        right['modifications'][0]['proposed_text']='red'
        self.assertEqual(combine_modifications([left,right]),[])
        for row in (left,right):
            self.assertEqual(row['modifications'],[])
            self.assertEqual(row['protected'][0]['text'],req['split_result']['memory_text'])
            self.assertIn('overlapping_modifications',[p['code'] for p in row['pending']])
