"""Freeze provenance then perform exactly one v2 call per saved one-fact case."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMP = HERE.parent.parent
BASE = COMP/'runs/real_cases_20261106'
sys.path.insert(0,str(COMP/'part1_relation_judge'))
import relation_judge as v1
import relation_judge_v2 as v2
from run_local_v2 import LocalQwenV2


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def write(p,value):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


old = json.loads((BASE/'manifest_before.json').read_text())
old_end = json.loads((BASE/'completion.json').read_text())
assert old_end['total_model_calls']==3
for path,digest in old['code_sha256'].items(): assert sha(path)==digest
assert hashlib.sha256(v1.SYSTEM.encode()).hexdigest()==old['system_prompt_utf8_sha256']
model=Path(old['model_dir'])
for name,metadata in old['model_files'].items():
    path=model/name
    assert path.stat().st_size==metadata['bytes']
    if 'sha256' in metadata: assert sha(path)==metadata['sha256']
cases={}
for name,item in old['cases'].items():
    input_path=Path(item['prepared_input_path'])
    assert sha(input_path)==item['prepared_input_sha256']
    data=json.loads(input_path.read_text())
    baseline=json.loads((BASE/f'{name}_run.json').read_text())
    assert data==baseline['input'] and len(data['split_result']['facts'])==1
    v1.validate_request(data)
    cases[name]={'input_path':str(input_path),'input_sha256':sha(input_path),'v1_run_path':str(BASE/f'{name}_run.json'),'v1_run_sha256':sha(BASE/f'{name}_run.json')}
files=[COMP/'part1_relation_judge'/'relation_judge.py',COMP/'part1_relation_judge'/'run_local.py',COMP/'part1_relation_judge'/'relation_judge_v2.py',COMP/'part1_relation_judge'/'run_local_v2.py',Path(__file__)]
with (HERE/'v2_system_prompt.txt').open('x',encoding='utf-8') as f: f.write(v2.SYSTEM)
manifest={'code_sha256':{str(p):sha(p) for p in files}, 'baseline_manifest_sha256':sha(BASE/'manifest_before.json'),
          'v1_prompt_sha256':hashlib.sha256(v1.SYSTEM.encode()).hexdigest(), 'v2_prompt_sha256':hashlib.sha256(v2.SYSTEM.encode()).hexdigest(),
          'model_dir':str(model),'model_file_identifiers':old['model_files'], 'cases':cases,
          'generation_parameters_both':{'local_files_only':True,'dtype':'bfloat16','device':'cuda:0','enable_thinking':False,'do_sample':False,'max_new_tokens':512,'pad_token_id':'tokenizer.eos_token_id','load_once':True,'calls_per_case':1,'retry':False},
          'changes':['v2 system prompt appended to v1','v2 case-only unique fragment recovery and audit','new runner subclass uses v2 prompt; same loading and decoding']}
write(HERE/'manifest_before.json',manifest)
backend=LocalQwenV2()
for name,case in cases.items():
    assert sha(case['input_path'])==case['input_sha256']
    data=json.loads(Path(case['input_path']).read_text())
    before_calls=backend.metrics['model_calls']; before_messages=len(backend.messages)
    result=v2.judge(data,backend)
    msgs=deepcopy(backend.messages[before_messages:])
    assert all(m[0]['content']==v2.SYSTEM for m in msgs)
    artifact={'case':name,'input':data,'model_messages':msgs,'result':result,
              'case_model_calls':backend.metrics['model_calls']-before_calls,
              'runtime_cumulative':deepcopy(backend.metrics),'manifest_sha256':sha(HERE/'manifest_before.json')}
    write(HERE/f'{name}_run.json',artifact)
    print(json.dumps({'case':name,'status':result['status'],'calls':artifact['case_model_calls'],'errors':[r['errors'] for r in result['results']]},ensure_ascii=False),flush=True)
write(HERE/'completion.json',{'total_model_calls':backend.metrics['model_calls'], 'code_sha256_after':{str(p):sha(p) for p in files},
      'v1_prompt_sha256':hashlib.sha256(v1.SYSTEM.encode()).hexdigest(),'v2_prompt_sha256':hashlib.sha256(v2.SYSTEM.encode()).hexdigest(),
      'input_sha256_after':{name:sha(c['input_path']) for name,c in cases.items()},'baseline_run_sha256_after':{name:sha(c['v1_run_path']) for name,c in cases.items()}})
