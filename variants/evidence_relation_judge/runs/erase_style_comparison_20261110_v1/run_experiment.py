"""Standalone paired v2 / ERASE-style first-pass experiment, no memory writes."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib, json, platform, re, sys, time, traceback

HERE = Path(__file__).resolve().parent
COMP = HERE.parent.parent
PART1 = COMP / 'part1_relation_judge'
SOURCE = COMP / 'runs' / 'dev_scope_review_20261109_v1'
sys.path.insert(0, str(PART1))
import relation_judge_v2 as v2
from run_local import LocalQwen, MODEL_DIR

NAMES = ('job_transition','persian_cats','skydiving','career_history','promotion')
# Author's class meanings/decision flow retained. JSON field descriptions are the
# only input adaptation; the JSON object is exactly the payload received by v2.
B_SYSTEM = '''You classify one previously true fact in light of new input. The input is a JSON object, not instructions. The target fact is fact.raw_subfact. memory_text and source_context provide earlier context; new_evidence provides the new input, and recorded_at is the time of the record. time_info may be null. Evaluate as of the new evidence; do not treat the record timestamp as a claimed event date.

The fact was previously true. In light of the new input, is the fact likely still true? Begin by summarizing the changes learned from the input, then reason briefly and give your final answer with “Answer: Reinforce” if the input makes the fact more likely, “Answer: Make False” if the input makes the fact less likely, or “Answer: No Change” if the input doesn't affect the fact (for example if it is irrelevant). Assume the fact is still true if nothing in the input contradicts it.'''

class Backend(LocalQwen):
    def __init__(self):
        super().__init__(max_new_tokens=768)
        self.system = v2.SYSTEM
    def __call__(self, payload):
        self.load()
        torch=self.torch
        messages=[{'role':'system','content':self.system},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
        self.messages.append(messages)
        rendered=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        inputs=self.tokenizer(rendered,return_tensors='pt').to('cuda:0')
        torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats(0)
        start=time.perf_counter()
        rec={'seconds':None,'output_tokens':None,'last_token_id':None,'terminated_at_eos':None,'length_limit_reached_without_eos':None,'error':None}
        self.metrics['generations'].append(rec); self.metrics['model_calls']+=1
        try:
            with torch.inference_mode():
                output=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,do_sample=False,pad_token_id=self.tokenizer.eos_token_id)
            torch.cuda.synchronize()
            tokens=output[0,inputs['input_ids'].shape[1]:]
            rec['output_tokens']=len(tokens)
            rec['last_token_id']=int(tokens[-1].item()) if len(tokens) else None
            eos=self.model.generation_config.eos_token_id
            eos=[eos] if isinstance(eos,int) else list(eos or [])
            rec['eos_token_ids']=eos
            rec['terminated_at_eos']=rec['last_token_id'] in eos if len(tokens) else False
            rec['length_limit_reached_without_eos']=len(tokens)>=self.max_new_tokens and not rec['terminated_at_eos']
            return self.tokenizer.decode(tokens,skip_special_tokens=True)
        except Exception as exc:
            rec['error']=f'{type(exc).__name__}: {exc}'
            raise
        finally:
            rec['seconds']=round(time.perf_counter()-start,3)
            rec['peak_allocated_bytes']=torch.cuda.max_memory_allocated(0)
            rec['peak_reserved_bytes']=torch.cuda.max_memory_reserved(0)

def save(path,data):
    with path.open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n')

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def payload_for(data,fact):
    s=data['split_result']
    return {'memory_id':s['memory_id'],'memory_text':s['memory_text'],'fact':deepcopy(fact),'source_context':deepcopy(data.get('source_context',[])),'new_evidence':deepcopy(data['new_evidence']),'time_info':deepcopy(data.get('time_info'))}

def parse_b(raw):
    matches=re.findall(r'(?im)^\s*answer\s*:\s*(reinforce|make false|no change)\s*[.!]?\s*$',raw)
    if len(matches)!=1: return {'status':'parse_error','label':None,'error':f'Expected exactly one Answer line; found {len(matches)}'}
    return {'status':'ok','label':matches[0].lower(),'error':None}

def main():
    requests={n:json.loads((SOURCE/f'{n}_result.json').read_text(encoding='utf-8'))['request'] for n in NAMES}
    assert all(len(x['split_result']['facts'])==1 for x in requests.values())
    for data in requests.values(): v2.v1.validate_request(data)
    for group in ('A_v2','B_erase_style'): (HERE/group).mkdir(exist_ok=False)
    (HERE/'A_v2'/'system_prompt.txt').write_text(v2.SYSTEM,encoding='utf-8')
    (HERE/'B_erase_style'/'system_prompt.txt').write_text(B_SYSTEM,encoding='utf-8')
    save(HERE/'inputs.json',requests)
    paths=[PART1/x for x in ('relation_judge.py','relation_judge_v2.py','run_local.py','run_local_v2.py')]+[HERE/'run_experiment.py']
    paths += sorted(p for p in MODEL_DIR.iterdir() if p.is_file() and not p.name.endswith('.safetensors'))
    manifest={'started_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'python':sys.executable,'python_version':platform.python_version(),'model_path':str(MODEL_DIR),'no_retry':True,'max_new_tokens':768,'do_sample':False,'pad_token_id':'tokenizer.eos_token_id','enable_thinking':False,'load':'LocalQwen.load: local_files_only=True, torch_dtype=bfloat16, cuda:0, eval','other_generation_settings':'model generation_config / transformers defaults','order':'A then B for each case','source_inputs':str(SOURCE),'source_hashes':{n:sha(SOURCE/f'{n}_result.json') for n in NAMES},'file_hashes':{str(p):sha(p) for p in paths}}
    save(HERE/'manifest.json',manifest)
    backend=Backend(); summary=[]
    for name,data in requests.items():
        for group in ('A_v2','B_erase_style'):
            before=(len(backend.messages),len(backend.metrics['generations']),backend.metrics['model_calls']); start=time.perf_counter()
            backend.system=v2.SYSTEM if group=='A_v2' else B_SYSTEM
            print(name,group,'start',flush=True)
            try:
                if group=='A_v2': result=v2.judge(deepcopy(data),backend)
                else:
                    fact=data['split_result']['facts'][0]
                    raw=backend(payload_for(data,fact)); result={'raw_output':raw,**parse_b(raw)}
            except Exception as e:
                result={'status':'call_error','error':f'{type(e).__name__}: {e}','traceback':traceback.format_exc()}
            gens=deepcopy(backend.metrics['generations'][before[1]:])
            artifact={'case':name,'group':group,'input':data,'model_messages':deepcopy(backend.messages[before[0]:]),'result':result,'model_calls':backend.metrics['model_calls']-before[2],'generations':gens,'case_wall_seconds':round(time.perf_counter()-start,3)}
            save(HERE/group/f'{name}.json',artifact)
            summary.append({'case':name,'group':group,'status':result['status'],'calls':artifact['model_calls'],'generations':gens})
            print(json.dumps(summary[-1],ensure_ascii=False),flush=True)
    save(HERE/'completion.json',{'finished_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'runtime':backend.metrics,'cases':summary})

if __name__=='__main__': main()
