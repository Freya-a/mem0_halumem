import csv,json,hashlib,collections
from pathlib import Path
P=Path(__file__).resolve().parent;root=P.parent;src=root/'usr_strict_consistency_20261030_v1'/'USR_一致性核对.csv'
r=list(csv.DictReader(src.open(encoding='utf-8-sig')))
notes={
1:('金毛的温顺、适应能力、偏好及其对象关系属于冻结核心；“十分”等表达强度不另作为必需。','温顺、新偏好有记忆；宠物适应能力与金毛在同条相邻但关系未明，待判断。'),
3:('非营利组织岗位、探索和人脉计划的阶段、工作灵活性与健康关系为核心；不要求确切岗位。','非营利兴趣与找工作未明确关联，部分。'),
4:('Susan 的支持、帮助专注与本次求职情境的关系为核心；无需额外强度修饰。','一般鼓励有记录，求职情境关联未明确，部分。'),
7:('转岗已发生与平衡更健康为核心阶段及比较；准确转岗日不作必需。','已明确保存，沿用用户暂定成功。'),
8:('模拟体验、享受、开放新事物、安全仍放在首位为冻结核心；不将“刺激”等词逐字作为额外评分要求。','安全重要性存在但优先顺序未明确；用户确认部分，泛化另待判断。'),
9:('茶馆体验、伯爵茶层次风味及欣赏加深的关联与比较为核心。','相关记忆分别存在，体验导致对伯爵茶欣赏加深未明确，部分。'),
10:('同一雇主、最近晋升与 Lead Director 为核心状态；不以旧宽泛 Director 单独判冲突。','新状态已存，沿用用户暂定成功。'),
11:('晋升后更多创作控制以及能推动真实性和创新的能力/期待关系是核心，重视控制不等于控制增加。','价值观与计划有存，新增控制程度及关联未明确，部分。'),
12:('心理健康显著改善的程度、晋升阶段，以及委派与减压、专注的关系是冻结核心；不要求临床诊断。','改善及委派关系已存，但显著程度未明确；用户确认部分，不是完全未存或病情恶化。'),
13:('角色变化导致工作生活平衡变好，比较方向与因果关系是核心；不要求额外程度词。','角色变化导致平衡改善有明文，初步成功。'),
14:('电影节/纪录片体验、波斯猫历史传承与王室关联，以及欣赏加深的关联和比较是核心。','波斯猫欣赏有存，纪录片体验及欣赏加深关系未明确，部分。'),
16:('现场演出促使探索、目前巴洛克重点和对其他影响开放是核心；不要求永久唯一偏好。','演出与转向分别有存，促成关系未明确，部分。'),
17:('转型方向及支持亲属动机、已建立专业联系并参加研讨会的进度为核心；不要求已正式就职。','转型方向有存，专业联系和研讨会未明确，部分。'),
18:('直接提供竞选建议与关键顾问角色意向的关系和范围为核心；不要求已任命。','关键顾问意向已存，“更直接”是否由此充分表达待判断。'),
19:('转型初期没有即时收入的时间限定，及依靠储蓄减支计划为核心；不能推断整月零收入。','储蓄减支计划有存，初期无即时收入未明确，部分。'),
21:('压力正在影响心理健康及其与收入不确定、兼顾学习竞选承诺的关联为核心；无需临床诊断。','压力及收入顾虑有存，心理影响和关联未明确，部分。'),
22:('两位朋友在转型期间共同提供鼓励与策略建议、集体归属和时段为核心。','未找到完整新事实，沿用已确认案例 D，失败。'),
23:('利用包括两人在内的人脉获取首批客户的计划关系与计划阶段为核心。','朋友和人脉有存，获取首批客户的计划关系未明确，部分。'),
24:('获得一些首批客户的完成阶段、宽慰及里程碑意义为冻结核心；客户具体数目和获客日期非必需。','已获客户有存，宽慰和里程碑意义未明确，部分。'),
}
assert len(r)==19 and set(notes)=={int(x['target']) for x in r}
for x in r:
 n=int(x['target']);x['core_qualifiers'],x['assessment']=notes[n]
 if n==12:x['authority']='用户确认的暂定部分覆盖'
fields=['target','classification','authority','core','core_qualifiers','assessment','after','source']
with (P/'USR_核心限定核对.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(r)
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
L=['# USR 核心限定一致性核对','', '核心限定以冻结审核确认的具体命题为准，包括必要的程度、比较、优先顺序、主体、关系和阶段；不将不改变核心含义的普通修饰词一律作为必需。允许明示的等价表达；上下文可能支持但不能可靠判断的关联单列待判断。用户确认的暂定结论按原意记录，其他判断均为初步。','', '|目标|核心限定与非必需内容|更新后表现及初步判断|来源|','|---|---|---|---|']
for x in r:L.append(f"|{x['target']}|{esc(x['core_qualifiers'])}|**{x['classification']}**（{x['authority']}）：{esc(x['assessment'])}<br>{x['after']}|[完整前后与审核]({x['source']})|")
(P/'USR_核心限定核对.md').write_text('\n'.join(L)+'\n')
c=dict(collections.Counter(x['classification'] for x in r));(P/'COUNTS.json').write_text(json.dumps({'usr_working_classification':c,'scope':'19 个主目标；工作分类、非最终值','user_confirmed_provisional':[7,8,10,12],'user_confirmed_evidence':[22]},ensure_ascii=False,indent=2)+'\n')
paths=[src,root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md']+[root/f'williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{int(x["target"]):02}_evidence.json' for x in r]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in paths))
print(json.dumps(c,ensure_ascii=False))
