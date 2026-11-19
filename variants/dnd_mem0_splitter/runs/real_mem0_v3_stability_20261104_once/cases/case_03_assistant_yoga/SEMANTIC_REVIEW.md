# case_03_assistant_yoga：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：助手来源、说话人归属、析取与状态。

选择原因：旧记忆含 practices or is open to；生成会话中有 assistant 的 yoga 表述，需检查来源角色和命题范围。

真实 memory_id：`992ae849-3f40-4ffe-a2ec-16e20959ca86`。

> Practices or is open to yoga for supporting personal health and transition

更新前快照：[session_008/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json:533)，JSON Pointer `/api_snapshot/results/58`；底层对应 `/database_points_with_vectors/58/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/add_return.json)，位置 `/return_value/results/46`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`Feb 05, 2026, 17:13:15`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content [characters 0:255, zero-based, end exclusive]`。

> I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.

- `ctx-2`，speaker=`assistant`，recorded_at=`Feb 05, 2026, 17:15:18`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/3/content [characters 327:523, zero-based, end exclusive]`。

> As you continue exploring job opportunities, remember the importance of balancing professional responsibilities with personal health. Practices like yoga could support this transition effectively.

## 程序检查

| 检查 | 结果 |
| --- | --- |
| 原有校验器 | passed |
| 返回事实数 | 1 |
| JSON 字段、ID、原文、编号、每条 memory 引文与来源编号 | 通过现有校验器 |
| 逐字引文 | 3/3 |
| 真实调用 / 自动重试 | 1 / 0 |
| 模型 / finish_reason | qwen-plus / stop |
| 离线重放 | 原始响应经 MockBackend 复核，与保存结果一致；不调用真实模型 |

显式生成参数为 {}，超时 180 秒，SDK max_retries=0，HTTP 不跟随重定向，response_format=json_object。服务默认采样值和具体模型修订未知。提示词逐字等于 [冻结 v3](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/frozen_prompt.txt)，SHA-256 为 `28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e`。

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_03_assistant_yoga/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_03_assistant_yoga/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_03_assistant_yoga/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

初步判断，待人工确认：现有 report.json 为格式检查 passed；审查 1 条已返回事实和全部 3 条 supports。旧记忆的 practices OR is open to、瑜伽对象及 personal health/transition 用途均保留，未被助手 could 建议覆盖。观察到 1 项 raw 来源边界问题：raw 新补 The user，违反本批次 frozen_prompt.txt 第2条；这与主体是否可由上下文合理关联是两件事，不判为凭空人物，也不判用户直接自述。原始发言归属、析取哪一支成立及具体实践状态仍未决。

### 事实 1

原始子事实：

> The user practices yoga or is open to practicing yoga for supporting personal health and transition.

上下文版本：

> The user practices yoga or is open to practicing yoga to support personal health and career transition.

覆盖及限定检查：初步判断，待人工确认：完整保留 practices or is open to 的单一析取，不拆成已实践与已开放两个肯定事实；保留 yoga、personal health、transition 及支持用途。contextualized 中 career 可由 ctx-1 的职业困境、找新工作和 ctx-2 的 job opportunities/this transition 共同消歧，属于有源且必要的语境说明。没有将 could 升格为用户实践事实，没有借来源纠正旧记忆，没有扩入职业目标、工作生活平衡等独立命题；这些额外细节仅在引文中出现。未添加日期、持续时间、姓名或关系。

初审状态：`issue_observed`。观察到的问题：raw 混入上下文主体。

观察项与依据：

- **raw 混入上下文主体**（observed，初步判断，待人工确认）

  输入或对照：`Practices or is open to yoga for supporting personal health and transition`

  输出：`The user practices yoga or is open to practicing yoga for supporting personal health and transition.`

  理由：初步判断，待人工确认：旧 memory_text 没有 user、说话人身份或可在文本内部恢复为 user 的共享主语；raw_subfact 新增 The user。已读取本批次 frozen_prompt.txt，第2条明确禁止为语法完整把省略主语补成用户，且上下文支持的身份只能必要时用于 contextualized_subfact。ctx-1 的第一人称职业经历和 ctx-2 面向 you 的建议能合理关联语义主体，但不能使 raw 越过来源边界；因此只记录 RAW_CONTEXT_LEAK，不追加 UNSUPPORTED_ADDITION 或人物虚构标签。

未决项（不自动判错）：

- ORIGINAL_SPEAKER：初步判断，待人工确认：ctx-1 是 user 的职业自述，但没有瑜伽；ctx-2 明确为 assistant 的 could 建议。尚无 user 直接自述实践或开放瑜伽的引文，旧记忆的上游形成方式也无法仅凭输入确定。输出 evidence[2] 明示 assistant，pending 也记录来源未决，未观察到将助手原话写成用户原话的明确断言。
- MODAL_OR_RELATION_SCOPE：初步判断，待人工确认：旧记忆只记 practices OR is open to，未确定哪一支成立；assistant 的 could 建议既不证实际实践，也不证用户接受或表达开放。正文保留旧析取，符合不纠正旧记忆的要求；用户实际状态、意向强弱与具体实践持续范围仍待核实，而非据此把正文认定为错误。

说话人及语义主体：

初步判断，待人工确认：语义主体与原始说话人分开审查。ctx-1 的 I 与 ctx-2 的 you/this transition 可把职业过渡语境合理关联到用户，因此 contextualized 的 The user 不一概判为虚构。证据未表明用户说过瑜伽实践或开放；memory supports 使用 Old memory states，assistant supports 明确说明建议来自助手，且 pending 留下原始来源疑问，所以不另记 SPEAKER_ATTRIBUTION_OVERCLAIM。raw 新补身份的边界问题已单独记录。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / 992ae849-3f40-4ffe-a2ec-16e20959ca86 | Practices or is open to yoga for supporting personal health and transition | Old memory states the user practices or is open to yoga for supporting personal health and transition. | 部分支持，不能自动计错：初步判断，待人工确认：该 memory 引文直接支持旧记忆如此记载 practices OR open、瑜伽及 health/transition 用途，不能证明现实状态或用户直接说过。supports 的 The user 并非引文明示主体，需要 ctx-1/ctx-2 的共享过渡语境关联；这是可合理关联的主体补足，不是用户原始发言归属证明。本项未明确声称 user said，故不自动记支持越界或说话人错误。 |
| 1 | context / ctx-1 | I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals. | Provides contextual grounding: 'transition' refers to career transition, and 'personal health' includes well-being in the context of work-life balance. | 直接支持：初步判断，待人工确认：ctx-1 明示 career、current role、new job、well-being 与 work-life balance；结合紧邻 ctx-2 的 job opportunities 和 this transition，足以把 transition 消歧为 career transition，并为 personal health 的健康福祉语境提供依据。supports 未声称这段用户引文证明瑜伽实践或开放，也未把 humanitarian goals 等引文额外细节加入正文。 |
| 2 | context / ctx-2 | As you continue exploring job opportunities, remember the importance of balancing professional responsibilities with personal health. Practices like yoga could support this transition effectively. | Confirms that 'yoga' was suggested by the assistant as a supportive practice for the user’s transition and personal health — consistent with the memory’s framing of openness or practice, but does not confirm the user’s actual practice status. | 部分支持，不能自动计错：初步判断，待人工确认：ctx-2 的 speaker=assistant 且原话为 yoga could support this transition，直接支持助手提出可能有帮助的瑜伽建议及职业过渡/个人健康语境。它不能证实用户实践，也不能证实用户开放。supports 把建议称为与旧析取表述 consistent，并明确不确认 actual practice；按兼容性表述理解，未见把 could 明确变成任一用户状态的断言，因此列为部分支持和范围未决，不自动记 observed 错误。人工仍应核对 consistent 是否会被误读为对 openness 的确认。 |

模型自身 pending_confirmations：

- Whether the user actually practices yoga or only expresses openness to it：The memory uses the disjunctive 'or' without specifying which disjunct holds; neither source_context confirms current practice nor clarifies intent level (e.g., intention vs. exploration).
- The speaker of the memory statement：The memory text is third-person ('Practices or is open...'), but input source_context shows the user self-reports career concerns (ctx-1) and the assistant recommends yoga (ctx-2); it is not stated whether this memory reflects user self-report, assistant summary, or system inference.
- Temporal scope of 'practices' (e.g., current, past, habitual)：The memory lacks tense markers or time anchors; 'Practices' is bare verb form without explicit present/habitual/ongoing marking, and no recorded_at from memory itself is provided.

## 人工待确认

1. 旧记忆中 practices OR is open to 的实际分支与来源：初步判断，待人工确认：需核实用户是否实践、是否开放，以及旧记忆形成于用户自述、助手建议提取或其他过程。不能把助手建议直接当用户同意，也不能据此删改旧记忆的析取。
2. supports[2] 中 consistent 的解释范围：初步判断，待人工确认：建议与旧记忆可以相容，但相容不构成对用户 openness/practice 的证实；当前列为部分支持而非已观察错误。
3. 原输出关于 practices 的时间待确认理由：初步判断，待人工确认：practices 是一般现在时的第三人称单数形式，并非原 pending 理由所称的无显式时态 bare verb。具体持续时间、频率或开始日期确实未给出；这项理由措辞不准确，但正文没有改时态或推定事件日期，因此不据此另计 TIME_SCOPE_CHANGE。

独立复核文件：[reviews/group_02.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_02.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
