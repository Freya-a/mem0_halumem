"""Small read-only frozen-scope evaluation: 3 replay cases and 2 new upstream cases."""
from pathlib import Path
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib,json,sys,time,traceback

HERE=Path(__file__).resolve().parent;COMP=HERE.parent.parent;PROJ=COMP.parent.parent
PART1=COMP/'part1_relation_judge';PART2=COMP/'part2_scope_judge';SPLITTER=PROJ/'variants/dnd_mem0_splitter'
sys.path[:0]=[str(PART2),str(PART1),str(SPLITTER)]
import relation_judge_v2 as v2
from run_local_v2 import LocalQwenV2
from scope_extract import LocalScopeExtractor, SYSTEM as SCOPE_SYSTEM
from scope_nli import LocalNLI
from scope_planner import plan_scope
from splitter import split_memory


def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(path,data):
 with path.open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
def jsonread(p):return json.loads(p.read_text(encoding='utf8'))
def now():return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()

def replay_old(name):
 request=jsonread(COMP/'runs/real_cases_20261106'/f'{name}_input.json')
 saved_v2=jsonread(COMP/'runs/controlled_v2_20261106'/f'{name}_run.json')
 split=jsonread(PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'split_result.json')['result']
 assert request==saved_v2['input'] and request['split_result']==split
 qwenpath=COMP/'runs/scope_v2_20261109'/('skydiving_retry.json' if name=='skydiving' else f'{name}.json')
 qwen=jsonread(qwenpath);raw=qwen['run_audit']['generation'][0]['raw_output']
 baseline=COMP/'runs/scope_v1_20261109/replay_v2'/f'{name}.json'
 saved_nli=deepcopy(jsonread(baseline)['results'][0]['nli']);assert saved_nli.pop('status')=='ok'
 def extract(payload):return json.loads(raw)
 def nli(premise,hypothesis):
  if (premise,hypothesis)!=(saved_nli['premise'],saved_nli['hypothesis']):raise ValueError('saved NLI inputs do not match')
  return {**saved_nli,'inference_mode':'replayed_real_saved_result','source_artifact':str(baseline)}
 out=plan_scope(request,saved_v2['result'],extractor=extract,nli=nli)
 out['evaluation_audit']={'input_origin':'existing v4 and v2 exact input match','v4_file':str(PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'split_result.json'),
  'v2_file':str(COMP/'runs/controlled_v2_20261106'/f'{name}_run.json'),'qwen_scope_file':str(qwenpath),'nli_file':str(baseline),
  'new_model_calls':0,'existing_model_outputs_replayed':True}
 save(HERE/f'{name}_result.json',out)
 print(name,'planner rows',len(out['results']),'status',[r['status'] for r in out['results']],'scope mods',len(out.get('modifications',[])),flush=True)


def pointer(obj,p):
 for part in p.strip('/').split('/'):
  obj=obj[int(part)] if isinstance(obj,list) else obj[part]
 return obj

def prepare_new(number,memid,case):
 evidence_path=PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1'/f'target_{number:02d}_evidence.json'
 d=jsonread(evidence_path); target=d['original_target']; text=d['before'][memid]
 dataset=PROJ/'dataset/HaluMem-Medium/HaluMem-Medium.jsonl'; line=target['dataset_line_one_based']
 with dataset.open(encoding='utf8') as f:
  for index,raw in enumerate(f,1):
   if index==line: original=json.loads(raw);break
 assert original['uuid']==target['user_uuid']
 def aligned(ev):
  raw=pointer(original,ev['json_pointer']);assert ev['quote'] in raw['content']
  assert ev['role']==raw['role'] and ev['timestamp']==raw['timestamp']
  return raw
 old=[]
 for i,ev in enumerate(target['old_dialogue_evidence'],1):
  aligned(ev); old.append({'source_id':f'old-{i}','source_ref':f"dataset line {line}, {ev['json_pointer']}",
    'text':ev['quote'],'speaker':ev['role'],'recorded_at':ev['timestamp']})
 new=[]
 for ev in target['new_dialogue_evidence']:
  aligned(ev);new.append({'source_id':'dialogue-'+str(ev['message_index_zero_based']),'text':ev['quote'],
    'speaker':ev['role'],'recorded_at':ev['timestamp']})
 split_request={'memory_id':memid,'memory_text':text,'source_context':old}
 request={'split_request':split_request,'new_evidence':new,'time_info':None}
 save(HERE/f'{case}_prepared.json',{'target_number':number,'target_id':target['target_id'],'user_uuid':target['user_uuid'],
      'old_before_source':str(evidence_path),'old_memory_before_exact_match':True,'dataset':str(dataset),'dataset_sha256':sha(dataset),
      'old_new_dialogue_pointer_text_role_time_verified':True,'model_request':request,
      'missing_existing_inputs':['matching pre-update v4 split','matching Qwen v2 result'],
      'selection_note':'source selection is not part of model prompt; no review labels supplied to models'})
 return request


def main():
 frozen=jsonread(HERE/'manifest_before.json')
 for path,expected in frozen['sha256'].items():assert sha(Path(path))==expected,path
 for name in ('promotion','skydiving','career_history'):replay_old(name)
 cases=[(7,'e6ab178b-c0f9-4adb-bfb7-e4648617a950','job_transition'),(14,'eef34a57-c82a-4995-877d-66b54b9589da','persian_cats')]
 prepared=[(case,prepare_new(n,mid,case)) for n,mid,case in cases]
 prompt=(SPLITTER/'prompt_versions/v4_boundaries_20261104/prompt.txt').read_text(encoding='utf8')
 model=LocalQwenV2(max_new_tokens=768); scope_model=LocalScopeExtractor(max_new_tokens=1600); nli=LocalNLI(); records=[]
 for case,request in prepared:
  gen={}; start=time.perf_counter()
  def v4_backend(payload):
   model.load();torch=model.torch
   messages=[{'role':'system','content':prompt},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
   rendered=model.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
   inputs=model.tokenizer(rendered,return_tensors='pt').to('cuda:0');t=time.perf_counter()
   with torch.inference_mode():
    output=model.model.generate(**inputs,max_new_tokens=1600,do_sample=False,pad_token_id=model.tokenizer.eos_token_id)
   tokens=output[0,inputs['input_ids'].shape[1]:];raw=model.tokenizer.decode(tokens,skip_special_tokens=True)
   gen.update(messages=messages,raw_output=raw,output_tokens=len(tokens),terminated_at_eos=bool(len(tokens) and tokens[-1].item()==model.tokenizer.eos_token_id),seconds=round(time.perf_counter()-t,3))
   return json.loads(raw)
  print(case,'v4 starting',flush=True)
  try:
   split=split_memory(request['split_request'],v4_backend)
   if not split['facts']:raise ValueError('v4 returned no facts')
   save(HERE/f'{case}_v4.json',{'status':'ok','result':split,'generation':gen,'model_path':model.metrics['model_dir'],'prompt_version':'v4_boundaries_20261104','max_new_tokens':1600,'no_retry':True})
  except Exception as exc:
   save(HERE/f'{case}_v4.json',{'status':'error','error':f'{type(exc).__name__}: {exc}','generation':gen,'traceback':traceback.format_exc(),'no_retry':True})
   records.append({'case':case,'status':'v4_failed','error':str(exc)});print(case,'v4 failed',type(exc).__name__,str(exc),flush=True);continue
  payload={'split_result':split,'source_context':request['split_request']['source_context'],'new_evidence':request['new_evidence'],'time_info':request['time_info']}
  print(case,'v4 done facts',len(split['facts']),'v2 starting',flush=True)
  before=model.metrics['model_calls'];m=len(model.messages)
  result=v2.judge(payload,model)
  save(HERE/f'{case}_v2.json',{'input':payload,'result':result,'case_model_calls':model.metrics['model_calls']-before,'model_messages':model.messages[m:],'runtime_metrics':deepcopy(model.metrics),'no_retry':True})
  print(case,'v2',result['status'],'scope starting',flush=True)
  scope_model.model=model.model;scope_model.tokenizer=model.tokenizer;scope_model.torch=model.torch
  qstart=scope_model.metrics['model_calls'];gstart=len(scope_model.metrics['generations']);msgstart=len(scope_model.messages)
  out=plan_scope(payload,result,nli=nli,extractor=scope_model)
  out['evaluation_audit']={'target':case,'v4':'new local Qwen output, existing v4 prompt and validator','v2':'new local Qwen output',
    'scope_extraction_calls':scope_model.metrics['model_calls']-qstart,'scope_extraction_prompt':SCOPE_SYSTEM,
    'scope_model_messages':deepcopy(scope_model.messages[msgstart:]),'scope_generations':deepcopy(scope_model.metrics['generations'][gstart:]),
    'nli':'new local model forward when called; see per-row status','no_mem0_write':True,'elapsed_seconds':round(time.perf_counter()-start,3)}
  save(HERE/f'{case}_result.json',out)
  records.append({'case':case,'status':out['status'],'v4_facts':len(split['facts']),'v2_status':result['status'],
    'row_statuses':[r['status'] for r in out['results']], 'scope_extraction_calls':out['evaluation_audit']['scope_extraction_calls']})
  print(case,'scope finished',records[-1],flush=True)
 after={p:sha(Path(p)) for p in frozen['sha256']}
 changed=[p for p,h in after.items() if h!=frozen['sha256'][p]]
 save(HERE/'completion.json',{'finished_at':now(),'records':records,'frozen_files_changed':changed,
   'v2_model_calls_new':model.metrics['model_calls'],'v4_calls_new':len(prepared),
   'scope_model_calls_new':scope_model.metrics['model_calls'],'qwen_versions':model.metrics,
   'dataset_sha256':sha(PROJ/'dataset/HaluMem-Medium/HaluMem-Medium.jsonl'),'no_mem0_write':True})
 print('complete frozen files changed',changed,flush=True)
if __name__=='__main__':main()
