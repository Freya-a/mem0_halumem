"""Offline A/B/C authorization comparison; B is unreviewed and never writes memory."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
RUN = PROJECT / 'variants/evidence_aligner/v4_scope_interface/runs/qwen_20261124_once'
FIXTURES = PROJECT / 'variants/evidence_scope_planner/v2_offline/fixtures'
V3 = PROJECT / 'variants/evidence_scope_planner/v3_offline/scope_planner.py'
FROZEN = RUN / 'frozen_at_call/interface.py'
CASES = ('susan', 'promotion', 'career_history', 'transition', 'skydiving')


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


interface = _module('comparison_v4_interface', FROZEN)
planner = _module('comparison_v3_planner', V3)


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(data):
    return hashlib.sha256(canonical(data).encode('utf-8')).hexdigest()


def make_new_only(record):
    """Project only existing new claim; prior relationship is kept separately."""
    r = copy.deepcopy(record)
    r.update(unit_id=None, relation='new_information', old_subject=None, old_attribute=None,
             old_value=None, old_conditions={'kind':'unknown'}, old_quotes=[],
             temporal_order={'relation':'unknown','basis':[], 'explanation':None})
    r['semantic_basis'] = [x for x in r.get('semantic_basis', [])
                           if isinstance(x,dict) and x.get('side') == 'new']
    return r


def _mark(a, index, kind, suffix=''):
    a['note'] = f'B:model_record={index};candidate={kind}{suffix}'
    a['authorization_origin'] = 'model_candidate_only'
    return a


def _quote_eligible(validation, index, has_old):
    checks=[q for q in validation.get('quote_checks',[]) if q.get('record_index')==index]
    new=[q for q in checks if q.get('side')=='new']
    old=[q for q in checks if q.get('side')=='old']
    return bool(new) and all(q.get('status')=='valid' for q in checks) and (not has_old or bool(old))


def _parts(value):
    """Only split explicit semicolon-separated model text; no inferred facts."""
    if not isinstance(value,str): return [value]
    parts=[x.strip() for x in value.split(';')]
    return parts if len(parts)>1 and all(parts) else [value]


def compare_case(payload, model_output):
    validation=interface.validate_output(model_output,payload)
    old,units,sources,base=interface.planner_inputs(payload,model_output)
    a_args=(old,copy.deepcopy(units),copy.deepcopy(sources),copy.deepcopy(base))
    a_plan=planner.build_scope_plan(*copy.deepcopy(a_args))
    b=copy.deepcopy(base)
    raw_records=model_output.get('records',[]) if isinstance(model_output,dict) else []
    for i,rec in enumerate(raw_records):
        if i>=len(b) or not isinstance(rec,dict): continue
        # This only models the B policy; v3 sees its compatibility flag, but
        # the origin is explicitly model-only and is never independent review.
        if _quote_eligible(validation,i,rec.get('unit_id') is not None):
            b[i]['semantic_support']='supported'
        _mark(b[i],i,'relation')
        if rec.get('relation') != 'change': continue
        for part_index,part in enumerate(_parts(rec.get('new_value'))):
            new_record=make_new_only(rec)
            new_record['new_value']=part
            # same_as_old cannot define a standalone assertion's scope.
            scope=new_record.get('new_conditions')
            inherited_scope=False
            if isinstance(scope,dict) and scope.get('kind')=='same_as_old':
                prior=rec.get('old_conditions')
                if isinstance(prior,dict) and prior.get('kind') in ('unconditional','finite'):
                    new_record['new_conditions']=copy.deepcopy(prior)
                    inherited_scope=True
                else:
                    new_record['new_conditions']={'kind':'unknown'}
            if part_index>0 and isinstance(part,str):
                # A further explicit clause can cite an already-linked new
                # quote only if that same text is an exact substring.
                matching=[q for q in rec.get('new_quotes',[]) if isinstance(q,dict)
                          and isinstance(q.get('quote'),str) and part.lower() in q['quote'].lower()]
                new_record['semantic_basis']=[{'side':'new','source_id':q['source_id'],'quote':q['quote']}
                                              for q in matching]
            # Isolated candidate is validated on new side; omission of other
            # input units is coverage metadata, not a record-specific error.
            isolated={'records':[new_record], 'unmatched_old_unit_ids':[u['unit_id'] for u in payload['old_units']]}
            part_validation=interface.validate_output(isolated,payload)
            projected=interface.adapt_output(isolated,payload)[0]
            if _quote_eligible(part_validation,0,False): projected['semantic_support']='supported'
            if isinstance(scope,dict) and scope.get('kind')=='same_as_old' and not inherited_scope:
                projected['validation_errors'].append('new-only scope cannot be inferred from old scope')
            suffix=f';part={part_index}' + (';scope=model_old_conditions' if inherited_scope else '')
            b.append(_mark(projected,i,'new_subfact',suffix))
    b_plan=planner.build_scope_plan(old,copy.deepcopy(units),copy.deepcopy(sources),copy.deepcopy(b))
    # A new-only proposal that duplicates an already-proposed modification is
    # not a separate independent add. Preserve it separately for review.
    suppressed=[]
    for item in list(b_plan['add']):
        note=item.get('note') or ''
        if 'candidate=new_subfact' not in note: continue
        prefix=note.split(';candidate=',1)[0]
        if any((m.get('note') or '').startswith(prefix+';candidate=relation') for m in b_plan['modify']):
            b_plan['add'].remove(item)
            suppressed.append({'item':item,'reason':'same model record already proposed as modify; avoid duplicate add'})
    emitted = {i: False for i in range(len(raw_records))}
    for category in ('modify', 'preserve', 'uncertain', 'add'):
        for item in b_plan[category]:
            note=item.get('note') or ''
            for i in emitted:
                if note.startswith(f'B:model_record={i};candidate=relation'):
                    emitted[i]=True
    relation_coverage = [{'record_index':i, 'relation_emitted':seen,
                          'reason': None if seen else 'planner output contains no decision for this original relation; inspect same-unit aggregation and source record'}
                         for i,seen in emitted.items()]
    return {'validation':validation,
            'A':{'alignments':a_args[3],'plan':a_plan,'authorization':'independent_required'},
            'B':{'alignments':b,'plan':b_plan,'suppressed_duplicate_adds':suppressed,
                 'relation_coverage':relation_coverage,
                 'authorization':'model_candidate_only'}}


def load_human(case):
    d=json.loads((FIXTURES/(case+'.json')).read_text(encoding='utf-8'))
    units=[{**u,'memory_id':d['memory_id'],'source_ref':d['old_memory_source_ref']} for u in d['units']]
    args=(d['old_memory'],units,d['sources'],d['alignments'])
    return {'input_provenance':d['input_provenance'],'alignments':d['alignments'],
            'plan':planner.build_scope_plan(*copy.deepcopy(args)), 'authorization':'existing_human_reviewed_input'}


def main():
    out=HERE/'results';out.mkdir(exist_ok=True)
    manifest=json.loads((RUN/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status')!='completed' or manifest.get('request_attempts')!=5:
        raise ValueError('saved run does not contain the complete five-case trial')
    counts={}
    for case in CASES:
        path=RUN/(case+'.json');raw=path.read_bytes();a=json.loads(raw)
        if json.loads(a['raw_response'])!=a['result']['parsed']:
            raise ValueError(f'{case}: parsed response differs from raw response')
        result=compare_case(a['prepared_input'],a['result']['parsed'])
        result['C']=load_human(case)
        # The three projections must refer to the same saved case. Human input
        # may select a subset of the available sources and different units.
        human=json.loads((FIXTURES/(case+'.json')).read_text(encoding='utf-8'))
        source_texts=a['prepared_input']['source_texts']
        if human['old_memory'] != source_texts['memory']['text']:
            raise ValueError(f'{case}: human and model old memory differ')
        available={s['source_id']:s for s in source_texts['messages']}
        for source in human['sources']:
            found=available.get(source['source_id'])
            if not found or any(found.get(k) != source.get(k) for k in ('text','source_ref')):
                raise ValueError(f"{case}: human source differs: {source['source_id']}")
        result.update(case_id=case, model_call=False, old_memory=a['prepared_input']['source_texts']['memory'],
                      prepared_input=a['prepared_input'], raw_model_output=a['result']['parsed'],
                      artifact_sha256=hashlib.sha256(raw).hexdigest(),
                      expected=json.loads((FIXTURES/(case+'.expected.json')).read_text(encoding='utf-8')))
        old_plan=json.loads((PROJECT/'variants/evidence_scope_planner/v3_offline/results'/(case+'.json')).read_text())['projections']['unprotected']['v3']
        if result['A']['plan'] != old_plan: raise ValueError(f'{case}: A does not reproduce prior v3 baseline')
        result['A']['matches_existing_baseline']=True
        for group in ('A','B','C'):
            result[group]['plan_sha256']=digest(result[group]['plan'])
        (out/(case+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        counts[case]={g:{k:len(result[g]['plan'][k]) for k in ('modify','preserve','uncertain','add')} for g in ('A','B','C')}
        print(case,canonical(counts[case]))
    m={'model_calls':0,'cases':list(CASES),'planner_sha256':hashlib.sha256(V3.read_bytes()).hexdigest(),
       'adapter_sha256':hashlib.sha256(FROZEN.read_bytes()).hexdigest(),'counts':counts}
    (out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
