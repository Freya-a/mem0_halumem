#!/usr/bin/env python3
import os,sys,json,hashlib,time,sqlite3,fcntl,re,types,threading,argparse,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from openai import OpenAI
from qdrant_client import QdrantClient, models
import engine

ROOT=engine.ROOT; OUT=Path(__file__).resolve().parent
PILOT=ROOT/'results/medium_dev/official_eval_pilot_20261029'
RUN=ROOT/'results/medium_dev/williams_native_prefix5_20261028_v3'
DATA=ROOT/'HaluMem/data/HaluMem-Medium.jsonl';DB=OUT/'checkpoints.sqlite3'
LOCK=threading.Lock(); CACHE={}
sys.modules['llms']=types.SimpleNamespace(llm_request_for_json=lambda x:None)
sys.path.insert(0,str(ROOT/'HaluMem/eval'))
import eval_tools

def hashfile(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def enc(o):return json.dumps(o,ensure_ascii=False,separators=(',',':'))
def db():
 c=sqlite3.connect(DB,timeout=60);c.execute('PRAGMA busy_timeout=60000');return c

def init_db():
 with db() as c:
  c.execute('PRAGMA journal_mode=WAL')
  c.executescript('''CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY,kind TEXT NOT NULL,source TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS stages(id TEXT NOT NULL,stage TEXT NOT NULL,status TEXT NOT NULL,payload TEXT,PRIMARY KEY(id,stage));
  CREATE TABLE IF NOT EXISTS calls(id INTEGER PRIMARY KEY AUTOINCREMENT,item TEXT NOT NULL,stage TEXT NOT NULL,origin TEXT NOT NULL,status TEXT NOT NULL,request TEXT,response TEXT,usage TEXT,model TEXT,request_id TEXT,started TEXT,elapsed REAL,error_type TEXT,error_code TEXT);''')

def getstage(item,stage):
 with db() as c:r=c.execute('SELECT status,payload FROM stages WHERE id=? AND stage=?',(item,stage)).fetchone()
 return (r[0],json.loads(r[1]) if r[1] is not None else None) if r else (None,None)

def putstage(item,stage,status,payload):
 with db() as c:c.execute('INSERT OR REPLACE INTO stages VALUES (?,?,?,?)',(item,stage,status,enc(payload) if payload is not None else None))

def identifier(kind,row):return f"{kind}_{row['uuid']}_s{row['session_index_zero_based']:03d}_"+(f"m{row['memory_point_index_zero_based']:03d}" if kind=='update' else f"q{row['question_index_zero_based']:03d}")

def fingerprint():
 paths=[DATA,PILOT/'update_candidates.jsonl',PILOT/'qa_candidates.jsonl',PILOT/'snapshot_audit.json',PILOT/'pilot_records.json',PILOT/'metadata.json',PILOT/'api_calls.json',PILOT/'update_retrieval.json',PILOT/'qa_retrieval.json',PILOT/'update_judge_raw.txt',PILOT/'qa_judge_raw.txt',PILOT/'qa_answer_prompt.txt',PILOT/'update_judge_prompt.txt',PILOT/'qa_judge_prompt.txt',ROOT/'HaluMem/eval/eval_tools.py',ROOT/'HaluMem/eval/prompts.py',OUT/'engine.py',OUT/'run_eval.py']
 return {str(x.relative_to(ROOT)):hashfile(x) for x in paths}

def prepare():
 fp=fingerprint(); sources={d['uuid']:d for line in DATA.open() if (d:=json.loads(line))['uuid'] in {'1b846c59-456e-9550-dffd-4d23f1eca81f','2f1f897e-d67f-dbc5-6a7b-b7634a9e294f','348492a7-cfe4-ee1d-73c3-c276d6ba8277'}}
 assert fp[str(DATA.relative_to(ROOT))]=='486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7'
 items=[];seen=set(); hashcache={}
 for kind,name,expected in [('update','update_candidates.jsonl',56),('qa','qa_candidates.jsonl',75)]:
  rows=[json.loads(l) for l in (PILOT/name).open()];assert len(rows)==expected
  for r in rows:
   uid=r['uuid'];index=r['session_index_zero_based'];ordinal=r['session_ordinal_one_based'];s=sources[uid]['sessions'][index]
   cp=json.loads((RUN/'users'/uid/'checkpoint.json').read_text());p=RUN/'users'/uid/f'session_{ordinal:03d}'/'after.json'
   assert Path(r['snapshot_path'])==p and p.exists()
   if str(p) not in hashcache:hashcache[str(p)]=hashfile(p)
   assert hashcache[str(p)]==r['snapshot_sha256']==cp['commits'][ordinal-1]['artifacts_sha256']['after.json']
   inp=json.loads((p.parent/'input.json').read_text()); assert inp['original_session_index_zero_based']==index and inp['raw_dialogue']==s['dialogue']
   if kind=='update': assert s['memory_points'][r['memory_point_index_zero_based']]==r['memory_point'] and r['memory_point']['is_update']=='True' and r['memory_point']['original_memories']
   else:assert s['questions'][r['question_index_zero_based']]==r['question']
   ident=identifier(kind,r);assert ident not in seen;seen.add(ident);items.append((ident,kind,enc(r)))
 with db() as c:
  old=c.execute("SELECT value FROM metadata WHERE key='fingerprint'").fetchone()
  if old:assert json.loads(old[0])==fp,'Frozen input or evaluation code changed; do not resume'
  else:c.execute("INSERT INTO metadata VALUES('fingerprint',?)",(enc(fp),))
  for ident,kind,src in items:
   oldrow=c.execute('SELECT kind,source FROM items WHERE id=?',(ident,)).fetchone()
   if oldrow:assert oldrow==(kind,src)
   else:c.execute('INSERT INTO items VALUES(?,?,?)',(ident,kind,src))
 assert len(items)==131
 return items

def import_pilot(items):
 uid='1b846c59-456e-9550-dffd-4d23f1eca81f';records=json.loads((PILOT/'pilot_records.json').read_text());calls=json.loads((PILOT/'api_calls.json').read_text())
 update_id=engine.find_pilot_update(items,records['update']['source']);update=next(x for x in items if x[0]==update_id)
 assert json.loads(update[2])['uuid']==uid and json.loads(update[2])['session_index_zero_based']==3
 qa=next(x for x in items if x[1]=='qa' and json.loads(x[2])['uuid']==uid and json.loads(x[2])['session_index_zero_based']==3 and json.loads(x[2])['question_index_zero_based']==0)
 assert json.loads(update[2])['memory_point']==records['update']['source'] and json.loads(qa[2])['question']==records['qa']['source']
 entries=[(update[0],'embedding',calls[0]),(qa[0],'embedding',calls[1]),(qa[0],'answer',calls[2]),(update[0],'judge',calls[3]),(qa[0],'judge',calls[4])]
 with db() as c:
  if c.execute("SELECT value FROM metadata WHERE key='pilot_imported'").fetchone():return
  for ident,stage,call in entries:
   assert call['status']=='ok'
   if stage=='embedding':payload={'reused_pilot':True}
   elif stage=='answer':payload={'text':records['qa']['system_response']}
   else:
    which='update' if ident==update[0] else 'qa'; payload={'raw':(PILOT/(which+'_judge_raw.txt')).read_text(),'score':records[which]['judge']}
   c.execute('INSERT INTO stages VALUES (?,?,?,?)',(ident,stage,'ok',enc(payload)))
   promptfile={'answer':'qa_answer_prompt.txt','judge':('update_judge_prompt.txt' if ident==update[0] else 'qa_judge_prompt.txt')}.get(stage)
   req={'prompt':(PILOT/promptfile).read_text()} if promptfile else {'reused_query':True}
   c.execute('INSERT INTO calls(item,stage,origin,status,request,response,usage,model,request_id,started,elapsed) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(ident,stage,'pilot','ok',enc(req),enc(payload),enc(call.get('usage')),call.get('response_model'),call.get('request_id'),call.get('started'),call.get('elapsed_seconds')))
  for ident,kind in [(update[0],'update'),(qa[0],'qa')]:
   hits=json.loads((PILOT/(kind+'_retrieval.json')).read_text());c.execute('INSERT INTO stages VALUES (?,?,?,?)',(ident,'retrieval','ok',enc({'hits':hits,'reused_pilot':True})))
  c.execute("INSERT INTO metadata VALUES('pilot_imported','true')")

def invoke(item,stage,request,fn,decode):
 status,payload=getstage(item,stage)
 if status is not None:return status,payload
 with db() as c:
  c.execute('INSERT INTO stages VALUES (?,?,?,NULL)',(item,stage,'started'))
  cur=c.execute('INSERT INTO calls(item,stage,origin,status,request,started) VALUES(?,?,?,?,?,?)',(item,stage,'development','started',enc(request),now()));call_id=cur.lastrowid
 t=time.monotonic()
 try:
  result=fn();elapsed=time.monotonic()-t; usage=result.usage.model_dump() if getattr(result,'usage',None) else None
  payload=decode(result); model=getattr(result,'model',None);rid=getattr(result,'_request_id',None)
  with db() as c:
   c.execute("UPDATE calls SET status='ok',response=?,usage=?,model=?,request_id=?,elapsed=? WHERE id=?",(enc(payload),enc(usage),model,rid,elapsed,call_id))
   c.execute("UPDATE stages SET status='ok',payload=? WHERE id=? AND stage=?",(enc(payload),item,stage))
  return 'ok',payload
 except Exception as e:
  elapsed=time.monotonic()-t; err={'type':type(e).__name__,'status_code':getattr(e,'status_code',None),'message':'Request failed; sensitive exception text withheld.'}
  with db() as c:
   c.execute("UPDATE calls SET status='error',elapsed=?,error_type=?,error_code=? WHERE id=?",(elapsed,err['type'],str(err['status_code']),call_id))
   c.execute("UPDATE stages SET status='error',payload=? WHERE id=? AND stage=?",(enc(err),item,stage))
  return 'error',err

def snapshot(row):
 path=row['snapshot_path']
 with LOCK:
  if path in CACHE:return CACHE[path]
  assert hashfile(path)==row['snapshot_sha256']
  snap=json.loads(Path(path).read_text());points=snap['database_points_with_vectors'];uid=row['uuid']
  assert snap['not_truncated'] and len(points)==snap['database_count_exact'] and all(p['payload'].get('user_id')==uid and len(p['vector'])==1024 for p in points)
  q=QdrantClient(':memory:');q.create_collection('snapshot',vectors_config=models.VectorParams(size=1024,distance=models.Distance.COSINE));q.upsert('snapshot',[models.PointStruct(id=p['id'],vector=p['vector'],payload=p['payload']) for p in points]);assert q.count('snapshot',exact=True).count==len(points)
  CACHE[path]=(q,threading.Lock());return CACHE[path]

def retrieve(row,vector,limit):
 q,lock=snapshot(row)
 with lock:hits=q.query_points('snapshot',query=vector,query_filter=models.Filter(must=[models.FieldCondition(key='user_id',match=models.MatchValue(value=row['uuid']))]),limit=limit).points
 return [{'id':str(h.id),'memory':h.payload['data'],'timestamp':h.payload.get('created_at'),'score':h.score} for h in hits]

def process(item,kind,src,llm,embed,env):
 row=json.loads(src);subject=row['memory_point'] if kind=='update' else row['question'];query=subject['memory_content'] if kind=='update' else subject['question']
 stat,retrieved=getstage(item,'retrieval')
 if stat!='ok':
  stat,e=invoke(item,'embedding',{'input':query.replace('\n',' '),'model':env['EMBEDDING_MODEL'],'dimensions':1024},lambda:embed.embeddings.create(model=env['EMBEDDING_MODEL'],input=[query.replace('\n',' ')],dimensions=1024),lambda r:{'vector':r.data[0].embedding})
  if stat!='ok':return
  if getstage(item,'retrieval')[0] is not None:return
  try:
   h=retrieve(row,e['vector'],10 if kind=='update' else 20);retrieved={'hits':h};putstage(item,'retrieval','ok',retrieved)
  except Exception as ex:putstage(item,'retrieval','error',{'type':type(ex).__name__,'message':'Snapshot reconstruction or search failed'});return
 hits=retrieved['hits'];memories=[f"{h['timestamp']}: {h['memory']}" for h in hits]
 if kind=='update':
  if not hits:return
  prompt=eval_tools.EVALUATION_PROMPT_FOR_UPDATE_MEMORY.format(memories='\n'.join(memories),updated_memory=subject['memory_content'],original_memory='\n'.join(subject['original_memories']))
 else:
  context='Memories for user '+row['uuid']+':\n\n    '+json.dumps(memories,indent=4)+'\n'
  prompt=engine.answer_prompt(context,subject)
  stat,answer=invoke(item,'answer',{'prompt':prompt,'model':env['LLM_MODEL'],'temperature':0,'max_tokens':16384},lambda:llm.chat.completions.create(model=env['LLM_MODEL'],messages=[{'role':'user','content':prompt}],temperature=0,max_tokens=16384),lambda r:{'text':r.choices[0].message.content or ''})
  if stat!='ok':return
  prompt=eval_tools.EVALUATION_PROMPT_FOR_QUESTION.format(question=subject['question'],reference_answer=subject['answer'],key_memory_points='\n'.join(e['memory_content'] for e in subject['evidence']),response=answer['text'])
 stat,result=invoke(item,'judge',{'prompt':prompt,'model':env['LLM_MODEL'],'temperature':0,'max_tokens':16384},lambda:llm.chat.completions.create(model=env['LLM_MODEL'],messages=[{'role':'user','content':prompt}],temperature=0,max_tokens=16384),lambda r:{'raw':r.choices[0].message.content or ''})
 if stat=='ok' and 'score' not in result:
  try:result['score']=engine.parse_score(result['raw']);putstage(item,'judge','ok',result)
  except (ValueError,json.JSONDecodeError) as ex:putstage(item,'judge','parse_error',{'raw':result['raw'],'type':type(ex).__name__})

def environment():
 env={}
 for line in (ROOT/'.env.local').read_text().splitlines():
  if line.strip() and not line.lstrip().startswith('#') and '=' in line:
   k,v=line.split('=',1);env[k.strip()]=v.strip().strip('"\'')
 for k in ['LLM_BASE_URL','LLM_API_KEY','LLM_MODEL','EMBEDDING_BASE_URL','EMBEDDING_API_KEY','EMBEDDING_MODEL','EMBEDDING_DIMS']:
  if os.getenv(k):env[k]=os.environ[k]
 assert env['LLM_MODEL']=='qwen-plus' and env['EMBEDDING_MODEL']=='text-embedding-v4' and env['EMBEDDING_DIMS']=='1024'
 assert env['LLM_BASE_URL']=='https://dashscope.aliyuncs.com/compatible-mode/v1' and env['EMBEDDING_BASE_URL']==env['LLM_BASE_URL']
 os.environ['NO_PROXY']='dashscope.aliyuncs.com';os.environ['no_proxy']='dashscope.aliyuncs.com'
 return env

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=8);parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args();assert 1<=args.workers<=8
 with (OUT/'run.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);init_db();items=prepare();import_pilot(items)
  print('Input verified; candidates:',len(items),'pilot records reused: 2',flush=True)
  if args.prepare_only:return
  env=environment();llm=OpenAI(api_key=env['LLM_API_KEY'],base_url=env['LLM_BASE_URL'],timeout=180,max_retries=0);embed=OpenAI(api_key=env['EMBEDDING_API_KEY'],base_url=env['EMBEDDING_BASE_URL'],timeout=180,max_retries=0)
  with ThreadPoolExecutor(max_workers=args.workers) as pool:
   futures={pool.submit(process,i,k,s,llm,embed,env):i for i,k,s in items}
   for n,f in enumerate(as_completed(futures),1):
    try:f.result()
    except Exception as e:print('worker_error',futures[f],type(e).__name__,flush=True)
    if n%10==0 or n==len(items):print('processed',n,'/',len(items),flush=True)
 print('Evaluation worker pass finished; inspect stage states and report.',flush=True)
if __name__=='__main__':main()
