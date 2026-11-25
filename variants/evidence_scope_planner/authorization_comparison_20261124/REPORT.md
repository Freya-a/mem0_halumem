# 离线授权方式对照：五案开发诊断

## 边界和结果

本报告只读取五次已保存模型响应，没有调用模型或 API，没有写入 Mem0 或真实记忆。五案用于开发诊断，不是论文准确率，也不是用户确认的金标准。三组调用同一份 v3 `build_scope_plan()`；A 的结果逐案与原 v3 unprotected 保存结果逐字节结构比对一致。C 的旧记忆及所选新证据文本、来源与模型所用案例一致，但 C 使用独立的人工对齐和人工事实拆分。

A 保持 v3 的独立语义授权门槛；B 仅在主引文可定位且绑定来源/单元后，将模型判断作为候选送入同一规划器，并保留规划器原有来源、范围、模态和时间检查；C 使用现有人工核对对齐输入。B 为适配 v3 的布尔门槛而写入内部 `semantic_support=supported`，这个值在 B **只表示模型候选**，不是独立授权，也不是语义正确证明；v3 原样输出的“independent evidence-supported”“evidenced later state”等理由在 B 亦不能当作独立审核结论。B 的任何动作都不能直接写入真实记忆。

B 对每个原有关系保留独立候选；对于模型 `change`，另从同一条模型记录投影新侧断言，不从预期或外部上下文补事实。仅按原 `new_value` 中字面分号拆分，后续部分必须在已绑定的新引文中逐字出现；`same_as_old` 仅在模型本身提供明确旧条件时继承，否则标未知。新事实独立评估无需证明与旧事实的时间先后；旧关系仍保留原有的时间/范围检查。若同一模型记录已经提出修改，重复的新增会单列为抑制项。仅为旧状态关系所需的错误不会自动污染独立新断言，但其新侧引文及语义依据仍须通过绑定校验。

自动结果给出引用可定位、字段及规划动作；下文每条的正确性判断由研究者依据原文和既有审核另行人工核对，未用于生成 A/B 规划。已有人工预期与 C 同为人工材料，不能作独立模型输出或未经审定的真值。`AUDIT.json` 将每条核对绑定到计划与动作哈希；报告生成时检查哈希及原模型逐条审核哈希，结果变动必须重新核对。

| 案例 | A 修改/保留/待确认/新增 | B 修改/保留/待确认/新增 | C 修改/保留/待确认/新增 |
|---|---:|---:|---:|
| susan | 0/0/5/0 | 0/0/3/2 | 0/1/1/2 |
| promotion | 0/0/2/0 | 1/1/0/0 | 0/1/3/0 |
| career_history | 0/0/3/0 | 0/0/3/2 | 0/2/1/1 |
| transition | 0/0/3/0 | 0/0/1/2 | 0/1/3/1 |
| skydiving | 0/0/8/0 | 0/0/11/1 | 0/0/4/2 |

| 人工逐项判断 | A | B | C |
|---|---:|---:|---:|
| 正确修改 | 0 | 0 | 0 |
| 错误或无充分依据的修改 | 0 | 1 | 0 |
| 正确新增 | 0 | 1 | 6 |
| 错误或无充分依据的新增 | 0 | 4 | 0 |
| 新增部分有依据、完整候选不可直接接受 | 0 | 2 | 0 |
| 保留项主体有误 | 0 | 1 | 0 |

这些是人工对**产生的动作**的判断，不是模型事实覆盖率；“错误或无充分依据”表示当前材料不授权该完整动作，并非断言其现实中必假。B 另有转岗原始关系未进入任何输出分类，不能用 0 修改或新增数量掩盖。A/B 使用原 v3 未加附加保护投影，skydiving A 为 8 条待确认；与 v3 报告另列的 protected 投影的 4 条不可混数。

## susan

旧记忆（`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`）：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：

- `new-0`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.
- `new-2`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`）：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.
- `ctx-1`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [60:218]`）：ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.

已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：
- modify：无
- preserve：ThomasSusan/Susan 朋友关系、支持和鼓励
- uncertain：新证据没有独立确认全名与称呼的映射；旧来源 ctx-1 可支持语境但不消除命名歧义
- add：Daniel 的见解促进职业思考；工作生活平衡及人道目标为另行表达的内容
- missing：Susan 身份跨来源仅由上下文支持；新证据未明确朋友关系变化。

模型原始各条关系及此前独立逐条审核：

- 记录 0：关系 `same`，单元 `friendship`；主体/属性/值 `["ThomasSusan","name","ThomasSusan"]` → `["Susan","name","Susan"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"friend named ThomasSusan","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"explanation":"Both refer to current, ongoing friendship; no temporal shift indicated in either quote","relation":"same"}`；模型理由：The old unit identifies 'ThomasSusan' as a friend; the new unit refers to 'Susan' in identical relational and functional context (support/encouragement), and contextual source 'ctx-1' explicitly equates 'ThomasSusan' with 'Susan' ('ThomasSusan is my Friend, Susan's support...'). This confirms same person, same relationship.；模型未知项 `[]`。
  - 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship`：valid，位置 `{"end":30,"start":6}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`：「friend named ThomasSusan」；定位通过。
  - 引文 `new/new-2/manually_mapped_new`：valid，位置 `{"end":96,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`：「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」；定位通过。
  - 既有独立审核 `partially_supported`：旧记忆包含朋友 ThomasSusan，新话语有 Susan 的支持；但所引旧片段未体现别名，模型把 ctx-1 当未绑定的 semantic_basis，无法用已引用单元证明同一时间友谊及同值；无条件亦无依据。
  - 自动接口问题：`["records[0].semantic_basis[1] not bound to cited same-side source/quote"]`。
- 记录 1：关系 `supplement`，单元 `support`；主体/属性/值 `["Susan","provides support and encouragement","provides support and encouragement"]` → `["Susan","support and encouragement","has indeed been invaluable... helps me stay focused on my goals"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"}`；模型理由：New statement affirms and enriches the old claim: adds evaluative ('invaluable') and functional ('helps me stay focused on my goals') detail without contradicting or replacing it.；模型未知项 `[]`。
  - 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support`：valid，位置 `{"end":94,"start":60}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`：「provides support and encouragement」；定位通过。
  - 引文 `new/new-2/manually_mapped_new`：valid，位置 `{"end":96,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`：「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」；定位通过。
  - 既有独立审核 `partially_supported`：新话语确实描述 Susan 的鼓励与帮助专注，能补充支持细节；但同一时间、无条件适用并未证明，原单元短引文未独立表明对象。
- 记录 2：关系 `new_information`，单元 `None`；主体/属性/值 `[null,null,null]` → `["current role","supports well-being","not supporting my well-being as much as I'd like"]`；条件 `[{"kind":"unknown"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"my current role isn't supporting my well-being as much as I'd like","side":"new","source_id":"new-0"}],"explanation":"Describes present state of current role; no comparative temporal marker relative to past","relation":"same"}`；模型理由：This is a newly introduced evaluation of the user's current job — not referenced in any old unit. It asserts a deficit in well-being support, which is novel information.；模型未知项 `[]`。
  - 引文 `new/new-0/unsplit-new-0`：valid，位置 `{"end":138,"start":72}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`：「my current role isn't supporting my well-being as much as I'd like」；定位通过。
  - 既有独立审核 `partially_supported`：用户确实称当前角色对福祉支持不及期望，可作为独立陈述；无旧单元却给新旧时间关系 same，且 unconditional 缺充分依据。
- 记录 3：关系 `new_information`，单元 `None`；主体/属性/值 `[null,null,null]` → `["I","career goal","find a new job that offers a better work-life balance and aligns with my humanitarian goals"]`；条件 `[{"kind":"unknown"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job...","side":"new","source_id":"new-0"}],"explanation":"The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment.","relation":"after"}`；模型理由：This expresses an active intention (‘crucial for me to find’) — a forward-looking plan, not yet realized. No prior mention of humanitarian goals or work-life balance as career criteria exists in old units.；模型未知项 `[]`。
  - 引文 `new/new-0/unsplit-new-0`：valid，位置 `{"end":255,"start":140}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`：「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」；定位通过。
  - 既有独立审核 `partially_supported`：找符合平衡和人道目标的新工作是愿望/计划，不是已完成；但 after 只比较该句内心理活动，不是相对旧事实，所引时间依据还含省略号且不在已引用片段内。
  - 自动接口问题：`["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"]`。

B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：

- 本案无从 change 投影的新侧候选。

### A 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（5）

1. `support` / `supplement`：旧值 `"provides support and encouragement"` → 新值 `"has indeed been invaluable... helps me stay focused on my goals"`；主体 `"Susan"`，属性 `"support and encouragement"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / support，valid，位置 {"end":94,"start":60}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「provides support and encouragement」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**暂缓**。Susan 的鼓励和专注子事实有原话支持；此记录没有独立授权，旧关系与新增应分开。
2. `None` / `new_information`：旧值 `null` → 新值 `"not supporting my well-being as much as I'd like"`；主体 `"current role"`，属性 `"supports well-being"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / unsplit-new-0，valid，位置 {"end":138,"start":72}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，原文「my current role isn't supporting my well-being as much as I'd like」。
   人工判断：**暂缓**。当前角色福祉支持不足有原话支持，但模型输出没有独立授权。
3. `None` / `new_information`：旧值 `null` → 新值 `"find a new job that offers a better work-life balance and aligns with my humanitarian goals"`；主体 `"I"`，属性 `"career goal"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：new new-0 / unsplit-new-0，valid，位置 {"end":255,"start":140}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，原文「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」。
   人工判断：**暂缓**。求职意向有原话支持；时间依据含省略号且未绑定，不能当作已完成。
4. `friendship` / `same`：旧值 `"ThomasSusan"` → 新值 `"Susan"`；主体 `"ThomasSusan"`，属性 `"name"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].semantic_basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / friendship，valid，位置 {"end":30,"start":6}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「friend named ThomasSusan」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**暂缓**。主引文可定位，但 ctx-1 不属于该记录关联的旧单元引文，姓名映射仍须核对。
5. `support` / `supplement`：旧值 `"provides support and encouragement"` → 新值 `"has indeed been invaluable... helps me stay focused on my goals"`；主体 `"Susan"`，属性 `"provides support and encouragement"`，范围 `{"kind":"unconditional"}`。
   规划器理由：impact of new information on old fact is not established；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / support，valid，位置 {"end":94,"start":60}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「provides support and encouragement」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**暂缓**。支持的新细节不自动证明整个旧友谊关系在所有条件下不受影响。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### B 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（3）

1. `None` / `new_information`：旧值 `null` → 新值 `"find a new job that offers a better work-life balance and aligns with my humanitarian goals"`；主体 `"I"`，属性 `"career goal"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：new new-0 / unsplit-new-0，valid，位置 {"end":255,"start":140}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，原文「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」。
   人工判断：**暂缓**。找工作是计划；模型时间依据不是逐字引用且没有旧状态可比较，暂缓是结构层结果。
2. `friendship` / `same`：旧值 `"ThomasSusan"` → 新值 `"Susan"`；主体 `"ThomasSusan"`，属性 `"name"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].semantic_basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / friendship，valid，位置 {"end":30,"start":6}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「friend named ThomasSusan」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**暂缓**。旧单元与新话语各有引文，但 ctx-1 语义依据未绑定；不能据此直接确定名字及友谊同值。
3. `support` / `supplement`：旧值 `"provides support and encouragement"` → 新值 `"has indeed been invaluable... helps me stay focused on my goals"`；主体 `"Susan"`，属性 `"provides support and encouragement"`，范围 `{"kind":"unconditional"}`。
   规划器理由：impact of new information on old fact is not established；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / support，valid，位置 {"end":94,"start":60}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「provides support and encouragement」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**暂缓**。新支持细节不能自动证明旧事实在所有范围都无影响。

**add**（2）

1. `support` / `supplement`：旧值 `"provides support and encouragement"` → 新值 `"has indeed been invaluable... helps me stay focused on my goals"`；主体 `"Susan"`，属性 `"support and encouragement"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / support，valid，位置 {"end":94,"start":60}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「provides support and encouragement」；new new-2 / manually_mapped_new，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**部分有依据，限定或属性有问题**。Susan 的支持和帮助专注有依据；unconditional 及该结构化关系的完整适用范围并未独立证实。
2. `None` / `new_information`：旧值 `null` → 新值 `"not supporting my well-being as much as I'd like"`；主体 `"current role"`，属性 `"supports well-being"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / unsplit-new-0，valid，位置 {"end":138,"start":72}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，原文「my current role isn't supporting my well-being as much as I'd like」。
   人工判断：**新增有依据**。用户明确说当前角色对福祉支持不如希望；这里仅按当前角色和相对期望理解，不推定永久状态。

可编辑位置：`[]`；保护事实：`[]`。

### C 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（1）

1. `support` / `same`：旧值 `"support and encouragement"` → 新值 `"support and encouragement"`；主体 `"user"`，属性 `"relationship.support"`，范围 `{"kind":"unconditional"}`。
   规划器理由：same value supported by new evidence；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / support，valid，位置 {"end":94,"start":60}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「provides support and encouragement」；new new-2 / support，valid，位置 {"end":96,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
   人工判断：**有依据**。人工输入明确对齐 Susan 的支持和鼓励；原记忆和新用户话语均支持该子事实。

**uncertain**（1）

1. `friendship` / `unknown`：旧值 `"friend named ThomasSusan"` → 新值 `"Susan provides support"`；主体 `"user"`，属性 `"relationship.friendship"`，范围 `null`。
   规划器理由：新话语支持 Susan 的支持，但未独立明确重新确认朋友关系；原句仍可保留，姓名指代依据旧来源。; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old a1332815-d6ba-4bdc-9ffa-657f7315d0ed / friendship，valid，位置 {"end":30,"start":6}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，原文「friend named ThomasSusan」；new new-2 / friendship，valid，位置 {"end":43,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Susan's support has indeed been invaluable.」。
   人工判断：**暂缓**。Susan 与 ThomasSusan 的跨源身份、朋友关系当前状态仍须核对。

**add**（2）

1. `None` / `supplement`：旧值 `null` → 新值 `"insights helped career thinking"`；主体 `"user"`，属性 `"relationship.Daniel"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-2 / None，valid，位置 {"end":179,"start":101}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，原文「Daniel's insights have really pushed me to think outside the box in my career.」。
   人工判断：**新增有依据**。Daniel 的见解推动职业思考有对应用户原话。
2. `None` / `plan`：旧值 `null` → 新值 `"find a new job offering better work-life balance and alignment with humanitarian goals"`；主体 `"user"`，属性 `"career.job_search"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / None，valid，位置 {"end":255,"start":140}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，原文「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」。
   人工判断：**新增有依据**。找更好平衡并符合人道目标的工作是计划，输出保留 planned 模态。

可编辑位置：`[]`；保护事实：`[]`。

### 差异与仍需处理

- 子事实及依据：S0 名字/朋友；S1 Susan 支持；S2 当前角色福祉；S3 求职计划；new-2 同句 Daniel 的见解被模型遗漏。
- 应处理但暂缓或未覆盖：A 暂缓支持、当前角色和求职计划；B 仍暂缓计划（无效时间依据），且没有 Daniel 候选；C 独立加入 Daniel 与计划。
- A/B 差异及风险：B 不再要求独立授权，故产生两个新增候选；两项分别审核，不能据此把友情/身份设为同值。
- 人工依赖及 C 的诊断作用：C 的身份、Daniel、计划拆分来自既存人工对齐；B 只复制模型字段与引用。

## promotion

旧记忆（`e13b825e-7ec7-4760-821e-0581d8da5650`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`）：Works at Historical Productions Ltd. as a Director

关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：

- `new-0`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：
- modify：职位细化为晋升后的 lead director
- preserve：Historical Productions Ltd. 雇主关系；Director 作为历史和可能仍成立的宽泛描述
- uncertain：准确晋升日期未知；宽泛 Director 与 lead director 的逻辑包含关系不由代码推理
- add：晋升 lead director 的事实
- missing：记录时间不是生效时间。

模型原始各条关系及此前独立逐条审核：

- 记录 0：关系 `same`，单元 `employer`；主体/属性/值 `["Historical Productions Ltd.","employer","Historical Productions Ltd."]` → `["Historical Productions Ltd.","employer","Historical Productions Ltd."]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","side":"new","source_id":"new-0"}],"explanation":"The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated.","relation":"same"}`；模型理由：The new utterance explicitly names 'Historical Productions Ltd.' as the employer in the context of a recent promotion, confirming continuity of employer affiliation.；模型未知项 `[]`。
  - 引文 `old/e13b825e-7ec7-4760-821e-0581d8da5650/employer`：valid，位置 `{"end":36,"start":9}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`：「Historical Productions Ltd.」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":92,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`：「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」；定位通过。
  - 既有独立审核 `partially_supported`：引文确实显示同一公司出现在旧文和晋升句；但 employer 的主体误写公司本身而非 user，单凭未提变化不足以证明旧新状态同时或 unconditional。
- 记录 1：关系 `change`，单元 `title`；主体/属性/值 `["user","title","Director"]` → `["user","title","lead director"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"I recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director').","relation":"after"}`；模型理由：The new utterance states a promotion occurred, and specifies the resulting title as 'lead director', which supersedes the prior 'Director' title. 'Lead director' is a more senior role than 'Director', consistent with promotion semantics.；模型未知项 `[]`。
  - 引文 `old/e13b825e-7ec7-4760-821e-0581d8da5650/title`：valid，位置 `{"end":50,"start":42}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`：「Director」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":92,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`：「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」；定位通过。
  - 既有独立审核 `partially_supported`：旧文 Director 与新话语 lead director 的晋升均有来源；recently 只相对说话时间，不能证明该晋升晚于旧记忆事实有效期，更不能自动否定 Director 作为宽泛称谓。

B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：

- `B:model_record=1;candidate=new_subfact;part=0`：主体 `"user"`，属性 `"title"`，值 `"lead director"`，条件 `{"kind":"unconditional"}`，模态 `"asserted"`，新引文 `[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","source_id":"new-0","unit_id":"manually_mapped_new"}]`，语义依据 `[{"quote":"I recently got promoted to lead director","side":"new","source_id":"new-0"}]`，校验错误 `[]`。
- 抑制的重复新增：`B:model_record=1;candidate=new_subfact;part=0` / `"lead director"`；same model record already proposed as modify; avoid duplicate add。

### A 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（2）

1. `employer` / `same`：旧值 `"Historical Productions Ltd."` → 新值 `"Historical Productions Ltd."`；主体 `"Historical Productions Ltd."`，属性 `"employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / employer，valid，位置 {"end":36,"start":9}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Historical Productions Ltd.」；new new-0 / manually_mapped_new，valid，位置 {"end":92,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
   人工判断：**暂缓**。公司名重现，但模型把公司当主体，且没有独立语义授权。
2. `title` / `change`：旧值 `"Director"` → 新值 `"lead director"`；主体 `"user"`，属性 `"title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / title，valid，位置 {"end":50,"start":42}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Director」；new new-0 / manually_mapped_new，valid，位置 {"end":92,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
   人工判断：**暂缓**。晋升已发生，但 recently 不证明其晚于旧记忆有效期，宽泛 Director 未必失效。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### B 组：实际计划及人工核对

**modify**（1）

1. `title` / `change`：旧值 `"Director"` → 新值 `"lead director"`；主体 `"user"`，属性 `"title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：different values and evidenced later state；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / title，valid，位置 {"end":50,"start":42}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Director」；new new-0 / manually_mapped_new，valid，位置 {"end":92,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
   人工判断：**修改无充分依据**。recently 只相对发话，不证明晋升晚于旧记忆有效期；lead director 不必否定宽泛 Director。此修改缺依据，并非证明晋升为假。

**preserve**（1）

1. `employer` / `same`：旧值 `"Historical Productions Ltd."` → 新值 `"Historical Productions Ltd."`；主体 `"Historical Productions Ltd."`，属性 `"employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：same value supported by new evidence；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / employer，valid，位置 {"end":36,"start":9}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Historical Productions Ltd.」；new new-0 / manually_mapped_new，valid，位置 {"end":92,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
   人工判断：**保留项的主体错误**。公司名虽相同，但模型把公司本身写成 employer 主体，不能认证为用户雇主关系。

**uncertain**（0）

无。

**add**（0）

无。

可编辑位置：`[{"end":50,"old_quote":"Director","start":42,"unit_id":"title"}]`；保护事实：`[]`。

### C 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（1）

1. `employer` / `same`：旧值 `"Historical Productions Ltd."` → 新值 `"Historical Productions Ltd."`；主体 `"user"`，属性 `"employment.employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：same value supported by new evidence；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / employer，valid，位置 {"end":36,"start":9}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Historical Productions Ltd.」；new new-0 / employer，valid，位置 {"end":71,"start":27}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「lead director at Historical Productions Ltd.」。
   人工判断：**有依据**。人工输入将用户作为主体，同一公司名由旧文及晋升话语支持。

**uncertain**（3）

1. `title` / `change`：旧值 `"Director"` → 新值 `"lead director"`；主体 `"user"`，属性 `"employment.title"`，范围 `null`。
   规划器理由：晋升具体生效日期未知。；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / title，valid，位置 {"end":50,"start":42}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Director」；new new-0 / title，valid，位置 {"end":40,"start":15}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「promoted to lead director」。
   人工判断：**暂缓**。确切晋升日未知；这不否认晋升已发生，也非所有操作都需要具体日期。
2. `title` / `change`：旧值 `"Director"` → 新值 `"lead director"`；主体 `"user"`，属性 `"employment.title"`，范围 `null`。
   规划器理由：Director 作为当前宽泛职位称谓是否仍成立无法仅靠字符串比较判断。；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / title，valid，位置 {"end":50,"start":42}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Director」；new new-0 / title，valid，位置 {"end":40,"start":15}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「promoted to lead director」。
   人工判断：**暂缓**。Director 是否仍是宽泛描述不能仅靠字符串推断。
3. `title` / `change`：旧值 `"Director"` → 新值 `"lead director"`；主体 `"user"`，属性 `"employment.title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：temporal order unknown；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e13b825e-7ec7-4760-821e-0581d8da5650 / title，valid，位置 {"end":50,"start":42}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，原文「Director」；new new-0 / title，valid，位置 {"end":40,"start":15}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，原文「promoted to lead director」。
   人工判断：**暂缓**。缺独立的相对旧事实先后依据，因此不覆盖旧状态。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### 差异与仍需处理

- 子事实及依据：同一公司名与晋升事件可从新句读取；Director 宽泛称谓、旧有效时间须另判。
- 应处理但暂缓或未覆盖：A/C 暂缓覆盖；B 提出无充分时间依据的修改，关联新值候选为避免重复被抑制，故不等于安全记录了晋升事件。
- A/B 差异及风险：B 机械接受模型 after 和主体字段，产生错误修改候选与主体错误的保留；C 同雇主主体来自人工核对。
- 人工依赖及 C 的诊断作用：人工 C 判断雇主不变并保留具体不确定；B 的 after 完全来自模型。

## career_history

旧记忆（`05afde13-35bd-4d26-bbae-6de427d58db1`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`）：Previously worked as a senior developer in Blockchain Tech

关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：

- `new-0`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- `new-2`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`）：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.

已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：
- modify：无
- preserve：曾在 Blockchain Tech 任 senior developer 的历史
- uncertain：具体离职或转型时间、当前雇佣关系及公司所有权细节
- add：咨询公司获得初始客户
- missing：本会话没有给出具体离职日期或直接否定历史。

模型原始各条关系及此前独立逐条审核：

- 记录 0：关系 `change`，单元 `employer`；主体/属性/值 `["I","employer","Blockchain Tech"]` → `["I","current employer / business ownership","consulting firm"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role.","relation":"after"}`；模型理由：New utterance asserts active operation of a consulting firm with secured clients, incompatible with ongoing employment as a senior developer at Blockchain Tech. The shift from 'worked as' (past) to 'my consulting firm' (present possessive + active milestone) signals career transition.；模型未知项 `[]`。
  - 引文 `old/05afde13-35bd-4d26-bbae-6de427d58db1/employer`：valid，位置 `{"end":58,"start":43}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`：「Blockchain Tech」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":103,"start":48}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`：「my consulting firm finally secured some initial clients」；定位通过。
  - 既有独立审核 `unsupported`：新句只说咨询公司获初始客户；不能由此推断本人所有权、正在经营、旧雇佣已结束或互不兼容，也不能由 lately/finally 判其晚于旧事实。旧整句及新前缀被用作时间依据但不在关联短引文内。
  - 自动接口问题：`["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]`。
- 记录 1：关系 `change`，单元 `title`；主体/属性/值 `["I","job title","senior developer"]` → `["I","current role","founder / operator of consulting firm"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct.","relation":"after"}`；模型理由：Possessive 'my consulting firm' and achievement of client acquisition imply founder/operator status, replacing prior employee title. No evidence of concurrent roles; 'Previously worked' implies discontinuation.；模型未知项 `[]`。
  - 引文 `old/05afde13-35bd-4d26-bbae-6de427d58db1/title`：valid，位置 `{"end":39,"start":23}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`：「senior developer」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":103,"start":48}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`：「my consulting firm finally secured some initial clients」；定位通过。
  - 既有独立审核 `unsupported`：新句未给出本人咨询公司的 founder/operator 职位，不能由 my firm 推断创办者或经营者，更不能得出前职位被替代；时间依据也超出已引用片段。
  - 自动接口问题：`["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]`。
- 记录 2：关系 `new_information`，单元 `None`；主体/属性/值 `[null,null,null]` → `["I","network contacts",["MooreSandra","GonzalezMary"]]`；条件 `[{"kind":"unknown"},{"kind":"unconditional"}]`；时序 `{"basis":[],"explanation":null,"relation":"unknown"}`；模型理由：Names 'MooreSandra' and 'GonzalezMary' are explicitly named as instrumental contacts whose connections enabled new opportunities; no prior mention in old memory units.；模型未知项 `[]`。
  - 引文 `new/new-2/unsplit-new-2`：valid，位置 `{"end":111,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`：「MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.」；定位通过。
  - 既有独立审核 `partially_supported`：两位联系人和其联系开门得到用户原句支持，但 new_value 输出数组不符合字符串/null 结构，且 unconditional 未给出完整依据。
  - 自动接口问题：`["records[2].new_value must be nonempty text or null (unknown)"]`。

B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：

- `B:model_record=0;candidate=new_subfact;part=0`：主体 `"I"`，属性 `"current employer / business ownership"`，值 `"consulting firm"`，条件 `{"kind":"unconditional"}`，模态 `"asserted"`，新引文 `[{"quote":"my consulting firm finally secured some initial clients","source_id":"new-0","unit_id":"manually_mapped_new"}]`，语义依据 `[{"quote":"my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}]`，校验错误 `[]`。
- `B:model_record=1;candidate=new_subfact;part=0`：主体 `"I"`，属性 `"current role"`，值 `"founder / operator of consulting firm"`，条件 `{"kind":"unconditional"}`，模态 `"asserted"`，新引文 `[{"quote":"my consulting firm finally secured some initial clients","source_id":"new-0","unit_id":"manually_mapped_new"}]`，语义依据 `[{"quote":"my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}]`，校验错误 `[]`。

### A 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（3）

1. `None` / `new_information`：旧值 `null` → 新值 `null`；主体 `"I"`，属性 `"network contacts"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']；缺失 `[]`；校验错误 `["records[2].new_value must be nonempty text or null (unknown)"]`；未知项 `[]`。
   引文：new new-2 / unsplit-new-2，valid，位置 {"end":111,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`，原文「MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.」。
   人工判断：**暂缓**。联系人是列表类型，不符合接口标量值；两人帮助的子事实原文可支持。
2. `employer` / `change`：旧值 `"Blockchain Tech"` → 新值 `"consulting firm"`；主体 `"I"`，属性 `"employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / employer，valid，位置 {"end":58,"start":43}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「Blockchain Tech」；new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**暂缓**。公司获客不证明当前雇主、所有权或旧雇佣终止，时间依据又未绑定。
3. `title` / `change`：旧值 `"senior developer"` → 新值 `"founder / operator of consulting firm"`；主体 `"I"`，属性 `"job title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / title，valid，位置 {"end":39,"start":23}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「senior developer」；new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**暂缓**。用户未声称创办或经营公司；旧职位被替代及时间依据均未证明。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### B 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（3）

1. `None` / `new_information`：旧值 `null` → 新值 `null`；主体 `"I"`，属性 `"network contacts"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']；缺失 `[]`；校验错误 `["records[2].new_value must be nonempty text or null (unknown)"]`；未知项 `[]`。
   引文：new new-2 / unsplit-new-2，valid，位置 {"end":111,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`，原文「MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.」。
   人工判断：**暂缓**。联系人 new_value 为数组，不能冒充合法标量字段；两人帮助的事实有依据。
2. `employer` / `change`：旧值 `"Blockchain Tech"` → 新值 `"consulting firm"`；主体 `"I"`，属性 `"employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / employer，valid，位置 {"end":58,"start":43}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「Blockchain Tech」；new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**暂缓**。旧新属性不一致，时间依据未绑定；获客不改变过去雇主的事实。
3. `title` / `change`：旧值 `"senior developer"` → 新值 `"founder / operator of consulting firm"`；主体 `"I"`，属性 `"job title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / title，valid，位置 {"end":39,"start":23}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「senior developer」；new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**暂缓**。时间依据未绑定且 founder/operator 不受证据支持，旧职称不应修改。

**add**（2）

1. `None` / `new_information`：旧值 `null` → 新值 `"consulting firm"`；主体 `"I"`，属性 `"current employer / business ownership"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**新增无充分依据**。my consulting firm 获客不证明用户现在以其为雇主或具有公司所有权。
2. `None` / `new_information`：旧值 `null` → 新值 `"founder / operator of consulting firm"`；主体 `"I"`，属性 `"current role"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**新增无充分依据**。原文未证明 founder/operator 职位；不能从公司获客反推。

可编辑位置：`[]`；保护事实：`[]`。

### C 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（2）

1. `employer` / `unrelated`：旧值 `"Blockchain Tech"` → 新值 `"secured initial clients"`；主体 `"user"`，属性 `"career.historical_employer"`，范围 `{"kind":"unconditional"}`。
   规划器理由：unchanged, earlier evidence, or outside evidence scope；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / employer，valid，位置 {"end":58,"start":43}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「Blockchain Tech」；new new-0 / employer，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**有依据**。此前 Blockchain Tech 雇主经历为旧记忆的历史事实。
2. `title` / `unrelated`：旧值 `"senior developer"` → 新值 `"secured initial clients"`；主体 `"user"`，属性 `"career.historical_title"`，范围 `{"kind":"unconditional"}`。
   规划器理由：unchanged, earlier evidence, or outside evidence scope；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / title，valid，位置 {"end":39,"start":23}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「senior developer」；new new-0 / title，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**有依据**。此前 senior developer 职位为旧记忆的历史事实。

**uncertain**（1）

1. `employer` / `unrelated`：旧值 `"Blockchain Tech"` → 新值 `"secured initial clients"`；主体 `"user"`，属性 `"career.historical_employer"`，范围 `null`。
   规划器理由：具体离职或转型时间未知；咨询公司获客不证明当前雇佣关系或所有权细节。；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old 05afde13-35bd-4d26-bbae-6de427d58db1 / employer，valid，位置 {"end":58,"start":43}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，原文「Blockchain Tech」；new new-0 / employer，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**暂缓**。离职和转型日期、现职以及所有权细节没有足够证据。

**add**（1）

1. `None` / `supplement`：旧值 `null` → 新值 `"secured initial clients"`；主体 `"user"`，属性 `"career.consulting_firm"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / None，valid，位置 {"end":103,"start":48}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，原文「my consulting firm finally secured some initial clients」。
   人工判断：**新增有依据**。用户说咨询公司获得初始客户；不由此推断用户的所有权或职位。

可编辑位置：`[]`；保护事实：`[]`。

### 差异与仍需处理

- 子事实及依据：用户说咨询公司获初始客户；MooreSandra、GonzalezMary 的联系提供帮助。旧文记的是此前技术职位。
- 应处理但暂缓或未覆盖：模型未把获客独立生成正确的结构化候选；联系人值数组未过字段检查；A/B 对旧工作变更继续暂缓。
- A/B 差异及风险：B 从两条 change 拆出新侧候选，但继承模型臆造的当前雇主/创办经营关系，因此出现两个错误新增；C 只新增获客并保留旧历史。
- 人工依赖及 C 的诊断作用：C 的历史保留、获客拆分和身份边界是先前人工核对；B 不借用它们。

## transition

旧记忆（`e6ab178b-c0f9-4adb-bfb7-e4648617a950`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`）：Looking for a new job with better work-life balance

关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：

- `new-0`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`）：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.

已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：
- modify：求职进展改为已经转到新职位，不断言停止任何求职
- preserve：追求较好工作生活平衡的旧目标
- uncertain：新职位名称和实际切换日期；是否继续另找工作
- add：新职位工作生活平衡改善
- missing：没有具体职位名或事实生效日期。

模型原始各条关系及此前独立逐条审核：

- 记录 0：关系 `change`，单元 `job_search`；主体/属性/值 `["I","job search status","looking for a new job with better work-life balance"]` → `["I","job search status","transitioned to a new role with healthier work-life balance"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"Looking for a new job with better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"},{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'","relation":"after"}`；模型理由：The old unit states an active job search motivated by work-life balance; the new unit asserts successful transition to a role delivering that balance — a direct change in status.；模型未知项 `[]`。
  - 引文 `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：valid，位置 `{"end":51,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`：「Looking for a new job with better work-life balance」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":135,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`：「I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.」；定位通过。
  - 既有独立审核 `partially_supported`：已转岗和平衡改善有新引文；finally 不单独证明切换晚于旧记忆有效期，也不证明停止找工作，且 unconditional 和完整替换旧求职状态缺依据。
- 记录 1：关系 `supplement`，单元 `job_search`；主体/属性/值 `["I","motivation for job search","better work-life balance"]` → `["I","motivation for job search","better work-life balance (now realized as healthier balance)"]`；条件 `[{"kind":"unconditional"},{"kind":"unconditional"}]`；时序 `{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"}`；模型理由：The new utterance confirms the original goal ('better work-life balance') has been achieved ('much healthier now'), supplementing the old unit with outcome evidence without altering the core motivational attribute.；模型未知项 `[]`。
  - 引文 `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：valid，位置 `{"end":51,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`：「Looking for a new job with better work-life balance」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":135,"start":70}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`：「The balance between work and personal life is much healthier now.」；定位通过。
  - 既有独立审核 `partially_supported`：新话语确实称现在平衡更健康；是否完全实现此前目标、此前和现在动机同一时间及 unconditional 未证明。

B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：

- `B:model_record=0;candidate=new_subfact;part=0`：主体 `"I"`，属性 `"job search status"`，值 `"transitioned to a new role with healthier work-life balance"`，条件 `{"kind":"unconditional"}`，模态 `"asserted"`，新引文 `[{"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","source_id":"new-0","unit_id":"manually_mapped_new"}]`，语义依据 `[{"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}]`，校验错误 `[]`。
- 原关系记录 0 未单独出现在任何动作中：planner output contains no decision for this original relation; inspect same-unit aggregation and source record。此为输出覆盖缺口，不等同已经拒绝或接受修改。

### A 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（3）

1. `job_search` / `supplement`：旧值 `"better work-life balance"` → 新值 `"better work-life balance (now realized as healthier balance)"`；主体 `"I"`，属性 `"motivation for job search"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":51,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job with better work-life balance」；new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":70}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「The balance between work and personal life is much healthier now.」。
   人工判断：**暂缓**。平衡更健康有依据，但是否完全实现此前目标及适用范围未获独立授权。
2. `job_search` / `change`：旧值 `"looking for a new job with better work-life balance"` → 新值 `"transitioned to a new role with healthier work-life balance"`；主体 `"I"`，属性 `"job search status"`，范围 `{"kind":"unconditional"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":51,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job with better work-life balance」；new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.」。
   人工判断：**暂缓**。转岗已发生；是否晚于旧事实、是否停止找工作均未证明。
3. `job_search` / `supplement`：旧值 `"better work-life balance"` → 新值 `"better work-life balance (now realized as healthier balance)"`；主体 `"I"`，属性 `"motivation for job search"`，范围 `{"kind":"unconditional"}`。
   规划器理由：impact of new information on old fact is not established；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":51,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job with better work-life balance」；new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":70}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「The balance between work and personal life is much healthier now.」。
   人工判断：**暂缓**。新增改善与旧目标是否仍有效是两个判断；旧目标不可自动删除。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### B 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（1）

1. `job_search` / `supplement`：旧值 `"better work-life balance"` → 新值 `"better work-life balance (now realized as healthier balance)"`；主体 `"I"`，属性 `"motivation for job search"`，范围 `{"kind":"unconditional"}`。
   规划器理由：impact of new information on old fact is not established；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":51,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job with better work-life balance」；new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":70}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「The balance between work and personal life is much healthier now.」。
   人工判断：**暂缓**。新改善不自动证明旧平衡目标失效或已完全实现。

**add**（2）

1. `job_search` / `supplement`：旧值 `"better work-life balance"` → 新值 `"better work-life balance (now realized as healthier balance)"`；主体 `"I"`，属性 `"motivation for job search"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":51,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job with better work-life balance」；new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":70}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「The balance between work and personal life is much healthier now.」。
   人工判断：**新增无充分依据**。原话只说平衡更健康；模型结构称原目标已实现，证据不证明达到原目标。
2. `None` / `new_information`：旧值 `null` → 新值 `"transitioned to a new role with healthier work-life balance"`；主体 `"I"`，属性 `"job search status"`，范围 `{"kind":"unconditional"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":135,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.」。
   人工判断：**部分有依据，限定或属性有问题**。转岗与平衡更健康都有原话支持；但以 job search status 表述容易暗示停止求职，且适用范围未核实。

可编辑位置：`[]`；保护事实：`[]`。

### C 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（1）

1. `job_search` / `None`：旧值 `null` → 新值 `null`；主体 `null`，属性 `null`，范围 `null`。
   规划器理由：explicit protected claim；缺失 `null`；校验错误 `null`；未知项 `null`。
   引文：无。
   人工判断：**有依据**。原句中的更好工作生活平衡目标已作为明确保护事实。

**uncertain**（3）

1. `job_search` / `change`：旧值 `"looking for a new job"` → 新值 `"transitioned to a new role"`；主体 `"user"`，属性 `"career.transition_status"`，范围 `null`。
   规划器理由：转岗后是否继续寻找工作未知；不应将转岗解释为不再求职。；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":21,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job」；new new-0 / job_search，valid，位置 {"end":39,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「I've finally transitioned to a new role」。
   人工判断：**暂缓**。转岗后是否继续找工作未知。
2. `job_search` / `change`：旧值 `"looking for a new job"` → 新值 `"transitioned to a new role"`；主体 `"user"`，属性 `"career.transition_status"`，范围 `null`。
   规划器理由：职位切换的具体生效日期未知。；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":21,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job」；new new-0 / job_search，valid，位置 {"end":39,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「I've finally transitioned to a new role」。
   人工判断：**暂缓**。职位切换生效的具体日期未知。
3. `job_search` / `change`：旧值 `"looking for a new job"` → 新值 `"transitioned to a new role"`；主体 `"user"`，属性 `"career.transition_status"`，范围 `{"kind":"unconditional"}`。
   规划器理由：temporal order unknown；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e6ab178b-c0f9-4adb-bfb7-e4648617a950 / job_search，valid，位置 {"end":21,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，原文「Looking for a new job」；new new-0 / job_search，valid，位置 {"end":39,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「I've finally transitioned to a new role」。
   人工判断：**暂缓**。转岗相对于旧记忆事实的先后不足以直接覆盖旧求职状态。

**add**（1）

1. `None` / `supplement`：旧值 `null` → 新值 `"balance much healthier"`；主体 `"user"`，属性 `"career.work_life_balance"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / None，valid，位置 {"end":135,"start":70}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，原文「The balance between work and personal life is much healthier now.」。
   人工判断：**新增有依据**。用户明确说工作和生活的平衡现在更健康；不推断目标已完全实现。

可编辑位置：`[]`；保护事实：`[{"fact":"求职时追求更好的工作生活平衡","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","old_position":{"end":51,"start":27},"old_quote":"better work-life balance","old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","reason":"explicit protected claim","unit_id":"job_search"}]`。

### 差异与仍需处理

- 子事实及依据：用户说已经转岗，且现在工作与生活的平衡更健康；旧求职目标是否停止并未说明。
- 应处理但暂缓或未覆盖：A 对旧状态及新改善均暂缓；B 的旧 change 关系在 v3 同单元聚合时未单独出现在输出中，不能误称已判断；C 保护旧平衡并记录改善。
- A/B 差异及风险：B 产生两个新增候选，其一把更健康推为目标实现，另一事件值有依据但属性写作求职状态；C 的事实拆分来自人工。
- 人工依赖及 C 的诊断作用：C 保护目标和单独改善是既有人工输入；原模型 after 不能由 finally 自动证实。

## skydiving

旧记忆（`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`）：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：

- `new-0`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
- `new-2`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`）：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
- `new-8`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`）：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.
- `ctx-1`（user，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json#/raw_dialogue/6/content [0:169]`）：I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.

已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：
- modify：无
- preserve：旧极限运动顾虑、受伤风险和安全福祉取向；不要推广为所有偏好已改变
- uncertain：模拟跳伞与旧极限运动的覆盖关系、当前真实跳伞偏好；u3 短引文本身不完整
- add：尝试模拟跳伞且感觉刺激；仍重视安全
- missing：没有确定的事实有效日期；模拟体验不证明真实跳伞偏好变化。

模型原始各条关系及此前独立逐条审核：

- 记录 0：关系 `change`，单元 `u1`；主体/属性/值 `["I","attitude toward extreme sports (e.g., skydiving)","dislikes"]` → `["I","attitude toward extreme sports (e.g., skydiving)","found simulated skydiving thrilling; more open to trying new things"]`；条件 `[{"kind":"unconditional"},{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}]`；时序 `{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"}`；模型理由：The new statements report direct positive affect ('thrilling', 'enjoy') toward a skydiving-adjacent activity under controlled conditions, directly contradicting the prior categorical dislike — but only for simulated, not real, skydiving.；模型未知项 `[]`。
  - 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1`：valid，位置 `{"end":41,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`：「Dislikes extreme sports (e.g., skydiving)」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":129,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`：「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；定位通过。
  - 引文 `new/new-2/unsplit-new-2`：valid，位置 `{"end":129,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`：「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」；定位通过。
  - 既有独立审核 `unsupported`：新引文支持模拟跳伞刺激及更愿尝新，不证明真实极限运动或旧偏好改变；模型自身声称与旧厌恶矛盾并把模拟/团建写成同一维度的两个互斥枚举而不是组合，同时用 ctx-1 未关联时间依据及发言日期推 after。
  - 自动接口问题：`["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`。
- 记录 1：关系 `change`，单元 `u2`；主体/属性/值 `["I","reason for disliking extreme sports","high injury risk"]` → `["I","reason for disliking extreme sports","not stated as current barrier; explicitly affirms continued prioritization of safety"]`；条件 `[{"kind":"unconditional"},{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}]`；时序 `{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"}`；模型理由：The old claim ties dislike to injury risk as a general, unconditional barrier. The new statements do not retract that risk assessment, but show willingness to engage *only* in a low-risk variant (simulated), while reaffirming safety as a continuing priority — indicating refinement, not rejection, of the original rationale.；模型未知项 `[]`。
  - 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u2`：valid，位置 `{"end":65,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`：「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；定位通过。
  - 引文 `new/new-0/manually_mapped_new`：valid，位置 `{"end":129,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`：「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；定位通过。
  - 引文 `new/new-8/unsplit-new-8`：valid，位置 `{"end":105,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`：「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」；定位通过。
  - 既有独立审核 `unsupported`：新句没有撤回高受伤风险是旧厌恶理由；模型将未再提及当变化，模拟亦不能证明低风险，更不能据对话日期推事实时序；旧 ctx-1 不在已关联旧引文内。
  - 自动接口问题：`["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`。
- 记录 2：关系 `supplement`，单元 `u3`；主体/属性/值 `["I","commitment to safety and well-being","conflicting with extreme sports"]` → `["I","commitment to safety and well-being","still prioritized, even amid new thrill-seeking"]`；条件 `[{"kind":"same_as_old"},{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"}]`；时序 `{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"}`；模型理由：The new utterance does not negate the old conflict claim; instead, it clarifies that the commitment remains active and constrains the scope of acceptable experiences (e.g., simulated only), thereby refining rather than replacing the prior association.；模型未知项 `[]`。
  - 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u3`：valid，位置 `{"end":119,"start":67}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`：「conflicting with commitment to safety and well-being」；定位通过。
  - 引文 `new/new-8/unsplit-new-8`：valid，位置 `{"end":105,"start":0}`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`：「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」；定位通过。
  - 既有独立审核 `partially_supported`：新话语支持现在重视安全，但不证明旧极限运动与安全福祉的整条冲突因果继续成立，亦未证明只接受模拟；old_conditions 使用 same_as_old 违反结构约定。
  - 自动接口问题：`["records[2].old_conditions cannot use same_as_old"]`。

B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：

- `B:model_record=0;candidate=new_subfact;part=0`：主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，值 `"found simulated skydiving thrilling"`，条件 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`，模态 `"asserted"`，新引文 `[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"},{"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","source_id":"new-2","unit_id":"unsplit-new-2"}]`，语义依据 `[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}]`，校验错误 `[]`。
- `B:model_record=0;candidate=new_subfact;part=1`：主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，值 `"more open to trying new things"`，条件 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`，模态 `"asserted"`，新引文 `[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"},{"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","source_id":"new-2","unit_id":"unsplit-new-2"}]`，语义依据 `[{"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","side":"new","source_id":"new-2"}]`，校验错误 `[]`。
- `B:model_record=1;candidate=new_subfact;part=0`：主体 `"I"`，属性 `"reason for disliking extreme sports"`，值 `"not stated as current barrier"`，条件 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`，模态 `"asserted"`，新引文 `[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"},{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","source_id":"new-8","unit_id":"unsplit-new-8"}]`，语义依据 `[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}]`，校验错误 `[]`。
- `B:model_record=1;candidate=new_subfact;part=1`：主体 `"I"`，属性 `"reason for disliking extreme sports"`，值 `"explicitly affirms continued prioritization of safety"`，条件 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`，模态 `"asserted"`，新引文 `[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"},{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","source_id":"new-8","unit_id":"unsplit-new-8"}]`，语义依据 `[]`，校验错误 `[]`。

### A 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（8）

1. `u3` / `supplement`：旧值 `"conflicting with extreme sports"` → 新值 `"still prioritized, even amid new thrill-seeking"`；主体 `"I"`，属性 `"commitment to safety and well-being"`，范围 `{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"}`。
   规划器理由：upstream validation errors: ['records[2].old_conditions cannot use same_as_old']；缺失 `[]`；校验错误 `["records[2].old_conditions cannot use same_as_old"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u3，valid，位置 {"end":119,"start":67}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「conflicting with commitment to safety and well-being」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。新话语支持重视安全，但模型 old_conditions 使用非法 same_as_old，且旧因果关系未被重新证实。
2. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"kind":"unknown"}`。
   规划器理由：unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。旧无条件范围的余域无法从模型有限候选枚举；候选模拟/团建不是已审核的完整范围。
3. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"context":"simulated"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。模型时序依据引用未关联 ctx-1；模拟体验不能证明真实运动偏好改变。
4. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"context":"team-building event"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。同一模型记录将团建列为另一条件值，关系及条件组合均未经审核。
5. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"kind":"unknown"}`。
   规划器理由：unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。旧理由的无条件余域无法由有限候选求差；不得据空交集保留。
6. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"context":"simulated"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。未提及风险不等于否定风险理由；旧时序依据未绑定。
7. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"context":"team-building event"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。团建不是已证实的独立互斥范围，旧时序依据未绑定。
8. `u3` / `supplement`：旧值 `"conflicting with extreme sports"` → 新值 `"still prioritized, even amid new thrill-seeking"`；主体 `"I"`，属性 `"commitment to safety and well-being"`，范围 `null`。
   规划器理由：upstream validation errors: ['records[2].old_conditions cannot use same_as_old']; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `["records[2].old_conditions cannot use same_as_old"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u3，valid，位置 {"end":119,"start":67}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「conflicting with commitment to safety and well-being」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。旧条件非法，安全优先不证明完整旧冲突因果。

**add**（0）

无。

可编辑位置：`[]`；保护事实：`[]`。

### B 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（11）

1. `u3` / `supplement`：旧值 `"conflicting with extreme sports"` → 新值 `"still prioritized, even amid new thrill-seeking"`；主体 `"I"`，属性 `"commitment to safety and well-being"`，范围 `{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"}`。
   规划器理由：upstream validation errors: ['records[2].old_conditions cannot use same_as_old']；缺失 `[]`；校验错误 `["records[2].old_conditions cannot use same_as_old"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u3，valid，位置 {"end":119,"start":67}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「conflicting with commitment to safety and well-being」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。安全优先的子事实有依据，但旧侧 same_as_old 非法，完整冲突因果未被证实。
2. `None` / `new_information`：旧值 `null` → 新值 `"explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`。
   规划器理由：semantic support or bound basis missing；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。安全优先有原话，但自动拆出的新片段未能以模型给定属性/已绑定依据独立成立。
3. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"kind":"unknown"}`。
   规划器理由：unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。原模型旧条件无限定、新条件有限且未经审查，余域不能枚举。
4. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"context":"simulated"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。模拟体验不能直接证明真实偏好改变；旧侧时序依据未绑定。
5. `u1` / `change`：旧值 `"dislikes"` → 新值 `"found simulated skydiving thrilling; more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"context":"team-building event"}`。
   规划器理由：upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。模型将团建当另一同维条件值，未证明这些组合及其时间关系。
6. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"kind":"unknown"}`。
   规划器理由：unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。旧风险理由范围的余域无法依有限候选计算。
7. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"context":"simulated"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。安全优先不撤销原风险理由；模型旧时序依据未绑定。
8. `u2` / `change`：旧值 `"high injury risk"` → 新值 `"not stated as current barrier; explicitly affirms continued prioritization of safety"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"context":"team-building event"}`。
   规划器理由：upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；缺失 `[]`；校验错误 `["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u2，valid，位置 {"end":65,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving) due to high injury risk」；new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。团建条件的作用域和风险理由均不足以确定。
9. `u3` / `supplement`：旧值 `"conflicting with extreme sports"` → 新值 `"still prioritized, even amid new thrill-seeking"`；主体 `"I"`，属性 `"commitment to safety and well-being"`，范围 `null`。
   规划器理由：upstream validation errors: ['records[2].old_conditions cannot use same_as_old']; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `["records[2].old_conditions cannot use same_as_old"]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u3，valid，位置 {"end":119,"start":67}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「conflicting with commitment to safety and well-being」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**暂缓**。旧条件非法；新安全优先不独立证明原冲突因果。
10. `None` / `new_information`：旧值 `null` → 新值 `"found simulated skydiving thrilling"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`。
   规划器理由：conflicting or potentially conflicting new evidence；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。模型把模拟体验与更开放两条值置于同一属性和重叠范围，v3 将它们标作潜在冲突；原文支持模拟体验子事实。
11. `None` / `new_information`：旧值 `null` → 新值 `"more open to trying new things"`；主体 `"I"`，属性 `"attitude toward extreme sports (e.g., skydiving)"`，范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`。
   规划器理由：conflicting or potentially conflicting new evidence；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-2 / unsplit-new-2，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，原文「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。
   人工判断：**暂缓**。更愿尝新有原话，但不等于真实极限运动偏好变化；同属性候选冲突需拆解。

**add**（1）

1. `None` / `new_information`：旧值 `null` → 新值 `"not stated as current barrier"`；主体 `"I"`，属性 `"reason for disliking extreme sports"`，范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-0 / manually_mapped_new，valid，位置 {"end":129,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」；new new-8 / unsplit-new-8，valid，位置 {"end":105,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
   人工判断：**新增无充分依据**。“未称为当前障碍”是从未提及作出的推断；新话语不证明旧受伤风险理由已不再适用。

可编辑位置：`[]`；保护事实：`[]`。

### C 组：实际计划及人工核对

**modify**（0）

无。

**preserve**（0）

无。

**uncertain**（4）

1. `u1` / `unknown`：旧值 `"dislike"` → 新值 `"enjoyed"`；主体 `"user"`，属性 `"preference.extreme_sports"`，范围 `null`。
   规划器理由：模拟与真实跳伞是否同一适用范围、旧偏好是否改变无法确认。; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / u1，valid，位置 {"end":129,"start":77}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「I tried simulated skydiving. It was quite thrilling!」。
   人工判断：**暂缓**。模拟体验与真实极限运动偏好的关系未确定。
2. `u1` / `supplement`：旧值 `"dislike"` → 新值 `"tried and found thrilling"`；主体 `"user"`，属性 `"preference.extreme_sports"`，范围 `null`。
   规划器理由：impact of new information on old fact is not established; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / u1，valid，位置 {"end":129,"start":77}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「I tried simulated skydiving. It was quite thrilling!」。
   人工判断：**暂缓**。独立记录模拟体验不决定对原厌恶的影响。
3. `u2` / `None`：旧值 `null` → 新值 `null`；主体 `null`，属性 `null`，范围 `null`。
   规划器理由：no alignment for unit；缺失 `null`；校验错误 `null`；未知项 `null`。
   引文：无。
   人工判断：**暂缓**。受伤风险理由单元没有足以决定影响的对齐记录。
4. `u3` / `unknown`：旧值 `"prioritize safety"` → 新值 `"prioritize safety"`；主体 `"user"`，属性 `"safety.priority"`，范围 `null`。
   规划器理由：安全优先得到新证据支持，但新证据未证明极限运动与安全福祉的完整冲突关系仍成立，u3 的短引文本身也不足以支持完整因果关系。; scope: condition kind missing or unsupported；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u3，valid，位置 {"end":119,"start":67}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「conflicting with commitment to safety and well-being」；new new-8 / u3，valid，位置 {"end":105,"start":68}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「I still prioritize safety, of course.」。
   人工判断：**暂缓**。仍重视安全不足以确认旧极限运动冲突因果整体。

**add**（2）

1. `u1` / `supplement`：旧值 `"dislike"` → 新值 `"tried and found thrilling"`；主体 `"user"`，属性 `"experience.simulated_skydiving"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：old e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 / u1，valid，位置 {"end":41,"start":0}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，原文「Dislikes extreme sports (e.g., skydiving)」；new new-0 / u1，valid，位置 {"end":129,"start":77}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，原文「I tried simulated skydiving. It was quite thrilling!」。
   人工判断：**新增有依据**。用户明确说尝试模拟跳伞且觉得刺激；不推断真实跳伞偏好变化。
2. `None` / `supplement`：旧值 `null` → 新值 `"prioritize safety"`；主体 `"user"`，属性 `"safety.priority"`，范围 `{"kind":"unknown"}`。
   规划器理由：independent evidence-supported addition；缺失 `[]`；校验错误 `[]`；未知项 `[]`。
   引文：new new-8 / None，valid，位置 {"end":105,"start":68}，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，原文「I still prioritize safety, of course.」。
   人工判断：**新增有依据**。用户明确说仍将安全放在优先位置；不推断完整旧因果。

可编辑位置：`[]`；保护事实：`[]`。

### 差异与仍需处理

- 子事实及依据：模拟跳伞的愉快体验、更愿尝新和仍重视安全分别有原话；真实极限运动偏好与受伤理由是否改变未知。
- 应处理但暂缓或未覆盖：B 把分号分开的模型新值分别作为候选，但沿用模型同一属性/条件，两个可支持的体验子句被 v3 视为冲突，旧变化仍因 ctx-1 未绑定等待；C 独立记录模拟体验及安全优先。
- A/B 差异及风险：B 产生一个无依据新增（未提及被解释为当前无障碍）；A 全部待确认；C 按人工事实边界新增两个子事实。
- 人工依赖及 C 的诊断作用：模拟/真实区别与安全事实的精确拆分由 C 人工输入提供；B 没有从预期补属性。

## 复现与限制

本次验证：本目录 6 项接口与候选隔离测试通过；原 v3 测试集 40 项通过；五案 A 结果均与既存 v3 未加附加保护的结果一致。测试通过只说明这些程序检查通过，不代表 B 的候选经语义授权。

在本目录运行：
```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python comparison.py
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

自动链路能够校验引文位置、来源和显式范围/时序字段，不能验证自然语言蕴含关系，也不能把观察到的发话时间变成事实生效时间。B 的分号拆分保留模型属性，可能让不同子事实共享错误属性并触发虚假冲突；新增判断也可能因模型语义猜测而错误。C 的主体、条件、语义支持及事实拆分来自既有人工作业，不能归功于自动流程。需要单独人工语义审核及完整关系覆盖后才能讨论后续写入。

机器可读结果：`results/*.json`；人工判断：`AUDIT.json`；原逐条审核：`../../evidence_aligner/v4_scope_interface/human_reviews.json`；既有 v3 报告：`../v3_offline/REPORT.md`。
