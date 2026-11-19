"""Freeze target/source mapping; no model calls or memory writes."""
import hashlib,json,sys
from copy import deepcopy
from pathlib import Path
HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[3]
COMP=HERE.parents[1]
review_path=COMP/'runs/quote_provenance_20261110_v1/holdout_inventory.json'
reviews=json.loads(review_path.read_text())['rows']
recipes=json.loads((PROJECT/'diagnosis/medium_dev/recipes.json').read_text())['targets']
recipe={(x['user_uuid'],x['session_index'],x['point_index']):x for x in recipes}
USER_IDS={x['target_id'].split(':')[0] for x in reviews}
dataset=PROJECT/'HaluMem/data/HaluMem-Medium.jsonl'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(dataset)!='486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7':raise ValueError('dataset hash mismatch')
users={}
for line in dataset.open(encoding='utf-8'):
 u=json.loads(line)
 if u['uuid'] in USER_IDS:users[u['uuid']]=u
 if len(users)==3:break
selected={1:['d575dfc1-59ec-43b4-83c4-6b94457a83f6'],2:['ecc0de53-fe20-4875-bfb5-e1b5ea7d6470'],3:['b79a25de-05b7-47b7-bb0b-8c59b44a61ec'],4:['a1332815-d6ba-4bdc-9ffa-657f7315d0ed'],5:['0da9428c-2fe6-4254-b818-58991562b49d'],6:['a90e498c-4586-4237-8a4b-c830847f8819'],9:['8602da08-fefc-4875-ad50-dba104642365'],12:['4ffee399-c31f-4827-b5fc-5c661baf1fc9'],13:['4ffee399-c31f-4827-b5fc-5c661baf1fc9'],15:['e76eedc7-87e9-4282-b7db-68ed72b0c8ba'],16:['d1e2e0e6-45fd-49ef-bbec-e6521db283e6'],17:['aca2b85d-8856-4989-bfdd-b032fde1bda3'],18:['05afde13-35bd-4d26-bbae-6de427d58db1'],19:['46374680-0009-4625-a3a7-f2b4e329a7b5'],21:['e5ec2bdf-d263-4e0f-a4bd-e649154c5993'],22:['37756be3-aaee-4e1c-b8f7-a5fed3d94890','98c6916c-8aa9-4560-94ce-5697f39ac818'],23:['37756be3-aaee-4e1c-b8f7-a5fed3d94890','98c6916c-8aa9-4560-94ce-5697f39ac818']}
if set(selected)!={x['number'] for x in reviews}-{20}:raise ValueError('selection mismatch')
rows=[]; splits={}
for h in reviews:
 uid,s,m=h['target_id'].split(':'); si=int(s[1:]); mi=int(m[1:]); src=users[uid]; session=src['sessions'][si]; r=recipe[uid,si,mi]
 snapdir=PROJECT/'results/medium_dev/williams_native_prefix5_20261028_v3/users'/uid/f'session_{si+1:03}'
 before=snapdir/'before.json'; inpath=snapdir/'input.json'
 snap=json.loads(before.read_text()); recorded=json.loads(inpath.read_text())
 if recorded['user_uuid']!=uid or recorded['original_session_index_zero_based']!=si or not snap['not_truncated']:raise ValueError('bad snapshot')
 memories={x['id']:x for x in snap['api_snapshot']['results']}
 contexts=[]
 for j,(osi,idx) in enumerate(r['old_evidence'],1):
  if osi>=si: raise ValueError('old context not prior')
  msg=src['sessions'][osi]['dialogue'][idx]
  if msg['role']!='user':raise ValueError('old context not user')
  contexts.append({'source_id':f'ctx-{j}','source_ref':f'HaluMem/data/HaluMem-Medium.jsonl uuid={uid} /sessions/{osi}/dialogue/{idx}/content','text':msg['content'],'speaker':msg['role'],'recorded_at':msg['timestamp']})
 new=[]
 for idx in r['new_evidence']:
  msg=session['dialogue'][idx]
  if msg['role']!='user':raise ValueError('new evidence not user')
  new.append({'source_id':f'dialogue-{idx}','source_ref':f'{h["target_id"]} /sessions/{si}/dialogue/{idx}/content','text':msg['content'],'speaker':msg['role'],'recorded_at':msg['timestamp']})
 row={'number':h['number'],'target_id':h['target_id'],'user_uuid':uid,'session_index':si,'point_index':mi,'human_review':{k:h[k] for k in ['review_class','supported_new_state','allowed_modification_scope','uncertain_current_state']},'relation_label_review':'pending','old_snapshot':str(before),'old_snapshot_sha256':sha(before),'source_context':contexts,'new_evidence':new,'old_memory_records':[], 'eligibility':'merged_excluded' if h['number']==20 else 'pending_split','relatedness_note':'same user as original five; independence not established'}
 if h['number']==20:
  row['exclusion_reason']='human review merges main topic into 17/18; avoid treating as an independent test'; row['merged_into']=[17,18]
  # retain candidate old source and all new material without constructing an execution input
  for mid in ['05afde13-35bd-4d26-bbae-6de427d58db1','2b65ace7-5f31-4cb5-9582-8b8a1d99dd2b']:
   if mid in memories:row['old_memory_records'].append({'id':mid,'memory':memories[mid]['memory'],'split_status':'not_run_merged'})
 else:
  for mid in selected[h['number']]:
   if mid not in memories:raise ValueError(f'memory missing {h["number"]} {mid}')
   mem=memories[mid]['memory']; primary=deepcopy(contexts[:1]); splitinput={'memory_id':mid,'memory_text':mem,'source_context':primary}; key=hashlib.sha256(json.dumps(splitinput,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16]
   if key not in splits:splits[key]={'input':splitinput,'records':[],'status':'pending'}
   splits[key]['records'].append(h['number']); row['old_memory_records'].append({'id':mid,'memory':mem,'split_key':key})
 if h['number'] in [2,5,6,15]:row['review_role']='repeat_confirmation_control_not_independent_novelty'
 if h['number'] in [12,13]:row['relatedness_note']='same old memory and session; distinct overlapping evidence and target; not independent'
 if h['number'] in [17,18,19]:row['relatedness_note']='same user/session with different target attributes; plan mentions these targets; no independent exposure claim'
 if h['number'] in [22,23]:row['relatedness_note']='same old people/memory across different sessions; shared identity; target 22 previously reviewed in native D'
 if h['number']==18:row['relatedness_note']='same memory ID as prior career_history case but earlier snapshot text differs; same user, distinct session; not independent'
 rows.append(row)
# Reuse the validated saved v4 split when its memory and first context match.
known=PROJECT/'variants/dnd_mem0_splitter/runs/real_mem0_v3_v4_comparison_20261104_once'
old_input=json.loads((known/'inputs/case_02_subject_and_roster.json').read_text())
old_result=json.loads((known/'runs/case_02_subject_and_roster/v4/result.json').read_text())
for key,item in splits.items():
 if item['input']['memory_id']==old_result['memory_id']:
  assert item['input']['memory_text']==old_result['memory_text'] and item['input']['source_context'][0]['text']==old_input['source_context'][0]['text']
  item['input']=old_input; item['status']='reused_v4';item['reused_result_path']=str(known/'runs/case_02_subject_and_roster/v4/result.json');item['reused_result_sha256']=sha(Path(item['reused_result_path']))
  # Preserve ctx-1 from saved split; supplemental contexts (if present) retain distinct IDs.
  for row in rows:
   if 4==row['number']:row['source_context']=deepcopy(old_input['source_context'])
for name,obj in [('prepared.json',rows),('split_plan.json',splits)]:
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('records',len(rows),'excluded_merged',sum(x['eligibility']=='merged_excluded' for x in rows),'record_memories',sum(len(x['old_memory_records']) for x in rows if x['eligibility']!='merged_excluded'),'unique_splits',len(splits),'reused',sum(x['status']=='reused_v4' for x in splits.values()))
