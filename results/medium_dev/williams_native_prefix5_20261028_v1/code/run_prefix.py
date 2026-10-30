"""Bounded operational launch; native runtime and frozen harness are unchanged."""
import argparse
import csv
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
import medium_dev_run as r

uid = '1b846c59-456e-9550-dffd-4d23f1eca81f'
run = Path(__file__).resolve().parents[1]
args = argparse.Namespace(dataset=str(r.data.DATA), env_file=str(ROOT/'.env.local'),
    execute=True, worker=False, run_id=run.name, output_root=str(run.parent))
profile, manifest, users, settings, missing = r.prepared(args)
assert sys.version_info[:2] == (3,11) and os.environ.get('CONDA_DEFAULT_ENV') == 'mem0_halumem'
version = ROOT/'diagnosis/medium_dev/review_versions/human_review_v1_20261028'
for line in (version/'SHA256SUMS').read_text().splitlines():
    sha, name = line.split()
    assert r.data.digest(version/name) == sha, name
    assert (version/name).read_bytes() == (ROOT/'diagnosis/medium_dev'/name).read_bytes(), name
fp = r.data.read(version/'human_review_fingerprint.json')
assert hashlib.sha256(json.dumps(fp['payload'], ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()).hexdigest() == fp['version_fingerprint_sha256']
for section in ('source_sha256','native_source_sha256','artifact_sha256'):
    for name, sha in fp['payload'][section].items():
        assert r.data.digest(ROOT/name) == sha, name
with (version/'human_review.csv').open() as f:
    assert len(list(csv.DictReader(f))) == 24
sessions = r.prefix_sessions(manifest, users, uid)[:5]
assert [s['original_session_index_zero_based'] for s in sessions] == list(range(5))
assert sum(len(s['messages']) for s in sessions) == 150
for s in sessions:
    raw = users[uid][1]['sessions'][s['original_session_index_zero_based']]['dialogue']
    assert s['messages'] == [dict(role=m['role'],content=m['content']) for m in raw]
print('VERIFIED: review 24/24; immutable fingerprint; 5 complete sessions / 150 raw messages', flush=True)
out = run/'users'/uid
out.mkdir(parents=True, exist_ok=True)
os.chmod(run, 0o700)
os.environ['MEM0_DIR'] = str(out/'mem0_runtime')
os.environ['MEM0_TELEMETRY'] = 'False'
os.environ.pop('OPENROUTER_API_KEY', None)
with (run/'.run.lock').open('a') as lock, (out/'.worker.lock').open('a') as ulock:
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    fcntl.flock(ulock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not (run/'run_record.json').exists(), 'Fresh bounded launch only; use saved resume command'
    r.atomic(run/'run_record.json', r.run_fingerprint(manifest))
    r.atomic(run/'manifest.json', manifest)
    r.atomic(run/'profile.json', profile)
    shutil.copytree(version, run/'human_review_version')
    for name in ['medium_dev_run.py','medium_dev_data.py','medium_dev_review.py','local_smoke.py','local_update_case.py']:
        shutil.copy2(ROOT/'scripts'/name, run/'code'/name)
    r.atomic(run/'scope.json', dict(user_uuid=uid, original_session_indices=list(range(5)), messages=150,
        stop_after_ordinal=5, review_fingerprint=fp['version_fingerprint_sha256'],
        launcher_sha256=r.data.digest(Path(__file__)), qa='not_run', improvements='not_run'))
    frozen = subprocess.run([sys.executable,'-m','pip','freeze','--all'],capture_output=True,text=True,check=True)
    (run/'requirements-freeze.txt').write_text(r.base.clean(frozen.stdout))
    import mem0
    assert r.md.version('mem0ai') == '0.1.118'
    assert Path(mem0.__file__).resolve() == ROOT/'mem0_v0.1.118/mem0/__init__.py'
    r.atomic(out/'environment.json',dict(mem0ai=r.md.version('mem0ai'),mem0_loaded_file=mem0.__file__,python=sys.version,conda_environment=os.environ.get('CONDA_DEFAULT_ENV')))
    config = r.config_for(profile,settings,out)
    r.atomic(out/'mem0_config.redacted.json',config)
    cp = r.checkpoint(out)
    assert cp['completed_ordinal'] == 0
    try:
        for s in sessions:
            n = s['chronological_session_ordinal_one_based']
            targets = [t for t in manifest['targets'] if t['user_uuid']==uid and t['chronological_session_ordinal_one_based']==n]
            cp = r.run_session(profile,settings,config,out,s,targets,cp)
            print(f'COMMITTED session {n}/5',flush=True)
        r.verify_commits(out,cp)
        r.verify_current_state(out,cp)
        r.atomic(out/'status.json',dict(status='paused_at_requested_boundary',completed_sessions=5,next_session_ordinal=6,qa='not_run'))
        r.atomic(run/'status.json',dict(status='requested_prefix_completed',full_development_run='partial',completed_sessions=5,messages=150,qa='not_run'))
    except BaseException:
        r.atomic(run/'status.json',dict(status='failed_or_partial',completed_sessions=r.checkpoint(out)['completed_ordinal']))
        raise
print('STOPPED at sessions[4]; checkpoint verified; no later session executed',flush=True)
