# v5 新事实拆分与关系对齐：五案实验

## 方法和边界

五案输入与保存的 v4 输入一致；每次仅一请求、自动重试为零。facts 是模型提出的新事实，relations 单独引用事实与旧单元。适配后每项事实和每项旧关系成为独立规划器候选；模型语义理由不等于独立审核，默认 semantic_support 为 unknown。未调用 Mem0，也未写真实记忆。五案用于开发诊断，不是论文准确率或用户确认金标准。

结构校验、逐字引文及来源校验、人工语义判断是不同结果。引文可定位并不证明其支持模型的全部推断。下文人工判断来自对原文和既有审核的独立核对，只写在 HUMAN_REVIEW.json，不作为模型输出、也不回填到规划器。完整回复、请求配置、耗时和可得用量保存在 runs 目录；人工预期作为比较材料，不输入模型或规划器。

v4 的严格 A 与本次 v5 默认计划都要求独立语义授权；旧 B 是放开该门槛的候选实验，其动作数量不能与本次默认计划直接比较。`supplement` 关系在适配时投影为旧影响 unknown（原始 relation 保留），以免对已经独立输出的新事实再次制造一条新增。

本次请求尝试 **5**，收到模型响应 **5**；状态 `completed`。模型 `qwen-plus-2025-12-01`，temperature `0`，JSON 对象格式，最大生成 `8192` tokens，自动重试 `0`。
可获得的合计用量：输入 54887，输出 9214，总计 64101 tokens；无返回用量的请求不计入总数。

下表的 passed/failed 是收到回复后的接口总校验状态，不是请求是否成功；具体结构、引文和依据绑定分列。

| 案例 | 接口状态/秒 | token 输入/输出/总计 | 结构 | 引文定位 | 依据绑定 | 模型事实/关系 | 完整支持的事实/关系 |
|---|---|---|---|---|---|---|---|
| susan | failed / 45.622 | 8027/2006/10033 | failed | passed | passed | 6/4 | 0/0 |
| promotion | passed / 28.991 | 12642/1269/13911 | passed | passed | passed | 3/2 | 0/0 |
| career_history | failed / 35.45 | 13680/1561/15241 | failed | passed | failed | 4/2 | 0/0 |
| transition | passed / 25.733 | 12199/1125/13324 | passed | passed | passed | 2/2 | 0/0 |
| skydiving | passed / 72.353 | 8339/3253/11592 | passed | passed | passed | 6/5 | 0/0 |

独立审核：事实 0/21 条、旧关系 0/15 条完整受支持；事实内核受支持 16/21，整条部分支持的事实 18 条、关系 3 条。完整判断按模型同时给出的值、来源、条件、理由和时间关系审查；只证实核心事实不能消除其他未证实字段。结构通过 3/5，引文定位通过 5/5，这些数字只反映五案与所选审核标准，不是准确率。

## susan

旧记忆 `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`）：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

- 新证据 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.
- 新证据 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`）：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.

v4：结构 `passed`，引文 `passed`，依据绑定 `failed`；严格 A 计划 `{"add":0,"modify":0,"preserve":0,"uncertain":5}`；放开授权的 B 候选计划 `{"add":2,"modify":0,"preserve":0,"uncertain":3}`。既有审核：结构四字段组中 schema、引文、覆盖通过，basis 因 #0 使用未绑定 ctx-1、#3 时间引文含省略号且未绑定而失败；6 条主引文都唯一匹配。预期保留 Susan 的朋友支持、独立新增 Daniel 的见解和求职计划；直接规划均待确认，未产生编辑/新增，属于对模型语义未知的保守结果而非事实不存在。模型对两条时间 same 与 unconditional 推断不足，Daniel 语义未独立输出，单元覆盖不能证明事实覆盖。

原人工预期（非模型输入、非用户确认金标准）：
- modify: 无
- preserve: ThomasSusan/Susan 朋友关系、支持和鼓励
- uncertain: 新证据没有独立确认全名与称呼的映射；旧来源 ctx-1 可支持语境但不消除命名歧义
- add: Daniel 的见解促进职业思考；工作生活平衡及人道目标为另行表达的内容

事实提取完整性：
- **present**：Susan 的支持珍贵；模型事实 `["f1"]`。结构化事实独立提出，范围仍需核对。
- **present**：Susan 的鼓励帮助专注目标；模型事实 `["f2"]`。与支持评价已拆开。
- **present**：Daniel 的见解推动职业思考；模型事实 `["f3"]`。v4 遗漏的 Daniel 独立提出。
- **present**：当前岗位对福祉支持不及期望；模型事实 `["f5"]`。模型保留 current 和比较限定。
- **partial**：寻找兼顾平衡及人道目标的工作计划；模型事实 `["f6"]`。有计划，但把两个要求写为数组且未分别独立结构化，接口校验失败。
- **partial**：这些联系开辟新可能；模型事实 `["f4"]`。模型提出，但对联系集合的完整归属有推断。

v5 自动校验：结构 `failed`，引文 `passed`，依据绑定 `passed`，单元覆盖 `passed`。错误：`["records[5].new_value must be nonempty text or null (unknown)"]`。

### 新事实：独立语义审核

**facts[0]**：`{"attribute":"support","conditions":{"kind":"unconditional"},"fact_id":"f1","modality":"asserted","quotes":[{"quote":"Susan's support has indeed been invaluable.","source_id":"new-2","unit_id":"manually_mapped_new"}],"rationale":"Direct attribution of 'invaluable' to Susan's support in user's own words.","subject":"Susan","uncertainties":[],"value":"invaluable"}`

- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":43,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Susan's support has indeed been invaluable.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户称 Susan 的支持十分宝贵；完整 unconditional 适用范围没有独立证明。
- 输出去向 `new_claim`：uncertain[0]（semantic support or bound basis missing）

**facts[1]**：`{"attribute":"encouragement","conditions":{"kind":"unconditional"},"fact_id":"f2","modality":"asserted","quotes":[{"quote":"Her encouragement helps me stay focused on my goals.","source_id":"new-2","unit_id":"manually_mapped_new"}],"rationale":"Direct causal claim about Susan's encouragement enabling goal focus.","subject":"Susan","uncertainties":[],"value":"helps me stay focused on my goals"}`

- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":96,"start":44}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Her encouragement helps me stay focused on my goals.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户称她的鼓励帮助自己专注目标；单独作用域为 unconditional 缺充分依据。
- 输出去向 `new_claim`：uncertain[1]（semantic support or bound basis missing）

**facts[2]**：`{"attribute":"insights","conditions":{"kind":"unconditional"},"fact_id":"f3","modality":"asserted","quotes":[{"quote":"And Daniel's insights have really pushed me to think outside the box in my career.","source_id":"new-2","unit_id":"manually_mapped_new"}],"rationale":"Direct attribution of cognitive impact (thinking outside the box) to Daniel's insights.","subject":"Daniel","uncertainties":[],"value":"pushed me to think outside the box in my career"}`

- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":179,"start":97}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「And Daniel's insights have really pushed me to think outside the box in my career.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：Daniel 的见解促使用户在职业上跳出固有思路；完整无条件范围未证明。
- 输出去向 `new_claim`：uncertain[2]（semantic support or bound basis missing）

**facts[3]**：`{"attribute":"effect","conditions":{"kind":"unconditional"},"fact_id":"f4","modality":"asserted","quotes":[{"quote":"It's been exciting to see how these connections have opened up new possibilities.","source_id":"new-2","unit_id":"manually_mapped_new"}],"rationale":"User explicitly states 'these connections' (referring to Susan and Daniel just mentioned) caused new possibilities.","subject":"connections (Susan, Daniel, etc.)","uncertainties":[],"value":"opened up new possibilities"}`

- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":261,"start":180}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「It's been exciting to see how these connections have opened up new possibilities.」。
- 独立审核 **partial**（事实或关系内核 `partial`）：用户说这些联系开辟了可能性，但将这些联系明确扩展为 Susan、Daniel 等的完整集合及无条件范围仍是推断。
- 输出去向 `new_claim`：uncertain[3]（semantic support or bound basis missing）

**facts[4]**：`{"attribute":"support for well-being","conditions":{"kind":"unconditional"},"fact_id":"f5","modality":"asserted","quotes":[{"quote":"my current role isn't supporting my well-being as much as I'd like","source_id":"new-0","unit_id":"unsplit-new-0"}],"rationale":"Direct comparative evaluation of current role's impact on well-being.","subject":"current role","uncertainties":[],"value":"not as much as I'd like"}`

- 引文 `new/new-0/unsplit-new-0`：`valid`，位置 `{"end":138,"start":72}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，逐字「my current role isn't supporting my well-being as much as I'd like」。
- 独立审核 **partial**（事实或关系内核 `supported`）：原话明确限定当前岗位和相对本人期望；无条件范围不应理解为永久。
- 输出去向 `new_claim`：uncertain[4]（semantic support or bound basis missing）

**facts[5]**：`{"attribute":"requirements","conditions":{"kind":"unconditional"},"fact_id":"f6","modality":"planned","quotes":[{"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","source_id":"new-0","unit_id":"unsplit-new-0"}],"rationale":"Explicit statement of intended future job criteria; 'crucial' signals commitment but not yet realized.","subject":"job search goal","uncertainties":[],"value":["better work-life balance","aligns with humanitarian goals"]}`

- 引文 `new/new-0/unsplit-new-0`：`valid`，位置 `{"end":255,"start":140}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，逐字「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户表达找兼顾平衡与人道目标的工作的计划；new_value 是数组，不符合接口标量，且两个条件没有分为独立记录。
- 输出去向 `new_claim`：uncertain[5]（upstream validation errors: ['records[5].new_value must be nonempty text or null (unknown)']）

### 旧关系：独立语义审核

**relations[0]**：`{"affected_part":"support","fact_id":"f1","old_attribute":"provides support and encouragement","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"provides support and encouragement","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","unit_id":"support"}],"old_subject":"Susan","old_value":"support and encouragement","rationale":"New fact affirms Susan's support (qualifying it as 'invaluable'), consistent with old unit stating she 'provides support'. No contradiction or change in core attribute; 'invaluable' is an intensifier, not a replacement.","relation":"same","relation_id":"r1","semantic_basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"uncertainties":[],"unit_id":"support"}`

- 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support`：`valid`，位置 `{"end":94,"start":60}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，逐字「provides support and encouragement」。
- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":43,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Susan's support has indeed been invaluable.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：评价支持珍贵与旧事实“提供支持和鼓励”不是同属性同值的 same；原话无充分依据证明两个状态在完整范围同值。
- 输出去向 `old_relation`：uncertain[8]（semantic support or bound basis missing）

**relations[1]**：`{"affected_part":"encouragement","fact_id":"f2","old_attribute":"provides support and encouragement","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"provides support and encouragement","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","unit_id":"support"}],"old_subject":"Susan","old_value":"support and encouragement","rationale":"New fact specifies *how* Susan's encouragement functions ('helps me stay focused on my goals'), adding functional detail not present in the generic 'encouragement' in the old unit.","relation":"supplement","relation_id":"r2","semantic_basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"uncertainties":[],"unit_id":"support"}`

- 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support`：`valid`，位置 `{"end":94,"start":60}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，逐字「provides support and encouragement」。
- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":96,"start":44}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Her encouragement helps me stay focused on my goals.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：鼓励帮助专注可以补充旧支持事实，但无条件旧范围及跨引文关系仍须核对；模型 supplement 被适配为旧影响 unknown。
- 输出去向 `old_relation`：uncertain[9]（model_relation=r2;index=1）

**relations[2]**：`{"affected_part":null,"fact_id":"f1","old_attribute":"friend named","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"friend named ThomasSusan","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","unit_id":"friendship"}],"old_subject":"ThomasSusan","old_value":"ThomasSusan","rationale":"Fact f1 concerns Susan's support quality; old unit concerns naming/identity of 'ThomasSusan'. No semantic overlap in subject or attribute.","relation":"unrelated","relation_id":"r3","semantic_basis":[],"temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"uncertainties":[],"unit_id":"friendship"}`

- 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship`：`valid`，位置 `{"end":30,"start":6}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，逐字「friend named ThomasSusan」。
- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":43,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Susan's support has indeed been invaluable.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：把 Susan 支持与 ThomasSusan 朋友关系判为主体完全无重叠不可靠；旧记忆完整原文明示 Susan 称呼，短旧引文不足以支持该结论。
- 输出去向 `old_relation`：uncertain[6]（unrelated label does not establish preservation）

**relations[3]**：`{"affected_part":null,"fact_id":"f2","old_attribute":"friend named","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"friend named ThomasSusan","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","unit_id":"friendship"}],"old_subject":"ThomasSusan","old_value":"ThomasSusan","rationale":"Fact f2 concerns Susan's encouragement effect; old unit concerns naming/identity. No shared semantic content.","relation":"unrelated","relation_id":"r4","semantic_basis":[],"temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"uncertainties":[],"unit_id":"friendship"}`

- 引文 `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship`：`valid`，位置 `{"end":30,"start":6}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`，逐字「friend named ThomasSusan」。
- 引文 `new/new-2/manually_mapped_new`：`valid`，位置 `{"end":96,"start":44}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，逐字「Her encouragement helps me stay focused on my goals.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：与上一条同理，功能不同不等于主体必然无关；不能单靠短旧引文认证无影响。
- 输出去向 `old_relation`：uncertain[7]（unrelated label does not establish preservation）

规划结果：`{"add":0,"modify":0,"preserve":0,"uncertain":10}`；可编辑位置 `[]`。

对比与限制：v4 未独立输出 Daniel；v5 拆出了支持、鼓励与 Daniel，但计划值仍是数组，两条 unrelated 的主体解释不可靠。旧记忆的身份指代与可编辑范围不能由新事实自动决定。

## promotion

旧记忆 `e13b825e-7ec7-4760-821e-0581d8da5650`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`）：Works at Historical Productions Ltd. as a Director

- 新证据 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

v4：结构 `passed`，引文 `passed`，依据绑定 `passed`；严格 A 计划 `{"add":0,"modify":0,"preserve":0,"uncertain":2}`；放开授权的 B 候选计划 `{"add":0,"modify":1,"preserve":1,"uncertain":0}`。既有审核：schema、引用、依据绑定和覆盖均通过，4 条主引文唯一定位，但结构通过并未证明语义。预期保留同雇主与历史职位并表达晋升；直接规划两条待确认且无编辑/新增，较预期保守。晋升已发生与晋升是否晚于旧事实、旧宽泛称谓是否不再成立需要分别判断。

原人工预期（非模型输入、非用户确认金标准）：
- modify: 职位细化为晋升后的 lead director
- preserve: Historical Productions Ltd. 雇主关系；Director 作为历史和可能仍成立的宽泛描述
- uncertain: 准确晋升日期未知；宽泛 Director 与 lead director 的逻辑包含关系不由代码推理
- add: 晋升 lead director 的事实

事实提取完整性：
- **present**：晋升已发生；模型事实 `["f3"]`。晋升事件单独提出。
- **present**：晋升职位 lead director；模型事实 `["f2"]`。职位单独提出，但并不能决定旧职位覆盖。
- **present**：公司 Historical Productions Ltd.；模型事实 `["f1"]`。公司关联有原话，连续雇佣与同一时刻仍需依据。
- **missing**：对此晋升感到兴奋；模型事实 `[]`。发话包含主观感受，但模型未单独输出。

v5 自动校验：结构 `passed`，引文 `passed`，依据绑定 `passed`，单元覆盖 `passed`。错误：`[]`。

### 新事实：独立语义审核

**facts[0]**：`{"attribute":"employer","conditions":{"kind":"unconditional"},"fact_id":"f1","modality":"asserted","quotes":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The speaker explicitly names 'Historical Productions Ltd.' as the employer in the context of a recent promotion, confirming current employment there.","subject":"I","uncertainties":[],"value":"Historical Productions Ltd."}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，逐字「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- 独立审核 **partial**（事实或关系内核 `supported`）：话语在晋升语境中明确公司；当时公司关联有依据，持续现职和完整无条件范围不能由此保证。
- 输出去向 `new_claim`：uncertain[0]（semantic support or bound basis missing）

**facts[1]**：`{"attribute":"title","conditions":{"kind":"unconditional"},"fact_id":"f2","modality":"asserted","quotes":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The speaker states they 'got promoted to lead director', asserting current holding of that title.","subject":"I","uncertainties":[],"value":"lead director"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，逐字「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- 独立审核 **partial**（事实或关系内核 `supported`）：话语支持晋升为 lead director；不要将其无条件推广到所有时间。
- 输出去向 `new_claim`：uncertain[1]（semantic support or bound basis missing）

**facts[2]**：`{"attribute":"employment_status","conditions":{"kind":"unconditional"},"fact_id":"f3","modality":"asserted","quotes":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The verb 'got promoted' is an asserted past event indicating a change in role; 'recently' modifies timing but does not alter the factual assertion of promotion having occurred.","subject":"I","uncertainties":[],"value":"promoted"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，逐字「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- 独立审核 **partial**（事实或关系内核 `supported`）：got promoted 表示发话前已发生晋升；相对旧职位有效时间仍未知，模型值未保留 recently。
- 输出去向 `new_claim`：uncertain[2]（semantic support or bound basis missing）

### 旧关系：独立语义审核

**relations[0]**：`{"affected_part":"Historical Productions Ltd.","fact_id":"f1","old_attribute":"employer","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Historical Productions Ltd.","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","unit_id":"employer"}],"old_subject":"I","old_value":"Historical Productions Ltd.","rationale":"Employer remains unchanged; new quote confirms same entity without qualification or contrast.","relation":"same","relation_id":"r1","semantic_basis":[{"quote":"Historical Productions Ltd.","side":"new","source_id":"new-0"},{"quote":"Historical Productions Ltd.","side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650"}],"temporal_order":{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms continued employment at the same company; 'recently promoted' implies continuity of employer, not replacement. No temporal displacement relative to old fact is indicated — both refer to current affiliation.","relation":"same"},"uncertainties":[],"unit_id":"employer"}`

- 引文 `old/e13b825e-7ec7-4760-821e-0581d8da5650/employer`：`valid`，位置 `{"end":36,"start":9}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，逐字「Historical Productions Ltd.」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，逐字「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- 独立审核 **partial**（事实或关系内核 `partial`）：两侧出现同公司，但同一时刻和持续雇佣不是单凭公司名与晋升话语可以独立证实；旧关系本身有原文。
- 输出去向 `old_relation`：uncertain[3]（semantic support or bound basis missing）

**relations[1]**：`{"affected_part":"Director","fact_id":"f2","old_attribute":"title","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Director","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","unit_id":"title"}],"old_subject":"I","old_value":"Director","rationale":"New title 'lead director' is more specific and hierarchical relative to 'Director'; 'promoted to' signals replacement, not coexistence. The old unit states 'Director' without modifiers; no evidence supports concurrent holding.","relation":"change","relation_id":"r2","semantic_basis":[{"quote":"lead director","side":"new","source_id":"new-0"},{"quote":"Director","side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650"}],"temporal_order":{"basis":[{"quote":"recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted to lead director' indicates the new title succeeded the prior one; 'promoted' entails replacement of former title, and 'recently' signals temporal succession after the prior state.","relation":"after"},"uncertainties":[],"unit_id":"title"}`

- 引文 `old/e13b825e-7ec7-4760-821e-0581d8da5650/title`：`valid`，位置 `{"end":50,"start":42}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`，逐字「Director」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，逐字「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：recently 相对发话而非旧事实有效时间；lead director 更具体也不证明宽泛 Director 失效。模型 after 和替代理由不足。
- 输出去向 `old_relation`：uncertain[4]（semantic support or bound basis missing）

规划结果：`{"add":0,"modify":0,"preserve":0,"uncertain":5}`；可编辑位置 `[]`。

对比与限制：v4 已提到晋升但错误推断 after 和职位替换；v5 将事件与职位分开并修正公司主体，仍重复作出同样未经支持的职位替换与先后判断。

## career_history

旧记忆 `05afde13-35bd-4d26-bbae-6de427d58db1`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`）：Previously worked as a senior developer in Blockchain Tech

- 新证据 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- 新证据 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`）：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.

v4：结构 `failed`，引文 `passed`，依据绑定 `failed`；严格 A 计划 `{"add":0,"modify":0,"preserve":0,"uncertain":3}`；放开授权的 B 候选计划 `{"add":2,"modify":0,"preserve":0,"uncertain":3}`。既有审核：schema 失败于联系人 new_value 数组，basis 因前两条时序依据不落在其引用内而失败；5 条主引文来源唯一、覆盖通过。原模型把咨询公司获客扩展为离职、经营/创办并判 change，证据不支持；现有人工预期保留旧历史并新增获客，模型没有独立输出获客记录，直接计划保守无新增或修改，不能误认为历史已核实保留。

原人工预期（非模型输入、非用户确认金标准）：
- modify: 无
- preserve: 曾在 Blockchain Tech 任 senior developer 的历史
- uncertain: 具体离职或转型时间、当前雇佣关系及公司所有权细节
- add: 咨询公司获得初始客户

事实提取完整性：
- **missing**：用户所称咨询公司获得初始客户；模型事实 `[]`。事件仅出现在 f1、f2 的引文和理由中；结构化 value 是身份或领域，缺独立获客事实。
- **missing**：用户因此感到宽慰与重要里程碑；模型事实 `[]`。引文存在但未独立形成事实。
- **partial**：两位联系人及其关系打开机会；模型事实 `["f3"]`。两个人及其作用被合并，且为公司打开的限定比原句更具体。
- **present**：关注维系这些关系以支持公司增长；模型事实 `["f4"]`。模型保留当前关注；重要性是用户主张。
- **unsupported**：用户为创办者或所有者；模型事实 `["f1"]`。模型有此事实但引文不能证明，不可当作正确提取。

v5 自动校验：结构 `failed`，引文 `passed`，依据绑定 `failed`，单元覆盖 `passed`。错误：`["records[5].temporal_order requires new-side basis and explanation","records[4].semantic_basis[0] not bound to cited same-side source/quote","records[5].semantic_basis[0] not bound to cited same-side source/quote","records[5].temporal_order.basis[0] not bound to cited same-side source/quote"]`。

### 新事实：独立语义审核

**facts[0]**：`{"attribute":"employment status","conditions":{"kind":"unconditional"},"fact_id":"f1","modality":"asserted","quotes":[{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The speaker refers to 'my consulting firm' and its securing of 'initial clients', indicating current ownership or leadership role in that firm; no indication this is hypothetical or planned.","subject":"I","uncertainties":[],"value":"founder/owner of a consulting firm"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":141,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，逐字「I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：my consulting firm 与获客不证明用户是创办者、所有者或该公司的当前雇员。
- 输出去向 `new_claim`：uncertain[0]（semantic support or bound basis missing）

**facts[1]**：`{"attribute":"professional domain","conditions":{"kind":"unconditional"},"fact_id":"f2","modality":"asserted","quotes":[{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The assistant's response (new-1) explicitly labels the firm as 'political consulting', and the user does not correct or qualify this — and later confirms it via vision ('key player in political consulting', new-8), services ('digital campaign strategies', new-10), and impact goals ('shaping political discourse', new-28). The user's own utterances consistently treat the domain as established fact, not aspiration.","subject":"I","uncertainties":[],"value":"political consulting"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":141,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，逐字「I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：已选 new-0 引文并未说 political consulting；理由援引其他未选来源，不能借其作为该条证据。
- 输出去向 `new_claim`：uncertain[1]（semantic support or bound basis missing）

**facts[2]**：`{"attribute":"relationship with MooreSandra and GonzalezMary","conditions":{"kind":"unconditional"},"fact_id":"f3","modality":"asserted","quotes":[{"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","source_id":"new-2","unit_id":"unsplit-new-2"}],"rationale":"Direct attribution of instrumental role and door-opening effect, stated in past tense but grounded in recent, completed action ('finally secured some initial clients' in new-0 implies prior enabling events).","subject":"I","uncertainties":[],"value":"they were instrumental in opening doors for my firm"}`

- 引文 `new/new-2/unsplit-new-2`：`valid`，位置 `{"end":111,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`，逐字「MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.」。
- 独立审核 **partial**（事实或关系内核 `partial`）：两名联系人及其关系打开机会有用户引文；合并两人，且“为公司打开”较原话更具体，未分别结构化。
- 输出去向 `new_claim`：uncertain[2]（semantic support or bound basis missing）

**facts[3]**：`{"attribute":"current focus","conditions":{"kind":"unconditional"},"fact_id":"f4","modality":"asserted","quotes":[{"quote":"I'm focusing on maintaining these relationships as they are crucial for my firm's growth.","source_id":"new-2","unit_id":"unsplit-new-2"}],"rationale":"Present continuous 'I'm focusing' expresses current active priority; 'these relationships' refers back to MooreSandra and GonzalezMary, and 'crucial for my firm's growth' specifies purpose.","subject":"I","uncertainties":[],"value":"maintaining relationships crucial for firm's growth"}`

- 引文 `new/new-2/unsplit-new-2`：`valid`，位置 `{"end":201,"start":112}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`，逐字「I'm focusing on maintaining these relationships as they are crucial for my firm's growth.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户说正专注维系这些关系并认为其对公司增长重要；客观上是否确实重要及无条件范围未独立证明。
- 输出去向 `new_claim`：uncertain[3]（semantic support or bound basis missing）

### 旧关系：独立语义审核

**relations[0]**：`{"affected_part":"Blockchain Tech","fact_id":"f1","old_attribute":"employer","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Blockchain Tech","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","unit_id":"employer"}],"old_subject":"I","old_value":"Blockchain Tech","rationale":"The new fact asserts current operation of 'my consulting firm', while the old unit states 'Previously worked as a senior developer in Blockchain Tech'. 'Previously' signals temporal displacement, and 'my consulting firm' implies current primary professional identity distinct from prior employer.","relation":"change","relation_id":"r1","semantic_basis":[{"quote":"Previously worked","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"}],"temporal_order":{"basis":[{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients.","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' implies completion of a recent transition; 'lately' situates relief in present time, after the event. This contrasts with the old memory's 'Previously worked', which explicitly marks prior employment.","relation":"after"},"uncertainties":[],"unit_id":"employer"}`

- 引文 `old/05afde13-35bd-4d26-bbae-6de427d58db1/employer`：`valid`，位置 `{"end":58,"start":43}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，逐字「Blockchain Tech」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":141,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，逐字「I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：新事实本身的创办/所有者身份无依据，获客不证明更换雇主；旧历史本身不应删除。语义依据还引用了不在绑定旧短引文中的 Previously worked。
- 输出去向 `old_relation`：uncertain[4]（upstream validation errors: ['records[4].semantic_basis[0] not bound to cited same-side source/quote']）

**relations[1]**：`{"affected_part":"senior developer","fact_id":"f1","old_attribute":"title","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"senior developer","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","unit_id":"title"}],"old_subject":"I","old_value":"senior developer","rationale":"The old unit anchors 'senior developer' to 'Blockchain Tech' in the past; the new fact anchors 'my consulting firm' to present activity. No evidence suggests dual concurrent roles; 'finally secured' and 'lately' reinforce recency and current relevance of the new role.","relation":"change","relation_id":"r2","semantic_basis":[{"quote":"Previously worked","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"}],"temporal_order":{"basis":[{"quote":"Previously worked","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"}],"explanation":"'Previously worked' establishes the old title as no longer current; new fact affirms current role as founder/owner of a consulting firm — incompatible with continuing as a senior developer at Blockchain Tech.","relation":"after"},"uncertainties":[],"unit_id":"title"}`

- 引文 `old/05afde13-35bd-4d26-bbae-6de427d58db1/title`：`valid`，位置 `{"end":39,"start":23}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`，逐字「senior developer」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":141,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，逐字「I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：新身份无依据；过去 senior developer 并不与新活动必然互斥，也未证明顺序或替换。所引旧时间依据未绑定，新侧时间依据缺失。
- 输出去向 `old_relation`：uncertain[5]（upstream validation errors: ['records[5].semantic_basis[0] not bound to cited same-side source/quote', 'records[5].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[5].temporal_order requires new-side basis and explanation']）

规划结果：`{"add":0,"modify":0,"preserve":0,"uncertain":6}`；可编辑位置 `[]`。

对比与限制：v4 也把获客扩展为角色/雇主变化；v5 仍未将获客作为结构化事实，继续推断创办/所有者并引入所选引文没有的领域；联系人新增仍合并主体。

## transition

旧记忆 `e6ab178b-c0f9-4adb-bfb7-e4648617a950`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`）：Looking for a new job with better work-life balance

- 新证据 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`）：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.

v4：结构 `passed`，引文 `passed`，依据绑定 `passed`；严格 A 计划 `{"add":0,"modify":0,"preserve":0,"uncertain":3}`；放开授权的 B 候选计划 `{"add":2,"modify":0,"preserve":0,"uncertain":1}`。既有审核：schema、主引文、basis 绑定和覆盖都通过，4 条主引文唯一命中；但结构通过不证明语义先后。人工预期保护旧平衡目标、表达已转岗及平衡改善；模型直接计划没有编辑、保留或新增，只列待确认。模型根据 finally 认定结束求职和时间 after 超出了证据；没有具体日期并不是拒绝的直接原因。

原人工预期（非模型输入、非用户确认金标准）：
- modify: 求职进展改为已经转到新职位，不断言停止任何求职
- preserve: 追求较好工作生活平衡的旧目标
- uncertain: 新职位名称和实际切换日期；是否继续另找工作
- add: 新职位工作生活平衡改善

事实提取完整性：
- **missing**：已转到新职位；模型事实 `[]`。原话在 f1 引文，模型结构化值却变成 no longer searching，不能当作正确的已转岗事实。
- **missing**：转岗带来宽慰；模型事实 `[]`。原话提到 relief，模型未独立输出；不能将原因扩展为求职结束。
- **present**：现在工作与生活的平衡更健康；模型事实 `["f2"]`。单独提出并保留 now。
- **unsupported**：已经停止求职；模型事实 `["f1"]`。这是模型推断，原话没有确认。

v5 自动校验：结构 `passed`，引文 `passed`，依据绑定 `passed`，单元覆盖 `passed`。错误：`[]`。

### 新事实：独立语义审核

**facts[0]**：`{"attribute":"job search status","conditions":{"kind":"unconditional"},"fact_id":"f1","modality":"asserted","quotes":[{"quote":"I've finally transitioned to a new role, and it's been a huge relief.","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The phrase 'finally transitioned to a new role' asserts completion of job search; 'it's been a huge relief' confirms resolution of prior stress associated with the search.","subject":"I","uncertainties":[],"value":"no longer searching"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":69,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，逐字「I've finally transitioned to a new role, and it's been a huge relief.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：原话说转到新职位，没有说不再求职；宽慰也不证明原先求职压力已消失。
- 输出去向 `new_claim`：uncertain[0]（semantic support or bound basis missing）

**facts[1]**：`{"attribute":"work-life balance","conditions":{"kind":"unconditional"},"fact_id":"f2","modality":"asserted","quotes":[{"quote":"The balance between work and personal life is much healthier now.","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"Direct self-assessment of current work-life balance as improved, using comparative 'much healthier now' implying change from prior state.","subject":"I","uncertainties":[],"value":"much healthier now"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":135,"start":70}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，逐字「The balance between work and personal life is much healthier now.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户说现在工作和生活平衡更健康；时间限定 now 有依据，unconditional 不宜扩大到其他时段。
- 输出去向 `new_claim`：uncertain[1]（semantic support or bound basis missing）

### 旧关系：独立语义审核

**relations[0]**：`{"affected_part":"Looking for a new job","fact_id":"f1","old_attribute":"job search status","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Looking for a new job with better work-life balance","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","unit_id":"job_search"}],"old_subject":"I","old_value":"looking for a new job","rationale":"New fact asserts completed transition, directly negating the prior active search state. Temporal marker 'finally' supports sequential ordering.","relation":"change","relation_id":"r1","semantic_basis":[{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"},{"quote":"Looking for a new job","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"}],"temporal_order":{"basis":[{"quote":"finally transitioned","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion relative to prior ongoing search; 'transitioned' is a past-tense completed action, temporally after the prior 'looking' state.","relation":"after"},"uncertainties":[],"unit_id":"job_search"}`

- 引文 `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：`valid`，位置 `{"end":51,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，逐字「Looking for a new job with better work-life balance」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":69,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，逐字「I've finally transitioned to a new role, and it's been a huge relief.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：已转岗不证明停止求职；finally 只确认转岗相对话语完成，不证明晚于旧记忆事实有效时间。
- 输出去向 `old_relation`：uncertain[2]（semantic support or bound basis missing）

**relations[1]**：`{"affected_part":"better work-life balance","fact_id":"f2","old_attribute":"work-life balance expectation","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Looking for a new job with better work-life balance","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","unit_id":"job_search"}],"old_subject":"I","old_value":"better work-life balance","rationale":"Old unit expresses desire for 'better work-life balance' as a future goal; new fact states current reality is 'much healthier', satisfying and superseding that goal.","relation":"change","relation_id":"r2","semantic_basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"},{"quote":"better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"}],"temporal_order":{"basis":[{"quote":"now","side":"new","source_id":"new-0"}],"explanation":"'Now' in 'much healthier now' refers to current state post-transition, which follows the prior aspirational state expressed in the old unit.","relation":"after"},"uncertainties":[],"unit_id":"job_search"}`

- 引文 `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：`valid`，位置 `{"end":51,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`，逐字「Looking for a new job with better work-life balance」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":135,"start":70}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，逐字「The balance between work and personal life is much healthier now.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：平衡更健康不证明旧目标已完全实现或应被替换；now 也不独立证明相对旧目标的有效时间先后。
- 输出去向 `old_relation`：uncertain[3]（semantic support or bound basis missing）

规划结果：`{"add":0,"modify":0,"preserve":0,"uncertain":4}`；可编辑位置 `[]`。

对比与限制：v4 把转岗与平衡写在合并值中并暗示状态替换；v5 虽拆出平衡，反而将转岗候选结构化成未被证实的停止求职，关系 after 仍缺依据。

## skydiving

旧记忆 `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`）：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

- 新证据 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
- 新证据 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`）：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
- 新证据 `new-8`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`）：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.

v4：结构 `failed`，引文 `passed`，依据绑定 `failed`；严格 A 计划 `{"add":0,"modify":0,"preserve":0,"uncertain":8}`；放开授权的 B 候选计划 `{"add":1,"modify":0,"preserve":0,"uncertain":11}`。既有审核：schema 因旧侧 same_as_old 失败，basis 因前两条引用未关联 ctx-1 失败，8 条主引文唯一且单位关联有效、覆盖通过。模型仍把模拟体验扩展成真实极限运动偏好/风险理由变化，并依据对话时间声称 after；这不成立。v2 直接计划没有修改、新增，u3 列待确认，但对 u1/u2 输出了无条件 preserve：其旧 unconditional 与新 finite 的条件无法求差，且依据错误被空交集路径掩盖；保留原文方向虽可审慎接受，报告必须指出范围理由错误和遗漏待确认。人工预期保留旧顾虑、独立增加模拟体验及安全优先；未授权模型直接添加，因此当前计划比预期更保守。 事后离线保护重算将两条不成立的 preserve 转为待确认；这只是在现有适配层防止不支持的范围计算，并非证明旧条件或模型语义。首次输出原样保存，未重跑模型。

原人工预期（非模型输入、非用户确认金标准）：
- modify: 无
- preserve: 旧极限运动顾虑、受伤风险和安全福祉取向；不要推广为所有偏好已改变
- uncertain: 模拟跳伞与旧极限运动的覆盖关系、当前真实跳伞偏好；u3 短引文本身不完整
- add: 尝试模拟跳伞且感觉刺激；仍重视安全

事实提取完整性：
- **present**：近期团队活动中尝试模拟跳伞；模型事实 `["f1"]`。模拟限定和活动上下文均保留。
- **present**：这次模拟体验刺激；模型事实 `["f2"]`。与尝试事件分开，不等同真实偏好。
- **present**：肾上腺素体验超出预期；模型事实 `["f3"]`。值受原话支持，但其理由把预期夸大为完全不享受。
- **present**：更愿意尝试新事物；模型事实 `["f4"]`。独立记录；不证明真实极限运动偏好。
- **present**：仍优先考虑安全；模型事实 `["f5"]`。独立记录；不证明旧受伤风险原因。
- **present**：目前享受刺激并观察后续；模型事实 `["f6"]`。有原文，但长期参与活动的理由是推测。

v5 自动校验：结构 `passed`，引文 `passed`，依据绑定 `passed`，单元覆盖 `passed`。错误：`[]`。

### 新事实：独立语义审核

**facts[0]**：`{"attribute":"experience with simulated skydiving","conditions":{"kind":"unconditional"},"fact_id":"f1","modality":"asserted","quotes":[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"User directly states having tried simulated skydiving recently in a team-building context; 'simulated' explicitly distinguishes it from real skydiving.","subject":"I","uncertainties":[],"value":"tried simulated skydiving at a team-building event recently"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，逐字「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 独立审核 **partial**（事实或关系内核 `supported`）：明确是最近团队活动中的模拟跳伞，不自动代表真实跳伞；unconditional 的完整范围未证实。
- 输出去向 `new_claim`：uncertain[0]（semantic support or bound basis missing）

**facts[1]**：`{"attribute":"affective response to simulated skydiving","conditions":{"kind":"unconditional"},"fact_id":"f2","modality":"asserted","quotes":[{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","source_id":"new-0","unit_id":"manually_mapped_new"}],"rationale":"The phrase 'It was quite thrilling!' is a direct, asserted evaluation of the experience.","subject":"I","uncertainties":[],"value":"found it thrilling"}`

- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，逐字「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户明确觉得这次模拟体验刺激；不能从一次体验外推真实偏好或其他时间。
- 输出去向 `new_claim`：uncertain[1]（semantic support or bound basis missing）

**facts[2]**：`{"attribute":"affective response to adrenaline rush","conditions":{"kind":"unconditional"},"fact_id":"f3","modality":"asserted","quotes":[{"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much.","source_id":"new-2","unit_id":"unsplit-new-2"}],"rationale":"User asserts an unexpected positive affective response to the adrenaline rush, indicating prior expectation of non-enjoyment.","subject":"I","uncertainties":[],"value":"didn't expect to enjoy the adrenaline rush so much"}`

- 引文 `new/new-2/unsplit-new-2`：`valid`，位置 `{"end":73,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，逐字「Yeah, the adrenaline rush was something I didn't expect to enjoy so much.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户说没想到会如此享受肾上腺素；理由声称原先预期完全不享受，比原话更强。
- 输出去向 `new_claim`：uncertain[2]（semantic support or bound basis missing）

**facts[3]**：`{"attribute":"attitude toward trying new things","conditions":{"kind":"unconditional"},"fact_id":"f4","modality":"asserted","quotes":[{"quote":"It's definitely made me more open to trying new things.","source_id":"new-2","unit_id":"unsplit-new-2"}],"rationale":"User explicitly states a change in openness as a consequence of the experience.","subject":"I","uncertainties":[],"value":"more open to trying new things"}`

- 引文 `new/new-2/unsplit-new-2`：`valid`，位置 `{"end":129,"start":74}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，逐字「It's definitely made me more open to trying new things.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户说更愿尝试新事物；不应扩大为真实极限运动喜好改变。
- 输出去向 `new_claim`：uncertain[3]（semantic support or bound basis missing）

**facts[4]**：`{"attribute":"priority regarding safety","conditions":{"kind":"unconditional"},"fact_id":"f5","modality":"asserted","quotes":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","source_id":"new-8","unit_id":"unsplit-new-8"}],"rationale":"User affirms continued prioritization of safety, using 'still' to signal persistence of this value despite new thrill-seeking behavior.","subject":"I","uncertainties":[],"value":"still prioritize safety"}`

- 引文 `new/new-8/unsplit-new-8`：`valid`，位置 `{"end":105,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，逐字「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户明确说仍优先考虑安全；该句未确认完整旧因果关系或所有时间。
- 输出去向 `new_claim`：uncertain[4]（semantic support or bound basis missing）

**facts[5]**：`{"attribute":"temporal framing of current engagement","conditions":{"kind":"unconditional"},"fact_id":"f6","modality":"asserted","quotes":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","source_id":"new-8","unit_id":"unsplit-new-8"}],"rationale":"'For now' signals a provisional, non-committal stance toward sustained engagement with thrill-seeking activities.","subject":"I","uncertainties":[],"value":"for now, enjoying the thrill and seeing where it takes me"}`

- 引文 `new/new-8/unsplit-new-8`：`valid`，位置 `{"end":105,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，逐字「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
- 独立审核 **partial**（事实或关系内核 `supported`）：用户说目前享受刺激并观察后续；理由关于长期参与刺激活动的解释超出原话。
- 输出去向 `new_claim`：uncertain[5]（semantic support or bound basis missing）

### 旧关系：独立语义审核

**relations[0]**：`{"affected_part":"skydiving","fact_id":"f1","old_attribute":"attitude toward extreme sports","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Dislikes extreme sports (e.g., skydiving)","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","unit_id":"u1"}],"old_subject":"I","old_value":"dislikes extreme sports (e.g., skydiving)","rationale":"Simulated skydiving is a variant of skydiving; user’s trial does not contradict dislike of *extreme* skydiving but adds nuance: they engaged with a *simulated*, lower-risk version — supplementing, not replacing, the prior generalization.","relation":"supplement","relation_id":"r1","semantic_basis":[{"quote":"simulated skydiving","side":"new","source_id":"new-0"},{"quote":"skydiving","side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"}],"temporal_order":{"basis":[{"quote":"recently","side":"new","source_id":"new-0"}],"explanation":"New fact specifies 'recently', while old memory lacks temporal anchoring but is from earlier session (Sep 2025 vs Apr 2026); 'recently' in new-0 refers to time before Apr 10, 2026, thus after Sep 2025.","relation":"after"},"uncertainties":["Whether 'simulated skydiving' is semantically subsumed under 'extreme sports' per user’s original definition remains unspecified; user treats it as distinct by qualifying it as 'simulated' and pairing it with safety affirmation."],"unit_id":"u1"}`

- 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1`：`valid`，位置 `{"end":41,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，逐字「Dislikes extreme sports (e.g., skydiving)」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，逐字「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：模拟体验与真实极限运动的旧态度之间影响未知；低风险及 after、旧事实有效时间由模型补推。
- 输出去向 `old_relation`：uncertain[6]（Whether 'simulated skydiving' is semantically subsumed under 'extreme sports' per user’s original definition remains unspecified; user treats it as distinct by qualifying it as 'simulated' and pairing it with safety affirmation.）；uncertain[9]（model_relation=r1;index=0）

**relations[1]**：`{"affected_part":"high injury risk","fact_id":"f1","old_attribute":"reason for disliking extreme sports","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","unit_id":"u2"}],"old_subject":"I","old_value":"due to high injury risk","rationale":"User’s choice of *simulated* skydiving — explicitly lower-risk — aligns with prior concern about injury risk; this action reflects risk-mitigated engagement rather than abandonment of the safety rationale.","relation":"supplement","relation_id":"r2","semantic_basis":[{"quote":"simulated skydiving","side":"new","source_id":"new-0"},{"quote":"due to high injury risk","side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"}],"temporal_order":{"basis":[{"quote":"recently","side":"new","source_id":"new-0"}],"explanation":"Same temporal reasoning as r1: 'recently' places event after prior memory dated Sep 2025.","relation":"after"},"uncertainties":["No explicit statement confirming user perceives simulated skydiving as low-injury-risk; inference relies on conventional understanding and user’s concurrent safety affirmation (f5)."],"unit_id":"u2"}`

- 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u2`：`valid`，位置 `{"end":65,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，逐字「Dislikes extreme sports (e.g., skydiving) due to high injury risk」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，逐字「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：选择模拟活动不证明用户认为其低风险，亦不独立证明旧受伤风险原因继续或消失；after 缺相对旧状态依据。
- 输出去向 `old_relation`：uncertain[7]（No explicit statement confirming user perceives simulated skydiving as low-injury-risk; inference relies on conventional understanding and user’s concurrent safety affirmation (f5).）；uncertain[12]（model_relation=r2;index=1）

**relations[2]**：`{"affected_part":"commitment to safety and well-being","fact_id":"f5","old_attribute":"commitment","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"conflicting with commitment to safety and well-being","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","unit_id":"u3"}],"old_subject":"I","old_value":"commitment to safety and well-being","rationale":"User reaffirms prioritization of safety, directly echoing the core value ('safety and well-being') cited in u3 as the basis for prior avoidance; 'still' confirms persistence, not change.","relation":"same","relation_id":"r3","semantic_basis":[{"quote":"I still prioritize safety, of course.","side":"new","source_id":"new-8"},{"quote":"commitment to safety and well-being","side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"}],"temporal_order":{"basis":[{"quote":"I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"'Still' indicates continuity of the commitment expressed in u3; no temporal displacement implied — both refer to enduring values.","relation":"same"},"uncertainties":[],"unit_id":"u3"}`

- 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u3`：`valid`，位置 `{"end":119,"start":67}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，逐字「conflicting with commitment to safety and well-being」。
- 引文 `new/new-8/unsplit-new-8`：`valid`，位置 `{"end":105,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，逐字「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
- 独立审核 **partial**（事实或关系内核 `partial`）：当前仍优先安全有依据，但不能据此确认旧陈述中的完整安全与福祉因果、同一有效时间或无条件范围。
- 输出去向 `old_relation`：uncertain[13]（semantic support or bound basis missing）

**relations[3]**：`{"affected_part":"skydiving","fact_id":"f2","old_attribute":"attitude toward skydiving","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Dislikes extreme sports (e.g., skydiving)","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","unit_id":"u1"}],"old_subject":"I","old_value":"dislikes extreme sports (e.g., skydiving)","rationale":"User reports finding simulated skydiving 'quite thrilling', which contradicts a blanket 'dislike' of skydiving — even if qualified as simulated — because the affective valence (thrill) is positive and specific to that activity instance.","relation":"change","relation_id":"r4","semantic_basis":[{"quote":"It was quite thrilling!","side":"new","source_id":"new-0"},{"quote":"Dislikes extreme sports (e.g., skydiving)","side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"}],"temporal_order":{"basis":[{"quote":"recently","side":"new","source_id":"new-0"}],"explanation":"Same as r1.","relation":"after"},"uncertainties":["Whether 'thrilling' implies reversal of 'dislike' or merely coexistence of positive sensation with prior aversion is ambiguous; however, 'dislikes' is a categorical judgment incompatible with reporting the same activity as thrilling without qualification — hence change is warranted."],"unit_id":"u1"}`

- 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1`：`valid`，位置 `{"end":41,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，逐字「Dislikes extreme sports (e.g., skydiving)」。
- 引文 `new/new-0/manually_mapped_new`：`valid`，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，逐字「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：觉得模拟体验刺激不证明真实跳伞厌恶消失；模型把正面体验与旧普遍偏好视为互斥缺依据，after 亦不成立。
- 输出去向 `old_relation`：uncertain[8]（Whether 'thrilling' implies reversal of 'dislike' or merely coexistence of positive sensation with prior aversion is ambiguous; however, 'dislikes' is a categorical judgment incompatible with reporting the same activity as thrilling without qualification — hence change is warranted.）；uncertain[10]（semantic support or bound basis missing）

**relations[4]**：`{"affected_part":"Dislikes extreme sports","fact_id":"f4","old_attribute":"attitude toward extreme sports","old_conditions":{"kind":"unconditional"},"old_quotes":[{"quote":"Dislikes extreme sports (e.g., skydiving)","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","unit_id":"u1"}],"old_subject":"I","old_value":"dislikes extreme sports (e.g., skydiving)","rationale":"Stating being 'more open to trying new things' — in direct response to the simulated skydiving experience — undermines the prior categorical 'dislikes', indicating a shift in disposition toward novelty, including previously avoided domains.","relation":"change","relation_id":"r5","semantic_basis":[{"quote":"It's definitely made me more open to trying new things.","side":"new","source_id":"new-2"},{"quote":"Dislikes extreme sports (e.g., skydiving)","side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"}],"temporal_order":{"basis":[{"quote":"It's definitely made me more open to trying new things.","side":"new","source_id":"new-2"}],"explanation":"'Made me' signals causal emergence post-experience; experience occurred recently (per new-0), thus after old memory.","relation":"after"},"uncertainties":[],"unit_id":"u1"}`

- 引文 `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1`：`valid`，位置 `{"end":41,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`，逐字「Dislikes extreme sports (e.g., skydiving)」。
- 引文 `new/new-2/unsplit-new-2`：`valid`，位置 `{"end":129,"start":74}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`，逐字「It's definitely made me more open to trying new things.」。
- 独立审核 **unsupported**（事实或关系内核 `unsupported`）：更愿尝试新事物不证明真实极限运动偏好改变；模型自行推断覆盖该领域和相对旧状态先后。
- 输出去向 `old_relation`：uncertain[11]（semantic support or bound basis missing）

规划结果：`{"add":0,"modify":0,"preserve":0,"uncertain":14}`；可编辑位置 `[]`。

对比与限制：v4 将模拟体验与开放态度合并；v5 成功单独列出模拟活动、刺激、开放及安全，但仍多次把体验或开放推断为真实极限运动偏好变化，且错误推断相对旧事实 after。

## 复现与限制

离线复核不调用模型：
```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

事实完整性按本报告逐案列出的人工核对目标判断，不能保证枚举源对话中的全部细节。人工语义审核不改变默认计划；如需安全执行更新，仍需要单独的授权和写入方案。本次不把有依据的新事实等同于允许修改旧事实。
