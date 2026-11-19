#!/usr/bin/env python3
"""One v9 call per byte-identical prior input; no retries, no Mem0."""
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
PROJECT=BASE.parents[1]
V8RUN=HERE.parent/'v8_five_reviewed_targets_20261118_01'
V9=BASE/'prompt_versions/v9_local_update'
sys.path.insert(0,str(BASE))
from splitter import ValidationError
from real_backend import OpenAICompatibleBackend,load_model_settings
spec=importlib.util.spec_from_file_location('v9_run',V9/'v9_splitter.py')
v9=importlib.util.module_from_spec(spec); spec.loader.exec_module(v9)
def sha(x): return hashlib.sha256(x).hexdigest()
def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def save(path,obj):
 with path.open('x',encoding='utf-8') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
def main():
 with (HERE/'started.marker').open('x',encoding='utf-8') as f: f.write(now()+'\n')
 previous=json.loads((V8RUN/'manifest.json').read_text())
 prompt=(V9/'prompt.txt').read_bytes(); prompt_hash=sha(prompt)
 (HERE/'frozen_prompt.txt').write_bytes(prompt)
 entries=[]
 for case in previous['cases']:
  name=case['case']; dst=HERE/name; dst.mkdir()
  old=V8RUN/name; inp=(old/'input.json').read_bytes()
  assert sha(inp)==case['input_sha256']
  (dst/'input.json').write_bytes(inp)
  (dst/'v8_result.json').write_bytes((old/'result.json').read_bytes())
  (dst/'provenance.json').write_bytes((old/'provenance.json').read_bytes())
  entries.append({'case':name,'target':case['reviewed_main_target'],'input_sha256':sha(inp),'prior_input':str((old/'input.json').relative_to(PROJECT)),'prior_result':str((old/'result.json').relative_to(PROJECT))})
 save(HERE/'manifest.json',{'created_at':now(),'model':'qwen-plus-2025-12-01','enable_thinking':False,'prompt_version':'v9_local_update','prompt_sha256':prompt_hash,'previous_v8_prompt_sha256':previous['prompt_sha256'],'previous_run':str(V8RUN.relative_to(PROJECT)),'max_calls_per_case':1,'sdk_max_retries':0,'cases':entries})
 try:
  settings=load_model_settings(PROJECT/'.env.local',environ={**os.environ,'LLM_MODEL':v9.MODEL})
  assert settings.model=='qwen-plus-2025-12-01'
  settings.generation['extra_body']={'enable_thinking':False}
 except (ValidationError, AssertionError) as e:
  save(HERE/'stopped.json',{'reason':'configuration_unavailable','details':e.as_dict() if isinstance(e,ValidationError) else 'model mismatch'});return
 save(HERE/'configuration.json',{'model':settings.model,'enable_thinking':False,'generation':settings.generation,'timeout_seconds':settings.timeout,'sdk_max_retries':0})
 reports=[]
 for entry in entries:
  name=entry['case']; path=HERE/name
  if sha((V9/'prompt.txt').read_bytes())!=prompt_hash:
   save(HERE/'stopped.json',{'reason':'prompt_changed','cases_completed':len(reports)});break
  req=json.loads((path/'input.json').read_text())
  save(path/'attempt.json',{'started_at':now(),'model':v9.MODEL,'enable_thinking':False,'prompt_sha256':prompt_hash})
  holder=[]
  def factory(text):
   backend=OpenAICompatibleBackend(settings,text); holder.append(backend)
   def audit(http_request):
    body=json.loads(http_request.content)
    assert body['model']==v9.MODEL and body['enable_thinking'] is False
    assert sha(body['messages'][0]['content'].encode())==prompt_hash
    assert json.loads(body['messages'][1]['content'])==req
    save(path/'request_audit.json',{'observed_at':now(),'model':body['model'],'enable_thinking':body['enable_thinking'],'prompt_sha256':prompt_hash,'input_matches':True,'response_format':body.get('response_format')})
   backend.client._client.event_hooks['request'].append(audit)
   return backend
  result=None; error=None
  try: result=v9.split_memory_v9(req,factory)
  except ValidationError as e: error=e.as_dict()
  except Exception as e: error={'code':'unexpected_local_error','type':type(e).__name__,'message':'Details hidden to protect credentials.'}
  backend=holder[0] if holder else None
  if backend and isinstance(backend.raw_content,str): (path/'raw_content.txt').write_text(backend.raw_content.replace(settings.api_key,'[REDACTED]'))
  metadata=backend.response_metadata if backend else {}; save(path/'response_metadata.json',metadata)
  if result is not None: save(path/'v9_result.json',result)
  rec={'case':name,'reviewed_main_target':entry['target'],'finished_at':now(),'model_calls':backend.call_count if backend else 0,'request_audit_present':(path/'request_audit.json').exists(),'status':'accepted' if result is not None else 'error','fact_count':len(result['facts']) if result is not None else None,'error':error,'returned_model':metadata.get('returned_model')}
  save(path/'report.json',rec);reports.append(rec);print(json.dumps(rec,ensure_ascii=False),flush=True)
  if error and (metadata.get('http_status') in (400,401,403,404,422) or not (path/'request_audit.json').exists()):
   save(HERE/'stopped.json',{'reason':'configuration_or_request_rejected','case':name,'details':error});break
 save(HERE/'batch_completion.json',{'finished_at':now(),'completed_cases':len(reports),'calls':sum(r['model_calls'] for r in reports),'accepted':sum(r['status']=='accepted' for r in reports),'reports':reports})
if __name__=='__main__': main()
