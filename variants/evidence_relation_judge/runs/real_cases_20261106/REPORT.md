# 组件一：三个真实案例的固定版本测试

**语义分析是待用户确认的初步判断，不是正确率评估。** 本次只使用已保存的 v4 结果和新证据。每个案例均只有一个 v4 子事实，故各调用一次、总计三次 `generate`；没有重新拆分或重试。各案例的 `*_run.json` 保存完整输入、实际消息（包括当前最终版系统提示词）、原始输出、解析候选、原组件校验和逐次指标；`offline_literal_audit.json` 只是补充逐项字面检查，不替换原组件结果。`manifest_before.json` 记录运行前代码、提示词、输入和模型文件标识；`completion.json` 记录运行后哈希。

来源核对：三个旧记忆 ID、原文与对应用户的 before 快照匹配；新证据与指定原始对话的文本、说话人、时间匹配；旧上下文与数据集指定字符范围匹配。原始文件的哈希均与已保存来源记录一致。三条拆分结果均记录相同 v4 提示词 SHA-256，且通过 v4 校验器；未重新运行拆分器。已有时间信息为 null；来源中的记录时间不当作事件生效时间。

提示词 SHA-256 为 `14dcec1be517b43005549252849f2ab1f482ae7a28d100d611ea1dc517ea84ee`；实际三次消息的系统提示词与之逐字一致。使用 `/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_relation_judge/model/Qwen3-8B`，`local_files_only=True`、本地离线环境，CUDA BF16 成功；模型只加载一次，加载耗时 7.502 秒。此轮代码和提示词均未修改。保存了模型配置/索引哈希及全部模型文件大小，而不是重新计算 16GB 权重的完整哈希。

各结果失败不等于模型主动输出 `uncertain`。对于失败案例，下文的标签只是解析出的模型原始候选，并未通过组件校验。字面引文匹配不证明语义正确。PyTorch 显存是本进程峰值，设备总量包含其他进程。

## skydiving

- 旧记忆 ID：`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`；事实 ID：`1`
- 旧子事实：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being
- 新证据：
  - `dialogue-0`：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
  - `dialogue-2`：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
  - `dialogue-8`：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.
- 原始候选标签：`possible_change`；组件状态：`error`
- 候选影响片段：I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
- 旧引文：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being
- 新引文（`dialogue-0`）：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
- 模型理由：New evidence shows the user tried simulated skydiving and found it thrilling, indicating a possible change in their attitude towards extreme sports.
- 模型待确认问题：
  - Does the user's recent experience with simulated skydiving indicate a change in their attitude towards extreme sports?
  - Is the user's commitment to safety and well-being still a factor in their attitude towards extreme sports?
- 格式与校验：失败，candidate fragment not found in this fact memory evidence；补充字面诊断中的旧/新引文均匹配；语义未自动校验。
- 模型调用 1 次；推理 13.308 秒；allocated 峰值 15.55 GiB，reserved 峰值 15.67 GiB；EOS：True。

初步分析：模型原文准确写出 simulated，并未把体验直接描述成真正跳伞；但仅凭模拟体验愉快便推断对“极限运动”的态度可能变化，有过度推广风险，尤其未证明对真正跳伞或其高伤害风险的态度发生变化。原文只说 simulated，并未明确写 indoor，不应自行增加“室内”。模型提出要确认对极限运动的态度，这是有用的问题；它还问是否仍重视安全，而 dialogue-8 已明确说仍优先考虑安全，问题未充分利用给定证据。该事实关于安全的部分不应因模拟体验而被直接认定改变。候选影响片段却摘自新证据而不是旧记忆，程序正确拒绝。

## promotion

- 旧记忆 ID：`e13b825e-7ec7-4760-821e-0581d8da5650`；事实 ID：`1`
- 旧子事实：Works at Historical Productions Ltd. as a Director
- 新证据：
  - `dialogue-0`：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!
- 原始候选标签：`possible_change`；组件状态：`ok`
- 候选影响片段：Works at Historical Productions Ltd. as a Director
- 旧引文：Works at Historical Productions Ltd. as a Director
- 新引文（`dialogue-0`）：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!
- 模型理由：The new evidence indicates a promotion to 'lead director', which suggests a change in the user's position at Historical Productions Ltd.
- 模型待确认问题：
  - Is the promotion to 'lead director' a direct replacement for the previous role of 'Director'?
  - Is there any indication that the previous role of 'Director' is no longer held by the user?
- 格式与校验：通过；补充字面诊断中的旧/新引文均匹配；语义未自动校验。
- 模型调用 1 次；推理 10.044 秒；allocated 峰值 15.49 GiB，reserved 峰值 15.67 GiB；EOS：True。

初步分析：职位从 Director 晋升为 lead director 有直接文字依据，`possible_change` 合理；原文仍明确同一家雇主，模型理由识别了职位变化，没有直接声称换雇主。问题保留了原职位与新头衔关系的不确定性。但候选影响片段覆盖整条旧事实，包括同一雇主，没把可能变化的职位与继续工作的雇主内容局部区分开；字面检查通过不代表这个范围恰当。

## career_history

- 旧记忆 ID：`05afde13-35bd-4d26-bbae-6de427d58db1`；事实 ID：`1`
- 旧子事实：Previously worked as a senior developer in Blockchain Tech
- 新证据：
  - `dialogue-0`：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- 原始候选标签：`uncertain`；组件状态：`error`
- 候选影响片段：previously worked as a senior developer in Blockchain Tech
- 旧引文：Previously worked as a senior developer in Blockchain Tech
- 新引文（`dialogue-0`）：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.
- 模型理由：The new evidence does not provide information about the user's employment history or any changes to it. It only mentions the user's current feelings about their consulting firm securing clients.
- 模型待确认问题：
  - Is the 'previously worked' in the memory referring to a role that ended before the current employment at Blockchain Tech?
  - Does the new evidence provide any information about the user's employment history or changes to it?
- 格式与校验：失败，candidate fragment not found in this fact memory evidence；补充字面诊断中的旧/新引文均匹配；语义未自动校验。
- 模型调用 1 次；推理 11.245 秒；allocated 峰值 15.51 GiB，reserved 峰值 15.67 GiB；EOS：True。

初步分析：咨询公司获得首批客户并不说明历史上的高级开发者经历失效；模型没有声称该经历被推翻，且注意到旧记忆的 previously 与 2025 年上下文 I work 的时间对齐问题。新证据不仅谈“感受”，还明确提到其咨询公司获得首批客户，理由用 only mentions feelings 表述过窄；第二个问题询问新证据是否涉及职业经历，较宽泛。第一个问题称 Blockchain Tech 为“current employment”，可能错误地把旧上下文当作新证据时点的当前状态；是否仍就职并未证明。旧引文及新引文虽逐字匹配，候选片段首字母由 `Previously` 改成 `previously`，不再是旧引文的精确子串，故校验失败。

## 限制与下一步建议

三例各仅一条 v4 子事实；因此本次能够观察复合事实内部的职位、雇主和安全等内容，但没有测试多条独立旧子事实之间是否误判。三个案例中有两次片段逐字校验失败，分别是复制了新证据和改变大小写；一次通过但候选范围覆盖了未变的雇主。建议在下一轮受控实验中优先考虑提示词示例或输出约束，强调旧原文逐字片段、局部属性及模拟与真实活动的区别；对大小写等字面失败如何处理也应先设计与人工审查，不能简单放宽后当成正确。本轮没有修改任何提示词或判断代码。是否调整应根据用户确认和更多有代表性的案例决定。

ERASE 第一轮的 `No Change` 表示新信息未显示影响旧事实；本组件的 `uncertain` 是本实现为证据不足或条件不明新增的设计，不能归属于 ERASE 原标签。
