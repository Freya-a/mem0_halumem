# FactTrack 源码检查与组件二初步设计

检查日期：2026-11-06（Asia/Shanghai）。范围：只静态阅读本地 FactTrack、组件一及本地模型的配置和既有记录；不读取 `evidence_temporal_judge/judge_v2.py`，未运行 Qwen、NLI 或 FactTrack，未安装、下载或调用云端 API。本文中的设计是供下一步讨论的建议，不是已实现的功能。

## 1. 仓库、版本和许可

项目内作者仓库为 [`../../external/FactTrack/`](../../external/FactTrack/)，绝对路径 `/home/shu1004/ld/system/mem0_halumem_diagnosis/external/FactTrack/`；`origin` 为 <https://github.com/cogito233/fact-track.git>，当前 HEAD 为 [`8b09d7fa5a805aa45a0d87a376d255665bd69460`](https://github.com/cogito233/fact-track/commit/8b09d7fa5a805aa45a0d87a376d255665bd69460)，提交时间 2024-07-03 15:34:51 UTC，提交信息 `init commit`。本次 `git status --porcelain=v1 --untracked-files=all --ignored` 无输出，作者仓库未修改。历史来源、论文及先前完整性检查详见仓库外的 [`FactTrack_PROVENANCE.md`](../../external/FactTrack_PROVENANCE.md)；论文脚注没有固定 commit，不能据此证明该 commit 与论文实验代码完全相同。

工作区还存在 `/home/shu1004/ld/external/FactTrack/`，没有 `.git`，无法独立由它确定来源和 commit。本次 `diff -qr --exclude=.git` 对两份目录无差异输出，说明比较时非 Git 文件内容和目录相同；以下行号均指项目内带 Git 元数据的仓库，不把无 Git 副本声称为独立可验证的克隆。

HEAD 中没有 `LICENSE`、`COPYING`、`NOTICE` 项目级许可文件，README 无项目级许可声明。仅 `fact-track/utils/llama_api_vLLM.py:1-2` 有 Meta 版权和 Llama 2 Community License 文件级声明，不能推广到整个仓库。既有来源记录称检查时 GitHub 元数据 `license: null`；本次未联网复核。**目前没有足够依据确认复制、改写或分发 FactTrack 代码的授权；复制或接入前应向权利人核实许可及第三方部分，不能因代码公开而假定可复制。**可以基于对公开机制的理解独立设计，但不能把这一描述当作法律许可结论。

`env.yml` 实际只有 `[y/N]: `，不是有效依赖清单；作者代码静态依赖和版本兼容性未被本次运行验证。即便未来确认授权，技术上也不能直接认为现有项目能运行其模块。

## 2. 程序位置和数据流

核心实现是 [`fact-track/core/contradict_detector.py`](../../external/FactTrack/fact-track/core/contradict_detector.py#L18) 的 `ContradictDetector_StatusPersistence`；三个指定函数均存在于这个类中。调度在 [`state_checker.py`](../../external/FactTrack/fact-track/core/state_checker.py#L47) 的 `OutlineItemStateChecker.fact_decompose/fact_check/fact_update`；故事时间坐标与遍历见 [`outline_detection.py`](../../external/FactTrack/fact-track/operation/outline_detection.py#L52)；Contriever 和 NLI 实现见 [`huggingface_api.py`](../../external/FactTrack/fact-track/utils/huggingface_api.py#L21)。

故事大纲由队列按层处理：根区间约 `[0,1]`，兄弟节点按顺序均分父区间，再用 `eps=1e-6` 分隔；先处理父层，再处理子层，处理顺序不等于简单故事时间顺序。每个情节由生成模型分解成事件前有效的 pre、事件后有效的 post、前后都有效的 static（[`fact_decompose`](../../external/FactTrack/fact-track/core/contradict_detector.py#L140)）。`OutlineItemStateChecker` 先对所有事实计算阻断后的候选区间，再逐条做矛盾检查，最后逐条插入；static 分别作为 pre 和 post 计算及插入，不能直接视为覆盖情节内部的单一区间。检测路径即使检查出错误也照样 `fact_update()`（`outline_detection.py:72-79`）。

有效状态保存在 `prefactList` 和 `postfactList`，每条实际为可变列表 `[fact, embedding, l, r, plot_idx, plot_text]`（`contradict_detector.py:454-476`；初始化处五元素注释过时）。pre 表示 `(l,r]`，锚点为右端 `r`；post 表示 `[l,r)`，锚点为左端 `l`。未阻断的边界分别初始化为 `-1e9`、`1e9`，并非真正无穷大；`epsilon=1e-6` 用于数值偏移。分解时 pre 以情节 `l` 为 base，post 以 `r` 为 base。`embedding` 由 Contriever 产生；索引和情节文本保存溯源。

## 3. 三个核心函数

以下说明是对当前源码的静态分析；默认值与调用方可能覆盖的值需区分。

### 3.1 `interval_blockCheck(fact, base, plot_idx, isPreFact=True)`

位置：[contradict_detector.py:314](../../external/FactTrack/fact-track/core/contradict_detector.py#L314)。

- **输入**：事实文本、锚点 `base`、情节 ID、方向；还读取对象中同类型事实列表、阈值和日志配置。
- **输出**：二元组 `(l, r)`；此函数计算候选边界，不直接插入事实或修改列表，但会记录部分比较日志。
- **逻辑**：先重置局部阈值并计算新事实 embedding。pre 从 `(-1e9, base]` 出发，把已有 pre 按其右锚点从近到远排序，仅考虑严格早于 `base` 的锚点；首次阻断即返回 `(旧右锚点 + epsilon, base)`。post 从 `[base, 1e9)` 出发，按已有 post 的左锚点由近到远，仅考虑严格晚于 `base` 的锚点；首次阻断返回 `(base, 旧左锚点 - epsilon)`。未阻断且 `is_query=False` 的候选按相似度倒序重新检查，最多 3 项，可能从该重查得到边界；都未阻断才返回初始范围。因此首次遍历偏向最近锚点，重查阶段按相似度排序，不能笼统保证最终总是最近阻断点；同锚点被严格不等式排除。
- **模型依赖**：每次先算 Contriever embedding；同类候选经 `block_check` 的余弦相似度筛选。相似度 `> same_threshold` 时仍调用一次 NLI，但直接返回阻断，即使 NLI 不表示矛盾；相似度 `< similarity_threshold` 时不调 NLI；中间区间调用 NLI，超过局部阈值后再依配置由 GPT 或 Hugging Face 阈值决定。默认 `model_name_contradict='gpt-4'` 会调用 OpenAI 判断；`gpt-3.5-turbo` 在 NLI `>0.9` 时短路，否则调用 OpenAI；`huggingface` 分支的阻断阈值是固定 `>0.8`。边界处等号以代码实际 `>` / `<` 为准。未触发云查询的候选重查可能重复计算 NLI。
- **其他依赖**：`block_check_reset`、`block_check`、`standardize_log`、`prefactList/postfactList`、`epsilon`；阈值默认 `similarity=0.5`、`nli=0.2359`、`same=0.95`，可被调用者覆盖。`block_check` 在部分云查询后会把局部 NLI 阈值倍增，重查前重置；日志只记录满足指定相似度和 NLI 条件的部分比较。

### 3.2 `interval_contradictCheck(fact, l, r, plot_idx, isPreFact=True)`

位置：[contradict_detector.py:376](../../external/FactTrack/fact-track/core/contradict_detector.py#L376)。

- **输入**：待检查事实及候选区间端点、情节 ID、方向；读取异类型事实列表。
- **输出**：`(flag, meta_info)`；`flag` 是是否发现至少一条矛盾，`meta_info` 只列判为矛盾的已有事实，包括 `fact`、`fact interval`、`plot`、`plot id`、`isPreFact`、`nli_score`。其中 `isPreFact` 取的是**当前输入事实**的方向，不是已有事实方向；没有矛盾时是空列表，不是注释所称的 `None`。
- **逻辑**：只比较相反方向：新 pre 对已有 post，新 post 对已有 pre。内部 `is_overlap` 只接受严格交叉：新 pre `(l,r]` 对旧 post `[l1,r1)` 要求 `l < l1 < r < r1`；新 post 则要求 `l1 < l < r1 < r`。相等端点、完全包含或相同区间等即使有数学上的共同点，也不会匹配。通过时间条件后算余弦相似度，低于阈值跳过；其余做 NLI，分数严格大于 NLI 阈值的候选按分数降序进入 `contradict_check`。循环条件是 `i > max_contradict_query`，默认值 5 实际最多处理下标 0–5 共 **6** 项，而非 5 项。最后收集判为矛盾的候选并记录比较。
- **模型依赖**：新事实 embedding 必算；重叠且相似度足够的每对候选调用 `huggingface_UnitContradictScore(新事实, 旧事实)`，把分数传给 `contradict_check`，后者不再重复推理。默认 GPT-4 对通过阈值的候选进一步云判断；GPT-3.5 在分数 `>0.9` 短路，否则云判断；`huggingface` 使用固定 `>0.2359` 的最终阈值（同时先经过可配置的 `self.nli_threshold`）。日志这里把 `is_query` 固定写为 True，不能据此证明一定调用了云模型。
- **其他依赖**：Contriever、NLI、可选 OpenAI、日志和类中阈值/事实存储。输出为空不证明事实相容：可能因方向、严格区间关系、相似度、阈值或候选上限而未检查到。

### 3.3 `interval_insert(fact, l, r, plot_idx, plot_text, isPreFact=True)`

位置：[contradict_detector.py:428](../../external/FactTrack/fact-track/core/contradict_detector.py#L428)。

- **输入**：新事实、已计算的区间、情节 ID 和原情节文本、方向；读取并修改同方向状态列表。
- **输出**：无显式返回，即 `None`；副作用是更新已有条目的端点、追加新事实及写比较日志。
- **逻辑**：先计算新事实 embedding。pre 按已有 pre 左端升序遍历，仅对 `旧r > 新r` 且 `旧l < 新r` 的项检查阻断；若阻断，将旧 `l` 改为 `新r + epsilon`。post 按旧 post 右端降序遍历，仅对 `旧l < 新l` 且 `旧r > 新l` 的项检查；若阻断，将旧 `r` 改为 `新l - epsilon`。依排序在不再符合范围时提前终止。插入新列表项后，对未云查询的候选按 **NLI 分数**降序再次检查，最多 3 项，成立时再次改旧端点。新事实追加不以是否发现矛盾为条件；更新仅针对同方向，不能等同于通用事实替换或自动写回 Mem0。
- **模型依赖**：和阻断函数一样走 `block_check`：新事实 Contriever embedding、候选相似度、依条件调用 NLI 及可选云判断；重查可能重复 NLI。高相似度即使不矛盾也可阻断并改变已有区间。
- **其他依赖**：可变列表、排序、阈值/局部状态、`epsilon` 和日志；没有事务、持久化或回滚接口。日志辅助，不是完整决策审计。

补充：同文件 `add_fact`（第 496 行）看似封装了以上流程，但其第 503 行调用 `interval_insert` 时未传必需的 `plot_text`，按当前签名会发生参数错误；`add_facts/add_plotDecomposition` 也经该路径。不能把这个便捷入口当成已验证可用接口。主要 `OutlineItemStateChecker.fact_update` 路径会传 `plot_text`。

## 4. NLI 和运行依赖的实际边界

作者 `huggingface_UnitContradictScore` 使用 `tokenizer_nli(fact1, fact2)`、模型 logits softmax，取标签顺序 `[entailment, neutral, contradiction]` 中 contradiction 分数（[`huggingface_api.py:65-82`](../../external/FactTrack/fact-track/utils/huggingface_api.py#L65)）；顺序为新事实作为 premise、已有事实作为 hypothesis。NLI 是有方向的模型评分，不能保证交换前后等价，也不等于真实时间矛盾。作者使用本地 `models/results_18k` 的**经微调**模型及 `facebook/contriever`，与本项目下载的 base NLI 不是同一个模型，不可直接沿用其阈值或分布。

这些作者模块不适合不加改造地导入：`contradict_detector.py` 读取 `BASE_PATH` 并导入 GPT 和 Hugging Face 工具；`gpt_api.py` 导入时以 `OPENAI_API_KEY` 创建客户端；`huggingface_api.py` 末尾导入即 `load_models()`，可能从网络获取 Contriever，找不到作者微调权重则报错。构造 detector 还初始化模型和写日志；`state_checker` 默认加载 rewrite 模型。依赖包括 PyTorch、Transformers、SciPy、pandas、OpenAI 客户端、Contriever 模型及作者 NLI 权重；`BASE_PATH` 拼接还依赖作者目录布局。以上是代码路径的静态判断，未验证实际环境或执行。

本项目本地模型为 [`model/DeBERTa-v3-base-mnli-fever-anli/`](model/DeBERTa-v3-base-mnli-fever-anli/)，本地 `config.json` 显示 ID 0 entailment、1 neutral、2 contradiction，模型卡标 `language: en`、`license: mit`。既有[下载核验记录](model/DeBERTa-v3-base-mnli-fever-anli.download-check.md)列出 revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` 及校验结果；这份先前记录最初的“未下载”段落已被后续“重新下载及核验”段落更新。模型卡的 MIT 声明仅针对该模型，不能授予 FactTrack 代码许可，模型及其依赖的适用条款仍应分别核实。

已有[离线英文小样本记录](runs/nli_offline_20261106_3fAnxn/REPORT.md)共 8 例中 6 例符合人工预期：一例不相关事实输出高 contradiction，一例不同年份的居住状态也误判 contradiction；该记录不代表中文性能或业务准确率。本次只读取记录，没有重跑。未来应先用目标语言、同一对象/属性/条件和带时间的标注样本单独评估，再决定是否使用及如何校准；保留三类分数、输入顺序、模型版本，NLI 只作辅助信号，不能单独关闭旧区间或替代事件时间推理。

## 5. 故事假设与对话记忆的差异

1. **时间坐标**：FactTrack 把故事树中兄弟顺序映射为可比较的相对坐标，默认为可沿时间前后传播；对话消息的记录顺序不等于所述事实发生顺序，可能回忆过去、谈未来或引用他人。“今天”还需要可追溯的时区和参照时间。未知端点不能写成已知无限延续。
2. **事实方向**：pre/post 是相对于明确故事事件的变化前后状态，static 是前后有效；普通陈述可能只是一次观察、历史更正、条件描述或计划，不能因为晚说就强制变成 post。新证据和旧记忆可能指同一历史时点，也可能没有可比时间。
3. **持续与阻断**：作者先假定向两端延伸，再由同类事实阻断，连高度相似事实也可阻断。对话里缺少结束证据时，既不能认定旧状态持续至今，也不能自动认定其在新对话时间结束。新状态确有时间也不代表它是旧状态的精确结束时刻；可能只有一个变更窗口。
4. **粒度和条件**：Mem0 一条旧记忆可含多个内容，人物、属性、适用条件、否定及范围可能不同；应以有来源的旧子事实/局部受影响片段为单位比较，保留同一记忆中未受影响部分。不同条件下看似相反的状态可能同时成立。
5. **边界与相交**：用户所述日期可能只有年/月、模糊范围或不确定顺序；需要显式开闭边界、精度和未知，不应继承 `1e-6` 与 `±1e9` 或严格交叉专用谓词。已知时间点相同与精度不足无法排除重叠应区分。
6. **矛盾和更正**：同一时段、同一对象属性条件下的互斥陈述才可能构成实质冲突；“历史记载有误”是修正主张，不等于状态变化。NLI/组件一错误、信息缺失和证据冲突均须显式保留，而不是伪装成无冲突或已更新。

例：旧记忆“2020 年住波士顿，也喜欢骑车”，新证据“2024 年住西雅图”。两条居住记录可先后为真，只能据证据表达两次观察及可能的变化窗口，不能指定 2020–2024 之间哪天搬家；骑车子事实不受这条证据自动影响。如果两条都只写“住在某地”而没有有效时间，先标未知/待确认，不能按对话时间截断旧记忆。

## 6. 组件二初步设计（建议，非最终协议）

### 与组件一衔接

[`relation_judge_v2.py`](part1_relation_judge/relation_judge_v2.py#L52) 对 `split_result.facts` 每项输出一行：顶层有 `status/results/errors`；行中有 `memory_id`、`fact_index`、`old_subfact`、`status`、`raw_output`、`candidate`、`located_candidate`、`fragment_match`、`validation`、`errors`。`located_candidate` 沿用组件一 schema：六种 `relation`（`support`、`possible_change`、`historical_correction`、`supplement`、`no_clear_impact`、`uncertain`）、`object/attribute/conditions`、`candidate_impact_fragment`、`old_quote`、带 `source_id/quote` 的 `new_quote`、`reason`、`confirmation_questions`。片段可能为空，或 `exact` 多处匹配且 start/end 为 null；不能把没有唯一偏移的片段当作唯一可写位置。校验检查结构、身份和引文来源，但 `semantic_correctness` 始终 `not_checked`，并未证明拆分、关系、对象或时间正确。

组件二应接收原请求上下文（`split_result`、新证据、可选 `source_context/time_info`，包括来源时间与其语义）及组件一完整结果，按 `(memory_id, fact_index)` 对齐，保留 `located_candidate` 与原文/溯源。不得把任意 `time_info` 假定为已解析事件时间；具体结构需在下一步定协议。每条独立检查 `row.status == 'ok'` 且 `validation.passed`，错误行产出 `upstream_error` 并保留原错误，不把失败当作 `no_clear_impact`；顶层 `partial_or_error` 下仍可处理合格行。`uncertain` 或实体、属性、条件不足的行保持不确定；其他标签均是候选提示而非可靠结论，尤其 `possible_change` 不等于旧状态失效，`historical_correction` 也须核验同一历史命题。

### 推荐处理流程

1. **时间证据标准化**：独立提取/接收旧、新事实的事件时间、观察时间和记录时间，分别记录原文、来源、精度、时区/参照及可信程度。每个端点显式区分 `known`、`unknown`、有证据支持的 `unbounded`；对相对时间缺失参照、粒度不明或解析冲突保留未知。不可将消息时间自动填为状态起止时间。
2. **候选边界与关系**：借鉴 FactTrack 的“基于同一属性候选寻找边界”的思想，但由对话证据约束；只在同一对象、属性、条件以及具有足够时间证据时提出边界，支持具体边界、边界窗口或未知。独立实现通用区间关系，至少区分先后、相交、包含、相等、端点接触和无法确定，并明确开闭与精度；无法可靠比较时返回 `unknown`，不将其视为不重叠。先用纯规则/已知字段判断时间，不用 NLI 推断时序。
3. **事实对检查**：先判断实体、属性、条件和事实粒度是否可比，再结合时间关系；有足够证据显示同一时段/条件相互排斥才提出冲突候选。局部英文 DeBERTa 可作为可选离线评分器，按显式指定的 premise/hypothesis 记录三类分数与版本；必要时两方向均保留但不假定分数对称。中文及时间场景性能待评估，冲突分数不是最终事实或时间判决。
4. **候选更新而非直接写入**：输出新事实候选与旧子事实边界变更建议，包含证据、推断理由、置信/不确定性及未满足条件；没有证据时给出 `unknown` 或待确认，不把新对话时间当旧事实结束点。更新建议需要独立的后续策略验证；本次不设 Mem0 写入机制。补充、支持、历史更正和可能变化分别保留，不把它们映射成同一种“替换”。

### 建议输入/输出轮廓

以下字段名、状态集合都是设计草案，不是现有代码承诺：

- 输入：原始 `request`（含 split、证据、上下文及原始时间）、`relation_result`、可选已知事实级时间证据和版本化已有状态快照；来源与记录时间分开。
- 每条输出：`memory_id`、`fact_index`、上游 `relation` 及验证状态；旧/新事实及其引用；旧/新时间证据及标准化结果；`temporal_relation`（含 `unknown`）；`semantic_signal`（可选 NLI 三分数、输入顺序和模型版本）；`assessment`（如 `compatible`、`possible_change`、`conflict_candidate`、`historical_correction_candidate`、`unknown`、`upstream_error`，精确定义待定）；`proposed_boundaries`（已知/窗口/未知、依据与开闭）、`proposed_updates`、`reason`、`confirmation_questions`、`errors`。模型未调用或失败要明确记录，不用零分代替。
- 示例：已知旧在 2020 年、新在 2024 年为不同住址且确认是同一属性，可输出先后观察和 `possible_change`；旧结束和新开始的精确时刻都仍未知，禁止填写“2024 年对话日”。当时间只知道先后而非完整有效范围时，应说观察先后，不能声称整个有效区间不相交。

### 复用边界与下一步

| 对象 | 初步判断 |
| --- | --- |
| FactTrack 作者函数及实现代码 | 许可和依赖均未核实到允许复制/直接接入的程度，当前不复制、不直接导入；授权明确后仍需重构副作用、依赖和语义，并逐函数审查。 |
| 先算候选边界、再比较、最后提出更新的思路 | 可作为独立设计的参考；不是声称源码已获得复制许可。 |
| 方向列表、严格交叉谓词、epsilon、默认无限延续、同类原地截断、现成阈值 | 不适用于直接套用；需为对话数据独立实现并验证。 |
| 组件一既有输出与引文定位 | 可作为上游接口使用，但状态、语义未验证、空片段和歧义偏移须保留。 |
| 已有本地 DeBERTa | 可考虑通过独立的离线可注入接口使用；模型卡标 MIT，具体许可与依赖分别核实，阈值和中文效果待目标数据评测。 |

下一步建议先写**组件二的数据契约与人工标注样例**：明确时间类型、端点/精度、事实粒度、未知状态、上下游错误传播和候选更新的证据条件，覆盖无时间、历史纠错、同刻冲突、先后观察、条件不同、复合记忆、边界接触及包含等情形；再据此实现独立的纯时间关系与候选边界逻辑，并用确定性样例验证，最后才评估并接入可选 NLI。是否获得作者代码许可及其依赖可用性是另行核实事项，不阻挡先整理数据契约。
