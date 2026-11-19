# 样本 1：多人物

本次助手逐项对照旧记忆及允许的旧来源上下文；未追加模型请求，尚未经用户确认，不是人工标准答案。

结果：qwen-plus 真实调用 1 次，重试 0 次；命令退出码 0，finish_reason=stop。返回 1 条，逐字引文 3/3 通过。程序检查通过不代表语义完全通过。

## 原始旧记忆与可靠快照

真实 memory_id：`93d9e572-f052-41b6-9387-9e7583b8c3ab`。

> Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition

选取位置：[session_009/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json:542)，JSON Pointer `/api_snapshot/results/59`。底层对应位置：`/database_points_with_vectors/59/payload/data`。

来源用户：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。生成会话为 session_008，快照位于目标 session_009 处理前。目标定位 ID（只用于本地来源定位）：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008:m000`。

实际生成返回：[session_008/add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/add_return.json)，位置 `/return_value/results/27`。实际 ADD 操作也核对 ID 和完整文本；生成前快照没有此 ID，生成后、前一会话结束和目标 before 中均可对应。历史 checkpoint 对这些来源文件保存的 SHA-256 已匹配。详细字段见 [批次 provenance.json](../provenance.json)。

## 实际输入的旧上下文

输入限于这条旧记忆及下列旧 user 发言节选。未输入目标新证据、目标处理后的记忆、人工标注、预期答案或其他记忆。source_ref 保留了精确 JSON Pointer 和字符范围，speaker 均为原始 role=user；没有补造姓名。recorded_at 使用原字符串，来源没有注明时区。

- `ctx-1`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/4/content`，字符 `[0, 105)`；原始时间 `Mar 01, 2026, 07:11:33`。

> Absolutely, my friends and colleagues were instrumental in this transition. Their support was invaluable.

- `ctx-2`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/8/content`，字符 `[0, 105)`；原始时间 `Mar 01, 2026, 07:16:19`。

> The support I received was incredible. Susan, Daniel, and Joshua really helped me see things differently.

## 实际模型输出

| 序号 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- |
| 1 | Susan, Daniel, and Joshua provided instrumental support during the user's career transition. | Susan, Daniel, and Joshua provided instrumental support during the user's career transition; the user described their support as 'invaluable' and said it helped them 'see things differently'. |

以上没有人工改写。见 [raw_content.txt](raw_content.txt)、[result.json](result.json)。每条 source_memory_id 均为原真实 ID；fact_index 是本次序号，不是新 Mem0 ID。

## 格式、ID 和引文检查

原有校验器在真实调用后执行严格 JSON/重复键、字段、类型、连续编号、顶层 ID/原文、事实 ID、来源 ID、每条必须含 memory 依据和逐字引文检查，全部通过。又将原始响应交给既有 MockBackend 离线重新校验，与保存结果完全一致；没有追加真实模型请求。

| 事实 | evidence 下标（从 0 开始） | 来源 | 引文 | 来源内字符范围 | 检查 |
| --- | --- | --- | --- | --- | --- |
| 1 | 0 | memory / 93d9e572-f052-41b6-9387-9e7583b8c3ab | Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition | [0, 105) | 逐字匹配 |
| 1 | 1 | context / ctx-1 | Absolutely, my friends and colleagues were instrumental in this transition. Their support was invaluable. | [0, 105) | 逐字匹配 |
| 1 | 2 | context / ctx-2 | The support I received was incredible. Susan, Daniel, and Joshua really helped me see things differently. | [0, 105) | 逐字匹配 |

[verification.json](verification.json) 保存全部检查及 supports 原文。引文匹配只证明 quote 出现在所声明来源中，不能证明 supports 的解释、事实完整性、人物归属或扩写必要性。

## 模型返回的 pending_confirmations

子事实 1：

`[]`。这不表示没有语义问题。

## 本次助手的初步语义复核

保留三个人名、支持行为及职业转变期间这一范围；遗漏朋友和同事关系，并加入了有旧来源的评价及效果。

| 维度 | 初步检查 |
| --- | --- |
| 人物 | Susan、Daniel、Joshua 均保留，没有交换姓名，也未擅自给每个人分配朋友或同事身份；但 Friends and colleagues 这一组关系描述从 raw 和补充版本中均消失，只有 evidence.quote 保留，事实文本仍有遗漏。 |
| 主语与受益人 | raw 增补 the user's career transition。旧文本没有显式写出受益人；旧 user 发言中的 my friends and colleagues、I received、helped me 为上下文版本归到同一发言者提供依据。raw 是否允许这样借助上下文明确受益人，仍需确认。 |
| 时间 | 保留过去式 provided 和 during career transition，没有添加日期或永久持续断言。 |
| 条件、否定与情态 | 原文无显式条件或否定句。instrumental support 的强度保留，没有把支持改成计划或可能；保留三人合述，没有强拆成三人各自独立完成整个支持过程。 |
| 语气 | 核心支持行为仍直接陈述，没有改成用户认为或用户感到三人提供了支持；新增的 user described、said 用来引入原文没有的上下文评价及效果。 |
| 引文支持边界 | invaluable 和 see things differently 确实出现在允许的旧上下文中，但不是理解原命题所必需的指代、时间等补充；有来源不等于符合本次最小补充范围。 |

具体问题位置：

- **旧关系信息遗漏**（`$.facts[0].raw_subfact / contextualized_subfact`）：Friends and colleagues 没有进入任何事实文本；引文含有这段文字不能代替子事实保留它。
- **有来源的超范围扩写**（`$.facts[0].contextualized_subfact`）：新增 invaluable 评价和 helped them see things differently 效果，均来自旧上下文，但超出必要上下文补足。
- **raw 来源边界待确认**（`$.facts[0].raw_subfact`）：the user's 明确受益人主要由来源上下文支持，旧记忆本身未显式说明。

## 待人工确认

1. 事实文本遗漏朋友和同事这一组关系描述是否判为必须修正的漏项。
2. 是否允许补充版本加入有来源但原记忆没有的支持评价及效果。
3. raw 中增补 the user's 是否超出仅依据 memory_text 的要求。
4. 输入没有提供三人各自属于朋友还是同事的明确映射；需要逐人关系时须另找可靠旧来源，不能自行分配。

本段待确认项是本次助手初审新增，和模型 pending_confirmations 分开保存。未据此修补模型输出或重发请求。

## 调用记录与范围

已执行命令：

```bash
python3 -B run_real.py --input runs/real_mem0_three_types_20261103_once/inputs/case_1_multi_person.json --run-dir runs/real_mem0_three_types_20261103_once/case_1_multi_person
```

配置沿用项目 .env.local 及已有进程覆盖规则；不输出密钥、完整配置或环境。system 提示词逐字复用 DESIGN.md，见 [prompt.txt](prompt.txt)。SDK max_retries=0、HTTP 重定向关闭，每个后端实例最多一次 create。token 元信息见 [response_metadata.json](response_metadata.json)，它不是质量评分。

本次仅拆分与检查。未判断新旧事实关系，未连接或修改 Mem0，未执行知识库新增、更新或删除，未运行完整开发子集，未修改已有实现或历史结果。
