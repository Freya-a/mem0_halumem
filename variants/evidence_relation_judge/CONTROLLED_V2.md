# 组件一受控改进版

改进版为 `relation_judge_v2.py` 和 `run_local_v2.py`；原 `relation_judge.py`、`run_local.py` 和既有运行记录不变。沿用相同六类标签、输入和基础引文校验。`SYSTEM` 在原提示词后追加区分旧片段/新引文、对象属性条件、局部范围、模拟与真实活动、证据约束及确认问题的要求；这是提示词干预，不能保证语义正确。

## 候选片段恢复

模型的原始 JSON 和 `candidate` 不修改；`fragment_match` 另存 `raw`、`located`、`method`、`start`、`end`；`located_candidate` 是仅对候选片段进行定位后的副本。

- `exact`：原片段已逐字存在于该事实的旧记忆引文；原样保留。重复出现时不猜测唯一位置，偏移可为 null。
- `unique_casefold`：当不存在已符合该事实引文的逐字匹配时，只比较与原片段**相同字符长度**的旧记忆连续子串；对 Unicode `casefold()` 后相等的所有重叠位置计数。全旧记忆恰有一个匹配，而且该位置包含在该事实的一条 memory 引文中，才恢复旧原文的写法。偏移是 Python 字符索引，右端不包含。此规则保守地不尝试不同长度的大小写映射、空格、标点或 Unicode 规范化。
- `ambiguous_casefold`、`outside_fact_evidence`、`not_found`：不恢复、不猜测，标为 validation 错误。空片段按原 v1 规则允许，方法为 `empty`。

定位后仍调用原版 `validate_candidate`，严格检查标签、ID、旧引文、新证据引文等；不会用新引文替代旧片段，也不会放宽证据来源。模型、解析或校验错误保留独立阶段与原始输出，不转换成模型的 `uncertain`。所有结果仅是候选，语义是否正确始终为 `not_checked`。

运行（必须是不存在的输出文件，不覆盖）：

```bash
PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  /home/shu1004/anaconda3/envs/emem_vllm/bin/python \
  system/mem0_halumem_diagnosis/variants/evidence_relation_judge/part1_relation_judge/run_local_v2.py \
  system/mem0_halumem_diagnosis/variants/evidence_relation_judge/runs/real_cases_20261106/promotion_input.json \
  --output /tmp/relation_v2_new.json
```

无模型测试：`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s system/mem0_halumem_diagnosis/variants/evidence_relation_judge/part1_relation_judge -p 'test_*.py' -v`。三个开发案例的完整前后结果和局限见 `runs/controlled_v2_20261106/REPORT.md`。
