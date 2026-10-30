#!/usr/bin/env python3
"""Five fixed cases; offline preparation followed by one-shot isolated workers."""
import collections, copy, datetime, difflib, hashlib, importlib.metadata, json, logging, os, shutil, sqlite3, sys, threading, time, traceback
from pathlib import Path
from zoneinfo import ZoneInfo
ROOT=Path('/home/shu1004/ld/system/mem0_halumem_diagnosis')
OUT=Path(__file__).resolve().parent.parent
PLAN=ROOT/'results/medium_dev/scoring_review_and_five_case_plan_20261029_v1'
sys.path.insert(0,str(ROOT/'scripts'))
import local_smoke as base
import medium_dev_run as run
import medium_dev_data as data


def validate_prompt(combined, original, addendum):
    if combined != original+'\n\n'+addendum: raise ValueError('prompt differs from exact original plus addendum')

def copy_backup(src, dst):
    ready=data.read(src/'ready.json')
    for rel, digest in ready['files_sha256'].items():
        p=(src/rel).resolve()
        if not p.is_relative_to(src.resolve()) or data.digest(p)!=digest: raise ValueError('backup hash mismatch: '+rel)
    dst.mkdir(parents=True, exist_ok=False)
    shutil.copytree(src/'qdrant',dst/'qdrant'); shutil.copy2(src/'history.db',dst/'history.db')
    for rel,digest in ready['files_sha256'].items():
        if data.digest(dst/rel)!=digest: raise ValueError('copied backup hash mismatch: '+rel)
    return ready

def now(): return datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()
def write(path,obj): run.atomic(path,obj)
def sha(p): return data.digest(p)
def check(cond,msg):
    if not cond: raise ValueError(msg)

def prepare():
    from mem0.configs.prompts import DEFAULT_UPDATE_MEMORY_PROMPT
    from qdrant_client import QdrantClient
    import mem0
    profile=data.read(run.PROFILE); run.source_check(profile)
    check(importlib.metadata.version('mem0ai')=='0.1.118' and Path(mem0.__file__).resolve()==ROOT/'mem0_v0.1.118/mem0/__init__.py','wrong installed source/version')
    settings,missing=run.settings_check(ROOT/'.env.local',profile,True)
    manifest=data.read(PLAN/'five_case_manifest.json'); cases=manifest['cases']
    check([x['case'] for x in cases]==['A','B','C','target_7','target_10'],'incorrect case set')
    combined=(PLAN/'simple_protection_update_prompt.txt').read_text(); addendum=(PLAN/'simple_protection_addendum.txt').read_text()
    validate_prompt(combined,DEFAULT_UPDATE_MEMORY_PROMPT,addendum)
    check(hashlib.sha256(combined.encode()).hexdigest()==manifest['combined_prompt_sha256'],'prompt hash mismatch')
    (OUT/'original_update_prompt.txt').write_text(DEFAULT_UPDATE_MEMORY_PROMPT)
    (OUT/'control_update_prompt.txt').write_text(combined)
    (OUT/'prompt.diff').write_text(''.join(difflib.unified_diff(DEFAULT_UPDATE_MEMORY_PROMPT.splitlines(keepends=True),combined.splitlines(keepends=True),fromfile='original',tofile='control')))
    shutil.copy2(PLAN/'five_case_manifest.json',OUT/'five_case_manifest.json')
    shutil.copy2(run.PROFILE,OUT/'profile.json')
    write(OUT/'environment.json',{'python':sys.version,'executable':sys.executable,'mem0ai':importlib.metadata.version('mem0ai'),'mem0_path':mem0.__file__,'versions':{x:importlib.metadata.version(x) for x in ['openai','qdrant-client','numpy','pydantic']},'native_source_sha256':profile['native_source_sha256'],'harness_sha256':profile['reused_harness_sha256'],'control_prompt_sha256':manifest['combined_prompt_sha256'],'sdk_max_retries':0,'credentials_present':not missing})
    users={}
    with (ROOT/'HaluMem/data/HaluMem-Medium.jsonl').open() as f:
        for line in f:
            u=json.loads(line)
            if u['uuid'] in {c['user_uuid'] for c in cases}: users[u['uuid']]=u
    result=[]
    for c in cases:
        dst=OUT/'cases'/c['case']; folder=Path(c['folder']); src=Path(c['backup_path'])
        for key,path in [('before_sha256',c['before_path']),('input_sha256',c['input_path']),('backup_ready_sha256',src/'ready.json')]: check(sha(path)==c[key],c['case']+' '+key)
        ready=copy_backup(src,dst); inp=data.read(c['input_path']); before=data.read(c['before_path'])
        source=users[c['user_uuid']]['sessions'][c['original_session_index']]['dialogue']
        check(inp['original_session_index_zero_based']==c['original_session_index'] and inp['messages']==[{'role':x['role'],'content':x['content']} for x in source] and len(inp['messages'])==c['messages'],'input mismatch')
        previous=data.read(folder.parent/f"session_{c['chronological_ordinal']-1:03d}"/'history_all.json')
        check(base.history_rows(dst/'history.db')==previous and len(previous)==c['history_rows'],'history mismatch')
        with sqlite3.connect(f'file:{dst/"history.db"}?mode=ro',uri=True) as db: check(db.execute('pragma integrity_check').fetchone()[0]=='ok','history corrupt')
        client=QdrantClient(path=str(dst/'qdrant'))
        try:
            points,count,pages=base.collect_points(client,'medium_dev',None)
            comp=base.verify_persistence(before['database_points_with_vectors'],points)
        finally: client.close()
        check(count==c['before_count'],'point count mismatch')
        shutil.copy2(c['input_path'],dst/'input.json'); shutil.copy2(c['before_path'],dst/'baseline_before.json')
        baseline={name:sha(folder/name) for name in ['after.json','actual_operations.json','full_operation_plan.json','api_calls.jsonl','update_model_io.json']}
        write(dst/'preflight.json',{'status':'PASS','case':c['case'],'input_role_content_source_match':True,'copy_files_sha256':ready['files_sha256'],'history_matches_previous':True,'history_rows':len(previous),'vector_verification':comp,'baseline_artifact_sha256':baseline,'baseline_folder':str(folder),'prepared_at':now(),'model_calls':0})
        result.append({'case':c['case'],'status':'PASS','points':count,'messages':len(inp['messages'])})
    write(OUT/'preflight.json',{'status':'PASS','cases':result,'model_calls':0,'time':now()})
    print(json.dumps(result,ensure_ascii=False))

class Journal:
    def __init__(self,path): self.path=path; self.lock=threading.Lock(); self.n=0
    def emit(self,e):
        with self.lock:
            with self.path.open('a') as f:
                f.write(json.dumps(base.clean(e),ensure_ascii=False,default=str)+'\n'); f.flush(); os.fsync(f.fileno())
    def wrap(self,resource,kind,prompt):
        original=resource.create
        def create(*args,**kwargs):
            with self.lock: self.n+=1; num=self.n
            if kind=='llm' and len(kwargs.get('messages',[]))==1:
                check(kwargs['messages'][0]['content'].startswith(prompt+'\n\n'),'actual update prompt drift')
            t=time.perf_counter(); self.emit({'id':num,'kind':kind,'status':'started','time':now(),'request':kwargs})
            try:
                response=original(*args,**kwargs)
                self.emit({'id':num,'kind':kind,'status':'ok','time':now(),'elapsed_seconds':time.perf_counter()-t,'response':response.model_dump(mode='json')})
                return response
            except BaseException:
                self.emit({'id':num,'kind':kind,'status':'error_or_unknown_sent','time':now(),'elapsed_seconds':time.perf_counter()-t,'traceback':traceback.format_exc()})
                raise
        resource.create=create

def worker(label):
    check(label in ['A','B','C','target_7','target_10'],'invalid case')
    dst=OUT/'cases'/label; check(data.read(dst/'preflight.json')['status']=='PASS','preflight absent')
    check(not (dst/'started.json').exists(),'one-shot run already started; no replay')
    check(os.environ.get('MEM0_DIR')==str(dst/'mem0_dir'),'MEM0_DIR must be case-specific before import')
    from mem0 import Memory
    from observer_guard import GuardObserver, derive
    from guard import guarded_add
    profile=data.read(OUT/'profile.json'); settings,_=run.settings_check(ROOT/'.env.local',profile,True)
    os.environ.pop('OPENROUTER_API_KEY',None)
    case=next(c for c in data.read(OUT/'five_case_manifest.json')['cases'] if c['case']==label)
    prompt=(OUT/'control_update_prompt.txt').read_text(); config=run.config_for(profile,settings,dst); config['custom_update_memory_prompt']=prompt
    write(dst/'configuration.json',config)
    observer=GuardObserver(dst); observer.phase=label; log=base.AuditHandler(dst/'runtime.jsonl'); log.phase=label
    journal=Journal(dst/'api_calls.jsonl'); (dst/'runtime.jsonl').touch(); (dst/'api_calls.jsonl').touch()
    logger=logging.getLogger();logger.setLevel(logging.INFO);logger.addHandler(log)
    for n in ['httpx','httpcore','openai']:logging.getLogger(n).setLevel(logging.WARNING)
    memory=None; initial=None; before=None; returned=None; elapsed=None; failure=None; tick=time.perf_counter()
    try:
        memory=Memory.from_config(copy.deepcopy(config))
        check(not memory.enable_graph and memory.custom_fact_extraction_prompt is None and memory.custom_update_memory_prompt==prompt,'config drift')
        before=base.snapshot(memory,case['user_uuid']); base.verify_persistence(data.read(dst/'baseline_before.json')['database_points_with_vectors'],before['database_points_with_vectors']); write(dst/'before.json',before)
        initial=base.history_rows(dst/'history.db')
        memory.llm.client=memory.llm.client.with_options(timeout=profile['timeout_seconds'],max_retries=0)
        memory.embedding_model.client=memory.embedding_model.client.with_options(timeout=profile['timeout_seconds'],max_retries=0)
        journal.wrap(memory.llm.client.chat.completions,'llm',prompt); journal.wrap(memory.embedding_model.client.embeddings,'embedding',prompt)
        observer.install(memory)
        write(dst/'started.json',{'status':'inflight','time':now(),'infer':True,'no_replay':True})
        messages=data.read(dst/'input.json')['messages']; observer.emit('session_add_input',messages=messages,user_id=case['user_uuid'],infer=True)
        start=time.perf_counter()
        try: returned=guarded_add(memory,copy.deepcopy(messages),user_id=case['user_uuid'],infer=True,audit=lambda event: observer.emit('guard_audit',**event))
        finally: elapsed=time.perf_counter()-start
    except BaseException:
        failure=base.clean(traceback.format_exc())
    finally:
        try:
            if memory:
                after=base.snapshot(memory,case['user_uuid']); rows=base.history_rows(dst/'history.db')
                write(dst/'after.json',after); write(dst/'history_all.json',rows)
                if initial is not None: write(dst/'actual_operations.json',rows[len(initial):])
                if before is not None and initial is not None: write(dst/'reconcile.json',base.reconcile(before,after,rows[len(initial):],returned))
        except BaseException: failure=(failure or '')+'\nPOST_SNAPSHOT_ERROR\n'+base.clean(traceback.format_exc())
        try: derived=derive(dst,observer)
        except BaseException: failure=(failure or '')+'\nDERIVATION_ERROR\n'+base.clean(traceback.format_exc())
        try: run.close_memory(memory);memory=None
        except BaseException: failure=(failure or '')+'\nCLOSE_ERROR\n'+base.clean(traceback.format_exc())
        try:
            if (dst/'after.json').exists(): run.persisted_check(dst,dst,data.read(dst/'after.json'))
        except BaseException: failure=(failure or '')+'\nPERSISTENCE_ERROR\n'+base.clean(traceback.format_exc())
        logger.removeHandler(log)
        write(dst/'add_return.json',{'return_value':returned,'exception':failure,'elapsed_seconds':elapsed})
        bad=[e for e in observer.entries if e['kind'].endswith('exception') or e.get('status')=='error' or e.get('parse_error')]
        checks={}
        try:
            summary=data.read(dst/'guard_summary.json'); plan=data.read(dst/'final_plan.json');
            ledger=[json.loads(line) for line in (dst/'api_calls.jsonl').read_text().splitlines() if line.strip()]
            begins={e['id']:e for e in ledger if e['status']=='started'};ends={e['id']:e for e in ledger if e['status']!='started'}
            ops=data.read(dst/'actual_operations.json')
            attempts=[e['event'] for e in observer.entries if e['kind']=='operation_attempt']
            intended=[p['event'] for p in (plan or []) if p.get('event') in ('ADD','UPDATE','DELETE')]
            runtime=[json.loads(line) for line in (dst/'runtime.jsonl').read_text().splitlines() if line.strip()]
            none_count=sum(e['message']=='NOOP for Memory.' for e in runtime)
            checks={'final_plan_accepted':summary['final_plan_accepted'],'sdk_started_all_completed':begins.keys()==ends.keys(),
                    'sdk_responses_ok':all(e['status']=='ok' for e in ends.values()),
                    'llm_untruncated':all(e['response']['choices'][0]['finish_reason']=='stop' for e in ends.values() if e['kind']=='llm' and e['status']=='ok'),
                    'planned_mutation_sequence_equals_attempts':intended==attempts,
                    'all_attempts_recorded_in_history':len(attempts)==len(ops),
                    'none_matches_dispatch':none_count==sum(p.get('event')=='NONE' for p in (plan or [])),
                    'persistence_checked':(dst/'persistence.json').exists() and data.read(dst/'persistence.json')['history_integrity']=='ok',
                    'history_reconciled':(dst/'reconcile.json').exists() and data.read(dst/'reconcile.json')['history_replayed_matches_database']}
        except BaseException: failure=(failure or '')+'\nVERIFICATION_ERROR\n'+base.clean(traceback.format_exc())
        status='completed_with_errors' if failure or log.errors or bad or not checks or not all(checks.values()) else 'completed'
        write(dst/'status.json',{'status':status,'error':failure,'native_error_count':len(log.errors),'observer_error_count':len(bad),'checks':checks,'add_elapsed_seconds':elapsed,'wall_elapsed_seconds':time.perf_counter()-tick,'finished_at':now()})
        print(label+': '+status,flush=True)
    return 1 if failure else 0

if __name__=='__main__':
    if sys.argv[1:] == ['prepare']: prepare()
    elif len(sys.argv)==3 and sys.argv[1]=='worker': sys.exit(worker(sys.argv[2]))
    else: raise SystemExit('usage: runner.py prepare | worker CASE')
