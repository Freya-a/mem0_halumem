#!/usr/bin/env python3
"""Manually prepared real-memory cases; offline, no semantic model or Mem0."""
import csv
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ER=HERE.parents[1]; PROJECT=ER.parents[1]
PLANNER=ER/'part2_scope_planner'; sys.path.insert(0,str(PLANNER))
from plan import build_plan
import relation_judge_v2

RUN=PROJECT/'results/medium_dev/williams_native_prefix5_20261028_v3/users'
PREV=PROJECT/'variants/dnd_mem0_splitter/runs/v8_five_reviewed_targets_20261118_01'
REVIEW=PROJECT/'diagnosis/medium_dev/human_review.csv'

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def evidence(source,quote): return {'source_id':source,'quote':quote}
def unit(name,attribute,subject_ref,attr_ref):
 return {'name':name,'subject':{'value':'user','evidence':[subject_ref]},'attribute':{'value':attribute,'evidence':[attr_ref]},'weekdays':{'kind':'unknown'},'valid':{'start':{'kind':'unknown'},'end':{'kind':'unknown'}}}
def text_input(user,session,index,source_id):
 p=RUN/user/f'session_{session:03d}'/'input.json'; row=load(p)['raw_dialogue'][index]
 assert row['role']=='user'
 return {'source_id':source_id,'text':row['content'],'speaker':row['role'],'recorded_at':row['timestamp'],'source_ref':str(p.relative_to(PROJECT))+f'#/raw_dialogue/{index}/content'}

def setup():
 with REVIEW.open(encoding='utf-8-sig',newline='') as f: reviewed=list(csv.DictReader(f))
 config=[
  ('susan',4,'01_susan',7,[0,2],'supplement','support_context', [('friendship','friendship','friend named ThomasSusan'),('support','friend_support','provides support and encouragement')], 1),
  ('promotion',10,'03_director',5,[0],'possible_change','job_title',[('employer','employer','Historical Productions Ltd.'),('title','job_title','Director')],0),
  ('career_history',24,'05_career_history',8,[0,2],'no_clear_impact','client_milestone',[('employer','historical_employer','Blockchain Tech'),('title','historical_title','senior developer')],0),
  ('transition',7,None,8,[0],'possible_change','transition_progress',[('job_search','transition_progress','Looking for a new job with better work-life balance')],0),
  ('skydiving',8,'02_skydiving',9,[0,2,8],'possible_change','simulated_skydiving_experience',[('attitude','extreme_sport_attitude','Dislikes extreme sports'),('risk','injury_risk_reason','high injury risk'),('safety','safety_commitment','commitment to safety and well-being')],0),
 ]
 records=[]
 for name,target,prior,session,indices,label,new_attr,parts,pick in config:
  rv=reviewed[target-1]; assert rv['review_decision'] in ('接受','修订后接受')
  user=rv['user_uuid']; before=RUN/user/f'session_{session:03d}'/'before.json'
  if prior:
   inp=load(PREV/prior/'input.json'); oldctx=deepcopy(inp['source_context'][0]); mid=inp['memory_id']; memory=inp['memory_text']
  else:
   mid='e6ab178b-c0f9-4adb-bfb7-e4648617a950'
   memory='Looking for a new job with better work-life balance'
   oldctx=text_input(user,7,0,'ctx-1')
  matches=[x for x in load(before)['api_snapshot']['results'] if x['id']==mid]
  assert len(matches)==1 and matches[0]['memory']==memory and matches[0]['user_id']==user
  new=[text_input(user,session,i,'new-'+str(i)) for i in indices]
  # The entire old memory is deliberately represented as one manual fact to isolate scope planning.
  fact={'fact_index':1,'source_memory_id':mid,'raw_subfact':memory,'contextualized_subfact':memory,'evidence':[{'source_type':'memory','source_id':mid,'quote':memory,'supports':'字面记录的旧记忆；不代表直接用户原话。'}],'pending_confirmations':[]}
  request={'split_result':{'memory_id':mid,'memory_text':memory,'facts':[fact]},'source_context':[oldctx],'new_evidence':new,'time_info':None}
  oldsubject=evidence(oldctx['source_id'],oldctx['text']); newsubject=evidence(new[pick]['source_id'],new[pick]['text'])
  oldunits=[unit(n,attr,oldsubject,evidence(mid,q)) for n,attr,q in parts]
  newunit=unit('manually_mapped_new',new_attr,newsubject,newsubject)
  annotations={'old_units':oldunits,'new_unit':newunit}
  candidate={'memory_id':mid,'fact_index':1,'old_subfact':memory,'relation':label,'object':'user','attribute':new_attr,'conditions':'unknown','candidate_impact_fragment':memory,'old_quote':memory,'new_quote':evidence(new[pick]['source_id'],new[pick]['text']),'reason':'人工整理的关系候选，只用于离线范围规划回放；不代表模型判断或人工确认金标准。','confirmation_questions':[]}
  def backend(_): return json.dumps(candidate,ensure_ascii=False)
  relation=relation_judge_v2.judge(request,backend)
  assert relation['status']=='ok',relation
  path=HERE/'cases'/name
  case={'case_id':name,'source_kind':'真实原生 Mem0 更新前快照及原用户对话；声明与关系为本次手工整理','human_review_target_number':target,'review_record_id':rv['target_id'],'review_decision':rv['review_decision'],'review_method':rv['review_method'],'memory_snapshot':str(before.relative_to(PROJECT)),'snapshot_sha256':sha(before),'memory_id':mid,'request':request,'manual_annotations':annotations,'manual_relation_candidate':candidate,'manual_relation_result':relation,'selection_limit':'此单个旧记忆并非全部旧知识；其他未输入事实不在本案判定范围。'}
  save(path/'input.json',case)
  output={'planner':'part2_scope_planner/plan.py:build_plan','upstream':'manual_candidate_validated_offline_not_model','structured':build_plan(request,relation,annotations),'baseline_only':build_plan(request,relation)}
  save(path/'output_before.json',output)
  records.append({'case':name,'target':target,'input':f'cases/{name}/input.json','output_before':f'cases/{name}/output_before.json','old_memory_id':mid,'new_sources':[x['source_id'] for x in new],'relation':label,'modify':len(output['structured']['modify']),'preserve':len(output['structured']['preserve']),'uncertain':len(output['structured']['uncertain']),'add':len(output['structured']['add'])})
 save(HERE/'manifest.json',{'created_at':datetime.now().isoformat(),'source_review':str(REVIEW.relative_to(PROJECT)),'source_review_sha256':sha(REVIEW),'planner_sha256_before':sha(PLANNER/'plan.py'),'description':'五个真实案例，所有输入中的声明切分、属性映射及关系标签由助手手工整理；非模型输出，非用户确认金标准。','cases':records})
 for r in records: print(json.dumps(r,ensure_ascii=False))
if __name__=='__main__':setup()
