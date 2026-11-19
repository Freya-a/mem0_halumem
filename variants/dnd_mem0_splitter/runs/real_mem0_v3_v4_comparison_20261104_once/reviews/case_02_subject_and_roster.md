# case_02_subject_and_roster

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`

选择理由：旧记忆省略拥有朋友的主体并保留姓名和别称；实际对应的同一条旧 user 发言还包含其他人物及工作细节。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/51`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_02_subject_and_roster) 和 [输入](../inputs/case_02_subject_and_roster.json)。

旧记忆原文：

```text
Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
```

## v3

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_02_subject_and_roster/v3/raw_content.txt) · [实际提示词](../runs/case_02_subject_and_roster/v3/prompt.txt) · [逐项程序检查](../runs/case_02_subject_and_roster/v3/program_checks.json)

初步判断，待人工确认：保留朋友、名称与支持鼓励；观察到 raw 补用户主体、contextualized 增加 well-being 效果，以及 pending 理由无依据地把 Susan 描述为语法上的不同指称。实际 supports 没有 full name 验证措辞，不能套用其他运行的姓名越界结论。

### 事实 1

raw：

```text
The user has a friend named ThomasSusan, who is referred to as 'Susan', and who provides support and encouragement.
```

contextualized：

```text
The user has a friend named ThomasSusan (referred to as 'Susan'), and Susan's support and encouragement inspire the user to maintain focus on promoting well-being in both personal and professional life.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：人物 token ThomasSusan 与称呼 Susan、朋友关系、支持鼓励均覆盖；无否定、时间、条件、情态改变。用户主体由 user 角色结合 I/my/me 直接支持，但 raw 仍不得从上下文补入。contextualized 增加有源效果/领域，超出必要补足。没有把 MartinezDaniel、WilliamsJoshua、其职业/工作细节写入正文。pending 第2项区分记忆摘要作者与用户原话，不与用户语义主体本身冲突；第1项的语法断言有局部问题。

观察到的问题：RAW_CONTEXT_LEAK、RELATION_SCOPE_CHANGE、SUPPORTED_UNNECESSARY_ADDITION。

- RAW_CONTEXT_LEAK：输入 `Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement`；输出 `The user has a friend named ThomasSusan, who is referred to as 'Susan', and who provides support and encouragement.`。初步判断，待人工确认：memory 未显式主体；ctx-1 user 的 I/my/me 可直接支持用户主体，但该信息只能用于 contextualized，raw 新增 The user 仍越过 memory-only 边界。

- SUPPORTED_UNNECESSARY_ADDITION：输入 `who provides support and encouragement`；输出 `The user has a friend named ThomasSusan (referred to as 'Susan'), and Susan's support and encouragement inspire the user to maintain focus on promoting well-being in both personal and professional life.`。初步判断，待人工确认：正文新增支持鼓励激励其维持个人/职业生活 well-being 关注的效果。该效果确有 ctx-1 用户来源，但不是补主体/别称所必需；它进入正文，故不是仅因 quote 更长而判错。

- RELATION_SCOPE_CHANGE：输入 `ThomasSusan (referred to as 'Susan')`；输出 `The memory text writes 'ThomasSusan' as one token and clarifies 'referred to as "Susan"', suggesting a single person; however, the context quote says 'ThomasSusan is my Friend, Susan's support...', using both 'ThomasSusan' and possessive 'Susan's' — which syntactically treats 'Susan' as a distinct referent. No source disambiguates orthographic convention (e.g., hyphenation, spacing) or naming practice, nor confirms whether 'ThomasSusan' reflects legal name, nickname, or transcription error.`。初步判断，待人工确认：此项仅针对 pending 理由的确定说法 using both ... which syntactically treats Susan as a distinct referent。旧记忆显式将 Susan 作为 ThomasSusan 的称呼；上下文先给全 token 再用 Susan 的所有格并不在语法上强制为不同人物。可保留命名形式/转写未知，但不能把这种未知说成语法已经区分了两个人。正文的单人/别称关系仍保留，不记遗漏。

引文 0：`memory/a1332815-d6ba-4bdc-9ffa-657f7315d0ed`

```text
Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
```

supports 原文：

```text
Old memory states the user has a friend named ThomasSusan (called 'Susan') who provides support and encouragement.
```

支持范围初审：partially_supported。初步判断，待人工确认：原 supports：Old memory states the user has a friend named ThomasSusan (called 'Susan') who provides support and encouragement.
原 quote：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
复核：memory 引文支持朋友、名称/称呼及支持鼓励；user 主体需要 ctx-1 而非该引文字面。Old memory states 不是声称用户亲口逐字说过，不自动计越界。

引文 1：`context/ctx-1`

```text
ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.
```

supports 原文：

```text
Confirms the speaker is the user (first-person 'my', 'me'); identifies ThomasSusan as the user's friend; specifies that Susan's support and encouragement inspire the user's focus on well-being across domains — this contextualizes the scope and effect of the support/encouragement mentioned in the memory.
```

支持范围初审：directly_supported。初步判断，待人工确认：原 supports：Confirms the speaker is the user (first-person 'my', 'me'); identifies ThomasSusan as the user's friend; specifies that Susan's support and encouragement inspire the user's focus on well-being across domains — this contextualizes the scope and effect of the support/encouragement mentioned in the memory.
原 quote：ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.
复核：source 的 user 元数据与 my/me 共同支持原始用户角色，quote 明确给朋友及支持效果。supports 准确描述这些来源信息，未说 ThomasSusan 已验证为真实完整姓名；正文扩写虽非必要，其效果内容本身确实有源。

模型 pending_confirmations（原样保留）：

```json
[
  {
    "item": "Whether 'ThomasSusan' is a single person with a compound name (e.g., Thomas Susan as full name, or ThomasSusan as fused given name), or two people (Thomas and Susan) mistakenly concatenated",
    "reason": "The memory text writes 'ThomasSusan' as one token and clarifies 'referred to as \"Susan\"', suggesting a single person; however, the context quote says 'ThomasSusan is my Friend, Susan's support...', using both 'ThomasSusan' and possessive 'Susan's' — which syntactically treats 'Susan' as a distinct referent. No source disambiguates orthographic convention (e.g., hyphenation, spacing) or naming practice, nor confirms whether 'ThomasSusan' reflects legal name, nickname, or transcription error."
  },
  {
    "item": "Whether the user explicitly self-identifies as the speaker in the memory (i.e., whether 'Has a friend...' is third-person narration by assistant vs. user's own reported statement)",
    "reason": "The memory text is written in third-person ('Has a friend...'), unlike the context quote which is first-person ('my Friend', 'me'). The source_context confirms the speaker is the user, but does not confirm that the memory text itself was authored or uttered by the user — it may be an assistant-generated summary. Thus, the original speaker of the memory sentence remains unconfirmed."
  }
]
```

初审待确认：初步判断，待人工确认：ThomasSusan token 的真实命名结构、法律全名或是否为转写形式不可从此片段验证；但这不许可改名或把旧记忆明确的称呼关联默默拆成两人。；初步判断，待人工确认：来源区分：该 user 原文直接自述 my Friend 及支持效果，足以支持命题层面的用户自述；旧记忆句子的逐字作者仍不等于该原始用户发言。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 朋友关系及名称 token | Has a friend named ThomasSusan | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都保留拥有朋友及 ThomasSusan token；v3 raw 主体来源边界另记，不抹去实际覆盖。 |
| 称呼/别称关联 | (referred to as 'Susan') | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都保留 ThomasSusan 与 Susan 的称呼关联；v3 pending 的 distinct referent 解释不等于正文丢失此关联。 |
| 支持和鼓励 | who provides support and encouragement | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都表达该朋友的支持和鼓励；v3 contextualized 还新增效果，另记有源非必要扩写。 |

初步判断，待人工确认：单条将朋友/称呼/支持作为相连命题保留，粒度较粗但没有关键遗漏；把来源中的同事名单另拆进旧事实反而没有必要。

案例未决项：初步判断，待人工确认：命名形式的真实含义有限未知；应将其与文本已明示的 Susan 称呼关联分开，不能用猜测改变旧命题。。

## v4

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_02_subject_and_roster/v4/raw_content.txt) · [实际提示词](../runs/case_02_subject_and_roster/v4/prompt.txt) · [逐项程序检查](../runs/case_02_subject_and_roster/v4/program_checks.json)

初步判断，待人工确认：raw 保留原省略主语，contextualized 只补用户；未带入 well-being 效果或同事名单。两项 supports 未见明确来源或身份验证越界；pending=[] 不表示真实完整身份已核验。

### 事实 1

raw：

```text
Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
```

contextualized：

```text
The user has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：raw 原样保留朋友、ThomasSusan、Susan 称呼和支持鼓励；contextualized 仅补 The user。用户角色加同事件 I/my Friend/me 足以支持此补足。否定、时间、条件、情态无变化；未扩写 well-being 效果，也未带入其他人物。context quote 虽含完整效果描述，正文没有，不能记正文扩写。用户原始片段直接支持朋友/支持命题；不要求用户曾逐字说出提取后的 memory 句型。

观察到的问题：未观察到明确问题。

引文 0：`memory/a1332815-d6ba-4bdc-9ffa-657f7315d0ed`

```text
Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
```

supports 原文：

```text
Old memory states the user has a friend named ThomasSusan, referred to as 'Susan', who provides support and encouragement.
```

支持范围初审：partially_supported。初步判断，待人工确认：原 supports：Old memory states the user has a friend named ThomasSusan, referred to as 'Susan', who provides support and encouragement.
原 quote：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
复核：该 memory 引文未显式 user 主体，其余朋友/名称/称呼/支持鼓励均直接表达；主体由 ctx-1 补足。说明记忆记载用户的合理概括不等于宣称该 fragment 字面有 user 或是用户原话，partial 不自动计错。

引文 1：`context/ctx-1`

```text
ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.
```

supports 原文：

```text
Confirms the user explicitly identifies ThomasSusan as 'my Friend' and attributes support and encouragement to 'Susan'; speaker metadata ('speaker': 'user') supports that this is the user's self-report.
```

支持范围初审：directly_supported。初步判断，待人工确认：原 supports：Confirms the user explicitly identifies ThomasSusan as 'my Friend' and attributes support and encouragement to 'Susan'; speaker metadata ('speaker': 'user') supports that this is the user's self-report.
原 quote：ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.
复核：quote 的 my Friend、Susan 的支持与 speaker=user 元数据共同支持用户自述；不是仅凭 speaker 元数据确定所有事实主语，也未验证真实完整身份。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：ThomasSusan 的真实完整身份/名字结构并未外部核验；本版只保留原 token 和称呼，未声称 full name 验证，因此此未知不自动算错误。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 朋友关系及名称 token | Has a friend named ThomasSusan | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都保留拥有朋友及 ThomasSusan token；v3 raw 主体来源边界另记，不抹去实际覆盖。 |
| 称呼/别称关联 | (referred to as 'Susan') | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都保留 ThomasSusan 与 Susan 的称呼关联；v3 pending 的 distinct referent 解释不等于正文丢失此关联。 |
| 支持和鼓励 | who provides support and encouragement | [1]/[1] | preserved | 初步判断，待人工确认：两版本正文都表达该朋友的支持和鼓励；v3 contextualized 还新增效果，另记有源非必要扩写。 |

初步判断，待人工确认：与 v3 同为一条，覆盖不减少；去掉额外效果后更贴近旧记忆目标。

案例未决项：初步判断，待人工确认：真实名字形式仍无外部核验；文本内单个 token 与 Susan 称呼的关系足以原样保留，不要求为无争议拆分补现实身份信息。。

## 配对比较

改善：

- 初步判断，待人工确认：v4 修复 raw 上下文主体混入，并去掉 contextualized 有源但非必要的 well-being 效果。
- 初步判断，待人工确认：v4 不再把使用 ThomasSusan/Susan 解释成语法上必为不同人物；保留旧记忆的称呼关联。

持续问题/相同观察：

- 初步判断，待人工确认：两版本朋友、名称/称呼、支持鼓励覆盖完整；命名 token 的现实完整身份仍不能由现有文本外部验证，但两版本轮 supports 都未宣称 full name 已验证。

本轮新增问题：

未观察到明确项。

配对解释限制：

- 初步判断，待人工确认：v4 pending=[] 不能证明法律姓名或转写形式已核验；因为正文不改名/不宣称真实全名，此项只记有限未知。
