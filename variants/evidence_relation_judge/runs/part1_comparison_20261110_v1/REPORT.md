# 组件一：五个定向案例的受控对照

## 结论与范围

本次比较 v2 与严格版 v5；v4 是在复查标签含义前完成的探索版本，保留全部原始结果。五例为定向开发案例；v5 在看过 v4 部分结果后制定，非盲测，不能计算或声称总体准确率。人工审核确认的是事实及允许更新边界，**不是本次六标签的独立盲标**；下述标签优劣是研究者暂定分析，需人工确认。

范围只涉及组件一；未修改拆分器、组件二，未调用或写入 Mem0。组件一输出是待审核候选，不执行更新。

## 接口、方案与改动

- v2 六个标签：support（支持，无实质新增）、possible_change（同一对象属性可能随时间或条件变化或存在未定冲突）、historical_correction（明确纠正同一历史事实）、supplement（相容新增但本身不支持旧事实）、no_clear_impact（可判断无明显影响）、uncertain（证据等不足，无法可靠判其他类别）。后四种和前两种均保留原始含义。
- 候选字段为 memory_id、fact_index、old_subfact、relation、object、attribute、conditions、candidate_impact_fragment、old_quote、new_quote、reason、confirmation_questions；字段必须完全匹配。v2 以每旧子事实一次模型调用，不重试。校验请求与来源、标签/字段类型、身份、旧片段定位、新旧引文；旧片段仅允许唯一大小写修正。格式和字面引文匹配**不能证明语义正确**。
- 组件二 `scope_planner.py` 重新执行 v1 的严格 candidate 校验、复核 v2 原始片段定位，要求 upstream status/validation 均成功，传播 confirmation_questions，另行提取和审阅范围；`scope_planner_v2.py` 的独立阶段抽取有独立门控。新增候选字段、新标签或改含义会影响组件二；它并不把上游标签作为已经验证的事实。
- v4 在 v2 的提示词后增加阶段、混合、属性、活动、身份、时间规则；程序结构、输出和校验不变。但 v4 将纯粹的单标签表达不足映射为 uncertain，扩展了原有证据不足场景，不能视作严格保留标签语义，因而只留作探索结果。
- v5 将清楚的“既支持又新增、且无纠错或阶段变化”标为模型内部保留符 `mixed_unrepresentable`，理由分别描述两部分；v2 原校验拒绝该标记，结果保留为 `partial_or_error`／上游 error，并附未验证 sidecar。这不是新增合法标签，也不会把它映射成其他既有标签。普通候选结构不变；组件二对混合行走已有上游错误路径，不能自动处理新增和支持，也不会得到有效的普通候选。若未来要机器处理两种关系，需明确扩展接口与组件二；这次没有修改。
- v5 的混合拦截只在模型自己输出该保留符时起作用，**不能保证识别混合证据**。阶段变化优先 possible_change；同对象不同属性单独比较；模拟与真实活动分开；理由不得从“我的公司”推断雇佣、职务或所有权；记录时间不代替事件时间。上述是提示要求，不是程序保证。
- 变更：新增 `relation_judge_v4.py` / `run_local_v4.py`、`relation_judge_v5.py` / `run_local_v5.py`、相应契约测试与本次运行脚本；v5 新增的程序逻辑仅在模型选中混合保留符时附加未验证 sidecar，沿用 v2 错误处理。单线程运行适配器临时替换 v2 提示词，finally 恢复，不支持并发线程。

## 受控设置与实际执行

- 五个请求逐字取自既有 `dev_scope_review_20261109_v1/*_result.json` 的 request，每例恰好一个旧子事实。输入、完整提示词、完整模型消息、原始响应、解析/校验/错误和耗时均保存在本目录；见 `inputs.json`、`manifest.json`、各版本目录和 completion 文件。
- v2 与 v4 在同一进程使用同一模型实例，依次每例先 v2 再 v4。v5 因发现 v4 的标签语义问题而在独立进程重新加载相同路径的本地 Qwen3-8B；Python、模型加载方式、BF16、cuda:0、贪心 `do_sample=False`、`enable_thinking=False`、上限 768 和原始输入相同。两次进程不是同一实例，也非随机化顺序；共享 GPU 上存在其他进程，耗时并非严格性能基准。
- Transformers 提示 temperature、top_p、top_k 在当前生成模式下可能被忽略，两组设置一致。generation_config 与模型文件、代码的 SHA-256 见 manifest；未设置其他生成参数时沿用模型和库默认值。
- 前一进程模型加载 16.429 秒，含加载累计 136.17 秒；v5 加载 9.79 秒，含加载累计 73.258 秒。每案例每版真实调用一次：v2 5 次、v4 5 次、v5 5 次，共 15 次，无自动重试；v4 是额外探索，不充作 v5 的重试。模型调用时间与显存见各文件。

|案例|版本|调用|状态|生成 token|秒|到达 EOS|上限截断迹象|
|---|---|---:|---|---:|---:|---|---|
|job_transition|v2|1|ok|242|10.754|True|False|
|job_transition|v4|1|ok|269|11.044|True|False|
|job_transition|v5|1|ok|275|11.957|True|False|
|persian_cats|v2|1|ok|285|11.519|True|False|
|persian_cats|v4|1|ok|313|12.708|True|False|
|persian_cats|v5|1|ok|284|11.516|True|False|
|skydiving|v2|1|ok|356|14.329|True|False|
|skydiving|v4|1|ok|356|14.377|True|False|
|skydiving|v5|1|ok|357|14.341|True|False|
|career_history|v2|1|ok|292|11.71|True|False|
|career_history|v4|1|ok|285|11.532|True|False|
|career_history|v5|1|ok|357|14.328|True|False|
|promotion|v2|1|ok|268|10.767|True|False|
|promotion|v4|1|ok|270|10.923|True|False|
|promotion|v5|1|ok|279|11.275|True|False|

15 次真实输出均解析并通过既有格式／引文校验，均以 EOS 结束，未出现长度上限截断；这不证明语义正确。v5 五例均未输出混合保留符，因此没有真实触发混合拦截；该错误路径仅由合成契约测试验证。截断判定记录为生成达到 768 且末 token 非 EOS；解析/校验错误按各 JSON 原样保留，不自动重试。

## 逐案例：事实边界、原文和候选

各项输出均为模型候选；以下关系和理由正确性均待人工确认。新证据所列 recorded_at 是消息记录时间，不是事件发生时间。

### 转岗 / job_transition（人工记录 7）

- 旧子事实：`Looking for a new job with better work-life balance`。
- 人工确认新状态：截至2026-03-01用户确认已转到新岗位，自述工作生活平衡更健康；不能仅以仍等待完成此次转岗概括当前进展。
- 允许范围：更新所讨论这次岗位转变的当前进展，正确保留历史；2026-03-01仅为确认时间；不推断此后不再寻找任何机会。
- 人工未知：{"新雇主": "未知", "新职称": "未知", "薪资": "未知", "组织性质": "未知", "具体转岗日期": "未知", "是否离开Huaxin Consulting": "未知"}
- 新证据：
  - `dialogue-0` / `Mar 01, 2026, 07:04:00`：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.
  - `dialogue-2` / `Mar 01, 2026, 07:09:03`：Yes, the new role has definitely improved my mental health. The stress and pressure from my previous job were really taking a toll.

**v2**（状态 `ok`）：
- 关联与条件：object="User"；attribute="looking for a new job with better work-life balance"；conditions="current role not supporting well-being"。
- 关系：`support`；旧片段原始="Looking for a new job with better work-life balance"；定位={"raw": "Looking for a new job with better work-life balance", "located": "Looking for a new job with better work-life balance", "method": "exact", "start": 0, "end": 51}。
- 旧引文："Looking for a new job with better work-life balance"；新引文：{"source_id": "dialogue-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}。
- 理由：新证据表明用户已经找到了新的工作，并且工作与生活平衡得到了改善，这支持了旧事实中用户正在寻找更好工作与生活平衡的陈述。；问题：[]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v4**（状态 `ok`）：
- 关联与条件：object="User"；attribute="job search"；conditions="seeking better work-life balance"。
- 关系：`historical_correction`；旧片段原始="Looking for a new job with better work-life balance"；定位={"raw": "Looking for a new job with better work-life balance", "located": "Looking for a new job with better work-life balance", "method": "exact", "start": 0, "end": 51}。
- 旧引文："Looking for a new job with better work-life balance"；新引文：{"source_id": "dialogue-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}。
- 理由：新证据表明用户已经找到了新的工作，并且工作与生活平衡得到了改善，这与旧事实中用户正在寻找新工作的状态存在冲突，因此需要对旧事实进行更正。；问题：["用户是否已经找到了新的工作？", "新工作是否确实改善了用户的工作与生活平衡？"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v5**（状态 `ok`）：
- 关联与条件：object="User"；attribute="job search"；conditions="seeking better work-life balance"。
- 关系：`historical_correction`；旧片段原始="Looking for a new job with better work-life balance"；定位={"raw": "Looking for a new job with better work-life balance", "located": "Looking for a new job with better work-life balance", "method": "exact", "start": 0, "end": 51}。
- 旧引文："Looking for a new job with better work-life balance"；新引文：{"source_id": "dialogue-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}。
- 理由：新证据表明用户已经找到了新工作并实现了更好的工作与生活平衡，这与旧陈述中用户仍在寻找新工作的状态存在矛盾，因此需要对旧陈述进行更正。；问题：["用户是否在新工作中确实实现了更好的工作与生活平衡？", "旧陈述中提到的寻找新工作的状态是否已经改变？"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**初步比较（待确认）：** v2 将已转岗当作对仍在找工作的支持；v4/v5 虽识别阶段差异，却标 historical_correction 并称旧陈述需要更正。人工记录认为旧求职历史真实，仅当前阶段推进；按本次规则可能是 possible_change，但标签仍待人工确认。v4/v5 还询问材料已明确的内容。

### 波斯猫 / persian_cats（人工记录 14）

- 旧子事实：`Likes Persian cats because of their regal and calm nature, elegance, and historical charm`。
- 人工确认新状态：Williams Daniel自述近期参加电影节、观看波斯猫纪录片后，对其历史传承和王室关联的欣赏加深。
- 允许范围：补充纪录片体验及欣赏加深，保留原喜好；历史内容作为用户欣赏对象记录，不扩写成外部验证的品种史结论。
- 人工未知：准确观看日期、电影节与纪录片名称和地点未知；暹罗猫偏好及另一纪录片经历未获充分确定。
- 新证据：
  - `dialogue-0` / `Apr 10, 2026, 11:06:07`：I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty.
  - `dialogue-2` / `Apr 10, 2026, 11:15:58`：The history of Persian cats aligns perfectly with my interest in historical authenticity. However, I do reflect on the practical challenges of maintaining their regal appearance.

**v2**（状态 `ok`）：
- 关联与条件：object="Persian cats"；attribute="regal and calm nature, elegance, and historical charm"；conditions=""。
- 关系：`support`；旧片段原始="Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；定位={"raw": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "located": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "method": "exact", "start": 0, "end": 89}。
- 旧引文："Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；新引文：{"source_id": "dialogue-0", "quote": "I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty."}。
- 理由：新证据表明用户对波斯猫的历史渊源和与皇室的联系更加钦佩，这与旧事实中提到的用户喜欢波斯猫因其高贵、冷静的天性、优雅和历史魅力是一致的，因此新证据支持旧事实。；问题：[]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v4**（状态 `ok`）：
- 关联与条件：object="Persian cats"；attribute="regal and calm nature, elegance, and historical charm"；conditions="user's preference"。
- 关系：`supplement`；旧片段原始="Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；定位={"raw": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "located": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "method": "exact", "start": 0, "end": 89}。
- 旧引文："Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；新引文：{"source_id": "dialogue-0", "quote": "I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty."}。
- 理由：新证据补充了用户对波斯猫历史渊源和与皇室关联的进一步欣赏，这与旧事实中提到的历史魅力相容，但未改变原有事实。；问题：["新证据是否明确表示用户对波斯猫的喜好发生了变化？", "用户是否在新证据中提到对波斯猫的其他属性有新的看法？"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v5**（状态 `ok`）：
- 关联与条件：object="Persian cats"；attribute="regal and calm nature, elegance, and historical charm"；conditions=""。
- 关系：`support`；旧片段原始="Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；定位={"raw": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "located": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm", "method": "exact", "start": 0, "end": 89}。
- 旧引文："Likes Persian cats because of their regal and calm nature, elegance, and historical charm"；新引文：{"source_id": "dialogue-0", "quote": "I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty."}。
- 理由：新证据表明用户对波斯猫的历史渊源和与皇室的关联更加钦佩，这与旧事实中提到的用户喜欢波斯猫因其高贵、冷静的天性、优雅和历史魅力相一致，因此新证据支持旧事实。；问题：[]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**初步比较（待确认）：** v2 和 v5 标 support，理由涉及更钦佩，但没有清楚分开旧喜好受到支持与观看纪录片、欣赏加深的新增；v4 标 supplement 并说欣赏进一步加深，但未明确同时支持旧喜好，且有重复或不必要问题。三者均未按所提混合策略完整表达；标签待人工确认。对品种历史不作外部事实验证。

### 跳伞 / skydiving（人工记录 8）

- 旧子事实：`Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`。
- 人工确认新状态：Martin自述近期在团建中尝试并享受模拟跳伞，更愿意尝试新事物，同时仍将安全放在首位。
- 允许范围：补充本次模拟体验；保留旧安全顾虑的历史及原因，不整体删除，也不将旧宽泛概括作为无例外当前规则来否定新体验。一次正面体验不扩写为长期稳定偏好。
- 人工未知：真实跳伞的当前具体态度证据不足；准确体验日期、具体设施与安全程度未知。
- 新证据：
  - `dialogue-0` / `Apr 10, 2026, 10:40:32`：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
  - `dialogue-2` / `Apr 10, 2026, 10:48:20`：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
  - `dialogue-8` / `Apr 10, 2026, 10:57:54`：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.

**v2**（状态 `ok`）：
- 关联与条件：object="extreme sports (e.g., skydiving)"；attribute="dislike"；conditions="due to high injury risk, conflicting with commitment to safety and well-being"。
- 关系：`possible_change`；旧片段原始="Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；定位={"raw": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "located": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "method": "exact", "start": 0, "end": 119}。
- 旧引文："Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；新引文：{"source_id": "dialogue-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}。
- 理由：New evidence shows the user tried simulated skydiving and found it thrilling, indicating a possible change in attitude toward extreme sports. However, the user still prioritizes safety, which may suggest the core commitment to safety and well-being remains unchanged.；问题：["Does the user's experience with simulated skydiving indicate a change in their attitude toward extreme sports?", "Is the user's commitment to safety and well-being still intact despite the new experience?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v4**（状态 `ok`）：
- 关联与条件：object="extreme sports (e.g., skydiving)"；attribute="dislike"；conditions="due to high injury risk, conflicting with commitment to safety and well-being"。
- 关系：`possible_change`；旧片段原始="Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；定位={"raw": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "located": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "method": "exact", "start": 0, "end": 119}。
- 旧引文："Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；新引文：{"source_id": "dialogue-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}。
- 理由：New evidence indicates the user tried simulated skydiving and found it thrilling, suggesting a potential change in attitude toward extreme sports. However, the user still prioritizes safety, indicating the core commitment to safety and well-being remains.；问题：["Does the user's experience with simulated skydiving indicate a change in their attitude toward extreme sports?", "Is the user's continued prioritization of safety consistent with their previous commitment to safety and well-being?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v5**（状态 `ok`）：
- 关联与条件：object="extreme sports (e.g., skydiving)"；attribute="dislike"；conditions="due to high injury risk, conflicting with commitment to safety and well-being"。
- 关系：`possible_change`；旧片段原始="Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；定位={"raw": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "located": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "method": "exact", "start": 0, "end": 119}。
- 旧引文："Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"；新引文：{"source_id": "dialogue-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}。
- 理由：New evidence indicates the user tried simulated skydiving and found it thrilling, suggesting a potential change in attitude toward extreme sports. However, the user still prioritizes safety, indicating the core commitment to safety and well-being remains.；问题：["Does the user's experience with simulated skydiving indicate a change in their general attitude toward extreme sports?", "Is the user's continued prioritization of safety consistent with their previous commitment to safety and well-being?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**初步比较（待确认）：** 三版均标 possible_change，理由均由模拟体验推到对广义极限运动态度可能变化；这超出可确认的模拟体验边界，真实跳伞当前态度未知。三版虽提到安全优先，却重复询问该已明确内容；旧片段均为整句。标签待确认。

### 职业历史 / career_history（人工记录 24）

- 旧子事实：`Previously worked as a senior developer in Blockchain Tech`。
- 人工确认新状态：Donald明确报告咨询公司已经获得一些首批客户，因此感到宽慰并视为重要里程碑；不能弱化成潜在客户或仅计划。
- 允许范围：记录已获客里程碑和用户主观感受，保留启动和获客计划历史；关系作用另存集体归因，不推断财务、合同、数量或全面心理恢复。
- 人工未知：准确获客日期、客户数量和身份、合同付款情况未知；具体家庭创业支持缺充分确认。
- 新证据：
  - `dialogue-0` / `Jan 05, 2026, 07:43:42`：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.

**v2**（状态 `ok`）：
- 关联与条件：object="User"；attribute="employment history"；conditions="previously worked"。
- 关系：`uncertain`；旧片段原始="previously worked as a senior developer in Blockchain Tech"；定位={"raw": "previously worked as a senior developer in Blockchain Tech", "located": "Previously worked as a senior developer in Blockchain Tech", "method": "unique_casefold", "start": 0, "end": 58}。
- 旧引文："Previously worked as a senior developer in Blockchain Tech"；新引文：{"source_id": "dialogue-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}。
- 理由：The new evidence mentions the user's current employment at a consulting firm, but it does not provide any direct information about their previous role as a senior developer in Blockchain Tech. The temporal relationship between the past employment and the current consulting role is unclear.；问题：["Is the user's current employment at a consulting firm related to their previous role as a senior developer in Blockchain Tech?", "Does the new evidence provide any information about the user's employment history prior to their current role at the consulting firm?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v4**（状态 `ok`）：
- 关联与条件：object="User"；attribute="employment status"；conditions="previously worked"。
- 关系：`no_clear_impact`；旧片段原始="previously worked as a senior developer in Blockchain Tech"；定位={"raw": "previously worked as a senior developer in Blockchain Tech", "located": "Previously worked as a senior developer in Blockchain Tech", "method": "unique_casefold", "start": 0, "end": 58}。
- 旧引文："Previously worked as a senior developer in Blockchain Tech"；新引文：{"source_id": "dialogue-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}。
- 理由：The new evidence discusses the user's current employment as a consultant and a recent milestone, but it does not provide any direct information about the user's previous role as a senior developer at Blockchain Tech. Therefore, the new evidence does not clearly impact the old fact.；问题：["Is the current employment at the consulting firm related to the previous role at Blockchain Tech?", "Does the new evidence provide any information about the user's employment history at Blockchain Tech?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v5**（状态 `ok`）：
- 关联与条件：object="user"；attribute="employment status"；conditions="previously worked"。
- 关系：`uncertain`；旧片段原始="previously worked as a senior developer in Blockchain Tech"；定位={"raw": "previously worked as a senior developer in Blockchain Tech", "located": "Previously worked as a senior developer in Blockchain Tech", "method": "unique_casefold", "start": 0, "end": 58}。
- 旧引文："Previously worked as a senior developer in Blockchain Tech"；新引文：{"source_id": "dialogue-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}。
- 理由：The new evidence mentions the user's current employment at a consulting firm, but it does not provide any direct information about their previous role at Blockchain Tech. The memory states the user 'previously worked' there, but the context describes current employment, creating a potential conflict in timing and role. The lack of explicit time anchors or confirmation of the end of the previous role makes it uncertain whether the new evidence supports, contradicts, or is unrelated to the old fact.；问题：["Does the user's current employment at a consulting firm indicate the end of their previous role at Blockchain Tech?", "Is there any evidence in the new quote that confirms or denies the user's previous employment at Blockchain Tech?", "Is the 'previously worked' statement in the memory still valid in light of the user's current employment status?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**初步比较（待确认）：** 三版理由都将“我的咨询公司”推成当前受雇，v4 还称咨询师，提问也带入该前提，故未解决身份推断。v5 还指出旧上下文与 previously 的时态待核，但不能据此认定现实冲突。此输入无其他朋友对话；标签待确认。

### 晋升 / promotion（人工记录 10）

- 旧子事实：`Works at Historical Productions Ltd. as a Director`。
- 人工确认新状态：Williams Daniel当前具体职称为Lead Director，雇主仍为Historical Productions Ltd.；此前Director职称保留为带时间历史。
- 允许范围：本目标核心为当前具体职称变化；保留雇主和有依据的其他知识，历史职称与当前职称分开判断。全会话范围须综合全部新证据，不能将其他有充分证据的属性更新一概判为越界。
- 人工未知：准确晋升日期未知；具体收入金额与储蓄数值尚缺充分用户确认。
- 新证据：
  - `dialogue-0` / `Feb 01, 2026, 18:47:19`：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

**v2**（状态 `ok`）：
- 关联与条件：object="User"；attribute="position"；conditions="at Historical Productions Ltd."。
- 关系：`possible_change`；旧片段原始="Works at Historical Productions Ltd. as a Director"；定位={"raw": "Works at Historical Productions Ltd. as a Director", "located": "Works at Historical Productions Ltd. as a Director", "method": "exact", "start": 0, "end": 50}。
- 旧引文："Works at Historical Productions Ltd. as a Director"；新引文：{"source_id": "dialogue-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}。
- 理由：The new evidence indicates a change in the user's position from 'Director' to 'lead director' at the same company, suggesting a possible change in the role.；问题：["Is the promotion to 'lead director' a new role or an advancement within the 'Director' role?", "Does the term 'lead director' imply a different level of responsibility or authority compared to 'Director'?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v4**（状态 `ok`）：
- 关联与条件：object="User"；attribute="position"；conditions="at Historical Productions Ltd."。
- 关系：`possible_change`；旧片段原始="Works at Historical Productions Ltd. as a Director"；定位={"raw": "Works at Historical Productions Ltd. as a Director", "located": "Works at Historical Productions Ltd. as a Director", "method": "exact", "start": 0, "end": 50}。
- 旧引文："Works at Historical Productions Ltd. as a Director"；新引文：{"source_id": "dialogue-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}。
- 理由：The new evidence indicates a change in the user's position from 'Director' to 'lead director' at the same company, suggesting a possible change in the role.；问题：["Is the promotion to 'lead director' a new role or an advancement within the existing 'Director' role?", "Does the new role of 'lead director' imply a change in responsibilities or authority at Historical Productions Ltd.?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**v5**（状态 `ok`）：
- 关联与条件：object="User"；attribute="position"；conditions="at Historical Productions Ltd."。
- 关系：`possible_change`；旧片段原始="Works at Historical Productions Ltd. as a Director"；定位={"raw": "Works at Historical Productions Ltd. as a Director", "located": "Works at Historical Productions Ltd. as a Director", "method": "exact", "start": 0, "end": 50}。
- 旧引文："Works at Historical Productions Ltd. as a Director"；新引文：{"source_id": "dialogue-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}。
- 理由：New evidence indicates a promotion to 'lead director', suggesting a change in the user's position at Historical Productions Ltd. The old fact states the user works as a 'Director', which may now be outdated.；问题：["Is the promotion to 'lead director' a direct replacement for the previous role of 'Director'?", "Does the new role of 'lead director' imply a change in the user's responsibilities or status at Historical Productions Ltd.?"]。
- 校验：{"passed": true, "checks": ["schema", "relation", "fact_identity", "old_quote", "new_quote", "candidate_fragment"], "semantic_correctness": "not_checked"}；错误：[]。

**初步比较（待确认）：** 三版均标 possible_change，attribute 为 position，理由集中于 Director 至 lead director，v2/v4 明说同一公司；但三版候选旧片段均为包括雇主的整句，未局部分开职称。准确晋升日期未知，标签待确认。

## 尚需组件二和上游处理

- 组件二负责独立核实同一主体、对象、属性和事件关系，提出局部保护、阶段历史化/相对时序及新增候选并去重；记录时间不能直接作为有效期。此次没有运行或修改组件二，也未证明端到端更新效果。其既有实现对错误行停止上游采用，并保留待审；对一般阶段历史化需依赖已有的独立提取及门控。
- 上游拆分器可能把职称与雇主、旧偏好和多种理由合在同一个子事实，增加局部范围选择难度；职业历史输入中 memory 的 previously 与旧来源当时现在时的对齐待定，拆分器自带 contextualized_subfact 和 supports 均为上游候选，不是新增证据；选取哪些对话也会影响可判断范围。此次冻结已有拆分，不将缺失关系归咎于组件一。
