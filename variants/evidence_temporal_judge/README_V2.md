# 证据与时间区间判断 v2（离线原型）

v2 位于 `judge_v2.py`，v1 的 `judge.py`、默认入口和既有 `runs/` 均保留。v1 将时间关系交给单事实判断 backend；v2 先使用相同的 v4 拆分与 ERASE 式逐事实影响判断，再实际执行“有效范围确定 → 候选阻断 → 区间/事实对冲突检查 → 区间调整候选”。详细来源、调用链、模型可用性和授权状态见 [PROVENANCE_V2.md](PROVENANCE_V2.md)。只返回候选，不改 Mem0、事实、来源或输入对象。

## 调用

```python
import judge_v2
result = judge_v2.split_and_judge(
    request, new_evidence, time_info,
    splitter_backend_factory, fact_backend, candidate_backend, nli_backend,
    time_verifier=time_verifier,
)
# 如果已经有拆分结果（无法证明来自 v4），也可调用：
result = judge_v2.judge(split_result, source_context, new_evidence, time_info,
                        fact_backend, candidate_backend, nli_backend,
                        time_verifier=time_verifier)
```

前六个参数、拆分结构、逐字引文验证和 backend 格式与 [v1](README.md) 一致。`split_and_judge` 直接调用 v1 的 `split_with_v4`，显式读取 `variants/dnd_mem0_splitter/prompt_versions/v4_boundaries_20261104/prompt.txt`，结果记录运行时的绝对路径与实际字节 SHA-256；低层 `judge` 不会伪称传入事实由 v4 产生。事实 ID 来自输入的真实 `memory_id`，示例使用合成 ID。拆分、事实影响、新增候选和 NLI 均由调用者注入；此模块没有真实模型客户端。

`time_info` 是调用方**已有且有出处的事件时间声明**，不是自动抽取器；`null` 表示没有时间信息：

```json
{
  "facts": {
    "1": {"start": {"value":"2020-01-01","precision":"day"}, "end": null,
          "basis": {"source_type":"memory", "source_id":"synthetic-m1", "quote":"2020年1月1日起住在北京"}}
  },
  "sources": {
    "synthetic-new1": {"start":{"value":"2023-01-01","precision":"day"}, "end":null,
      "kind":"actual", "basis":{"source_id":"synthetic-new1", "quote":"2023年1月1日搬到上海"},
      "recorded_at":"2023-03-01"}
  },
  "transitions": [{"fact_index":1, "source_id":"synthetic-new1", "quote":"2023年1月1日搬到上海",
                   "at":{"value":"2023-01-01","precision":"day"}, "kind":"actual"}]
}
```

`facts` 以 v4 的 `fact_index` 字符串为键，`sources` 以来源 ID 为键。`basis` 必须逐字属于该事实的旧证据或相应新来源；新来源可携带并保留 `recorded_at`，它不参与区间计算。`transitions` 中每项是调用者声明**该新来源的实际事件直接阻断指定旧事实受影响片段**，并提供原文和事件边界；不是仅声明两个事件先后。也支持单个 `transition` 字段，二者均有时合并。程序验证引文归属和日期文本精度，日期、活动性质、状态变更是否真的由引文支持需要另行语义评估。上面的结构必须和示例脚本中的原文一起使用，不能把无日期的引文当成已证明日期。

### 时间依据的三项检查

每个非空的旧/新起点和终点、以及相关的实际转换时间，都分别记录在 `facts[*].time_checks` 中：

- `quote_status`：`matched` 表示引文属于指定来源（旧时间依据还必须属于该事实的已有引文），`invalid` 表示不匹配。旧时间可以来自该事实已有证据中的上下文来源。
- `precision_status`：`matched` 表示引文中出现了与声明精度相符的日期文本，`insufficient` 表示没有。它只支持常见的 `YYYY`、`YYYY-MM`、`YYYY-MM-DD` 及阿拉伯数字的中文年月日格式；精确日期可支持较粗的年月声明。相对时间、其他日期格式、独立锚点推算和缺少日期文本的引文会保守地标为依据不足。日期文本属于记录时间还是事件时间，不能通过这项检查确定。
- `semantic_status`：`time_verifier` 对日期是否属于**该事实的指定事件或边界**的外部评估，取 `supported`、`not_supported`、`uncertain`；未注入为 `not_checked`，异常或无效响应为 `failed`。其 `semantic_reason` 是评估者提供的理由，不是程序核实的事实。

可选 `time_verifier(payload)` 接收 `task: "time_support"`、`role`（`old_start`、`old_end`、`new_start`、`new_end`、`transition`）、`boundary`、`basis`、完整 `source` 和旧 `fact`，返回 `{"status":"supported", "reason":"..."}` 或上述其他状态。调用方必须提供独立的人工或模型语义评估，核实日期所属事件、记录时间、事实片段及转换关系。程序不内置语义识别器；注入评估也可能出错，不能当成已证明的真相。离线示例的评估是手写模拟响应。**不传 verifier 时默认 `not_checked`：有明确日历文本也只输出待确认，不产生需要该时间依据的区间结论或日精度调整。**

当一项非空时间声明的引文、精度或语义评估不满足要求时，结果保留原声明与检查详情、将修改候选降为 `confirm`，不把该声明用于范围结论；评估器异常为 `failed`，不暴露异常内容。输入中的未知边界仍为未知，不会因为检查通过而补全。一个较早的年份级转换如果可能阻断旧状态，也会阻止选择后来的具体日作为确定的最近阻断点。

每个边界使用 `year`、`month`、`day` 精度，格式分别为 `YYYY`、`YYYY-MM`、`YYYY-MM-DD`，未知用 `null`。输入的明确边界为包含端点；粗精度表示边界位置可能落在该年/月任一天，不是人为补齐成精确时间。只有能从端点范围确定不重叠或必然重叠时才下相应关系；未知边界不等于无限远。可以在部分边界未知时，仅凭已知旧终点和新起点确认不重叠。涉及区间判断的是事件有效期，不是来源的发表、采集或记录时间；无法确定时必须留空。转换阻断只接受日精度、实际活动、同一被引用来源、匹配 `fact_index`，并且旧起点确定、新起点不早于该事件。多个符合条件的声明选旧起点之后最早的阻断；它是候选，不会更新任何事实。旧终点候选采用排他边界，避免故事索引 epsilon 与自然日换算。

`nli_backend(payload)` 返回例如 `{"relation":"contradiction", "score":0.93}`，`relation` 可为 `contradiction`、`compatible` 或 `uncertain`，可选 `score` 为 0–1；分数不会阈值化为结论。`payload` 是事实、完整被选新来源、原始逐事实影响候选。分数和关系仅供辅助，候选冲突还要求 `Make False`、涉及证据、实际活动和确定的重叠；状态转变还需模型候选 `before_after` 与引用支持的转换声明。NLI 的 `compatible` 也不会独自证明相容。异常或格式错误标记 `failed`，保留旧事实与确认候选，不返回异常内容。此处的关联和语义是注入者声明，不经过人工审核；分数绝不证明旧事实已失效。

一次仅在逐事实影响结果引用**恰好一个**新来源时比较其范围；没有引文或引用多个来源时保守待确认，多个来源不能自动合并。活动标记为 `simulation` 或 `unknown` 时不视为真实状态变化。没有明确事件时间、存在精度歧义、NLI 不确定或影响不足时，修改降级为待确认；其他未涉及片段可同时保护。若区间明确不重叠，保留旧事实，不提出截断。当前不单独表达旧事实的假设/虚构性质、复杂周期/时区/时刻、多个来源联合推断或通用静态事实持久性；也不会从对话中自动推断这些信息。输入日期归一化及其依据必须由上游提供。

## 输出和离线示例

每个结果保留原始 `fact.evidence`、新来源、完整 `time_info`、分片的 `modify`/`protect`/`confirm`、原始 `impact_judgment`、`time_checks`、`intervals`、`interval_relation`、NLI 返回值、时间结论、理由及 `interval_adjustments`。新增候选在 `new_candidates`。`path` 列出该事实实际到达的适配流程阶段；为空可表示逐事实 backend 已失败或未涉及。阶段名不是作者代码运行记录。

```bash
python variants/evidence_temporal_judge/examples/v2_offline.py
python -m unittest discover -s variants/evidence_temporal_judge -p 'test_*.py' -v
```

示例是手写的合成 v4 响应、影响响应、模拟 NLI 和模拟时间语义评估，不读取真实数据。输出要点如下（完整输入和输出均由脚本给出）：

```json
{
  "memory_id":"synthetic-m1",
  "temporal_relation":"before_after",
  "components":[{"fragment":"小李从2020年1月1日起住在北京","action":"modify"},
                {"fragment":"喜欢茶","action":"protect"}],
  "interval_adjustments":[{"fragments":["小李从2020年1月1日起住在北京"],
    "proposed_end":{"value":"2023-01-01","precision":"day","inclusive":false},
    "basis":{"source_id":"synthetic-new1","quote":"2023年1月1日搬到上海"}}],
  "new_candidates":{"status":"ok","candidates":[{"source_id":"synthetic-new1","quote":"现在住在上海","reason":"新的住址候选"}]}
}
```

以上是为阅读抽取的字段：实际 `temporal_relation`、`components` 和 `interval_adjustments` 在 `facts[0]` 内。这里的 `modify` 是局部复核候选，历史记忆仍然保留；不是自动改写指令。
