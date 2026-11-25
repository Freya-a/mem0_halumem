# v5 五案：字段与语义离线归因

## 边界、定义和方法

本报告只读取五案原始请求、原始响应、v5 保存的审核和现有代码；不调用模型或 API，不修改旧结果、Mem0 或真实记忆。逐条核对 21 条事实与 15 条关系。模型原始输出和旧审核原样保留；本轮的字段表达建议是独立人工分析，不输入对齐器、规划器或任何授权链路。请求消息、原始响应、先前审核逐条哈希及代码快照均经校验。

`unconditional` 在 v5 提示词中要求“证据明确无额外适用限制”；在规划器实现中，`_conditions` 把它解析为 `(None, [()])`，其含义是**对本次实际比较的条件维度没有约束**。当旧条件为 unconditional 且新条件为有限范围时，代码将有限范围视为可能重叠，但不把无限余集枚举成完整有限范围。它不是日期字段，也不会自动从 subject、attribute 或 value 中删除 `simulated`、`current`、`recently` 等文字；但是规划器不理解这些文字。如果比较所需的轴没有被结构化或声明，代码也不能自动保证这些限定被纳入范围运算。

应区分三个情况：①原文**明确否定某个已声明比较轴的限制**时，才有证据在该轴上声称无限定，例如“所有指定门店均适用”；这不证明所有时间、主体或其他轴均无限定。②原文对该轴未提及，范围是未知，不能从空白推出无限定。③原文明确“当前”“模拟”“该次活动”等限定时，必须保留该限定；它可能已经在 subject、attribute、value 里，也可能需要在明确且可表示的比较轴上使用 finite。事件日期不明并不自动否定事件或迫使所有语义判断失败。

旧审核全部判为 partial 或 unsupported，其中若干仅笼统说“完整 unconditional 未证”，没有指明相关比较轴；本报告原样保留该结论，并标出需澄清标准的记录。**不能据此倒推 36 条事实都是错误，也不能统一改成 unknown 后宣布正确**：例如模拟限定已在值中，但某些关系仍错误地把模拟体验推成真实偏好变化。

统计的口径：①沿用旧审核的 core_verdict，partial 或 unsupported 计入“内核不完全受支持”；②主体、身份、取值或关系判断存在扩写，另单列仅在理由发现的扩写；③分开统计已知限定丢失/扩大、已编码、原文未提，且把所有 `unconditional` 的证据充分性列为待核实而不自动计错；④只计无依据的时间或因果推断，原话支持的因果不计；⑤记录能具体指出的 schema、映射或提示词契约边界与缺口，包括刻意保守但需解释的映射，另列旧审核标准需明确比较轴。类别允许重叠，计数基于研究者逐条标注，不是性能或准确率。

| 归因口径 | 记录数 / 36 | 说明 |
|---|---:|---|
| ①内核未完全支持 | 19 | 沿用旧审核 core_verdict；事实和关系均计 |
| ②身份、主体、取值或关系扩写 | 19 | 不将仅出现在理由的扩写计入此行 |
| ②仅在理由中发现扩写 | 3 | 与上一行分列 |
| ③原文明示限定丢失或扩大 | 8 | 不把已嵌入值中的限定计入此项 |
| ③unconditional 未有逐轴明确的无限定证明 | 36 | 待核实，不等价于 36 项均错误 |
| ④时间或因果推断缺依据 | 16 | 有原文支持的时间及因果不计 |
| ⑤具体 schema／映射约束或缺口 | 14 | 含需澄清的保守映射，不均为实现错误 |
| ⑤旧审核范围标准需澄清轴 | 16 | 需复核，不自动推翻旧审核 |
| 至少两类主要原因重叠 | 22 | 主要原因只含①②③明确限定丢失④⑤具体契约 |

③限定处理分类：已在主体、属性或值中表达 16 条；明示限定丢失或扩大 8 条；相应比较范围未提及 12 条。36 条原始条件字段均为 unconditional；这不等于 36 条都已被证明错误。

| 主要原因交集 | 记录数 |
|---|---:|
| ①内核 ∩ ②扩写 | 19 |
| ①内核 ∩ ③丢限定 | 5 |
| ①内核 ∩ ④无依据时序因果 | 13 |
| ①内核 ∩ ⑤契约 | 9 |
| ②扩写 ∩ ③丢限定 | 5 |
| ②扩写 ∩ ④无依据时序因果 | 13 |
| ②扩写 ∩ ⑤契约 | 9 |
| ③丢限定 ∩ ④无依据时序因果 | 7 |
| ③丢限定 ∩ ⑤契约 | 4 |
| ④无依据时序因果 ∩ ⑤契约 | 8 |

## 独立语义授权的实际来源

v5 `interface.analyze()` 对每条适配结果直接设置 `semantic_support="unknown"`；`_new_basis()` 从模型选定的引文机械生成新侧依据，证明可绑定，不证明语义。规划器要求 `semantic_support="supported"` 且语义依据能绑定有效引文，才可能继续处理新增或旧关系；本轮保存的 36 个模型候选均为 unknown。v5 运行流程中 `HUMAN_REVIEW.json` 由事后报告脚本读取，不被 runner 或 adapter 读取，不能算自动授权。当前链路没有产生独立语义授权的组件：要启用该路径，需要另一个可追溯、作用于具体主张的独立审核方及其授权契约；不能把模型的 rationale、引文定位或换名后的模型判断当授权。

另有两个实现边界：新事实新增分支在语义授权等检查通过后，会把 `new_conditions` 原样作为 scope，但不会调用 `_conditions()` 验证 unknown 范围，因此 unknown 不是自动阻止新增的保证；旧关系的范围路径则会对 unknown 标待确认。`unrelated` 还要求 `no_impact_confirmed`，v5 模型 schema 没有提供独立审核签发该字段的路径；模型所称“属性不同”不等价于旧事实已确认不受影响。

## 最少必要修改建议（仅建议，未实施）

1. **明确现有条件契约和审核口径。** 在提示词、schema 文档和审核表中列出本次要比较的维度及其证据：明确无限定、未提及和有具体限定分别处理；限定已在主体/属性/值中时标明其位置，不要求无意义地重复。只有相关轴明确且有证据时才用 unconditional。若要让代码保证这一点，需要下游共同读取和检查轴与依据，不能只加一段提示词。
2. **补充事实时间的最小表示，并明确标量与拆分。** 可增加可选、来源绑定的事件时间字段（例如相对发话已发生 / 计划 / 未知及对应引文），保持现有 `temporal_order` 专用于新旧事实有效时间比较；没有必要推断具体日期。明确 `value` 是字符串或 null；对合取要求拆成可核验子事实时保留同一实体及合取关系。现有规划器不会自动消费新增字段，未来需适配、验证与测试。
3. **在模型外定义独立授权边界。** 分开审核新事实与旧影响，绑定输入记录、引文、范围和审核者/证据；模型理由只能是候选。未获得独立授权的关系保持待确认。保留原始输出与人工作业分离，修补无关关系的 no-impact 授权表达；这不是让审核结果悄悄进入本次自动链路。

## susan

旧记忆 `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`）：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

- 选中新话语 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`）：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.
- 选中新话语 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`）：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.

字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{"attribute":"support for well-being","conditions":{"kind":"unknown"},"subject":"current role","value":"not as much as I'd like"}`。current 已在主体中、比较对象已在值中；若尚未确定参与比较的其他轴，unknown 不会抹去这些词。找新工作的两个要求需分别核对且保留同一职位的合取。

### 新事实

**事实 f1**（记录哈希 `4c306805452100d684d2054361b90e88d1e42296c5ecaa509bb5f45c8bbb52ee`）

原模型输出：
```json
{
  "fact_id": "f1",
  "subject": "Susan",
  "attribute": "support",
  "value": "invaluable",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable."
    }
  ],
  "rationale": "Direct attribution of 'invaluable' to Susan's support in user's own words.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/manually_mapped_new]`："Susan's support has indeed been invaluable."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；用户称 Susan 的支持十分宝贵；完整 unconditional 适用范围没有独立证明。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：保留 Susan／support／invaluable；原文没说支持在任何比较维度上均无限制，若要做范围运算而未声明轴则条件未知。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：原审核只说完整无条件范围未证明；没有指出具体轴，不能把它等价为事实内核错误。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f2**（记录哈希 `db450e2dab84f5dfe67f1d5cdb96dedd2ce235cf883fe204e156c5e12df53b76`）

原模型输出：
```json
{
  "fact_id": "f2",
  "subject": "Susan",
  "attribute": "encouragement",
  "value": "helps me stay focused on my goals",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Her encouragement helps me stay focused on my goals."
    }
  ],
  "rationale": "Direct causal claim about Susan's encouragement enabling goal focus.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/manually_mapped_new]`："Her encouragement helps me stay focused on my goals."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；用户称她的鼓励帮助自己专注目标；单独作用域为 unconditional 缺充分依据。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：保留 Susan 的鼓励帮助用户专注其目标；原文未声明适用范围，待比较轴确定后再判断。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：上一轮没有指明哪一个范围轴使该断言过宽，不能仅凭完整范围未证实否认内核。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f3**（记录哈希 `59b8264ee810b80d0116dcd41bce6bcc6f21ab28b33fa620ced80f9108cf0da3`）

原模型输出：
```json
{
  "fact_id": "f3",
  "subject": "Daniel",
  "attribute": "insights",
  "value": "pushed me to think outside the box in my career",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "And Daniel's insights have really pushed me to think outside the box in my career."
    }
  ],
  "rationale": "Direct attribution of cognitive impact (thinking outside the box) to Daniel's insights.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/manually_mapped_new]`："And Daniel's insights have really pushed me to think outside the box in my career."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；Daniel 的见解促使用户在职业上跳出固有思路；完整无条件范围未证明。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留主体 Daniel、其见解、用户职业思考；career 已在 value 中，其他比较维度未知，不要丢掉 career。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：职业限定已由值表达；不必机械认为没有条件轴就将该内核判错。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f4**（记录哈希 `ed52799376e164269f8ffdcb7e7fe07b2ff80034cb603dabe13b1e24c8f64efb`）

原模型输出：
```json
{
  "fact_id": "f4",
  "subject": "connections (Susan, Daniel, etc.)",
  "attribute": "effect",
  "value": "opened up new possibilities",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "It's been exciting to see how these connections have opened up new possibilities."
    }
  ],
  "rationale": "User explicitly states 'these connections' (referring to Susan and Daniel just mentioned) caused new possibilities.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/manually_mapped_new]`："It's been exciting to see how these connections have opened up new possibilities."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `partial`；用户说这些联系开辟了可能性，但将这些联系明确扩展为 Susan、Daniel 等的完整集合及无条件范围仍是推断。
- ① 内核：`partial`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把 these connections 写为 Susan、Daniel、etc. 的具体集合超出单句可证范围；前文可提供指代线索但不证明集合完整。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：保留原句指称 these connections；集合的确切成员待确认，未提及的范围轴未知。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：代词解消与适用条件是不同问题；unconditional 不会修复主体集合扩写。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**事实 f5**（记录哈希 `8e4e7b451bf6a665193e028939e5630a89db74b307b082fdc2bf23cc37cb9f3a`）

原模型输出：
```json
{
  "fact_id": "f5",
  "subject": "current role",
  "attribute": "support for well-being",
  "value": "not as much as I'd like",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "my current role isn't supporting my well-being as much as I'd like"
    }
  ],
  "rationale": "Direct comparative evaluation of current role's impact on well-being.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/unsplit-new-0]`："my current role isn't supporting my well-being as much as I'd like"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；原话明确限定当前岗位和相对本人期望；无条件范围不应理解为永久。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留 subject=current role、比较对象 as much as I would like；当前角色已在主体中，时间持续区间未给出。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：current 已在 subject 中；unconditional 不是代码自动把 subject 改为所有岗位，但未知其他范围时仍不应证明所有比较维度无限制。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f6**（记录哈希 `0c179188dcbd733d86d1ab54df300883b4a4a1a988f359cce63a4f9c45b65d38`）

原模型输出：
```json
{
  "fact_id": "f6",
  "subject": "job search goal",
  "attribute": "requirements",
  "value": [
    "better work-life balance",
    "aligns with humanitarian goals"
  ],
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "planned",
  "quotes": [
    {
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
    }
  ],
  "rationale": "Explicit statement of intended future job criteria; 'crucial' signals commitment but not yet realized.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/unsplit-new-0]`："It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；用户表达找兼顾平衡与人道目标的工作的计划；new_value 是数组，不符合接口标量，且两个条件没有分为独立记录。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：分别表示同一个期望新工作需要更好平衡、符合人道目标；两项必须保留合取，modality=planned。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：模型 value 为数组；v4 校验要求标量字符串，但 v5 提示词未明确写出 value 的类型，也未说明拆开后需保留同一工作的合取。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

### 新旧关系

**关系 r1**（记录哈希 `b96e0a8f808d727a4950b7e37e9049e3440b9995b068b317e2951bf5731ae073`）

原模型输出：
```json
{
  "relation_id": "r1",
  "fact_id": "f1",
  "unit_id": "support",
  "relation": "same",
  "old_subject": "Susan",
  "old_attribute": "provides support and encouragement",
  "old_value": "support and encouragement",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "support",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement"
    }
  ],
  "affected_part": "support",
  "temporal_order": {
    "relation": "unknown",
    "basis": [],
    "explanation": null
  },
  "rationale": "New fact affirms Susan's support (qualifying it as 'invaluable'), consistent with old unit stating she 'provides support'. No contradiction or change in core attribute; 'invaluable' is an intensifier, not a replacement.",
  "semantic_basis": [
    {
      "side": "old",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement"
    },
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable."
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support]`："provides support and encouragement"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`。
- 关联新事实逐字引文 `[new-2/manually_mapped_new]`："Susan's support has indeed been invaluable."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`unsupported`；内核 `unsupported`；评价支持珍贵与旧事实“提供支持和鼓励”不是同属性同值的 same；原话无充分依据证明两个状态在完整范围同值。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把“支持有价值”当成与“提供支持和鼓励”同值；可以补充评价，但 same 的精确同属性同值要求未满足。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：旧支持事实与新支持评价属性不同；不应填 same，旧影响可暂记 unknown；旧范围轴未说明。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：schema 的 same 需要相同主体、属性和值；自然语言“相容”不等于该枚举的 same。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**关系 r2**（记录哈希 `74f54456369af65116c1a4d85cce34f2147b962fe1c670930f381caba6b5d0be`）

原模型输出：
```json
{
  "relation_id": "r2",
  "fact_id": "f2",
  "unit_id": "support",
  "relation": "supplement",
  "old_subject": "Susan",
  "old_attribute": "provides support and encouragement",
  "old_value": "support and encouragement",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "support",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement"
    }
  ],
  "affected_part": "encouragement",
  "temporal_order": {
    "relation": "unknown",
    "basis": [],
    "explanation": null
  },
  "rationale": "New fact specifies *how* Susan's encouragement functions ('helps me stay focused on my goals'), adding functional detail not present in the generic 'encouragement' in the old unit.",
  "semantic_basis": [
    {
      "side": "old",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement"
    },
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "Her encouragement helps me stay focused on my goals."
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support]`："provides support and encouragement"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`。
- 关联新事实逐字引文 `[new-2/manually_mapped_new]`："Her encouragement helps me stay focused on my goals."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；鼓励帮助专注可以补充旧支持事实，但无条件旧范围及跨引文关系仍须核对；模型 supplement 被适配为旧影响 unknown。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：Susan 的鼓励可补充功能细节；保持 supplement 并将其对旧断言的影响单独设 unknown，比较范围未说明。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：模型 supplement 被 v5 适配成旧影响 unknown；旧审核认为范围未证，但未指出具体比较维度。（具体契约边界标记：True；旧审核范围口径需澄清轴：True）

**关系 r3**（记录哈希 `0f9ebbacc008ff875424a6c72f7035b7fbe6f7ba1cb6ce9b5ce8bd0bd6598443`）

原模型输出：
```json
{
  "relation_id": "r3",
  "fact_id": "f1",
  "unit_id": "friendship",
  "relation": "unrelated",
  "old_subject": "ThomasSusan",
  "old_attribute": "friend named",
  "old_value": "ThomasSusan",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "friendship",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "friend named ThomasSusan"
    }
  ],
  "affected_part": null,
  "temporal_order": {
    "relation": "unknown",
    "basis": [],
    "explanation": null
  },
  "rationale": "Fact f1 concerns Susan's support quality; old unit concerns naming/identity of 'ThomasSusan'. No semantic overlap in subject or attribute.",
  "semantic_basis": [],
  "uncertainties": []
}
```
- 旧文逐字引文 `[a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship]`："friend named ThomasSusan"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`。
- 关联新事实逐字引文 `[new-2/manually_mapped_new]`："Susan's support has indeed been invaluable."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`unsupported`；内核 `unsupported`；把 Susan 支持与 ThomasSusan 朋友关系判为主体完全无重叠不可靠；旧记忆完整原文明示 Susan 称呼，短旧引文不足以支持该结论。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：模型理由断言主体无交集，但完整旧文提供 Susan 的称呼；不能据短引文断言身份不相关。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：旧文完整记忆明确 ThomasSusan referred to as Susan；属性不同不等于主体不同，关系及无影响仍需判断。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：模型把 unrelated 当属性不同；规划器 unrelated 表示旧事实无影响并需要 no_impact_confirmed，两个定义未对齐。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**关系 r4**（记录哈希 `700e123de0940624119cf14edc11cd749e3e95c58ffa87b7564698b4a0292121`）

原模型输出：
```json
{
  "relation_id": "r4",
  "fact_id": "f2",
  "unit_id": "friendship",
  "relation": "unrelated",
  "old_subject": "ThomasSusan",
  "old_attribute": "friend named",
  "old_value": "ThomasSusan",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "friendship",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "friend named ThomasSusan"
    }
  ],
  "affected_part": null,
  "temporal_order": {
    "relation": "unknown",
    "basis": [],
    "explanation": null
  },
  "rationale": "Fact f2 concerns Susan's encouragement effect; old unit concerns naming/identity. No shared semantic content.",
  "semantic_basis": [],
  "uncertainties": []
}
```
- 旧文逐字引文 `[a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship]`："friend named ThomasSusan"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`。
- 关联新事实逐字引文 `[new-2/manually_mapped_new]`："Her encouragement helps me stay focused on my goals."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`。
- 旧审核：`unsupported`；内核 `unsupported`；与上一条同理，功能不同不等于主体必然无关；不能单靠短旧引文认证无影响。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：模型说 no shared semantic content，不能由属性不同推出关系主体和旧影响均无关。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：旧朋友关系与鼓励功能分别判断；完整旧文包含 Susan 指称，旧范围轴未说明。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：unrelated 在提示词中不够区分“不同属性”和“可证明无旧影响”，规划器需要额外确认。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

## promotion

旧记忆 `e13b825e-7ec7-4760-821e-0581d8da5650`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`）：Works at Historical Productions Ltd. as a Director

- 选中新话语 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{"attribute":"promotion event","conditions":{"kind":"unknown"},"old_relation":"unknown","subject":"I","temporal_order":{"relation":"unknown"},"value":"recently promoted to lead director at Historical Productions Ltd."}`。recently 是相对话语的事件时间；与旧 Director 的先后和是否排斥另判。old_relation 为解释性标签，不是 v5 事实字段。

### 新事实

**事实 f1**（记录哈希 `ffff4b10499b34c7a69e6062b883ff3ae915c72fb62c08fe21f54a8624b58eba`）

原模型输出：
```json
{
  "fact_id": "f1",
  "subject": "I",
  "attribute": "employer",
  "value": "Historical Productions Ltd.",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "rationale": "The speaker explicitly names 'Historical Productions Ltd.' as the employer in the context of a recent promotion, confirming current employment there.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；话语在晋升语境中明确公司；当时公司关联有依据，持续现职和完整无条件范围不能由此保证。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：从晋升时 at 公司推断不受时间限定的 current employment 过强。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：表达用户在所述晋升语境中与 Historical Productions Ltd. 的雇佣关联；其后持续期未给出；为关系比较单列事件时间。
- ④ 时间或因果：晋升在发话前 recently，不能证明当前雇佣连续或晚于旧事实。（无依据推断标记：True）
- ⑤ 字段与审核标准：现有 schema 没有事实有效时间与相对发话事件时间分开的字段；unconditional 也不能表达这个差异。（具体契约边界标记：True；旧审核范围口径需澄清轴：True）

**事实 f2**（记录哈希 `b66a5ed9843e4f37d3faa4a216b3d86043960ef948232793816d39185cba31dd`）

原模型输出：
```json
{
  "fact_id": "f2",
  "subject": "I",
  "attribute": "title",
  "value": "lead director",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "rationale": "The speaker states they 'got promoted to lead director', asserting current holding of that title.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；话语支持晋升为 lead director；不要将其无条件推广到所有时间。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：表达最近晋升所得 lead director，保留该事件与公司和相对发话的时间；职位何时起止未知。
- ④ 时间或因果：理由将最近晋升推成发话时仍担任；所引文字未明确给出持续区间。recently 不决定相对旧职位事实的先后。（无依据推断标记：True）
- ⑤ 字段与审核标准：条件维度与职位值中的时间语义界限没有明确，旧审核须列明所担心的时间轴。（具体契约边界标记：True；旧审核范围口径需澄清轴：True）

**事实 f3**（记录哈希 `6824fc8bab555914a86a86591269a17e781b54dbbd3ef790b358ec973b25d344`）

原模型输出：
```json
{
  "fact_id": "f3",
  "subject": "I",
  "attribute": "employment_status",
  "value": "promoted",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "rationale": "The verb 'got promoted' is an asserted past event indicating a change in role; 'recently' modifies timing but does not alter the factual assertion of promotion having occurred.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；got promoted 表示发话前已发生晋升；相对旧职位有效时间仍未知，模型值未保留 recently。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：表达用户最近晋升至 lead director、关联该公司；晋升目标和 recently 未在此条值中体现。
- ④ 时间或因果：仅可判断事件在发话前最近发生；相对旧事实顺序未知。（无依据推断标记：False）
- ⑤ 字段与审核标准：事实与事件时间缺少专用字段；若跨事实引用目标职位，需明确事件关联而非假装同条已含。（具体契约边界标记：True；旧审核范围口径需澄清轴：True）

### 新旧关系

**关系 r1**（记录哈希 `ca2293518102ec1c311510968c2b4d025627498152325b68c735b805d84c3ef1`）

原模型输出：
```json
{
  "relation_id": "r1",
  "fact_id": "f1",
  "unit_id": "employer",
  "relation": "same",
  "old_subject": "I",
  "old_attribute": "employer",
  "old_value": "Historical Productions Ltd.",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "employer",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Historical Productions Ltd."
    }
  ],
  "affected_part": "Historical Productions Ltd.",
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I recently got promoted to lead director at Historical Productions Ltd."
      }
    ],
    "explanation": "The new statement affirms continued employment at the same company; 'recently promoted' implies continuity of employer, not replacement. No temporal displacement relative to old fact is indicated — both refer to current affiliation."
  },
  "rationale": "Employer remains unchanged; new quote confirms same entity without qualification or contrast.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "Historical Productions Ltd."
    },
    {
      "side": "old",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Historical Productions Ltd."
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e13b825e-7ec7-4760-821e-0581d8da5650/employer]`："Historical Productions Ltd."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `partial`；两侧出现同公司，但同一时刻和持续雇佣不是单凭公司名与晋升话语可以独立证实；旧关系本身有原文。
- ① 内核：`partial`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：名称重复本身不证明整个雇佣关系的持续与同刻成立。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：两侧公司名称相同可保留为公司名一致；持续雇佣及同一有效时间分别未知。
- ④ 时间或因果：same 时间假设和持续雇佣未被新旧有效期证实。（无依据推断标记：True）
- ⑤ 字段与审核标准：same 值相同与同一有效时间是不同判断；缺少明确有效时间表示。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**关系 r2**（记录哈希 `17c4fc9b49f52ffc2c9249cecbfeadbe0468106e9f9d5ba22dd518dbd10fa258`）

原模型输出：
```json
{
  "relation_id": "r2",
  "fact_id": "f2",
  "unit_id": "title",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "title",
  "old_value": "Director",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "title",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Director"
    }
  ],
  "affected_part": "Director",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "recently got promoted"
      }
    ],
    "explanation": "'Recently got promoted to lead director' indicates the new title succeeded the prior one; 'promoted' entails replacement of former title, and 'recently' signals temporal succession after the prior state."
  },
  "rationale": "New title 'lead director' is more specific and hierarchical relative to 'Director'; 'promoted to' signals replacement, not coexistence. The old unit states 'Director' without modifiers; no evidence supports concurrent holding.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "lead director"
    },
    {
      "side": "old",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Director"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e13b825e-7ec7-4760-821e-0581d8da5650/title]`："Director"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；recently 相对发话而非旧事实有效时间；lead director 更具体也不证明宽泛 Director 失效。模型 after 和替代理由不足。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：更具体的 lead director 不必否定旧的 Director；不能推断替代。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：新话语中的晋升事件可记录；Director 是否仍为宽泛称谓、是否应覆盖、相对旧事实先后均待确认。
- ④ 时间或因果：recently 只相对发话，不证明新状态晚于旧记忆事实的有效时间。（无依据推断标记：True）
- ⑤ 字段与审核标准：change 需要值排他和时序证据；引文可定位不验证这些语义。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

## career_history

旧记忆 `05afde13-35bd-4d26-bbae-6de427d58db1`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`）：Previously worked as a senior developer in Blockchain Tech

- 选中新话语 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- 选中新话语 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`）：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.

字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{"attribute":"initial clients","conditions":{"kind":"unknown"},"subject":"my consulting firm","value":"secured some initial clients"}`。主语忠于“my consulting firm”，并不声明用户是所有者或创办者；获客事实不能由 founder/owner 的原候选改一个条件字段就得到。

### 新事实

**事实 f1**（记录哈希 `1b940476ee3481ba5e1f08b048885ceeb5353c3cf71bfddd543181cf4adb5704`）

原模型输出：
```json
{
  "fact_id": "f1",
  "subject": "I",
  "attribute": "employment status",
  "value": "founder/owner of a consulting firm",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
    }
  ],
  "rationale": "The speaker refers to 'my consulting firm' and its securing of 'initial clients', indicating current ownership or leadership role in that firm; no indication this is hypothetical or planned.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；my consulting firm 与获客不证明用户是创办者、所有者或该公司的当前雇员。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：my consulting firm 不证明 founder、owner 或本人雇员身份。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：所选原句支持“用户所称咨询公司获得初始客户”；没有单独结构化该事件，条件轴未明确。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：核心身份错误，不能通过调整 unconditional 或单纯补日期修复。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**事实 f2**（记录哈希 `3e2f2010e1a65956ccc5399785299773c38fedaa8a9a7ff2513fe3225465f82d`）

原模型输出：
```json
{
  "fact_id": "f2",
  "subject": "I",
  "attribute": "professional domain",
  "value": "political consulting",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
    }
  ],
  "rationale": "The assistant's response (new-1) explicitly labels the firm as 'political consulting', and the user does not correct or qualify this — and later confirms it via vision ('key player in political consulting', new-8), services ('digital campaign strategies', new-10), and impact goals ('shaping political discourse', new-28). The user's own utterances consistently treat the domain as established fact, not aspiration.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；已选 new-0 引文并未说 political consulting；理由援引其他未选来源，不能借其作为该条证据。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：模型给出 political consulting，引用却没有；其他对话仅为上下文，不能当成该条已绑定证据。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：选中的 new-0 只说 consulting firm 获客；政治咨询领域不在该引文内，不可使用未选来源冒充其直接证据。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：逐字引文存在与能够支持取值是两项检查；当前校验只证明前者。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**事实 f3**（记录哈希 `f762b72884e26f6cdc5651f0ff9b6ae8f7da2523ba846145d1e45587188386c7`）

原模型输出：
```json
{
  "fact_id": "f3",
  "subject": "I",
  "attribute": "relationship with MooreSandra and GonzalezMary",
  "value": "they were instrumental in opening doors for my firm",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."
    }
  ],
  "rationale": "Direct attribution of instrumental role and door-opening effect, stated in past tense but grounded in recent, completed action ('finally secured some initial clients' in new-0 implies prior enabling events).",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/unsplit-new-2]`："MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `partial`；两名联系人及其关系打开机会有用户引文；合并两人，且“为公司打开”较原话更具体，未分别结构化。
- ① 内核：`partial`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：模型把两个人合为一条，并把“为我打开想不到的门”具体化为“为公司打开”。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：两位联系人各自作用如可确认需分别表达；仅保留他们很有帮助、其关系打开原话所说的机会，是否为公司未知。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：True）
- ⑤ 字段与审核标准：同一引文中的并列主体是否拆分及复数事实如何绑定，schema 和提示词需说清。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**事实 f4**（记录哈希 `ab7023f7f70a32420c14bf20ce8c49220088c8a20b23a3562164dd1203f797ab`）

原模型输出：
```json
{
  "fact_id": "f4",
  "subject": "I",
  "attribute": "current focus",
  "value": "maintaining relationships crucial for firm's growth",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "I'm focusing on maintaining these relationships as they are crucial for my firm's growth."
    }
  ],
  "rationale": "Present continuous 'I'm focusing' expresses current active priority; 'these relationships' refers back to MooreSandra and GonzalezMary, and 'crucial for my firm's growth' specifies purpose.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/unsplit-new-2]`："I'm focusing on maintaining these relationships as they are crucial for my firm's growth."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；用户说正专注维系这些关系并认为其对公司增长重要；客观上是否确实重要及无条件范围未独立证明。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留用户当前专注维持这些关系，以及用户认为其对公司增长重要；current focus 已在属性中。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：主观判断应标记为用户观点；当前时点已编码，不能只凭 unconditional 就认定主体条件全丢。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

### 新旧关系

**关系 r1**（记录哈希 `2b0d6c66996f2d3a1d2436fd01ccf7fa4d373c945852e92ce28d8d78c782644b`）

原模型输出：
```json
{
  "relation_id": "r1",
  "fact_id": "f1",
  "unit_id": "employer",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "employer",
  "old_value": "Blockchain Tech",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "employer",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "Blockchain Tech"
    }
  ],
  "affected_part": "Blockchain Tech",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients."
      }
    ],
    "explanation": "The phrase 'finally secured' implies completion of a recent transition; 'lately' situates relief in present time, after the event. This contrasts with the old memory's 'Previously worked', which explicitly marks prior employment."
  },
  "rationale": "The new fact asserts current operation of 'my consulting firm', while the old unit states 'Previously worked as a senior developer in Blockchain Tech'. 'Previously' signals temporal displacement, and 'my consulting firm' implies current primary professional identity distinct from prior employer.",
  "semantic_basis": [
    {
      "side": "old",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "Previously worked"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[05afde13-35bd-4d26-bbae-6de427d58db1/employer]`："Blockchain Tech"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；新事实本身的创办/所有者身份无依据，获客不证明更换雇主；旧历史本身不应删除。语义依据还引用了不在绑定旧短引文中的 Previously worked。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：咨询公司获客不能证明 founder、owner、现雇主切换。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：旧记忆是以前在 Blockchain Tech 工作的历史；保持该历史，获客不证明新雇主身份或对旧历史的影响。
- ④ 时间或因果：finally、lately 不能证明获客与旧历史有效期先后或工作不兼容。（无依据推断标记：True）
- ⑤ 字段与审核标准：旧单元短引文仅 Blockchain Tech，模型 semantic_basis 引用 Previously worked 不在绑定旧引文中；旧记忆上下文可见但不能假装该引文已绑定。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**关系 r2**（记录哈希 `75bce0dc33528a09d5d953a42efb21eae63d0de1cc7f5eb4bba04ed1a9fc9681`）

原模型输出：
```json
{
  "relation_id": "r2",
  "fact_id": "f1",
  "unit_id": "title",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "title",
  "old_value": "senior developer",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "title",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "senior developer"
    }
  ],
  "affected_part": "senior developer",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
        "quote": "Previously worked"
      }
    ],
    "explanation": "'Previously worked' establishes the old title as no longer current; new fact affirms current role as founder/owner of a consulting firm — incompatible with continuing as a senior developer at Blockchain Tech."
  },
  "rationale": "The old unit anchors 'senior developer' to 'Blockchain Tech' in the past; the new fact anchors 'my consulting firm' to present activity. No evidence suggests dual concurrent roles; 'finally secured' and 'lately' reinforce recency and current relevance of the new role.",
  "semantic_basis": [
    {
      "side": "old",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "Previously worked"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[05afde13-35bd-4d26-bbae-6de427d58db1/title]`："senior developer"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；新身份无依据；过去 senior developer 并不与新活动必然互斥，也未证明顺序或替换。所引旧时间依据未绑定，新侧时间依据缺失。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把 founder/owner 当已确认职位且假定与 senior developer 不兼容。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：旧 senior developer 是历史职位；没有证据证明新活动替代该历史或二者排他。
- ④ 时间或因果：过去工作语句不能独立证明新职位时间先后或排他；时间依据仅旧侧且超出已绑定引文。（无依据推断标记：True）
- ⑤ 字段与审核标准：旧侧历史限定在完整旧文而非指定短引文中；关系需要合规绑定，不应从其他单元补造引用。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

## transition

旧记忆 `e6ab178b-c0f9-4adb-bfb7-e4648617a950`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`）：Looking for a new job with better work-life balance

- 选中新话语 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`）：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.

字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{"attribute":"career event","conditions":{"kind":"unknown"},"old_relation":"unknown","subject":"I","temporal_order":{"relation":"unknown"},"value":"transitioned to a new role"}`。已转岗是事实事件，是否仍求职未知；不把该值改写为 no longer searching。old_relation 为说明，非事实 schema 字段。

### 新事实

**事实 f1**（记录哈希 `cb906fdf27bfc7123b3007db4d96d564030ff54c4be69eef1d08fdcf9379f9f7`）

原模型输出：
```json
{
  "fact_id": "f1",
  "subject": "I",
  "attribute": "job search status",
  "value": "no longer searching",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I've finally transitioned to a new role, and it's been a huge relief."
    }
  ],
  "rationale": "The phrase 'finally transitioned to a new role' asserts completion of job search; 'it's been a huge relief' confirms resolution of prior stress associated with the search.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："I've finally transitioned to a new role, and it's been a huge relief."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；原话说转到新职位，没有说不再求职；宽慰也不证明原先求职压力已消失。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：no longer searching 并非原话；转岗与停止求职不是同一事实。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：应独立表达用户已转到新职位及 relief；是否继续求职未知。该模型值没有正确承载已转岗事实。
- ④ 时间或因果：finally 表明转岗相对话语已完成，不能证明停止求职或原求职压力解除。（无依据推断标记：True）
- ⑤ 字段与审核标准：改 conditions 为 unknown 也不会修复错误取值；需要重拆事实并单独查证。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**事实 f2**（记录哈希 `0527f5a8a2215648bc5db672a240256fc8966f8a5591cf451d10bc737b9ddf1b`）

原模型输出：
```json
{
  "fact_id": "f2",
  "subject": "I",
  "attribute": "work-life balance",
  "value": "much healthier now",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "The balance between work and personal life is much healthier now."
    }
  ],
  "rationale": "Direct self-assessment of current work-life balance as improved, using comparative 'much healthier now' implying change from prior state.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："The balance between work and personal life is much healthier now."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；用户说现在工作和生活平衡更健康；时间限定 now 有依据，unconditional 不宜扩大到其他时段。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留用户 now 评价工作与个人生活的平衡更健康；now 已出现在 value，起止时间未知。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：原审核提醒不推广到其他时段是合理的；但 now 已在 value，unconditional 并非代码自动将该词删除。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

### 新旧关系

**关系 r1**（记录哈希 `dfceb4c982d01f07c1c9b970d6dccdb992b32627886451219cdf3d44bee41d25`）

原模型输出：
```json
{
  "relation_id": "r1",
  "fact_id": "f1",
  "unit_id": "job_search",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "job search status",
  "old_value": "looking for a new job",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance"
    }
  ],
  "affected_part": "Looking for a new job",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "finally transitioned"
      }
    ],
    "explanation": "'Finally' signals completion relative to prior ongoing search; 'transitioned' is a past-tense completed action, temporally after the prior 'looking' state."
  },
  "rationale": "New fact asserts completed transition, directly negating the prior active search state. Temporal marker 'finally' supports sequential ordering.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "I've finally transitioned to a new role"
    },
    {
      "side": "old",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search]`："Looking for a new job with better work-life balance"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："I've finally transitioned to a new role, and it's been a huge relief."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；已转岗不证明停止求职；finally 只确认转岗相对话语完成，不证明晚于旧记忆事实有效时间。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：新值 no longer searching 无依据；将转岗等同结束求职是实质错误。
- ③ 条件类别 `lost`，模型原字段 `{"kind":"unconditional"}`；建议：旧求职事实与“已转岗”分开；停止求职未知，旧求职是否失效未知。
- ④ 时间或因果：finally 表示转岗相对话语已经发生，不证明相对旧求职有效期的 after。（无依据推断标记：True）
- ⑤ 字段与审核标准：change 的旧新值要有相同属性并有可审核的相对生效次序；主引文存在不能补足语义。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**关系 r2**（记录哈希 `bfad93dfe8681c568ab790957da642127871674c7b8a88a3bdc1279c731e7b0a`）

原模型输出：
```json
{
  "relation_id": "r2",
  "fact_id": "f2",
  "unit_id": "job_search",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "work-life balance expectation",
  "old_value": "better work-life balance",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance"
    }
  ],
  "affected_part": "better work-life balance",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "now"
      }
    ],
    "explanation": "'Now' in 'much healthier now' refers to current state post-transition, which follows the prior aspirational state expressed in the old unit."
  },
  "rationale": "Old unit expresses desire for 'better work-life balance' as a future goal; new fact states current reality is 'much healthier', satisfying and superseding that goal.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "The balance between work and personal life is much healthier now."
    },
    {
      "side": "old",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "better work-life balance"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search]`："Looking for a new job with better work-life balance"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："The balance between work and personal life is much healthier now."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；平衡更健康不证明旧目标已完全实现或应被替换；now 也不独立证明相对旧目标的有效时间先后。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把平衡变健康写为旧求职目标已完全实现并被替代，证据不足。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：更健康的当前平衡是新评价；旧目标是否实现或停止、适用范围与先后均待确认。
- ④ 时间或因果：now 只锚定该话语当前，不证明它发生在旧目标有效期之后。（无依据推断标记：True）
- ⑤ 字段与审核标准：原值是 expectation，新值是当前评价，属性不同；关系不能只按字符串比较。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

## skydiving

旧记忆 `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`）：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

- 选中新话语 `new-0`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
- 选中新话语 `new-2`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`）：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
- 选中新话语 `new-8`（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`）：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.

字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{"attribute":"simulated skydiving experience","conditions":{"dimensions":{"activity_mode":["simulated"]},"kind":"finite"},"subject":"I","value":"tried simulated skydiving at a team-building event recently"}`。仅在 activity_mode 是已选比较轴并约定 simulated 的规范含义时，可以给新事实 finite；旧记忆未明确同一轴取值，不能据此推断旧真实偏好改变或求出旧范围。

### 新事实

**事实 f1**（记录哈希 `7eddc65bc133bce7a8f5fdbcfa4466e57079b6667525c9608b4353e41b7e42cc`）

原模型输出：
```json
{
  "fact_id": "f1",
  "subject": "I",
  "attribute": "experience with simulated skydiving",
  "value": "tried simulated skydiving at a team-building event recently",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
    }
  ],
  "rationale": "User directly states having tried simulated skydiving recently in a team-building context; 'simulated' explicitly distinguishes it from real skydiving.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；明确是最近团队活动中的模拟跳伞，不自动代表真实跳伞；unconditional 的完整范围未证实。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留 simulated、team-building event、recently 与已尝试；这些限制都在 attribute/value 中。
- ④ 时间或因果：recently 仅相对新话语；没有给具体事件日期或相对旧事实次序。（无依据推断标记：False）
- ⑤ 字段与审核标准：原审核称无条件范围未证，但模拟、团建和最近均已编码；不能把 unconditional 一律读作体验适用于真实活动。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f2**（记录哈希 `04f4771b4c56f21070f2d841915e51c4fe42584477a3dc1e2c72c0e632a9b307`）

原模型输出：
```json
{
  "fact_id": "f2",
  "subject": "I",
  "attribute": "affective response to simulated skydiving",
  "value": "found it thrilling",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
    }
  ],
  "rationale": "The phrase 'It was quite thrilling!' is a direct, asserted evaluation of the experience.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-0/manually_mapped_new]`："Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`。
- 旧审核：`partial`；内核 `supported`；用户明确觉得这次模拟体验刺激；不能从一次体验外推真实偏好或其他时间。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留“对这次 simulated skydiving 感到 thrilling”；模拟限定已在 attribute，需绑定同次体验。
- ④ 时间或因果：未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。（无依据推断标记：False）
- ⑤ 字段与审核标准：模型值没明说是哪一次但属性限定模拟；事件引用需要维持关联，不能笼统判为所有真实跳伞体验。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f3**（记录哈希 `274c713fda832f39943c6ca141fc9f3f8023f2ee5eaa547ce413eff3627cb78c`）

原模型输出：
```json
{
  "fact_id": "f3",
  "subject": "I",
  "attribute": "affective response to adrenaline rush",
  "value": "didn't expect to enjoy the adrenaline rush so much",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much."
    }
  ],
  "rationale": "User asserts an unexpected positive affective response to the adrenaline rush, indicating prior expectation of non-enjoyment.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/unsplit-new-2]`："Yeah, the adrenaline rush was something I didn't expect to enjoy so much."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；用户说没想到会如此享受肾上腺素；理由声称原先预期完全不享受，比原话更强。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：模型 rationale 把“不曾料到这么享受”扩大为先前预计不享受。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留对这次 adrenaline rush 没想到会如此享受；不是原以为完全不享受。
- ④ 时间或因果：前后预期程度比较由原话支持，不支持“先前完全不享受”。（无依据推断标记：False）
- ⑤ 字段与审核标准：值本身较准确，错误主要在 rationale；不能因条件而掩盖该区别。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f4**（记录哈希 `e3f265e85f4796830cca7f1de65659316145f2391181cf755caa4322129d3680`）

原模型输出：
```json
{
  "fact_id": "f4",
  "subject": "I",
  "attribute": "attitude toward trying new things",
  "value": "more open to trying new things",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "It's definitely made me more open to trying new things."
    }
  ],
  "rationale": "User explicitly states a change in openness as a consequence of the experience.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-2/unsplit-new-2]`："It's definitely made me more open to trying new things."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`。
- 旧审核：`partial`；内核 `supported`；用户说更愿尝试新事物；不应扩大为真实极限运动喜好改变。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留更愿意尝试新事物，和此体验的关联；新事物不自动等同真实极限运动。
- ④ 时间或因果：用户说 it made me 更开放，体验与开放程度的自述因果有原话；不推断和旧记忆的时间顺序。（无依据推断标记：False）
- ⑤ 字段与审核标准：事件触发因果可以有依据，不能把所有因果都当成幻觉。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f5**（记录哈希 `f8f57fc24162473396d0ff35e8976ac65e248afffd013aca9459f8bbd4c9c092`）

原模型输出：
```json
{
  "fact_id": "f5",
  "subject": "I",
  "attribute": "priority regarding safety",
  "value": "still prioritize safety",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
    }
  ],
  "rationale": "User affirms continued prioritization of safety, using 'still' to signal persistence of this value despite new thrill-seeking behavior.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-8/unsplit-new-8]`："For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`。
- 旧审核：`partial`；内核 `supported`；用户明确说仍优先考虑安全；该句未确认完整旧因果关系或所有时间。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：本轮未发现明确扩写；不等于已独立授权。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留用户 still prioritize safety；still 是用户自述的延续，实际完整有效期和过去对应旧断言的范围未知。
- ④ 时间或因果：still 支持相对发话的延续，不自动证明恰与旧事实相同时间段。（无依据推断标记：False）
- ⑤ 字段与审核标准：safety 已在 attribute/value；以前审核需要明确具体比较维度，不能一概等同所有时间。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

**事实 f6**（记录哈希 `66d5f86c1a3a8a9d02570fe503645cddc02ca4a365a7b3dbf78967bf7af33de5`）

原模型输出：
```json
{
  "fact_id": "f6",
  "subject": "I",
  "attribute": "temporal framing of current engagement",
  "value": "for now, enjoying the thrill and seeing where it takes me",
  "conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "quotes": [
    {
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
    }
  ],
  "rationale": "'For now' signals a provisional, non-committal stance toward sustained engagement with thrill-seeking activities.",
  "uncertainties": []
}
```
- 新文逐字引文 `[new-8/unsplit-new-8]`："For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`。
- 旧审核：`partial`；内核 `supported`；用户说目前享受刺激并观察后续；理由关于长期参与刺激活动的解释超出原话。
- ① 内核：`supported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：理由扩展为对长期参与 thrill-seeking activities 的非承诺立场，原话未明确长期计划。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留 for now、enjoying thrill、seeing where it takes me；限定已在 value。
- ④ 时间或因果：for now 仅表明说话时暂时状态，不证明长期计划。（无依据推断标记：True）
- ⑤ 字段与审核标准：既有 value 已包含时间限定；应区分支持的原值和超出原文的 rationale。（具体契约边界标记：False；旧审核范围口径需澄清轴：True）

### 新旧关系

**关系 r1**（记录哈希 `685dfcf45b664af91da4b64f16f41b0577d741989118efb98dcb9205767bce13`）

原模型输出：
```json
{
  "relation_id": "r1",
  "fact_id": "f1",
  "unit_id": "u1",
  "relation": "supplement",
  "old_subject": "I",
  "old_attribute": "attitude toward extreme sports",
  "old_value": "dislikes extreme sports (e.g., skydiving)",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "u1",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "affected_part": "skydiving",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "recently"
      }
    ],
    "explanation": "New fact specifies 'recently', while old memory lacks temporal anchoring but is from earlier session (Sep 2025 vs Apr 2026); 'recently' in new-0 refers to time before Apr 10, 2026, thus after Sep 2025."
  },
  "rationale": "Simulated skydiving is a variant of skydiving; user’s trial does not contradict dislike of *extreme* skydiving but adds nuance: they engaged with a *simulated*, lower-risk version — supplementing, not replacing, the prior generalization.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "simulated skydiving"
    },
    {
      "side": "old",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "skydiving"
    }
  ],
  "uncertainties": [
    "Whether 'simulated skydiving' is semantically subsumed under 'extreme sports' per user’s original definition remains unspecified; user treats it as distinct by qualifying it as 'simulated' and pairing it with safety affirmation."
  ]
}
```
- 旧文逐字引文 `[e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1]`："Dislikes extreme sports (e.g., skydiving)"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；模拟体验与真实极限运动的旧态度之间影响未知；低风险及 after、旧事实有效时间由模型补推。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把模拟作为旧态度可确认的细化，并称其低风险，原文没有证明。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：新事实只涉及模拟体验；旧 u1 实际是否包含模拟、态度是否变化均未知。旧句未显式给出模拟/真实条件，不能凭空补全。
- ④ 时间或因果：recently 与发话时间不能证明晚于旧事实；模型提及会话日期不等于事实生效时间。（无依据推断标记：True）
- ⑤ 字段与审核标准：supplement 被投影为旧影响 unknown，保留原始关系；新事实模拟限定在关联事实属性和值内，旧范围仍未知。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**关系 r2**（记录哈希 `7219b6fddc5a522e5345a874b4826339b3d4247e133608bc6fdd1e9895f5e2e1`）

原模型输出：
```json
{
  "relation_id": "r2",
  "fact_id": "f1",
  "unit_id": "u2",
  "relation": "supplement",
  "old_subject": "I",
  "old_attribute": "reason for disliking extreme sports",
  "old_value": "due to high injury risk",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "u2",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk"
    }
  ],
  "affected_part": "high injury risk",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "recently"
      }
    ],
    "explanation": "Same temporal reasoning as r1: 'recently' places event after prior memory dated Sep 2025."
  },
  "rationale": "User’s choice of *simulated* skydiving — explicitly lower-risk — aligns with prior concern about injury risk; this action reflects risk-mitigated engagement rather than abandonment of the safety rationale.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "simulated skydiving"
    },
    {
      "side": "old",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "due to high injury risk"
    }
  ],
  "uncertainties": [
    "No explicit statement confirming user perceives simulated skydiving as low-injury-risk; inference relies on conventional understanding and user’s concurrent safety affirmation (f5)."
  ]
}
```
- 旧文逐字引文 `[e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u2]`："Dislikes extreme sports (e.g., skydiving) due to high injury risk"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；选择模拟活动不证明用户认为其低风险，亦不独立证明旧受伤风险原因继续或消失；after 缺相对旧状态依据。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：认为选择模拟是基于对低伤害风险的认识与风险规避，原句没有此因果。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：旧风险理由是否仍适用未知；新事实是一次模拟活动，不能据此确认对旧原因的影响。
- ④ 时间或因果：recently 不能证明相对旧事实的 after；选择模拟的动机也未给出。（无依据推断标记：True）
- ⑤ 字段与审核标准：对于模拟活动的限定已在引用事实中；用户对风险的主观判断并未作为独立事实给出。（具体契约边界标记：False；旧审核范围口径需澄清轴：False）

**关系 r3**（记录哈希 `7d4ccf0f665ab661a5723cf72b2f066c6c8e244a1d837bf1956057c92b83af95`）

原模型输出：
```json
{
  "relation_id": "r3",
  "fact_id": "f5",
  "unit_id": "u3",
  "relation": "same",
  "old_subject": "I",
  "old_attribute": "commitment",
  "old_value": "commitment to safety and well-being",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "u3",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "conflicting with commitment to safety and well-being"
    }
  ],
  "affected_part": "commitment to safety and well-being",
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-8",
        "quote": "I still prioritize safety, of course."
      }
    ],
    "explanation": "'Still' indicates continuity of the commitment expressed in u3; no temporal displacement implied — both refer to enduring values."
  },
  "rationale": "User reaffirms prioritization of safety, directly echoing the core value ('safety and well-being') cited in u3 as the basis for prior avoidance; 'still' confirms persistence, not change.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-8",
      "quote": "I still prioritize safety, of course."
    },
    {
      "side": "old",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "commitment to safety and well-being"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u3]`："conflicting with commitment to safety and well-being"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。
- 关联新事实逐字引文 `[new-8/unsplit-new-8]`："For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`。
- 旧审核：`partial`；内核 `partial`；当前仍优先安全有依据，但不能据此确认旧陈述中的完整安全与福祉因果、同一有效时间或无条件范围。
- ① 内核：`partial`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把安全优先扩展为安全和福祉的完整旧冲突理由持续不变。
- ③ 条件类别 `unspecified`，模型原字段 `{"kind":"unconditional"}`；建议：新证据仅支持仍优先安全；旧 u3 的安全与福祉及冲突因果整体是否相同待确认。
- ④ 时间或因果：still 支持延续，但不足以建立和旧事实完全同一有效时间。（无依据推断标记：True）
- ⑤ 字段与审核标准：旧 value 含 well-being、冲突关系，新 value 仅 safety；same 的同属性同值要求未满足。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**关系 r4**（记录哈希 `ba4ce14a6f2f40b9d5f30f6e59708baf688d9cd7aba697899dd3581e6682e4e5`）

原模型输出：
```json
{
  "relation_id": "r4",
  "fact_id": "f2",
  "unit_id": "u1",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "attitude toward skydiving",
  "old_value": "dislikes extreme sports (e.g., skydiving)",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "u1",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "affected_part": "skydiving",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "recently"
      }
    ],
    "explanation": "Same as r1."
  },
  "rationale": "User reports finding simulated skydiving 'quite thrilling', which contradicts a blanket 'dislike' of skydiving — even if qualified as simulated — because the affective valence (thrill) is positive and specific to that activity instance.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "It was quite thrilling!"
    },
    {
      "side": "old",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "uncertainties": [
    "Whether 'thrilling' implies reversal of 'dislike' or merely coexistence of positive sensation with prior aversion is ambiguous; however, 'dislikes' is a categorical judgment incompatible with reporting the same activity as thrilling without qualification — hence change is warranted."
  ]
}
```
- 旧文逐字引文 `[e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1]`："Dislikes extreme sports (e.g., skydiving)"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。
- 关联新事实逐字引文 `[new-0/manually_mapped_new]`："Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`。
- 旧审核：`unsupported`；内核 `unsupported`；觉得模拟体验刺激不证明真实跳伞厌恶消失；模型把正面体验与旧普遍偏好视为互斥缺依据，after 亦不成立。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把觉得模拟刺激推成真实跳伞厌恶被否定。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留模拟活动刺激这一体验；该体验与真实跳伞偏好是否矛盾或覆盖旧厌恶未知。
- ④ 时间或因果：recently 不证明晚于旧态度有效期。（无依据推断标记：True）
- ⑤ 字段与审核标准：刺激是体验评价而非相同属性上的偏好反值；关联事实含模拟限定，不应在旧比较中丢失。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

**关系 r5**（记录哈希 `1ccbe57c5465c61eb9bfc7ed46f172c821c6b34216630e342483c93641cbb0af`）

原模型输出：
```json
{
  "relation_id": "r5",
  "fact_id": "f4",
  "unit_id": "u1",
  "relation": "change",
  "old_subject": "I",
  "old_attribute": "attitude toward extreme sports",
  "old_value": "dislikes extreme sports (e.g., skydiving)",
  "old_conditions": {
    "kind": "unconditional"
  },
  "old_quotes": [
    {
      "unit_id": "u1",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "affected_part": "Dislikes extreme sports",
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-2",
        "quote": "It's definitely made me more open to trying new things."
      }
    ],
    "explanation": "'Made me' signals causal emergence post-experience; experience occurred recently (per new-0), thus after old memory."
  },
  "rationale": "Stating being 'more open to trying new things' — in direct response to the simulated skydiving experience — undermines the prior categorical 'dislikes', indicating a shift in disposition toward novelty, including previously avoided domains.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "It's definitely made me more open to trying new things."
    },
    {
      "side": "old",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "uncertainties": []
}
```
- 旧文逐字引文 `[e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1]`："Dislikes extreme sports (e.g., skydiving)"；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。
- 关联新事实逐字引文 `[new-2/unsplit-new-2]`："It's definitely made me more open to trying new things."；来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`。
- 旧审核：`unsupported`；内核 `unsupported`；更愿尝试新事物不证明真实极限运动偏好改变；模型自行推断覆盖该领域和相对旧状态先后。
- ① 内核：`unsupported`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。
- ② 主体、身份、值或理由扩写：把一般尝新开放度扩大为极限运动喜好改变。
- ③ 条件类别 `embedded`，模型原字段 `{"kind":"unconditional"}`；建议：保留更愿尝试新事物，但其是否覆盖真实极限运动及旧偏好未知。
- ④ 时间或因果：made me 支持体验使人更开放的自述，不证明体验晚于旧记忆事实的有效时间。（无依据推断标记：True）
- ⑤ 字段与审核标准：属性“尝试新事物”与“极限运动偏好”不是自动同一属性。（具体契约边界标记：True；旧审核范围口径需澄清轴：False）

## 复核

```sh
PYTHONDONTWRITEBYTECODE=1 python diagnose.py
```

脚本只读取 v5 保存材料，验证请求/响应和旧审核哈希，并在本诊断目录生成 `DIAGNOSIS.json` 和本报告；不调用模型、API 或 Mem0。原审核与建议字段均不回填自动流程。
