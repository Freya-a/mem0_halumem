"""Launch the pinned local CUDA server and retain startup diagnostics."""
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import build_opener, ProxyHandler
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
server=ROOT/'local_backend/llama.cpp/build/bin/llama-server'
model=ROOT/'model/Qwen3.5-27B-Q4_K_M/Qwen3.5-27B-Q4_K_M.gguf'
args=[str(server),'--model',str(model),'--alias','local-qwen35','--host','127.0.0.1','--port','18081','--cors-origins','localhost','--ctx-size','4096','--parallel','1','--n-gpu-layers','99','--fit','off','--batch-size','512','--ubatch-size','128','--jinja','--reasoning','off','--reasoning-format','none','--verbose']
def gpu():
    return subprocess.run(['nvidia-smi','--query-gpu=memory.used,memory.total','--format=csv,noheader,nounits','-i','0'],capture_output=True,text=True,timeout=5).stdout.strip()
def save(info):
    with (HERE/'server_launch.json').open('x',encoding='utf-8') as f: json.dump(info,f,ensure_ascii=False,indent=2); f.write('\n')
if not model.exists() or not server.exists(): raise SystemExit('Verified model and built server required')
if model.stat().st_size != 16740812704: raise SystemExit('Unexpected model size')
with socket.socket() as probe:
    try: probe.bind(('127.0.0.1', 18081))
    except OSError as exc: raise SystemExit('Required loopback port is unavailable: ' + str(exc))
before=gpu(); env=os.environ.copy(); env['CUDA_VISIBLE_DEVICES']='0'; env.pop('GGML_CUDA_ENABLE_UNIFIED_MEMORY',None)
start=time.monotonic()
with (HERE/'server.log').open('x',encoding='utf-8') as log:
    process=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,env=env)
    opener=build_opener(ProxyHandler({}))
    status='not_ready'; error=None
    while time.monotonic()-start<300:
        if process.poll() is not None:
            status='exited'; error='server exited with code '+str(process.returncode); break
        try:
            with opener.open('http://127.0.0.1:18081/health',timeout=2) as res:
                if res.status==200:
                    status='ready'; break
        except Exception:
            pass
        time.sleep(0.25)
    seconds=round(time.monotonic()-start,3)
    save({'command':args,'cuda_visible_devices':'0','unified_memory_enabled':False,'pid':process.pid,'status':status,'startup_seconds':seconds,'gpu_before_mib_used_total':before,'gpu_after_mib_used_total':gpu(),'error':error,'log':str(HERE/'server.log')})
    print(json.dumps({'status':status,'startup_seconds':seconds,'pid':process.pid},ensure_ascii=False),flush=True)
    if status!='ready':
        if process.poll() is None: process.terminate()
        process.wait()
        raise SystemExit(1)
    try: process.wait()
    except KeyboardInterrupt:
        process.terminate(); process.wait()
