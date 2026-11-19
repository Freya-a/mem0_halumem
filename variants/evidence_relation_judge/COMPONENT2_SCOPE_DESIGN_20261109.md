# 组件二第二部分：新旧事实失效范围判断器设计

日期：2026-11-09（Asia/Shanghai）。状态：设计提案，尚未实现或运行。本文基于本地 FactTrack 作者源码、[既有源码调研](FACTTRACK_COMPONENT2_RESEARCH_20261106.md)、[组件二第一部分](part1_relation_judge/relation_judge_v2.py)及其三个[已保存的受控案例](runs/controlled_v2_20261106/REPORT.md)。不使用 `evidence_temporal_judge/judge_v2.py`。本轮未更新 Mem0 数据、调用模型或运行完整开发子集。

## 1. 建议的路线与来源边界

建议采用“证据约束的范围规划器”：Qwen 产出带原文依据的语义候选，独立程序进行对象/属性/条件门控、时间关系计算、局部范围保护和候选动作编排；DeBERTa 是可关闭、需校准的辅助信号。最终先输出可审核的计划，不直接写入。另一种路线是直接导入作者类，改动较少，但其故事时序假设、隐藏的模型加载、云依赖、区间谓词和许可状态均不适合当前任务；纯提示词复核则无法独立约束边界和保护范围。

[FactTrack 论文](https://aclanthology.org/2025.naacl-long.144/)提出分解方向事实、推导有效区间、检查矛盾、插入和更新世界状态。项目内作者仓库为 `external/FactTrack`，origin 为 https://github.com/cogito233/fact-track.git；本次只读核对 HEAD 为 `8b09d7fa5a805aa45a0d87a376d255665bd69460`，`git status --short` 无输出。论文未固定 commit，不能声称其即论文实验版本。既有[来源与完整性记录](../../external/FactTrack_PROVENANCE.md)记载更严格的检查。

许可：该 commit 本地未见项目级 LICENSE/COPYING/NOTICE，README 无项目级许可；历史 GitHub 元数据检查为 `license: null`，仅 `llama_api_vLLM.py` 具有特定文件的 Meta/Llama 2 声明。本次网页可读[指定 commit 的 README](https://github.com/cogito233/fact-track/blob/8b09d7fa5a805aa45a0d87a376d255665bd69460/README.md)，但 GitHub API 本次未能访问，因此历史 `license: null` 未作当前复核，不能断言远端当前状态或远端 HEAD 与本地一致。应联系权利人核实复制、改写、分发权限及第三方资源；本文不是法律结论。

| 类别 | 本方案处理 |
|---|---|
| 直接复用或改写作者代码 | 当前**不复制、不导入、不改写**作者代码；获得明确许可并单独评估依赖前不进入该路径。未来如果获准，应逐文件登记版本、差异和许可。 |
| 参考机制重新实现 | 参考先找边界、再查冲突、最后插入的程序组织和状态追踪思想；独立设计对象、区间与证据协议，不声称逐行复刻。 |
| 本项目新增 | 子事实与原文映射、条件和范围保护、观察/记录/有效时间分离、不确定性、局部补丁与 Mem0 接口、审计和消融。现有 v2 及本项目 DeBERTa 是现有组件，并非 FactTrack 作者代码。 |

## 2. 原作者三函数：输入、输出和内部机制

来源均为 [contradict_detector.py](../../external/FactTrack/fact-track/core/contradict_detector.py)，静态阅读，没有运行。类存储的每项为 `[fact, embedding, l, r, plot_idx, plot_text]`；pre 区间 `(l,r]`、post 区间 `[l,r)`。作者先以大纲树生成的相对故事坐标计算情节时间，分解事实为 pre/post/static；static 分别按 pre/post 处理。对话顺序无法替代故事坐标。

### 2.1 `interval_blockCheck(fact, base, plot_idx, isPreFact=True)`

- **输入与依赖**：文本、故事锚点、情节 ID 和方向；还依赖同方向事实列表、Contriever、`block_check`、NLI、阈值、日志，某些配置调用 OpenAI。
- **输出**：`(l, r)`；只推导候选区间，不插入事实，但有日志副作用。
- **步骤**：pre 从 `(-1e9, base]` 向较早的已有 pre 锚点由近及远寻找阻断，返回 `(旧右端 + 1e-6, base)`；post 从 `[base, 1e9)` 向较晚 post 寻找，返回 `(base, 旧左端 - 1e-6)`。同锚点被严格不等式排除。首轮未云查询的候选再按相似度重查至多 3 项，因此最终结果不保证始终为最近阻断点。
- **判断细节**：`block_check` 先做 embedding 相似度筛选；相似度超过 `same_threshold` 即使 NLI 不显示矛盾也阻断；中间相似度才依据 NLI 及配置的 Hugging Face 或云模型判断。作者默认阈值和模型不适用于本项目的 DeBERTa。
- **适配作用**：参考其“从有来源的同属性候选查找边界”；不能继承其自动延伸、同义即截断、浮点 epsilon、无穷哨兵及最近即真实变化时刻。输出具体边界、边界窗口或未知，且不改原状态。

### 2.2 `interval_contradictCheck(fact, l, r, plot_idx, isPreFact=True)`

- **输入与依赖**：新事实、候选端点、情节 ID、方向；读取相反方向列表，依赖 embedding 相似度、NLI、可选 OpenAI、阈值和日志。
- **输出**：`(flag, meta_info)`；`meta_info` 为矛盾项列表，无结果为 `[]`。其中 `isPreFact` 是新事实的方向。
- **步骤**：仅比较新 pre 对旧 post 或反之。pre 时重叠谓词为 `l < old_l < r < old_r`，post 为 `old_l < l < old_r < r`；相等端点、包含等普通区间交集不符合谓词。通过时间筛选后计算相似度和 NLI，候选按 NLI 分数降序交给 `contradict_check`。默认 `max_contradict_query=5` 因 `i > max` 最多处理 6 项。
- **适配作用**：参考“先区间再语义复核”，但独立实现完整区间关系与未知状态，并加对象、属性、条件和互斥门控。无冲突输出不等于已证明相容。

### 2.3 `interval_insert(fact, l, r, plot_idx, plot_text, isPreFact=True)`

- **输入与依赖**：事实、区间、情节 ID、原情节文本、方向；读取并原地更改同方向列表，依赖 embedding、`block_check`、NLI、可选云模型、阈值及日志。
- **输出**：`None`；副作用是缩短被阻断的旧区间并追加新项，即使之前发现矛盾也追加。
- **步骤**：pre 按旧左端升序，满足旧右端大于新右端且旧左端小于新右端时判断阻断，成立则旧左端改为新右端加 epsilon；post 按旧右端降序，对跨越新左端的旧项判断，成立则旧右端改为新左端减 epsilon。然后追加新项，并按 NLI 分数重查至多 3 项。
- **适配作用**：参考“旧状态变更与新事实插入一起规划”；改为纯函数生成附前置条件的候选动作，之后由独立执行器批准/核验再写入，保留旧历史和证据。原函数既不是事务也不是通用 Mem0 替换。

补充：源码 `add_fact` 调用 `interval_insert` 时缺少 `plot_text`，不能作为已验证可运行接口。作者 `env.yml` 无有效依赖清单；导入相关模块可能立即加载模型、读取环境变量或创建云客户端。不得直接把 FactTrack 嵌进运行路径。

## 3. 输入、事实和时间模型

入口建议 `plan_scope(request, relation_result, *, nli=None, config) -> ScopePlan`。`request` 必须保留 v2 原请求的 `split_result`、全部 `new_evidence`、`source_context` 和原样 `time_info`；`relation_result` 是完整 v2 输出。按 `(memory_id, fact_index)` 唯一连接，校验重复、缺失、原文和证据来源；每行仅在 `status=ok` 且 `validation.passed=true` 时继续，`partial_or_error` 不使其他成功行失效。错误行返回 `upstream_error`；沿用 `pending_confirmations`。`semantic_correctness=not_checked` 明确保留，六类 relation 都只是提示，不得当真值。

设计候选结构（字段名为提案）：

```text
FactCandidate {
  fact_id, memory_id?, fact_index?, raw_text, proposition,
  subject {value, source_refs, status},
  object {value, source_refs, status},
  attribute {value, source_refs, status},
  value, polarity, modality, conditions[], granularity,
  source_refs[{source_id, quote, offsets?}],
  time: {valid_time, observation_time, recorded_at},
  inherited_uncertainties[], extraction_status
}
```

`subject`、事实的 `object`、活动对象和 `attribute` 分开；v2 的 `object` 在跳伞案例是活动而晋升案例是用户，不能不加解析就视为统一实体 ID。新证据分解为独立的原文支持命题，例如同一证据包含晋升和兴奋，不应将二者并成一个互斥岗位值。原始记忆、拆分事实及其引文始终保留；子事实内部可再识别属性单元和依赖，但分解可信度不足即待确认，禁止依靠字符串片段机械删除从属关系。

时间字段分别为：

```text
TimeEvidence {
  kind: event | valid_start | valid_end | valid_period | observation | recorded,
  expression, source_id, quote, reference_time?, reference_source?, timezone?,
  precision: instant | day | month | year | relative | unknown,
  resolved_range?: [earliest, latest], resolution: known | unresolved | conflicting
}
Endpoint {state: known | unknown | unbounded, value?, inclusive?, evidence[]}
Validity {start: Endpoint, end: Endpoint, basis: explicit | inferred | unknown}
```

`resolved_range` 是某个时间表达可能指向的**时间点范围**，不是事实贯穿该范围的有效期。一个表达可仅给出“发生在记录之前”的约束，不能给“recently”自定天数；记录时间的时间戳只证明记录时刻，观察时态只能作为有来源、需解释的观察线索，不自动成为状态开始或结束。只有来源及语义支持时解析相对时间；缺时区则不凭客户端时区补来源时区。`previously` 可以表达相对过去，但参照及边界不足则保留未定。无证据时为 `unknown`，`unbounded` 仅用于明确无限边界；不得以 `null`、±1e9 或当天冒充无限或已知边界。历史更正（同一历史命题的真伪修订）与状态变化（不同时间的状态）单独标识。

## 4. 具体数据流及函数职责

建议置于 `variants/evidence_relation_judge/` 下的新文件，不修改原作者目录：

1. `scope_contracts.py: align_inputs(request, relation_result)`：校验 ID、字面引用、唯一性和上游状态，保留原始输出；返回对齐行和显式错误。片段偏移按 Python Unicode 字符、半开 `[start,end)`；`exact` 多次命中即使 method 为 exact、start/end 为 null，也不能当唯一写位置。
2. `extract_scope_candidates(aligned_row, all_evidence, qwen_backend)`：Qwen 结合 v2 候选和全部来源，分别提取旧/新命题、对象、属性、条件、可能的细粒度片段和时间表达，每项给原文及 source ID；允许多来源；不支持项标未知。程序 `validate_provenance()` 验证每条引用存在且原文一致、span 属于旧事实证据；引用成立不证明语义成立。
3. `normalize_times(candidates, source_metadata)`：程序解析明确定义且无歧义的日期、精度、相对表达及锚点；Qwen 可提出表达类型但不得单凭模型补日期。冲突或缺少锚点保持未知。`compare_intervals(a,b)` 返回 `before/after/overlap/contains/contained_by/equal/touches/disjoint/unknown`，开闭端点单独判断；粗精度或端点不确定时仅在所有可能解释一致时给确定关系，否则 `unknown`。对点、空区间、开闭和跨时区须显式测试。
4. `assess_comparability(old, new)`：Qwen 提供对象共指、属性、条件、模态和互斥候选；规则校验其引文及字段完备性，仅返回 `comparable / different / unknown` 和证据。条件相同且同一时间并不自动意味着值互斥：须有互斥依据；无法辨识、粒度包含关系不清、模拟/真实未能区分均为 unknown。对显式已识别的不同对象、条件或历史/计划模态防止跨范围替换；未知不能默认为相同。
5. `propose_boundary(old, new, time_relation, comparability)`：借鉴 blockCheck 查找同对象、属性、条件的候选证据，但只根据明确结束、开始、变更或观察证据给 `exact / window / unknown / no_boundary`。若仅有更早旧观察和更晚新观察，在状态确有互斥且存在变化假设的前提下，可提出两个观察之间的**候选窗口**，不可断言只有一次变化或以新记录时刻截断。缺少依据时不制造窗口。
6. `check_conflict(old, new, comparison, time_relation, nli=None)`：仅对可比命题结合时间和互斥证据输出 `conflict_candidate / temporal_change_candidate / compatible_candidate / unknown`；不同时间的状态可先后为真，未知时间不等于不重叠。历史更正即使有更晚记录也不等于状态变更；直接纠正、同一历史命题及其作用范围须分别核验。
7. `plan_patches(old_memory, fact_units, boundary, checks)`：独立实现 insert 的“计划”阶段，返回四类互相可并存的动作；先处理保护和待确认，再提出局部修改与新增。不得仅凭 Qwen 整句 span、NLI 高分或消息时间制造写入许可。
8. `validate_plan(plan, original_memory)`：检查动作定位唯一、原文 hash/版本、保护与修改不冲突、依赖条件被完整保留、每个事实/时间有来源、没有未授权时态升级。无法定位或分解不可靠则 `pending`，不退化为整条 UPDATE/DELETE。保存原因码、所有候选、门控结果、模型版本和分数；不把未检查的候选记成兼容。

### 程序与模型的边界

Qwen3-8B 做自然语言命题提取、共指与属性候选、条件/范围及时间表达候选、解释和确认问题；其结果均为待校验结构。程序做来源字面校验、身份对齐、端点与区间计算、硬条件门控、冲突/保护检查和候选编排；程序能阻止缺字段导致的越界，但不能证明抽取或语义分类正确。可选 `score_nli(premise, hypothesis)` 对门控后的事实对保存三类 logits/softmax、方向、版本、语言及截断情况；可选双向分别记录。它只作为复核排序/分歧提示，不能独立关闭区间、覆盖规则或证明互斥。本地英文 DeBERTa revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` 在既有 8 例英文冒烟中 6 例与预期一致，含无关句和跨年状态误报；中文、领域、时间和阈值均待标注校准，不能使用作者微调模型阈值。

## 5. 候选动作与示例协议

```json
{
  "memory_id": "真实UUID", "memory_version": "原文哈希",
  "fact_index": 1, "plan_status": "needs_review",
  "patches": [{"kind":"modify_candidate", "span":{"start":null,"end":null},
    "old_text":"", "proposed_text":"", "conditions":["唯一定位", "语义范围已核验"],
    "time_effect":{"type":"unknown"}, "evidence_refs":[], "reason_codes":[]}],
  "protected": [{"text":"", "span":null, "reason":"未被新证据否定", "evidence_refs":[]}],
  "pending": [{"issue":"边界或范围未知", "question":"", "evidence_refs":[]}],
  "additions": [{"text":"有来源的新命题", "evidence_refs":[], "time":{}, "dedupe":"unchecked"}],
  "upstream": {"status":"ok", "semantic_correctness":"not_checked"},
  "audit": {"decisions":[], "nli":null}
}
```

以上是结构示意，空值不能满足实际写入前置条件。`modify_candidate` 可为片段替换、明确的历史限定或带证据的边界调整；新文本须保留主体、条件、否定、模态及旧记忆中不受影响的信息。`protected` 可是单元或不可安全切割的整个旧事实，不等于确认其永远为真。`pending` 同时承载拆分/关系错误和时间缺口；`additions` 先保留证据，再独立去重，不因为无法修改旧事实而丢弃新事实。多个新证据对同一旧片段冲突时合并计划并升级待确认，不以处理顺序覆盖。

## 6. 三个真实案例：预期行为及上游缺口

以下是设计期人工分析，不是程序已运行的结果；完整输入及一次性 v2 输出见[受控对照](runs/controlled_v2_20261106/REPORT.md)和 `runs/real_cases_20261106/*_input.json`。

| 案例 | 已有 v2 实际输出 | 本设计在抽取正确时应给出的计划 | 第一部分仍需改进 |
|---|---|---|---|
| 晋升 | `possible_change`，整句 `Works at Historical Productions Ltd. as a Director` 均被定位；理由称同公司职位变化。 | 把公司作为受保护的雇佣条件；`Director` 与 `lead director` 是岗位范围候选，新增有来源的晋升陈述；旧职位是否被替代、概念是否包含及精确变更时点待确认。旧上下文记录于 2025-09-05，新晋升消息记录于 2026-02-01，“recently”没有确定日期或时区，不能自动以新消息时间关闭旧状态。若可安全形成局部改写，也需保留公司和旧角色历史，并单独校验。 | 已定位整句不代表整句都受影响；需细分雇主/职位、论证新旧角色关系并保留“recently”的不确定性。 |
| 模拟跳伞 | `possible_change`，唯一定位整条旧事实；引用 dialogue-0，却在理由中声称仍重视安全，该依据实际来自 dialogue-8。 | 新增“体验模拟跳伞感到兴奋”“更愿意尝试新事物”（分别引用 dialogue-0、2）；安全优先引用 dialogue-8 并保护旧安全承诺。对真实极限运动的顾虑和风险判断保留，模拟与真实活动并不自动互斥；是否改变对真实跳伞的态度可待确认，不据此修改整句。 | 需正确区分模拟/真实、体验/一般偏好，覆盖全部相关引文，别重复询问已明确的安全陈述；拆分不足或 Qwen 分类错，程序无法保证自行识别。 |
| 职业历史 | `uncertain`，大小写唯一恢复后定位整句；理由和问题把 `my consulting firm` 升级为当前受雇/职位。 | 保护历史高级开发经历；记录旧上下文现在时与旧摘要 `previously` 的时间对齐未决。新增候选仅表达“其咨询公司获得初始客户”，保留关系和来源，不断言雇佣、所有权、职位或离开原公司；继续保留与之有关的待确认。 | `my` 不充分证明雇佣关系；需修复语义升级、问题前提及旧时间来源对齐。纯规则仅能拦住它显式标出的不确定性，不能保证识别所有错误。 |

## 7. Mem0 0.1.118 接入与执行边界

实际项目源码在 [mem0/memory/main.py](../../mem0_v0.1.118/mem0/memory/main.py#L310)。同步 `Memory.add` 对向量和图并行调用；`_add_to_vector_store(infer=True)` 先抽取新事实、逐项 top-5 检索并去重旧记忆，再将真实 UUID 临时映射为数字，调用 `get_update_memory_messages` 得到 ADD/UPDATE/DELETE/NONE，最后逐项执行 `_create_memory/_update_memory/_delete_memory`。`infer=False` 是直接添加路径；procedural memory 和 async 有各自路径。现有执行过程逐条捕错，不提供跨动作原子事务。

建议先在隔离 variant 做 **shadow 模式**：在检索去重后保留真实 ID、完整原消息及来源，先拆旧记忆，再运行 v2 与 `plan_scope`；同时保留原版计划供只读对照，不执行 shadow 动作。另一种插入位置是原版模型计划生成之后、动作循环之前：将 UPDATE/DELETE 映射回真实 UUID 并经范围计划复核，ADD 单独检查来源和去重；必须避免把临时数字当真实 UUID，也不能只靠抽取后的新事实而丢失原证据。两种位置可组合：前者准备候选，后者作为唯一写前闸门。

未来允许实际执行前，执行器必须重新读取旧文并比较原文 hash/版本，冲突重算；验证 memory ID 属于本次用户过滤范围，检查多个动作相互冲突，重组完整旧记忆而不丢受保护信息，更新 embedding 和 history，并将计划、结果、失败和幂等键持久化。Mem0 现有逐动作调用并不天然原子；跨向量库、SQLite history、图数据库的事务、失败补偿和并发语义须另设计，不能声称已有原子提交。若 `enable_graph=True`，原版 `add` 并行图写不经过向量写闸门；实验先禁用图，未来要单独接入或统一编排。同步/异步、`infer=False`、直接公开 update/delete 及 procedural 分支必须明确是否在保护范围内；未接入的路径不能声称受保护。

## 8. 评测与对照设计

先建立人工标注小型挑战集及逐例审计，再讨论完整开发子集；本轮均未运行。锁定用户、会话、历史前缀、真实对话、检索参数、模型及解码、时间元数据、执行环境和标注版本；每组从互不共享的初始快照执行，或在相同冻结候选上做离线评估。离线候选相同可隔离判断器，端到端各组后续记忆不同则要另报检索/状态漂移；不得混为同一分母。确认是否允许写入时再单独执行。

| 组别 | 原生 Mem0 | 普通复核 | 时间规则 | 范围保护 | NLI |
|---|---|---|---|---|---|
| A | 原版 infer=True，原计划直接执行 | 无 | 无 | 无 | 无 |
| B | 相同检索和原计划 | Qwen 按相同输入输出复核决定，记录调用量 | 无 | 无 | 无 |
| C | 相同 | 同 B | 开 | 关 | 关 |
| D | 相同 | 同 B | 开 | 开 | 关 |
| E | 相同 | 同 B | 开 | 开 | 开（校准后辅助） |
| F | 相同 | 同 B | 关 | 开 | 关 |

`D-C` 测范围保护，`D-F` 测时间判断，`E-D` 测 NLI 增益，`B-A` 测普通复核；这不是完整因子设计，若要检验交互还需其他组合。固定除目标开关外的提示词、阈值和策略；关闭某项时显式记录未评估，不能将未知伪装成通过。统一最基本的 ID、引用和安全校验；为研究语义范围保护关闭时，用隔离副本和人工标注比较候选，不在真实记忆上执行不安全计划。

标注单位为旧子事实、可影响/保护的属性片段、新增命题及时间关系，另有跨事实依赖。报告过度修改/遗漏更新、保护召回与错误保护、受影响范围精确率/召回率、时间关系和未知识别、待确认率及其正确率、支持的新增事实召回、历史保留、语义增编、端到端任务指标、模型调用次数和延迟。给出分母、不可定位/上游失败率，按用户和案例类型分层及成对误差；置信区间按用户/会话聚类，样本不足只报告描述性结果。别用三个案例推断总体效果。事先以与测试集分离的数据校准 NLI 阈值，记录中文和英文分别表现；NLI 不具备越过保护门控的权力。

最小验证集包括：相同端点的开闭、相交/包含/相等/不相交、日期粒度重叠及未知、相对时间无锚点、历史更正与状态变化、同义重复、非互斥多值、条件差异、同原文多次出现、上游 partial error、旧文版本变化、跨片段依赖及上述三例；为每个断言预期动作与不应发生的动作。只在实现后运行这些小规模验证。
