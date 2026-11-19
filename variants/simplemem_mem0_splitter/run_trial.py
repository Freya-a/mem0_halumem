"""One-shot five-case trial; no automatic retries or resume."""
import json
import os
from pathlib import Path
import re
import time
from dotenv import dotenv_values
from openai import OpenAI, APIStatusError
from splitter import build_extraction_prompt, parse_and_validate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN = HERE / 'run'
MODEL = 'qwen-plus-2025-12-01'
# Pointers into original_memories, never pass the enclosing updated memory to model.
SELECTED = [(4,1,1), (9,2,0), (11,1,1), (16,3,0), (3,1,0)]
SYSTEM = 'You are a professional information extraction assistant, skilled at extracting structured, unambiguous information from conversations. You must output valid JSON format.'


def save(path, data):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.replace(temp,path)


def main():
    RUN.mkdir(exist_ok=True)
    if (RUN/'manifest.json').exists():
        raise RuntimeError('Trial already started: refusing to repeat requests')
    with (ROOT/'dataset/HaluMem-Medium/HaluMem-Medium.jsonl').open(encoding='utf-8') as f:
        record=json.loads(next(f))
    cases=[]
    for n,(session,index,old_index) in enumerate(SELECTED,1):
        point=next(x for x in record['sessions'][session]['memory_points'] if x['index']==index)
        text=point['original_memories'][old_index]
        cases.append({'memory_id':f'halumem-1-s{session}-m{index}-old{old_index}', 'memory_text':text, 'source_context':None,
                      'source':{'file':'dataset/HaluMem-Medium/HaluMem-Medium.jsonl','line':1,'uuid':record['uuid'],'session_index_zero_based':session,'memory_point_index':index,'original_memories_index_zero_based':old_index}})
    manifest={'model':MODEL,'maximum_requests':5,'automatic_retries':0,'call_count':0,'cases':[], 'status':'preparing'}
    save(RUN/'cases.json',cases); save(RUN/'manifest.json',manifest)
    # Follow the existing medium_full profile; read credentials only inside runtime.
    config=dotenv_values(ROOT/'.env.server.medium-full')
    key=os.environ.get('DASHSCOPE_API_KEY') or config.get('DASHSCOPE_API_KEY')
    workspace=os.environ.get('DASHSCOPE_WORKSPACE_ID') or config.get('DASHSCOPE_WORKSPACE_ID')
    if not key or not workspace or not re.fullmatch(r'(?:llm|ws)-[a-zA-Z0-9-]+', workspace):
        manifest.update(status='configuration_error',error='DASHSCOPE_API_KEY or valid DASHSCOPE_WORKSPACE_ID missing'); save(RUN/'manifest.json',manifest); return
    profile=json.loads((ROOT/'config/medium_full_qwen_plus_20251201.json').read_text())
    base=profile['llm']['config']['openai_base_url'].replace('{DASHSCOPE_WORKSPACE_ID}',workspace)
    client=OpenAI(api_key=key,base_url=base,max_retries=0,timeout=180.0)
    manifest['status']='running'; save(RUN/'manifest.json',manifest)
    for i, case in enumerate(cases,1):
        inp={k:case[k] for k in ('memory_id','memory_text','source_context')}
        prompt=build_extraction_prompt(**inp)
        messages=[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}]
        artifact={'input':inp,'source':case['source'],'request':{'model':MODEL,'messages':messages,'temperature':0.1,'max_tokens':4096,'automatic_retries':0},
                  'call':{'model':MODEL,'attempt':1,'status':'started'},'raw_response':None,'validation':None}
        path=RUN/f'case_{i}.json'; save(path,artifact)
        manifest['call_count']+=1
        manifest['cases'].append({'file':path.name,'memory_id':inp['memory_id'],'status':'started'})
        save(RUN/'manifest.json',manifest)
        started=time.monotonic()
        try:
            completion=client.chat.completions.create(model=MODEL,messages=messages,temperature=0.1,max_tokens=4096)
            elapsed=round(time.monotonic()-started,3)
            artifact['raw_response']=completion.choices[0].message.content
            artifact['call'].update(status='success',elapsed_seconds=elapsed,returned_model=completion.model,finish_reason=completion.choices[0].finish_reason)
            artifact['validation']=parse_and_validate(artifact['raw_response'],**inp)
            manifest['cases'][-1].update(status='success',elapsed_seconds=elapsed,returned_model=completion.model,validation_status=artifact['validation']['status'])
            save(path,artifact); save(RUN/'manifest.json',manifest)
            if completion.model != MODEL:
                manifest.update(status='stopped_model_mismatch',error='returned model differs from requested snapshot'); break
        except Exception as exc:
            elapsed=round(time.monotonic()-started,3)
            # Avoid persisting exception bodies, which may contain credentials or request headers.
            msg={'type':type(exc).__name__}
            if isinstance(exc,APIStatusError): msg['http_status']=exc.status_code
            causes=[]
            cause=exc.__cause__
            while cause is not None and len(causes)<5:
                detail={'type':type(cause).__name__}
                if isinstance(cause,OSError): detail['errno']=cause.errno
                causes.append(detail); cause=cause.__cause__
            if causes: msg['cause_chain']=causes
            artifact['call'].update(status='error',elapsed_seconds=elapsed,error=msg)
            manifest['cases'][-1].update(status='error',elapsed_seconds=elapsed,error=msg)
            manifest.update(status='stopped_api_error',error=msg)
            save(path,artifact); break
    else: manifest['status']='completed'
    save(RUN/'manifest.json',manifest)

if __name__ == '__main__': main()
