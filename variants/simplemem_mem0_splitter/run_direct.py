"""One-shot direct-connection trial using the five previously selected memories."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import time
import httpx
from dotenv import dotenv_values
from openai import APIStatusError, OpenAI
from splitter import build_extraction_prompt, parse_and_validate
from run_trial import HERE, ROOT, MODEL, SYSTEM, save

RUN = HERE / 'run_20261119_direct'


def create_http_client():
    # This affects only this client, not the process or machine proxy configuration.
    return httpx.Client(trust_env=False, follow_redirects=False, timeout=180.0)


def safe_error(exc):
    result = {'type': type(exc).__name__}
    if isinstance(exc, APIStatusError):
        result['http_status'] = exc.status_code
        code = getattr(exc, 'code', None)
        if isinstance(code, str) and re.fullmatch(r'[A-Za-z0-9_.-]{1,80}', code):
            result['provider_error_code'] = code
    chain, seen, node = [], {id(exc)}, exc.__cause__ or exc.__context__
    while node is not None and id(node) not in seen and len(chain) < 8:
        seen.add(id(node))
        item = {'type': type(node).__name__}
        if isinstance(node, OSError) and isinstance(node.errno, int):
            item['errno'] = node.errno
        verify_code = getattr(node, 'verify_code', None)
        if isinstance(verify_code, int): item['tls_verify_code'] = verify_code
        chain.append(item)
        node = node.__cause__ or node.__context__
    result['cause_chain'] = chain
    return result


def main():
    # Exclusive directory creation protects both old evidence and this run from replay.
    RUN.mkdir(mode=0o700, exist_ok=False)
    cases=json.loads((HERE/'run/cases.json').read_text(encoding='utf-8'))
    if len(cases) != 5 or len({x['memory_id'] for x in cases}) != 5:
        raise ValueError('Expected exactly five distinct prior cases')
    save(RUN/'cases.json', cases)
    manifest={'model':MODEL,'maximum_requests':5,'automatic_retries':0,'client_trust_env':False,
              'http_redirects':False,'request_attempts':0,'model_responses':0,'status':'preparing',
              'cases':[{'memory_id':c['memory_id'],'status':'not_started'} for c in cases]}
    save(RUN/'manifest.json',manifest)
    config=dotenv_values(ROOT/'.env.server.medium-full')
    key=os.environ.get('DASHSCOPE_API_KEY') or config.get('DASHSCOPE_API_KEY')
    workspace=os.environ.get('DASHSCOPE_WORKSPACE_ID') or config.get('DASHSCOPE_WORKSPACE_ID')
    manifest['configuration_sources']={'base_url':'config/medium_full_qwen_plus_20251201.json',
      'key':'process_environment' if os.environ.get('DASHSCOPE_API_KEY') else '.env.server.medium-full',
      'workspace':'process_environment' if os.environ.get('DASHSCOPE_WORKSPACE_ID') else '.env.server.medium-full'}
    if not key or not workspace or not re.fullmatch(r'(?:llm|ws)-[a-zA-Z0-9-]+',workspace):
        manifest.update(status='configuration_error',error={'type':'MissingOrInvalidConfiguration'}); save(RUN/'manifest.json',manifest); return
    profile=json.loads((ROOT/'config/medium_full_qwen_plus_20251201.json').read_text(encoding='utf-8'))
    base=profile['llm']['config']['openai_base_url'].replace('{DASHSCOPE_WORKSPACE_ID}',workspace)
    manifest['status']='running'; save(RUN/'manifest.json',manifest)
    with create_http_client() as http:
        client=OpenAI(api_key=key,base_url=base,max_retries=0,timeout=180.0,http_client=http)
        for i,case in enumerate(cases,1):
            inp={k:case[k] for k in ('memory_id','memory_text','source_context')}
            messages=[{'role':'system','content':SYSTEM},{'role':'user','content':build_extraction_prompt(**inp)}]
            artifact={'input':inp,'source':case['source'],
                      'request':{'model':MODEL,'messages':messages,'temperature':0.1,'max_tokens':4096,'automatic_retries':0},
                      'call':{'status':'started','attempts':1,'request_transmitted':'unknown','model_response_received':False},
                      'raw_response':None,'provider_response':None,'validation':None}
            path=RUN/f'case_{i}.json'; save(path,artifact)
            manifest['request_attempts']+=1
            manifest['cases'][i-1].update(status='started',file=path.name,attempts=1)
            save(RUN/'manifest.json',manifest)
            started=time.monotonic()
            try:
                completion=client.chat.completions.create(model=MODEL,messages=messages,temperature=0.1,max_tokens=4096)
            except Exception as exc:
                elapsed=round(time.monotonic()-started,3)
                err=safe_error(exc)
                if isinstance(exc,APIStatusError): artifact['call']['request_transmitted']=True
                artifact['call'].update(status='request_error',elapsed_seconds=elapsed,error=err)
                manifest['cases'][i-1].update(status='request_error',elapsed_seconds=elapsed,error=err)
                manifest.update(status='stopped_request_error',error=err)
                save(path,artifact); save(RUN/'manifest.json',manifest)
                print(f'case {i}: request error {err["type"]}',flush=True)
                return
            elapsed=round(time.monotonic()-started,3)
            manifest['model_responses']+=1
            artifact['call'].update(status='response_received',request_transmitted=True,model_response_received=True,
                elapsed_seconds=elapsed,returned_model=completion.model)
            artifact['provider_response']=completion.model_dump(mode='json')
            artifact['raw_response']=completion.choices[0].message.content if completion.choices else None
            artifact['call']['finish_reason']=completion.choices[0].finish_reason if completion.choices else None
            save(path,artifact)
            try:
                artifact['validation']=parse_and_validate(artifact['raw_response'],**inp)
                manifest['cases'][i-1].update(status='response_received',elapsed_seconds=elapsed,
                   returned_model=completion.model,validation_status=artifact['validation']['status'])
            except Exception as exc:
                err=safe_error(exc)
                artifact['call'].update(status='processing_error',error=err)
                manifest['cases'][i-1].update(status='processing_error',elapsed_seconds=elapsed,error=err)
                manifest.update(status='stopped_processing_error',error=err)
                save(path,artifact); save(RUN/'manifest.json',manifest); return
            save(path,artifact); save(RUN/'manifest.json',manifest)
            print(f'case {i}: response received; validation {artifact["validation"]["status"]}; {elapsed}s',flush=True)
            if completion.model != MODEL:
                manifest.update(status='stopped_model_mismatch',error={'type':'ReturnedModelMismatch'})
                save(RUN/'manifest.json',manifest); return
    manifest['status']='completed'; save(RUN/'manifest.json',manifest)

if __name__ == '__main__': main()
