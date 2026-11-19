# case_07_no_children：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：明确否定状态、缺失主语、上下文家庭细节。

选择原因：简短否定状态；旧 user 家庭介绍可提供主体线索，同时含父母和关系状态等额外内容。

真实 memory_id：`40c29476-81a2-477d-9e75-a2a3a92d46c7`。

> No children

更新前快照：[session_005/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json:191)，JSON Pointer `/api_snapshot/results/20`；底层对应 `/database_points_with_vectors/20/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_001/add_return.json)，位置 `/return_value/results/10`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`Sep 04, 2025, 19:38:09`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_001/input.json#/raw_dialogue/8/content [characters 0:87, zero-based, end exclusive]`。

> Good, let me introduce my family. Both parents are alive, no_relationship, No children.

## 程序检查

| 检查 | 结果 |
| --- | --- |
| 原有校验器 | passed |
| 返回事实数 | 1 |
| JSON 字段、ID、原文、编号、每条 memory 引文与来源编号 | 通过现有校验器 |
| 逐字引文 | 2/2 |
| 真实调用 / 自动重试 | 1 / 0 |
| 模型 / finish_reason | qwen-plus / stop |
| 离线重放 | 原始响应经 MockBackend 复核，与保存结果一致；不调用真实模型 |

显式生成参数为 {}，超时 180 秒，SDK max_retries=0，HTTP 不跟随重定向，response_format=json_object。服务默认采样值和具体模型修订未知。提示词逐字等于 [冻结 v3](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/frozen_prompt.txt)，SHA-256 为 `28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e`。

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_07_no_children/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_07_no_children/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_07_no_children/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

格式检查通过，1条返回事实。No children 的否定状态保留，未扩写为不想要孩子或从未有过孩子。观察到 raw 从上下文补入用户主语；用户家庭自我介绍足以支持 contextualized，但不能突破 raw 仅恢复 memory 内部成分的边界。

### 事实 1

原始子事实：

> The user has no children.

上下文版本：

> The user has no children.

覆盖及限定检查：覆盖无子女状态，has no children 保留否定范围；未引申为不愿生育、永久无子女、终身从未有过孩子或无亲属。Both parents are alive 和 no_relationship 仅在逐字引文中出现，没有变成 raw/contextualized 的额外家庭事实。未增加日期、条件或其他情态。

初审状态：`issue_observed`。观察到的问题：raw 混入上下文主体。

观察项与依据：

- **raw 混入上下文主体**（observed，初步判断，待人工确认）

  输入或对照：`No children`

  输出：`The user has no children.`

  理由：memory 只有 No children，内部没有可恢复的 The user 主语。raw 中新增 The user 属于借上下文补主体；该补足应留在 contextualized。ctx-1 的 let me introduce my family 为语义主体提供可靠依据，所以不将其认定为无依据的身份添加。

未决项（不自动判错）：

未发现需要单独登记的指代、身份或原始说话人未决项。具体事件日期等未提供细节，不因缺失就自动判错。

说话人及语义主体：

- semantic_subject：user；由 let me introduce my family 的自我家庭介绍可靠支持。
- original_speaker：ctx-1 明确标记为 user，且包含 No children。
- assessment：contextualized 的主体与来源归属无明显问题；raw 的用户补足违反来源边界。未将家庭介绍中的其他人物/关系细节写成新事实。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / 40c29476-81a2-477d-9e75-a2a3a92d46c7 | No children | Old memory states 'No children', expressing the absence of children in the user's family. | 部分支持，不能自动计错：No children 直接支持无子女的否定状态，但该 memory 引文本身不包含用户或家庭所属的显式主语；用户主体需结合 ctx-1 的家庭自我介绍。全输入有支持，故不另记无依据新增或 supports 越界。 |
| 1 | context / ctx-1 | Good, let me introduce my family. Both parents are alive, no_relationship, No children. | Confirms the phrase 'No children' is part of the user's self-introduction about their family; speaker is explicitly labeled as 'user'. | 直接支持：原引文含 let me introduce my family 与 No children，且 speaker=user；支持这是用户关于自身家庭的陈述。supports 不推导生育意愿、既往终身史或父母/伴侣新事实。 |

模型自身 pending_confirmations：

`[]`。

## 人工待确认

本例没有额外具体未决项；整个语义初审仍待人工最终确认。

独立复核文件：[reviews/group_03.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_03.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
