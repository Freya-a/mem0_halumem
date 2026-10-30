import collections, hashlib, json, os, pathlib, sys
ROOT=pathlib.Path('/home/shu1004/ld/system/mem0_halumem_diagnosis'); OUT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts')); import local_smoke as base
from mem0.configs.prompts import get_update_memory_messages

def read(p): return json.loads(pathlib.Path(p).read_text())
def digest(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def main():
 m=read(OUT/'five_case_manifest.json'); combined=(OUT/'control_update_prompt.txt').read_text(); all_cases=[]; counts=collections.Counter(); tokens={'llm':collections.Counter(),'embedding':collections.Counter()}
 assert read(OUT/'connectivity_summary.json')['status']=='PASS'
 for c in m['cases']:
  d=OUT/'cases'/c['case']; pre=read(d/'preflight.json'); status=read(d/'status.json'); before=read(d/'before.json'); after=read(d/'after.json'); ops=read(d/'actual_operations.json'); plan=read(d/'full_operation_plan.json'); ledger=[json.loads(x) for x in (d/'api_calls.jsonl').read_text().splitlines()]; log=[json.loads(x) for x in (d/'runtime.jsonl').read_text().splitlines()]; updates=read(d/'update_model_io.json'); obs=read(d/'observations.json'); persistence=read(d/'persistence.json');
  assert persistence['history_integrity']=='ok' and read(d/'reconcile.json')['history_replayed_matches_database'] and status['error'] is None
  inputs=[x for x in updates if x['kind']=='model_input']; outputs=[x for x in updates if x['kind']=='model_output']; assert len(inputs)==len(outputs)==1
  x=inputs[0]; assert x['messages'][0]['content']==get_update_memory_messages(x['native_retrieved_old_memory'],x['native_new_facts'],combined)
  assert not outputs[0]['parse_error'] and x['messages'][0]['content'].startswith(combined)
  starts={x['id']:x for x in ledger if x['status']=='started'}; ends={x['id']:x for x in ledger if x['status']!='started'}; assert starts.keys()==ends.keys() and len(ledger)==2*len(starts)
  for i,finish in ends.items():
   assert finish['status']=='ok' and starts[i]['kind']==finish['kind']
   kind=finish['kind']; counts[kind]+=1; res=finish['response'];
   for k,v in (res.get('usage') or {}).items():
    if isinstance(v,int): tokens[kind][k]+=v
   if kind=='llm': assert res['choices'][0]['finish_reason']=='stop'
   if kind=='embedding': assert all(len(v['embedding'])==1024 for v in res['data'])
  assert sum(x['kind']=='llm' for x in ends.values())==2
  assert pre['status']=='PASS' and before['database_count_exact']==c['before_count']
  for name,h in pre['baseline_artifact_sha256'].items(): assert digest(pathlib.Path(c['folder'])/name)==h
  for rel,h in pre['copy_files_sha256'].items(): assert digest(pathlib.Path(c['backup_path'])/rel)==h
  for key,path in [('before_sha256',c['before_path']),('input_sha256',c['input_path']),('backup_ready_sha256',pathlib.Path(c['backup_path'])/'ready.json')]: assert digest(path)==c[key]
  none_plan=sum(x['event']=='NONE' for x in plan); none_actual=sum(x['message']=='NOOP for Memory.' for x in log); assert none_plan==none_actual
  unresolved=[{'id':x['id'],'event':x['event'],'text':x['text']} for x in plan if x.get('event') in ('UPDATE','DELETE') and x.get('resolved_existing_memory_id') is None]
  errors=[x['message'] for x in log if x['level']=='ERROR']; assert len(errors)==len(unresolved)
  all_cases.append({'case':c['case'],'status':status['status'],'before_count':before['database_count_exact'],'after_count':after['database_count_exact'],'operation_counts':dict(collections.Counter(x['event'] for x in ops)),'plan_counts':dict(collections.Counter(x['event'] for x in plan)),'none_dispatch':none_actual,'invalid_id_skips':unresolved,'native_errors':errors,'llm_calls':sum(x['kind']=='llm' for x in ends.values()),'embedding_calls':sum(x['kind']=='embedding' for x in ends.values()),'elapsed_seconds':status['add_elapsed_seconds'],'full_update_prompt_reconstructed_exact':True,'history_and_persistence_verified':True})
 old=ROOT/'results/medium_dev/five_case_simple_prompt_20261029_v1'; prior=read(OUT/'previous_failed_run_sha256.json'); assert all(digest(old/k)==v for k,v in prior.items())
 settings=base.read_env(ROOT/'.env.local'); secrets=[v for k,v in settings.items() if 'API_KEY' in k and base.usable(v)]
 for f in OUT.rglob('*'):
  if f.is_file() and f.suffix not in ('.sqlite','.db','.pyc'):
   content=f.read_bytes(); assert not any(s.encode() in content for s in secrets), 'credential scan failed'
 result={'status':'PASS','cases':all_cases,'experiment_calls':dict(counts),'experiment_usage':{k:dict(v) for k,v in tokens.items()},'connectivity_calls':{'llm':1,'embedding':1},'failed_run_hashes_unchanged':len(prior),'baseline_and_backup_hashes_unchanged':True,'credential_scan':'PASS','update_model_inputs_exact':True}
 (OUT/'verification_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
