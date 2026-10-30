"""Continue actual native state after audited, swallowed native plan errors; never retry calls."""
import fcntl
import os
from pathlib import Path
import sys
import argparse

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1]
uid='1b846c59-456e-9550-dffd-4d23f1eca81f'
out=run/'users'/uid
args=argparse.Namespace(dataset=str(r.data.DATA),env_file=str(ROOT/'.env.local'),execute=True,worker=False)
profile,manifest,users,settings,missing=r.prepared(args)
assert r.data.read(run/'run_record.json')==r.run_fingerprint(manifest)
assert os.environ.get('CONDA_DEFAULT_ENV')=='mem0_halumem'
os.environ['MEM0_DIR']=str(out/'mem0_runtime')
os.environ['MEM0_TELEMETRY']='False'

def commit_observed(cp,n):
    folder=out/f'session_{n:03d}'
    # Only a returned native add with complete snapshots and successful API calls is eligible.
    # Transport, parse, observer, or persistence errors still abort. No mutation is repaired.
    ret=r.data.read(folder/'add_return.json')
    assert ret['exception'] is None and ret['return_value'] is not None
    before=r.data.read(folder/'before.json'); after=r.data.read(folder/'after.json')
    ops=r.data.read(folder/'actual_operations.json')
    r.base.reconcile(before,after,ops,ret['return_value'])
    calls=[__import__('json').loads(x) for x in (folder/'api_calls.jsonl').read_text().splitlines()]
    assert calls and all(c['status']=='ok' and (c['kind']!='llm' or c['response']['choices'][0]['finish_reason']=='stop') for c in calls)
    observations=[__import__('json').loads(x) for x in (folder/'observations.jsonl').read_text().splitlines()]
    assert not any(e['kind'].endswith('exception') or e.get('parse_error') or e.get('status')=='error' for e in observations)
    errors=[__import__('json').loads(x) for x in (folder/'runtime.jsonl').read_text().splitlines() if __import__('json').loads(x)['level']=='ERROR']
    assert errors and all('Error processing memory action:' in e['message'] for e in errors)
    r.persisted_check(folder,out,after)
    r.atomic(folder/'observed_anomaly.json',dict(status='native_add_returned_with_swallowed_plan_errors',errors=errors,
        policy='Preserve native resulting state. No replay, repair, rollback, or success assertion. Strict harness rejection remains in error.json.'))
    artifacts={p.name:r.data.digest(p) for p in folder.iterdir() if p.is_file()}
    cp=dict(completed_ordinal=n,commits=cp['commits']+[dict(ordinal=n,artifacts_sha256=artifacts)],committed_at=r.now())
    r.atomic(out/'checkpoint.json',cp)
    print(f'OBSERVED session {n}/5 with native anomaly; no replay',flush=True)
    return cp

with (run/'.run.lock').open('a') as lock,(out/'.worker.lock').open('a') as ulock:
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(ulock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    cp=r.checkpoint(out);r.verify_commits(out,cp)
    assert cp['completed_ordinal']==1
    cp=commit_observed(cp,2)
    config=r.config_for(profile,settings,out)
    r.atomic(run/'continuation_policy.json',dict(launcher_sha256=r.data.digest(Path(__file__)),
        reason='Observe native swallowed operation errors without changing native behavior or retrying sessions',
        boundary=5,strict_harness_failures_preserved=True))
    try:
        for s in r.prefix_sessions(manifest,users,uid)[2:5]:
            n=s['chronological_session_ordinal_one_based']
            targets=[t for t in manifest['targets'] if t['user_uuid']==uid and t['chronological_session_ordinal_one_based']==n]
            try:cp=r.run_session(profile,settings,config,out,s,targets,cp)
            except Exception:cp=commit_observed(cp,n)
            print(f'FINISHED observed session {n}/5',flush=True)
        r.verify_commits(out,cp);r.verify_current_state(out,cp)
        r.atomic(run/'status.json',dict(status='requested_prefix_completed_with_native_anomalies',completed_sessions=5,messages=150,qa='not_run',official_scoring='not_run'))
        r.atomic(out/'status.json',dict(status='paused_at_requested_boundary_with_native_anomalies',completed_sessions=5,next_session_ordinal=6))
    except BaseException:
        r.atomic(run/'status.json',dict(status='failed_or_partial',completed_sessions=r.checkpoint(out)['completed_ordinal']))
        raise
print('STOP at sessions[4], verified persistent checkpoint',flush=True)
