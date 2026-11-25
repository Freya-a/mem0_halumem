# v4 对齐器与 v2 范围规划器接口实验

新版本读取已有五案来源，去除旧单元里的人工属性/预期元数据，仅保留单元 ID、逐字引文和来源；原始完整会话只供上下文，新证据引用必须来自已选用户新单元。对于 skydiving 旧单元缺失 source_id 的情况，仅当单元引文在指定旧记忆唯一命中时，确定性补记该记忆 ID，并标记 `source_binding`；原始冲突来源不覆盖。

`prompt.txt` 定义输出；`interface.py` 分别检查字段结构、引文及单元、依据绑定和输入覆盖，并适配 `../../evidence_scope_planner/v2_offline/scope_planner.py`。模型自述的语义理由不是独立认证；直接输入规划器时 `semantic_support='unknown'`。`runner.py` 针对五案各调用一次、自动重试为零；请求前持久化尝试并拒绝重用运行目录。`FIVE_QUOTES.md` 和 `check_five_quotes.py` 是上一轮五条未解析引文的逐一核查。

首次回放发现 v2 规划器在旧范围无条件、新范围有限且无法求差时，可能错误保留整个旧范围。首次规划结果与运行时的代码快照保留在运行目录中；事后 v4 适配层对 v2 无法计算的条件组合做通用保守降级，原始条件仍保存在 `raw_record` 和 `scope_guard`。`reanalysis.py` 仅从已保存响应离线生成 `offline_safe/`，不重发请求、不覆盖首次结果；它不表示已精确算出未知范围。

不联网验证：

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_aligner/v4_scope_interface
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python runner.py --run-dir /tmp/v4-preflight-not-created
PYTHONDONTWRITEBYTECODE=1 python check_five_quotes.py
```

上述 runner 未传 `--execute`，只做离线预检。实际运行的 `runs/qwen_20261124_once/` 包含每案精确请求、原始响应、调用状态、配置、耗时、可获得用量、结构/来源校验及规划结果；`REPORT.md` 将独立人工语义审核与结构和引文结果分开。报告可离线重建：

```bash
PYTHONDONTWRITEBYTECODE=1 python review.py --run-dir runs/qwen_20261124_once
```

`reanalysis.py --run-dir <运行目录>` 只在尚无 `offline_safe/` 时创建结果，拒绝覆盖已保存的防护后结果；本次目录已生成，无需重复运行。人工审核通过内容哈希绑定，如结果变化会显示待审核，不会自动认作正确。

不要将实验报告的五案计数视为正式准确率。模型语义、时间和条件判断仍需要独立核实；直接规划严格保留待确认，引用唯一命中不保证语义成立。不做真实记忆写入。
