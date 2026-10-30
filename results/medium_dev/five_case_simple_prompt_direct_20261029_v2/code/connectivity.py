#!/usr/bin/env python3
"""Exactly one LLM and one embedding connectivity request, no SDK retries."""
import json, os, sys, time, traceback
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from openai import OpenAI
ROOT=Path('/home/shu1004/ld/system/mem0_halumem_diagnosis')
OUT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as run
import local_smoke as base

def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def save(name,obj): run.atomic(OUT/name,obj)
def main():
    profile=run.data.read(run.PROFILE); settings,_=run.settings_check(ROOT/'.env.local',profile,True)
    hosts={urlsplit(settings[k]).hostname for k in ('LLM_BASE_URL','EMBEDDING_BASE_URL')}
    assert hosts=={'dashscope.aliyuncs.com'}
    existing=[]
    for name in ('NO_PROXY','no_proxy'):
        for item in os.environ.get(name,'').split(','):
            item=item.strip()
            if item and item not in existing: existing.append(item)
    if 'dashscope.aliyuncs.com' not in existing: existing.append('dashscope.aliyuncs.com')
    os.environ['NO_PROXY']=os.environ['no_proxy']=','.join(existing)
    proxy_map=httpx._utils.get_environment_proxies()
    # httpx uses this marker to bypass both HTTP and HTTPS proxy for this domain.
    assert any(proxy is None and httpx._utils.URLPattern(pattern).matches(httpx.URL('https://dashscope.aliyuncs.com/compatible-mode/v1')) for pattern,proxy in proxy_map.items())
    save('network_environment.json',{'time':now(),'llm_host':urlsplit(settings['LLM_BASE_URL']).hostname,'embedding_host':urlsplit(settings['EMBEDDING_BASE_URL']).hostname,'change':'only this run process and children: NO_PROXY/no_proxy append exact dashscope.aliyuncs.com, retaining existing exclusions','httpx_bypass_rule_verified':True,'system_proxy_changed':False,'env_file_changed':False,'sdk_retries':0,'timeout_seconds':profile['timeout_seconds']})
    results={}
    for kind in ('llm','embedding'):
        request={'model':settings['LLM_MODEL'],'messages':[{'role':'user','content':'Reply with OK.'}],'max_tokens':16,'temperature':0.5} if kind=='llm' else {'model':settings['EMBEDDING_MODEL'],'input':'Connectivity test.','dimensions':1024,'encoding_format':'float'}
        key=settings['LLM_API_KEY'] if kind=='llm' else settings['EMBEDDING_API_KEY']; url=settings['LLM_BASE_URL'] if kind=='llm' else settings['EMBEDDING_BASE_URL']
        client=OpenAI(api_key=key,base_url=url,timeout=profile['timeout_seconds'],max_retries=0)
        entry={'kind':kind,'started_at':now(),'status':'started','request':request}; save('connectivity_'+kind+'.json',entry); start=time.perf_counter()
        try:
            response=client.chat.completions.create(**request) if kind=='llm' else client.embeddings.create(**request)
            body=response.model_dump(mode='json')
            if kind=='embedding':
                dims=len(body['data'][0]['embedding']); body['data']=[{'index':x['index'],'dimensions':len(x['embedding'])} for x in body['data']]; entry['dimensions']=dims
                if dims!=1024: raise ValueError('embedding dimension is not 1024')
            entry.update(status='ok',response=body)
        except Exception:
            entry.update(status='error_or_unknown_sent',error=base.clean(traceback.format_exc()))
        finally:
            entry.update(finished_at=now(),elapsed_seconds=time.perf_counter()-start); save('connectivity_'+kind+'.json',entry); client.close()
        results[kind]={'status':entry['status'],'dimensions':entry.get('dimensions'),'elapsed_seconds':entry['elapsed_seconds'],'model_returned':entry.get('response',{}).get('model'),'usage':entry.get('response',{}).get('usage')}
        print(json.dumps({'kind':kind,**results[kind]},ensure_ascii=False),flush=True)
    ok=all(x['status']=='ok' for x in results.values()) and results['embedding']['dimensions']==1024
    save('connectivity_summary.json',{'status':'PASS' if ok else 'FAIL','tests':results,'calls_attempted':2,'finished_at':now()})
    return 0 if ok else 1
if __name__=='__main__': sys.exit(main())
