# 多人物：v1 与 v2 对比

提示词调整及真实请求记录日期：2026-11-03（Asia/Shanghai）。中断后报告补齐日期：2026-11-04（Asia/Shanghai）。本次续接未追加模型请求。

本次助手对保存的新旧响应逐项初审；尚未经用户确认，不是自动语义评分，也未向 qwen-plus 提供本文件。

新版状态：**有效结果**。每条实际 qwen-plus 调用 1 次，重试 0 次；本样本 CLI 退出码为 0。

## 输入与来源

真实 memory_id：`93d9e572-f052-41b6-9387-9e7583b8c3ab`。

> Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition

可靠更新前快照：[session_009/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json:542)，JSON Pointer `/api_snapshot/results/59`。

生成会话 session_008 的实际 ADD、生成后快照、前一会话 after 及目标 session_009 before 已按原有来源链和 checkpoint 哈希核对。详情见 [provenance.previous.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/provenance.previous.json)。

新版 input.json 与旧次 input.json 字节完全一致，包括 memory_id、旧文本和每个 source_context 的文本、角色、时间、引用位置。未增加助手回述、后续证据、旧模型响应、人工复核或标准答案。

允许的旧上下文：

- `ctx-1`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/4/content [characters 0:105, zero-based, end exclusive]`；speaker=`user`，recorded_at=`Mar 01, 2026, 07:11:33`。

> Absolutely, my friends and colleagues were instrumental in this transition. Their support was invaluable.

- `ctx-2`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/8/content [characters 0:105, zero-based, end exclusive]`；speaker=`user`，recorded_at=`Mar 01, 2026, 07:16:19`。

> The support I received was incredible. Susan, Daniel, and Joshua really helped me see things differently.

## 程序检查与拒绝原因

| 检查 | v1 | v2 |
| --- | --- | --- |
| 原有校验器整体结果 | 通过 | 通过 |
| 已验证事实数 | 1 | 1 |
| 保存的候选事实数 | 1 | 1 |
| result.json | 存在 | 存在 |
| 逐字引文 | 原程序通过 3/3 | 原程序通过 3/3 |
| ID、旧文本和输入 | 旧输入基线 | 字节一致，候选回显及事实 ID 匹配 |

原有校验器只检查结构、ID 和逐字引文，不检查关系完整性、语义支持、主语归属或补充必要性。详见 [本样本 verification.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/case_1_multi_person/verification.json)。

## 新旧事实文本逐条对比

本轮两版事实数量和出现顺序相同，按原序号列出；这不是自动语义对齐评分。v2 栏是否有效，以前面的程序状态为准。

| 序号 | 版本 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- | --- |
| 1 | v1 | Susan, Daniel, and Joshua provided instrumental support during the user's career transition. | Susan, Daniel, and Joshua provided instrumental support during the user's career transition; the user described their support as 'invaluable' and said it helped them 'see things differently'. |
| 1 | v2 | Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during a career transition. | The user's friends and colleagues Susan, Daniel, and Joshua provided instrumental support during the user's career transition. |

## 引文和 supports 原样对照

下表均为保存的模型原文。字面匹配仅证明 quote 出现在指定来源，不证明 supports 没有推断。对于 v2 被拒绝候选，全表只是额外只读诊断。

| 版本 | 事实 | 来源 | quote | supports |
| --- | --- | --- | --- | --- |
| v1 | 1 | memory / 93d9e572-f052-41b6-9387-9e7583b8c3ab | Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition | Core proposition: Susan, Daniel, and Joshua provided instrumental support during career transition. |
| v1 | 1 | context / ctx-1 | Absolutely, my friends and colleagues were instrumental in this transition. Their support was invaluable. | Confirms 'instrumental' nature of support and characterizes it as 'invaluable'; establishes 'this transition' refers to the user's career transition. |
| v1 | 1 | context / ctx-2 | The support I received was incredible. Susan, Daniel, and Joshua really helped me see things differently. | Names Susan, Daniel, and Joshua as providers of 'incredible' support and specifies a qualitative effect: helping the user 'see things differently'. |
| v2 | 1 | memory / 93d9e572-f052-41b6-9387-9e7583b8c3ab | Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition | The memory states that Susan, Daniel, and Joshua — identified as friends and colleagues — provided instrumental support during a career transition. |
| v2 | 1 | context / ctx-1 | Absolutely, my friends and colleagues were instrumental in this transition. Their support was invaluable. | The speaker ('user') explicitly identifies themselves as the recipient of instrumental support from 'my friends and colleagues' during 'this transition', confirming the subject of the transition and the possessive relationship. |
| v2 | 1 | context / ctx-2 | The support I received was incredible. Susan, Daniel, and Joshua really helped me see things differently. | The speaker ('user') confirms receiving support from Susan, Daniel, and Joshua personally, and frames it as helping 'me' — corroborating their role as supporters in the user's experience. |

## 本次助手语义初审

关键关系得到保留，raw 不再从上下文填入用户受益人，补充正文去掉额外评价；supports 的个别明确确认表述仍偏强。

改善：

- 旧 raw 只留人名，新 raw 与补充版本均保留 friends and colleagues，修复了已观察到的关系漏项。
- 新 raw 写 during a career transition，不再在 raw 中增补 the user's；用户归属留在补充版本。
- 补充版本去掉 invaluable 和 see things differently 两项原文没有的评价及效果，仅补人物关系和职业转变的归属。
- 新增三项模型待确认，包含具体支持形式、职业转变时间范围和朋友/同事这组关系的归属范围。

未解决或新增问题：

- `$.facts[0].evidence[1].supports`：ctx-1 只直接写 my friends and colleagues 与 this transition，没有独立写出支持受益人或职业转变属于谁。supports 用 explicitly identifies themselves as the recipient、confirming the subject of the transition，强于单条引文的字面表达。ctx-2 的 I received/helped me 可以支持整体受益人补足，但不能使 ctx-1 单条引文变成明确确认。

| 维度 | 对照检查 |
| --- | --- |
| 人物与关系 | 三个人名和群体关系保留，未明确分配每个人属于朋友还是同事；模型主动把此范围标为待确认。 |
| 时间、条件、否定和情态 | provided 和 during 的过去行为及时间范围保留，无新日期、条件、否定或完成状态。 |
| 语气 | 支持行为仍直接陈述，没有改成用户认为或用户感觉。 |
| 主语依据 | 补充版本中的 user 受益人有 ctx-2 的 I received/helped me 以及同一旧生成会话的对应关系支持；raw 保留旧记忆自身范围。 |

## 模型自身的待确认项

### v1

事实 1：

`[]`。

### v2

事实 1：

- **Specific nature and form of 'instrumental support'**：The memory and contexts describe support as 'instrumental', 'invaluable', and 'incredible', and mention helping the user 'see things differently', but do not specify concrete actions (e.g., job referrals, advice, emotional scaffolding).

- **Temporal scope and phase of the career transition**：The memory says 'during career transition' without specifying start/end points, duration, or whether it refers to a single discrete transition or multiple transitions; no context provides explicit timeline anchors beyond relative references ('this transition').

- **Whether 'friends and colleagues' is a single overlapping group or two distinct groups, with Susan/Daniel/Joshua belonging to one or both**：The phrasing 'Friends and colleagues (Susan, Daniel, and Joshua)' is syntactically ambiguous: it could mean (a) [Friends] and [colleagues] — where the parenthetical names apply to both categories, or (b) [Friends and colleagues] as a compound noun phrase, with the names exemplifying the combined group. Neither memory nor contexts resolve this syntactic scope.

## 待人工确认

1. 是否接受补充版本对职业转变受益人的关联，以及 supports 对 ctx-1 使用明确确认的语气。
2. 朋友和同事是合并群体还是重叠身份，以及三人各自角色；当前输入不能逐人确认。
3. 具体支持形式和职业转变时间范围，若下游确实需要这些信息，应继续保留未明。

以上由本次助手新增，未经用户确认；与模型自身的 pending_confirmations 分开保存。

## 请求与结果保留

两版显式参数一致：qwen-plus、generation_parameters={}、timeout=180 秒、response_format=json_object、SDK max_retries=0、HTTP 不跟随重定向。温度、seed、token 上限未显式固定，服务默认值、实际模型修订和旧次依赖版本锁不明；配置路径一致也不能独立证明历史端点从未变化。

新版原始响应：[raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_prompt_v2_20261103_once/case_1_multi_person/raw_content.txt)。旧次结果：[旧 result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_three_types_20261103_once/case_1_multi_person/result.json)。本次未修改 Python 运行器、校验器、Mem0 或知识库，未运行完整开发子集。
