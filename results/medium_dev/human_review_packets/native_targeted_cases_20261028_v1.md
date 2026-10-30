# 原生 Mem0 定向案件：供人工核验

状态：**全部待用户人工复核**。来源为 `williams_native_prefix5_20261028_v3` 的已保存原始对话、完整快照、模型计划和操作日志；本整理未重新运行模型，也未修改原运行结果或审核结论。原始会话和 dialogue 索引均为零基；原对话时间未提供时区，下面保留原始表示。

## 案件概览

| 案件 | 用户／原始会话 | 审核目标 | 定向复核对象 | 初步状态 |
|---|---|---|---|---|
| A | Martin `2f1f897e-d67f-dbc5-6a7b-b7634a9e294f` / `sessions[8]` | 第8条 | 极限运动的高受伤风险理由 | 具体理由部分受损候选；安全顾虑有较宽的改写 |
| B | Williams `1b846c59-456e-9550-dffd-4d23f1eca81f` / `sessions[6]` | 第14条 | 喜欢波斯猫的平静、优雅理由 | 平静理由受损候选；高贵和历史喜好部分保留 |
| C | Donald `348492a7-cfe4-ee1d-73c3-c276d6ba8277` / `sessions[7]` | 第24条共享会话中的保护候选 | 原 Blockchain Tech 高级开发人员历史 | 雇主与职级细节受损候选；技术工作经历的概括保留 |
| D | 同一 Donald / `sessions[5]` | 第22条 | Sandra、Mary 在转型期间的集体支持新事实 | 新事实未保存候选；**不自动判为旧知识损伤** |

A、B、C 分属三个不同的“用户＋会话”，每项均关联到各自一条已记录的实际 UPDATE。D 与 C 虽属同一用户，却是不同会话；D 中 Sandra 与 Mary 的两条旧关系属于同一次会话上下文，不当作两次独立错误。目标第7、10条的前置状态另附于文末。

这里的“真实受损候选／转存或改写后保留／原本未入库／证据不足”是供你选择的审查区分，并非已确认标签；同一条复合记忆可以部分受损、部分保留。本批是按已有发现定向抽取的案件，**不构成总体错误率**。

## A｜Martin：高受伤风险的历史理由

**原始旧事实。** `/sessions/2/dialogue/6`，用户，Sep 06, 2025, 22:52:30：

> I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.

中文：他过去因**受伤风险高**回避包括跳伞在内的极限运动，并重视安全和健康。来源：[旧会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json)。

**新证据。** `/sessions/8/dialogue/0、2、8`：用户称最近在团建中尝试模拟跳伞、意外享受刺激，更愿意尝试新事物，并说 “I still prioritize safety, of course.” 这是模拟体验和当前态度；不能自动推断他不再担心真实极限运动受伤，或已享受所有极限运动。来源：[目标会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json)。

**更新前是否存在。** 存在，完整 before 为116条。ID `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`：

> Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

**模型计划与实际操作。** 模型计划用临时 ID `5` 对上述真实 ID 执行 UPDATE，旧文本与 before 一致；实际 history sequence `187` 记录了同一 ID 的 UPDATE，前后文本与完整快照一致。新文本完整为：

> Previously avoided extreme sports due to safety concerns, but recently tried simulated skydiving at a team-building event and is now more open to trying new things and extreme sports; finds adrenaline rush from extreme sports enjoyable and creatively stimulating; values safety while engaging in thrilling activities

**更新后整体及初步判断。** 完整 after 为120条；相关旧 ID 现在包含“过去因安全顾虑回避”和“重视安全”，所以**安全顾虑／原则有较宽改写保留**。对整个 after 的相关内容核对未找到针对极限运动的“受伤风险高”或等价的具体理由；**具体历史理由可能真实受损**，待你判断“一般安全顾虑”能否满足保护要求。新文本把开放尝试新事物扩写为更开放尝试极限运动、享受极限运动，范围是否超过原话也请单独核验。实际 UPDATE 指向该 ID，故有操作级证据，不只是前后快照推测。

证据：[before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json) · [after.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/after.json) · [完整模型计划](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/full_operation_plan.json) · [实际操作](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/actual_operations.json)。

## B｜Williams：波斯猫平静与优雅的理由

**原始旧事实。** `/sessions/2/dialogue/6`，用户，Sep 06, 2025, 22:24:16：

> I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.

中文：他喜欢波斯猫，理由包括高贵、**平静的性情**，以及它们带来的优雅和历史感。来源：[旧会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_003/input.json)。

**新证据。** `/sessions/6/dialogue/0、2`：用户看了波斯猫纪录片，对其历史血统和王室关联的欣赏加深，也考虑维持高贵外观的实际养护挑战。原话没有撤销对其平静性情或优雅的欣赏。来源：[目标会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/input.json)。

**更新前是否存在。** 存在，完整 before 为94条。ID `eef34a57-c82a-4995-877d-66b54b9589da`：

> Likes Persian cats because of their regal and calm nature, elegance, and historical charm

**模型计划与实际操作。** 模型计划以临时 ID `0` UPDATE 上述真实 ID；实际 history sequence `119` 对同一 ID 执行 UPDATE。after 对应文本是：

> Has a deep admiration for Persian cats and their historical lineage and association with royalty, and reflects on the practical challenges of maintaining their regal appearance while balancing historical admiration with practical care requirements

**更新后整体及初步判断。** 完整 after 为109条。波斯猫的欣赏、历史血统和高贵外观有记录；整个 after 中未找到明确的“波斯猫性情平静”等价内容，故**平静理由为真实受损候选**。另一条关于英国短毛猫平静的记忆针对不同品种，不能代替波斯猫的事实。原有“优雅”一词也未在波斯猫记忆中明确出现；新“高贵外观”是否足以保留其含义，留待你判断。实际 UPDATE 直接覆盖旧 ID，可核对操作级证据；纪录片体验未明确绑定到最终波斯猫记忆是另一个新状态覆盖问题，不重复算作同一旧理由损伤。

证据：[before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/before.json) · [after.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/after.json) · [完整模型计划](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/full_operation_plan.json) · [实际操作](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/actual_operations.json)。

## C｜Donald：既有技术岗位的雇主和职级

**原始旧事实。** `/sessions/1/dialogue/2`，用户，Sep 05, 2025, 09:10:09：

> I work at Blockchain Tech as a senior developer.

中文：他当时在 Blockchain Tech 任高级开发人员。原话同段还分别给出月收入17,000美元和储蓄16,800美元；岗位、收入与储蓄是不同事实。来源：[旧会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_002/input.json)。

**新证据。** `/sessions/7/dialogue/0`，Jan 05, 2026, 07:43:42：

> I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.

中文：咨询公司已获得一些首批客户，用户感到宽慰并视为里程碑；这可更新当前进展，未否定此前具体工作经历。来源：[目标会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json)。

**更新前是否存在。** 存在，完整 before 为114条。ID `05afde13-35bd-4d26-bbae-6de427d58db1`：

> Previously worked as a senior developer in Blockchain Tech

该条在本会话前已经明确记为过去经历，不需要把它当成当前职位。

**模型计划与实际操作。** 模型计划以临时 ID `10` UPDATE 上述真实 ID；实际 history sequence `157` 执行同一 UPDATE，替换后为：

> Formerly worked in technology

**更新后整体及初步判断。** 完整 after 为125条；“过去从事技术工作”概括得以保留，**Blockchain Tech 雇主和 senior developer 职级不再由此条表达**。after 中还有 `BrownMichelle is a colleague at Blockchain Tech ...`，它可说明 Michelle 的同事与公司关联，不能单独证明 Donald 曾在该公司担任高级开发人员。核对整个 after 未定位到等价的“Donald 曾在 Blockchain Tech 任高级开发”陈述，因此两项具体历史细节为**部分真实受损候选**。原月收入和储蓄仍有各自记录，不与此损伤混算。实际 UPDATE 指向该 ID，有操作级证据。

证据：[before.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json) · [after.json](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/after.json) · [完整模型计划](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/full_operation_plan.json) · [实际操作](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/actual_operations.json)。

## D｜Donald 第22条：集体支持新事实未保存

**旧事实及 before。** `/sessions/1/dialogue/6` 用户称 Sandra 是朋友、共同政治观点带来伙伴感和鼓励；Mary 是密友，经常讨论政治策略。目标会话 before 中分别存在：

- `37756be3-aaee-4e1c-b8f7-a5fed3d94890`：`MooreSandra is a friend who shares political views and supports the same politician`
- `98c6916c-8aa9-4560-94ce-5697f39ac818`：`GonzalezMary is a close friend who discusses political strategies`

两条分别保存了部分旧关系，不预设完整保存旧原话中的所有支持细节。来源：[旧会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_002/input.json)。

**新证据。** `/sessions/5/dialogue/10`，用户，Dec 10, 2025, 18:27:24：

> MooreSandra and GonzalezMary have been incredibly supportive, providing encouragement and strategic advice throughout this transition.

这是两人在此次转型期间的**集体**支持，不能把所有帮助各自归给某一人。来源：[目标会话完整输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/input.json)。

**提取、计划与原生跳过。** 抽取事实中已有 `Friends MooreSandra and GonzalezMary are providing encouragement and strategic advice`。更新模型输出同一文本并计划 `UPDATE` 临时 ID `53`，同时填写的 `old_memory` 是 Mary 的旧关系。该会话旧记忆映射只有 `0–47`，其中 Mary 的真实 ID 对应临时 ID `15`，Sandra 对应 `16`；模型给出的 `53` 不在映射中。原生 runtime 记录 `Error: '53'` 并跳过该计划，没有对 `53` 对应的记忆执行操作；不能擅自把它改映射为 `15` 或补写。

**实际操作与完整 after。** history sequence `101、102` 分别对 Mary、Sandra 旧 ID 做了同文 UPDATE，两个 before 文本在 after 仍存在。完整 after 为102条；另有泛指“计划向政治领域朋友咨询意见”和“新联系人提供视角与资源”等记录，但没有定位到同时表达 **Sandra 和 Mary 在本次转型中提供鼓励及策略建议** 的等价新事实。故初步为**新增目标未保存候选**；旧关系部分有保留，不能自动把未保存的新关系判成对旧关系的损伤。

证据：[抽取事实](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/extracted_facts.json) · [模型输入输出及临时 ID 映射](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/update_model_io.json) · [完整计划](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/full_operation_plan.json) · [原生日志](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/runtime.jsonl) · [实际操作](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/actual_operations.json) · [完整 after](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_006/after.json)。

## 附：第7、10条状态替换的旧状态是否入库

**第7条，Martin / `sessions[7]`：是，存在相关旧求职阶段。** 更新前实际记忆 `e6ab178b-c0f9-4adb-bfb7-e4648617a950` 为 `Looking for a new job with better work-life balance`，本会话被召回；更新后该旧文本仍在，另新增 `Has transitioned to a new role with healthier work-life balance`。更新前还存在 `Current role is Director at Huaxin Consulting`，但该条本会话未召回，after 仍原样存在。原话在 Mar 01, 2026 确认完成此次转岗；不推断新雇主或职称。旧求职记忆未显式标注为过去，能否在下游准确消歧尚未测。完整对照：[第7条证据](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_07_evidence.json)。

**第10条，Williams / `sessions[4]`：是，存在具体旧职称。** 更新前实际记忆 `e13b825e-7ec7-4760-821e-0581d8da5650` 为 `Works at Historical Productions Ltd. as a Director`，被召回。实际 history sequence `78` 对其做同文 UPDATE；after 仍保留该文本，另以 ADD 保存 `Recently promoted to lead director at Historical Productions Ltd`。这是同一雇主的具体旧职称，不只是“从事导演工作”的宽泛概括；旧文本未显式写成历史。完整对照：[第10条证据](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_10_evidence.json)。

第7、10条新状态可以从 after 中明确看到；是否需要显式历史化旧文本以及如何用于严格纠错分母，仍待人工按统一规则裁定。以上记忆写入时间是实验执行时间，不应当作对话中的真实事件时间。
