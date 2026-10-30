#!/usr/bin/env python3
"""Linux/Mac portable entry: default offline dry-run; --execute is explicit."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime
import fcntl
import hashlib
import importlib.metadata as md
import json
import logging
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from zoneinfo import ZoneInfo

import medium_dev_data as data
import local_smoke as base
import medium_dev_review as review

ROOT=data.ROOT
PROFILE=ROOT/'config/medium_dev.profile.json'


def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).isoformat()


def atomic(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('w') as f:
        json.dump(base.clean(value),f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)


def no_network():
    def denied(*a,**k):
        raise RuntimeError('Network forbidden in offline preparation/dry-run')
    socket.socket.connect=denied
    socket.socket.connect_ex=denied
    socket.create_connection=denied
    socket.getaddrinfo=denied
    socket.gethostbyname=denied


def safe_run_path(args):
    data.require(bool(args.run_id and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}',args.run_id)), 'Supply a safe --run-id')
    out=Path(args.output_root).expanduser().resolve()/args.run_id
    for legacy in ['results/local_smoke','results/local_update_case']:
        data.require(not out.is_relative_to(ROOT/legacy), 'Existing experiment directories are protected')
    return out


def source_check(profile):
    for rel, expected in profile['native_source_sha256'].items():
        data.require(data.digest(ROOT/'mem0_v0.1.118'/rel)==expected, f'Native source changed: {rel}')
    for rel, expected in profile['reused_harness_sha256'].items():
        data.require(data.digest(ROOT/rel)==expected, f'Reused harness changed: {rel}')


def environment_check(profile):
    data.require(sys.version_info[:2]==(3,11), 'Use Python 3.11')
    data.require(os.environ.get('CONDA_DEFAULT_ENV')=='mem0_halumem','Use conda run -n mem0_halumem python')
    # Import package to confirm actual load, but NEVER instantiate Memory in preflight/dry-run.
    # MEM0 setup writes a small identity config; keep that in a disposable tempdir.
    with tempfile.TemporaryDirectory(prefix='medium-import-') as tmp:
        previous=os.environ.get('MEM0_DIR'); os.environ['MEM0_DIR']=tmp;os.environ['MEM0_TELEMETRY']='False'
        try:
            import mem0
            loaded=Path(mem0.__file__).resolve()
            data.require(md.version('mem0ai')==profile['mem0ai_version']==mem0.__version__, 'Wrong installed Mem0 version')
            data.require(loaded==ROOT/'mem0_v0.1.118/mem0/__init__.py','Mem0 is not the local pinned source')
            direct=json.loads(md.distribution('mem0ai').read_text('direct_url.json') or '{}')
            data.require(direct.get('dir_info',{}).get('editable') is True,'Install local Mem0 with pip -e')
            env=dict(python=sys.version, executable=sys.executable, conda_environment=os.environ['CONDA_DEFAULT_ENV'],
                     mem0ai=md.version('mem0ai'), mem0_loaded_file=str(loaded), editable_install=direct,
                     dependency_versions={k:md.version(k) for k in ['openai','qdrant-client','numpy','pydantic']})
        finally:
            if previous is None:os.environ.pop('MEM0_DIR',None)
            else:os.environ['MEM0_DIR']=previous
    return env


def settings_check(env_file,profile,need_keys):
    # Explicit file only; avoid the old harness's implicit HaluMem and .env.local discovery.
    values=base.read_env(Path(env_file).expanduser().resolve()) if env_file else {}
    values.update({k:v for k,v in os.environ.items() if k in {
        'LLM_BASE_URL','LLM_API_KEY','LLM_MODEL','EMBEDDING_BASE_URL','EMBEDDING_API_KEY','EMBEDDING_MODEL','EMBEDDING_DIMS',
        'OPENAI_MAX_TOKENS','OPENAI_TEMPERATURE','OPENAI_TIMEOUT'}})
    required=dict(LLM_BASE_URL=profile['llm']['openai_base_url'],LLM_MODEL=profile['llm']['model'],
                  EMBEDDING_BASE_URL=profile['embedder']['openai_base_url'],EMBEDDING_MODEL=profile['embedder']['model'],
                  EMBEDDING_DIMS=str(profile['embedder']['embedding_dims']),OPENAI_MAX_TOKENS=str(profile['llm']['max_tokens']),
                  OPENAI_TEMPERATURE=str(profile['llm']['temperature']),OPENAI_TIMEOUT=str(profile['timeout_seconds']))
    for k, expected in required.items():
        actual=values.get(k,expected)
        data.require(actual==expected,f'Configuration differs from validated profile: {k}')
        values[k]=expected
    missing=[]
    for k in ['LLM_API_KEY','EMBEDDING_API_KEY']:
        if not base.usable(values.get(k)):missing.append(k)
        else:base.SECRETS.append(values[k])
    data.require(not need_keys or not missing,'Missing required credentials: '+','.join(missing))
    return values,missing


def prepared(args):
    profile=data.read(PROFILE);source_check(profile)
    manifest,users=data.validate_manifest(dataset=Path(args.dataset).resolve())
    settings,missing=settings_check(args.env_file,profile,args.execute or args.worker)
    return profile,manifest,users,settings,missing


def prefix_sessions(manifest,users,uid):
    p=next(p for p in manifest['prefixes'] if p['user_uuid']==uid)
    user=users[uid][1]
    return [data.session_input(user,i,n) for n,(i,_) in enumerate(data.ordered(user)[:p['full_sessions_required']],1)]


def pending_session(user_out,completed):
    folders=sorted(user_out.glob('session_[0-9][0-9][0-9]'))
    pending=[f for f in folders if int(f.name.split('_')[1])>completed]
    data.require(len(pending)<=1,'Multiple uncommitted session directories; manual investigation required')
    return pending[0] if pending else None


def checkpoint(user_out):
    p=user_out/'checkpoint.json'
    return data.read(p) if p.exists() else dict(completed_ordinal=0,commits=[])


def verify_commits(user_out,cp):
    data.require([r['ordinal'] for r in cp['commits']]==list(range(1,cp['completed_ordinal']+1)), 'Checkpoint has a gap')
    for record in cp['commits']:
        folder=user_out/f'session_{record["ordinal"]:03d}'
        for name,sha in record['artifacts_sha256'].items():
            data.require(data.digest(folder/name)==sha,f'Committed artifact changed: {folder/name}')


def config_for(profile,settings,out):
    llm=deepcopy(profile['llm']);llm['api_key']=settings['LLM_API_KEY']
    emb=deepcopy(profile['embedder']);emb['api_key']=settings['EMBEDDING_API_KEY']
    return dict(version='v1.1',llm=dict(provider='openai',config=llm),embedder=dict(provider='openai',config=emb),
                vector_store=dict(provider='qdrant',config=dict(collection_name='medium_dev',path=str(out/'qdrant'),
                    on_disk=True,embedding_model_dims=emb['embedding_dims'])),history_db_path=str(out/'history.db'))


def close_memory(memory):
    if memory:
        memory.vector_store.client.close()
        memory._telemetry_vector_store.client.close()
        memory.db.connection.close()
        memory.llm.client.close()
        memory.embedding_model.client.close()


def persisted_check(folder,user_out,after):
    from qdrant_client import QdrantClient
    client=QdrantClient(path=str(user_out/'qdrant'))
    try:
        points,count,pages=base.collect_points(client,'medium_dev',None)
        result=base.verify_persistence(after['database_points_with_vectors'],points)
    finally:client.close()
    import sqlite3
    with sqlite3.connect(f'file:{user_out/"history.db"}?mode=ro',uri=True) as db:
        data.require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','History integrity failed')
    atomic(folder/'persistence.json',dict(count=count,pages=pages,comparison=result,history_integrity='ok'))


def verify_current_state(user_out,cp):
    if cp['completed_ordinal']==0:return
    data.require((user_out/'qdrant').is_dir() and (user_out/'history.db').is_file(),
                 'Committed database files are missing; refuse recreation or replay')
    last=user_out/f'session_{cp["completed_ordinal"]:03d}'
    after=data.read(last/'after.json')
    persisted_check(user_out,user_out,after)
    data.require(base.history_rows(user_out/'history.db')==data.read(last/'history_all.json'),
                 'Current history differs from last committed history')


def run_session(profile,settings,config,user_out,s,targets,cp):
    # Import only in the execute worker, after MEM0_DIR is fixed for this user/process.
    from mem0 import Memory
    from local_update_case import Observer,derived_session
    ordinal=s['chronological_session_ordinal_one_based'];folder=user_out/f'session_{ordinal:03d}'
    folder.mkdir(exist_ok=False)
    observer=Observer(folder);api=base.APIAudit(folder/'api_calls.jsonl');log=base.AuditHandler(folder/'runtime.jsonl')
    observer.phase=api.phase=log.phase=folder.name
    (folder/'runtime.jsonl').touch();(folder/'api_calls.jsonl').touch()
    logging.getLogger().setLevel(logging.INFO);logging.getLogger().addHandler(log)
    for name in ['httpx','httpcore','openai']:logging.getLogger(name).setLevel(logging.WARNING)
    memory=None;tick=time.perf_counter();returned=None;failure=None;initial_rows=None;add_elapsed=None
    atomic(folder/'input.json',s)
    atomic(folder/'target_links.json',dict(target_ids=[t['target_id'] for t in targets],session_group_id=(targets[0]['session_group_id'] if targets else None)))
    try:
        memory=Memory.from_config(deepcopy(config))
        data.require(not memory.enable_graph and memory.custom_fact_extraction_prompt is None and memory.custom_update_memory_prompt is None,'Native prompt/graph drift')
        before=base.snapshot(memory,s['user_uuid'])
        if ordinal==1:data.require(before['database_count_exact']==0 and not base.history_rows(user_out/'history.db'),'New user database is not empty')
        else:
            prev=user_out/f'session_{ordinal-1:03d}'
            base.verify_persistence(data.read(prev/'after.json')['database_points_with_vectors'],before['database_points_with_vectors'])
            data.require(base.history_rows(user_out/'history.db')==data.read(prev/'history_all.json'),'History drift since last checkpoint')
        atomic(folder/'before.json',before)
        initial_rows=base.history_rows(user_out/'history.db')
        close_memory(memory);memory=None
        backup=folder/'rollback_before';backup.mkdir()
        shutil.copytree(user_out/'qdrant',backup/'qdrant')
        shutil.copy2(user_out/'history.db',backup/'history.db')
        atomic(backup/'ready.json',dict(ordinal=ordinal,prior_checkpoint=cp,files_sha256={str(p.relative_to(backup)):data.digest(p) for p in backup.rglob('*') if p.is_file()}))
        # From this durable marker until checkpoint commit, normal resume must refuse replay.
        atomic(folder/'started.json',dict(time=now(),status='inflight',infer=True))
        memory=Memory.from_config(deepcopy(config))
        memory.llm.client=memory.llm.client.with_options(timeout=profile['timeout_seconds'],max_retries=0)
        memory.embedding_model.client=memory.embedding_model.client.with_options(timeout=profile['timeout_seconds'],max_retries=0)
        api.wrap(memory.llm.client.chat.completions,'llm');api.wrap(memory.embedding_model.client.embeddings,'embedding')
        observer.install(memory)
        observer.emit('session_add_input',messages=s['messages'],raw_dialogue=s['raw_dialogue'],user_id=s['user_uuid'],infer=True)
        add_tick=time.perf_counter()
        try:returned=memory.add(deepcopy(s['messages']),user_id=s['user_uuid'],infer=True)
        finally:add_elapsed=time.perf_counter()-add_tick
        after=base.snapshot(memory,s['user_uuid']);atomic(folder/'after.json',after)
        rows=base.history_rows(user_out/'history.db');ops=rows[len(initial_rows):]
        atomic(folder/'actual_operations.json',ops);atomic(folder/'history_all.json',rows)
        atomic(folder/'add_return.json',dict(return_value=returned,exception=None,add_elapsed_seconds=add_elapsed))
        plans=derived_session(folder,folder,observer,log)
        base.reconcile(before,after,ops,returned)
        for e in observer.entries:
            if e['kind']=='model_output':
                parsed=e.get('parsed')
                data.require(isinstance(parsed,dict),'Model JSON must be an object')
                if e['stage']=='extraction':
                    data.require(isinstance(parsed.get('facts'),list) and all(isinstance(x,str) for x in parsed['facts']),'Invalid extraction facts shape')
                else:
                    data.require(isinstance(parsed.get('memory'),list) and all(isinstance(x,dict) and x.get('event') in ('ADD','UPDATE','DELETE','NONE') for x in parsed['memory']),'Invalid update plan shape')
        bad=[e for e in observer.entries if e['kind'].endswith('exception') or e.get('status')=='error' or e.get('parse_error')]
        sdk_bad=[c for c in api.calls if c['status']!='ok' or (c['kind']=='llm' and c['response']['choices'][0]['finish_reason']!='stop')]
        data.require(not bad and not sdk_bad and not log.errors,'Native/model/transport error; session remains uncommitted')
        data.require(plans['planned_NONE_matches_native_dispatch'],'NONE plan dispatch mismatch')
        full_plan=data.read(folder/'full_operation_plan.json')
        intended=[p['event'] for p in full_plan if p.get('text') and p['event']!='NONE']
        attempted=[e['event'] for e in observer.entries if e['kind']=='operation_attempt']
        data.require(intended==attempted,'Planned mutation sequence does not match native operation attempts')
        usage=api.summary();usage['note']='Provider-reported usage only; unavailable fields remain absent. SDK max_retries=0.'
        atomic(folder/'verification.json',dict(status='completed',elapsed_seconds=time.perf_counter()-tick,
            add_elapsed_seconds=add_elapsed,native_error_count=0,token_usage=usage,planned_mutations_match_attempts=True,**plans))
        close_memory(memory);memory=None
        persisted_check(folder,user_out,after)
        atomic(folder/'target_operation_correspondence.json',review.review_rows(targets,user_out,completed_override=ordinal))
        artifacts={p.name:data.digest(p) for p in folder.iterdir() if p.is_file()}
        new_cp=dict(completed_ordinal=ordinal,commits=cp['commits']+[dict(ordinal=ordinal,artifacts_sha256=artifacts)],committed_at=now())
        atomic(user_out/'checkpoint.json',new_cp)
        return new_cp
    except BaseException:
        failure=base.clean(traceback.format_exc())
        atomic(folder/'error.json',dict(status='failed_or_partial_uncommitted',traceback=failure,elapsed_seconds=time.perf_counter()-tick,
            handling='Ordinary resume refused. Inspect partial writes; explicitly rollback this session to saved before-state or use a new run_id.'))
        if memory:
            for name,fn in [('after_partial.json',lambda:base.snapshot(memory,s['user_uuid'])),
                            ('history_partial.json',lambda:base.history_rows(user_out/'history.db'))]:
                try:atomic(folder/name,fn())
                except Exception:pass
        if initial_rows is not None:
            try:
                partial_rows=base.history_rows(user_out/'history.db')
                atomic(folder/'actual_operations_partial.json',partial_rows[len(initial_rows):])
            except Exception:pass
        if not (folder/'add_return.json').exists():atomic(folder/'add_return.json',dict(return_value=returned,exception=failure,add_elapsed_seconds=add_elapsed))
        try:derived_session(folder,folder,observer,log)
        except Exception:pass
        raise
    finally:
        try:close_memory(memory)
        finally:logging.getLogger().removeHandler(log)


def rollback(user_out):
    cp=checkpoint(user_out);verify_commits(user_out,cp)
    folder=pending_session(user_out,cp['completed_ordinal'])
    data.require(folder is not None,'No incomplete session to roll back')
    backup=folder/'rollback_before'
    data.require((backup/'ready.json').is_file(),'No complete before-state backup; preserve run and use a NEW run_id')
    ready=data.read(backup/'ready.json')
    data.require(ready['prior_checkpoint']==cp,'Backup/checkpoint mismatch')
    for rel,sha in ready['files_sha256'].items():
        data.require(data.digest(backup/rel)==sha,'Rollback before-state backup is corrupt')
    archive=user_out/'recovery'/f'{folder.name}_{uuid.uuid4().hex[:8]}'
    archive.mkdir(parents=True,exist_ok=False)
    # Persist recovery intent first. Crashes during recovery require investigation, never automatic retries.
    marker=user_out/'RECOVERY_IN_PROGRESS.json'
    data.require(not marker.exists(),'An earlier recovery was interrupted; inspect manually')
    atomic(marker,dict(archive=str(archive),session=folder.name,time=now()))
    shutil.move(str(folder),str(archive/folder.name))
    for name in ['qdrant','history.db','history.db-wal','history.db-shm','history.db-journal']:
        if (user_out/name).exists():shutil.move(str(user_out/name),str(archive/name))
    saved=archive/folder.name/'rollback_before'
    shutil.copytree(saved/'qdrant',user_out/'qdrant');shutil.copy2(saved/'history.db',user_out/'history.db')
    atomic(archive/'rollback_record.json',dict(time=now(),restored_before_session=folder.name,checkpoint=cp,
        note='Partial writes archived. Prior billed calls cannot be undone. Explicit resume may now re-input only this rolled-back session.'))
    marker.unlink()


def worker(args,profile,manifest,users,settings):
    run=safe_run_path(args);uid=args.user;data.require(uid in manifest['selected_users'],'Unknown user')
    data.require((run/'run_record.json').is_file(),'Worker requires a parent-created run record')
    data.require(data.read(run/'run_record.json')==run_fingerprint(manifest),'Run fingerprint changed; use NEW run_id')
    out=run/'users'/uid;out.mkdir(parents=True,exist_ok=True)
    with (out/'.worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.rollback_incomplete:
            rollback(out);return 0
        data.require(not (out/'RECOVERY_IN_PROGRESS.json').exists(),'Interrupted recovery; manual investigation required')
        cp=checkpoint(out);verify_commits(out,cp)
        data.require(pending_session(out,cp['completed_ordinal']) is None,'Uncommitted session exists: inspect and explicitly --rollback-incomplete, or use new run_id. NO blind retry.')
        # A fresh interpreter per user avoids shared mem0_dir/migration store state.
        os.environ['MEM0_DIR']=str(out/'mem0_runtime');os.environ['MEM0_TELEMETRY']='False'
        os.environ.pop('OPENROUTER_API_KEY',None)
        import mem0
        data.require(Path(mem0.__file__).resolve()==ROOT/'mem0_v0.1.118/mem0/__init__.py' and md.version('mem0ai')=='0.1.118','Wrong runtime source')
        atomic(out/'environment.json',dict(mem0_loaded_file=mem0.__file__,mem0ai=md.version('mem0ai'),python=sys.version,
            source_sha256=profile['native_source_sha256'],conda_environment=os.environ.get('CONDA_DEFAULT_ENV')))
        verify_current_state(out,cp)
        config=config_for(profile,settings,out);atomic(out/'mem0_config.redacted.json',config)
        for s in prefix_sessions(manifest,users,uid):
            ordinal=s['chronological_session_ordinal_one_based']
            if ordinal<=cp['completed_ordinal']:continue
            targets=[t for t in manifest['targets'] if t['user_uuid']==uid and t['chronological_session_ordinal_one_based']==ordinal]
            cp=run_session(profile,settings,config,out,s,targets,cp)
            print(f'{uid} committed session {ordinal}',flush=True)
        atomic(out/'status.json',dict(status='completed',completed_sessions=cp['completed_ordinal'],qa='not_run',official_scoring='not_run'))
    return 0


def dry_run(args,profile,manifest,users,settings,missing):
    no_network();env=environment_check(profile)
    run=safe_run_path(args);out=run/'dry_run'
    out.mkdir(parents=True,exist_ok=True)
    plans=[]
    for uid in manifest['selected_users']:
        sessions=prefix_sessions(manifest,users,uid)
        for s in sessions:
            source=users[uid][1]['sessions'][s['original_session_index_zero_based']]
            data.require(s['messages']==[dict(role=m['role'],content=m['content']) for m in source['dialogue']],'Input pollution')
            data.require(all(set(m)=={'role','content'} for m in s['messages']),'Forbidden label input')
        atomic(out/f'{uid}.inputs.json',sessions)
        plans.append(dict(user_uuid=uid,session_ordinals=[s['chronological_session_ordinal_one_based'] for s in sessions],
            message_count=sum(len(s['messages']) for s in sessions),input_sha256=data.digest(out/f'{uid}.inputs.json'),
            vector_path=str(run/'users'/uid/'qdrant'),history_path=str(run/'users'/uid/'history.db'),
            runtime_path=str(run/'users'/uid/'mem0_runtime')))
    # Exercise the real recovery code using opaque files, never Qdrant/SQLite/Memory.
    with tempfile.TemporaryDirectory(prefix='medium-checkpoint-probe-') as temp:
        probe=Path(temp);first=probe/'session_001';first.mkdir()
        atomic(first/'after.json',{'dry_run_fixture':True})
        cp=dict(completed_ordinal=1,commits=[dict(ordinal=1,artifacts_sha256={'after.json':data.digest(first/'after.json')})])
        atomic(probe/'checkpoint.json',cp);verify_commits(probe,cp)
        partial=probe/'session_002';backup=partial/'rollback_before';(backup/'qdrant').mkdir(parents=True)
        (backup/'qdrant'/'opaque-state').write_text('before')
        (backup/'history.db').write_bytes(b'opaque-before-not-a-database')
        atomic(backup/'ready.json',dict(prior_checkpoint=cp,files_sha256={str(p.relative_to(backup)):data.digest(p) for p in backup.rglob('*') if p.is_file()}))
        (probe/'qdrant').mkdir();(probe/'qdrant'/'opaque-state').write_text('partial')
        (probe/'history.db').write_bytes(b'opaque-partial-not-a-database')
        data.require(pending_session(probe,1)==partial,'Partial session not detected')
        data.require([n for n in range(1,4) if n>cp['completed_ordinal']]==[2,3],'Resume replayed a completed ordinal')
        rollback(probe)
        data.require((probe/'qdrant'/'opaque-state').read_text()=='before','Rollback did not restore vector files')
        data.require((probe/'history.db').read_bytes()==b'opaque-before-not-a-database','Rollback did not restore history files')
        data.require(checkpoint(probe)==cp and pending_session(probe,1) is None,'Recovery changed committed progress')
        archives=list((probe/'recovery').iterdir())
        data.require(len(archives)==1 and (archives[0]/'qdrant'/'opaque-state').read_text()=='partial','Partial state was not archived')
        (first/'after.json').write_text('corruption')
        detected=False
        try:verify_commits(probe,cp)
        except ValueError:detected=True
        data.require(detected,'Committed artifact corruption not detected')
        absent=probe/'absent-store';absent.mkdir();detected=False
        try:verify_current_state(absent,cp)
        except ValueError:detected=True
        data.require(detected,'Missing committed database was not refused before opening')
        # Exercise metadata export and CSV-only edit preservation without a model/database.
        for uid in manifest['selected_users']:
            data.require(bool(review.export_user_name(users[uid][1])),'Missing official export name')
        packet_dir=probe/'review-packet';packet_dir.mkdir()
        review.make_review(manifest,packet_dir)
        human_bytes=(packet_dir/'review_pending.csv').read_bytes()+b'\nHUMAN_EDIT_DRY_RUN\n'
        (packet_dir/'review_pending.csv').write_bytes(human_bytes)
        review.make_review(manifest,packet_dir)
        data.require(any(p.read_bytes()==human_bytes for p in (packet_dir/'review_archive').glob('*.csv')),
                     'CSV-only human edits were not archived')
    atomic(out/'report.json',dict(status='passed_offline_dry_run',environment=env,manifest_sha256=data.digest(data.DEV/'manifest.json'),
        profile_sha256=data.digest(PROFILE),missing_credentials=missing,credentials_required_for_dry_run=False,
        network='blocked_in_process',memory_objects_constructed=0,model_calls=0,qa='未运行',official_scoring='未运行',
        plans=plans,checks=['dataset_sha256','frozen_selection','evidence_locations','complete_prefix','chronological_order',
        'raw_dialogue_only','source_hashes','actual_import_version_and_path','separate_paths','partial_session_detection','resume_ordinal_filter','explicit_rollback_restores_before_files','partial_files_archived','committed_artifact_corruption_detection','missing_committed_database_refused','export_name_resolution','csv_only_human_edits_preserved']))
    review.make_review(manifest,run)
    print(json.dumps(dict(status='passed_offline_dry_run',report=str(out/'report.json'),target_count=manifest['total_targets'],model_calls=0),ensure_ascii=False))
    return 0


def run_fingerprint(manifest):
    return dict(manifest_sha256=data.digest(data.DEV/'manifest.json'),profile_sha256=data.digest(PROFILE),
        harness_sha256={p.name:data.digest(p) for p in [Path(__file__),ROOT/'scripts/medium_dev_data.py',ROOT/'scripts/medium_dev_review.py']},
        dataset_sha256=manifest['dataset_sha256'],user_order=manifest['selected_users'])


def main():
    p=argparse.ArgumentParser(description=__doc__)
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--dry-run',action='store_true');modes.add_argument('--preflight',action='store_true')
    modes.add_argument('--execute',action='store_true');modes.add_argument('--export-official',action='store_true')
    modes.add_argument('--rollback-incomplete',action='store_true')
    p.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    p.add_argument('--resume',action='store_true');p.add_argument('--user')
    p.add_argument('--run-id',default='offline_preparation');p.add_argument('--env-file')
    p.add_argument('--dataset',default=str(data.DATA));p.add_argument('--output-root',default=str(ROOT/'results/medium_dev'))
    args=p.parse_args()
    if not args.execute and not args.worker:no_network()
    profile,manifest,users,settings,missing=prepared(args)
    data.require(sys.version_info[:2]==(3,11) and os.environ.get('CONDA_DEFAULT_ENV')=='mem0_halumem','Use conda run -n mem0_halumem python (3.11)')
    if args.worker:return worker(args,profile,manifest,users,settings)
    if args.preflight or args.dry_run or not any([args.execute,args.export_official,args.rollback_incomplete]):
        return dry_run(args,profile,manifest,users,settings,missing)
    run=safe_run_path(args)
    if args.export_official or args.rollback_incomplete:
        data.require((run/'run_record.json').is_file(),'Export/rollback requires an actual run record')
        data.require(data.read(run/'run_record.json')==run_fingerprint(manifest),'Run fingerprint changed')
        with (run/'.run.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            if args.export_official:
                for uid in manifest['selected_users']:
                    user_out=run/'users'/uid;cp=checkpoint(user_out)
                    verify_commits(user_out,cp);verify_current_state(user_out,cp)
                review.make_review(manifest,run);review.export_official(manifest,users,run);return 0
            data.require(bool(args.user),'Rollback requires explicit --user UUID')
            return worker(args,profile,manifest,users,settings)
    existing=(run/'run_record.json').exists()
    data.require(args.resume==existing,'Existing run needs --resume; fresh run must omit --resume')
    run.mkdir(parents=True,exist_ok=True);os.chmod(run,0o700)
    with (run/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        record=run_fingerprint(manifest)
        if existing:data.require(data.read(run/'run_record.json')==record,'Run fingerprint changed; use NEW run_id')
        else:
            atomic(run/'run_record.json',record);atomic(run/'manifest.json',manifest);atomic(run/'profile.json',profile)
            code=run/'code';code.mkdir(exist_ok=False)
            for name in ['medium_dev_run.py','medium_dev_data.py','medium_dev_review.py','local_smoke.py','local_update_case.py']:
                shutil.copy2(ROOT/'scripts'/name,code/name)
            frozen=subprocess.run([sys.executable,'-m','pip','freeze','--all'],capture_output=True,text=True,check=True)
            (run/'requirements-freeze.txt').write_text(base.clean(frozen.stdout))
        status='completed'
        try:
            selected=[args.user] if args.user else manifest['selected_users']
            data.require(all(u in manifest['selected_users'] for u in selected),'Unknown user')
            for uid in selected:
                command=[sys.executable,str(Path(__file__).resolve()),'--worker','--run-id',args.run_id,'--user',uid,
                         '--output-root',str(Path(args.output_root).resolve()),'--dataset',str(Path(args.dataset).resolve())]
                if args.env_file:command+=['--env-file',str(Path(args.env_file).expanduser().resolve())]
                subprocess.run(command,cwd=ROOT,check=True)
            if any(checkpoint(run/'users'/u)['completed_ordinal']!=len(prefix_sessions(manifest,users,u)) for u in manifest['selected_users']):status='partial_users_completed'
        except BaseException:
            status='failed_or_partial';raise
        finally:
            atomic(run/'status.json',dict(status=status,time=now(),qa='未运行',official_scoring='未运行'))
            try:review.make_review(manifest,run)
            except Exception:
                atomic(run/'review_generation_error.json',dict(traceback=base.clean(traceback.format_exc())))
                if status=='completed':raise
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception:
        print(base.clean(traceback.format_exc()),file=sys.stderr);sys.exit(1)
