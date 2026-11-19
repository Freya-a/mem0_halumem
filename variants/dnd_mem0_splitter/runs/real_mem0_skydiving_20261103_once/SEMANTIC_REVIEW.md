# 一条真实 Mem0 旧记忆的拆分测试

日期：2026-11-03（Asia/Shanghai）。本次复用已有 `run_real.py`、`real_backend.py`、`splitter.py` 和 `DESIGN.md` 提示词，没有修改拆分器实现。

结果：qwen-plus 实际调用 1 次，重试 0 次，退出码 0，返回 2 条子事实；程序格式、ID 和逐字引文检查通过。人工初审未发现明确漏掉的旧命题或凭空新增的独立事实，但第 2 条的语气、粒度及 raw 中补回主语的边界仍需确认。程序通过不等于语义完全正确。

## 1. 选中的真实旧记忆与来源

真实 memory_id：`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`。

原始文本（逐字保留）：

> Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

本次所说的真实记忆，是既有真实 Mem0 原生开发运行中已落盘的记录；本次没有连接 Mem0 查询或修改在线状态。

来源运行：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/`。

来源用户目录：`users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/`。以下位置均相对此用户目录，JSON Pointer 使用从 0 开始的数组下标。

| 核对位置 | 具体位置与结果 |
| --- | --- |
| 目标会话处理前的 Mem0 API 快照 | `session_009/before.json#/api_snapshot/results/100`：ID、完整原文、user_id 对应 |
| 同一快照的底层数据库记录 | `session_009/before.json#/database_points_with_vectors/100`：id 与 payload.data、payload.user_id 对应 |
| 前一会话结束快照 | `session_008/after.json`：同 ID 的完整 API 记录与目标 before 一致 |
| 早期生成会话的结束快照 | `session_003/after.json`：同 ID、同原文；`session_003/before.json` 中尚无此 ID |
| 实际生成返回 | `session_003/add_return.json#/return_value/results/4`：同 ID、同原文，event=ADD |
| 实际生成操作记录 | `session_003/actual_operations.json#/4`：memory_id 对应，new_memory 相同，event=ADD |
| 生成时抽取文本 | `session_003/extracted_facts.json#/0/parsed/facts/4`：与旧记忆文本逐字一致 |

目标 before 标记 `not_truncated=true`，API 和底层数据库记录均为 116 条，与精确计数一致。仅选取上述 1 条记忆传给模型，没有传入整个快照或其他旧记忆。

快照的先后含义还通过静态读取 `scripts/medium_dev_run.py` 确认：第 215 行保存 before，第 231 行才调用 memory.add；本次没有执行该脚本。前一会话 after 中同一记录的一致性，进一步支持它在目标会话处理前已经存在。目标定位 ID 为 `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008:m000`，只用于来源定位，没有作为额外字段传给模型。

来源明细和完整旧记录见 [provenance.json](provenance.json)，来源文件及原有实现、历史运行文件的 SHA-256 基线见 [source_integrity.before.json](source_integrity.before.json)。

## 2. 实际模型输入及单次调用

完整模型数据输入见 [input.json](input.json)。除选中的 ID 和旧文本，仅补入一段可靠关联的旧来源发言：

> I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.

来源：上述用户目录的 `session_003/input.json#/raw_dialogue/6/content`，只取字符 `[0, 169)`，为该发言前两句。原始 role 为 `user`，dialogue_turn 为 3，原始 timestamp 为 `Sep 06, 2025, 22:52:30`。时间未附时区，未推定时区。speaker 字段只保留 `user`，未补入姓名。

该上下文用于澄清省略的主体及“风险与自身安全、健康承诺相冲突”的归属。关联依据是同一用户同一生成会话的输入、精确抽取文本、实际 ADD 返回和操作、后续快照链，不只依据文本相似。后面的拳击、摔跤等内容均未发送。

原发言时间早于目标会话开始时间 `Apr 10, 2026, 10:40:32`；后者只用于本地核对先后，没有传入模型。Mem0 的 created_at 是运行处理时间，不作为原始发言时间。

system 消息逐字使用 `DESIGN.md` 唯一的 text 代码块，保存在 [prompt.txt](prompt.txt)。user 消息仅为 input.json 对应对象。未向模型传入目标新证据、更新后的记忆、人工标注、标准答案或本报告。

已执行命令（临时输入现已清理，原内容保存在 input.json）：

```bash
python3 -B run_real.py --input runs/.real_mem0_skydiving_20261103_once_preflight/input.json --run-dir runs/real_mem0_skydiving_20261103_once
```

沿用项目 `.env.local` 和现有进程覆盖规则读取配置，未输出密钥或完整环境变量。配置模型与返回模型均为 qwen-plus；SDK `max_retries=0`，HTTP 重定向关闭；实际 create 尝试 1 次，无模型探测、纠错请求或自动重试。

`finish_reason=stop`；服务返回 token 记账为 prompt 1215、completion 711、total 1926。这些数字不是质量评分。元信息见 [attempt.json](attempt.json)、[response_metadata.json](response_metadata.json)、[report.json](report.json)。

## 3. 实际拆分结果

以下均为模型实际输出，没有人工改写；原始响应见 [raw_content.txt](raw_content.txt)，通过程序校验后的结果见 [result.json](result.json)。fact_index 仅为本次序号，不是新 Mem0 ID。

### 子事实 1

raw_subfact：

> Dislikes extreme sports (e.g., skydiving) due to high injury risk.

contextualized_subfact：

> The speaker dislikes extreme sports (such as skydiving) because they carry a high risk of injury.

### 子事实 2

raw_subfact：

> The high injury risk of extreme sports conflicts with the speaker's commitment to safety and well-being.

contextualized_subfact：

> The speaker holds a commitment to safety and well-being, and perceives the high injury risk of extreme sports as conflicting with that commitment.

两条的 source_memory_id 均为选中的真实 ID。每条都有 1 条 memory 引文和 1 条 context 引文。两条模型返回的 pending_confirmations 均为 `[]`；这不替代下方人工待确认项。

## 4. 程序检查结果

真实入口校验通过后，又在本地将 raw_content.txt 交给既有 `split_memory(..., MockBackend(...))` 离线复核；没有再次使用真实后端或发起模型请求。

| 检查 | 实际结果 |
| --- | --- |
| 严格 JSON、重复键、字段结构、类型、必填及未知字段 | 通过既有校验器 |
| 顶层 ID 和完整原文 | 与输入逐字一致 |
| 两条 source_memory_id、所有 memory evidence.source_id | 均与输入真实 ID 一致 |
| fact_index | 连续整数 1、2 |
| 每条至少有 memory 依据 | 2/2 通过 |
| context 来源编号 | 均为输入存在的 ctx-old-sports-utterance |
| 逐字引文 | 4/4 是所声明来源中的非空连续子串 |
| 保存结果与原始响应重新校验结果 | 完全一致 |
| 提示词 | 与现有 DESIGN.md 的提示词逐字一致，SHA-256 对应 |
| 已有文件保护 | 基线中的 45 个旧文件 SHA-256 全部不变，包含使用的来源文件、已有实现和历史运行产物 |

两条 memory 引文都覆盖旧记忆全文；第 1 条 context 引文覆盖旧发言节选全文，第 2 条 context 引文为该节选第二句。逐条引文及字符位置见 [verification.json](verification.json)。引文存在只证明可追溯，不自动证明 supports 的解释正确、拆分完整或粒度恰当。

## 5. 对照旧记忆的人工初步检查

本段是人工性质的初步语义复核，未调用额外模型评分；检查对象只限旧记忆与允许的旧来源上下文。

| 维度 | 初步判断 |
| --- | --- |
| 命题覆盖 | 第 1 条保留“不喜欢极限运动（如跳伞）及高受伤风险这一原因”；第 2 条保留“高风险与安全、健康承诺相冲突”。整体未发现明确遗漏的旧记忆命题 |
| 信息增加 | 未加入新的经历、计划、运动种类、姓名或现实真实性判断。speaker 的归属可由旧发言中的 I/my 支持。第 2 条的 perceives 是释义性改写，是否改变原句断言语气需确认 |
| 时间与情态 | 旧记忆无显式时间或可能性限定；输出没有补出日期、过去式、一直如此或已改变等断言。没有用 Mem0 创建时间、当前日期解释旧陈述 |
| 条件与原因 | 旧记忆无 if 条件；due to 的原因关系在第 1 条保留。第 2 条仍将冲突连到高受伤风险，没有错误改成“安全承诺导致受伤风险” |
| 否定与态度 | Dislikes 在 raw 中保留，补充版本仍为 dislikes；没有改成喜欢，也没有将回避绝对化为从未参与 |
| 人物与指代 | 补充版本使用 The speaker，旧发言中 I/my 均属于同一 user，没有移交给其他人物。最小输入未提供自然人姓名，所以不能声称模型恢复了 Martin 等具体姓名 |
| 范围 | 保留极限运动这一类别及跳伞这个例子，没有增加 all/always 等全称限定。第 2 条未重复跳伞例子，但整体第 1 条保留了它 |
| 来源边界 | 旧发言有 avoid，但所选旧记忆没有独立写出回避行为。没有单独生成“回避”事实，不能据此算作漏拆旧记忆；本次也没有从上下文另抽新事实 |
| 粒度 | 第 1 条将态度与其原因保留在一起；第 2 条补充版本含“持有承诺”及“认为风险与承诺冲突”两个分句，尚不能认定已经达到最细原子粒度 |

## 6. 仍需用户确认

1. 第 2 条的 `perceives ... as conflicting` 是否可接受为原文 `conflicting with` 的释义，还是应严格保留原句直接陈述冲突的语气。
2. 是否接受本次两条的粒度：尤其第 2 条补充版本把“持有安全和健康承诺”与“风险与承诺冲突”写在同一句中。第 2 条单独流转时是否还应重复“如跳伞”这一例示范围，也可一并确认。
3. 第 2 条 raw 已写入 `the speaker's`，旧记忆本身只有省略主语的 Dislikes，明确的说话人归属来自旧发言。设计允许补回共享主语；仍需确认此处是否仅属最小补主语，或应将说话人归属严格留到 contextualized 版本。当前输出未提供具体姓名；若后续业务需要姓名，需另行提供可靠的人物来源。

以上是人工新增的待确认点，不是模型返回的 pending_confirmations。没有为消除这些疑点修改输出或追加请求。

## 7. 本次范围

仅新增本运行目录的输入、来源追溯、提示词、单次响应、检查和本报告；临时准备目录已清理，既有自拟案例结果保留。本次没有判断新旧事实关系，没有连接或修改 Mem0，没有知识库新增、更新或删除，没有执行完整开发子集，没有安装依赖，也没有修改 existing external/ 或配置文件。
