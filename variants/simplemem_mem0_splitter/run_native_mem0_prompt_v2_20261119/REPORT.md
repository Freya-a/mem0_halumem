# 原生 Mem0 旧记忆：SimpleMem prompt_v2 五例试运行

五条输入直接读取指定原生运行对应目标会话的 before.json，按 ID 找到 `api_snapshot.results[].memory`，并与底层 payload 的 ID、user_id、data 核对；快照 SHA-256 与目标会话列表保存在各例 JSON。用户 ID 仅作来源元数据，未加入模型消息；所有 `source_context` 均为 null，未将新证据或后续会话传入模型。未执行记忆更新。

模型 `qwen-plus-2025-12-01`，提示词 `prompt_v2`，请求 5 次，模型响应 5 次，接口错误 0；自动重试 0；总调用耗时 42.081 秒。程序状态：通过 2、待复核 1、失败 2。每个案例调用一次，连接使用独立客户端直连、项目配置文件优先。

以下逐字展示模型返回；自动程序只检查结构和逐字命中，不代表语义忠实、完整或人工验收。语义检查为助手初评。实际提示词、响应、实体、位置偏移、错误和参数均保存在各例 JSON。

## 案例 1：d575dfc1-59ec-43b4-83c4-6b94457a83f6

旧记忆：Likes dogs, especially Labradors, because they are friendly, loyal, and great companions for outdoor activities like jogging

实际上下文：null；来源用户 ID：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。

来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json`；目标会话组：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s004`。目标会话可供人工审阅；并不作为拆分器输入。

请求一次，16.238 秒，返回模型 `qwen-plus-2025-12-01`；程序状态 **failed**。

- **u1**
  - raw_statement：Likes dogs
  - contextualized_statement：Likes dogs
  - memory_quotes：["Likes dogs"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：Likes dogs, especially Labradors
  - contextualized_statement：Likes dogs, especially Labradors
  - memory_quotes：["Likes dogs, especially Labradors"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u3**
  - raw_statement：Labradors are friendly
  - contextualized_statement：Labradors are friendly
  - memory_quotes：["they are friendly"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u4**
  - raw_statement：Labradors are loyal
  - contextualized_statement：Labradors are loyal
  - memory_quotes：["they are loyal"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u5**
  - raw_statement：Labradors are great companions for outdoor activities like jogging
  - contextualized_statement：Labradors are great companions for outdoor activities like jogging
  - memory_quotes：["they are friendly, loyal, and great companions for outdoor activities like jogging"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u6**
  - raw_statement：Likes dogs, especially Labradors, because they are friendly, loyal, and great companions for outdoor activities like jogging
  - contextualized_statement：Likes dogs, especially Labradors, because they are friendly, loyal, and great companions for outdoor activities like jogging
  - memory_quotes：["Likes dogs, especially Labradors, because they are friendly, loyal, and great companions for outdoor activities like jogging"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

unresolved：["The pronoun 'they' in 'they are friendly, loyal, and great companions...' is ambiguous: it could refer to dogs generally or specifically to Labradors; the original text does not explicitly resolve this reference.", "No subject (e.g., person's name or identifier) is stated for the preference — 'Likes dogs' lacks an explicit agent; the grammatical subject is elided and not recoverable from the given text."]

程序 errors：["units[3].memory_quotes[0] not found verbatim in source"]

程序 warnings：["unresolved issues reported by model"]

助手语义初评：u6 完整保留喜欢狗、尤其拉布拉多，以及友善、忠诚和适合户外活动的原因；u1、u2、u3–u5 与 u6 高度重叠。u3–u5 将原句中的 they 确定为拉布拉多并写成无归属属性，但模型的 unresolved 同时说 they 可能指狗或拉布拉多；原文未提供姓名，不能补姓名。u4 引文 they are loyal 不是连续片段（原文为 they are friendly, loyal），造成校验失败。u6 适合保留完整关系，但若后续须独立修改某个原因，需要范围判断器进一步处理，不能直接按重复单元自动更新。

## 案例 2：e1d4f8f9-0520-427d-94fd-a2ac0ee69d03

旧记忆：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

实际上下文：null；来源用户 ID：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。

来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`；目标会话组：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008`。目标会话可供人工审阅；并不作为拆分器输入。

请求一次，8.502 秒，返回模型 `qwen-plus-2025-12-01`；程序状态 **passed**。

- **u1**
  - raw_statement：Dislikes extreme sports (e.g., skydiving)
  - contextualized_statement：Dislikes extreme sports (e.g., skydiving)
  - memory_quotes：["Dislikes extreme sports (e.g., skydiving)"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：Dislikes extreme sports due to high injury risk
  - contextualized_statement：Dislikes extreme sports due to high injury risk
  - memory_quotes：["Dislikes extreme sports (e.g., skydiving) due to high injury risk"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null
- **u3**
  - raw_statement：Dislikes extreme sports because it conflicts with commitment to safety and well-being
  - contextualized_statement：Dislikes extreme sports because it conflicts with commitment to safety and well-being
  - memory_quotes：["conflicting with commitment to safety and well-being"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

unresolved：[]

程序 errors：[]

程序 warnings：[]

助手语义初评：不喜欢极限运动、跳伞举例、受伤风险及安全和福祉取向都有覆盖，没有断言偏好已改变。u1/u2/u3 有重叠，且 u3 只引用 conflicting...，没有单独引用极限运动主体，单独引文不足以完整支持该单元；u3 的 it 和冲突关联需要结合原句，可能改变原文关系。未提供主体姓名，未应从用户 ID 推断。虽自动通过，仍需语义审核。

## 案例 3：8602da08-fefc-4875-ad50-dba104642365

旧记忆：Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia

实际上下文：null；来源用户 ID：`1b846c59-456e-9550-dffd-4d23f1eca81f`。

来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_004/before.json`；目标会话组：`1b846c59-456e-9550-dffd-4d23f1eca81f:s003`。目标会话可供人工审阅；并不作为拆分器输入。

请求一次，4.884 秒，返回模型 `qwen-plus-2025-12-01`；程序状态 **passed**。

- **u1**
  - raw_statement：Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia
  - contextualized_statement：Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia
  - memory_quotes：["Likes Earl Grey tea because of its rich history, tradition, and bergamot aroma that evokes nostalgia"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

unresolved：[]

程序 errors：[]

程序 warnings：[]

助手语义初评：u1 逐字保留喜好与历史、传统、佛手柑香气及怀旧之间的关系，没有明显新增或遗漏；单元维持复合原因并非错误，但若只修改一个原因，后续范围判断器必须在内部处理。主体在原文中省略，模型未列为未决，不能将用户 ID 直接扩成姓名。

## 案例 4：4ffee399-c31f-4827-b5fc-5c661baf1fc9

旧记忆：Experiences stress due to historical accuracy demands and tight production schedules

实际上下文：null；来源用户 ID：`1b846c59-456e-9550-dffd-4d23f1eca81f`。

来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json`；目标会话组：`1b846c59-456e-9550-dffd-4d23f1eca81f:s005`。目标会话可供人工审阅；并不作为拆分器输入。

请求一次，5.869 秒，返回模型 `qwen-plus-2025-12-01`；程序状态 **needs_review**。

- **u1**
  - raw_statement：Experiences stress due to historical accuracy demands and tight production schedules
  - contextualized_statement：Experiences stress due to historical accuracy demands and tight production schedules
  - memory_quotes：["Experiences stress due to historical accuracy demands and tight production schedules"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

unresolved：["Subject of 'Experiences stress' is unspecified (e.g., who or what experiences stress)", "No explicit identification of the agent or entity subject to historical accuracy demands and tight production schedules", "No temporal specification (e.g., when this stress occurs or occurred)", "No clarification whether 'historical accuracy demands' and 'tight production schedules' are concurrent, independent, or jointly causal"]

程序 errors：[]

程序 warnings：["unresolved issues reported by model"]

助手语义初评：u1 完整保留历史准确性要求和紧张制作日程两个压力来源，未说压力已经消失，也未从后续会话添加事实；主体及时间未在原文明确，模型列为未决。两个原因被合在一个单元，是否分别处理留给后续范围判断；程序待复核由 unresolved 触发，时间未指明并不表示必须捏造时间。

## 案例 5：05afde13-35bd-4d26-bbae-6de427d58db1

旧记忆：Works at Blockchain Tech as a senior developer

实际上下文：null；来源用户 ID：`348492a7-cfe4-ee1d-73c3-c276d6ba8277`。

来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/before.json`；目标会话组：`348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003`。目标会话可供人工审阅；并不作为拆分器输入。

请求一次，6.588 秒，返回模型 `qwen-plus-2025-12-01`；程序状态 **failed**。

- **u1**
  - raw_statement：Works at Blockchain Tech as a senior developer
  - contextualized_statement：Works at Blockchain Tech as a senior developer
  - memory_quotes：["Works at Blockchain Tech as a senior developer"]
  - context_quotes：[]
  - entities：[{"type": "organization", "name": "Blockchain Tech", "disambiguation_support": "explicit name in memory"}, {"type": "job_title", "name": "senior developer", "disambiguation_support": "explicit title in memory"}]
  - condition：null；valid_time：null

unresolved：["The subject (who 'works') is not explicitly named — pronoun or referent is missing; identity of the person is unresolved.", "No temporal scope (e.g., current, past, future) is specified — tense is ambiguous (present habitual vs. present continuous vs. generic fact)."]

程序 errors：["units[0].entities must be a list of nonempty strings"]

程序 warnings：["unresolved issues reported by model"]

助手语义初评：u1 保留 Blockchain Tech 与 senior developer 的雇主—职位关系，未推断离职或转职；主体在原文中省略且模型标记未决。引文逐字命中，但 entities 是对象数组而不是当前 schema 要求的字符串数组，程序因此失败。整条关系可供判断；若新证据只影响职位或雇主，仍需后续在该单元内部划分影响范围。

## 建议

建议继续修改和离线验证拆分器：重点是确保引文连续逐字、实体类型遵循 schema、避免整体单元与拆分单元冗余，并明确区分归属、指代不确定和单独引文的充分性。不要根据五例或程序通过数声称整体效果可靠；也不要把 failed 或仅有自动通过的单元当作已人工确认事实。保持复合单元并不必然错误，但下游局部影响范围判断需要能够处理其内部属性。
