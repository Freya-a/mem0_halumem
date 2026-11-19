# 提示词 v2：相同三条真实旧记忆的新旧对比

提示词调整和真实模型调用记录：2026-11-03（Asia/Shanghai）。中断后完成报告与最终核验：2026-11-04（Asia/Shanghai）。这次续接复用已保存的三次请求，新增真实模型调用 0 次。

**结论：本轮仅部分改善，不能认定调整已解决五类问题。** 多人物样本保留了朋友和同事关系，前两条补充正文收短；状态样本仍将未确认主体写成 user，金毛候选仍有关系变化和扩写，并因全部缺少 memory evidence 被程序拒绝。

程序状态：3 次真实请求，每条 1 次、重试 0 次；2 个样本通过、1 个失败。合计返回 7 条候选，仅前两样本的 3 条是通过程序校验的结果；金毛 4 条仅保存在 raw_content.txt，不存在有效 result.json。38 项现有离线测试通过，这不等于模型语义复测通过。

## 提示词改动及旧版保护

当前 [DESIGN.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/DESIGN.md) 的唯一 text 代码块为 v2_targeted_20261103。具体规则和实施选择见 [PROMPT_CHANGELOG.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/PROMPT_CHANGELOG.md)。原输出 JSON 结构、手写示例、Python 后端和校验器保持不变。

| 版本材料 | 位置 |
| --- | --- |
| 第一版完整设计 | [v1 DESIGN.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v1_original_20261103/DESIGN.md) |
| 原提示词 | [v1 prompt.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v1_original_20261103/prompt.txt) |
| 新提示词 | [v2 prompt.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v2_targeted_20261103/prompt.txt) |
| 逐行改动 | [changes.diff](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v2_targeted_20261103/changes.diff) |
| 版本与哈希 | [revision.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v2_targeted_20261103/revision.json) |

修改为通用约束：事实文本覆盖名单、身份与关系；raw 只恢复旧记忆内部共享成分；补充默认复制 raw，逐项检查消歧必要性；不替换动作或态度的对象、特征、原因，不额外主观化原文；supports 只说明当前引文直接支持的范围；区分记忆记载、直接自述和助手回述，不明则待确认。

新版系统提示词没有三条案例的人名、动物名称、ID、原文或期望拆分答案。旧次模型响应、人工复核、原助手回述说明和本报告均没有进入数据输入。

## 可比性和调用控制

三份新版 input.json 与旧次对应 input.json 字节完全一致，旧记忆、ID、source_context 及其角色、时间和 source_ref 都没有改变。相关 20 个历史来源文件仍匹配原 checkpoint 哈希。

| 控制项 | 核对结果 |
| --- | --- |
| 请求与返回模型 | 两版均为 qwen-plus |
| 显式生成参数 | 两版均为 {}；未显式指定温度、token 上限或 seed |
| 超时 | 两版均为 180 秒 |
| 输出格式 | 两版均为 json_object，结构未修改 |
| SDK 重试 / HTTP 重定向 | 两版均为 0 / 关闭 |
| 实际请求 | 每条 1 次，共 3 次，无重试、纠错或模型切换 |
| 无法确认 | 服务默认采样值、具体模型修订、旧次依赖版本锁；旧次未保存端点指纹，不能独立证明历史端点未变 |

各请求的 started_at、参数和 token 元信息保留在对应目录 attempt.json 与 response_metadata.json；token 数不是质量评分。[preflight.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/preflight.json) 记录逐项一致性和这些限制。

## 程序检查

| 样本 | 旧版 | 新版 | 新版原有校验器 / 字面诊断 |
| --- | --- | --- | --- |
| 多人物 | 通过，1 条 | 通过，1 条 | 通过，3/3 引文逐字匹配 |
| 时间或状态变化 | 通过，2 条 | 通过，2 条 | 通过，3/3 引文逐字匹配 |
| 多个偏好及相关事实 | 通过，4 条 | 失败，4 条未通过候选 | missing_memory_evidence；另做只读字面检查 8/8 匹配，整体仍失败 |

金毛样本四条候选全是 context evidence，没有任何 memory evidence。原校验器在 $.facts[0].evidence 拒绝；未修改候选，用 MockBackend 离线重放复现同一错误。没有补引文或生成替代 result.json。finish_reason=stop 且原始文本可解析为 JSON；为何模型忽略规则，单次样本无法确定。

前两条共 6 条引文通过完整现有校验器。金毛另有 8 条引文的只读字面匹配诊断，不能替代原程序通过。程序核验不证明 supports 的推断正确，也不证明补充必要或语义完整。详细机器记录见 [verification.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/verification.json)。

## 五项重点结果

| 重点 | 新旧对比结论 |
| --- | --- |
| 朋友和同事是否保留 | 多人物样本由旧版遗漏改善为新版 raw 和补充版本均保留，并新增群体关系范围待确认。 |
| 是否仍有不必要的上下文扩写 | 多人物和状态样本的额外评价及来源对照正文已去掉；金毛候选仍扩写地点、评价和目标解释，且第 2 条新增 companionship。 |
| 对温顺印象深刻的关系是否保持 | 金毛新旧 raw 均保持；新旧补充版本均将 impressed 的特征转向 adaptability，因此该问题未解决。新版金毛仅为未通过校验的候选。 |
| supports 是否仍有无依据扩写 | 仍有。状态样本 memory 引文未明确主体却写成 explicitly states the user；金毛候选仍把开放体验与 wellness goals 对齐，并跨源推导职业功能。post-work recovery 字样消失不代表支持范围已合格。 |
| 是否出现新的遗漏或语义变化 | 状态样本由旧版泛称 speaker 改成待确认却仍断言的 user，且不再列出旧版的 initial/now 时间锚点疑问。金毛第 2 条补充版本增加 companionship，四条候选全部漏掉 memory evidence，是新的程序拒绝原因。 |

## 样本 1：多人物

真实 ID：`93d9e572-f052-41b6-9387-9e7583b8c3ab`。可靠更新前快照：[session_009/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json:542)，位置 `/api_snapshot/results/59`。

旧记忆原文：

> Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition

以下为保存的新旧实际文本。v2 已通过程序校验。

| 序号 | 版本 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- | --- |
| 1 | v1 | Susan, Daniel, and Joshua provided instrumental support during the user's career transition. | Susan, Daniel, and Joshua provided instrumental support during the user's career transition; the user described their support as 'invaluable' and said it helped them 'see things differently'. |
| 1 | v2 | Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during a career transition. | The user's friends and colleagues Susan, Daniel, and Joshua provided instrumental support during the user's career transition. |

**本次助手语义初审**：关键关系得到保留，raw 不再从上下文填入用户受益人，补充正文去掉额外评价；supports 的个别明确确认表述仍偏强。

改善：

- 旧 raw 只留人名，新 raw 与补充版本均保留 friends and colleagues，修复了已观察到的关系漏项。
- 新 raw 写 during a career transition，不再在 raw 中增补 the user's；用户归属留在补充版本。
- 补充版本去掉 invaluable 和 see things differently 两项原文没有的评价及效果，仅补人物关系和职业转变的归属。
- 新增三项模型待确认，包含具体支持形式、职业转变时间范围和朋友/同事这组关系的归属范围。

未解决或新增问题：

- `$.facts[0].evidence[1].supports`：ctx-1 只直接写 my friends and colleagues 与 this transition，没有独立写出支持受益人或职业转变属于谁。supports 用 explicitly identifies themselves as the recipient、confirming the subject of the transition，强于单条引文的字面表达。ctx-2 的 I received/helped me 可以支持整体受益人补足，但不能使 ctx-1 单条引文变成明确确认。

人物、时间、条件、否定和情态检查：

- **人物与关系**：三个人名和群体关系保留，未明确分配每个人属于朋友还是同事；模型主动把此范围标为待确认。
- **时间、条件、否定和情态**：provided 和 during 的过去行为及时间范围保留，无新日期、条件、否定或完成状态。
- **语气**：支持行为仍直接陈述，没有改成用户认为或用户感觉。
- **主语依据**：补充版本中的 user 受益人有 ctx-2 的 I received/helped me 以及同一旧生成会话的对应关系支持；raw 保留旧记忆自身范围。

**待人工确认**：

1. 是否接受补充版本对职业转变受益人的关联，以及 supports 对 ctx-1 使用明确确认的语气。
2. 朋友和同事是合并群体还是重叠身份，以及三人各自角色；当前输入不能逐人确认。
3. 具体支持形式和职业转变时间范围，若下游确实需要这些信息，应继续保留未明。

逐条原始引文、supports、新旧模型 pending_confirmations 及允许上下文见 [case_1_multi_person/SEMANTIC_REVIEW.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/case_1_multi_person/SEMANTIC_REVIEW.md)。

## 样本 2：时间或状态变化

真实 ID：`05b23c45-294e-402c-bcb9-d66ccbac6371`。可靠更新前快照：[session_007/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json:38)，位置 `/api_snapshot/results/3`。

旧记忆原文：

> Expressed initial skepticism about integrating Golden Retriever preference into daily life, but now sees pets as sources of emotional support and stress relief

以下为保存的新旧实际文本。v2 已通过程序校验。

| 序号 | 版本 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- | --- |
| 1 | v1 | The speaker expressed initial skepticism about integrating their Golden Retriever preference into daily life. | The speaker expressed initial skepticism about integrating their preference for Golden Retrievers into daily life. |
| 1 | v2 | Expressed initial skepticism about integrating Golden Retriever preference into daily life | The user expressed initial skepticism about integrating their preference for Golden Retrievers into daily life |
| 2 | v1 | The speaker now sees pets as sources of emotional support and stress relief. | The speaker now sees pets as sources of emotional support and stress relief, consistent with their own prior statement that 'Pets can definitely provide emotional support, which is valuable' and their expressed optimism about using their Golden Retriever preference to help manage stress. |
| 2 | v2 | Now sees pets as sources of emotional support and stress relief | The user now sees pets as sources of emotional support and stress relief |

**本次助手语义初审**：raw 的来源边界和补充篇幅改善，但上下文版本及 memory supports 明确填入 user，与模型自己的主体待确认项冲突；原始自述归属问题未解决。

改善：

- 新 raw 保留省略主语，不再像旧版补入 The speaker。
- 第 2 条补充版本去掉 consistent with、此前原话和额外乐观态度，只保留核心命题及新增的 user 主语。
- 第 2 条 context supports 明确承认该引文没有表达 stress relief 或 now，部分收紧了支持范围。

未解决或新增问题：

- `$.facts[0].contextualized_subfact / $.facts[1].contextualized_subfact`：两条均补 The user，但 pending_confirmations 又明确说主体未定、来源原句未直接覆盖相关命题。应将主体保持未定，而不是在正文先断言。旧版正文保留泛称 speaker，新版在此更肯定。
- `$.facts[0].evidence[0].supports / $.facts[1].evidence[0].supports`：两段 memory supports 均称 The memory explicitly states the user...，而旧记忆文本没有写出 user 主语。这是新增的来源归属过度说明。
- `$.facts[*].pending_confirmations`：旧版明确提出 initial 阶段和 now 的时间锚点疑问；新版待确认改为人物、偏好含义和 pets 范围，不再提出这两个时间问题。原文字面 initial/now 仍保留，没有新增错误日期，但不确定性覆盖减少。
- `$.facts[0].pending_confirmations[0].reason`：将 Expressed... 称为 passive construction 不准确；这里是省略主语，并非被动语态。此项属于诊断措辞问题，不是新增旧事实。

人物、时间、条件、否定和情态检查：

- **人物与原始说话人**：旧记忆没有明确主体；允许上下文只有 user 的乐观和情感支持发言，没有直接怀疑自述。模型能指出缺直接原句，却仍在补充版本确定为 user。
- **时间与状态**：initial、now、skepticism 和 sees 均保留；未声称怀疑已消失，未补日期，但两个时间锚点仍需人工追踪。
- **条件、否定和情态**：未改成已整合偏好或实际养犬。原文的 sees 属于原有态度表述，不算新加的用户认为。
- **旧助手回述限制**：已在旧报告发现的助手回述仍只保存在本地来源说明，没有新增到模型输入。因此只能检查模型是否谨慎处理缺少直接自述，不能要求模型识别未提供的那段助手发言。

**待人工确认**：

1. 主体未定时补充版本断言 user，以及 memory supports 声称明确 user，是否应判为不可接受的归属变化。
2. 最初怀疑的真实直接来源：当前允许上下文不能证明用户直接表达；原有助手回述也不单独证明此事。
3. initial 阶段与 now 的时间锚点；新版未主动列出，仍需人工保留。
4. preference 及 pets 的范围是否需要进一步澄清；不能把新增待确认解释当成已经出现的事实。

逐条原始引文、supports、新旧模型 pending_confirmations 及允许上下文见 [case_2_time_state/SEMANTIC_REVIEW.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/case_2_time_state/SEMANTIC_REVIEW.md)。

## 样本 3：多个偏好及相关事实

真实 ID：`aa764342-2fe6-4632-9efd-e5e0cc032185`。可靠更新前快照：[session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_006/before.json:497)，位置 `/api_snapshot/results/54`。

旧记忆原文：

> Recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career

以下为保存的新旧实际文本。**v2 仅为被拒绝的候选，不能当作有效拆分结果。**

| 序号 | 版本 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- | --- |
| 1 | v1 | Recently interacted with a friend's Golden Retriever and was impressed by its gentle nature. | The user recently spent time at a friend's house and interacted with their Golden Retriever, finding it gentle and impressive in its adaptability. |
| 1 | v2 | Recently interacted with a friend's Golden Retriever and was impressed by its gentle nature. | The user recently spent time at a friend's house and interacted with their Golden Retriever, and found it to be a gentle creature with impressive adaptability. |
| 2 | v1 | Values adaptability, calm demeanor, and emotional support in pets. | The user values adaptability in pets (as observed in the friend's Golden Retriever), calm demeanor (cited as crucial for their active lifestyle), and emotional support (described as invaluable). |
| 2 | v2 | Values adaptability, calm demeanor, and emotional support in pets. | The user values adaptability in pets (as observed in the friend's Golden Retriever), calm demeanor in pets (crucial for their active lifestyle), and emotional support and companionship from pets (which they describe as invaluable). |
| 3 | v1 | Is drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals. | The user is drawn to Golden Retrievers because they perceive them as compatible with their active lifestyle (where calm demeanor is crucial) and wellness goals (implied by emphasis on balance, emotional support, and integration as a step toward new experiences). |
| 3 | v2 | Drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals. | The user is drawn to Golden Retrievers because they perceive them as compatible with their active lifestyle (e.g., offering balance and calm after a long day) and supportive of their wellness goals (via emotional support, companionship, and contributing to life balance). |
| 4 | v1 | Is optimistic about integrating this preference as a step toward new experiences and balancing demanding career. | The user is optimistic about integrating their preference for Golden Retrievers as a step toward new experiences and interactions, and as a means to achieve balance against a demanding career. |
| 4 | v2 | Optimistic about integrating this preference as a step toward new experiences and balancing demanding career. | The user is optimistic about integrating their preference for Golden Retrievers as a step toward new experiences and interactions, and as a means to achieve balance — particularly against the backdrop of a demanding career. |

**本次助手语义初审**：四条候选 raw 基本覆盖旧文，但补充版本仍改变印象对象、加入 perceive 及额外细节；新增 companionship，并因四条都没有 memory evidence 被程序拒绝。

改善：

- 候选 raw 仍基本覆盖四个分号段；没有明显新增的 raw 命题。
- post-work recovery 和 implied by 两个旧字样不再出现，但相应的扩写及推断问题没有因此解决。

未解决或新增问题：

- `$.facts[*].evidence`：四条候选全部只有 context evidence，没有任何 memory evidence。旧版每条都有 memory 依据；本次是新的来源结构缺失。程序正确在第一条拒绝，不能给其余候选补引文后宣布通过。
- `$.facts[0].contextualized_subfact`：仍加入朋友家地点，并将 impressed by gentle nature 改成 gentle creature with impressive adaptability。温顺仍被提及，但原来的印象关系没有保留；问题未解决。
- `$.facts[1].contextualized_subfact`：原旧记忆只写 emotional support，新候选增加 emotional support and companionship。companionship 虽有旧上下文来源，但不是必要消歧；相比旧版补充版本，这是新的内容扩写。
- `$.facts[2].contextualized_subfact`：仍写 because they perceive them as compatible，并添加 via emotional support, companionship, and contributing to life balance 的解释；直接理由主观化和目标推导未解决。
- `$.facts[2].evidence[0].supports`：将开放体验、互动与 wellness goals 对齐，当前引文没有明确表达该目标归类，仍是支持范围扩写。
- `$.facts[3].evidence[1].supports`：明确借用 memory_text 再把当前 context 引文解释为 occupational demands 的功能性应对，超出单条引文直接表达的内容；没有 memory evidence 也使这层跨源说明不可作为合格证据链。
- `$.facts[3].contextualized_subfact`：仍增加 interactions 和背景性描述，而非仅消除 this preference 的指代。

人物、时间、条件、否定和情态检查：

- **人物与主语**：The user 对互动行为有 ctx-1 的 I 和同一旧生成会话的关联依据；没有改成用户拥有朋友的狗，也没有加入新姓名。无法据此自动证明每个偏好或目标均有用户直接原话。
- **时间与情态**：recently、values、drawn to、optimistic 的主要字面范围仍在；没有增加固定日期、已经养犬或已经达到职业平衡。第 3 条新增的 perceive 仍改变理由的表达方式。
- **覆盖与粒度**：raw 未发现明确的新漏项，三个偏好和两个目标仍各自合并，粒度是否合适仍待确认。不能将候选 raw 覆盖视作整个响应合格。
- **条件与否定**：本样本没有显式条件或直接否定句，不能据此验证这类范围处理。

**待人工确认**：

1. 温顺印象关系、perceive 改写和 wellness 目标推导仍未解决，是否据此认定本次提示词调整在该样本未达目标。
2. 新增 companionship 及地点、评价、interactions 等有来源细节是否均应排除出最小补充版本。
3. supports 的目标归类和职业功能推断，以及直接原始说话人归属，仍需人工审查。

逐条原始引文、supports、新旧模型 pending_confirmations 及允许上下文见 [case_3_compound_preferences/SEMANTIC_REVIEW.md](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/case_3_compound_preferences/SEMANTIC_REVIEW.md)。

## 来源归属的特别限制

旧报告发现 initial skepticism 可能来自助手回述；那段助手文本没有包含在原先允许的上下文中，本次按要求没有添加。不能要求模型识别未提供的具体助手发言，但它应承认缺少直接用户自述及主体不清。新版状态样本虽提出主体待确认，正文和 memory supports 仍确定写 user，因此不能认定此问题已解决。

## 结果保护与边界

修改前跟踪的 104 个既有文件中，只有 DESIGN.md 按授权改变，其余 103 个保持 SHA-256 一致；完整旧设计有原样备份，旧运行结果及已有 Python 源码未变。新旧语义初审分开记录于 [manual_comparison.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/manual_comparison.json)，不是已获用户确认的标准标注。

这里只对一组三条固定输入做单次前后比较，不能排除未固定采样或模型修订因素，也不能推断总体质量。这些样本没有显式 if/unless 条件句或直接 not 否定句，相关能力仍未覆盖。

本次只调整提示词、执行已保存的三次拆分并离线核查。未修改 Mem0，未写入知识库，未执行新旧事实关系判断，未运行完整开发子集；没有输出密钥或完整环境变量。没有继续调整第二版提示词或追加请求以消除本次失败。
