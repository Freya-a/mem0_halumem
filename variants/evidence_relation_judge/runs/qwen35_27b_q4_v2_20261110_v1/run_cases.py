"""Run saved five-case v2 inputs once each, with no retries or memory writes."""
import hashlib
import json
import sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'part1_relation_judge'))
import relation_judge_v2 as judge
from run_llama_server_v2 import LlamaServerV2

NAMES=['job_transition','persian_cats','skydiving','career_history','promotion']
BASE=ROOT/'runs/erase_style_comparison_20261110_v1/A_v2'
CLOUD=ROOT/'runs/qwen_plus_v2_diagnosis_20261110_v1'

def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def save(path, value):
    with path.open('x',encoding='utf-8') as out:
        json.dump(value,out,ensure_ascii=False,indent=2)
        out.write('\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    preflight=json.loads((HERE/'preflight.json').read_text(encoding='utf-8'))
    if not preflight.get('plain_text_ok') or not preflight.get('json_no_thinking_ok'):
        raise RuntimeError('successful plain text and no-thinking JSON preflight required')
    inputs=json.loads((CLOUD/'inputs.json').read_text(encoding='utf-8'))
    if (CLOUD/'system_prompt.txt').read_text(encoding='utf-8')!=judge.SYSTEM:
        raise RuntimeError('v2 prompt differs from saved baseline')
    baselines={}
    for name in NAMES:
        baselines[name]=json.loads((BASE/f'{name}.json').read_text(encoding='utf-8'))
        if baselines[name]['input']!=inputs[name] or len(inputs[name]['split_result']['facts'])!=1:
            raise RuntimeError(f'input mismatch or not one fact: {name}')
        judge.v1.validate_request(inputs[name])
        if (HERE/f'{name}.started.json').exists() or (HERE/f'{name}.json').exists():
            raise RuntimeError(f'prior attempt exists for {name}; do not retry automatically')
    save(HERE/'inputs.json',inputs)
    (HERE/'system_prompt.txt').write_text(judge.SYSTEM,encoding='utf-8')
    save(HERE/'manifest.json',{'started_at':now(),'inputs_source':str(CLOUD/'inputs.json'),'baseline_local':str(BASE),'baseline_cloud':str(CLOUD),'input_sha256':sha(CLOUD/'inputs.json'),'local_case_sha256':{n:sha(BASE/f'{n}.json') for n in NAMES},'cloud_case_sha256':{n:sha(CLOUD/f'{n}.json') for n in NAMES},'judge_sha256':{p:sha(ROOT/'part1_relation_judge'/p) for p in ['relation_judge.py','relation_judge_v2.py','run_llama_server_v2.py']},'parameters':{'temperature':0,'n_predict':768,'stream':False,'chat_template_kwargs':{'enable_thinking':False}},'transport':'/apply-template renders messages without generation; /completion returns unparsed generated text; one completion per fact','sampling':'temperature zero; other llama.cpp defaults; no client retries','gpu_peak':'nvidia-smi GPU 0 device-wide sampled at 0.2 second intervals; includes other processes and can miss brief peaks','comparison_limits':'Qwen3-8B uses BF16 transformers greedy enable_thinking=False; qwen-plus remote API temperature=0 with provider defaults and unpinned alias; Qwen3.5 uses GGUF Q4_K_M llama.cpp template and sampling implementation. Identical message text does not imply identical tokenizer or internal template.'})
    summaries=[]
    for name in NAMES:
        backend=LlamaServerV2()
        def call(payload):
            messages=[{'role':'system','content':judge.SYSTEM},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
            if [messages]!=baselines[name]['model_messages']:
                raise RuntimeError('message mismatch before sending')
            save(HERE/f'{name}.started.json',{'case':name,'started_at':now(),'input':inputs[name],'messages':messages,'intended_calls':1})
            return backend(payload)
        started=now()
        result=judge.judge(deepcopy(inputs[name]),call)
        save(HERE/f'{name}.json',{'case':name,'started_at':started,'finished_at':now(),'input':inputs[name],'calls_attempted':sum(r['generation_attempted'] for r in backend.records),'calls':backend.records,'result':result})
        row={'case':name,'status':result['status'],'calls_attempted':sum(r['generation_attempted'] for r in backend.records),'elapsed_seconds':backend.records[0]['elapsed_seconds'] if backend.records else None}
        summaries.append(row)
        print(json.dumps(row,ensure_ascii=False),flush=True)
        if not backend.records or backend.records[0]['error']:
            break
    save(HERE/'completion.json',{'finished_at':now(),'calls_attempted':sum(x['calls_attempted'] for x in summaries),'cases':summaries,'remaining_not_called':NAMES[len(summaries):]})

if __name__=='__main__': main()
