#!/usr/bin/env python3
import json
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PLANNER=HERE.parents[1]/'part2_scope_planner'
sys.path.insert(0,str(PLANNER));sys.path.insert(0,str(HERE))
from plan import build_plan as original
from plan_experimental import build_plan as experimental
import relation_judge_v2

def load(p):return json.loads(p.read_text())
def save(p,x):
 with p.open('x',encoding='utf-8') as f: json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
for d in sorted((HERE/'cases').iterdir()):
 c=load(d/'input.json');args=(c['request'],c['manual_relation_result'],c['manual_annotations'])
 before=original(*args);after=experimental(*args)
 assert all(before[k]==after[k] for k in before)
 save(d/'output_after.json',{'structured':after,'baseline_only':experimental(c['request'],c['manual_relation_result'])})
 if d.name=='susan':
  refined=deepcopy(c);refined['manual_annotations']['new_unit']['attribute']['value']='friend_support'
  refined['manual_relation_candidate']['attribute']='friend_support'
  candidate=refined['manual_relation_candidate']
  refined['manual_relation_result']=relation_judge_v2.judge(refined['request'],lambda _:json.dumps(candidate,ensure_ascii=False))
  assert refined['manual_relation_result']['status']=='ok'
  refined['representation_revision']='将新支持上下文与旧支持映射为同一 friend_support 候选属性；不改变来源或推断时间；仍需人工核对该映射。'
  save(d/'input_representation_refined.json',refined)
  rargs=(refined['request'],refined['manual_relation_result'],refined['manual_annotations'])
  save(d/'output_representation_refined.json',{'original_planner':original(*rargs),'experimental_planner':experimental(*rargs)})
 print(d.name,'input sources',len(c['request']['new_evidence']),'old add sources',len({e['source_id'] for a in before['add'] for e in a['new_evidence']}),'inventory',len(after['new_evidence_inventory']))
