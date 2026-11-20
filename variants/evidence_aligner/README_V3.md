# Evidence aligner v3

v3 的独立入口是 `aligner_v3.align_evidence_v3(old_units, new_units, source_texts)`；[提示词](prompts/alignment_v3.txt)、[代码](aligner_v3.py)和 v1/v2 并存。模型每条记录只生成旧／新单元 ID、属性、关系、逐字片段、按需限定词和缺失依据；不再重复生成主张的主体、客体、改写句、解释、来源 ID 或单独的变化引文。相同单元可以出现在多条记录中。

限定词带 `side`、`kind`、`quote`、`claim_quote`；后者须包含限定词并与同侧关联单元的引文相包含，允许引用同来源的必要上下文。校验器从关联单元及逐字片段推导来源：一个可能来源才记录 `source_completions` 和字符位置，多个来源列入 `ambiguities` 并报错；同一来源中的重复片段保留所有位置。`parsed` 和 `raw_response` 保持模型原样。程序分别列出 `structure_errors`、`missing_evidence`、未处理单元和 `scope_review`，结构结果的 `status=passed` **仅代表确定性结构检查通过**，不代表关系、因果、身份、限定词的语义或复合断言已经核实；`semantic_review.status` 初始为 `not_reviewed`。

一次事后人工语义审核可写入运行目录的 `semantic_audit.json`，再用 `review_alignment_v3.py` 产生 `reviewed_results.json`。二者与模型原始结果分开；生成器将结构错误、人工标注的语义错误和仍需人工判断的条目分别输出，不自动宣称语义正确。单元覆盖只说明有可定位引文或列为未匹配，不能证明单元中的每个断言都已经处理。

## 验证和配对运行

在 `system/mem0_halumem_diagnosis` 目录下：

```bash
python -m unittest discover -s variants/evidence_aligner/tests -v
python variants/evidence_aligner/run_alignment_v3.py --preflight
python variants/evidence_aligner/review_alignment_v3.py variants/evidence_aligner/runs/v3_paired_20261120
```

重跑须明确指定不存在的运行目录，会产生最多五次付费请求，每案最多一次，失败不重试：

```bash
python variants/evidence_aligner/run_alignment_v3.py --run-dir variants/evidence_aligner/runs/v3_new_run
```

脚本在调用前比对 v1、v2 与 v3 的完整输入、三类组成部分及 user 消息字节，并核对模型参数和原产物哈希；运行时冻结代码和提示词，逐案保存调用、模型、原始及提供方响应、用量与校验。网络请求失败或提供方返回不同快照时停止，剩余案例标记为未开始，不进行自动重试。

本轮离线基线见 [v2 诊断](runs/v2_offline_diagnosis_20261120/REPORT.md)，五案 v3 的结果与完整人工审核见 [v3 报告](runs/v3_paired_20261120/REPORT.md)。v3 在身份文字复述和结构上有改善，但五案均有语义错误、待判断问题或缺失依据，尤其职业历史与跳伞出现未支持的 `state_change`，不能直接把本轮结构通过结果作为可靠对齐结论。
