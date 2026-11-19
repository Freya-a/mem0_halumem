import json,re
from pathlib import Path
from difflib import SequenceMatcher
P=Path(__file__).resolve().parents[4]
H=Path(__file__).resolve().parent
review=json.loads((P/'variants/evidence_relation_judge/runs/quote_provenance_20261110_v1/holdout_inventory.json').read_text())['rows']
recipes=json.loads((P/'diagnosis/medium_dev/recipes.json').read_text())['targets']
recipe={(x['user_uuid'],x['session_index'],x['point_index']):x for x in recipes}
users={}
for line in (P/'HaluMem/data/HaluMem-Medium.jsonl').open():
 d=json.loads(line)
 if d['uuid'] in {x['target_id'].split(':')[0] for x in review}:users[d['uuid']]=d
 if len(users)==3:break
saved={}
def find(obj,path):
 if isinstance(obj,dict):
  if isinstance(obj.get('memory_id'),str) and isinstance(obj.get('memory_text'),str) and isinstance(obj.get('facts'),list) and obj['facts']:
   if all(isinstance(f,dict) and 'raw_subfact' in f and 'evidence' in f for f in obj['facts']):
    saved.setdefault((obj['memory_id'],obj['memory_text']),[]).append((str(path.relative_to(P)),obj))
  for v in obj.values():find(v,path)
 elif isinstance(obj,list):
  for v in obj:find(v,path)
for top in ['variants/dnd_mem0_splitter/runs','variants/evidence_relation_judge/runs']:
 for p in (P/top).rglob('*.json'):
  if p.stat().st_size>4_000_000 or H in p.parents:continue
  try:find(json.loads(p.read_text(encoding='utf-8')),p)
  except (ValueError,OSError,RecursionError):pass
print('split_objects',len(saved))
out=[]
for row in review:
 uid,s,m=row['target_id'].split(':'); si=int(s[1:]);mi=int(m[1:]); r=recipe[(uid,si,mi)]
 session=users[uid]['sessions'][si]
 base=P/'results/medium_dev/williams_native_prefix5_20261028_v3/users'/uid/f'session_{si+1:03}'
 before=base/'before.json'; inp=base/'input.json'
 if not before.exists() or not inp.exists():
  out.append({'number':row['number'],'missing':'snapshot','snapshot':str(before)});continue
 snap=json.loads(before.read_text()); msgs=json.loads(inp.read_text()); assert msgs['original_session_index_zero_based']==si
 memories=snap['api_snapshot']['results']; old=r['old_proposition']
 tok=lambda x:set(re.findall(r'[a-z0-9]+',x.lower()))-{'the','and','or','to','a','as','is','in','of','his','her','he','she','user','martin','williams','daniel','donald','has','with','for'}
 scores=[]
 for x in memories:
  overlap=tok(old)&tok(x['memory']);score=len(overlap)/max(1,len(tok(old)|tok(x['memory'])))
  if score>0.06:scores.append((round(score,3),x['id'],x['memory'],len(saved.get((x['id'],x['memory']),[]))))
 scores.sort(reverse=True)
 splits=[]
 for x in memories:
  found=saved.get((x['id'],x['memory']),[])
  if found:splits.append({'memory_id':x['id'],'memory_text':x['memory'],'paths':[v[0] for v in found][:8],'facts_count':[len(v[1]['facts']) for v in found][:8]})
 out.append({'number':row['number'],'uid':uid,'session':si,'point':mi,'review_class':row['review_class'],'old_proposition':old,'old_evidence':r.get('old_evidence'),'new_evidence':r.get('new_evidence'),'new_messages':[{'idx':i,**session['dialogue'][i]} for i in r.get('new_evidence',[])],'snapshot':str(before.relative_to(P)),'snapshot_count':len(memories),'saved_split_memories':splits,'top_memory_matches':scores[:12]})
(H/'discovery.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
for x in out:
 print('\n#',x['number'],x.get('old_proposition'), 'splits',len(x.get('saved_split_memories',[])))
 for c in x.get('top_memory_matches',[])[:5]:print(' ',c)
 for s in x.get('saved_split_memories',[]):print('  SPLIT',s['memory_id'],s['memory_text'][:100],s['paths'][:1])
