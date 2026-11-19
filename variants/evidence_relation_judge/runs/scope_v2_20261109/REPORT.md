# 组件二第二部分：局部范围候选与验证

2026-11-09。输出均为**待审核候选**，没有对 Mem0 写入，也没有运行完整开发子集。本报告将真实模型输出、程序实际输出、人工预期分别标出；来源字符串匹配不证明语义解释正确。

## 输入检查：子事实不等于字段

三个已保存输入的 v4 `split_result.facts` 都只有一个子事实：

| 案例 | 旧记忆及 v4 拆分结果 | 仍在同一句中的内容 |
|---|---|---|
| 晋升 | `Works at Historical Productions Ltd. as a Director`；唯一子事实原文与整条记忆相同 | 雇主和职位。v2 的影响片段也是整句。 |
| 模拟跳伞 | `Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being`；唯一子事实原文与整条相同 | 活动态度、具体活动例子、伤害风险、原因与安全承诺。 |
| 职业历史 | `Previously worked as a senior developer in Blockchain Tech`；唯一子事实原文与整条相同 | 过去时、雇主和职位。v4 还记录旧摘要过去时与旧上下文当时现在时的对齐疑问。 |

上述 v4 是已拆分的子事实，但并不是已证实的对象/属性字段或安全补丁边界。完整输入与 v2 原始候选、引文、验证结果、错误在各输出的 `request` 和 `relation_result` 内。

## 程序实现和约束

- `part2_scope_judge/scope_planner.py` 接受原请求、完整 v2 结果和可选抽取器/NLI，保留旧文、真实 ID、fact_index、原始上游错误、校验结果和所有证据。新增加 `scope_actions.py` 和 `scope_evidence.py`。
- 范围抽取可返回旧/新主体、对象、属性、值、条件、模态和互斥候选，并为每个字段及互斥候选提供 `source_id` 与原文引文；程序区分引文找到、缺失、无效。`literal_quote_verified` 仅表示字面出现在正确来源且旧字段属于该事实的证据，并不验证字段解释、蕴含或互斥。缺少字段引文不会生成冲突候选。
- 给相同对象/属性/条件的候选赋予明确的相交或先后时间以及有引文的互斥候选时，程序可生成 `conflict_candidate` 或 `temporal_change_candidate`；它们的语义均为未核验并带前提条件，最终关系仍为 unknown。NLI 没有写入这些判定的条件。
- 明确更正路径目前只识别一类很窄的英文直接结构：旧事实含独立的 `My <attribute> is <old>.` 或分号结尾子句，新 user 来源明确写 `Correction: my <attribute> is <new>, not <old>.`。须对应 v4 事实、完整旧引文及唯一定位，并通过 v2 上游校验。程序给出旧值字符 span、新值、旧新来源、原文哈希和未知时间，保护前后原文；语义、指代、条件和依赖仍需人审。多个值冲突、多个位置、跨子事实或失败上游时不提出修改。此路径不涵盖所有明确自然语言更正，也不从 `possible_change` 或 NLI 自动替换。
- 模型提出的同文字对象/属性/条件，只有旧新两侧都给出来源、内容确在引文中、旧文内唯一定位时，才可形成局部 `protected_candidate`；原有整体保护不会因此自动撤销。原文余下内容与目标存在关联时仍需人审。
- 新增候选按**大小写敏感的完整文本**做空白规范化，允许去掉开头的 `Hey,` / `Hi,` / `Hello,` 后合并；不以普通子串或模型分数判断同义。逐事实及顶层均合并，同时保留各来源和原始/模型候选种类。语义相同但措辞不同的重复仍未解决。模型改写、引文仅覆盖部分新增候选时分别记录 `new_fact_semantics_unverified` 或 `new_fact_quote_partial`。
- 新事实引文可复用 v2 的唯一大小写恢复：保存原始模型引文、恢复方式和恢复后源文；多处候选或找不到时保留错误。语义仍未核验。字段引文不做该恢复，错误照实保留。
- 时间仍只处理有来源的 ISO 日精度 `valid_period` 候选；消息记录时间不变成失效时间、`recently` 等不被补成具体日期。候选的时间语义、时区、开放端点与不确定范围仍未完整解析。

## FactTrack：实际执行与改造边界

作者源码位置仍为 `external/FactTrack/fact-track/core/contradict_detector.py`；与 Git 检出 `8b09d7fa5a805aa45a0d87a376d255665bd69460` 的对应文件一致。此次完成后，Git 状态为空，顶层副本与检出逐文件比较无差异。

| 作者函数 | 真实运行路径 |
|---|---|
| `interval_blockCheck`（314 行） | 在提供有来源的有限区间时，运行原函数抽出的 pre 列表排序表达式；先后区间的候选窗口会消费该顺序作为门控。窗口仍明确以同对象、同条件、互斥、确有状态变化为待核验前提。 |
| `interval_contradictCheck`（376 行） | 对有限区间实际执行原函数嵌套的原始 `is_overlap`。严格交叉时它直接参与选择 `overlap` 分支；其他情况由新增的完整区间比较处理，覆盖包含、相等、端点。它不独自认定语义矛盾。 |
| `interval_insert`（428 行） | 运行原函数抽出的 pre 列表排序表达式并记录顺序；**目前只用于审计，尚未驱动业务修改或新增决策**。实际的只读局部候选和保护重组为本项目新代码。 |

三个完整原方法仍只在隔离探针和合成程序测试执行；并未在实际业务调用原类。原因包括故事 pre/post 方向、原地状态修改、embedding、原模型/阈值、epsilon 和无限哨兵不适合直接解释现实事实，且无来源时间时不能制造坐标。

三个真实案例均无有来源的事实有效区间，故上述原排序及谓词在这三例实际输出中为 `not_called`；不能声称原方法判定了它们。在 `synthetic_for_report.json` 的 **sourced_interval_overlap** 小样例中，原谓词实际返回 `original_pre_overlap=true`，程序走 `original_overlap_true`；在 **sourced_interval_sequential** 中，原 blockCheck 排序实际参与条件窗口的门控，窗口 2024-12-31 至 2025-01-01。两个样例的来源时间文本和 v2 候选是为了测试添加的，时间是否属于真实有效期和语义互斥均没有被证明。insert 排序在这两个例子仍仅记录，完整原方法仍属探针。

## 验证方法与模型记录

运行：

```bash
python -m unittest discover -s part1_relation_judge -p 'test*.py'
python -m unittest discover -s part2_scope_judge -p 'test*.py'
```

实际为 13 + 47 = **60 项通过**。它们是程序测试，不是语义准确率、标注评测或完整开发集结果。覆盖明确更正、上下文保护、同/跨子事实冲突、重复片段、引用、条件缺失、源时间、区间包含与相交、去重和失败路径。

三个案例再次从本地 Qwen3-8B 抽取字段与引文，每例各一次。跳伞第一次在 1,100 token 截断，留下解析错误；用紧凑引文提示重试一次，745 token 正常结束，但其中新事实引文将原文 `the` 写成 `The`，当时旧版引用校验报错。两次原始输出与失败分别保存在 `skydiving.json` 和 `skydiving_retry.json`；最终程序在 `final_checked/skydiving.json` 使用唯一大小写恢复处理新事实引文，字段引用的无效项仍原样报告，未当作通过。初次抽取运行期间代码有后续修改，因此初次输出内写入的代码哈希不能作为模型开始时的版本证据；最终 `replay_final.py` 对保存的模型原始文本进行离线回放，记录回放开始时的当前代码哈希，且前后哈希相等。回放没有新 Qwen 调用。

本轮**保留并回放上轮的真实 DeBERTa 输出**，不是本轮重新前向；回放时逐字核对输入一致。模型为本地 `DeBERTa-v3-base-mnli-fever-anli`，权重 SHA-256 `06d6fd89edd4f97816831626daafbdb0b029cf63bae8edc0bccab1d64e2e7707`，与历史下载核验的 revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` 对应；本轮未联网重验 revision。输入顺序是 **旧 contextualized_subfact 为 premise → v2 新引文为 hypothesis**；完整输入、logits、softmax、版本、截断及真实运行来源均在 `final_checked/*.json` 的 `nli` 中。分数只作审计。

## 真实案例：逐案结果与人工核对

### 晋升

- **输入/拆分**：旧记忆及 v4 子事实均为 `Works at Historical Productions Ltd. as a Director`；`dialogue-0`：`I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!`。旧上下文记录在 2025-09-05，新消息记录在 2026-02-01；它们是记录时间，`recently` 未解析为事件日期。
- **模型候选**：已保存 v2 为 `possible_change`，候选片段是旧句整句。本轮 Qwen 提取旧/新职位 `Director` / `lead director`，共同对象为公司，互斥 unknown，但 comparability 输出 `different`；程序的文字比较为 `same_scope_candidate`，两者分歧保留 pending。字段引文存在不证明职位解释或互斥正确。
- **程序实际输出**：[promotion.json](final_checked/promotion.json)：`modifications=[]`；保留整体旧事实并增加 `Historical Productions Ltd.` 的精确局部保护候选；晋升新证据和模型的同文本新增候选合并为 1 项，保留两类来源；关系与有效期 unknown。未调用 FactTrack 时间代码。
- **NLI**：premise `User works at Historical Productions Ltd. as a Director.` → hypothesis `I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!`；真实历史 softmax `entailment=0.001028, neutral=0.998747, contradiction=0.000225`。
- **人工核对**：保护雇主合理；`lead director` 是否替代、包含或升级 `Director`，以及准确时点均未证明。不产生职位替换是有意保留不确定性；程序尚不能自动证明职位层级或作历史改写。

### 模拟跳伞

- **输入/拆分**：旧事实是对极限运动、伤害风险及安全承诺的混合句。新来源 `dialogue-0` 为模拟跳伞并觉得刺激，`dialogue-2` 为更愿尝试新事物，`dialogue-8` 为仍优先安全。消息记录时间不表示态度变化时间。
- **模型候选**：v2 为 `possible_change` 并定位旧整句，所引用的新句仅 `dialogue-0`，而理由中安全信息来自 `dialogue-8`。重试 Qwen 区分 simulated skydiving 和原极限运动，但把旧伤害风险/安全放进 value；仅部分字段给引用。它提出的三个新增命题全部为原句或近原句。
- **程序实际输出**：[skydiving.json](final_checked/skydiving.json)：没有局部修改；旧事实整体保护，三条原始新证据和抽取候选合并为 3 项；关系/有效期 unknown。`dialogue-2` 新事实引文唯一大小写恢复，字段 subject 的错误引文没有恢复并列为 `field_evidence_invalid`；部分引文只覆盖候选文本的一部分，也列入 pending。未调用 FactTrack 时间代码。
- **NLI**：premise `User dislikes extreme sports (e.g., skydiving) due to high injury risk, which conflicts with their commitment to safety and well-being.` → v2 `dialogue-0` 完整引文；真实历史 softmax `0.002221 / 0.861620 / 0.136158`（entailment / neutral / contradiction）。未比较 `dialogue-2` 或 `dialogue-8`。
- **人工核对**：模拟体验不直接推翻真实极限运动顾虑；安全陈述有 `dialogue-8` 来源。当前程序没有自动切分并保护安全部分，也没有消除 v2 关于安全是否保持的重复问题，仍需确认真实活动态度。

### 职业历史

- **输入/拆分**：旧事实 `Previously worked as a senior developer in Blockchain Tech`；旧上下文为 `I work at Blockchain Tech as a senior developer.`；新 `dialogue-0` 说 `my consulting firm` 获得初始客户。v4 已标明旧摘要过去时和旧上下文现在时的对齐不明。
- **模型候选**：已保存 v2 为 `uncertain`，大小写唯一恢复后定位整句；其理由和问题包含当前受雇咨询公司的无依据前提。本轮 Qwen 虽把新 value 写成 `secured initial clients`，却仍将新 attribute 写作 `employment`，理由仍称当前受雇；新证据不充分支持该解释。引文找到并未证明这个字段的含义。
- **程序实际输出**：[career_history.json](final_checked/career_history.json)：无修改，整体保护旧事实，保留 v4 原时间对齐问题和 v2 未验证问题；原始新证据与同文本候选合并为 1 项；关系/有效期 unknown。未调用 FactTrack 时间代码。
- **NLI**：premise `User previously worked as a senior developer in Blockchain Tech` → hypothesis `I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.`；真实历史 softmax `0.001703 / 0.997842 / 0.000455`。
- **人工核对**：新证据支持“my consulting firm 取得初始客户”的说法，但不足以确定雇佣、职位、所有权或离开原公司。程序没有自动识别该 Qwen/v2 语义升级，也未清理包含错误前提的问题。

## 人工构造的小样例：预期与程序实际

完整输入、人工预期、实际输出见 [synthetic_for_report.json](synthetic_for_report.json)。前五个是手写 v4/v2 形状的接口数据，ID 为 `synthetic-memory-1`，其中 v2 候选**不是模型调用**，NLI 禁用；时间例是在保存的晋升输入及 v2 结果上人工添加的有来源时间语句，亦非真实业务时间。下表不是模型评测。

| 手工核对的场景 | 预期 | 实际 |
|---|---|---|
| `My favorite color is blue; I enjoy hiking.`，新证据 `Correction: my favorite color is green, not blue.` | 只提出 `blue → green` 候选，保护 hiking，失效时间未知 | 1 个修改候选，span `[21,25)`，原文及更正有来源；其余两段保护，`time_effect=unknown`，状态 needs_review。 |
| 新证据只是 `My favorite color is green now.` | 不强推旧事实失效或具体修改 | 0 个修改候选。 |
| 两条明确更正分别说 green 和 red | 冲突、待确认 | 0 个修改，记录 `conflicting_corrections`。 |
| 旧句相同断言重复两次 | 未唯一定位 | 0 个修改。 |
| 两个来源给完全相同更正 | 只提出一个修改和一个新增候选，保留两个来源 | 1 个修改、1 个新增，保留 `new-1` 和 `new-2`。 |
| 来源给出交叉的两段有限时期 | 时间相交候选，语义待核验 | overlap，实际经过作者原谓词，0 个修改。 |
| 来源给出先后的两段有限时期 | 有条件的候选窗口，不自动失效 | before、条件窗口，实际使用作者排序，0 个修改。 |

## 仍需完成与风险

1. 局部修改只覆盖上述明确英文模板；一般汉语、普通“现在变了”、复合句、历史更正/状态变化与模态条件的泛化仍需有来源的抽取、语义核验和标注评估。模型引用正确也不能自动证明字段解释正确。
2. 目前会保护整个复杂子事实，少数同字面且有双侧引用的字段可额外给局部保护候选；不能普遍拆解依赖、生成保留上下文的自然语言改写，不能清理有错误前提的问题。
3. FactTrack 的 `interval_insert` 完整业务适配、原方法的真实案例调用、多个有来源边界候选的搜索与冲突处理尚未完成；现有 `interval_insert` 原排序仅为审计。完整方法用于合成隔离探针。
4. 仅做严格字面和少量问候语去重；语义重复、包含关系以及跨来源关系需校准。局部修改均为提案，需人工核对及未来执行器重新读原文、核验版本和跨动作依赖。
5. NLI 未校准；相对时间、时区、开放和粗粒度时间、冲突来源、非英语路径和端到端 Mem0 的写入闸门均未完成。此次无 Mem0 写入。
