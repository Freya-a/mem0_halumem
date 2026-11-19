# 组件一旧引文来源：独立提示实验与五例回归

## 结论与限制

**晋升例的引文来源错误在本次单次回放中消失，五例全部通过原有格式、来源和片段定位校验。** 旧 v2 同模型运行的晋升例未通过，其余四例通过；两次是针对已知错误设计的单次开发诊断，不能据此估算成功率或证明改进可泛化。**格式与逐字来源通过不等于语义正确**：所有关系标签、理由和问题仍须人工审核。职业历史例还出现了值得注意的新时间和身份前提风险，因此建议先保留本实验作为候选，不替换 v2；在其他已确认边界案例上固定提示并单独验证后再考虑采用。

## 晋升例：错误与修正

[原 v2 完整输入和输出](../qwen35_27b_q4_v2_20261110_v1/promotion.json)的旧记忆为 `Works at Historical Productions Ltd. as a Director`，该事实的 `source_type=memory` 引文相同；旧上下文 `source_type=context` 则为 `I work at Historical Productions Ltd. as a Director.`。原始模型把后者填入 `old_quote`，它确实来自给定旧上下文，但不是旧记忆引文。v2 先成功定位 `candidate_impact_fragment` 为 `as a Director`，再由原 `validate_candidate` 在本事实的 memory 引文中逐字查找 `old_quote`，因此返回 `old_quote not found in this fact memory evidence`；没有更改原文件或把结果当作成功。

[实验回放](promotion.json)原样输出 `old_quote: Works at Historical Productions Ltd. as a Director`，来自旧记忆，引文和片段均通过原 v2 校验。两轮晋升候选的差异只有 `old_quote`：关系均为 `possible_change`，候选片段均为 `as a Director`，新引文与理由也相同。这只说明本例输出来源被修正；不证明历史职称应被删除，也不确定实际晋升日期。

## 实验边界和可复核记录

- [实验判断器](experimental_judge.py)在原 `v2.SYSTEM` 后追加通用来源核对段：`old_quote` 从当前事实中 `source_type=memory` 且 `source_id=memory_id` 的 quote 逐字取非空连续文本；旧 context、`source_context` 和 `contextualized_subfact` 可用于理解，但不得冒充旧记忆引文。旧记忆不足以支持所需表述时应如实说明；没有合法引文不得编造或替换。新增段和完整 system prompt 分别保存在代码与 [system_prompt.txt](system_prompt.txt)。
- 六类关系标签、输出字段、v2 请求验证、JSON 解析、引文和片段校验均未修改。实验的 `judge` 直接引用 `relation_judge_v2.judge`；[实验后端](experimental_backend.py)是原本地后端副本，只将判断器模块引用指向实验版。未在解析前清洗或替换引文；若无 memory 来源，原请求验证在调用模型前返回 `input_error`。
- 现有模型文件重新计算 SHA-256 与先前一致：`84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806`；服务构建 `b1-78ffbaa`、上下文 4096、同一 GGUF Q4_K_M。五个输入及 user 消息与上轮逐字一致；system 消息只追加上述约束。两轮完成请求参数均为 `temperature=0`、`n_predict=768`、非流式，模板 `enable_thinking=false`；实际生成设置在各原始响应中。逐案先调用 `/apply-template`（不生成），再调用 `/completion` 一次（生成），没有自动重试。变更提示本身会影响整个输出，不能排除其他运行状态导致差异。
- [manifest.json](manifest.json)记录固定文件散列、提示散列和服务器版本；[inputs.json](inputs.json)、每例 `*.started.json` 和 `*.json` 保存输入、原始消息、渲染、请求、未改动的响应、解析/校验结果、实际调用数、耗时及显存采样。五次共 47.885 秒，均值约 9.58 秒，设备总显存采样峰值 17,530 MiB，含其他进程，采样可能漏掉短峰。以上不是性能基准。
- 离线契约测试覆盖：实验沿用 v2 validator；原晋升上下文引文仍被拒绝；替换为真实 memory 引文才通过；缺少 memory evidence 时不调用模型。本次没有修改拆分器、组件二，也没有写入 Mem0。

## 五例逐案对照

[机器可核对的字段差异](comparison.json)保留两轮候选及校验细节。这里的语义观察均为初步分析，**待人工审核**。

|案例|Qwen3.5 原 v2|实验版|引文、关系和理由观察|
|---|---|---|---|
|转岗|`possible_change`；通过|`possible_change`；通过|旧/新引文和候选片段均未变，仍区分已转岗与原求职状态。新输出从一个变成两个相近的求职问题，存在重复或追问范围过宽的风险；不能据此推断以后不再找工作。两版条件都写 Feb/Mar，日期是发言记录时间，不能直接当作转岗日期。|
|波斯猫|`supplement`；通过|`supplement`；通过|引文和 `historical charm` 片段未变；新理由更明确提到纪录片，但仍同时说支持旧喜好并新增养护考虑。v2 的 `support`/`supplement` 互斥定义不能自然表达“支持兼新增”，并未修复；所选第一条新引文自身不覆盖理由提及的另一条养护证据。|
|模拟跳伞|`uncertain`；通过|`uncertain`；通过|引文和旧片段未变，均区分模拟与真实活动并承认安全优先。新条件将现实活动与高风险连写，须避免把旧用户顾虑当作独立验证的客观风险；问题变动不证明当前真实跳伞态度。|
|职业历史／咨询公司|`uncertain`；通过|`uncertain`；通过|旧/新引文和片段未变，均未在理由中直接断言受雇于咨询公司。实验版 `conditions` 新写 `Time period prior to Jan 05, 2026`，但该日是新发言记录时间，不能据此确定旧职位结束边界；新问题中的 `while also running a consulting firm` 预设经营身份，`my consulting firm` 并不足以单独确定。相对原版，这是需复核的潜在退化。|
|晋升|`possible_change`；旧引文来源错误、未通过|`possible_change`；通过|旧引文由 context 原句变为 memory 原文，其余候选字段相同。雇主与 Director 历史应保留；候选片段不是更新指令。|

## 后续人工边界候选

[完整清单](HOLDOUT_INVENTORY.md)及 [结构化清单](holdout_inventory.json)基于冻结审核记录（LLM 辅助、用户确认事实与更新边界）。排除这五条目标 7、8、10、14、24，并额外排除与晋升同会话的 11 后，列出 18 条、11 个用户会话：13 条接受／修订后接受主目标、4 条重复确认对照、1 条归并项。它们不是 18 个独立实验，重复和归并项不得重复计数；第 15 条补充范围未固定，第 20 条是关联子目标。第 22 条另有既有原生运行定向确认，不是本实验标签。

清单只承诺未参与本次五例调整，不声称其他实验从未使用，也不把自动初标当人工确认；案例涉及同一批用户及共享会话，且有的曾出现在其他实验计划。后续先核实各自共同 before 的旧记忆和来源，再建立独立人工关系标签盲审，优先覆盖 memory/context 近义但不逐字相同、无足够旧记忆支持、时间边界、身份推断和支持兼新增；不要把 5/5 当作总体准确率。
