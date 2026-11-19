# v8：8 条真实记忆定向回归

## 结论

v8 在本次瑜伽案例中保留了析取整体，没有重复 v7 的两个确定分支；在饮酒和运动偏好案例中保留原文的谓词与明确因果关系。但波斯猫案例仍丢失 `while`，也发现支持说明越界及消歧不足。**v8 仍不能当作语义可靠的自动拆分器。**

8 条分别调用 1 次，均通过结构、身份与逐字引文检查；语义判断为 AI 初审，待人工确认。此前这 8 条的 v6/v7 问题直接用于 v8 规则设计，是定向回归，不是独立验证，也不能计算总体错误率或证明稳定性。v6/v7/v8 各一次输出，模型修订与服务端采样默认值不明，观察不能单独归因于提示词。此次不修补、不重试、不调整冻结提示词。

## 设置与审计

逐字复用 [v6 输入](../v6_real_dev_20261109_01_once/REPORT.md)，使用 `qwen-plus`、未显式设置生成参数，每条一次客户端请求、SDK 重试关闭。提示词已在调用前保存在 [frozen_prompt.txt](frozen_prompt.txt)，model 原始响应与报告分别存于每个 case 目录；实际参数与完成情况见 [attempt.json](attempt.json)、[batch_completion.json](batch_completion.json)。[audit.py](audit.py) 离线比对 v6 与 v8 的输入字节、提示词哈希，并重放每条原始响应；确认 8 个接受结果可复现。只验证格式与来源子串，不能验证语义。

## 逐例初步观察

| 案例 | 输出数量 | 初步观察 |
| --- | --- | --- |
| [人物与关系](case_01_multi_person/result.json) | 1 | 对同事和朋友的感谢及两个人名均保留为一条；上下文用 assistant 回述为用户归属提供线索，不等于用户本人逐字确认这些对象。粒度较粗。 |
| [瑜伽析取](case_03_assistant_yoga/result.json) | 1 | `Practices or is open` 完整保留且 pending 指明分支未知，避免 v7 拆为两个确定句。context 对 transition 的关联、assistant 建议和用户自述边界仍须评估；assistant 建议不证明用户实践。 |
| [否定与原因](case_04_negative_relative/result.json) | 1 | 原记忆中的 dislike、because 及 while 连同原因整体保留，不再将 raw 改为 v6 的 avoid。context 中的因果句直接连接 avoid，supports 对 dislike/avoid 的因果“完全匹配”说法偏强，需区分来源直接表述与旧记忆。 |
| [升职时间](case_05_relative_time/result.json) | 1 | 保留 recently、职位及机构，补充主体有第一人称来源；无精确日期推断。 |
| [计划与可能性](case_06_plan_possibility/result.json) | 1 | 历史剧计划与科幻剧 possibly 均保留在一条；ctx-2 的创作控制意愿不能直接证明用户有这两项具体计划，supports 用它支持计划归属有越界风险。assistant 提问不等于用户亲口确认。 |
| [伴侣资料](case_08_partner_profile/result.json) | 2 | 日期与职业/专长分开；补充版仍写 Partner，未利用现有第一人称上下文消除归属且 pending 为空。将无时态职业片段补为 is 的时态及来源中 `keen eye for` 弱于旧文 `specializing in` 均需复核。 |
| [运动偏好](case_10_sports_preferences/result.json) | 1 | 完整保留 dislike、because 与另一偏好，避免 v6 的明确因果连接丢失；一条包含多个属性，粒度较粗；and prefers 的语法附着范围仍有歧义。 |
| [波斯猫照料](case_11_persian_care/result.json) | 3 | 欣赏、反思挑战、平衡分别出现，但原文的 **while** 在事实正文丢失；v7 曾在该次样本保留。ctx-3 是 assistant 回述/类比，supports 说它确认平衡行为的范围偏强，不能当成用户直接自述。 |

## 补充对照

另从过去下游实验中选取 3 条不在上述 8 条或原 11 条开发案例中的真实记忆，在 v8 提示词冻结后用同样输入分别运行 v4 和 v8。它们曾用于其他实验、非随机样本，不代表独立总体测试。结果见 [3 条配对对照报告](../v8_v4_unseen_cases_20261109_01_once/REPORT.md)。
