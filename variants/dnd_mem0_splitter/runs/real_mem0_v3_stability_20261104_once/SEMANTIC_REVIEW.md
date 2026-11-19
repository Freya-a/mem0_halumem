# 固定 v3：7 条未参与调词的真实旧记忆测试

日期：2026-11-04（Asia/Shanghai）。**语义判断均为“初步判断，待人工确认”**，不是人工已确认金标准，也不是自动语义评分。

**程序检查：7/7 通过，15/15 条引文逐字匹配。** 7 条不同旧记忆分别真实调用 qwen-plus 1 次，合计 7 次，重试 0 次；返回 7 条事实，每例 1 条。memory 引文每条都有，未自动补写或改标。

**语义与字段边界初审：6 个案例观察到至少一项问题，5 个案例有具体未决项；全部 7 个案例/7 条事实仍待人工最终确认。** 这些集合相交，不能相加为错误率。不确定性不自动计错，6 个案例有问题也不等于其核心命题都错误。

主要重复问题是 5 个 raw 从上下文补入 The user；此主体通常有依据，问题在于 v3 要求 raw 只依据旧记忆。另有 2 个案例 supports 范围越界、2 个案例断言与待决状态不一致，以及 1 个案例有源但非必要的正文扩写。否定、or、possibly、recently 在本轮正文中均保留；未观察到关键旧命题遗漏或时间、否定、情态被改写。

## 产物入口

- [程序汇总](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/program_summary.json)
- [统计汇总与统计口径](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/summary.json)
- [逐案例 CSV](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/case_review.csv)
- [逐事实 CSV](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/fact_review.csv)
- [逐引文 supports CSV](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/supports_review.csv)
- [完整语义明细 JSON](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)
- [案例选择与输入来源](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json)
- [仅建议、未应用的提示词调整](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/PROMPT_SUGGESTIONS.md)

## 固定项与调用控制

冻结提示词：[frozen_prompt.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/frozen_prompt.txt)，版本 v3_memory_example_20261104，SHA-256 `28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e`。当前 DESIGN.md、原解析器/校验器/后端及已有结果均未修改；本次开始时跟踪的 198 个旧文件 SHA-256 全部不变。

所有案例均来自既有真实 Mem0 原生开发运行的更新前落盘快照，核对 API 与底层 payload、实际 ADD、生成前后及前一会话 after 的 ID/文本；42 个来源文件与历史 checkpoint 哈希匹配。这里不代表本次连接 Mem0 核验在线状态。来源先后依据现有脚本在 memory.add 前保存 before，未执行该开发脚本。

7 个 ID 均不在此前 splitter 真实模型运行输入中；此前金毛、跳伞、多人物及怀疑/现在状态等输入排除。模型只收到固定 v3 和本例旧记忆、原始旧上下文；本次选择理由、人工复核、预期答案和目标新证据不在输入里。v3 原有的自拟格式示例保持原样，没有新增评测答案。

模型请求名与返回名均 qwen-plus；显式生成参数 {}，超时 180 秒，response_format=json_object，SDK max_retries=0，HTTP 重定向关闭。温度、token 上限、seed 未显式固定；服务端默认值、具体模型修订、路由及后台采样参数无法确认。没有模型探测、切换、纠错或重试。参数与计数见 [preflight.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/preflight.json)、[batch_execution.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/batch_execution.json)、[execution_journal.jsonl](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/execution_journal.jsonl)。

## 选择与覆盖

| 案例 | 真实 memory_id | 主要覆盖 | 快照位置 |
| --- | --- | --- | --- |
| case_01_multi_person | 130bf22c-9e71-4ad2-bf51-43bac36ab2c8 | 多个人物、身份关系、混合说话人 | [session_011/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_011/before.json) `/api_snapshot/results/13` |
| case_02_subject_and_roster | a1332815-d6ba-4bdc-9ffa-657f7315d0ed | 缺失主语、姓名与别称、上下文额外人物 | [session_005/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json) `/api_snapshot/results/51` |
| case_03_assistant_yoga | 992ae849-3f40-4ffe-a2ec-16e20959ca86 | 助手来源、说话人归属、析取与状态 | [session_008/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json) `/api_snapshot/results/58` |
| case_04_negative_relative | 30a88f0c-d4b8-4089-95b2-82938e45558c | 否定偏好、原因与作用范围、亲属代词、上下文额外偏好 | [session_004/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/before.json) `/api_snapshot/results/17` |
| case_05_relative_time | 2570a550-4b52-43fc-b5c4-079261785a1a | 相对时间、职位状态变化、上下文额外感受 | [session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json) `/api_snapshot/results/11` |
| case_06_plan_possibility | 0618a2ca-e7d0-483f-b80a-335124dbb075 | 计划、可能性、助手问句、缺失主语 | [session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json) `/api_snapshot/results/1` |
| case_07_no_children | 40c29476-81a2-477d-9e75-a2a3a92d46c7 | 明确否定状态、缺失主语、上下文家庭细节 | [session_005/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json) `/api_snapshot/results/20` |

未在本次检查的已有目标 before 快照清单中找到可靠的显式 if/unless 条件记忆，因此没有编造条件案例。case04 检查了 while 场景范围，case03 检查析取，case06 检查计划/可能性；它们不能替代完整条件句覆盖。样本为目的性抽样，不代表开发集总体分布。

## 每例与每条事实的结果

每例本轮只返回一条，下表列其实际 raw 和上下文版本。完整输入、原始响应、每项引文和 supports 的判断在对应独立报告中；所有语义结论均待人工确认。

| 案例 | raw_subfact | contextualized_subfact | 程序引文 | 初审观察 | 具体未决 |
| --- | --- | --- | --- | --- | --- |
| [case_01_multi_person](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_01_multi_person/SEMANTIC_REVIEW.md) | The user is grateful towards colleagues like Steven and friends like Mary. | The user is grateful towards colleagues like Steven and friends like Mary. | 1/1 | 断言与待确认状态不一致、raw 混入上下文主体 | 有 |
| [case_02_subject_and_roster](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_02_subject_and_roster/SEMANTIC_REVIEW.md) | The user has a friend named ThomasSusan, who is referred to as 'Susan', and who provides support and encouragement. | The user has a friend named ThomasSusan (referred to as 'Susan'), and Susan's support and encouragement inspire the user to maintain focus on promoting well-being in both personal and professional life. | 2/2 | 断言与待确认状态不一致、raw 混入上下文主体、有来源但非必要的正文扩写、supports 支持范围越界 | 有 |
| [case_03_assistant_yoga](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_03_assistant_yoga/SEMANTIC_REVIEW.md) | The user practices yoga or is open to practicing yoga for supporting personal health and transition. | The user practices yoga or is open to practicing yoga to support personal health and career transition. | 3/3 | raw 混入上下文主体 | 有 |
| [case_04_negative_relative](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_04_negative_relative/SEMANTIC_REVIEW.md) | They do not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative. | The user does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative. | 2/2 | 未观察到明确分类问题 | 有 |
| [case_05_relative_time](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_05_relative_time/SEMANTIC_REVIEW.md) | The user was recently promoted to lead director at Historical Productions Ltd. | The user was recently promoted to lead director at Historical Productions Ltd. | 2/2 | raw 混入上下文主体 | 无额外具体未决项 |
| [case_06_plan_possibility](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_06_plan_possibility/SEMANTIC_REVIEW.md) | There are plans to initiate groundbreaking historical dramas and possibly science fiction dramas. | The user has plans to initiate groundbreaking historical dramas and possibly science fiction dramas. | 3/3 | supports 支持范围越界 | 有 |
| [case_07_no_children](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_07_no_children/SEMANTIC_REVIEW.md) | The user has no children. | The user has no children. | 2/2 | raw 混入上下文主体 | 无额外具体未决项 |

### case_01_multi_person

旧记忆原文：

> Grateful towards colleagues like Steven and friends like Mary

**初步判断，待人工确认：** 初步判断，待人工确认：格式检查 passed；1 条事实覆盖感谢态度、Steven/colleagues、Mary/friends 及 like 的举例表述，未见关键命题遗漏。观察到 raw 用上下文补出 The user 的来源边界问题，以及肯定用户主体与将主体列为待确认之间的表述冲突；不据此认定用户主体虚构。原始说话人和具体人物身份仍有局部未决项。

### case_02_subject_and_roster

旧记忆原文：

> Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

**初步判断，待人工确认：** 初步判断，待人工确认：格式检查 passed；1 条事实保留朋友关系、ThomasSusan/Susan 名称关联及支持鼓励。观察到 raw 主体来自上下文、contextualized 增加有源但非必要的 well-being 效果，以及 context supports 将名称 token 升格为已验证 full name 的越界与待决状态冲突。未把其他同事名单带入正文。

### case_03_assistant_yoga

旧记忆原文：

> Practices or is open to yoga for supporting personal health and transition

**初步判断，待人工确认：** 初步判断，待人工确认：现有 report.json 为格式检查 passed；审查 1 条已返回事实和全部 3 条 supports。旧记忆的 practices OR is open to、瑜伽对象及 personal health/transition 用途均保留，未被助手 could 建议覆盖。观察到 1 项 raw 来源边界问题：raw 新补 The user，违反本批次 frozen_prompt.txt 第2条；这与主体是否可由上下文合理关联是两件事，不判为凭空人物，也不判用户直接自述。原始发言归属、析取哪一支成立及具体实践状态仍未决。

### case_04_negative_relative

旧记忆原文：

> Does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative

**初步判断，待人工确认：** 初步判断，待人工确认：现有 report.json 为格式检查 passed；审查 1 条已返回事实和全部 2 条 supports。未发现协议分类中的明确正文忠实度或支持范围错误；否定偏好、because 原因和 while 范围完整保留。亲属具体身份及支持持续范围仍未决，不能把这些不确定计为错误。

### case_05_relative_time

旧记忆原文：

> Recently promoted to lead director at Historical Productions Ltd

**初步判断，待人工确认：** 格式检查通过，1条返回事实。职位晋升、lead director、机构和 recently 均保留；未把发言日期等同晋升日期。观察到 raw 补入 memory 未表达的用户主语，属于来源边界问题；该主体在 contextualized 中有 ctx-1 第一人称依据，不判为主体完全无依据。

### case_06_plan_possibility

旧记忆原文：

> Plans to initiate groundbreaking historical dramas and possibly science fiction dramas

**初步判断，待人工确认：** 格式检查通过，1条返回事实。raw 保留未定主体，contextualized 的用户语义主体可由 assistant 的 you plan 指向；plans 与仅作用于 science fiction dramas 的 possibly 均保留。观察到 ctx-2 supports 将泛化的创作控制/真实性回应当作具体剧类计划的本人意图依据；原计划是否有用户明确原话仍未决。

### case_07_no_children

旧记忆原文：

> No children

**初步判断，待人工确认：** 格式检查通过，1条返回事实。No children 的否定状态保留，未扩写为不想要孩子或从未有过孩子。观察到 raw 从上下文补入用户主语；用户家庭自我介绍足以支持 contextualized，但不能突破 raw 仅恢复 memory 内部成分的边界。

## 数量与错误类型

| 指标 | 数量 |
| --- | --- |
| 程序格式/ID/引文整体通过 | 7/7 案例 |
| 程序失败 | 0/7 案例 |
| 返回事实 / 有效结果事实 | 7 / 7 |
| memory / context 引文 | 7 / 8 |
| 引文逐字匹配 | 15/15 |
| 语义最终确认待人工 | 7 案例 / 7 事实 |
| 观察到问题（含字段来源边界） | 6 案例 / 6 事实 |
| 有具体未决项 | 5 案例 / 5 事实 |
| 未观察到明确分类问题 | 1 案例，仍有亲属与范围未决 |
| 模型自身 pending 数组项 | 12 项，分布于 5 案例 |

具体未决项计数来自独立复核中的主体/原始说话人/指代/范围等明确未知。所有语义判断本来都要人工最终确认；没有单列未决项不等于已证明正确。未给出精确晋升日期没有被自动判错：case05 保留 recently，未将记录时间当事件日期。

| 初审问题类型 | 涉及案例 | 涉及事实 | 案例编号 |
| --- | --- | --- | --- |
| 断言与待确认状态不一致 | 2 | 2 | case_01_multi_person, case_02_subject_and_roster |
| raw 混入上下文主体 | 5 | 5 | case_01_multi_person, case_02_subject_and_roster, case_03_assistant_yoga, case_05_relative_time, case_07_no_children |
| 有来源但非必要的正文扩写 | 1 | 1 | case_02_subject_and_roster |
| supports 支持范围越界 | 2 | 2 | case_02_subject_and_roster, case_06_plan_possibility |

各类型相互重叠，共 10 项观察记录；它们不是独立错误率。未观察到 NEGATION_CHANGE、MODAL_OR_DISJUNCTION_CHANGE、TIME_SCOPE_CHANGE、KEY_FACT_OMISSION 或凭空人物事实，但不能由小样本中的零观察推断能力已经稳定。

supports 的 15 项初审为：直接支持 7、部分支持 6、越界 2。部分支持通常涉及从关联上下文补主体或助手仅提供建议，不自动算错误。具体越界是 full name 验证和将一般创作回应升级为具体计划意图证据。

## 证据归属与未决项

- case01：语义主体可由用户表达感谢的意向与助手 Your gratitude 关联；具名角色的可见原话来自 assistant，不能直接称用户说过整个具名命题。pending 将主体和原始说话人混写，需人工厘清。
- case02：用户第一人称明确支持朋友关系和 Susan 称呼；ThomasSusan 的结构未知，不能说已经验证 full name。well-being 效果有源，但不是补主体所必需。
- case03：assistant 的 could 建议既不证明 user 实践，也不证明 user 表达开放。正文正确保留旧记忆的 OR，未知不被自动判成旧事实错误。
- case04：亲属身份、支持持续范围未知；没有据此改成具体亲属或永久戒酒。
- case05：同一晋升事件有 user 第一人称原话；recently 保留，具体事件日期未提供。
- case06：assistant 问句可表明它讨论的对象是 user，但 user 对创作控制/真实性的回应不足以证明具体历史剧/科幻剧计划就是其本人明确意图。
- case07：家庭自我介绍支持 user 无子女的通常解释；没有扩成整个家族无子女、不想要孩子或终身从未有过孩子。

关键区别：raw 补出用户主语的来源边界问题，不等同“人物身份是编造的”。memory 引文证明旧记忆记载，不独立验证现实真实性或用户原话；原始说话人和命题主体也不是同一个判断。

## 后续建议与本次边界

建议保留本轮数据，优先审阅重复的 raw 主体混入、supports 范围越界及断言/待决冲突，再决定是否调词。具体、尚未应用的建议见 [PROMPT_SUGGESTIONS.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/PROMPT_SUGGESTIONS.md)。当前没有修改或替换 v3，也没有为了消除这些问题追加请求。

7 例全部仅产生 1 条事实；其中关系/别称/并列目标仍常合并，不能据格式成功证明细粒度拆分已充分验证。后续应补更长多命题旧记忆与可靠显式条件句，并保留独立案例避免只围绕本轮调词。

独立案例组按 dispatching-parallel-agents 工作流并行复核，仅读取指定案例，分别写入新 reviews/group_01.json、group_02.json、group_03.json；没有额外模型调用。主代理逐项核对原文、统一统计定义并保留这些复核记录。

本次不修改 Mem0、不写知识库、不运行完整开发子集，不覆盖原始输入、历史运行或已有报告；没有输出 API 密钥或完整环境变量。
