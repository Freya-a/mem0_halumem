#!/usr/bin/env python3
"""One request per reviewed-target old memory, using the unmodified v8 entry."""
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
PROJECT = BASE.parents[1]
SRC = PROJECT / 'results/medium_dev/williams_native_prefix5_20261028_v3/users'
V8 = BASE / 'prompt_versions/v8_v4_v7_combined'
sys.path.insert(0, str(BASE))
from splitter import ValidationError
from real_backend import OpenAICompatibleBackend, load_model_settings
spec = importlib.util.spec_from_file_location('v8_original', V8 / 'v8_splitter.py')
v8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v8)

CASES = [
 ('01_susan', 4, '2f1f897e-d67f-dbc5-6a7b-b7634a9e294f', 7, 'a1332815-d6ba-4bdc-9ffa-657f7315d0ed', 2, 6, "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."),
 ('02_skydiving', 8, '2f1f897e-d67f-dbc5-6a7b-b7634a9e294f', 9, 'e1d4f8f9-0520-427d-94fd-a2ac0ee69d03', 3, 6, 'I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.'),
 ('03_director', 10, '1b846c59-456e-9550-dffd-4d23f1eca81f', 5, 'e13b825e-7ec7-4760-821e-0581d8da5650', 2, 2, 'I work at Historical Productions Ltd. as a Director.'),
 ('04_persian_cat', 14, '1b846c59-456e-9550-dffd-4d23f1eca81f', 7, 'eef34a57-c82a-4995-877d-66b54b9589da', 3, 6, 'I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.'),
 ('05_career_history', 24, '348492a7-cfe4-ee1d-73c3-c276d6ba8277', 8, '05afde13-35bd-4d26-bbae-6de427d58db1', 2, 2, 'I work at Blockchain Tech as a senior developer.'),
]
def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def sha(data): return hashlib.sha256(data).hexdigest()
def save(path, obj):
 with path.open('x', encoding='utf-8') as f:
  json.dump(obj, f, ensure_ascii=False, indent=2); f.write('\n')
def prepare():
 prompt = (V8 / 'prompt.txt').read_bytes()
 (HERE / 'frozen_prompt.txt').write_bytes(prompt)
 entries=[]
 for name, target, user, session, mid, old_session, idx, quote in CASES:
  case=HERE/name; case.mkdir()
  before=SRC/user/f'session_{session:03d}'/'before.json'
  dialogue=SRC/user/f'session_{old_session:03d}'/'input.json'
  records=json.loads(before.read_text(encoding='utf-8'))['api_snapshot']['results']
  rows=[row for row in records if row['id']==mid]
  assert len(rows)==1 and rows[0]['user_id']==user
  utterance=json.loads(dialogue.read_text(encoding='utf-8'))['raw_dialogue'][idx]
  assert utterance['role']=='user' and quote in utterance['content']
  start=utterance['content'].index(quote)
  req={'memory_id':mid,'memory_text':rows[0]['memory'],'source_context':[{'source_id':'ctx-1','source_ref':f'{dialogue.relative_to(PROJECT)}#/raw_dialogue/{idx}/content [{start}:{start+len(quote)}]','text':quote,'speaker':'user','recorded_at':utterance['timestamp']}]}
  save(case/'input.json',req)
  entry={'case':name,'reviewed_main_target':target,'user_uuid':user,'target_session_one_based':session,'before_snapshot':str(before.relative_to(PROJECT)),'before_snapshot_sha256':sha(before.read_bytes()),'before_snapshot_index':records.index(rows[0]),'source_input_sha256':sha(dialogue.read_bytes()),'context_scope':'verbatim excerpt of prior user message; target session not supplied','input_sha256':sha((case/'input.json').read_bytes())}
  save(case/'provenance.json',entry); entries.append(entry)
 save(HERE/'manifest.json',{'created_at':now(),'model_requested':v8.MODEL,'enable_thinking':False,'prompt_version':'v8_v4_v7_combined','prompt_sha256':sha(prompt),'entry':'prompt_versions/v8_v4_v7_combined/v8_splitter.py:split_memory_v8','backend':'real_backend.OpenAICompatibleBackend','sdk_max_retries':0,'per_case_max_calls':1,'cases':entries,'scope':'read only existing snapshots and prior dialogue; no Mem0 calls or writes; no full dataset run'})
 return sha(prompt)
def main():
 with (HERE/'started.marker').open('x',encoding='utf-8') as f: f.write(now()+'\n')
 prompt_hash=prepare()
 try:
  settings=load_model_settings(PROJECT/'.env.local',environ={**os.environ,'LLM_MODEL':v8.MODEL})
  assert settings.model==v8.MODEL
  settings.generation['extra_body']={'enable_thinking':False}
 except (ValidationError, AssertionError) as e:
  save(HERE/'stopped.json',{'reason':'configuration_unavailable','detail':e.as_dict() if isinstance(e,ValidationError) else 'model mismatch','model_calls':0})
  return
 save(HERE/'configuration.json',{'model':settings.model,'enable_thinking':False,'generation':settings.generation,'timeout_seconds':settings.timeout,'source':'.env.local plus standard environment overrides; model forced by v8 constant','sdk_max_retries':0})
 reports=[]
 for entry in json.loads((HERE/'manifest.json').read_text())['cases']:
  name=entry['case']; path=HERE/name
  if sha((V8/'prompt.txt').read_bytes())!=prompt_hash:
   save(HERE/'stopped.json',{'reason':'prompt_changed','cases_completed':len(reports)}); break
  req=json.loads((path/'input.json').read_text())
  save(path/'attempt.json',{'started_at':now(),'model':v8.MODEL,'enable_thinking':False,'prompt_sha256':prompt_hash})
  holder=[]
  def factory(prompt):
   backend=OpenAICompatibleBackend(settings,prompt)
   holder.append(backend)
   def audit(http_request):
    body=json.loads(http_request.content)
    assert body['model']==v8.MODEL and body['enable_thinking'] is False
    assert sha(body['messages'][0]['content'].encode())==prompt_hash
    assert json.loads(body['messages'][1]['content'])==req
    save(path/'request_audit.json',{'observed_at':now(),'model':body['model'],'enable_thinking':body['enable_thinking'],'prompt_sha256':prompt_hash,'input_matches':True,'response_format':body.get('response_format')})
   backend.client._client.event_hooks['request'].append(audit)
   return backend
  result=None; error=None
  try: result=v8.split_memory_v8(req,factory)
  except ValidationError as e: error=e.as_dict()
  except Exception as e: error={'code':'unexpected_local_error','type':type(e).__name__,'message':'Details hidden to protect credentials.'}
  backend=holder[0] if holder else None
  if backend and isinstance(backend.raw_content,str):
   (path/'raw_content.txt').write_text(backend.raw_content.replace(settings.api_key,'[REDACTED]'),encoding='utf-8')
  metadata=backend.response_metadata if backend else {}
  save(path/'response_metadata.json',metadata)
  if result is not None: save(path/'result.json',result)
  record={'case':name,'reviewed_main_target':entry['reviewed_main_target'],'finished_at':now(),'model_calls':backend.call_count if backend else 0,'request_audit_present':(path/'request_audit.json').exists(),'status':'accepted' if result is not None else 'error','facts':len(result['facts']) if result is not None else None,'error':error,'returned_model':metadata.get('returned_model')}
  save(path/'report.json',record); reports.append(record)
  print(json.dumps(record,ensure_ascii=False),flush=True)
  if error and (metadata.get('http_status') in (400,401,403,404,422) or not (path/'request_audit.json').exists()):
   save(HERE/'stopped.json',{'reason':'configuration_or_request_rejected','case':name,'details':error}); break
 save(HERE/'batch_completion.json',{'finished_at':now(),'completed_cases':len(reports),'calls':sum(r['model_calls'] for r in reports),'accepted':sum(r['status']=='accepted' for r in reports),'reports':reports})
if __name__=='__main__': main()
