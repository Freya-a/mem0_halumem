# 候选事实拆分与覆盖检查：离线五案

## 范围与结论

本次只读取 v4 已保存的五次原始响应及既有 v3 授权对照，未调用模型或 API，未写真实记忆或 Mem0。新版本保留 v3 条件和时间计算及 A/B/C 输入政策；B 的 `semantic_support=supported` 仅是原实验中的模型候选兼容标记，不构成独立语义授权。覆盖通过不代表事实正确，更不表示可以执行写入；五案仅用于开发诊断。

定位到的缺口：转岗 B 的两条旧关系都落入 `job_search` 同一范围；记录 1 是 supplement，v3 将它的新事实另行输出，但对旧事实影响设置了 `impact of new information on old fact is not established`。进入范围单元时，原 v3 的 `if uncertain` 仅输出带理由的记录 1，然后 `continue`，因此同格的记录 0 `change` 被跳过。修复后，每条受该范围阻塞的关系均单独输出 `uncertain`；记录 0 的原因是 `scope decision blocked by another unresolved overlapping candidate`。这是聚合阻塞的程序原因，不是已经完成时间或语义审核。

新规划器给每个输入分配 `candidate_index`，分别追踪 `old_relation` 和 `new_claim`；A/B 原始关系和 B 原有投影的新侧子候选都在账本中。每个子判断必须指向最终 `modify/preserve/uncertain/add` 的具体索引；聚合中没有独立结果时，保守补 `uncertain`，并阻止与该未决同单元范围重叠的编辑。输出项中没有输入候选来源的受保护事实仍单独保留，不冒充候选判断。该机制追踪已给出的输入，不能证明自然语言中所有潜在事实都被模型提出，也不能保证每个候选内部所有自然语言子事实已自动拆开。

人工审核与程序回放严格分开：下文“人工子判断”只写在 `MANUAL_SUBFACTS.json`，不进入规划器。`atomic` 表示模型已有单独结构化内容，`combined` 表示仅在合并值/理由中明确，`quote_or_rationale` 表示仅在引文或理由中出现，`unsupported_relation` 表示模型确实声称但引文不足以证明，`not_asserted` 表示不能从模型输出确认该关系。对于后四种，自动链路不能凭人工审核当作已生成的独立事实；需要人工重新对齐，或将来通过重新模型拆分并审核取得独立候选。本次没有进行模型重拆。

| 案例 | 旧 B 修改/保留/待确认/新增 | 新 B 修改/保留/待确认/新增 | 新 B 候选 / 子判断 / 已映射子判断 |
|---|---:|---:|---:|
| susan | 0/0/3/2 | 0/0/3/2 | 4 / 5 / 5 |
| promotion | 1/1/0/0 | 1/1/0/1 | 3 / 3 / 3 |
| career_history | 0/0/3/2 | 0/0/3/2 | 5 / 5 / 5 |
| transition | 0/0/1/2 | 0/0/2/2 | 3 / 4 / 4 |
| skydiving | 0/0/11/1 | 0/0/11/1 | 7 / 8 / 8 |

B 总计 22 条输入候选、25 项可追踪子判断，全部关联最终输出。A/C 的输入及覆盖见逐案账本。这里的子判断是程序中原有关系与新增路径、及旧 B 已有的新侧投影，不是对复杂自然语言的完整人工拆分。

晋升 B 新增数从 0 变 1 与聚合修复无关：原对照脚本在 v3 运行后抑制与修改来自同一模型记录的新增候选；本次为保留每个输入的明确去向，不再执行该对照后处理，保留新侧候选 `add`，同时标明它与该条修改语义重叠。此候选是模型原文投影而非独立授权，不能与修改一起当成已批准的两次写入；新职位话语有依据，但旧职位替换与时间仍不成立。

逐字段比较（忽略新增追踪字段）后的不同输出类别：promotion/B: add；transition/B: uncertain；其余案例组的原有输出内容一致。

## susan

旧记忆（`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`）：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

### 保存的模型原始记录与逐字引文

**模型记录 0（完整保存字段）**

```json
{
  "unit_id": "friendship",
  "relation": "same",
  "old_subject": "ThomasSusan",
  "new_subject": "Susan",
  "old_attribute": "name",
  "new_attribute": "name",
  "old_value": "ThomasSusan",
  "new_value": "Susan",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "friendship",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "friend named ThomasSusan"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "old",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
        "quote": "friend named ThomasSusan"
      },
      {
        "side": "new",
        "source_id": "new-2",
        "quote": "Susan's support has indeed been invaluable."
      }
    ],
    "explanation": "Both refer to current, ongoing friendship; no temporal shift indicated in either quote"
  },
  "semantic_rationale": "The old unit identifies 'ThomasSusan' as a friend; the new unit refers to 'Susan' in identical relational and functional context (support/encouragement), and contextual source 'ctx-1' explicitly equates 'ThomasSusan' with 'Susan' ('ThomasSusan is my Friend, Susan's support...'). This confirms same person, same relationship.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
    },
    {
      "side": "old",
      "source_id": "ctx-1",
      "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."
    }
  ],
  "uncertainties": []
}
```
- `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/friendship`：valid，位置 `{"end":30,"start":6}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`；逐字引文：「friend named ThomasSusan」。
- `new/new-2/manually_mapped_new`：valid，位置 `{"end":96,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`；逐字引文：「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。

**模型记录 1（完整保存字段）**

```json
{
  "unit_id": "support",
  "relation": "supplement",
  "old_subject": "Susan",
  "new_subject": "Susan",
  "old_attribute": "provides support and encouragement",
  "new_attribute": "support and encouragement",
  "old_value": "provides support and encouragement",
  "new_value": "has indeed been invaluable... helps me stay focused on my goals",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "support",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "old",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
        "quote": "provides support and encouragement"
      },
      {
        "side": "new",
        "source_id": "new-2",
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
      }
    ],
    "explanation": "Both describe current, ongoing supportive function; no indication of change in timing or duration"
  },
  "semantic_rationale": "New statement affirms and enriches the old claim: adds evaluative ('invaluable') and functional ('helps me stay focused on my goals') detail without contradicting or replacing it.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
    }
  ],
  "uncertainties": []
}
```
- `old/a1332815-d6ba-4bdc-9ffa-657f7315d0ed/support`：valid，位置 `{"end":94,"start":60}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`；逐字引文：「provides support and encouragement」。
- `new/new-2/manually_mapped_new`：valid，位置 `{"end":96,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`；逐字引文：「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。

**模型记录 2（完整保存字段）**

```json
{
  "unit_id": null,
  "relation": "new_information",
  "old_subject": null,
  "new_subject": "current role",
  "old_attribute": null,
  "new_attribute": "supports well-being",
  "old_value": null,
  "new_value": "not supporting my well-being as much as I'd like",
  "old_conditions": {
    "kind": "unknown"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [],
  "new_quotes": [
    {
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "my current role isn't supporting my well-being as much as I'd like"
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "my current role isn't supporting my well-being as much as I'd like"
      }
    ],
    "explanation": "Describes present state of current role; no comparative temporal marker relative to past"
  },
  "semantic_rationale": "This is a newly introduced evaluation of the user's current job — not referenced in any old unit. It asserts a deficit in well-being support, which is novel information.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "my current role isn't supporting my well-being as much as I'd like"
    }
  ],
  "uncertainties": []
}
```
- `new/new-0/unsplit-new-0`：valid，位置 `{"end":138,"start":72}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`；逐字引文：「my current role isn't supporting my well-being as much as I'd like」。

**模型记录 3（完整保存字段）**

```json
{
  "unit_id": null,
  "relation": "new_information",
  "old_subject": null,
  "new_subject": "I",
  "old_attribute": null,
  "new_attribute": "career goal",
  "old_value": null,
  "new_value": "find a new job that offers a better work-life balance and aligns with my humanitarian goals",
  "old_conditions": {
    "kind": "unknown"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "planned",
  "old_quotes": [],
  "new_quotes": [
    {
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job..."
      }
    ],
    "explanation": "The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment."
  },
  "semantic_rationale": "This expresses an active intention (‘crucial for me to find’) — a forward-looking plan, not yet realized. No prior mention of humanitarian goals or work-life balance as career criteria exists in old units.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
    }
  ],
  "uncertainties": []
}
```
- `new/new-0/unsplit-new-0`：valid，位置 `{"end":255,"start":140}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`；逐字引文：「It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.」。

### B 组每个输入候选及子判断的最终去向

- 输入 0：`B:model_record=0;candidate=relation`；关系 `same`，旧/新值 `"ThomasSusan"` → `"Susan"`。
  - `old_relation` → `uncertain[1]`（upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']；范围 `{"kind":"unconditional"}`）
- 输入 1：`B:model_record=1;candidate=relation`；关系 `supplement`，旧/新值 `"provides support and encouragement"` → `"has indeed been invaluable... helps me stay focused on my goals"`。
  - `old_relation` → `uncertain[2]`（impact of new information on old fact is not established；范围 `{"kind":"unconditional"}`）
  - `new_claim` → `add[0]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）
- 输入 2：`B:model_record=2;candidate=relation`；关系 `new_information`，旧/新值 `null` → `"not supporting my well-being as much as I'd like"`。
  - `new_claim` → `add[1]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）
- 输入 3：`B:model_record=3;candidate=relation`；关系 `new_information`，旧/新值 `null` → `"find a new job that offers a better work-life balance and aligns with my humanitarian goals"`。
  - `new_claim` → `uncertain[0]`（upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']；范围 `{"kind":"unconditional"}`）

### 原 B 修改和新增的人工子判断

**原 B `add[0]`；模型记录 1**。原候选主体 `"Susan"`，属性 `"support and encouragement"`，旧值 `"provides support and encouragement"`，新值 `"has indeed been invaluable... helps me stay focused on my goals"`；此前审核：Susan 的支持和帮助专注有依据；unconditional 及该结构化关系的完整适用范围并未独立证实。

- 原动作关联的新引文 `new-2`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`，`{"end":96,"start":0}`）：「Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.」。
- **原文支持**：Susan 的支持被说成很有价值。逐字依据 「Susan's support has indeed been invaluable.」；模型可得性 `combined`：值与理由含此内容，但和帮助专注合并；要独立结构化需拆分。
- **原文支持**：她的鼓励帮助用户专注目标。逐字依据 「Her encouragement helps me stay focused on my goals.」；模型可得性 `combined`：已有模型值/理由包含该事实，但并非独立记录。
- **关系仍需确认**：完整无条件适用范围及旧支持关系是否受影响。逐字依据 「Susan's support has indeed been invaluable.」；模型可得性 `unsupported_relation`：模型写 unconditional；引文不足以确立完整范围或旧事实同一关系。

**原 B `add[1]`；模型记录 2**。原候选主体 `"current role"`，属性 `"supports well-being"`，旧值 `null`，新值 `"not supporting my well-being as much as I'd like"`；此前审核：用户明确说当前角色对福祉支持不如希望；这里仅按当前角色和相对期望理解，不推定永久状态。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`，`{"end":138,"start":72}`）：「my current role isn't supporting my well-being as much as I'd like」。
- **原文支持**：用户当时认为当前岗位对福祉的支持不如期望。逐字依据 「my current role isn't supporting my well-being as much as I'd like」；模型可得性 `atomic`：模型已有独立 new_information 值，但应保持 current 与相对期望限定。
- **无依据扩展**：该评价适用于所有岗位或所有时间。逐字依据 「my current role isn't supporting my well-being as much as I'd like」；模型可得性 `not_asserted`：这是需要排除的扩展；原模型未单独声称所有岗位或永远如此。

### A、C 组覆盖及新旧数量

- A 旧 `{"add":0,"modify":0,"preserve":0,"uncertain":5}` → 新 `{"add":0,"modify":0,"preserve":0,"uncertain":5}`；输入 4 条，子判断 5 项。
  - 输入 0（`same`）：old_relation → uncertain[3]
  - 输入 1（`supplement`）：old_relation → uncertain[4]；new_claim → uncertain[0]
  - 输入 2（`new_information`）：new_claim → uncertain[1]
  - 输入 3（`new_information`）：new_claim → uncertain[2]
- C 旧 `{"add":2,"modify":0,"preserve":1,"uncertain":1}` → 新 `{"add":2,"modify":0,"preserve":1,"uncertain":1}`；输入 4 条，子判断 4 项。
  - 输入 0（`unknown`）：old_relation → uncertain[0]
  - 输入 1（`same`）：old_relation → preserve[0]
  - 输入 2（`supplement`）：new_claim → add[0]
  - 输入 3（`plan`）：new_claim → add[1]

## promotion

旧记忆（`e13b825e-7ec7-4760-821e-0581d8da5650`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`）：Works at Historical Productions Ltd. as a Director

### 保存的模型原始记录与逐字引文

**模型记录 0（完整保存字段）**

```json
{
  "unit_id": "employer",
  "relation": "same",
  "old_subject": "Historical Productions Ltd.",
  "new_subject": "Historical Productions Ltd.",
  "old_attribute": "employer",
  "new_attribute": "employer",
  "old_value": "Historical Productions Ltd.",
  "new_value": "Historical Productions Ltd.",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "employer",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Historical Productions Ltd."
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
      }
    ],
    "explanation": "The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated."
  },
  "semantic_rationale": "The new utterance explicitly names 'Historical Productions Ltd.' as the employer in the context of a recent promotion, confirming continuity of employer affiliation.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "uncertainties": []
}
```
- `old/e13b825e-7ec7-4760-821e-0581d8da5650/employer`：valid，位置 `{"end":36,"start":9}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`；逐字引文：「Historical Productions Ltd.」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`；逐字引文：「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。

**模型记录 1（完整保存字段）**

```json
{
  "unit_id": "title",
  "relation": "change",
  "old_subject": "user",
  "new_subject": "user",
  "old_attribute": "title",
  "new_attribute": "title",
  "old_value": "Director",
  "new_value": "lead director",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "title",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Director"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I recently got promoted"
      }
    ],
    "explanation": "'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director')."
  },
  "semantic_rationale": "The new utterance states a promotion occurred, and specifies the resulting title as 'lead director', which supersedes the prior 'Director' title. 'Lead director' is a more senior role than 'Director', consistent with promotion semantics.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director"
    }
  ],
  "uncertainties": []
}
```
- `old/e13b825e-7ec7-4760-821e-0581d8da5650/title`：valid，位置 `{"end":50,"start":42}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`；逐字引文：「Director」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":92,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`；逐字引文：「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。

### B 组每个输入候选及子判断的最终去向

- 输入 0：`B:model_record=0;candidate=relation`；关系 `same`，旧/新值 `"Historical Productions Ltd."` → `"Historical Productions Ltd."`。
  - `old_relation` → `preserve[0]`（same value supported by new evidence；范围 `{"kind":"unconditional"}`）
- 输入 1：`B:model_record=1;candidate=relation`；关系 `change`，旧/新值 `"Director"` → `"lead director"`。
  - `old_relation` → `modify[0]`（different values and evidenced later state；范围 `{"kind":"unconditional"}`）
- 输入 2：`B:model_record=1;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"lead director"`。
  - `new_claim` → `add[0]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）

### 原 B 修改和新增的人工子判断

**原 B `modify[0]`；模型记录 1**。原候选主体 `"user"`，属性 `"title"`，旧值 `"Director"`，新值 `"lead director"`；此前审核：recently 只相对发话，不证明晋升晚于旧记忆有效期；lead director 不必否定宽泛 Director。此修改缺依据，并非证明晋升为假。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`，`{"end":92,"start":0}`）：「I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!」。
- **原文支持**：发话时用户已晋升为 lead director。逐字依据 「I recently got promoted to lead director」；模型可得性 `combined`：模型 new_value 给出 lead director，事件也写在理由；晋升事件并非独立记录。
- **原文支持**：新话语将该职位与 Historical Productions Ltd. 联系起来。逐字依据 「at Historical Productions Ltd.」；模型可得性 `combined`：公司和职位同时出现于引文与模型说明；主体需从话语明确为用户。
- **关系仍需确认**：该晋升是否晚于旧记忆所描述的职位有效期。逐字依据 「I recently got promoted」；模型可得性 `unsupported_relation`：模型明确写 after；recently 仅确定相对话语发生，不能证明相对旧状态的先后。
- **关系仍需确认**：旧 Director 是否因此不再成立。逐字依据 「I recently got promoted to lead director」；模型可得性 `unsupported_relation`：模型声称 supersedes，但宽泛职位称谓可能仍成立，现有字段不能证明替代。

本次额外显露的 `B add[0]` 是旧对照抑制的 `new_subfact`，值为 `lead director`，与上述 `modify[0]` 来自同一模型记录。发话者晋升及新职位由引文支持；覆盖旧职位的先后关系不因此成立。

### A、C 组覆盖及新旧数量

- A 旧 `{"add":0,"modify":0,"preserve":0,"uncertain":2}` → 新 `{"add":0,"modify":0,"preserve":0,"uncertain":2}`；输入 2 条，子判断 2 项。
  - 输入 0（`same`）：old_relation → uncertain[0]
  - 输入 1（`change`）：old_relation → uncertain[1]
- C 旧 `{"add":0,"modify":0,"preserve":1,"uncertain":3}` → 新 `{"add":0,"modify":0,"preserve":1,"uncertain":3}`；输入 2 条，子判断 2 项。
  - 输入 0（`same`）：old_relation → preserve[0]
  - 输入 1（`change`）：old_relation → uncertain[0], uncertain[1], uncertain[2]

## career_history

旧记忆（`05afde13-35bd-4d26-bbae-6de427d58db1`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`）：Previously worked as a senior developer in Blockchain Tech

### 保存的模型原始记录与逐字引文

**模型记录 0（完整保存字段）**

```json
{
  "unit_id": "employer",
  "relation": "change",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "employer",
  "new_attribute": "current employer / business ownership",
  "old_value": "Blockchain Tech",
  "new_value": "consulting firm",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "employer",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "Blockchain Tech"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients"
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
        "quote": "Previously worked as a senior developer in Blockchain Tech"
      },
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"
      }
    ],
    "explanation": "The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role."
  },
  "semantic_rationale": "New utterance asserts active operation of a consulting firm with secured clients, incompatible with ongoing employment as a senior developer at Blockchain Tech. The shift from 'worked as' (past) to 'my consulting firm' (present possessive + active milestone) signals career transition.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients"
    }
  ],
  "uncertainties": []
}
```
- `old/05afde13-35bd-4d26-bbae-6de427d58db1/employer`：valid，位置 `{"end":58,"start":43}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`；逐字引文：「Blockchain Tech」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":103,"start":48}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`；逐字引文：「my consulting firm finally secured some initial clients」。

**模型记录 1（完整保存字段）**

```json
{
  "unit_id": "title",
  "relation": "change",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "job title",
  "new_attribute": "current role",
  "old_value": "senior developer",
  "new_value": "founder / operator of consulting firm",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "title",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "senior developer"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients"
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
        "quote": "Previously worked as a senior developer in Blockchain Tech"
      },
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"
      }
    ],
    "explanation": "Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct."
  },
  "semantic_rationale": "Possessive 'my consulting firm' and achievement of client acquisition imply founder/operator status, replacing prior employee title. No evidence of concurrent roles; 'Previously worked' implies discontinuation.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients"
    }
  ],
  "uncertainties": []
}
```
- `old/05afde13-35bd-4d26-bbae-6de427d58db1/title`：valid，位置 `{"end":39,"start":23}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`；逐字引文：「senior developer」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":103,"start":48}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`；逐字引文：「my consulting firm finally secured some initial clients」。

**模型记录 2（完整保存字段）**

```json
{
  "unit_id": null,
  "relation": "new_information",
  "old_subject": null,
  "new_subject": "I",
  "old_attribute": null,
  "new_attribute": "network contacts",
  "old_value": null,
  "new_value": [
    "MooreSandra",
    "GonzalezMary"
  ],
  "old_conditions": {
    "kind": "unknown"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [],
  "new_quotes": [
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."
    }
  ],
  "temporal_order": {
    "relation": "unknown",
    "basis": [],
    "explanation": null
  },
  "semantic_rationale": "Names 'MooreSandra' and 'GonzalezMary' are explicitly named as instrumental contacts whose connections enabled new opportunities; no prior mention in old memory units.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-2",
      "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."
    }
  ],
  "uncertainties": []
}
```
- `new/new-2/unsplit-new-2`：valid，位置 `{"end":111,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`；逐字引文：「MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.」。

### B 组每个输入候选及子判断的最终去向

- 输入 0：`B:model_record=0;candidate=relation`；关系 `change`，旧/新值 `"Blockchain Tech"` → `"consulting firm"`。
  - `old_relation` → `uncertain[1]`（upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']；范围 `{"kind":"unconditional"}`）
- 输入 1：`B:model_record=1;candidate=relation`；关系 `change`，旧/新值 `"senior developer"` → `"founder / operator of consulting firm"`。
  - `old_relation` → `uncertain[2]`（upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']；范围 `{"kind":"unconditional"}`）
- 输入 2：`B:model_record=2;candidate=relation`；关系 `new_information`，旧/新值 `null` → `null`。
  - `new_claim` → `uncertain[0]`（upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']；范围 `{"kind":"unconditional"}`）
- 输入 3：`B:model_record=0;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"consulting firm"`。
  - `new_claim` → `add[0]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）
- 输入 4：`B:model_record=1;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"founder / operator of consulting firm"`。
  - `new_claim` → `add[1]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）

### 原 B 修改和新增的人工子判断

**原 B `add[0]`；模型记录 0**。原候选主体 `"I"`，属性 `"current employer / business ownership"`，旧值 `null`，新值 `"consulting firm"`；此前审核：my consulting firm 获客不证明用户现在以其为雇主或具有公司所有权。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，`{"end":103,"start":48}`）：「my consulting firm finally secured some initial clients」。
- **原文支持**：用户所称咨询公司获得了首批客户。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `quote_or_rationale`：模型引文和语义理由提及获客，但 new_value 是公司而非获客事件；要独立结构化需重新拆分。
- **无依据扩展**：用户当前以该咨询公司为雇主或为公司的所有者。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `unsupported_relation`：模型的 current employer / business ownership 是有依据不足的关系；my 不足以确定所有权或雇佣。
- **关系仍需确认**：用户是否已结束 Blockchain Tech 旧工作。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `unsupported_relation`：模型推断工作互斥和转变；获客不证明离职或新旧关系先后。

**原 B `add[1]`；模型记录 1**。原候选主体 `"I"`，属性 `"current role"`，旧值 `null`，新值 `"founder / operator of consulting firm"`；此前审核：原文未证明 founder/operator 职位；不能从公司获客反推。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`，`{"end":103,"start":48}`）：「my consulting firm finally secured some initial clients」。
- **原文支持**：用户所称咨询公司获得了首批客户。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `quote_or_rationale`：原模型理由和引文包含事件，结构化 new_value 却是职位；需要重新拆分。
- **无依据扩展**：用户是咨询公司的创办者或经营者。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `unsupported_relation`：模型明确提出 founder/operator，但引文没有证明。
- **关系仍需确认**：新活动是否替代此前 senior developer 职位。逐字依据 「my consulting firm finally secured some initial clients」；模型可得性 `unsupported_relation`：模型推断替代；没有独立事实证明职位互斥或有效时间。

### A、C 组覆盖及新旧数量

- A 旧 `{"add":0,"modify":0,"preserve":0,"uncertain":3}` → 新 `{"add":0,"modify":0,"preserve":0,"uncertain":3}`；输入 3 条，子判断 3 项。
  - 输入 0（`change`）：old_relation → uncertain[1]
  - 输入 1（`change`）：old_relation → uncertain[2]
  - 输入 2（`new_information`）：new_claim → uncertain[0]
- C 旧 `{"add":1,"modify":0,"preserve":2,"uncertain":1}` → 新 `{"add":1,"modify":0,"preserve":2,"uncertain":1}`；输入 3 条，子判断 3 项。
  - 输入 0（`supplement`）：new_claim → add[0]
  - 输入 1（`unrelated`）：old_relation → preserve[0], uncertain[0]
  - 输入 2（`unrelated`）：old_relation → preserve[1]

## transition

旧记忆（`e6ab178b-c0f9-4adb-bfb7-e4648617a950`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`）：Looking for a new job with better work-life balance

### 保存的模型原始记录与逐字引文

**模型记录 0（完整保存字段）**

```json
{
  "unit_id": "job_search",
  "relation": "change",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "job search status",
  "new_attribute": "job search status",
  "old_value": "looking for a new job with better work-life balance",
  "new_value": "transitioned to a new role with healthier work-life balance",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
        "quote": "Looking for a new job with better work-life balance"
      },
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "I've finally transitioned to a new role"
      }
    ],
    "explanation": "'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'"
  },
  "semantic_rationale": "The old unit states an active job search motivated by work-life balance; the new unit asserts successful transition to a role delivering that balance — a direct change in status.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
    }
  ],
  "uncertainties": []
}
```
- `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：valid，位置 `{"end":51,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`；逐字引文：「Looking for a new job with better work-life balance」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":135,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`；逐字引文：「I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.」。

**模型记录 1（完整保存字段）**

```json
{
  "unit_id": "job_search",
  "relation": "supplement",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "motivation for job search",
  "new_attribute": "motivation for job search",
  "old_value": "better work-life balance",
  "new_value": "better work-life balance (now realized as healthier balance)",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "unconditional"
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "The balance between work and personal life is much healthier now."
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "The balance between work and personal life is much healthier now."
      }
    ],
    "explanation": "The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself."
  },
  "semantic_rationale": "The new utterance confirms the original goal ('better work-life balance') has been achieved ('much healthier now'), supplementing the old unit with outcome evidence without altering the core motivational attribute.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "The balance between work and personal life is much healthier now."
    }
  ],
  "uncertainties": []
}
```
- `old/e6ab178b-c0f9-4adb-bfb7-e4648617a950/job_search`：valid，位置 `{"end":51,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`；逐字引文：「Looking for a new job with better work-life balance」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":135,"start":70}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`；逐字引文：「The balance between work and personal life is much healthier now.」。

### B 组每个输入候选及子判断的最终去向

- 输入 0：`B:model_record=0;candidate=relation`；关系 `change`，旧/新值 `"looking for a new job with better work-life balance"` → `"transitioned to a new role with healthier work-life balance"`。
  - `old_relation` → `uncertain[0]`（scope decision blocked by another unresolved overlapping candidate；范围 `{"kind":"unconditional"}`）
- 输入 1：`B:model_record=1;candidate=relation`；关系 `supplement`，旧/新值 `"better work-life balance"` → `"better work-life balance (now realized as healthier balance)"`。
  - `old_relation` → `uncertain[1]`（impact of new information on old fact is not established；范围 `{"kind":"unconditional"}`）
  - `new_claim` → `add[0]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）
- 输入 2：`B:model_record=0;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"transitioned to a new role with healthier work-life balance"`。
  - `new_claim` → `add[1]`（independent evidence-supported addition；范围 `{"kind":"unconditional"}`）

### 原 B 修改和新增的人工子判断

**原 B `add[0]`；模型记录 1**。原候选主体 `"I"`，属性 `"motivation for job search"`，旧值 `"better work-life balance"`，新值 `"better work-life balance (now realized as healthier balance)"`；此前审核：原话只说平衡更健康；模型结构称原目标已实现，证据不证明达到原目标。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，`{"end":135,"start":70}`）：「The balance between work and personal life is much healthier now.」。
- **原文支持**：用户表示现在工作与个人生活平衡更健康。逐字依据 「The balance between work and personal life is much healthier now.」；模型可得性 `combined`：模型值与理由包含改善，但和旧目标实现合并；应分为独立新断言。
- **无依据扩展**：原来的求职平衡目标已完全实现。逐字依据 「The balance between work and personal life is much healthier now.」；模型可得性 `unsupported_relation`：模型标为 realized；更健康不证明达到旧目标或所有目标已实现。
- **关系仍需确认**：更健康状态与旧目标之间的对应及持续性。逐字依据 「The balance between work and personal life is much healthier now.」；模型可得性 `not_asserted`：需要更多证据；原话没有独立确认目标实现和持续时间。

**原 B `add[1]`；模型记录 0**。原候选主体 `"I"`，属性 `"job search status"`，旧值 `null`，新值 `"transitioned to a new role with healthier work-life balance"`；此前审核：转岗与平衡更健康都有原话支持；但以 job search status 表述容易暗示停止求职，且适用范围未核实。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`，`{"end":135,"start":0}`）：「I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.」。
- **原文支持**：用户说自己已经转到新职位。逐字依据 「I've finally transitioned to a new role」；模型可得性 `combined`：模型 new_value 合并了转岗与平衡改善；要单独表示事件需拆分。
- **原文支持**：用户说现在工作与生活的平衡更健康。逐字依据 「The balance between work and personal life is much healthier now.」；模型可得性 `combined`：该事实与转岗合在同一 new_value，不能把整个 job search status 当成独立事实。
- **关系仍需确认**：转岗后用户是否已经停止求职。逐字依据 「I've finally transitioned to a new role」；模型可得性 `unsupported_relation`：模型以 job search status 和 successful transition 推断替换，原话并未说停止求职。
- **关系仍需确认**：转岗相对旧求职事实有效时间是否更晚。逐字依据 「I've finally transitioned to a new role」；模型可得性 `unsupported_relation`：finally 相对话语表示转岗完成，不证明相对旧事实的先后。

### A、C 组覆盖及新旧数量

- A 旧 `{"add":0,"modify":0,"preserve":0,"uncertain":3}` → 新 `{"add":0,"modify":0,"preserve":0,"uncertain":3}`；输入 2 条，子判断 3 项。
  - 输入 0（`change`）：old_relation → uncertain[1]
  - 输入 1（`supplement`）：old_relation → uncertain[2]；new_claim → uncertain[0]
- C 旧 `{"add":1,"modify":0,"preserve":1,"uncertain":3}` → 新 `{"add":1,"modify":0,"preserve":1,"uncertain":3}`；输入 2 条，子判断 2 项。
  - 输入 0（`change`）：old_relation → uncertain[0], uncertain[1], uncertain[2]
  - 输入 1（`supplement`）：new_claim → add[0]

## skydiving

旧记忆（`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`）：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

### 保存的模型原始记录与逐字引文

**模型记录 0（完整保存字段）**

```json
{
  "unit_id": "u1",
  "relation": "change",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "attitude toward extreme sports (e.g., skydiving)",
  "new_attribute": "attitude toward extreme sports (e.g., skydiving)",
  "old_value": "dislikes",
  "new_value": "found simulated skydiving thrilling; more open to trying new things",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "finite",
    "dimensions": {
      "context": [
        "simulated",
        "team-building event"
      ]
    }
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "u1",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
    },
    {
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "ctx-1",
        "quote": "I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."
      },
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
      }
    ],
    "explanation": "The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession."
  },
  "semantic_rationale": "The new statements report direct positive affect ('thrilling', 'enjoy') toward a skydiving-adjacent activity under controlled conditions, directly contradicting the prior categorical dislike — but only for simulated, not real, skydiving.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
    }
  ],
  "uncertainties": []
}
```
- `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u1`：valid，位置 `{"end":41,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`；逐字引文：「Dislikes extreme sports (e.g., skydiving)」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`；逐字引文：「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- `new/new-2/unsplit-new-2`：valid，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`；逐字引文：「Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.」。

**模型记录 1（完整保存字段）**

```json
{
  "unit_id": "u2",
  "relation": "change",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "reason for disliking extreme sports",
  "new_attribute": "reason for disliking extreme sports",
  "old_value": "high injury risk",
  "new_value": "not stated as current barrier; explicitly affirms continued prioritization of safety",
  "old_conditions": {
    "kind": "unconditional"
  },
  "new_conditions": {
    "kind": "finite",
    "dimensions": {
      "context": [
        "simulated",
        "team-building event"
      ]
    }
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "u2",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
    },
    {
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
    }
  ],
  "temporal_order": {
    "relation": "after",
    "basis": [
      {
        "side": "old",
        "source_id": "ctx-1",
        "quote": "I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."
      },
      {
        "side": "new",
        "source_id": "new-0",
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
      }
    ],
    "explanation": "Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026."
  },
  "semantic_rationale": "The old claim ties dislike to injury risk as a general, unconditional barrier. The new statements do not retract that risk assessment, but show willingness to engage *only* in a low-risk variant (simulated), while reaffirming safety as a continuing priority — indicating refinement, not rejection, of the original rationale.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
    }
  ],
  "uncertainties": []
}
```
- `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u2`：valid，位置 `{"end":65,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`；逐字引文：「Dislikes extreme sports (e.g., skydiving) due to high injury risk」。
- `new/new-0/manually_mapped_new`：valid，位置 `{"end":129,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`；逐字引文：「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- `new/new-8/unsplit-new-8`：valid，位置 `{"end":105,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`；逐字引文：「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。

**模型记录 2（完整保存字段）**

```json
{
  "unit_id": "u3",
  "relation": "supplement",
  "old_subject": "I",
  "new_subject": "I",
  "old_attribute": "commitment to safety and well-being",
  "new_attribute": "commitment to safety and well-being",
  "old_value": "conflicting with extreme sports",
  "new_value": "still prioritized, even amid new thrill-seeking",
  "old_conditions": {
    "kind": "same_as_old"
  },
  "new_conditions": {
    "kind": "finite",
    "dimensions": {
      "context": [
        "simulated skydiving",
        "team-building event"
      ]
    }
  },
  "modality": "asserted",
  "old_quotes": [
    {
      "unit_id": "u3",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "conflicting with commitment to safety and well-being"
    }
  ],
  "new_quotes": [
    {
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
    }
  ],
  "temporal_order": {
    "relation": "same",
    "basis": [
      {
        "side": "new",
        "source_id": "new-8",
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
      }
    ],
    "explanation": "The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience."
  },
  "semantic_rationale": "The new utterance does not negate the old conflict claim; instead, it clarifies that the commitment remains active and constrains the scope of acceptable experiences (e.g., simulated only), thereby refining rather than replacing the prior association.",
  "semantic_basis": [
    {
      "side": "new",
      "source_id": "new-8",
      "quote": "I still prioritize safety, of course."
    }
  ],
  "uncertainties": []
}
```
- `old/e1d4f8f9-0520-427d-94fd-a2ac0ee69d03/u3`：valid，位置 `{"end":119,"start":67}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`；逐字引文：「conflicting with commitment to safety and well-being」。
- `new/new-8/unsplit-new-8`：valid，位置 `{"end":105,"start":0}`，来源 `results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`；逐字引文：「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。

### B 组每个输入候选及子判断的最终去向

- 输入 0：`B:model_record=0;candidate=relation`；关系 `change`，旧/新值 `"dislikes"` → `"found simulated skydiving thrilling; more open to trying new things"`。
  - `old_relation` → `uncertain[2]`（unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；范围 `{"kind":"unknown"}`）；`uncertain[3]`（upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；范围 `{"context":"simulated"}`）；`uncertain[4]`（upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']；范围 `{"context":"team-building event"}`）
- 输入 1：`B:model_record=1;candidate=relation`；关系 `change`，旧/新值 `"high injury risk"` → `"not stated as current barrier; explicitly affirms continued prioritization of safety"`。
  - `old_relation` → `uncertain[5]`（unconditional old scope remainder cannot be enumerated relative to proposed finite conditions；范围 `{"kind":"unknown"}`）；`uncertain[6]`（upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；范围 `{"context":"simulated"}`）；`uncertain[7]`（upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']；范围 `{"context":"team-building event"}`）
- 输入 2：`B:model_record=2;candidate=relation`；关系 `supplement`，旧/新值 `"conflicting with extreme sports"` → `"still prioritized, even amid new thrill-seeking"`。
  - `old_relation` → `uncertain[8]`（upstream validation errors: ['records[2].old_conditions cannot use same_as_old']; scope: condition kind missing or unsupported；范围 `null`）
  - `new_claim` → `uncertain[0]`（upstream validation errors: ['records[2].old_conditions cannot use same_as_old']；范围 `{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"}`）
- 输入 3：`B:model_record=0;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"found simulated skydiving thrilling"`。
  - `new_claim` → `uncertain[9]`（conflicting or potentially conflicting new evidence；范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`）
- 输入 4：`B:model_record=0;candidate=new_subfact;part=1`；关系 `new_information`，旧/新值 `null` → `"more open to trying new things"`。
  - `new_claim` → `uncertain[10]`（conflicting or potentially conflicting new evidence；范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`）
- 输入 5：`B:model_record=1;candidate=new_subfact;part=0`；关系 `new_information`，旧/新值 `null` → `"not stated as current barrier"`。
  - `new_claim` → `add[0]`（independent evidence-supported addition；范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`）
- 输入 6：`B:model_record=1;candidate=new_subfact;part=1`；关系 `new_information`，旧/新值 `null` → `"explicitly affirms continued prioritization of safety"`。
  - `new_claim` → `uncertain[1]`（semantic support or bound basis missing；范围 `{"dimensions":{"context":["simulated","team-building event"]},"kind":"finite"}`）

### 原 B 修改和新增的人工子判断

**原 B `add[0]`；模型记录 1**。原候选主体 `"I"`，属性 `"reason for disliking extreme sports"`，旧值 `null`，新值 `"not stated as current barrier"`；此前审核：“未称为当前障碍”是从未提及作出的推断；新话语不证明旧受伤风险理由已不再适用。

- 原动作关联的新引文 `new-0`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`，`{"end":129,"start":0}`）：「Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!」。
- 原动作关联的新引文 `new-8`（valid，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`，`{"end":105,"start":0}`）：「For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.」。
- **原文支持**：用户尝试了模拟跳伞并认为刺激。逐字依据 「I tried simulated skydiving. It was quite thrilling!」；模型可得性 `quote_or_rationale`：相关引文在原记录 1；该动作的 new_value 却不是体验事实；原记录 0 合并表达了模拟体验。
- **原文支持**：用户仍然优先考虑安全。逐字依据 「I still prioritize safety, of course.」；模型可得性 `combined`：原记录 1 的 new_value 将此与另一个无依据判断合并；不能把整值视为已证实。
- **无依据扩展**：旧受伤风险现在不再是障碍。逐字依据 「I still prioritize safety, of course.」；模型可得性 `unsupported_relation`：模型写 not stated as current barrier；没有再次提及并不证明原理由已消失。
- **关系仍需确认**：模拟体验是否改变真实极限运动偏好。逐字依据 「I tried simulated skydiving. It was quite thrilling!」；模型可得性 `unsupported_relation`：模型另条 change 声称态度变化，模拟与真实活动不能自动等同。

**补查：原 B 待确认的模型记录 0（模拟与真实活动）**

- **原文支持**：用户尝试模拟跳伞并觉得刺激；逐字依据 「I tried simulated skydiving. It was quite thrilling!」；`combined`：模型 new_value 有该内容但与更愿尝新合并，属性却是极限运动态度。
- **原文支持**：用户表示更愿尝试新事物；逐字依据 「It's definitely made me more open to trying new things.」；`combined`：模型 new_value 含该内容；要保留新事物范围须单独拆分，不能换成真实极限运动偏好。
- **关系仍需确认**：真实极限运动或真实跳伞偏好是否改变；逐字依据 「I tried simulated skydiving. It was quite thrilling!」；`unsupported_relation`：模型 change 把模拟体验联系到旧真实极限运动偏好；引文不足以确定该关系。

### A、C 组覆盖及新旧数量

- A 旧 `{"add":0,"modify":0,"preserve":0,"uncertain":8}` → 新 `{"add":0,"modify":0,"preserve":0,"uncertain":8}`；输入 3 条，子判断 4 项。
  - 输入 0（`change`）：old_relation → uncertain[1], uncertain[2], uncertain[3]
  - 输入 1（`change`）：old_relation → uncertain[4], uncertain[5], uncertain[6]
  - 输入 2（`supplement`）：old_relation → uncertain[7]；new_claim → uncertain[0]
- C 旧 `{"add":2,"modify":0,"preserve":0,"uncertain":4}` → 新 `{"add":2,"modify":0,"preserve":0,"uncertain":4}`；输入 4 条，子判断 5 项。
  - 输入 0（`unknown`）：old_relation → uncertain[0]
  - 输入 1（`supplement`）：old_relation → uncertain[1]；new_claim → add[0]
  - 输入 2（`unknown`）：old_relation → uncertain[3]
  - 输入 3（`supplement`）：new_claim → add[1]

## 验证、复现及剩余限制

新增测试覆盖同范围待确认阻塞并列关系、新旧子判断分别追踪、重复候选、相互冲突候选、缺失单元和二维条件组合；另对新规划器运行既有 v3 范围及接口测试。覆盖账本断言最终索引存在，回放校验保存原始响应、旧输入重建及旧人工审核动作哈希。

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python replay.py
PYTHONDONTWRITEBYTECODE=1 python make_report.py
```

尚不能自动完成自然语言的语义蕴含、拆句、否定和隐含时序审核。模型若只把获客放在引文或理由里、把转岗和平衡写成一个值、或将模拟体验绑定真实极限运动态度，必须经人工重新对齐或未来重拆并审核；现有程序不能用上面的人工子判断补写模型输出。即使逐个候选均有去向，也不意味着模型覆盖了原文所有事实。覆盖后备机制不会自动把多条等价候选认作同一输出：被聚合成单个代表的其他候选会保守待确认，可能阻止本可完成的编辑；需要进一步实现并验证安全的等价合并。

