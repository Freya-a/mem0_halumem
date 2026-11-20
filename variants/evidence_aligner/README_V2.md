# Evidence aligner v2

v2 使用独立入口 `aligner_v2.align_evidence_v2(old_units, new_units, source_texts)` 和独立提示词 [alignment_v2.txt](prompts/alignment_v2.txt)。v1 入口、提示词、固定案例和运行结果均保留。

每条记录分别给出 `old_claim`、`new_claim`，各含 `subject`、`object`、`attribute`、`statement`、各自的 `qualifiers` 和 `event_date`。记录另有 `target_relation`、`change_type`、双侧引文、`change_evidence`、关系说明和未知项。独立新增可令 `old_claim` 为 `null`；`state_change` 必须关联旧单元，并提供位于新引文内的 `change_evidence`。限定词使用 `{kind, source_id, quote}`，挂在对应主张下。

程序校验 JSON、字段类型、单元和来源 ID、两侧引文与各单元的归属、逐字位置、限定词来源、事件日期以及单元覆盖。`quote_locations` 给出来源中的 Python 字符偏移，左闭右开；一个引文多次出现时保留所有位置。逐字来源与结构通过不能证明关系说明、限定词作用对象或语义结论正确，需另行语义审核。

## 精确配对回放

直接从 `runs/fixed_five_20261120/*.json` 读取 v1 的 `input`，而不是重新构造单元；比较完整输入、三个输入组成部分和实际发送的 user 消息字节的 SHA-256。每案 `input_validation` 保留两版值、单元 ID 和 v1 产物哈希。脚本在每次调用前再次核对；提示词及代码快照、输入、请求、原始和解析响应、校验、调用次数、token 用量均存于独立运行目录。

在 `/home/shu1004/ld/system/mem0_halumem_diagnosis` 下：

```bash
python variants/evidence_aligner/run_alignment_v2.py --preflight
python -m unittest discover -s variants/evidence_aligner/tests -v
```

重新试跑需指定尚不存在的新目录，会产生最多五次付费请求：

```bash
python variants/evidence_aligner/run_alignment_v2.py --run-dir variants/evidence_aligner/runs/v2_new_run
```

模型为 `qwen-plus-2025-12-01`，温度 0、JSON 输出、`max_retries=0`；每案最多一次，失败不重试。默认目录已存在时会拒绝覆盖。此前固定案例中的人工单元与未细分消息仍按 v1 原样使用；覆盖率只涉及输入单元，不代表完整会话的所有事实都已拆分。

本次配对结果与逐项语义审核见 [v1/v2 报告](runs/v2_paired_20261120/REPORT.md)，每案原始输出及结构错误保存在同一目录。结果显示 v2 有部分语义改善，但五案均未通过 v2 结构校验，不应把这轮当作可以直接下游写入的结果。
