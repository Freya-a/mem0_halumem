# Evidence aligner：属性级证据对齐

v2 的独立接口、提示词与配对回放说明见 [README_V2.md](README_V2.md)。

`aligner.align_evidence(old_units, new_units, source_texts)` 在一次 Qwen 请求中比较一条旧记忆的全部输入单元与本轮全部输入的新单元，输出关联 ID、属性、变化类型、新旧主张、两侧逐字引文、条件、时间词、事件日期和未知项。本目录不计算影响范围，也不写 Mem0。

关系判断参考 [ERASE 的 `edit_retrieved_facts()`](https://github.com/belindal/ERASE/blob/main/models/kb_model.py#L612)：对照输入与既有事实、在没有反证时不推翻旧事实；本实现把逐事实多次查询改为整案一次查询，并增加属性、来源引文和不确定性，没有复制 ERASE 实现或执行其后续写入操作。

## 输入与输出

- `old_units`：SimpleMem `units` 数组，每项至少包含 `unit_id`、`raw_statement`、`memory_quotes`；`source_id` 可省略，默认指向 `source_texts.memory.source_id`。
- `new_units`：同样包含 `unit_id`、`raw_statement`、`memory_quotes`，并显式给出对应消息的 `source_id`；每个输入单元目前只能绑定一个来源。多来源的新证据可分别作为多个单元关联同一记录。
- `source_texts`：`memory` 对象含 `source_id`、`text`；`messages` 数组中每条含 `source_id`、`text`、`speaker` 和 `side`（`old` 或 `new`），可附带 `recorded_at`、`source_ref` 等元数据。ID 在全部来源内唯一，输入引文必须逐字出现在各自来源中。
- 结果含 `parsed`、`raw_response`、`parse_errors`、`validation_errors`、`coverage` 和 `semantic_correctness`。`unmatched_old_unit_ids` 是模型明确认为没有相关新证据的旧单元，并非事实已验证；未提及的 ID 进入 `uncovered_*` 并报错。解析失败时原始响应和待覆盖 ID 仍保留。
- 记录中的 `event_date` 为原文日期字符串或 `null`；录入时间不是事件日期。`conditions`、`time_expressions` 的每项均为 `{source_id, quote}`；`unknowns` 是字符串数组。旧引文必须位于相关旧单元的记忆引文中，新引文必须位于相关新单元的证据中；每个被关联单元都要有相应引文。

`passed` 只表示 JSON、字段、ID、引用归属及单元 ID 覆盖通过。逐字匹配、模型写了某个 ID、日期字面格式与引用存在，都不能证明引用支持该项语义、每个属性都被提及、时间词适用该事件或结论正确。需要语义复核；本次职业历史和跳伞结果是反例。

默认后端读取 `config/medium_full_qwen_plus_20251201.json` 和 `.env.server.medium-full`，复用 SimpleMem 试验的文件优先配置、直连客户端和关系判断器的引用定位逻辑；使用 `qwen-plus-2025-12-01`、`temperature=0`、`response_format={"type":"json_object"}`、`max_retries=0`，不会自动重试。调用将发送提供的旧记忆及完整消息，且可能产生费用。`backend=` 可注入离线测试后端。

## 五案与运行

工作目录为 `/home/shu1004/ld/system/mem0_halumem_diagnosis`：

```bash
python variants/evidence_aligner/run_alignment_trial.py --preflight
python -m unittest discover -s variants/evidence_aligner/tests -v
```

一次新的实际试验（最多五次付费请求，每案一次；目录必须不存在）：

```bash
python variants/evidence_aligner/run_alignment_trial.py --run-dir variants/evidence_aligner/runs/fixed_five_new
```

脚本为每案在调用前保存输入与完整提示词；调用后保存原始响应、提供方响应、解析结果、引用及覆盖错误。断网或接口错误时停止，不重试；模型名不符时停止。目录独占创建，避免覆盖旧实验或误续跑。已完成的一次运行见 [报告](runs/fixed_five_20261120/REPORT.md) 与 [manifest](runs/fixed_five_20261120/manifest.json)。

五案沿用 `evidence_relation_judge/runs/scope_positioning_20261118_v1` 的固定案例。跳伞旧单元采用与其旧记忆完全匹配的新版 SimpleMem `prompt_v2` 三个单元；其余四案没有对应的新版 SimpleMem 五案拆分产物，使用先前固定的**人工**属性单元。每案已有一个人工固定的新单元；对原固定案例中其余已选消息逐条添加未细分的来源单元，不能冒称它们是 SimpleMem 输出。完整会话作为带说话人和来源 ID 的上下文一并输入，但未被固定或追加为单元的其余会话内容不计入单元覆盖。因此，此试验不能证明整段会话的所有事实均已拆分或覆盖。

试验代码的原始快照保存在 `runs/fixed_five_20261120/frozen_code/`。试跑后仅加固了日期字面格式、异常类型和默认客户端关闭；[离线重校验](runs/fixed_five_20261120/offline_revalidation.json) 没有调用模型，五份响应的状态、错误与覆盖结论均未变化。
