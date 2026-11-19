# case_01_multi_person：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：多个人物、身份关系、混合说话人。

选择原因：两名具名人物与不同关系标签；对应旧来源包含 user 发言和 assistant 对人物关系的描述。

真实 memory_id：`130bf22c-9e71-4ad2-bf51-43bac36ab2c8`。

> Grateful towards colleagues like Steven and friends like Mary

更新前快照：[session_011/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_011/before.json:128)，JSON Pointer `/api_snapshot/results/13`；底层对应 `/database_points_with_vectors/13/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_009/add_return.json)，位置 `/return_value/results/18`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`May 20, 2026, 09:04:14`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_009/input.json#/raw_dialogue/8/content [characters 0:108, zero-based, end exclusive]`。

> Maintaining these relationships is crucial. I'll ensure to keep in touch and express my gratitude regularly.

- `ctx-2`，speaker=`assistant`，recorded_at=`May 20, 2026, 09:04:14`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_009/input.json#/raw_dialogue/9/content [characters 160:289, zero-based, end exclusive]`。

> Your gratitude towards colleagues like Steven and friends like Mary highlights the importance of having a strong support network.

## 程序检查

| 检查 | 结果 |
| --- | --- |
| 原有校验器 | passed |
| 返回事实数 | 1 |
| JSON 字段、ID、原文、编号、每条 memory 引文与来源编号 | 通过现有校验器 |
| 逐字引文 | 1/1 |
| 真实调用 / 自动重试 | 1 / 0 |
| 模型 / finish_reason | qwen-plus / stop |
| 离线重放 | 原始响应经 MockBackend 复核，与保存结果一致；不调用真实模型 |

显式生成参数为 {}，超时 180 秒，SDK max_retries=0，HTTP 不跟随重定向，response_format=json_object。服务默认采样值和具体模型修订未知。提示词逐字等于 [冻结 v3](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/frozen_prompt.txt)，SHA-256 为 `28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e`。

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_01_multi_person/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_01_multi_person/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_01_multi_person/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

初步判断，待人工确认：格式检查 passed；1 条事实覆盖感谢态度、Steven/colleagues、Mary/friends 及 like 的举例表述，未见关键命题遗漏。观察到 raw 用上下文补出 The user 的来源边界问题，以及肯定用户主体与将主体列为待确认之间的表述冲突；不据此认定用户主体虚构。原始说话人和具体人物身份仍有局部未决项。

### 事实 1

原始子事实：

> The user is grateful towards colleagues like Steven and friends like Mary.

上下文版本：

> The user is grateful towards colleagues like Steven and friends like Mary.

覆盖及限定检查：初步判断，待人工确认：raw/contextualized 均保留 grateful、colleagues like Steven、friends like Mary，未改人物、关系或 like 的范围。输入没有明确否定、事件日期、条件或计划/可能性成分，输出也未新增这些成分。contextualized 的用户主体可由同一事件的 ctx-1 第一人称感谢及 ctx-2 的 Your gratitude 合理关联；但冻结 v3 的 raw-only 规则不允许为省略主语补用户，因此 raw 的 The user 仍越过来源边界。正文未带入 ctx-1 的定期联系计划或 ctx-2 的 strong support network 等额外内容。

初审状态：`issue_observed`。观察到的问题：断言与待确认状态不一致、raw 混入上下文主体。

观察项与依据：

- **raw 混入上下文主体**（observed，初步判断，待人工确认）

  输入或对照：`Grateful towards colleagues like Steven and friends like Mary`

  输出：`The user is grateful towards colleagues like Steven and friends like Mary.`

  理由：初步判断，待人工确认：此处 output_quote 是 raw_subfact。memory 未给出主体，也没有可在 memory 内部恢复的共享用户主体；raw 新增 The user，依赖 source_context 才能补足。依据主代理提供的冻结 v3 第2条，补足应放在 contextualized。此判断是字段来源边界问题，不是认定用户这一语义主体无依据或已被证伪。

- **断言与待确认状态不一致**（observed，初步判断，待人工确认）

  输入或对照：`The subject of 'Grateful' (i.e., who holds this attitude)`

  输出：`The user is grateful towards colleagues like Steven and friends like Mary.`

  理由：初步判断，待人工确认：input_quote 引自本次输出 pending_confirmations 的 item，而非原始 memory。正文直接固定为用户持有此态度，pending 又将谁持有该态度本身列为待确认，存在明确的断言/待决状态不一致。pending 理由还把语义主体与是否由用户原话表达混在一起；上下文可支持用户主体，但不能证明此记忆概括是用户原话。此项不等同于主语虚构。

未决项（不自动判错）：

- ORIGINAL_SPEAKER：初步判断，待人工确认：ctx-1 是 user 的第一人称联系/表达感谢意向；具名的 Steven/colleagues 与 Mary/friends 在提供的片段中只由 ctx-2 assistant 表述。旧 memory 是提取概括，其原始说话人不能仅从 memory 引文认定为 user。
- SUBJECT_OR_IDENTITY：初步判断，待人工确认：现有文本足以保留 like Steven / like Mary 的记忆命题，但不能验证两人的真实身份或 like 在完整历史中是否只是泛指例示；这不是因此改写或否定旧记忆的依据。待决项关于“没有任何来源肯定关系”的说法过宽，ctx-2 实际给出了这些关系标签；它仍不是独立的现实核验。

说话人及语义主体：

- semantic_subject：初步判断，待人工确认：用户主体有上下文的同事件关联：ctx-1 用户说 I'll ... express my gratitude；ctx-2 assistant 用 Your gratitude 描述具名关系。可作为 contextualized 的主体解释，不自动构成捏造。
- original_utterance_attribution：初步判断，待人工确认：用户直接发言支持其表达感谢的意向；具体姓名与关系的可见原始发言是 assistant。模型正文及 supports 未明说“用户亲口说过完整具名命题”，故不另标 SPEAKER_ATTRIBUTION_OVERCLAIM。
- pending_review：初步判断，待人工确认：模型的第一个 pending 把主体和原始说话人混写，已记录断言/待决冲突。第二个 pending 的实际身份疑问可保留为有限未知，但维持旧记忆不要求证明人物现实身份。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / 130bf22c-9e71-4ad2-bf51-43bac36ab2c8 | Grateful towards colleagues like Steven and friends like Mary | Old memory states the user is grateful towards colleagues like Steven and friends like Mary. | 部分支持，不能自动计错：初步判断，待人工确认：memory 引文直接支持感谢、两个人名及关系/like 范围，但字面上没有 user 主语；必要上下文为用户主体提供合理关联。因此支持主体属于上下文补足，不能说 memory 本身显式写了 user，更不能由此推出完整概括是用户原话。supports 的 Old memory states 未明确声称用户直接说过，未单独判来源归属错误；partial 不自动计为错误。 |

模型自身 pending_confirmations：

- The subject of 'Grateful' (i.e., who holds this attitude)：The memory text is a fragment without explicit subject; it does not grammatically specify whether 'Grateful' is self-attributed by the user, reported by the assistant, or ascribed to another person. Although context-2 quotes the assistant paraphrasing this sentiment, and context-1 shows the user speaking about maintaining relationships and expressing gratitude, neither confirms the original memory fragment was uttered by the user nor that it reflects their direct self-report — it could be an extracted summary, assistant rephrasing, or third-party observation.
- Whether 'Steven' and 'Mary' are actual named individuals in the user's life vs. generic examples：The phrases 'colleagues like Steven' and 'friends like Mary' use 'like', indicating Steven and Mary serve as exemplars — but the memory text does not clarify whether they are real, specific people known to the user or merely illustrative placeholders. No source context affirms their concrete identity or relationship status to the user.

## 人工待确认

1. ORIGINAL_SPEAKER：初步判断，待人工确认：请人工区分“描述用户的命题”与“用户直接自述”；当前片段不能确认 Steven/Mary 的具名关系概括由用户亲口说出。
2. SUBJECT_OR_IDENTITY：初步判断，待人工确认：具体人物身份及 like 是否泛指在现有片段内无法进一步核实；不应把这种现实身份未知自动算成拆分错误，也不应要求用补写事实来消除未知。
3. ASSERTION_PENDING_CONFLICT：初步判断，待人工确认：请人工确认输出待决状态是否应收窄为原始说话人归属；本报告所标冲突限于正文与 pending 同时对语义主体给出不同确定程度。

独立复核文件：[reviews/group_01.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_01.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
