# 离线候选覆盖追踪

基于 `../v3_offline/scope_planner.py` 的独立副本，增加候选编号、旧关系/新增子判断追踪、重叠范围阻塞时的逐条待确认，以及不可归属结果的保守后备处理。修改未进入原 v3、对齐器或 Mem0。范围和时间逻辑仍按 v3 工作。追踪不证明语义正确；尤其 B 组的 `semantic_support` 是旧实验使用的模型候选兼容标记，不是独立授权。

- `REPORT.md`：五案原始记录、逐字引文、旧 B 动作的人工作业拆分、每个候选去向和新旧差异。
- `MANUAL_SUBFACTS.json`：基于原文及既有审核整理的人工作业结果，不是模型输出，不输入规划器。生成器仅供审计溯源，拒绝覆盖已有审核。
- `scope_planner.py`：新规划器副本。
- `replay.py`：用保存的模型响应重建三组输入，检查旧实验重现并生成 `results/*.json`。
- `make_report.py`：核对旧审核与动作哈希、子事实所引证据和全量动作覆盖后生成报告。
- `tests/test_coverage.py`：聚合缺口、子判断、来源缺失、冲突及二维范围检查。

在本目录执行：

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python replay.py
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

`results/*.json` 保存新旧计划及 `candidate_coverage`；每一项通过分类与索引指向最终输出。覆盖账本只追踪实际输入的候选和规划器拆出的判断，无法证明模型已经发现原文的所有事实。所有输出仅供研究，不能作为真实记忆写入授权。
