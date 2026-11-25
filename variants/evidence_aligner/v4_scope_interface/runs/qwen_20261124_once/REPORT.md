# 五案对齐与范围规划小样本报告

独立语义审核以模型原始记录的 SHA-256 绑定，不从模型自述或引文命中自动生成。未审或不匹配项标为 not_reviewed；这不是正式论文准确率。模型直接规划结果维持 semantic_support=unknown，不注入人工预期。

**运行信息与统计**

```json
{
  "manifest": {
    "model": "qwen-plus-2025-12-01",
    "temperature": 0,
    "response_format": {
      "type": "json_object"
    },
    "max_tokens": 8192,
    "automatic_retries": 0,
    "maximum_requests": 5,
    "request_attempts": 5,
    "model_responses": 5,
    "status": "completed",
    "prompt_sha256": "2c84229b2cfed9036afbccb8e98cbf3a7db18d91e49dd2aa620c1fef4e94d372",
    "cases": [
      {
        "case_id": "susan",
        "status": "failed",
        "attempts": 1,
        "elapsed_seconds": 42.579,
        "returned_model": "qwen-plus-2025-12-01",
        "usage": {
          "completion_tokens": 1856,
          "prompt_tokens": 7923,
          "total_tokens": 9779,
          "completion_tokens_details": null,
          "prompt_tokens_details": null
        }
      },
      {
        "case_id": "promotion",
        "status": "passed",
        "attempts": 1,
        "elapsed_seconds": 20.28,
        "returned_model": "qwen-plus-2025-12-01",
        "usage": {
          "completion_tokens": 875,
          "prompt_tokens": 12538,
          "total_tokens": 13413,
          "completion_tokens_details": null,
          "prompt_tokens_details": null
        }
      },
      {
        "case_id": "career_history",
        "status": "failed",
        "attempts": 1,
        "elapsed_seconds": 29.835,
        "returned_model": "qwen-plus-2025-12-01",
        "usage": {
          "completion_tokens": 1306,
          "prompt_tokens": 13576,
          "total_tokens": 14882,
          "completion_tokens_details": null,
          "prompt_tokens_details": null
        }
      },
      {
        "case_id": "transition",
        "status": "passed",
        "attempts": 1,
        "elapsed_seconds": 22.896,
        "returned_model": "qwen-plus-2025-12-01",
        "usage": {
          "completion_tokens": 997,
          "prompt_tokens": 12095,
          "total_tokens": 13092,
          "completion_tokens_details": null,
          "prompt_tokens_details": null
        }
      },
      {
        "case_id": "skydiving",
        "status": "failed",
        "attempts": 1,
        "elapsed_seconds": 40.424,
        "returned_model": "qwen-plus-2025-12-01",
        "usage": {
          "completion_tokens": 1799,
          "prompt_tokens": 8235,
          "total_tokens": 10034,
          "completion_tokens_details": null,
          "prompt_tokens_details": null
        }
      }
    ]
  },
  "statistics": {
    "case_count": 5,
    "request_attempts": 5,
    "model_responses": 5,
    "structured_passed": 3,
    "quote_passed_cases": 5,
    "basis_passed_cases": 2,
    "coverage_passed_cases": 5,
    "complete_validation_passed": 2,
    "quote_checks": {
      "valid": 27
    },
    "record_reviews": {
      "partially_supported": 10,
      "unsupported": 4
    },
    "action_reviews": {
      "uncertain:supported": 15,
      "preserve:unsupported": 2
    },
    "plans": {
      "uncertain": 15,
      "preserve": 2
    },
    "safe_plans": {
      "uncertain": 17
    },
    "safe_action_reviews": {
      "uncertain:supported": 17
    }
  }
}
```

结构通过、引用定位、语义支持和规划结果是独立指标。模型原始响应与请求详情保存在每案 JSON；原始证据、来源指针和全部位置见各案校验。

首次请求所用代码与提示词的冻结快照保存在 `frozen_at_call/`；首次直接规划结果未改动。`offline_safe/` 使用事后加保护的适配器对同一回复纯离线重算，保存 adapter/planner/响应/输入散列；它没有额外调用模型，也不能补齐未知范围或推断语义。

## susan

**请求与来源**

```json
{
  "call": {
    "status": "failed",
    "attempts": 1,
    "request_transmitted": true,
    "elapsed_seconds": 42.579,
    "returned_model": "qwen-plus-2025-12-01",
    "finish_reason": "stop"
  },
  "usage": {
    "completion_tokens": 1856,
    "prompt_tokens": 7923,
    "total_tokens": 9779,
    "completion_tokens_details": null,
    "prompt_tokens_details": null
  }
}
```

旧记忆：{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "text": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement", "speaker": "memory", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json"}

输入所选新单元：[{"unit_id": "manually_mapped_new", "source_id": "new-2", "memory_quotes": ["Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."]}, {"unit_id": "unsplit-new-0", "source_id": "new-0", "memory_quotes": ["I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."]}]

所选新证据及来源：[{"source_id": "new-0", "side": "new", "speaker": "user", "text": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.", "recorded_at": "Feb 05, 2026, 17:13:15", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content"}, {"source_id": "new-2", "side": "new", "speaker": "user", "text": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.", "recorded_at": "Feb 05, 2026, 17:15:18", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"}]

原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：[{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "verified", "reason": null}, {"source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "status": "verified", "reason": null}, {"source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "verified", "reason": null}]

独立人工预期：{"case_id": "susan", "provenance": "人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。", "modify": [], "preserve": ["ThomasSusan/Susan 朋友关系、支持和鼓励"], "uncertain": ["新证据没有独立确认全名与称呼的映射；旧来源 ctx-1 可支持语境但不消除命名歧义"], "add": ["Daniel 的见解促进职业思考；工作生活平衡及人道目标为另行表达的内容"], "missing": ["Susan 身份跨来源仅由上下文支持；新证据未明确朋友关系变化。"]}

**接口和逐引文校验**（引用定位不等于语义支持）

```json
{
  "status": "failed",
  "errors": [
    "records[0].semantic_basis[1] not bound to cited same-side source/quote",
    "records[3].temporal_order.basis[0] not bound to cited same-side source/quote"
  ],
  "schema_status": "passed",
  "quote_status": "passed",
  "basis_status": "failed",
  "coverage_status": "passed",
  "schema_errors": [],
  "quote_errors": [],
  "basis_errors": [
    "records[0].semantic_basis[1] not bound to cited same-side source/quote",
    "records[3].temporal_order.basis[0] not bound to cited same-side source/quote"
  ],
  "coverage_errors": [],
  "record_errors": [
    [
      "records[0].semantic_basis[1] not bound to cited same-side source/quote"
    ],
    [],
    [],
    [
      "records[3].temporal_order.basis[0] not bound to cited same-side source/quote"
    ]
  ],
  "quote_checks": [
    {
      "record_index": 0,
      "side": "old",
      "index": 0,
      "unit_id": "friendship",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "friend named ThomasSusan",
      "status": "valid",
      "position": {
        "start": 6,
        "end": 30
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 96
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "old",
      "index": 0,
      "unit_id": "support",
      "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "quote": "provides support and encouragement",
      "status": "valid",
      "position": {
        "start": 60,
        "end": 94
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-2",
      "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 96
      },
      "reason": null
    },
    {
      "record_index": 2,
      "side": "new",
      "index": 0,
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "my current role isn't supporting my well-being as much as I'd like",
      "status": "valid",
      "position": {
        "start": 72,
        "end": 138
      },
      "reason": null
    },
    {
      "record_index": 3,
      "side": "new",
      "index": 0,
      "unit_id": "unsplit-new-0",
      "source_id": "new-0",
      "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "status": "valid",
      "position": {
        "start": 140,
        "end": 255
      },
      "reason": null
    }
  ],
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**模型记录 0**

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
独立语义审核：{"sha256": "8c58fc2178c70dfedd19429d66b60473ff730ef2a80de6017fc04c43760adf8a", "verdict": "partially_supported", "reason": "旧记忆包含朋友 ThomasSusan，新话语有 Susan 的支持；但所引旧片段未体现别名，模型把 ctx-1 当未绑定的 semantic_basis，无法用已引用单元证明同一时间友谊及同值；无条件亦无依据。"}

**模型记录 1**

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
独立语义审核：{"sha256": "ca6d1c572284c3c2fd518e2f39859342c4aae95f412db9476d0e2d70f0b16a52", "verdict": "partially_supported", "reason": "新话语确实描述 Susan 的鼓励与帮助专注，能补充支持细节；但同一时间、无条件适用并未证明，原单元短引文未独立表明对象。"}

**模型记录 2**

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
独立语义审核：{"sha256": "c2deb92e099da22d6ceae0df7e71476726c0e2e9da7b5486d90edfadbdb3cb3e", "verdict": "partially_supported", "reason": "用户确实称当前角色对福祉支持不及期望，可作为独立陈述；无旧单元却给新旧时间关系 same，且 unconditional 缺充分依据。"}

**模型记录 3**

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
独立语义审核：{"sha256": "d629b9dce70f6573424901c1f7076838d59e367c03d612637407e371e8bdb801", "verdict": "partially_supported", "reason": "找符合平衡和人道目标的新工作是愿望/计划，不是已完成；但 after 只比较该句内心理活动，不是相对旧事实，所引时间依据还含省略号且不在已引用片段内。"}

**未经独立审核补全的模型直接规划结果**

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - 输出：{"unit_id": "support", "fact": "provides support and encouragement", "relation": "supplement", "subject": "Susan", "attribute": "support and encouragement", "old_value": "provides support and encouragement", "new_value": "has indeed been invaluable... helps me stay focused on my goals", "old_quotes": [{"side": "old", "unit_id": "support", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement", "position": {"start": 60, "end": 94}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "provides support and encouragement", "old_position": {"start": 60, "end": 94}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "explanation": "Both describe current, ongoing supportive function; no indication of change in timing or duration"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "value": "has indeed been invaluable... helps me stay focused on my goals", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "db43f7440a259ccaf45d57d739447930356929a9910952fd7d875495f8378f62", "verdict": "supported", "reason": "补充的支持细节有证据，但模型语义自证不可作为独立授权；暂缓新增符合 v2 契约，人工核对后可另评。"}
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "current role", "attribute": "supports well-being", "old_value": null, "new_value": "not supporting my well-being as much as I'd like", "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-0", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like", "position": {"start": 72, "end": 138}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "my current role isn't supporting my well-being as much as I'd like", "new_position": {"start": 72, "end": 138}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like"}], "explanation": "Describes present state of current role; no comparative temporal marker relative to past"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like"}], "value": "not supporting my well-being as much as I'd like", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "0bbb70d8003a56a1585a41f4acfb9eec8bfb8c179f7a269e72560ba654841e3e", "verdict": "supported", "reason": "角色对福祉的评价有新证据，但模型无独立语义授权，暂缓符合接口；并不能因此认定该事实为假。"}
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "I", "attribute": "career goal", "old_value": null, "new_value": "find a new job that offers a better work-life balance and aligns with my humanitarian goals", "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-0", "source_id": "new-0", "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.", "position": {"start": 140, "end": 255}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.", "new_position": {"start": 140, "end": 255}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "new", "source_id": "new-0", "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job..."}], "explanation": "The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."}], "value": "find a new job that offers a better work-life balance and aligns with my humanitarian goals", "scope": {"kind": "unconditional"}, "status": "planned", "reason": "upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "f3cc1940ce20fb3f9475820bf1e08c35a8631b5758fe3207484d46c9cda2914f", "verdict": "supported", "reason": "目标是计划；语义授权未给且时间依据不属于关联引文，暂缓符合接口，不能当已找到工作。"}
  - 输出：{"unit_id": "friendship", "fact": "friend named ThomasSusan", "relation": "same", "subject": "ThomasSusan", "attribute": "name", "old_value": "ThomasSusan", "new_value": "Susan", "old_quotes": [{"side": "old", "unit_id": "friendship", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "friend named ThomasSusan", "position": {"start": 6, "end": 30}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "friend named ThomasSusan", "old_position": {"start": 6, "end": 30}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].semantic_basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "friend named ThomasSusan"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable."}], "explanation": "Both refer to current, ongoing friendship; no temporal shift indicated in either quote"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}, {"side": "old", "source_id": "ctx-1", "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "7237caa7348ce7fb3dda03768cea258ef5abffed8d2057ecaeb495583e6547b6", "verdict": "supported", "reason": "friendship 语义依据引入未绑定 ctx-1，并且 same 与姓名映射缺充分关联证据；暂缓适当。"}
  - 输出：{"unit_id": "support", "fact": "provides support and encouragement", "relation": "supplement", "subject": "Susan", "attribute": "provides support and encouragement", "old_value": "provides support and encouragement", "new_value": "has indeed been invaluable... helps me stay focused on my goals", "old_quotes": [{"side": "old", "unit_id": "support", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement", "position": {"start": 60, "end": 94}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "provides support and encouragement", "old_position": {"start": 60, "end": 94}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "explanation": "Both describe current, ongoing supportive function; no indication of change in timing or duration"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "scope": {"kind": "unconditional"}, "reason": "impact of new information on old fact is not established"}；独立审核：{"sha256": "f101fbbc47cc8bcd2528262649be99494325bd818612e3f8454d89f37fea8504", "verdict": "supported", "reason": "支持补充本身并不证明对旧事实影响；暂缓该影响符合契约，同时应保留原文，不应解释成支持消失。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

规划器引文位置和原因：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "friendship",
    "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "quote": "friend named ThomasSusan",
    "position": {
      "start": 6,
      "end": 30
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-2",
    "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "position": {
      "start": 0,
      "end": 96
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "support",
    "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "quote": "provides support and encouragement",
    "position": {
      "start": 60,
      "end": 94
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-2",
    "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "position": {
      "start": 0,
      "end": 96
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-0",
    "source_id": "new-0",
    "quote": "my current role isn't supporting my well-being as much as I'd like",
    "position": {
      "start": 72,
      "end": 138
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 3,
    "side": "new",
    "unit_id": "unsplit-new-0",
    "source_id": "new-0",
    "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
    "position": {
      "start": 140,
      "end": 255
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）

状态与散列：{"status": "completed_offline", "provenance": {"artifact_sha256": "e103297ef7fedb6215bd2e793e5b273b10c4f449371122974b45c82872e2cb45", "adapter_sha256": "d6c1a3f08c6a77d8908007422a68d710fa5d1ca9941f82ef277afbaff6077b8e", "planner_sha256": "3c46dc51936a19d0b52dcaf08f4f5b1edb2ed8e41ad403fd0c9b4dbdf49042a1", "raw_response_sha256": "b8e81e0820d90d8b0995af2f58dae547200f9a6dafba66a1e646aecf495cbbc3"}}

- modify（0）：
- preserve（0）：
- uncertain（5）：
  - 输出：{"unit_id": "support", "fact": "provides support and encouragement", "relation": "supplement", "subject": "Susan", "attribute": "support and encouragement", "old_value": "provides support and encouragement", "new_value": "has indeed been invaluable... helps me stay focused on my goals", "old_quotes": [{"side": "old", "unit_id": "support", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement", "position": {"start": 60, "end": 94}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "provides support and encouragement", "old_position": {"start": 60, "end": 94}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "explanation": "Both describe current, ongoing supportive function; no indication of change in timing or duration"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "value": "has indeed been invaluable... helps me stay focused on my goals", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "db43f7440a259ccaf45d57d739447930356929a9910952fd7d875495f8378f62", "verdict": "supported", "reason": "补充的支持细节有证据，但模型语义自证不可作为独立授权；暂缓新增符合 v2 契约，人工核对后可另评。"}
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "current role", "attribute": "supports well-being", "old_value": null, "new_value": "not supporting my well-being as much as I'd like", "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-0", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like", "position": {"start": 72, "end": 138}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "my current role isn't supporting my well-being as much as I'd like", "new_position": {"start": 72, "end": 138}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like"}], "explanation": "Describes present state of current role; no comparative temporal marker relative to past"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my current role isn't supporting my well-being as much as I'd like"}], "value": "not supporting my well-being as much as I'd like", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "0bbb70d8003a56a1585a41f4acfb9eec8bfb8c179f7a269e72560ba654841e3e", "verdict": "supported", "reason": "角色对福祉的评价有新证据，但模型无独立语义授权，暂缓符合接口；并不能因此认定该事实为假。"}
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "I", "attribute": "career goal", "old_value": null, "new_value": "find a new job that offers a better work-life balance and aligns with my humanitarian goals", "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-0", "source_id": "new-0", "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.", "position": {"start": 140, "end": 255}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.", "new_position": {"start": 140, "end": 255}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[3].temporal_order.basis[0] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "new", "source_id": "new-0", "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job..."}], "explanation": "The realization ('I've realized') precedes the plan ('to find a new job'); the plan is future-directed and follows the assessment."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."}], "value": "find a new job that offers a better work-life balance and aligns with my humanitarian goals", "scope": {"kind": "unconditional"}, "status": "planned", "reason": "upstream validation errors: ['records[3].temporal_order.basis[0] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "f3cc1940ce20fb3f9475820bf1e08c35a8631b5758fe3207484d46c9cda2914f", "verdict": "supported", "reason": "目标是计划；语义授权未给且时间依据不属于关联引文，暂缓符合接口，不能当已找到工作。"}
  - 输出：{"unit_id": "friendship", "fact": "friend named ThomasSusan", "relation": "same", "subject": "ThomasSusan", "attribute": "name", "old_value": "ThomasSusan", "new_value": "Susan", "old_quotes": [{"side": "old", "unit_id": "friendship", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "friend named ThomasSusan", "position": {"start": 6, "end": 30}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "friend named ThomasSusan", "old_position": {"start": 6, "end": 30}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].semantic_basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "friend named ThomasSusan"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable."}], "explanation": "Both refer to current, ongoing friendship; no temporal shift indicated in either quote"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}, {"side": "old", "source_id": "ctx-1", "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[0].semantic_basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "7237caa7348ce7fb3dda03768cea258ef5abffed8d2057ecaeb495583e6547b6", "verdict": "supported", "reason": "friendship 语义依据引入未绑定 ctx-1，并且 same 与姓名映射缺充分关联证据；暂缓适当。"}
  - 输出：{"unit_id": "support", "fact": "provides support and encouragement", "relation": "supplement", "subject": "Susan", "attribute": "provides support and encouragement", "old_value": "provides support and encouragement", "new_value": "has indeed been invaluable... helps me stay focused on my goals", "old_quotes": [{"side": "old", "unit_id": "support", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement", "position": {"start": 60, "end": 94}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "position": {"start": 0, "end": 96}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "provides support and encouragement", "old_position": {"start": 60, "end": 94}, "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.", "new_position": {"start": 0, "end": 96}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content", "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "old", "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}, {"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "explanation": "Both describe current, ongoing supportive function; no indication of change in timing or duration"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."}], "scope": {"kind": "unconditional"}, "reason": "impact of new information on old fact is not established"}；独立审核：{"sha256": "f101fbbc47cc8bcd2528262649be99494325bd818612e3f8454d89f37fea8504", "verdict": "supported", "reason": "支持补充本身并不证明对旧事实影响；暂缓该影响符合契约，同时应保留原文，不应解释成支持消失。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

事后规划器引用检查：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "friendship",
    "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "quote": "friend named ThomasSusan",
    "position": {
      "start": 6,
      "end": 30
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-2",
    "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "position": {
      "start": 0,
      "end": 96
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "support",
    "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "quote": "provides support and encouragement",
    "position": {
      "start": 60,
      "end": 94
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-2",
    "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "position": {
      "start": 0,
      "end": 96
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-0",
    "source_id": "new-0",
    "quote": "my current role isn't supporting my well-being as much as I'd like",
    "position": {
      "start": 72,
      "end": 138
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 3,
    "side": "new",
    "unit_id": "unsplit-new-0",
    "source_id": "new-0",
    "quote": "It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
    "position": {
      "start": 140,
      "end": 255
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**与原文和人工预期的差异：** 结构四字段组中 schema、引文、覆盖通过，basis 因 #0 使用未绑定 ctx-1、#3 时间引文含省略号且未绑定而失败；6 条主引文都唯一匹配。预期保留 Susan 的朋友支持、独立新增 Daniel 的见解和求职计划；直接规划均待确认，未产生编辑/新增，属于对模型语义未知的保守结果而非事实不存在。模型对两条时间 same 与 unconditional 推断不足，Daniel 语义未独立输出，单元覆盖不能证明事实覆盖。

## promotion

**请求与来源**

```json
{
  "call": {
    "status": "passed",
    "attempts": 1,
    "request_transmitted": true,
    "elapsed_seconds": 20.28,
    "returned_model": "qwen-plus-2025-12-01",
    "finish_reason": "stop"
  },
  "usage": {
    "completion_tokens": 875,
    "prompt_tokens": 12538,
    "total_tokens": 13413,
    "completion_tokens_details": null,
    "prompt_tokens_details": null
  }
}
```

旧记忆：{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "text": "Works at Historical Productions Ltd. as a Director", "speaker": "memory", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json"}

输入所选新单元：[{"unit_id": "manually_mapped_new", "source_id": "new-0", "memory_quotes": ["I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"]}]

所选新证据及来源：[{"source_id": "new-0", "side": "new", "speaker": "user", "text": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "recorded_at": "Feb 01, 2026, 18:47:19", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"}]

原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：[{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "status": "verified", "reason": null}, {"source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "status": "verified", "reason": null}]

独立人工预期：{"case_id": "promotion", "provenance": "人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。", "modify": ["职位细化为晋升后的 lead director"], "preserve": ["Historical Productions Ltd. 雇主关系；Director 作为历史和可能仍成立的宽泛描述"], "uncertain": ["准确晋升日期未知；宽泛 Director 与 lead director 的逻辑包含关系不由代码推理"], "add": ["晋升 lead director 的事实"], "missing": ["记录时间不是生效时间。"]}

**接口和逐引文校验**（引用定位不等于语义支持）

```json
{
  "status": "passed",
  "errors": [],
  "schema_status": "passed",
  "quote_status": "passed",
  "basis_status": "passed",
  "coverage_status": "passed",
  "schema_errors": [],
  "quote_errors": [],
  "basis_errors": [],
  "coverage_errors": [],
  "record_errors": [
    [],
    []
  ],
  "quote_checks": [
    {
      "record_index": 0,
      "side": "old",
      "index": 0,
      "unit_id": "employer",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Historical Productions Ltd.",
      "status": "valid",
      "position": {
        "start": 9,
        "end": 36
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 92
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "old",
      "index": 0,
      "unit_id": "title",
      "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "quote": "Director",
      "status": "valid",
      "position": {
        "start": 42,
        "end": 50
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 92
      },
      "reason": null
    }
  ],
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**模型记录 0**

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
独立语义审核：{"sha256": "9c51846f5da1d00717f68c7a05260b85c51761d1ece351deb987343b209fdbe2", "verdict": "partially_supported", "reason": "引文确实显示同一公司出现在旧文和晋升句；但 employer 的主体误写公司本身而非 user，单凭未提变化不足以证明旧新状态同时或 unconditional。"}

**模型记录 1**

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
独立语义审核：{"sha256": "f6852da7cee031c64fa2bfeff627426e57e03a8edd9b9adf046021d6e4182ac9", "verdict": "partially_supported", "reason": "旧文 Director 与新话语 lead director 的晋升均有来源；recently 只相对说话时间，不能证明该晋升晚于旧记忆事实有效期，更不能自动否定 Director 作为宽泛称谓。"}

**未经独立审核补全的模型直接规划结果**

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - 输出：{"unit_id": "employer", "fact": "Historical Productions Ltd.", "relation": "same", "subject": "Historical Productions Ltd.", "attribute": "employer", "old_value": "Historical Productions Ltd.", "new_value": "Historical Productions Ltd.", "old_quotes": [{"side": "old", "unit_id": "employer", "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Historical Productions Ltd.", "position": {"start": 9, "end": 36}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "position": {"start": 0, "end": 92}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Historical Productions Ltd.", "old_position": {"start": 9, "end": 36}, "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "new_position": {"start": 0, "end": 92}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}], "explanation": "The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "4368518c3747f9a719c762303c31eb32d57831f90a5e995ee9b1d0eeacdfa97c", "verdict": "supported", "reason": "模型将公司当主体且缺独立语义支持，适配后暂缓旧项保留符合 v2 安全契约；人工可据原文进一步判断同雇主。"}
  - 输出：{"unit_id": "title", "fact": "Director", "relation": "change", "subject": "user", "attribute": "title", "old_value": "Director", "new_value": "lead director", "old_quotes": [{"side": "old", "unit_id": "title", "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Director", "position": {"start": 42, "end": 50}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "position": {"start": 0, "end": 92}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Director", "old_position": {"start": 42, "end": 50}, "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "new_position": {"start": 0, "end": 92}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted"}], "explanation": "'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director')."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director"}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "286f996abfb7ed3033025f97f9ea6cbe5d4874a8d4042bb586aa82bf86b50469", "verdict": "supported", "reason": "模型 after 缺相对旧状态先后证明，semantic_support 亦 unknown；即使无精确日期不是自动失败，当前情况暂缓编辑是合理的。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

规划器引文位置和原因：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "employer",
    "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "quote": "Historical Productions Ltd.",
    "position": {
      "start": 9,
      "end": 36
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "position": {
      "start": 0,
      "end": 92
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "title",
    "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "quote": "Director",
    "position": {
      "start": 42,
      "end": 50
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "position": {
      "start": 0,
      "end": 92
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）

状态与散列：{"status": "completed_offline", "provenance": {"artifact_sha256": "4e63e45886bd534b66638ee61972c82152de4cc666fd7c4b4f8489d0973eff19", "adapter_sha256": "d6c1a3f08c6a77d8908007422a68d710fa5d1ca9941f82ef277afbaff6077b8e", "planner_sha256": "3c46dc51936a19d0b52dcaf08f4f5b1edb2ed8e41ad403fd0c9b4dbdf49042a1", "raw_response_sha256": "ba7e8d734a6948604e266e5f7dc80fae09e9344b52268739310b924622797fbd"}}

- modify（0）：
- preserve（0）：
- uncertain（2）：
  - 输出：{"unit_id": "employer", "fact": "Historical Productions Ltd.", "relation": "same", "subject": "Historical Productions Ltd.", "attribute": "employer", "old_value": "Historical Productions Ltd.", "new_value": "Historical Productions Ltd.", "old_quotes": [{"side": "old", "unit_id": "employer", "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Historical Productions Ltd.", "position": {"start": 9, "end": 36}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "position": {"start": 0, "end": 92}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Historical Productions Ltd.", "old_position": {"start": 9, "end": 36}, "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "new_position": {"start": 0, "end": 92}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}], "explanation": "The phrase 'at Historical Productions Ltd.' affirms ongoing employment with the same employer; no temporal shift in employer identity is indicated."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "4368518c3747f9a719c762303c31eb32d57831f90a5e995ee9b1d0eeacdfa97c", "verdict": "supported", "reason": "模型将公司当主体且缺独立语义支持，适配后暂缓旧项保留符合 v2 安全契约；人工可据原文进一步判断同雇主。"}
  - 输出：{"unit_id": "title", "fact": "Director", "relation": "change", "subject": "user", "attribute": "title", "old_value": "Director", "new_value": "lead director", "old_quotes": [{"side": "old", "unit_id": "title", "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Director", "position": {"start": 42, "end": 50}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "position": {"start": 0, "end": 92}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Director", "old_position": {"start": 42, "end": 50}, "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!", "new_position": {"start": 0, "end": 92}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content", "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted"}], "explanation": "'Recently got promoted' indicates the new title ('lead director') came into effect after the prior title ('Director')."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I recently got promoted to lead director"}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "286f996abfb7ed3033025f97f9ea6cbe5d4874a8d4042bb586aa82bf86b50469", "verdict": "supported", "reason": "模型 after 缺相对旧状态先后证明，semantic_support 亦 unknown；即使无精确日期不是自动失败，当前情况暂缓编辑是合理的。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

事后规划器引用检查：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "employer",
    "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "quote": "Historical Productions Ltd.",
    "position": {
      "start": 9,
      "end": 36
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "position": {
      "start": 0,
      "end": 92
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "title",
    "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "quote": "Director",
    "position": {
      "start": 42,
      "end": 50
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "position": {
      "start": 0,
      "end": 92
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**与原文和人工预期的差异：** schema、引用、依据绑定和覆盖均通过，4 条主引文唯一定位，但结构通过并未证明语义。预期保留同雇主与历史职位并表达晋升；直接规划两条待确认且无编辑/新增，较预期保守。晋升已发生与晋升是否晚于旧事实、旧宽泛称谓是否不再成立需要分别判断。

## career_history

**请求与来源**

```json
{
  "call": {
    "status": "failed",
    "attempts": 1,
    "request_transmitted": true,
    "elapsed_seconds": 29.835,
    "returned_model": "qwen-plus-2025-12-01",
    "finish_reason": "stop"
  },
  "usage": {
    "completion_tokens": 1306,
    "prompt_tokens": 13576,
    "total_tokens": 14882,
    "completion_tokens_details": null,
    "prompt_tokens_details": null
  }
}
```

旧记忆：{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "text": "Previously worked as a senior developer in Blockchain Tech", "speaker": "memory", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json"}

输入所选新单元：[{"unit_id": "manually_mapped_new", "source_id": "new-0", "memory_quotes": ["I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."]}, {"unit_id": "unsplit-new-2", "source_id": "new-2", "memory_quotes": ["MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."]}]

所选新证据及来源：[{"source_id": "new-0", "side": "new", "speaker": "user", "text": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.", "recorded_at": "Jan 05, 2026, 07:43:42", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"}, {"source_id": "new-2", "side": "new", "speaker": "user", "text": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.", "recorded_at": "Jan 05, 2026, 07:44:55", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content"}]

原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：[{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "status": "verified", "reason": null}, {"source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "status": "verified", "reason": null}, {"source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content", "status": "verified", "reason": null}]

独立人工预期：{"case_id": "career_history", "provenance": "人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。", "modify": [], "preserve": ["曾在 Blockchain Tech 任 senior developer 的历史"], "uncertain": ["具体离职或转型时间、当前雇佣关系及公司所有权细节"], "add": ["咨询公司获得初始客户"], "missing": ["本会话没有给出具体离职日期或直接否定历史。"]}

**接口和逐引文校验**（引用定位不等于语义支持）

```json
{
  "status": "failed",
  "errors": [
    "records[0].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[0].temporal_order.basis[1] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[1] not bound to cited same-side source/quote",
    "records[2].new_value must be nonempty text or null (unknown)"
  ],
  "schema_status": "failed",
  "quote_status": "passed",
  "basis_status": "failed",
  "coverage_status": "passed",
  "schema_errors": [
    "records[2].new_value must be nonempty text or null (unknown)"
  ],
  "quote_errors": [],
  "basis_errors": [
    "records[0].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[0].temporal_order.basis[1] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[1] not bound to cited same-side source/quote"
  ],
  "coverage_errors": [],
  "record_errors": [
    [
      "records[0].temporal_order.basis[0] not bound to cited same-side source/quote",
      "records[0].temporal_order.basis[1] not bound to cited same-side source/quote"
    ],
    [
      "records[1].temporal_order.basis[0] not bound to cited same-side source/quote",
      "records[1].temporal_order.basis[1] not bound to cited same-side source/quote"
    ],
    [
      "records[2].new_value must be nonempty text or null (unknown)"
    ]
  ],
  "quote_checks": [
    {
      "record_index": 0,
      "side": "old",
      "index": 0,
      "unit_id": "employer",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "Blockchain Tech",
      "status": "valid",
      "position": {
        "start": 43,
        "end": 58
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients",
      "status": "valid",
      "position": {
        "start": 48,
        "end": 103
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "old",
      "index": 0,
      "unit_id": "title",
      "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "quote": "senior developer",
      "status": "valid",
      "position": {
        "start": 23,
        "end": 39
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "my consulting firm finally secured some initial clients",
      "status": "valid",
      "position": {
        "start": 48,
        "end": 103
      },
      "reason": null
    },
    {
      "record_index": 2,
      "side": "new",
      "index": 0,
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 111
      },
      "reason": null
    }
  ],
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**模型记录 0**

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
独立语义审核：{"sha256": "c22408c0b7c5e39f3e533e75c8e11a91aaf6f0c45c04a9f85a34b5e421ee6435", "verdict": "unsupported", "reason": "新句只说咨询公司获初始客户；不能由此推断本人所有权、正在经营、旧雇佣已结束或互不兼容，也不能由 lately/finally 判其晚于旧事实。旧整句及新前缀被用作时间依据但不在关联短引文内。"}

**模型记录 1**

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
独立语义审核：{"sha256": "d9b507b62151f84138dca6b06cb509a3e7089ba018f1b4349a7d9faf8970c313", "verdict": "unsupported", "reason": "新句未给出本人咨询公司的 founder/operator 职位，不能由 my firm 推断创办者或经营者，更不能得出前职位被替代；时间依据也超出已引用片段。"}

**模型记录 2**

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
独立语义审核：{"sha256": "1890f71a3388be7cb93f80164a524fdb6e2b9c07935322beb775d187c08e2f79", "verdict": "partially_supported", "reason": "两位联系人和其联系开门得到用户原句支持，但 new_value 输出数组不符合字符串/null 结构，且 unconditional 未给出完整依据。"}

**未经独立审核补全的模型直接规划结果**

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "I", "attribute": "network contacts", "old_value": null, "new_value": null, "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-2", "source_id": "new-2", "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.", "position": {"start": 0, "end": 111}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.", "new_position": {"start": 0, "end": 111}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].new_value must be nonempty text or null (unknown)"], "unknowns": [], "temporal_order": {"relation": "unknown", "basis": [], "explanation": null}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."}], "value": null, "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']"}；独立审核：{"sha256": "0d05606577f9661b1e45bdcb52865969e4c25ba2b6da3219a372863698ab4440", "verdict": "supported", "reason": "联系人可作独立信息，但值类型错误且无独立语义授权，规划器暂缓而不添加符合契约。"}
  - 输出：{"unit_id": "employer", "fact": "Blockchain Tech", "relation": "change", "subject": "I", "attribute": "employer", "old_value": "Blockchain Tech", "new_value": "consulting firm", "old_quotes": [{"side": "old", "unit_id": "employer", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Blockchain Tech", "position": {"start": 43, "end": 58}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients", "position": {"start": 48, "end": 103}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Blockchain Tech", "old_position": {"start": 43, "end": 58}, "new_quote": "my consulting firm finally secured some initial clients", "new_position": {"start": 48, "end": 103}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].temporal_order.basis[0] not bound to cited same-side source/quote", "records[0].temporal_order.basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Previously worked as a senior developer in Blockchain Tech"}, {"side": "new", "source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"}], "explanation": "The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "25fd19268f098e42f96159610ad92cebdd68f99af4e2cf0e2160808891a73cbb", "verdict": "supported", "reason": "新旧雇主变化与时间均无证据，basis 超出引文；暂缓正确，并应保留过去 Blockchain Tech 历史。"}
  - 输出：{"unit_id": "title", "fact": "senior developer", "relation": "change", "subject": "I", "attribute": "job title", "old_value": "senior developer", "new_value": "founder / operator of consulting firm", "old_quotes": [{"side": "old", "unit_id": "title", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "senior developer", "position": {"start": 23, "end": 39}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients", "position": {"start": 48, "end": 103}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "senior developer", "old_position": {"start": 23, "end": 39}, "new_quote": "my consulting firm finally secured some initial clients", "new_position": {"start": 48, "end": 103}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[1].temporal_order.basis[0] not bound to cited same-side source/quote", "records[1].temporal_order.basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Previously worked as a senior developer in Blockchain Tech"}, {"side": "new", "source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"}], "explanation": "Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "9247313cdd69c5233657181e0f651a1bc59aff25a1694272ea53801adee3a93f", "verdict": "supported", "reason": "founder/operator 为无证推断，时间依据也不受引用约束；暂缓正确，不能删除 senior developer 历史。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

规划器引文位置和原因：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "employer",
    "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "quote": "Blockchain Tech",
    "position": {
      "start": 43,
      "end": 58
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "my consulting firm finally secured some initial clients",
    "position": {
      "start": 48,
      "end": 103
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "title",
    "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "quote": "senior developer",
    "position": {
      "start": 23,
      "end": 39
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "my consulting firm finally secured some initial clients",
    "position": {
      "start": 48,
      "end": 103
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-2",
    "source_id": "new-2",
    "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.",
    "position": {
      "start": 0,
      "end": 111
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  }
]
```

**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）

状态与散列：{"status": "completed_offline", "provenance": {"artifact_sha256": "ee17f04abbcd6fb39e151b907085007d8c2fd15cfb5c592e357515eb37a3830b", "adapter_sha256": "d6c1a3f08c6a77d8908007422a68d710fa5d1ca9941f82ef277afbaff6077b8e", "planner_sha256": "3c46dc51936a19d0b52dcaf08f4f5b1edb2ed8e41ad403fd0c9b4dbdf49042a1", "raw_response_sha256": "06329d2f66450d62fc3e12711b7c965bf8b7029266f327f0e22a8d29abc21b75"}}

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - 输出：{"unit_id": null, "fact": null, "relation": "new_information", "subject": "I", "attribute": "network contacts", "old_value": null, "new_value": null, "old_quotes": [], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-2", "source_id": "new-2", "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.", "position": {"start": 0, "end": 111}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": null, "old_position": null, "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.", "new_position": {"start": 0, "end": 111}, "source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content", "memory_id": null, "old_source_ref": null, "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].new_value must be nonempty text or null (unknown)"], "unknowns": [], "temporal_order": {"relation": "unknown", "basis": [], "explanation": null}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-2", "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined."}], "value": null, "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "upstream validation errors: ['records[2].new_value must be nonempty text or null (unknown)']"}；独立审核：{"sha256": "0d05606577f9661b1e45bdcb52865969e4c25ba2b6da3219a372863698ab4440", "verdict": "supported", "reason": "联系人可作独立信息，但值类型错误且无独立语义授权，规划器暂缓而不添加符合契约。"}
  - 输出：{"unit_id": "employer", "fact": "Blockchain Tech", "relation": "change", "subject": "I", "attribute": "employer", "old_value": "Blockchain Tech", "new_value": "consulting firm", "old_quotes": [{"side": "old", "unit_id": "employer", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Blockchain Tech", "position": {"start": 43, "end": 58}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients", "position": {"start": 48, "end": 103}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Blockchain Tech", "old_position": {"start": 43, "end": 58}, "new_quote": "my consulting firm finally secured some initial clients", "new_position": {"start": 48, "end": 103}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].temporal_order.basis[0] not bound to cited same-side source/quote", "records[0].temporal_order.basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Previously worked as a senior developer in Blockchain Tech"}, {"side": "new", "source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"}], "explanation": "The phrase 'finally secured' and 'lately' indicate the consulting firm is newly operational, post-dating prior employment at Blockchain Tech; 'Previously worked' confirms temporal precedence of old role."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[0].temporal_order.basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "25fd19268f098e42f96159610ad92cebdd68f99af4e2cf0e2160808891a73cbb", "verdict": "supported", "reason": "新旧雇主变化与时间均无证据，basis 超出引文；暂缓正确，并应保留过去 Blockchain Tech 历史。"}
  - 输出：{"unit_id": "title", "fact": "senior developer", "relation": "change", "subject": "I", "attribute": "job title", "old_value": "senior developer", "new_value": "founder / operator of consulting firm", "old_quotes": [{"side": "old", "unit_id": "title", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "senior developer", "position": {"start": 23, "end": 39}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients", "position": {"start": 48, "end": 103}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "senior developer", "old_position": {"start": 23, "end": 39}, "new_quote": "my consulting firm finally secured some initial clients", "new_position": {"start": 48, "end": 103}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content", "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[1].temporal_order.basis[0] not bound to cited same-side source/quote", "records[1].temporal_order.basis[1] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Previously worked as a senior developer in Blockchain Tech"}, {"side": "new", "source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients"}], "explanation": "Same basis as above: 'Previously worked' anchors old title in past; 'my consulting firm' and 'finally secured' confirm new role is current and distinct."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'records[1].temporal_order.basis[1] not bound to cited same-side source/quote']"}；独立审核：{"sha256": "9247313cdd69c5233657181e0f651a1bc59aff25a1694272ea53801adee3a93f", "verdict": "supported", "reason": "founder/operator 为无证推断，时间依据也不受引用约束；暂缓正确，不能删除 senior developer 历史。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

事后规划器引用检查：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "employer",
    "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "quote": "Blockchain Tech",
    "position": {
      "start": 43,
      "end": 58
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "my consulting firm finally secured some initial clients",
    "position": {
      "start": 48,
      "end": 103
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "title",
    "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "quote": "senior developer",
    "position": {
      "start": 23,
      "end": 39
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "my consulting firm finally secured some initial clients",
    "position": {
      "start": 48,
      "end": 103
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-2",
    "source_id": "new-2",
    "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.",
    "position": {
      "start": 0,
      "end": 111
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  }
]
```

**与原文和人工预期的差异：** schema 失败于联系人 new_value 数组，basis 因前两条时序依据不落在其引用内而失败；5 条主引文来源唯一、覆盖通过。原模型把咨询公司获客扩展为离职、经营/创办并判 change，证据不支持；现有人工预期保留旧历史并新增获客，模型没有独立输出获客记录，直接计划保守无新增或修改，不能误认为历史已核实保留。

## transition

**请求与来源**

```json
{
  "call": {
    "status": "passed",
    "attempts": 1,
    "request_transmitted": true,
    "elapsed_seconds": 22.896,
    "returned_model": "qwen-plus-2025-12-01",
    "finish_reason": "stop"
  },
  "usage": {
    "completion_tokens": 997,
    "prompt_tokens": 12095,
    "total_tokens": 13092,
    "completion_tokens_details": null,
    "prompt_tokens_details": null
  }
}
```

旧记忆：{"source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "text": "Looking for a new job with better work-life balance", "speaker": "memory", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json"}

输入所选新单元：[{"unit_id": "manually_mapped_new", "source_id": "new-0", "memory_quotes": ["I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."]}]

所选新证据及来源：[{"source_id": "new-0", "side": "new", "speaker": "user", "text": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.", "recorded_at": "Mar 01, 2026, 07:04:00", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"}]

原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：[{"source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "verified", "reason": null}, {"source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "verified", "reason": null}]

独立人工预期：{"case_id": "transition", "provenance": "人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。", "modify": ["求职进展改为已经转到新职位，不断言停止任何求职"], "preserve": ["追求较好工作生活平衡的旧目标"], "uncertain": ["新职位名称和实际切换日期；是否继续另找工作"], "add": ["新职位工作生活平衡改善"], "missing": ["没有具体职位名或事实生效日期。"]}

**接口和逐引文校验**（引用定位不等于语义支持）

```json
{
  "status": "passed",
  "errors": [],
  "schema_status": "passed",
  "quote_status": "passed",
  "basis_status": "passed",
  "coverage_status": "passed",
  "schema_errors": [],
  "quote_errors": [],
  "basis_errors": [],
  "coverage_errors": [],
  "record_errors": [
    [],
    []
  ],
  "quote_checks": [
    {
      "record_index": 0,
      "side": "old",
      "index": 0,
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 51
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 135
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "old",
      "index": 0,
      "unit_id": "job_search",
      "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "quote": "Looking for a new job with better work-life balance",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 51
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "The balance between work and personal life is much healthier now.",
      "status": "valid",
      "position": {
        "start": 70,
        "end": 135
      },
      "reason": null
    }
  ],
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**模型记录 0**

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
独立语义审核：{"sha256": "5187a431953f4f9b9ffd8720136b22ab5e14df3d5756e9de20826512e4b2a998", "verdict": "partially_supported", "reason": "已转岗和平衡改善有新引文；finally 不单独证明切换晚于旧记忆有效期，也不证明停止找工作，且 unconditional 和完整替换旧求职状态缺依据。"}

**模型记录 1**

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
独立语义审核：{"sha256": "77ba3f9295a72a8885abf8fb309b2eeafcc1b7f54331d29170f710450ee9d1aa", "verdict": "partially_supported", "reason": "新话语确实称现在平衡更健康；是否完全实现此前目标、此前和现在动机同一时间及 unconditional 未证明。"}

**未经独立审核补全的模型直接规划结果**

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "supplement", "subject": "I", "attribute": "motivation for job search", "old_value": "better work-life balance", "new_value": "better work-life balance (now realized as healthier balance)", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now.", "position": {"start": 70, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "The balance between work and personal life is much healthier now.", "new_position": {"start": 70, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "explanation": "The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "value": "better work-life balance (now realized as healthier balance)", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "7346beae6f15c8d643c8f0533f8766e7b0fe190b081132e0b53831ca9ba24a86", "verdict": "supported", "reason": "平衡改善有新证据，但未经独立语义授权，暂缓此补充符合 v2 契约。"}
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "change", "subject": "I", "attribute": "job search status", "old_value": "looking for a new job with better work-life balance", "new_value": "transitioned to a new role with healthier work-life balance", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.", "position": {"start": 0, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.", "new_position": {"start": 0, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance"}, {"side": "new", "source_id": "new-0", "quote": "I've finally transitioned to a new role"}], "explanation": "'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "5e09e309ac1215e387d53f8cc9ec7cefcf1b833bc309a4e734e9701f140f0eb4", "verdict": "supported", "reason": "是否继续求职、相对旧事实先后均未明，暂缓覆盖旧状态符合要求。"}
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "supplement", "subject": "I", "attribute": "motivation for job search", "old_value": "better work-life balance", "new_value": "better work-life balance (now realized as healthier balance)", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now.", "position": {"start": 70, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "The balance between work and personal life is much healthier now.", "new_position": {"start": 70, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "explanation": "The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "scope": {"kind": "unconditional"}, "reason": "impact of new information on old fact is not established"}；独立审核：{"sha256": "ba8b3ed9785e3b7c23a6c676e619fdb0026c4c90fa9dea2eb2c87462e6540b4b", "verdict": "supported", "reason": "平衡改善不自动证明原求职目标消失或目标完全实现，对旧事实影响待确认适当。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

规划器引文位置和原因：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "job_search",
    "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "quote": "Looking for a new job with better work-life balance",
    "position": {
      "start": 0,
      "end": 51
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
    "position": {
      "start": 0,
      "end": 135
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "job_search",
    "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "quote": "Looking for a new job with better work-life balance",
    "position": {
      "start": 0,
      "end": 51
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "The balance between work and personal life is much healthier now.",
    "position": {
      "start": 70,
      "end": 135
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）

状态与散列：{"status": "completed_offline", "provenance": {"artifact_sha256": "c6f872cd0576508c836fed057e9838e4baa55007d8cf7bb1225010933ce87d78", "adapter_sha256": "d6c1a3f08c6a77d8908007422a68d710fa5d1ca9941f82ef277afbaff6077b8e", "planner_sha256": "3c46dc51936a19d0b52dcaf08f4f5b1edb2ed8e41ad403fd0c9b4dbdf49042a1", "raw_response_sha256": "cde9b74d0b53618e501b17f1aa53663553beafb5b2db3046d65c9f3a61d15420"}}

- modify（0）：
- preserve（0）：
- uncertain（3）：
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "supplement", "subject": "I", "attribute": "motivation for job search", "old_value": "better work-life balance", "new_value": "better work-life balance (now realized as healthier balance)", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now.", "position": {"start": 70, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "The balance between work and personal life is much healthier now.", "new_position": {"start": 70, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "explanation": "The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "value": "better work-life balance (now realized as healthier balance)", "scope": {"kind": "unconditional"}, "status": "asserted", "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "7346beae6f15c8d643c8f0533f8766e7b0fe190b081132e0b53831ca9ba24a86", "verdict": "supported", "reason": "平衡改善有新证据，但未经独立语义授权，暂缓此补充符合 v2 契约。"}
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "change", "subject": "I", "attribute": "job search status", "old_value": "looking for a new job with better work-life balance", "new_value": "transitioned to a new role with healthier work-life balance", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.", "position": {"start": 0, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.", "new_position": {"start": 0, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance"}, {"side": "new", "source_id": "new-0", "quote": "I've finally transitioned to a new role"}], "explanation": "'Finally' signals completion of prior search; 'transitioned' is past-tense achievement, contrasting ongoing 'looking for'"}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}], "scope": {"kind": "unconditional"}, "reason": "semantic support or bound basis missing"}；独立审核：{"sha256": "5e09e309ac1215e387d53f8cc9ec7cefcf1b833bc309a4e734e9701f140f0eb4", "verdict": "supported", "reason": "是否继续求职、相对旧事实先后均未明，暂缓覆盖旧状态符合要求。"}
  - 输出：{"unit_id": "job_search", "fact": "Looking for a new job with better work-life balance", "relation": "supplement", "subject": "I", "attribute": "motivation for job search", "old_value": "better work-life balance", "new_value": "better work-life balance (now realized as healthier balance)", "old_quotes": [{"side": "old", "unit_id": "job_search", "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance", "position": {"start": 0, "end": 51}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now.", "position": {"start": 70, "end": 135}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}], "old_quote": "Looking for a new job with better work-life balance", "old_position": {"start": 0, "end": 51}, "new_quote": "The balance between work and personal life is much healthier now.", "new_position": {"start": 70, "end": 135}, "source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content", "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": [], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "explanation": "The new statement affirms the *fulfillment* of the previously stated motivation, not a temporal shift in the motivation itself."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "The balance between work and personal life is much healthier now."}], "scope": {"kind": "unconditional"}, "reason": "impact of new information on old fact is not established"}；独立审核：{"sha256": "ba8b3ed9785e3b7c23a6c676e619fdb0026c4c90fa9dea2eb2c87462e6540b4b", "verdict": "supported", "reason": "平衡改善不自动证明原求职目标消失或目标完全实现，对旧事实影响待确认适当。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

事后规划器引用检查：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "job_search",
    "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "quote": "Looking for a new job with better work-life balance",
    "position": {
      "start": 0,
      "end": 51
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
    "position": {
      "start": 0,
      "end": 135
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "job_search",
    "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "quote": "Looking for a new job with better work-life balance",
    "position": {
      "start": 0,
      "end": 51
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "The balance between work and personal life is much healthier now.",
    "position": {
      "start": 70,
      "end": 135
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  }
]
```

**与原文和人工预期的差异：** schema、主引文、basis 绑定和覆盖都通过，4 条主引文唯一命中；但结构通过不证明语义先后。人工预期保护旧平衡目标、表达已转岗及平衡改善；模型直接计划没有编辑、保留或新增，只列待确认。模型根据 finally 认定结束求职和时间 after 超出了证据；没有具体日期并不是拒绝的直接原因。

## skydiving

**请求与来源**

```json
{
  "call": {
    "status": "failed",
    "attempts": 1,
    "request_transmitted": true,
    "elapsed_seconds": 40.424,
    "returned_model": "qwen-plus-2025-12-01",
    "finish_reason": "stop"
  },
  "usage": {
    "completion_tokens": 1799,
    "prompt_tokens": 8235,
    "total_tokens": 10034,
    "completion_tokens_details": null,
    "prompt_tokens_details": null
  }
}
```

旧记忆：{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "text": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being", "speaker": "memory", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json"}

输入所选新单元：[{"unit_id": "manually_mapped_new", "source_id": "new-0", "memory_quotes": ["Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"]}, {"unit_id": "unsplit-new-2", "source_id": "new-2", "memory_quotes": ["Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."]}, {"unit_id": "unsplit-new-8", "source_id": "new-8", "memory_quotes": ["For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."]}]

所选新证据及来源：[{"source_id": "new-0", "side": "new", "speaker": "user", "text": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "recorded_at": "Apr 10, 2026, 10:40:32", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content"}, {"source_id": "new-2", "side": "new", "speaker": "user", "text": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.", "recorded_at": "Apr 10, 2026, 10:48:20", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content"}, {"source_id": "new-8", "side": "new", "speaker": "user", "text": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "recorded_at": "Apr 10, 2026, 10:57:54", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content"}]

原始本地文件与来源指针核验（不替代引文唯一和关联单元检查）：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "verified", "reason": null}, {"source_id": "new-0", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content", "status": "verified", "reason": null}, {"source_id": "new-2", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content", "status": "verified", "reason": null}, {"source_id": "new-8", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "verified", "reason": null}]

独立人工预期：{"case_id": "skydiving", "provenance": "人工依据原文独立整理的预期，不输入规划器；非用户确认金标准。", "modify": [], "preserve": ["旧极限运动顾虑、受伤风险和安全福祉取向；不要推广为所有偏好已改变"], "uncertain": ["模拟跳伞与旧极限运动的覆盖关系、当前真实跳伞偏好；u3 短引文本身不完整"], "add": ["尝试模拟跳伞且感觉刺激；仍重视安全"], "missing": ["没有确定的事实有效日期；模拟体验不证明真实跳伞偏好变化。"]}

**接口和逐引文校验**（引用定位不等于语义支持）

```json
{
  "status": "failed",
  "errors": [
    "records[0].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[2].old_conditions cannot use same_as_old"
  ],
  "schema_status": "failed",
  "quote_status": "passed",
  "basis_status": "failed",
  "coverage_status": "passed",
  "schema_errors": [
    "records[2].old_conditions cannot use same_as_old"
  ],
  "quote_errors": [],
  "basis_errors": [
    "records[0].temporal_order.basis[0] not bound to cited same-side source/quote",
    "records[1].temporal_order.basis[0] not bound to cited same-side source/quote"
  ],
  "coverage_errors": [],
  "record_errors": [
    [
      "records[0].temporal_order.basis[0] not bound to cited same-side source/quote"
    ],
    [
      "records[1].temporal_order.basis[0] not bound to cited same-side source/quote"
    ],
    [
      "records[2].old_conditions cannot use same_as_old"
    ]
  ],
  "quote_checks": [
    {
      "record_index": 0,
      "side": "old",
      "index": 0,
      "unit_id": "u1",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving)",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 41
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 129
      },
      "reason": null
    },
    {
      "record_index": 0,
      "side": "new",
      "index": 1,
      "unit_id": "unsplit-new-2",
      "source_id": "new-2",
      "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 129
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "old",
      "index": 0,
      "unit_id": "u2",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 65
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 0,
      "unit_id": "manually_mapped_new",
      "source_id": "new-0",
      "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 129
      },
      "reason": null
    },
    {
      "record_index": 1,
      "side": "new",
      "index": 1,
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 105
      },
      "reason": null
    },
    {
      "record_index": 2,
      "side": "old",
      "index": 0,
      "unit_id": "u3",
      "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "quote": "conflicting with commitment to safety and well-being",
      "status": "valid",
      "position": {
        "start": 67,
        "end": 119
      },
      "reason": null
    },
    {
      "record_index": 2,
      "side": "new",
      "index": 0,
      "unit_id": "unsplit-new-8",
      "source_id": "new-8",
      "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "status": "valid",
      "position": {
        "start": 0,
        "end": 105
      },
      "reason": null
    }
  ],
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**模型记录 0**

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
独立语义审核：{"sha256": "0302e545080f924a0045fc8ed630380f9f393747f62b0e5a89bcfd58fbf2150d", "verdict": "unsupported", "reason": "新引文支持模拟跳伞刺激及更愿尝新，不证明真实极限运动或旧偏好改变；模型自身声称与旧厌恶矛盾并把模拟/团建写成同一维度的两个互斥枚举而不是组合，同时用 ctx-1 未关联时间依据及发言日期推 after。"}

**模型记录 1**

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
独立语义审核：{"sha256": "3e3b236f11100b1bb2716306a70b3df8c766e70ae43648587d320c55175c6c36", "verdict": "unsupported", "reason": "新句没有撤回高受伤风险是旧厌恶理由；模型将未再提及当变化，模拟亦不能证明低风险，更不能据对话日期推事实时序；旧 ctx-1 不在已关联旧引文内。"}

**模型记录 2**

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
独立语义审核：{"sha256": "a24a702bb40ef825a9c90f3d84afb54d872dff5a9f602bdecac678f14a8a109c", "verdict": "partially_supported", "reason": "新话语支持现在重视安全，但不证明旧极限运动与安全福祉的整条冲突因果继续成立，亦未证明只接受模拟；old_conditions 使用 same_as_old 违反结构约定。"}

**未经独立审核补全的模型直接规划结果**

- modify（0）：
- preserve（2）：
  - 输出：{"unit_id": "u1", "fact": "Dislikes extreme sports (e.g., skydiving)", "relation": "change", "subject": "I", "attribute": "attitude toward extreme sports (e.g., skydiving)", "old_value": "dislikes", "new_value": "found simulated skydiving thrilling; more open to trying new things", "old_quotes": [{"side": "old", "unit_id": "u1", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving)", "position": {"start": 0, "end": 41}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}, {"side": "new", "unit_id": "unsplit-new-2", "source_id": "new-2", "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "Dislikes extreme sports (e.g., skydiving)", "old_position": {"start": 0, "end": 41}, "new_quote": null, "new_position": null, "source_id": null, "source_ref": null, "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].temporal_order.basis[0] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "ctx-1", "quote": "I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."}, {"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "explanation": "The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "scope": {"kind": "unconditional"}, "reason": "unchanged, earlier evidence, or outside evidence scope"}；独立审核：{"sha256": "6f684dfc517b436a627bd53f3842d3e2d249fdc336756ca9597c6878fe2f506b", "verdict": "unsupported", "reason": "旧厌恶原文本身可被保留，但此输出宣称其在证据范围之外被确定保留：本条 old unconditional 与 new finite 不可相减，且模型时间依据引用了未关联 ctx-1；规划器应将受影响部分列待确认，而不是把未能计算当成不重叠。"}
  - 输出：{"unit_id": "u2", "fact": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "relation": "change", "subject": "I", "attribute": "reason for disliking extreme sports", "old_value": "high injury risk", "new_value": "not stated as current barrier; explicitly affirms continued prioritization of safety", "old_quotes": [{"side": "old", "unit_id": "u2", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "position": {"start": 0, "end": 65}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}, {"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "old_position": {"start": 0, "end": 65}, "new_quote": null, "new_position": null, "source_id": null, "source_ref": null, "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[1].temporal_order.basis[0] not bound to cited same-side source/quote"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "ctx-1", "quote": "I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."}, {"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "explanation": "Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "scope": {"kind": "unconditional"}, "reason": "unchanged, earlier evidence, or outside evidence scope"}；独立审核：{"sha256": "5cea5735127918b35988a31f6d7332d02790fafebda732ad4a03246fc9fe61f9", "verdict": "unsupported", "reason": "旧高受伤风险理由没有被新证据推翻，可保留原文；但确定的 outside-evidence-scope 理由无法从 unconditional 对 finite 的条件差和未绑定时间依据推出，漏掉该部分待确认。"}
- uncertain（2）：
  - 输出：{"unit_id": "u3", "fact": "conflicting with commitment to safety and well-being", "relation": "supplement", "subject": "I", "attribute": "commitment to safety and well-being", "old_value": "conflicting with extreme sports", "new_value": "still prioritized, even amid new thrill-seeking", "old_quotes": [{"side": "old", "unit_id": "u3", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "conflicting with commitment to safety and well-being", "position": {"start": 67, "end": 119}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "conflicting with commitment to safety and well-being", "old_position": {"start": 67, "end": 119}, "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "new_position": {"start": 0, "end": 105}, "source_id": "new-8", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].old_conditions cannot use same_as_old"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "explanation": "The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "I still prioritize safety, of course."}], "value": "still prioritized, even amid new thrill-seeking", "scope": {"kind": "finite", "dimensions": {"context": ["simulated skydiving", "team-building event"]}}, "status": "asserted", "reason": "upstream validation errors: ['records[2].old_conditions cannot use same_as_old']"}；独立审核：{"sha256": "260be55b9674de4bb3a23ea2ebad40bc70ee366454ea6a160e4a7979fd8c5eeb", "verdict": "supported", "reason": "same_as_old 不能放在旧条件，且语义证据不足；该新增暂缓符合 v2 契约，但新话语独立表达安全优先仍可由人工另审。"}
  - 输出：{"unit_id": "u3", "fact": "conflicting with commitment to safety and well-being", "relation": "supplement", "subject": "I", "attribute": "commitment to safety and well-being", "old_value": "conflicting with extreme sports", "new_value": "still prioritized, even amid new thrill-seeking", "old_quotes": [{"side": "old", "unit_id": "u3", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "conflicting with commitment to safety and well-being", "position": {"start": 67, "end": 119}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "conflicting with commitment to safety and well-being", "old_position": {"start": 67, "end": 119}, "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "new_position": {"start": 0, "end": 105}, "source_id": "new-8", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].old_conditions cannot use same_as_old"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "explanation": "The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "I still prioritize safety, of course."}], "reason": "upstream validation errors: ['records[2].old_conditions cannot use same_as_old']"}；独立审核：{"sha256": "9b5a15194e2b875744337a6fa050a84c817d93fdb69a9e880050818ec75ebd59", "verdict": "supported", "reason": "旧安全冲突关系无法由安全优先单独证实且条件结构错误，暂缓相关影响适当。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

规划器引文位置和原因：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "u1",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "Dislikes extreme sports (e.g., skydiving)",
    "position": {
      "start": 0,
      "end": 41
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "unsplit-new-2",
    "source_id": "new-2",
    "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "u2",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
    "position": {
      "start": 0,
      "end": 65
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "unsplit-new-8",
    "source_id": "new-8",
    "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "position": {
      "start": 0,
      "end": 105
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "old",
    "unit_id": "u3",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "conflicting with commitment to safety and well-being",
    "position": {
      "start": 67,
      "end": 119
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-8",
    "source_id": "new-8",
    "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "position": {
      "start": 0,
      "end": 105
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
    "status": "valid",
    "reason": null
  }
]
```

**事后离线适配保护重算**（未再次调用模型；没有覆盖首次结果）

状态与散列：{"status": "completed_offline", "provenance": {"artifact_sha256": "a276e0066d48de68a4ffd6226eeca28390a89390db3308639830778282fa1654", "adapter_sha256": "d6c1a3f08c6a77d8908007422a68d710fa5d1ca9941f82ef277afbaff6077b8e", "planner_sha256": "3c46dc51936a19d0b52dcaf08f4f5b1edb2ed8e41ad403fd0c9b4dbdf49042a1", "raw_response_sha256": "4452eb6fd8ada021ff8c82f79763081c0d002cecee49c5a45d02747aab461741"}}

- modify（0）：
- preserve（0）：
- uncertain（4）：
  - 输出：{"unit_id": "u3", "fact": "conflicting with commitment to safety and well-being", "relation": "supplement", "subject": "I", "attribute": "commitment to safety and well-being", "old_value": "conflicting with extreme sports", "new_value": "still prioritized, even amid new thrill-seeking", "old_quotes": [{"side": "old", "unit_id": "u3", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "conflicting with commitment to safety and well-being", "position": {"start": 67, "end": 119}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "conflicting with commitment to safety and well-being", "old_position": {"start": 67, "end": 119}, "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "new_position": {"start": 0, "end": 105}, "source_id": "new-8", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].old_conditions cannot use same_as_old"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "explanation": "The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "I still prioritize safety, of course."}], "value": "still prioritized, even amid new thrill-seeking", "scope": {"kind": "finite", "dimensions": {"context": ["simulated skydiving", "team-building event"]}}, "status": "asserted", "reason": "upstream validation errors: ['records[2].old_conditions cannot use same_as_old']"}；独立审核：{"sha256": "260be55b9674de4bb3a23ea2ebad40bc70ee366454ea6a160e4a7979fd8c5eeb", "verdict": "supported", "reason": "旧侧 same_as_old 不符合字段规则；独立新事实语义未知，暂缓合适，仍可由人工另审安全优先。"}
  - 输出：{"unit_id": "u1", "fact": "Dislikes extreme sports (e.g., skydiving)", "relation": "change", "subject": "I", "attribute": "attitude toward extreme sports (e.g., skydiving)", "old_value": "dislikes", "new_value": "found simulated skydiving thrilling; more open to trying new things", "old_quotes": [{"side": "old", "unit_id": "u1", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving)", "position": {"start": 0, "end": 41}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}, {"side": "new", "unit_id": "unsplit-new-2", "source_id": "new-2", "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content", "status": "valid", "reason": null}], "old_quote": "Dislikes extreme sports (e.g., skydiving)", "old_position": {"start": 0, "end": 41}, "new_quote": null, "new_position": null, "source_id": null, "source_ref": null, "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[0].temporal_order.basis[0] not bound to cited same-side source/quote", "planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "ctx-1", "quote": "I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."}, {"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "explanation": "The old statement is from Sep 2025; the new statement uses 'recently' and is timestamped Apr 2026, confirming temporal succession."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[0].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']"}；独立审核：{"sha256": "b63efea1bac883a01e3737b1a8e1feb2683b8d87395d4046a82b44a595a3e3b3", "verdict": "supported", "reason": "新模拟条件不能从旧无条件范围计算差，旧 ctx-1 时间依据也未绑定；保护后 u1 明确待确认，未把模拟扩展到真实偏好。"}
  - 输出：{"unit_id": "u2", "fact": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "relation": "change", "subject": "I", "attribute": "reason for disliking extreme sports", "old_value": "high injury risk", "new_value": "not stated as current barrier; explicitly affirms continued prioritization of safety", "old_quotes": [{"side": "old", "unit_id": "u2", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "position": {"start": 0, "end": 65}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "manually_mapped_new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "position": {"start": 0, "end": 129}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content", "status": "valid", "reason": null}, {"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk", "old_position": {"start": 0, "end": 65}, "new_quote": null, "new_position": null, "source_id": null, "source_ref": null, "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[1].temporal_order.basis[0] not bound to cited same-side source/quote", "planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope"], "unknowns": [], "temporal_order": {"relation": "after", "basis": [{"side": "old", "source_id": "ctx-1", "quote": "I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being."}, {"side": "new", "source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}], "explanation": "Same temporal basis as previous record: old statement predates new by ~7 months; 'recently' anchors new event in Apr 2026."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "scope": {"kind": "unconditional"}, "reason": "upstream validation errors: ['records[1].temporal_order.basis[0] not bound to cited same-side source/quote', 'planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope']"}；独立审核：{"sha256": "25ccb8ea1f847e11d9f7b9d3c7f8ccbabe6962b9659a72cbee5aaaad550d1974", "verdict": "supported", "reason": "对旧受伤风险理由的更改没有证据，且新条件范围不可在 v2 中安全求差；保护后 u2 待确认。"}
  - 输出：{"unit_id": "u3", "fact": "conflicting with commitment to safety and well-being", "relation": "supplement", "subject": "I", "attribute": "commitment to safety and well-being", "old_value": "conflicting with extreme sports", "new_value": "still prioritized, even amid new thrill-seeking", "old_quotes": [{"side": "old", "unit_id": "u3", "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "conflicting with commitment to safety and well-being", "position": {"start": 67, "end": 119}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "status": "valid", "reason": null}], "new_quotes": [{"side": "new", "unit_id": "unsplit-new-8", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "position": {"start": 0, "end": 105}, "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "status": "valid", "reason": null}], "old_quote": "conflicting with commitment to safety and well-being", "old_position": {"start": 67, "end": 119}, "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.", "new_position": {"start": 0, "end": 105}, "source_id": "new-8", "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content", "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json", "note": null, "time_note": null, "missing_reasons": [], "validation_errors": ["records[2].old_conditions cannot use same_as_old"], "unknowns": [], "temporal_order": {"relation": "same", "basis": [{"side": "new", "source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}], "explanation": "The new statement affirms continuity of the safety commitment — no temporal shift implied; it coexists with the new experience."}, "semantic_support": "unknown", "semantic_basis": [{"side": "new", "source_id": "new-8", "quote": "I still prioritize safety, of course."}], "reason": "upstream validation errors: ['records[2].old_conditions cannot use same_as_old']"}；独立审核：{"sha256": "9b5a15194e2b875744337a6fa050a84c817d93fdb69a9e880050818ec75ebd59", "verdict": "supported", "reason": "u3 旧条件结构错误且安全优先不证明冲突因果保持，旧项影响待确认合适。"}
- add（0）：
- editable_spans（0）：
- protected_facts（0）：

事后规划器引用检查：

```json
[
  {
    "alignment_index": 0,
    "side": "old",
    "unit_id": "u1",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "Dislikes extreme sports (e.g., skydiving)",
    "position": {
      "start": 0,
      "end": 41
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 0,
    "side": "new",
    "unit_id": "unsplit-new-2",
    "source_id": "new-2",
    "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "old",
    "unit_id": "u2",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
    "position": {
      "start": 0,
      "end": 65
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "manually_mapped_new",
    "source_id": "new-0",
    "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "position": {
      "start": 0,
      "end": 129
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 1,
    "side": "new",
    "unit_id": "unsplit-new-8",
    "source_id": "new-8",
    "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "position": {
      "start": 0,
      "end": 105
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "old",
    "unit_id": "u3",
    "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "quote": "conflicting with commitment to safety and well-being",
    "position": {
      "start": 67,
      "end": 119
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
    "status": "valid",
    "reason": null
  },
  {
    "alignment_index": 2,
    "side": "new",
    "unit_id": "unsplit-new-8",
    "source_id": "new-8",
    "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "position": {
      "start": 0,
      "end": 105
    },
    "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
    "status": "valid",
    "reason": null
  }
]
```

**与原文和人工预期的差异：** schema 因旧侧 same_as_old 失败，basis 因前两条引用未关联 ctx-1 失败，8 条主引文唯一且单位关联有效、覆盖通过。模型仍把模拟体验扩展成真实极限运动偏好/风险理由变化，并依据对话时间声称 after；这不成立。v2 直接计划没有修改、新增，u3 列待确认，但对 u1/u2 输出了无条件 preserve：其旧 unconditional 与新 finite 的条件无法求差，且依据错误被空交集路径掩盖；保留原文方向虽可审慎接受，报告必须指出范围理由错误和遗漏待确认。人工预期保留旧顾虑、独立增加模拟体验及安全优先；未授权模型直接添加，因此当前计划比预期更保守。 事后离线保护重算将两条不成立的 preserve 转为待确认；这只是在现有适配层防止不支持的范围计算，并非证明旧条件或模型语义。首次输出原样保存，未重跑模型。

## 旧版五条引用核对

逐条来源、单元绑定和可复现实验见 [FIVE_QUOTES.md](../../FIVE_QUOTES.md)。
