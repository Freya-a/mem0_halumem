# case_08_partner_profile

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`a0890e00-0564-4490-8e5b-15b02025e910`

选择理由：同一关系对象同时含出生日期、职业和专长等可分别核查的信息。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_004/before.json#/api_snapshot/results/40`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_08_partner_profile) 和 [输入](../inputs/case_08_partner_profile.json)。

旧记忆原文：

```text
Partner was born on 1980-06-16, art curator specializing in historical artifacts
```

## v3

程序：passed；候选事实 2 条；逐字引文 2/2。

[原始响应](../runs/case_08_partner_profile/v3/raw_content.txt) · [实际提示词](../runs/case_08_partner_profile/v3/prompt.txt) · [逐项程序检查](../runs/case_08_partner_profile/v3/program_checks.json)

初步判断，待人工确认：2 条事实、2 条 supports；日期、职业、专长全部覆盖，未发现明确分类问题。两版均没有把旧 specialization 改成较弱来源措辞，也均未在 pending 披露来源强度差异。

### 事实 1

raw：

```text
Partner was born on 1980-06-16.
```

contextualized：

```text
Partner was born on 1980-06-16.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：fact1 保留 Partner 出生于 1980-06-16，人物标签和日期一致。日期是旧记忆明确生日，不是 source_context 的 Sep 04, 2025 记录时间，未转算年龄或加入地点。未增否定、条件或可能性，pending=[] 没有与正文同项冲突；memory supports 只证明旧记忆如此记载，不代表现实身份/生日已独立核验。原会话是 user 介绍 My Partner，语义主体是伴侣，不是说话用户。

观察到的问题：未观察到明确问题。

引文 0：`memory/a0890e00-0564-4490-8e5b-15b02025e910`

```text
Partner was born on 1980-06-16
```

supports 原文：

```text
Old memory states Partner's date of birth as 1980-06-16.
```

支持范围初审：directly_supported。初步判断，待人工确认：Old memory states Partner's birth date as 1980-06-16 与 memory quote 完全相符，只说明旧记忆，未宣称用户生日、原始亲口表述或现实生日已验证。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

### 事实 2

raw：

```text
Partner is an art curator specializing in historical artifacts.
```

contextualized：

```text
Partner is an art curator specializing in historical artifacts.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：fact2 在旧句内部恢复共享 Partner 主语，保留 art curator 职业和 specializing in historical artifacts 专长，两者及其从属关系都进入 raw/contextualized 正文，不能只因它们同处一条事实判遗漏。is 是原职业同位说明的最小语法恢复，没有借 source_context 加用户/姓名，也没有把兴趣 shares a passion for history 扩入正文。保持 specializing 而不替换为 keen eye，符合旧命题忠实性；旧总结与原会话证据强度不同应列待确认。没有否定、逻辑条件或可能性被改动，也没有凭空把资料当当前现实已核验。

观察到的问题：未观察到明确问题。

引文 0：`memory/a0890e00-0564-4490-8e5b-15b02025e910`

```text
art curator specializing in historical artifacts
```

supports 原文：

```text
Old memory states Partner's professional role and specialization.
```

支持范围初审：directly_supported。初步判断，待人工确认：Old memory states Partner's professional role and specialization 对旧记忆中的 art curator specializing in historical artifacts 有据；Partner 的主语由同一旧句内部共享，未借上下文偷补。该 supports 没有声称 user 原话 keen eye 已验证 specialization，故不记支持越界，但后者证据强度仍未决。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：旧记忆的 specializing in historical artifacts 比 user 原话 with a keen eye for historical artifacts 更强；keen eye 可表示鉴赏力，不能直接证明专业 specialization。两版只引用 memory 且 pending=[]，均未披露这一具体来源强度差异；需人工核实旧总结的形成依据，但不能因此改写或删除旧命题。；初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| Partner 出生日期 | Partner was born on 1980-06-16 | [1]/[1] | preserved | 初步判断，待人工确认：两版 fact1 均保留 Partner、born 和完整出生日期，未用来源记录日替换生日。 |
| Partner 职业 | art curator | [2]/[2] | preserved | 初步判断，待人工确认：两版 fact2 都从原句内部共享 Partner 主语恢复其职业 art curator，没有加入姓名或用户身份。 |
| 职业专长 | specializing in historical artifacts | [2]/[2] | preserved | 初步判断，待人工确认：两版 fact2 均保留旧记忆的 specialization 命题和 historical artifacts 对象，没有为迁就较弱原会话 keen eye 而删改为兴趣或眼光。 |

初步判断，待人工确认：两版均拆为生日 1 条、职业连同专长 1 条。art curator 和 specializing 各有可检查信息点，但关系保留且正文无遗漏；是否进一步拆成 3 条属于粒度选择，不能记 OMISSION。

案例未决项：初步判断，待人工确认：旧记忆的 specializing in historical artifacts 比 user 原话 with a keen eye for historical artifacts 更强；keen eye 可表示鉴赏力，不能直接证明专业 specialization。两版只引用 memory 且 pending=[]，均未披露这一具体来源强度差异；需人工核实旧总结的形成依据，但不能因此改写或删除旧命题。；初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

## v4

程序：passed；候选事实 2 条；逐字引文 2/2。

[原始响应](../runs/case_08_partner_profile/v4/raw_content.txt) · [实际提示词](../runs/case_08_partner_profile/v4/prompt.txt) · [逐项程序检查](../runs/case_08_partner_profile/v4/program_checks.json)

初步判断，待人工确认：2 条事实、2 条 supports；日期、职业、专长全部覆盖，未发现明确分类问题。两版均没有把旧 specialization 改成较弱来源措辞，也均未在 pending 披露来源强度差异。

### 事实 1

raw：

```text
Partner was born on 1980-06-16
```

contextualized：

```text
Partner was born on 1980-06-16
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：fact1 保留 Partner 出生于 1980-06-16，人物标签和日期一致。日期是旧记忆明确生日，不是 source_context 的 Sep 04, 2025 记录时间，未转算年龄或加入地点。未增否定、条件或可能性，pending=[] 没有与正文同项冲突；memory supports 只证明旧记忆如此记载，不代表现实身份/生日已独立核验。原会话是 user 介绍 My Partner，语义主体是伴侣，不是说话用户。

观察到的问题：未观察到明确问题。

引文 0：`memory/a0890e00-0564-4490-8e5b-15b02025e910`

```text
Partner was born on 1980-06-16
```

supports 原文：

```text
Old memory explicitly states Partner's birth date as 1980-06-16.
```

支持范围初审：directly_supported。初步判断，待人工确认：Old memory explicitly states Partner's birth date as 1980-06-16 与 memory quote 完全相符，只说明旧记忆，未宣称用户生日、原始亲口表述或现实生日已验证。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

### 事实 2

raw：

```text
Partner is an art curator specializing in historical artifacts
```

contextualized：

```text
Partner is an art curator specializing in historical artifacts
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

初步判断，待人工确认：fact2 在旧句内部恢复共享 Partner 主语，保留 art curator 职业和 specializing in historical artifacts 专长，两者及其从属关系都进入 raw/contextualized 正文，不能只因它们同处一条事实判遗漏。is 是原职业同位说明的最小语法恢复，没有借 source_context 加用户/姓名，也没有把兴趣 shares a passion for history 扩入正文。保持 specializing 而不替换为 keen eye，符合旧命题忠实性；旧总结与原会话证据强度不同应列待确认。没有否定、逻辑条件或可能性被改动，也没有凭空把资料当当前现实已核验。

观察到的问题：未观察到明确问题。

引文 0：`memory/a0890e00-0564-4490-8e5b-15b02025e910`

```text
art curator specializing in historical artifacts
```

supports 原文：

```text
Old memory explicitly states Partner's professional role and specialization.
```

支持范围初审：directly_supported。初步判断，待人工确认：Old memory explicitly states Partner's professional role and specialization 对旧记忆中的 art curator specializing in historical artifacts 有据；Partner 的主语由同一旧句内部共享，未借上下文偷补。该 supports 没有声称 user 原话 keen eye 已验证 specialization，故不记支持越界，但后者证据强度仍未决。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：初步判断，待人工确认：旧记忆的 specializing in historical artifacts 比 user 原话 with a keen eye for historical artifacts 更强；keen eye 可表示鉴赏力，不能直接证明专业 specialization。两版只引用 memory 且 pending=[]，均未披露这一具体来源强度差异；需人工核实旧总结的形成依据，但不能因此改写或删除旧命题。；初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| Partner 出生日期 | Partner was born on 1980-06-16 | [1]/[1] | preserved | 初步判断，待人工确认：两版 fact1 均保留 Partner、born 和完整出生日期，未用来源记录日替换生日。 |
| Partner 职业 | art curator | [2]/[2] | preserved | 初步判断，待人工确认：两版 fact2 都从原句内部共享 Partner 主语恢复其职业 art curator，没有加入姓名或用户身份。 |
| 职业专长 | specializing in historical artifacts | [2]/[2] | preserved | 初步判断，待人工确认：两版 fact2 均保留旧记忆的 specialization 命题和 historical artifacts 对象，没有为迁就较弱原会话 keen eye 而删改为兴趣或眼光。 |

初步判断，待人工确认：两版均拆为生日 1 条、职业连同专长 1 条。art curator 和 specializing 各有可检查信息点，但关系保留且正文无遗漏；是否进一步拆成 3 条属于粒度选择，不能记 OMISSION。

案例未决项：初步判断，待人工确认：旧记忆的 specializing in historical artifacts 比 user 原话 with a keen eye for historical artifacts 更强；keen eye 可表示鉴赏力，不能直接证明专业 specialization。两版只引用 memory 且 pending=[]，均未披露这一具体来源强度差异；需人工核实旧总结的形成依据，但不能因此改写或删除旧命题。；初步判断，待人工确认：source_context 的 My Partner 可合理指向用户的伴侣，speaker=user 是此资料发言者而非出生或职业事实的主体。输入没有伴侣姓名或可验证的真实完整身份；保持 Partner 标签，不把伴侣等同用户本人，也不从资料真实性作额外推断。。

## 配对比较

改善：

未观察到明确项。

持续问题/相同观察：

- 初步判断，待人工确认：两版除句末标点及 supports 的 explicitly 等措辞外，事实内容与拆分粒度实质一致；三个覆盖单元全部 preserved。
- 初步判断，待人工确认：两版均保留 specializing 旧命题并仅声称 memory 记载，但 pending 都未披露 specialization 与原会话 keen eye 的证据强度差异；当前记录为具体未决，不将不确定自动计为错误。

本轮新增问题：

未观察到明确项。

配对解释限制：

- 初步判断，待人工确认：需核实原会话 keen eye 是否足以支撑旧总结的专业 specialization，以及伴侣真实身份；不能补入分享历史热情，也不能因此删改现有旧命题。
