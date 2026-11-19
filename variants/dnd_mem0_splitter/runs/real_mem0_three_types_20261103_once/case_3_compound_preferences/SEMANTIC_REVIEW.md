# 样本 3：多个偏好及相关事实

本次助手逐项对照旧记忆及允许的旧来源上下文；未追加模型请求，尚未经用户确认，不是人工标准答案。

结果：qwen-plus 真实调用 1 次，重试 0 次；命令退出码 0，finish_reason=stop。返回 4 条，逐字引文 12/12 通过。程序检查通过不代表语义完全通过。

## 原始旧记忆与可靠快照

真实 memory_id：`aa764342-2fe6-4632-9efd-e5e0cc032185`。

> Recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career

选取位置：[session_006/before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_006/before.json:497)，JSON Pointer `/api_snapshot/results/54`。底层对应位置：`/database_points_with_vectors/54/payload/data`。

来源用户：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。生成会话为 session_005，快照位于目标 session_006 处理前。目标定位 ID（只用于本地来源定位）：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s005:m001`, `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s005:m004`。

实际生成返回：[session_005/add_return.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/add_return.json)，位置 `/return_value/results/1`。实际 ADD 操作也核对 ID 和完整文本；生成前快照没有此 ID，生成后、前一会话结束和目标 before 中均可对应。历史 checkpoint 对这些来源文件保存的 SHA-256 已匹配。详细字段见 [批次 provenance.json](../provenance.json)。

## 实际输入的旧上下文

输入限于这条旧记忆及下列旧 user 发言节选。未输入目标新证据、目标处理后的记忆、人工标注、预期答案或其他记忆。source_ref 保留了精确 JSON Pointer 和字符范围，speaker 均为原始 role=user；没有补造姓名。recorded_at 使用原字符串，来源没有注明时区。

- `ctx-1`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/0/content`，字符 `[0, 169)`；原始时间 `Jan 06, 2026, 17:48:59`。

> I recently spent some time at a friend's house and interacted with their Golden Retriever. It was such a gentle creature, and I found its adaptability really impressive.

- `ctx-2`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/2/content`，字符 `[0, 149)`；原始时间 `Jan 06, 2026, 17:55:15`。

> Yes, the emotional support and companionship they offer are invaluable. I think this change reflects my openness to new experiences and interactions.

- `ctx-3`：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/input.json#/raw_dialogue/4/content`，字符 `[0, 128)`；原始时间 `Jan 06, 2026, 17:59:17`。

> Absolutely, pets do offer that balance. I find their calm demeanor crucial for my active lifestyle, especially after a long day.

## 实际模型输出

| 序号 | raw_subfact（原样） | contextualized_subfact（原样） |
| --- | --- | --- |
| 1 | Recently interacted with a friend's Golden Retriever and was impressed by its gentle nature. | The user recently spent time at a friend's house and interacted with their Golden Retriever, finding it gentle and impressive in its adaptability. |
| 2 | Values adaptability, calm demeanor, and emotional support in pets. | The user values adaptability in pets (as observed in the friend's Golden Retriever), calm demeanor (cited as crucial for their active lifestyle), and emotional support (described as invaluable). |
| 3 | Is drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals. | The user is drawn to Golden Retrievers because they perceive them as compatible with their active lifestyle (where calm demeanor is crucial) and wellness goals (implied by emphasis on balance, emotional support, and integration as a step toward new experiences). |
| 4 | Is optimistic about integrating this preference as a step toward new experiences and balancing demanding career. | The user is optimistic about integrating their preference for Golden Retrievers as a step toward new experiences and interactions, and as a means to achieve balance against a demanding career. |

以上没有人工改写。见 [raw_content.txt](raw_content.txt)、[result.json](result.json)。每条 source_memory_id 均为原真实 ID；fact_index 是本次序号，不是新 Mem0 ID。

## 格式、ID 和引文检查

原有校验器在真实调用后执行严格 JSON/重复键、字段、类型、连续编号、顶层 ID/原文、事实 ID、来源 ID、每条必须含 memory 依据和逐字引文检查，全部通过。又将原始响应交给既有 MockBackend 离线重新校验，与保存结果完全一致；没有追加真实模型请求。

| 事实 | evidence 下标（从 0 开始） | 来源 | 引文 | 来源内字符范围 | 检查 |
| --- | --- | --- | --- | --- | --- |
| 1 | 0 | memory / aa764342-2fe6-4632-9efd-e5e0cc032185 | Recently interacted with a friend's Golden Retriever and impressed by its gentle nature | [0, 87) | 逐字匹配 |
| 1 | 1 | context / ctx-1 | I recently spent some time at a friend's house and interacted with their Golden Retriever. It was such a gentle creature, and I found its adaptability really impressive. | [0, 169) | 逐字匹配 |
| 2 | 0 | memory / aa764342-2fe6-4632-9efd-e5e0cc032185 | values adaptability, calm demeanor, and emotional support in pets | [89, 154) | 逐字匹配 |
| 2 | 1 | context / ctx-1 | I found its adaptability really impressive. | [126, 169) | 逐字匹配 |
| 2 | 2 | context / ctx-3 | I find their calm demeanor crucial for my active lifestyle, especially after a long day. | [40, 128) | 逐字匹配 |
| 2 | 3 | context / ctx-2 | Yes, the emotional support and companionship they offer are invaluable. | [0, 71) | 逐字匹配 |
| 3 | 0 | memory / aa764342-2fe6-4632-9efd-e5e0cc032185 | drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals | [156, 247) | 逐字匹配 |
| 3 | 1 | context / ctx-3 | Absolutely, pets do offer that balance. I find their calm demeanor crucial for my active lifestyle, especially after a long day. | [0, 128) | 逐字匹配 |
| 3 | 2 | context / ctx-2 | Yes, the emotional support and companionship they offer are invaluable. I think this change reflects my openness to new experiences and interactions. | [0, 149) | 逐字匹配 |
| 4 | 0 | memory / aa764342-2fe6-4632-9efd-e5e0cc032185 | optimistic about integrating this preference as a step toward new experiences and balancing demanding career | [249, 357) | 逐字匹配 |
| 4 | 1 | context / ctx-2 | Yes, the emotional support and companionship they offer are invaluable. I think this change reflects my openness to new experiences and interactions. | [0, 149) | 逐字匹配 |
| 4 | 2 | context / ctx-3 | Absolutely, pets do offer that balance. | [0, 39) | 逐字匹配 |

[verification.json](verification.json) 保存全部检查及 supports 原文。引文匹配只证明 quote 出现在所声明来源中，不能证明 supports 的解释、事实完整性、人物归属或扩写必要性。

## 模型返回的 pending_confirmations

子事实 1：

`[]`。这不表示没有语义问题。

子事实 2：

`[]`。这不表示没有语义问题。

子事实 3：

`[]`。这不表示没有语义问题。

子事实 4：

`[]`。这不表示没有语义问题。

## 本次助手的初步语义复核

四条 raw 基本覆盖旧记忆四个分号段；上下文版本改变了印象所指特征，并出现 perceive 改写和 implied 推断，部分扩写虽然有旧引文仍超出必要补足。

| 维度 | 初步检查 |
| --- | --- |
| 人物与主语 | raw 大体保留省略主语，contextualized 增补 The user。ctx-1 中的 I、ctx-2 中的 I think、ctx-3 中的 I find，结合同一用户同一生成会话的 ID/ADD/快照链，为这一归属提供依据；没有单凭记忆所属用户默认主语，也未补入姓名。朋友仍是犬的主人，没有改成用户拥有 Golden Retriever。 |
| 时间 | Recently 保留，没有把原始发言时间 Jan 06, 2026 当成实际互动日期。recently 的精确时间范围未确定，模型没有主动标记。 |
| 条件、否定与情态 | 原文无显式 if 条件或直接否定句。values、drawn to 和 optimistic 保留为偏好、吸引理由及乐观态度，没有改成已整合偏好或已实现职业平衡。 |
| 覆盖与粒度 | raw 保留相遇与温顺印象、三个受重视的特征、吸引理由、乐观态度与两个目标。第 2 条仍合并三个偏好，第 4 条仍合并两个目标，不能认定已是最细原子粒度。 |
| 语气 | 第 3 条补充版本确实将直接给出的 compatibility 理由改为 because they perceive them as compatible。原句本身包含偏好态度，但新增 perceive 是否改变其中理由的断言力度，需用户确认；程序检查无法判定。 |
| 信息增加与变更 | 第 1 条由 impressed by its gentle nature 改为 finding it gentle and impressive in its adaptability，印象的对象从温顺转到了适应性。来源 ctx-1 确有适应性印象，但不能静默替换原记忆的关系。第 3 条新增 wellness goals (implied by ...) 的解释；旧记忆已明确写 wellness goals，后面的推导并非必要。第 4 条增加 interactions，属于有旧来源但原文未明确展开的细节。 |
| 引文支持边界 | 第 2 条 evidence 中的 supports 把 especially after a long day 解释为 post-work recovery，来源未明确说明下班或恢复；该推断只出现在 supports，不在主事实文本。第 3 条 supports 把 openness 与 wellness goals 对齐，也不由引文字面自动推出。 |

具体问题位置：

- **印象对象发生变化**（`$.facts[0].contextualized_subfact`）：原文因温顺而留下印象；补充版本把 impressed 的特征转成 adaptability，并添加朋友家这一有来源但非必要的地点。
- **有来源的超范围扩写**（`$.facts[1].contextualized_subfact`）：新增观察例子、crucial 和 invaluable 等上下文展开，三个偏好仍合并为一条。
- **引文解释越界**（`$.facts[1].evidence[2].supports`）：after a long day 不自动推出 post-work recovery；程序仅验证 quote 存在，不验证 supports 的这层解释。
- **perceive 语气变化及额外推断**（`$.facts[2].contextualized_subfact`）：加入主观 perceive；并用 implied by 对 wellness goals 进行额外解释，尽管旧记忆已经明示 wellness goals。
- **有来源的范围展开**（`$.facts[3].contextualized_subfact`）：增加 interactions；是否允许在补足 this preference 之外增加此细节需确认。

## 待人工确认

1. 第 1 条补充版本把温顺印象转成适应性印象，是否判为语义改变；旧记忆和旧上下文在此处的差异也需保留为待确认。
2. 第 3 条 because they perceive them as compatible 是否允许作为原文 compatibility 理由的释义。
3. 第 3 条 implied by 及其 wellness goals 推导，以及第 2 条 supports 中 post-work recovery 的解释是否应排除。
4. 第 2 条三个偏好及第 4 条两个目标是否需要更细拆分；本次没有重新调用模型。
5. recently 的精确范围、是否接受朋友家和 interactions 等有来源的扩写，以及补充版本允许的最小范围。

本段待确认项是本次助手初审新增，和模型 pending_confirmations 分开保存。未据此修补模型输出或重发请求。

## 调用记录与范围

已执行命令：

```bash
python3 -B run_real.py --input runs/real_mem0_three_types_20261103_once/inputs/case_3_compound_preferences.json --run-dir runs/real_mem0_three_types_20261103_once/case_3_compound_preferences
```

配置沿用项目 .env.local 及已有进程覆盖规则；不输出密钥、完整配置或环境。system 提示词逐字复用 DESIGN.md，见 [prompt.txt](prompt.txt)。SDK max_retries=0、HTTP 重定向关闭，每个后端实例最多一次 create。token 元信息见 [response_metadata.json](response_metadata.json)，它不是质量评分。

本次仅拆分与检查。未判断新旧事实关系，未连接或修改 Mem0，未执行知识库新增、更新或删除，未运行完整开发子集，未修改已有实现或历史结果。
