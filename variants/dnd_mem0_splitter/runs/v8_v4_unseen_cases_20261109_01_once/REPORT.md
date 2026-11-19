# v4 / v8：3 条新选真实记忆配对初审

v8 提示词冻结后，从既有下游时序实验保存的输入中选择 3 条不在之前 11 条开发案例里的真实记忆。两版输入逐字段相同，各调用一次 `qwen-plus`；两版依次交替调用，SDK 重试关闭，不修补；服务端具体模型修订和默认采样未知。它们未用于本次 v8 提示词修改，但之前用于其他下游实验，样本为定向选取、非随机且仅 3 条，因此不是严格独立总体评估或质量排名。

6 次均通过 schema/ID/逐字引文检查；**程序检查不证明语义正确**。下面均为 AI 初步观察，待人工确认。历史输入与来源位置、冻结 prompt 哈希、模型调用及响应分别保存在 [manifest.json](manifest.json)、[attempt.json](attempt.json)、各 case 目录；[audit.py](audit.py) 离线重放结果并核对来源输入与哈希。

| 案例 | v4 与 v8 本轮观察 |
| --- | --- |
| 职业：[v4](promotion/v4/result.json) · [v8](promotion/v8/result.json) | 两版均保留公司和职位，从对应第一人称用户来源补足主体。没有观察到明显命题差异；各只运行一次。 |
| 极限运动：[v4](skydiving/v4/result.json) · [v8](skydiving/v8/result.json) | 两版都把不喜欢、高风险、与安全承诺的冲突作为一条保留，并引用用户来源补主体。来源直接把高风险作为“避免”的原因，旧记忆则将其关联到“不喜欢”；v8 的 supports 把 dislike/avoid 一并说成被来源明确因果连接，偏强；v4 的“confirms causality”也要审视其所指范围。 |
| 过去职业：[v4](career_history/v4/result.json) · [v8](career_history/v8/result.json) | v4 raw 改写为 `Worked ...`，未原样保留 `Previously`；v8 保留 `Previously worked`。两版均将用户的现在时历史发言与旧记忆的过去表述留作时间对齐问题；记录时间是发言记录时间，并非职位开始或结束日期。v8 pending 的“没有说明 Sep 05, 2025 是否为记录时间”等表述与输入中明确的 `recorded_at` 字段不够一致，应人工复核。 |

这 3 条中 v8 未出现瑜伽式析取错误，但它们不包含同类析取，不能检验该问题是否泛化解决。更多不同结构的未参与调整案例和人工语义标注仍然必要。
