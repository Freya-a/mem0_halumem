# HaluMem-Medium 开发子集：材料审计和评分小测

日期：2026-10-29（Asia/Shanghai）。这是对 3 个已运行用户的开发前缀开展的离线材料审计和单点流程试验，不是完整开发集评分，也不是论文分数复现。原生运行 `williams_native_prefix5_20261028_v3`、原数据、回滚备份和冻结审核均只读；未重新输入会话。该运行以“保留已返回的原生结果及被吞掉的异常”的观测政策完成，4 个会话的 `observed_anomaly.json` 应随任何后续分析保留，不能称为无异常运行。

## 可复用情况与范围

- 28 会话、990 消息的原始输入和各会话前/后全量记忆及 1024 维向量可复用。`snapshot_audit.json` 对 28 会话的 input/before/after 逐一核验检查点 SHA-256，逐项核对源对话、用户、完整条目数及向量维数，错误数 0。数据 SHA-256 为 `486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7`。该审计不声称对全部运行产物作了完整哈希验证。
- 这些前缀有 **56 个 `is_update == "True"` 且 `original_memories` 非空的官方更新候选**和 **75 道挂载在相应会话的官方题目**。`update_candidates.jsonl` 和 `qa_candidates.jsonl` 保留来源位置、原标注和匹配的会话后快照及哈希；只作为候选材料清单，未假称已检索、已评分。官方 `evaluation.py` 实际把有非空 `memories_from_system` 的更新点计入更新记录；其余点落入 integrity 流程，因此 56 不是已经确认的官方更新计分分母。必须显式记录空检索及错误，不能静默改变分母。
- 24 项是人工审核的选取诊断目标，覆盖 16 个会话组，不等于全部官方更新样本，也不是 24 次独立更新。知识保护诊断继续参见原运行 `development_diagnosis_v1/`；其语义保护判定和官方更新/QA分类分别保存与报告，不能互换。
- 源数据每题附在某个 session，官方 Mem0 适配器先 add 该 session，然后在该 session 后立即搜索并回答。小测对应原数组 `sessions[3]`（第 4 会话）完成后的快照，不包含后续会话的库状态；不能使用最终库代替历史状态。题目本身的日期措辞仍应逐题检查；官方代码以题目挂载的会话为截点，并不另行按问题文字回滚。

## 本地官方流程核对

`HaluMem/eval/eval_memzero.py` 使用托管 `MemoryClient`、用户姓名和自定义提取指令；每个会话整段 add 后，针对每个有 original 的更新点以目标 `memory_content` 检索 top 10；针对每题以问题检索 top 20，用 `PROMPT_MEMZERO` 和检索上下文生成 `system_response`。上下文包含检索记忆的 `created_at`。`HaluMem/eval/evaluation.py` 对更新评分传入检索字符串、目标更新、原始记忆，对 QA 评分传入问题、参考答案、evidence 中的 memory_content 和系统回答。`eval_tools.py` 定义完整提示词及分类，`llms.py` 要求模型返回带 `json` 标记的代码块并解析 JSON。

官方更新标签为 Correct/Hallucination/Omission/Other；QA 为 Correct/Hallucination/Omission。`aggregate_eval_results` 分别对全部记录和有效记录计各类比例，输出记录数和有效数，invalid 的全体分母仍保留。官方整体 JSON 输出为 `results/<frame>-<version>/<frame>_eval_stat_result.json`，逐用户中间评分在 `tmp2/`，运行输入为 `<frame>_eval_results.jsonl`。整套聚合还需要 extraction 等记录，多个分母直接相除：空类别/小样本可出现除零；不能把本次两个点直接宣称为该 CLI 的完整聚合输出。本次直接运行两个官方评分函数、提示词和等价的严格 JSON 解析器；没有调用 `evaluation.py` 的整套 process_user/aggregate，也没有声称完整 CLI 通过。当前环境缺少 `python-dotenv`，以局部注入 llms 函数进行调用审计，未安装依赖或改动官方源码。

官方 eval README 中模型配置示例是 `gpt-4o`，代码通过环境变量配置；本地 README 未独立证明论文所用的确切评分模型版本。此次回答和评分使用 `qwen-plus`（temperature=0，max_tokens=16384，timeout=180 秒，不自动重试），因此明确是**评分模型协议调整**，不能宣称复现论文分数。模型别名可能变化，服务未返回固定权重版本。检索使用已有 `text-embedding-v4`、1024 维快照和本地内存 Qdrant cosine；公式、过滤、top-k 对齐本地 Mem0 检索机制，但属于对官方托管 Mem0 适配器的替代，且当前查询 embedding 重算，不是原运行时保存的查询结果。原生库建立时无官方托管 custom instructions，系统输出本身也不是论文实验配置。

重要时间限制：快照 payload 的 `created_at` 是 Mem0 实际执行时间，不是原始对话事件时间。本次沿用官方适配器的 created_at 上下文格式并保存原值，没有冒充事件日期；这会影响时间推理和新旧记忆优先级，应在解释结果时保留，不能直接与论文结果比较。不要仅将快照中的执行时间当成原始事件时间。

## 小范围测试结果

同一用户 `1b846c59-456e-9550-dffd-4d23f1eca81f`，原 `sessions[3]` 结束 `Jan 06, 2026, 08:02:28`，该会话第一个带原始记忆的更新点（`memory_points[2]`）及第一题（`questions[0]`）。完整来源、top-k 命中、提示词、模型原始输出与调用日志都在本目录。

| 官方分类 | 样本 | 小测标签 | 解释 |
|---|---|---|---|
| 更新 | Earl Grey 饮茶体验使喜爱加深 | `Omission` | 评分模型认为检索命中只分别记录原有喜好和到访茶馆，缺少喜爱加深以及与到访关联。1 条有效结果；不是开发集比例。 |
| 问答 | 随后可能探索何种历史饮品 | `Hallucination` | 系统答“没有指定具体历史饮品”；评分模型认为该否定结论与寻求推荐的参考信息冲突。参考答案本身为“Recommendations for historical beverages”，评分理由存在可争议推断，须人工复核；保留原始判词，不静默改标签。1 条有效结果；不是开发集比例。 |

分别生成 `update_judge_prompt.txt`、`qa_answer_prompt.txt`、`qa_judge_prompt.txt`，分别保存 `update_judge_raw.txt`、`qa_answer.txt`、`qa_judge_raw.txt`；`pilot_records.json` 保存官方函数输入及判词，`*_retrieval.json` 保存 ID、文本、原 created_at 和相似度。数据集中原有参考答案、证据仅输入评分器，未用于查询和回答生成。

调用量共 5 次，成功 5 次，错误 0、自动重试 0：2 次 embedding（共 42 tokens），1 次 QA 回答和 2 次评分（聊天输入 3393 tokens、输出 455 tokens）。总计服务报告 3890 tokens；以 `api_calls.json` 为准，未估算费用。提示词与回答可能含数据原文，请按实验数据处理。

## 尚缺材料与后续路径

1. 原运行没有保存官方目标更新检索、逐题检索和系统回答。快照能够支持逐会话后从副本重建检索；需要对其余候选逐点调用 embedding，保存命中及请求元数据，对每道 QA 调用回答模型，再按官方函数评分，明确可能存在空检索或模型错误。不可填造检索、响应或评分。模型/embedding 别名漂移与历史事件时间缺失属于不可从快照精确恢复的限制。
2. 检查每个问题的挂载会话与问题日期、证据的关系；有歧义时单列，不能借后续快照补答案。导出应包括 UUID、原始 session 与 memory/QA 下标、快照哈希、截点、检索 ID/分数、模型版本/参数、提示词、响应、标签和失败。每个用户只搜索自己的对应快照。
3. 在独立评测目录将 56/75 候选按明确的空检索和错误政策处理，使用官方记录字段和分类汇总分别报告 all/valid 的分子及分母；不得将缺失或失败伪装成正常标签。对 official CLI 的 extraction 要求和零分母另行处理并披露，不覆盖官方数据或原有诊断。开发子集包含先前调试用户，并非总体无偏估计。
4. 建议下一份报告放在 `results/medium_dev/official_eval_pilot_20261029/` 的新版本目录或同级新目录，分设官方更新指标、官方 QA 指标、知识保护诊断与人工复核；完整逐点评分材料、失败记录及协议差异一并保存。扩大到开发子集需新建独立输出并核定调用量，不运行整个数据集。

`pilot.py` 是本次实验记录，重新执行会再次调用付费接口且覆盖本目录的同名小测文件；请勿在本目录直接重跑。每次新运行应使用新目录并改为可恢复、防覆盖的逐项记录。
