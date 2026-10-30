import csv,json,collections,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;root=P.parent; old=root/'kpr_jsr_reconciliation_20261030_v1';base=root/'williams_native_prefix5_20261028_v3/development_diagnosis_v1'
f=list(csv.DictReader((old/'KPR_事实台账.csv').open(encoding='utf-8-sig'))); u=list(csv.DictReader((old/'KPR_待核候选组.csv').open(encoding='utf-8-sig'))); oldj=list(csv.DictReader((old/'JSR_逐目标.csv').open(encoding='utf-8-sig'))); oldcross=list(csv.DictReader((old/'KPR_候选映射.csv').open(encoding='utf-8-sig')))
E={n:json.loads((base/f'target_{n:02}_evidence.json').read_text()) for n in [7,10,12,17,19]}
esc=lambda t:str(t).replace('|','\\|').replace('\n','<br>')
# Historical director job is one combined employer+role fact: enrich P028, don't count U12 twice.
p28=next(x for x in f if x['id']=='P028');e=E[10];mid='e13b825e-7ec7-4760-821e-0581d8da5650';promotion='2570a550-4b52-43fc-b5c4-079261785a1a'
assert e['before'][mid]=='Works at Historical Productions Ltd. as a Director' and e['after'][mid]==e['before'][mid] and 'promoted to lead director' in e['after'][promotion].lower()
p28.update(fact='此前在 Historical Productions Ltd. 担任 Director 的岗位（雇主与职位一起计）',candidates=p28['candidates']+',10/5,11/5',before_eligibility='前存完整：旧岗位及雇主',retain_requirement='前职务作为历史保留；不能仅凭 Director 字面认为现在职级冲突',after_status='完整保留（结合时间上下文，初判）',after=f'`{mid}` {esc(e["after"][mid])}<br>`{promotion}` {esc(e["after"][promotion])}',basis='前快照是当时 Director；用户随后确认在同雇主晋升 Lead Director，after 有最近晋升及原句。上下文支持此前岗位，无需在旧句添加过去；Director也可为当前职业概括。')
# Broad filmmaker identity is not automatically a second job beside this one. Keep pending until granularity/identity distinction is fixed.
p29=next(x for x in f if x['id']=='P029');f.remove(p29)
resolved={'U06','U08','U12','U16','U20','U21'}
assert resolved <= {x['id'] for x in u}
u=[x for x in u if x['id'] not in resolved]
u.append({'id':'V01','session':p29['session'],'candidates':p29['candidates'],'claim':'电影行业就业身份与 Director 岗位的事实粒度','before_eligibility':'前存 filmmaker 及具体雇主/导演岗位；是否构成独立合格事实待判断','retain_requirement':'职业概括若为岗位同一事实的子集，不得再加一项；若按不同事实计须说明范围','after_status':'待判断','detail':'前后均有 Is a filmmaker，亦有该雇主 Director 及晋升记录；行业身份是职业类别还是同一岗位的重复归属尚未冻结。','before_locator':p29['before'],'after_locator':p29['after'],'source':p29['source']})
# Four historical propositions resolved by same-user previous snapshot plus explicit newer context.
items=[
 ('T01',7,'7/2,7/3','先前工作职责和压力影响心理健康',['58589cd3-36bc-439f-8003-d6416735b820'],['58589cd3-36bc-439f-8003-d6416735b820','63afc877-8768-4e3d-98d4-68bcb2538e65'],'前快照保存因工作要求而心理受压；后快照保留原记忆，并明确新岗位减轻前一岗位压力。历史经历按上下文保留；是否仍有同样压力未确定。'),
 ('T02',7,'7/4,7/3','此前考虑因心理健康影响而转职',['ecc0de53-fe20-4875-bfb5-e1b5ea7d6470'],['ecc0de53-fe20-4875-bfb5-e1b5ea7d6470','818912c6-02bb-44f1-8350-8ce250f1fc3e'],'前快照有因心理健康考虑转职；后快照既保留该句又有已转入新岗位。历史上的考虑可由前后上下文识别；不推断之后不可能再找工作。'),
 ('T03',12,'12/7,13/7','此前电影历史准确性要求和紧张日程带来的压力',['4ffee399-c31f-4827-b5fc-5c661baf1fc9'],['4ffee399-c31f-4827-b5fc-5c661baf1fc9','03afcc93-335c-4519-81ad-e375984ffe31','317d0abd-09eb-461b-aec9-72c31c5fc989'],'前快照明示压力及其来源；后保留原句并记录委派减压和晋升后心理改善。此前压力及原因可结合截点确认；压力降低不等于现时一定无压力。'),
 ('T04',19,'17/7,18/7,19/2,20/8,20/2','此前记录的 16,800 美元储蓄金额',['31884358-05ca-4517-bc84-2a7f5fdad0c8'],['31884358-05ca-4517-bc84-2a7f5fdad0c8','e2eeaf05-508f-435b-ba6e-a3229d3f1443'],'前快照已有储蓄金额；后仍有同额储蓄及过渡期间依靠储蓄的计划。以前曾有该数额可结合同一用户此前陈述与快照作为历史事实；不能断言此后余额始终不变，准确日期未在旧记忆中明确保存。'),
]
for id,n,candidates,claim,bids,aids,basis in items:
 e=E[n];assert all(mid in e['before'] for mid in bids) and all(mid in e['after'] for mid in aids)
 s=e['review']['session_group_id'];
 assert not any(x['session']==s and x['fact']==claim for x in f)
 f.append({'id':id,'session':s,'fact':claim,'candidates':candidates,'before_eligibility':'限定事实更新前完整（初判）','retain_requirement':'应保留历史内容；不推断当前状态','after_status':'完整保留（结合时间上下文，初判）','before':'<br>'.join(f'`{i}` {esc(e["before"][i])}' for i in bids),'after':'<br>'.join(f'`{i}` {esc(e["after"][i])}' for i in aids),'source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json','basis':basis})
# Keep N014 as absence of an explicitly stored date, and separate it from historical amount T04.
assert next(x for x in f if x['id']=='N014')['after_status'].startswith('前存缺口')
# Recompute with one consolidated protection set per shared session, including auxiliary candidates.
ret=collections.defaultdict(list);lost=collections.defaultdict(list);pre=collections.defaultdict(list);pending=collections.defaultdict(list)
for x in f:
 if x['after_status'].startswith('完整保留'):ret[x['session']].append(x['id'])
 elif x['after_status'].startswith('部分损伤'):lost[x['session']].append(x['id'])
 else:pre[x['session']].append(x['id'])
for x in u:pending[x['session']].append(x['id'])
j=[]
for x in oldj:
 s=x['session'];assert ret[s] or lost[s]
 if x['usr'] in ['部分','失败'] or lost[s]:state='失败'
 elif pending[s]:state='待判断'
 else:state='成功'
 y=dict(x);y.update(known_retained=','.join(ret[s]),confirmed_damage=','.join(lost[s]),not_preexisting=','.join(pre[s]),pending_groups=','.join(pending[s]),jsr=state,reason=('USR 工作分类不满足严格成功；已找到合格保护项。' if x['usr'] in ['部分','失败'] else ('已确认保护损伤。' if lost[s] else ('保护事实资格/关系/时间或岗位粒度仍有未决项。' if pending[s] else 'USR 成功且所有保护事项均已判完整保留。'))));j.append(y)
group=collections.defaultdict(list)
for x in j:group[x['session']].append(x)
sessions=[]
for s,rows in group.items():
 state='失败' if any(x['jsr']=='失败' for x in rows) else ('待判断' if any(x['jsr']=='待判断' for x in rows) else '成功')
 sessions.append({'session':s,'targets':','.join(x['target'] for x in rows),'jsr':state,'retained':','.join(ret[s]),'loss':','.join(lost[s]),'pending':','.join(pending[s])})
# Sensitivity: only facts explicitly associated with the evaluated target, without co-session union.
target_only=[]
for x in j:
 target=x['target']; session=x['session']
 refers=lambda row:any(c.split('/')[0]==target for c in row['candidates'].split(','))
 ok=[z for z in f if z['session']==session and z['after_status'].startswith('完整保留') and refers(z)]
 damage=[z for z in f if z['session']==session and z['after_status'].startswith('部分损伤') and refers(z)]
 undecided=[z for z in u if z['session']==session and refers(z)]
 assert ok or damage,('目标无可验证合格项',target)
 state='失败' if x['usr'] in ('部分','失败') or damage else ('待判断' if undecided else '成功')
 target_only.append({'target':target,'session':session,'usr':x['usr'],'eligible_retained':','.join(z['id'] for z in ok),'damage':','.join(z['id'] for z in damage),'pending':','.join(z['id'] for z in undecided),'jsr':state})
with (P/'JSR_仅目标候选.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=target_only[0].keys());w.writeheader();w.writerows(target_only)
# Reconcile all candidate rows; do not overwrite historical mapping.
xwalk=[]
for oldrow in oldcross:
 id=oldrow['candidate'];refs=[]
 for z in f+u:
  if id in z['candidates'].split(','):refs.append(z['id'])
 assert refs,('缺失候选',id)
 xwalk.append({'candidate':id,'session':oldrow['session'],'scope':oldrow['scope'],'claim':oldrow['claim'],'new_references':','.join(dict.fromkeys(refs)),'source':oldrow['source']})
for filename,rows in [('KPR_事实台账.csv',f),('KPR_待核候选组.csv',u),('KPR_候选映射.csv',xwalk),('JSR_逐目标.csv',j),('JSR_逐会话.csv',sessions)]:
 with (P/filename).open('w',encoding='utf-8-sig',newline='') as h:
  w=csv.DictWriter(h,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
K=['# KPR 事实机会台账：时间与岗位口径更新','', '按用户确认，允许结合同用户及对应截点的上下文识别历史；仍不明确的时间归属不强判。岗位主统计按雇主和职级合为一项岗位事实；其他职业类别与岗位是否重复单列 V01。已判保留是限定事实的初判，待判断组不得加进已判分母。','']
for x in f:K += [f"## {x['id']} {x['fact']}",f"- 会话：`{x['session']}`；原候选：{x['candidates']}；前：{x['before_eligibility']}；应保留：{x['retain_requirement']}；后：**{x['after_status']}**。",f"- 前证据：{x['before']}",f"- 后证据：{x['after']}",f"- {x['basis']} [完整证据]({x['source']})",'']
(P/'KPR_事实台账.md').write_text('\n'.join(K))
U=['# KPR 待核候选组：新口径','', '以下为尚未完全拆定或时间、资格及岗位粒度不明的候选组，并非待判断唯一事实总数。不能把组数与事实数相加。','']
for x in u:U += [f"## {x['id']} / {x['candidates']}：{x['claim']}",f"- 会话：`{x['session']}`；更新前：{x['before_eligibility']}；保留要求：{x['retain_requirement']}；更新后：{x['after_status']}。",f"- 说明：{x['detail']}",f"- 前定位：{x['before_locator']}",f"- 后定位：{x['after_locator']}",f"- [完整证据]({x['source']})",'']
(P/'KPR_待核候选组.md').write_text('\n'.join(U))
J=['# JSR 逐目标：时间与岗位口径更新','', '19 个主目标为主口径；各目标保护集为该会话所有冻结候选并集。USR 未完整或确定保护损伤足以判联合失败；USR 成功但仍有未决保护事项则待判断。19 个目标均找到至少一个暂定合格保护事实；保护前存缺口不计损伤。','', '|目标|会话／共享目标|USR 与来源|已保留 / 损伤 / 前存缺口 / 待核组|JSR|依据|','|---|---|---|---|---|---|']
for x in j:J.append(f"|[{x['target']}]({x['source']})|`{x['session']}` / {x['session_targets']}|{x['usr']}；{x['usr_authority']}|{x['known_retained'] or '—'} / {x['confirmed_damage'] or '—'} / {x['not_preexisting'] or '—'} / {x['pending_groups'] or '—'}|**{x['jsr']}**|{x['reason']}|")
J+=['','按 15 个主目标会话去重的工作结果见 [逐会话 CSV](JSR_逐会话.csv)；两种单位不得相加。[仅按目标自身候选的敏感性表](JSR_仅目标候选.csv)使用不同保护集合，可与主口径比较，但不能混加。',''];(P/'JSR_逐目标.md').write_text('\n'.join(J))
status=collections.Counter(x['after_status'] for x in f);counts={'kpr_retained':sum(v for k,v in status.items() if k.startswith('完整保留')),'kpr_user_confirmed_damaged':status['部分损伤（用户已确认）'],'kpr_before_incomplete':status['前存缺口；不记更新损伤'],'pending_candidate_groups':len(u),'pending_unique_facts':'待核验','jsr_target':dict(collections.Counter(x['jsr'] for x in j)),'jsr_session':dict(collections.Counter(x['jsr'] for x in sessions)),'jsr_target_only':dict(collections.Counter(x['jsr'] for x in target_only)),'eligible_target_count':sum(bool(ret[x['session']] or lost[x['session']]) for x in j),'primary_targets':len(j),'primary_sessions':len(sessions),'candidate_rows':len(xwalk)}
(P/'COUNTS.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n')
sources=[old/'KPR_事实台账.csv',old/'KPR_待核候选组.csv',old/'KPR_候选映射.csv',old/'JSR_逐目标.csv',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md']+[base/f'target_{n:02}_evidence.json' for n in range(1,25)]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+str(x.relative_to(root))+'\n' for x in sources))
print(json.dumps(counts,ensure_ascii=False,indent=2))
