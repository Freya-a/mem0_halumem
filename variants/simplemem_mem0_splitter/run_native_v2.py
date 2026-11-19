"""One-shot prompt_v2 trial over five specified native Mem0 before snapshots."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys
import time
from dotenv import dotenv_values
from openai import OpenAI, APIStatusError
from run_file_priority import HERE, ROOT, MODEL, SYSTEM, save, choose_file_settings, create_http_client, safe_error
from prompt_v2 import build_extraction_prompt_v2
from splitter import parse_and_validate

RUN = HERE / 'run_native_mem0_prompt_v2_20261119'
NATIVE = ROOT / 'results/medium_dev/williams_native_prefix5_20261028_v3/users'
SELECTION = [
 ('2f1f897e-d67f-dbc5-6a7b-b7634a9e294f','session_005','d575dfc1-59ec-43b4-83c4-6b94457a83f6'),
 ('2f1f897e-d67f-dbc5-6a7b-b7634a9e294f','session_009','e1d4f8f9-0520-427d-94fd-a2ac0ee69d03'),
 ('1b846c59-456e-9550-dffd-4d23f1eca81f','session_004','8602da08-fefc-4875-ad50-dba104642365'),
 ('1b846c59-456e-9550-dffd-4d23f1eca81f','session_006','4ffee399-c31f-4827-b5fc-5c661baf1fc9'),
 ('348492a7-cfe4-ee1d-73c3-c276d6ba8277','session_004','05afde13-35bd-4d26-bbae-6de427d58db1'),
]


def load_cases():
    cases=[]
    for user_id,session,mid in SELECTION:
        path=NATIVE/user_id/session/'before.json'
        content=path.read_bytes(); snapshot=json.loads(content)
        api=[x for x in snapshot['api_snapshot']['results'] if x.get('id')==mid]
        points=[x for x in snapshot['database_points_with_vectors'] if x.get('id')==mid]
        if len(api)!=1 or len(points)!=1 or not snapshot.get('not_truncated'):
            raise ValueError(f'Invalid snapshot or memory ID: {mid}')
        entry=api[0]; payload=points[0]['payload']
        if entry['user_id']!=user_id or payload['user_id']!=user_id or entry['memory']!=payload['data']:
            raise ValueError(f'API snapshot and payload disagree: {mid}')
        target_links=json.loads((path.parent/'target_links.json').read_text())
        cases.append({'memory_id':mid,'memory_text':entry['memory'],'source_context':None,
            'source':{'user_id':user_id,'before_file':str(path.relative_to(ROOT)),'snapshot_sha256':hashlib.sha256(content).hexdigest(),
                      'api_snapshot_pointer':'/api_snapshot/results (id lookup)',
                      'database_payload_cross_check':True,'target_ids':target_links['target_ids'],
                      'session_group_id':target_links['session_group_id']}})
    return cases


def main():
    cases=load_cases()
    if '--preflight' in sys.argv:
        print(json.dumps(cases,ensure_ascii=False,indent=2)); return
    RUN.mkdir(mode=0o700,exist_ok=False)
    save(RUN/'cases.json',cases)
    manifest={'model':MODEL,'prompt_version':'prompt_v2','maximum_requests':5,'automatic_retries':0,'client_trust_env':False,
              'http_redirects':False,'request_attempts':0,'model_responses':0,'status':'preparing',
              'configuration_sources':{'base_url':'config/medium_full_qwen_plus_20251201.json',
                'key':'.env.server.medium-full','workspace':'.env.server.medium-full','priority':'file_only_fail_closed'},
              'cases':[{'memory_id':c['memory_id'],'status':'not_started'} for c in cases]}
    save(RUN/'manifest.json',manifest)
    cfg=dotenv_values(ROOT/'.env.server.medium-full'); key,workspace=choose_file_settings(cfg)
    if not key or not workspace or not re.fullmatch(r'(?:llm|ws)-[a-zA-Z0-9-]+',workspace):
        manifest.update(status='configuration_error',error={'type':'MissingOrInvalidConfiguration'});save(RUN/'manifest.json',manifest);return
    profile=json.loads((ROOT/'config/medium_full_qwen_plus_20251201.json').read_text())
    base=profile['llm']['config']['openai_base_url'].replace('{DASHSCOPE_WORKSPACE_ID}',workspace)
    manifest['status']='running';save(RUN/'manifest.json',manifest)
    with create_http_client() as http:
        client=OpenAI(api_key=key,base_url=base,max_retries=0,timeout=180.0,http_client=http)
        for i,case in enumerate(cases,1):
            inp={k:case[k] for k in ('memory_id','memory_text','source_context')}
            messages=[{'role':'system','content':SYSTEM},{'role':'user','content':build_extraction_prompt_v2(**inp)}]
            item={'input':inp,'source':case['source'],'request':{'model':MODEL,'prompt_version':'prompt_v2','messages':messages,
                'temperature':0.1,'max_tokens':4096,'automatic_retries':0},'call':{'status':'started','attempts':1,
                'request_transmitted':'unknown','model_response_received':False},'raw_response':None,'provider_response':None,'validation':None}
            path=RUN/f'case_{i}.json';save(path,item)
            manifest['request_attempts']+=1;manifest['cases'][i-1].update(status='started',file=path.name,attempts=1);save(RUN/'manifest.json',manifest)
            started=time.monotonic()
            try: response=client.chat.completions.create(model=MODEL,messages=messages,temperature=0.1,max_tokens=4096)
            except Exception as exc:
                elapsed=round(time.monotonic()-started,3);err=safe_error(exc)
                if isinstance(exc,APIStatusError):item['call']['request_transmitted']=True
                item['call'].update(status='request_error',elapsed_seconds=elapsed,error=err)
                manifest['cases'][i-1].update(status='request_error',elapsed_seconds=elapsed,error=err)
                manifest.update(status='stopped_request_error',error=err);save(path,item);save(RUN/'manifest.json',manifest)
                print(f'case {i}: request error {err["type"]}',flush=True);return
            elapsed=round(time.monotonic()-started,3);manifest['model_responses']+=1
            item['call'].update(status='response_received',request_transmitted=True,model_response_received=True,elapsed_seconds=elapsed,
                returned_model=response.model,finish_reason=response.choices[0].finish_reason if response.choices else None)
            item['provider_response']=response.model_dump(mode='json')
            item['raw_response']=response.choices[0].message.content if response.choices else None;save(path,item)
            try:item['validation']=parse_and_validate(item['raw_response'],**inp)
            except Exception as exc:
                err=safe_error(exc);item['call'].update(status='processing_error',error=err)
                manifest['cases'][i-1].update(status='processing_error',elapsed_seconds=elapsed,error=err)
                manifest.update(status='stopped_processing_error',error=err);save(path,item);save(RUN/'manifest.json',manifest);return
            manifest['cases'][i-1].update(status='response_received',elapsed_seconds=elapsed,returned_model=response.model,
                validation_status=item['validation']['status']);save(path,item);save(RUN/'manifest.json',manifest)
            print(f'case {i}: response received; validation {item["validation"]["status"]}; {elapsed}s',flush=True)
            if response.model!=MODEL:
                manifest.update(status='stopped_model_mismatch',error={'type':'ReturnedModelMismatch'});save(RUN/'manifest.json',manifest);return
    manifest['status']='completed';save(RUN/'manifest.json',manifest)

if __name__=='__main__':main()
