"""Read-only runtime verification and review artifacts; no model calls."""
import collections
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
run=Path(__file__).resolve().parents[1]
uid='1b846c59-456e-9550-dffd-4d23f1eca81f'
out=run/'users'/uid
cp=r.checkpoint(out)
assert cp['completed_ordinal']==5
r.verify_commits(out,cp);r.verify_current_state(out,cp)
manifest,users=r.data.validate_manifest()
assert len(list(out.glob('session_[0-9][0-9][0-9]')))==5
counts=[];anomalies=[];calls=[]
required=['input.json','before.json','after.json','recall_candidates.json','update_model_io.json','full_operation_plan.json','execution_results.json','actual_operations.json','history_all.json','add_return.json','persistence.json']
for n,s in enumerate(r.prefix_sessions(manifest,users,uid)[:5],1):
    f=out/f'session_{n:03d}'
    assert r.data.read(f/'input.json')==s
    for name in required:assert (f/name).is_file(),(n,name)
    obs=[json.loads(x) for x in (f/'observations.jsonl').read_text().splitlines()]
    inp=[x for x in obs if x['kind']=='session_add_input']
    assert len(inp)==1 and inp[0]['messages']==s['messages'] and inp[0]['infer'] is True
    assert all(set(m)=={'role','content'} for m in s['messages'])
    b=r.data.read(f/'before.json');a=r.data.read(f/'after.json')
    assert b['not_truncated'] and a['not_truncated']
    ops=r.data.read(f/'actual_operations.json')
    counts.append(dict(ordinal=n,original_index=s['original_session_index_zero_based'],messages=len(s['messages']),before=b['database_count_exact'],after=a['database_count_exact'],operations=dict(collections.Counter(x['event'] for x in ops))))
    if (f/'observed_anomaly.json').exists():anomalies.append(dict(ordinal=n,details=r.data.read(f/'observed_anomaly.json')))
    calls.extend(json.loads(x) for x in (f/'api_calls.jsonl').read_text().splitlines())
assert sum(x['messages'] for x in counts)==150
f=out/'session_005'
before={p['id']:p['payload']['data'] for p in r.data.read(f/'before.json')['database_points_with_vectors']}
after={p['id']:p['payload']['data'] for p in r.data.read(f/'after.json')['database_points_with_vectors']}
diff=[dict(id=i,before=before.get(i),after=after.get(i)) for i in sorted(before.keys()|after.keys()) if before.get(i)!=after.get(i)]
r.atomic(run/'verification_summary.json',dict(status='verified_complete_prefix_with_recorded_native_anomalies',sessions=counts,model_api_calls=len(calls),native_anomalies=anomalies,empty_initial_database=r.data.read(out/'session_001/before.json')['database_count_exact']==0,review_version='human_review_v1_20261028',input_policy='Exact full raw dialogue role/content only; no labels or prefilled memories',checkpoint_verified=True))
r.atomic(run/'target_before_after.json',dict(before=before,after=after,changed=diff,actual_operations=r.data.read(f/'actual_operations.json')))
lines=['# 晋升目标完整前后对照','', '用户：'+uid+'；原始 sessions[4]；本文件只用于运行后复核，未进入模型输入。','', '## 更新前全部记忆','']
lines += [f'- `{i}`: {t}' for i,t in sorted(before.items())]
lines += ['', '## 更新后全部记忆','']+[f'- `{i}`: {t}' for i,t in sorted(after.items())]
lines += ['', '## 全部变化','']+[f'- `{d["id"]}`\n  - 前：{d["before"]}\n  - 后：{d["after"]}' for d in diff]
(run/'target_before_after.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(sessions=counts,anomaly_sessions=[x['ordinal'] for x in anomalies],changed=diff),ensure_ascii=False,indent=2))
