# v5 事实拆分与关系对齐实验

对齐器先输出 `facts`，再输出引用事实 ID 的 `relations`。适配层将新事实和旧关系分别投影到 `../../evidence_scope_planner/candidate_coverage_20261124/`，对引用、来源、字段及候选覆盖进行检查。模型语义自述不是独立授权；本次默认规划结果对事实和旧关系均保留待确认。

- `prompt.txt`、`interface.py`、`runner.py`：本次运行的提示词、适配层和调用包装。
- `PRECALL.json`：调用前代码、提示词、五案输入哈希与请求设置；完整运行时快照也在运行目录的 `frozen_at_call/`。
- `runs/qwen_20261124_once/`：每案精确请求、原始内容和 provider 响应、状态、耗时、可得用量、独立规划结果。`failed` 可能表示收到回复后的接口校验失败，具体看 `call` 和 `result.validation`。
- `HUMAN_REVIEW.json`：研究者对模型事实与旧关系分别进行的哈希绑定审核，不作为模型输出，也不输入规划器。
- `REPORT.md`：五案原文、结果、引用、人工判断、覆盖追踪、v4 比较及限制。

离线核验，不调用模型：

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

本次五个请求已结束且不自动重试。运行目录不可复用；不要为离线复核再次执行请求。本实验不接入 Mem0，不产生真实记忆写入。实验仅供开发诊断，不用于论文准确率。
