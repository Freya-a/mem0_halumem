# 离线事实范围交集

本目录现包括基于下述范围计算的候选 `ScopePlan`；新增规划实现、两组回放、验收及限制见 [SCOPE_PLAN_REPORT.md](SCOPE_PLAN_REPORT.md)。本目录不修改旧记忆，不调用模型或 Mem0。`cases/*.json` 中的主体、属性和范围是**人工整理的候选输入**；不是模型提取，也不等于已经证实的事实。范围结果取决于这些输入的正确性。

## 参考源码与实现边界

- 已阅读 [FactTrack `interval_blockCheck`](../../../external/FactTrack/fact-track/core/contradict_detector.py#L314) 和 [`interval_contradictCheck`](../../../external/FactTrack/fact-track/core/contradict_detector.py#L376)：前者从故事锚点和前后方向寻找阻断边界；后者先筛选跨方向区间，再进行相似度、NLI 和矛盾判断。参考了“显式端点、先按区间筛选”的组织思想。
- **直接复用 FactTrack 代码：无。** 其 overlap 谓词仅覆盖特定严格交叉，不覆盖完全包含与相等端点；blockCheck 的故事坐标、方向、相似度和 epsilon 裁剪也不能直接代表对话事实的有效时间。这里独立实现通用闭区间及星期交集，不自动推断阻断点、不复制作者代码。
- [ATOM](https://aclanthology.org/2026.findings-eacl.49/) 使用观察时间与有效时间双时间模型。这里仅参考这一区分；不声称实现其知识图谱或整个方法。`observation` 是来源记录／观察字段，独立于 `valid`，来源消息时间不会自动填入有效端点，也不能证明事件发生时间。

## 表示与结果

`scope.py` 提供 `Field`、`Weekdays`、`Bound`、`Interval`、`Scope` 和纯函数 `compare(old, new)`，字段和端点保留 `Evidence(source_id, quote)`。主体和属性的字符串是调用方提供的**规范化候选**；直接按相同或不同值计算，程序不判断共指、同义、语义支持或属性间依赖，因此比较前必须人工核对。输入的值与范围是候选，重叠不等于事实冲突或修改许可。

- 星期使用 0–6（周一–周日）：`all` 表示明确适用于全部，`known` 是已知星期集合，`unknown` 是未知；`unknown` 不等于 `all`。
- 有效时间为**日期精度、两端包含且非空**的区间。端点 `known` 为确定日期，`unbounded` 为明确无界的模型范围，`unknown` 为边界缺失；不能把缺失端点视为无限。已知起点、未知终点时，隐含未知终点不早于起点，反之亦然。不同时间精度、时区、小时与周期例外不在本实现中。
- 返回 `overlap`、`disjoint` 或 `unknown`。端点和其他维度完整时，确定相交返回完整 `intersection` 和 `intersection_complete=true`。若端点不完整但已知端点可以证明至少有一个共同日期，也返回 `overlap`：`intersection` 仅为一个有保证的单日子集、`intersection_complete=false`，并保留 `missing`。此证明是保守的，不保证找出每一种可证明的部分交集。无法证明时不伪造交集，返回 `missing`、`possible_weekdays`（仅为上界，不是已确定交集）和 `known_time_constraints`。若某已知维度足以证明不相交，可忽略其他维度未知。有限日期范围会核查其中是否真的存在对应星期。
- 回放层要求已知主体、属性、星期和已知或无界端点有非空引文，且旧、新字段各自引用正确一侧的来源；纯数学 API 允许无引文输入，供独立计算与测试。引文核对只验证 `source_id` 和文本逐字匹配，不验证其语义支持。来源与标注保存在输入、`annotated_old_scopes`、`annotated_new_scope` 及确定交集中；`known_time_constraints` 是候选端点的约束，不是推断出的确切未知边界。

## 三案

| 文件 | 来源与回放观察 | 仍缺或需核对 |
|---|---|---|
| `cases/promotion.json` | 读取既有 v2 整句候选，其字面范围覆盖 `Director` 和 `Historical Productions Ltd.`。手工规范化属性将职称与雇主分开，比较新职称范围时前者为 unknown、后者在属性维度 disjoint；后者只代表属性不同，不代表雇佣状态已消失。 | 晋升日期、旧/新有效区间端点和星期范围未提供；属性对齐及历史化语义仍需核对。记录时间不充当生效日。 |
| `cases/job_transition.json` | 读取既有 v2 的 `support`；仅作为原始关系候选，既不证明同一阶段，也不提供生效边界或授权修改。人工候选把两条陈述映射到同一转岗进度，范围比较为 unknown。 | 转岗时间、有效端点和星期范围未知；同一转岗事项及阶段关联仍需语义复核，也不能推断不再寻找其他机会。 |
| `cases/synthetic_wednesday_01.json` | **手工构造**输入与 mock 候选，通过现有 `judge(data, backend)` 校验。旧规则为周一/周三，新规则为 2026-12-01 起周三：交集为该日期起的周三，单独周一为 disjoint。 | 手工样例中 `onward` 被明确定义为该测试的无界规则域；它不是对真实未来的保证。旧规则域与新规则域的重叠只是在计算候选适用域，不能断言冲突后旧值仍真实有效。没有来源观察时间。 |

两条真实案例同时保存引文实验路径，回放时单独读取其候选，不覆盖基线。`candidate_attributes` 只按旧记忆中**人工标注属性引文**与组件一候选片段的字面包含关系报告：周三模拟案例的 `Wednesdays` 是条件片段，不覆盖人工标注的属性引文 `work from home`，所以该列表为空；星期交集仍依据单独的有引文标注计算。人工预期仅在 `cases/expected.json`，生产回放不读取该文件。

## 命令

从本目录运行（只需 Python 标准库）：

```bash
python replay.py > cases/replay_results.json
python -m unittest discover -s . -p 'test_*.py' -v
```

`cases/replay_results.json` 是上述离线命令生成的结果快照，包含未改动的真实基线结果、单列实验候选、模拟结果、带来源的人工输入和比较结果。它可以从当前源码和样例重新生成。旧版数据路径相对于本目录；请保留仓库目录结构。
