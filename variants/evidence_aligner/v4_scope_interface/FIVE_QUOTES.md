# 上一轮五条未完成来源或单元解析的引文

核查对象为 `variants/evidence_scope_planner/v2_offline/results/{skydiving,susan}.json` 中 `quote_audit` 的 `planner_v2` 项：`resolved_in_projection_list=false` 的五个原始引文条目。这里的 v1/v2 指**旧对齐器版本**，不是范围规划器版本。五个条目在对应原始来源中均能唯一逐字命中；未解析的共同原因是关联旧单元约束未满足，而不是文本不存在。位置为 Python Unicode 字符偏移，左闭右开。

以下路径均相对于项目根目录，完整用户 ID 为 `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。

- **Q1：** `Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`，source_id `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`；该旧记忆在 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json` 的 `api_snapshot.results` 中按 ID 找到，源文本唯一位置 `[0,119)`。
- **Q2：** `Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement`，source_id `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`；该旧记忆在 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json` 的 `api_snapshot.results` 中按 ID 找到，源文本唯一位置 `[0,94)`。
- **Q3：** `ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.`，source_id `ctx-1`；来源是历史用户话语 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content`，在该 content 中的唯一位置 `[60,218)`；该片段本身在 ctx-1 文本中的位置为 `[0,158)`。它不是 Q2 所在的旧记忆来源。

| 条目 | 模型产物 | 原引文 | 模型关联的旧单元及该单元在旧记忆中的原引文位置 | 未解析原因 |
|---|---|---|---|---|
| 1 | `runs/fixed_five_20261120/skydiving.json`，`result.parsed.records[0].old_quotes[0]` | Q1 | `u1`：`Dislikes extreme sports (e.g., skydiving)`，`[0,41)` | Q1 是整句，超出 u1 的引用范围。 |
| 2 | `runs/fixed_five_20261120/skydiving.json`，`result.parsed.records[1].old_quotes[0]` | Q1 | `u2`：`Dislikes extreme sports (e.g., skydiving) due to high injury risk`，`[0,65)` | Q1 还包含 u2 范围以外的安全冲突分句。 |
| 3 | `runs/fixed_five_20261120/skydiving.json`，`result.parsed.records[2].old_quotes[0]` | Q1 | `u3`：`conflicting with commitment to safety and well-being`，`[67,119)` | Q1 的前段不属于 u3 原引文；u3 短片段本身也不足以独立证明拆分器写出的完整因果关系。 |
| 4 | `runs/fixed_five_20261120/susan.json`，`result.parsed.records[0].old_quotes[0]` | Q2 | `friendship`：`friend named ThomasSusan`，`[6,30)` | Q2 同时包含称谓与支持分句，超过 friendship 单元。 |
| 5 | `runs/v2_paired_20261120/susan.json`，`result.parsed.records[2].old_quotes[0]` | Q3 | `friendship`：`friend named ThomasSusan`，`[6,30)`；`support`：`provides support and encouragement`，`[60,94)` | Q3 是另一次历史会话的 `ctx-1`，不是这两个旧记忆单元的引文；其提及朋友支持不能直接当成旧工作对福祉的支持。 |

表中 `runs/` 路径指 `variants/evidence_aligner/runs/`。每条的 source_id、关联单元和独立原始来源都保留，可用于人工复核。引文存在、源侧存在与单元绑定有效是三个不同问题，且都不自动证明模型的关系判断有语义支持；例如模拟跳伞的愉快体验不能自动证明真实极限运动偏好改变。

不能自动把前三条的整句裁成 u1/u2/u3 或把第五条 `ctx-1` 改写为旧记忆来源：裁剪可能删去因果和限定条件，重绑也会改变模型实际提交的证据。需要重新给出经验证的原文单元引文与关系，或将影响部分待确认。

可从项目根目录只读重现（不调用模型/API、不写文件）：

```bash
PYTHONDONTWRITEBYTECODE=1 python variants/evidence_aligner/v4_scope_interface/check_five_quotes.py
```

脚本逐条打印模型产物与记录索引、source_id、真实 source_ref、逐字原文、来源唯一位置、每个关联旧单元的原引文和位置，并断言五条均不能完整落入所关联旧单元。
