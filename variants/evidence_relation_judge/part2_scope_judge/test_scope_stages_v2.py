import copy
import json
from pathlib import Path
import unittest

import scope_planner_v2 as planner

HERE=Path(__file__).resolve().parent.parent
RUN=HERE/'runs/dev_scope_review_20261109_v1'

def original(name):
    d=json.loads((RUN/f'{name}_result.json').read_text())
    return d['request'], d['relation_result']

def proposal(req, new_id, new_quote, old_fragment, old_stage, new_stage, cue, protected=()):
    text=req['split_result']['memory_text']; mid=req['split_result']['memory_id']
    return {'same_subject':'same','same_issue':'same','relation':'progressed',
       'new_phase_status':'completed', 'old_phase':{'text':old_stage,'source_id':mid,'quote':text,'impact_fragment':old_fragment},
       'new_phase':{'text':new_stage,'source_id':new_id,'quote':new_quote,'completion_cue':cue},
       'link_explanation':'A candidate relation requiring semantic review',
       'protected_fragments':list(protected)}

class StagePlanTests(unittest.TestCase):
    def test_completed_stage_proposes_sourced_relative_history_without_exact_date(self):
        req,rel=original('job_transition'); new=req['new_evidence'][0]['text']
        p=proposal(req,'dialogue-0',new,req['split_result']['memory_text'],'looking','transitioned','transitioned')
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        c=out['historicalizations'][0]
        self.assertEqual(c['old_phase']['text'],'looking')
        self.assertEqual(c['new_phase']['text'],'transitioned')
        self.assertEqual(c['time']['exact_transition_time']['state'],'unknown')
        self.assertEqual(c['time']['relative_order'],'old_before_new_candidate')
        self.assertEqual(c['status'],'needs_review')
        self.assertEqual(c['evidence_refs'][1]['source_id'],'dialogue-0')
        self.assertFalse(c['semantic_verified'])

    def test_promotion_preserves_employer_and_scope(self):
        req,rel=original('promotion'); quote=req['new_evidence'][0]['text']
        p=proposal(req,'dialogue-0',quote,'Director','Director role','lead director role','promoted',['Historical Productions Ltd.'])
        c=planner.plan_scope(req,rel,stage_extractor=lambda _:p)['historicalizations'][0]
        self.assertEqual(c['impact']['text'],'Director')
        self.assertEqual(c['protected'][0]['text'],'Historical Productions Ltd.')
        self.assertTrue(c['protected'][0]['span']['end']<=c['impact']['span']['start'])

    def test_unresolved_or_different_identity_never_suggests_history(self):
        req,rel=original('job_transition');p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','transitioned')
        for key,val in [('same_subject','different'),('same_issue','unknown'),('relation','unknown'),('new_phase_status','in_progress')]:
            with self.subTest(key=key):
                q=copy.deepcopy(p);q[key]=val
                out=planner.plan_scope(req,rel,stage_extractor=lambda _:q)
                self.assertFalse(out['historicalizations'])
                self.assertEqual(out['results'][0]['stage_assessment']['status'],'needs_confirmation')

    def test_unverified_or_noncompletion_cue_cannot_form_history(self):
        req,rel=original('job_transition');p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','healthier')
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertFalse(out['historicalizations'])
        self.assertEqual(out['results'][0]['stage_assessment']['status'],'needs_confirmation')

    def test_negated_or_conditional_completion_is_not_completed(self):
        req,rel=original('job_transition');req['new_evidence'][0]['text']='I have not transitioned to a new role.'
        row=rel['results'][0]
        for key in ('candidate','located_candidate'):
            row[key]['new_quote']['quote']=req['new_evidence'][0]['text']
        p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','transitioned')
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertFalse(out['historicalizations'])

    def test_unlocatable_source_and_upstream_error_are_preserved(self):
        req,rel=original('job_transition');p=proposal(req,'dialogue-0','fabricated transitioned',req['split_result']['memory_text'],'old','new','transitioned')
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertFalse(out['historicalizations']);self.assertEqual(out['results'][0]['stage_assessment']['status'],'error')
        rel['results'][0]['status']='error';out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertFalse(out['historicalizations']);self.assertEqual(out['results'][0]['status'],'upstream_error')

    def test_ambiguous_fragment_and_protection_overlap_are_rejected(self):
        req,rel=original('promotion');p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],'Director','old','new','promoted',['Director'])
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertFalse(out['historicalizations']);self.assertEqual(out['results'][0]['stage_assessment']['status'],'error')

    def test_backend_failure_remains_error_not_no_change(self):
        req,rel=original('promotion')
        def broken(_):raise RuntimeError('backend unavailable')
        out=planner.plan_scope(req,rel,stage_extractor=broken)
        self.assertEqual(out['results'][0]['stage_assessment']['status'],'error')
        self.assertIn('backend unavailable',out['results'][0]['stage_assessment']['error'])
        self.assertFalse(out['historicalizations'])

class EvidenceGateTests(unittest.TestCase):
    def test_old_subject_not_established_from_memory_alone(self):
        req,rel=original('job_transition');req['source_context']=[]
        fact=req['split_result']['facts'][0];fact['evidence']=[e for e in fact['evidence'] if e['source_type']=='memory']
        p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],fact['raw_subfact'],'old','new','transitioned')
        row=planner.plan_scope(req,rel,stage_extractor=lambda _:p)['results'][0]
        self.assertEqual(row['stage_assessment']['status'],'needs_confirmation')
        self.assertFalse(row.get('historicalizations'))

    def test_opposite_explicit_new_evidence_requires_confirmation(self):
        req,rel=original('job_transition')
        req['new_evidence'].append({'source_id':'dialogue-conflict','speaker':'user','text':'I have not transitioned yet.'})
        p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','transitioned')
        row=planner.plan_scope(req,rel,stage_extractor=lambda _:p)['results'][0]
        self.assertEqual(row['stage_assessment']['status'],'needs_confirmation')
        self.assertFalse(row.get('historicalizations'))

    def test_uncertain_semantics_may_omit_unavailable_phase_text(self):
        req,rel=original('promotion')
        result={'same_subject':'same','same_issue':'unknown','relation':'unknown','new_phase_status':'unknown',
                'old_phase':{},'new_phase':{},'link_explanation':'insufficient evidence','protected_fragments':[]}
        row=planner.plan_scope(req,rel,stage_extractor=lambda _:result)['results'][0]
        self.assertEqual(row['stage_assessment']['status'],'needs_confirmation')

class CrossFactStageTests(unittest.TestCase):
    def test_duplicate_same_stage_plan_is_merged_across_facts(self):
        req,rel=original('job_transition')
        fact=copy.deepcopy(req['split_result']['facts'][0]);fact['fact_index']=2;req['split_result']['facts'].append(fact)
        row=copy.deepcopy(rel['results'][0]);row['fact_index']=2
        for k in ('candidate','located_candidate'):row[k]['fact_index']=2
        rel['results'].append(row)
        p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','transitioned')
        out=planner.plan_scope(req,rel,stage_extractor=lambda _:p)
        self.assertEqual(len(out['historicalizations']),1)
        self.assertEqual(out['historicalizations'][0]['fact_indices'],[1,2])

    def test_overlapping_different_stage_proposals_require_joint_review(self):
        req,rel=original('job_transition')
        fact=copy.deepcopy(req['split_result']['facts'][0]);fact['fact_index']=2;req['split_result']['facts'].append(fact)
        row=copy.deepcopy(rel['results'][0]);row['fact_index']=2
        for k in ('candidate','located_candidate'):row[k]['fact_index']=2
        rel['results'].append(row)
        p=proposal(req,'dialogue-0',req['new_evidence'][0]['text'],req['split_result']['memory_text'],'old','new','transitioned')
        def extract(payload):
            q=copy.deepcopy(p)
            if payload['fact']['fact_index']==2:q['old_phase']['impact_fragment']='Looking for a new job'
            return q
        out=planner.plan_scope(req,rel,stage_extractor=extract)
        self.assertFalse(out['historicalizations'])
        self.assertTrue(all(any(x['code']=='overlapping_stage_candidates' for x in r['pending']) for r in out['results']))
