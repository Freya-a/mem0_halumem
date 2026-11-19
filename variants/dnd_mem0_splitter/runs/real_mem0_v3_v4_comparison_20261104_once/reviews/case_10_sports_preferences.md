# case_10_sports_preferences

**初步判断，待人工确认**。程序检查与语义初审分别记录，未改模型输出。

memory_id：`4f51947c-5cb3-419e-a04e-1142410c0b9e`

选择理由：同一句含不喜欢、态度理由及另一类运动偏好，适合区分覆盖与细分粒度。

更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/25`

完整旧上下文与来源见 [CASE_CATALOG](../CASE_CATALOG.md#case_10_sports_preferences) 和 [输入](../inputs/case_10_sports_preferences.json)。

旧记忆原文：

```text
Dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth
```

## v3

程序：passed；候选事实 2 条；逐字引文 4/4。

[原始响应](../runs/case_10_sports_preferences/v3/raw_content.txt) · [实际提示词](../runs/case_10_sports_preferences/v3/prompt.txt) · [逐项程序检查](../runs/case_10_sports_preferences/v3/program_checks.json)

2条分别保留明确因果态度和运动偏好，主体/主观看法/关键特征均覆盖。and prefers 的附加因果作用范围只列未决；未观察到确定正文错误。

### 事实 1

raw：

```text
Dislikes wrestling because finds it too confrontational.
```

contextualized：

```text
The user dislikes wrestling because they find it too confrontational.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

保留不喜欢 wrestling 的负面态度，以及 because 连接的理由；finds 仍把 too confrontational 限定为主体看法，没有改成摔跤客观上太对抗。raw 未填用户；contextualized 的 user 和 they 来自同一偏好的第一人称来源，不能仅凭 speaker 元数据而定主体，但此处 I dislike/I find 足以关联。无时间、条件或额外行动。

观察到的问题：未观察到明确问题。

引文 0：`memory/4f51947c-5cb3-419e-a04e-1142410c0b9e`

```text
Dislikes wrestling because finds it too confrontational
```

supports 原文：

```text
Old memory states a dislike of wrestling grounded in finding it too confrontational.
```

支持范围初审：directly_supported。声明的 memory 引文直接含不喜欢、because 因果和 finds 主观看法；supports 只复述这部分，不宣称来源是用户亲口陈述。

引文 1：`context/ctx-1`

```text
I dislike wrestling, because I find wrestling too confrontational and prefer sports that emphasize teamwork and personal growth.
```

supports 原文：

```text
Confirms the subject is the user (first-person speaker), and that 'finds it too confrontational' refers to the user's own judgment; also provides syntactic clarity for pronoun and verb agreement in contextualized version.
```

支持范围初审：directly_supported。ctx-1 的 I dislike/I find 与同一 wrestling 态度直接相连，结合 user 角色可支持用户主体和其主观判断；语法补全未增添实际参与运动或其他行动。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：{"type": "CAUSE_SCOPE", "reason": "and prefers 可以与 dislikes 作更高层并列，也可与 finds 一同处于 because 下。输入不能排除两种附加作用范围；明确的“不喜欢←觉得太对抗”因果在两版都保留，不能把歧义本身计成因果遗漏。"}。

### 事实 2

raw：

```text
Prefers sports emphasizing teamwork and personal growth.
```

contextualized：

```text
The user prefers sports that emphasize teamwork and personal growth.
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

保留偏好的对象为强调 teamwork 和 personal growth 的运动，两项特征均进入正文。raw 仍省略主体，补充版用户主体有 I ... prefer 依据；没有把偏好说成实际参与、擅长或职业。与 fact1 分条后仍保留明确的对抗性 because 理由；偏好本身是否也是 because 并列理由仅列歧义。无否定、日期、条件或情态新增。

观察到的问题：未观察到明确问题。

引文 0：`memory/4f51947c-5cb3-419e-a04e-1142410c0b9e`

```text
prefers sports emphasizing teamwork and personal growth
```

supports 原文：

```text
Old memory states a preference for sports with those characteristics.
```

支持范围初审：directly_supported。memory 引文直接含偏好运动和 teamwork/personal growth 两特征，supports 未添加个人体育行为或用户直接自述归属。

引文 1：`context/ctx-1`

```text
I dislike wrestling, because I find wrestling too confrontational and prefer sports that emphasize teamwork and personal growth.
```

supports 原文：

```text
Confirms the subject is the user and that the preference is active and self-attributed; 'that emphasize' clarifies the grammatical head of the noun phrase, supporting the relative clause interpretation in contextualized version.
```

支持范围初审：directly_supported。context 的第一人称 prefer 直接支持用户自我归属的当前偏好及 that emphasize 的特征结构；active 按偏好状态理解，不据此推出实际参加运动。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：{"type": "CAUSE_SCOPE", "reason": "and prefers 可以与 dislikes 作更高层并列，也可与 finds 一同处于 because 下。输入不能排除两种附加作用范围；明确的“不喜欢←觉得太对抗”因果在两版都保留，不能把歧义本身计成因果遗漏。"}。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 不喜欢摔跤 | Dislikes wrestling | [1]/[1] | preserved | 正文明确保留 dislike 的负面态度及 wrestling 对象。 |
| 太对抗为主体看法 | finds it too confrontational | [1]/[1] | preserved | 正文均保留 finds，没有把个人看法提升为类别客观断言。 |
| 不喜欢与对抗性看法的 because 理由关系 | Dislikes wrestling because finds it too confrontational | [1]/[1] | preserved | 两版正文均原样/近义保留 because；不能因事实条数不同而判该明确关系丢失。 |
| 偏好强调团队合作的运动 | prefers sports emphasizing teamwork and personal growth | [2]/[2] | preserved | 偏好与 teamwork 的对象特征联系均在正文，而非仅在引文。 |
| 偏好强调个人成长的运动 | prefers sports emphasizing teamwork and personal growth | [2]/[2] | preserved | personal growth 与 teamwork 并列作为所偏好运动的特征保留。 |
| and prefers 是否也在 because 的作用范围内 | because finds it too confrontational and prefers sports emphasizing teamwork and personal growth | [1, 2]/[1, 2] | uncertain | v3 分成对抗性理由与独立偏好；若原句将偏好也纳入 because，该附加联系会变弱，但原句也容许高层并列偏好，故列 uncertain 而不计确定错误。 |

两条有助于独立判断偏好，fact1 仍整体保留不喜欢与对抗性理由；不是只拆出理由。是否需把并列偏好连回 because 依赖语法作用范围，不能自动按遗漏计错。

案例未决项：{"type": "CAUSE_SCOPE", "reason": "and prefers 可以与 dislikes 作更高层并列，也可与 finds 一同处于 because 下。输入不能排除两种附加作用范围；明确的“不喜欢←觉得太对抗”因果在两版都保留，不能把歧义本身计成因果遗漏。"}。

## v4

程序：passed；候选事实 1 条；逐字引文 2/2。

[原始响应](../runs/case_10_sports_preferences/v4/raw_content.txt) · [实际提示词](../runs/case_10_sports_preferences/v4/prompt.txt) · [逐项程序检查](../runs/case_10_sports_preferences/v4/program_checks.json)

1条保留原复合句和全部明确信息点，粗粒度不构成遗漏。一个 supports 的 for emphasis 修辞解释超出引文直接表达。

### 事实 1

raw：

```text
Dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth
```

contextualized：

```text
User dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth
```

程序：编号=True；事实 ID=True；memory 引文=True；全部逐字引文=True。

一条正文保留 dislikes wrestling、because finds it too confrontational 和偏好强调 teamwork/personal growth 的运动；finds 的主观视角未被客观化。raw 原样保留省略主体，contextualized 的 User 可由同一段第一人称关联。没有添加实际运动行为、时间、条件或否定变化，and prefers 的语法附着歧义原样保留。

观察到的问题：SUPPORTS_OVERREACH。

- SUPPORTS_OVERREACH：输入 `I dislike wrestling, because I find wrestling too confrontational and prefer sports that emphasize teamwork and personal growth.`；输出 `Confirms the subject is the user (first-person 'I'), validates the causal structure ('because'), and matches the core attitudes and reasons; 'wrestling' is repeated for emphasis but does not alter the proposition's scope or object.`。supports 说 wrestling is repeated for emphasis；来源只显示名词重复，没有说明重复是为了强调。前面的主体/因果等结论有源，但这一修辞目的超过引文直接表达。

引文 0：`memory/4f51947c-5cb3-419e-a04e-1142410c0b9e`

```text
Dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth
```

supports 原文：

```text
Old memory records a dislike of wrestling grounded in its perceived confrontational nature, and a preference for sports highlighting teamwork and personal growth.
```

支持范围初审：directly_supported。memory 引文直接覆盖态度、主观看法、明确 because 因果和偏好特征；supports 的 perceived 保持原 finds 的主体判断，没有现实真实性或原始用户发言归属的过度声明。

引文 1：`context/ctx-1`

```text
I dislike wrestling, because I find wrestling too confrontational and prefer sports that emphasize teamwork and personal growth.
```

supports 原文：

```text
Confirms the subject is the user (first-person 'I'), validates the causal structure ('because'), and matches the core attitudes and reasons; 'wrestling' is repeated for emphasis but does not alter the proposition's scope or object.
```

支持范围初审：overreach。主语、because 结构、态度和对象均有引文直接支持；但尾句把 wrestling 的重复归因为 for emphasis。重复本身可见，修辞目的未由引文明说，属于 supports 的局部额外解释；不把这一局部问题算作正文因果遗漏。

模型 pending_confirmations（原样保留）：

```json
[]
```

初审待确认：{"type": "CAUSE_SCOPE", "reason": "and prefers 可以与 dislikes 作更高层并列，也可与 finds 一同处于 because 下。输入不能排除两种附加作用范围；明确的“不喜欢←觉得太对抗”因果在两版都保留，不能把歧义本身计成因果遗漏。"}。

覆盖与拆分粒度：

| 信息点 | 输入原文 | raw/补充事实序号 | 初审 | 理由 |
| --- | --- | --- | --- | --- |
| 不喜欢摔跤 | Dislikes wrestling | [1]/[1] | preserved | 正文明确保留 dislike 的负面态度及 wrestling 对象。 |
| 太对抗为主体看法 | finds it too confrontational | [1]/[1] | preserved | 正文均保留 finds，没有把个人看法提升为类别客观断言。 |
| 不喜欢与对抗性看法的 because 理由关系 | Dislikes wrestling because finds it too confrontational | [1]/[1] | preserved | 两版正文均原样/近义保留 because；不能因事实条数不同而判该明确关系丢失。 |
| 偏好强调团队合作的运动 | prefers sports emphasizing teamwork and personal growth | [1]/[1] | preserved | 偏好与 teamwork 的对象特征联系均在正文，而非仅在引文。 |
| 偏好强调个人成长的运动 | prefers sports emphasizing teamwork and personal growth | [1]/[1] | preserved | personal growth 与 teamwork 并列作为所偏好运动的特征保留。 |
| and prefers 是否也在 because 的作用范围内 | because finds it too confrontational and prefers sports emphasizing teamwork and personal growth | [1]/[1] | preserved | v4 一条保留完整表达及原有附着歧义，覆盖 preserved 不代表已消除歧义。 |

一条同时包含态度、理由和偏好；较粗但完整保留原句关系与歧义，不能因数量少于 v3 直接算语义退步。

案例未决项：{"type": "CAUSE_SCOPE", "reason": "and prefers 可以与 dislikes 作更高层并列，也可与 finds 一同处于 because 下。输入不能排除两种附加作用范围；明确的“不喜欢←觉得太对抗”因果在两版都保留，不能把歧义本身计成因果遗漏。"}。

## 配对比较

改善：

- v4 整体保留原句，避免分条时对 and prefers 另作句法选择；这属于对原歧义的保留，不证明 v3 明确丢失因果。

持续问题/相同观察：

- 明确的“不喜欢摔跤，因为觉得太对抗”关系、finds 的主观视角以及 teamwork/personal growth 偏好在两版正文都保留。
- 两版 raw 均未从上下文补用户主体，contextualized 的用户归属有同一偏好第一人称依据。

本轮新增问题：

- v4 的 context supports 新增 for emphasis 这一引文未说明的修辞目的，属于局部 SUPPORTS_OVERREACH；正文未受影响。

配对解释限制：

- and prefers 是否也受 because 管辖仍有语法歧义；v3 的作用范围风险与确定因果遗漏分开，v4 保留原歧义。
