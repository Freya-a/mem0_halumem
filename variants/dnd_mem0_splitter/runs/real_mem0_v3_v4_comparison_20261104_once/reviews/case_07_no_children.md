# case_07_no_children

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`40c29476-81a2-477d-9e75-a2a3a92d46c7`

选择理由：简短否定状态；旧 user 家庭介绍可提供主体线索，同时含父母和关系状态等额外内容。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/20`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_07_no_children) 和 [输入](../inputs/case_07_no_children.json)。

旧记忆原文：

```text
No children
```

## v3

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_07_no_children/v3/raw_content.txt) · [实际提示词](../runs/case_07_no_children/v3/prompt.txt) · [逐项程序检查](../runs/case_07_no_children/v3/program_checks.json)

初步判断，待人工确认：1 条事实、2 条 supports。否定事实完整，但 raw 新补 The user，观察到 RAW_CONTEXT_LEAK；contextualized 的用户补足有明确来源。

### 事实 1

raw：

```text
The user has no children.
```

contextualized：

```text
The user has no children.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：旧记忆只有 No children；否定对象 children 和家庭状态均完整保留。ctx-1 的 let me introduce my family 与同一列表中的 No children 以及 speaker=user，共同支持 contextualized 的用户主体，也支持这句话出自用户；不是仅凭角色默认全部命题主体。v3 raw 新补 The user，越过仅用 memory 的来源边界；该主体在 contextualized 中有依据，不是虚构人物。v4 raw 保留省略形式。两版均没有扩入父母存活、no_relationship 等 quote 内额外细节，没有引入时间永久性、否定偏好或生育能力推断，也没有 pending 的确定性冲突。

观察到的问题：RAW_CONTEXT_LEAK。

- RAW_CONTEXT_LEAK：输入 `No children`；输出 `The user has no children.`。初步判断，待人工确认：旧 memory 没有 user 或可内部恢复的身份；v3 raw 只有借上下文才可补 The user，违反 raw 来源边界。第一人称家庭介绍使 contextualized 的同一补足合理，故不同时判无依据主体或原始说话人错误。

引文 0：`memory/40c29476-81a2-477d-9e75-a2a3a92d46c7`

```text
No children
```

supports 原文：

```text
Old memory states 'No children' as a standalone factual assertion.
```

支持范围初审：directly_supported。初步判断，待人工确认：memory supports 只说明旧记忆把 No children 记作独立断言，没有把 memory quote 说成验证用户身份、亲口自述或现实真实性。

引文 1：`context/ctx-1`

```text
Good, let me introduce my family. Both parents are alive, no_relationship, No children.
```

supports 原文：

```text
Confirms 'No children' is part of the user's self-introduction about their family; speaker is explicitly labeled 'user'.
```

支持范围初审：directly_supported。初步判断，待人工确认：quote 中 let me introduce my family 与同一 No children 自我家庭介绍，加上 speaker=user，直接支持用户来源与语义主体；supports 未扩出父母状态或关系字段。角色元数据不是唯一依据。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：本条未另列具体未决项，仍待人工复核。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 无子女的否定家庭事实 | No children | [1]/[1] | preserved | 初步判断，待人工确认：两版正文保留无子女的否定，不转换为不想要、不能生育、没有任何亲属或其他关系判断。 |

初步判断，待人工确认：单一无子女事实保持 1 条，适合原目标的粒度。

案例未决项：无另列具体未决项，仍待人工确认。

## v4

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_07_no_children/v4/raw_content.txt) · [实际提示词](../runs/case_07_no_children/v4/prompt.txt) · [逐项程序检查](../runs/case_07_no_children/v4/program_checks.json)

初步判断，待人工确认：1 条事实、2 条 supports。raw 保留原省略，contextualized 补足用户有明确同主题第一人称来源；未发现明确分类问题。

### 事实 1

raw：

```text
No children
```

contextualized：

```text
The user has no children.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：旧记忆只有 No children；否定对象 children 和家庭状态均完整保留。ctx-1 的 let me introduce my family 与同一列表中的 No children 以及 speaker=user，共同支持 contextualized 的用户主体，也支持这句话出自用户；不是仅凭角色默认全部命题主体。v3 raw 新补 The user，越过仅用 memory 的来源边界；该主体在 contextualized 中有依据，不是虚构人物。v4 raw 保留省略形式。两版均没有扩入父母存活、no_relationship 等 quote 内额外细节，没有引入时间永久性、否定偏好或生育能力推断，也没有 pending 的确定性冲突。

观察到的问题：未观察到明确问题。

引文 0：`memory/40c29476-81a2-477d-9e75-a2a3a92d46c7`

```text
No children
```

supports 原文：

```text
Old memory states 'No children' as a standalone factual claim.
```

支持范围初审：directly_supported。初步判断，待人工确认：Old memory states 'No children' as a standalone factual claim 准确说明旧记忆内容，不越过到本人直接自述。

引文 1：`context/ctx-1`

```text
Good, let me introduce my family. Both parents are alive, no_relationship, No children.
```

supports 原文：

```text
The phrase 'No children' appears in a first-person self-introduction by the speaker labeled 'user', confirming the subject of this statement is the user.
```

支持范围初审：directly_supported。初步判断，待人工确认：supports 的 first-person self-introduction 对 let me introduce my family 有据；同一来源的 No children 加 user 角色可以确定此家庭陈述的语义主体。没有把父母存活或 no_relationship 变成新增正文事实。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：本条未另列具体未决项，仍待人工复核。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 无子女的否定家庭事实 | No children | [1]/[1] | preserved | 初步判断，待人工确认：两版正文保留无子女的否定，不转换为不想要、不能生育、没有任何亲属或其他关系判断。 |

初步判断，待人工确认：与 v3 同为 1 条事实，差异是来源边界而非覆盖或粒度。

案例未决项：无另列具体未决项，仍待人工确认。

## 配对比较

改善：

- 初步判断，待人工确认：v4 将 raw 的 The user has no children 改为 No children，修复 v3 raw 身份偷补，同时保留 contextualized 中有依据的用户主体。

持续问题/相同观察：

- 初步判断，待人工确认：两版无子女否定事实完整，supports 未把来源 quote 的其他家庭信息扩入正文，且用户原始发言与主体均有同主题第一人称依据。

本轮新增问题：

未观察到明确项。

配对解释限制：

未观察到明确项。
