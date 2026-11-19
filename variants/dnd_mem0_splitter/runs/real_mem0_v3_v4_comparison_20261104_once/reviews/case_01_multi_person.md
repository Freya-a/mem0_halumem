# case_01_multi_person

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`130bf22c-9e71-4ad2-bf51-43bac36ab2c8`

选择理由：两名具名人物与不同关系标签；对应旧来源包含 user 发言和 assistant 对人物关系的描述。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_011/before.json#/api_snapshot/results/13`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_01_multi_person) 和 [输入](../inputs/case_01_multi_person.json)。

旧记忆原文：

```text
Grateful towards colleagues like Steven and friends like Mary
```

## v3

程序：passed；候选事实 1 条；逐字引文 1/1。

[原始响应](../runs/case_01_multi_person/v3/raw_content.txt) · [实际提示词](../runs/case_01_multi_person/v3/prompt.txt) · [逐项程序检查](../runs/case_01_multi_person/v3/program_checks.json)

初步判断，待人工确认：1 条事实完整保留两组感谢对象；观察到 raw 补用户主体的边界问题、主体断言与 pending 的混写冲突，以及 pending 对 like/instance 的过度怀疑。后两者的作用位置是 pending 说明，正文没有删除人物关系。

### 事实 1

raw：

```text
The user is grateful towards colleagues like Steven and friends like Mary.
```

contextualized：

```text
The user is grateful towards colleagues like Steven and friends like Mary.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：人物 Steven/Mary、同事/朋友两组关系、grateful 对象与 like 举例范围均保留；无否定、事件日期、条件或计划情态变化。raw 新增用户主体越过字段来源边界；contextualized 的用户主体可由同事件上下文合理补足。没有把定期联系计划或 strong support network 加到事实正文。pending 第1项混写主体与原始发言，第2项对类别举例的否定解释有问题；正文覆盖完整。

观察到的问题：ASSERTION_PENDING_CONFLICT、RAW_CONTEXT_LEAK、RELATION_SCOPE_CHANGE。

- RAW_CONTEXT_LEAK：输入 `Grateful towards colleagues like Steven and friends like Mary`；输出 `The user is grateful towards colleagues like Steven and friends like Mary.`。初步判断，待人工确认：memory 省略主语且没有可在 memory 内部恢复的共享 user；raw 补 The user 需要上下文。ctx-1 的第一人称感谢与 ctx-2 的 Your gratitude 可合理支持 contextualized 用户主体，但不解除 raw-only 约束；不据此判用户主体虚构。

- ASSERTION_PENDING_CONFLICT：输入 `Grateful towards colleagues like Steven and friends like Mary`；输出 `The subject of 'Grateful' (i.e., who holds this attitude)`。初步判断，待人工确认：正文直接写 The user is grateful，pending item 却把 who holds this attitude 本身列为待确认。其理由又把原始说话人/是否逐字用户自述和语义主体混在一起。记录的是输出确定程度混写，不是把缺少用户原话当作所有主体未知。

- RELATION_SCOPE_CHANGE：输入 `colleagues like Steven and friends like Mary`；输出 `The phrase 'colleagues like Steven' and 'friends like Mary' uses 'like' to indicate exemplification, not definitive classification. The memory does not assert Steven *is* a colleague or Mary *is* a friend — only that they are instances illustrative of those categories. No source context provides independent verification of their actual roles or relationships to the user.`。初步判断，待人工确认：此 finding 只针对 pending 理由。like 在此将 Steven/Mary 作为相应类别的例子；理由一面称其为 instances，一面断言 memory does not assert 对应关系，过度把文本内的举例关系与外部真实性验证混为一谈。可未知的是实际身份/现实关系是否真实，不是因此否认旧记忆表达了类别归属。事实正文仍保留原关系，不记 OMISSION。

引文 0：`memory/130bf22c-9e71-4ad2-bf51-43bac36ab2c8`

```text
Grateful towards colleagues like Steven and friends like Mary
```

supports 原文：

```text
Old memory states the user is grateful towards colleagues like Steven and friends like Mary.
```

支持范围初审：partially_supported。初步判断，待人工确认：原 supports：Old memory states the user is grateful towards colleagues like Steven and friends like Mary.
原 quote：Grateful towards colleagues like Steven and friends like Mary
复核：引文直接支持感谢、两个人名及对应关系/like 范围，但本身没有 user 主语。必要上下文能合理补出用户语义主体；Old memory states 不等于声称用户亲口说过，不单独记 SUPPORTS_OVERREACH。

模型 pending_confirmations（原样保留）：

```json
[
  {
    "item": "The subject of 'Grateful' (i.e., who holds this attitude)",
    "reason": "The memory text is a fragment without explicit subject; it does not grammatically specify whether 'Grateful' is self-attributed by the user, reported by the assistant, or ascribed to another person. Although context-2 quotes the assistant paraphrasing this sentiment, and context-1 has the user speaking about maintaining relationships and expressing gratitude, neither source explicitly confirms the user directly uttered this exact phrase or unambiguously self-attributes this specific gratitude statement."
  },
  {
    "item": "Whether 'Steven' and 'Mary' are confirmed colleagues and friends respectively",
    "reason": "The phrase 'colleagues like Steven' and 'friends like Mary' uses 'like' to indicate exemplification, not definitive classification. The memory does not assert Steven *is* a colleague or Mary *is* a friend — only that they are instances illustrative of those categories. No source context provides independent verification of their actual roles or relationships to the user."
  }
]
```

初审待确认：初步判断，待人工确认：原始来源：提供的具名感谢/关系表述来自 ctx-2 assistant；ctx-1 user 只直接说维护这些关系并表达感谢，不能确认具名旧命题是用户直接原话。；初步判断，待人工确认：语义主体有同事件 user/Your gratitude 关联；具体人物真实身份和关系现实真伪未被核验，忠实保留旧命题不要求完成外部核验。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 对同事的感谢及 Steven 举例 | Grateful towards colleagues like Steven | [1]/[1] | preserved | 初步判断，待人工确认：两版本的 raw/contextualized 都保留感谢态度、colleagues 群体、Steven 及 like 举例；不能把 pending 的解释问题误记为正文关系遗漏。 |
| 对朋友的感谢及 Mary 举例 | and friends like Mary | [1]/[1] | preserved | 初步判断，待人工确认：两版本的 raw/contextualized 都保留同一感谢态度、friends 群体、Mary 及 like 举例。 |

初步判断，待人工确认：单条并列保留两组感谢对象，属于较粗粒度观察；所有关键态度对象/人物关系均在正文，没有因未拆成两条而记遗漏。

案例未决项：初步判断，待人工确认：具名命题的用户直接原话未确认；pending 存在明确主体问题与来源问题混写，最终错误类型仍待人工确认。。

## v4

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_01_multi_person/v4/raw_content.txt) · [实际提示词](../runs/case_01_multi_person/v4/prompt.txt) · [逐项程序检查](../runs/case_01_multi_person/v4/program_checks.json)

初步判断，待人工确认：raw 恢复省略主语，contextualized 才补 User；memory supports 承认主体未显式给出，context supports 只确认 assistant 的语义归属。未见明确文本层面的事实/支持越界；pending=[] 不能视为具名命题的用户原话或现实身份已验证。

### 事实 1

raw：

```text
Grateful towards colleagues like Steven and friends like Mary
```

contextualized：

```text
User is grateful towards colleagues like Steven and friends like Mary
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：raw 原样保留旧记忆；contextualized 仅补用户主体。Steven/colleagues、Mary/friends、感谢态度及 like 举例范围完整；无否定、时间、条件或情态新增/变化。ctx-2 的 Your gratitude 直接把讨论中的感谢归于用户，结合 ctx-1 的第一人称关系维护/感谢，可合理确定语义主体；这不证明具名概括由用户直接说出。完整 context quote 包含 strong support network，但正文没有带入，不记额外扩写。

观察到的问题：未观察到明确问题。

引文 0：`memory/130bf22c-9e71-4ad2-bf51-43bac36ab2c8`

```text
Grateful towards colleagues like Steven and friends like Mary
```

supports 原文：

```text
Old memory records gratitude directed toward colleagues (e.g., Steven) and friends (e.g., Mary); subject is not explicitly stated in this string.
```

支持范围初审：directly_supported。初步判断，待人工确认：原 supports：Old memory records gratitude directed toward colleagues (e.g., Steven) and friends (e.g., Mary); subject is not explicitly stated in this string.
原 quote：Grateful towards colleagues like Steven and friends like Mary
复核：准确说明记忆的感谢对象及举例关系，并明确此引文字面未给主体；没有冒称用户原话或验证现实关系。

引文 1：`context/ctx-2`

```text
Your gratitude towards colleagues like Steven and friends like Mary highlights the importance of having a strong support network.
```

supports 原文：

```text
Assistant's use of 'Your gratitude' directly attributes the gratitude to the user; confirms semantic subject as user.
```

支持范围初审：directly_supported。初步判断，待人工确认：原 supports：Assistant's use of 'Your gratitude' directly attributes the gratitude to the user; confirms semantic subject as user.
原 quote：Your gratitude towards colleagues like Steven and friends like Mary highlights the importance of having a strong support network.
复核：assistant 的 Your gratitude 确实直接把这项感谢归给被对话的用户，支持语义主体补足。supports 明说 Assistant，未将其变成 user 直接发言；confirms semantic subject 不等于确认现实事实/用户原话。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：原始来源未决：assistant 对用户的直接语义归属不是用户直接自述。ctx-1 不含 Steven/Mary，现有片段仍无法确认用户亲口表达过完整具名感谢命题；模型 pending=[] 没有记录此局部来源限制。；初步判断，待人工确认：人物现实身份与现实关系未验证；原记忆的 like 关系可以忠实保留，不因此自动判错。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 对同事的感谢及 Steven 举例 | Grateful towards colleagues like Steven | [1]/[1] | preserved | 初步判断，待人工确认：两版本的 raw/contextualized 都保留感谢态度、colleagues 群体、Steven 及 like 举例；不能把 pending 的解释问题误记为正文关系遗漏。 |
| 对朋友的感谢及 Mary 举例 | and friends like Mary | [1]/[1] | preserved | 初步判断，待人工确认：两版本的 raw/contextualized 都保留同一感谢态度、friends 群体、Mary 及 like 举例。 |

初步判断，待人工确认：仍为一条并列事实，覆盖与 v3 相同；不是条数更多才更忠实。

案例未决项：初步判断，待人工确认：原始具名命题是否为用户直接自述仍未确认；本报告显式保留该项，不能从输出 pending=[] 推导来源已经核验。。

## 配对比较

改善：

- 初步判断，待人工确认：v4 修复 raw 补用户主体；memory supports 明示引文无主体，并把必要主体补足的 assistant 来源分开引用。
- 初步判断，待人工确认：v4 去掉 v3 对 like/instance 的过度否定解释和混写主体/原始说话人的 pending，正文两组关系仍完整。

持续问题/相同观察：

- 初步判断，待人工确认：两版本正文均保留感谢对象和关系；具名内容只在 assistant 片段中可见，用户直接原话未确认这一来源限制持续存在。

本轮新增问题：

未观察到明确项。

配对解释限制：

- 初步判断，待人工确认：v4 pending=[] 未记录具名命题原始用户自述不明；应保留来源未决，不能自动判其已证实，也不因 assistant 来源自动判用户主体虚构。
