# 小论文范围定位：5 案离线回放

2026-11-18。五案均来自 medium_dev 已审核主目标和原生 Mem0 的更新前真实快照，包含原始旧记忆、较早用户来源及目标会话的新证据；没有手工构造的整案。**声明切分、属性映射、上游关系标签和本报告的预期均为本轮助手手工整理，不是模型输出，也不是用户确认的金标准。** 24 条既有审核确认的是数据目标与证据边界，不等于确认每个范围标签、关联或系统结果。

原 v8/v9 五案报告用于追溯 Susan、晋升、职业历史、跳伞四案旧记忆；转岗为额外选取的真实旧快照。每案使用一个人工整理的整条旧事实，另以有引用的 old_units 手工区分旧属性；关系候选通过现有 v2 校验器的手写 backend 构造，**没有调用模型**。`output_before.json` 是现有规划器在 structured 与 baseline-only 下的直接结果；预期放在独立 `expected.json`，不会喂给规划器。

有效时间的开始/结束与未给出的条件均为 unknown；发言记录时间只是 observation，不当作生效日期。手工标注使用未知星期表示数据没有给出该维度，并不推定活动只在某天发生。所有 add 都是原文候选，不等于已拆分、已去重或应写入。

## 总览

| 案例 / 审核目标 | 原规划器：modify / preserve / uncertain / add | 原 add 引用的新来源 / 输入新来源 | 重点 |
|---|---:|---:|---|
| susan / 4 | 0 / 2 / 1 / 1 | 1 / 2 | 原回放将新上下文属性标成 support_context、旧支持标成 friend_support，字符串不相等导致旧支持得到 disjoint_preserve；这首先是手工声明表示/属性对齐问题，而不是证据证明支持关系相斥。另做同一 friend_support 映射回放后，朋友关系仍是 disjoint_preserve，支持变为 hold_provisional 并出现 boundary_unknown；该映射仍需人工审核。原 add 只含 new-2，遗漏判断求职情境所需的 new-0。 |
| promotion / 10 | 0 / 2 / 2 / 1 | 1 / 1 | 属性映射可分离旧公司和职位：雇主 disjoint_preserve、职称 hold_provisional、possible_change 与 boundary_unknown；add 只有晋升原文候选。未产出明确的“旧职位历史化候选”，与拟议范围有缺口。 |
| career_history / 24 | 0 / 2 / 1 / 1 | 1 / 2 | 公司及职位各有 disjoint_preserve，与保留具体旧职业历史的方向一致；new-0 获客原文进入 add，但 new-2 两人关系作用没有进入原 add。职业历史属性与获客不同，程序不会识别完整事件语义。 |
| transition / 7 | 0 / 1 / 2 / 1 | 1 / 1 | 旧求职状态得到 hold_provisional，possible_change、boundary_unknown 和完整新角色原文候选均出现；没有给出该次求职阶段历史化候选。 |
| skydiving / 8 | 0 / 3 / 1 / 1 | 1 / 3 | 旧态度、风险和安全承诺以不同属性得到 disjoint_preserve，新模拟体验原文进入 add，new-2 的享受/开放与 new-8 的安全优先不在原 add。 |

## 逐案来源与拟议范围

### susan｜审核目标 4

**旧声明：** Martin 有 ThomasSusan（称 Susan）这一朋友，提供支持和鼓励。  
**旧记忆原文：** `Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement`  
**新声明：** Martin 正寻找更平衡的工作；同一会话称 Susan 的支持与鼓励帮助其保持目标专注。两句话的求职情境关联沿用已审核目标，但不归因 Daniel 的贡献。

**旧快照：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，ID `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`。
- `ctx-1`（user，记录于 Sep 06, 2025, 01:02:20）：ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [60:218]`
- `new-0`（user，记录于 Feb 05, 2026, 17:13:15）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`
- `new-2`（user，记录于 Feb 05, 2026, 17:15:18）：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`

**应修改／历史化候选：**

- 无证据要求删除或替换旧朋友关系／旧支持；如表达新的求职情境，可在原支持上补充，具体存储方式待确认。 引文：old：“Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement”；new-2：“Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.”

**应保留：**

- 保留朋友身份、Susan 的支持与鼓励，不改写为仅在本次求职中存在。 引文：old：“Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement”

**待确认：**

- 旧支持开始/结束时间、是否专属求职、ThomasSusan 名字的真实构成均未知；不能确定接受 offer 或完成转岗。 引文：old：“Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement”；new-0：“It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.”

**独立新增候选：**

- 候选独立新增：Susan 的支持、鼓励帮助用户保持目标专注的求职情境；原关系与新增情境可合并或分开，不自动判定必须写一条。 引文：new-0：“It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.”；new-2：“Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.”

**原规划器对照：** modify：无；preserve：disjoint_preserve / friendship；disjoint_preserve / friend_support；uncertain：relation_not_correction / support_context；add：raw_evidence_candidate / support_context。原回放将新上下文属性标成 support_context、旧支持标成 friend_support，字符串不相等导致旧支持得到 disjoint_preserve；这首先是手工声明表示/属性对齐问题，而不是证据证明支持关系相斥。另做同一 friend_support 映射回放后，朋友关系仍是 disjoint_preserve，支持变为 hold_provisional 并出现 boundary_unknown；该映射仍需人工审核。原 add 只含 new-2，遗漏判断求职情境所需的 new-0。

**定位与实验修正：** 实验副本的清单显示 new-0 与 new-2，但不自动建立跨句归因或生成独立新事实。

[输入](cases/susan/input.json) · [候选预期](cases/susan/expected.json) · [原输出](cases/susan/output_before.json) · [实验输出](cases/susan/output_after.json)

### promotion｜审核目标 10

**旧声明：** Williams 在 Historical Productions Ltd. 担任 Director。  
**旧记忆原文：** `Works at Historical Productions Ltd. as a Director`  
**新声明：** 用户自述最近升为同一公司的 lead director。

**旧快照：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，ID `e13b825e-7ec7-4760-821e-0581d8da5650`。
- `ctx-1`（user，记录于 Sep 05, 2025, 14:42:35）：I work at Historical Productions Ltd. as a Director.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_002/input.json#/raw_dialogue/2/content [55:107]`
- `new-0`（user，记录于 Feb 01, 2026, 18:47:19）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`

**应修改／历史化候选：**

- 职位局部应作为同次晋升的旧具体职称进行历史化候选；不据此修改公司；如何表示历史及准确边界待确认。 引文：old：“Works at Historical Productions Ltd. as a Director”；new-0：“I recently got promoted to lead director at Historical Productions Ltd.”

**应保留：**

- 保留 Historical Productions Ltd. 雇主及旧 Director 的历史事实。 引文：old：“Works at Historical Productions Ltd. as a Director”；new-0：“I recently got promoted to lead director at Historical Productions Ltd.”

**待确认：**

- 准确晋升生效日、旧职位失效日及完整有效期未知；不把发言记录日充当事件日。 引文：new-0：“I recently got promoted to lead director at Historical Productions Ltd.”

**独立新增候选：**

- 候选独立新增：在该公司升为 lead director，保留 recently。 引文：new-0：“I recently got promoted to lead director at Historical Productions Ltd.”

**原规划器对照：** modify：无；preserve：disjoint_preserve / employer；hold_provisional / job_title；uncertain：possible_change / job_title；boundary_unknown / job_title；add：raw_evidence_candidate / job_title。属性映射可分离旧公司和职位：雇主 disjoint_preserve、职称 hold_provisional、possible_change 与 boundary_unknown；add 只有晋升原文候选。未产出明确的“旧职位历史化候选”，与拟议范围有缺口。

**定位与实验修正：** 范围规则只接受历史事实明确纠正且交集完整才生成 modify；本案是经审核的状态阶段变化，不是对旧历史的纠错。准确日期未知，不能放宽为确定覆盖；所缺是独立的待审核历史化表达，而非允许无边界写入。

[输入](cases/promotion/input.json) · [候选预期](cases/promotion/expected.json) · [原输出](cases/promotion/output_before.json) · [实验输出](cases/promotion/output_after.json)

### career_history｜审核目标 24

**旧声明：** Donald 曾在 Blockchain Tech 担任 senior developer；旧原话在较早来源中为当时现在时。  
**旧记忆原文：** `Previously worked as a senior developer in Blockchain Tech`  
**新声明：** 用户表示咨询公司获得一些首批客户、感到宽慰并视为里程碑；另称 MooreSandra、GonzalezMary 的人脉提供了集体帮助。

**旧快照：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，ID `05afde13-35bd-4d26-bbae-6de427d58db1`。
- `ctx-1`（user，记录于 Sep 05, 2025, 09:10:09）：I work at Blockchain Tech as a senior developer.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_002/input.json#/raw_dialogue/2/content [61:109]`
- `new-0`（user，记录于 Jan 05, 2026, 07:43:42）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`
- `new-2`（user，记录于 Jan 05, 2026, 07:44:55）：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`

**应修改／历史化候选：**

- 新获客证据未推翻旧技术职业历史；无证据要求修改或删除这条旧职业事实。 引文：old：“Previously worked as a senior developer in Blockchain Tech”；new-0：“my consulting firm finally secured some initial clients”

**应保留：**

- 保留曾任 senior developer 及 Blockchain Tech 两项职业历史，不把职业细节泛化掉。 引文：old：“Previously worked as a senior developer in Blockchain Tech”

**待确认：**

- 旧岗位准确开始/结束时间、获客日、客户数和身份未知；获客不证明之前没有客户，也不证明具体当前雇佣身份。 引文：old：“Previously worked as a senior developer in Blockchain Tech”；new-0：“my consulting firm finally secured some initial clients”

**独立新增候选：**

- 候选独立新增：公司已获一些首批客户、用户因此感到宽慰并视为里程碑。 引文：new-0：“I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.”

- 候选另记：MooreSandra 与 GonzalezMary 的人脉作用按集体归因，不把具体行动分别安给每人。 引文：new-2：“MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.”

**原规划器对照：** modify：无；preserve：disjoint_preserve / historical_employer；disjoint_preserve / historical_title；uncertain：relation_not_correction / client_milestone；add：raw_evidence_candidate / client_milestone。公司及职位各有 disjoint_preserve，与保留具体旧职业历史的方向一致；new-0 获客原文进入 add，但 new-2 两人关系作用没有进入原 add。职业历史属性与获客不同，程序不会识别完整事件语义。

**定位与实验修正：** 实验清单同时列出两段原文，仅解决证据可见性；没有拆出获客、宽慰或集体关系的可写新事实，也不验证关系作用与客户之间的具体因果。

[输入](cases/career_history/input.json) · [候选预期](cases/career_history/expected.json) · [原输出](cases/career_history/output_before.json) · [实验输出](cases/career_history/output_after.json)

### transition｜审核目标 7

**旧声明：** Martin 正寻找更有工作生活平衡的新工作。  
**旧记忆原文：** `Looking for a new job with better work-life balance`  
**新声明：** 用户称已完成转到新岗位，工作生活平衡更健康。

**旧快照：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，ID `e6ab178b-c0f9-4adb-bfb7-e4648617a950`。
- `ctx-1`（user，记录于 Feb 05, 2026, 17:13:15）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`
- `new-0`（user，记录于 Mar 01, 2026, 07:04:00）：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`

**应修改／历史化候选：**

- 已审核的同次转岗进度可提出旧求职阶段历史化候选；不推出今后不再寻找其他机会。 引文：old：“Looking for a new job with better work-life balance”；new-0：“I've finally transitioned to a new role”

**应保留：**

- 保留此前寻找更平衡工作的历史与工作生活平衡诉求。 引文：old：“Looking for a new job with better work-life balance”

**待确认：**

- 转岗具体日期、新雇主、新职称、组织性质及是否离开旧公司未知；新旧描述属于同一转岗的映射来自既有审核，具体存储决策待确认。 引文：new-0：“I've finally transitioned to a new role”；old：“Looking for a new job with better work-life balance”

**独立新增候选：**

- 候选独立新增：用户自述完成新岗位转变，工作生活平衡更健康。 引文：new-0：“I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.”

**原规划器对照：** modify：无；preserve：hold_provisional / transition_progress；uncertain：possible_change / transition_progress；boundary_unknown / transition_progress；add：raw_evidence_candidate / transition_progress。旧求职状态得到 hold_provisional，possible_change、boundary_unknown 和完整新角色原文候选均出现；没有给出该次求职阶段历史化候选。

**定位与实验修正：** 声明表示需要人工确认“求职”与已完成的转岗是否指同一进程，审核已有该方向的结论；范围规则还将普通状态进展与历史纠错混在同一修改门槛下。不能由记录日期补齐转岗生效日，也不能判定不再寻找其他机会。

[输入](cases/transition/input.json) · [候选预期](cases/transition/expected.json) · [原输出](cases/transition/output_before.json) · [实验输出](cases/transition/output_after.json)

### skydiving｜审核目标 8

**旧声明：** Martin 不喜欢极限运动，包括跳伞；旧记忆给出受伤风险与安全健康原则的关系。  
**旧记忆原文：** `Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`  
**新声明：** 用户近期尝试并享受模拟跳伞，因此更愿意尝试新事物，并表示仍优先考虑安全。

**旧快照：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，ID `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`。
- `ctx-1`（user，记录于 Sep 06, 2025, 22:52:30）：I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json#/raw_dialogue/6/content [0:169]`
- `new-0`（user，记录于 Apr 10, 2026, 10:40:32）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`
- `new-2`（user，记录于 Apr 10, 2026, 10:48:20）：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`
- `new-8`（user，记录于 Apr 10, 2026, 10:57:54）：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.  
  来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`

**应修改／历史化候选：**

- 不要求以模拟体验覆盖或否定整个旧风险理由；旧泛化的当前适用范围需要具体限定，修改方案待确认。 引文：old：“Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being”；new-0：“I tried simulated skydiving”

**应保留：**

- 保留旧高受伤风险、安全健康承诺及其历史语境，不将旧偏好无条件视为当前适用。 引文：old：“Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being”；new-8：“I still prioritize safety, of course.”

**待确认：**

- 真实跳伞当前态度、模拟体验准确日期及旧广泛偏好当前范围未知；模拟活动不等同于真实跳伞。 引文：new-0：“I tried simulated skydiving”；old：“Dislikes extreme sports (e.g., skydiving)”

**独立新增候选：**

- 候选独立新增：近期团建尝试模拟跳伞并觉得刺激。 引文：new-0：“Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!”

- 候选独立新增：用户意外享受肾上腺素感，并更愿意尝试新事物。 引文：new-2：“the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.”

- 保留当前陈述：目前仍将安全放在首位；与旧安全原则可能重复，需去重。 引文：new-8：“I still prioritize safety, of course.”

**原规划器对照：** modify：无；preserve：disjoint_preserve / extreme_sport_attitude；disjoint_preserve / injury_risk_reason；disjoint_preserve / safety_commitment；uncertain：possible_change / simulated_skydiving_experience；add：raw_evidence_candidate / simulated_skydiving_experience。旧态度、风险和安全承诺以不同属性得到 disjoint_preserve，新模拟体验原文进入 add，new-2 的享受/开放与 new-8 的安全优先不在原 add。

**定位与实验修正：** 属性名不同只能说明本次手工标签不同，不能证明模拟体验对旧宽泛偏好的影响在语义上不相交；真实跳伞的当前态度仍未知。实验清单保留全部三条原文，但并未解析新增事实，也不意味着需改写旧风险。

[输入](cases/skydiving/input.json) · [候选预期](cases/skydiving/expected.json) · [原输出](cases/skydiving/output_before.json) · [实验输出](cases/skydiving/output_after.json)

## 小范围实验修正及界限

`plan_experimental.py` 是现有 `plan.py` 的独立副本，唯一改动是在输出中增加 `new_evidence_inventory`：逐项保留输入的新来源原文及记录元数据，并标明是否被上游候选和已验证候选引用；每条明确 `independent_fact_verified=false`、`old_fact_relation_verified=false`。它不改变原有 `modify / preserve / uncertain / add`，也不把清单项自动视为新增事实或授权写入。五案输入新来源共 9 条，原 add 引用 5 条，实验清单展示全部 9 条；原始输入文件本来就有这些来源，所以这是**规划输出可见性缺口**，不是原始数据丢失。

这个修正未处理多来源语义合并、关系归因、历史化候选或自动去重；因此不能据此说五案已经得到完整范围规划。原 `part2_scope_planner/plan.py` 未修改，实验副本未接入运行链。原始回放、Susan 属性映射调整后的回放和实验副本结果分别保留，不覆盖历史结果。

现有规则对状态变化与历史纠错使用同一个严格修改门槛；对于晋升和转岗，可研究增加**不指定生效日、不执行写入的待审核状态进展/历史化候选**。应先由你确认范围语义，再用独立案例检验，不宜直接把 possible_change 当作纠正或自行关闭时间区间。

## 待你确认的金标准边界

1. Susan 的求职情境是否作为独立新增单元，还是与旧支持事实合并；ThomasSusan / Susan 身份歧义如何记录。
2. 晋升与转岗在未知准确生效日时，是否应提出“旧状态历史化”候选，以及希望保留哪些相对先后信息；不能把候选等同执行修改。
3. 模拟跳伞是否需要对旧宽泛当前偏好提出范围限定，以及保留旧风险理由的粒度。
4. Donald 获客与两人集体人脉作用的独立新增粒度和跨句关系；不能按个人分别归因，也不能推断客户数量或获客日。

验证：现有规划器离线测试 37 项、实验副本针对多来源及上游失败的测试 3 项；逐案引文与来源追溯及改动范围另见 `verification.json`。本次无模型、Mem0 或知识库调用。
