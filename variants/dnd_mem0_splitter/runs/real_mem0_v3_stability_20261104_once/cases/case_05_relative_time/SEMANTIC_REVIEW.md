# case_05_relative_time：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：相对时间、职位状态变化、上下文额外感受。

选择原因：recently 与职位变化及机构；原始 user 发言带记录时间和额外感受，可检查时间解释及补充范围。

真实 memory_id：`2570a550-4b52-43fc-b5c4-079261785a1a`。

> Recently promoted to lead director at Historical Productions Ltd

更新前快照：[session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json:110)，JSON Pointer `/api_snapshot/results/11`；底层对应 `/database_points_with_vectors/11/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/add_return.json)，位置 `/return_value/results/14`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`Feb 01, 2026, 18:47:19`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content [characters 0:92, zero-based, end exclusive]`。

> I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

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

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_05_relative_time/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_05_relative_time/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_05_relative_time/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

格式检查通过，1条返回事实。职位晋升、lead director、机构和 recently 均保留；未把发言日期等同晋升日期。观察到 raw 补入 memory 未表达的用户主语，属于来源边界问题；该主体在 contextualized 中有 ctx-1 第一人称依据，不判为主体完全无依据。

### 事实 1

原始子事实：

> The user was recently promoted to lead director at Historical Productions Ltd.

上下文版本：

> The user was recently promoted to lead director at Historical Productions Ltd.

覆盖及限定检查：覆盖原记忆的近期晋升、职位 lead director 和机构 Historical Productions Ltd。recently 仍为相对时间，未增添具体晋升日期或把 Feb 01, 2026 当作事件日；记录时间是发言记录而非事件发生日。上下文的 exciting 仅保留在引文中，没有成为 raw/contextualized 的额外感受事实。无否定、条件或析取命题需要另行恢复。

初审状态：`issue_observed`。观察到的问题：raw 混入上下文主体。

观察项与依据：

- **raw 混入上下文主体**（observed，初步判断，待人工确认）

  输入或对照：`Recently promoted to lead director at Historical Productions Ltd`

  输出：`The user was recently promoted to lead director at Historical Productions Ltd.`

  理由：memory 省略晋升主体，内部没有可恢复的 The user 共享成分；raw 新增用户主语，超出仅恢复 memory 内部共享成分的边界。ctx-1 的 I recently got promoted 足以支持 contextualized 的用户主体，故此处只记 raw 来源边界问题，不记 UNSUPPORTED_ADDITION 或主体身份错误。

未决项（不自动判错）：

未发现需要单独登记的指代、身份或原始说话人未决项。具体事件日期等未提供细节，不因缺失就自动判错。

说话人及语义主体：

- semantic_subject：user；由同一晋升事件的 ctx-1 第一人称可靠支持。
- original_speaker：ctx-1 明确标记为 user。
- assessment：contextualized 的语义主体和 self-reported 归属有依据；raw 不能因此自动补主语。没有把 assistant 的表述冒充 user 原话。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / 2570a550-4b52-43fc-b5c4-079261785a1a | Recently promoted to lead director at Historical Productions Ltd | Old memory states that the user was recently promoted to lead director at Historical Productions Ltd. | 部分支持，不能自动计错：声明的 memory 引文直接支持 recently、晋升、职位及机构；引文本身未明说 the user。用户主体需结合 ctx-1 的同一事件第一人称确定，故不能把该引文视为独立包含显式用户主语；全输入范围内该主体有依据，不另判 supports 越界。 |
| 1 | context / ctx-1 | I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting! | Confirms the promotion is the user's own, specifies first-person agency ('I got promoted'), and anchors 'recently' to the speaker's perspective; supports interpreting the memory as self-reported. | 直接支持：ctx-1 是 user 的 I recently got promoted，同一职位与机构使事件关联可靠；支持用户自述和相对时间依说话视角理解。supports 没有把发言记录时间写成晋升发生日，也没有把 exciting 写为新增事实。此处 agency 依其括号例子理解为第一人称事件主体，并非推断用户主动促成晋升。 |

模型自身 pending_confirmations：

`[]`。

## 人工待确认

本例没有额外具体未决项；整个语义初审仍待人工最终确认。

独立复核文件：[reviews/group_03.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_03.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
