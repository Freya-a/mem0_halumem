import csv,json,collections,re,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent; root=P.parent; base=root/'williams_native_prefix5_20261028_v3'/'development_diagnosis_v1'; old=root/'usr_kpr_evidence_review_20261029_v1'
D={x['number']:x for x in json.loads((base/'target_decisions.json').read_text())['targets']}; E={i:json.loads((base/f'target_{i:02}_evidence.json').read_text()) for i in range(1,25)}
R=list(csv.DictReader((old/'KPR_候选索引.csv').open(encoding='utf-8-sig'))); R={r['id']:r for r in R}
counts=json.loads((old/'COUNTS.json').read_text())
primary=[1,3,4,7,8,9,10,11,12,13,14,16,17,18,19,21,22,23,24]
states={1:'成功',3:'部分',4:'部分',7:'成功',8:'待判断',9:'部分',10:'成功',11:'部分',12:'成功',13:'成功',14:'部分',16:'部分',17:'部分',18:'成功',19:'部分',21:'部分',22:'失败',23:'部分',24:'部分'}
source=lambda n:f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json'
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
rows=[]
for n in primary:
 d=D[n]; e=E[n]; note=d['verdict']['note']; u=d['verdict']['unknown']; s=states[n];human=n in (7,10,22)
 if n==8: note+=' 已有诊断为部分；但 after 将模拟体验扩展到真实极限运动，正确性与完整性如何综合计分尚待统一，列待判断。'
 if n==22: note+=' 案例 D 已用户确认新事实未找到、计划被跳过；不算旧知识损伤。'
 if n in (7,10): note+=' 用户已确认 USR 暂记成功，旧状态时间边界单列。'
 if n==14: note+=' 用户确认旧平静及优雅的处理属 KPR，不代替此处对纪录片体验的 USR 判定。'
 text='<br>'.join(f'`{k}` {esc(v)}' for k,v in d['new_related_memory'].items()) or '原诊断未定位相关新记忆；完整 after 见证据'
 rows.append({'target':n,'classification':s,'authority':'用户已确认的暂定结论' if human else '基于现有材料的初步判定，非用户确认','core':e['review']['supported_new_state'],'after':text,'note':note,'limits':u,'source':source(n)})
with (P/'USR_逐目标.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
L=['# USR 逐目标核验','', '单位：冻结审核的 19 个主目标。成功要求冻结边界内的核心新内容完整正确；部分覆盖不算成功；待判断不纳入成功或失败。7、10 为用户确认的暂定成功，22 引用案例 D 的用户确认；其余为本轮基于已有材料的初步判定，不冒充用户确认。目标 8 的超范围表述影响如何判严格成功尚未统一，暂列待判断。新旧时间关系与 KPR 分别评价。','', '|目标|冻结审核核心新内容|更新后相关记忆（原诊断选取；全量见来源）|初步判断及边界|来源|','|---|---|---|---|---|']
for r in rows:L.append(f"|{r['target']}|{esc(r['core'])}|{r['after']}|**{r['classification']}**；{r['authority']}。{esc(r['note'])}<br>限制：{esc(r['limits'])}|[完整证据]({r['source']})| ")
(P/'USR_逐目标.md').write_text('\n'.join(L)+'\n')
# Prior directly assessed records are complete candidate propositions, de-duplicated per session and fact.
facts=[]
for i,g in enumerate(counts['selected_groups'],1):
 ids=g['candidate_rows']; rr=R[ids[0]]; n=int(ids[0].split('/')[0]);facts.append({'id':f'P{i:03}','session':g['session'],'fact':g['fact'],'candidates':','.join(ids),'status':'保留','basis':'文本可直接核对；仍非用户逐项终审','before':rr['before_text'],'after':rr['after_text'],'source':source(n)})
# Additional individually checked concrete facts. The cited exact texts are verified in complete snapshots.
extra=[
('7/12','人道目标和个人健康优先于财务稳定',['Financial stability is secondary to humanitarian goals and personal well-being'],['Financial stability is secondary to humanitarian goals and personal well-being']),
('9/1','喜爱伯爵茶及历史、传统、佛手柑香气和怀旧的理由',['Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia'],['Appreciates Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia']),
('10/4,11/2','喜爱历史剧与年代片，并对科幻大片偏重视觉效果有顾虑',['Likes period pieces because','Likes historical dramas because','Dislikes science fiction blockbusters because'],['Likes period pieces because','Likes historical dramas because','Dislikes science fiction blockbusters because']),
('12/2','在 Historical Productions Ltd. 晋升 Lead Director',['Recently promoted to lead director at Historical Productions Ltd'],['Recently promoted to lead director at Historical Productions Ltd']),
('13/2','以目标和工作生活平衡维持动力',['Motivated by setting clear goals and maintaining work-life balance'],['Motivated by setting clear goals and maintaining work-life balance']),
('17/1,18/4','支持亲属政治事业是人生目标',['Life goal is to support the political career of a close relative'],['Life goal is to support the political career of a close relative']),
('17/4,18/1','Blockchain Tech 高级开发职位的经历',['Works at Blockchain Tech as a senior developer'],['Previously worked as a senior developer in Blockchain Tech']),
('18/2','技术岗位职责包含创新解决方案',['Role involves innovating new solutions and ensuring technology remains cutting-edge'],['Role involves innovating new solutions and ensuring technology remains cutting-edge']),
('21/4','支持亲属政治事业是人生目标',['Life goal is to support the political career of a close relative'],['Life goal is to support the political career of a close relative']),
('8/4','练习瑜伽以保持思维清晰和柔韧',['Practices yoga for mental clarity and flexibility'],['Practices yoga regularly for mental clarity and flexibility']),
('24/2','转型前月收入为 17,000 美元',['Monthly income was 17,000 USD before transition'],['Monthly income was 17,000 USD before transition']),
]
def find(n,phase,terms):
 dic=E[n][phase]; hits=[]
 for term in terms:
  matches=[(id,v) for id,v in dic.items() if term.casefold() in v.casefold()]
  assert matches,(n,phase,term)
  for item in matches:
   if item not in hits:hits.append(item)
 return '<br>'.join(f'`{id}` {esc(v)}' for id,v in hits)
covered={}
for ids,fact,b,a in extra:
 ids=ids.split(',');n=int(ids[0].split('/')[0]);session=E[n]['review']['session_group_id']
 for i in ids:assert E[int(i.split('/')[0])]['review']['session_group_id']==session
 facts.append({'id':f'P{len(facts)+1:03}','session':session,'fact':fact,'candidates':','.join(ids),'status':'保留','basis':'本轮明确核对限定的事实，不推及其他复合要素或精确日期','before':find(n,'before',b),'after':find(n,'after',a),'source':source(n)})
 for i in ids:covered.setdefault(i,[]).append(fact)
# User-confirmed losses. Case B elegance: stored generic elegance; home relationship not explicit in before.
losses=[
('8/2','过去回避极限运动的高受伤风险理由','e1d4f8f9-0520-427d-94fd-a2ac0ee69d03','用户确认：高受伤风险理由部分损伤；一般安全顾虑仍存。'),
('14/1','波斯猫平静性情是喜爱理由','eef34a57-c82a-4995-877d-66b54b9589da','用户确认该细节损失。'),
('14/1','波斯猫优雅是喜爱理由','eef34a57-c82a-4995-877d-66b54b9589da','用户确认高贵外观不能完整替代家中优雅感且 after 无等价表达；before 只明确 elegance，未明确“家中”，精确关系的前存资格另待确认。'),
('24/2','曾在 Blockchain Tech 担任高级开发人员','05afde13-35bd-4d26-bbae-6de427d58db1','用户确认雇主和高级职级损失；技术经历概括仍存。'),
]
for i,(id,f,mid,basis) in enumerate(losses,1):
 n=int(id.split('/')[0]);x=E[n];facts.append({'id':f'L{i:03}','session':x['review']['session_group_id'],'fact':f,'candidates':id,'status':'损伤','basis':basis,'before':f'`{mid}` '+esc(x['before'][mid]),'after':f'`{mid}` '+esc(x['after'][mid]),'source':source(n)});covered.setdefault(id,[]).append(f)
# Before-not-saved judgments rely on complete before, diagnosis, and earlier user confirmation for case D.
notstored=[('3/2','建立全球健康倡议的目标','完整 before 有改善医疗可及性、全球健康背景等，但没有明确“建立全球健康倡议”；原诊断也指出此前已被概括。','未找到该完整目标，不计本次损伤。'),('24/6','Sandra 和 Mary 在此次转型期间共同提供鼓励及策略建议','完整 before 有两人的朋友、政治观点、策略讨论和人脉，但不含此次转型期间二人的集体鼓励与建议；对应目标 22 案例 D 已用户确认新增目标未找到。','after 同样未找到该具体集体支持；不计本次损伤。')]
for i,(id,f,b,a) in enumerate(notstored,1):
 n=int(id.split('/')[0]);facts.append({'id':f'N{i:03}','session':E[n]['review']['session_group_id'],'fact':f,'candidates':id,'status':'前未明确保存','basis':'完整具体命题未明确入库；关联概括不视作完整关系。','before':b,'after':a,'source':source(n)});covered.setdefault(id,[]).append(f)
with (P/'KPR_可核对事实.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=facts[0].keys());w.writeheader();w.writerows(facts)
K=['# KPR：可核对的具体事实','', '此表的单位是同一用户、同一会话、同一具体命题；同会话的重复候选合并。跨会话分别计保护机会。P 是前后均有明确文本的保留事实，L 是用户已确认的具体损伤，N 是完整 before 没有明确保存的具体命题，不计本次损伤。保留结论为文本核对，不代表用户逐项终审。此表只是可核对的子集，不能作总体 KPR。','']
for f in facts:K += [f"## {f['id']} {f['fact']}",f"- 会话：`{f['session']}`；候选：{f['candidates']}；状态：**{f['status']}**。{f['basis']}",f"- 更新前：{f['before']}",f"- 更新后：{f['after']}",f"- [完整证据]({f['source']})",'']
(P/'KPR_可核对事实.md').write_text('\n'.join(K))
# Coverage ledger: every original primary candidate row remains visible; other 33 rows linked but excluded.
# Only complete original propositions marked completed; a subset fact does not resolve its parent candidate.
selected=set(id for g in counts['selected_groups'] for id in g['candidate_rows'])
full_add={'7/12','9/1','10/4','11/2','12/2','13/2','17/1','18/4','17/4','18/1','18/2','21/4','8/4'}
resolved_whole={'8/2','3/2','24/6'} # B/C composite still require remaining elements.
# same session, explicitly equivalent candidate-level propositions; do not force partial overlaps together
same={
 '10/3':'W-真实性与布景协作','11/1':'W-真实性与布景协作',
 '10/4':'W-电影偏好','11/2':'W-电影偏好',
 '10/5':'W-旧Director带时间历史','11/5':'W-旧Director带时间历史',
 '12/1':'W-身体健康运动饮食','13/1':'W-身体健康运动饮食',
 '12/5':'W-自我照顾及支持','13/3':'W-自我照顾及支持',
 '12/6':'W-休息与阅读传记减压','13/4':'W-休息与阅读传记减压',
 '12/7':'W-旧压力细节与日程','13/7':'W-旧压力细节与日程',
 '17/1':'D-支持亲属政治目标','18/4':'D-支持亲属政治目标',
 '17/4':'D-Blockchain高级开发经历','18/1':'D-Blockchain高级开发经历',
 '17/3':'D-技术经历和问题解决可迁移','18/3':'D-技术经历和问题解决可迁移',
 '17/7':'D-16800储蓄','18/7':'D-16800储蓄',
 '8/3':'M-瑜伽喜好及益处',
}
# Focused assessments of unresolved candidate propositions, separately from the raw locator matches.
notes={}
def mark(ids,msg):
 for i in ids.split(','): notes[i]=msg
mark('1/6,7/14,8/3','before 与 after 明确记录练瑜伽及柔韧/思维清晰作用，但未明确“喜欢”；不能把练习直接当作喜好。')
mark('3/3','before 与 after 有工作生活平衡和心理健康相关陈述；复合的个人健康诉求需明确具体关系。')
mark('4/1','before、after 均有 Susan 朋友身份和一般支持；对个人与职业健康的具体支持范围前存未明确。')
mark('4/2','before 有 Daniel 同事身份和医疗咨询专长；促使创新及职业成长等关联未完整前存，after 新增部分关联，不得计为旧损伤。')
mark('4/3','before 有 Joshua 同事身份、协作和医疗管理见解；团队效能及领导风格的完整影响关系前存未明确，after 才新增部分。')
mark('7/1','before、after 都有 Huaxin 总监的当前语句；是否是历史、转岗后雇主是否改变均未知，不能认定冲突或带时间历史完整。')
mark('7/2,7/3,7/4','before、after 有工作压力影响心理健康及考虑转职的文字；新旧时间关系未明确，且特定总监职责与心理影响的绑定程度各不相同。')
mark('7/5,7/7','before 的求职/人道目标/平衡散见多条，完整关联和此前阶段的时间标签需核对；after 不能由共存自动补全关系。')
mark('7/6','before、after 均有通过人脉获得面试和 offer；尚无精确过去时间标签，不推断已接受。')
mark('7/11','before、after 有改善医疗可及性的目标；理解全球健康倡议不等于建立倡议。建立倡议这一要素不能因本次算损伤。')
mark('7/13','多项具体宠物偏好并非一个原子事实；before 和 after 可见若干偏好，需逐个拆分且排除误匹配。')
mark('7/15','before、after 保存朋友金毛的温顺及宠物适应性；适应性是否明确归属于金毛需结合完整文本。')
mark('8/1','before 有对安全的重视；after 有 values safety，但是否表达“安全放在首位”仍待确认。')
mark('8/5','before 只明确练瑜伽，未明确一直是常规；after 写 regularly。不能将前存未明的频率算损伤。')
mark('10/3,11/1','before、after 分别有历史真实性取向和与布景人员协作，但“工作兴趣”的完整关系是否已存需核对；同会话合并。')
mark('10/5,11/5','before、after 均有 Director 当前语气；新晋升表述已存，不因 Director 一词判冲突，带时间历史是否满足仍待判断。')
mark('11/3','before、after 均有 Steven 布景专长和共同历史兴趣，但对电影真实性的具体作用未明确前存。')
mark('12/1,13/1','before、after 分别有身体健康及运动饮食；“运动饮食支持身体健康”的因果关系未明确。')
mark('12/3,12/5,13/3,13/5','before 与 after 有自我照顾及向朋友同事寻求减压支持；是否等于主要支持来源或有助平衡不可自动推断。')
mark('12/4','before、after 分别有 Mary 的情绪支持与休息鼓励和 Steven 的布景专长；Steven 对本目标的支持作用未明确前存。')
mark('12/6,13/4','before 有阅读历史传记爱好，但未明确休息与阅读传记帮助减压的完整关系；不把关系前存缺失算更新损伤。')
mark('12/7,13/7','before、after 同存电影历史准确性和紧张制作日程导致压力；是旧经历还是当前状态的时间表达尚待判断。')
mark('13/6','before、after 有父母及伴侣相关事实；候选“家庭身份”本身范围不明确，不能由没有繁重家庭负担推断身份变化。')
mark('14/1','平静和一般优雅细节已按用户确认分开记录；前存只写 elegance，原对话“为家中增添”关系并未单独写出；高贵和历史感的精确对应尚待判断。')
mark('17/2','before、after 保存创新解决方案的岗位职责；技术经历与能力及其完整关系需拆分，不能把相关游戏问题解决视为技术职业能力。')
mark('17/3,18/3','before 未定位技术经历与问题解决能力可迁移至政治咨询的明确关系；单独存在经历和能力不能当作关系前存，不能算本次损伤。')
mark('17/7,18/7','before、after 均有 16,800 美元储蓄；日期和“与收入区别”的复合边界须单独核查。')
mark('19/1','before 有当时月收入 17,000 美元，after 标为转型前；快照未保存精确 2025-09-05 日期，不应将日期前存缺失计为本次损伤。')
mark('19/2','before、after 均有储蓄金额，但没有明确 2025-09-05 历史时间；不能把快照之外的对话日期当作已存。')
mark('21/1','before、after 均有心理稳定正常的语句；新状态下旧记录作为历史如何消歧待判断，不直接判冲突。')
mark('21/3','before、after 同有政治支持的目标感和通过活动等维持健康；复合“主观益处”及时间边界需明确。')
mark('21/5','支持亲属的人生目标前后存在；是否足以表达本次职业选择的“主要动机”，需核对关联和范围。')
mark('22/1,23/1,24/4','before、after 有 Sandra 朋友身份和共同政治观点；伙伴感、鼓励与此次转型支持的具体关系未完整前存，不将缺失部分归因本次更新。')
mark('22/2,23/2,24/5','before、after 有 Mary 亲密朋友身份和政治策略讨论；具体支持作用范围和与转型的关联未完整前存。')
mark('23/3,24/7','before、after 有政治活动结识策略师 John；其独立具体见解未明确前存。')
mark('23/4','before、after 有新人脉提供新视角和资源；整理思路的作用未明确，不能因相关视角片段存在视为完整。')
mark('24/1','before 有带日期的启动句但日期来源缺充分用户确认；after 改为已创办。此前获客计划本身未明确存入，不能把未存计划算损伤。')
mark('24/2','雇主职级损伤已有确认，转型前月收入数额单列已保留；储蓄日期及其他财务历史资格仍待核验。')
mark('24/3','before、after 有对转型焦虑及旧心理稳定说法，但原候选中压力影响心理健康的完整历史关系并未明确前存。')
ledger=[]
for id,r in R.items():
 n=int(id.split('/')[0]);session=E[n]['review']['session_group_id']; group=session+' :: '+same.get(id,r['fact'])
 if r['scope']!='主目标':status='非主目标：留存追溯，不纳入工作分母'
 elif id in selected or id in full_add:status='限定候选整体可核对：前后完整保留（初步）'
 elif id in resolved_whole:status={'8/2':'既有人工确认：复合候选部分损伤','3/2':'前未明确保存完整目标；不计损伤','24/6':'前未明确保存集体支持；不计损伤'}[id]
 elif id in ('14/1','24/2'):status='部分事实已明确；其余要素及精确时间仍待判断'
 else:status='复合候选或时间／关系待判断；不得把相关片段当完整'
 ledger.append({'candidate':id,'scope':r['scope'],'session':session,'candidate_fact':r['fact'],'group':group,'status':status,'assessment':notes.get(id,''),'resolved_subfacts':'；'.join(covered.get(id,[])),'before':r['before_text'],'after':r['after_text'],'source':source(n),'old_pointer':r['pointer']})
with (P/'KPR_候选覆盖.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=ledger[0].keys());w.writeheader();w.writerows(ledger)
pend=[r for r in ledger if r['scope']=='主目标' and ('待判断' in r['status'])]
groups=collections.defaultdict(list)
for r in pend:groups[r['group']].append(r)
U=['# KPR：待判断候选与覆盖索引','',f'完整覆盖原始 176 行候选，其中 143 行属于 19 个主目标，33 行为重复确认或归并目标，详见 [CSV](KPR_候选覆盖.csv)。下列保留 {len(pend)} 个主目标候选行，按同会话、已明确等价的候选合并为 {len(groups)} 个**待核对候选组**。这是工作组数，不是唯一事实数；复合候选可以包含多个事实，与可核对事实表可能部分重叠，不可相加作总体分母。无法确定全部事实数时，总体 KPR 分母及待判断唯一事实数均记待核验。','', '每项提供完整定位器原文与目标快照链接。定位器命中可能含无关文本；“前未完整”“历史化”和“事实资格”须逐条核对。以下未标用户确认的判断均非用户终审。','']
for group,rs in groups.items():
 r=rs[0];n=int(r['candidate'].split('/')[0]);ids=', '.join(x['candidate'] for x in rs);sub='；'.join(dict.fromkeys(x['resolved_subfacts'] for x in rs if x['resolved_subfacts']))
 U += [f'## 候选 {ids}：{r["candidate_fact"]}',f'- 会话：`{r["session"]}`；{r["status"]}。'+(f' 已拆出：{sub}；未拆出的关系、时间或完整资格仍待判断。' if sub else ''),f'- 核对结果：{r["assessment"] or "尚须拆分并核对完整关系和时间。"}',f'- 前：{r["before"]}',f'- 后：{r["after"]}',f'- [完整目标证据]({r["source"]})；原对话指针 `{r["old_pointer"] or "见冻结候选"}`。','']
(P/'KPR_待判断.md').write_text('\n'.join(U))
stat={'usr':dict(collections.Counter(x['classification'] for x in rows)),'all_candidate_rows':len(ledger),'primary_candidate_rows':sum(r['scope']=='主目标' for r in ledger),'secondary_candidate_rows':sum(r['scope']!='主目标' for r in ledger),'fact_status':dict(collections.Counter(x['status'] for x in facts)),'pending_candidate_rows':len(pend),'pending_candidate_groups':len(groups),'strict_kpr_denominator':'待核验：候选复合、语义重复、前存资格和时间有效性尚未完全确定','fact_dedup_unit':'用户×会话×明确具体命题；待判断候选组不是事实数'}
(P/'COUNTS.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2)+'\n')
files=[base/'target_decisions.json',base/'protection_observations.json',old/'COUNTS.json',old/'KPR_候选索引.csv',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md',root/'human_review_packets/native_case_review_v1_20261028/review_record.json']+[base/f'target_{n:02}_evidence.json' for n in primary]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in files))
print(json.dumps(stat,ensure_ascii=False,indent=2))
