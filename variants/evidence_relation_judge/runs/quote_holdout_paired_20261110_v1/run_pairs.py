"""Run two frozen component-one prompts once per audited fact; never retry."""
import hashlib,json,sys
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.request import build_opener,ProxyHandler
HERE=Path(__file__).resolve().parent;PROJECT=HERE.parents[3];COMP=HERE.parents[1]
sys.path.insert(0,str(COMP/'part1_relation_judge'));sys.path.insert(0,str(COMP/'runs/quote_provenance_20261110_v1'))
import relation_judge_v2 as v2
from run_llama_server_v2 import LlamaServerV2 as Base
import experimental_judge as exp
from experimental_backend import LlamaServerV2 as Experimental

def now():return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def digest_text(s):return hashlib.sha256(s.encode()).hexdigest()
prevm=json.loads((COMP/'runs/quote_provenance_20261110_v1/manifest.json').read_text())
if digest_text(v2.SYSTEM)!=prevm['v2_system_sha256'] or digest_text(exp.SYSTEM)!=prevm['experimental_system_sha256']:raise RuntimeError('judge prompt changed')
for path,expected in prevm['source_sha256'].items():
 if sha(Path(path))!=expected:raise RuntimeError('source file changed: '+path)
splitman=json.loads((HERE/'split_manifest.json').read_text()); splitdone=json.loads((HERE/'split_completion.json').read_text()); plans=json.loads((HERE/'split_plan.json').read_text()); rows=json.loads((HERE/'prepared.json').read_text()); decisions=json.loads((HERE/'split_review.json').read_text())
with build_opener(ProxyHandler({})).open('http://127.0.0.1:18081/props',timeout=10) as r:props=json.load(r)
if props['model_path']!=str(COMP/'model/Qwen3.5-27B-Q4_K_M/Qwen3.5-27B-Q4_K_M.gguf') or props['build_info']!=prevm['server_build'] or props['default_generation_settings']['n_ctx']!=4096:raise RuntimeError('live service mismatch')
if splitman['model_sha256']!=prevm['model_sha256']:raise RuntimeError('model checksum mismatch')
if (HERE/'pair_manifest.json').exists():raise RuntimeError('prior run exists')
(HERE/'pairs').mkdir(exist_ok=False)
(HERE/'prompt_v2.txt').write_text(v2.SYSTEM,encoding='utf8');(HERE/'prompt_experimental.txt').write_text(exp.SYSTEM,encoding='utf8')
units=[]; skipped=[]
for row in rows:
 if row['eligibility']=='merged_excluded':skipped.append({'record':row['number'],'reason':row['exclusion_reason']});continue
 for memory in row['old_memory_records']:
  key=memory['split_key']; artifact=json.loads((HERE/'split_results'/f'{key}.json').read_text()); decision=decisions[key]
  if artifact['status'] not in ('ok','reused_v4') or not decision['usable']:
   skipped.append({'record':row['number'],'memory_id':memory['id'],'split_key':key,'reason':decision['reason']});continue
  split=deepcopy(artifact['result']); data={'split_result':split,'source_context':deepcopy(row['source_context']),'new_evidence':deepcopy(row['new_evidence']),'time_info':None}
  if split['memory_id']!=memory['id'] or split['memory_text']!=memory['memory']:raise RuntimeError('snapshot mismatch')
  v2.v1.validate_request(data)
  units.append({'record':row['number'],'memory_id':memory['id'],'split_key':key,'input':data,'target_id':row['target_id'],'split_review':decision})
save(HERE/'pair_inputs.json',units);save(HERE/'pair_manifest.json',{'started_at':now(),'v2_prompt_sha256':digest_text(v2.SYSTEM),'experimental_prompt_sha256':digest_text(exp.SYSTEM),'server_build':props['build_info'],'model_sha256':splitman['model_sha256'],'context':4096,'parameters':{'temperature':0,'n_predict':768,'stream':False,'chat_template_kwargs':{'enable_thinking':False}},'upstream_splitter_calls':splitdone['calls_attempted'],'record_memory_units':len(units),'fact_count_per_version':sum(len(u['input']['split_result']['facts']) for u in units),'potential_component1_calls':2*sum(len(u['input']['split_result']['facts']) for u in units),'no_retry':True,'execution_order':'alternate version order by record-memory unit','skipped':skipped,'split_review_sha256':sha(HERE/'split_review.json'),'prepared_sha256':sha(HERE/'prepared.json'),'notes':'Same input and validated source contexts for both versions. Raw model output retained. Labels are not blind gold.'})
summary=[]; transport_failure=None
for i,unit in enumerate(units):
 label=f"{unit['record']:02d}_{unit['memory_id']}"; order=['v2','experimental'] if i%2==0 else ['experimental','v2']
 for version in order:
  backend=Base() if version=='v2' else Experimental();judge=v2 if version=='v2' else exp;start=now();calls=0
  def call(payload):
   fid=payload['fact']['fact_index'];path=HERE/'pairs'/f'{label}_{version}_fact{fid}.started.json'
   save(path,{'started_at':now(),'record':unit['record'],'version':version,'fact_index':fid,'payload':payload,'intended_generations':1,'system_prompt_sha256':digest_text(judge.SYSTEM)})
   try:return backend(payload)
   finally:
    if backend.records:save(HERE/'pairs'/f'{label}_{version}_fact{fid}.call.json',backend.records[-1])
  result=judge.judge(deepcopy(unit['input']),call)
  calls=sum(r['generation_attempted'] for r in backend.records)
  artifact={'record':unit['record'],'target_id':unit['target_id'],'memory_id':unit['memory_id'],'version':version,'started_at':start,'finished_at':now(),'input':unit['input'],'calls_attempted':calls,'calls':backend.records,'result':result,'semantic_review':'pending'}
  save(HERE/'pairs'/f'{label}_{version}.json',artifact)
  s={'record':unit['record'],'memory_id':unit['memory_id'],'version':version,'facts':len(unit['input']['split_result']['facts']),'calls_attempted':calls,'status':result['status'],'errors':[r['errors'] for r in result['results'] if r['errors']]}; summary.append(s);print(json.dumps(s,ensure_ascii=False),flush=True)
  if any(r.get('error') for r in backend.records):
   transport_failure={'record':unit['record'],'memory_id':unit['memory_id'],'version':version,'errors':[r['error'] for r in backend.records if r.get('error')]};break
 if transport_failure:break
save(HERE/'pair_completion.json',{'finished_at':now(),'model_calls':sum(x['calls_attempted'] for x in summary),'records':summary,'skipped':skipped,'transport_failure':transport_failure,'expected_version_units':2*len(units),'completed_version_units':len(summary)})
