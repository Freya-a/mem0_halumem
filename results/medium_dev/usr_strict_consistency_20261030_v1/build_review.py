import csv,json,collections,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent; root=P.parent; base=root/'williams_native_prefix5_20261028_v3'/'development_diagnosis_v1'; old=root/'usr_kpr_reconciliation_20261030_v1'
rows=list(csv.DictReader((old/'USR_逐目标.csv').open(encoding='utf-8-sig')))
adjust={
 1:('待判断','原诊断完整。用户明确欣赏金毛的适应能力；after 同条先写金毛温顺，再写重视宠物的适应能力，但未直接说金毛有此能力。相邻表达是否足以保留该具体关联待确认；暂不推断关联必然存在或不存在。'),
 8:('部分','用户确认：模拟跳伞、正面感受和对新事物更开放已存；values safety 没有明确表达安全仍放在首位。更愿尝试极限运动是否扩范围另列待核验。'),
 12:('部分','原诊断完整。after 明确保存晋升后心理健康改善、委派减压及专注改善，但没有明确保存冻结核心的“显著”程度；按与目标 8 相同的明确程度要求，初步记部分。'),
 18:('待判断','原诊断完整。after 有目标成为竞选关键顾问的意向，但没有明写“更直接地为竞选提供建议”的比较程度；关键顾问角色是否足以明确表达该限定，留待确认。'),
}
checks={
 1:'适应能力与金毛的明确关联；新偏好、温顺。',3:'非营利组织与拟申请/从事岗位的关联；人脉、指导及工作灵活性。',4:'Susan 支持与求职情境的关联。',7:'新岗位与更健康的工作生活平衡；旧求职时间另列。',8:'模拟体验、正面感受、开放新事物及安全优先程度。',9:'茶馆体验与伯爵茶层次风味欣赏加深的关联。',10:'同一雇主、晋升和 Lead Director；旧职称时间另列。',11:'晋升后控制空间增加与可推动真实性、创新的关联。',12:'晋升后的心理改善程度；委派与减压和项目专注的关系。',13:'角色变化与工作生活平衡变好，比较方向明确。',14:'电影节纪录片体验与波斯猫历史传承欣赏加深的关联。',16:'现场演出促成探索、当前巴洛克重点及开放性。',17:'转型及直接支持亲属的动机；专业人脉与研讨会的推进。',18:'直接建议的意向和关键顾问角色，尤其“更直接”的程度。',19:'转型初期没有即时收入；依靠储蓄并减支。',21:'转型压力与心理健康的关系及原因。',22:'两位朋友在转型期间集体提供鼓励和策略建议。',23:'利用包括两位朋友在内的人脉获取首批客户的计划关系。',24:'已获首批客户及因此宽慰、里程碑的主观意义。'}
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
for r in rows:
 n=int(r['target']);r['prior_classification']=r['classification'];r['checks']=checks[n]
 if n in adjust:r['classification'],r['consistency_note']=adjust[n]
 else:r['consistency_note']='此前初步分类沿用；核对核心限定、关系及阶段，仍非自动人工终审。' if n not in (7,10,22) else '沿用用户既有确认；时间和保护内容另评价。'
 if n==8:r['note']='已保存模拟跳伞、正面感受、开放尝试和重视安全；用户确认安全优先程度未明确保存，范围是否扩大另待核验。'
 r['authority']='用户确认的暂定部分覆盖' if n==8 else ('用户确认的暂定成功' if n in (7,10) else ('用户已确认核心新事实未找到' if n==22 else '本轮初步判定，未经用户确认'))
fields=['target','classification','prior_classification','authority','core','checks','after','note','limits','consistency_note','source']
with (P/'USR_一致性核对.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
L=['# USR 一致性核对表','', '以冻结审核所列各目标核心为准，要求在更新后完整知识中明确表达关键关系、程度、阶段和条件；不要求逐字一致，等价语义可计入。严格成功须核心完整正确；部分不算成功，不能确定等价关系时单列待判断。旧历史、KPR 和非核心补充不自动并入 USR。用户对 7、8、10 及案例 D 的确认分别保留，其余均为初步判定。','', '|目标|冻结核心及一致性核对点|关键更新后记忆|此前 → 本轮|判定依据与限制|证据|','|---|---|---|---|---|---|']
for r in rows:
 L.append(f"|{r['target']}|{esc(r['core'])}<br>核对：{esc(r['checks'])}|{r['after']}|{r['prior_classification']} → **{r['classification']}**<br>{r['authority']}|{esc(r['consistency_note'])}<br>原诊断：{esc(r['note'])}<br>限制：{esc(r['limits'])}|[目标证据]({r['source']})|")
(P/'USR_一致性核对.md').write_text('\n'.join(L)+'\n')
counts=dict(collections.Counter(r['classification'] for r in rows));(P/'COUNTS.json').write_text(json.dumps({'usr_by_classification':counts,'units':'19个主目标；不代表独立会话实验','prior_report':'../usr_kpr_reconciliation_20261030_v1/REPORT.md','note':'非最终值；等价性待确认的目标1和18单列待判断'},ensure_ascii=False,indent=2)+'\n')
files=[old/'USR_逐目标.csv',root/'usr_kpr_interactive_review_20261030_v1'/'REVIEW.md']+[base/f'target_{int(r["target"]):02}_evidence.json' for r in rows]
(P/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in files))
print(json.dumps(counts,ensure_ascii=False))
