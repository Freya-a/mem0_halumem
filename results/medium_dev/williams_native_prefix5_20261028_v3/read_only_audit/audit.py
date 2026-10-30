"""Pre-continuation audit. Opens only disposable database copies; no model calls."""
import hashlib,json,os,shutil,sqlite3,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1]
uid='1b846c59-456e-9550-dffd-4d23f1eca81f'
out=run/'users'/uid
def read(p):return json.loads(p.read_text())
def inventory(p):return {str(f.relative_to(p)):r.data.digest(f) for f in p.rglob('*') if f.is_file() and not f.is_relative_to(run/'read_only_audit')}
original=inventory(run)
version=run/'human_review_version'
fp=read(version/'human_review_fingerprint.json')
assert hashlib.sha256(json.dumps(fp['payload'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==fp['version_fingerprint_sha256']
for group in ('source_sha256','native_source_sha256','artifact_sha256'):
    for p,sha in fp['payload'][group].items():assert r.data.digest(ROOT/p)==sha,p
failures=[]
for n in (1,2):
    f=run.parent/f'williams_native_prefix5_20261028_v{n}'/'users'/uid
    cfg=read(f/'mem0_config.redacted.json')
    assert Path(cfg['history_db_path']).resolve()==f/'history.db'
    assert Path(cfg['vector_store']['config']['path']).resolve()==f/'qdrant'
    assert read(f/'session_001/before.json')['database_count_exact']==0
    assert read(f/'session_001/after_partial.json')['database_count_exact']==0
    assert read(f/'session_001/actual_operations_partial.json')==[]
    assert r.base.history_rows(f/'history.db')==[]
    calls=[json.loads(x) for x in (f/'session_001/api_calls.jsonl').read_text().splitlines()]
    assert len(calls)==1 and calls[0]['status']=='error'
    failures.append(dict(run_id=f.parents[1].name,history_path=cfg['history_db_path'],vector_path=cfg['vector_store']['config']['path'],writes=0,failed_api_requests=1))
cp=r.checkpoint(out);r.verify_commits(out,cp)
assert cp['completed_ordinal']==5
assert sorted(f.name for f in out.glob('session_[0-9][0-9][0-9]'))==[f'session_{i:03d}' for i in range(1,6)]
with tempfile.TemporaryDirectory(prefix='mem0-readonly-audit-') as t:
    t=Path(t);shutil.copytree(out/'qdrant',t/'qdrant');shutil.copy2(out/'history.db',t/'history.db')
    r.persisted_check(t,t,read(out/'session_005/after.json'))
    assert r.base.history_rows(t/'history.db')==read(out/'session_005/history_all.json')
    assert read(t/'persistence.json')['history_integrity']=='ok'
os.environ['MEM0_TELEMETRY']='False'
with tempfile.TemporaryDirectory(prefix='mem0-audit-import-') as t:
    os.environ['MEM0_DIR']=t
    from mem0.memory.main import get_update_memory_messages,get_fact_retrieval_messages,parse_messages
    from mem0.memory.utils import remove_code_blocks
    manifest,users=r.data.validate_manifest()
    sessions=r.prefix_sessions(manifest,users,uid)[:5]
    for n,s in enumerate(sessions,1):
        f=out/f'session_{n:03d}';obs=read(f/'observations.json')
        assert read(f/'input.json')==s
        sdk=[json.loads(x) for x in (f/'api_calls.jsonl').read_text().splitlines() if json.loads(x)['kind']=='llm']
        ins=[e for e in obs if e['kind']=='model_input'];outs=[e for e in obs if e['kind']=='model_output']
        assert len(sdk)==len(ins)==len(outs)==2
        sys_prompt,user_prompt=get_fact_retrieval_messages(parse_messages(s['messages']))
        assert ins[0]['messages']==[dict(role='system',content=sys_prompt),dict(role='user',content=user_prompt)]
        update=get_update_memory_messages(ins[1]['native_retrieved_old_memory'],ins[1]['native_new_facts'],None)
        assert ins[1]['messages']==[dict(role='user',content=update)]
        for req,inp,output in zip(sdk,ins,outs):
            assert req['request']['messages']==inp['messages']
            assert req['response']['choices'][0]['message']['content']==output['raw_response']
            assert req['request']['model']=='qwen-plus' and req['request']['temperature']==0.5 and req['request']['max_tokens']==16384
        searches=[e for e in obs if e['kind']=='recall_input']
        assert searches and all(e['limit']==5 and e['filters']=={'user_id':uid} for e in searches)
    f=out/'session_002';io=read(f/'update_model_io.json');inp,output=io
    mapping=inp['native_temp_uuid_mapping'];assert set(mapping)==set(map(str,range(15)))
    rec=[e for e in read(f/'recall_candidates.json') if e['kind']=='recall_output']
    ordered=list(dict.fromkeys(str(c['id']) for e in rec for c in e['candidates']))
    assert list(mapping.values())==ordered
    actions=json.loads(remove_code_blocks(output['raw_response']))['memory']
    bad=[x for x in actions if x['event'] in ('UPDATE','DELETE') and x['id'] not in mapping]
    assert len(bad)==1 and bad[0]['id']=='19'
    assert bad[0]['old_memory']=='Career goal is to become a renowned director known for historically accurate films'
    real_id=next(i for i,t in ((i,p['payload']['data']) for i,p in ((p['id'],p) for p in read(f/'before.json')['database_points_with_vectors'])) if t==bad[0]['old_memory'])
    actual=read(f/'actual_operations.json')
    assert len(actual)==14 and all(x['event']=='ADD' for x in actual)
    assert not any(x['memory_id']==real_id for x in actual)
    errors=[json.loads(x) for x in (f/'runtime.jsonl').read_text().splitlines() if json.loads(x)['level']=='ERROR']
    assert len(errors)==1 and "Error: '19'" in errors[0]['message']
assert inventory(run)==original,'Audit modified existing evidence'
r.atomic(run/'read_only_audit/result.json',dict(status='PASS',review_fingerprint=fp['version_fingerprint_sha256'],
    failed_launches=failures,formal_v3_first_before_empty=True,completed_ordinals=list(range(1,6)),
    committed_artifacts_verified=True,current_vectors_and_history_match=True,existing_files_unchanged=True,
    observed_vs_sdk_raw_io_equal=True,native_prompt_regeneration_equal=True,native_recall_top5_and_user_filter_equal=True,
    invalid_id_origin=dict(mapping=mapping,model_raw_action=bad[0],real_old_memory_id=real_id,actual_operations=14,
      diagnosis='Provider output assigns UPDATE to new temporary ID19 absent from existing ID0..14 map. Native lookup raises before observer operation wrapper; native catches and skips. Instrumentation forwards identical arguments and raw result; no response or retrieval mutation.'),
    source_review='Observer.install and APIAudit.wrap reviewed: original arguments/results forwarded; mappings only deep-copied for logging. Frozen native/harness hashes match audit version.',
    condition_for_resume='Confirmed clean independent namespace and unchanged native data path. Continue existing native state; retain observed anomaly.'))
print('PASS: namespace isolation; native model/processing origin; checkpoint/vectors/history; existing evidence unchanged')
