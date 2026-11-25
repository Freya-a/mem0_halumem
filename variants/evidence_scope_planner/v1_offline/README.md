# 离线影响范围规划器 v1

只使用 Python 标准库。它是研究用的计划生成器，不执行修改、不连接 Mem0，不调用模型、API 或全量数据。`scope_planner.py` 是纯函数实现；`adapter.py` 读取既存 v1/v2/v3 对齐产物，回放选用 v3。原始材料和旧代码均未改动。

在本目录运行：

```bash
python -m unittest discover -s tests -v
python replay.py
python make_report.py
```

`replay.py` 重新生成 `results/{case}.json`；`make_report.py` 从独立预期和回放结果生成 `REPORT.md`。`fixtures/*.json` 是人工核对输入，`*.expected.json` 是独立人工预期，仅供报告，绝不传入规划器。`ALIGNER_AUDIT.md` 记录三版输出及引文；`SOURCES.md` 记录原始数据位置、标识、上下文和缺失。

## 函数接口

`build_scope_plan(old_memory, old_units, evidence_sources, alignments)` 返回普通字典（ScopePlan），含 `modify`、`preserve`、`uncertain`、`add`、`editable_spans`、`protected_facts`、`quote_checks`。位置为 Python Unicode 字符零基、左闭右开区间。每个旧 unit 使用 `id`、`quote`、`fact`，可给 `memory_id`、`source_ref` 和 `protected_claims`（含旧文 `quote` 与 `fact`）；来源提供 `source_id`、`text`、`source_ref`。来源指针的真实性由调用方提供和核对；函数检查 ID 唯一、指针非空及引文是否唯一在该指定文本中，不能自行证明外部路径内容或用户身份。

对齐记录使用 `unit_id`、`relation`、`old_subject`/`new_subject`、`old_attribute`/`new_attribute`、`old_value`/`new_value`、`old_quote`/`new_quote`、`source_id`、`old_conditions`/`new_conditions`。relation 为 `change`、`same`、`supplement`、`plan`、`unrelated` 或 `unknown`；独立 `supplement`/`plan` 可用空 unit_id。计划输出 `status=planned`。`missing_reasons` 会阻止该记录的动作；可用 `uncertainties` 提供其他具体未知，`preserve_history` 显式保留历史旧值。`unrelated` 只有明确 `no_impact_confirmed` 才可作为不影响旧项的输入。

条件用 `{"kind":"unconditional"}` 显式声明无额外条件，或用 `{"kind":"finite","dimensions":{"城市":["上海","南京"],"服务":["堂食","外带"]}}` 描述有限笛卡尔积；`{"kind":"same_as_old"}` 是新范围明确等于旧范围。没有条件、空结构或 `unknown` 不是全域。每个组合独立求交与差，最多 10000 组合；同值交集不改。有限条件维度不一致、未知剩余或不受支持的条件都暂缓。

精确日期区间、开放集合、自然语言条件归一化和语义蕴含不在此版本实现范围；日期可以作为已明确的离散条件值，但不能据对话时间猜测事实有效期。模型适配不将空限定词变成无条件，不从引文推断主体或值；因此 v3 对本接口通常会缺关键字段。不能仅凭引用有效、模型结构通过或本程序结果认定语义正确。条件过大、无来源、重复或互相冲突的证据均需要人工审查。

设计只借鉴 ERASE 的先判断后修订、FactTrack 的时间有效性意识及 Cedar 的条件交叠思路；未调用或复制其代码，亦未复用旧 part2_scope_planner。有限组合、校验和适配均为本目录新实现。
