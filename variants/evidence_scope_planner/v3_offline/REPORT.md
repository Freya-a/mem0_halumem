# 五案离线范围回放对照

五案同批保存的 v4 响应分别以首次冻结的未防护适配器与后续防护适配器投影；每组内把同一输入深拷贝给 v2 与 v3，输入 SHA-256 相等。未防护组 v2 与首次保存计划完全一致，防护组 v2 与 17 条 offline_safe 结果完全一致。本次不调用模型，未注入人工预期或独立语义授权。17 条逐项追踪见 [TRACE_17.md](TRACE_17.md)。

数字为条目数，顺序为 modify / preserve / uncertain / add；可能是对同一事实的多个原因，不能当准确率。主要算法比较应看相同的未防护投影；v4 防护投影因兼容旧版会丢失可供 v3 判断的有限范围信息，两种投影不可混为一谈。

## 接口、引文与语义审核分别统计

- 已保存响应 5 案；原调用 5 次，本次回放新增 0 次。
- 原模型字段结构通过 3/5 案；完整接口校验通过 2/5 案。
- 主引文来源定位通过 27/27 条；依据绑定通过 2/5 案。引用可定位不证明语义。
- 独立人工记录审核（按原模型记录散列绑定）：partially_supported=10；unsupported=4。未输出的事实不计入该分母。

## 防护后 17 项待确认的原因

逐条的模型判断、原引文、适配结果及 v2 拒绝原因见 [TRACE_17.md](TRACE_17.md)。按可重叠类别统计：①模型语义错误或依据不足 17 项；②字段、引文绑定或来源问题 9 项；③缺少独立语义授权 17 项；④范围无法可靠计算或条件未知 4 项；⑤其他原因 2 项。类别不互斥，不能相加得 17；某一子事实有证据，不等于整条关系和时间判断有证据。

## 独立构造的新增和修改路径

通用测试 `tests/test_paths.py` 不使用五案输入或预期。新增案例是用户明确说喜欢茶：没有独立授权时 add=0 且待确认；独立审核确认既有主张与引文后 add=1。修改案例是旧“房间关闭”，新文明确说“之前关闭、现在开放”：无需具体日历日期，未授权时 modify=0，独立审核绑定原有引文后 modify=1，位置为旧文中 closed。两次审核只改变独立授权标志，并未改写模型候选字段。可运行 `python -m unittest discover -s tests -p test_paths.py -v` 复验。

## 逐案数量对照

| 案例 | 未防护 v2 | 未防护 v3 | 防护后 v2 | 防护后 v3 |
| --- | --- | --- | --- | --- |
| susan | 0/0/5/0 | 0/0/5/0 | 0/0/5/0 | 0/0/5/0 |
| promotion | 0/0/2/0 | 0/0/2/0 | 0/0/2/0 | 0/0/2/0 |
| career_history | 0/0/3/0 | 0/0/3/0 | 0/0/3/0 | 0/0/3/0 |
| transition | 0/0/3/0 | 0/0/3/0 | 0/0/3/0 | 0/0/3/0 |
| skydiving | 0/2/2/0 | 0/0/8/0 | 0/0/4/0 | 0/0/4/0 |

## 逐案证据与范围结论

### susan

旧记忆：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement（`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`）

选中新证据：

- `new-0`：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`）
- `new-2`：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`）

原模型校验：schema=passed；quote=passed；basis=failed；coverage=passed；overall=failed。

已有独立人工预期（仅供比较，未输入规划器）：`{"add":["Daniel 的见解促进职业思考；工作生活平衡及人道目标为另行表达的内容"],"case_id":"susan","missing":["Susan 身份跨来源仅由上下文支持；新证据未明确朋友关系变化。"],"modify":[],"preserve":["ThomasSusan/Susan 朋友关系、支持和鼓励"],"provenance":"人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。","uncertain":["新证据没有独立确认全名与称呼的映射；旧来源 ctx-1 可支持语境但不消除命名歧义"]}`。

已有独立人工整体评审：结构四字段组中 schema、引文、覆盖通过，basis 因 #0 使用未绑定 ctx-1、#3 时间引文含省略号且未绑定而失败；6 条主引文都唯一匹配。预期保留 Susan 的朋友支持、独立新增 Daniel 的见解和求职计划；直接规划均待确认，未产生编辑/新增，属于对模型语义未知的保守结果而非事实不存在。模型对两条时间 same 与 unconditional 推断不足，Daniel 语义未独立输出，单元覆盖不能证明事实覆盖。。

模型记录 0；独立人工审核：partially_supported；旧记忆包含朋友 ThomasSusan，新话语有 Susan 的支持；但所引旧片段未体现别名，模型把 ctx-1 当未绑定的 semantic_basis，无法用已引用单元证明同一时间友谊及同值；无条件亦无依据。。

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

模型记录 1；独立人工审核：partially_supported；新话语确实描述 Susan 的鼓励与帮助专注，能补充支持细节；但同一时间、无条件适用并未证明，原单元短引文未独立表明对象。。

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

模型记录 2；独立人工审核：partially_supported；用户确实称当前角色对福祉支持不及期望，可作为独立陈述；无旧单元却给新旧时间关系 same，且 unconditional 缺充分依据。。

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

模型记录 3；独立人工审核：partially_supported；找符合平衡和人道目标的新工作是愿望/计划，不是已完成；但 after 只比较该句内心理活动，不是相对旧事实，所引时间依据还含省略号且不在已引用片段内。。

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

**unprotected 投影**：两代规划器同一输入 SHA-256 `b6fd81897969e85d4ea78816768acf604f3c7a507325abaa469410b89f26507b`，v2 结果与原存档一致。

**v2**（0/0/5/0；独立范围审核：appropriate_with_limit）：五项暂缓：Susan 支持与求职意向有子事实依据，但旧名映射、跨源 ctx-1、非逐字时间依据和独立语义授权未解决；模型漏掉 Daniel 的独立见解，不能把暂缓等同完整预期。

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - #0 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support","value":"has indeed been invaluable... helps me stay focused on my goals"}`
  - #1 `{"new_position":{"end":138,"start":72},"new_quote":"my current role isn't supporting my well-being as much as I'd like","new_quotes":[{"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"not supporting my well-being as much as I'd like","reason":"semantic support or bound basis missing","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"my current role isn't supporting my well-being as much as I'd like","side":"new","source_id":"new-0"}],"explanation":"Describes present state of current role; no comparative temporal marker relative to past","relation":"same"},"value":"not supporting my well-being as much as I'd like"}`
  - #2 `{"new_position":{"end":255,"start":140},"new_quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","new_quotes":[{"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals","reason":"upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job...","side":"new","source_id":"new-0"}],"explanation":"The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment.","relation":"after"},"validation_errors":["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"],"value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals"}`
  - #3 `{"fact":"friend named ThomasSusan","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Susan","old_position":{"end":30,"start":6},"old_quote":"friend named ThomasSusan","old_quotes":[{"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"ThomasSusan","reason":"upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"friend named ThomasSusan","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"explanation":"Both refer to current, ongoing friendship; no temporal shift indicated in either quote","relation":"same"},"unit_id":"friendship","validation_errors":["records[0].semantic_basis[1] not bound to cited same-side source/quote"]}`
  - #4 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"},{"alignment_index":0,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"},{"alignment_index":1,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"},{"alignment_index":3,"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}]`

**v3**（0/0/5/0；独立范围审核：appropriate_with_limit）：与未防护旧版的五项范围动作一致；不授权含错源/未认证的判断是保守的，求职计划与 Susan 鼓励可待独立确认，Daniel 未覆盖。

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - #0 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support","value":"has indeed been invaluable... helps me stay focused on my goals"}`
  - #1 `{"new_position":{"end":138,"start":72},"new_quote":"my current role isn't supporting my well-being as much as I'd like","new_quotes":[{"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"not supporting my well-being as much as I'd like","reason":"semantic support or bound basis missing","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"my current role isn't supporting my well-being as much as I'd like","side":"new","source_id":"new-0"}],"explanation":"Describes present state of current role; no comparative temporal marker relative to past","relation":"same"},"value":"not supporting my well-being as much as I'd like"}`
  - #2 `{"new_position":{"end":255,"start":140},"new_quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","new_quotes":[{"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals","reason":"upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job...","side":"new","source_id":"new-0"}],"explanation":"The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment.","relation":"after"},"validation_errors":["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"],"value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals"}`
  - #3 `{"fact":"friend named ThomasSusan","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Susan","old_position":{"end":30,"start":6},"old_quote":"friend named ThomasSusan","old_quotes":[{"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"ThomasSusan","reason":"upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"friend named ThomasSusan","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"explanation":"Both refer to current, ongoing friendship; no temporal shift indicated in either quote","relation":"same"},"unit_id":"friendship","validation_errors":["records[0].semantic_basis[1] not bound to cited same-side source/quote"]}`
  - #4 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"},{"alignment_index":0,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"},{"alignment_index":1,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"},{"alignment_index":3,"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}]`

**guarded 投影**：两代规划器同一输入 SHA-256 `b6fd81897969e85d4ea78816768acf604f3c7a507325abaa469410b89f26507b`，v2 结果与原存档一致。

**v2**（0/0/5/0；独立范围审核：appropriate_with_limit）：五项防护后待确认与既存 17 项来源和原因一致；模型未独立输出 Daniel，不能说已完整保留或新增。

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - #0 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support","value":"has indeed been invaluable... helps me stay focused on my goals"}`
  - #1 `{"new_position":{"end":138,"start":72},"new_quote":"my current role isn't supporting my well-being as much as I'd like","new_quotes":[{"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"not supporting my well-being as much as I'd like","reason":"semantic support or bound basis missing","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"my current role isn't supporting my well-being as much as I'd like","side":"new","source_id":"new-0"}],"explanation":"Describes present state of current role; no comparative temporal marker relative to past","relation":"same"},"value":"not supporting my well-being as much as I'd like"}`
  - #2 `{"new_position":{"end":255,"start":140},"new_quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","new_quotes":[{"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals","reason":"upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job...","side":"new","source_id":"new-0"}],"explanation":"The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment.","relation":"after"},"validation_errors":["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"],"value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals"}`
  - #3 `{"fact":"friend named ThomasSusan","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Susan","old_position":{"end":30,"start":6},"old_quote":"friend named ThomasSusan","old_quotes":[{"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"ThomasSusan","reason":"upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"friend named ThomasSusan","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"explanation":"Both refer to current, ongoing friendship; no temporal shift indicated in either quote","relation":"same"},"unit_id":"friendship","validation_errors":["records[0].semantic_basis[1] not bound to cited same-side source/quote"]}`
  - #4 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"},{"alignment_index":0,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"},{"alignment_index":1,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"},{"alignment_index":3,"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}]`

**v3**（0/0/5/0；独立范围审核：appropriate_with_limit）：同一防护投影给新版仍为五项待确认，未把有效子事实等同经过独立授权；该输出并不代表 Susan 或计划为假。

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - #0 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support","value":"has indeed been invaluable... helps me stay focused on my goals"}`
  - #1 `{"new_position":{"end":138,"start":72},"new_quote":"my current role isn't supporting my well-being as much as I'd like","new_quotes":[{"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"not supporting my well-being as much as I'd like","reason":"semantic support or bound basis missing","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"my current role isn't supporting my well-being as much as I'd like","side":"new","source_id":"new-0"}],"explanation":"Describes present state of current role; no comparative temporal marker relative to past","relation":"same"},"value":"not supporting my well-being as much as I'd like"}`
  - #2 `{"new_position":{"end":255,"start":140},"new_quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","new_quotes":[{"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}],"new_value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals","reason":"upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job...","side":"new","source_id":"new-0"}],"explanation":"The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment.","relation":"after"},"validation_errors":["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"],"value":"find a new job that offers a better work-life balance and aligns with my humanitarian goals"}`
  - #3 `{"fact":"friend named ThomasSusan","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Susan","old_position":{"end":30,"start":6},"old_quote":"friend named ThomasSusan","old_quotes":[{"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"ThomasSusan","reason":"upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"friend named ThomasSusan","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable.","side":"new","source_id":"new-2"}],"explanation":"Both refer to current, ongoing friendship; no temporal shift indicated in either quote","relation":"same"},"unit_id":"friendship","validation_errors":["records[0].semantic_basis[1] not bound to cited same-side source/quote"]}`
  - #4 `{"fact":"provides support and encouragement","memory_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","new_position":{"end":96,"start":0},"new_quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","new_quotes":[{"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"has indeed been invaluable... helps me stay focused on my goals","old_position":{"end":94,"start":60},"old_quote":"provides support and encouragement","old_quotes":[{"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","old_value":"provides support and encouragement","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[{"quote":"provides support and encouragement","side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed"},{"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","side":"new","source_id":"new-2"}],"explanation":"Both describe current, ongoing supportive function; no indication of change in timing or duration","relation":"same"},"unit_id":"support"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":30,"start":6},"quote":"friend named ThomasSusan","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"friendship"},{"alignment_index":0,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":94,"start":60},"quote":"provides support and encouragement","reason":null,"side":"old","source_id":"a1332815-d6ba-4bdc-9ffa-657f7315d0ed","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json","status":"valid","unit_id":"support"},{"alignment_index":1,"position":{"end":96,"start":0},"quote":"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":138,"start":72},"quote":"my current role isn't supporting my well-being as much as I'd like","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"},{"alignment_index":3,"position":{"end":255,"start":140},"quote":"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"unsplit-new-0"}]`

### promotion

旧记忆：Works at Historical Productions Ltd. as a Director（`e13b825e-7ec7-4760-821e-0581d8da5650`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`）

选中新证据：

- `new-0`：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`）

原模型校验：schema=passed；quote=passed；basis=passed；coverage=passed；overall=passed。

已有独立人工预期（仅供比较，未输入规划器）：`{"add":["晋升 lead director 的事实"],"case_id":"promotion","missing":["记录时间不是生效时间。"],"modify":["职位细化为晋升后的 lead director"],"preserve":["Historical Productions Ltd. 雇主关系；Director 作为历史和可能仍成立的宽泛描述"],"provenance":"人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。","uncertain":["准确晋升日期未知；宽泛 Director 与 lead director 的逻辑包含关系不由代码推理"]}`。

已有独立人工整体评审：schema、引用、依据绑定和覆盖均通过，4 条主引文唯一定位，但结构通过并未证明语义。预期保留同雇主与历史职位并表达晋升；直接规划两条待确认且无编辑/新增，较预期保守。晋升已发生与晋升是否晚于旧事实、旧宽泛称谓是否不再成立需要分别判断。。

模型记录 0；独立人工审核：partially_supported；引文确实显示同一公司出现在旧文和晋升句；但 employer 的主体误写公司本身而非 user，单凭未提变化不足以证明旧新状态同时或 unconditional。。

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

模型记录 1；独立人工审核：partially_supported；旧文 Director 与新话语 lead director 的晋升均有来源；recently 只相对说话时间，不能证明该晋升晚于旧记忆事实有效期，更不能自动否定 Director 作为宽泛称谓。。

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

**unprotected 投影**：两代规划器同一输入 SHA-256 `57b4b2d1f57f67393f76ce2f9f28fc845e0161931120968c36fe65af0e510a0d`，v2 结果与原存档一致。

**v2**（0/0/2/0；独立范围审核：appropriate_with_limit）：两项暂缓；公司名称重现和晋升发生有依据，但模型误写公司为主体、recently 不证明晚于旧事实且宽泛 Director 不必失效；缺独立认证。

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - #0 `{"fact":"Historical Productions Ltd.","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Historical Productions Ltd.","old_position":{"end":36,"start":9},"old_quote":"Historical Productions Ltd.","old_quotes":[{"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Historical Productions Ltd.","reason":"semantic support or bound basis missing","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","side":"new","source_id":"new-0"}],"explanation":"The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated.","relation":"same"},"unit_id":"employer"}`
  - #1 `{"fact":"Director","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"lead director","old_position":{"end":50,"start":42},"old_quote":"Director","old_quotes":[{"position":{"end":50,"start":42},"quote":"Director","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Director","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director').","relation":"after"},"unit_id":"title"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":50,"start":42},"quote":"Director","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**v3**（0/0/2/0；独立范围审核：appropriate_with_limit）：相同未防护输入的两项暂缓合理；这是缺独立授权和相对顺序，不是因为缺具体日期，原有职位历史仍需要单独保护。

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - #0 `{"fact":"Historical Productions Ltd.","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Historical Productions Ltd.","old_position":{"end":36,"start":9},"old_quote":"Historical Productions Ltd.","old_quotes":[{"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Historical Productions Ltd.","reason":"semantic support or bound basis missing","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","side":"new","source_id":"new-0"}],"explanation":"The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated.","relation":"same"},"unit_id":"employer"}`
  - #1 `{"fact":"Director","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"lead director","old_position":{"end":50,"start":42},"old_quote":"Director","old_quotes":[{"position":{"end":50,"start":42},"quote":"Director","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Director","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director').","relation":"after"},"unit_id":"title"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":50,"start":42},"quote":"Director","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**guarded 投影**：两代规划器同一输入 SHA-256 `57b4b2d1f57f67393f76ce2f9f28fc845e0161931120968c36fe65af0e510a0d`，v2 结果与原存档一致。

**v2**（0/0/2/0；独立范围审核：appropriate_with_limit）：防护组与原存记录一致：同雇主与晋升子事实可审核，但模型的主体/范围和先后不足以授权旧职位替换。

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - #0 `{"fact":"Historical Productions Ltd.","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Historical Productions Ltd.","old_position":{"end":36,"start":9},"old_quote":"Historical Productions Ltd.","old_quotes":[{"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Historical Productions Ltd.","reason":"semantic support or bound basis missing","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","side":"new","source_id":"new-0"}],"explanation":"The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated.","relation":"same"},"unit_id":"employer"}`
  - #1 `{"fact":"Director","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"lead director","old_position":{"end":50,"start":42},"old_quote":"Director","old_quotes":[{"position":{"end":50,"start":42},"quote":"Director","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Director","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director').","relation":"after"},"unit_id":"title"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":50,"start":42},"quote":"Director","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**v3**（0/0/2/0；独立范围审核：appropriate_with_limit）：防护组仍两项暂缓；不会把 recently 当做相对旧事实 after，但仍未给出人工预期中经审阅的历史保留与晋升表达。

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - #0 `{"fact":"Historical Productions Ltd.","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"Historical Productions Ltd.","old_position":{"end":36,"start":9},"old_quote":"Historical Productions Ltd.","old_quotes":[{"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Historical Productions Ltd.","reason":"semantic support or bound basis missing","relation":"same","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","side":"new","source_id":"new-0"}],"explanation":"The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated.","relation":"same"},"unit_id":"employer"}`
  - #1 `{"fact":"Director","memory_id":"e13b825e-7ec7-4760-821e-0581d8da5650","new_position":{"end":92,"start":0},"new_quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","new_quotes":[{"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"lead director","old_position":{"end":50,"start":42},"old_quote":"Director","old_quotes":[{"position":{"end":50,"start":42},"quote":"Director","reason":null,"source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","old_value":"Director","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"I recently got promoted","side":"new","source_id":"new-0"}],"explanation":"'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director').","relation":"after"},"unit_id":"title"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":36,"start":9},"quote":"Historical Productions Ltd.","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":50,"start":42},"quote":"Director","reason":null,"side":"old","source_id":"e13b825e-7ec7-4760-821e-0581d8da5650","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":92,"start":0},"quote":"I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**时间说明：** 以上新引文证明事件已发生；`recently` / `finally` 不能单独确定新状态晚于旧记忆的事实有效时间。缺具体日期与先后未知是两回事；本案先后不足以授权覆盖。

### career_history

旧记忆：Previously worked as a senior developer in Blockchain Tech（`05afde13-35bd-4d26-bbae-6de427d58db1`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`）

选中新证据：

- `new-0`：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`）
- `new-2`：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`）

原模型校验：schema=failed；quote=passed；basis=failed；coverage=passed；overall=failed。

已有独立人工预期（仅供比较，未输入规划器）：`{"add":["咨询公司获得初始客户"],"case_id":"career_history","missing":["本会话没有给出具体离职日期或直接否定历史。"],"modify":[],"preserve":["曾在 Blockchain Tech 任 senior developer 的历史"],"provenance":"人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。","uncertain":["具体离职或转型时间、当前雇佣关系及公司所有权细节"]}`。

已有独立人工整体评审：schema 失败于联系人 new_value 数组，basis 因前两条时序依据不落在其引用内而失败；5 条主引文来源唯一、覆盖通过。原模型把咨询公司获客扩展为离职、经营/创办并判 change，证据不支持；现有人工预期保留旧历史并新增获客，模型没有独立输出获客记录，直接计划保守无新增或修改，不能误认为历史已核实保留。。

模型记录 0；独立人工审核：unsupported；新句只说咨询公司获初始客户；不能由此推断本人所有权、正在经营、旧雇佣已结束或互不兼容，也不能由 lately/finally 判其晚于旧事实。旧整句及新前缀被用作时间依据但不在关联短引文内。。

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

模型记录 1；独立人工审核：unsupported；新句未给出本人咨询公司的 founder/operator 职位，不能由 my firm 推断创办者或经营者，更不能得出前职位被替代；时间依据也超出已引用片段。。

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

模型记录 2；独立人工审核：partially_supported；两位联系人和其联系开门得到用户原句支持，但 new_value 输出数组不符合字符串/null 结构，且 unconditional 未给出完整依据。。

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

**unprotected 投影**：两代规划器同一输入 SHA-256 `43d5ad0d9bec8361f322ba36891ac82cb897a8d8ee1c1e6a7ff00c0aff6a9726`，v2 结果与原存档一致。

**v2**（0/0/3/0；独立范围审核：appropriate_with_limit）：三项暂缓：咨询公司获客不证明原职位/雇主变动、本人 founder 或 operator；时间依据越过引文边界，联系人值数组不合契约，获客未被独立输出。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"new_position":{"end":111,"start":0},"new_quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","new_quotes":[{"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"reason":"upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"validation_errors":["records[2].new_value must be nonempty text or null (unknown)"]}`
  - #1 `{"fact":"Blockchain Tech","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"consulting firm","old_position":{"end":58,"start":43},"old_quote":"Blockchain Tech","old_quotes":[{"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"Blockchain Tech","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role.","relation":"after"},"unit_id":"employer","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
  - #2 `{"fact":"senior developer","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"founder / operator of consulting firm","old_position":{"end":39,"start":23},"old_quote":"senior developer","old_quotes":[{"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"senior developer","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct.","relation":"after"},"unit_id":"title","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}]`

**v3**（0/0/3/0；独立范围审核：appropriate_with_limit）：相同投影的三项待确认合理；旧文是 Previously 历史，模型错误变化未获授权，但缺少对历史及获客子事实的独立保留/新增。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"new_position":{"end":111,"start":0},"new_quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","new_quotes":[{"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"reason":"upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"validation_errors":["records[2].new_value must be nonempty text or null (unknown)"]}`
  - #1 `{"fact":"Blockchain Tech","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"consulting firm","old_position":{"end":58,"start":43},"old_quote":"Blockchain Tech","old_quotes":[{"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"Blockchain Tech","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role.","relation":"after"},"unit_id":"employer","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
  - #2 `{"fact":"senior developer","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"founder / operator of consulting firm","old_position":{"end":39,"start":23},"old_quote":"senior developer","old_quotes":[{"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"senior developer","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct.","relation":"after"},"unit_id":"title","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}]`

**guarded 投影**：两代规划器同一输入 SHA-256 `43d5ad0d9bec8361f322ba36891ac82cb897a8d8ee1c1e6a7ff00c0aff6a9726`，v2 结果与原存档一致。

**v2**（0/0/3/0；独立范围审核：appropriate_with_limit）：保留旧版四类结果和来源限制：联系人的新信息有部分依据但结构字段错误，历史角色变化及相对时序不能由获客推知。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"new_position":{"end":111,"start":0},"new_quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","new_quotes":[{"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"reason":"upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"validation_errors":["records[2].new_value must be nonempty text or null (unknown)"]}`
  - #1 `{"fact":"Blockchain Tech","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"consulting firm","old_position":{"end":58,"start":43},"old_quote":"Blockchain Tech","old_quotes":[{"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"Blockchain Tech","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role.","relation":"after"},"unit_id":"employer","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
  - #2 `{"fact":"senior developer","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"founder / operator of consulting firm","old_position":{"end":39,"start":23},"old_quote":"senior developer","old_quotes":[{"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"senior developer","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct.","relation":"after"},"unit_id":"title","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}]`

**v3**（0/0/3/0；独立范围审核：appropriate_with_limit）：防护组与 v2 同为三项暂缓；尚未独立保留过去任职或新增获客，暂缓不等于否定这些子事实。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"new_position":{"end":111,"start":0},"new_quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","new_quotes":[{"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"reason":"upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']","relation":"new_information","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","temporal_order":{"basis":[],"explanation":null,"relation":"unknown"},"validation_errors":["records[2].new_value must be nonempty text or null (unknown)"]}`
  - #1 `{"fact":"Blockchain Tech","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"consulting firm","old_position":{"end":58,"start":43},"old_quote":"Blockchain Tech","old_quotes":[{"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"Blockchain Tech","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role.","relation":"after"},"unit_id":"employer","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","records[0].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
  - #2 `{"fact":"senior developer","memory_id":"05afde13-35bd-4d26-bbae-6de427d58db1","new_position":{"end":103,"start":48},"new_quote":"my consulting firm finally secured some initial clients","new_quotes":[{"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"founder / operator of consulting firm","old_position":{"end":39,"start":23},"old_quote":"senior developer","old_quotes":[{"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","old_value":"senior developer","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Previously worked as a senior developer in Blockchain Tech","side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1"},{"quote":"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients","side":"new","source_id":"new-0"}],"explanation":"Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct.","relation":"after"},"unit_id":"title","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","records[1].temporal_order.basis[1] not bound to cited same-side source/quote"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":58,"start":43},"quote":"Blockchain Tech","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"employer"},{"alignment_index":0,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":39,"start":23},"quote":"senior developer","reason":null,"side":"old","source_id":"05afde13-35bd-4d26-bbae-6de427d58db1","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json","status":"valid","unit_id":"title"},{"alignment_index":1,"position":{"end":103,"start":48},"quote":"my consulting firm finally secured some initial clients","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":2,"position":{"end":111,"start":0},"quote":"MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}]`

### transition

旧记忆：Looking for a new job with better work-life balance（`e6ab178b-c0f9-4adb-bfb7-e4648617a950`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`）

选中新证据：

- `new-0`：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`）

原模型校验：schema=passed；quote=passed；basis=passed；coverage=passed；overall=passed。

已有独立人工预期（仅供比较，未输入规划器）：`{"add":["新职位工作生活平衡改善"],"case_id":"transition","missing":["没有具体职位名或事实生效日期。"],"modify":["求职进展改为已经转到新职位，不断言停止任何求职"],"preserve":["追求较好工作生活平衡的旧目标"],"provenance":"人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。","uncertain":["新职位名称和实际切换日期；是否继续另找工作"]}`。

已有独立人工整体评审：schema、主引文、basis 绑定和覆盖都通过，4 条主引文唯一命中；但结构通过不证明语义先后。人工预期保护旧平衡目标、表达已转岗及平衡改善；模型直接计划没有编辑、保留或新增，只列待确认。模型根据 finally 认定结束求职和时间 after 超出了证据；没有具体日期并不是拒绝的直接原因。。

模型记录 0；独立人工审核：partially_supported；已转岗和平衡改善有新引文；finally 不单独证明切换晚于旧记忆有效期，也不证明停止找工作，且 unconditional 和完整替换旧求职状态缺依据。。

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

模型记录 1；独立人工审核：partially_supported；新话语确实称现在平衡更健康；是否完全实现此前目标、此前和现在动机同一时间及 unconditional 未证明。。

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

**unprotected 投影**：两代规划器同一输入 SHA-256 `fc6bb853e167fe2655d9bca9fd2d8caa7584fd6b32d31e60acc13a44c205de27`，v2 结果与原存档一致。

**v2**（0/0/3/0；独立范围审核：appropriate_with_limit）：三项暂缓：引文支持已转岗与现在平衡更健康，但不证明停止找工作、原目标完全实现或新状态晚于旧事实；平衡目标未输出为保留。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search","value":"better work-life balance (now realized as healthier balance)"}`
  - #1 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":0},"new_quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"transitioned to a new role with healthier work-life balance","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"looking for a new job with better work-life balance","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Looking for a new job with better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"},{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'","relation":"after"},"unit_id":"job_search"}`
  - #2 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":0,"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":1,"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**v3**（0/0/3/0；独立范围审核：appropriate_with_limit）：同一未防护输入的三项暂缓是保守处理，finally 不足以单独证明先后；尚未独立表达已发生转岗和改善。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search","value":"better work-life balance (now realized as healthier balance)"}`
  - #1 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":0},"new_quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"transitioned to a new role with healthier work-life balance","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"looking for a new job with better work-life balance","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Looking for a new job with better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"},{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'","relation":"after"},"unit_id":"job_search"}`
  - #2 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":0,"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":1,"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**guarded 投影**：两代规划器同一输入 SHA-256 `fc6bb853e167fe2655d9bca9fd2d8caa7584fd6b32d31e60acc13a44c205de27`，v2 结果与原存档一致。

**v2**（0/0/3/0；独立范围审核：appropriate_with_limit）：保留既存三项待确认：补充改善与旧目标影响分别审核；没有具体日期并非自动失败原因。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search","value":"better work-life balance (now realized as healthier balance)"}`
  - #1 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":0},"new_quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"transitioned to a new role with healthier work-life balance","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"looking for a new job with better work-life balance","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Looking for a new job with better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"},{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'","relation":"after"},"unit_id":"job_search"}`
  - #2 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":0,"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":1,"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**v3**（0/0/3/0；独立范围审核：appropriate_with_limit）：防护组两版均没有授权覆盖或新增；仍须分别保护平衡目标和记录更健康平衡，不可将待确认误作反证。

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - #0 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"semantic support or bound basis missing","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search","value":"better work-life balance (now realized as healthier balance)"}`
  - #1 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":0},"new_quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"transitioned to a new role with healthier work-life balance","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"looking for a new job with better work-life balance","reason":"semantic support or bound basis missing","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"Looking for a new job with better work-life balance","side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950"},{"quote":"I've finally transitioned to a new role","side":"new","source_id":"new-0"}],"explanation":"'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'","relation":"after"},"unit_id":"job_search"}`
  - #2 `{"fact":"Looking for a new job with better work-life balance","memory_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","new_position":{"end":135,"start":70},"new_quote":"The balance between work and personal life is much healthier now.","new_quotes":[{"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}],"new_value":"better work-life balance (now realized as healthier balance)","old_position":{"end":51,"start":0},"old_quote":"Looking for a new job with better work-life balance","old_quotes":[{"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","old_value":"better work-life balance","reason":"impact of new information on old fact is not established","relation":"supplement","scope":{"kind":"unconditional"},"semantic_support":"unknown","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","temporal_order":{"basis":[{"quote":"The balance between work and personal life is much healthier now.","side":"new","source_id":"new-0"}],"explanation":"The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself.","relation":"same"},"unit_id":"job_search"}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":0,"position":{"end":135,"start":0},"quote":"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":51,"start":0},"quote":"Looking for a new job with better work-life balance","reason":null,"side":"old","source_id":"e6ab178b-c0f9-4adb-bfb7-e4648617a950","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json","status":"valid","unit_id":"job_search"},{"alignment_index":1,"position":{"end":135,"start":70},"quote":"The balance between work and personal life is much healthier now.","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"}]`

**时间说明：** 以上新引文证明事件已发生；`recently` / `finally` 不能单独确定新状态晚于旧记忆的事实有效时间。缺具体日期与先后未知是两回事；本案先后不足以授权覆盖。

### skydiving

旧记忆：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being（`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`）

选中新证据：

- `new-0`：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`）
- `new-2`：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`）
- `new-8`：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`）

原模型校验：schema=failed；quote=passed；basis=failed；coverage=passed；overall=failed。

已有独立人工预期（仅供比较，未输入规划器）：`{"add":["尝试模拟跳伞且感觉刺激；仍重视安全"],"case_id":"skydiving","missing":["没有确定的事实有效日期；模拟体验不证明真实跳伞偏好变化。"],"modify":[],"preserve":["旧极限运动顾虑、受伤风险和安全福祉取向；不要推广为所有偏好已改变"],"provenance":"人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。","uncertain":["模拟跳伞与旧极限运动的覆盖关系、当前真实跳伞偏好；u3 短引文本身不完整"]}`。

已有独立人工整体评审：schema 因旧侧 same_as_old 失败，basis 因前两条引用未关联 ctx-1 失败，8 条主引文唯一且单位关联有效、覆盖通过。模型仍把模拟体验扩展成真实极限运动偏好/风险理由变化，并依据对话时间声称 after；这不成立。v2 直接计划没有修改、新增，u3 列待确认，但对 u1/u2 输出了无条件 preserve：其旧 unconditional 与新 finite 的条件无法求差，且依据错误被空交集路径掩盖；保留原文方向虽可审慎接受，报告必须指出范围理由错误和遗漏待确认。人工预期保留旧顾虑、独立增加模拟体验及安全优先；未授权模型直接添加，因此当前计划比预期更保守。 事后离线保护重算将两条不成立的 preserve 转为待确认；这只是在现有适配层防止不支持的范围计算，并非证明旧条件或模型语义。首次输出原样保存，未重跑模型。。

模型记录 0；独立人工审核：unsupported；新引文支持模拟跳伞刺激及更愿尝新，不证明真实极限运动或旧偏好改变；模型自身声称与旧厌恶矛盾并把模拟/团建写成同一维度的两个互斥枚举而不是组合，同时用 ctx-1 未关联时间依据及发言日期推 after。。

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

模型记录 1；独立人工审核：unsupported；新句没有撤回高受伤风险是旧厌恶理由；模型将未再提及当变化，模拟亦不能证明低风险，更不能据对话日期推事实时序；旧 ctx-1 不在已关联旧引文内。。

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

模型记录 2；独立人工审核：partially_supported；新话语支持现在重视安全，但不证明旧极限运动与安全福祉的整条冲突因果继续成立，亦未证明只接受模拟；old_conditions 使用 same_as_old 违反结构约定。。

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

**unprotected 投影**：两代规划器同一输入 SHA-256 `287c98c8fc24f8db85351259482dcead71771b941fe5483c733e6f9ce1a75b07`，v2 结果与原存档一致。

**v2**（0/2/2/0；独立范围审核：unsupported）：u1/u2 两项无条件 preserve 的 outside-scope 理由不可成立：无条件旧域无法枚举有限新条件的余集，且模型时间依据引用未关联 ctx-1；漏列受影响部分的待确认。旧顾虑可以作为原文被保留，但不能把错误的范围证明当成依据。

- modify（0）：
- preserve（2）：
  - #0 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"unchanged, earlier evidence, or outside evidence scope","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #1 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"unchanged, earlier evidence, or outside evidence scope","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
- uncertain（2）：
  - #0 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","scope":{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"},"semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"],"value":"still prioritized, even amid new thrill-seeking"}`
  - #1 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"},{"alignment_index":1,"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"},{"alignment_index":1,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"},{"alignment_index":2,"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"},{"alignment_index":2,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}]`

**v3**（0/0/8/0；独立范围审核：appropriate_with_limit）：两项旧事实无条件 preserve 已撤回；未枚举的旧域剩余列 unknown，并对模型提出的有限候选列待确认。模型把 simulated 与 team-building 置于同一维度的两个值，属于未经证实的候选表达，不能视作实际两个正确范围；仍未独立新增模拟体验和安全偏好。

- modify（0）：
- preserve（0）：
- uncertain（8）：
  - #0 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","scope":{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"},"semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"],"value":"still prioritized, even amid new thrill-seeking"}`
  - #1 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"unconditional old scope remainder cannot be enumerated relative to proposed finite conditions","relation":"change","scope":{"kind":"unknown"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #2 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"change","scope":{"context":"simulated"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #3 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"change","scope":{"context":"team-building event"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #4 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"unconditional old scope remainder cannot be enumerated relative to proposed finite conditions","relation":"change","scope":{"kind":"unknown"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #5 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"change","scope":{"context":"simulated"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #6 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote']","relation":"change","scope":{"context":"team-building event"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"]}`
  - #7 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']; scope: condition kind missing or unsupported","relation":"supplement","semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"},{"alignment_index":1,"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"},{"alignment_index":1,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"},{"alignment_index":2,"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"},{"alignment_index":2,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}]`

**guarded 投影**：两代规划器同一输入 SHA-256 `2868fd751241286a8c81dd39a2256b1365f9fa4daff7838f7e4f371dca295c17`，v2 结果与原存档一致。

**v2**（0/0/4/0；独立范围审核：appropriate_with_limit）：四项暂缓与保存的 v4 防护后 17 项一致；适配器将无法求差的新范围降为 unknown，避免旧版误报无条件保留，原条件保存在 raw_record。

- modify（0）：
- preserve（0）：
- uncertain（4）：
  - #0 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","scope":{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"},"semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"],"value":"still prioritized, even amid new thrill-seeking"}`
  - #1 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"]}`
  - #2 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"]}`
  - #3 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"},{"alignment_index":1,"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"},{"alignment_index":1,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"},{"alignment_index":2,"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"},{"alignment_index":2,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}]`

**v3**（0/0/4/0；独立范围审核：appropriate_with_limit）：四项暂缓适合已经被防护改成 unknown 的投影，不能用来证明 v3 处理原 finite 条件的能力；模拟体验与安全子事实仍缺独立授权，真实偏好不能由模拟推翻。

- modify（0）：
- preserve（0）：
- uncertain（4）：
  - #0 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']","relation":"supplement","scope":{"dimensions":{"context":["simulated skydiving","team-building event"]},"kind":"finite"},"semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"],"value":"still prioritized, even amid new thrill-seeking"}`
  - #1 `{"fact":"Dislikes extreme sports (e.g., skydiving)","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"}],"new_value":"found simulated skydiving thrilling; more open to trying new things","old_position":{"end":41,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving)","old_quotes":[{"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"dislikes","reason":"upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']; scope: condition kind missing or unsupported","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession.","relation":"after"},"unit_id":"u1","validation_errors":["records[0].temporal_order.basis[0] not bound to cited same-side source/quote","planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"]}`
  - #2 `{"fact":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_quotes":[{"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"not stated as current barrier; explicitly affirms continued prioritization of safety","old_position":{"end":65,"start":0},"old_quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","old_quotes":[{"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"high injury risk","reason":"upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']; scope: condition kind missing or unsupported","relation":"change","scope":{"kind":"unconditional"},"semantic_support":"unknown","temporal_order":{"basis":[{"quote":"I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.","side":"old","source_id":"ctx-1"},{"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","side":"new","source_id":"new-0"}],"explanation":"Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026.","relation":"after"},"unit_id":"u2","validation_errors":["records[1].temporal_order.basis[0] not bound to cited same-side source/quote","planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"]}`
  - #3 `{"fact":"conflicting with commitment to safety and well-being","memory_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","new_position":{"end":105,"start":0},"new_quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","new_quotes":[{"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}],"new_value":"still prioritized, even amid new thrill-seeking","old_position":{"end":119,"start":67},"old_quote":"conflicting with commitment to safety and well-being","old_quotes":[{"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"}],"old_source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","old_value":"conflicting with extreme sports","reason":"upstream validation errors: ['records[2].old_conditions cannot use same_as_old']; scope: condition kind missing or unsupported","relation":"supplement","semantic_support":"unknown","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","temporal_order":{"basis":[{"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","side":"new","source_id":"new-8"}],"explanation":"The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience.","relation":"same"},"unit_id":"u3","validation_errors":["records[2].old_conditions cannot use same_as_old"]}`
- add（0）：
- 可编辑位置：`[]`
- 保护事实：`[]`
- 引文检查：`[{"alignment_index":0,"position":{"end":41,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving)","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u1"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":0,"position":{"end":129,"start":0},"quote":"Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.","reason":null,"side":"new","source_id":"new-2","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content","status":"valid","unit_id":"unsplit-new-2"},{"alignment_index":1,"position":{"end":65,"start":0},"quote":"Dislikes extreme sports (e.g., skydiving) due to high injury risk","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u2"},{"alignment_index":1,"position":{"end":129,"start":0},"quote":"Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!","reason":null,"side":"new","source_id":"new-0","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content","status":"valid","unit_id":"manually_mapped_new"},{"alignment_index":1,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"},{"alignment_index":2,"position":{"end":119,"start":67},"quote":"conflicting with commitment to safety and well-being","reason":null,"side":"old","source_id":"e1d4f8f9-0520-427d-94fd-a2ac0ee69d03","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json","status":"valid","unit_id":"u3"},{"alignment_index":2,"position":{"end":105,"start":0},"quote":"For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.","reason":null,"side":"new","source_id":"new-8","source_ref":"results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content","status":"valid","unit_id":"unsplit-new-8"}]`

## 限制

未经独立语义授权的模型候选不会被当作已审核事实；模型组没有修改或新增，并不意味着接口无可走通路径。独立构造的通用新增及修改用例见 README。不可计算的范围必须待确认，模型拟定的有限组合不能自动视为正确；尤其跳伞模型把模拟与团建列为同一维度两个值，不足以证明是互斥分类。

一个复合 unit 中不同主体或属性的多个关系可能被合并、保守误判为值冲突，产生过多待确认；当前版本不具备完整的复合事实消歧能力，需要拆分或人工复核。
