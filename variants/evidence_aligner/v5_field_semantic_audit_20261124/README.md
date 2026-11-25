# v5 字段与语义离线归因

本目录保留对 v5 五案 21 条事实及 15 条关系的逐条人工归因，不修改 v5 输入、模型响应、旧审核、规划器或真实记忆。

- `REPORT.md`：原文、模型输出、旧审核、五类原因、条件字段表达示例、交集统计和最小修改建议。
- `DIAGNOSIS.json`：同一归因的机器可读版本，保留逐记录哈希、旧审核和各项标记。
- `annotations.py`：独立人工逐条说明；它不是模型结果，也不被规划器读取。
- `diagnose.py`：核对请求、响应、旧审核和运行时代码快照哈希后生成报告与统计。
- `tests/test_diagnosis.py`：检查条目覆盖、交集统计、条件解析和独立授权状态。

本次统计的多个类别可以重叠；`unconditional` 缺少逐轴明确证明是待核实，不等于事实被证明错误。对 relation 的限定分类可涉及关联新事实中已表达的限定；旧侧是否有相同范围仍需分别判断。

只读旧材料并重建本目录报告：

```sh
PYTHONDONTWRITEBYTECODE=1 python diagnose.py
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

脚本不调用模型或 API，不写入 Mem0，也不回填人工审核至自动流程。
