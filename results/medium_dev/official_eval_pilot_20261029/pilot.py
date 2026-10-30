#!/usr/bin/env python3
"""Small, non-replay HaluMem scorer pilot using immutable session snapshots."""
import os,sys,json,hashlib,re,time,types
from pathlib import Path
from datetime import datetime
from collections import Counter
from openai import OpenAI
from qdrant_client import QdrantClient, models

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RUN=ROOT/'results/medium_dev/williams_native_prefix5_20261028_v3'
DATA=ROOT/'HaluMem/data/HaluMem-Medium.jsonl'
U='1b846c59-456e-9550-dffd-4d23f1eca81f'
ORD=4

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj): (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def stamp():return datetime.now().astimezone().isoformat()

def audit():
 users={x.name for x in (RUN/'users').iterdir() if x.is_dir()}
 source={d['uuid']:d for l in DATA.open() if (d:=json.loads(l))['uuid'] in users}
 stats=[];errors=[]
 for uid in sorted(users):
  cp=json.loads((RUN/'users'/uid/'checkpoint.json').read_text())
  sorted_sessions=sorted(enumerate(source[uid]['sessions']),key=lambda x:datetime.strptime(x[1]['start_time'],'%b %d, %Y, %H:%M:%S'))
  for c,(idx,s) in zip(cp['commits'],sorted_sessions):
   n=c['ordinal']; folder=RUN/'users'/uid/f'session_{n:03d}'
   for name in ['input.json','before.json','after.json']:
    actual=digest(folder/name); expected=c['artifacts_sha256'][name]
    if actual!=expected:errors.append([uid,n,name,'hash mismatch'])
   inp=json.loads((folder/'input.json').read_text()); snap=json.loads((folder/'after.json').read_text());points=snap['database_points_with_vectors']
   if inp['original_session_index_zero_based']!=idx or inp['raw_dialogue']!=s['dialogue'] or inp['messages']!=[{'role':m['role'],'content':m['content']} for m in s['dialogue']]:errors.append([uid,n,'input mismatch'])
   if not snap['not_truncated'] or len(points)!=snap['database_count_exact'] or any(p['payload'].get('user_id')!=uid or not isinstance(p['vector'],list) or len(p['vector'])!=1024 for p in points):errors.append([uid,n,'snapshot mismatch'])
   stat={'uuid':uid,'ordinal':n,'source_index':idx,'start_time':s['start_time'],'end_time':s['end_time'],'snapshot_count':len(points),'update_candidates':sum(m['is_update']=='True' and bool(m.get('original_memories')) for m in s['memory_points']),'questions':len(s.get('questions',[])),'after_sha256':digest(folder/'after.json')}
   stats.append(stat)
  if len(cp['commits'])!=cp['completed_ordinal']:errors.append([uid,'checkpoint length mismatch'])
 result={'dataset_sha256':digest(DATA),'sessions':stats,'errors':errors,'count':len(stats),'updates_with_original':sum(s['update_candidates'] for s in stats),'questions':sum(s['questions'] for s in stats),'notes':'候选数为有原始记忆的更新点；官方评分器会将未提供或空检索的更新点划入integrity而非update。'}
 save('snapshot_audit.json',result)
 if errors:raise RuntimeError('snapshot audit failed; see snapshot_audit.json')
 return source

source=audit();session=source[U]['sessions'][3]
folder=RUN/'users'/U/'session_004';snap=json.loads((folder/'after.json').read_text())
update=next(m for m in session['memory_points'] if m['is_update']=='True' and m.get('original_memories'))
qa=session['questions'][0]
assert json.loads((folder/'input.json').read_text())['original_session_index_zero_based']==3
q=QdrantClient(':memory:');q.create_collection('snapshot',vectors_config=models.VectorParams(size=1024,distance=models.Distance.COSINE))
q.upsert('snapshot',[models.PointStruct(id=p['id'],vector=p['vector'],payload=p['payload']) for p in snap['database_points_with_vectors']])
assert q.count('snapshot',exact=True).count==snap['database_count_exact']
# Explicitly load only this file; process overrides for the specific keys are respected.
env={}
for line in (ROOT/'.env.local').read_text().splitlines():
 line=line.strip()
 if line and not line.startswith('#') and '=' in line:
  k,v=line.split('=',1);env[k.strip()]=v.strip().strip('"\'')
for k in ['LLM_BASE_URL','LLM_API_KEY','LLM_MODEL','EMBEDDING_BASE_URL','EMBEDDING_API_KEY','EMBEDDING_MODEL','EMBEDDING_DIMS']:
 if os.getenv(k):env[k]=os.environ[k]
assert env['LLM_MODEL']=='qwen-plus' and env['EMBEDDING_MODEL']=='text-embedding-v4' and int(env['EMBEDDING_DIMS'])==1024
os.environ['NO_PROXY']='dashscope.aliyuncs.com';os.environ['no_proxy']='dashscope.aliyuncs.com'
llm=OpenAI(api_key=env['LLM_API_KEY'],base_url=env['LLM_BASE_URL'],timeout=180,max_retries=0)
emb=OpenAI(api_key=env['EMBEDDING_API_KEY'],base_url=env['EMBEDDING_BASE_URL'],timeout=180,max_retries=0)
calls=[]
def call(kind,fn):
 row={'kind':kind,'started':stamp()};calls.append(row);save('api_calls.json',calls);t=time.monotonic()
 try:
  r=fn();row.update(status='ok',elapsed_seconds=round(time.monotonic()-t,3),response_model=getattr(r,'model',None),usage=r.usage.model_dump() if r.usage else None,request_id=getattr(r,'_request_id',None));save('api_calls.json',calls);return r
 except Exception as e:
  row.update(status='error',elapsed_seconds=round(time.monotonic()-t,3),error_type=type(e).__name__,error='API request failed; details suppressed to prevent accidental secret disclosure');save('api_calls.json',calls);raise

def search(query,limit,kind):
 r=call(kind,lambda:emb.embeddings.create(model=env['EMBEDDING_MODEL'],input=[query.replace('\n',' ')],dimensions=1024))
 hits=q.query_points('snapshot',query=r.data[0].embedding,query_filter=models.Filter(must=[models.FieldCondition(key='user_id',match=models.MatchValue(value=U))]),limit=limit).points
 return [{'id':str(h.id),'memory':h.payload['data'],'timestamp':h.payload.get('created_at'),'score':h.score} for h in hits]

# Import official prompts and functions without importing llms.py, whose dotenv dependency is absent.
sys.path.insert(0,str(ROOT/'HaluMem/eval'))
sys.modules['llms']=types.SimpleNamespace(llm_request_for_json=lambda p:None)
import eval_tools,prompts
save('metadata.json',{'run':str(RUN),'snapshot':str(folder/'after.json'),'snapshot_sha256':digest(folder/'after.json'),'uuid':U,'ordinal_one_based':4,'source_session_index_zero_based':3,'session_end':session['end_time'],'update_source_memory_index':update['index'],'qa_source_question_index_zero_based':0,'embedding_model':env['EMBEDDING_MODEL'],'embedding_dimensions':1024,'answer_and_judge_model':env['LLM_MODEL'],'temperature':0.0,'max_tokens':16384,'timeout_seconds':180,'sdk_retries':0,'search_limits':{'update':10,'qa':20},'notes':['使用每会话after快照和本地Qdrant cosine重建检索；非原运行期间保存的检索。','快照created_at为实际执行时间，不是对话时间；保持官方上下文格式并披露限制。','qwen-plus作为回答模型和评分模型；相对于论文及托管Mem0流程是协议调整。','无原始库写入或会话重放。']})
try:
 uh=search(update['memory_content'],10,'update_embedding');save('update_retrieval.json',uh)
 memories=[f"{h['timestamp']}: {h['memory']}" for h in uh]
 update_prompt=eval_tools.EVALUATION_PROMPT_FOR_UPDATE_MEMORY.format(memories='\n'.join(memories),updated_memory=update['memory_content'],original_memory='\n'.join(update['original_memories']))
 (OUT/'update_judge_prompt.txt').write_text(update_prompt)
 qh=search(qa['question'],20,'qa_embedding');save('qa_retrieval.json',qh)
 context='Memories for user '+U+':\n\n    '+json.dumps([f"{h['timestamp']}: {h['memory']}" for h in qh],indent=4)+'\n'
 answer_prompt=prompts.PROMPT_MEMZERO.format(context=context,question=qa['question']);(OUT/'qa_answer_prompt.txt').write_text(answer_prompt)
 def completion(kind,prompt):
  r=call(kind,lambda:llm.chat.completions.create(model=env['LLM_MODEL'],messages=[{'role':'user','content':prompt}],temperature=0,max_tokens=16384));return r.choices[0].message.content or ''
 response=completion('qa_answer',answer_prompt);(OUT/'qa_answer.txt').write_text(response+'\n')
 judge_prompt=eval_tools.EVALUATION_PROMPT_FOR_QUESTION.format(question=qa['question'],reference_answer=qa['answer'],key_memory_points='\n'.join(i['memory_content'] for i in qa['evidence']),response=response);(OUT/'qa_judge_prompt.txt').write_text(judge_prompt)
 # Invoke the official evaluation functions and retain their raw completions and strict parser behavior.
 kind=['update_judge']
 def judge(prompt):
  raw=completion(kind[0],prompt);(OUT/(kind[0]+'_raw.txt')).write_text(raw+'\n')
  match=re.search(r'```json\s*(\{.*?\})\s*```',raw,re.DOTALL)
  if not match:raise ValueError('Official JSON code-block parser did not match; raw response saved')
  return json.loads(match.group(1).strip())
 eval_tools.llm_request_for_json=judge
 ur=eval_tools.evaluation_for_update_memory('\n'.join(memories),update['memory_content'],'\n'.join(update['original_memories']))
 kind[0]='qa_judge'
 qr=eval_tools.evaluation_for_question(qa['question'],qa['answer'],'\n'.join(i['memory_content'] for i in qa['evidence']),response)
 save('pilot_records.json',{'update':{'source':update,'memories_from_system':memories,'judge':ur},'qa':{'source':qa,'context':context,'system_response':response,'judge':qr}})
 save('status.json',{'status':'complete','api_attempts':len(calls),'errors':sum(c['status']!='ok' for c in calls),'update_label':ur.get('evaluation_result'),'qa_label':qr.get('evaluation_result')})
except Exception as e:
 save('status.json',{'status':'failed','api_attempts':len(calls),'errors':sum(c['status']!='ok' for c in calls),'error_type':type(e).__name__,'message':str(e) if isinstance(e,ValueError) else 'See api_calls.json; details suppressed.'})
 raise
