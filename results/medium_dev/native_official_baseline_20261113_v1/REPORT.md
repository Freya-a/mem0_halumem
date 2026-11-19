# 原生 Mem0 开发子集：HaluMem 官方评分基线

2026-11-13（Asia/Shanghai）。使用已有原生 Mem0 结果、现有 `scripts/halumem_official/prepare.py` 和未修改的官方 `HaluMem/eval/evaluation.py`；评分器完整执行并退出 0。原生系统、检索和 QA 回答没有重跑，评分器对提取、更新、QA 重新调用模型。结果仅适用于选定的 3 用户、28 会话开发前缀，不与论文完整 Medium 分数直接比较。[范围、异常与案例](SCOPE_AND_CASES.md)；[输入与哈希](input_manifest.json)；[运行配置与代码指纹](run_metadata.json)。

## 官方指标

以下是本次官方输出。`all` 和 `valid` 的精确分子、分母也保存在 [metrics.csv](metrics.csv)；所有百分比四舍五入至两位。**6 条提取准确性评分无效，1 条更新评分无效**；它们不是已知的 0 分或已知错误类别。

| 指标 | 官方 all | 官方 valid | 分母 / 说明 |
|---|---:|---:|---|
| R | 62.92% | 62.92% | 241 / 383 非干扰参考点完整覆盖；无效 0 |
| Weighted R | 74.02% | 74.02% | 加权得分 212.625 / 重要度和 287.25；无效 0 |
| Target P | 98.35% | 98.35% | 267.5 / 272 个已被判为目标的提取记忆；另有 6 条无效项目标归属未知 |
| Acc. | 58.35% | 58.92% | 加权得分 360 / 全部 617；valid 为 360 / 611 |
| FMR | 50.00% | 50.00% | 19 / 38 干扰参考点得到 0 分；无效 0 |
| F1 | 76.74% | 官方未给出 | 官方用 all 口径的 Target P 和 R 计算；受 6 条目标归属未知影响 |
| 更新 C | 21.43% | 21.82% | 12 / 56；valid 12 / 55 |
| 更新 H | 0.00% | 0.00% | 0 / 56；valid 0 / 55 |
| 更新 O | 75.00% | 76.36% | 42 / 56；valid 42 / 55 |
| 问答 C | 56.00% | 56.00% | 42 / 75；无效 0 |
| 问答 H | 37.33% | 37.33% | 28 / 75；无效 0 |
| 问答 O | 6.67% | 6.67% | 5 / 75；无效 0 |

更新还有 **Other 1/56**，以及 **无效 1/56**；all 的 C/H/O 不应强制加至 100%。官方 all 的 Acc. 将无效项留在分母、分子不加分，所以它是官方约定的 all 值，不能解读为已确认六项均错误。官方异常路径会将六条无效准确性评分的 `is_included_in_golden_memories` 设置为 `false`；这些条目是否应计入 Target P 实际未知，因此 Target P 98.35% 和依赖它的 F1 是有缺失的官方程序输出，**不是六项完整判定后的确定值**。官方代码没有提供 valid 口径 F1，不自行补造。

逐条无效记录在 [invalid_scores.jsonl](invalid_scores.jsonl)：6 条 accuracy、1 条 update。无效更新与旧记录中解析失败的 Martin/Joshua 目标为同一项；这次官方程序没有保留具体异常或原始回复，不能认定两次失败原因相同。此次 QA 和更新的评分是重新调用模型产生的，不能与 2026-10-29 的旧报告数字混为同一批标签；旧报告未执行完整提取评分。[历史分数及限制](../official_eval_development_20261029_v1/REPORT.md)。

## 逐案、版本和核验

- 官方完整汇总及四类逐条记录：[memzero_eval_stat_result.json](results/memzero-development/memzero_eval_stat_result.json)；[逐用户中间文件](results/memzero-development/tmp2/) 保留各用户原始评分条目。
- 24 条人工审核目标与既有官方更新点的对应、重复与归并、证据不确定和原生会话异常：[target_audit_scored.csv](target_audit_scored.csv)。其中旧标签与本轮新标签分列；这份审核表不改变官方 56 点分母。
- 对 R、Weighted R、Target P、Acc.、FMR、F1 及更新/问答 C 的汇总做了独立算术复核：[verification.json](verification.json)。这只能核对算术和计数，不能证明模型判词语义正确。官方输出保留逐条得分/标签，但 `evaluation.py` 丢弃评分理由与原始响应；无法事后从本次官方文件恢复它们，也没有保存每次调用的 token/实际费用。
- 评估模型为 `qwen-plus` 别名，temperature 0、max tokens 16384、timeout 180 秒、官方并发 10；别名未固定权重版本。官方代码提交 `718f16ff0c83413b1c86fa83fc13cc1a639871f9`；Mem0 提交 `ed5a1e9fc68fcd7671a70c33a540d24573755449`。详细依赖、代码哈希、重试设置和时间见 [run_metadata.json](run_metadata.json)，运行日志见 [official_run.log](official_run.log)。
- **环境限制**：本次评分使用 Python 3.10.20、OpenAI SDK 2.44.0，而上游 `pyproject.toml` 声明 Python >=3.11、OpenAI SDK `^1.109.0`。官方代码在本次环境执行完成、算术核验通过，但这不是上游声明的依赖组合，影响可复现性；后续严格对比应在固定、符合要求的同一环境下对两组评分。
- 原始输入没有可用于官方 `search_duration_ms` 的完整检索耗时；官方输出中检索时间为 0 表示未提供，不能理解为实测 0。

## 尚需补充与后续对比

如需完整判定的提取指标，需补评六条 accuracy 并明确各自目标归属；如需完整更新分母，需补评一条无效更新。应记录评分请求、原始响应、版本和重试，而不是从空值猜结论；补评后的结果需与本报告原始输出分开保存并披露方法。复核结果仍依赖评分模型，目标/评分时间及四个原生异常会话也应审查。完整 Medium 结果需要对未运行的用户和会话另行执行完整 Mem0 与评测流程。

两个已确认的旧知识细节受损案例及官方评分覆盖边界见 [SCOPE_AND_CASES.md](SCOPE_AND_CASES.md)。本次没有添加旧知识保持率或联合成功率。后续方法的输入、模型、快照截点、检索和评分设置如何配对，见 [COMPARISON.md](COMPARISON.md)。
