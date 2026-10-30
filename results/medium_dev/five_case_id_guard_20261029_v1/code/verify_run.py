import collections,hashlib,json,pathlib,sys
from mem0.configs.prompts import get_update_memory_messages
import guard
ROOT=pathlib.Path('/home/shu1004/ld/system/mem0_halumem_diagnosis');OUT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts')); import local_smoke as base

def read(p): return json.loads(pathlib.Path(p).read_text())
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 manifest=read(OUT/'five_case_manifest.json'); combined=(OUT/'control_update_prompt.txt').read_text(); rows=[]; counts=collections.Counter(); usage={'llm':collections.Counter(),'embedding':collections.Counter()}
 assert digest(OUT/'code/guard.py')==digest(ROOT/'variants/invalid_temp_id_guard_20261029/guard.py')
 for case in manifest['cases']:
  d=OUT/'cases'/case['case']; status=read(d/'status.json'); g=read(d/'guard_summary.json'); pre=read(d/'preflight.json'); assert status['status']=='completed' and all(status['checks'].values())
  log=[json.loads(x) for x in (d/'runtime.jsonl').read_text().splitlines()]; calls=[json.loads(x) for x in (d/'api_calls.jsonl').read_text().splitlines()]; starts={x['id']:x for x in calls if x['status']=='started'};ends={x['id']:x for x in calls if x['status']!='started'};assert starts.keys()==ends.keys() and len(calls)==2*len(starts)
  llm_responses=[]; call_counts=collections.Counter();case_usage={'llm':collections.Counter(),'embedding':collections.Counter()}
  for i,x in ends.items():
   assert x['status']=='ok' and starts[i]['kind']==x['kind'];kind=x['kind'];counts[kind]+=1;call_counts[kind]+=1
   response=x['response']
   for k,v in (response.get('usage') or {}).items():
    if isinstance(v,int):usage[kind][k]+=v;case_usage[kind][k]+=v
   if kind=='llm': assert response['choices'][0]['finish_reason']=='stop';llm_responses.append({'model':response.get('model'),'system_fingerprint':response.get('system_fingerprint'),'finish_reason':response['choices'][0]['finish_reason']})
   else: assert all(len(v['embedding'])==1024 for v in response['data'])
  update=read(d/'update_model_io.json'); ins=[x for x in update if x['kind']=='model_input'];outs=[x for x in update if x['kind']=='model_output']; audit=read(d/'guard_audit.json'); ini=next(x for x in audit if x['stage']=='initial'); mapping=read(d/'valid_ids.json')['id_to_uuid']; assert len(ins)==len(outs)==1+g['retry_triggered']
  assert ins[0]['messages'][0]['content']==get_update_memory_messages(ins[0]['native_retrieved_old_memory'],ins[0]['native_new_facts'],combined)
  assert ins[0]['native_temp_uuid_mapping']==mapping and ini['raw_response']==outs[0]['raw_response'] and ini['errors']==guard.validate_plan(ini['raw_response'],mapping)
  if g['retry_triggered']:
   req=next(x for x in audit if x['stage']=='retry_request');rsp=next(x for x in audit if x['stage']=='retry_response');assert req['messages']==ins[1]['messages'] and rsp['raw_response']==outs[1]['raw_response'] and rsp['errors']==guard.validate_plan(rsp['raw_response'],mapping)==[]
  else: assert not ini['errors'] and not any(x['stage'].startswith('retry_') for x in audit)
  plan=read(d/'final_plan.json'); ops=read(d/'actual_operations.json'); mutations=[x for x in plan if x['event'] in ('ADD','UPDATE','DELETE')];assert len(mutations)==len(ops)
  for planned,actual in zip(mutations,ops):
   assert planned['event']==actual['event']
   if planned['event'] in ('UPDATE','DELETE'): assert mapping[planned['id']]==actual['memory_id']
   if planned['event'] in ('ADD','UPDATE'): assert planned['text']==actual['new_memory']
  n=sum(x['event']=='NONE' for x in plan);assert n==sum(x['message']=='NOOP for Memory.' for x in log)
  for name,h in pre['baseline_artifact_sha256'].items(): assert digest(pathlib.Path(case['folder'])/name)==h
  for rel,h in pre['copy_files_sha256'].items(): assert digest(pathlib.Path(case['backup_path'])/rel)==h
  for key,path in [('before_sha256',case['before_path']),('input_sha256',case['input_path']),('backup_ready_sha256',pathlib.Path(case['backup_path'])/'ready.json')]: assert digest(path)==case[key]
  rows.append({'case':case['case'],'status':status['status'],'initial_invalid_ids':g['initial_invalid_ids'],'valid_id_count':len(mapping),'valid_id_min':min(map(int,mapping)) if mapping else None,'valid_id_max':max(map(int,mapping)) if mapping else None,'retry':g['retry_triggered'],'initial_plan_counts':g['initial_plan_counts'],'final_plan_counts':g['final_plan_counts'],'actual_operation_counts':dict(collections.Counter(x['event'] for x in ops)),'skipped_none':n,'native_errors':[x['message'] for x in log if x['level']=='ERROR'],'calls':dict(call_counts),'usage':{k:dict(v) for k,v in case_usage.items()},'elapsed_seconds':status['add_elapsed_seconds'],'llm_returned':llm_responses,'all_plan_mutations_match_history_in_order':True})
 fingerprints=read(OUT/'prior_run_fingerprints.json')
 for name,files in fingerprints.items():
  for rel,h in files.items():assert digest(ROOT/'results/medium_dev'/name/rel)==h
 profile=read(OUT/'profile.json')
 for rel,h in profile['native_source_sha256'].items():assert digest(ROOT/'mem0_v0.1.118'/rel)==h
 env=base.read_env(ROOT/'.env.local');secrets=[v for k,v in env.items() if 'API_KEY' in k and base.usable(v)]
 for f in OUT.rglob('*'):
  if f.is_file() and f.suffix not in ('.sqlite','.db','.pyc'):
   raw=f.read_bytes();assert not any(s.encode() in raw for s in secrets),'credential scan failed'
 result={'status':'PASS','cases':rows,'calls':dict(counts),'usage':{k:dict(v) for k,v in usage.items()},'prior_run_file_counts':{k:len(v) for k,v in fingerprints.items()},'backup_baseline_native_source_unchanged':True,'credential_scan':'PASS','all_actual_update_prompts_verified':True}
 (OUT/'verification_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
