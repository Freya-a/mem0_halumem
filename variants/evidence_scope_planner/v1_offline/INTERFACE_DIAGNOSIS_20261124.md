# 模型对齐结果与范围规划器接口诊断（离线）

## 范围与方法

本报告读取同目录 `REPORT.md`、`ALIGNER_AUDIT.md`、`SOURCES.md`、`adapter.py` 和 `scope_planner.py`，以及 `variants/evidence_aligner/runs/{fixed_five_20261120,v2_paired_20261120,v3_paired_20261120}/{case}.json` 的五案保存产物。三版每案依次调用当前 `load_aligner_case()` 与 `build_scope_plan()`，仅在内存中执行，不写回原结果，不调用模型/API；人工预期和人工对齐未注入模型输出。报告中的“原模型记录”是保存的 `result.parsed.records`；模型文本原样可在原产物 `raw_response` 和 `result.raw_response` 中核查。附录打印每条完整 parsed 记录、完整适配投影及规划器全部决策，包含各版结构错误和最终原因；不是新的模型输出。

分类：①模型或其输出规范没有提供判断所需信息；②适配器未向下游暴露已有信息、映射不匹配或错误归因；③规划器契约/校验粒度限制或时间处理不足；④模型语义判断、引文或结构存在问题。一条记录可以同时属于多类；原文存在信息不等于模型已经可靠规范化了该信息。

## 先看晋升案：完整字段流转

旧记忆 `Works at Historical Productions Ltd. as a Director`；新用户证据 `I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!`。旧引用 `Historical Productions Ltd.` 的位置是 [9,36)，`Director` 为 [42,50)，新句在 `new-0` 为 [0,92)，都是 Unicode 字符、左闭右开。记录时间是对话记录时间，并非晋升生效日期。旧单元 employer/title 为已有人工映射，非同文同 ID 的 SimpleMem 拆分。

| 版本 / 原记录 | 模型输出的关键字段 | 适配器投影及仍保留在 raw_record 的信息 | 规划器结果与分类 |
| --- | --- | --- | --- |
| v1 title | `job_title` / `state_change`；`old_value=Director`、`new_claim=lead director`、`time_expressions=[recently]`、`event_date=null`；两侧引文和来源均有。 | `relation=change`，旧值有；两主体、`new_value`、新旧条件为 null；`new_claim`、`recently` 只保留在 raw_record。 | 暂缓：缺主体、新值和规范条件。①模型无结构化主体/条件；②该条明确给出 `lead director` 却未作为规划器可用新值暴露，时间表达也仅在 raw_record。v1 的 `new_claim` 在其他记录可能是整句，不能一律无条件当作原子值。 |
| v1 employer | `no_clear_change`；`old_value` 与 `new_claim` 都是公司名，旧引文公司名、新引文晋升句。 | `relation=unknown`、旧值保留，新值和主体缺失，条件为 null。 | 暂缓；②已有同名信息未投影，`no_clear_change`→`unknown` 是保守映射，不能自动宣称同值或全域。 |
| v2 employer | 两侧 claim 的 subject=`user`、object=`Historical Productions Ltd.`、attribute=`employer`；`target_relation=same`、`change_type=support`。 | 主体、属性进入规划器；object、statement 保留在 raw_record；`target_relation` 仅保留为上游元数据，`support`→`unknown`，值/条件为 null。 | 暂缓；②已有对象及 same 信号未被规划器消费，但 object 的语义并不总等于属性值，不能普遍强行映射。此条本身的结构错误与另一条分开。 |
| v2 title | 两侧 subject=`user`、attribute=`job_title`、object=null；statement 分别称 Director / lead director；`target_relation=partially_overlapping`、`state_change`，change_evidence 为普通字符串。 | 主体、属性与 change 被投影；值/条件为 null，statement 在 raw_record；校验错误称 change_evidence 应为带 source_id/quote 的对象，故无法按该结构验证。 | 暂缓；①缺明确原子值/条件，②statement 与 target_relation 未被规划器消费，④保存记录的证据字段结构不合规范。 |
| v3 employer | `no_clear_change`，旧公司名及新晋升整句；qualifiers=[]、missing_evidence=[]。 | `unknown`；subject/value/conditions 均 null，双引文及来源有。 | 暂缓；①v3 格式未输出主体和值，②不能将空限定数组变成无条件。 |
| v3 title | `state_change`，旧 `Director`、新晋升整句；qualifier 为 new/time/`recently`，关联新句；`missing_evidence=[]`。 | `change`；新旧属性 `job_title`、引文及来源保留；主体、值、条件均 null；限定词只在 raw_record。 | 暂缓；①规范化主体/值/条件未提供，②相对时间信号无法直接供规划器使用。 |

规划器对 change/same 要求双侧 subject、attribute、value 一致可比较，并要求有可处理的 old/new_conditions 或显式 same_as_old；还会先用 `missing_reasons` 阻断。v1/v2/v3 晋升案当前内存回放均为 modify=0、preserve=0、uncertain=2、add=0。完整记录、适配输出和所有待确认原因为下方晋升字段明细；v2 整案 status=failed，具体是 title 记录的 change_evidence 结构错误，不能把它说成晋升事实不存在。

### 日期与时间关系：分开判断

`event_date=null` 或缺少精确日期并非当前函数的直接拒绝理由：代码没有要求该字段。`recently got promoted` 和模型 `state_change` 表达了相对变化/事件已发生，但没有足够信息算出具体日期；原语句不能作为时间戳，也不能由空条件推断全面覆盖。v3 的 `recently` 与 transition 的 `finally` 被保留在 raw_record，却没有传成规划器可消费的时间关系；planner API 也没有 `temporal_relation` 判断。

可复现的内存对照：构造相同已规范的 Director→lead director 输入，分别附加 `temporal_relation=before_old` 和 `after_old`（该字段不是现有接口），结果两次均 modify=1、uncertain=0。此实验说明字段被忽略，不代表两个标注是真的，也不能证明现有五案应自动修改；如果证据实际上早于旧事实，当前接口不能阻止时间倒置。需要区分“能否确认事件先后/生效”与“能否给出日历日期”；对相关事实既无法确认先后又影响当前状态时应暂缓，而已确认相对变化不应仅因缺日历日期被一概拒绝。相对变化也不意味着 Director 的宽泛称谓已为假或历史事实可以删除。

## 其余四案对照

表中斜杠按 v1 / v2 / v3 排列；括号内为实际内存回放 `modify,preserve,uncertain,add`。原始逐记录字段与最终原因见下方明细。

| 案例 | 原模型关系与关键引文 | 适配器输出及最终待确认 | 归因与判断 |
| --- | --- | --- | --- |
| Susan | v1 `support / supplement / plan`；v2 两个 `support`、一个 `no_clear_change`；v3 `support / supplement / new_information`。旧友谊/支持，新 Susan 鼓励和求职意向。 | 全部 0,0,3,0。support→unknown；独立 plan 保留 plan 但缺主体/值，旧条件也被无条件列缺；v3 最后记录虽关联两个旧单元却无旧引。 | ①/②/③/④。v1 整句旧引用超出 friendship 单元，plan 时间表达结构不合 schema；v3 缺关联旧引用。未知雇主、职位、计划何时完成并不必然妨碍将有证据的意向作为计划保存，但此记录还有引文/结构及主体等各自需核对的问题。不要把 Daniel 的话归给 Susan。 |
| 转岗 | 三版均 `state_change`；旧 `Looking for a new job with better work-life balance`，新 `finally transitioned to a new role`、平衡改善。 | 全部 0,0,1,0。v1/v3 缺主体、值、条件；v2 值和条件未投影且有校验错误；v3 带来源错误的旧 `lately`。 | ①/②/④。已转岗的相对进展不需要具体日历日，但不证明此后完全停止求职；旧句的平衡目标应受保护。v3 的旧限定词来自未关联的上下文，不能自动接受。 |
| 职业历史 | v1 对旧 employer/title 判 `state_change`，另有获客和人脉 `new_information`；v2 为活动/职位 `new_information`；v3 对旧 employer/title 判 `state_change`，人脉为 `new_information`。旧文明确 `Previously worked...`，新句称咨询公司获客。 | v1 0,0,4,0；v2/v3 均 0,0,3,0。独立 `new_information`→`unrelated`，旧条件被错误地列为必要缺项；v2 未覆盖新单元的全局错误还被附到其他记录。 | ②/③/④，另有①值和条件不足。咨询公司获客不能证明历史工作或职位发生改变，v1/v3 的 state_change 不可靠；已保存的独立新增也受映射不兼容阻断。不能只凭材料里的 `my firm` 推断所有权、现职或离职日期。 |
| 跳伞 | v1 对态度/理由判 `state_change`；v2 对体验判 `supplement`，其余 support/supplement；v3 对态度/理由仍判 `state_change`、安全冲突 `no_clear_change`。新引文明说 `simulated skydiving`。 | v1/v3 各 0,0,3,0，v2 0,0,4,0。v3 u2/u3 多条新引文各自保留在 `resolved_new_quotes`，但单引文投影被清空，最终首要原因显示 source missing。 | ①/②/③/④。v3 自报模拟不足以证明真实运动态度或受伤理由变化，却仍给 state_change；不能扩大成真实活动偏好变化。`source missing` 在这里并不证明原始引文来源不存在，须逐条验证。只有安全优先也不能单独证明旧完整因果关系。 |

## 跨接口诊断与修复顺序

1. **优先修适配器和双方的接口契约，规划器相对时间保护需同步设计。** 可复现的硬错误：`adapter.py` 把模型 `new_information` 映射为 `unrelated`，而 `scope_planner.py` 对 `unit_id=None` 只接受 `supplement` 或 `plan`；所以即便将来其他字段补齐，独立新增仍会被关系门禁拒绝。现有 career_history 原产物本身还缺其他必需字段，因此不能声称仅修这个映射就可通过。适配应传递被来源约束的原始 claim/qualifier/多引用，区分“原文明确给出但未类型化”与“确实没有提供”，保留关系及错误的作用范围；不可把 v1 所有 `new_claim` 或 v2 所有 `object` 盲目当原子值，也不可从空限定词推断全域。
2. **调整规划器按动作检查必需信息，并增加明确相对时间接口。** 当前缺项、上游 unknowns 全部合并成 blocker，连独立新增也被适配器报告缺旧条件；未知完成时间不一定阻止明确的计划新增。多来源引用应逐条校验；将引用命中状态与语义/操作资格分开。对冲突、未证实范围和不明先后仍须暂缓。`quote_checks` 的 invalid 有时包括字段缺失，而不等价于逐字引文未命中；`source missing` 也可能只是多引用无法投影。
3. **再改进并重新评估对齐器的语义和输出协议。** v3 按提示词只输出引文、关系与限定词，不给主体/值，不能把 schema 缺项完全归责于模型个案。另一方面，跳伞和职业历史的错误 `state_change` 是语义问题；必须针对模拟/真实、历史/当前、计划/完成和限定词来源做独立评审。优先级是修通并保护可审查的信息流，不是无条件放宽门禁；即使对齐器字段完整，错误关系仍应被拦截或标待确认。

## 拆分与来源限制

只有 skydiving 复用 `variants/simplemem_mem0_splitter/offline_entity_recheck_20261119/case_2.json` 中同 memory_id、同旧文的真实 SimpleMem 三个单元；它们重叠，u3 短引文不足以独立证明完整因果。promotion、Susan、transition、career_history 使用先前人工映射旧单元。career_history 曾有相同 ID 的拆分，但更早 session_004 旧文为 `Works...`，本案 session_008 为 `Previously worked...`，不能当同一旧文本。新证据只选择部分用户消息，有些是 unsplit；完整会话用于上下文，不是对整场对话的完整拆分。五案 memory_id、user、session、source_ref 与时间限制详见 `SOURCES.md`。

## 晋升案完整原始字段、适配投影及规划器输出
### promotion / v1

来源：`variants/evidence_aligner/runs/fixed_five_20261120/promotion.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "job_title",
      "change_type": "state_change",
      "old_value": "Director",
      "new_claim": "lead director",
      "old_quotes": [
        {
          "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
          "quote": "Director"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "recently"
        }
      ],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "employer",
      "change_type": "no_clear_change",
      "old_value": "Historical Productions Ltd.",
      "new_claim": "Historical Productions Ltd.",
      "old_quotes": [
        {
          "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
          "quote": "Historical Productions Ltd."
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "recently"
        }
      ],
      "event_date": null,
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "title",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "job_title",
    "new_attribute": "job_title",
    "old_value": "Director",
    "new_value": null,
    "old_quote": "Director",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Director",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "employer",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "employer",
    "new_attribute": "employer",
    "old_value": "Historical Productions Ltd.",
    "new_value": null,
    "old_quote": "Historical Productions Ltd.",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "no_clear_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Historical Productions Ltd.",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "employer",
      "fact": "employer",
      "relation": "unknown",
      "old_quote": "Historical Productions Ltd.",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": "Historical Productions Ltd.",
      "new_value": null,
      "subject": null,
      "attribute": "employer",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "title",
      "fact": "job_title",
      "relation": "change",
      "old_quote": "Director",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": "Director",
      "new_value": null,
      "subject": null,
      "attribute": "job_title",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Historical Productions Ltd.",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "Director",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### promotion / v2

来源：`variants/evidence_aligner/runs/v2_paired_20261120/promotion.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": "Historical Productions Ltd.",
        "attribute": "employer",
        "statement": "user works at Historical Productions Ltd.",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "Historical Productions Ltd.",
        "attribute": "employer",
        "statement": "user works at Historical Productions Ltd.",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "same",
      "change_type": "support",
      "old_quotes": [
        {
          "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
          "quote": "Historical Productions Ltd."
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
        }
      ],
      "change_evidence": [],
      "relation_explanation": "Both claims assert the same employer–employee relationship with Historical Productions Ltd.; the new statement reaffirms the employer without altering it.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": null,
        "attribute": "job_title",
        "statement": "user is a Director",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": null,
        "attribute": "job_title",
        "statement": "user is a lead director",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "partially_overlapping",
      "change_type": "state_change",
      "old_quotes": [
        {
          "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
          "quote": "Director"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
        }
      ],
      "change_evidence": [
        "got promoted to lead director"
      ],
      "relation_explanation": "The new claim specifies a promotion from 'Director' to 'lead director', indicating a change in job title. The phrase 'got promoted to lead director' directly supports that the prior title has changed.",
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "schema",
      "path": "records[1].change_evidence[0]",
      "message": "source_id and quote required"
    },
    {
      "code": "change_evidence_not_in_new_quote",
      "path": "records[1].change_evidence[0]",
      "message": "must be within a cited new quote"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "employer",
    "relation": "unknown",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "employer",
    "new_attribute": "employer",
    "old_value": null,
    "new_value": null,
    "old_quote": "Historical Productions Ltd.",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "support",
    "upstream_target_relation": "same",
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Historical Productions Ltd.",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "title",
    "relation": "change",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "job_title",
    "new_attribute": "job_title",
    "old_value": null,
    "new_value": null,
    "old_quote": "Director",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "state_change",
    "upstream_target_relation": "partially_overlapping",
    "upstream_structure_errors": [
      {
        "code": "schema",
        "path": "records[1].change_evidence[0]",
        "message": "source_id and quote required"
      },
      {
        "code": "change_evidence_not_in_new_quote",
        "path": "records[1].change_evidence[0]",
        "message": "must be within a cited new quote"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Director",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}",
      "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "employer",
      "fact": "employer",
      "relation": "unknown",
      "old_quote": "Historical Productions Ltd.",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "employer",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "title",
      "fact": "job_title",
      "relation": "change",
      "old_quote": "Director",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "job_title",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}",
        "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}; upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Historical Productions Ltd.",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "Director",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### promotion / v3

来源：`variants/evidence_aligner/runs/v3_paired_20261120/promotion.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "employer",
      "relation": "no_clear_change",
      "old_quotes": [
        "Historical Productions Ltd."
      ],
      "new_quotes": [
        "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
      ],
      "qualifiers": [],
      "missing_evidence": []
    },
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "job_title",
      "relation": "state_change",
      "old_quotes": [
        "Director"
      ],
      "new_quotes": [
        "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "time",
          "quote": "recently",
          "claim_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"
        }
      ],
      "missing_evidence": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": [],
  "validation_errors": null,
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": [],
    "mentioned_old_unit_ids": [
      "employer",
      "title"
    ],
    "mentioned_new_unit_ids": [
      "manually_mapped_new"
    ]
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "employer",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "employer",
    "new_attribute": "employer",
    "old_value": null,
    "new_value": null,
    "old_quote": "Historical Productions Ltd.",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "no_clear_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Historical Productions Ltd.",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "title",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "job_title",
    "new_attribute": "job_title",
    "old_value": null,
    "new_value": null,
    "old_quote": "Director",
    "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
    "source_id": "new-0",
    "old_quote_source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Director",
        "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "employer",
      "fact": "employer",
      "relation": "unknown",
      "old_quote": "Historical Productions Ltd.",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "employer",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "title",
      "fact": "job_title",
      "relation": "change",
      "old_quote": "Director",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "job_title",
      "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Historical Productions Ltd.",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 9,
        "end": 36
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "Director",
      "source_id": "new-0",
      "new_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!",
      "old_position": {
        "start": 42,
        "end": 50
      },
      "new_position": {
        "start": 0,
        "end": 92
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

## 其余四案逐版完整字段明细

### susan / v1

来源：`variants/evidence_aligner/runs/fixed_five_20261120/susan.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "friendship"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "friendship",
      "change_type": "support",
      "old_value": "ThomasSusan (referred to as 'Susan')",
      "new_claim": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "old_quotes": [
        {
          "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
          "quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."
        }
      ],
      "conditions": [],
      "time_expressions": [],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "support"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "support_context",
      "change_type": "supplement",
      "old_value": "provides support and encouragement",
      "new_claim": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_quotes": [
        {
          "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
          "quote": "provides support and encouragement"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."
        }
      ],
      "conditions": [],
      "time_expressions": [],
      "event_date": null,
      "unknowns": [
        "Daniel's identity or relationship status (e.g., friend, colleague, mentor) is not specified in user's own words"
      ]
    },
    {
      "old_unit_ids": [],
      "new_unit_ids": [
        "unsplit-new-0"
      ],
      "attribute": "career_status",
      "change_type": "plan",
      "old_value": null,
      "new_claim": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "old_quotes": [],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
        }
      ],
      "conditions": [],
      "time_expressions": [
        "lately"
      ],
      "event_date": null,
      "unknowns": [
        "Current employer name",
        "Current job title",
        "Timeline for job search completion",
        "Whether any applications or interviews have occurred yet"
      ]
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "quote_provenance",
      "path": "records[0].old_quotes[0]",
      "message": "not an exact quote within a linked unit on the correct side"
    },
    {
      "code": "unit_without_quote",
      "path": "records[0].old_unit_ids",
      "message": "friendship"
    },
    {
      "code": "schema",
      "path": "records[2].time_expressions[0]",
      "message": "source_id and quote required"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "friendship",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "friendship",
    "new_attribute": "friendship",
    "old_value": "ThomasSusan (referred to as 'Susan')",
    "new_value": null,
    "old_quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
    "source_id": "new-2",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "support",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[0].old_quotes[0]",
        "message": "not an exact quote within a linked unit on the correct side"
      },
      {
        "code": "unit_without_quote",
        "path": "records[0].old_unit_ids",
        "message": "friendship"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
        "source_id": null
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[0].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[0].old_unit_ids', 'message': 'friendship'}",
      "old quote has missing, ambiguous, or mismatched linked-unit source: Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "support",
    "relation": "supplement",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "support_context",
    "new_attribute": "support_context",
    "old_value": "provides support and encouragement",
    "new_value": null,
    "old_quote": "provides support and encouragement",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
    "source_id": "new-2",
    "old_quote_source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "supplement",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "provides support and encouragement",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: Daniel's identity or relationship status (e.g., friend, colleague, mentor) is not specified in user's own words"
    ]
  },
  {
    "unit_id": null,
    "relation": "plan",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": null,
    "new_attribute": "career_status",
    "old_value": null,
    "new_value": null,
    "old_quote": null,
    "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
    "source_id": "new-0",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "plan",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "schema",
        "path": "records[2].time_expressions[0]",
        "message": "source_id and quote required"
      }
    ],
    "resolved_old_quotes": [],
    "resolved_new_quotes": [
      {
        "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'schema', 'path': 'records[2].time_expressions[0]', 'message': 'source_id and quote required'}",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: Current employer name",
      "model unknown: Current job title",
      "model unknown: Timeline for job search completion",
      "model unknown: Whether any applications or interviews have occurred yet"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "plan",
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "subject": null,
      "attribute": "career_status",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "upstream validation error: {'code': 'schema', 'path': 'records[2].time_expressions[0]', 'message': 'source_id and quote required'}",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: Current employer name",
        "model unknown: Current job title",
        "model unknown: Timeline for job search completion",
        "model unknown: Whether any applications or interviews have occurred yet"
      ],
      "reason": "missing upstream information: upstream validation error: {'code': 'schema', 'path': 'records[2].time_expressions[0]', 'message': 'source_id and quote required'}; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: Current employer name; model unknown: Current job title; model unknown: Timeline for job search completion; model unknown: Whether any applications or interviews have occurred yet"
    },
    {
      "unit_id": "friendship",
      "fact": "friendship",
      "relation": "unknown",
      "old_quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 0,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": "ThomasSusan (referred to as 'Susan')",
      "new_value": null,
      "subject": null,
      "attribute": "friendship",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[0].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[0].old_unit_ids', 'message': 'friendship'}",
        "old quote has missing, ambiguous, or mismatched linked-unit source: Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "old quote is outside its designated unit"
    },
    {
      "unit_id": "support",
      "fact": "friend_support",
      "relation": "supplement",
      "old_quote": "provides support and encouragement",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": "provides support and encouragement",
      "new_value": null,
      "subject": null,
      "attribute": "support_context",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: Daniel's identity or relationship status (e.g., friend, colleague, mentor) is not specified in user's own words"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: Daniel's identity or relationship status (e.g., friend, colleague, mentor) is not specified in user's own words"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-0",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "status": "invalid",
      "new_error": "missing upstream information: upstream validation error: {'code': 'schema', 'path': 'records[2].time_expressions[0]', 'message': 'source_id and quote required'}; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: Current employer name; model unknown: Current job title; model unknown: Timeline for job search completion; model unknown: Whether any applications or interviews have occurred yet"
    },
    {
      "unit_id": "friendship",
      "alignment_index": 0,
      "old_quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 0,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "status": "invalid",
      "old_error": "old quote is outside its designated unit",
      "new_error": null
    },
    {
      "unit_id": "support",
      "alignment_index": 0,
      "old_quote": "provides support and encouragement",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### susan / v2

来源：`variants/evidence_aligner/runs/v2_paired_20261120/susan.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "friendship"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": "ThomasSusan",
        "attribute": "relationship",
        "statement": "has friendship with ThomasSusan",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "Susan",
        "attribute": "relationship",
        "statement": "has friendship with Susan",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "same",
      "change_type": "support",
      "old_quotes": [
        {
          "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
          "quote": "friend named ThomasSusan"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "The new quote refers to 'Susan' as a supportive figure and uses the same first name previously associated with 'ThomasSusan' in the old unit; the context (e.g., 'Susan's support', 'her encouragement') confirms continuity of the person and relationship. No change in the friendship claim is indicated — only reaffirmation.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "support"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "ThomasSusan",
        "object": "user",
        "attribute": "support",
        "statement": "provides support and encouragement",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "Susan",
        "object": "user",
        "attribute": "support",
        "statement": "provides support and encouragement",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "same",
      "change_type": "support",
      "old_quotes": [
        {
          "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
          "quote": "provides support and encouragement"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "The new quote explicitly affirms Susan's support and encouragement, directly aligning with the old claim about ThomasSusan providing support and encouragement. The name 'Susan' is used consistently with prior reference to 'ThomasSusan' (i.e., 'ThomasSusan' is a compound name or alias for Susan), confirming identity and continuity of the support function.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "friendship",
        "support"
      ],
      "new_unit_ids": [
        "unsplit-new-0"
      ],
      "old_claim": {
        "subject": "user",
        "object": null,
        "attribute": "well-being_support_from_role",
        "statement": "current role supports well-being",
        "qualifiers": [
          {
            "kind": "negation",
            "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
            "quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"
          }
        ],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "current role",
        "attribute": "well-being_support",
        "statement": "does not support well-being as much as desired",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "different",
      "change_type": "no_clear_change",
      "old_quotes": [
        {
          "source_id": "ctx-1",
          "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "The old evidence describes well-being support *from Susan*, not from the user's current role. The new claim concerns the *current role's insufficiency* in supporting well-being — a distinct subject-object-attribute triple. There is no prior claim about the current role’s support level, so this is not a change but an independent new assertion.",
      "unknowns": [
        "Whether the user previously held a view about their current role’s support for well-being"
      ]
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "quote_provenance",
      "path": "records[2].old_quotes[0]",
      "message": "quote not found in the linked source/units on the correct side"
    },
    {
      "code": "unit_without_quote",
      "path": "records[2].old_unit_ids",
      "message": "friendship"
    },
    {
      "code": "unit_without_quote",
      "path": "records[2].old_unit_ids",
      "message": "support"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "friendship",
    "relation": "unknown",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "relationship",
    "new_attribute": "relationship",
    "old_value": null,
    "new_value": null,
    "old_quote": "friend named ThomasSusan",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
    "source_id": "new-2",
    "old_quote_source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "support",
    "upstream_target_relation": "same",
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "friend named ThomasSusan",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "support",
    "relation": "unknown",
    "old_subject": "ThomasSusan",
    "new_subject": "Susan",
    "old_attribute": "support",
    "new_attribute": "support",
    "old_value": null,
    "new_value": null,
    "old_quote": "provides support and encouragement",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
    "source_id": "new-2",
    "old_quote_source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "support",
    "upstream_target_relation": "same",
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "provides support and encouragement",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": null,
    "relation": "unknown",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "well-being_support_from_role",
    "new_attribute": "well-being_support",
    "old_value": null,
    "new_value": null,
    "old_quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.",
    "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
    "source_id": "new-0",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "no_clear_change",
    "upstream_target_relation": "different",
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[2].old_quotes[0]",
        "message": "quote not found in the linked source/units on the correct side"
      },
      {
        "code": "unit_without_quote",
        "path": "records[2].old_unit_ids",
        "message": "friendship"
      },
      {
        "code": "unit_without_quote",
        "path": "records[2].old_unit_ids",
        "message": "support"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.",
        "source_id": null
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'quote not found in the linked source/units on the correct side'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}",
      "multiple old unit IDs; no unique unit binding",
      "old quote has missing, ambiguous, or mismatched linked-unit source: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: Whether the user previously held a view about their current role’s support for well-being"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "unknown",
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "subject": "user",
      "attribute": "well-being_support",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'quote not found in the linked source/units on the correct side'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}",
        "multiple old unit IDs; no unique unit binding",
        "old quote has missing, ambiguous, or mismatched linked-unit source: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: Whether the user previously held a view about their current role’s support for well-being"
      ],
      "reason": "missing upstream information: upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'quote not found in the linked source/units on the correct side'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old quote has missing, ambiguous, or mismatched linked-unit source: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: Whether the user previously held a view about their current role’s support for well-being"
    },
    {
      "unit_id": "friendship",
      "fact": "friendship",
      "relation": "unknown",
      "old_quote": "friend named ThomasSusan",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 6,
        "end": 30
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "relationship",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "support",
      "fact": "friend_support",
      "relation": "unknown",
      "old_quote": "provides support and encouragement",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": null,
      "new_value": null,
      "subject": "ThomasSusan",
      "attribute": "support",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-0",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "status": "invalid",
      "new_error": "missing upstream information: upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'quote not found in the linked source/units on the correct side'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old quote has missing, ambiguous, or mismatched linked-unit source: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: Whether the user previously held a view about their current role’s support for well-being"
    },
    {
      "unit_id": "friendship",
      "alignment_index": 0,
      "old_quote": "friend named ThomasSusan",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 6,
        "end": 30
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "support",
      "alignment_index": 0,
      "old_quote": "provides support and encouragement",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 261
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### susan / v3

来源：`variants/evidence_aligner/runs/v3_paired_20261120/susan.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "friendship"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "friendship",
      "relation": "support",
      "old_quotes": [
        "friend named ThomasSusan"
      ],
      "new_quotes": [
        "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
      ],
      "qualifiers": [],
      "missing_evidence": []
    },
    {
      "old_unit_ids": [
        "support"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "support",
      "relation": "supplement",
      "old_quotes": [
        "provides support and encouragement"
      ],
      "new_quotes": [
        "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."
      ],
      "qualifiers": [],
      "missing_evidence": []
    },
    {
      "old_unit_ids": [
        "friendship",
        "support"
      ],
      "new_unit_ids": [
        "unsplit-new-0"
      ],
      "attribute": "career_wellbeing_alignment",
      "relation": "new_information",
      "old_quotes": [],
      "new_quotes": [
        "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "time",
          "quote": "lately",
          "claim_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like."
        }
      ],
      "missing_evidence": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": [
    {
      "code": "missing_quote",
      "path": "records[2].old_quotes",
      "message": "at least one quote required"
    },
    {
      "code": "unit_without_quote",
      "path": "records[2].old_unit_ids",
      "message": "friendship"
    },
    {
      "code": "unit_without_quote",
      "path": "records[2].old_unit_ids",
      "message": "support"
    }
  ],
  "validation_errors": null,
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": [],
    "mentioned_old_unit_ids": [
      "friendship",
      "support"
    ],
    "mentioned_new_unit_ids": [
      "manually_mapped_new",
      "unsplit-new-0"
    ]
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "friendship",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "friendship",
    "new_attribute": "friendship",
    "old_value": null,
    "new_value": null,
    "old_quote": "friend named ThomasSusan",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "source_id": "new-2",
    "old_quote_source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "support",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "friend named ThomasSusan",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "support",
    "relation": "supplement",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "support",
    "new_attribute": "support",
    "old_value": null,
    "new_value": null,
    "old_quote": "provides support and encouragement",
    "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
    "source_id": "new-2",
    "old_quote_source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "supplement",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "provides support and encouragement",
        "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": null,
    "relation": "unrelated",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "career_wellbeing_alignment",
    "new_attribute": "career_wellbeing_alignment",
    "old_value": null,
    "new_value": null,
    "old_quote": null,
    "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
    "source_id": "new-0",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "new_information",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "missing_quote",
        "path": "records[2].old_quotes",
        "message": "at least one quote required"
      },
      {
        "code": "unit_without_quote",
        "path": "records[2].old_unit_ids",
        "message": "friendship"
      },
      {
        "code": "unit_without_quote",
        "path": "records[2].old_unit_ids",
        "message": "support"
      }
    ],
    "resolved_old_quotes": [],
    "resolved_new_quotes": [
      {
        "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}",
      "multiple old unit IDs; no unique unit binding",
      "old side lacks a single uniquely represented quote",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "unrelated",
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "subject": null,
      "attribute": "career_wellbeing_alignment",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}",
        "multiple old unit IDs; no unique unit binding",
        "old side lacks a single uniquely represented quote",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "reason": "missing upstream information: upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old side lacks a single uniquely represented quote; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "friendship",
      "fact": "friendship",
      "relation": "unknown",
      "old_quote": "friend named ThomasSusan",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "old_position": {
        "start": 6,
        "end": 30
      },
      "new_position": {
        "start": 0,
        "end": 96
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "friendship",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "support",
      "fact": "friend_support",
      "relation": "supplement",
      "old_quote": "provides support and encouragement",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 96
      },
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "support",
      "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-0",
      "new_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.",
      "new_position": {
        "start": 0,
        "end": 255
      },
      "status": "invalid",
      "new_error": "missing upstream information: upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old side lacks a single uniquely represented quote; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "friendship",
      "alignment_index": 0,
      "old_quote": "friend named ThomasSusan",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "old_position": {
        "start": 6,
        "end": 30
      },
      "new_position": {
        "start": 0,
        "end": 96
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "support",
      "alignment_index": 0,
      "old_quote": "provides support and encouragement",
      "source_id": "new-2",
      "new_quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.",
      "old_position": {
        "start": 60,
        "end": 94
      },
      "new_position": {
        "start": 0,
        "end": 96
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### transition / v1

来源：`variants/evidence_aligner/runs/fixed_five_20261120/transition.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "job_search"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "transition_progress",
      "change_type": "state_change",
      "old_value": "looking for a new job",
      "new_claim": "has transitioned to a new role",
      "old_quotes": [
        {
          "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
          "quote": "Looking for a new job with better work-life balance"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "finally"
        }
      ],
      "event_date": null,
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "job_search",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "transition_progress",
    "new_attribute": "transition_progress",
    "old_value": "looking for a new job",
    "new_value": null,
    "old_quote": "Looking for a new job with better work-life balance",
    "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
    "source_id": "new-0",
    "old_quote_source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Looking for a new job with better work-life balance",
        "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "job_search",
      "fact": "transition_progress",
      "relation": "change",
      "old_quote": "Looking for a new job with better work-life balance",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
      "old_value": "looking for a new job",
      "new_value": null,
      "subject": null,
      "attribute": "transition_progress",
      "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "job_search",
      "alignment_index": 0,
      "old_quote": "Looking for a new job with better work-life balance",
      "source_id": "new-0",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### transition / v2

来源：`variants/evidence_aligner/runs/v2_paired_20261120/transition.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "job_search"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": null,
        "attribute": "transition_progress",
        "statement": "Looking for a new job with better work-life balance",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": null,
        "attribute": "transition_progress",
        "statement": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "different",
      "change_type": "state_change",
      "old_quotes": [
        {
          "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
          "quote": "Looking for a new job with better work-life balance"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
        }
      ],
      "change_evidence": [
        "I've finally transitioned to a new role"
      ],
      "relation_explanation": "The old claim describes an ongoing search (‘looking for’), indicating an uncompleted state. The new claim explicitly states completion (‘finally transitioned’) and reports improved work-life balance as an achieved outcome. ‘Finally transitioned’ directly contradicts the prior searching state and confirms a change in status.",
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "schema",
      "path": "records[0].change_evidence[0]",
      "message": "source_id and quote required"
    },
    {
      "code": "change_evidence_not_in_new_quote",
      "path": "records[0].change_evidence[0]",
      "message": "must be within a cited new quote"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "job_search",
    "relation": "change",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "transition_progress",
    "new_attribute": "transition_progress",
    "old_value": null,
    "new_value": null,
    "old_quote": "Looking for a new job with better work-life balance",
    "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
    "source_id": "new-0",
    "old_quote_source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "state_change",
    "upstream_target_relation": "different",
    "upstream_structure_errors": [
      {
        "code": "schema",
        "path": "records[0].change_evidence[0]",
        "message": "source_id and quote required"
      },
      {
        "code": "change_evidence_not_in_new_quote",
        "path": "records[0].change_evidence[0]",
        "message": "must be within a cited new quote"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Looking for a new job with better work-life balance",
        "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'schema', 'path': 'records[0].change_evidence[0]', 'message': 'source_id and quote required'}",
      "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[0].change_evidence[0]', 'message': 'must be within a cited new quote'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "job_search",
      "fact": "transition_progress",
      "relation": "change",
      "old_quote": "Looking for a new job with better work-life balance",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "transition_progress",
      "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'schema', 'path': 'records[0].change_evidence[0]', 'message': 'source_id and quote required'}",
        "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[0].change_evidence[0]', 'message': 'must be within a cited new quote'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'schema', 'path': 'records[0].change_evidence[0]', 'message': 'source_id and quote required'}; upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[0].change_evidence[0]', 'message': 'must be within a cited new quote'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "job_search",
      "alignment_index": 0,
      "old_quote": "Looking for a new job with better work-life balance",
      "source_id": "new-0",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### transition / v3

来源：`variants/evidence_aligner/runs/v3_paired_20261120/transition.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "job_search"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "transition_progress",
      "relation": "state_change",
      "old_quotes": [
        "Looking for a new job with better work-life balance"
      ],
      "new_quotes": [
        "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
      ],
      "qualifiers": [
        {
          "side": "old",
          "kind": "time",
          "quote": "lately",
          "claim_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."
        },
        {
          "side": "new",
          "kind": "time",
          "quote": "finally",
          "claim_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."
        }
      ],
      "missing_evidence": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": [
    {
      "code": "qualifier_anchor_provenance",
      "path": "records[0].qualifiers[0]",
      "message": "claim_quote must overlap a cited quote in its linked source"
    }
  ],
  "validation_errors": null,
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": [],
    "mentioned_old_unit_ids": [
      "job_search"
    ],
    "mentioned_new_unit_ids": [
      "manually_mapped_new"
    ]
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "job_search",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "transition_progress",
    "new_attribute": "transition_progress",
    "old_value": null,
    "new_value": null,
    "old_quote": "Looking for a new job with better work-life balance",
    "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
    "source_id": "new-0",
    "old_quote_source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "qualifier_anchor_provenance",
        "path": "records[0].qualifiers[0]",
        "message": "claim_quote must overlap a cited quote in its linked source"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Looking for a new job with better work-life balance",
        "source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'qualifier_anchor_provenance', 'path': 'records[0].qualifiers[0]', 'message': 'claim_quote must overlap a cited quote in its linked source'}",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "job_search",
      "fact": "transition_progress",
      "relation": "change",
      "old_quote": "Looking for a new job with better work-life balance",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "transition_progress",
      "memory_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'qualifier_anchor_provenance', 'path': 'records[0].qualifiers[0]', 'message': 'claim_quote must overlap a cited quote in its linked source'}",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'qualifier_anchor_provenance', 'path': 'records[0].qualifiers[0]', 'message': 'claim_quote must overlap a cited quote in its linked source'}; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "job_search",
      "alignment_index": 0,
      "old_quote": "Looking for a new job with better work-life balance",
      "source_id": "new-0",
      "new_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.",
      "old_position": {
        "start": 0,
        "end": 51
      },
      "new_position": {
        "start": 0,
        "end": 135
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### career_history / v1

来源：`variants/evidence_aligner/runs/fixed_five_20261120/career_history.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "employer",
      "change_type": "state_change",
      "old_value": "Blockchain Tech",
      "new_claim": "consulting firm",
      "old_quotes": [
        {
          "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
          "quote": "Blockchain Tech"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "my consulting firm finally secured some initial clients"
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "lately"
        }
      ],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "title",
      "change_type": "state_change",
      "old_value": "senior developer",
      "new_claim": "founder/owner of consulting firm",
      "old_quotes": [
        {
          "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
          "quote": "senior developer"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "my consulting firm finally secured some initial clients"
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "lately"
        }
      ],
      "event_date": null,
      "unknowns": [
        "exact title or role name in the consulting firm"
      ]
    },
    {
      "old_unit_ids": [],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "client_milestone",
      "change_type": "new_information",
      "old_value": null,
      "new_claim": "consulting firm secured some initial clients",
      "old_quotes": [],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "lately"
        }
      ],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [],
      "new_unit_ids": [
        "unsplit-new-2"
      ],
      "attribute": "network_contact_effectiveness",
      "change_type": "new_information",
      "old_value": null,
      "new_claim": "MooreSandra and GonzalezMary were instrumental; their connections opened doors",
      "old_quotes": [],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."
        }
      ],
      "conditions": [],
      "time_expressions": [],
      "event_date": null,
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "employer",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "employer",
    "new_attribute": "employer",
    "old_value": "Blockchain Tech",
    "new_value": null,
    "old_quote": "Blockchain Tech",
    "new_quote": "my consulting firm finally secured some initial clients",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Blockchain Tech",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "my consulting firm finally secured some initial clients",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "title",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "title",
    "new_attribute": "title",
    "old_value": "senior developer",
    "new_value": null,
    "old_quote": "senior developer",
    "new_quote": "my consulting firm finally secured some initial clients",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "senior developer",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "my consulting firm finally secured some initial clients",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: exact title or role name in the consulting firm"
    ]
  },
  {
    "unit_id": null,
    "relation": "unrelated",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": null,
    "new_attribute": "client_milestone",
    "old_value": null,
    "new_value": null,
    "old_quote": null,
    "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
    "source_id": "new-0",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "new_information",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [],
    "resolved_new_quotes": [
      {
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": null,
    "relation": "unrelated",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": null,
    "new_attribute": "network_contact_effectiveness",
    "old_value": null,
    "new_value": null,
    "old_quote": null,
    "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
    "source_id": "new-2",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "new_information",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [],
    "resolved_new_quotes": [
      {
        "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "unrelated",
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "new_position": {
        "start": 0,
        "end": 141
      },
      "subject": null,
      "attribute": "client_milestone",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "reason": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": null,
      "relation": "unrelated",
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content",
      "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
      "new_position": {
        "start": 0,
        "end": 201
      },
      "subject": null,
      "attribute": "network_contact_effectiveness",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "reason": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "employer",
      "fact": "historical_employer",
      "relation": "change",
      "old_quote": "Blockchain Tech",
      "new_quote": "my consulting firm finally secured some initial clients",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 48,
        "end": 103
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": "Blockchain Tech",
      "new_value": null,
      "subject": null,
      "attribute": "employer",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "title",
      "fact": "historical_title",
      "relation": "change",
      "old_quote": "senior developer",
      "new_quote": "my consulting firm finally secured some initial clients",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 48,
        "end": 103
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": "senior developer",
      "new_value": null,
      "subject": null,
      "attribute": "title",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: exact title or role name in the consulting firm"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: exact title or role name in the consulting firm"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-0",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "new_position": {
        "start": 0,
        "end": 141
      },
      "status": "invalid",
      "new_error": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": null,
      "source_id": "new-2",
      "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
      "new_position": {
        "start": 0,
        "end": 201
      },
      "status": "invalid",
      "new_error": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Blockchain Tech",
      "source_id": "new-0",
      "new_quote": "my consulting firm finally secured some initial clients",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 48,
        "end": 103
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "senior developer",
      "source_id": "new-0",
      "new_quote": "my consulting firm finally secured some initial clients",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 48,
        "end": 103
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### career_history / v2

来源：`variants/evidence_aligner/runs/v2_paired_20261120/career_history.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": "Blockchain Tech",
        "attribute": "historical_employer",
        "statement": "user was employed by Blockchain Tech",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "consulting firm",
        "attribute": "current_activity",
        "statement": "user runs a consulting firm that secured initial clients",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "different",
      "change_type": "new_information",
      "old_quotes": [
        {
          "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
          "quote": "Blockchain Tech"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "The old claim states a past employer (Blockchain Tech); the new claim describes current entrepreneurial activity (own consulting firm securing clients). These are distinct roles — historical employment vs. current founder/operator status — with no textual indication that the prior role ended or was replaced, nor any identity link between 'Blockchain Tech' and 'consulting firm'. The new evidence introduces a new domain (political consulting), not a revision of the old employer.",
      "unknowns": [
        "start date of consulting firm",
        "end date of Blockchain Tech employment"
      ]
    },
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": "senior developer",
        "attribute": "historical_title",
        "statement": "user held the title of senior developer",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "consulting firm",
        "attribute": "current_role",
        "statement": "user is the founder/operator of a consulting firm",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "different",
      "change_type": "new_information",
      "old_quotes": [
        {
          "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
          "quote": "senior developer"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "The old claim specifies a historical job title ('senior developer'); the new claim implies a current role as head of a consulting firm. No statement in the new evidence denies or replaces the prior title, nor equates 'senior developer' with any current function. The two reflect different career stages and domains (technology employment vs. political consulting entrepreneurship) without overlap in subject-object-attribute alignment.",
      "unknowns": [
        "whether senior developer role has ended",
        "current formal title at consulting firm"
      ]
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "uncovered_unit",
      "path": "new_units",
      "message": "unsplit-new-2"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [
      "unsplit-new-2"
    ],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "employer",
    "relation": "unrelated",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "historical_employer",
    "new_attribute": "current_activity",
    "old_value": null,
    "new_value": null,
    "old_quote": "Blockchain Tech",
    "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "new_information",
    "upstream_target_relation": "different",
    "upstream_structure_errors": [
      {
        "code": "uncovered_unit",
        "path": "new_units",
        "message": "unsplit-new-2"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Blockchain Tech",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: start date of consulting firm",
      "model unknown: end date of Blockchain Tech employment"
    ]
  },
  {
    "unit_id": "title",
    "relation": "unrelated",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "historical_title",
    "new_attribute": "current_role",
    "old_value": null,
    "new_value": null,
    "old_quote": "senior developer",
    "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "new_information",
    "upstream_target_relation": "different",
    "upstream_structure_errors": [
      {
        "code": "uncovered_unit",
        "path": "new_units",
        "message": "unsplit-new-2"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "senior developer",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model unknown: whether senior developer role has ended",
      "model unknown: current formal title at consulting firm"
    ]
  },
  {
    "unit_id": null,
    "relation": "unknown",
    "old_quote": null,
    "new_quote": null,
    "source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "missing_reasons": [
      "upstream new unit unhandled or uncovered: unsplit-new-2"
    ],
    "upstream_coverage": true,
    "unhandled_new_unit_id": "unsplit-new-2"
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "unknown",
      "source_id": null,
      "source_ref": null,
      "new_quote": null,
      "new_position": null,
      "subject": null,
      "attribute": null,
      "value": null,
      "scope": null,
      "missing_reasons": [
        "upstream new unit unhandled or uncovered: unsplit-new-2"
      ],
      "reason": "evidence source missing or source id duplicated"
    },
    {
      "unit_id": "employer",
      "fact": "historical_employer",
      "relation": "unrelated",
      "old_quote": "Blockchain Tech",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 0,
        "end": 141
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "historical_employer",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: start date of consulting firm",
        "model unknown: end date of Blockchain Tech employment"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: start date of consulting firm; model unknown: end date of Blockchain Tech employment"
    },
    {
      "unit_id": "title",
      "fact": "historical_title",
      "relation": "unrelated",
      "old_quote": "senior developer",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 0,
        "end": 141
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "historical_title",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model unknown: whether senior developer role has ended",
        "model unknown: current formal title at consulting firm"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'uncovered_unit', 'path': 'new_units', 'message': 'unsplit-new-2'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model unknown: whether senior developer role has ended; model unknown: current formal title at consulting firm"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": null,
      "new_quote": null,
      "new_position": null,
      "status": "invalid",
      "new_error": "evidence source missing or source id duplicated"
    },
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Blockchain Tech",
      "source_id": "new-0",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 0,
        "end": 141
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "senior developer",
      "source_id": "new-0",
      "new_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 0,
        "end": 141
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### career_history / v3

来源：`variants/evidence_aligner/runs/v3_paired_20261120/career_history.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "employer"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "employer",
      "relation": "state_change",
      "old_quotes": [
        "Blockchain Tech"
      ],
      "new_quotes": [
        "my consulting firm"
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "time",
          "quote": "lately",
          "claim_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
        }
      ],
      "missing_evidence": []
    },
    {
      "old_unit_ids": [
        "title"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "title",
      "relation": "state_change",
      "old_quotes": [
        "senior developer"
      ],
      "new_quotes": [
        "consulting firm"
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "time",
          "quote": "lately",
          "claim_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."
        }
      ],
      "missing_evidence": []
    },
    {
      "old_unit_ids": [],
      "new_unit_ids": [
        "unsplit-new-2"
      ],
      "attribute": "network_support",
      "relation": "new_information",
      "old_quotes": [],
      "new_quotes": [
        "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."
      ],
      "qualifiers": [],
      "missing_evidence": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": [],
  "validation_errors": null,
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": [],
    "mentioned_old_unit_ids": [
      "employer",
      "title"
    ],
    "mentioned_new_unit_ids": [
      "manually_mapped_new",
      "unsplit-new-2"
    ]
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "employer",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "employer",
    "new_attribute": "employer",
    "old_value": null,
    "new_value": null,
    "old_quote": "Blockchain Tech",
    "new_quote": "my consulting firm",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Blockchain Tech",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "my consulting firm",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "title",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "title",
    "new_attribute": "title",
    "old_value": null,
    "new_value": null,
    "old_quote": "senior developer",
    "new_quote": "consulting firm",
    "source_id": "new-0",
    "old_quote_source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "senior developer",
        "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "consulting firm",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": null,
    "relation": "unrelated",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": null,
    "new_attribute": "network_support",
    "old_value": null,
    "new_value": null,
    "old_quote": null,
    "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
    "source_id": "new-2",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "new_information",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [],
    "resolved_new_quotes": [
      {
        "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "unrelated",
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content",
      "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
      "new_position": {
        "start": 0,
        "end": 201
      },
      "subject": null,
      "attribute": "network_support",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "reason": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "employer",
      "fact": "historical_employer",
      "relation": "change",
      "old_quote": "Blockchain Tech",
      "new_quote": "my consulting firm",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 48,
        "end": 66
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "employer",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "title",
      "fact": "historical_title",
      "relation": "change",
      "old_quote": "senior developer",
      "new_quote": "consulting firm",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 51,
        "end": 66
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "title",
      "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-2",
      "new_quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.",
      "new_position": {
        "start": 0,
        "end": 201
      },
      "status": "invalid",
      "new_error": "missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "employer",
      "alignment_index": 0,
      "old_quote": "Blockchain Tech",
      "source_id": "new-0",
      "new_quote": "my consulting firm",
      "old_position": {
        "start": 43,
        "end": 58
      },
      "new_position": {
        "start": 48,
        "end": 66
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "title",
      "alignment_index": 0,
      "old_quote": "senior developer",
      "source_id": "new-0",
      "new_quote": "consulting firm",
      "old_position": {
        "start": 23,
        "end": 39
      },
      "new_position": {
        "start": 51,
        "end": 66
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### skydiving / v1

来源：`variants/evidence_aligner/runs/fixed_five_20261120/skydiving.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "u1"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "attitude_toward_extreme_sports",
      "change_type": "state_change",
      "old_value": "dislikes",
      "new_claim": "tried simulated skydiving and found it thrilling",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        }
      ],
      "conditions": [],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "recently"
        }
      ],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "u2"
      ],
      "new_unit_ids": [
        "manually_mapped_new",
        "unsplit-new-2",
        "unsplit-new-8"
      ],
      "attribute": "reason_for_disliking_extreme_sports",
      "change_type": "state_change",
      "old_value": "high injury risk",
      "new_claim": "still prioritizes safety, but now enjoys the thrill and is more open to trying new things",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        },
        {
          "source_id": "new-2",
          "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."
        },
        {
          "source_id": "new-8",
          "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "conditions": [
        {
          "source_id": "new-8",
          "quote": "For now"
        }
      ],
      "time_expressions": [
        {
          "source_id": "new-0",
          "quote": "recently"
        }
      ],
      "event_date": null,
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "u3"
      ],
      "new_unit_ids": [
        "unsplit-new-8"
      ],
      "attribute": "commitment_to_safety_and_well_being",
      "change_type": "support",
      "old_value": "conflicts with commitment to safety and well-being",
      "new_claim": "still prioritizes safety, while enjoying the thrill",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-8",
          "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "conditions": [
        {
          "source_id": "new-8",
          "quote": "For now"
        }
      ],
      "time_expressions": [
        {
          "source_id": "new-8",
          "quote": "For now"
        }
      ],
      "event_date": null,
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "quote_provenance",
      "path": "records[0].old_quotes[0]",
      "message": "not an exact quote within a linked unit on the correct side"
    },
    {
      "code": "unit_without_quote",
      "path": "records[0].old_unit_ids",
      "message": "u1"
    },
    {
      "code": "quote_provenance",
      "path": "records[1].old_quotes[0]",
      "message": "not an exact quote within a linked unit on the correct side"
    },
    {
      "code": "unit_without_quote",
      "path": "records[1].old_unit_ids",
      "message": "u2"
    },
    {
      "code": "quote_provenance",
      "path": "records[2].old_quotes[0]",
      "message": "not an exact quote within a linked unit on the correct side"
    },
    {
      "code": "unit_without_quote",
      "path": "records[2].old_unit_ids",
      "message": "u3"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "u1",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "attitude_toward_extreme_sports",
    "new_attribute": "attitude_toward_extreme_sports",
    "old_value": "dislikes",
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
    "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "source_id": "new-0",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[0].old_quotes[0]",
        "message": "not an exact quote within a linked unit on the correct side"
      },
      {
        "code": "unit_without_quote",
        "path": "records[0].old_unit_ids",
        "message": "u1"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "source_id": null
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[0].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[0].old_unit_ids', 'message': 'u1'}",
      "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "u2",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "reason_for_disliking_extreme_sports",
    "new_attribute": "reason_for_disliking_extreme_sports",
    "old_value": "high injury risk",
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
    "new_quote": null,
    "source_id": null,
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[1].old_quotes[0]",
        "message": "not an exact quote within a linked unit on the correct side"
      },
      {
        "code": "unit_without_quote",
        "path": "records[1].old_unit_ids",
        "message": "u2"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "source_id": null
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      },
      {
        "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
        "source_id": "new-2"
      },
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[1].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].old_unit_ids', 'message': 'u2'}",
      "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "new side lacks a single uniquely represented quote",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "u3",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "commitment_to_safety_and_well_being",
    "new_attribute": "commitment_to_safety_and_well_being",
    "old_value": "conflicts with commitment to safety and well-being",
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
    "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "source_id": "new-8",
    "old_quote_source_id": null,
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v1",
    "upstream_relation": "support",
    "upstream_target_relation": null,
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[2].old_quotes[0]",
        "message": "not an exact quote within a linked unit on the correct side"
      },
      {
        "code": "unit_without_quote",
        "path": "records[2].old_unit_ids",
        "message": "u3"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "source_id": null
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'u3'}",
      "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "u1",
      "fact": "Dislikes extreme sports (e.g., skydiving)",
      "relation": "change",
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
      "old_value": "dislikes",
      "new_value": null,
      "subject": null,
      "attribute": "attitude_toward_extreme_sports",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[0].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[0].old_unit_ids', 'message': 'u1'}",
        "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "old quote is outside its designated unit"
    },
    {
      "unit_id": "u2",
      "fact": "Dislikes extreme sports due to high injury risk",
      "relation": "change",
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "new_quote": null,
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": null,
      "source_id": null,
      "source_ref": null,
      "old_value": "high injury risk",
      "new_value": null,
      "subject": null,
      "attribute": "reason_for_disliking_extreme_sports",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[1].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].old_unit_ids', 'message': 'u2'}",
        "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "new side lacks a single uniquely represented quote",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "old quote is outside its designated unit"
    },
    {
      "unit_id": "u3",
      "fact": "Dislikes extreme sports because it conflicts with commitment to safety and well-being",
      "relation": "unknown",
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "source_id": "new-8",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
      "old_value": "conflicts with commitment to safety and well-being",
      "new_value": null,
      "subject": null,
      "attribute": "commitment_to_safety_and_well_being",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].old_quotes[0]', 'message': 'not an exact quote within a linked unit on the correct side'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'u3'}",
        "old quote has missing, ambiguous, or mismatched linked-unit source: Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "old quote is outside its designated unit"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "u1",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "source_id": "new-0",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "status": "invalid",
      "old_error": "old quote is outside its designated unit",
      "new_error": null
    },
    {
      "unit_id": "u2",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "source_id": null,
      "new_quote": null,
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": null,
      "status": "invalid",
      "old_error": "old quote is outside its designated unit",
      "new_error": "evidence source missing or source id duplicated"
    },
    {
      "unit_id": "u3",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "source_id": "new-8",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 0,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "status": "invalid",
      "old_error": "old quote is outside its designated unit",
      "new_error": null
    }
  ]
}
```

### skydiving / v2

来源：`variants/evidence_aligner/runs/v2_paired_20261120/skydiving.json`；保存的 result.status=`failed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "u1"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "old_claim": {
        "subject": "user",
        "object": "extreme sports (e.g., skydiving)",
        "attribute": "attitude",
        "statement": "dislikes",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "simulated skydiving",
        "attribute": "experience",
        "statement": "tried and found thrilling",
        "qualifiers": [
          {
            "kind": "simulation",
            "source_id": "new-0",
            "quote": "simulated skydiving"
          }
        ],
        "event_date": null
      },
      "target_relation": "partially_overlapping",
      "change_type": "supplement",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving)"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-0",
          "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        }
      ],
      "change_evidence": [],
      "relation_explanation": "Old claim is about disliking real extreme sports (e.g., skydiving); new claim is about trying *simulated* skydiving and enjoying it. Simulation is a distinct activity type with different risk profile; enjoyment of simulation does not contradict dislike of actual skydiving. New evidence adds a qualified positive experience but does not override or negate the original attitude toward unqualified extreme sports.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "u2"
      ],
      "new_unit_ids": [
        "manually_mapped_new",
        "unsplit-new-2",
        "unsplit-new-8"
      ],
      "old_claim": {
        "subject": "user",
        "object": "extreme sports",
        "attribute": "reason_for_attitude",
        "statement": "dislikes due to high injury risk",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "simulated skydiving",
        "attribute": "risk_assessment",
        "statement": "still prioritizes safety",
        "qualifiers": [
          {
            "kind": "simulation",
            "source_id": "new-0",
            "quote": "simulated skydiving"
          }
        ],
        "event_date": null
      },
      "target_relation": "partially_overlapping",
      "change_type": "support",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-8",
          "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "change_evidence": [
        "I still prioritize safety, of course."
      ],
      "relation_explanation": "Old claim identifies high injury risk as the reason for disliking extreme sports. New claim affirms continued prioritization of safety — consistent with the original rationale — while engaging in a *simulated* version. The new evidence supports the enduring validity of the safety concern (i.e., it remains operative), rather than invalidating it. No claim is made that injury risk is absent or irrelevant for real skydiving.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "u3"
      ],
      "new_unit_ids": [
        "unsplit-new-8"
      ],
      "old_claim": {
        "subject": "user",
        "object": "extreme sports",
        "attribute": "reason_for_attitude",
        "statement": "dislikes because it conflicts with commitment to safety and well-being",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": "simulated skydiving",
        "attribute": "attitude_toward_safety",
        "statement": "prioritizes safety",
        "qualifiers": [
          {
            "kind": "simulation",
            "source_id": "new-0",
            "quote": "simulated skydiving"
          }
        ],
        "event_date": null
      },
      "target_relation": "partially_overlapping",
      "change_type": "support",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "conflicting with commitment to safety and well-being"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-8",
          "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "change_evidence": [
        "I still prioritize safety, of course."
      ],
      "relation_explanation": "Old claim grounds dislike in a conflict with commitment to safety and well-being. New claim explicitly reaffirms that commitment ('I still prioritize safety, of course'), indicating continuity of the core value. The new activity is simulated — thus not inherently conflicting — and the affirmation of safety priority supports, rather than contradicts, the original reasoning framework.",
      "unknowns": []
    },
    {
      "old_unit_ids": [
        "u1",
        "u2",
        "u3"
      ],
      "new_unit_ids": [
        "unsplit-new-2"
      ],
      "old_claim": {
        "subject": "user",
        "object": "extreme sports",
        "attribute": "attitude",
        "statement": "dislikes",
        "qualifiers": [],
        "event_date": null
      },
      "new_claim": {
        "subject": "user",
        "object": null,
        "attribute": "openness_to_experience",
        "statement": "more open to trying new things",
        "qualifiers": [],
        "event_date": null
      },
      "target_relation": "different",
      "change_type": "supplement",
      "old_quotes": [
        {
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving)"
        }
      ],
      "new_quotes": [
        {
          "source_id": "new-2",
          "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."
        }
      ],
      "change_evidence": [],
      "relation_explanation": "Old claims are specific to extreme sports and their perceived risks. New claim expresses a general increase in openness to trying *new things*, which is a broader dispositional shift — not a direct reversal of the specific dislike. It does not state or imply revised attitude toward real extreme sports, nor does it retract the prior reasons. Thus, it supplements rather than changes the old claims.",
      "unknowns": []
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": null,
  "validation_errors": [
    {
      "code": "unit_without_quote",
      "path": "records[1].new_unit_ids",
      "message": "manually_mapped_new"
    },
    {
      "code": "unit_without_quote",
      "path": "records[1].new_unit_ids",
      "message": "unsplit-new-2"
    },
    {
      "code": "schema",
      "path": "records[1].change_evidence[0]",
      "message": "source_id and quote required"
    },
    {
      "code": "change_evidence_not_in_new_quote",
      "path": "records[1].change_evidence[0]",
      "message": "must be within a cited new quote"
    },
    {
      "code": "quote_provenance",
      "path": "records[2].new_claim.qualifiers[0]",
      "message": "quote not found in the linked source/units on the correct side"
    },
    {
      "code": "schema",
      "path": "records[2].change_evidence[0]",
      "message": "source_id and quote required"
    },
    {
      "code": "change_evidence_not_in_new_quote",
      "path": "records[2].change_evidence[0]",
      "message": "must be within a cited new quote"
    },
    {
      "code": "unit_without_quote",
      "path": "records[3].old_unit_ids",
      "message": "u3"
    }
  ],
  "coverage": {
    "uncovered_old_unit_ids": [],
    "uncovered_new_unit_ids": [],
    "unmatched_old_unit_ids": []
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "u1",
    "relation": "supplement",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "attitude",
    "new_attribute": "experience",
    "old_value": null,
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving)",
    "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "source_id": "new-0",
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "supplement",
    "upstream_target_relation": "partially_overlapping",
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving)",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "u2",
    "relation": "unknown",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "reason_for_attitude",
    "new_attribute": "risk_assessment",
    "old_value": null,
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
    "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "source_id": "new-8",
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "support",
    "upstream_target_relation": "partially_overlapping",
    "upstream_structure_errors": [
      {
        "code": "unit_without_quote",
        "path": "records[1].new_unit_ids",
        "message": "manually_mapped_new"
      },
      {
        "code": "unit_without_quote",
        "path": "records[1].new_unit_ids",
        "message": "unsplit-new-2"
      },
      {
        "code": "schema",
        "path": "records[1].change_evidence[0]",
        "message": "source_id and quote required"
      },
      {
        "code": "change_evidence_not_in_new_quote",
        "path": "records[1].change_evidence[0]",
        "message": "must be within a cited new quote"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'manually_mapped_new'}",
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'unsplit-new-2'}",
      "upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}",
      "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": "u3",
    "relation": "unknown",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "reason_for_attitude",
    "new_attribute": "attitude_toward_safety",
    "old_value": null,
    "new_value": null,
    "old_quote": "conflicting with commitment to safety and well-being",
    "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
    "source_id": "new-8",
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "support",
    "upstream_target_relation": "partially_overlapping",
    "upstream_structure_errors": [
      {
        "code": "quote_provenance",
        "path": "records[2].new_claim.qualifiers[0]",
        "message": "quote not found in the linked source/units on the correct side"
      },
      {
        "code": "schema",
        "path": "records[2].change_evidence[0]",
        "message": "source_id and quote required"
      },
      {
        "code": "change_evidence_not_in_new_quote",
        "path": "records[2].change_evidence[0]",
        "message": "must be within a cited new quote"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "conflicting with commitment to safety and well-being",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].new_claim.qualifiers[0]', 'message': 'quote not found in the linked source/units on the correct side'}",
      "upstream validation error: {'code': 'schema', 'path': 'records[2].change_evidence[0]', 'message': 'source_id and quote required'}",
      "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[2].change_evidence[0]', 'message': 'must be within a cited new quote'}",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  },
  {
    "unit_id": null,
    "relation": "supplement",
    "old_subject": "user",
    "new_subject": "user",
    "old_attribute": "attitude",
    "new_attribute": "openness_to_experience",
    "old_value": null,
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving)",
    "new_quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
    "source_id": "new-2",
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v2",
    "upstream_relation": "supplement",
    "upstream_target_relation": "different",
    "upstream_structure_errors": [
      {
        "code": "unit_without_quote",
        "path": "records[3].old_unit_ids",
        "message": "u3"
      }
    ],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving)",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
        "source_id": "new-2"
      }
    ],
    "missing_reasons": [
      "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[3].old_unit_ids', 'message': 'u3'}",
      "multiple old unit IDs; no unique unit binding",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": null,
      "relation": "supplement",
      "source_id": "new-2",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content",
      "new_quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
      "new_position": {
        "start": 0,
        "end": 129
      },
      "subject": "user",
      "attribute": "openness_to_experience",
      "value": null,
      "scope": null,
      "missing_reasons": [
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[3].old_unit_ids', 'message': 'u3'}",
        "multiple old unit IDs; no unique unit binding",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "reason": "missing upstream information: upstream validation error: {'code': 'unit_without_quote', 'path': 'records[3].old_unit_ids', 'message': 'u3'}; multiple old unit IDs; no unique unit binding; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "u1",
      "fact": "Dislikes extreme sports (e.g., skydiving)",
      "relation": "supplement",
      "old_quote": "Dislikes extreme sports (e.g., skydiving)",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 41
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "attitude",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "u2",
      "fact": "Dislikes extreme sports due to high injury risk",
      "relation": "unknown",
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 0,
        "end": 65
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "source_id": "new-8",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "reason_for_attitude",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'manually_mapped_new'}",
        "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'unsplit-new-2'}",
        "upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}",
        "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'manually_mapped_new'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[1].new_unit_ids', 'message': 'unsplit-new-2'}; upstream validation error: {'code': 'schema', 'path': 'records[1].change_evidence[0]', 'message': 'source_id and quote required'}; upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[1].change_evidence[0]', 'message': 'must be within a cited new quote'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "u3",
      "fact": "Dislikes extreme sports because it conflicts with commitment to safety and well-being",
      "relation": "unknown",
      "old_quote": "conflicting with commitment to safety and well-being",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 67,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "source_id": "new-8",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content",
      "old_value": null,
      "new_value": null,
      "subject": "user",
      "attribute": "reason_for_attitude",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].new_claim.qualifiers[0]', 'message': 'quote not found in the linked source/units on the correct side'}",
        "upstream validation error: {'code': 'schema', 'path': 'records[2].change_evidence[0]', 'message': 'source_id and quote required'}",
        "upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[2].change_evidence[0]', 'message': 'must be within a cited new quote'}",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: upstream validation error: {'code': 'quote_provenance', 'path': 'records[2].new_claim.qualifiers[0]', 'message': 'quote not found in the linked source/units on the correct side'}; upstream validation error: {'code': 'schema', 'path': 'records[2].change_evidence[0]', 'message': 'source_id and quote required'}; upstream validation error: {'code': 'change_evidence_not_in_new_quote', 'path': 'records[2].change_evidence[0]', 'message': 'must be within a cited new quote'}; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": null,
      "source_id": "new-2",
      "new_quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
      "new_position": {
        "start": 0,
        "end": 129
      },
      "status": "invalid",
      "new_error": "missing upstream information: upstream validation error: {'code': 'unit_without_quote', 'path': 'records[3].old_unit_ids', 'message': 'u3'}; multiple old unit IDs; no unique unit binding; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"
    },
    {
      "unit_id": "u1",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving)",
      "source_id": "new-0",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 41
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "u2",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
      "source_id": "new-8",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 0,
        "end": 65
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "u3",
      "alignment_index": 0,
      "old_quote": "conflicting with commitment to safety and well-being",
      "source_id": "new-8",
      "new_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
      "old_position": {
        "start": 67,
        "end": 119
      },
      "new_position": {
        "start": 0,
        "end": 105
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    }
  ]
}
```

### skydiving / v3

来源：`variants/evidence_aligner/runs/v3_paired_20261120/skydiving.json`；保存的 result.status=`passed`。

**模型 parsed 全部记录和校验元数据**

```json
{
  "records": [
    {
      "old_unit_ids": [
        "u1"
      ],
      "new_unit_ids": [
        "manually_mapped_new"
      ],
      "attribute": "attitude_toward_extreme_sports",
      "relation": "state_change",
      "old_quotes": [
        "Dislikes extreme sports (e.g., skydiving)"
      ],
      "new_quotes": [
        "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "simulation",
          "quote": "simulated",
          "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        },
        {
          "side": "new",
          "kind": "time",
          "quote": "recently",
          "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        }
      ],
      "missing_evidence": [
        "No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"
      ]
    },
    {
      "old_unit_ids": [
        "u2"
      ],
      "new_unit_ids": [
        "manually_mapped_new",
        "unsplit-new-2",
        "unsplit-new-8"
      ],
      "attribute": "reason_for_disliking_extreme_sports",
      "relation": "state_change",
      "old_quotes": [
        "Dislikes extreme sports (e.g., skydiving) due to high injury risk"
      ],
      "new_quotes": [
        "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
        "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "simulation",
          "quote": "simulated",
          "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        },
        {
          "side": "new",
          "kind": "time",
          "quote": "recently",
          "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        },
        {
          "side": "new",
          "kind": "plan",
          "quote": "For now",
          "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        },
        {
          "side": "new",
          "kind": "negation",
          "quote": "still prioritize safety",
          "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "missing_evidence": [
        "No statement retracting or qualifying that high injury risk *itself* is no longer a reason for dislike; 'still prioritize safety' affirms the original safety concern remains operative; 'simulated' explicitly limits scope — no evidence about real skydiving risk perception change"
      ]
    },
    {
      "old_unit_ids": [
        "u3"
      ],
      "new_unit_ids": [
        "manually_mapped_new",
        "unsplit-new-8"
      ],
      "attribute": "safety_commitment_conflict_with_extreme_sports",
      "relation": "no_clear_change",
      "old_quotes": [
        "conflicting with commitment to safety and well-being"
      ],
      "new_quotes": [
        "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
      ],
      "qualifiers": [
        {
          "side": "new",
          "kind": "simulation",
          "quote": "simulated",
          "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"
        },
        {
          "side": "new",
          "kind": "plan",
          "quote": "For now",
          "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        },
        {
          "side": "new",
          "kind": "negation",
          "quote": "still prioritize safety",
          "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."
        }
      ],
      "missing_evidence": [
        "No evidence that simulated skydiving resolves or negates the conflict with safety commitment; 'still prioritize safety' confirms the commitment remains intact and unconflicted *by this activity* — but does not address whether real extreme sports would still conflict"
      ]
    }
  ],
  "unmatched_old_unit_ids": [],
  "parse_errors": [],
  "structure_errors": [],
  "validation_errors": null,
  "coverage": {
    "unhandled_old_unit_ids": [],
    "unhandled_new_unit_ids": [],
    "unmatched_old_unit_ids": [],
    "mentioned_old_unit_ids": [
      "u1",
      "u2",
      "u3"
    ],
    "mentioned_new_unit_ids": [
      "manually_mapped_new",
      "unsplit-new-2",
      "unsplit-new-8"
    ]
  }
}
```

**适配输出**（省略 `raw_record` 的重复副本，上一块为其原始完整内容）

```json
[
  {
    "unit_id": "u1",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "attitude_toward_extreme_sports",
    "new_attribute": "attitude_toward_extreme_sports",
    "old_value": null,
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving)",
    "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
    "source_id": "new-0",
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving)",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      }
    ],
    "missing_reasons": [
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model missing evidence: No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"
    ]
  },
  {
    "unit_id": "u2",
    "relation": "change",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "reason_for_disliking_extreme_sports",
    "new_attribute": "reason_for_disliking_extreme_sports",
    "old_value": null,
    "new_value": null,
    "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
    "new_quote": null,
    "source_id": null,
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "state_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      },
      {
        "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.",
        "source_id": "new-2"
      },
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "new side lacks a single uniquely represented quote",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model missing evidence: No statement retracting or qualifying that high injury risk *itself* is no longer a reason for dislike; 'still prioritize safety' affirms the original safety concern remains operative; 'simulated' explicitly limits scope — no evidence about real skydiving risk perception change"
    ]
  },
  {
    "unit_id": "u3",
    "relation": "unknown",
    "old_subject": null,
    "new_subject": null,
    "old_attribute": "safety_commitment_conflict_with_extreme_sports",
    "new_attribute": "safety_commitment_conflict_with_extreme_sports",
    "old_value": null,
    "new_value": null,
    "old_quote": "conflicting with commitment to safety and well-being",
    "new_quote": null,
    "source_id": null,
    "old_quote_source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
    "old_conditions": null,
    "new_conditions": null,
    "upstream_version": "v3",
    "upstream_relation": "no_clear_change",
    "upstream_target_relation": null,
    "upstream_structure_errors": [],
    "resolved_old_quotes": [
      {
        "quote": "conflicting with commitment to safety and well-being",
        "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03"
      }
    ],
    "resolved_new_quotes": [
      {
        "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
        "source_id": "new-0"
      },
      {
        "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.",
        "source_id": "new-8"
      }
    ],
    "missing_reasons": [
      "new side lacks a single uniquely represented quote",
      "not explicitly supplied as old_subject",
      "not explicitly supplied as new_subject",
      "not explicitly supplied as old_value",
      "not explicitly supplied as new_value",
      "old_conditions not explicitly normalized",
      "new_conditions not explicitly normalized",
      "model missing evidence: No evidence that simulated skydiving resolves or negates the conflict with safety commitment; 'still prioritize safety' confirms the commitment remains intact and unconflicted *by this activity* — but does not address whether real extreme sports would still conflict"
    ]
  }
]
```

**规划器实际输出**（包含全部最终理由与引文检查）

```json
{
  "modify": [],
  "preserve": [],
  "uncertain": [
    {
      "unit_id": "u1",
      "fact": "Dislikes extreme sports (e.g., skydiving)",
      "relation": "change",
      "old_quote": "Dislikes extreme sports (e.g., skydiving)",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 41
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "source_id": "new-0",
      "source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content",
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "attitude_toward_extreme_sports",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model missing evidence: No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"
      ],
      "note": null,
      "time_note": null,
      "reason": "missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model missing evidence: No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"
    },
    {
      "unit_id": "u2",
      "fact": "Dislikes extreme sports due to high injury risk",
      "relation": "change",
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
      "new_quote": null,
      "old_position": {
        "start": 0,
        "end": 65
      },
      "new_position": null,
      "source_id": null,
      "source_ref": null,
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "reason_for_disliking_extreme_sports",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "new side lacks a single uniquely represented quote",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model missing evidence: No statement retracting or qualifying that high injury risk *itself* is no longer a reason for dislike; 'still prioritize safety' affirms the original safety concern remains operative; 'simulated' explicitly limits scope — no evidence about real skydiving risk perception change"
      ],
      "note": null,
      "time_note": null,
      "reason": "evidence source missing or source id duplicated"
    },
    {
      "unit_id": "u3",
      "fact": "Dislikes extreme sports because it conflicts with commitment to safety and well-being",
      "relation": "unknown",
      "old_quote": "conflicting with commitment to safety and well-being",
      "new_quote": null,
      "old_position": {
        "start": 67,
        "end": 119
      },
      "new_position": null,
      "source_id": null,
      "source_ref": null,
      "old_value": null,
      "new_value": null,
      "subject": null,
      "attribute": "safety_commitment_conflict_with_extreme_sports",
      "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "old_source_ref": "results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json",
      "missing_reasons": [
        "new side lacks a single uniquely represented quote",
        "not explicitly supplied as old_subject",
        "not explicitly supplied as new_subject",
        "not explicitly supplied as old_value",
        "not explicitly supplied as new_value",
        "old_conditions not explicitly normalized",
        "new_conditions not explicitly normalized",
        "model missing evidence: No evidence that simulated skydiving resolves or negates the conflict with safety commitment; 'still prioritize safety' confirms the commitment remains intact and unconflicted *by this activity* — but does not address whether real extreme sports would still conflict"
      ],
      "note": null,
      "time_note": null,
      "reason": "evidence source missing or source id duplicated"
    }
  ],
  "add": [],
  "editable_spans": [],
  "protected_facts": [],
  "quote_checks": [
    {
      "unit_id": "u1",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving)",
      "source_id": "new-0",
      "new_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!",
      "old_position": {
        "start": 0,
        "end": 41
      },
      "new_position": {
        "start": 0,
        "end": 129
      },
      "status": "valid",
      "old_error": null,
      "new_error": null
    },
    {
      "unit_id": "u2",
      "alignment_index": 0,
      "old_quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk",
      "source_id": null,
      "new_quote": null,
      "old_position": {
        "start": 0,
        "end": 65
      },
      "new_position": null,
      "status": "invalid",
      "old_error": null,
      "new_error": "evidence source missing or source id duplicated"
    },
    {
      "unit_id": "u3",
      "alignment_index": 0,
      "old_quote": "conflicting with commitment to safety and well-being",
      "source_id": null,
      "new_quote": null,
      "old_position": {
        "start": 67,
        "end": 119
      },
      "new_position": null,
      "status": "invalid",
      "old_error": null,
      "new_error": "evidence source missing or source id duplicated"
    }
  ]
}
```

