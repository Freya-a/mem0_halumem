# 五个开发案例：v2 与 ERASE 式第一轮分类对照

## 任务与边界

本报告只比较旧子事实判断，不替换原组件、不运行拆分器或组件二、不写入 Mem0。A 是现有组件一 v2；B 是**ERASE 式分类对照**，不是作者完整 ERASE 基线。五例是有针对性的开发案例；人工审核为 LLM 辅助、用户确认，确认的是事实和更新边界，**不是六标签或三标签的独立盲标**。以下各条标签判断均是分析者提出，需人工复核；不得用这五例推断总体准确率或普遍优劣。

## 两种任务的定义与差异

v2 实际系统提示词和校验见本目录 `A_v2/system_prompt.txt`、[relation_judge.py](../../part1_relation_judge/relation_judge.py) 与 [relation_judge_v2.py](../../part1_relation_judge/relation_judge_v2.py)。单条旧子事实、整条旧记忆、来源上下文、新证据及可选时间输入，输出 JSON 候选、理由、待确认问题及引用；从上到下按提示词优先级：

| v2 标签 | 含义 |
|---|---|
| uncertain | 对象、属性、条件、时间或证据不足，不能可靠判断其他类，需具体提问 |
| historical_correction | 新证据明确指出对同一历史事实的旧描述有误；新状态不同本身不算 |
| possible_change | 同一对象属性可能随时间或条件变化，或文本不能定论的冲突；不认定旧事实已失效 |
| support | 支持或延续同一事实，且不含实质新增 |
| supplement | 与旧事实相容、增加相关不同信息，但本身不支持旧事实真实性或表明变化 |
| no_clear_impact | 可判断无明显相关影响，而非因歧义无法判断 |

[ERASE 论文附录 A.1](https://aclanthology.org/2025.findings-naacl.168.pdf)第一轮以新输入、时间、逐个检索事实为输入，预设旧事实此前为真，比较它在新输入下现时是否仍可能为真；**reinforce**：新输入使其更可能为真；**make false**：新输入使其更不可能为真；**no change**：不影响，例如不相关；无矛盾则假设仍真。reinforce/no change 分入仍真集，make false 分入需后续处理集。论文作者用的是可能性及默认保真策略，“make false”不等于证明旧陈述过去就是错的。

这些不是一一对应的标签：v2 的 possible_change 不承诺旧事实不再成立，historical_correction 指历史描述原本有误，与 ERASE 假定此前为真不同；v2 设有 uncertain 而 ERASE 三类无专门不确定类，no change 涵盖不相干及默认不变；新证据既支持又新增时，v2 的 support/supplement 定义存在单标签表达张力。ERASE 首轮不专门提取新增内容，不因没有单独输出新增而判错。对复合旧事实，ERASE 的单事实分类不能自行保证每个属性都应同样更新。

## 来源、执行流程和适配

- 作者仓库 [belindal/ERASE](https://github.com/belindal/ERASE)，本机有 Git 副本 `system/mem0_halumem_diagnosis/external/ERASE`，HEAD `b93f898780b3cf40fedd4e9a00c51af9a27688bc`。顶层 `external/ERASE/models/kb_model.py` 与 Git 副本同文件 SHA-256 `5f13b6638b08080dd1f972998307bae5425348891f70b3448c742b5b20162c1e`；[来源记录](../../../../external/ERASE_SOURCE.md)。论文：Li 等，*Language Modeling with Editable External Knowledge*，NAACL Findings 2025。
- 作者 [kb_model.py](../../../../external/ERASE/models/kb_model.py) 的 `get_operations`（800 行附近）先 `retrieve_facts_to_edit`，再 `edit_retrieved_facts`，随后 `extract_new_facts`；启用 overwrite 且有检索事实时，第一轮对每个去重事实各调用一次模型（原实现 `temperature=0.0, max_tokens=100`），收集 still_true 与 false_unknown，第二轮对后者根据输入和 still_true 重写；之后组合增加、强化和降低等操作。作者实际解析先截首行，再验证类别；格式无效时追加提示重试，超过阈值回退 no change，最后按字符串识别。仓库还存在作者未发布数据与依赖，未运行完整作者系统。
- B 保存论文的“以前为真—总结变化—解释—三类别回答—无矛盾保真”结构及类别核心含义。为与 A 完全一致，输入改为同一个序列化 JSON：`fact.raw_subfact` 指定待判事实，`memory_text`、`source_context` 是旧上下文、`new_evidence` 是新输入；把原文合并在系统消息，负载放用户消息；对照以新证据所示时点判断，记录时间仅作记录时间，不伪造事件日期（`time_info` 均为空）。这改变了原论文仅输入文档/时间/事实的上下文和消息结构，可能影响结果；包含上游自动生成的 `supports`、`pending_confirmations` 等字段，与 A 相同，不是独立人工真值。完整提示及每次消息见分组目录。
- 依用户要求，两组各自每事实一次调用，无重试或失败回退；B 按唯一 `Answer:` 行解析，保留原响应和解析错误，而非复刻作者首行截取/重试；两组均以 768 新 token 为上限而非作者的 100。B 未做检索、重写、新事实抽取或 ERASE 更新操作。

## 执行设置

请求原样复制自 `dev_scope_review_20261109_v1/*_result.json` 的 `request`，每例恰有一个子事实；A/B 的实际用户消息会逐字核验。完整快照在 [inputs.json](inputs.json)，模型消息、原始输出、解析、耗时及错误在各组 JSON，版本与散列在 [manifest.json](manifest.json)。此前 v2 五例运行见 [历史对照报告](../part1_comparison_20261110_v1/REPORT.md)，本次为新的独立实际运行。

两组在同一进程、同一模型实例运行现有 `LocalQwen.load`：本地 Qwen3-8B，AutoTokenizer/AutoModelForCausalLM，local_files_only，BF16，cuda:0，eval；`enable_thinking=False`、`do_sample=False`、`max_new_tokens=768`，pad 为 tokenizer EOS，其他按模型 generation_config 与 transformers 默认设置；生成时 temperature/top_p/top_k 提示可能忽略。顺序是每例 A 后 B，非随机；共享 GPU，耗时不可当作严格性能基准。每次记录结束 token，按模型 generation_config 的多个 EOS 判定；达到上限且非 EOS 为长度截断迹象。

|案例|组|调用|状态|生成 token|耗时（秒）|EOS|达到上限且非 EOS|
|---|---|---:|---|---:|---:|---|---|
|job_transition|A_v2|1|ok|242|10.594|True|False|
|job_transition|B_erase_style|1|ok|62|2.638|True|False|
|persian_cats|A_v2|1|ok|285|11.446|True|False|
|persian_cats|B_erase_style|1|ok|119|4.896|True|False|
|skydiving|A_v2|1|ok|356|14.291|True|False|
|skydiving|B_erase_style|1|ok|80|3.358|True|False|
|career_history|A_v2|1|ok|292|11.713|True|False|
|career_history|B_erase_style|1|ok|52|2.224|True|False|
|promotion|A_v2|1|ok|268|10.599|True|False|
|promotion|B_erase_style|1|ok|46|1.939|True|False|

## 逐案输入、输出与分析

以下新证据为两组实际收到的全部新消息；旧记忆、旧来源、完整 payload 和来源字段可从各组 JSON 核验。新消息的记录时间不是事件发生日期。

### 转岗（job_transition）

- 旧记忆全文：`Looking for a new job with better work-life balance`。
- 旧子事实：`Looking for a new job with better work-life balance`。
- 旧来源上下文：
  - old-1（Feb 05, 2026, 17:13:15）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.
  - old-2（Feb 05, 2026, 17:37:37）：I'm really looking forward to finding a position that supports both my career goals and my personal health. It's been a challenging journey, but I'm hopeful about the future.
- 新证据：
  - dialogue-0（Mar 01, 2026, 07:04:00）：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.
  - dialogue-2（Mar 01, 2026, 07:09:03）：Yes, the new role has definitely improved my mental health. The stress and pressure from my previous job were really taking a toll.
- 人工确认和边界：已确认截至新消息时这次转岗已完成、工作生活平衡更健康；保留旧求职阶段的历史，不推断以后再也不找工作。新雇主、职称、转岗准确日期及是否离开旧雇主未知。
- A 标签：`support`；理由：新证据表明用户已经找到了新的工作，并且工作与生活平衡得到了改善，这支持了旧事实中用户正在寻找更好工作与生活平衡的陈述。；旧片段：`Looking for a new job with better work-life balance`；引用：{"source_id": "dialogue-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}；问题：[]。
- B 标签：`reinforce`；完整理由及输出：'The new evidence indicates that the user has successfully transitioned to a new role that provides a healthier work-life balance, confirming that their goal of finding such a job has been achieved. This supports the previously stated fact that the user is looking for a new job with better work-life balance.\n\nAnswer: Reinforce'。
- 分析者判断（非人工盲标）：A 与 B 都识别已转新岗位及平衡改善，均把此次目标达成当作旧句“正在寻找”得到支持，未区分旧求职阶段和新进展，是对当前状态的错误判断；两者没有声称日后绝不会继续求职。按 v2 定义，分析者暂倾向 possible_change；按 ERASE 原文 make false 可能更贴近此次求职阶段的结束，但旧句没有限定“这一次”且未来求职未知，不能推断所有求职停止，三类标签仍需人工确认。

### 波斯猫（persian_cats）

- 旧记忆全文：`Likes Persian cats because of their regal and calm nature, elegance, and historical charm`。
- 旧子事实：`Likes Persian cats because of their regal and calm nature, elegance, and historical charm`。
- 旧来源上下文：
  - old-1（Sep 06, 2025, 22:24:16）：I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home. I don't like parrots, because The constant noise and chatter of parrots can be quite distracting, especially when I'm focused on creating a quiet, historical atmosphere. I like greyhounds, because greyhounds have a noble history and a gentle demeanor that I find soothing and fitting for my lifestyle. I like tortoises, because their slow, deliberate movements remind me of the passage of time and history, which I find fascinating. I like British shorthair cats, because their calm and collected nature aligns with my preference for peace and quiet, and they have a historical charm.
- 新证据：
  - dialogue-0（Apr 10, 2026, 11:06:07）：I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty.
  - dialogue-2（Apr 10, 2026, 11:15:58）：The history of Persian cats aligns perfectly with my interest in historical authenticity. However, I do reflect on the practical challenges of maintaining their regal appearance.
- 人工确认和边界：已确认用户观看纪录片后对波斯猫历史传承与王室关联的欣赏加深；保留原有喜好及其他理由。准确观看时间、影片和地点未知；品种史仅作为用户欣赏对象，不当作外部验证事实。
- A 标签：`support`；理由：新证据表明用户对波斯猫的历史渊源和与皇室的联系更加钦佩，这与旧事实中提到的用户喜欢波斯猫因其高贵、冷静的天性、优雅和历史魅力是一致的，因此新证据支持旧事实。；旧片段：`Likes Persian cats because of their regal and calm nature, elegance, and historical charm`；引用：{"source_id": "dialogue-0", "quote": "I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty."}；问题：[]。
- B 标签：`reinforce`；完整理由及输出："The new evidence indicates that the user recently attended a film festival and watched a documentary about Persian cats, which deepened their admiration for their historical lineage and association with royalty. Additionally, the user reflects on the practical challenges of maintaining the regal appearance of Persian cats, but this does not contradict their appreciation for their historical and regal qualities.\n\nThe input reinforces the user's admiration for Persian cats, particularly their historical and regal aspects, which aligns with the previously stated fact. There is no evidence to suggest that the user no longer likes Persian cats for these reasons.\n\nAnswer: Reinforce"。
- 分析者判断（非人工盲标）：A 将更深欣赏视作支持，识别了旧喜好和新经历的联系，但 support 按自身定义排除实质新增，而纪录片和欣赏加深同时属于新增：单标签表达不足，不能把旧喜好与新增看成互斥。B 的 reinforce 与新证据对相关旧喜好的支持一致；它实际也提到纪录片和欣赏加深，即使未单独提取新增也不构成第一轮错误。旧事实包含平静性情等多项原因，新证据并未逐一证明所有属性。

### 模拟跳伞（skydiving）

- 旧记忆全文：`Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`。
- 旧子事实：`Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`。
- 旧来源上下文：
  - old-context-1（Sep 06, 2025, 22:52:30）：I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.
- 新证据：
  - dialogue-0（Apr 10, 2026, 10:40:32）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
  - dialogue-2（Apr 10, 2026, 10:48:20）：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
  - dialogue-8（Apr 10, 2026, 10:57:54）：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.
- 人工确认和边界：已确认团建中尝试并享受模拟跳伞，更愿尝试新事物，仍重视安全；保留原安全顾虑的历史与原因。真实跳伞当前态度和具体设施、安全程度未知。
- A 标签：`possible_change`；理由：New evidence shows the user tried simulated skydiving and found it thrilling, indicating a possible change in attitude toward extreme sports. However, the user still prioritizes safety, which may suggest the core commitment to safety and well-being remains unchanged.；旧片段：`Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`；引用：{"source_id": "dialogue-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}；问题：["Does the user's experience with simulated skydiving indicate a change in their attitude toward extreme sports?", "Is the user's commitment to safety and well-being still intact despite the new experience?"]。
- B 标签：`make false`；完整理由及输出：'The new evidence shows that the user recently tried simulated skydiving at a team-building event and found it thrilling. They also mentioned enjoying the adrenaline rush and being more open to trying new things. However, they still prioritize safety. This suggests a shift in attitude toward extreme sports, as they are now open to experiencing them in a controlled environment, while still valuing safety.\n\nAnswer: Make False'。
- 分析者判断（非人工盲标）：A 从模拟体验推断对广义极限运动态度可能改变，标 possible_change，整句作为候选范围；它未断言真实跳伞态度必然改变，但这种从模拟直接推广的依据不足，并把已明确的安全优先再次提出疑问。B 将模拟体验推广为极限运动中的态度变化并标 make false，更强地判定旧整体事实不再可靠；所谓 controlled environment 并非原文证明的设施或安全程度。按 ERASE 默认保真原则，分析者暂倾向 no change，但旧描述宽泛程度及模拟活动是否纳入需人工确认，不能因此声称用户对真实跳伞的态度已知。

### 职业历史／咨询公司（career_history）

- 旧记忆全文：`Previously worked as a senior developer in Blockchain Tech`。
- 旧子事实：`Previously worked as a senior developer in Blockchain Tech`。
- 旧来源上下文：
  - old-context-1（Sep 05, 2025, 09:10:09）：I work at Blockchain Tech as a senior developer.
- 新证据：
  - dialogue-0（Jan 05, 2026, 07:43:42）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- 人工确认和边界：已确认咨询公司获得一些首批客户，用户感到宽慰并视作里程碑；记录获客与感受、保留此前计划历史，不推断合同、付款或数量。旧记录过去时与旧上下文当时现在时的时间关系未决；公司身份和雇佣关系不可从 my firm 确定。
- A 标签：`uncertain`；理由：The new evidence mentions the user's current employment at a consulting firm, but it does not provide any direct information about their previous role as a senior developer in Blockchain Tech. The temporal relationship between the past employment and the current consulting role is unclear.；旧片段：`previously worked as a senior developer in Blockchain Tech`；引用：{"source_id": "dialogue-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}；问题：["Is the user's current employment at a consulting firm related to their previous role as a senior developer in Blockchain Tech?", "Does the new evidence provide any information about the user's employment history prior to their current role at the consulting firm?"]。
- B 标签：`no change`；完整理由及输出："The new evidence indicates that the user is currently feeling relieved due to securing initial clients with their consulting firm. This information does not provide any direct or indirect confirmation or contradiction regarding the user's previous role as a senior developer in Blockchain Tech.\n\nAnswer: No Change"。
- 分析者判断（非人工盲标）：A 指出新证据未直接说明旧工作，但将 my consulting firm 解释为当前受雇并将该前提带入问题，缺少依据；uncertain 对新证据是否改变过去经历可能过度保守，分析者倾向 no_clear_impact 或 supplement，取决于何种关联满足定义，需人工确认。B 判 no change 并解释旧经历未受直接影响，基本符合其默认保真任务；其说 securing clients with their consulting firm 表示与公司有关，未明确断言雇佣身份，不能等同 A 的雇佣推断。

### 晋升（promotion）

- 旧记忆全文：`Works at Historical Productions Ltd. as a Director`。
- 旧子事实：`Works at Historical Productions Ltd. as a Director`。
- 旧来源上下文：
  - old-context-1（Sep 05, 2025, 14:42:35）：I work at Historical Productions Ltd. as a Director.
- 新证据：
  - dialogue-0（Feb 01, 2026, 18:47:19）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!
- 人工确认和边界：已确认当前具体职称 Lead Director，雇主仍是 Historical Productions Ltd.；旧 Director 应保留为带时间历史，保护雇主。准确晋升日期未知。
- A 标签：`possible_change`；理由：The new evidence indicates a change in the user's position from 'Director' to 'lead director' at the same company, suggesting a possible change in the role.；旧片段：`Works at Historical Productions Ltd. as a Director`；引用：{"source_id": "dialogue-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}；问题：["Is the promotion to 'lead director' a new role or an advancement within the 'Director' role?", "Does the term 'lead director' imply a different level of responsibility or authority compared to 'Director'?"]。
- B 标签：`make false`；完整理由及输出：'The new evidence indicates that the user was promoted to "lead director" at Historical Productions Ltd., which is a higher position than the previously stated "Director." This suggests a change in the user\'s role.\n\nAnswer: Make False'。
- 分析者判断（非人工盲标）：A 的 possible_change 和理由区分职称变化与同一雇主，但候选影响片段为整句而非单独职称，存在范围过宽风险；额外追问具体职责不影响已确认晋升。B 将整句标 make false，理由集中于职称变化，未说明雇主失效；若 Director 表示原具体职称，这一整体分类可理解，但不应据此删除雇主，且 lead director 与泛称 director 是否蕴含关系会影响句子的逻辑真值，需人工确认。第一轮本身不是局部改写。

## 可能原因与下一步

- 两组都在转岗例把目标达成混同于旧状态延续；下一步应在更多有真实阶段变化且存在继续活动可能性的案例上检查“状态、事件与目标”的区别，避免把完成一次活动推成永不继续。v2 的提示明确说新状态不等于历史纠错，但模型仍可能混淆；B 默认保真与三分类也可能把间接支持优先于阶段变化。这些是待验证假设，不是已证明的因果机制。
- 模拟跳伞表明即使 A 提示中明确区分模拟与真实，模型仍可能将特定活动外推；B 的三类单事实输出更容易掩盖复合旧句的局部变化。建议对不同活动对象、条件、时态和复合旧句做人工标注的扩展集，单独评估理由和影响范围。
- 咨询公司暴露 A 的身份推断，建议加入公司关系未知、所有者／雇员／顾问都可能的反例；波斯猫暴露 v2 对支持与新增同时出现的单标签表达张力。应先讨论接口与下游如何表达混合关系，而非依据五例增加针对性提示。
- 晋升例应检查上游事实粒度、对职称和雇主分别判定，以及 Director 作为具体头衔或上位类别的歧义。独立验证不同顺序、模型、样本与人工盲标之前，不能归因于提示差异或断言任一方法普遍更好。本次未运行或验证组件二的实际处理。

## 格式核验与历史纠错检查

本轮 10 次调用均返回、以模型的 EOS 结束、没有达到 768 token 上限；A 的五条均通过现有 schema、引用和候选片段校验，B 的五条均解析出单个合法标签。**这仅证明格式及字面引用检查通过，不证明语义正确。** 完整日志为 [run.log](run.log)，每条推理的计时、token 及 EOS 见各 JSON，模型和环境运行信息见 [completion.json](completion.json)。已核对每例两组的实际用户消息逐字一致，且与冻结源请求对应。

本轮 A 五例没有输出 `historical_correction`；B 任务预设旧事实此前为真，也没有声称旧记录此前描述错误。特别地，转岗不应因状态变化就改称旧记录当时有误。A 转岗理由说“找到了新的工作”，但原文只明确转到新岗位，不足以确定换了雇主；需要保留这一身份和事件边界。
