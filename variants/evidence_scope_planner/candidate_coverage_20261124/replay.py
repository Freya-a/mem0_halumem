"""Replay saved responses; do not contact models, APIs, or memory storage."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import scope_planner as planner

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'authorization_comparison_20261124'
PROJECT=HERE.parents[2]

def module(path):
    spec=importlib.util.spec_from_file_location('prior_comparison',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

cmp=module(PRIOR/'comparison.py')

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def counts(plan):return {key:len(plan[key]) for key in ('modify','preserve','uncertain','add')}

def without_tracking(value):
    if isinstance(value,dict):
        return {k:without_tracking(v) for k,v in value.items()
                if k not in ('candidate_index','judgment_kind','candidate_coverage')}
    if isinstance(value,list):return [without_tracking(x) for x in value]
    return value

def human_args(case):
    f=read(cmp.FIXTURES/(case+'.json'))
    units=[{**u,'memory_id':f['memory_id'],'source_ref':f['old_memory_source_ref']} for u in f['units']]
    return (f['old_memory'],units,f['sources'],f['alignments'])

def main():
    out=HERE/'results';out.mkdir(exist_ok=True)
    checks={}
    for case in cmp.CASES:
        path=cmp.RUN/(case+'.json'); saved=read(path); prior=read(PRIOR/'results'/(case+'.json'))
        if sha(path)!=prior['artifact_sha256'] or json.loads(saved['raw_response'])!=saved['result']['parsed']:
            raise ValueError(f'{case}: saved raw model response differs')
        if cmp.digest(prior['B']['plan'])!=prior['B']['plan_sha256']:
            raise ValueError(f'{case}: prior B plan hash changed')
        payload=saved['prepared_input']; model=saved['result']['parsed']
        rebuilt=cmp.compare_case(payload,model)
        for g in ('A','B'):
            if rebuilt[g]['alignments']!=prior[g]['alignments'] or rebuilt[g]['plan']!=prior[g]['plan']:
                raise ValueError(f'{case}/{g}: failed to reconstruct prior experiment')
        hargs=human_args(case)
        if cmp.planner.build_scope_plan(*copy.deepcopy(hargs))!=prior['C']['plan']:
            raise ValueError(f'{case}/C: old human plan does not reproduce')
        old,units,sources,_=cmp.interface.planner_inputs(payload,model)
        arguments={'A':(old,units,sources,rebuilt['A']['alignments']),
                   'B':(old,units,sources,rebuilt['B']['alignments']),'C':hargs}
        groups={}
        for g,args in arguments.items():
            newplan=planner.build_scope_plan(*copy.deepcopy(args))
            if len(newplan['candidate_coverage'])!=len(args[3]):raise AssertionError('input count mismatch')
            if any(not j['outputs'] for c in newplan['candidate_coverage'] for j in c['judgments']):
                raise AssertionError('missing output for judgment')
            old_behavior=without_tracking(prior[g]['plan']);new_behavior=without_tracking(newplan)
            changes=[key for key in old_behavior if old_behavior[key]!=new_behavior[key]]
            groups[g]={'old_plan':prior[g]['plan'],'new_plan':newplan,'inputs':args[3],
                       'old_counts':counts(prior[g]['plan']),'new_counts':counts(newplan),
                       'changed_categories':changes,
                       'candidate_count':len(newplan['candidate_coverage']),
                       'judgment_count':sum(len(c['judgments']) for c in newplan['candidate_coverage'])}
        result={'case_id':case,'raw_sha256':sha(path),'prior_plan_sha256':prior['B']['plan_sha256'],
                'old_memory':payload['source_texts']['memory'],'sources':payload['source_texts']['messages'],
                'raw_model_output':model,'validation':rebuilt['validation'],'groups':groups,
                'old_B_suppressed_duplicate_adds':prior['B']['suppressed_duplicate_adds']}
        (out/(case+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        checks[case]={g:{k:groups[g][k] for k in ('old_counts','new_counts','candidate_count','judgment_count')} for g in 'ABC'}
        print(case,json.dumps(checks[case],ensure_ascii=False,separators=(',',':')))
    manifest={'new_model_calls':0,'prior_report_sha256':sha(PRIOR/'REPORT.md'),
              'prior_audit_sha256':sha(PRIOR/'AUDIT.json'),'planner_sha256':sha(HERE/'scope_planner.py'),
              'cases':checks}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
