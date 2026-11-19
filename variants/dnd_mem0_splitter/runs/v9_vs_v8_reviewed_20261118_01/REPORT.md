# v8 / v9：5 条旧记忆逐案对照

本试验逐字复用 5 组既有 v8 输入；每组 v9 仅一次 `qwen-plus-2025-12-01` 请求，`enable_thinking=false`，SDK 重试关闭。5 次均返回指定模型并通过原有结构、ID、逐字引文检查；完整调用记录见 `batch_completion.json`。本报告中的语义检查为助手初审，需人工确认；引文逐字匹配不证明 supports 或语义正确。

5 条中 v8 均为 1 条，v9 只有 Susan 案拆为 2 条，其余仍为 1 条。样本是定向选取且部分曾用于设计，不是独立总体评估，也不能从单次输出计算可靠率。v8 和 v9 虽使用同一模型与输入，调用时间不同，模型服务和采样仍可能变化。未修改提示词来追逐本次结果。

## 检查汇总

| 案例 / 主目标 | v8 → v9 数量 | 局部更新与粒度 | 遗漏、语义及待确认 |
|---|---:|---|---|
| 01_susan / 4 | 1 → 2 | v9 将朋友关系与支持拆为两条，相比 v8 的一条更便于分别更新；支持条保留 ThomasSusan/Susan 与受支持者。 | 未发现正文漏掉旧事实。v9 的 memory supports 说引文本身确定“用户”是朋友，超出该引文：主体需上下文支持。姓名是否为拼接等仍未证实，v8 有待确认项，v9 的待确认项却为空，须人工核查。 |
| 02_skydiving / 8 | 1 → 1 | 两版都是一条；将不喜欢、受伤风险和安全健康冲突保持一起合理，局部原因改动时应在该关系内处理，避免变成无条件断言。 | 旧记忆的否定和因果保留。原对话的 because 直接关联 avoid，而不是直接将其写成 dislike 的原因；v9 supports 将 avoid 称为行为后果，来源未明确说明是“不喜欢”的后果，解释可能越界。 |
| 03_director / 10 | 1 → 1 | 两版都是一条。保留公司与职位的关系是合理的，但 v9 未实现雇主与职位分别维护的目标；若职位改变，需要修改整条并保留公司。 | 旧文本的雇主和职位均在。上下文是 2025-09-05 的自述，v9 没有记录现在时的时间锚点或待确认项，不能据此认定当前职位；可分别形成带相同工作关系和时间边界的条目，但不能随意延长状态。 |
| 04_persian_cat / 14 | 1 → 1 | 两版都是一条。原因与喜欢保持相连是合理的；多种理由无法分别修改，后续若拆分仍须保留各理由与喜欢的因果及其作用范围。 | 旧记忆各项理由均保留。用户原话明确的 because 与高贵、平静相连；优雅和历史说的是猫给家带来的效果，v9 supports 将其全部表述为确认喜欢的理由偏强，需人工确认。 |
| 05_career_history / 24 | 1 → 1 | 两版都是一条，保留过去时间和具体公司与职位。雇主和职位不能单独维护，v9 未在此实现可分别修改的粒度。 | 旧事实和 previously 保留，时间起止待确认。v9 的第二个 pending 称上下文缺少大小写一致性，但两处 Blockchain Tech 大小写实际上相同；这是待确认理由中的无依据描述，不应采信。 |

## 逐案并排：全部原始及补足子事实、引文和待确认项

### 01_susan · 审核主目标 4

**旧记忆：** Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

**相同输入上下文：** user，Sep 06, 2025, 01:02:20：ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.

**上下文来源：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [60:218]`

| v8 全部子事实 | v9 全部子事实 |
|---|---|
| **#1 raw:** Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement<br><br>**contextualized:** The user has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement.<br><br>**引文 [memory/a1332815-d6ba-4bdc-9ffa-657f7315d0ed]:** “Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement”<br>**supports:** Old memory states the user has a friend named ThomasSusan, referred to as 'Susan', who provides support and encouragement.<br><br>**引文 [context/ctx-1]:** “ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.”<br>**supports:** The speaker ('user') explicitly identifies ThomasSusan as 'my Friend' and refers to 'Susan's support and encouragement', confirming the user is the subject of the friendship and recipient of that support; 'Susan' is used as a referential form for ThomasSusan in this utterance.<br><br>**待确认：** Whether 'ThomasSusan' is a single compound name (e.g., legal or preferred name) or a conflation/concatenation of two names (e.g., 'Thomas' and 'Susan')<br>**原因：** The memory text writes 'ThomasSusan' as one token without internal punctuation or explanation; the context quote repeats 'ThomasSusan' identically but does not clarify orthographic or identity intent. No source disambiguates whether this is a full name, nickname, typo, or merged reference.<br><br>**待确认：** Whether 'provides support and encouragement' in the memory corresponds precisely to 'Susan's support and encouragement inspire me...' in context — specifically, whether the inspiration effect is part of the original factual claim or an added interpretation<br>**原因：** The memory states Susan 'provides support and encouragement' (neutral action); the context adds that this 'inspires [the user] to maintain focus on promoting well-being'. The inspirational effect is not asserted in the memory text and cannot be assumed part of the raw subfact without conflating description with consequence. | **#1 raw:** Has a friend named ThomasSusan (referred to as 'Susan')<br><br>**contextualized:** User has a friend named ThomasSusan, who is referred to as 'Susan'.<br><br>**引文 [memory/a1332815-d6ba-4bdc-9ffa-657f7315d0ed]:** “Has a friend named ThomasSusan (referred to as 'Susan')”<br>**supports:** Old memory explicitly states the user has a friend named ThomasSusan, with the note that this person is referred to as 'Susan'.<br><br>**引文 [context/ctx-1]:** “ThomasSusan is my Friend”<br>**supports:** Context confirms 'ThomasSusan' is the user's friend and uses first-person 'my', supporting that the subject of the friendship is the user.<br><br>**待确认：** [] |
| — | **#2 raw:** ThomasSusan (referred to as 'Susan') provides support and encouragement<br><br>**contextualized:** ThomasSusan (referred to as 'Susan') provides support and encouragement to the user.<br><br>**引文 [memory/a1332815-d6ba-4bdc-9ffa-657f7315d0ed]:** “ThomasSusan (referred to as 'Susan') who provides support and encouragement”<br>**supports:** Old memory states ThomasSusan (called 'Susan') provides support and encouragement — but does not specify recipient.<br><br>**引文 [context/ctx-1]:** “Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.”<br>**supports:** Context confirms Susan's support and encouragement are directed at the speaker ('inspire me'), establishing the user as the recipient.<br><br>**待确认：** [] |

**局部更新：** v9 将朋友关系与支持拆为两条，相比 v8 的一条更便于分别更新；支持条保留 ThomasSusan/Susan 与受支持者。

**语义检查：** 未发现正文漏掉旧事实。v9 的 memory supports 说引文本身确定“用户”是朋友，超出该引文：主体需上下文支持。姓名是否为拼接等仍未证实，v8 有待确认项，v9 的待确认项却为空，须人工核查。

完整原始 JSON： [v8](01_susan/v8_result.json) · [v9](01_susan/v9_result.json)；原始模型内容见 `raw_content.txt`。

### 02_skydiving · 审核主目标 8

**旧记忆：** Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

**相同输入上下文：** user，Sep 06, 2025, 22:52:30：I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.

**上下文来源：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json#/raw_dialogue/6/content [0:169]`

| v8 全部子事实 | v9 全部子事实 |
|---|---|
| **#1 raw:** Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being<br><br>**contextualized:** User dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with their commitment to safety and well-being<br><br>**引文 [memory/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03]:** “Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being”<br>**supports:** Old memory states a dislike of extreme sports, cites high injury risk as reason, and frames this as conflicting with a commitment to safety and well-being.<br><br>**引文 [context/ctx-1]:** “I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.”<br>**supports:** Confirms the subject is the user (first-person 'I'), validates the causal link ('because'), and confirms the conflict framing ('goes against my commitment').<br><br>**待确认：** [] | **#1 raw:** Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being<br><br>**contextualized:** User dislikes extreme sports (e.g., skydiving) due to high injury risk, which conflicts with their commitment to safety and well-being.<br><br>**引文 [memory/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03]:** “Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being”<br>**supports:** Old memory states a dislike of extreme sports linked causally to injury risk and framed as conflicting with a commitment to safety and well-being.<br><br>**引文 [context/ctx-1]:** “I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.”<br>**supports:** Confirms the subject is the user (first-person 'I'), specifies 'avoid' as behavioral consequence, and preserves the causal chain (injury risk → conflict with commitment); 'such as skydiving' matches 'e.g., skydiving'; 'goes against' matches 'conflicting with'.<br><br>**待确认：** [] |

**局部更新：** 两版都是一条；将不喜欢、受伤风险和安全健康冲突保持一起合理，局部原因改动时应在该关系内处理，避免变成无条件断言。

**语义检查：** 旧记忆的否定和因果保留。原对话的 because 直接关联 avoid，而不是直接将其写成 dislike 的原因；v9 supports 将 avoid 称为行为后果，来源未明确说明是“不喜欢”的后果，解释可能越界。

完整原始 JSON： [v8](02_skydiving/v8_result.json) · [v9](02_skydiving/v9_result.json)；原始模型内容见 `raw_content.txt`。

### 03_director · 审核主目标 10

**旧记忆：** Works at Historical Productions Ltd. as a Director

**相同输入上下文：** user，Sep 05, 2025, 14:42:35：I work at Historical Productions Ltd. as a Director.

**上下文来源：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_002/input.json#/raw_dialogue/2/content [55:107]`

| v8 全部子事实 | v9 全部子事实 |
|---|---|
| **#1 raw:** Works at Historical Productions Ltd. as a Director<br><br>**contextualized:** The user works at Historical Productions Ltd. as a Director.<br><br>**引文 [memory/e13b825e-7ec7-4760-821e-0581d8da5650]:** “Works at Historical Productions Ltd. as a Director”<br>**supports:** Old memory states the subject works at Historical Productions Ltd. as a Director; subject is not explicitly named or pronominalized in this fragment.<br><br>**引文 [context/ctx-1]:** “I work at Historical Productions Ltd. as a Director.”<br>**supports:** The first-person utterance by speaker 'user' directly expresses the same role and employer; used to resolve the subject of the memory fragment as the user.<br><br>**待确认：** [] | **#1 raw:** Works at Historical Productions Ltd. as a Director<br><br>**contextualized:** User works at Historical Productions Ltd. as a Director.<br><br>**引文 [memory/e13b825e-7ec7-4760-821e-0581d8da5650]:** “Works at Historical Productions Ltd. as a Director”<br>**supports:** Old memory states a work affiliation and role at Historical Productions Ltd.; subject is not explicitly named in the memory text.<br><br>**引文 [context/ctx-1]:** “I work at Historical Productions Ltd. as a Director.”<br>**supports:** First-person utterance by speaker 'user' confirms the subject is the user and matches the verb form ('work' vs memory's 'Works') and all key content; used to resolve subject and tense normalization.<br><br>**待确认：** [] |

**局部更新：** 两版都是一条。保留公司与职位的关系是合理的，但 v9 未实现雇主与职位分别维护的目标；若职位改变，需要修改整条并保留公司。

**语义检查：** 旧文本的雇主和职位均在。上下文是 2025-09-05 的自述，v9 没有记录现在时的时间锚点或待确认项，不能据此认定当前职位；可分别形成带相同工作关系和时间边界的条目，但不能随意延长状态。

完整原始 JSON： [v8](03_director/v8_result.json) · [v9](03_director/v9_result.json)；原始模型内容见 `raw_content.txt`。

### 04_persian_cat · 审核主目标 14

**旧记忆：** Likes Persian cats because of their regal and calm nature, elegance, and historical charm

**相同输入上下文：** user，Sep 06, 2025, 22:24:16：I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.

**上下文来源：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_003/input.json#/raw_dialogue/6/content [0:144]`

| v8 全部子事实 | v9 全部子事实 |
|---|---|
| **#1 raw:** Likes Persian cats because of their regal and calm nature, elegance, and historical charm<br><br>**contextualized:** User likes Persian cats because of their regal and calm nature, elegance, and historical charm<br><br>**引文 [memory/eef34a57-c82a-4995-877d-66b54b9589da]:** “Likes Persian cats because of their regal and calm nature, elegance, and historical charm”<br>**supports:** Old memory states a liking for Persian cats grounded in three linked attributes: (1) regal and calm nature, (2) elegance, and (3) historical charm.<br><br>**引文 [context/ctx-1]:** “I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.”<br>**supports:** Confirms the user as speaker; links 'regal and calm nature' directly to admiration, and 'elegance' and 'history' to the cats' presence in the home — supporting the attribution of all three qualities to Persian cats as reasons for liking them. 'History' maps to 'historical charm' in the memory text.<br><br>**待确认：** [] | **#1 raw:** Likes Persian cats because of their regal and calm nature, elegance, and historical charm<br><br>**contextualized:** User likes Persian cats because of their regal and calm nature, elegance, and historical charm.<br><br>**引文 [memory/eef34a57-c82a-4995-877d-66b54b9589da]:** “Likes Persian cats because of their regal and calm nature, elegance, and historical charm”<br>**supports:** Old memory states a liking for Persian cats grounded in three linked attributes: (1) regal and calm nature, (2) elegance, and (3) historical charm.<br><br>**引文 [context/ctx-1]:** “I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.”<br>**supports:** Confirms the subject is the user (first-person 'I'), links 'regal and calm nature' directly to admiration, and maps 'elegance' and 'history' (i.e., historical charm) to the effect of their presence at home — supporting the tripartite rationale without altering its scope or causal framing.<br><br>**待确认：** [] |

**局部更新：** 两版都是一条。原因与喜欢保持相连是合理的；多种理由无法分别修改，后续若拆分仍须保留各理由与喜欢的因果及其作用范围。

**语义检查：** 旧记忆各项理由均保留。用户原话明确的 because 与高贵、平静相连；优雅和历史说的是猫给家带来的效果，v9 supports 将其全部表述为确认喜欢的理由偏强，需人工确认。

完整原始 JSON： [v8](04_persian_cat/v8_result.json) · [v9](04_persian_cat/v9_result.json)；原始模型内容见 `raw_content.txt`。

### 05_career_history · 审核主目标 24

**旧记忆：** Previously worked as a senior developer in Blockchain Tech

**相同输入上下文：** user，Sep 05, 2025, 09:10:09：I work at Blockchain Tech as a senior developer.

**上下文来源：** `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_002/input.json#/raw_dialogue/2/content [61:109]`

| v8 全部子事实 | v9 全部子事实 |
|---|---|
| **#1 raw:** Previously worked as a senior developer in Blockchain Tech.<br><br>**contextualized:** The user previously worked as a senior developer at Blockchain Tech.<br><br>**引文 [memory/05afde13-35bd-4d26-bbae-6de427d58db1]:** “Previously worked as a senior developer in Blockchain Tech”<br>**supports:** Old memory states prior employment as a senior developer in Blockchain Tech.<br><br>**引文 [context/ctx-1]:** “I work at Blockchain Tech as a senior developer.”<br>**supports:** The speaker (user) self-identifies as currently working at Blockchain Tech as a senior developer; this confirms the user is the subject of the role and organization, supporting attribution of the past role to the same person. It does not confirm the past-tense 'previously worked' — only that the role and company are consistent and speaker-identified.<br><br>**待确认：** Temporal scope of 'previously worked'<br>**原因：** The memory asserts past employment, but the context shows current employment; no information is provided about when the prior role ended or whether it was the same position, a prior iteration, or a different engagement. The word 'previously' lacks anchoring time point or duration in both memory and context.<br><br>**待确认：** Exact nature of employment relationship during the prior period<br>**原因：** Memory says 'worked as a senior developer', but does not specify full-time, contract, internal vs. client-facing, or team context. Context only confirms current role, not historical details. | **#1 raw:** Previously worked as a senior developer in Blockchain Tech<br><br>**contextualized:** The user previously worked as a senior developer in Blockchain Tech.<br><br>**引文 [memory/05afde13-35bd-4d26-bbae-6de427d58db1]:** “Previously worked as a senior developer in Blockchain Tech”<br>**supports:** Old memory states prior employment as a senior developer at Blockchain Tech.<br><br>**引文 [context/ctx-1]:** “I work at Blockchain Tech as a senior developer.”<br>**supports:** The speaker (user) uses first-person present-tense to state current employment at Blockchain Tech in the same role; this confirms the identity of the subject ('user') and the factual plausibility of the prior role, but does not confirm the temporal scope or end date of the prior role. It does not support that the prior role ended before Sep 05, 2025 — only that the current role is ongoing as of that date.<br><br>**待确认：** Temporal boundary of 'previously worked'<br>**原因：** The memory asserts past employment, but provides no start/end dates or relative timing (e.g., 'before joining X', 'until last year'). The context states current employment as of Sep 05, 2025, but does not specify whether the 'previous' role was immediately prior, overlapping, or separated by a gap. Thus, the duration, sequence, and termination of the prior role remain unspecified.<br><br>**待确认：** Whether 'Blockchain Tech' refers to the same organization in both memory and context<br>**原因：** Both memory and context name 'Blockchain Tech', but neither provides a disambiguating identifier (e.g., legal name, domain, incorporation details). The context quote lacks capitalization consistency or qualifying modifiers, and no source confirms organizational identity unambiguously. |

**局部更新：** 两版都是一条，保留过去时间和具体公司与职位。雇主和职位不能单独维护，v9 未在此实现可分别修改的粒度。

**语义检查：** 旧事实和 previously 保留，时间起止待确认。v9 的第二个 pending 称上下文缺少大小写一致性，但两处 Blockchain Tech 大小写实际上相同；这是待确认理由中的无依据描述，不应采信。

完整原始 JSON： [v8](05_career_history/v8_result.json) · [v9](05_career_history/v9_result.json)；原始模型内容见 `raw_content.txt`。

## 可追溯性

`manifest.json` 包含输入 SHA-256、模型、提示词版本和哈希；每个目录的 `input.json` 为原运行文件逐字节复制，`provenance.json` 保留快照与原始对话来源。`request_audit.json` 核对了实际客户端请求体的模型、thinking 参数、提示词哈希和输入；`response_metadata.json` 与 `report.json` 保存返回模型及错误。`frozen_prompt.txt` 为调用前冻结的 v9 提示词。服务端内部执行细节不由客户端审计证明。

目标 24 对应的是该会话的旧职业保护对象，并非获客新事实。来源记录时间是发言时间，不自动是事件发生时间。没有导入、调用或写入 Mem0；没有运行完整数据集。
