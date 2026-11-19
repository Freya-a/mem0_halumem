# case_04_negative_relative：真实旧记忆拆分检查

**语义复核：初步判断，待人工确认。** 程序检查与语义判断分开记录；未确认项不自动算成错误。

日期：2026-11-04（Asia/Shanghai）。本例真实 qwen-plus 调用 1 次，重试 0 次。

## 选择与来源

覆盖类型：否定偏好、原因与作用范围、亲属代词、上下文额外偏好。

选择原因：否定偏好与清醒负责的理由，包含 relative；原始饮料偏好发言还提到能量饮料、绿茶和汽水。

真实 memory_id：`30a88f0c-d4b8-4089-95b2-82938e45558c`。

> Does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative

更新前快照：[session_004/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/before.json:164)，JSON Pointer `/api_snapshot/results/17`；底层对应 `/database_points_with_vectors/17/payload/data`。

原实际 ADD：[add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_003/add_return.json)，位置 `/return_value/results/13`。生成前无此 ID，生成后、前一会话 after 及目标 before 中 ID/旧文本对应；相关历史 checkpoint 哈希匹配。具体链见 [selection.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/selection.json) 与 [source_provenance.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/source_provenance.json)。本次仅使用落盘记录，不连接 Mem0。

以下是实际允许的旧上下文；来源角色和原始时间没有改写，没有人为增加评价或预期答案。原始时间没有注明时区，未推定时区。

- `ctx-1`，speaker=`user`，recorded_at=`Sep 06, 2025, 14:02:33`；`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_003/input.json#/raw_dialogue/10/content [characters 0:548, zero-based, end exclusive]`。

> I don't like to drink energy drinks. I avoid energy drinks because they make me jittery and unable to concentrate on supporting my relative. I like to drink green tea for its calming effect, helping me stay focused and composed during stressful situations. I don't like to drink soda due to its excessive sweetness and lack of nutritional value, which doesn't align with my health-conscious lifestyle. I don't like to drink alcoholic drinks. I avoid alcoholic drinks because I need to stay clear-headed and responsible while supporting my relative.

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

原始响应 [raw_content.txt](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_04_negative_relative/raw_content.txt)、通过结果 [result.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_04_negative_relative/result.json)、程序明细 [program_checks.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/cases/case_04_negative_relative/program_checks.json) 均保留；没有修补引文或改标来源。

## 逐事实语义检查

初步判断，待人工确认：现有 report.json 为格式检查 passed；审查 1 条已返回事实和全部 2 条 supports。未发现协议分类中的明确正文忠实度或支持范围错误；否定偏好、because 原因和 while 范围完整保留。亲属具体身份及支持持续范围仍未决，不能把这些不确定计为错误。

### 事实 1

原始子事实：

> They do not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative.

上下文版本：

> The user does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative.

覆盖及限定检查：初步判断，待人工确认：保留不喜欢饮用 alcoholic drinks 的否定偏好，未改写为从不饮用、完全禁酒或从未饮酒；保留 because they need to stay clear-headed and responsible 的因果关系及 while supporting their relative 的作用范围。raw 的 They 可从同一旧记忆内部 they need/their relative 恢复，符合内部共享主语规则。contextualized 的 The user 有同主题 user 第一人称来源，未推定姓名、具体亲属关系、支持方式或持续时间。能量饮料、绿茶、汽水等额外偏好未扩入正文；也未把记录时间当事件时间。

初审状态：`uncertain_only`。观察到的问题：未观察到明确分类问题。

观察项与依据：

未观察到明确分类问题；不表示已证明完全正确。

未决项（不自动判错）：

- RELATIVE_OR_OTHER_REFERENT：初步判断，待人工确认：原 memory 的 their relative 与 user 原话的 my relative 仅能支持该主体的一位亲属，不能确定姓名或属于父母、兄弟姐妹、子女等哪种关系。输出保持泛称并记录待确认，没有补造亲属身份。
- MODAL_OR_RELATION_SCOPE：初步判断，待人工确认：while supporting 明确保留支持亲属时需清醒负责的范围，但没有给出支持的持续时间、频率或当前是否持续。此处是 because 因果和 while 范围，不是已明示的 if/unless 逻辑条件。输出正文未扩展为永久戒酒或无条件的支持状态。

说话人及语义主体：

初步判断，待人工确认：ctx-1 明确标记 speaker=user，且同一饮酒内容使用 I/my relative，可靠同主题第一人称关联支持 contextualized 将省略主体补为用户。memory 引文本身仅证明旧记忆记载；context supports 才说明用户来源。该例不是助手建议，也没有原始说话人越界；亲属本人并非饮酒偏好的主体。

逐条 evidence / supports（判断均为初步判断，待人工确认）：

| 下标 | 来源 | quote | 模型 supports | 初审分类与理由 |
| --- | --- | --- | --- | --- |
| 0 | memory / 30a88f0c-d4b8-4089-95b2-82938e45558c | Does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative | Old memory states a dislike of alcoholic drinks grounded in the need to remain clear-headed and responsible during support of their relative. | 直接支持：初步判断，待人工确认：supports 准确说明旧记忆记载 dislike、清醒和负责的必要性及 supporting relative 时的理由范围；没有把否定偏好强化为永不饮用，也没有声称单凭 memory 确认用户原话或现实真实性。 |
| 1 | context / ctx-1 | I don't like to drink alcoholic drinks. I avoid alcoholic drinks because I need to stay clear-headed and responsible while supporting my relative. | Confirms the speaker is the user (first-person 'I'), specifies the attitude ('don't like' / 'avoid'), and matches the causal reasoning and referent ('my relative'). | 直接支持：初步判断，待人工确认：所引连续两句逐字包含 I don't like alcoholic drinks、I avoid、because I need to stay clear-headed and responsible、while supporting my relative；speaker=user 元数据与第一人称同主题内容共同支持用户来源、态度、原因和泛称亲属。avoid 虽未出现在旧记忆正文中，但直接在此 quote 内且仅在 supports 描述来源，不是正文新增戒酒事实。该项未确定亲属身份或支持时长。 |

模型自身 pending_confirmations：

- The identity of 'their relative'：The memory and source context both use 'my relative' / 'their relative' without naming or specifying the relationship (e.g., parent, sibling, child) or identifying information.
- Whether 'supporting their relative' refers to ongoing, current, or situational support：The memory and context state the reason conditionally ('because they need to stay... while supporting...') but provide no temporal scope (e.g., duration, frequency, or triggering circumstance) for the support role.

## 人工待确认

1. their relative 的具体身份：初步判断，待人工确认：输入没有姓名、亲属类别或其他可唯一定位信息；保持原泛称，人工确认前不补具体关系。
2. 支持亲属的持续范围及原 pending 理由的条件措辞：初步判断，待人工确认：持续时间和频率确实未知。原输出把 because...while... 概括为 conditionally，措辞需人工校核：because 表原因，while 限定支持期间，不能改成额外 if 条件。正文已经保留原 because 与 while，未观察到条件或时间范围被改写，故不把理由措辞的不精确自动计为正文错误。

独立复核文件：[reviews/group_02.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/reviews/group_02.json)。主代理核对原始文本后汇总，详情见 [semantic_reviews.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/runs/real_mem0_v3_stability_20261104_once/semantic_reviews.json)。

不确定性不作为自动错误。raw 的上下文主体混入不等同人物虚构；引用中额外细节不等同事实正文扩写；助手讨论用户不等于用户直接自述。

本例只拆分与核查，不进行新旧事实关系判断，不修改 Mem0 或知识库，不运行完整开发子集。
