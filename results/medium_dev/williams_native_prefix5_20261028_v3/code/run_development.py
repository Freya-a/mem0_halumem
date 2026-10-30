"""Continue native development observation, with per-user fresh interpreter and no replay."""
import argparse,fcntl,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1]
order=['1b846c59-456e-9550-dffd-4d23f1eca81f','2f1f897e-d67f-dbc5-6a7b-b7634a9e294f','348492a7-cfe4-ee1d-73c3-c276d6ba8277']
p=argparse.ArgumentParser();p.add_argument('--user');args=p.parse_args()
profile,manifest,users,settings,missing=r.prepared(argparse.Namespace(dataset=str(r.data.DATA),env_file=str(ROOT/'.env.local'),execute=True,worker=False))
assert r.data.read(run/'run_record.json')==r.run_fingerprint(manifest)
assert r.data.read(run/'read_only_audit/result.json')['status']=='PASS'
assert os.environ.get('CONDA_DEFAULT_ENV')=='mem0_halumem'

def commit_native_return(out,cp,n):
    folder=out/f'session_{n:03d}'
    ret=r.data.read(folder/'add_return.json')
    assert ret['exception'] is None and ret['return_value'] is not None,'Native add did not return; stop without retry'
    before=r.data.read(folder/'before.json');after=r.data.read(folder/'after.json')
    ops=r.data.read(folder/'actual_operations.json')
    r.base.reconcile(before,after,ops,ret['return_value'])
    calls=[json.loads(x) for x in (folder/'api_calls.jsonl').read_text().splitlines()]
    obs=[json.loads(x) for x in (folder/'observations.jsonl').read_text().splitlines()]
    logs=[json.loads(x) for x in (folder/'runtime.jsonl').read_text().splitlines()]
    errors=[x for x in logs if x['level']=='ERROR']
    assert errors or any(x.get('parse_error') or x['kind'].endswith('exception') or x.get('status')=='error' for x in obs),'Unexpected strict validator failure; investigate'
    r.persisted_check(folder,out,after)
    r.atomic(folder/'observed_anomaly.json',dict(status='native_add_returned_with_recorded_anomalies',errors=errors,
        observer_anomalies=[x for x in obs if x.get('parse_error') or x['kind'].endswith('exception') or x.get('status')=='error'],
        sdk_anomalies=[x for x in calls if x['status']!='ok'],policy='Native actual state preserved; no repair, rollback, or retry. Strict rejection kept in error.json.'))
    artifacts={f.name:r.data.digest(f) for f in folder.iterdir() if f.is_file()}
    cp=dict(completed_ordinal=n,commits=cp['commits']+[dict(ordinal=n,artifacts_sha256=artifacts)],committed_at=r.now())
    r.atomic(out/'checkpoint.json',cp)
    print(f'{out.name} OBSERVED native anomaly session {n}',flush=True)
    return cp

if args.user:
    uid=args.user;assert uid in order
    out=run/'users'/uid
    if uid!=order[0]:assert not out.exists(),'Other users must start from fresh independent state'
    out.mkdir(parents=True,exist_ok=True)
    os.environ['MEM0_DIR']=str(out/'mem0_runtime');os.environ['MEM0_TELEMETRY']='False'
    os.environ.pop('OPENROUTER_API_KEY',None)
    import mem0
    assert r.md.version('mem0ai')=='0.1.118' and Path(mem0.__file__).resolve()==ROOT/'mem0_v0.1.118/mem0/__init__.py'
    with (out/'.worker.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        cp=r.checkpoint(out);r.verify_commits(out,cp)
        assert r.pending_session(out,cp['completed_ordinal']) is None
        if uid==order[0]:assert cp['completed_ordinal']==5
        else:assert cp['completed_ordinal']==0
        r.verify_current_state(out,cp)
        r.atomic(out/'development_environment.json',dict(mem0ai=r.md.version('mem0ai'),mem0_loaded_file=mem0.__file__,python=sys.version,conda_environment=os.environ.get('CONDA_DEFAULT_ENV')))
        config=r.config_for(profile,settings,out);r.atomic(out/'development_config.redacted.json',config)
        for s in r.prefix_sessions(manifest,users,uid):
            n=s['chronological_session_ordinal_one_based']
            if n<=cp['completed_ordinal']:continue
            targets=[t for t in manifest['targets'] if t['user_uuid']==uid and t['chronological_session_ordinal_one_based']==n]
            try:cp=r.run_session(profile,settings,config,out,s,targets,cp)
            except Exception:cp=commit_native_return(out,cp,n)
            print(f'{uid} completed session {n}',flush=True)
        r.verify_commits(out,cp);r.verify_current_state(out,cp)
        r.atomic(out/'status.json',dict(status='complete_native_observation',completed_sessions=cp['completed_ordinal'],anomaly_sessions=[x.parent.name for x in out.glob('session_*/observed_anomaly.json')],qa='not_run'))
else:
    assert sum(len(r.prefix_sessions(manifest,users,u)) for u in order)==28
    assert sum(len(s['messages']) for u in order for s in r.prefix_sessions(manifest,users,u))==990
    with (run/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        archive=run/'pre_continuation';archive.mkdir(exist_ok=False)
        for f in [run/'status.json',run/'users'/order[0]/'status.json',run/'users'/order[0]/'checkpoint.json']:
            shutil.copy2(f,archive/(('user_' if f.parent.name==order[0] else '')+f.name))
        r.atomic(run/'development_scope.json',dict(order=order,total_sessions=28,total_messages=990,existing_sessions_not_replayed=5,
            review_version='human_review_v1_20261028',launcher_sha256=r.data.digest(Path(__file__)),qa='not_run',improvements='not_run',
            anomaly_policy='Preserve every normally returned native add and its swallowed errors, verifying actual snapshots/history. Never replay.'))
        try:
            for uid in order:
                subprocess.run([sys.executable,str(Path(__file__).resolve()),'--user',uid],cwd=ROOT,check=True)
            r.atomic(run/'status.json',dict(status='complete_28_session_native_observation',sessions=28,messages=990,qa='not_run',official_scoring='not_run'))
        except BaseException:
            r.atomic(run/'status.json',dict(status='development_failed_or_partial',completed={u:r.checkpoint(run/'users'/u)['completed_ordinal'] for u in order}))
            raise
