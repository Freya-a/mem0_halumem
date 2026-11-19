"""Use frozen upstream v4 splitter on selected memory once; no retries or writes to memory."""
import hashlib,json,sys,time
from pathlib import Path
from urllib.request import build_opener,ProxyHandler,Request
from datetime import datetime
from zoneinfo import ZoneInfo
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[3];COMP=HERE.parents[1]
SPLITTER=PROJECT/'variants/dnd_mem0_splitter'
sys.path.insert(0,str(SPLITTER)); import splitter
prompt_path=SPLITTER/'prompt_versions/v4_boundaries_20261104/prompt.txt'
P=prompt_path.read_text(encoding='utf8'); plans=json.loads((HERE/'split_plan.json').read_text())
model=COMP/'model/Qwen3.5-27B-Q4_K_M/Qwen3.5-27B-Q4_K_M.gguf'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while c:=f.read(8388608):h.update(c)
 return h.hexdigest()
def now():return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def save(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
opener=build_opener(ProxyHandler({}))
with opener.open('http://127.0.0.1:18081/props',timeout=10) as r:props=json.load(r)
if props['model_path']!=str(model) or props['build_info']!='b1-78ffbaa' or props['default_generation_settings']['n_ctx']!=4096:raise RuntimeError('server identity differs')
modelsha=sha(model)
if modelsha!='84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806':raise RuntimeError('model checksum differs')
for p in [HERE/'split_manifest.json',HERE/'split_completion.json']:
 if p.exists():raise RuntimeError('previous run marker exists')
(HERE/'split_results').mkdir(exist_ok=False)
(HERE/'frozen_splitter_prompt.txt').write_text(P,encoding='utf8')
save(HERE/'split_manifest.json',{'started_at':now(),'model_sha256':modelsha,'server_build':props['build_info'],'context_size':4096,'splitter_code_sha256':sha(SPLITTER/'splitter.py'),'splitter_prompt_path':str(prompt_path),'splitter_prompt_sha256':sha(prompt_path),'prepared_sha256':sha(HERE/'prepared.json'),'split_plan_sha256':sha(HERE/'split_plan.json'),'parameters':{'temperature':0,'n_predict':1024,'stream':False,'chat_template_kwargs':{'enable_thinking':False}},'client_retries':0,'notes':'Independent upstream calls; request contains only old memory and old context. Outputs and failures remain unmodified. Reused saved v4 split recorded separately.'})
def post(path,payload):
 data=json.dumps(payload,ensure_ascii=False).encode('utf8')
 with opener.open(Request('http://127.0.0.1:18081'+path,data=data,headers={'Content-Type':'application/json'}),timeout=300) as r:return r.read().decode('utf8')
results=[]
for key,item in plans.items():
 out=HERE/'split_results'/f'{key}.json'; req=item['input']
 if item['status']=='reused_v4':
  path=Path(item['reused_result_path']); result=json.loads(path.read_text()); assert sha(path)==item['reused_result_sha256']
  # Replay the unchanged upstream validator, without invoking a model.
  checked=splitter.split_memory(req,lambda _: {'facts':result['facts']})
  assert checked==result
  save(out,{'status':'reused_v4','calls_attempted':0,'input':req,'result':result,'source_path':str(path),'source_sha256':sha(path)})
  results.append({'key':key,'status':'reused_v4','calls_attempted':0,'facts':len(result['facts'])});continue
 state={'key':key,'status':'error','calls_attempted':0,'input':req,'messages':None,'template_response_raw':None,'generation_request':None,'raw_http_response':None,'raw_output':None,'result':None,'error':None,'elapsed_seconds':None,'started_at':now()}
 save(HERE/'split_results'/f'{key}.started.json',{'started_at':now(),'input':req,'planned_calls':1})
 def call(payload):
  msgs=[{'role':'system','content':P},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}];state['messages']=msgs
  render={'messages':msgs,'chat_template_kwargs':{'enable_thinking':False}}
  state['template_response_raw']=post('/apply-template',render)
  prompt=json.loads(state['template_response_raw'])['prompt']
  gen={'prompt':prompt,'temperature':0,'n_predict':1024,'stream':False};state['generation_request']=gen
  state['calls_attempted']+=1; state['raw_http_response']=post('/completion',gen)
  state['raw_output']=json.loads(state['raw_http_response'])['content']
  return json.loads(state['raw_output'])
 t=time.perf_counter()
 try:
  result=splitter.split_memory(req,call);state['result']=result
  state['status']='ok' if result['facts'] else 'empty_facts'
 except Exception as e:state['error']={'type':type(e).__name__,'message':str(e)}
 state['elapsed_seconds']=round(time.perf_counter()-t,3);state['finished_at']=now();save(out,state)
 row={'key':key,'records':item['records'],'status':state['status'],'calls_attempted':state['calls_attempted'],'facts':len(state['result']['facts']) if state['result'] else None,'error':state['error']};results.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
save(HERE/'split_completion.json',{'finished_at':now(),'calls_attempted':sum(x['calls_attempted'] for x in results),'results':results})
