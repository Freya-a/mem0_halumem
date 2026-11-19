"""Run v4 and v8 once each on frozen inputs; keep success and failure artifacts."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
sys.path.insert(0,str(BASE))
from splitter import split_memory, _read_json, ValidationError
from real_backend import OpenAICompatibleBackend, load_model_settings

def sha(b): return hashlib.sha256(b).hexdigest()
def now(): return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def save(p,x):
    with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2); f.write('\n')
def main():
    with (ROOT/'started.marker').open('x',encoding='utf-8') as f: f.write(now())
    manifest=_read_json(ROOT/'manifest.json')
    prompts={v:(ROOT/'prompts'/f'{v}.txt').read_bytes() for v in ('v4','v8')}
    for v,p in prompts.items(): assert sha(p)==manifest['prompts_sha256'][v]
    for case in manifest['cases']: assert sha((ROOT/'inputs'/f"{case['case']}.json").read_bytes()) == case['input_sha256']
    settings=load_model_settings(BASE.parent.parent/'.env.local')
    save(ROOT/'attempt.json',{'model':settings.model,'generation_parameters':settings.generation,
         'timeout_seconds':settings.timeout,'sdk_max_retries':0,'provider_defaults_and_model_revision':'unknown',
         'order':[{'case':case['case'],'version':v} for i,case in enumerate(manifest['cases']) for v in (('v4','v8') if i%2==0 else ('v8','v4'))]})
    results=[]
    for i,case in enumerate(manifest['cases']):
        for version in (('v4','v8') if i%2==0 else ('v8','v4')):
            d=ROOT/case['case']/version; d.mkdir(parents=True,exist_ok=False)
            request=_read_json(ROOT/'inputs'/f"{case['case']}.json")
            backend=None; result=None; failure=None
            save(d/'attempt.json',{'case':case['case'],'version':version,'started_at':now(),
                'prompt_sha256':sha(prompts[version]),'input_sha256':case['input_sha256']})
            try:
                backend=OpenAICompatibleBackend(settings,prompts[version].decode('utf-8'))
                result=split_memory(request,backend)
            except ValidationError as error: failure=error.as_dict()
            finally:
                if backend is not None: backend.close()
            if backend and isinstance(backend.raw_content,str):
                with (d/'raw_content.txt').open('x',encoding='utf-8') as f: f.write(backend.raw_content.replace(settings.api_key,'[REDACTED]'))
            save(d/'response_metadata.json',backend.response_metadata if backend else {})
            if result is not None: save(d/'result.json',result)
            report={'case':case['case'],'version':version,'finished_at':now(),
                'model_calls':backend.call_count if backend else 0,'program_status':'passed' if result is not None else 'failed',
                'fact_count':len(result['facts']) if result is not None else None,'error':failure,
                'semantic_status':'not evaluated by program'}
            save(d/'report.json',report); results.append(report); print(json.dumps(report,ensure_ascii=False),flush=True)
    save(ROOT/'batch_completion.json',{'finished_at':now(),'reports':results,'calls':sum(r['model_calls'] for r in results),'passed':sum(r['program_status']=='passed' for r in results)})
if __name__=='__main__': main()
