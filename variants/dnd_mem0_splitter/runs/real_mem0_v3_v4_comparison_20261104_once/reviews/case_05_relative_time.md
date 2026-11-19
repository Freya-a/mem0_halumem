# case_05_relative_time

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`2570a550-4b52-43fc-b5c4-079261785a1a`

选择理由：recently 与职位变化及机构；原始 user 发言带记录时间和额外感受，可检查时间解释及补充范围。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json#/api_snapshot/results/11`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_05_relative_time) 和 [输入](../inputs/case_05_relative_time.json)。

旧记忆原文：

```text
Recently promoted to lead director at Historical Productions Ltd
```

## v3

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_05_relative_time/v3/raw_content.txt) · [实际提示词](../runs/case_05_relative_time/v3/prompt.txt) · [逐项程序检查](../runs/case_05_relative_time/v3/program_checks.json)

初步判断，待人工确认：1 条事实、2 条 supports；未发现明确分类问题，全部旧信息覆盖。相对时间精确事件日保留为具体未决。

### 事实 1

raw：

```text
Someone was recently promoted to lead director at Historical Productions Ltd.
```

contextualized：

```text
The user was recently promoted to lead director at Historical Productions Ltd.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：人物方面，旧记忆省略主语，ctx-1 的 user 角色加第一人称 I recently got promoted 与同一事件/职位/机构明确关联，足以支持 contextualized 的 The user，也支持用户原始发言归属。两版保留晋升、lead director、Historical Productions Ltd 与 recently；没有否定、条件或可能性内容需要额外补造，没有加入来源的 exciting 感受。v3 raw 的 Someone 是未指名占位和最小语法改写，未导入 user 等身份，不能仅因新增泛称就判 RAW_CONTEXT_LEAK；v4 raw 原样保留省略形式。没有把发言日写成晋升日，且没有与 pending 的确定性冲突。

观察到的问题：未观察到明确问题。

引文 0：`memory/2570a550-4b52-43fc-b5c4-079261785a1a`

```text
Recently promoted to lead director at Historical Productions Ltd
```

supports 原文：

```text
Old memory states that someone was recently promoted to lead director at Historical Productions Ltd.
```

支持范围初审：directly_supported。初步判断，待人工确认：memory quote 原文为 Recently promoted to lead director at Historical Productions Ltd，supports 仅称 Old memory states that someone was recently promoted...，忠实描述旧记忆的事件、职位、机构与 recency；someone 不声称具体身份，也不证明现实真实性。

引文 1：`context/ctx-1`

```text
I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!
```

supports 原文：

```text
Context confirms the subject is the user (speaker), and 'recently promoted' corresponds to 'recently got promoted'; 'lead director at Historical Productions Ltd' is verbatim matched.
```

支持范围初审：directly_supported。初步判断，待人工确认：context quote 的 I recently got promoted to lead director at Historical Productions Ltd. 与 speaker=user 共同确认该同一事件的语义主体和用户直接发言；supports 中主体及逐字职位/机构比对均有依据。quote 的 It's quite exciting! 没有进入正文，不算扩写。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：精确晋升日期及 recently 的具体跨度未给出；ctx-1 recorded_at=Feb 01, 2026, 18:47:19 只是来源记录锚点，不是事件日。两版 pending=[] 未进一步标出这一具体未知，但不因此把保留 recently 的正文记为时间错误或关键遗漏。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 晋升事件 | promoted | [1]/[1] | preserved | 初步判断，待人工确认：两版的 raw/contextualized 均保留晋升事件，而非静态在职或已经离任。 |
| 晋升后职位 | lead director | [1]/[1] | preserved | 初步判断，待人工确认：保留职位 lead director，没有降低为泛称 director。 |
| 机构 | Historical Productions Ltd | [1]/[1] | preserved | 初步判断，待人工确认：保留完整机构名称与 at 关系。 |
| 相对时间 | Recently | [1]/[1] | preserved | 初步判断，待人工确认：保留 recently，不把 recorded_at 当晋升日，不使用当前日期重算。 |

初步判断，待人工确认：1 条事实保留同一晋升事件的职位、机构、时间修饰，拆成多条没有明显收益。

案例未决项：初步判断，待人工确认：精确晋升日期及 recently 的具体跨度未给出；ctx-1 recorded_at=Feb 01, 2026, 18:47:19 只是来源记录锚点，不是事件日。两版 pending=[] 未进一步标出这一具体未知，但不因此把保留 recently 的正文记为时间错误或关键遗漏。。

## v4

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_05_relative_time/v4/raw_content.txt) · [实际提示词](../runs/case_05_relative_time/v4/prompt.txt) · [逐项程序检查](../runs/case_05_relative_time/v4/program_checks.json)

初步判断，待人工确认：1 条事实、2 条 supports；未发现明确分类问题，全部旧信息覆盖。raw 更直接保留原省略表达。

### 事实 1

raw：

```text
Recently promoted to lead director at Historical Productions Ltd
```

contextualized：

```text
The user was recently promoted to lead director at Historical Productions Ltd.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：人物方面，旧记忆省略主语，ctx-1 的 user 角色加第一人称 I recently got promoted 与同一事件/职位/机构明确关联，足以支持 contextualized 的 The user，也支持用户原始发言归属。两版保留晋升、lead director、Historical Productions Ltd 与 recently；没有否定、条件或可能性内容需要额外补造，没有加入来源的 exciting 感受。v3 raw 的 Someone 是未指名占位和最小语法改写，未导入 user 等身份，不能仅因新增泛称就判 RAW_CONTEXT_LEAK；v4 raw 原样保留省略形式。没有把发言日写成晋升日，且没有与 pending 的确定性冲突。

观察到的问题：未观察到明确问题。

引文 0：`memory/2570a550-4b52-43fc-b5c4-079261785a1a`

```text
Recently promoted to lead director at Historical Productions Ltd
```

supports 原文：

```text
Old memory records a recent promotion to lead director at Historical Productions Ltd; the quote itself lacks explicit subject and tense marking.
```

支持范围初审：directly_supported。初步判断，待人工确认：supports 准确说明旧记忆记载近期晋升及职位机构，且引文本身未明确主语和有限动词时态；没有以 memory 独自验证用户身份。

引文 1：`context/ctx-1`

```text
I recently got promoted to lead director at Historical Productions Ltd.
```

supports 原文：

```text
First-person past-tense statement by speaker labeled 'user', confirming the subject ('I' → user), event (promotion), role (lead director), organization (Historical Productions Ltd), and recency ('recently').
```

支持范围初审：directly_supported。初步判断，待人工确认：quote 是用户第一人称 I recently got promoted...，同时含晋升、lead director、机构和 recently；supports 的确认范围限于这一直接自述。speaker 元数据与同主题第一人称共同作用，不是单靠角色判主体。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：精确晋升日期及 recently 的具体跨度未给出；ctx-1 recorded_at=Feb 01, 2026, 18:47:19 只是来源记录锚点，不是事件日。两版 pending=[] 未进一步标出这一具体未知，但不因此把保留 recently 的正文记为时间错误或关键遗漏。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 晋升事件 | promoted | [1]/[1] | preserved | 初步判断，待人工确认：两版的 raw/contextualized 均保留晋升事件，而非静态在职或已经离任。 |
| 晋升后职位 | lead director | [1]/[1] | preserved | 初步判断，待人工确认：保留职位 lead director，没有降低为泛称 director。 |
| 机构 | Historical Productions Ltd | [1]/[1] | preserved | 初步判断，待人工确认：保留完整机构名称与 at 关系。 |
| 相对时间 | Recently | [1]/[1] | preserved | 初步判断，待人工确认：保留 recently，不把 recorded_at 当晋升日，不使用当前日期重算。 |

初步判断，待人工确认：与 v3 相同为 1 条同一事件事实，未因更短 raw 失去任何覆盖单元。

案例未决项：初步判断，待人工确认：精确晋升日期及 recently 的具体跨度未给出；ctx-1 recorded_at=Feb 01, 2026, 18:47:19 只是来源记录锚点，不是事件日。两版 pending=[] 未进一步标出这一具体未知，但不因此把保留 recently 的正文记为时间错误或关键遗漏。。

## 配对比较

改善：

- 初步判断，待人工确认：v4 raw 原样保留旧记忆的省略表达，memory supports 也明确引文本身没有主体；这提高来源边界的可见性，但 v3 的泛称 someone 本身未构成明确身份偷补错误。

持续问题/相同观察：

- 初步判断，待人工确认：两版均保留事件、完整职位、机构和 recently，没有将记录日误作事件日，也未把兴奋感扩入正文。

本轮新增问题：

未观察到明确项。

配对解释限制：

- 初步判断，待人工确认：精确晋升日和 recently 跨度两版均未确定；这不是自动错误或遗漏。
