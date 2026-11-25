# v3 离线范围规划与错误归因

本目录独立于 `../v2_offline`。它只读五次已保存的 v4 模型响应，不调用模型/API，不修改旧代码、旧运行结果或 Mem0。模型候选、独立审核和人工预期分别保存，模型的自我解释不是独立语义授权。

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_scope_planner/v3_offline
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python replay.py
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

`scope_planner.py` 提供 `build_scope_plan(old_memory, old_units, evidence_sources, alignments)`；输入保持 v2 的主体、属性、值、模态、引文及来源、显式语义审核与时间关系契约。新证据来源要有 `source_id`、`source_ref`、`side='new'`、`speaker='user'`。规划器对旧引文检查旧单元归属，并分别核验新旧引用在指定文本中的唯一位置；它没有 `new_units` 输入，无法自行核验新引文是否属于所关联的新单元，这项由 v4 适配器核验。`source_ref` 的实际文件指针和外部来源真实性依赖调用方的独立核对。独立语义审核必须显式提供 `semantic_support='supported'` 与已关联的新侧 `semantic_basis`；不能把模型 relation、模型自评、人工预期或字面命中当授权。发生变化还需明确 `modality='asserted'`、相对旧事实的时间先后及已绑定依据；没有具体日历日期不妨碍已证实的相对顺序，未知先后不能直接覆盖。

适用条件的三种状态不同：`{'kind':'unconditional'}` 断言没有额外限制，但不提供可枚举的全集；`{'kind':'unknown'}` 是范围未知；`{'kind':'finite','dimensions':...}` 表示给定维度上的完整有限笛卡尔积。`same_as_old` 仅在新侧明确等于旧范围时可用。旧完整有限积与新有限积按条件组合求交及差；对于明确无条件的旧范围和有限新范围，可计算有证据的有限交集，但域外剩余不能枚举，必须待确认。未知范围、维度不匹配、无独立证实的候选范围不能用于生成假定的剩余范围；若某处存在未经确认的冲突或引用问题，其他可确定的组合仍可分别处理。未知不是全部，无条件也不是一个已知有限全集。

`tests/test_paths.py` 使用独立构造的通用句子，不使用五案内容或预期：模型候选无独立授权时新增及修改均暂缓；随后仅加一项独立审核标志并保留原始字段，测试能分别新增“喜欢茶”、修改“之前关闭、现在开放”，后者无需具体日期。二维有限条件回归分别检查上海、南京 × 堂食、外带的 1 个修改和 3 个保留组合。

`replay.py` 从 `../../evidence_aligner/v4_scope_interface/runs/qwen_20261124_once/` 读取同一批保存的原始响应。未防护投影由 `frozen_at_call/interface.py` 构造，防护投影由 v4 当前 interface 构造；每组将完全相同的投影拷贝给 v2 与 v3，保留并核对输入哈希。未防护 v2 必须复现当时首次结果，防护后 v2 必须复现 `offline_safe` 结果。两组不能交叉比较：v4 防护会将旧规划器无法计算的条件变为 unknown，因此会遮住 v3 能处理的有限交集信息。`results/*.json` 保存全部计划、引文与哈希；`TRACE_17.md` 是防护后旧版 17 条待确认的逐项原因；`RANGE_REVIEW.json` 保存按计划哈希绑定的独立范围审核；`REPORT.md` 对照两代结果并区分接口、引文和语义审核。

统计是单次小样本的观察，不是正式准确率。明确无限定不代表适用于所有历史时刻；由模型给出的有限范围、主体、值和相对先后仍须独立审核。时间区间、无限域的精确差集以及自然语言蕴含不在本版本实现范围。

对一个复合 unit 中不同主体或属性的多条关系，当前实现可能把它们合并并保守标为值冲突，造成额外 `uncertain`；它没有完整的复合事实消歧能力。应先提供可可靠定位、按事实拆开的单元，或将结果交由人工复核，不能把额外待确认当作真实矛盾。
