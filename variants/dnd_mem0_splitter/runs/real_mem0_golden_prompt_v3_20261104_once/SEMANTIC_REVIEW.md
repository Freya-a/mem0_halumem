# v3 金毛旧记忆复测：程序检查与初步语义复核

日期：2026-11-04（Asia/Shanghai）。本次助手逐项初审，尚未经用户确认。

**本次通过 memory 引文检查。** qwen-plus 真实调用 1 次，重试 0 次，命令退出码 0，finish_reason=stop；返回 4 条事实，每条各有 1 项 memory，引文总计 4 项 memory + 7 项 context，11/11 逐字匹配。原响应直接通过现有校验器，没有自动补引文、改标或修补结果。

**语义初审仍有待确认项。** raw 和补充正文均保留“对温顺印象深刻”，正文没有 perceive 式改写或 companionship 扩写；第一条仍增加朋友家地点，部分 supports 对主体、指代和职业平衡的解释仍超出当前引文字面。原始自述来源没有全部确认。

## 最小修改与版本保留

仅修改 DESIGN.md 的引文规则 10、格式示例及对应版本说明，并加入完全自拟的教室地点消歧例子。v2 规则 1—9、11—13、原 JSON 字段结构和首版手写示例保持不变；Python 解析器、校验器、真实入口均未修改。

- [保留的 v2 提示词](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v2_targeted_20261103/prompt.txt)
- [完整 v2 设计备份](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v3_memory_example_20261104/parent_v2_DESIGN.md)
- [v3 提示词](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v3_memory_example_20261104/prompt.txt)
- [v2 到 v3 的逐行差异](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v3_memory_example_20261104/changes.diff)
- [版本及哈希](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v3_memory_example_20261104/revision.json)
- [自拟示例及离线验证记录](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v3_memory_example_20261104/synthetic_example.json)
- [提示词版本记录](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/PROMPT_CHANGELOG.md)

格式示例明确列出 source_type=memory，source_id 对应输入 memory_id，quote 为 memory_text 的非空逐字片段；context 仅在实际使用时追加，不能替代 memory。自拟例子的输入为“陈宁在那间教室练习书法。”，用独立来源消解教室地点，既有校验器离线验证通过。它不含本案例的人物、动物、真实 ID、事实或人工复核答案。

## 实际输入与可靠来源

真实 memory_id：`aa764342-2fe6-4632-9efd-e5e0cc032185`。

> Recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career

更新前快照：[session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_006/before.json:497)，JSON Pointer `/api_snapshot/results/54`。底层对应位置：`/database_points_with_vectors/54/payload/data`。

该记录在目标会话之前已经存在；原实际 ADD、生成后快照、前一会话 after 和目标 before 的 ID/文本对应关系沿用先前已核对的来源链，相关 checkpoint 哈希再次匹配。本次没有连接 Mem0 查询当前在线状态。来源字段见 [provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/provenance.json)。

真实数据输入与 v2 金毛案例 input.json 字节完全一致。没有加入后续新证据、人工标准答案、旧模型响应、额外助手回述或本次复核内容。

允许的旧上下文（全部保持原样）：

- `ctx-1`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/0/content [characters 0:169, zero-based, end exclusive]`，speaker=`user`，原始记录时间 `Jan 06, 2026, 17:48:59`。

> I recently spent some time at a friend's house and interacted with their Golden Retriever. It was such a gentle creature, and I found its adaptability really impressive.

- `ctx-2`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/2/content [characters 0:149, zero-based, end exclusive]`，speaker=`user`，原始记录时间 `Jan 06, 2026, 17:55:15`。

> Yes, the emotional support and companionship they offer are invaluable. I think this change reflects my openness to new experiences and interactions.

- `ctx-3`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/4/content [characters 0:128, zero-based, end exclusive]`，speaker=`user`，原始记录时间 `Jan 06, 2026, 17:59:17`。

> Absolutely, pets do offer that balance. I find their calm demeanor crucial for my active lifestyle, especially after a long day.

## 模型参数及请求限制

与 v2 显式参数一致：qwen-plus，generation_parameters={}，timeout=180 秒，response_format=json_object，SDK max_retries=0，HTTP 重定向关闭。未显式固定温度、token 上限或 seed。服务端默认采样值、具体模型修订未固定；历史端点值也不能只从配置路径独立确认，不能声称完全可复现。

本次仅启动一次真实入口：

```bash
python3 -B run_real.py --input runs/real_mem0_golden_prompt_v3_20261104_once/input.json --run-dir runs/real_mem0_golden_prompt_v3_20261104_once/model_run
```

请求记录、提示词和原始响应分别保存在 [attempt.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/model_run/attempt.json)、[prompt.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/model_run/prompt.txt)、[raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/model_run/raw_content.txt)。服务 token 记账为 prompt 2890、completion 1570、total 4460；它不是质量评分。未输出密钥或完整环境变量。

## 程序检查

| 项目 | v2 金毛案例 | 本次 v3 |
| --- | --- | --- |
| 真实调用 / 重试 | 1 / 0 | 1 / 0 |
| 原校验器 | missing_memory_evidence，拒绝 | 通过，退出码 0 |
| memory evidence | 四条都为 0 | 四条各 1 项 |
| context evidence | 8 项 | 7 项 |
| 引文逐字检查 | 仅另做 8/8 字面诊断，不能替代校验通过 | 11/11 经完整现有校验器通过 |
| result.json | 没有生成 | 已生成 |
| 引文补写或来源改标 | 没有 | 没有 |

检查覆盖严格 JSON、字段类型、连续序号、旧文本和 ID 对应、每条至少一项 memory、来源 ID 及逐字引文。离线将本次 raw_content.txt 交给现有 MockBackend 重放，与保存的 result.json 完全一致，未额外调用真实模型。38 项现有离线测试通过；自拟例子也经既有校验器验证。

详细机器记录见 [verification.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/verification.json)；程序不验证引文是否逻辑支持 supports、语义是否完整或补充是否必要。

## 实际事实与上下文版本

以下均从实际 result.json 原样读取，没有人工改写：

| 序号 | raw_subfact | contextualized_subfact |
| --- | --- | --- |
| 1 | Recently interacted with a friend's Golden Retriever and impressed by its gentle nature. | The user recently spent time at a friend's house and interacted with their Golden Retriever, and was impressed by its gentle nature. |
| 2 | Values adaptability, calm demeanor, and emotional support in pets. | The user values adaptability, calm demeanor, and emotional support in pets. |
| 3 | Drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals. | The user is drawn to Golden Retrievers because they are compatible with the user's active lifestyle and wellness goals. |
| 4 | Optimistic about integrating this preference as a step toward new experiences and balancing demanding career. | The user is optimistic about integrating a preference for Golden Retrievers as a step toward new experiences and balancing a demanding career. |

所有 source_memory_id 均为上述真实 ID。fact_index 是本次编号，不是新的 Mem0 ID。完整结果见 [model_run/result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/model_run/result.json)。

## 实际引文及 supports

下列每条引文都匹配其声明来源；memory 的 source_id 全部为 `aa764342-2fe6-4632-9efd-e5e0cc032185`，context 的 source_id 保持输入编号。所有 supports 也是模型原文，存在的语义疑点在下一节另列。

| 事实 | 来源 | quote | supports | 字符范围 |
| --- | --- | --- | --- | --- |
| 1 | memory / 原 memory_id | Recently interacted with a friend's Golden Retriever and impressed by its gentle nature | Old memory states the user recently interacted with a friend's Golden Retriever and was impressed by its gentle nature. | [0, 87) |
| 1 | context / ctx-1 | I recently spent some time at a friend's house and interacted with their Golden Retriever. It was such a gentle creature, and I found its adaptability really impressive. | Confirms the interaction occurred at a friend's house and that the user perceived the dog’s gentleness; 'gentle creature' directly supports 'gentle nature'. | [0, 169) |
| 2 | memory / 原 memory_id | values adaptability, calm demeanor, and emotional support in pets | Old memory explicitly states the user values these three attributes in pets. | [89, 154) |
| 2 | context / ctx-1 | I found its adaptability really impressive. | Supports that adaptability is valued, observed in the friend's Golden Retriever. | [126, 169) |
| 2 | context / ctx-2 | Yes, the emotional support and companionship they offer are invaluable. | Confirms emotional support is valued (‘invaluable’). | [0, 71) |
| 2 | context / ctx-3 | I find their calm demeanor crucial for my active lifestyle, especially after a long day. | Confirms calm demeanor is valued (‘crucial’). | [40, 128) |
| 3 | memory / 原 memory_id | drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals | Old memory states the user is drawn to Golden Retrievers specifically for compatibility with active lifestyle and wellness goals. | [156, 247) |
| 3 | context / ctx-3 | I find their calm demeanor crucial for my active lifestyle, especially after a long day. | Links Golden Retrievers (‘their’) and active lifestyle; confirms ‘active lifestyle’ is the user’s own. | [40, 128) |
| 4 | memory / 原 memory_id | optimistic about integrating this preference as a step toward new experiences and balancing demanding career | Old memory states the user is optimistic about integrating ‘this preference’ (i.e., preference for Golden Retrievers) as a step toward new experiences and balancing a demanding career. | [249, 357) |
| 4 | context / ctx-2 | Yes, the emotional support and companionship they offer are invaluable. I think this change reflects my openness to new experiences and interactions. | Confirms the user frames pet-related change as reflecting openness to new experiences; ‘this change’ aligns with integrating the preference. | [0, 149) |
| 4 | context / ctx-3 | Absolutely, pets do offer that balance. | Confirms pets are seen as offering balance — consistent with ‘balancing demanding career’. | [0, 39) |

## 本次助手语义初审

v3 四条均补回 memory evidence 并通过程序检查；raw 和补充正文均保留对温顺印象深刻的关系，正文不再加入 perceive 或 companionship。仍有朋友家地点扩写、单条 supports 的人物或指代归属过强、一般佐证以及原始自述来源未确认的问题。

| 用户关注项 | 本次观察 |
| --- | --- |
| memory 引文 | 已从原始响应确认四条各有 1 项 memory，source_id 对应输入 memory_id，quote 均为旧文本非空逐字片段；不是程序补写或从 context 改标。 |
| 温顺／适应性关系 | v3 第 1 条 raw 和 contextualized 都是 impressed by its gentle nature。适应性仍在第 2 条作为原文列举的宠物偏好，而没有替换第 1 条的印象对象。ctx-1 原话仍把 really impressive 连到 adaptability；这是旧记忆与旧来源表述的差别，不能据引文匹配认定两者完全等价。 |
| perceive | raw 和 contextualized 中没有 perceive 式兼容性改写，第 3 条直接保留兼容性理由。第 1 条 context supports 仍出现 perceived，用于描述来源中的温顺感知；不能声称这个词从所有字段消失。 |
| companionship | raw 和 contextualized 都没有加入 companionship；该词仍在按原样引用的 ctx-2 中出现，不能因此算新增了一个偏好事实。 |
| 不必要扩写 | 第 1 条仍加入 at a friend's house，虽然旧上下文有这段地点，但不是理解原子事实所需。其余三条正文相较 v2 明显收短，去掉括号评价、目标推导和 interactions。部分 context evidence 仍用于一般佐证，而非必要消歧。 |
| 原始说话人归属 | 互动行为可由同一旧生成会话的 ctx-1 中 I 与记忆事件对应到 user；这为补充主语提供实际依据。不能据此证明每项 Mem0 概括都由用户直接说过，尤其 wellness goals、乐观整合偏好及 demanding career 在允许节选中没有完整直接自述，原始发言归属仍需确认。 |
| 新遗漏或错误 | 未发现 raw 对旧记忆四个分号段的明显新增漏项，也未新增日期或已完成状态。但 memory supports 仍把原文未显式写出的主体称为 user，部分 context supports 继续超出当前引文；模型的第 4 条待确认理由偏重同句语法绑定，上文已有的偏好线索仍需纳入判断。 |

### 子事实 1

覆盖：互动、朋友的 Golden Retriever、最近及对温顺印象深刻均保留。

相较 v2：补充正文不再把印象对象替换为 adaptability。

剩余问题：

- `$.facts[0].contextualized_subfact`：保留 at a friend's house 这一有来源但非必要的地点扩写。
- `$.facts[0].evidence[0].supports`：单条 memory quote 没有显式 user 主语；该 supports 却说 Old memory states the user...。整体主语可借助旧上下文关联，但不能称是这条引文单独明示。
- `$.facts[0].evidence[1]`：引文明确描述 gentle creature，并把 really impressive 连到 adaptability。它可支持互动和温顺特征，不能单独确认用户直接说过 impressed by gentle nature；原关系由 memory quote 保留。

### 子事实 2

覆盖：adaptability、calm demeanor、emotional support 三个受重视属性均保留，仍合为一条。

相较 v2：正文不再加入 companionship，也没有 crucial/invaluable 等括号扩写。

剩余问题：

- `$.facts[1].evidence[0].supports`：Old memory explicitly states the user... 对 user 的明确归属强于当前 memory quote 的字面内容。
- `$.facts[1].evidence`：三条 context 引文主要用于确认这些属性受重视；其作为必要消歧的用途未完全说明，证据补充是否过量仍需确认。

### 子事实 3

覆盖：受 Golden Retrievers 吸引、active lifestyle 与 wellness goals 两项兼容性理由均保留。

相较 v2：删除 perceive 和 wellness goals 的额外机制推导。

剩余问题：

- `$.facts[2].evidence[0].supports`：memory quote 未显式写 user；人物归属不应只靠这条引文宣称。
- `$.facts[2].evidence[1].supports`：将 their 直接称为 Golden Retrievers 的指代偏强。该来源完整文本先写 pets，当前引文自身也没有明示品种；跨来源的关联需要区分于单条引文明确表达的范围。

### 子事实 4

覆盖：optimistic、整合偏好、新体验和繁忙职业的平衡目标保留，没有写成已经实现。

相较 v2：正文不再加入 interactions 或额外背景描写。

剩余问题：

- `$.facts[3].evidence[0].supports`：对 user 以及 this preference 的具体解释借用了单条引文之外的信息；若作为补足，应和 memory quote 单独直接支持的部分区分。
- `$.facts[3].evidence[2].supports`：pets offer balance 并不直接说明职业平衡；consistent with balancing demanding career 仍是跨来源的一般佐证，当前 context quote 没有 career。
- `$.facts[3].pending_confirmations[0]`：正文确定补为 Golden Retrievers，同时模型又标其范围不确定。该指代有旧记忆上文的实际线索，要求同句显式名词前项作为唯一依据偏严；最终是否保留确定表述或限定范围需人工确认。

| 维度 | 初步判断 |
| --- | --- |
| 人物与关系 | 朋友仍是犬的主人，没有改成用户拥有犬；未加入姓名。The user 的事件主语补足有旧第一人称来源依据，但所有原始发言是否都是用户直接自述仍未确认。 |
| 时间 | recently 保留，未换成当前日期、发言日期或 Mem0 处理日期；具体事件日期仍不明。 |
| 条件与否定 | 原文无显式条件或直接否定句，不能据本样本判断这类范围处理已经可靠。 |
| 情态与态度 | values、drawn to 和 optimistic 保留；没有推出实际养犬、已整合偏好或已实现职业平衡。 |
| 粒度 | 四个原文段落基本覆盖，三个偏好和两个目标仍各自合并，不是最细原子粒度的证明。 |

没有发现明确新增的 raw 核心漏项，不代表已经证明完全无遗漏；四条仍保留合并偏好和目标的粒度。本次是单次固定输入复测，不能证明改动必然造成这些差异或推断总体模型质量。

## 模型 pending_confirmations 与人工待确认

第 1—3 条模型均返回 []。第 4 条返回一项：

- **Whether 'this preference' unambiguously refers only to Golden Retrievers (and not broader pet preference)**：The memory uses 'this preference' without explicit antecedent noun phrase in the same sentence; while context strongly implies Golden Retrievers (via prior clauses and contextual utterances), the anaphor is not syntactically bound within the memory_text alone.

模型没有主动标记本次助手指出的原始自述来源及其他 supports 问题。以下是另行新增、未经用户确认的人工待确认项：

1. 原记忆的温顺印象关系与 ctx-1 的适应性印象表述之间，原始发言究竟如何表达；本次只忠实保留旧记忆，并未核实其现实真实性。
2. 是否应去掉第 1 条额外地点，以及不服务于消歧的一般 context 佐证。
3. 原始说话人或直接自述来源：互动可对到 user，但不能把每个 Mem0 概括都确认成用户原话；memory supports 中明确 user 的用语应进一步审查。
4. their 的品种范围、this preference 的指代范围，以及 supports 对职业平衡的跨来源解释。
5. 若下游需要绝对事件时间或更细粒度事实，当前结果仍需补充可靠来源或另行确定粒度。

逐项初审保存于 [manual_review.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_golden_prompt_v3_20261104_once/manual_review.json)，不修改模型原始响应。

## 文件保护与范围

本次开始时跟踪的 149 个已有文件中，147 个 SHA-256 不变；仅 DESIGN.md 和 PROMPT_CHANGELOG.md 按授权修改。完整 v2 设计已另存，其提示词归档和历史运行记录未变，版本记录中的原 v2 段落也保持原样。

本次不修改 Mem0，不写知识库，不执行新旧事实关系判断，不运行完整开发子集。没有自动补引文、把 context 改标为 memory 或为改善结果追加请求。
