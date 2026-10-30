"""Build review evidence solely from existing artifacts. Never calls a model."""
import collections,csv,hashlib,json,os,sys,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1];dest=run/'development_diagnosis_v1';dest.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='mem0-final-import-') as temp:
    os.environ['MEM0_DIR']=temp;os.environ['MEM0_TELEMETRY']='False'
    from mem0.memory.main import get_update_memory_messages,get_fact_retrieval_messages,parse_messages
rows=list(csv.DictReader((run/'human_review_version/human_review.csv').open(encoding='utf-8-sig')))
manifest,users=r.data.validate_manifest()
r.source_check(r.data.read(r.PROFILE))
assert r.data.read(run/'run_record.json')==r.run_fingerprint(manifest)
version=run/'human_review_version'
for line in (version/'SHA256SUMS').read_text().splitlines():
    sha,name=line.split()
    assert r.data.digest(version/name)==sha,name
    assert (version/name).read_bytes()==(ROOT/'diagnosis/medium_dev'/name).read_bytes(),name
fingerprint=r.data.read(version/'human_review_fingerprint.json')
assert hashlib.sha256(json.dumps(fingerprint['payload'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==fingerprint['version_fingerprint_sha256']
for group in ('source_sha256','native_source_sha256','artifact_sha256'):
    for name,sha in fingerprint['payload'][group].items():assert r.data.digest(ROOT/name)==sha,name
summary=[];global_ops=collections.Counter();plans_total=collections.Counter();mismatches=[]
for uid in manifest['selected_users']:
    out=run/'users'/uid;cp=r.checkpoint(out);r.verify_commits(out,cp)
    sessions=r.prefix_sessions(manifest,users,uid)
    assert cp['completed_ordinal']==len(sessions),(uid,cp['completed_ordinal'])
    with tempfile.TemporaryDirectory(prefix='mem0-final-verify-') as t:
        t=Path(t);shutil.copytree(out/'qdrant',t/'qdrant');shutil.copy2(out/'history.db',t/'history.db')
        r.persisted_check(t,t,r.data.read(out/f'session_{len(sessions):03d}/after.json'))
        assert r.base.history_rows(t/'history.db')==r.data.read(out/f'session_{len(sessions):03d}/history_all.json')
    previous_history=[]
    for s in sessions:
        n=s['chronological_session_ordinal_one_based'];f=out/f'session_{n:03d}'
        assert r.data.read(f/'input.json')==s
        obs=r.data.read(f/'observations.json');ins=[x for x in obs if x['kind']=='session_add_input']
        assert len(ins)==1 and ins[0]['messages']==s['messages'] and ins[0]['infer'] is True
        assert all(set(m)=={'role','content'} for m in s['messages'])
        llm_in=[x for x in obs if x['kind']=='model_input'];llm_out=[x for x in obs if x['kind']=='model_output']
        sdk=[json.loads(line) for line in (f/'api_calls.jsonl').read_text().splitlines()]
        sdk_llm=[x for x in sdk if x['kind']=='llm']
        assert len(llm_in)==len(llm_out)==len(sdk_llm)==2,(uid,n,'LLM calls')
        sys_prompt,user_prompt=get_fact_retrieval_messages(parse_messages(s['messages']))
        assert llm_in[0]['messages']==[dict(role='system',content=sys_prompt),dict(role='user',content=user_prompt)]
        update=get_update_memory_messages(llm_in[1]['native_retrieved_old_memory'],llm_in[1]['native_new_facts'],None)
        assert llm_in[1]['messages']==[dict(role='user',content=update)]
        for req,inp,outp in zip(sdk_llm,llm_in,llm_out):
            assert req['status']=='ok' and req['request']['messages']==inp['messages']
            assert req['response']['choices'][0]['message']['content']==outp['raw_response']
            assert req['request']['model']=='qwen-plus' and req['request']['temperature']==0.5 and req['request']['max_tokens']==16384
        for req in sdk:
            assert req['status']=='ok'
            if req['kind']=='embedding':
                assert req['request']['model']=='text-embedding-v4'
                assert all(x['dimensions']==1024 and x['all_finite'] for x in req['response']['data'])
        assert all(x['limit']==5 and x['filters']=={'user_id':uid} for x in obs if x['kind']=='recall_input')
        b=r.data.read(f/'before.json');a=r.data.read(f/'after.json')
        assert b['not_truncated'] and a['not_truncated']
        if n==1:assert b['database_count_exact']==0
        else:r.base.verify_persistence(r.data.read(out/f'session_{n-1:03d}/after.json')['database_points_with_vectors'],b['database_points_with_vectors'])
        actual=r.data.read(f/'actual_operations.json');plan=r.data.read(f/'full_operation_plan.json')
        r.base.reconcile(b,a,actual,r.data.read(f/'add_return.json')['return_value'])
        assert r.data.read(f/'history_all.json')==previous_history+actual,(uid,n,'history continuity')
        previous_history=r.data.read(f/'history_all.json')
        noop=sum(1 for line in (f/'runtime.jsonl').read_text().splitlines() if json.loads(line)['message']=='NOOP for Memory.')
        assert noop==sum(p['event']=='NONE' and bool(p.get('text')) for p in plan),(uid,n,'NONE dispatch')
        remaining=list(actual);unexecuted=[];matched=[]
        for p in plan:
            if not p.get('text') or p['event']=='NONE':continue
            found=next((x for x in remaining if x['event']==p['event'] and
                (p['event']=='ADD' or x['memory_id']==p['resolved_existing_memory_id']) and
                (p['event']=='DELETE' or x['new_memory']==p['text'])),None)
            if found:remaining.remove(found);matched.append(dict(plan_index=p['plan_index_zero_based'],actual_sequence=found['sequence']))
            else:unexecuted.append(p)
        diff=dict(user_uuid=uid,ordinal=n,planned= dict(collections.Counter(x['event'] for x in plan)),actual=dict(collections.Counter(x['event'] for x in actual)),
            unexecuted_plans=unexecuted,unexpected_actual=remaining,matched=matched,
            same_text_updates=sum(x['event']=='UPDATE' and x['old_memory']==x['new_memory'] for x in actual))
        if unexecuted or remaining:mismatches.append(diff)
        global_ops.update(x['event'] for x in actual);plans_total.update(x['event'] for x in plan)
        summary.append(dict(user_uuid=uid,ordinal=n,original_index=s['original_session_index_zero_based'],messages=len(s['messages']),before=b['database_count_exact'],after=a['database_count_exact'],**{k:v for k,v in diff.items() if k not in ('user_uuid','ordinal')},anomaly=(f/'observed_anomaly.json').exists()))
assert len(summary)==28 and sum(x['messages'] for x in summary)==990
for number,t in enumerate(rows,1):
    uid=t['user_uuid'];target=next(x for x in manifest['targets'] if x['target_id']==t['target_id'])
    f=run/'users'/uid/f'session_{target["chronological_session_ordinal_one_based"]:03d}'
    def texts(name):return {p['id']:p['payload']['data'] for p in r.data.read(f/name)['database_points_with_vectors']}
    before=texts('before.json');after=texts('after.json')
    rec=[x for x in r.data.read(f/'recall_candidates.json') if x['kind']=='recall_output']
    recalled={str(c['id']) for x in rec for c in x['candidates']}
    evidence=dict(number=number,target_id=t['target_id'],review=t,original_target=target,
        before=before,after=after,recalled_ids=sorted(recalled),recall_queries=rec,
        changed=[dict(id=i,before=before.get(i),after=after.get(i)) for i in sorted(before.keys()|after.keys()) if before.get(i)!=after.get(i)],
        raw_facts=r.data.read(f/'extracted_facts.json'),plan=r.data.read(f/'full_operation_plan.json'),actual=r.data.read(f/'actual_operations.json'))
    r.atomic(dest/f'target_{number:02d}_evidence.json',evidence)
    lines=[f'# {number}. {t["target_id"]}',f'预期：{t["supported_new_state"]}',f'原旧命题：{target["old_proposition"]}','## 更新前（R=已召回）']
    lines += [f'{i} {"R" if i in recalled else "-"} {text}' for i,text in before.items()]
    lines += ['## 全部文本变化']+[f'{x["id"]}: {x["before"]} => {x["after"]}' for x in evidence['changed']]
    (dest/f'target_{number:02d}_evidence.md').write_text('\n'.join(lines)+'\n')
r.atomic(dest/'runtime_verification.json',dict(status='PASS',sessions=summary,total_sessions=28,total_messages=990,
    actual_operations=dict(global_ops),planned_operations=dict(plans_total),plan_actual_mismatches=mismatches,
    native_anomaly_sessions=[dict(user_uuid=x['user_uuid'],ordinal=x['ordinal']) for x in summary if x['anomaly']],
    input_verified=True,native_prompts_reconstructed_and_sdk_messages_equal=True,native_model_raw_responses_equal=True,
    sdk_model_parameters_and_embedding_dimensions_verified=True,recall_top5_and_user_filter_verified=True,
    first_five_not_replayed=True,review_snapshot_and_source_fingerprint_verified=True,qa='not_run',review_model_calls=0))
print(json.dumps(dict(sessions=28,messages=990,actual=dict(global_ops),planned=dict(plans_total),mismatches=len(mismatches)),ensure_ascii=False))
