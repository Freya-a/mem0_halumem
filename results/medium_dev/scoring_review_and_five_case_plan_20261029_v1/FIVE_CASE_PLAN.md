# 五案例：既有原生 Mem0 与简单保护提示的对照方案

**状态：方案及候选提示词已准备；简单保护组未实现、未执行，原生基线不重跑。**范围只含已有共同起点的 A、B、C、目标 7、目标 10，共 5 个用户会话、3 个用户。五案源自已观察到的原生表现，是定向探索，不是盲选或总体评估。本方案不运行其他方法或完整数据集。

## 对照对象与共同起点

原生组直接引用历史已观察到的相应 `after.json`、实际操作和调用日志；不复制后再对它重新 add。简单保护组每案只从该案的 `rollback_before/qdrant/` 和 `rollback_before/history.db` 复制独立物理副本，一次输入该案 `input.json.messages` 的全部原始 role/content。五案逐项路径、源哈希、用户、目标记忆 ID、历史操作与调用数见 [five_case_manifest.json](five_case_manifest.json)；[本轮只读复核](snapshot_reverification.json)为 5/5 PASS，无模型调用。

| 案例 | 用户 / 原数组下标 | 共用起点记忆数 | 输入消息数 | 历史基线关注点 |
|---|---|---:|---:|---|
| A | Martin `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f` / `sessions[8]` | 116 | 38 | 历史上极限运动的高受伤风险具体理由部分损失；一般安全顾虑仍在。 |
| B | Williams `1b846c59-456e-9550-dffd-4d23f1eca81f` / `sessions[6]` | 94 | 44 | 波斯猫平静性情细节损失，“优雅”能否等价保留仍待判。 |
| C | Donald `348492a7-cfe4-ee1d-73c3-c276d6ba8277` / `sessions[7]` | 114 | 60 | 过去 Blockchain Tech 雇主及高级职级细节损失，宽泛技术经历仍在。 |
| 目标 7 | Martin / `sessions[7]` | 107 | 60 | 已保存新岗位和平衡；旧求职语句的时间表达需进一步评价。 |
| 目标 10 | Williams / `sessions[4]` | 72 | 60 | 已保存晋升；旧 Director 语句是否应明确历史化仍待评价。 |

这五个起点均是原生前缀实际状态，含已记录的较早无效临时 ID 跳过操作的影响；不修复或补写。各案内共用自己的起点，跨案不能假设独立。完整已确认原生证据见 [既有定向复核](../human_review_packets/native_case_review_v1_20261028/README.md)。

## 唯一拟改变的系统行为

目标版本 `mem0ai==0.1.118` 的 `MemoryConfig.custom_update_memory_prompt` 会**替换**更新提示，而不是自动追加（见 `mem0/configs/prompts.py:get_update_memory_messages`）。因此设置该配置的完整值为冻结的 [simple_protection_update_prompt.txt](simple_protection_update_prompt.txt)：逐字保留该版本 `DEFAULT_UPDATE_MEMORY_PROMPT`，在其末尾追加通用 [simple_protection_addendum.txt](simple_protection_addendum.txt)。完整提示 SHA-256 `076baeb2afa9d8c4a0c87c7e24d7037a284793af17fc09e557ad08fbbb53389b`。新增段只要求保留未被反驳的独立细节、允许记录带限定的历史、正确保存新状态、不要虚构事实，并沿用原有 ADD/UPDATE/DELETE/NONE 与 ID/JSON 规则；没有案例事实、预期答案、人工标签或 QA 证据。原有提示中存在更积极的更新/删除规则，与补充原则之间可能有歧义，这正是该简单提示干预的一部分；不对输出做保护过滤或修正。

事实抽取提示、原生 top-5 召回、infer=True、执行逻辑、图关闭均不变；延续原始 profile：qwen-plus、text-embedding-v4/1024、temperature 0.5、max_tokens 16384、timeout 180 秒、SDK retry 0。`get_update_memory_messages` 仍会追加当前召回记忆、新抽取事实与 JSON 格式指令；执行前将最终组装的更新模型输入完整落盘，验证确是上述默认提示加这段文字及正常输入。原提示中可能有动态日期内容，必须保存实际渲染结果及执行时间，不凭模板相同声称实际输入逐字相同。

## 运行前离线检查与拟执行步骤

需单独开发一个只支持这五个固定 case 的新 runner（**目前不存在可直接执行的对照 runner**），输出写入新的 `results/medium_dev/five_case_simple_prompt_<run_id>/`，不要把现有 `medium_dev_run.py --resume` 指向原运行或原生库。拟执行流程如下：

1. 将 manifest、完整提示与源码/profile hash 固定到新目录。确认案例数5、每个 `ready.json` 的文件 SHA、备份无截断且只读原源；对每案把备份文件复制到各自独立目录并核验拷贝 SHA。`MEM0_DIR`、Qdrant 路径、history.db 和临时目录分别隔离，进程启动前设置 `MEM0_DIR`，防止 import 缓存串库；禁止指向原库、其他案或其他组的可写位置。
2. 在副本上校验点数、ID、payload、float32 向量（rtol=1e-6、atol=1e-7）、`history.db` 与共同起点 `before.json`/上一会话 history 一致；核对完整原始 role/content 输入和 source index。校验失败即停止该案，不调用模型。与原版文件逐字比较的只是复制前文件；Qdrant 打开或写入后使用语义及向量核对。
3. 为每案以原用户 UUID、完整 session messages、`infer=True` 调用一次原生 `Memory.add`；配置唯一差异为固定的 `custom_update_memory_prompt`。不传入 persona、标准记忆点、旧标注、QA、人工保护标签、基线 after 或预测值。不得重输前缀、预填事实、修改源码、拦截/更正模型计划或用关键词阻止写入。
4. 完整记录实际 SDK 每次 LLM/embedding 请求和返回、脱敏配置、model 别名/服务返回版本、时间、使用量及可获得费用；保留抽取结果、每个事实的原生 top-5、模型提示/响应、临时 ID 映射、完整操作计划含 NONE、实际写入及异常、history、前后全量快照和持久化重开核对。对无效 ID、解析失败、网络故障或部分写入，保留所有状态和错误，不当作成功、自动修复或重放；开始/结束状态和外部调用写入可恢复账本，不确定是否已发送的请求必须单列，不静默重复扣费。
5. 保存并核验原基线引用的 hash，保持它与简单提示组独立；针对每案在原生 observed after 与新 after 对照分析，列出新事实表达、受保护细节、历史状态、矛盾/误写、额外缺失、异常与实际调用。审查者先看完整 after，再以事先冻结的目标检查，不能只看单一记忆 ID 或操作名称。

原生基线记录为此前观察的一次运行：5 案总计 LLM **10** 次、embedding **147** 次；这不是简单提示组的预算上限。预计简单组通常每案一次抽取和一次更新，实际 embedding 数、异常、输出长度会变，必须按调用记录实计；服务未提供费用时，不估算账单。新旧调用相隔时日，qwen-plus 是可变别名、temperature 0.5：提取事实、召回、操作也可能因随机性或服务变化不同。即使唯一配置变化是提示，也不能把任何单次观察差异确定归因于提示本身；报告历史模型时间、实际 prompt、返回版本与所有差异。

## 评测口径与可比性

- 三项保护（A/B/C）：判断旧快照中已存在的具体命题是否在整个 after 有证据、部分保留、明确损伤或无法判断；对改变后的有效事实也要判断是否正确，不因保护而冻结过时状态。不要把未曾入库或未召回的事实当作本次覆盖损伤。
- 两项状态（7/10）：分别检查新状态是否完整、旧状态与新状态是否可按时间区分、是否有虚构关系。Director 可是宽泛职业称谓，不能仅因字符串共存判错；不要推断确切晋升日、雇主或新职位等无依据细节。
- 两组采用同一人工审核定义、记录原生与对照组每案分项及原文依据，区分 LLM 辅助与用户确认；附逐案全量证据链接。不得将这 5 案推广为官方总体更新指标或自动并入 24 目标分母。样本选择及历史基线不盲，不能当作无偏成效检验。
- 本次评分复核发现 QA 的事件日期和会话挂载截点可能不一致；未来若另做 QA，必须先锁定问题规定的知识截点及对应快照，不能直接使用后续会话快照。本方案不安排 QA 评分。

本计划只准备方案、样本清单和候选提示文件，没有调用模型，没有执行任何对照实验。后续执行前须实现并离线检验隔离 runner，记录方案及提示指纹；失败或状态未知不得悄悄重试。
