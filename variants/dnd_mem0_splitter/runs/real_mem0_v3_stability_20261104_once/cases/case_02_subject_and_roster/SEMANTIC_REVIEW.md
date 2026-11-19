# case_02_subject_and_roster：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：缺失主语、姓名与别称、上下文额外人物。

选择原因：旧记忆省略拥有朋友的主体并保留姓名和别称；实际对应的同一条旧 user 发言还包含其他人物及工作细节。

真实 memory_id：`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`。

> Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

更新前快照：[session_005/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json:470)，JSON Pointer `/api_snapshot/results/51`；底层对应 `/database_points_with_vectors/51/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/add_return.json)，位置 `/return_value/results/9`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`Sep 06, 2025, 01:02:20`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [characters 0:590, zero-based, end exclusive]`。

> Of course. I have several important friends and colleagues: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life. MartinezDaniel is my Colleague, Daniel's expertise in healthcare consulting challenges me to push boundaries and innovate in our projects, significantly impacting my career growth. WilliamsJoshua is my Colleague, Joshua's collaborative approach and insights into healthcare management enhance our team's effectiveness, positively influencing my work and leadership style.

## 程序检查

| 检查 | 结果 |
| --- | --- |
| 原有校验器 | passed |
| 返回事实数 | 1 |
| JSON 字段、ID、原文、编号、每条 memory 引文与来源编号 | 通过现有校验器 |
| 逐字引文 | 2/2 |
| 真实调用 / 自动重试 | 1 / 0 |
| 模型 / finish_reason | qwen-plus / stop |
| 离线重放 | 原始响应经 MockBackend 复核，与保存结果一致；不调用真实模型 |

显式生成参数为 {}，超时 180 秒，SDK max_retries=0，HTTP 不跟随重定向，response_format=json_object。服务默认采样值和具体模型修订未知。提示词逐字等于 [冻结 v3](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/frozen_prompt.txt)，SHA-256 为 `28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e`。

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_02_subject_and_roster/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_02_subject_and_roster/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_02_subject_and_roster/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

初步判断，待人工确认：格式检查 passed；1 条事实保留朋友关系、ThomasSusan/Susan 名称关联及支持鼓励。观察到 raw 主体来自上下文、contextualized 增加有源但非必要的 well-being 效果，以及 context supports 将名称 token 升格为已验证 full name 的越界与待决状态冲突。未把其他同事名单带入正文。

### 事实 1

原始子事实：

> The user has a friend named ThomasSusan, who is referred to as 'Susan', and who provides support and encouragement.

上下文版本：

> The user has a friend named ThomasSusan (referred to as 'Susan'), and Susan's support and encouragement inspire the user to maintain focus on promoting well-being in both personal and professional life.

覆盖及限定检查：初步判断，待人工确认：raw 完整保留 Has a friend、ThomasSusan、referred to as Susan、provides support and encouragement；contextualized 也保留朋友及别称关联，并改用有源的支持鼓励效果表述。没有遗漏关键名字/关系，没有否定、时间、条件或情态变化。user 主体由 source_context 的 user 角色及 I/my/me 直接支持；raw 增加该主体仍违反仅从 memory 内恢复内容的边界。contextualized 正文确实新增了支持鼓励激励其维持个人和职业生活 well-being 关注的命题；它有 user 来源，但不是消歧或保留旧记忆所必需。引文中的其他细节本身不计新增，MartinezDaniel/WilliamsJoshua 及工作细节也没有进入事实正文。

初审状态：`issue_observed`。观察到的问题：断言与待确认状态不一致、raw 混入上下文主体、有来源但非必要的正文扩写、supports 支持范围越界。

观察项与依据：

- **raw 混入上下文主体**（observed，初步判断，待人工确认）

  输入或对照：`Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement`

  输出：`The user has a friend named ThomasSusan, who is referred to as 'Susan', and who provides support and encouragement.`

  理由：初步判断，待人工确认：此处 output_quote 是 raw_subfact。memory 省略拥有朋友的主体；source_context 的 user 第一人称可以支持用户主体，但冻结 v3 第2条要求此类上下文补足留在 contextualized，raw 不应填 The user。这是字段边界问题，不是将有来源的用户主体判为虚构。

- **有来源但非必要的正文扩写**（observed，初步判断，待人工确认）

  输入或对照：`Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement`

  输出：`Susan's support and encouragement inspire the user to maintain focus on promoting well-being in both personal and professional life.`

  理由：初步判断，待人工确认：output_quote 是 contextualized_subfact 的实质内容片段。旧 memory 只有支持和鼓励，并无激励保持 well-being 关注及个人/职业领域的效果；该效果虽被 ctx-1 用户原文直接支持，但超出补主体或解释别称所需。它已进入事实正文，故属于有源但非必要扩写，不是仅因证据引文含更多细节而判错。

- **supports 支持范围越界**（observed，初步判断，待人工确认）

  输入或对照：`ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.`

  输出：`validates 'ThomasSusan' as the full name and 'Susan' as the used reference`

  理由：初步判断，待人工确认：两处输入确实使用 ThomasSusan token，并将其与 Susan 关联，足以保留原命名/别称命题；它们不能验证 ThomasSusan 是完整真实姓名而非串接、数据形式或笔误。supports 的 full name 验证结论超出所引文本。此判断只针对 supports 新加强度，不将 raw 沿用原 memory 的 named ThomasSusan 另判无依据。

- **断言与待确认状态不一致**（observed，初步判断，待人工确认）

  输入或对照：`Whether 'ThomasSusan' is a single compound name (e.g., a double-barrelled first name) or a conflation/typo of two names (e.g., 'Thomas' and 'Susan')`

  输出：`validates 'ThomasSusan' as the full name and 'Susan' as the used reference`

  理由：初步判断，待人工确认：input_quote 引自本次输出 pending_confirmations 的 item。supports 声称已验证 full name，同时 pending 明确保留名称是否为串接/笔误的疑问，确定程度冲突。仅保留文本 token 和已使用的 Susan 称呼可以与未知并存，但 full name 已验证这一更强断言不能由现有证据消除该未知。

未决项（不自动判错）：

- SUBJECT_OR_IDENTITY：初步判断，待人工确认：ThomasSusan 的 token 结构、完整姓名性质、是否为串接/笔误无法在本输入中确定；应保持原记忆命名而不擅自改名或合并拆分人物。
- MODAL_OR_RELATION_SCOPE：初步判断，待人工确认：支持鼓励的具体方式、频率、场景没有给出。模型将它列为待确认属于额外细节未知，本身不是拆分错误，也不是完成原命题所需补全的缺口。

说话人及语义主体：

- semantic_subject：初步判断，待人工确认：ctx-1 的元数据 speaker=user，正文 I have / my Friend / inspire me 足以直接支持拥有朋友、接受支持者是用户；不应将省略主语的 memory 一律判为主体虚构。
- original_utterance_attribution：初步判断，待人工确认：朋友、姓名 token、Susan 称呼及 well-being 效果均出现在该 user 原始片段中。context supports 关于 speaker=user 可结合角色元数据支持；第一人称词本身并不能单独确定系统角色，但这里元数据已明确。
- pending_review：初步判断，待人工确认：姓名结构 pending 与 full name 验证冲突已单列；具体支持方式 pending 不应转化为错误计数或要求新增事实。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / a1332815-d6ba-4bdc-9ffa-657f7315d0ed | Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement | Old memory states the user has a friend named ThomasSusan (called 'Susan') who provides support and encouragement. | 部分支持，不能自动计错：初步判断，待人工确认：memory 引文直接支持朋友关系、ThomasSusan/Susan 名称关联及支持鼓励；user 主体不在该引文字面内，但同事件 user 第一人称来源足以补足。因此主体有依据，supports 作为纯 memory 来源描述并非全为字面支持；未声称其是用户原话，也未把 ThomasSusan 说成已核验 full name，此处不单独计错误。 |
| 1 | context / ctx-1 | ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life. | Confirms speaker is the user (first-person 'my', 'me'); specifies that Susan's support and encouragement inspire the user's focus on well-being across domains; validates 'ThomasSusan' as the full name and 'Susan' as the used reference; supports contextualizing 'provides support and encouragement' as having an inspiring effect tied to well-being goals. | 支持范围越界（初审）：初步判断，待人工确认：quote 与 source 的 user 元数据共同支持用户角色、朋友关系、Susan 的使用以及激励关注 well-being 的效果；后者虽为非必要正文扩写，但确实有源。越界部分是将 ThomasSusan token 验证为 full name；输入只显示其使用形式，且模型自己保留串接/笔误 pending。不能由该 evidence 验证真实完整姓名。 |

模型自身 pending_confirmations：

- Whether 'ThomasSusan' is a single compound name (e.g., a double-barrelled first name) or a conflation/typo of two names (e.g., 'Thomas' and 'Susan')：The memory text and source context both present 'ThomasSusan' as a single token without internal punctuation or clarification; no disambiguating evidence (e.g., usage elsewhere, correction, or syntactic separation) is provided.
- The specific nature or mode of Susan's support and encouragement (e.g., verbal, practical, emotional, frequency, context)：Both memory and context describe the support and encouragement only at the level of effect ('inspire me to maintain focus...') and domain ('personal and professional life'), without specifying actions, occasions, or forms.

## 人工待确认

1. SUBJECT_OR_IDENTITY：初步判断，待人工确认：ThomasSusan 是完整姓名、复合名字还是串接/笔误仍无法确认；当前只能忠实保留 token 和 Susan 称呼，不能自动纠正。
2. MODAL_OR_RELATION_SCOPE：初步判断，待人工确认：具体支持方式/频率在片段内未知，但不属于原记忆必须补全的内容，也不单独计为错误。
3. ASSERTION_PENDING_CONFLICT：初步判断，待人工确认：请人工确认 full name 已验证与姓名结构 pending 的确定程度冲突；这不否定源文本确实使用了 ThomasSusan 和 Susan。

独立复核文件：[reviews/group_01.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_01.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
