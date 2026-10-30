# 无效临时 ID 的独立保护原型

这是对用户提出的无效 ID 问题做的**离线开发原型**，不是已运行的五案例简单提示对照，也不修改原生 Mem0 源码、已完成的对照、备份或冻结审核。没有连接模型，也没有重放任何案例。它会改变运行行为和提示词，若将来使用，须作为新的实验方法和新运行记录，不能替换或修正历史对照数据。

## 原因和四条受影响的计划

Mem0 0.1.118 召回旧记忆后，把真实 UUID 映射为字符串临时 ID，模型只能使用该次列表中的 ID。原生代码通过 `temp_uuid_mapping[resp.get("id")]` 查找 UPDATE/DELETE；不存在时捕获 KeyError，记录错误并继续执行其他计划，所以 `Memory.add()` 仍可返回。该行为见 [原生实现](../../mem0_v0.1.118/mem0/memory/main.py)。这不是后处理时删除结果；模型计划中的那几条更新从未进入实际写库。

| 对照案例 | 模型输出的无效 ID | 当次有效 ID 范围 | 旧文本唯一精确匹配的候选 ID | 风险 |
|---|---:|---:|---:|---|
| B | 44 | 0–36 | 26 | 模型计划中对应旧 ID 26 另有 NONE |
| B | 45 | 0–36 | 28 | 旧 ID 28 另有同文 UPDATE |
| C | 62 | 0–51 | 46 | 旧 ID 46 另有同文 UPDATE；无效计划的新文本会丢失“忠诚、支持”等旧细节 |
| 第 10 条 | 43 | 0–37 | 24 | 旧 ID 24 另有 NONE；无效计划的新文本可能丢失喜欢传记的具体理由 |

候选匹配是对记录的离线诊断，不应视为模型意图已确定，不能把它自动改号、补写或直接替换旧结果。详细证据是各案 [B 更新输入输出](../../results/medium_dev/five_case_simple_prompt_direct_20261029_v2/cases/B/update_model_io.json)、[C 更新输入输出](../../results/medium_dev/five_case_simple_prompt_direct_20261029_v2/cases/C/update_model_io.json)、[第 10 条更新输入输出](../../results/medium_dev/five_case_simple_prompt_direct_20261029_v2/cases/target_10/update_model_io.json)及相邻目录里的 `full_operation_plan.json`、`runtime.jsonl`、`actual_operations.json`。已执行的 A/B/C 目标 UPDATE 和第 7、10 条新状态可在实际快照与操作中核对；但 B/C/10 是**部分执行且有错误**，不应表述为整段会话完全成功。

## 原型做什么

[guard.py](guard.py) 提供 `guarded_add(memory, messages, *, audit, **kwargs)`，适用于 0.1.118 的同步、图关闭、单调用场景，需由未来的独立 runner 显式启用：

1. 在原生逻辑处理模型更新计划**之前**，检查完整 JSON 以及每条 UPDATE/DELETE 是否引用本次有效临时 ID。
2. 若无效，最多向同一个 LLM 再发送一次纠错请求，包含原始模型上下文、原始回复、验证错误及有效 ID 列表；不注入人工答案或预期事实。纠错后的**整个**计划再次检查。
3. 若第二次仍无效、纠错请求出错或无法解析，拒绝整个更新计划并向调用者显式抛出 `InvalidUpdatePlan`。即使旧版捕获内部异常，这个包装仍会报告失败；不能将该会话当成功。
4. `audit` 回调需持久化初次响应、验证错误、纠错请求及纠错响应；调用方还必须独立记录 SDK 请求、耗时、token、费用和状态，并在启动前复制隔离数据库。

这阻止了无效 ID 引起的**计划内部分写入**，也提供一次模型重新生成机会；并不能保证纠正后的事实一定正确或旧细节一定保留。有效计划开始执行后，如数据库或其他操作发生错误，原生流程仍可能部分写入，必须检查日志和快照。纠错请求增加模型调用及成本；`guarded_add` 临时替换实例的方法，只支持同一个 Memory 实例同时运行一个调用，且依赖该版本原生函数的局部变量，不支持异步或图记忆。现有简单对照 runner 的 observer 使用调用栈识别阶段，不能未经适配地叠加此包装；将来启用时应核验完整模型输入、阶段记录和账本。

## 离线验证

运行 `MEM0_DIR=/tmp/mem0_invalid_id_guard_test_20261029 MEM0_TELEMETRY=False /home/shu1004/anaconda3/envs/mem0_halumem/bin/python variants/invalid_temp_id_guard_20261029/test_guard.py`。测试读取上次保存的原始模型输出，验证四个无效 ID 会被拒绝；覆盖纠错成功、再次无效、异常传递和不执行写入。另用实际 Mem0 0.1.118 `_add_to_vector_store` 配合内存中的假 LLM、向量检索和写入函数验证失败关闭和有效 ID 纠正路径；未连接网络或真实数据库。结果见运行输出，测试不证明真实模型一定能纠正，也不能证明知识保护效果。
