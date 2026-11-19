"""Evidence-constrained phase proposals layered over the unchanged scope planner.

All semantic assessments, including entity and episode matching, are model
candidates for human review. No operation in this module writes memories.
"""
from copy import deepcopy
import re

import scope_planner as baseline

# General completion cues, not task-specific decision rules. Deliberately narrow:
# other forms abstain until separately supported and evaluated.
_COMPLETION = re.compile(r'\b(?:transitioned|promoted|completed|finished|graduated|approved|joined|retired|resigned|departed|moved|delivered|launched|opened|closed|won|secured|started|began|became|ended|married)\b|(?:已经|已完成|已晋升|已获批|已毕业|已退休|已离职)',re.I)
_UNCERTAIN = re.compile(r"\b(?:not|never|neither|no|if|unless|might|may|could|would|planning|planned|considering|consider|hopes?|wants?|intend|intends|will|expects?|anticipated|possibly|perhaps)\b|(?:尚未|没有|如果|可能|计划|希望|考虑|尚无)",re.I)


def _span(memory, fragment):
    if not isinstance(fragment,str) or not fragment:raise ValueError('empty impact or protection fragment')
    matches=[i for i in range(len(memory)) if memory.startswith(fragment,i)]
    if len(matches)!=1:raise ValueError('fragment not uniquely located')
    return {'start':matches[0],'end':matches[0]+len(fragment)}


def _assessment(request, fact, proposal):
    if not isinstance(proposal,dict):raise ValueError('stage extractor must return an object')
    for key in ('same_subject','same_issue','relation','new_phase_status','old_phase','new_phase','link_explanation','protected_fragments'):
        if key not in proposal:raise ValueError('missing stage field: '+key)
    if proposal['same_subject'] not in ('same','different','unknown') or proposal['same_issue'] not in ('same','different','unknown'):
        raise ValueError('invalid subject or issue assessment')
    if proposal['relation'] not in ('progressed','coexists','different','unknown') or proposal['new_phase_status'] not in ('completed','in_progress','planned','unknown'):
        raise ValueError('invalid phase assessment')
    if not isinstance(proposal['link_explanation'],str) or not proposal['link_explanation'].strip():raise ValueError('missing link explanation')
    for key,expected in (('same_subject','same'),('same_issue','same'),('relation','progressed'),('new_phase_status','completed')):
        if proposal[key]!=expected:
            return {'status':'needs_confirmation','reason':f'{key}={proposal[key]} does not establish completed same-issue progression','proposal':proposal}
    old,new=proposal['old_phase'],proposal['new_phase']
    if not isinstance(old,dict) or not isinstance(new,dict):raise ValueError('invalid phase object')
    for key in ('text','source_id','quote','impact_fragment'):
        if not isinstance(old.get(key),str) or not old[key].strip():raise ValueError('missing old phase field: '+key)
    for key in ('text','source_id','quote','completion_cue'):
        if not isinstance(new.get(key),str):raise ValueError('missing new phase field: '+key)
    if not new['text'].strip() or not new['quote'].strip():raise ValueError('missing new phase text or quote')
    memory=request['split_result']['memory_text'];mid=request['split_result']['memory_id'];frag=old['impact_fragment']
    if old['source_id']!=mid or old['quote'] not in memory:raise ValueError('old phase quote/source mismatch')
    if frag not in old['quote'] or frag not in fact['raw_subfact']:raise ValueError('impact fragment is outside the old fact or old quote')
    impact=_span(memory,frag)
    if not any(e.get('source_type')=='memory' and old['quote'] in e.get('quote','') for e in fact.get('evidence',[])):
        raise ValueError('old phase is outside fact evidence')
    context={x['source_id']:x for x in request.get('source_context',[])}
    subject_refs=[{'source_type':'context','source_id':e['source_id'],'quote':e['quote']} for e in fact.get('evidence',[])
                  if e.get('source_type')=='context' and e.get('source_id') in context
                  and context[e['source_id']].get('speaker')=='user'
                  and re.search(r'\b(?:I|my|me|mine)\b|我|本人',e.get('quote',''),re.I)]
    if not subject_refs:
        return {'status':'needs_confirmation','reason':'no linked first-person user context for old subject','proposal':proposal}
    sources={x['source_id']:x for x in request['new_evidence']};source=sources.get(new['source_id'])
    if not source or new['quote'] not in source['text']:raise ValueError('new phase quote/source mismatch')
    if source.get('speaker')!='user':return {'status':'needs_confirmation','reason':'new phase speaker is not established user','proposal':proposal}
    if not isinstance(proposal['protected_fragments'],list) or any(not isinstance(x,str) for x in proposal['protected_fragments']):raise ValueError('invalid protected fragments')
    protected=[]
    for x in proposal['protected_fragments']:
        position=_span(memory,x)
        if position['start']<impact['end'] and impact['start']<position['end']:raise ValueError('protection overlaps affected span')
        if x not in fact['raw_subfact']:raise ValueError('protected fragment outside old fact')
        protected.append({'text':x,'span':position,'reason':'model-proposed protection, verify semantic role'})
    for key,expected in (('same_subject','same'),('same_issue','same'),('relation','progressed'),('new_phase_status','completed')):
        if proposal[key]!=expected:
            return {'status':'needs_confirmation','reason':f'{key}={proposal[key]} does not establish completed same-issue progression','proposal':proposal}
    cue=new['completion_cue']
    if not cue or cue not in new['quote'] or not _COMPLETION.search(cue):
        return {'status':'needs_confirmation','reason':'no supported completion cue in new quote','proposal':proposal}
    if _UNCERTAIN.search(new['quote']):
        return {'status':'needs_confirmation','reason':'new quote contains negation, condition or uncertain modality','proposal':proposal}
    cue_word=_COMPLETION.search(cue).group()
    conflicting=[x['source_id'] for x in request['new_evidence'] if x['source_id']!=new['source_id']
                 and x.get('speaker')=='user' and re.search(r'\b'+re.escape(cue_word)+r'\b',x['text'],re.I)
                 and _UNCERTAIN.search(x['text'])]
    if conflicting:return {'status':'needs_confirmation','reason':'other source contains negated or uncertain completion cue','conflicting_sources':conflicting,'proposal':proposal}
    return {'status':'candidate','proposal':proposal,'impact':{'text':frag,'span':impact},'protected':protected,
            'source_refs':[{'source_type':'memory','source_id':mid,'quote':old['quote']},
                           {'source_type':'new','source_id':new['source_id'],'quote':new['quote']}],
            'subject_refs':subject_refs,'checks':['unique old span','old fact evidence','first-person user context candidate','new user source quote','literal completion cue','model-proposed same subject and issue'],
            'semantic_verified':False}


def plan_scope(request, relation_result, *, nli=None, extractor=None, stage_extractor=None):
    """Generate review-only historicalization candidates without altering v1 behavior."""
    result=baseline.plan_scope(request,relation_result,nli=nli,extractor=extractor)
    result['historicalizations']=[]
    if result.get('status')=='input_error':return result
    facts={f['fact_index']:f for f in request['split_result']['facts']}
    for row in result['results']:
        row['stage_assessment']={'status':'not_called','reason':'disabled or upstream error'}
        if row['status']=='upstream_error' or stage_extractor is None:continue
        fact=facts[row['fact_index']]
        # Deliberately withhold v2/v3's label and fragment from this independent pass.
        payload={'memory_id':row['memory_id'],'memory_text':request['split_result']['memory_text'],'fact':deepcopy(fact),
                 'source_context':deepcopy(request.get('source_context',[])),
                 'new_evidence':deepcopy(request['new_evidence']),'time_info':deepcopy(request.get('time_info'))}
        raw=None
        try:
            raw=stage_extractor(payload)
            assessed=_assessment(request,fact,raw)
            row['stage_assessment']=assessed
            if assessed['status']!='candidate':
                row['pending'].append({'code':'phase_relation_unresolved','reason':assessed['reason']})
                continue
            impact=assessed['impact'];span=impact['span']
            if any(span['start']<x['span']['end'] and x['span']['start']<span['end'] for x in row['modifications']):
                row['stage_assessment']['status']='needs_confirmation'
                row['stage_assessment']['reason']='overlapping modification candidate'
                row['pending'].append({'code':'phase_modification_overlap'})
                continue
            p=assessed['proposal']
            history={'kind':'historicalization_candidate','status':'needs_review','semantic_verified':False,
                'memory_id':row['memory_id'],'memory_sha256':row['memory_sha256'],'fact_index':row['fact_index'],
                'old_phase':deepcopy(p['old_phase']),'new_phase':deepcopy(p['new_phase']),
                'impact':impact,'protected':deepcopy(assessed['protected']),
                'time':{'relative_order':'old_before_new_candidate','exact_transition_time':{'state':'unknown'},
                        'basis':'model-proposed stage relation; timestamps are not change dates'},
                'evidence_refs':deepcopy(assessed['source_refs']), 'old_subject_context':deepcopy(assessed['subject_refs']), 'link_explanation':p['link_explanation'],
                'conditions':['verify same subject and episode/attribute from cited evidence',
                    'retain old content as historical and preserve surrounding conditions',
                    'verify granularity and scope; do not treat candidate as a write instruction'],
                'proposed_text':None}
            row.setdefault('historicalizations',[]).append(history)
            row['pending'].append({'code':'historicalization_semantics_unverified','reason':'same episode, transition and protected scope require human review'})
            result['historicalizations'].append(history)
        except Exception as exc:
            row['stage_assessment']={'status':'error','error':f'{type(exc).__name__}: {exc}','raw':raw}
            row['pending'].append({'code':'stage_extraction_error','reason':str(exc)})
    proposals=result['historicalizations']; conflicts=set()
    def identity(x):
        return (x['impact']['span']['start'],x['impact']['span']['end'],x['old_phase']['text'],
                x['new_phase']['text'],x['new_phase']['source_id'],x['new_phase']['quote'],
                tuple(y['text'] for y in x['protected']))
    for i,a in enumerate(proposals):
        for j in range(i+1,len(proposals)):
            b=proposals[j]; aa=a['impact']['span'];bb=b['impact']['span']
            if aa['start']<bb['end'] and bb['start']<aa['end'] and identity(a)!=identity(b):conflicts.update((i,j))
    for i in conflicts:
        candidate=proposals[i]
        row=next(r for r in result['results'] if r['fact_index']==candidate['fact_index'])
        row['historicalizations'].remove(candidate)
        row['stage_assessment']['status']='needs_confirmation'
        row['stage_assessment']['reason']='overlapping stage candidates need joint review'
        row['pending'].append({'code':'overlapping_stage_candidates','candidate':deepcopy(candidate)})
    groups={};result['historicalizations']=[]
    for i,candidate in enumerate(proposals):
        if i in conflicts:continue
        key=identity(candidate)
        if key not in groups:
            group=deepcopy(candidate);group['fact_indices']=[]
            groups[key]=group;result['historicalizations'].append(group)
        if candidate['fact_index'] not in groups[key]['fact_indices']:
            groups[key]['fact_indices'].append(candidate['fact_index'])
    return result
