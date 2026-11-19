# v2 来源、适配和验证记录

检查对象为本地 `external/FactTrack`，commit **`8b09d7fa5a805aa45a0d87a376d255665bd69460`**；ERASE 为 `b93f898780b3cf40fedd4e9a00c51af9a27688bc`。本次未改作者仓库。项目级许可证检查：FactTrack 未发现项目级 LICENSE 文件或 README 许可声明；`fact-track/utils/llama_api_vLLM.py` 有 Meta/Llama 2 的子组件版权与许可注记，不能据此推定整个仓库的许可。**复制、修改、后续公开的授权均未确认。**这里记录来源不是授权证明。

## 作者调用链和数据结构

`operation/outline_detection.py` 等构造 `OutlineItemStateChecker`，调用 `fact_decompose` → `fact_check` → 之后的 `fact_update`。`state_checker.py::fact_decompose` 首先调用 detector 的 `fact_decompose`，对 pre、post 分别以 plot 左、右坐标调用 `interval_blockCheck`，static 分别走两侧。检查阶段对每一段调用 `interval_contradictCheck`；更新阶段调用 `interval_insert`。detector 另有 `add_fact` 组合上述操作。检测器持有按 pre/post 区分的可变列表，每条近似 `[fact, embedding, l, r, plot_idx, plot_text]`，范围与相邻 plot 坐标相关，并非日历日期。

`fact_decompose` 用模型生成 pre/post/static 的编号文本并解析；异常时可能返回空列表。`interval_blockCheck` 在同类 pre/post 里沿方向查找第一个由相似度、NLI 和可选 GPT 判断的阻断点；pre 从 `(-1e9, base]`、post 从 `[base, 1e9)` 开始，用 `epsilon` 缩边。`interval_contradictCheck` 检索对侧 pre/post 列表，在源码的特定交叉排列满足 `l < l1 < r < r1`（或反向）时经 embedding、NLI 排序和 `contradict_check` 检查；它并非一般包含、相等和边界接触下的完整区间相交判断。`contradict_check` 使用 NLI 门限，并按配置再用 GPT 或作者 huggingface 阈值。`interval_insert` 再对同类历史条目缩区间并将新条目加入可变列表。`block_check` 的极高相似度也可成为阻断依据。模型阈值、故事坐标、列表顺序、检索近似和自动持久化都是与本项目不同的假设。

## 逐项来源和覆盖

所有 FactTrack 行使用上述 commit，文件均相对于 `external/FactTrack/`。**直接调用的 FactTrack 作者函数：无。**没有逐字复制或局部编辑作者函数体；提取的是下表注明的流程步骤和数据关系，并针对对话记忆重新实现。v1 直接调用本项目自己的 `split_memory` 和校验器，v2 直接调用本项目 v1 的 `split_with_v4`、`judge`、来源引文校验器；它们不是 FactTrack 作者代码。列出的测试均在 `test_judge_v2.py`，实际执行路径是 `judge_v2.py` 及本项目 v1/splitter，而不是作者函数。

| 作者文件和函数 | v2 提取的关键流程 / 修改原因 | 具体覆盖 |
|---|---|---|
| `fact-track/core/state_checker.py::fact_decompose`, `fact_check`, `fact_update` | 重新实现按事实依次确定范围、检查阻断、查冲突、提出调整的编排；旧事实由项目 v4 拆分，证据影响由 v1 逐事实判断。调整只输出，不调用 `fact_update`，不执行静态事实的两段自动持久化。 | `test_transition_adjustment_is_candidate_and_preserves_partial_fact` 检查完整适配路径及原始输入不变；`test_fact_backend_failure_preserves_fact_as_confirmation_candidate` 检查失败不冒充已运行的后续阶段。 |
| `fact-track/core/contradict_detector.py::fact_decompose` | 参考 pre/post/static 的状态概念；不采用其故事模型提示、编号解析、空结果回退或推测性陈述。用户已有 v4 事实、时间范围和显式转换声明；未知不能造时间。 | `test_transition_adjustment_is_candidate_and_preserves_partial_fact`、`test_missing_time_is_insufficient_not_a_processing_error`、`test_simulation_cannot_change_actual_state`。 |
| 同文件 `interval_blockCheck`, `block_check` | 重新实现按时间方向选最近有依据的阻断：`_block_check` 从指定事实、同一来源的真实日精度转换声明中，选旧起点之后最早阻断；以未知边界取代无限故事区间，不使用 embedding/同义性自动阻断。转换关联是调用者声明，仍需语义核验。 | `test_nearest_evidence_backed_blocker_is_a_fragment_candidate`、`test_transition_for_other_fact_does_not_adjust_this_fact`、`test_record_time_is_not_event_time_and_unknown_bounds_are_unknown`、`test_simulation_cannot_change_actual_state`。 |
| 同文件 `interval_contradictCheck` | 参考“先确定有效区间，再对潜在冲突事实做语义判断”，但 `_interval_relation` 使用带精度的日历边界，覆盖包含和接触；未知不作为无限。重叠仅是必要的时间条件，不单独判矛盾。 | `test_overlap_requires_semantic_conflict_and_evidence_impact`、`test_overlap_containment_and_boundary_touch`、`test_precision_ambiguity_and_invalid_dates`、`test_disjoint_historical_facts_retained`。 |
| 同文件 `contradict_check`；`fact-track/utils/huggingface_api.py::huggingface_UnitContradictScore` | 用 `_nli` 注入事实对结果，不复用作者分数阈值，不将分数直接作为已证伪；联合逐事实影响、实际活动和时间依据。失败与不确定不被当成无冲突。 | `test_nli_uncertain_failure_and_invalid_quotes_fail_closed`、`test_strong_nli_alone_cannot_propose_modification`、`test_overlap_requires_semantic_conflict_and_evidence_impact`。 |
| `contradict_detector.py::interval_insert` | 参考新状态可阻断旧状态的调整步骤，但 `_block_check` 与 `_review_fact` 只生成带来源、排他终点及被影响片段的候选；不写列表、不改已有事实、不同于作者 epsilon 修改。 | `test_transition_adjustment_is_candidate_and_preserves_partial_fact`、`test_nearest_evidence_backed_blocker_is_a_fragment_candidate`、`test_disjoint_historical_facts_retained`。 |
| ERASE `models/kb_model.py::KBModel.edit_retrieved_facts` | 直接复用本项目 v1 基于该流程做的逐事实影响判断和标签；没有调用 ERASE、自动改写或更新 KB。v2 将其未经时间验证的原意见保留为 `impact_judgment`，不足时降级 `modify`。 | `test_strong_nli_alone_cannot_propose_modification`、`test_fact_backend_failure_preserves_fact_as_confirmation_candidate`、`test_transition_adjustment_is_candidate_and_preserves_partial_fact`；v1 回归测试位于 `test_judge.py`。 |

## 不能直接调用的原因与 NLI 检查

`contradict_detector.py` 导入时读取 `BASE_PATH` 并导入 `gpt_api` 和 `huggingface_api`；`gpt_api` 在模块导入时创建依赖 `OPENAI_API_KEY` 的客户端，`huggingface_api` 在末尾立即 `load_models()`：Contriever 不存在时尝试从 Hugging Face 获取并保存，微调 NLI 不存在时抛异常。detector 初始化加载模型、创建或覆盖日志文件。区间函数本身也依赖 embeddings、全局模型、plot 坐标、可变列表和日志。直接导入/初始化违背本次禁止真实模型、下载及修改原仓库的约束，因而没有尝试执行有副作用的导入；这是源码与文件检查，不是完整运行时兼容性测试。

本地检查到 Python 环境中 `torch 2.9.1`、`transformers 4.44.2`、`scipy 1.13.1`、`pandas 2.2.3`、`openai 1.100.2` 的包元数据；未执行模型模块导入或验证所有依赖互相兼容。仓库下未见 `models/results_18k`、`models/contriever` 模型目录或 `.bin`/`.safetensors` 权重，README 将模型列为另行下载，`env.yml` 的内容不足以重建依赖。结论仅限本地检查路径，不能断言用户机器其他位置没有权重。**没有运行作者 NLI 模型，也没有下载权重。**

未来如用户单独授权并取得权重及许可，可在隔离进程配置 `BASE_PATH`、本地模型和依赖，禁用自动下载与导入副作用，检查作者 `huggingface_UnitContradictScore(fact1, fact2)` 的标签方向和输入顺序，并由外部包装器转换为 `{relation, score}` 注入 `nli_backend`。阈值和校准应通过真实 Mem0 数据另行验证；现有代码不会自动加载或把作者分数映射为真值。

## 已执行范围和未验证项

后续精度修正为 v2 增加 `time_checks`：分别记录旧/新状态边界及转换时间的引文归属、日期文本精度和外部 `time_verifier` 语义意见。该机制是本项目的保守适配，不调用 FactTrack 或 ERASE 作者函数。测试先复现了年份原文配日精度声明、旧起点精度错误、记录日期和相对时间被错误锚定，随后验证不足时不产生确定的日精度候选。明确日期的正例采用手写模拟语义意见；即使文字包含日期，程序也不能自行证明日期所属事件，外部意见仍需复核。缺省未注入评估器时，相关时间声明只作待确认。日期字面格式覆盖范围及多转换阻断的保守处理见 [README_V2.md](README_V2.md)。

`test_judge_v2.py` 全部使用手写事实、时间声明、影响结果与模拟 NLI；旧 v1 测试中的 OpenAI SDK 测试使用 `httpx.MockTransport`，不是远程请求。覆盖确定/未知边界、before/after/overlap、包含和接触、时间精度、历史保留、部分修改和同时保护、虚构与实际活动、记录时间分离、NLI 不确定/错误、逐事实 backend 错误、缺失来源/引文、最近阻断和不跨事实应用。测试的引用校验只是字面校验，构造的日期声明有些是为边界组合手写的，不代表引文已语义证明该日期；可运行示例使用带明确日期的合成来源。

未运行真实模型、作者 FactTrack 代码/权重、完整开发子集或真实 Mem0 案例；未检验真实拆分质量、日期归一化准确性、模型提示与 NLI 校准、跨多来源/多事实交互或与 Mem0 的存储集成。`path` 列表只跟踪进入的适配阶段，不代表作者函数执行。项目目录和作者仓库之外位置的模型缓存、许可证、依赖兼容性未穷举。
