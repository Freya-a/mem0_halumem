"""Compare original saved Qwen3.5 outputs with this run, without grading semantics."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'runs/qwen35_27b_q4_v2_20261110_v1'
NAMES=['job_transition','persian_cats','skydiving','career_history','promotion']
summary={}
for name in NAMES:
 old=json.loads((BASE/f'{name}.json').read_text(encoding='utf-8'))
 new=json.loads((HERE/f'{name}.json').read_text(encoding='utf-8'))
 if old['input']!=new['input']: raise RuntimeError('input mismatch: '+name)
 o,n=old['result']['results'][0],new['result']['results'][0]
 oc,nc=o.get('candidate') or {},n.get('candidate') or {}
 if not isinstance(oc,dict):oc={}
 if not isinstance(nc,dict):nc={}
 fields=sorted(set(oc)|set(nc))
 oldcall,newcall=old['calls'][0],new['calls'][0]
 params=lambda r:{k:v for k,v in r['request'].items() if k!='prompt'}
 if params(oldcall)!=params(newcall): raise RuntimeError('generation parameters differ: '+name)
 if oldcall['messages'][1]!=newcall['messages'][1]: raise RuntimeError('user message differs: '+name)
 summary[name]={'input_equal':True,'user_message_equal':True,'generation_parameters_equal':True,'calls_attempted':new['calls_attempted'],'v2':{'status':o['status'],'candidate':o.get('candidate'),'errors':o.get('errors'),'validation':o['validation'],'elapsed_seconds':oldcall['elapsed_seconds']},'experiment':{'status':n['status'],'candidate':n.get('candidate'),'errors':n.get('errors'),'validation':n['validation'],'elapsed_seconds':newcall['elapsed_seconds']},'changed_fields':{k:{'v2':oc.get(k),'experiment':nc.get(k)} for k in fields if oc.get(k)!=nc.get(k)},'semantic_correctness':'not_checked'}
with (HERE/'comparison.json').open('x',encoding='utf-8') as f: json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:{'old_status':v['v2']['status'],'new_status':v['experiment']['status'],'changed_fields':list(v['changed_fields'])} for k,v in summary.items()},ensure_ascii=False,indent=2))
