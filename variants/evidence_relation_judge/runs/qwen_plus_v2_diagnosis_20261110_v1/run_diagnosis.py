"""One request per saved v2 case; no retries, no memory operations."""
import hashlib,json,os,sys,time
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import dotenv_values
from openai import OpenAI

HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent
BASE=HERE.parent/'erase_style_comparison_20261110_v1'
PART=COMP/'part1_relation_judge'
sys.path.insert(0,str(PART))
import relation_judge_v2 as judge

NAMES=['job_transition','persian_cats','skydiving','career_history','promotion']
def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
 with p.open('x',encoding='utf8') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
def main():
 config=dotenv_values(COMP.parents[1]/'.env.local')
 assert config.get('LLM_MODEL')=='qwen-plus' and config.get('LLM_BASE_URL')=='https://dashscope.aliyuncs.com/compatible-mode/v1'
 key=config.get('LLM_API_KEY'); assert key
 inputs=json.loads((BASE/'inputs.json').read_text())
 prompt=(BASE/'A_v2/system_prompt.txt').read_text()
 assert prompt==judge.SYSTEM
 baseline={}
 for name in NAMES:
  old=json.loads((BASE/'A_v2'/f'{name}.json').read_text()); data=inputs[name]
  assert old['input']==data and len(data['split_result']['facts'])==1 and old['model_calls']==1
  judge.v1.validate_request(data)
  f=data['split_result']['facts'][0]; s=data['split_result']; payload={'memory_id':s['memory_id'],'memory_text':s['memory_text'],'fact':f,'source_context':data.get('source_context',[]),'new_evidence':data['new_evidence'],'time_info':data.get('time_info')}
  assert old['model_messages']==[[{'role':'system','content':prompt},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]]
  baseline[name]=old
 save(HERE/'inputs.json',inputs)
 (HERE/'system_prompt.txt').write_text(prompt,encoding='utf8')
 params={'model':'qwen-plus','temperature':0,'max_tokens':768,'stream':False}
 manifest={'started_at':now(),'baseline':str(BASE),'source_hashes':{n:sha(BASE/'A_v2'/f'{n}.json') for n in NAMES},'judge_hashes':{p.name:sha(p) for p in (PART/'relation_judge.py',PART/'relation_judge_v2.py')},'endpoint_host':'dashscope.aliyuncs.com','sdk':'openai','sdk_retries':0,'timeout_seconds':180,'parameters':params,'differences':'Local: greedy do_sample=False, max_new_tokens=768, enable_thinking=False, model generation_config defaults. API: temperature=0 and max_tokens=768; no direct do_sample, pad/eos or tokenizer control; top_p and other parameters provider defaults; thinking setting not sent, server/model default applies; temperature=0 does not prove identical decoding. Requested alias may change; use response model for returned identifier.','pricing':'No pricing or invoice returned by standard response; no estimate.'}
 save(HERE/'manifest.json',manifest)
 # Match this workspace's existing direct DashScope connection, without changing system configuration.
 for n in ('NO_PROXY','no_proxy'):
  parts=[x.strip() for x in os.environ.get(n,'').split(',') if x.strip()]
  if 'dashscope.aliyuncs.com' not in parts: parts.append('dashscope.aliyuncs.com')
  os.environ[n]=','.join(parts)
 client=OpenAI(api_key=key,base_url=config['LLM_BASE_URL'],timeout=180,max_retries=0)
 summaries=[]
 for name in NAMES:
  old=baseline[name]; started=now(); state={'calls_attempted':0,'messages':None,'response':None,'error':None,'elapsed_seconds':None}
  def backend(payload):
   messages=[{'role':'system','content':prompt},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
   assert messages==old['model_messages'][0]
   state['messages']=deepcopy(messages)
   # Durable intent is recorded before transport; never rerun this case automatically.
   save(HERE/f'{name}.started.json',{'case':name,'started_at':now(),'input':inputs[name],'model_messages':messages,'parameters':params,'calls_attempted':1,'completion':'unknown until result file is written'})
   state['calls_attempted']+=1; start=time.perf_counter()
   try:
    response=client.chat.completions.create(messages=messages,**params)
    state['response']=response.model_dump(mode='json')
    content=response.choices[0].message.content
    if not isinstance(content,str): raise ValueError('No textual response content')
    return content
   except Exception as e:
    state['error']={'type':type(e).__name__,'http_status':getattr(e,'status_code',None),'message':'Details omitted to avoid exposing credentials or request data'}
    raise RuntimeError('API call or response failed; see safe error metadata') from None
   finally: state['elapsed_seconds']=round(time.perf_counter()-start,3)
  result=judge.judge(deepcopy(inputs[name]),backend)
  artifact={'case':name,'started_at':started,'finished_at':now(),'input':inputs[name],'model_messages':state['messages'],'request_parameters':params,'requested_model':'qwen-plus','returned_model':(state['response'] or {}).get('model'),'raw_api_response':state['response'],'result':result,'calls_attempted':state['calls_attempted'],'elapsed_seconds':state['elapsed_seconds'],'api_error':state['error'],'cost':None,'cost_note':'Provider response does not include invoice or cost.'}
  save(HERE/f'{name}.json',artifact)
  row={'case':name,'status':result['status'],'calls_attempted':state['calls_attempted'],'elapsed_seconds':state['elapsed_seconds'],'returned_model':artifact['returned_model'],'error':state['error']}; summaries.append(row)
  print(json.dumps(row,ensure_ascii=False),flush=True)
  if state['error'] or state['calls_attempted']!=1: break
 client.close()
 save(HERE/'completion.json',{'finished_at':now(),'calls_attempted':sum(x['calls_attempted'] for x in summaries),'cases':summaries,'remaining_not_called':NAMES[len(summaries):]})
if __name__=='__main__': main()
