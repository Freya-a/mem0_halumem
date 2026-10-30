# 五案例简单保护提示对照：直接连接运行报告

运行于 2026-10-29，中国标准时间。本次五个定向案例从各自会话前原始备份的独立副本运行一次；旧版原生结果直接引用历史记录。**观察到 A、B、C 的目标旧知识细节在简单提示组仍有损失；第 7 条保存转岗，第 10 条保存晋升。** B、C、第 10 条各存在原生跳过的无效 ID 更新，结果须连同这些错误理解。五案是按已观察结果定向选择的开发探索；不是总体损伤率，也不能将单次差异归因于提示。

本报告的简单提示组语义判断由本次助手依据完整前后快照和原会话作出，**尚未经用户确认或独立盲审**；原生 A/B/C 判断引用已有 LLM 辅助、用户确认的[定向复核](../human_review_packets/native_case_review_v1_20261028/README.md)。下述“新信息”指每案表中所列目标信息，不是对整段会话全部事实的穷尽评分。

## 五案例结果

| 案例 | 原生基线 | 简单提示对照 | 核心证据 |
|---|---|---|---|
| A：运动安全 | 保存团建模拟跳伞和态度变化；高受伤风险的具体历史理由部分损失，一般安全顾虑保留。 | 保存模拟跳伞和安全顾虑；旧记忆改写为以往因安全顾虑回避，完整 after 未找到高受伤风险这一具体理由，故该细节仍损失。对极限活动更开放、享受刺激的广泛表述可能超过模拟体验原话，需谨慎。 | [原会话](cases/A/input.json) · [旧状态](cases/A/before.json) · [原生 after](../williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/after.json) · [对照 after](cases/A/after.json) · [实际操作](cases/A/actual_operations.json) |
| B：波斯猫 | 保存历史血统、王室关联和养护考虑；平静性情损失，优雅是否等价保留未知。纪录片体验在最终波斯猫记忆中是否绑定待判。 | 保存纪录片体验、历史血统、王室关联及养护考虑；完整 after 未找到波斯猫“平静性情”的等价内容，细节仍损失；优雅与高贵外观是否等价仍未知。英国短毛猫的平静不能代指波斯猫。两条其他 UPDATE 因无效临时 ID 被跳过。 | [原会话](cases/B/input.json) · [旧状态](cases/B/before.json) · [原生 after](../williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/after.json) · [对照 after](cases/B/after.json) · [实际操作](cases/B/actual_operations.json) · [错误](cases/B/runtime.jsonl) |
| C：历史职位 | 保存咨询公司获得首批客户；历史雇主 Blockchain Tech 与 senior developer 职级细节损失，宽泛技术经历仍在。 | 保存首批客户；目标旧记忆被改成“以前从事技术工作”，完整 after 未找到同一人曾在 Blockchain Tech 任高级开发人员的等价陈述；同事与公司关联不能代替该职位经历。另有一条 UPDATE 因无效临时 ID 跳过。 | [原会话](cases/C/input.json) · [旧状态](cases/C/before.json) · [原生 after](../williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/after.json) · [对照 after](cases/C/after.json) · [实际操作](cases/C/actual_operations.json) · [错误](cases/C/runtime.jsonl) |
| 第 7 条：转岗 | 保存转岗及更好的工作生活平衡；旧求职语句依旧以现在时存在，历史化和消歧待判。 | 保存转岗与更好的平衡，原“正在找新工作”记忆直接更新为新状态，不再以现在时保留该求职句；转岗本身表明状态转换，但原求职阶段的具体表述没有单独保留。另一条先前的 Director at Huaxin 仍称 current role；它与新岗位的关系和时间消歧未知，不推测新雇主或职称。 | [原会话](cases/target_7/input.json) · [旧状态](cases/target_7/before.json) · [原生 after](../williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/after.json) · [对照 after](cases/target_7/after.json) · [实际操作](cases/target_7/actual_operations.json) |
| 第 10 条：晋升 | 保存最近晋升 Lead Director；旧 Director 未显式历史化，作为宽泛称谓可能兼容。 | 同样保存晋升；旧 Director 仍未显式历史化，与 Lead Director 可能兼容，不能仅凭旧词出现判错；明确时间关系与下游消歧仍待评估。另有一条关于历史传记的 UPDATE 因无效临时 ID 跳过。 | [原会话](cases/target_10/input.json) · [旧状态](cases/target_10/before.json) · [原生 after](../williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/after.json) · [对照 after](cases/target_10/after.json) · [实际操作](cases/target_10/actual_operations.json) · [错误](cases/target_10/runtime.jsonl) |

原生第 7 条额外存在此前的 Director 职称语句，不能根据该文本自行确定新职称或雇主。第 10 条的晋升日期未给出，不使用实验数据库写入时间推断事件时间。A/B/C 只对已明确的目标旧细节做判断，完整 after 里的其他知识没有逐项人工核验。

## 操作与跳过

ADD、UPDATE、DELETE 是实际 history 写入；NONE 是模型计划并由原生逻辑执行的不写入操作。无效 ID 跳过是模型计划的 UPDATE 未执行，不计入实际 UPDATE。各案的完整计划、ID 映射、原始输出和运行日志保存在相应 `cases/<案例>/` 目录。

| 案例 | 原生实际 ADD / UPDATE / DELETE；计划 NONE | 对照实际 ADD / UPDATE / DELETE；计划 NONE | 对照错误及跳过 |
|---|---|---|---|
| A | 5 / 15 / 1；1 | 7 / 5 / 0；49 | 无 |
| B | 15 / 8 / 0；30 | 14 / 3 / 0；34 | UPDATE 临时 ID `44`、`45` 无映射，跳过 2 条；[日志](cases/B/runtime.jsonl) |
| C | 11 / 12 / 0；38 | 13 / 11 / 0；40 | UPDATE 临时 ID `62` 无映射，跳过 1 条；[日志](cases/C/runtime.jsonl) |
| 第 7 条 | 9 / 23 / 0；15 | 7 / 24 / 0；21 | 无 |
| 第 10 条 | 12 / 14 / 0；25 | 12 / 11 / 0；27 | UPDATE 临时 ID `43` 无映射，跳过 1 条；[日志](cases/target_10/runtime.jsonl) |

未修复、重映射或重放这些操作。B、C、10 因原生执行错误标记为 `completed_with_errors`；其他已写入状态是真实的，不能把整个会话当成全成功。全部操作和 NONE 的实际结果、完整前后快照、history 重放和持久化重开检验见 [verification_summary.json](verification_summary.json)。

## 网络、配置、用量与可比性

两种请求的接口域名均为 `dashscope.aliyuncs.com`。仅在本轮测试进程和五个工作进程临时为 `NO_PROXY` 和 `no_proxy` 加入该域名，保留已有排除项；未修改系统代理、VS Code 或 `.env.local`。网络设置见 [network_environment.json](network_environment.json)。连通性先各请求一次：`qwen-plus` 成功，`text-embedding-v4` 成功且返回 **1024** 维；见 [LLM 测试](connectivity_llm.json)、[Embedding 测试](connectivity_embedding.json)。

五案沿用 `mem0ai==0.1.118`、`qwen-plus`、`text-embedding-v4/1024`、temperature 0.5、max_tokens 16384、timeout 180 秒、SDK retry 0 和原生抽取、检索及写库逻辑。唯一提示变更是 `custom_update_memory_prompt` 中的原始完整提示加冻结通用保护段；原始、对照、完整差异分别见 [原提示](original_update_prompt.txt)、[对照提示](control_update_prompt.txt)、[差异](prompt.diff)。逐案保存的实际更新模型输入可由原生组装函数及实际召回、抽取结果**逐字重建**，见各案 `update_model_io.json` 与 [校验](verification_summary.json)。没有注入审核答案、保护候选或预期结果。

| 案例 | LLM / Embedding 成功调用 | LLM 输入 / 输出 token | Embedding token | 会话耗时（秒） |
|---|---:|---:|---:|---:|
| A | 2 / 20 | 5,151 / 2,760 | 315 | 66.47 |
| B | 2 / 23 | 5,679 / 2,445 | 372 | 59.47 |
| C | 2 / 26 | 7,635 / 2,797 | 267 | 68.62 |
| 第 7 条 | 2 / 31 | 5,973 / 2,612 | 425 | 65.90 |
| 第 10 条 | 2 / 30 | 6,280 / 2,256 | 342 | 57.25 |
| **五案合计** | **10 / 130** | **30,718 / 12,870** | **1,721** | — |
| 连通性测试 | 1 / 1 | 12 / 2 | 5 | LLM 0.91；Embedding 0.71 |
| **本次总计** | **11 / 131** | **30,730 / 12,872** | **1,726** | — |

以上均为 SDK 成功请求及服务返回用量，模型请求分别有完整开始和结束账本。返回的 LLM 模型标识均为 `qwen-plus`，Embedding 为 `text-embedding-v4`；所有 LLM 输出 `finish_reason=stop`，返回的 `system_fingerprint` 为空。服务未返回费用，账单金额未知，不估算。原生基线五案 LLM 10、Embedding 147；历史和本次的可变 `qwen-plus` 别名均未提供可确认的后端版本，无法确定权重一致，且调用时间不同、temperature 非零。提示以外的随机性和服务变化均可能影响结果。

五份备份复制前哈希、复制后点数、ID、payload、向量、history 和完整原始 role/content 全部通过检查，见 [preflight.json](preflight.json)。运行后重新检查源备份、基线引用文件和[上次失败记录](../five_case_simple_prompt_20261029_v1/REPORT.md)的 161 个文件哈希未变；本次没有重跑原生基线或整个数据集。各案 `api_calls.jsonl`、`observations.jsonl`、`input.json`、`before.json`、`after.json`、`actual_operations.json`、`runtime.jsonl`、`status.json` 与 `persistence.json` 为完整运行证据。
