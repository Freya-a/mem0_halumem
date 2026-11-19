# judge_scope + 区间审查：独立组合版

`combined.py` 不修改、重写或写入记忆。`combine(request, split, new_evidence, scope_result, time_info, ...)` 消费同一旧记忆、同一份已经运行的 v4 拆分和 `judge_scope` 输出；检查拆分结构、记忆身份、来源及引文，保留 A 的完整原文和逐段候选。实际调用 `judge_v2._review_fact` 进行后续区间检查；这使用的是 v2 原有内部接口，不运行 FactTrack 作者仓库或作者 NLI。范围和新增候选的语义正确性仍未核验。

`judge_scope` 不输出 ERASE 或事实对时间方向。组合层不会由 `modify` 推断 `Make False`，也不会凭引文或分数生成 before/after。调用者可用 `pair_assessments={fact_index: {erase_label, temporal_relation, reason, provenance}}` 提供有明确来源的独立判断；不提供时标为 `not_provided` / `No Change` / `unclear`，其中 `No Change` 只是为旧接口填入的中性占位，不是模型判断。不注入 NLI 时使用 `uncertain` 占位，仅用于调用旧接口，不是 NLI 推理。旧接口本身处理单来源；多来源、未涉及、证据不足及范围判断失败分别有单独状态，后续区间步骤明确延后。

注入 `time_verifier` 和 `nli_backend` 时，必须传 `backend_provenance`，分别包含 `time_verifier` 或 `nli` 的 `kind`（`simulation`、`human`、`model`、`replay`）和 `source`；`kind=model` 还须 `model`。每次接口调用的输入、原始返回或错误类型、来源在 `evaluator_calls` 中记录，调用者负责对模型适配器配置、提示词、原始响应和调用次数进行持久化。模型调用不自动重试；模拟须标明 simulation，不是作者 NLI。

`time_info`、`time_verifier(payload)` 和 `nli_backend(payload)` 的实际格式及精度检查见 [README_V2.md](../README_V2.md)。时间声明需要旧事实或新来源的逐字引文、符合精度的日期文本和对事件归属的独立核验。记录日期不是事件日期；相对时间也不会被自动转换。组合结果的 `scope` 和 `final.scope_components` 原样保留 A，`temporal` 保存 v2 全部原始输出，包括它自己在时间不足时对动作的降级；`final.temporal_dependent_conclusions` 将依赖时间的部分单独标为待确认，避免旧 v2 的降级吞掉不依赖时间的范围候选。区间关系和调整均是候选，不证明事实失效。

`split_and_scope(...)` 为新运行显式使用 v1 的 `split_with_v4`，读取 `variants/dnd_mem0_splitter/prompt_versions/v4_boundaries_20261104/prompt.txt`，返回实际路径和文件字节 SHA-256，再运行 `judge_scope` 与组合层；拆分器默认入口没有改变。调用者传入真实后端时应在外部保存提示词、配置、请求、响应及调用日志；函数本身不写文件。复用拆分时必须由调用者像 `run_comparison.py` 一样先核对原始提示词哈希、拆分请求与响应、来源快照和各文件哈希；`combine` 不会仅凭传入内容声称它来自 v4。

复现：

```bash
cd system/mem0_halumem_diagnosis/variants/evidence_temporal_judge
python -m unittest discover -s scope_interval -p 'test_*.py' -v
python -m unittest discover -s . -p 'test_*.py' -v
python scope_interval/run_comparison.py runs/NEW_UNIQUE_DIRECTORY
python scope_interval/controlled_replay.py runs/NEW_UNIQUE_DIRECTORY/synthetic_controlled.json
python scope_interval/scan_dev_dates.py runs/NEW_UNIQUE_DIRECTORY/dev_date_scan.json
```

输出文件均排他创建，运行目录必须不存在。`controlled_replay.py` 的输入、范围判断、时间语义和 NLI 均为手写模拟，并不声称运行了 v4 或模型。
