"""Two-stage model facts/relations -> coverage planner; never authorizes semantics."""
import copy
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def _load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
v4=_load('saved_v4_interface',HERE.parent/'v4_scope_interface/runs/qwen_20261124_once/frozen_at_call/interface.py')
planner=_load('coverage_planner',ROOT/'variants/evidence_scope_planner/candidate_coverage_20261124/scope_planner.py')
FACT_FIELDS=('fact_id','subject','attribute','value','conditions','modality','quotes','rationale','uncertainties')
REL_FIELDS=('relation_id','fact_id','unit_id','relation','old_subject','old_attribute','old_value','old_conditions','old_quotes','affected_part','temporal_order','rationale','semantic_basis','uncertainties')
RELATIONS={'change','same','supplement','unrelated','unknown'}

def prepare_input(case):return v4.prepare_input(case)

def _safe_id(x):return isinstance(x,str) and bool(x.strip())
def _new_basis(quotes):
    if not isinstance(quotes,list):return []
    return [{'side':'new','source_id':q.get('source_id'),'quote':q.get('quote')} for q in quotes if isinstance(q,dict)]

def project(output):
    errors=[]; local=[]; records=[];origin=[]
    if not isinstance(output,dict):output={};errors.append('top-level output must be object')
    facts=output.get('facts');relations=output.get('relations'); unmatched=output.get('unmatched_old_unit_ids')
    if not isinstance(facts,list):errors.append('facts must be array');facts=[]
    if not isinstance(relations,list):errors.append('relations must be array');relations=[]
    if not isinstance(unmatched,list):errors.append('unmatched_old_unit_ids must be array');unmatched=[]
    ids=[x.get('fact_id') if isinstance(x,dict) else None for x in facts]
    duplicate={x for x in ids if _safe_id(x) and ids.count(x)>1}
    valid_facts={x['fact_id']:x for x in facts if isinstance(x,dict) and _safe_id(x.get('fact_id')) and x['fact_id'] not in duplicate}
    for i,f in enumerate(facts):
        errs=[]
        if not isinstance(f,dict):f={};errs.append('fact must be object')
        for k in FACT_FIELDS:
            if k not in f:errs.append(f'facts[{i}].{k} missing')
        fid=f.get('fact_id')
        if not _safe_id(fid):errs.append(f'facts[{i}].fact_id invalid')
        elif fid in duplicate:errs.append(f'facts[{i}].fact_id duplicate')
        if isinstance(f.get('conditions'),dict) and f['conditions'].get('kind')=='same_as_old':errs.append(f'facts[{i}].conditions cannot refer to old scope')
        quotes=f.get('quotes')
        rec={'unit_id':None,'relation':'new_information','old_subject':None,'old_attribute':None,'old_value':None,
             'new_subject':f.get('subject'),'new_attribute':f.get('attribute'),'new_value':f.get('value'),
             'old_conditions':{'kind':'unknown'},'new_conditions':f.get('conditions'),'modality':f.get('modality'),
             'old_quotes':[],'new_quotes':quotes,'temporal_order':{'relation':'unknown','basis':[],'explanation':None},
             'semantic_rationale':f.get('rationale'),'semantic_basis':_new_basis(quotes),'uncertainties':f.get('uncertainties')}
        records.append(rec);local.append(errs);origin.append({'kind':'fact','index':i,'id':fid})
    relation_ids=[r.get('relation_id') if isinstance(r,dict) else None for r in relations]
    for i,r in enumerate(relations):
        errs=[]
        if not isinstance(r,dict):r={};errs.append('relation must be object')
        for k in REL_FIELDS:
            if k not in r:errs.append(f'relations[{i}].{k} missing')
        rid=r.get('relation_id');fid=r.get('fact_id');f=valid_facts.get(fid,{}) if _safe_id(fid) else {}
        if not _safe_id(rid):errs.append(f'relations[{i}].relation_id invalid')
        elif relation_ids.count(rid)>1:errs.append(f'relations[{i}].relation_id duplicate')
        if not f:errs.append(f'relations[{i}].fact_id missing, unknown or duplicate')
        if not isinstance(r.get('relation'),str) or r['relation'] not in RELATIONS:
            errs.append(f'relations[{i}].relation invalid')
        affected=r.get('affected_part');oldquotes=r.get('old_quotes')
        if affected is not None and (not isinstance(affected,str) or not affected or not isinstance(oldquotes,list)
            or not any(isinstance(q,dict) and isinstance(q.get('quote'),str) and affected in q['quote'] for q in oldquotes)):
            errs.append(f'relations[{i}].affected_part must be null or inside linked old quote')
        relation=r.get('relation')
        # A supplement's new assertion is already a separate fact candidate.
        # It does not independently determine impact on the old unit.
        if relation=='supplement':relation='unknown'
        rec={'unit_id':r.get('unit_id'),'relation':relation,'old_subject':r.get('old_subject'),
             'old_attribute':r.get('old_attribute'),'old_value':r.get('old_value'),
             'new_subject':f.get('subject'),'new_attribute':f.get('attribute'),'new_value':f.get('value'),
             'old_conditions':r.get('old_conditions'),'new_conditions':f.get('conditions'),
             'modality':f.get('modality'),'old_quotes':oldquotes,'new_quotes':f.get('quotes'),
             'temporal_order':r.get('temporal_order'),'semantic_rationale':r.get('rationale'),
             'semantic_basis':r.get('semantic_basis'),'uncertainties':r.get('uncertainties')}
        records.append(rec);local.append(errs);origin.append({'kind':'relation','index':i,'id':rid,'fact_id':fid,'raw_relation':r.get('relation')})
    # A malformed fact must not become usable via its relation.
    by_id={o['id']:local[i] for i,o in enumerate(origin) if o['kind']=='fact' and _safe_id(o['id'])}
    for i,o in enumerate(origin):
        if o['kind']=='relation' and o.get('fact_id') in by_id and by_id[o['fact_id']]:
            local[i].append('referenced fact has structural errors')
    return {'records':records,'unmatched_old_unit_ids':unmatched},local,origin,errors

def analyze(payload,output):
    projected,local,origin,top_errors=project(output)
    validation=v4.validate_output(projected,payload)
    validation['schema_errors'].extend(top_errors)
    for i,errs in enumerate(local):
        validation['schema_errors'].extend(errs)
        validation['record_errors'][i].extend(errs)
    if validation['schema_errors']:validation['schema_status']='failed'
    validation['errors']=[*validation['schema_errors'],*validation['quote_errors'],*validation['basis_errors'],*validation['coverage_errors']]
    validation['status']='failed' if validation['errors'] else 'passed'
    old,units,sources,alignments=v4.planner_inputs(payload,projected)
    for i,entry in enumerate(alignments):
        if i < len(origin):
            entry['validation_errors'] += local[i]
            entry['note']='model_'+origin[i]['kind']+'='+str(origin[i]['id'])+';index='+str(origin[i]['index'])
            entry['origin']=origin[i]
        entry['semantic_support']='unknown'
    plan=planner.build_scope_plan(old,units,sources,alignments)
    return {'status':validation['status'],'validation':validation,'projected':projected,
            'origins':origin,'alignments':alignments,'plan':plan,'parsed':copy.deepcopy(output)}
