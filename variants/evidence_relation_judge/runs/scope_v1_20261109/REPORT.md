# 组件二第二部分：初版实现与实际验证记录

日期：2026-11-09。此版是**保守的审计原型，未完成设计文档全部功能**：能运行并对输入、时间候选、引用和模型输出留痕；尚不能可靠地产生细粒度修改补丁或确定语义关系。以下先列实际结果，再列人工复核；人工判断不等同于程序自动判断。

## 1. FactTrack 实际复用核验

用户指定的 `external/FactTrack` 是没有 `.git` 的源码副本。与 `system/mem0_halumem_diagnosis/external/FactTrack` 检出 `8b09d7fa5a805aa45a0d87a376d255665bd69460` 逐文件 `diff -rq --exclude=.git` 无差异；两份 `fact-track/core/contradict_detector.py` SHA-256 均为 `a2ffd889e955440af3ef4f39995b3e4a3e06c80b7d8e6d2d59a4212e8282c51f`，Git 检出状态为空。顶层副本自己的 commit 无法直接核验，只能由相同内容与检出关联；论文版本未核验。

在 base Python 实际导入顶层副本：不设 `BASE_PATH` 时 `KeyError: 'BASE_PATH'`；设 `BASE_PATH=/home/shu1004/ld/external` 时 `ModuleNotFoundError: No module named 'gpt_api'`（源码拼出的 utils 路径与这里目录布局不匹配）；显式将真实 utils 加入 `PYTHONPATH` 后，进一步在 `gpt_api.py` 导入 torch 时遇到 `ImportError: libcudnn.so.9`。这些是对应环境下的实际错误，不等于其他环境也必然失败。源码初始化还会加载分类模型、依赖日志与模型工具，并写日志；未为此调用原类构造函数。导入时产生的本次 Python 缓存已删除，最终两份目录逐文件一致。

| 原函数 | 位置 | 本版真实使用方式 | 改动和限制 |
|---|---|---|---|
| `interval_blockCheck` | 314 行 | 对经来源校验的有限区间，运行从原函数 AST 抽出的 pre 列表排序表达式，保存排序；独立探针还在隔离副本上运行完整原方法 | 不接受原来的无限哨兵、epsilon、embedding 同义即阻断或故事坐标推断作为有效时间；本版只生成附条件的候选窗口，非原函数完整业务路径的直接调用。 |
| `interval_contradictCheck` | 376 行 | 从原方法抽取其原样嵌套 `is_overlap` 并执行，保存双方向结果；隔离探针可运行完整原方法 | 原谓词仅匹配严格交叉，包含、相等会漏；新增独立区间关系函数。探针遇到需要真实相似度/NLI 的冲突分支时明确不调用，不编造分数。该谓词只作审计，不能决定冲突。 |
| `interval_insert` | 428 行 | 执行抽出的 pre 列表排序表达式；隔离探针完整运行原方法，观察复制状态追加与改写 | 原函数会原地改旧区间并追加新事实。本版不把这种修改应用于原记忆，也不把探针结果用于规划；当前仅保留旧事实、待确认和来源候选，尚无可执行的局部补丁。 |

`scope_planner.facttrack_original_probe()` 用原始源码 AST 加载三个完整原方法，不执行原文件顶层导入或构造函数；输入是人为给出的有限数字区间及明确的阻断布尔值、人工分配的 pre/post 状态，源代码本身未改。离线测试中 `(10,20)` 与 `(30,40)`、显式非阻断的隔离演示，三个原方法均运行，复制列表由 1 项变 2 项，原旧区间仍为 `[10,20]`。这是验证调用路径的合成程序测试，**不是**三例真实语义判断，也没有真实 NLI 分数。若未提供明确布尔判断，或原矛盾路径需要 NLI，探针返回 `not_called`。

运行路径对原排序和谓词的复用是真实的，但三个原函数没有直接驱动真实案例的边界及补丁规划。三例没有来源明确的有效期，原排序/重叠和完整函数均标为未调用。不能把此版称为已完成 FactTrack 全部关键逻辑的业务级适配。该 commit 未发现项目级许可证；本地读取及运行方式、来源和修改应在任何进一步复制或分发前另行核实权限。

## 2. 实现、输入与命令

- `scope_planner.py`：接收 v4 原请求和 v2 完整结果，保存输入、完整上游行及错误；复核 ID、引文、片段唯一性，保留上游 pending；保护旧子事实、保留每条新证据，关系默认未知。
- 可选 extraction callable 接收完整来源与 v2 候选，输出对象、属性、条件和新命题候选；程序只核对新命题引文的字面来源；对主体、对象、属性和条件做候选文字比较，不把文字一致当语义确认；缺字段为未知。**不验证含义**。`scope_extract.py` 提供本地 Qwen 实现。
- 时间仅解析本版显式协议 `time_info` 列表里的 `valid_period`、ISO 日精度起止及来源引文；带 `side`、`source_id`、`quote`，多事实必须指定 `fact_index`。日期须出现在同侧来源引文。即使字面合法，时间表达是否真的代表有效期仍未做语义核验。两个先后区间产生的窗口仅为有前置条件的候选。其他日期、开放端点、相对表达、时区和冲突不自动推断；消息记录时间只保存、永不当作失效时间。
- `scope_nli.py`：本地离线 DeBERTa；记录 premise 为旧 contextualized 子事实、hypothesis 为 v2 所引新证据，模型版本、输入、token 截断、logits 与 softmax，分数不影响计划。禁用及失败有明确状态。
- `run_scope.py`：命令行将结果写入新文件，避免覆盖；Python API `plan_scope(request, result, nli=None, extractor=None)`。

示例（以工作目录 `variants/evidence_relation_judge` 为准）：

```bash
/home/shu1004/anaconda3/envs/emem_vllm/bin/python part2_scope_judge/run_scope.py \
  runs/real_cases_20261106/promotion_input.json \
  runs/controlled_v2_20261106/promotion_run.json \
  --output /tmp/promotion-scope.json --nli --extract-qwen
```

不提供开关时两模型均不调用。支持直接传完整 v2 结果或含 `result` 的保存运行文件。输出**仅供审核**，不连接、不写入 Mem0。

## 3. 离线程序测试

在当前 variant 目录运行 `python -m unittest discover -s part1_relation_judge -p 'test*.py' -v` 和 `python -m unittest discover -s part2_scope_judge -p 'test*.py' -v`：32 项通过，包含原有 v1/v2 测试与 19 个新测试。覆盖上游失败和重复行、无效引文、重复片段、多事实时间归属、禁用/失败 NLI、边界开闭、包含关系、原谓词限制及原函数隔离探针。这个结果只表明所测程序行为通过，不是语义准确率或完整数据集评测。

## 4. 真实保存案例和本地模型

输入来自 `runs/real_cases_20261106/*_input.json`，v2 已保存结果来自 `runs/controlled_v2_20261106/*_run.json`，逐例比较并确认 `input` 完全一致。先使用本地 Qwen3-8B 对三个案例各调用一次（`with_qwen/`，保留提示词、原输出及累计调用数），随后回放保存的抽取结果、对当前版本规划器重新运行并重新推理 NLI（`replay_v2/`；回放阶段 Qwen 新调用 0 次）。抽取没有通过人工语义正确性验证。

DeBERTa 本次实际运行本地权重 float32，GPU，权重 SHA-256 `06d6fd89edd4f97816831626daafbdb0b029cf63bae8edc0bccab1d64e2e7707`，与既有 revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb` 的下载核验记录一致；并非重新在线核验 revision。前提是旧 contextualized_subfact，假设是 v2 的 `new_quote`。三个完整 logits、输入及精度、截断记录保存在对应 JSON，下面按 entailment / neutral / contradiction 给 softmax。各条来源均为英语；分数不是校准正确率。

### 晋升

- 输入：旧记忆 `Works at Historical Productions Ltd. as a Director`；`dialogue-0` 为最近晋升 lead director 的消息。旧来源记录时间 2025-09-05，新消息记录时间 2026-02-01；均不指定时区。`recently` 无事件日期。
- 原 v2：`possible_change`，整条旧记忆是唯一片段；新引文为 `dialogue-0`。新 Qwen 抽取公司、岗位与两个值，但输出 comparability=`different`，其含义可能混淆属性可比性与岗位值不同。
- 程序实际：抽取的主体、对象、属性、条件文字一致，标为 `same_scope_candidate`，与抽取模型的 `different` 分歧列入待确认；关系本身仍未知。旧事实整体保护；无修改；原始新证据和抽取的同一整句各为候选，去重未检查；保留问题，有效期未知，FactTrack 时序表达式未调用。`recently` 保留未解析；没有用记录时间关闭旧职位。
- 实际 NLI：`neutral`，0.001028 / 0.998747 / 0.000225。
- 人工初步核对：雇主应保护；晋升可作为有来源新增候选，`Director` 和 `lead director` 的包含/替代关系与变更时间仍须确认。程序没有自动分解保护雇主或生成局部职位补丁；重复添加候选需后续去重。

### 模拟跳伞

- 输入：旧记忆关于极限运动、伤害风险和安全承诺；新来源 `dialogue-0` 为模拟跳伞体验，`dialogue-2` 表示更愿意尝试新事物，`dialogue-8` 表示仍重视安全。
- 原 v2：`possible_change`，整条旧事实是唯一片段，引用 `dialogue-0`；理由提到的安全实际来自 `dialogue-8`。新 Qwen 将对象提为 simulated skydiving、comparability=`different`，保留了三条来源，但把伤害风险放在旧 value 而非 conditions，新增项也仍为整句。
- 程序实际：整体保护旧事实、无修改；三条原始来源和三条抽取候选均保留，语义关系和有效期未知，记录时间无失效作用。旧安全承诺未单独定位；所有 v2 问题作为未验证问题原样保留，包括安全是否仍重视的问题。
- 实际 NLI：`neutral`，0.002221 / 0.861620 / 0.136158；该分数只比较旧子事实与 `dialogue-0`，不包含其他两个来源。
- 人工初步核对：模拟体验不能直接推翻真实极限运动顾虑；`dialogue-8` 明确支持仍重视安全。程序未识别、删除重复问题，也未分离保护范围或确认是否影响真实跳伞偏好。

### 职业历史

- 输入：旧记忆 `Previously worked as a senior developer in Blockchain Tech`，旧上下文称当时在该公司工作；`dialogue-0` 称 `my consulting firm` 取得初始客户。
- 原 v2：`uncertain`，大小写唯一恢复后定位完整旧记忆；带假定目前在咨询公司工作的理由与问题。新 Qwen 再次抽取 `employment=current`、comparability=`different`，即使提示词明确警告勿仅凭 `my` 推断雇佣。
- 程序实际：保护整个旧事实；保留 v4 关于过去时与旧上下文现在时对齐的 pending；保留未验证的 v2 问题、新证据及 Qwen 候选；不接受当前雇佣为事实，不修改旧历史；关系和有效期未知。
- 实际 NLI：`neutral`，0.001703 / 0.997842 / 0.000455。
- 人工初步核对：新材料支持的是“my consulting firm 获得初始客户”的陈述，不足以断言雇佣、职位或离职；旧历史应保护，时间对齐仍需确认。程序没有自动指出 Qwen 的语义升级，也没有清理带错误前提的问题。

## 5. 未完成

1. 尚无可证明语义可信的独立对象/属性/条件/互斥门控。可选 Qwen 抽取只校验新命题的来源字面匹配，字段本身未附逐项可验证引文；`relation.classification` 故意保持 unknown，也不能自动判定历史更正、状态变化或兼容。
2. 尚无完整的 `interval_blockCheck` / `interval_insert` 业务级改造、相邻候选排序和对多事实证据的边界搜索；源代码排序和重叠作为隔离审计调用，完整方法只在合成探针中运行。
3. 尚无可靠的局部事实分解、依赖保护、冲突合并、去重、局部修改文本或补丁校验；当前整个旧子事实受保护，`modifications` 始终为空。新增项可能包含原始证据和重复的模型候选，不等于可直接写入的事实。
4. 尚未实现充分的相对时间解析、开放/不确定区间、时区与粗粒度表示、明确失效点或多源时间冲突解析。`compare_intervals` 只接收精确有限端点；无效或未知返回 unknown。
5. NLI 未校准，不验证互斥，当前只对 v2 引文方向做探索性推理，不以其更改状态。未运行完整开发子集、写入 Mem0 或进行独立人工标注评测。
