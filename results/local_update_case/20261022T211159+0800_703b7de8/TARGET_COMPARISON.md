# 单个目标对照与证据

目标核心事实已通过 **ADD** 持久化，没有对标注所指旧命题执行 UPDATE。标注旧命题没有精确匹配到目标前的 62 条实际记忆；此前是否有严格语义等价记忆，标为待人工核验。本轮不能据此判断更新保护是否有效。

用户 UUID：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。数据源为 `HaluMem/data/HaluMem-Medium.jsonl` 第 1 行；下面的 JSON pointer 均相对该行用户对象。会话按开始时间排序，序号从 1 开始，原始索引从 0 开始。

| 目标字段 | 原文及位置 |
| --- | --- |
| 目标会话 | 第 4 会话，原始索引 3，Dec 15, 2025, 06:11:23 至 08:41:23；完整 60 条消息均输入一次 |
| 标注位置 | `/sessions/3/memory_points/0`，`is_update: "True"`，`original_memories` 非空；见 [target.json](target.json) |
| 标注旧命题 | `Martin Mark is considering a career change due to health impacts from his current role.`；位置 `/sessions/3/memory_points/0/original_memories/0` |
| 标注新命题 | `Martin Mark is considering a career change due to the impact of his current role on his mental health.`；位置 `/sessions/3/memory_points/0/memory_content` |
| 原始新增证据 | `I've been reflecting a lot on my career lately, especially how my current role as a director at Huaxin Consulting is impacting my mental health. It's becoming increasingly clear that I need to make a change.`；用户消息，Dec 15, 2025, 06:11:23；`/sessions/3/dialogue/0/content`；[input.json](session_04/input.json) 第 13 行 |
| 此前相关原文 | 第 2 会话用户消息 `/sessions/1/dialogue/4/content`，Sep 05, 2025, 23:15:17，包含 `my mental health occasionally feels strained due to the demanding nature of my role`；该句谈工作压力，没有明确转行意向；见 [raw_history_prefix.json](raw_history_prefix.json) |

所有检查以本轮冻结日志和实际数据库为依据。`observations.jsonl` 中 sequence 与物理行号一致。`facts[2]`、`plan[9]` 等数组下标从 0 开始。不存在的旧记忆没有可提供的实际 ID，以“不存在精确匹配”明确标记。

| 检查项 | 判断 | 原文位置、记忆 ID、日志位置 |
| --- | --- | --- |
| 新证据是否进入输入 | **是**。完整消息进入一次 `Memory.add(..., infer=True)`，也进入原生提取提示词和 SDK 实际请求 | `/sessions/3/dialogue/0/content`；输入阶段尚无目标记忆 ID；[observations.jsonl](observations.jsonl) 行 139（原始输入）、140（提取模型输入）；[api_calls.jsonl](api_calls.jsonl) 行 36；[input.json](session_04/input.json) 第 13 行 |
| 新证据是否被提取 | **是，核心内容被提取**：`Career change is being considered due to impact on mental health`；没有显式保留“current role 导致该影响”限定 | 同上原文；提取时尚无目标 UUID，后写入 `704a9763-9d2e-4cfc-8868-859ebcc41d70`；[extracted_facts.json](session_04/extracted_facts.json) `parsed.facts[2]`（第 13 行）；[observations.jsonl](observations.jsonl) 行 141 |
| 标注旧命题是否已存在 | **未发现精确匹配**。目标前 62 条记忆没有显式转行命题；前 3 会话标注也无此旧句。更广义的语义等价关系：**待人工核验** | 标注旧句位置 `/sessions/3/memory_points/0/original_memories/0`；无精确匹配 ID。完整逐条候选见 [target_before_memory_audit.json](target_before_memory_audit.json)、[before.json](session_04/before.json)。关键词结果只辅助检查，不作为语义证明 |
| 相关旧记忆是否被召回 | **是；它只表达工作压力影响心理健康，不等于完整旧命题**。top-1 为 `Mental health occasionally feels strained due to job demands and pressure to deliver high-quality healthcare solutions`，score **0.5582962992191942** | 原文 `/sessions/1/dialogue/4/content`；ID `9a10ef7e-b165-4362-a1b3-f93c35f601a3`，源自原运行第 2 会话 ADD；[observations.jsonl](observations.jsonl) 行 147，`candidates[0]`；更新模型输入见行 184，临时 ID `9`；[prefix_memory_origins.json](prefix_memory_origins.json) |
| 实际目标操作是否执行 | **是，执行 ADD**，没有覆盖相关旧记忆。模型计划 `id: "9", event: "ADD"`；原生 ADD 忽略这个临时 ID，生成新 UUID | 目标原文 `/sessions/3/dialogue/0/content`；实际新 ID `704a9763-9d2e-4cfc-8868-859ebcc41d70`；[full_operation_plan.json](session_04/full_operation_plan.json) `plan[9]`；[observations.jsonl](observations.jsonl) 行 185（模型输出）、192/193（ADD 尝试/成功）；[actual_operations.json](session_04/actual_operations.json) `array[3]`，SQLite history sequence **66** |
| 最终目标状态是否正确 | **核心状态存在；严格完整等价待人工核验**。新记忆表达“考虑转行、原因涉及心理健康”；单条记忆没有明确“当前角色造成影响”限定。工作角色及工作压力记忆仍存在，可供人工组合核对。不能称为“标注旧命题已成功更新” | 原文 `/sessions/3/dialogue/0/content`；新 ID `704a9763-9d2e-4cfc-8868-859ebcc41d70`；相关旧 ID `9a10ef7e-b165-4362-a1b3-f93c35f601a3`；[final_snapshot.json](final_snapshot.json) 第 318 行及 [reopened_snapshot.json](reopened_snapshot.json)，均通过重新打开实际 Qdrant 的校验；该旧 ID 文本未变，未执行 DELETE |

目标召回完整 top-5（未经调参；分数是原 Qdrant 返回值）：

| 排名 | 实际 ID | score | 内容要点 |
| --- | --- | --- | --- |
| 1 | `9a10ef7e-b165-4362-a1b3-f93c35f601a3` | 0.5582962992191942 | 工作压力影响心理健康 |
| 2 | `77e035ac-87b9-4cbb-b806-45a0c660aeb4` | 0.4433999247752169 | 心理状态 mildly abnormal、无已诊断问题 |
| 3 | `ed88894a-0679-413e-a6dd-8590b1dfc3ec` | 0.4207029155726773 | 喜欢瑜伽，保持灵活与头脑清晰 |
| 4 | `7271ec7f-affb-42af-9baa-0a6aa8d7bec6` | 0.3884017908032146 | 不喜欢赌博游戏及其心理健康影响 |
| 5 | `2a17f70c-f57f-4ada-a43d-c0c680bb61ec` | 0.3804381177373684 | 热衷改善健康结果 |

其他操作中的原生异常：第 4 会话完整计划 `plan[42]` 要求 UPDATE `id: "42"`（同理心及辩论能力），但原生临时 ID 映射只有 `0`–`34`。`mem0/memory/main.py:446` 查表失败，`main.py:471` 捕获并记日志，随后继续执行剩余操作。它没有到达 `_update_memory`，也没有对应 SQLite history；不能把该计划计作成功 UPDATE。证据为 [runtime.jsonl](runtime.jsonl) 第 **203** 行、[errors.json](errors.json)、[plan_execution_correspondence.json](session_04/plan_execution_correspondence.json) `plan[42]`。该异常未修复、未重试；它不是所选目标的 ADD 失败。

本表是基于实际原文与持久化结果的诊断；未调用问答评测或额外 LLM 作语义裁判。更强的语义正确性及更新保护结论均保留为未知或待人工核验。
