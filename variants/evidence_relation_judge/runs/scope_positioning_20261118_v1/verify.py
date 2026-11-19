import csv
import hashlib
import json
from pathlib import Path
import re
import sys
HERE=Path(__file__).resolve().parent; ER=HERE.parents[1]; PROJECT=ER.parents[1];PLANNER=ER/'part2_scope_planner'
sys.path.insert(0,str(PLANNER));sys.path.insert(0,str(HERE))
from plan import build_plan
from plan_experimental import build_plan as experiment
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
manifest=load(HERE/'manifest.json'); assert sha(PLANNER/'plan.py')==manifest['planner_sha256_before']
reviewpath=PROJECT/manifest['source_review'];assert sha(reviewpath)==manifest['source_review_sha256']
with reviewpath.open(encoding='utf-8-sig',newline='') as f:review=list(csv.DictReader(f))
assert len(review)==24 and len(manifest['cases'])==5
assert sha(PROJECT/'variants/dnd_mem0_splitter/prompt_versions/v8_v4_v7_combined/prompt.txt')=='094d8adf71bbf623d2bdc5f43dd64cebaeb8ad0ba05b77c8d7881a28eb7c2557'
assert sha(PROJECT/'variants/dnd_mem0_splitter/prompt_versions/v9_local_update/prompt.txt')=='0e4629a707e2a6a17b1aa645f9c6b23869748f4bbd42fbea7d777a5f12e99f4e'
report=(HERE/'REPORT.md').read_text(); quote_count=0;source_count=0
for entry in manifest['cases']:
 d=HERE/'cases'/entry['case']; c=load(d/'input.json');req=c['request'];row=review[c['human_review_target_number']-1]
 assert c['review_record_id']==row['target_id'] and row['review_decision'] in ('接受','修订后接受')
 snapshot=PROJECT/c['memory_snapshot']; assert sha(snapshot)==c['snapshot_sha256'];matches=[x for x in load(snapshot)['api_snapshot']['results'] if x['id']==c['memory_id']]
 assert len(matches)==1 and matches[0]['user_id']==row['user_uuid'] and matches[0]['memory']==req['split_result']['memory_text']
 texts={'old':req['split_result']['memory_text']}
 for src in req['source_context']+req['new_evidence']:
  ref=src['source_ref'];path,fragment=ref.split('#',1);match=re.match(r'/raw_dialogue/(\d+)/content',fragment);assert match,(entry['case'],ref)
  source=load(PROJECT/path)['raw_dialogue'][int(match.group(1))]
  assert src['text'] in source['content'] and src['speaker']==source['role']=='user' and src['recorded_at']==source['timestamp']
  texts[src['source_id']]=src['text'];source_count+=1
 expected=load(d/'expected.json')
 for category in ('modify','preserve','uncertain','add'):
  assert expected[category]
  for item in expected[category]:
   assert item['scope'] in report
   for e in item['evidence']:
    assert e['source_id'] in texts and e['quote'] in texts[e['source_id']] and e['quote'] in report
    quote_count+=1
 for unit in c['manual_annotations']['old_units']+[c['manual_annotations']['new_unit']]:
  assert unit['weekdays']['kind']=='unknown' and unit['valid']['start']['kind']==unit['valid']['end']['kind']=='unknown'
 args=req,c['manual_relation_result'],c['manual_annotations'];before=build_plan(*args);after=experiment(*args)
 assert before==load(d/'output_before.json')['structured'] and after==load(d/'output_after.json')['structured']
 assert all(before[k]==after[k] for k in before) and [x['source_id'] for x in after['new_evidence_inventory']]==[x['source_id'] for x in req['new_evidence']]
 assert all(not x['independent_fact_verified'] and not x['old_fact_relation_verified'] for x in after['new_evidence_inventory'])
refined=load(HERE/'cases/susan/input_representation_refined.json'); b=load(HERE/'cases/susan/output_representation_refined.json')['original_planner']; assert b==build_plan(refined['request'],refined['manual_relation_result'],refined['manual_annotations'])
assert any(x['code']=='hold_provisional' and x['attribute']=='friend_support' for x in b['preserve'])
result={'status':'passed','review_rows_checked':len(review),'cases':len(manifest['cases']),'source_messages_traced':source_count,'expected_quotes_traced':quote_count,'original_planner_unchanged':True,'v8_v9_prompts_unchanged':True,'offline_replay_reproduced':True,'experiment_preserves_original_categories':True,'unknown_scope_asserted':True,'test_counts':{'existing_planner':37,'experiment':3},'caveat':'逐字匹配和程序复现不能证明语义；预期不是用户确认金标准。'}
with (HERE/'verification.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
