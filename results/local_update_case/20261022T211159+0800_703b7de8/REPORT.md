# 单个更新标注目标的本地诊断

本轮已完整输入到所选目标会话结束。目标“因心理健康影响而考虑转行”通过 **ADD** 写入，实际新记忆 ID 为 `704a9763-9d2e-4cfc-8868-859ebcc41d70`。标注所引用的完整旧命题未精确匹配到目标前数据库，因此不能将本例称为该旧命题的 UPDATE 成功案例。完整限定是否语义等价，留待人工核验。逐项证据见 [目标对照表](TARGET_COMPARISON.md)。

诊断已完成，但原生会话处理有 **1 条操作错误**：一个其他 UPDATE 使用了不存在的临时 ID `42`。原生逻辑捕获后继续运行，所有后续操作及最终快照均已保存。原执行器的严格检查因此以退出码 1 结束；[summary.json](summary.json) 保留 `status: failed`，没有改写为全通过。[diagnostic_summary.json](diagnostic_summary.json) 将诊断状态单独记录为 `completed_with_native_action_error`。[independent_verification.json](independent_verification.json) 的 `passed` 仅表示证据、操作（含失败）及数据库状态一致，不表示所有模型计划执行成功。

- 运行 ID：`20261022T211159+0800_703b7de8`。
- 关联原运行：[20261022T203207+0800_a40c12d5](../../local_smoke/20261022T203207+0800_a40c12d5/REPORT.md)。其完整副本在 [linked_original/](linked_original/REPORT.md)，原目录逐文件 SHA-256 前后完全一致。
- 固定用户 UUID：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。
- 环境沿用 `mem0_halumem`，Python 3.11.17，editable `mem0ai==0.1.118` 加载当前 `mem0_v0.1.118/mem0`；LLM 为 `qwen-plus`，Embedding 为 `text-embedding-v4`、1024 维。沿用原接口、温度、最大输出及 SDK timeout 配置，未更换模型。
- 原生提取/更新提示词、top-5 召回、临时 ID 映射及操作分派未改动；两个源码仓库 tracked diff 为空。观察器只记录并返回原响应、原异常；见 [observer_checks.json](observer_checks.json)、[source_git_verification.json](source_git_verification.json)。
- 标注、original_memories 和答案只供静态选样与离线诊断。实际输入严格等于原始 dialogue 的全部 role/content，没有预填标准记忆、persona、答案或额外系统消息。两个阶段的 SDK 输入均与原生提示词构造结果逐字核对。

历史核验与执行边界：

原 REPORT、summary、数据 SHA-256、UUID、前两完整会话、API 提取请求、add 返回、全量快照链、SQLite history 和磁盘 Qdrant 已交叉验证。前两会话各 12、8 条消息，对应 17、12 条 ADD，合计 29 条实际记忆；每个 ID 的会话来源见 [prefix_memory_origins.json](prefix_memory_origins.json)。原始索引为 0、1。核验成功后，复制 Qdrant 和 history 到本目录，从第三会话续接；没有重复输入前两会话。见 [prefix_verification.json](prefix_verification.json)。

选样在调用模型之前完成：按会话时间、标注数组顺序扫描该用户后续会话，显式兼容字符串和布尔 `is_update`，选中第 4 会话、原始索引 3、标注索引 0；此前检查项均不满足“真且 original_memories 非空”。见 [selection_scan.json](selection_scan.json) 与 [target.json](target.json)。第三会话完整输入，第四会话完整输入后停止，没有运行第五会话或选择第二个目标。原始时间作为旁证保留，写入时间保持 Mem0 原生 US/Pacific 运行时行为。

| 会话（原始索引） | 本轮输入消息 | 实际记忆数 | 提取事实 | 完整计划 | 实际操作 | 原生错误 |
| --- | --- | --- | --- | --- | --- | --- |
| 1（0，沿用） | 本轮不重复输入；原 12 条 | 0 → 17 | 原运行记录 | 原运行记录 | ADD 17 | 0 |
| 2（1，沿用） | 本轮不重复输入；原 8 条 | 17 → 29 | 原运行记录 | 原运行记录 | ADD 12 | 0 |
| 3（2） | 32 条，全部 | 29 → 62 | 33 | ADD 33、NONE 21 | ADD 33 | 0 |
| 4（3，目标） | 60 条，全部 | 62 → 78 | 21 | ADD 16、UPDATE 6、NONE 27 | ADD 16、UPDATE 5；NONE 27 不写库 | 1 个 UPDATE 因无效临时 ID 失败 |

本轮新增实际 ADD 49、UPDATE 5、DELETE 0；其中目标操作为 ADD。其他 UPDATE 是完整会话原生处理的结果，不代表额外选择了诊断目标。最终 78 条记忆，SQLite 共 83 条 history（29 条沿用＋54 条本轮实际写操作），NONE 共 48 次。每条计划，包括 NONE 与失败项，均有 [session_03/plan_execution_correspondence.json](session_03/plan_execution_correspondence.json)、[session_04/plan_execution_correspondence.json](session_04/plan_execution_correspondence.json) 对应记录。

本轮执行约 125.871 秒，4 次 LLM 调用、55 次 Embedding 调用。接口报告 LLM 16,180 tokens，Embedding 883 tokens；未进行额外接口试调用，离线复核未增加模型调用。上游未提供固定模型修订号，SDK 隐藏重试未独立计数。

完整观察与核验产物：

- [raw_history_prefix.json](raw_history_prefix.json) 保存到目标为止的全部原始历史前缀，仅含原始对话及时间；[selected_input.json](selected_input.json) 是本轮真正需要输入的第 3、4 会话。
- `session_03/`、`session_04/` 各有 `input.json`、`before.json`、`after.json`、`extracted_facts.json`、`recall_candidates.json`、`update_model_io.json`、`full_operation_plan.json`、`execution_results.json`、`actual_operations.json`、`add_return.json` 和 `verification.json`。
- [observations.jsonl](observations.jsonl) 按行记录时间、输入、提取输出、每条事实的召回候选及 ID/score、更新模型原始输入输出、实际方法调用及结果；[api_calls.jsonl](api_calls.jsonl) 保存 SDK 原始请求/响应、usage、finish_reason 和耗时。Embedding 响应只保存维度和有限性，完整记忆向量保存在快照与数据库中。
- [runtime.jsonl](runtime.jsonl)、[errors.json](errors.json) 保留原生错误及严格检查失败的 traceback。无效 ID 操作在进入写方法前失败，故其结果通过原生日志与完整计划对应；未伪造成功调用记录。
- [initial_snapshot.json](initial_snapshot.json)、各会话 before/after、[final_snapshot.json](final_snapshot.json) 为分页 scroll＋exact count＋显式 limit get_all 交叉核验的完整记忆快照，含 payload 和向量。目标前 62、最终 78 条均没有截断；最终 scroll 分两页。
- [reopened_snapshot.json](reopened_snapshot.json) 来自重新打开实际 Qdrant。ID/payload 严格相等，向量使用原运行已验证的浮点容差，最大差异 `2.460658182767972e-08`。SQLite `integrity_check: ok`；每会话历史重放和 add 返回均吻合最终数据库。
- [target_before_memory_audit.json](target_before_memory_audit.json) 保留目标前全部 62 条记忆，精确匹配和关键词检查不代替语义判断。
- `full_operation_plan.initial.json` 是最初生成的派生计划。后续仅将 ADD 的 `resolved_existing_memory_id` 改为 null，避免误将模型给出的临时数字 ID 解释为 ADD 写入的 UUID；原始模型输出没有修改，见 [derived_artifact_note.json](derived_artifact_note.json)。
- [local_update_case.py](local_update_case.py) 是实际执行时的脚本快照；[environment.json](environment.json) 记录其哈希。当前项目脚本仅更正上述派生 ADD 字段的含义，未重跑已输入会话。完整依赖、配置均保存在本目录，凭据脱敏。

仅离线复核，不调用模型、不重放会话：

```sh
conda run --no-capture-output -n mem0_halumem python scripts/verify_update_case.py results/local_update_case/20261022T211159+0800_703b7de8
```

也可在项目根目录执行本目录的 [verify-existing.sh](verify-existing.sh)。`--execute` 有一次性标记，拒绝对本目录重复输入。

更强的“更新保护有效”“标注旧命题已被正确覆盖”结论仍是未知；本轮证据只支持目标核心事实已新增、相关工作压力旧记忆仍保留，以及一条其他 UPDATE 被原生临时 ID 查表错误阻止。
