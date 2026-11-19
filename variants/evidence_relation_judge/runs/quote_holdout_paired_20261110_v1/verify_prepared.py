"""Offline provenance check: input records, saved snapshots, user dialogue and split evidence."""
import hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; PROJECT=HERE.parents[3];COMP=HERE.parents[1]
sys.path.insert(0,str(COMP/'part1_relation_judge'));import relation_judge_v2 as judge
rows=json.loads((HERE/'prepared.json').read_text()); recipes=json.loads((PROJECT/'diagnosis/medium_dev/recipes.json').read_text())['targets']; recipes={(x['user_uuid'],x['session_index'],x['point_index']):x for x in recipes}
users={}
for line in (PROJECT/'HaluMem/data/HaluMem-Medium.jsonl').open():
 d=json.loads(line)
 if d['uuid'] in {x['user_uuid'] for x in rows}:users[d['uuid']]=d
 if len(users)==3:break
review=json.loads((HERE/'split_review.json').read_text());reports=[]
for row in rows:
 uid,si,mi=row['user_uuid'],row['session_index'],row['point_index']; rr=recipes[uid,si,mi]; sess=users[uid]['sessions'][si]
 path=Path(row['old_snapshot']); assert hashlib.sha256(path.read_bytes()).hexdigest()==row['old_snapshot_sha256'];snap=json.loads(path.read_text()); before={x['id']:x['memory'] for x in snap['api_snapshot']['results']}
 session_input=json.loads((path.parent/'input.json').read_text()); assert session_input['original_session_index_zero_based']==si and session_input['user_uuid']==uid
 source_msgs=sess['dialogue']; snapshot_msgs=session_input['raw_dialogue']
 assert len(snapshot_msgs)==len(source_msgs)
 for a,b in zip(snapshot_msgs,source_msgs):assert a['role']==b['role'] and a['content']==b['content'] and a['timestamp']==b['timestamp']
 assert len(row['source_context'])==len(rr['old_evidence']) and len(row['new_evidence'])==len(rr['new_evidence'])
 for got,(osi,j) in zip(row['source_context'],rr['old_evidence']):
  src=users[uid]['sessions'][osi]['dialogue'][j]; assert got['text']==src['content'] and got['speaker']==src['role']=='user' and got['recorded_at']==src['timestamp'] and osi<si
 for got,j in zip(row['new_evidence'],rr['new_evidence']):
  src=source_msgs[j];assert got['text']==src['content'] and got['speaker']==src['role']=='user' and got['recorded_at']==src['timestamp']
 for mem in row['old_memory_records']:
  assert before[mem['id']]==mem['memory']
  if 'split_key' not in mem:continue
  key=mem['split_key'];a=json.loads((HERE/'split_results'/f'{key}.json').read_text()); assert a['result']['memory_text']==mem['memory'] and a['result']['memory_id']==mem['id']
  req={'split_result':a['result'],'source_context':row['source_context'],'new_evidence':row['new_evidence'],'time_info':None}
  judge.v1.validate_request(req)
 reports.append({'record':row['number'],'original_target':row['target_id'],'memory_count':len(row['old_memory_records']),'old_context_count':len(row['source_context']),'new_evidence_count':len(row['new_evidence']),'source_and_snapshot_checks':'passed','split_semantic_status':'excluded_upstream_bad_title' if row['number']==2 else 'not_run_merged' if row['number']==20 else 'initial_screen_only'})
with (HERE/'prepared_verification.json').open('x',encoding='utf8') as f:json.dump({'records':reports,'count':len(reports),'notes':'Program provenance checks do not verify semantic entailment; target mappings and splits are preliminary and await human review.'},f,ensure_ascii=False,indent=2);f.write('\n')
print('verified 18 target records against source dialogue and full before snapshots; judge input provenance validated')
