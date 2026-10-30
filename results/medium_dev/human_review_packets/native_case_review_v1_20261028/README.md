# 定向复核结论与方法原型共同起点

版本：`native_case_review_v1_20261028`；2026-10-28。复核方式：**LLM 辅助、用户确认**。这是独立于 `human_review_v1_20261028` 的本轮复核记录，不覆盖原审核、原生运行或原证据包。结构化记录见 [review_record.json](review_record.json)。

## 用户确认的定向结论

| 案件 | 原始用户会话 | 本轮结论 | 后续仍待确认 |
|---|---|---|---|
| A | Martin `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f` / `sessions[8]` | 历史上“高受伤风险”具体理由部分损失；一般安全顾虑仍保留。实际 UPDATE：记忆 `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`、history sequence 187。 | 全部快照中的其他未经逐项复核内容待确认；不把新模拟体验扩写为对所有真实极限运动的态度。 |
| B | Williams `1b846c59-456e-9550-dffd-4d23f1eca81f` / `sessions[6]` | 波斯猫“平静性情”细节损失。实际 UPDATE：记忆 `eef34a57-c82a-4995-877d-66b54b9589da`、history sequence 119。 | “优雅”是否等价保留暂定未知；完整快照其他未经逐项复核内容待确认。 |
| C | Donald `348492a7-cfe4-ee1d-73c3-c276d6ba8277` / `sessions[7]` | 历史雇主 Blockchain Tech 和高级职级细节损失；技术工作经历的宽泛概括仍在。实际 UPDATE：记忆 `05afde13-35bd-4d26-bbae-6de427d58db1`、history sequence 157。 | 历史职位不能写成当前职位；完整快照其他未经逐项复核内容待确认。 |
| D | Donald / `sessions[5]` | 模型输出无效临时 ID `53` 导致计划操作被原生跳过，目标新事实未找到；不计为旧知识损伤。 | Sandra、Mary 原有关系的部分内容仍在；其他未逐项核实内容待确认。 |

A、B、C 分属三个用户会话，每项对应各自一条实际 UPDATE。D 和 C 虽同一用户但在不同会话；D 的两位朋友不是两次独立错误。各案原话、计划、实际操作及完整前后快照链接见[原证据包](../native_targeted_cases_20261028_v1.md)。本次确认不代表独立盲审，也不能把此前的 `3/167` 当作总体损伤率。

第7、10条：更新前的相关旧状态均实际存在；新旧状态的时间表达、是否需要进一步消歧及最终评价**仍待进一步评价**，不只凭旧文本存在判错。

- 第7条旧记忆是 `Looking for a new job with better work-life balance`，新记忆是 `Has transitioned to a new role with healthier work-life balance`；用户在原数据 `Mar 01, 2026, 07:04:00` 确认转岗，不据此猜测新雇主或职称。
- 第10条旧记忆是 `Works at Historical Productions Ltd. as a Director`，新记忆是 `Recently promoted to lead director at Historical Productions Ltd`；用户在 `Feb 01, 2026, 18:47:19` 确认最近晋升，准确晋升日期未知。“Director”作为宽泛职业称谓与“Lead Director”可能兼容，不能只根据词语出现判断失败。

## 可用于原型的五个共同起点

下面是**五个不同用户会话**，不是五个独立用户：A 与第7条均属于 Martin，B 与第10条均属于 Williams；每行有各自不同的会话前备份。A、B、C 用于知识保护检查；第7、10条用于检查新状态是否保存，同时保留其时间表达待进一步评价。D 是独立的无效 ID／新事实未保存案例，本轮不额外把它加入这五个原型案例。

| 案例 | 起点：原始用户、下一会话 | 更新前完整知识条数 | 新会话完整消息数 | 快照备份与原文 |
|---|---|---:|---:|---|
| A 保护 | Martin `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f` / `sessions[8]` | 116 | 38 | [备份校验清单](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/rollback_before/ready.json) · [完整快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json) · [完整新会话](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json) |
| B 保护 | Williams `1b846c59-456e-9550-dffd-4d23f1eca81f` / `sessions[6]` | 94 | 44 | [备份校验清单](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/rollback_before/ready.json) · [完整快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/before.json) · [完整新会话](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/input.json) |
| C 保护 | Donald `348492a7-cfe4-ee1d-73c3-c276d6ba8277` / `sessions[7]` | 114 | 60 | [备份校验清单](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/rollback_before/ready.json) · [完整快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json) · [完整新会话](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json) |
| 第7条状态 | Martin / `sessions[7]` | 107 | 60 | [备份校验清单](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/rollback_before/ready.json) · [完整快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json) · [完整新会话](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json) |
| 第10条状态 | Williams / `sessions[4]` | 72 | 60 | [备份校验清单](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/rollback_before/ready.json) · [完整快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json) · [完整新会话](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json) |

第7条 before 含 `Looking for a new job with better work-life balance`；第10条 before 含 `Works at Historical Productions Ltd. as a Director`。两者都有目标更新所需的实际旧状态，而不仅仅是原始对话中的旧事实；但“严格纠错”与时间表达的最终口径仍待统一，不因存在旧文本就判错。

已离线核验5/5个备份：`rollback_before/ready.json` 所列文件哈希与原备份一致；将 Qdrant 复制到临时目录后，点 ID 和 payload/metadata 与 `before.json` 精确一致，向量按 float32 容差 `rtol=1e-6, atol=1e-7` 一致；`history.db` 的全部记录等于上一已提交会话的 history；每个 `input.json.messages` 与原始会话的全部 role/content 一致。完整计数和 SHA-256 见 [common_snapshot_validation.json](common_snapshot_validation.json)，离线复核脚本是 [verify_snapshots.py](verify_snapshots.py)。本次核验没有模型调用。

## 三组共同比较约束

1. 每个案例分别以对应 `rollback_before/qdrant/` 和 `rollback_before/history.db` 的**独立物理副本**启动原生 Mem0、简单提示对照和改进方法；`MEM0_DIR`、运行日志和输出路径也按案例与组隔离。使用原用户 UUID，不共享可写 Qdrant 或 SQLite 文件，不从 after 构造初始状态。备份复制后先核验文件哈希、点 ID／payload／向量及 history，再调用方法；不重新抽取前缀或手工预填事实。
2. 每组只输入该行 `input.json.messages` 的完整原始 user/assistant role/content，一次处理整个会话；时间戳和原始索引用作旁证，不额外拼入提示词。人工保护标注、人工结论、目标标签、`memory_points`、`original_memories`、QA 答案和其他组的 after／操作不得进入被测方法输入。保护标注只在运行后评测时使用。
3. 原生组固定官方 `mem0ai==0.1.118`、原生提示词、infer=True、top-5、关闭图记忆及已有模型配置；不得改变原生源码或过滤其输出。简单提示对照若实现，应只改变预先固定的通用更新提示词，保留同一抽取、检索、模型、数据和执行流程；不把本案例的保护内容写进提示。`custom_update_memory_prompt` 是该版本已有配置入口，但具体提示尚未编写或运行。改进方法须记录自身所有差异及额外组件；不得让它读取人工保护答案。
4. 各组逐案例记录所有 LLM／Embedding 实际请求、失败和重试、模型别名与提供商返回信息、耗时及可获得的 usage；同时保存初始快照、召回、原始模型输入输出、含 NONE 的计划、实际 ADD／UPDATE／DELETE、history、完整 after、异常和检查点。`NONE` 是计划，不是写库操作；同文 UPDATE 应如实统计。新方法的额外调用也要计入。不可仅按 UPDATE 事件或单条记忆判成功，须按完整 after 的语义和时间范围判断。
5. 五个起点来自原生实际运行的前缀，包含此前被原生跳过的计划产生的既有影响：Martin 的第6会话、Williams 的第2会话和 Donald 的第6会话均有已记录无效 ID。它们是共同起点的一部分，不为任何组修复或补写。各案例内同一快照可比较，跨案例仍有用户内和时间关联。

可以将现有原生结果作为上述同一起点上的**一次已观察到的基线**，无需重跑或覆盖；它已经在当时从表列会话前备份继续运行。若以后需要同时期的原生重复运行，也应从对应备份的独立副本开始，作为新的重复并单独计数，不覆盖已有基线。模型别名可能随时间变化、temperature=0.5，现有历史结果与后续调用不保证同一权重或随机输出，比较时需记录模型返回信息和调用时间。本批案例由已见结果定向挑选，只适合探索性原型，不代表总体性能。

## 调用与实际写库操作

以下数字直接来自既有原生会话 `api_calls.jsonl` 和 `actual_operations.json`；LLM、Embedding 均是实际 SDK 请求数，SDK 重试设为0。实际操作按整个会话记录，并不全部归因于目标。没有估算缺失 token 或费用。

| 案例 | 已有原生 LLM / Embedding 调用 | 已有原生实际写库操作 | 简单提示对照 | 改进方法 |
|---|---:|---|---|---|
| A | 2 / 27 | UPDATE 15、ADD 5、DELETE 1 | 未运行；本轮调用0、写入0 | 未运行；本轮调用0、写入0 |
| B | 2 / 27 | UPDATE 8、ADD 15 | 未运行；本轮调用0、写入0 | 未运行；本轮调用0、写入0 |
| C | 2 / 24 | UPDATE 12、ADD 11 | 未运行；本轮调用0、写入0 | 未运行；本轮调用0、写入0 |
| 第7条 | 2 / 36 | UPDATE 23、ADD 9 | 未运行；本轮调用0、写入0 | 未运行；本轮调用0、写入0 |
| 第10条 | 2 / 33 | UPDATE 14、ADD 12 | 未运行；本轮调用0、写入0 | 未运行；本轮调用0、写入0 |

原生模型、向量库和 history 均保留在原运行目录；本轮只建立本复核记录和离线核验产物，未启动三组新运行，也未开展全量 QA。
