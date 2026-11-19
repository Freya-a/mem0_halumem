# v7 与 v6：真实记忆定向回归初审

**结论：v7 在本次部分关系样本上有改善，但出现或保留了严重语义问题，还不应直接作为可靠拆分器使用。** 语义结论均为 AI 初审，待人工确认。格式通过不能证明语义正确。

## 设置和限制

选用 [v6 上次验证](../v6_real_dev_20261109_01_once/REPORT.md) 的同 8 条真实开发子集记忆和来源上下文，输入逐字一致；每条对 `qwen-plus` 发起一次 v7 模型请求，无 SDK 重试、无人工修补、无新证据或评审传入。生成参数未显式设定，供应商默认采样、具体模型修订及内部行为未知，因而 v6/v7 仅为单次观察，不能单独归因提示词、代表稳定效果或推断总体质量。样本为 v7 设计所依据的定向回归案例，不是独立测试集。

v6 程序接受 7/8、拒绝 1/8；v7 接受 8/8。程序仅检查结构、ID、逐字引文来源，不检查原子性、关系或语义。一条 v7 语义错误案例仍可通过程序，见瑜伽案例。[audit.py](audit.py) 对每条保存响应重新运行已有校验，核对输入与 v6 字节一致、原始响应与 result 一致及提示词哈希一致；结果为 8/8 复现。

## 逐例观察

| 案例 | v6 → v7 程序 / 事实数 | 主要观察（AI 初审，待人工确认） |
| --- | --- | --- |
| [人物与关系](case_01_multi_person/result.json) | 通过 2 → 通过 2 | 继续分开同事与朋友；v7 在补充版中确定“用户”，却仅给 memory 引文，未引用可用于主体归属的上下文；memory supports 说用户表达感谢，超出了该引文单独能证明的原始发言归属。对时间、身份的 pending 与补充版的确定程度也值得核对。 |
| [瑜伽与来源角色](case_03_assistant_yoga/result.json) | 拒绝 → 通过 2 | **仍有严重错误。** 原文为“练习或愿意尝试”，v7 把两分支分别输出为“练习”和“愿意尝试”的确定事实，不能从析取推出两个分支均成立；pending 又说分支未确定，正文与之不一致。`career transition` 及 `user` 被补出但无对应 context 引文，且 pending 又称 transition 的指代未定。v6 的候选也有情态升级和非逐字引文，因此不能把 v7 程序通过解读为该案例已修复。 |
| [否定与原因](case_04_negative_relative/result.json) | 通过 2 → 通过 1 | v7 保留原文“不喜欢”及 because/while 原始关系，不再用 v6 的 `Avoids` 替换原 raw 谓词。v7 的 memory supports 把记忆引文写成用户直接陈述，原记忆本身不能单独证明原始说话人；context 引文另提供第一人称来源。 |
| [相对时间与升职](case_05_relative_time/result.json) | 通过 1 → 通过 1 | 两版均保留 recently、职位和机构，并引用用户自述补足主体；没有推出精确事件日期。 |
| [计划及可能性](case_06_plan_possibility/result.json) | 通过 2 → 通过 2 | v7 仍保留两项计划及 possibly，但补出用户主体而未引用 assistant 来源；assistant 问句能说明其对用户的归属，不能独立证明用户亲口确认。groundbreaking 修饰第二分支与否仍可复核。 |
| [伴侣资料](case_08_partner_profile/result.json) | 通过 2 → 通过 2 | 出生日期与职业/专长仍分开；v7 只引用 memory，未列补足“用户的伴侣”的 context，也未披露来源 `keen eye for` 与旧记忆 `specializing in` 的强度差异；无时态职业片段被写成 `is`，时间定位需复核。 |
| [运动偏好](case_10_sports_preferences/result.json) | 通过 3 → 通过 2 | v6 将不喜欢与其原因拆散，v7 第 1 条在正文保留 `because` 关系，同时第 2 条保留另一偏好。`and prefers` 是否也处于 because 范围仍有歧义，v7 未在 pending 说明；第 2 条截短 context 引文本身没有出现说话主体。 |
| [波斯猫与照料](case_11_persian_care/result.json) | 通过 5 → 通过 2 | v7 第 2 条正文保留 `while` 所连接的反思与平衡；v6 将两者拆开。v7 的 assistant 引文 supports 将回述/类比写成用户既有行为模式，超过这段助手表述能独立证明的范围；未披露直接用户来源对平衡活动支持的缺口。较粗粒度需结合下游用途评估。 |

## 代码和后续

v7 保持 DnD 风格单调用配对及现有 schema，提示词新增谓词、情态、关系、引文和待确认一致性规则；[v7 入口](../../prompt_versions/v7_dnd_relation_preserving/v7_splitter.py) 和 [提示词](../../prompt_versions/v7_dnd_relation_preserving/prompt.txt) 独立保存，v6 未修改。当前实验提示词在调用前冻结，未据输出改写或重跑。

接下来需要重点处理析取分支不可单独断言、补足主体必须附相应来源、以及 supports 超出单条引文的问题；修改后除复跑这些回归案例，还须使用从未用于设计的真实记忆作独立评估，并进行人工语义复核。不应把格式 8/8 当作语义通过率。
