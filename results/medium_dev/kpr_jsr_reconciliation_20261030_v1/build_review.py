import json,csv,re,collections,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent; root=P.parent; orig=root/'williams_native_prefix5_20261028_v3'/'development_diagnosis_v1'; old=root/'usr_kpr_reconciliation_20261030_v1'; recent=root/'usr_kpr_working_update_20261030_v1'
usr=list(csv.DictReader((recent/'USR_工作分类.csv').open(encoding='utf-8-sig'))); E={n:json.loads((orig/f'target_{n:02}_evidence.json').read_text()) for n in range(1,25)}
a=list(csv.DictReader((old/'KPR_可核对事实.csv').open(encoding='utf-8-sig')));b=list(csv.DictReader((recent/'KPR_新增拆分事实.csv').open(encoding='utf-8-sig')));candidate=list(csv.DictReader((old/'KPR_候选覆盖.csv').open(encoding='utf-8-sig')))
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
facts=[]
for r in a:
 if r['status']=='保留':facts.append({'id':r['id'],'session':r['session'],'fact':r['fact'],'candidates':r['candidates'],'before_eligibility':'限定具体命题前存完整（初判）','retain_requirement':'本会话未见明确撤销；暂定应保留该限定内容','after_status':'完整保留（文本证据、初判）','before':r['before'],'after':r['after'],'source':r['source'],'basis':r['basis']})
for r in b:facts.append({'id':r['id'],'session':r['session'],'fact':r['fact'],'candidates':r['candidates'],'before_eligibility':'限定具体命题前存完整（初判）','retain_requirement':'本会话未见明确撤销；暂定应保留该限定内容','after_status':'完整保留（文本证据、初判）','before':f'`{r["memory_id"]}` {esc(r["before"])}','after':f'`{r["memory_id"]}` {esc(r["after"])}','source':r['source'],'basis':'同一记忆的前后全文一致；仅评所列事实，不扩展为复合候选完整。'})
# Cross-batch overlap audited by same session+memory IDs and separate manual semantic review per session.
index=collections.defaultdict(list)
for r in facts:
 for mid in re.findall(r'`([0-9a-f-]{36})`',r['before']):index[(r['session'],mid)].append(r['id'])
collisions={k:v for k,v in index.items() if len(v)>1};assert not collisions,collisions
assert len(facts)==97 and len({(r['session'],r['fact']) for r in facts})==97
# Four additional explicitly delimited retained facts identified while resolving compound groups.
extra=[('7/15','曾与朋友的金毛互动并欣赏其温顺','aa764342-2fe6-4632-9efd-e5e0cc032185'),('7/11','改善服务不足社区的医疗可及性是职业动机','b79a25de-05b7-47b7-bb0b-8c59b44a61ec'),('13/6','父母健在','322dffcf-4884-43fa-a185-718600a36cdc'),('13/6','有从事历史文物工作的伴侣','a0890e00-0564-4490-8e5b-15b02025e910')]
for id,f,mid in extra:
 n=int(id.split('/')[0]);e=E[n];session=e['review']['session_group_id'];assert mid in e['before'] and mid in e['after'] and e['before'][mid]==e['after'][mid],(id,mid);assert (session,mid) not in index,(id,mid)
 facts.append({'id':f'R{len([x for x in facts if x["id"].startswith("R")])+1:02}','session':session,'fact':f,'candidates':id,'before_eligibility':'限定具体命题前存完整（初判）','retain_requirement':'本会话未见明确撤销；暂定应保留该限定内容','after_status':'完整保留（文本证据、初判）','before':f'`{mid}` {esc(e["before"][mid])}','after':f'`{mid}` {esc(e["after"][mid])}','source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json','basis':'拆自复合候选；不推及尚未明确的其他关系或时间。'});index[(session,mid)].append(facts[-1]['id'])
# Income fact and source-date qualifier are separated; the old amount is historicalized rather than kept current.
e=E[19];mid='46374680-0009-4625-a3a7-f2b4e329a7b5';session=e['review']['session_group_id'];assert e['before'][mid]=='Monthly income is 17000 USD' and e['after'][mid]=='Monthly income was 17,000 USD before transition';assert (session,mid) not in index
facts.append({'id':'R05','session':session,'fact':'转型前月收入为 17,000 美元','candidates':'19/1','before_eligibility':'数额和月收入关系前存完整（初判）','retain_requirement':'转型后作为历史而非当前收入保留','after_status':'完整保留（文本证据、初判）','before':f'`{mid}` '+esc(e['before'][mid]),'after':f'`{mid}` '+esc(e['after'][mid]),'source':'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_19_evidence.json','basis':'after 明确历史化到转型前；2025-09-05 是用户陈述日期，未被前存记忆显式绑定，另见 N013。'})
index[(session,mid)].append('R05')
# Non-primary protections are included in KPR. Target 15 is a separate session with no primary USR target.
secondary=[
 ('20/2','经常为政治活动和事业提供经济支持',['58c2e1c2-74b6-4c5b-ab38-433b8e2b7cf2']),
 ('15/1','Mary 是提供情绪支持并鼓励休息的朋友',['924d86c9-298a-4566-8e2a-d5d83f7874ae']),
 ('15/2','Steven 是有布景设计专长并热爱历史细节的同事',['b4c92aa8-44f5-48ff-a94d-137e67f02293']),
 ('15/4','最高学历 Bachelor，专业 Film Studies',['1fd623c5-30e6-4b18-8b4e-2969cb10aab2','7a85fc34-7cea-4f18-9a00-c03c7ec689c4']),
 ('15/5','父亲是退休历史教授',['0682fdb0-5fc9-40a0-9913-6396cab3b675']),
 ('15/6','喜欢 1920 年代爵士乐及其历史文化意义',['38d07cc6-7e8e-4e05-a5aa-646dc7b7aa19']),
]
for j,(id,f,mids) in enumerate(secondary,6):
 n=int(id.split('/')[0]);e=E[n];session=e['review']['session_group_id']
 for mid in mids:assert mid in e['before'] and mid in e['after'] and e['before'][mid]==e['after'][mid] and (session,mid) not in index,(id,mid)
 facts.append({'id':f'R{j:02}','session':session,'fact':f,'candidates':id,'before_eligibility':'限定具体命题前存完整（初判）','retain_requirement':'本会话未见明确撤销；暂定应保留该限定内容','after_status':'完整保留（文本证据、初判）','before':'<br>'.join(f'`{mid}` '+esc(e['before'][mid]) for mid in mids),'after':'<br>'.join(f'`{mid}` '+esc(e['after'][mid]) for mid in mids),'source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json','basis':'来自重复确认或归并目标的保护候选；只评具体命题，不增加主 USR 目标。'})
 for mid in mids:index[(session,mid)].append(facts[-1]['id'])
# Yoga practice/benefits are saved; liking yoga is a distinct proposition absent from the earlier snapshots.
for j,id in enumerate(['1/6','7/14'],12):
 n=int(id.split('/')[0]);e=E[n];mid='04d538a9-5ea1-4364-a5f0-47a108ead2a6';session=e['review']['session_group_id'];assert mid in e['before'] and e['before'][mid]==e['after'][mid] and (session,mid) not in index
 facts.append({'id':f'R{j:02}','session':session,'fact':'练习瑜伽以保持柔韧性和思维清晰','candidates':id,'before_eligibility':'限定具体命题前存完整（初判）','retain_requirement':'本会话未见明确撤销；暂定应保留','after_status':'完整保留（文本证据、初判）','before':f'`{mid}` '+esc(e['before'][mid]),'after':f'`{mid}` '+esc(e['after'][mid]),'source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json','basis':'仅记录练习及作用；不能由此推断喜欢瑜伽。'})
 index[(session,mid)].append(facts[-1]['id'])
# Preserve confirmed A/B calm/C; previous L003 is NOT automatically a loss for the unstored house relation.
for r in a:
 if r['id'] in ['L001','L002','L004']:
  facts.append({'id':r['id'],'session':r['session'],'fact':r['fact'],'candidates':r['candidates'],'before_eligibility':'完整前存（用户复核）','retain_requirement':'未被新会话否定，应按历史或原偏好保留','after_status':'部分损伤（用户已确认）','before':r['before'],'after':r['after'],'source':r['source'],'basis':r['basis']})
 if r['id'] in ['N001','N002']:
  facts.append({'id':r['id'],'session':r['session'],'fact':r['fact'],'candidates':r['candidates'],'before_eligibility':'前未明确完整保存','retain_requirement':'不作为本次旧存量保护分母；不认定该事实现实中不存在','after_status':'前存缺口；不记更新损伤','before':r['before'],'after':r['after'],'source':r['source'],'basis':r['basis']})
# Additional pre-update missing relations. Exact scope and why the subfact is missing are stated.
missing=[
 ('7/15','这只金毛的适应能力','前存仅记金毛温顺及一般宠物适应性，用户对同一表述已确认并非明确绑定金毛。','after仍未明确把适应性归于金毛；其温顺已作为 R01 保留。'),
 ('7/11','建立全球健康倡议的目标','before 保存改善医疗可及性的目标和了解全球倡议，未明确保存建立全球健康倡议。','after 不能用相关可及性目标替代建立倡议；R02 单列可及性动机。'),
 ('8/1','安全处于首要优先级','before 记载高受伤风险与重视安全，未明确保存安全排首位。','after 保存 values safety，用户已确认不足以明确安全排首位；这是新的 USR 部分覆盖，非原本前存优先级的损伤。'),
 ('8/5','瑜伽一直是常规活动','before 明确有瑜伽练习，但没有明确一直或规律频率。','after 写 regularly；不以先前未明确的频率作为损伤。'),
 ('11/3','Steven 的布景专长对电影真实性的具体作用','before 有 Steven 同事身份、布景专长、共同历史兴趣，未明确其专长对电影真实性产生的具体作用。','after 保留该同事资料；不能以一般专长替代作用关系。'),
 ('12/1,13/1','健康良好由运动和均衡饮食支持的关系','before 分别存身体健康及运动饮食，但未明确二者的支持关系。','after 两项均有存；不将并存直接认作因果或支持关系。'),
 ('12/6,13/4','阅读历史传记帮助减压的关系','before 有阅读历史传记爱好和一般减压支持，但未明确阅读传记帮助减压。','after 不将阅读爱好及一般压力片段并存当作该关系。'),
 ('12/6,13/4','休息帮助减压的关系','before 有 Mary 鼓励休息及自我照顾/支持管理压力，但未明确休息帮助减压的关系。','after 不以独立片段并存自动补全该关系。'),
 ('13/5','朋友同事是主要支持来源','before 有寻求朋友同事支持管理压力，没有明确主要支持来源。','after 新增 main support system；此前未明确的主要程度不计损伤。'),
 ('17/3,18/3','技术经历与问题解决能力可迁移至政治咨询的关系','before 有技术创新经历、问题解决和支持亲属目标，但未明确保存它们可迁移至政治咨询的关系。','after 不以相关技能和咨询方向并存自动构成迁移关系。'),
 ('19/1','将 17,000 美元月收入与 2025-09-05 陈述日期明确绑定','before 有月收入数额与收入关系，没有明确 2025-09-05 日期。','after 将收入表述为转型前，但没有该准确日期；日期先前未存不计损伤。用户在该日期陈述，并不证明收入始于该日。'),
 ('19/2','将 16,800 美元储蓄与 2025-09-05 陈述日期明确绑定','before 有储蓄金额，没有明确 2025-09-05 日期。','after 仍有金额但没有该准确日期；日期先前未存不计损伤，余额的历史时间表达仍待判断。'),
 ('15/2','Steven 布景专长对电影历史真实性的具体贡献','before 有 Steven 布景专长和历史兴趣，未明确保存其对电影真实性的具体贡献。','after 相同的同事资料仍在；不能用一般专长代替具体贡献。'),
 ('15/3','兼顾新旧关系且各自提供不同支持和机会','before 有多位朋友同事及支持，但没有明确将新旧关系区分并绑定不同支持和机会。','after 有一般关系与支持，不自动等于新旧关系分别提供不同机会。'),
 ('1/6','喜欢瑜伽这一偏好','before 只有练瑜伽和柔韧、思维清晰作用，没有明确喜欢瑜伽。','after 仍有练瑜伽及作用；练习不能自动等于喜好，不将前存不完整的喜好计为损伤。'),
 ('7/14','喜欢瑜伽这一偏好','before 只有练习瑜伽及作用，没有明确喜欢瑜伽。','after 保留练习及作用；不推断喜好已前存或计算损伤。'),
 ('8/3','喜欢瑜伽这一偏好','before 有练习瑜伽及作用，但没有明确喜欢这一偏好。','after 写规律练习及作用，不将练习自动等同喜欢；前存未明确的偏好不计损伤。'),
]
for j,(ids,f,bef,aft) in enumerate(missing,3):
 first=ids.split(',')[0];n=int(first.split('/')[0]);e=E[n];session=e['review']['session_group_id'];
 for id in ids.split(','):assert E[int(id.split('/')[0])]['review']['session_group_id']==session
 facts.append({'id':f'N{j:03}','session':session,'fact':f,'candidates':ids,'before_eligibility':'前未明确完整保存','retain_requirement':'不作为本次旧存量保护分母；不认定原对话无此事实','after_status':'前存缺口；不记更新损伤','before':bef,'after':aft,'source':f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json','basis':'限定完整关系/程度未明确前存；具体可核对的组成部分另列，不倒填对话日期。'})
# Pending whole-candidate groups from prior audit. The following were fully decomposed into retained and/or pre-absent subfacts here.
closed={'7/15','7/11','8/1','8/5','11/3','12/1','13/1','12/6','13/4','13/5','17/3','18/3','7/11','19/1','1/6','7/14','8/3','7/6','7/13'}
groups=collections.defaultdict(list)
for x in candidate:
 if x['scope']=='主目标' and '待判断' in x['status']:groups[x['group']].append(x)
assert len(groups)==51
pending=[]
for key,arr in groups.items():
 ids=[x['candidate'] for x in arr]
 if set(ids)<=closed:continue
 x=arr[0];pending.append({'id':f'U{len(pending)+1:02}','session':x['session'],'candidates':','.join(ids),'claim':x['candidate_fact'],'before_eligibility':'待完整拆分或时间/关系等价核验','retain_requirement':'待确认事实粒度和历史有效性；不得假定当前有效','after_status':'待判断','detail':x['assessment'],'before_locator':x['before'],'after_locator':x['after'],'source':x['source']})
assert len(pending)==36,(len(pending),[x['candidates'] for x in pending])
# target 20/2 is a compound secondary candidate in an existing primary session; its time and savings relationship remain open.
r20=next(x for x in candidate if x['candidate']=='20/2')
pending.append({'id':f'U{len(pending)+1:02}','session':r20['session'],'candidates':'20/2','claim':r20['candidate_fact'],'before_eligibility':'时间及复合关系待拆分；政治资助和月收入已单列','retain_requirement':'历史记录与当前有效性分开核验','after_status':'待判断','detail':'前有政治资助、收入和储蓄，不能仅凭共存确认“储蓄有限”及其因果、准确时间；R05/R06 已单列具体事实。','before_locator':r20['before'],'after_locator':r20['after'],'source':r20['source']})
# Repeated candidate rows in shared sessions map to corresponding primary candidate facts and unresolved portions.
aliases={
 '2/1':'3/6','2/2':'3/7','2/3':'3/8','2/4':'3/1','2/5':'3/2','2/6':'3/4','2/7':'3/5',
 '5/1':'4/2','5/2':'4/1','5/3':'4/3','5/4':'4/4','5/5':'4/5','5/6':'4/6',
 '6/1':'4/3','6/2':'4/1','6/3':'4/2','6/4':'4/4','6/5':'4/5','6/6':'4/6',
 '20/1':'17/4','20/3':'17/2','20/4':'17/1','20/5':'17/3','20/6':'17/5','20/7':'17/6','20/8':'17/7',
}
# P067 is the same innovation-duty subfact present in 17/2, 18/2 and 20/3.
next(x for x in facts if x['id']=='P067')['candidates']+=',17/2'
# Same-transition income/date subfacts also belong to 20/2.
for target_id in ['R05','N013']:next(x for x in facts if x['id']==target_id)['candidates']+=',20/2'
for alias,primary in aliases.items():
 matches=[x for x in facts+pending if primary in x['candidates'].split(',')]
 assert matches,(alias,primary)
 for x in matches:
  if alias not in x['candidates'].split(','):x['candidates']+=','+alias
# Ensure user-confirmed general-elegance nuance is not silently counted as the unstored home relation.
assert any(x['candidates']=='14/1' for x in pending)
cross=collections.defaultdict(list)
for z in facts+pending:
 for id in z['candidates'].split(','):cross[id].append(z['id'])
coverage=[]
for x in candidate:
 id=x['candidate'];assert cross[id],('候选未映射',id)
 coverage.append({'candidate':id,'session':x['session'],'scope':x['scope'],'claim':x['candidate_fact'],'fact_or_pending_ids':','.join(dict.fromkeys(cross[id])),'source':x['source']})
with (P/'KPR_候选映射.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=coverage[0].keys());w.writeheader();w.writerows(coverage)
with (P/'KPR_事实台账.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=facts[0].keys());w.writeheader();w.writerows(facts)
with (P/'KPR_待核候选组.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=pending[0].keys());w.writeheader();w.writerows(pending)
# Explicit 19-subtarget / 15-session JSR; protection union from all primary candidates in a session.
by_session=collections.defaultdict(list)
for r in usr:by_session[E[int(r['target'])]['review']['session_group_id']].append(r)
known=collections.defaultdict(list);dam=collections.defaultdict(list);preabs=collections.defaultdict(list);unknown=collections.defaultdict(list)
for f in facts:
 if f['after_status'].startswith('完整保留'):known[f['session']].append(f['id'])
 elif f['after_status'].startswith('部分损伤'):dam[f['session']].append(f['id'])
 else:preabs[f['session']].append(f['id'])
for q in pending:unknown[q['session']].append(q['id'])
assert len(by_session)==15
js=[]
for r in usr:
 n=int(r['target']);s=E[n]['review']['session_group_id']; assert known[s] or dam[s],('缺少合格项',n)
 if r['classification'] in ('部分','失败'):state='失败';reason='USR 核心未完整；已有合格保护事实，故联合条件不成立。'
 elif dam[s]:state='失败';reason='USR 成功，但该会话保护事实已有确认损伤。'
 elif unknown[s]:state='待判断';reason='USR 暂记成功，仍有同会话保护候选资格、完整性或时间表达未确定。'
 else:state='成功';reason='USR 暂记成功且同会话合格保护集合已完整判断为保留。'
 js.append({'target':n,'session':s,'session_targets':','.join(x['target'] for x in by_session[s]),'usr':r['classification'],'usr_authority':r['authority'],'known_retained':','.join(known[s]),'confirmed_damage':','.join(dam[s]),'not_preexisting':','.join(preabs[s]),'pending_groups':','.join(unknown[s]),'eligible_status':'至少有一项限定具体事实暂定合格；完整保护集合仍待核验','jsr':state,'reason':reason,'source':r['source']})
with (P/'JSR_逐目标.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=js[0].keys());w.writeheader();w.writerows(js)
js_sessions=[]
for session,rs in by_session.items():
 relevant=[x for x in js if x['session']==session]
 if any(x['jsr']=='失败' for x in relevant):state='失败'
 elif any(x['jsr']=='待判断' for x in relevant):state='待判断'
 else:state='成功'
 js_sessions.append({'session':session,'targets':','.join(x['target'] for x in rs),'usr_classes':','.join(f"{x['target']}:{x['classification']}" for x in rs),'jsr':state,'known_retained':','.join(known[session]),'confirmed_damage':','.join(dam[session]),'pending_groups':','.join(unknown[session])})
with (P/'JSR_逐会话.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=js_sessions[0].keys());w.writeheader();w.writerows(js_sessions)
# Sensitivity check: only that target's protection candidates, without co-session union.
js_target_only=[]
for row in js:
 target=str(row['target']); session=row['session']
 refers=lambda x:any(c.split('/')[0]==target for c in x['candidates'].split(','))
 valid=[x for x in facts if x['session']==session and x['after_status'].startswith('完整保留') and refers(x)]
 lost=[x for x in facts if x['session']==session and x['after_status'].startswith('部分损伤') and refers(x)]
 unsure=[x for x in pending if x['session']==session and refers(x)]
 assert valid or lost,('该目标无可验证合格保护事实',target)
 status='失败' if row['usr'] in ('部分','失败') or lost else ('待判断' if unsure else '成功')
 js_target_only.append({'target':target,'session':session,'usr':row['usr'],'retained':','.join(x['id'] for x in valid),'damage':','.join(x['id'] for x in lost),'pending':','.join(x['id'] for x in unsure),'jsr':status})
with (P/'JSR_仅目标候选.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=js_target_only[0].keys());w.writeheader();w.writerows(js_target_only)

K=['# KPR 事实机会台账','', '单位是用户 × 原始会话 × 限定具体事实。P 为上一批、B 为追加批、R 为本轮新拆的保留事实；L 为已用户确认损伤；N 是更新前未明确完整保存的限定内容，不进入合格分母。N 仍需上下文核验，不能说用户从未表达过。前存与应保留基于冻结候选、完整快照、对本会话未见明确撤销的暂定判断，不代表全部由用户逐项确认。','']
for f in facts:K += [f"## {f['id']} {f['fact']}",f"- 会话 `{f['session']}`；候选 {f['candidates']}；前：{f['before_eligibility']}；保留要求：{f['retain_requirement']}；后：**{f['after_status']}**。",f"- 前证据：{f['before']}",f"- 后证据：{f['after']}",f"- {f['basis']} [完整证据]({f['source']})",'']
(P/'KPR_事实台账.md').write_text('\n'.join(K))
# Transparent cross-batch deduplication audit, grouped by the original user/session.
D=collections.defaultdict(list)
for x in facts:
 if x['after_status'].startswith('完整保留'):D[x['session']].append(x)
A=['# KPR 已判定保留事实的去重审计','', '先按用户和原始会话分组，再比较主体、对象、关系和限定。前版 P 批 70 项与 B 批 27 项逐会话比较：没有发现同一具体命题需要合并；相同记忆 ID 的自动交叉检查也没有碰撞，但不同 ID 并不能单独证明事实不同，因此结合事实内容复核。R 批 13 项包括本轮拆分和原先未并入的重复确认会话保护事实，同样核对会话及含义。合计 110 个限定事实机会；原候选的上位复合组可能与这些事实部分重叠，不能再当作额外确定事实。','', '|原用户会话|P 批|B 批|R 批|事实及原候选|','|---|---|---|---|---|']
for session,items in D.items():
 counts=collections.Counter(x['id'][0] for x in items); desc='<br>'.join(f"{x['id']} {esc(x['fact'])}（{x['candidates']}）" for x in items)
 A.append(f"|`{session}`|{counts['P']}|{counts['B']}|{counts['R']}|{desc}|")
A+=['','原 176 个候选行均在 [候选映射 CSV](KPR_候选映射.csv) 追溯到事实或待核组。相同会话的重复确认/归并候选被映射到已整理的相同或重叠子事实及未决组；跨会话不合并。映射到同一未决组仅表示有重叠，不宣称每条复合候选完全等价。','']
(P/'KPR_去重审计.md').write_text('\n'.join(A))

U=['# KPR 待核候选组','', '以下是尚未完全拆定的候选组，不等于待判断唯一事实数；其组成可能与已核事实部分重叠。每项必须先判断具体事实和更新前资格，再核验完整 after；定位器可能误命中，不可直接用匹配数评分。','']
for q in pending:U += [f"## {q['id']} / {q['candidates']}：{q['claim']}",f"- 会话 `{q['session']}`；更新前：{q['before_eligibility']}；仍应保留：{q['retain_requirement']}；更新后：{q['after_status']}。",f"- 现有核对：{q['detail']}",f"- 前定位：{q['before_locator']}",f"- 后定位：{q['after_locator']}",f"- [完整证据]({q['source']})",'']
(P/'KPR_待核候选组.md').write_text('\n'.join(U))
J=['# JSR 逐目标工作试算','', '主口径单位：19 个主目标，不是 19 次独立会话。某目标 JSR 成功需其严格 USR 成功，并且同一会话所有合格保护事实完整保留；目标的会话保护集合取该会话内所有冻结保护候选之并集，包括同会话的重复确认及归并目标；这些目标只补充保护候选，不额外计为主目标案例。任一必要条件已失败则失败；USR 成功但有资格或保护结果未知则待判断。每个目标已找到至少一条暂定合格保护事实；前存缺口不进入保护分母。USR 的部分=严格非成功；初判不能冒充用户确认。','', '|目标|会话／共享目标|USR 与来源|已保留 / 已确认损伤 / 前存缺口 / 待核候选组|JSR|原因|','|---|---|---|---|---|---|']
for r in js:J.append(f"|[{r['target']}]({r['source']})|`{r['session']}` / {r['session_targets']}|{r['usr']}；{r['usr_authority']}|{r['known_retained'] or '—'} / {r['confirmed_damage'] or '—'} / {r['not_preexisting'] or '—'} / {r['pending_groups'] or '—'}|**{r['jsr']}**|{r['reason']}|")
J+=['','同一会话另做去重口径：只将所有主目标的 USR 均成功且该会话全部合格保护事实完整保留判为联合成功；任一必要条件已失败则该会话失败，否则待判断。见 [逐会话 CSV](JSR_逐会话.csv)。不同口径不能相加。另作[仅用每个目标自身保护候选的敏感性核对](JSR_仅目标候选.csv)；当前分类数量相同，但未核项目和每项引用的保护集合不同。','']
(P/'JSR_逐目标.md').write_text('\n'.join(J))
# Source totals: all frozen 24 targets have 16 contexts, while 19 primary have 15.
allD=json.loads((orig/'target_decisions.json').read_text())['targets'];allcontexts={x['session_group'] for x in allD};assert len(allcontexts)==16
ct=collections.Counter(f['after_status'] for f in facts);jc=collections.Counter(r['jsr'] for r in js);sc=collections.Counter(r['jsr'] for r in js_sessions)
stat={'kpr_text_preserved':ct['完整保留（文本证据、初判）'],'kpr_user_confirmed_partial_damage':ct['部分损伤（用户已确认）'],'kpr_pre_not_fully_saved':ct['前存缺口；不记更新损伤'],'kpr_pending_candidate_groups':len(pending),'kpr_pending_unique_facts':'待核验','jsr_by_primary_subtarget':dict(jc),'jsr_by_primary_session':dict(sc),'jsr_only_target_candidates':dict(collections.Counter(r['jsr'] for r in js_target_only)),'primary_targets':len(js),'primary_sessions':len(by_session),'all24_sessions':len(allcontexts),'eligible_target_count':sum(bool(known[r['session']] or dam[r['session']]) for r in js),'kpr_sessions':len({r['session'] for r in facts} | {r['session'] for r in pending}),'candidate_rows':len(coverage),'cross_batch_identity_collisions':len(collisions)}
(P/'COUNTS.json').write_text(json.dumps(stat,ensure_ascii=False,indent=2)+'\n')
sources=[old/'KPR_可核对事实.csv',old/'KPR_候选覆盖.csv',recent/'KPR_新增拆分事实.csv',recent/'USR_工作分类.csv',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md',root/'human_review_packets/native_case_review_v1_20261028/review_record.json',orig/'target_decisions.json']+[orig/f'target_{n:02}_evidence.json' for n in range(1,25)]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+str(x.relative_to(root))+'\n' for x in sources))
print(json.dumps(stat,ensure_ascii=False,indent=2))
