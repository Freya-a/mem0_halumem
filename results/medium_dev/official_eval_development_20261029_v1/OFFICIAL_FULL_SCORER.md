# 完整官方评分入口

本目录的 `run_eval.py` 和 `REPORT.md` 是既有的更新及问答开发评测，并没有运行完整官方评分。为保留历史结果和代码指纹，它们未被改写。

完整官方评分的输入适配、使用说明和项目额外指标清单见 [scripts/halumem_official](../../../scripts/halumem_official/README.md)。该入口直接执行 `HaluMem/eval/evaluation.py`，包含提取、更新与问答评分，并在独立新目录输出结果。
