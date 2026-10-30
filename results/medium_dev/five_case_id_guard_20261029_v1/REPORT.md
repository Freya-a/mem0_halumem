# 五案例：简单保护提示＋临时 ID 检查验证

2026-10-29（中国标准时间），先运行 B 并检查计划、实际操作、history 与数据库重开状态，全部通过后再运行 A、C、第 7、10 条。五案均完成：最终计划的全部写库操作与 history 按顺序一致，未发生无效 ID 跳写。**C 的首次计划出现无效 ID，触发一次纠正；纠正后的完整计划通过校验并执行。** 这表明该分支在本次运行中工作，但 ID 合法不代表记忆内容或知识保护必然正确。

五案按此前发现定向选择，单次输出可能变化；本报告的新运行语义判断由助手依据完整快照和原会话作出，尚未经过用户确认或独立盲审。旧结果参见[原生定向复核](../human_review_packets/native_case_review_v1_20261028/README.md)和[简单提示组报告](../five_case_simple_prompt_direct_20261029_v2/REPORT.md)，它们均是各自一次历史运行。

## 计划、纠正与实际操作

表中 A/U/D 是 ADD/UPDATE/DELETE 实际写库次数；NONE 是最终计划明确选择不操作、由原生逻辑执行的数量，不是错误。首次计划被拒绝时，其全部操作均未落地，之后模型返回一个新的完整计划；不能简单把两份计划中的条目逐一视为相同操作。

| 案例 | 首次有效 ID / 无效 ID | 纠正 | 首次计划 A/U/D/NONE | 最终计划 A/U/D/NONE | 实际写库 A/U/D；NONE；错误 | 证据 |
|---|---|---|---|---|---|---|
| B | 0–37 / 无 | 未触发 | 14/6/0/32 | 14/6/0/32 | 14/6/0；32；无 | [首次计划](cases/B/initial_plan.json) · [校验](cases/B/guard_audit.json) · [最终计划](cases/B/final_plan.json) · [写库](cases/B/actual_operations.json) |
| A | 0–45 / 无 | 未触发 | 6/5/0/40 | 6/5/0/40 | 6/5/0；40；无 | [首次计划](cases/A/initial_plan.json) · [校验](cases/A/guard_audit.json) · [最终计划](cases/A/final_plan.json) · [写库](cases/A/actual_operations.json) |
| C | 0–55 / `70` | 触发一次；纠正后通过 | 14/14/0/42 | 14/12/0/43 | 14/12/0；43；无 | [首次计划](cases/C/initial_plan.json) · [纠正请求与响应](cases/C/guard_audit.json) · [最终计划](cases/C/final_plan.json) · [写库](cases/C/actual_operations.json) |
| 第 7 条 | 0–47 / 无 | 未触发 | 8/22/0/26 | 8/22/0/26 | 8/22/0；26；无 | [首次计划](cases/target_7/initial_plan.json) · [校验](cases/target_7/guard_audit.json) · [最终计划](cases/target_7/final_plan.json) · [写库](cases/target_7/actual_operations.json) |
| 第 10 条 | 0–35 / 无 | 未触发 | 9/12/0/24 | 9/12/0/24 | 9/12/0；24；无 | [首次计划](cases/target_10/initial_plan.json) · [校验](cases/target_10/guard_audit.json) · [最终计划](cases/target_10/final_plan.json) · [写库](cases/target_10/actual_operations.json) |

C 首次计划共有 70 项，其中包含 28 个拟写库操作；整个计划因无效 `70` 被拦截，未执行其中任何一项。纠正后为 69 项，其中 26 个写库操作全部实际落地，43 个 NONE。`70` 所指拟议内容为“创新和积极思考”，其 `old_memory` 文本还包含忠诚和支持；模型纠正后的计划对该旧条目选择 NONE，并保留原文本。没有人工映射 ID，也没有执行首次被拒绝的计划。C 的[有效 ID 与 UUID 映射](cases/C/valid_ids.json)、[完整模型输入输出](cases/C/update_model_io.json)、[前后快照](cases/C/after.json)和[原生日志](cases/C/runtime.jsonl)可供核对。

B 本次未产生无效 ID，因此没有纠正请求或响应；其 [guard_audit.json](cases/B/guard_audit.json) 仅包含首次校验。前次简单提示组 B 曾有 `44`、`45` 无效，但这是不同调用的另一份计划，不能假设此次模型会复现。五案最终计划不存在因无效 ID 而跳过的写入，且未出现未完成或停止案例。

## 目标新信息和旧细节

| 案例 | 既有观察 | 本次带 ID 检查结果 | 证据 |
|---|---|---|---|
| B | 原生和简单提示组均保存部分波斯猫新信息，但平静性情细节损失；优雅是否等价保留未知。 | 保存纪录片、血统和王室关联；泛化记录提及兼顾宠物养护的实际考虑，但没有明确将波斯猫外观养护挑战完整绑定该猫种，新信息部分保留。原波斯猫平静性情在完整 after 未定位到，优雅是否由新表述等价保留未知。 | [输入](cases/B/input.json) · [前快照](cases/B/before.json) · [后快照](cases/B/after.json) · [写库](cases/B/actual_operations.json) |
| A | 原生与简单提示组均保存模拟跳伞；高受伤风险的历史具体理由损失，一般安全顾虑保留。 | 保存模拟跳伞、安全顾虑；高受伤风险这一具体旧理由在完整 after 未定位到，仍损失。写入“通过极限运动和瑜伽保持活跃”可能超出模拟跳伞经历原话，需谨慎。 | [输入](cases/A/input.json) · [前快照](cases/A/before.json) · [后快照](cases/A/after.json) · [写库](cases/A/actual_operations.json) |
| C | 原生与简单提示组均保存咨询公司获得首批客户；Blockchain Tech 历史雇主和高级开发职级细节损失。 | 保存公司获得首批客户；目标旧记忆变成“以前从事技术工作”，完整 after 未找到该用户曾在 Blockchain Tech 任高级开发的等价表述，具体历史雇主与职级仍损失。另一条同事与公司关系不等于本人职位经历。 | [输入](cases/C/input.json) · [前快照](cases/C/before.json) · [后快照](cases/C/after.json) · [写库](cases/C/actual_operations.json) |
| 第 7 条 | 原生保存转岗，但旧求职语句仍以现在时存在；简单提示组将该旧语句更新为新状态，另有旧 Director current role 待消歧。 | 保存新岗位及更好的工作生活平衡，并把旧求职记忆更新为转岗状态；求职阶段未单独历史化。另一条 Director at Huaxin 仍为 current role，与新岗位的时间关系未知；不能推测新雇主或职称。 | [输入](cases/target_7/input.json) · [前快照](cases/target_7/before.json) · [后快照](cases/target_7/after.json) · [写库](cases/target_7/actual_operations.json) |
| 第 10 条 | 原生和简单提示组均保存最近晋升；旧 Director 未显式历史化，但可能为兼容的宽泛称谓。 | 保存最近晋升 Lead Director；旧 Director 仍在，没有显式历史化，不能只凭两词共存判错，完整时间消歧仍未知。 | [输入](cases/target_10/input.json) · [前快照](cases/target_10/before.json) · [后快照](cases/target_10/after.json) · [写库](cases/target_10/actual_operations.json) |

上述判断覆盖各案已冻结关注点，而非完整会话所有事实。受影响其他细节仍可能存在；第 7、10 条不根据数据库实验写入时间推断真实事件日期。

## 模型调用、环境与限制

仅本轮工作进程临时将百炼域名加入 `NO_PROXY`/`no_proxy`；保持 `qwen-plus`、`text-embedding-v4`、1024 维、temperature 0.5、max_tokens 16384、timeout 180 秒、SDK retry 0。每案独立 Qdrant、history、`MEM0_DIR`，从该案原始会话前备份复制并验证；完整消息一次传入，未传入人工答案、保护候选或预期结果。ID 原型是独立复制且与[已有原型](../../../variants/invalid_temp_id_guard_20261029/guard.py)的 SHA-256 一致；它在出现无效 ID 时会增加一次带纠正反馈的 LLM 请求，因此方法不同于“仅加一条保护提示”。

| 案例 | LLM / Embedding 调用 | LLM 输入 / 输出 token | Embedding token | 会话耗时（秒） |
|---|---:|---:|---:|---:|
| B | 2 / 24 | 5,675 / 2,409 | 386 | 59.34 |
| A | 2 / 19 | 4,919 / 2,376 | 345 | 57.91 |
| C | 3 / 29 | 14,217 / 6,075 | 339 | 141.74 |
| 第 7 条 | 2 / 32 | 6,045 / 2,670 | 377 | 66.53 |
| 第 10 条 | 2 / 26 | 6,215 / 2,041 | 324 | 50.95 |
| **本轮合计** | **11 / 130** | **37,071 / 15,571** | **1,771** | — |

本轮无额外连通性测试调用；C 的第 3 次 LLM 即纠正请求。调用与响应完整记录于各案 `api_calls.jsonl`；LLM 均返回 `qwen-plus`，Embedding 均返回 `text-embedding-v4`，所有 LLM 返回 `finish_reason=stop`，未提供 `system_fingerprint`。服务未返回费用，实际账单未知。

模型别名可变，历史基线、简单提示组和本次调用的后端版本无法确认一致；temperature 非零、时间不同，模型抽取、召回、ID、计划和语义均可能变化。因此不能从这些单次输出差异断言纠正机制产生了某种保护效果，尤其 B 本次未触发纠正。ID 检查也无法发现合法但错误的 ID 或语义不当的更新，且合法计划执行期间的其他写库错误仍可能造成部分写入。

[离线和执行校验](verification_summary.json)确认：实际更新提示可由原生组装函数及真实召回、抽取逐字还原；首次及纠正输入输出与账本一致；最终计划所有写库操作的顺序、ID 和内容与 history 一致；五案数据库重开和快照核对通过。原生源码、原基线、备份及前两次运行的 330 个记录文件哈希复核未变；未重跑原生基线或整个数据集。
