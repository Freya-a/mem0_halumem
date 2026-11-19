from pathlib import Path
import json
p=Path(__file__).resolve().parent
load=lambda x:json.loads(x.read_text())
insights={
'susan':('原回放将新上下文属性标成 support_context、旧支持标成 friend_support，字符串不相等导致旧支持得到 disjoint_preserve；这首先是手工声明表示/属性对齐问题，而不是证据证明支持关系相斥。另做同一 friend_support 映射回放后，朋友关系仍是 disjoint_preserve，支持变为 hold_provisional 并出现 boundary_unknown；该映射仍需人工审核。原 add 只含 new-2，遗漏判断求职情境所需的 new-0。','实验副本的清单显示 new-0 与 new-2，但不自动建立跨句归因或生成独立新事实。'),
'promotion':('属性映射可分离旧公司和职位：雇主 disjoint_preserve、职称 hold_provisional、possible_change 与 boundary_unknown；add 只有晋升原文候选。未产出明确的“旧职位历史化候选”，与拟议范围有缺口。','范围规则只接受历史事实明确纠正且交集完整才生成 modify；本案是经审核的状态阶段变化，不是对旧历史的纠错。准确日期未知，不能放宽为确定覆盖；所缺是独立的待审核历史化表达，而非允许无边界写入。'),
'career_history':('公司及职位各有 disjoint_preserve，与保留具体旧职业历史的方向一致；new-0 获客原文进入 add，但 new-2 两人关系作用没有进入原 add。职业历史属性与获客不同，程序不会识别完整事件语义。','实验清单同时列出两段原文，仅解决证据可见性；没有拆出获客、宽慰或集体关系的可写新事实，也不验证关系作用与客户之间的具体因果。'),
 'transition':('旧求职状态得到 hold_provisional，possible_change、boundary_unknown 和完整新角色原文候选均出现；没有给出该次求职阶段历史化候选。','声明表示需要人工确认“求职”与已完成的转岗是否指同一进程，审核已有该方向的结论；范围规则还将普通状态进展与历史纠错混在同一修改门槛下。不能由记录日期补齐转岗生效日，也不能判定不再寻找其他机会。'),
'skydiving':('旧态度、风险和安全承诺以不同属性得到 disjoint_preserve，新模拟体验原文进入 add，new-2 的享受/开放与 new-8 的安全优先不在原 add。','属性名不同只能说明本次手工标签不同，不能证明模拟体验对旧宽泛偏好的影响在语义上不相交；真实跳伞的当前态度仍未知。实验清单保留全部三条原文，但并未解析新增事实，也不意味着需改写旧风险。')}
lines=['# 小论文范围定位：5 案离线回放','',
'2026-11-18。五案均来自 medium_dev 已审核主目标和原生 Mem0 的更新前真实快照，包含原始旧记忆、较早用户来源及目标会话的新证据；没有手工构造的整案。**声明切分、属性映射、上游关系标签和本报告的预期均为本轮助手手工整理，不是模型输出，也不是用户确认的金标准。** 24 条既有审核确认的是数据目标与证据边界，不等于确认每个范围标签、关联或系统结果。','',
'原 v8/v9 五案报告用于追溯 Susan、晋升、职业历史、跳伞四案旧记忆；转岗为额外选取的真实旧快照。每案使用一个人工整理的整条旧事实，另以有引用的 old_units 手工区分旧属性；关系候选通过现有 v2 校验器的手写 backend 构造，**没有调用模型**。`output_before.json` 是现有规划器在 structured 与 baseline-only 下的直接结果；预期放在独立 `expected.json`，不会喂给规划器。','',
'有效时间的开始/结束与未给出的条件均为 unknown；发言记录时间只是 observation，不当作生效日期。手工标注使用未知星期表示数据没有给出该维度，并不推定活动只在某天发生。所有 add 都是原文候选，不等于已拆分、已去重或应写入。','',
'## 总览','','| 案例 / 审核目标 | 原规划器：modify / preserve / uncertain / add | 原 add 引用的新来源 / 输入新来源 | 重点 |','|---|---:|---:|---|']
for name in ('susan','promotion','career_history','transition','skydiving'):
 d=p/'cases'/name;c=load(d/'input.json');a=load(d/'output_before.json')['structured'];newids={e['source_id'] for z in a['add'] for e in z['new_evidence']};total=len(c['request']['new_evidence']);
 lines.append(f"| {name} / {c['human_review_target_number']} | {len(a['modify'])} / {len(a['preserve'])} / {len(a['uncertain'])} / {len(a['add'])} | {len(newids)} / {total} | {insights[name][0]} |")
lines+=['','## 逐案来源与拟议范围','']
catlabels={'modify':'应修改／历史化候选','preserve':'应保留','uncertain':'待确认','add':'独立新增候选'}
for name in ('susan','promotion','career_history','transition','skydiving'):
 d=p/'cases'/name;c=load(d/'input.json');e=load(d/'expected.json');req=c['request'];before=load(d/'output_before.json')['structured'];after=load(d/'output_after.json')['structured']
 lines += [f"### {name}｜审核目标 {c['human_review_target_number']}",'',f"**旧声明：** {e['old_statement']}  ",f"**旧记忆原文：** `{req['split_result']['memory_text']}`  ",f"**新声明：** {e['new_statement']}",'',f"**旧快照：** `{c['memory_snapshot']}`，ID `{c['memory_id']}`。"]
 for src in req['source_context']+req['new_evidence']:
  lines += [f"- `{src['source_id']}`（{src.get('speaker','unknown')}，记录于 {src.get('recorded_at','unknown')}）：{src['text']}  ",f"  来源：`{src.get('source_ref','见 input.json')}`"]
 lines+=['']
 for category in ('modify','preserve','uncertain','add'):
  lines.append(f"**{catlabels[category]}：**")
  for item in e[category]:
   refs='；'.join(f"{z['source_id']}：“{z['quote']}”" for z in item['evidence'])
   lines+=['',f"- {item['scope']} 引文：{refs}"]
  lines+=['']
 def rows(key): return '；'.join(f"{z['code']} / {z.get('attribute')}" for z in before[key]) or '无'
 lines += [f"**原规划器对照：** modify：{rows('modify')}；preserve：{rows('preserve')}；uncertain：{rows('uncertain')}；add：{rows('add')}。{insights[name][0]}",'',f"**定位与实验修正：** {insights[name][1]}",'',f"[输入](cases/{name}/input.json) · [候选预期](cases/{name}/expected.json) · [原输出](cases/{name}/output_before.json) · [实验输出](cases/{name}/output_after.json)",'']
lines += ['## 小范围实验修正及界限','',
'`plan_experimental.py` 是现有 `plan.py` 的独立副本，唯一改动是在输出中增加 `new_evidence_inventory`：逐项保留输入的新来源原文及记录元数据，并标明是否被上游候选和已验证候选引用；每条明确 `independent_fact_verified=false`、`old_fact_relation_verified=false`。它不改变原有 `modify / preserve / uncertain / add`，也不把清单项自动视为新增事实或授权写入。五案输入新来源共 9 条，原 add 引用 5 条，实验清单展示全部 9 条；原始输入文件本来就有这些来源，所以这是**规划输出可见性缺口**，不是原始数据丢失。','',
'这个修正未处理多来源语义合并、关系归因、历史化候选或自动去重；因此不能据此说五案已经得到完整范围规划。原 `part2_scope_planner/plan.py` 未修改，实验副本未接入运行链。原始回放、Susan 属性映射调整后的回放和实验副本结果分别保留，不覆盖历史结果。','',
'现有规则对状态变化与历史纠错使用同一个严格修改门槛；对于晋升和转岗，可研究增加**不指定生效日、不执行写入的待审核状态进展/历史化候选**。应先由你确认范围语义，再用独立案例检验，不宜直接把 possible_change 当作纠正或自行关闭时间区间。','',
'## 待你确认的金标准边界','',
'1. Susan 的求职情境是否作为独立新增单元，还是与旧支持事实合并；ThomasSusan / Susan 身份歧义如何记录。',
'2. 晋升与转岗在未知准确生效日时，是否应提出“旧状态历史化”候选，以及希望保留哪些相对先后信息；不能把候选等同执行修改。',
'3. 模拟跳伞是否需要对旧宽泛当前偏好提出范围限定，以及保留旧风险理由的粒度。',
'4. Donald 获客与两人集体人脉作用的独立新增粒度和跨句关系；不能按个人分别归因，也不能推断客户数量或获客日。','',
'验证：现有规划器离线测试 37 项、实验副本针对多来源及上游失败的测试 3 项；逐案引文与来源追溯及改动范围另见 `verification.json`。本次无模型、Mem0 或知识库调用。','']
(p/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
