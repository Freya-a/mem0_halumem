#!/usr/bin/env python3
import json,sqlite3,hashlib,sys,collections
import engine,run_eval
from pathlib import Path
OUT=Path(__file__).resolve().parent
records=[json.loads(l) for l in (OUT/'records.jsonl').open()];calls=[json.loads(l) for l in (OUT/'api_calls.jsonl').open()];call_by_id={x['id']:x for x in calls};assert len(records)==131 and len({x['id'] for x in records})==131
assert len([r for r in records if r['kind']=='update'])==56 and len([r for r in records if r['kind']=='qa'])==75
snapshots={}; verification={'records':0,'retrievals_recomputed':0,'pilot_retrievals_validated':0,'answer_prompts_verified':0,'judge_prompts_verified':0,'valid_judgments_verified':0,'errors':[]}
with sqlite3.connect(OUT/'checkpoints.sqlite3') as c:
 embedding={i:json.loads(p) for i,p in c.execute("select id,payload from stages where stage='embedding' and status='ok'")}
for r in records:
 try:
  src=r['source'];p=Path(src['snapshot_path']);path=str(p)
  if path not in snapshots:
   assert hashlib.sha256(p.read_bytes()).hexdigest()==src['snapshot_sha256'];d=json.loads(p.read_text());snapshots[path]={str(x['id']):x for x in d['database_points_with_vectors']}
  points=snapshots[path]
  for hit in r['hits']:
   point=points[hit['id']];assert hit['memory']==point['payload']['data'] and hit['timestamp']==point['payload'].get('created_at') and point['payload']['user_id']==src['uuid']
  v=embedding[r['id']]
  if 'vector' in v:
   rebuilt=run_eval.retrieve(src,v['vector'],10 if r['kind']=='update' else 20)
   assert [x['id'] for x in rebuilt]==[x['id'] for x in r['hits']]
   assert all(abs(a['score']-b['score'])<1e-6 for a,b in zip(rebuilt,r['hits']))
   verification['retrievals_recomputed']+=1
  else:assert v.get('reused_pilot');verification['pilot_retrievals_validated']+=1
  own=[call_by_id[c] for c in r['model_calls']];subject=src['memory_point'] if r['kind']=='update' else src['question'];memories=[f"{h['timestamp']}: {h['memory']}" for h in r['hits']]
  judges=[x for x in own if x['stage']=='judge'];assert judges
  if r['kind']=='update':
   prompt=run_eval.eval_tools.EVALUATION_PROMPT_FOR_UPDATE_MEMORY.format(memories='\n'.join(memories),updated_memory=subject['memory_content'],original_memory='\n'.join(subject['original_memories']))
  else:
   context='Memories for user '+src['uuid']+':\n\n    '+json.dumps(memories,indent=4)+'\n'
   answer=next(x for x in own if x['stage']=='answer');assert answer['request']['prompt']==engine.answer_prompt(context,subject);verification['answer_prompts_verified']+=1
   response=r['stages']['answer']['payload']['text'];prompt=run_eval.eval_tools.EVALUATION_PROMPT_FOR_QUESTION.format(question=subject['question'],reference_answer=subject['answer'],key_memory_points='\n'.join(e['memory_content'] for e in subject['evidence']),response=response)
  for judge in judges:assert judge['request']['prompt']==prompt
  verification['judge_prompts_verified']+=1
  if r['judge']=='ok':
   score=r['stages']['judge']['payload']['score'];assert score==engine.parse_score(r['stages']['judge']['payload']['raw']);assert score['evaluation_result']==r['label'];verification['valid_judgments_verified']+=1
  verification['records']+=1
 except Exception as e:verification['errors'].append({'id':r['id'],'type':type(e).__name__})
# Scan output artifacts for the two local credentials without printing their values.
keys=[]
for l in (engine.ROOT/'.env.local').read_text().splitlines():
 if '=' in l and not l.lstrip().startswith('#'):
  k,v=l.split('=',1)
  if k.strip().endswith('_API_KEY') and len(v.strip().strip('"\''))>8:keys.append(v.strip().strip('"\'').encode())
leaks=[]
for p in OUT.rglob('*'):
 if p.is_file() and p.name not in ('run.lock',):
  data=p.read_bytes()
  if any(k in data for k in keys):leaks.append(str(p.relative_to(OUT)))
verification['credential_leak_files']=leaks
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(verification,ensure_ascii=False,indent=2));assert not verification['errors'] and not leaks
