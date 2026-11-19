"""Replay five frozen facts once each; retain prompts, raw responses and v2 validation."""
import hashlib
import json
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.request import ProxyHandler,build_opener
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'part1_relation_judge'))
sys.path.insert(0,str(HERE))
import relation_judge_v2 as v2
import experimental_judge as exp
from experimental_backend import LlamaServerV2

BASE=ROOT/'runs/qwen35_27b_q4_v2_20261110_v1'
NAMES=['job_transition','persian_cats','skydiving','career_history','promotion']
MODEL=ROOT/'model/Qwen3.5-27B-Q4_K_M/Qwen3.5-27B-Q4_K_M.gguf'
EXPECTED_SHA='84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806'
def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while chunk:=f.read(8*1024*1024): h.update(chunk)
    return h.hexdigest()
def save(path,obj):
    with path.open('x',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
    # Validate the *live* service identity, not merely the prior run manifest.
    opener=build_opener(ProxyHandler({}))
    with opener.open('http://127.0.0.1:18081/props',timeout=10) as r: props=json.load(r)
    oldprops=json.loads((BASE/'server_props.json').read_text(encoding='utf-8'))
    for key in ('model_alias','model_path','build_info','chat_template'):
        if props[key]!=oldprops[key]: raise RuntimeError(f'live server differs on {key}')
    if props['default_generation_settings']['n_ctx']!=4096: raise RuntimeError('unexpected context size')
    model_sha=digest(MODEL)
    if model_sha!=EXPECTED_SHA: raise RuntimeError('model SHA-256 differs')
    inputs=json.loads((BASE/'inputs.json').read_text(encoding='utf-8'))
    baselines={}
    for name in NAMES:
        old=json.loads((BASE/f'{name}.json').read_text(encoding='utf-8'))
        if old['input']!=inputs[name] or old['calls_attempted']!=1 or len(inputs[name]['split_result']['facts'])!=1: raise RuntimeError('baseline mismatch: '+name)
        if (HERE/f'{name}.started.json').exists() or (HERE/f'{name}.json').exists(): raise RuntimeError('prior case attempt: '+name)
        v2.v1.validate_request(inputs[name])
        baselines[name]=old
    save(HERE/'inputs.json',inputs)
    (HERE/'system_prompt.txt').write_text(exp.SYSTEM,encoding='utf-8')
    save(HERE/'manifest.json',{'started_at':now(),'model_path':str(MODEL),'model_sha256':model_sha,'server_build':props['build_info'],'context':4096,'base_dir':str(BASE),'base_case_sha256':{n:digest(BASE/f'{n}.json') for n in NAMES},'source_sha256':{str(p):digest(p) for p in [ROOT/'part1_relation_judge/relation_judge.py',ROOT/'part1_relation_judge/relation_judge_v2.py',HERE/'experimental_judge.py',HERE/'experimental_backend.py']},'input_sha256':digest(BASE/'inputs.json'),'v2_system_sha256':hashlib.sha256(v2.SYSTEM.encode()).hexdigest(),'experimental_system_sha256':hashlib.sha256(exp.SYSTEM.encode()).hexdigest(),'added_instruction':exp.PROVENANCE_INSTRUCTION,'request_parameters':{'temperature':0,'n_predict':768,'stream':False,'chat_template_kwargs':{'enable_thinking':False}},'no_retry':True,'semantic_correctness':'not_checked','notes':'Same v2 judge and validator; experimental prompt extension only. /apply-template does not generate; one /completion per fact. GPU peak sampled every 0.2 sec, device-wide including other processes.'})
    rows=[]
    for name in NAMES:
        backend=LlamaServerV2()
        def call(payload):
            messages=[{'role':'system','content':exp.SYSTEM},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
            old=baselines[name]['calls'][0]['messages']
            if messages[1]!=old[1] or old[0]['content']!=v2.SYSTEM: raise RuntimeError('input or base prompt mismatch before generation')
            save(HERE/f'{name}.started.json',{'started_at':now(),'case':name,'input':inputs[name],'messages':messages,'intended_completions':1})
            return backend(payload)
        started=now()
        result=exp.judge(deepcopy(inputs[name]),call)
        calls=sum(x['generation_attempted'] for x in backend.records)
        save(HERE/f'{name}.json',{'case':name,'started_at':started,'finished_at':now(),'input':inputs[name],'calls_attempted':calls,'calls':backend.records,'result':result})
        row={'case':name,'status':result['status'],'calls_attempted':calls,'elapsed_seconds':backend.records[0]['elapsed_seconds'] if backend.records else None}
        rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
        if not backend.records or backend.records[0]['error']: break
    save(HERE/'completion.json',{'finished_at':now(),'calls_attempted':sum(x['calls_attempted'] for x in rows),'cases':rows,'remaining_not_called':NAMES[len(rows):]})
if __name__=='__main__': main()
