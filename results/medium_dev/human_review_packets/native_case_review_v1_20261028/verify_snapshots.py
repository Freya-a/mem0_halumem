import collections, json, shutil, sys, tempfile
from pathlib import Path
ROOT=Path('/home/shu1004/ld/system/mem0_halumem_diagnosis')
sys.path.insert(0,str(ROOT/'scripts'))
import medium_dev_run as r
from qdrant_client import QdrantClient
RUN=ROOT/'results/medium_dev/williams_native_prefix5_20261028_v3'
cases=[('A','2f1f897e-d67f-dbc5-6a7b-b7634a9e294f',9,'e1d4f8f9-0520-427d-94fd-a2ac0ee69d03'),
       ('B','1b846c59-456e-9550-dffd-4d23f1eca81f',7,'eef34a57-c82a-4995-877d-66b54b9589da'),
       ('C','348492a7-cfe4-ee1d-73c3-c276d6ba8277',8,'05afde13-35bd-4d26-bbae-6de427d58db1'),
       ('target_7','2f1f897e-d67f-dbc5-6a7b-b7634a9e294f',8,'e6ab178b-c0f9-4adb-bfb7-e4648617a950'),
       ('target_10','1b846c59-456e-9550-dffd-4d23f1eca81f',5,'e13b825e-7ec7-4760-821e-0581d8da5650')]
manifest,users=r.data.validate_manifest()
output=[]
for label,uid,n,mid in cases:
    user=RUN/'users'/uid; folder=user/f'session_{n:03d}'; backup=folder/'rollback_before'
    ready=r.data.read(backup/'ready.json');cp=r.checkpoint(user);r.verify_commits(user,cp)
    assert ready['ordinal']==n and ready['prior_checkpoint']['completed_ordinal']==n-1
    assert ready['prior_checkpoint']['commits']==cp['commits'][:n-1]
    for rel,sha in ready['files_sha256'].items():assert r.data.digest(backup/rel)==sha,(label,rel)
    before=r.data.read(folder/'before.json');previous=r.data.read(user/f'session_{n-1:03d}'/'history_all.json')
    assert r.base.history_rows(backup/'history.db')==previous
    source=users[uid][1]['sessions'][n-1]
    data=r.data.read(folder/'input.json')
    assert data['original_session_index_zero_based']==n-1
    assert data['messages']==[dict(role=m['role'],content=m['content']) for m in source['dialogue']]
    assert all(set(m)=={'role','content'} for m in data['messages'])
    assert data['raw_dialogue']==[dict(m) for m in source['dialogue']]
    with tempfile.TemporaryDirectory(prefix='mem0-common-snapshot-') as tmp:
        temp=Path(tmp);shutil.copytree(backup/'qdrant',temp/'qdrant')
        client=QdrantClient(path=str(temp/'qdrant'))
        try:
            points,count,pages=r.base.collect_points(client,'medium_dev',None)
            r.base.verify_persistence(before['database_points_with_vectors'],points)
        finally:client.close()
    assert count==before['database_count_exact']
    target=[p['payload']['data'] for p in before['database_points_with_vectors'] if p['id']==mid]
    assert len(target)==1
    api=[json.loads(s) for s in (folder/'api_calls.jsonl').read_text().splitlines()]
    actual=r.data.read(folder/'actual_operations.json');plan=r.data.read(folder/'full_operation_plan.json')
    output.append(dict(case=label,user_uuid=uid,original_session_index=n-1,chronological_ordinal=n,
        messages=len(data['messages']),start_time=data['start_time'],end_time=data['end_time'],
        before_count=count,history_rows=len(previous),target_memory_id=mid,target_memory_text=target[0],
        before_sha256=r.data.digest(folder/'before.json'),input_sha256=r.data.digest(folder/'input.json'),
        backup_ready_sha256=r.data.digest(backup/'ready.json'),backup_files=len(ready['files_sha256']),
        baseline_api_calls=dict(collections.Counter(x['kind'] for x in api)),
        baseline_api_status=dict(collections.Counter(x['status'] for x in api)),
        baseline_actual_operations=dict(collections.Counter(x['event'] for x in actual)),
        baseline_plan=dict(collections.Counter(x['event'] for x in plan)),
        vector_and_payload_match=True,backup_file_hashes_match=True,history_matches_previous_commit=True,
        dialogue_role_content_matches_source=True))
print(json.dumps({'status':'PASS','cases':output,'model_calls':0},ensure_ascii=False,indent=2))
