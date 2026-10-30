# 原生Mem0开发诊断报告（24项目标）

日期：2026-10-28。run_id：`williams_native_prefix5_20261028_v3`。审核版本：`human_review_v1_20261028`。本报告为LLM辅助运行后语义诊断，尚未经用户逐项确认；不覆盖或回写已冻结的人工审核。

已完成3位用户28个完整会话、990条原始消息。Williams续跑剩余6会话，已完成5会话未重输；Martin、Donald各从独立空库运行9、8会话。模型配置、原生提示词、top-5检索及更新执行逻辑未改动；没有加入改进模块、QA或额外评判模型调用。

## 只读核查与运行可信度

[只读审计证据](../read_only_audit/result.json)确认v1/v2路径独立，均0实际写入；v3首before为空，失败启动没有污染正式知识库。已核对前5会话产物哈希、向量库、history及检查点一致，并用临时库副本核查，未改动原证据。

第2会话的UPDATE临时ID19已在提供商原始响应中，旧映射只有0–14；原生查表在操作插桩之前抛KeyError，原生逐操作捕获后跳过。SDK原始文本与Observer原样返回文本相同；冻结源码重新生成的抽取及更新提示词逐字相等，召回映射按原候选顺序生成。Observer和APIAudit只记录并原样转发参数、结果及异常；没有重写模型输出。该结论基于源码及已存数据流证据，不声称进行过一轮新的未插桩在线反事实实验。

续跑保留正常返回的原生Memory.add的实际状态及其吞掉的异常。外层严格运行器拒绝记录保存在各error.json，附observed_anomaly.json后提交带异常观测检查点；没有补写记忆、修正临时ID、回滚或重试会话。此为外层记录政策，不是原生修复。

最终检查：所有28会话实际add输入逐项等于原始dialogue的role/content，完整助手消息保留；没有把persona、memory_points、original_memories、人工审核答案、保护标签或QA答案输入被测模型，也未预填知识。所有提交哈希、会话前后连续性、history重放及磁盘副本持久化核验通过。见[runtime_verification.json](runtime_verification.json)。

## 口径与分母

原始24条按审核分为19个接受/修订主目标、4个重复确认、1个归并条目。19个是诊断子目标数，合属16个目标会话情境，存在用户内和共享会话关联，不能当19或24次统计独立实验。“完整”要求本审核核心新增语义在整个after中明确可表达；“部分”表示只保存了部分核心或缺少关键关系。补充细化不要求旧正文删除，亦不以UPDATE事件判成功。审核中另存的补充及关联方法计划单列，不回填官方分母。

| 指标 | 分子 / 分母 | 说明 |
|---|---:|---|
| 完整会话输入 | 28 / 28 | 包含原有5个已提交会话，未重输 |
| 完整原始消息 | 990 / 990 | 对照固定3用户前缀 |
| 有记录的目标会话情境 | 16 / 16 | 共同会话内的子目标共享一次输入与操作 |
| 主目标核心完整保存 | 6 / 19 | 不含重复确认或归并条目 |
| 主目标核心部分覆盖 | 12 / 19 | 不并入完整保存分子 |
| 主目标核心未保存 | 1 / 19 | 与部分覆盖区分 |
| 重复确认核心保留 | 3 / 4 | 第2、5、6、15条；不要求新增语义 |
| 关联方法计划完整保存 | 0 / 1 | 第20条，不新增独立转型样本 |
| 时间状态候选的新阶段明确保存 | 2 / 2 | 第7、10条的共同旧状态已实际入库；按整体知识判断 |
| 时间状态候选的旧当前记录显式历史化 | 0 / 2 | 旧语句仍在，不能因此断言下游时间消歧完成 |
| 更新前定位到相关旧知识片段 | 24 / 24 | 完整旧命题覆盖与相关片段不是同一指标；详见逐项限定 |
| 至少一条相关旧片段被召回 | 24 / 24 | 仅限before有相关片段的条目，不代表召回全部充分 |
| 保护候选中可定位相关存量 | 167 / 176 | 含复合候选的部分覆盖及跨目标重复 |
| 确认存量部分损伤 | 3 / 167 | 分母仅可定位存量候选；不是全部候选均完整入库 |
| before未定位保护候选 | 9 / 176 | 不判保留成功或本次损伤 |
| 计划变更实际落地 | 617 / 625 | 具有文本的ADD/UPDATE/DELETE，一一对应核验；NONE另计 |
| 计划变更未落地 | 8 / 625 | 4个会话的原生无效临时ID；实际额外未计划操作0项 |
| 含计划/实际差异的会话 | 4 / 28 | 异常均保留实际状态并标记 |
| 同文UPDATE | 180 / 215 | 文本未变，向量及元数据仍可能被写入；不当作语义更新成功 |

保护计数按“目标×保护候选”记账，不是唯一事实数；共176行、116种原始保护表述，后者仍非语义唯一事实数。完整逐条before/after/召回ID见[protection_review.md](protection_review.md)和[protection_observations.json](protection_observations.json)。确认损伤还按实际用户、会话及记忆ID去重列在下文。

第7和10条为预指定时间状态替换候选，两者before均有相关旧当前阶段。它们的新阶段保存与旧当前记录显式历史化分别评价；本次只做单方法开发诊断，没有多方法共同快照比较。第24条的旧获客计划不能推导“尚无任何客户”，不加入严格纠错分母。

## 24项目标汇总

|序号|用户 / 原始会话|审核类型|新状态判断|before相关ID / 已召回|保护损伤 / 可定位候选|
|---:|---|---|---|---:|---:|
|[1](#target-1)|Martin s4|修订后接受|核心新状态完整保存|1 / 1|0 / 6|
|[2](#target-2)|Martin s5|重复确认|重复确认核心保留|3 / 3|0 / 6|
|[3](#target-3)|Martin s5|修订后接受|核心新状态部分覆盖|4 / 4|0 / 7|
|[4](#target-4)|Martin s6|修订后接受|核心新状态部分覆盖|1 / 1|0 / 6|
|[5](#target-5)|Martin s6|重复确认|重复确认核心保留|1 / 1|0 / 6|
|[6](#target-6)|Martin s6|重复确认|重复确认核心保留|1 / 1|0 / 6|
|[7](#target-7)|Martin s7|修订后接受|核心新状态完整保存|4 / 3|0 / 15|
|[8](#target-8)|Martin s8|修订后接受|核心新状态部分覆盖|1 / 1|1 / 10|
|[9](#target-9)|Williams s3|接受|核心新状态部分覆盖|1 / 1|0 / 6|
|[10](#target-10)|Williams s4|接受|核心新状态完整保存|1 / 1|0 / 7|
|[11](#target-11)|Williams s4|修订后接受|核心新状态部分覆盖|2 / 2|0 / 7|
|[12](#target-12)|Williams s5|修订后接受|核心新状态完整保存|1 / 1|0 / 8|
|[13](#target-13)|Williams s5|修订后接受|核心新状态完整保存|2 / 2|0 / 8|
|[14](#target-14)|Williams s6|接受|核心新状态部分覆盖|1 / 1|1 / 8|
|[15](#target-15)|Williams s7|重复确认|重复确认部分覆盖|3 / 3|0 / 5|
|[16](#target-16)|Williams s10|修订后接受|核心新状态部分覆盖|1 / 1|0 / 5|
|[17](#target-17)|Donald s3|修订后接受|核心新状态部分覆盖|2 / 2|0 / 6|
|[18](#target-18)|Donald s3|修订后接受|核心新状态完整保存|1 / 1|0 / 6|
|[19](#target-19)|Donald s3|修订后接受|核心新状态部分覆盖|1 / 1|0 / 4|
|[20](#target-20)|Donald s3|归并|关联方法计划部分覆盖|3 / 3|0 / 7|
|[21](#target-21)|Donald s4|修订后接受|核心新状态部分覆盖|1 / 1|0 / 7|
|[22](#target-22)|Donald s5|接受|核心新状态未保存|2 / 2|0 / 5|
|[23](#target-23)|Donald s6|接受|核心新状态部分覆盖|2 / 2|0 / 7|
|[24](#target-24)|Donald s7|修订后接受|核心新状态部分覆盖|3 / 3|1 / 9|

## 逐项证据与未知项

<a id="target-1"></a>
### 1. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s004:m000
判定：**核心新状态完整保存**。新增与朋友金毛互动、温顺、适应性和新的偏好；拉布拉多旧喜好及理由原文保留。没有要求推断当前品种排序。

更新前相关实际记忆：
- `d575dfc1-59ec-43b4-83c4-6b94457a83f6`（已召回）：Likes dogs, especially Labradors, because they are friendly, loyal, and great companions for outdoor activities like jogging

更新后相关实际记忆：
- `aa764342-2fe6-4632-9efd-e5e0cc032185`：Recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career

本会话计划：{'UPDATE': 1, 'NONE': 20, 'ADD': 1}；实际：{'UPDATE': 1, 'ADD': 1}；未执行计划0项、同文UPDATE 1项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 6；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：拉布拉多与金毛的当前排序未知，按审核边界不计缺失。
证据：[完整前后及操作](target_01_evidence.json)；[便于浏览的前快照与差异](target_01_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-2"></a>
### 2. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s005:m001
判定：**重复确认核心保留**。原有考虑转职及心理健康动机仍在，另增当前工作心理负担和转职考虑；重复确认核心保留，不要求新增。全球健康倡议细节在此前第4会话已丢失，本次不能计为新损伤。

更新前相关实际记忆：
- `0db431ab-6638-42b8-b509-d715dbb286bc`（已召回）：Considers work-life balance a key factor in evaluating new roles
- `58589cd3-36bc-439f-8003-d6416735b820`（已召回）：Mental health occasionally feels strained due to job demands and pressure to deliver high-quality healthcare solutions
- `ecc0de53-fe20-4875-bfb5-e1b5ea7d6470`（已召回）：Career change is being considered due to impact on mental health

更新后相关实际记忆：
- `0db431ab-6638-42b8-b509-d715dbb286bc`：Considers work-life balance a key factor in evaluating new roles
- `58589cd3-36bc-439f-8003-d6416735b820`：Mental health occasionally feels strained due to job demands and pressure to deliver high-quality healthcare solutions
- `d89a12f2-be5e-49dc-b30c-0a8c65984ab9`：Experiencing mental strain from current role and considering career change for mental health
- `ecc0de53-fe20-4875-bfb5-e1b5ea7d6470`：Career change is being considered due to impact on mental health

本会话计划：{'NONE': 34, 'UPDATE': 8, 'ADD': 10}；实际：{'UPDATE': 7, 'ADD': 10}；未执行计划1项、同文UPDATE 7项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 7；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：无法从本次after还原此前已被概括丢失的全球健康倡议细节。
证据：[完整前后及操作](target_02_evidence.json)；[便于浏览的前快照与差异](target_02_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-3"></a>
### 3. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s005:m004
判定：**核心新状态部分覆盖**。保存对医疗可及性非营利组织的兴趣、转职考虑、工作灵活性、人脉计划与寻求指导；但未明确把非营利组织与考虑申请或从事的岗位绑定。

更新前相关实际记忆：
- `06075b1c-6c8f-4dae-ac38-2a1333dc5a3a`（已召回）：Financial stability is secondary to humanitarian goals and personal well-being
- `1b88d72f-28fa-46e5-9628-a0831e1e046e`（已召回）：Measures success by impact on healthcare access, personal health, and creativity
- `5bf042d6-3f1b-4e97-8a3e-4d9a67a22bf8`（已召回）：Hope to provide healthcare access to 1 million people in underserved areas
- `b79a25de-05b7-47b7-bb0b-8c59b44a61ec`（已召回）：Primary career motivation is improving healthcare access for underserved communities

更新后相关实际记忆：
- `04d538a9-5ea1-4364-a5f0-47a108ead2a6`：Practices yoga for mental clarity and flexibility
- `07c06494-0e65-46b5-83a4-077c41bab41a`：Plans to network with professionals in the non-profit sector
- `61cef1b4-a449-4e7f-a16a-3e0fb99a0401`：Interested in non-profit organizations focused on healthcare access
- `bd52b893-fb10-4022-a5e2-812302934c8d`：Likes comfortable athletic wear for its comfort and flexibility, ideal for active lifestyle
- `eb152c7d-17df-4b3a-8a99-9f6211614e2a`：Believes flexibility in job is crucial for managing professional responsibilities and personal well-being

本会话计划：{'NONE': 34, 'UPDATE': 8, 'ADD': 10}；实际：{'UPDATE': 7, 'ADD': 10}；未执行计划1项、同文UPDATE 7项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 8；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：对非营利组织感兴趣和考虑转职并存，不必然等于明确保存考虑非营利岗位；不要求已获得具体岗位。
证据：[完整前后及操作](target_03_evidence.json)；[便于浏览的前快照与差异](target_03_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-4"></a>
### 4. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s006:m001
判定：**核心新状态部分覆盖**。Susan朋友身份保留，新增鼓励和帮助专注目标；完整知识有求职事实，但Susan支持与本次求职的情境联系未被明确绑定。其通用支持保存，情境细化只部分覆盖。

更新前相关实际记忆：
- `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`（已召回）：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

更新后相关实际记忆：
- `37fd291e-d0a7-4d4c-9fdd-f5342b7648dd`：Grateful for support from Susan, Daniel, and Joshua
- `88e4fcd9-0719-4f3c-bb36-a14bed591477`：Susan provides encouragement and helps maintain focus on goals
- `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

本会话计划：{'NONE': 7, 'UPDATE': 35, 'ADD': 13}；实际：{'UPDATE': 35, 'ADD': 13}；未执行计划0项、同文UPDATE 35项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 6；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：不能凭同一快照共存完全确认支持专用于此次求职。
证据：[完整前后及操作](target_04_evidence.json)；[便于浏览的前快照与差异](target_04_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-5"></a>
### 5. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s006:m002
判定：**重复确认核心保留**。Daniel同事身份和医疗咨询专长保留，新增推动跳出框架与创新的见解。再次确认内容可表达；不强加专用于本次求职的归因。

更新前相关实际记忆：
- `0da9428c-2fe6-4254-b818-58991562b49d`（已召回）：Has a colleague named MartinezDaniel (referred to as 'Daniel') with expertise in healthcare consulting

更新后相关实际记忆：
- `0da9428c-2fe6-4254-b818-58991562b49d`：Has a colleague named MartinezDaniel (referred to as 'Daniel') with expertise in healthcare consulting
- `37fd291e-d0a7-4d4c-9fdd-f5342b7648dd`：Grateful for support from Susan, Daniel, and Joshua
- `845853d3-9c8f-4075-828c-206f4a2531cc`：Daniel offers insights that push thinking outside the box and foster innovation

本会话计划：{'NONE': 7, 'UPDATE': 35, 'ADD': 13}；实际：{'UPDATE': 35, 'ADD': 13}；未执行计划0项、同文UPDATE 35项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 6；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：before并未完整保存其所有早期职业成长贡献，未存部分不评为本次损伤。
证据：[完整前后及操作](target_05_evidence.json)；[便于浏览的前快照与差异](target_05_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-6"></a>
### 6. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s006:m003
判定：**重复确认核心保留**。Joshua同事身份、协作方式和医疗管理见解保留，新增对领导风格的积极影响；重复确认核心得到表达。

更新前相关实际记忆：
- `a90e498c-4586-4237-8a4b-c830847f8819`（已召回）：Has a colleague named WilliamsJoshua (referred to as 'Joshua') known for collaborative approach and insights in healthcare management

更新后相关实际记忆：
- `3588abfc-5f64-40cf-b71d-53d7108d0375`：Joshua's collaborative approach has positively influenced leadership style
- `37fd291e-d0a7-4d4c-9fdd-f5342b7648dd`：Grateful for support from Susan, Daniel, and Joshua
- `a90e498c-4586-4237-8a4b-c830847f8819`：Has a colleague named WilliamsJoshua (referred to as 'Joshua') known for collaborative approach and insights in healthcare management

本会话计划：{'NONE': 7, 'UPDATE': 35, 'ADD': 13}；实际：{'UPDATE': 35, 'ADD': 13}；未执行计划0项、同文UPDATE 35项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 6；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：before未完整保存团队效能等全部贡献，未存部分不评为本次损伤。
证据：[完整前后及操作](target_06_evidence.json)；[便于浏览的前快照与差异](target_06_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-7"></a>
### 7. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s007:m000
判定：**核心新状态完整保存**。before明确Looking for a new job及考虑转职、面试/offer。after新增Has transitioned to a new role with healthier work-life balance，并存新岗位减压。新阶段明确保存；旧求职和Current role is Director at Huaxin未历史化，时间组织仍有不足。

更新前相关实际记忆：
- `bc4366a1-d9e6-4e96-84fe-6247e96ef3d6`（未召回）：Has secured interviews and job offers through social network
- `d89a12f2-be5e-49dc-b30c-0a8c65984ab9`（已召回）：Experiencing mental strain from current role and considering career change for mental health
- `e6ab178b-c0f9-4adb-bfb7-e4648617a950`（已召回）：Looking for a new job with better work-life balance
- `ecc0de53-fe20-4875-bfb5-e1b5ea7d6470`（已召回）：Career change is being considered due to impact on mental health

更新后相关实际记忆：
- `0db431ab-6638-42b8-b509-d715dbb286bc`：Considers work-life balance a key factor in evaluating new roles
- `63afc877-8768-4e3d-98d4-68bcb2538e65`：New role improves mental health and reduces stress from previous job
- `727c24da-80f3-48b2-a34c-2e29f8e76da3`：Interested in opportunities with higher salary as part of career transition
- `818912c6-02bb-44f1-8350-8ce250f1fc3e`：Has transitioned to a new role with healthier work-life balance
- `93d9e572-f052-41b6-9387-9e7583b8c3ab`：Friends and colleagues (Susan, Daniel, and Joshua) provided instrumental support during career transition
- `992ae849-3f40-4ffe-a2ec-16e20959ca86`：Practices or is open to yoga for supporting personal health and transition
- `d2f9ec87-e472-4808-890e-395443f45c64`：New role has a creative aspect that enables innovation in healthcare
- `e6ab178b-c0f9-4adb-bfb7-e4648617a950`：Looking for a new job with better work-life balance

本会话计划：{'NONE': 15, 'UPDATE': 23, 'ADD': 9}；实际：{'UPDATE': 23, 'ADD': 9}；未执行计划0项、同文UPDATE 20项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 15 / 15；确认部分损伤 0 / 15。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：不推断新岗位具体雇主、职称、收入；旧状态消歧及下游回答未测。
证据：[完整前后及操作](target_07_evidence.json)；[便于浏览的前快照与差异](target_07_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-8"></a>
### 8. 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008:m000
判定：**核心新状态部分覆盖**。记录团建模拟跳伞、享受刺激、更开放尝试及重视安全；但values safety不明确表达用户仍把安全放在首位。旧运动回避改为过去式，high injury risk的旧理由被缩成safety concerns，构成局部历史细节损伤。

更新前相关实际记忆：
- `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`（已召回）：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

更新后相关实际记忆：
- `aa764342-2fe6-4632-9efd-e5e0cc032185`：Owns Golden Retrievers (previously had Labradors); recently interacted with a friend's Golden Retriever and impressed by its gentle nature; values adaptability, calm demeanor, and emotional support in pets; drawn to Golden Retrievers for their compatibility with active lifestyle and wellness goals; optimistic about integrating this preference as a step toward new experiences and balancing demanding career
- `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`：Previously avoided extreme sports due to safety concerns, but recently tried simulated skydiving at a team-building event and is now more open to trying new things and extreme sports; finds adrenaline rush from extreme sports enjoyable and creatively stimulating; values safety while engaging in thrilling activities

本会话计划：{'NONE': 1, 'UPDATE': 15, 'DELETE': 1, 'ADD': 5}；实际：{'UPDATE': 15, 'DELETE': 1, 'ADD': 5}；未执行计划0项、同文UPDATE 12项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 10 / 10；确认部分损伤 1 / 10。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：新记忆把模拟体验扩写为更开放尝试极限运动、享受极限运动，范围可能超出用户证据；Owns Golden Retrievers (previously had Labradors)亦超出偏好证据，不能推断其实际养犬。
证据：[完整前后及操作](target_08_evidence.json)；[便于浏览的前快照与差异](target_08_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-9"></a>
### 9. 1b846c59-456e-9550-dffd-4d23f1eca81f:s003:m001
判定：**核心新状态部分覆盖**。茶馆到访与一般风味探索已保存；伯爵茶旧理由保留。但未明确保存本次体验使其对伯爵茶层次风味欣赏加深；抽取阶段已省略该联系。

更新前相关实际记忆：
- `8602da08-fefc-4875-ad50-dba104642365`（已召回）：Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia

更新后相关实际记忆：
- `24ac231f-fd30-4418-8db6-0bd0cd4e06de`：Recently visited a historic tea house
- `7620713d-829a-441e-ae4f-cf4398ca3f04`：Inspired by tea house visit to explore nuanced tastes and their relation to broader goals
- `7ad28253-8ba5-4531-b52c-208430e589b2`：Plans to revisit the tea house with friends who share passion for historical exploration
- `8602da08-fefc-4875-ad50-dba104642365`：Appreciates Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia
- `911de0b3-2dbe-423c-abb6-85f569c657bb`：Plans to revisit the tea house with colleagues interested in modern architecture

本会话计划：{'UPDATE': 4, 'NONE': 6, 'ADD': 8}；实际：{'UPDATE': 4, 'ADD': 8}；未执行计划0项、同文UPDATE 0项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 6；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：后续能否正确回答体验和伯爵茶关系未测。
证据：[完整前后及操作](target_09_evidence.json)；[便于浏览的前快照与差异](target_09_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-10"></a>
### 10. 1b846c59-456e-9550-dffd-4d23f1eca81f:s004:m000
判定：**核心新状态完整保存**。新ADD明确最近晋升Lead Director并保留雇主；旧Director已入库、召回并以相同文本UPDATE。整体可表达新职称；旧具体职称未显式历史化，不能声称时间冲突完全消除。

更新前相关实际记忆：
- `e13b825e-7ec7-4760-821e-0581d8da5650`（已召回）：Works at Historical Productions Ltd. as a Director

更新后相关实际记忆：
- `2570a550-4b52-43fc-b5c4-079261785a1a`：Recently promoted to lead director at Historical Productions Ltd

本会话计划：{'NONE': 25, 'UPDATE': 14, 'ADD': 12}；实际：{'UPDATE': 14, 'ADD': 12}；未执行计划0项、同文UPDATE 14项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 7；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：严格消歧及下游回答未测。
证据：[完整前后及操作](target_10_evidence.json)；[便于浏览的前快照与差异](target_10_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-11"></a>
### 11. 1b846c59-456e-9550-dffd-4d23f1eca81f:s004:m003
判定：**核心新状态部分覆盖**。保存真实性、创新和创作控制的价值取向及叙事计划；未明确保存晋升带来更多创作控制空间和能力增量。“重视控制”不足以等同“拥有更多控制”。

更新前相关实际记忆：
- `199dfd83-57fc-4c71-ba24-e78ac99fd607`（已召回）：Collaborates with set dressers to create period settings
- `f71eebcd-d556-436f-97be-a8dca4c99de9`（已召回）：Goal is to create historically accurate films

更新后相关实际记忆：
- `11f664eb-b3d2-44e6-9942-9e425a5e731e`：Dislikes fast food burgers because they taste overly processed and lack authenticity and quality
- `26744cf2-1ca8-4c32-9b41-473761aa1223`：Dislikes auto-tuned pop music because it lacks authenticity and depth
- `4307efba-c7a6-458b-a0b5-e0b25d272fa3`：Reflects on balancing historical authenticity with embracing new flavors
- `6176ea3e-1c00-4532-acbe-ce6ae1ea1f9d`：Dislikes energy drinks because they are too sweet, artificial, and lack authenticity and historical roots
- `702889f6-20b1-46cf-95b9-cb5eeac421e2`：Dislikes science fiction because its futuristic themes conflict with preference for historical accuracy and authenticity
- `ede9660f-f56c-4e47-b331-48cf33e00740`：Values authenticity, innovation, and creative control
- `eee03dd5-d84c-4a87-a5b0-afba59162367`：Friend: WilliamsRichard (fellow director, inspires innovative storytelling)

本会话计划：{'NONE': 25, 'UPDATE': 14, 'ADD': 12}；实际：{'UPDATE': 14, 'ADD': 12}；未执行计划0项、同文UPDATE 14项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 7；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：部分能力可从Lead Director背景推断，但未以明确记忆保存，不作完整覆盖。
证据：[完整前后及操作](target_11_evidence.json)；[便于浏览的前快照与差异](target_11_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-12"></a>
### 12. 1b846c59-456e-9550-dffd-4d23f1eca81f:s005:m000
判定：**核心新状态完整保存**。保存晋升后心理改善、委派减压与增强项目专注；旧压力来源和身体健康仍在。新增“Colleagues Steven and Mary”与旧Mary朋友身份并存，是会话来源混合的归属风险，非旧支持内容被删。

更新前相关实际记忆：
- `4ffee399-c31f-4827-b5fc-5c661baf1fc9`（已召回）：Experiences stress due to historical accuracy demands and tight production schedules

更新后相关实际记忆：
- `03afcc93-335c-4519-81ad-e375984ffe31`：Delegating tasks has reduced stress and enhanced focus on projects
- `317d0abd-09eb-461b-aec9-72c31c5fc989`：Improved mental health since promotion

本会话计划：{'NONE': 25, 'UPDATE': 6, 'ADD': 10}；实际：{'UPDATE': 6, 'ADD': 10}；未执行计划0项、同文UPDATE 6项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 8 / 9；确认部分损伤 0 / 8。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：未要求临床康复或无压力；相关临床状态不可推断。
证据：[完整前后及操作](target_12_evidence.json)；[便于浏览的前快照与差异](target_12_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-13"></a>
### 13. 1b846c59-456e-9550-dffd-4d23f1eca81f:s005:m001
判定：**核心新状态完整保存**。明确新增Work-life balance improved due to role change；与心理改善和委派归因分开存储，兼容的旧压力及身体记录保留。

更新前相关实际记忆：
- `4ffee399-c31f-4827-b5fc-5c661baf1fc9`（已召回）：Experiences stress due to historical accuracy demands and tight production schedules
- `e15483c3-f7fb-4952-a8ef-23c1fcd3d2ab`（已召回）：Physically healthy with no chronic diseases

更新后相关实际记忆：
- `1043672a-eb91-4a73-841a-f6204f50bf61`：Work-life balance improved due to role change

本会话计划：{'NONE': 25, 'UPDATE': 6, 'ADD': 10}；实际：{'UPDATE': 6, 'ADD': 10}；未执行计划0项、同文UPDATE 6项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 8 / 9；确认部分损伤 0 / 8。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：家庭身份原始信息的完整性不足，不以No demanding family life推断身份变化。
证据：[完整前后及操作](target_13_evidence.json)；[便于浏览的前快照与差异](target_13_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-14"></a>
### 14. 1b846c59-456e-9550-dffd-4d23f1eca81f:s006:m000
判定：**核心新状态部分覆盖**。波斯猫欣赏、历史血统与王室关联保存；抽取的电影节/波斯猫纪录片体验没有进入最终知识，而非完全缺少抽取。旧平静、优雅等喜好理由被覆盖缩减，确认至少平静理由损伤。

更新前相关实际记忆：
- `eef34a57-c82a-4995-877d-66b54b9589da`（已召回）：Likes Persian cats because of their regal and calm nature, elegance, and historical charm

更新后相关实际记忆：
- `1b1fd0ea-358d-48b7-a160-134bbb6da849`：Seeks recognition at major film festivals like Cannes and Sundance
- `1cc86bcf-f1b7-48e2-901a-2d50214975f0`：Also has a deep admiration for Siamese cats, especially after watching a documentary highlighting their historical significance and royal connections
- `8c75c81e-6f7e-4604-81b7-e4d0b2115d81`：Success means recognition at major film festivals like Cannes and Sundance
- `bf54f3d3-d427-4898-a1cb-37c1f63a3954`：Draws professional inspiration from personal interests, especially the historical significance of Persian and Siamese cats
- `eef34a57-c82a-4995-877d-66b54b9589da`：Has a deep admiration for Persian cats and their historical lineage and association with royalty, and reflects on the practical challenges of maintaining their regal appearance while balancing historical admiration with practical care requirements

本会话计划：{'UPDATE': 8, 'NONE': 30, 'ADD': 15}；实际：{'UPDATE': 8, 'ADD': 15}；未执行计划0项、同文UPDATE 6项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 8 / 8；确认部分损伤 1 / 8。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：暹罗猫回应的指代本来有歧义，不将新Siamese纪录片事实当充分确认。
证据：[完整前后及操作](target_14_evidence.json)；[便于浏览的前快照与差异](target_14_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-15"></a>
### 15. 1b846c59-456e-9550-dffd-4d23f1eca81f:s007:m006
判定：**重复确认部分覆盖**。Mary朋友身份及情绪支持/鼓励休息、Steven同事身份及布景/历史细节专长均保留；但Steven的布景贡献与电影真实性之间的具体联系未明确保存。属重复确认，不要求新增。

更新前相关实际记忆：
- `924d86c9-298a-4566-8e2a-d5d83f7874ae`（已召回）：Friend: WilliamsMary (provides emotional support and encourages breaks)
- `b4c92aa8-44f5-48ff-a94d-137e67f02293`（已召回）：Colleague: SmithSteven (expert in set design, shares passion for historical detail)
- `d7d27de9-fc3f-4dfc-9cc5-32bb46446d21`（已召回）：Colleagues Steven and Mary are key supporters

更新后相关实际记忆：
- `924d86c9-298a-4566-8e2a-d5d83f7874ae`：Friend: WilliamsMary (provides emotional support and encourages breaks)
- `b4c92aa8-44f5-48ff-a94d-137e67f02293`：Colleague: SmithSteven (expert in set design, shares passion for historical detail)
- `d7d27de9-fc3f-4dfc-9cc5-32bb46446d21`：Colleagues Steven and Mary are key supporters

本会话计划：{'NONE': 43, 'UPDATE': 11, 'ADD': 4}；实际：{'UPDATE': 11, 'ADD': 4}；未执行计划0项、同文UPDATE 11项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 5 / 6；确认部分损伤 0 / 5。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：兼顾新旧关系的保护候选在本会话before未定位，新人脉范围未固定，不增独立目标。
证据：[完整前后及操作](target_15_evidence.json)；[便于浏览的前快照与差异](target_15_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-16"></a>
### 16. 1b846c59-456e-9550-dffd-4d23f1eca81f:s010:m001
判定：**核心新状态部分覆盖**。新增转向Baroque symphonies、现场管弦演出、对Romantic潜在影响开放以及配乐探索；演出促使探索的因果联系未明确绑定。旧古典交响乐、爵士和流行音乐顾虑保留。

更新前相关实际记忆：
- `d1e2e0e6-45fd-49ef-bbec-e6521db283e6`（已召回）：Likes classical symphonies because of their complexity, historical significance, and authentic auditory experience

更新后相关实际记忆：
- `07b520bb-6f6e-4f54-9ed3-02c7d650a8ff`：Is exploring ways to incorporate Baroque music into films to enhance historical accuracy and emotional resonance
- `5c8ec51a-5a6d-408d-b30e-c1b4cb8b64a5`：Has shifted musical preferences towards Baroque symphonies
- `69c67f53-58c8-46c2-8467-2c589d407654`：Has found success in using Baroque music to enhance emotional depth in films
- `76117ba8-7005-4d63-b2e0-8efc3272257e`：Finds Baroque music's historical richness and complexity aligns with appreciation for authenticity
- `d6ce2aa9-d5f8-44b6-b4b4-0259a34bdc1b`：Recently attended a live orchestral performance at a renowned concert hall

本会话计划：{'NONE': 42, 'UPDATE': 18, 'ADD': 18}；实际：{'UPDATE': 13, 'ADD': 18}；未执行计划5项、同文UPDATE 13项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 5 / 5；确认部分损伤 0 / 5。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：不推断永久或唯一音乐偏好；配乐已成功应用的措辞比“发现其潜力”更强；5个映射外UPDATE被跳过。
证据：[完整前后及操作](target_16_evidence.json)；[便于浏览的前快照与差异](target_16_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-17"></a>
### 17. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003:m001
判定：**核心新状态部分覆盖**。保存从技术转向政治咨询及支持亲属的既有目标，原技术职称改为过去式。但已与专业人士建立联系和参加研讨会的推进细节未明确保存。

更新前相关实际记忆：
- `05afde13-35bd-4d26-bbae-6de427d58db1`（已召回）：Works at Blockchain Tech as a senior developer
- `aca2b85d-8856-4989-bfdd-b032fde1bda3`（已召回）：Employed in the technology industry

更新后相关实际记忆：
- `0466398c-b5f8-4bb7-ae1d-17f8c315395d`：Does not like backpacking because they find it too unpredictable and prefer organized travel that allows focus on supporting their relative
- `137cce2a-9956-40b8-bf29-26adcedd0266`：Does not like exotic birds because their care requires too much attention, diverting focus from supporting their relative
- `23cca496-1e02-4b98-87de-3a968f3a74b1`：Likes eating chocolate cake as a treat after a successful event, celebrating their relative's positive impact
- `2758550a-32b1-4e3e-88ac-0a2b6fc90dcc`：Motivation for life goal is growing up in a family that values political engagement and having a close relative in politics
- `30a88f0c-d4b8-4089-95b2-82938e45558c`：Does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative
- `311ff045-6a32-4685-ab09-c9c40acbf95d`：Does not like drinking energy drinks because they make them jittery and unable to concentrate on supporting their relative
- `33835e8a-ed5c-4c8a-a112-ec9b9eb738ab`：Does not like wearing casual shorts because they feel too informal for the image they want to project in support of their relative
- `46374680-0009-4625-a3a7-f2b4e329a7b5`：Monthly income was 17,000 USD before transition
- `6e979956-47d6-405f-95d5-df176978b42a`：Likes classical music for its soothing melodies, helping them maintain focus and clarity while working on their relative's campaign
- `7625de05-9638-4b2b-95c4-7a40e5ae75e2`：Does not like listening to heavy metal because its aggressive sound distracts from the calm environment needed to support their relative
- `77cd587e-0953-4ee5-8ec0-6081e217af09`：Does not like playing first-person shooters because their violent nature doesn't resonate with their values or their relative's peaceful campaign
- `7e126cf9-36f4-4c5f-b112-b544a4265300`：Likes wearing red scarves as they symbolize passion and support, qualities associated with their relative's campaign
- `8c0a007f-e94b-4855-a3e6-a07a08fb2949`：Likes wearing formal suits because they make them feel confident and prepared to support their relative during important events
- `9105b4a5-3d60-476c-83f1-b83591272c73`：Likes golden retrievers for their friendly nature and loyalty, qualities they admire and see reflected in their relative
- `913bef92-248b-416b-ba35-052af3a4e960`：Life goal is to support the political career of a close relative
- `97b23dbc-01c7-4472-afb2-bb70973427aa`：BrownMichelle is a colleague at Blockchain Tech who helps balance professional responsibilities with political interests
- `aca2b85d-8856-4989-bfdd-b032fde1bda3`：Career transition from technology to political consulting
- `c5574ceb-d644-4992-83a8-c0575b1d5cec`：Hopes to ensure the relative wins at least three electoral campaigns and establishes a significant legislative legacy
- `dd29d5f5-3dad-42bb-9472-bf58b5a29adb`：Likes eating roast chicken because it reminds them of family gatherings where they discussed their relative's achievements
- `e2eeaf05-508f-435b-ba6e-a3229d3f1443`：Plans to rely on savings and cut unnecessary expenses during transition
- `e8ccc4b9-74e0-4aab-9e09-8105194d1f5f`：Likes playing board games for their social aspect, allowing bonding with family and friends while supporting their relative
- `e93f9a31-f517-471e-8bb5-313470b1d41e`：Does not like adventure sports trips because they distract from the purpose of travel, which is to support their relative's campaign
- `eb0ed6ce-d718-4d1d-adcb-427b9a4a739a`：Does not like solo travel; prefers traveling with others to stay connected and focused on their relative's goals
- `fd0b7cb9-9438-4410-81d8-ded013f055be`：Likes playing strategy games because they challenge the mind and improve problem-solving skills useful for supporting their relative

本会话计划：{'NONE': 19, 'UPDATE': 7, 'ADD': 7}；实际：{'UPDATE': 7, 'ADD': 7}；未执行计划0项、同文UPDATE 2项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 7；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：技术经历保留，不把转型记成已正式确立的新职位；专业联系和研讨会未定位。
证据：[完整前后及操作](target_17_evidence.json)；[便于浏览的前快照与差异](target_17_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-18"></a>
### 18. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003:m003
判定：**核心新状态完整保存**。新增Aims to be a key advisor in political campaigns，保留角色意向；Blockchain Tech高级开发经历改为previously worked。没有把顾问设想写成正式任职。

更新前相关实际记忆：
- `05afde13-35bd-4d26-bbae-6de427d58db1`（已召回）：Works at Blockchain Tech as a senior developer

更新后相关实际记忆：
- `05c87805-dec1-4f41-b721-fc7082b4f39d`：Uses data analytics to analyze voter patterns and tailor campaign strategies
- `19dfbf08-ba3c-4c42-b531-36eff71d832a`：Also mentioned financial consulting as a possible related field
- `4f0c0c15-9a4b-43ab-b97e-f65ff01ed50f`：Aims to be a key advisor in political campaigns
- `58c2e1c2-74b6-4c5b-ab38-433b8e2b7cf2`：Frequently contributes financially to political campaigns and causes supporting a specific politician
- `6e979956-47d6-405f-95d5-df176978b42a`：Likes classical music for its soothing melodies, helping them maintain focus and clarity while working on their relative's campaign
- `77cd587e-0953-4ee5-8ec0-6081e217af09`：Does not like playing first-person shooters because their violent nature doesn't resonate with their values or their relative's peaceful campaign
- `7e126cf9-36f4-4c5f-b112-b544a4265300`：Likes wearing red scarves as they symbolize passion and support, qualities associated with their relative's campaign
- `a1834932-bc7e-4c41-9710-25713ae07aae`：Likes eating fresh salads for their healthy and refreshing taste, keeping them energized during long campaign days
- `aca2b85d-8856-4989-bfdd-b032fde1bda3`：Career transition from technology to political consulting
- `c5574ceb-d644-4992-83a8-c0575b1d5cec`：Hopes to ensure the relative wins at least three electoral campaigns and establishes a significant legislative legacy
- `e93f9a31-f517-471e-8bb5-313470b1d41e`：Does not like adventure sports trips because they distract from the purpose of travel, which is to support their relative's campaign

本会话计划：{'NONE': 19, 'UPDATE': 7, 'ADD': 7}；实际：{'UPDATE': 7, 'ADD': 7}；未执行计划0项、同文UPDATE 2项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 6 / 7；确认部分损伤 0 / 6。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：具体政治咨询职位、任命及职级未知。
证据：[完整前后及操作](target_18_evidence.json)；[便于浏览的前快照与差异](target_18_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-19"></a>
### 19. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003:m004
判定：**核心新状态部分覆盖**。17,000美元月收入改为转型前历史，16,800美元储蓄独立保留，新增依靠储蓄和减少开支的计划；但没有明确保存转型初期没有即时收入。

更新前相关实际记忆：
- `46374680-0009-4625-a3a7-f2b4e329a7b5`（已召回）：Monthly income is 17000 USD

更新后相关实际记忆：
- `31884358-05ca-4517-bc84-2a7f5fdad0c8`：Has savings of 16,800 USD
- `46374680-0009-4625-a3a7-f2b4e329a7b5`：Monthly income was 17,000 USD before transition
- `e2eeaf05-508f-435b-ba6e-a3229d3f1443`：Plans to rely on savings and cut unnecessary expenses during transition

本会话计划：{'NONE': 19, 'UPDATE': 7, 'ADD': 7}；实际：{'UPDATE': 7, 'ADD': 7}；未执行计划0项、同文UPDATE 2项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 4 / 4；确认部分损伤 0 / 4。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：无法依据未明确的收入状态推断目标日整月收入为零。
证据：[完整前后及操作](target_19_evidence.json)；[便于浏览的前快照与差异](target_19_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-20"></a>
### 20. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003:m005
判定：**关联方法计划部分覆盖**。新增数据分析、战略沟通、领导力相关记忆，但Uses data analytics表述成已在实际使用，用户审核确认的是计划/预期；技术经历和问题解决能力作为将有帮助的关联没有完整明确保存。方向归17、角色归18，不作为独立主目标。

更新前相关实际记忆：
- `2b65ace7-5f31-4cb5-9582-8b8a1d99dd2b`（已召回）：Role involves innovating new solutions and ensuring technology remains cutting-edge
- `58c2e1c2-74b6-4c5b-ab38-433b8e2b7cf2`（已召回）：Frequently contributes financially to political campaigns and causes supporting a specific politician
- `913bef92-248b-416b-ba35-052af3a4e960`（已召回）：Life goal is to support the political career of a close relative

更新后相关实际记忆：
- `05c87805-dec1-4f41-b721-fc7082b4f39d`：Uses data analytics to analyze voter patterns and tailor campaign strategies
- `3e887750-cbcf-4e95-af28-58a7c5da3895`：Focuses on strategic communication and understanding voter behavior
- `799ad175-99c1-40e9-870a-4d4acb767863`：Values strategic communication and leadership skills
- `fd0b7cb9-9438-4410-81d8-ded013f055be`：Likes playing strategy games because they challenge the mind and improve problem-solving skills useful for supporting their relative

本会话计划：{'NONE': 19, 'UPDATE': 7, 'ADD': 7}；实际：{'UPDATE': 7, 'ADD': 7}；未执行计划0项、同文UPDATE 2项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 8；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：不能把潜在能力迁移或计划当成已实施；原来源与用户确认边界详见证据。
证据：[完整前后及操作](target_20_evidence.json)；[便于浏览的前快照与差异](target_20_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-21"></a>
### 21. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s004:m000
判定：**核心新状态部分覆盖**。新增职业转型感到压力和不堪重负、收入不确定顾虑；before稳定正常的心理记录仍保留。但没有明确保存用户所说压力正在影响心理健康的关系及兼顾学习/竞选承诺的归因。

更新前相关实际记忆：
- `e5ec2bdf-d263-4e0f-a4bd-e649154c5993`（已召回）：Mental health is stable and normal with no mental health issues

更新后相关实际记忆：
- `7cf37b2e-3d24-447a-a44d-5071804b3d04`：Values mental health as essential to effectively supporting their relative
- `7e0d2d3d-3d72-48fa-a320-fe9256e70ca0`：Considers meditation and mindfulness practices effective for stress relief
- `8ca919d1-21f0-4555-8f5f-4d775a2873f9`：Believes physical activities can help manage stress
- `b8df9f1d-75a3-4061-ad91-09a212382af5`：Concerned about income uncertainty and loss of financial stability
- `bdc018c2-84bb-4b2f-b3c8-60e0affdb884`：Likes drinking green tea for its calming effect, helping them stay focused and composed during stressful situations
- `d012c01a-8b10-4335-b210-bd3fa579e4b1`：Feeling stressed and overwhelmed by the career transition
- `e5ec2bdf-d263-4e0f-a4bd-e649154c5993`：Mental health is stable and normal with no mental health issues
- `fe76478b-2e5c-4d34-9e9c-bf81870bd39b`：Maintains physical and mental health through activity, work, and political engagement

本会话计划：{'UPDATE': 5, 'NONE': 17, 'ADD': 8}；实际：{'UPDATE': 5, 'ADD': 8}；未执行计划0项、同文UPDATE 4项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 7；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：旧稳定记录未显式标为历史，不能推断临床诊断、永久状态或唯一原因。
证据：[完整前后及操作](target_21_evidence.json)；[便于浏览的前快照与差异](target_21_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-22"></a>
### 22. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s005:m004
判定：**核心新状态未保存**。before已有Sandra朋友/政治观点和Mary密友/政治策略讨论，after仍保留；但没有明确保存二人在这次转型期间共同提供鼓励与策略建议。更新模型曾计划该句，临时ID53不在旧映射，原生跳过，实际没有对应写入。

更新前相关实际记忆：
- `37756be3-aaee-4e1c-b8f7-a5fed3d94890`（已召回）：MooreSandra is a friend who shares political views and supports the same politician
- `98c6916c-8aa9-4560-94ce-5697f39ac818`（已召回）：GonzalezMary is a close friend who discusses political strategies

更新后相关实际记忆：
- `37756be3-aaee-4e1c-b8f7-a5fed3d94890`：MooreSandra is a friend who shares political views and supports the same politician
- `98c6916c-8aa9-4560-94ce-5697f39ac818`：GonzalezMary is a close friend who discusses political strategies

本会话计划：{'UPDATE': 8, 'NONE': 41, 'ADD': 17}；实际：{'UPDATE': 7, 'ADD': 17}；未执行计划1项、同文UPDATE 3项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 5 / 5；确认部分损伤 0 / 5。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：新增其他人脉资源和未来咨询朋友计划不能替代这两位朋友的集体支持；不擅自给每人分配具体贡献。
证据：[完整前后及操作](target_22_evidence.json)；[便于浏览的前快照与差异](target_22_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-23"></a>
### 23. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s006:m001
判定：**核心新状态部分覆盖**。新增政治咨询公司及人脉包括Sandra、Mary；但利用这些人脉获取首批客户的计划未明确保存。两人原有朋友关系及John的独立身份仍在。

更新前相关实际记忆：
- `37756be3-aaee-4e1c-b8f7-a5fed3d94890`（已召回）：MooreSandra is a friend who shares political views and supports the same politician
- `98c6916c-8aa9-4560-94ce-5697f39ac818`（已召回）：GonzalezMary is a close friend who discusses political strategies

更新后相关实际记忆：
- `37756be3-aaee-4e1c-b8f7-a5fed3d94890`：MooreSandra is a friend who shares political views and supports the same politician
- `82eb2023-d684-48c1-b428-be0a6d9f9109`：Network includes MooreSandra and GonzalezMary
- `98c6916c-8aa9-4560-94ce-5697f39ac818`：GonzalezMary is a close friend who discusses political strategies
- `b29fc79b-a371-461e-b445-d5a33bc8e2e5`：Uses case studies, success stories, and anecdotes from past networking experiences to demonstrate value
- `bfb15d6b-4748-4e95-9cbe-9d54ba1eb063`：Has shared past networking experiences that led to career success
- `cf54b6a7-21e5-4f2e-b815-9b1ffadc51b7`：Stays connected with network by regularly attending events and maintaining communication with key contacts
- `e556e311-a618-49a2-993a-2e12e3615873`：Attended a cultural festival in Chicago for networking purposes

本会话计划：{'NONE': 18, 'UPDATE': 19, 'ADD': 12}；实际：{'UPDATE': 19, 'ADD': 12}；未执行计划0项、同文UPDATE 19项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 7 / 7；确认部分损伤 0 / 7。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：公司启动进度及确切日期分别核验；人脉中有二人不等于已存获客计划或已经有客户。
证据：[完整前后及操作](target_23_evidence.json)；[便于浏览的前快照与差异](target_23_evidence.md)；[保护候选逐项](protection_review.md)。

<a id="target-24"></a>
### 24. 348492a7-cfe4-ee1d-73c3-c276d6ba8277:s007:m006
判定：**核心新状态部分覆盖**。新增Firm has secured initial clients，实际获客核心已保存；用户自述宽慰和里程碑意义未明确保存。旧Blockchain Tech高级开发历史被压缩为Formerly worked in technology，雇主和职级细节丢失；薪资和储蓄记录仍各自保留。

更新前相关实际记忆：
- `5f43f157-643f-40bf-877b-7af38fe8a462`（已召回）：Firm advises political campaigns
- `65dbdbf4-2be4-4cac-9d30-402b83bb731e`（已召回）：Launching a political consulting firm on December 20, 2025
- `f37cc10b-e4f7-4b82-93c8-af457ad5015c`（已召回）：Optimistic about the firm's future, emphasizing innovative strategies and modern technology

更新后相关实际记忆：
- `62f8f274-43b9-483e-95ca-9bb441076ec1`：Firm has secured initial clients
- `8027e6ed-1bb7-4d16-8428-7341cce5aa62`：Measures success by campaign effectiveness and positive feedback from clients and stakeholders
- `dd29d5f5-3dad-42bb-9472-bf58b5a29adb`：Likes eating roast chicken because it reminds them of family gatherings where they discussed their relative's achievements

本会话计划：{'NONE': 38, 'UPDATE': 12, 'ADD': 11}；实际：{'UPDATE': 12, 'ADD': 11}；未执行计划0项、同文UPDATE 3项。这是同会话共享记录，不把全部操作归因给本目标。
保护候选：可定位相关存量 9 / 10；确认部分损伤 1 / 9。复合候选是否完整入库及逐项召回另见保护表。
未知/范围限定：Sandra/Mary在获客中的集体贡献未明确保存；家庭创业支持与准确公司启动日期由助手提出，缺充分用户确认，不能视为已证实事实或有效保护损伤。
证据：[完整前后及操作](target_24_evidence.json)；[便于浏览的前快照与差异](target_24_evidence.md)；[保护候选逐项](protection_review.md)。

## 原生异常及计划/实际差异

v1/v2启动失败各一次，均发生在首次抽取请求，0写入；正式v3范围不含这两次失败命名空间。以下为正式28会话中的操作差异，全部保存实际状态，没有重试。

### 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f / 原始sessions[5]
计划：{'NONE': 34, 'UPDATE': 8, 'ADD': 10}；实际：{'UPDATE': 7, 'ADD': 10}；同文UPDATE：7。
- 未落地：临时ID `44`，UPDATE，Prefers Golden Retrievers (previously preferred Labradors)；解析到旧UUID：None。

### 348492a7-cfe4-ee1d-73c3-c276d6ba8277 / 原始sessions[5]
计划：{'UPDATE': 8, 'NONE': 41, 'ADD': 17}；实际：{'UPDATE': 7, 'ADD': 17}；同文UPDATE：3。
- 未落地：临时ID `53`，UPDATE，Friends MooreSandra and GonzalezMary are providing encouragement and strategic advice；解析到旧UUID：None。

### 1b846c59-456e-9550-dffd-4d23f1eca81f / 原始sessions[1]
计划：{'NONE': 15, 'ADD': 14, 'UPDATE': 1}；实际：{'ADD': 14}；同文UPDATE：0。
- 未落地：临时ID `19`，UPDATE，Meticulous director focused on historical accuracy；解析到旧UUID：None。

### 1b846c59-456e-9550-dffd-4d23f1eca81f / 原始sessions[10]
计划：{'NONE': 42, 'UPDATE': 18, 'ADD': 18}；实际：{'UPDATE': 13, 'ADD': 18}；同文UPDATE：13。
- 未落地：临时ID `62`，UPDATE，Has perfectionist traits and strives for historical accuracy in every detail；解析到旧UUID：None。
- 未落地：临时ID `70`，UPDATE，Measures success by audience impact and recognition at major film festivals；解析到旧UUID：None。
- 未落地：临时ID `73`，UPDATE，Uses strategic thinking to carefully select musical and thematic influences that align with vision and historical authenticity；解析到旧UUID：None。
- 未落地：临时ID `75`，UPDATE，Celebrates successes by sharing them with network and reflecting on audience impact；解析到旧UUID：None。
- 未落地：临时ID `77`，UPDATE，Believes balancing artistic vision with practical production involves careful planning and collaboration with a skilled team；解析到旧UUID：None。

## 保护内容损伤与解释边界

- 目标8 / 保护2：此前因受伤风险而回避极限运动的安全顾虑及历史原因。新记忆保留过去回避与safety concerns，但省略旧high injury risk具体历史理由。整体after未在其他记忆补回；属历史理由细节部分缩减，不等于安全原则全丢。
- 目标14 / 保护1：波斯猫既有喜好及高贵、平静、优雅和历史感理由。旧平静/优雅等理由原文在before；after波斯猫记忆被改写，完整after未保留平静理由，新对话未撤销。至少平静属性确认损伤。
- 目标24 / 保护2：带时间的职业和财务历史，收入与储蓄分别核验。此前Blockchain Tech高级开发的已存历史缩减为Formerly worked in technology；用户已确认的雇主与高级职位细节丢失。收入和储蓄独立记录仍在。

全会话合法更新依据完整原始对话判定，不把其他有依据的新信息算越界；旧收入、职称、健康与职业阶段的当前有效性和历史真实性分开。保护结论只核查after可用知识，history保存旧文本不等于当前记忆库已保留相同可检索知识。对于复合候选未入库的细节和精确事件时间，本报告不虚构完整性。

额外观察：Williams第9条所在会话把Name is Williams Daniel改成Name is Williams，属姓名细节缩减；也把“成为知名导演”的目标收窄为制作历史准确电影。Martin较早的原始sessions[3]把全球健康倡议目标概括为医疗可及性职业动机，后续before已无建立该倡议的细节。Martin sessions[6]新写入Is a software engineer，该会话原始对话未出现software；原生抽取提示词示例中有Is a Software engineer，存在示例影响的可能，但仅凭记录无法证明因果。Martin sessions[8]把金毛偏好升级成养犬事实，且将模拟体验泛化至极限运动；Donald sessions[7]新增家庭支持，原对话主要由助手提出，缺充分用户确认。以上另行解释，不混入176保护分母。完整助手消息照原文输入；被保存的助手断言不等于已获用户确认。

## 复核入口与可重复验证

- [逐项目JSON](target_decisions.json) / [CSV](target_decisions.csv)：语义结论、未知项及ID。
- [运行核验](runtime_verification.json)：28会话消息数、快照、全部计划和实际操作差异。
- `../users/<UUID>/session_XXX/`：完整原始输入、含向量快照、召回候选、模型输入输出、全计划、实际history、异常、持久化和检查点。
- `../human_review_version/`：冻结审核副本；原始manifest/profile/run_record仍绑定原版本。
- `../pre_continuation/`：续跑前5会话检查点及状态；本轮没有重输前5会话。旧`RESULT_SHA256SUMS`中的checkpoint路径指向当时的状态；续跑后当前checkpoint已推进，旧哈希对应此处的`user_checkpoint.json`，不是现在的checkpoint文件。
- `../development_console.log`：顺序运行及带异常提交；各用户最终checkpoint分别11、9、8。

验证命令（不调用模型）：`conda run -n mem0_halumem python results/medium_dev/williams_native_prefix5_20261028_v3/code/collect_diagnosis.py`。该命令只读取现有运行资料，在临时副本上开库，并再生成离线评价证据。源码哈希及冻结审核应保持不变。

本开发子集含已调试用户、用户内时序关联和共享会话目标；不能报告为无偏总体性能或独立样本显著性。未运行全量QA、官方评分、后续召回问答或改进模块，未知下游回答质量。
