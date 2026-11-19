# 三类真实 Mem0 旧记忆：单次拆分测试与初步复核

日期：2026-11-03（Asia/Shanghai）。本次助手逐项复核，尚未经用户确认，不是人工标准答案。

三类均找到可靠更新前快照，未自拟记忆或 ID。每条 qwen-plus 调用 1 次，重试 0 次，合计 3 次；得到 1、2、4 条，共 7 条。格式、ID 和逐字引文均通过，19/19 条引文匹配。**语义初审仍发现关系遗漏、超范围上下文扩写、印象对象和 perceive 语气变化，不能将程序通过视为忠实拆分已获确认。**

完整机器检查见 [verification.json](verification.json)，来源链见 [provenance.json](provenance.json)，逐项初审及人工待确认项见 [manual_review.json](manual_review.json)。

## 选取与调用约束

从已有 Williams 原生开发运行 williams_native_prefix5_20261028_v3 中，只读目标会话 before 快照及更早的相关记录。各样本均核对真实 ID、旧文本、底层 payload、生成 ADD、生成后快照及前一会话 after；相关 20 个历史文件的 SHA-256 与原 checkpoint 保存值一致。这里的真实指已有真实 Mem0 原生运行落盘记录，本次没有连接 Mem0 读取在线状态。

静态检查 scripts/medium_dev_run.py：第 215 行保存 before，第 231 行才调用 memory.add；本次没有执行该脚本。三个样本来自同一开发用户的不同旧记忆、不同目标前快照，不代表总体效果评估。

只向模型发送各自选中的 ID、完整旧文本和生成会话的必要旧 user 发言节选。人工问题、原 checkpoint、目标定位 ID、来源风险说明、快照其余条目及本报告均没有进入模型输入。system 提示词完整复用现有 DESIGN.md。源码没有改动，没有安装依赖。

| 样本 | 旧快照 | 真实 memory_id | 调用/重试 | 子事实 | 引文 |
| --- | --- | --- | --- | --- | --- |
| 1：多人物 | session_009/before.json /api_snapshot/results/59 | 93d9e572-f052-41b6-9387-9e7583b8c3ab | 1 / 0 | 1 | 3/3 |
| 2：时间或状态变化 | session_007/before.json /api_snapshot/results/3 | 05b23c45-294e-402c-bcb9-d66ccbac6371 | 1 / 0 | 2 | 4/4 |
| 3：多个偏好及相关事实 | session_006/before.json /api_snapshot/results/54 | aa764342-2fe6-4632-9efd-e5e0cc032185 | 1 / 0 | 4 | 12/12 |

## 样本 1：多人物

ID：`93d9e572-f052-41b6-9387-9e7583b8c3ab`。来源：[session_009/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json:542)，位置 `/api_snapshot/results/59`。

旧记忆原文：

> Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition

以下是模型实际输出，未人工修补：

| 序号 | raw_subfact | contextualized_subfact |
| --- | --- | --- |
| 1 | Susan, Daniel, and Joshua provided instrumental support during the user's career transition. | Susan, Daniel, and Joshua provided instrumental support during the user's career transition; the user described their support as 'invaluable' and said it helped them 'see things differently'. |

程序：格式、ID、原文、来源编号及逐字引文检查通过，3/3 匹配；原始响应离线复核与保存结果一致。

初审：保留三个人名、支持行为及职业转变期间这一范围；遗漏朋友和同事关系，并加入了有旧来源的评价及效果。

- **人物**：Susan、Daniel、Joshua 均保留，没有交换姓名，也未擅自给每个人分配朋友或同事身份；但 Friends and colleagues 这一组关系描述从 raw 和补充版本中均消失，只有 evidence.quote 保留，事实文本仍有遗漏。
- **主语与受益人**：raw 增补 the user's career transition。旧文本没有显式写出受益人；旧 user 发言中的 my friends and colleagues、I received、helped me 为上下文版本归到同一发言者提供依据。raw 是否允许这样借助上下文明确受益人，仍需确认。
- **时间**：保留过去式 provided 和 during career transition，没有添加日期或永久持续断言。
- **条件、否定与情态**：原文无显式条件或否定句。instrumental support 的强度保留，没有把支持改成计划或可能；保留三人合述，没有强拆成三人各自独立完成整个支持过程。
- **语气**：核心支持行为仍直接陈述，没有改成用户认为或用户感到三人提供了支持；新增的 user described、said 用来引入原文没有的上下文评价及效果。
- **引文支持边界**：invaluable 和 see things differently 确实出现在允许的旧上下文中，但不是理解原命题所必需的指代、时间等补充；有来源不等于符合本次最小补充范围。

**待人工确认**：

1. 事实文本遗漏朋友和同事这一组关系描述是否判为必须修正的漏项。
2. 是否允许补充版本加入有来源但原记忆没有的支持评价及效果。
3. raw 中增补 the user's 是否超出仅依据 memory_text 的要求。
4. 输入没有提供三人各自属于朋友还是同事的明确映射；需要逐人关系时须另找可靠旧来源，不能自行分配。

模型自身待确认项：0 项（按每条事实中的数组项计）。与上方助手初审的待确认项分别保留。完整上下文、逐条引文、模型待确认原文及来源说明见 [case_1_multi_person/SEMANTIC_REVIEW.md](case_1_multi_person/SEMANTIC_REVIEW.md)。

## 样本 2：时间或状态变化

ID：`05b23c45-294e-402c-bcb9-d66ccbac6371`。来源：[session_007/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json:38)，位置 `/api_snapshot/results/3`。

旧记忆原文：

> Expressed initial skepticism about integrating Golden Retriever preference into daily life, but now sees pets as sources of emotional support and stress relief

以下是模型实际输出，未人工修补：

| 序号 | raw_subfact | contextualized_subfact |
| --- | --- | --- |
| 1 | The speaker expressed initial skepticism about integrating their Golden Retriever preference into daily life. | The speaker expressed initial skepticism about integrating their preference for Golden Retrievers into daily life. |
| 2 | The speaker now sees pets as sources of emotional support and stress relief. | The speaker now sees pets as sources of emotional support and stress relief, consistent with their own prior statement that 'Pets can definitely provide emotional support, which is valuable' and their expressed optimism about using their Golden Retriever preference to help manage stress. |

程序：格式、ID、原文、来源编号及逐字引文检查通过，4/4 匹配；原始响应离线复核与保存结果一致。

初审：raw 基本覆盖旧记忆两个阶段，保留 initial、now 和 sees 的态度范围；补充版本夹入来源对照说明，人物、时间及初始怀疑的直接来源仍需确认。

- **人物与主语**：使用泛称 The speaker，没有强行填入具体姓名；模型主动标记说话人身份及 their 与 user 的对应关系待确认。
- **时间与状态**：initial skepticism 和 now 均保留；没有擅自把 now 换成当前日期、Mem0 处理日期或固定发言日期，也没有声称怀疑已经完全消失。模型标记初始阶段的时间范围和 now 的锚点。
- **条件、否定与情态**：integrating preference 仍为怀疑对象，并未改成已经整合偏好、已经养犬或完成行为；原文无显式条件或直接否定句。
- **语气**：原文已经写 now sees pets as，因此保留 sees 属于保留原来的态度表述，不能算把直接陈述额外改成用户认为。contextualized 中的 consistent with 是新增的来源一致性说明，不是原命题必需的补充。
- **覆盖与扩写**：两个旧命题均保留。第 2 条补充版本加入此前原话和 integrating preference 帮助管理压力的乐观态度；这些有旧来源，但把来源比较和额外状态写入了子事实。
- **旧来源限制**：已检查的生成会话中，initial skepticism 主要由 assistant 回述，而非发现 user 的直接怀疑自述。旧 Mem0 文字真实存在不等于这段原始自述已获核实。本次不改写或纠正旧记忆，该来源问题另列待确认。

**待人工确认**：

1. initial skepticism 究竟对应哪个阶段、事件或日期。
2. now 的可靠时间锚点，以及是否需要在补充版本中保留记录时间与事件时间的区别。
3. The speaker、their 与来源 user 的指代对应；模型也已标记此项。
4. 是否接受第 2 条中的来源对照说明及额外乐观态度，还是应限定为必要的上下文补足。
5. 若要确认用户确实表达过初始怀疑，需要找到可靠的用户原话；现有 assistant 回述不单独证明此点。

模型自身待确认项：3 项（按每条事实中的数组项计）。与上方助手初审的待确认项分别保留。完整上下文、逐条引文、模型待确认原文及来源说明见 [case_2_time_state/SEMANTIC_REVIEW.md](case_2_time_state/SEMANTIC_REVIEW.md)。

## 样本 3：多个偏好及相关事实

ID：`aa764342-2fe6-4632-9efd-e5e0cc032185`。来源：[session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_006/before.json:497)，位置 `/api_snapshot/results/54`。

旧记忆原文：

> Recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career

以下是模型实际输出，未人工修补：

| 序号 | raw_subfact | contextualized_subfact |
| --- | --- | --- |
| 1 | Recently interacted with a friend's Golden Retriever and was impressed by its gentle nature. | The user recently spent time at a friend's house and interacted with their Golden Retriever, finding it gentle and impressive in its adaptability. |
| 2 | Values adaptability, calm demeanor, and emotional support in pets. | The user values adaptability in pets (as observed in the friend's Golden Retriever), calm demeanor (cited as crucial for their active lifestyle), and emotional support (described as invaluable). |
| 3 | Is drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals. | The user is drawn to Golden Retrievers because they perceive them as compatible with their active lifestyle (where calm demeanor is crucial) and wellness goals (implied by emphasis on balance, emotional support, and integration as a step toward new experiences). |
| 4 | Is optimistic about integrating this preference as a step toward new experiences and balancing demanding career. | The user is optimistic about integrating their preference for Golden Retrievers as a step toward new experiences and interactions, and as a means to achieve balance against a demanding career. |

程序：格式、ID、原文、来源编号及逐字引文检查通过，12/12 匹配；原始响应离线复核与保存结果一致。

初审：四条 raw 基本覆盖旧记忆四个分号段；上下文版本改变了印象所指特征，并出现 perceive 改写和 implied 推断，部分扩写虽然有旧引文仍超出必要补足。

- **人物与主语**：raw 大体保留省略主语，contextualized 增补 The user。ctx-1 中的 I、ctx-2 中的 I think、ctx-3 中的 I find，结合同一用户同一生成会话的 ID/ADD/快照链，为这一归属提供依据；没有单凭记忆所属用户默认主语，也未补入姓名。朋友仍是犬的主人，没有改成用户拥有 Golden Retriever。
- **时间**：Recently 保留，没有把原始发言时间 Jan 06, 2026 当成实际互动日期。recently 的精确时间范围未确定，模型没有主动标记。
- **条件、否定与情态**：原文无显式 if 条件或直接否定句。values、drawn to 和 optimistic 保留为偏好、吸引理由及乐观态度，没有改成已整合偏好或已实现职业平衡。
- **覆盖与粒度**：raw 保留相遇与温顺印象、三个受重视的特征、吸引理由、乐观态度与两个目标。第 2 条仍合并三个偏好，第 4 条仍合并两个目标，不能认定已是最细原子粒度。
- **语气**：第 3 条补充版本确实将直接给出的 compatibility 理由改为 because they perceive them as compatible。原句本身包含偏好态度，但新增 perceive 是否改变其中理由的断言力度，需用户确认；程序检查无法判定。
- **信息增加与变更**：第 1 条由 impressed by its gentle nature 改为 finding it gentle and impressive in its adaptability，印象的对象从温顺转到了适应性。来源 ctx-1 确有适应性印象，但不能静默替换原记忆的关系。第 3 条新增 wellness goals (implied by ...) 的解释；旧记忆已明确写 wellness goals，后面的推导并非必要。第 4 条增加 interactions，属于有旧来源但原文未明确展开的细节。
- **引文支持边界**：第 2 条 evidence 中的 supports 把 especially after a long day 解释为 post-work recovery，来源未明确说明下班或恢复；该推断只出现在 supports，不在主事实文本。第 3 条 supports 把 openness 与 wellness goals 对齐，也不由引文字面自动推出。

**待人工确认**：

1. 第 1 条补充版本把温顺印象转成适应性印象，是否判为语义改变；旧记忆和旧上下文在此处的差异也需保留为待确认。
2. 第 3 条 because they perceive them as compatible 是否允许作为原文 compatibility 理由的释义。
3. 第 3 条 implied by 及其 wellness goals 推导，以及第 2 条 supports 中 post-work recovery 的解释是否应排除。
4. 第 2 条三个偏好及第 4 条两个目标是否需要更细拆分；本次没有重新调用模型。
5. recently 的精确范围、是否接受朋友家和 interactions 等有来源的扩写，以及补充版本允许的最小范围。

模型自身待确认项：0 项（按每条事实中的数组项计）。与上方助手初审的待确认项分别保留。完整上下文、逐条引文、模型待确认原文及来源说明见 [case_3_compound_preferences/SEMANTIC_REVIEW.md](case_3_compound_preferences/SEMANTIC_REVIEW.md)。

## 共同边界与结果保护

三个样本没有明确的 if/unless 条件句或直接的 not 否定句；不能据此推断条件及否定范围的处理已经可靠。

主语补充方面：样本 1 的 user 受益人和样本 3 的 The user 有同一生成会话的第一人称 user 发言及 ID/ADD/快照链作为依据，不只是默认记忆所属人；样本 1 在 raw 中使用这种补充的边界仍待确认。样本 2 保留泛称 speaker 并主动标记指代不确定。没有补造人物姓名。

语气方面：样本 1 的支持行为没有改成用户认为；样本 2 原文已有 sees，保留它不算新增主观化；样本 3 第 3 条确实新增 perceive，须与原文直接给出的 compatibility 理由逐项确认。

68 个基线旧文件的 SHA-256 复核全部不变，包含使用的来源文件、现有实现和此前各次运行产物；新结果保存在本新目录。每条真实响应原样保留，检查失败或语义疑点均未触发纠错、重试或模型切换。没有输出 API 密钥或完整环境变量。

本次没有判断新旧事实关系，没有连接或修改 Mem0，没有知识库新增、更新或删除，也没有运行完整开发子集。只读取已有运行产物并执行这三次拆分请求及离线检查。
