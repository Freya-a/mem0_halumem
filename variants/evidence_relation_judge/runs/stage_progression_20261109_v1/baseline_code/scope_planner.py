"""Review-only scope planner. No memory writes; extracted FactTrack predicate is diagnostic."""
from __future__ import annotations
import ast
from datetime import date
from types import SimpleNamespace
from copy import deepcopy
import hashlib
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'part1_relation_judge'))
import relation_judge as v1
import relation_judge_v2 as v2
from scope_actions import deduplicate_additions, explicit_correction, combine_additions, combine_modifications, local_protection_candidates
from scope_evidence import validate_field_evidence, assess_exclusivity

FACTTRACK = Path(__file__).resolve().parents[5] / 'external/FactTrack/fact-track/core/contradict_detector.py'
FACTTRACK_SHA256 = 'a2ffd889e955440af3ef4f39995b3e4a3e06c80b7d8e6d2d59a4212e8282c51f'


def _original_overlap():
    """Compile the original nested is_overlap, with no imports or class initialisation."""
    source = FACTTRACK.read_bytes()
    if hashlib.sha256(source).hexdigest() != FACTTRACK_SHA256:
        raise ValueError('FactTrack source hash mismatch')
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ContradictDetector_StatusPersistence')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'interval_contradictCheck')
    node = next(n for n in method.body if isinstance(n, ast.FunctionDef) and n.name == 'is_overlap')
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    scope = {}
    exec(compile(module, str(FACTTRACK), 'exec'), {'__builtins__': {}}, scope)
    return scope['is_overlap']


def facttrack_overlap(l, r, l1, r1, is_pre):
    return _original_overlap()(l, r, l1, r1, is_pre)


def compare_intervals(a, b):
    """Finite, exact endpoints only, represented as (start,end,start_closed,end_closed)."""
    if a is None or b is None:
        return 'unknown'
    try:
        al, ar, ac, ad = a; bl, br, bc, bd = b
        if any(type(x) is not bool for x in (ac, ad, bc, bd)):
            return 'unknown'
        if al > ar or bl > br or (al == ar and not (ac and ad)) or (bl == br and not (bc and bd)):
            return 'unknown'
        if ar < bl or (ar == bl and not (ad and bc)): return 'before'
        if br < al or (br == al and not (bd and ac)): return 'after'
        if a == b: return 'equal'
        if ar == bl or br == al: return 'touches'
        a_contains = (al < bl or (al == bl and (ac or not bc))) and (ar > br or (ar == br and (ad or not bd)))
        b_contains = (bl < al or (bl == al and (bc or not ac))) and (br > ar or (br == ar and (bd or not ad)))
        if a_contains: return 'contains'
        if b_contains: return 'contained_by'
        return 'overlap'
    except (TypeError, ValueError):
        return 'unknown'


def _unique(text, fragment):
    return bool(fragment) and sum(text.startswith(fragment, i) for i in range(len(text))) == 1


def _nli(nli, old, new):
    if nli is None: return {'status': 'disabled'}
    try:
        result = nli(old, new)
        if not isinstance(result, dict): raise TypeError('NLI must return an audit dictionary')
        return {'status': 'ok', **result}
    except Exception as exc:
        return {'status': 'error', 'error': f'{type(exc).__name__}: {exc}'}


def facttrack_original_probe(old_interval, new_interval, *, block_verdict=None):
    """Execute all three original methods on an isolated illustrative post-fact state.

    The caller supplies a verdict; the probe never manufactures an NLI score. It
    abstains where the original conflict path would require an NLI inference.
    Its synthetic pre/post assignment, epsilon and endpoints are diagnostic only.
    """
    if type(block_verdict) is not bool:
        return {'status':'not_called','reason':'no independently supplied block verdict'}
    ol,orr=old_interval; nl,nr=new_interval
    if not (ol < orr and nl < nr):
        return {'status':'not_called','reason':'invalid finite interval'}
    if facttrack_overlap(nl,nr,ol,orr,False):
        return {'status':'not_called','reason':'original conflict branch requires actual similarity and NLI models'}
    source=FACTTRACK.read_bytes()
    if hashlib.sha256(source).hexdigest()!=FACTTRACK_SHA256: raise ValueError('FactTrack source hash mismatch')
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ContradictDetector_StatusPersistence')
    names=('interval_blockCheck','interval_contradictCheck','interval_insert')
    methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
    namespace={'get_embedding_contriever':lambda fact:fact, '__builtins__':__builtins__}
    module=ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name='OriginalMethods',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[]))
    exec(compile(module,str(FACTTRACK),'exec'),namespace)
    detector=namespace['OriginalMethods']()
    old=['old', 'old', ol, orr, 'old', 'old source']
    detector.prefactList=[deepcopy(old)]; detector.postfactList=[deepcopy(old)]
    detector.epsilon=1e-6; detector.max_resident_candidate=3; detector.max_contradict_query=5
    detector.similarity_threshold=0.5; detector.nli_threshold=0.2359
    detector.block_check_reset=lambda:None
    detector.block_check=lambda *args:(block_verdict,None,None,True)
    detector.standardize_log=lambda *args,**kwargs:None
    l,r=detector.interval_blockCheck('new',nl,'new',isPreFact=False)
    flag,meta=detector.interval_contradictCheck('new',nl,nr,'new',isPreFact=False)
    detector.interval_insert('new',nl,nr,'new','new source',isPreFact=False)
    return {'status':'called','calls':list(names),'original_block_interval':[l,r],
            'original_conflict_flag':flag,'original_conflict_items':meta,
            'existing_interval_after':detector.postfactList[0][2:4], 'inserted_fact_count':len(detector.postfactList),
            'block_verdict_source':'caller-supplied, no NLI',
            'limitations':'synthetic pre/post assignment; copied state; sentinel and epsilon retained; no decision applied'}


def _facttrack_order(method_name, list_name, rows):
    """Execute the original method's actual sorting expression on isolated list data."""
    source = FACTTRACK.read_bytes()
    if hashlib.sha256(source).hexdigest() != FACTTRACK_SHA256:
        raise ValueError('FactTrack source hash mismatch')
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ContradictDetector_StatusPersistence')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    for node in ast.walk(method):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == list_name for t in node.targets):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'sorted':
                expression=ast.fix_missing_locations(ast.Expression(body=node.value))
                return eval(compile(expression, str(FACTTRACK), 'eval'), {'__builtins__': {'sorted':sorted}, 'self':SimpleNamespace(prefactList=rows, postfactList=rows)})
    raise ValueError('FactTrack ordering expression missing')


def _intervals(request, fact_index):
    sources={x['source_id']:x['text'] for x in request.get('source_context',[])+request.get('new_evidence',[])}
    side_sources={'old':{x['source_id'] for x in request.get('source_context',[])}, 'new':{x['source_id'] for x in request.get('new_evidence',[])}}
    found={'old':[], 'new':[]}; errors=[]
    raw=request.get('time_info')
    if raw is None: return found, errors
    if not isinstance(raw, list): return found, [{'reason':'time_info is not a list of sourced validity candidates', 'raw':raw}]
    for item in raw:
        try:
            if isinstance(item,dict) and item.get('fact_index') is not None and item.get('fact_index') != fact_index:
                continue
            if len(request['split_result']['facts']) > 1 and isinstance(item,dict) and item.get('fact_index') is None:
                raise ValueError('time evidence must identify fact_index when multiple facts exist')
            if not isinstance(item,dict) or item.get('side') not in found or item.get('kind') != 'valid_period':
                raise ValueError('unsupported time entry')
            if item.get('source_id') not in side_sources[item['side']]:
                raise ValueError('time source does not belong to the stated side')
            quote=item.get('quote'); text=sources.get(item.get('source_id'))
            if not isinstance(quote,str) or not quote or not text or quote not in text:
                raise ValueError('time quote missing or not in source')
            if item['start'] not in quote or item['end'] not in quote:
                raise ValueError('dates not present in source quote')
            start=date.fromisoformat(item['start']); end=date.fromisoformat(item['end'])
            if start>end: raise ValueError('period ends before it starts')
            found[item['side']].append({'start':start.isoformat(),'end':end.isoformat(), 'source_id':item['source_id'], 'quote':quote, 'semantic_correctness':'not_checked'})
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({'reason':str(exc), 'raw':item})
    return found,errors


def _assess_time(request, fact_index):
    time=_times(request); found,errors=_intervals(request, fact_index)
    time.update(period_candidates=found, errors=errors, interval_relation='unknown')
    boundary={'kind':'unknown','reason':'no validated explicit validity boundary'}
    trace={'status':'not_called','reason':'exact sourced period candidates unavailable; record times are not validity intervals'}
    if len(found['old'])==1 and len(found['new'])==1 and not errors:
        old,new=found['old'][0],found['new'][0]
        a=(date.fromisoformat(old['start']).toordinal(),date.fromisoformat(old['end']).toordinal(),True,True)
        b=(date.fromisoformat(new['start']).toordinal(),date.fromisoformat(new['end']).toordinal(),True,True)
        # Facts use the author's [fact, embedding, l, r, plot_idx, plot_text] shape.
        entries=[['old',None,a[0],a[1],'old',old['quote']], ['new',None,b[0],b[1],'new',new['quote']]]
        try:
            trace={'status':'called','source_sha256':FACTTRACK_SHA256,
                   'block_check_pre_order':[x[0] for x in _facttrack_order('interval_blockCheck','prefactList',entries)],
                   'insert_pre_order':[x[0] for x in _facttrack_order('interval_insert','prefactList',entries)],
                   'original_pre_overlap':facttrack_overlap(a[0],a[1],b[0],b[1],True),
                   'original_post_overlap':facttrack_overlap(a[0],a[1],b[0],b[1],False),
                   'role':'original ordering and overlap predicate; no original models, thresholds, state mutation or validity inference'}
            if trace['original_pre_overlap'] or trace['original_post_overlap']:
                time['interval_relation']='overlap'
                trace['decision_path']='original_overlap_true'
            else:
                time['interval_relation']=compare_intervals(a,b)
                trace['decision_path']='general_interval_fallback'
        except Exception as exc:
            trace={'status':'error','error':f'{type(exc).__name__}: {exc}','decision_path':'general_interval_fallback'}
            time['interval_relation']=compare_intervals(a,b)
        order=trace.get('block_check_pre_order')
        chronological_order = order is None or (order.index('new') < order.index('old'))
        if time['interval_relation']=='before' and chronological_order:
            if order is not None: trace['boundary_order_used']='block_check_pre_order'
            boundary={'kind':'window_candidate','earliest':old['end'],'latest':new['start'],
                      'evidence':[old,new], 'conditions':['time expressions actually denote valid periods','same object, attribute and conditions','mutually exclusive states','a state transition occurred'],
                      'reason':'conditional window between supplied periods; neither event nor exclusivity is established'}
    return time,boundary,trace


def _times(request):
    """Preserve all metadata, but recording time is never a validity endpoint."""
    observations = []
    for source in request.get('source_context', []) + request.get('new_evidence', []):
        if source.get('recorded_at'):
            observations.append({'kind': 'recorded', 'source_id': source['source_id'], 'value': source['recorded_at'], 'validity_effect': 'none'})
    expressions = []
    for source in request.get('source_context', []) + request.get('new_evidence', []):
        for match in re.finditer(r'\b(recently|previously|lately|for now)\b', source['text'], re.I):
            expressions.append({'source_id': source['source_id'], 'quote': match.group(), 'resolution': 'unresolved', 'reason': 'no validated event-time anchor'})
    return {'valid_start': {'state':'unknown'}, 'valid_end': {'state':'unknown'}, 'time_info_raw': deepcopy(request.get('time_info')), 'recorded_times': observations, 'expressions': expressions}


def _candidate_scope(extracted):
    """Compare literal model-proposed dimensions, never assert semantic equality."""
    old=extracted.get('old'); new=extracted.get('new')
    out={'status':'unknown','field_comparisons':{},'value_relation':'unknown','semantic_verified':False,
         'reason':'literal comparison of unverified model candidates; no semantic entailment or exclusivity established'}
    if not isinstance(old,dict) or not isinstance(new,dict): return out
    for field in ('subject','object','attribute','conditions','modality','value'):
        a,b=old.get(field),new.get(field)
        if not isinstance(a,str) or not isinstance(b,str) or not a.strip() or not b.strip():
            comparison='unknown'
        elif a.strip().casefold()==b.strip().casefold(): comparison='same_text'
        else: comparison='different_text'
        out['field_comparisons'][field]={'old':a,'new':b,'comparison':comparison}
    out['value_relation']=out['field_comparisons']['value']['comparison']
    gate=[out['field_comparisons'][f]['comparison'] for f in ('subject','object','attribute','conditions')]
    if all(x=='same_text' for x in gate): out['status']='same_scope_candidate'
    return out


def _relation_candidate(scope, exclusivity, time):
    result={'kind':'unknown','semantic_verified':False,'conditions':[],
            'reason':'candidate fields, mutual exclusivity, and temporal relation require independent support'}
    if scope.get('status')!='same_scope_candidate' or exclusivity.get('candidate')!='mutually_exclusive':
        return result
    fields=scope.get('field_comparisons',{})
    if any(fields.get(field,{}).get('source_refs',{}).get(side,{}).get('status')!='literal_quote_verified'
           for field in ('subject','object','attribute','conditions','value') for side in ('old','new')):
        result['reason']='one or more required model fields lack source quotes'
        return result
    relation=time.get('interval_relation')
    if relation in ('overlap','contains','contained_by','equal','touches'):
        result['kind']='conflict_candidate'
    elif relation in ('before','after'):
        result['kind']='temporal_change_candidate'
    if result['kind']!='unknown':
        result['conditions']=['verify field evidence and same subject, object, attribute, conditions',
                              'verify mutually exclusive values and proposition meanings',
                              'verify cited periods are the actual validity periods',
                              'do not infer action from this candidate alone']
        result['time_relation_candidate']=relation
        result['exclusivity']=deepcopy(exclusivity)
    return result


def plan_scope(request, relation_result, *, nli=None, extractor=None):
    """Accept the complete v4/v2 input; candidates remain unverified and review-only."""
    request, relation_result = deepcopy(request), deepcopy(relation_result)
    output = {'status':'needs_review', 'request':request, 'relation_result':relation_result, 'results':[], 'errors':[]}
    try:
        new_map = v1.validate_request(request)
        if set(x['source_id'] for x in request.get('source_context', [])) & set(new_map):
            raise ValueError('source IDs collide across source collections')
    except Exception as exc:
        output.update(status='input_error', errors=[{'type':type(exc).__name__, 'message':str(exc)}])
        return output
    split = request['split_result']; memory = split['memory_text']
    incoming = relation_result.get('results', []) if isinstance(relation_result, dict) else []
    if not isinstance(incoming, list): incoming=[]
    expected={(split['memory_id'],f['fact_index']) for f in split['facts']}
    extras=[deepcopy(r) for r in incoming if not isinstance(r,dict) or (r.get('memory_id'),r.get('fact_index')) not in expected]
    if extras: output['errors'].append({'type':'unmatched_upstream_rows', 'rows':extras})
    for fact in split['facts']:
        mid, idx = split['memory_id'], fact['fact_index']
        matched=[r for r in incoming if isinstance(r,dict) and r.get('memory_id')==mid and r.get('fact_index')==idx]
        upstream = matched[0] if len(matched)==1 else None
        row={'memory_id':mid,'fact_index':idx,'memory_text':memory,'memory_sha256':hashlib.sha256(memory.encode()).hexdigest(),
             'old_fact':fact,'status':'needs_review','upstream':{'full_row':upstream, 'semantic_correctness':'not_checked', 'errors':[]},
             'time':_times(request), 'boundary':{'kind':'unknown','reason':'no validated explicit validity boundary'},
             'relation':{'classification':'unknown','reason':'object, attribute, conditions and exclusivity require independent semantic assessment'},
             'modifications':[], 'protected':[{'text':fact['raw_subfact'], 'reason':'scope and semantic impact not verified; protect complete fact', 'evidence_refs':deepcopy(fact['evidence'])}],
             'pending':[{'code':'semantic_scope_unverified','reason':'v2 label and fragment are candidates only'}],
             'additions':[{'text':src['text'],'source_id':src['source_id'],'quote':src['text'],'kind':'raw_evidence_candidate','dedupe':'unchecked','semantic_correctness':'not_checked'} for src in request['new_evidence']],
             'nli':{'status':'not_called','reason':'upstream failure or missing source'},
             'extraction':{'status':'not_called','reason':'disabled or upstream failure'},
             'scope_assessment':{'status':'unknown','semantic_verified':False,'reason':'no independent extraction'},
             'facttrack':{'status':'not_called','reason':'exact valid intervals unavailable; record times are not validity intervals'}}
        row['time'], row['boundary'], row['facttrack'] = _assess_time(request, idx)
        if row['time']['errors']:
            row['pending'].append({'code':'time_evidence_invalid','detail':row['time']['errors']})
        for item in fact.get('pending_confirmations', []): row['pending'].append({'code':'upstream_confirmation','detail':item})
        try:
            if len(matched)!=1: raise ValueError('missing or duplicate upstream row')
            if upstream.get('status')!='ok' or upstream.get('validation',{}).get('passed') is not True:
                raise ValueError('upstream row failed validation')
            if upstream.get('old_subfact') != fact['raw_subfact']: raise ValueError('upstream old fact mismatch')
            candidate=upstream.get('located_candidate')
            v1.validate_candidate(candidate,split,fact,new_map)
            original=upstream.get('candidate')
            if not isinstance(original,dict): raise ValueError('missing raw candidate')
            recomputed=v2.locate_fragment(memory,original.get('candidate_impact_fragment'),[e['quote'] for e in fact['evidence'] if e['source_type']=='memory'])
            if recomputed['located'] != candidate['candidate_impact_fragment']: raise ValueError('raw and located candidate mismatch')
            row['fragment_match_rechecked']=recomputed
            frag=candidate['candidate_impact_fragment']
            if not _unique(memory,frag) or recomputed['start'] is None:
                row['pending'].append({'code':'fragment_not_unique','reason':'fragment is absent, outside fact, or not unique in memory'})
            if _unique(memory,frag) and recomputed['start'] is not None:
                changes, protection, issues = explicit_correction(memory, fact, request['new_evidence'], recomputed)
                row['modifications'] = changes
                if changes: row['protected'] = protection
                row['pending'].extend(issues)
            for q in candidate['confirmation_questions']:
                row['pending'].append({'code':'upstream_question_unverified','question':q})
            row['relation']['upstream_candidate']=deepcopy(candidate)
            if extractor is not None:
                extraction_raw=None
                try:
                    extraction_raw=extractor({'memory_id':mid,'memory_text':memory,'fact':fact,
                        'source_context':request.get('source_context',[]),'new_evidence':request['new_evidence'],
                        'time_info':request.get('time_info'),'relation_candidate':candidate})
                    if not isinstance(extraction_raw,dict): raise ValueError('extractor must return an object')
                    new_facts=deepcopy(extraction_raw.get('new_facts',[]))
                    if not isinstance(new_facts,list): raise ValueError('new_facts must be a list')
                    for item in new_facts:
                        if not isinstance(item,dict) or not isinstance(item.get('text'),str) or not item['text'].strip(): raise ValueError('invalid new fact')
                        q=item.get('quote'); sid=item.get('source_id')
                        if not isinstance(sid,str) or sid not in new_map or not isinstance(q,str) or not q: raise ValueError('new fact quote/source mismatch')
                        match=v2.locate_fragment(new_map[sid],q,[new_map[sid]])
                        if match['located'] is None: raise ValueError('new fact quote/source mismatch: '+str(match['method']))
                        item['quote_match']=match
                        item['quote']=match['located']
                        if item['text'] in item['quote']:
                            item['support_status']='literal_text_in_quote'
                        elif item['text'] in new_map[sid]:
                            item['support_status']='quote_partial_for_literal_text'
                            row['pending'].append({'code':'new_fact_quote_partial','source_id':sid,'text':item['text']})
                        else:
                            item['support_status']='paraphrase_unverified'
                            row['pending'].append({'code':'new_fact_semantics_unverified','source_id':sid,'text':item['text']})
                    row['extraction']={'status':'ok','result':extraction_raw,'semantic_correctness':'not_checked',
                        'new_fact_candidates':deepcopy(new_facts),'note':'literal citation only; no entailment or comparability confirmed'}
                    row['relation']['exclusivity'], exclusivity_issues = assess_exclusivity(extraction_raw, request, fact)
                    row['pending'].extend(exclusivity_issues)
                    row['extraction']['field_evidence'], evidence_issues = validate_field_evidence(extraction_raw, request, fact)
                    row['pending'].extend(evidence_issues)
                    row['scope_assessment']=_candidate_scope(extraction_raw)
                    for dimension, comparison in row['scope_assessment'].get('field_comparisons',{}).items():
                        comparison['source_refs']={side:deepcopy(row['extraction']['field_evidence'][side][dimension]) for side in ('old','new')}
                    missing=[{'side':side,'field':field} for side in ('old','new') for field, value in extraction_raw.get(side,{}).items()
                             if field in row['extraction']['field_evidence'][side] and isinstance(value,str) and value.strip() and row['extraction']['field_evidence'][side][field]['status']=='missing'] if all(isinstance(extraction_raw.get(side,{}),dict) for side in ('old','new')) else []
                    if missing: row['pending'].append({'code':'field_evidence_missing','fields':missing})
                    row['protected'].extend(local_protection_candidates(memory, fact, row['scope_assessment'], row['modifications']))
                    row['relation']['candidate_assessment']=_relation_candidate(row['scope_assessment'],row['relation']['exclusivity'],row['time'])
                    if row['scope_assessment']['status']=='same_scope_candidate' and extraction_raw.get('comparability')=='different':
                        row['pending'].append({'code':'extractor_comparison_disagreement','reason':'same candidate fields but extractor says different; value difference does not settle scope'})
                    row['additions'].extend({'text':x['text'],'source_id':x['source_id'],'quote':x['quote'],
                        'kind':'extracted_candidate','dedupe':'unchecked','semantic_correctness':'not_checked','support_status':x['support_status']} for x in new_facts)
                except Exception as exc:
                    row['extraction']={'status':'error','error':f'{type(exc).__name__}: {exc}','raw':extraction_raw}
                    row['pending'].append({'code':'extraction_error','reason':str(exc)})
            quote=candidate['new_quote']
            row['nli']=_nli(nli,fact['contextualized_subfact'],quote['quote'])
            if row['nli']['status']=='error':
                row['pending'].append({'code':'nli_error','reason':row['nli']['error']})
        except Exception as exc:
            row['status']='upstream_error'
            row['upstream']['errors']=deepcopy(upstream.get('errors',[])) if isinstance(upstream,dict) else []
            row['upstream']['errors'].append({'stage':'scope_alignment','type':type(exc).__name__,'message':str(exc)})
            row['pending'].append({'code':'upstream_error','reason':str(exc)})
        row['additions']=deduplicate_additions(row['additions'])
        output['results'].append(row)
    output['modifications']=combine_modifications(output['results'])
    output['additions']=combine_additions(output['results'])
    return output
