import json,csv,collections,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;root=P.parent;old=root/'kpr_jsr_temporal_policy_20261030_v1';base=root/'williams_native_prefix5_20261028_v3/development_diagnosis_v1';run=base.parent
facts=list(csv.DictReader((old/'KPR_事实台账.csv').open(encoding='utf-8-sig')));pending={x['id']:x for x in csv.DictReader((old/'KPR_待核候选组.csv').open(encoding='utf-8-sig'))};cross=list(csv.DictReader((old/'KPR_候选映射.csv').open(encoding='utf-8-sig')));oldj=list(csv.DictReader((old/'JSR_逐目标.csv').open(encoding='utf-8-sig')))
case_groups={7:[7],10:[10,11],13:[12,13],18:[17,18,19,20]};representative={7:7,10:10,13:12,18:17}
E={n:json.loads((base/f'target_{n:02}_evidence.json').read_text()) for n in range(1,25)}
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
S={}
for target,rep in representative.items():
 d=E[rep];session=d['review']['session_group_id'];b=d['before'];a=d['after'];sid=int(d['original_target']['original_session_index_zero_based'])+1;user=d['review']['user_uuid'];sessiondir=run/'users'/user/f'session_{sid:03}'
 for phase in ['before','after']:
  z=json.loads((sessiondir/f'{phase}.json').read_text());snap={x['id']:x['memory'] for x in z['api_snapshot']['results']};assert z['not_truncated'] and snap==d[phase]
 for n in case_groups[target]:assert E[n]['review']['session_group_id']==session and E[n]['before']==b and E[n]['after']==a
 removed=[i for i in b if i not in a];changed={i:(b[i],a[i]) for i in b if i in a and b[i]!=a[i]};added={i:v for i,v in a.items() if i not in b};assert not removed
 S[target]={'session':session,'before_count':len(b),'after_count':len(a),'same_count':len(b)-len(changed),'removed':removed,'changed':changed,'added':added,'snapshot_dir':str(sessiondir.relative_to(P.parent))}
assert not S[10]['changed'] and not S[13]['changed']
assert set(S[7]['changed'])=={'845853d3-9c8f-4075-828c-206f4a2531cc','88e4fcd9-0719-4f3c-bb36-a14bed591477','e9823d6d-9441-4fc8-b19c-95a76a730dde'}
assert set(S[18]['changed'])=={'05afde13-35bd-4d26-bbae-6de427d58db1','31884358-05ca-4517-bc84-2a7f5fdad0c8','46374680-0009-4625-a3a7-f2b4e329a7b5','aca2b85d-8856-4989-bfdd-b032fde1bda3','f4549cf1-dc0e-4ba5-8ea4-e126d97c20d3'}
# Outcomes are scoped to each candidate proposition. Precondition uncertainty is not JSR uncertainty
# when every possible supporting pre-snapshot statement is retained and not contradicted after.
D={
'U05':('前存完整：旧 Director/Huaxin 岗位；新岗位雇主未知。','历史岗位应保留，不把旧雇主强指定为新雇主。','相同旧句仍在，结合旧快照及后来的转岗可表达此前岗位；是否仍任职未知，未见明确冲突。','保留（历史上下文）',['13a9a169-1fbc-4b0c-976d-b0d21209526d'],['13a9a169-1fbc-4b0c-976d-b0d21209526d','818912c6-02bb-44f1-8350-8ce250f1fc3e']),
'U07':('before 有当前 Huaxin 总监和当前工作心理压力及转职考虑；结合同时期角色上下文可识别。','既有压力及此前考虑作为历史保留，不假定当前职位。','相关旧句均原文保留，新增明确前一岗位压力；同一历史信息可以结合上下文读取。','保留（历史上下文；与 T01/T02 重叠）',['13a9a169-1fbc-4b0c-976d-b0d21209526d','d89a12f2-be5e-49dc-b30c-0a8c65984ab9'],['13a9a169-1fbc-4b0c-976d-b0d21209526d','d89a12f2-be5e-49dc-b30c-0a8c65984ab9','63afc877-8768-4e3d-98d4-68bcb2538e65']),
'U09':('before 有找平衡新工作、人道职业目标和兼顾医疗倡议及生活平衡的理想岗位；完整关联是否等价可争议。','已保存的求职、职业目标及其关系应按当时历史保留。','相关旧句逐字保留，新增转岗并未撤销过去目标；即使把该组合认作合格关系，也没有相应旧信息损伤。','条件保留：前存资格不改变 JSR',['e6ab178b-c0f9-4adb-bfb7-e4648617a950','a07bd4a7-257f-4dab-b7e2-224841cb4746','1fd1c83f-6203-4e36-aa42-4009909da526'],['e6ab178b-c0f9-4adb-bfb7-e4648617a950','a07bd4a7-257f-4dab-b7e2-224841cb4746','1fd1c83f-6203-4e36-aa42-4009909da526','818912c6-02bb-44f1-8350-8ce250f1fc3e']),
'U10':('before 有理想岗位兼顾医疗倡议与平衡生活、找更平衡工作；是否完整表达“职业目标及个人健康”的关联可争议。','已存的理想岗位和求职诉求按旧阶段保留。','上述旧句均未改写；即使认为前存资格成立，after 的可用旧信息仍在。','条件保留：前存资格不改变 JSR',['a07bd4a7-257f-4dab-b7e2-224841cb4746','e6ab178b-c0f9-4adb-bfb7-e4648617a950','eb152c7d-17df-4b3a-8a99-9f6211614e2a'],['a07bd4a7-257f-4dab-b7e2-224841cb4746','e6ab178b-c0f9-4adb-bfb7-e4648617a950','eb152c7d-17df-4b3a-8a99-9f6211614e2a']),
'U11':('before 保存与布景人员合作及制作历史准确电影的目标；对合作感到自豪这一细节未明确前存。','已存协作与真实性取向应保留；前未存的自豪感不计损伤。','两条相关旧记忆原文保留；是否把两项作为一个复合兴趣，不改变已存信息保留。','保留已存事实；主观细节前存未明确',['199dfd83-57fc-4c71-ba24-e78ac99fd607','f71eebcd-d556-436f-97be-a8dca4c99de9'],['199dfd83-57fc-4c71-ba24-e78ac99fd607','f71eebcd-d556-436f-97be-a8dca4c99de9']),
'V01':('before 完整保存 filmmaker 身份及 Director 岗位。','二者无论分开计或合并为职业/岗位概括，均应保留已有内容。','两条旧句原文保留，新增 Lead Director 可与 filmmaker 并存；计数粒度不影响 JSR。','保留；KPR 独立计数口径未定',['e6112994-45c2-43d2-86d8-7c8d978f690e','e13b825e-7ec7-4760-821e-0581d8da5650'],['e6112994-45c2-43d2-86d8-7c8d978f690e','e13b825e-7ec7-4760-821e-0581d8da5650','2570a550-4b52-43fc-b5c4-079261785a1a']),
'U13':('before 保存向朋友同事寻求支持管理压力及 Mary 的朋友/情绪支持；一般支持是否足以证明全部同事支持可争议。','已存支持和寻求支持内容应保留。','原句与 Mary 友人支持均原样保留，还新增朋友同事为主要支持来源；前资格争议不构成损伤。','保留已存事实；超出前存部分不计损伤',['bba09e85-d53e-4636-b39e-c77308301d33','924d86c9-298a-4566-8e2a-d5d83f7874ae'],['bba09e85-d53e-4636-b39e-c77308301d33','924d86c9-298a-4566-8e2a-d5d83f7874ae','e76eedc7-87e9-4282-b7db-68ed72b0c8ba']),
'U14':('before 有 Mary 的朋友、情绪支持及鼓励休息，有 Steven 同事/布景专长；Steven 具体支持作用未明确前存。','分别保留已存身份与 Mary 的支持；不可把前未存的 Steven 具体支持计损伤。','两条旧记忆原样保留，新增两人支持；新增句称 Mary 为同事但旧友人身份仍在，两种身份未证明互斥。','保留已存事实；未明确前存的支持不计损伤',['924d86c9-298a-4566-8e2a-d5d83f7874ae','b4c92aa8-44f5-48ff-a94d-137e67f02293'],['924d86c9-298a-4566-8e2a-d5d83f7874ae','b4c92aa8-44f5-48ff-a94d-137e67f02293','d7d27de9-fc3f-4dfc-9cc5-32bb46446d21']),
'U15':('before 保存自我照顾及寻求支持来管理压力；是否明确等于维持平衡可争议。','已保存的自我照顾和支持关系应保留。','相同旧句原文保留；不需要把管理压力推断成完整的平衡关系，前资格争议不改变保护结果。','条件保留：前存资格不改变 JSR',['bba09e85-d53e-4636-b39e-c77308301d33'],['bba09e85-d53e-4636-b39e-c77308301d33']),
'U17':('before 保存父母健在及伴侣资料；用户本人婚姻与无子女未被这两条清楚完整表达，父母已婚的归属亦不能倒推。','保留已存且有依据的家庭事实；前未明确保存内容不作为损伤。','父母、伴侣旧句都原文保留；“无需平衡繁重家庭生活”不否定有伴侣或父母。','保留已存身份；本人婚姻/无子女前存不足',['322dffcf-4884-43fa-a185-718600a36cdc','a0890e00-0564-4490-8e5b-15b02025e910'],['322dffcf-4884-43fa-a185-718600a36cdc','a0890e00-0564-4490-8e5b-15b02025e910','4fc05270-e53d-4b0a-ac6e-459e7a0677fe']),
'U19':('before 保存 Blockchain Tech 高级开发岗位及角色包含创新技术解决方案。','历史技术岗位和已存创新职责应保留；能力迁移到政治咨询的完整关系未明确前存。','职位改成此前在 Blockchain Tech 任高级开发；创新职责句原文保留。不能由新数据分析句倒推出旧迁移关系。','保留已存岗位与职责；迁移关系前存不足',['05afde13-35bd-4d26-bbae-6de427d58db1','2b65ace7-5f31-4cb5-9582-8b8a1d99dd2b'],['05afde13-35bd-4d26-bbae-6de427d58db1','2b65ace7-5f31-4cb5-9582-8b8a1d99dd2b']),
'U37':('before 分别保存 17,000 美元月收入、16,800 美元储蓄和经常政治捐助；未明确保存储蓄有限由捐助造成的因果。','收入与储蓄分别作为历史保留、捐助按存量保留；前存没有的因果不算损伤。','收入改为转型前，储蓄数额和捐助仍在；不将同一数额推断为永久当前余额。','保留已存事实；因果和精确日期前存不足',['46374680-0009-4625-a3a7-f2b4e329a7b5','31884358-05ca-4517-bc84-2a7f5fdad0c8','58c2e1c2-74b6-4c5b-ab38-433b8e2b7cf2'],['46374680-0009-4625-a3a7-f2b4e329a7b5','31884358-05ca-4517-bc84-2a7f5fdad0c8','58c2e1c2-74b6-4c5b-ab38-433b8e2b7cf2']),
}
# 12 unresolved groups are fully evaluated for JSR; source scope avoids automatically counting omitted pre-existing facts.
case_resolved=[]
for target in [7,10,13,18]:
 row=next(x for x in oldj if int(x['target'])==target); ids=row['pending_groups'].split(',');assert all(i in D for i in ids)
 rep=representative[target];d=E[rep]
 for id in ids:
  q=pending[id];pre,retain,post,status,bids,aids=D[id];assert all(i in d['before'] for i in bids) and all(i in d['after'] for i in aids)
  case_resolved.append({'target':target,'group':id,'candidates':q['candidates'],'claim':q['claim'],'before_qualification':pre,'retain_rule':retain,'after_result':post,'verdict':status,'before_evidence':'<br>'.join(f'`{i}` {esc(d["before"][i])}' for i in bids),'after_evidence':'<br>'.join(f'`{i}` {esc(d["after"][i])}' for i in aids),'source':q['source']})
assert len(case_resolved)==12
with (P/'四会话_逐组复核.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=case_resolved[0].keys());w.writeheader();w.writerows(case_resolved)
# Preserve all 73 original candidate references; U/V IDs now point to explicit resolution, not still-pending status.
selected={n for ns in case_groups.values() for n in ns};coverage=[r for r in cross if int(r['candidate'].split('/')[0]) in selected];assert len(coverage)==73
for r in coverage:r['jsr_group_resolution']='；'.join(f'{z}: {D[z][3]}' for z in r['new_references'].split(',') if z in D) or '既有事实/前存资格结论，见会话事实表'
with (P/'四会话_原候选映射.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=coverage[0].keys());w.writeheader();w.writerows(coverage)
# Case facts are grouped using previously deduplicated fact IDs; unresolved composite groups are explanatory,
# not additional independent facts. Prior N items are excluded from protected denominator.
allrows=[]
for target in [7,10,13,18]:
 session=S[target]['session']; session_facts=[x for x in facts if x['session']==session];
 for x in session_facts:
  allrows.append({'target':target,'record':x['id'],'candidates':x['candidates'],'fact':x['fact'],'before':x['before_eligibility'],'retain':x['retain_requirement'],'after':x['after_status'],'before_evidence':x['before'],'after_evidence':x['after'],'source':x['source']})
 for x in [q for q in case_resolved if q['target']==target]:allrows.append({'target':target,'record':x['group'],'candidates':x['candidates'],'fact':x['claim']+'（复合候选，不增加独立事实）','before':x['before_qualification'],'retain':x['retain_rule'],'after':x['verdict']+'：'+x['after_result'],'before_evidence':x['before_evidence'],'after_evidence':x['after_evidence'],'source':x['source']})
with (P/'四会话_保护事实.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=allrows[0].keys());w.writeheader();w.writerows(allrows)
# 19 main targets, single union-of-session-protections JSR scope.
j=[]
for x in oldj:
 y=dict(x);n=int(y['target'])
 if n in case_groups:
  assert y['usr']=='成功' and not y['confirmed_damage']
  y['jsr']='成功';y['pending_groups']='';y['reason']='本轮完整快照和同会话候选并集核对：已存且仍应保留的内容均保留；前存资格不清的组合即使视作合格，其原支持语句也保留且无明确冲突。'
 y['joint_authority']='依据既有材料的本轮初判，未经用户逐项确认' if n in case_groups else ('依据用户确认的 USR 暂定分类及保护资格作出的联合初判' if n in [1,8,12] else '沿用既有材料的联合初判；不是用户终审')
 j.append(y)
with (P/'JSR_19主目标.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=j[0].keys());w.writeheader();w.writerows(j)
L=['# 四个会话的保护事实核验','', '每个会话合并所有冻结候选，包括同会话的重复确认/归并目标；既有 P/B/R/T 为不重复的已拆事实，N 为前未明确完整保存的内容。U/V 是复合候选核验条目，会引用已列子事实而不再新增计数。这里的“保留”是在相应截点结合上下文的初判，不证明下游检索或问答成功。','']
for target in [7,10,13,18]:
 s=S[target];rep=representative[target];d=E[rep];L += [f'## 目标 {target}：同会话目标 {", ".join(map(str,case_groups[target]))}',f'- USR 暂定成功；JSR **暂定成功（本轮基于既有材料的初判，非用户确认）**。before {s["before_count"]} 条，after {s["after_count"]} 条；{s["same_count"]} 条旧记忆原文相同，{len(s["changed"])} 条改写，删除 {len(s["removed"])} 条。',f'- [逐目标证据](../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{rep:02}_evidence.json)；[完整 before](../{s["snapshot_dir"]}/before.json)；[完整 after](../{s["snapshot_dir"]}/after.json)。','', '|已合并事实或候选组|原候选|更新前完整性|仍应保留|更新后|证据|','|---|---|---|---|---|---|']
 for x in [r for r in allrows if r['target']==target]:
  L.append(f"|{x['record']} {esc(x['fact'])}|{x['candidates']}|{esc(x['before'])}|{esc(x['retain'])}|{esc(x['after'])}|[快照]({x['source']})<br>前：{x['before_evidence']}<br>后：{x['after_evidence']}|")
 L+=['','### 完整快照中被改写的旧记忆','']
 if not s['changed']:L+=['全部旧记忆原文相同；新增信息与所列旧保护内容未见明确冲突。','']
 else:
  for mid,(b,a) in s['changed'].items():L += [f'- `{mid}`：{esc(b)} → {esc(a)}']
  if target==7:L+=['','Daniel 的具体见解和 Susan 的鼓励语句不属于目标 7 冻结保护候选并集；本次不把未列入候选的潜在细节变化自动纳入该口径的 JSR。医疗行业与医疗领域工作为同义概括。','']
  if target==18:L+=['','转型后旧岗位以过去式保留，旧工资标为转型前，储蓄数额保持；转型本身不证明是否仍兼有技术工作。新数据分析句把计划写成使用的风险属于关联方法计划的新状态核验，不因相关词出现便视为已存旧知识损伤。','']
(P/'四会话_保护事实.md').write_text('\n'.join(L))
J=['# JSR：19 个主目标','', '只使用每个目标所在会话的全部冻结保护候选并集，不混用目标自身候选口径。USR 部分/失败为联合失败；USR 暂定成功且所有合格保护事实保留、或对前存资格有争议但其可能支持信息在 after 原样保留且无明确冲突时，依据已有材料初判联合成功。所有本轮联合判断均非用户逐项确认；新内容 USR 的用户确认与 JSR 初判分别标识。','', '|目标|会话/共享目标|USR 与来源|JSR 工作分类|联合结论来源与依据|','|---|---|---|---|---|']
for x in j:J.append(f"|[{x['target']}]({x['source']})|`{x['session']}` / {x['session_targets']}|{x['usr']}；{x['usr_authority']}|**{x['jsr']}**|{x['joint_authority']}。{esc(x['reason'])}|")
(P/'JSR_19主目标.md').write_text('\n'.join(J)+'\n')
counts=collections.Counter(x['jsr'] for x in j);assert counts=={'成功':4,'失败':15};assert len(j)==19
stat={'jsr':dict(counts),'main_targets':len(j),'adjudicated':len(j),'unresolved':sum(x['jsr']=='待判断' for x in j),'joint_success_ids':[int(x['target']) for x in j if x['jsr']=='成功'],'four_case_candidate_rows':len(coverage),'resolved_groups':len(case_resolved),'joint_verdicts':'全部为依据现有材料的暂定联合初判；用户已确认的新状态按原来源区分','scope':'同一目标所在会话的冻结保护候选并集'}
(P/'COUNTS.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2)+'\n')
# Hash original diagnostic/snapshot and frozen reviews used here.
paths=[old/'KPR_事实台账.csv',old/'KPR_待核候选组.csv',old/'KPR_候选映射.csv',old/'JSR_逐目标.csv',old/'POLICY.md',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md']
for n in selected:paths.append(base/f'target_{n:02}_evidence.json')
for t in [7,10,13,18]:
 d=E[representative[t]];directory=run/'users'/d['review']['user_uuid']/f"session_{int(d['original_target']['original_session_index_zero_based'])+1:03}"
 paths.extend([directory/'before.json',directory/'after.json',directory/'input.json'])
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+str(x.relative_to(root))+'\n' for x in sorted(paths)))
print(json.dumps({'counts':stat,'snapshots':{str(k):{'before':v['before_count'],'after':v['after_count'],'same':v['same_count'],'changed':len(v['changed'])} for k,v in S.items()}},ensure_ascii=False,indent=2))
