import csv,json,collections,hashlib,re
from pathlib import Path
P=Path(__file__).resolve().parent;root=P.parent;base=root/'williams_native_prefix5_20261028_v3/development_diagnosis_v1';prior=root/'usr_core_qualifiers_20261030_v1';kprior=root/'usr_kpr_reconciliation_20261030_v1'
rows=list(csv.DictReader((prior/'USR_核心限定核对.csv').open(encoding='utf-8-sig')))
for r in rows:
 n=int(r['target'])
 if n==1:r.update(classification='部分',authority='用户确认的暂定分类',assessment='金毛接触、温顺和新偏好已存；金毛与适应能力的具体关系未明确。')
 elif n==18:r.update(classification='成功',authority='用户确认的暂定分类',assessment='关键顾问角色意向足以表达直接提供建议；与过去相比更直接未明确，另作备注。冻结核心未单列为亲属竞选提供建议的独立关系。')
 elif n in [7,8,10,12]:r['authority']='用户确认的暂定分类'
 elif n==22:r['authority']='依据用户已确认的事实形成的初步分类；用户确认新事实未找到'
 else:r['authority']='依据已有材料的初步判定，非用户确认'
with (P/'USR_工作分类.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
L=['# 19 个主目标的 USR 工作分类','', '根据用户对 1、7、8、10、12、18 的暂定确认及既有证据整理；目标 22 的新事实未找到是用户已确认的事实，其严格分类仍标为据此作出的初判。其余项目为已有材料的初判，不能写成已人工确认。18 与之前的报告采用同一冻结边界；比较更直接未明确表达单列。核心程度、优先级、关系和阶段须同样检查；一般修饰词不机械要求原词。','', '|目标|工作分类|结论来源|核心和具体判断|证据|','|---|---|---|---|---|']
for r in rows:L.append(f"|{r['target']}|{r['classification']}|{r['authority']}|{esc(r['core'])}<br>{esc(r['assessment'])}|[目标证据]({r['source']})|")
(P/'USR_工作分类.md').write_text('\n'.join(L)+'\n')
c=collections.Counter(r['classification'] for r in rows);a=collections.Counter(r['authority'] for r in rows)
E={int(r['target']):json.loads((base/f'target_{int(r["target"]):02}_evidence.json').read_text()) for r in rows}
# Each batch item is an explicitly delimited proposition, not its entire composite parent.
batch=[
('4/1','Susan 是提供支持和鼓励的朋友','a1332815-d6ba-4bdc-9ffa-657f7315d0ed'),
('4/2','Daniel 是具有医疗咨询专长的同事','0da9428c-2fe6-4254-b818-58991562b49d'),
('4/3','Joshua 是擅长协作并有医疗管理见解的同事','a90e498c-4586-4237-8a4b-c830847f8819'),
('7/13','Martin 喜欢猫','f936f9b5-1dd7-4761-a22f-a3f0bdfd3678'),
('7/13','Martin 喜欢鹦鹉','5dabe140-b7bd-41a5-83c3-e2e51e0fc3f1'),
('7/13','Martin 不喜欢蛇等爬行动物','9b768fe2-b39f-42e7-b754-b881c32165a5'),
('7/13','Martin 喜欢狗尤其拉布拉多及友善忠诚等理由','d575dfc1-59ec-43b4-83c4-6b94457a83f6'),
('7/6','通过人脉获得面试与录用通知','bc4366a1-d9e6-4e96-84fe-6247e96ef3d6'),
('10/3,11/1','与布景人员合作制作年代场景','199dfd83-57fc-4c71-ba24-e78ac99fd607'),
('10/3,11/1','目标是制作历史准确的电影','f71eebcd-d556-436f-97be-a8dca4c99de9'),
('12/1,13/1','规律运动并保持均衡饮食','72acfe7a-ac52-44ec-998a-247f71f5d3a1'),
('12/1,13/1','身体健康且无慢性病','e15483c3-f7fb-4952-a8ef-23c1fcd3d2ab'),
('12/4','Mary 是提供情绪支持并鼓励休息的朋友','924d86c9-298a-4566-8e2a-d5d83f7874ae'),
('12/4','Steven 是有布景设计专长并热爱历史细节的同事','b4c92aa8-44f5-48ff-a94d-137e67f02293'),
('12/5,13/3','重视自我照顾并向朋友同事寻求支持以管理压力','bba09e85-d53e-4636-b39e-c77308301d33'),
('12/6,13/4','阅读历史传记是爱好','6a80e8a5-7007-4694-ab27-0f1581980a3a'),
('21/3','支持政治人物带来目标感和满足感','19e69d99-975a-4e8c-977a-ccfccb7a1452'),
('21/3','通过活动、工作和政治参与维护身心健康','fe76478b-2e5c-4d34-9e9c-bf81870bd39b'),
('22/1','Sandra 是朋友且有共同政治观点','37756be3-aaee-4e1c-b8f7-a5fed3d94890'),
('22/2','Mary 是讨论政治策略的亲密朋友','98c6916c-8aa9-4560-94ce-5697f39ac818'),
('23/1','Sandra 是朋友且有共同政治观点','37756be3-aaee-4e1c-b8f7-a5fed3d94890'),
('23/2','Mary 是讨论政治策略的亲密朋友','98c6916c-8aa9-4560-94ce-5697f39ac818'),
('23/3','在政治活动中认识政治策略师 John','d740c750-1802-4c13-beaa-80da0950a61f'),
('23/4','新人脉为亲属的政治竞选提供新视角和资源','ea7b33a6-5ea3-48fe-b6b4-5bd8ff5adc7f'),
('24/4','Sandra 是朋友且有共同政治观点','37756be3-aaee-4e1c-b8f7-a5fed3d94890'),
('24/5','Mary 是讨论政治策略的亲密朋友','98c6916c-8aa9-4560-94ce-5697f39ac818'),
('24/7','在政治活动中认识政治策略师 John','d740c750-1802-4c13-beaa-80da0950a61f'),
]
old=list(csv.DictReader((kprior/'KPR_可核对事实.csv').open(encoding='utf-8-sig')));old_ids=set()
for r in old:
 if r['status']=='保留':
  for mid in re.findall(r'`([0-9a-f-]{36})`',r['before']):old_ids.add((r['session'],mid))
k=[]
for ids,fact,mid in batch:
 ids=ids.split(','); n=int(ids[0].split('/')[0]);e=E[n];session=e['review']['session_group_id'];
 for candidate in ids:assert E[int(candidate.split('/')[0])]['review']['session_group_id']==session
 assert mid in e['before'] and mid in e['after'] and e['before'][mid]==e['after'][mid],(ids,mid)
 assert (session,mid) not in old_ids,(ids,'之前已计该同会话记忆',mid)
 k.append({'id':f'B{len(k)+1:02}','session':session,'fact':fact,'candidates':','.join(ids),'memory_id':mid,'before':e['before'][mid],'after':e['after'][mid],'status':'文本完整保留；事实有效性和复合候选其余要素另核验','source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json'})
assert len({(x['session'],x['memory_id'],x['fact']) for x in k})==len(k)
with (P/'KPR_新增拆分事实.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=k[0].keys());w.writeheader();w.writerows(k)
M=['# KPR 批量核对：新增可直接核对的事实','',f'基于此前 70 个限定事实，另拆出 {len(k)} 个限定事实；每行只评价明确列出的单个事实，不将复合候选其他关系、时间或原因自动视为保留。每项以原始「用户×会话×具体事实」计，同一会话内多目标候选合并，跨会话是不同保护机会。before 与 after 的同一记忆文本完全相同，仍需结合时效、候选边界和完整快照判断资格；文本存在不是用户终审。','', '|编号|会话及候选|具体事实|更新前后原文（两者相同）|证据|','|---|---|---|---|---|']
for x in k:M.append(f"|{x['id']}|`{x['session']}` / {x['candidates']}|{esc(x['fact'])}|`{x['memory_id']}` {esc(x['before'])}|[完整快照]({x['source']})|")
M+=['','边界例子：**B16** 只证明“阅读历史传记是爱好”有存；不证明“通过休息和阅读历史传记减压”的完整关系有存。Sandra、Mary 的朋友身份和讨论策略有存，不等于两人曾为转型共同提供鼓励及策略建议。John 的职业和结识记录不等于其具体见解有存。健康、运动饮食分别存有，不等于已保存因果关系。历史时间不明的内容不能从对话日期倒填。','']
(P/'KPR_新增拆分事实.md').write_text('\n'.join(M))
stats={'usr':dict(c),'usr_authorities':dict(a),'usr_user_confirmed':[int(r['target']) for r in rows if r['authority']=='用户确认的暂定分类'],'kpr_batch_additional':len(k),'old_text_retention_subfacts':70,'kpr_total_qualified_facts':'待核验','usr_scope':'19主目标，非独立会话'}
(P/'COUNTS.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
files=[prior/'USR_核心限定核对.csv',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md',kprior/'KPR_可核对事实.csv',root/'human_review_packets/native_case_review_v1_20261028/review_record.json']+[base/f'target_{int(r["target"]):02}_evidence.json' for r in rows]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in files))
print(json.dumps(stats,ensure_ascii=False,indent=2))
