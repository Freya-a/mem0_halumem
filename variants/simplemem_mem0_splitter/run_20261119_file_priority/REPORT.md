# 文件优先配置：五例真实试运行

本轮读取 `.env.server.medium-full` 中的 key 与 workspace，地址模板来自 `config/medium_full_qwen_plus_20251201.json`。文件与模板沿用项目加载规则，模型实际返回证明本轮组合可访问该模型；不输出凭据。客户端直连 `trust_env=False`，SDK 自动重试 0，重定向关闭。原提示词未改，旧两轮记录保留。

固定模型 `qwen-plus-2025-12-01`；请求 5 次，收到 5 个模型响应，接口失败 0 次；各例各一次，共 55.954 秒。

以下是模型输出的完整子事实和引文（`null` 为 JSON 空值），保留模型原文及错误，不等于经人工验收。自动程序只检查结构和逐字命中；语义分析为本次助手初步检查，需人工复核。每条完整 JSON、原始响应及引文偏移另存于对应 case 文件。

## 案例 1：halumem-1-s4-m1-old1

旧记忆：Martin Mark Pets I like Dogs, especially Labradors reason: I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit.

调用：18.284 秒；返回模型 `qwen-plus-2025-12-01`；自动校验 **failed**。

- **u1**
  - raw_statement：Martin Mark Pets I like Dogs, especially Labradors
  - contextualized_statement：Martin Mark likes dogs, especially Labradors
  - memory_quotes：["Martin Mark Pets I like Dogs, especially Labradors"]
  - context_quotes：[]
  - entities：["Martin Mark", "Dogs", "Labradors"]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit.
  - contextualized_statement：The speaker loves Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps the speaker stay fit.
  - memory_quotes：["I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit."]
  - context_quotes：[]
  - entities：["Labradors"]
  - condition：null；valid_time：null
- **u3**
  - raw_statement：Labradors are friendly
  - contextualized_statement：Labradors are friendly (according to the speaker)
  - memory_quotes：["they are friendly"]
  - context_quotes：[]
  - entities：["Labradors"]
  - condition：null；valid_time：null
- **u4**
  - raw_statement：Labradors are loyal
  - contextualized_statement：Labradors are loyal (according to the speaker)
  - memory_quotes：["they are loyal"]
  - context_quotes：[]
  - entities：["Labradors"]
  - condition：null；valid_time：null
- **u5**
  - raw_statement：Labradors are great companions for outdoor activities like jogging
  - contextualized_statement：Labradors are great companions for outdoor activities like jogging (according to the speaker)
  - memory_quotes：["great companions for outdoor activities like jogging"]
  - context_quotes：[]
  - entities：["Labradors", "jogging"]
  - condition：null；valid_time：null
- **u6**
  - raw_statement：Jogging helps me stay fit
  - contextualized_statement：Jogging helps the speaker stay fit (according to the speaker)
  - memory_quotes：["which helps me stay fit"]
  - context_quotes：[]
  - entities：["jogging"]
  - condition：null；valid_time：null

模型 unresolved：["Pronoun 'I' is ambiguous without source context; assumed to refer to Martin Mark but not explicitly confirmed in text.", "The phrase 'Martin Mark Pets' is syntactically unclear — could be a name + category label, a typo, or a compound identifier; no disambiguating context provided.", "No explicit indication whether 'Martin Mark' is one person (e.g., full name) or two people (e.g., Martin and Mark); 'Pets' may be a category tag or part of a title."]

程序错误：["units[3].memory_quotes[0] not found verbatim in source"]

程序警告：["unresolved issues reported by model", "units[0]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[1]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[2]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[3]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[4]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[5]: changed contextualized_statement without context quotes; check whether disambiguation was used"]

助手语义初评：原文主要信息在 u1–u6 中出现，但 u2 与 u3–u6 重复，粒度不一致；u3–u5 的独立表述弱化了“作为喜爱理由/说话者观点”的限定。u4 引文“they are loyal”不在原文，原文为“they are friendly, loyal”，该单元自动校验失败。u1 将 I 归到 Martin Mark 需要核实；模型自己也列为未决。u6 的引文单独缺少 jogging 先行词，需与上下文一起支持。

## 案例 2：halumem-1-s9-m2-old0

旧记忆：Martin Mark Games I dislike Violent video games reason: I avoid violent video games because they promote aggression, which is contrary to my values of peace and well-being.

调用：15.268 秒；返回模型 `qwen-plus-2025-12-01`；自动校验 **needs_review**。

- **u1**
  - raw_statement：I dislike violent video games.
  - contextualized_statement：I dislike violent video games.
  - memory_quotes：["I dislike Violent video games"]
  - context_quotes：[]
  - entities：["I", "violent video games"]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：I avoid violent video games because they promote aggression.
  - contextualized_statement：I avoid violent video games because they promote aggression.
  - memory_quotes：["I avoid violent video games because they promote aggression"]
  - context_quotes：[]
  - entities：["I", "violent video games", "aggression"]
  - condition：null；valid_time：null
- **u3**
  - raw_statement：Violent video games promote aggression.
  - contextualized_statement：Violent video games promote aggression.
  - memory_quotes：["they promote aggression"]
  - context_quotes：[]
  - entities：["violent video games", "aggression"]
  - condition：null；valid_time：null
- **u4**
  - raw_statement：Promoting aggression is contrary to my values of peace and well-being.
  - contextualized_statement：Promoting aggression is contrary to my values of peace and well-being.
  - memory_quotes：["which is contrary to my values of peace and well-being"]
  - context_quotes：[]
  - entities：["aggression", "peace", "well-being", "my values"]
  - condition：null；valid_time：null
- **u5**
  - raw_statement：My values include peace and well-being.
  - contextualized_statement：My values include peace and well-being.
  - memory_quotes：["my values of peace and well-being"]
  - context_quotes：[]
  - entities：["peace", "well-being", "my values"]
  - condition：null；valid_time：null

模型 unresolved：["The identity of 'I' is not explicitly named in the memory; 'Martin Mark Games' appears at the beginning but is not grammatically or semantically linked to the first-person statements — it may be a misformatted name, a title, a system tag, or unrelated metadata. No source context is provided to resolve this.", "The phrase 'Martin Mark Games' cannot be reliably assigned as an entity related to the speaker or content without disambiguating context.", "Capitalization of 'Violent video games' is inconsistent with standard noun phrasing and may reflect tagging or formatting artifact rather than intentional proper noun usage."]

程序错误：[]

程序警告：["unresolved issues reported by model"]

助手语义初评：保留了不喜欢、避免、理由和价值观，但 u2 与 u3 重复；u3 把说话者给出的理由表达为无归属的客观事实，存在语义强化风险，u4 的 which 指代也应结合原文核查。I 与 Martin Mark 的关联被列为未决。

## 案例 3：halumem-1-s11-m1-old1

旧记忆：[Sep 06, 2025, 22:43:36][Persona Memory]Martin Mark Movies I like to watch Documentaries reason: I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.

调用：8.967 秒；返回模型 `qwen-plus-2025-12-01`；自动校验 **needs_review**。

- **u1**
  - raw_statement：Martin Mark Movies I like to watch Documentaries
  - contextualized_statement：Martin Mark likes to watch documentaries.
  - memory_quotes：["Martin Mark Movies I like to watch Documentaries"]
  - context_quotes：[]
  - entities：["Martin Mark"]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.
  - contextualized_statement：I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.
  - memory_quotes：["I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge."]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

模型 unresolved：["Pronoun 'I' in 'I enjoy documentaries...' is not disambiguated to a specific person in the absence of source context; 'Martin Mark' is named but not explicitly equated with 'I'.", "The phrase 'Martin Mark Movies' is ambiguous — it may be a name, a title, or a malformed phrase (e.g., intended as 'Martin Mark: Movies I like to watch'); no source context supports resolution."]

程序错误：[]

程序警告：["unresolved issues reported by model", "units[0]: changed contextualized_statement without context quotes; check whether disambiguation was used"]

助手语义初评：完整保留了偏好与整体理由，但 u2 把多个可分别判断的原因保留在同一单元，粒度偏粗；u1 将 I 归到 Martin Mark 与未决指代并存，需核实。记录前缀未被填入 valid_time，符合不把记录时间直接当事实有效时间的要求。

## 案例 4：halumem-1-s16-m3-old0

旧记忆：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.

调用：4.317 秒；返回模型 `qwen-plus-2025-12-01`；自动校验 **passed**。

- **u1**
  - raw_statement：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.
  - contextualized_statement：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.
  - memory_quotes：["Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."]
  - context_quotes：[]
  - entities：["Martin"]
  - condition："even if he retires from his current role"；valid_time：null

模型 unresolved：[]

程序错误：[]

程序警告：[]

助手语义初评：保留 desire 和 even if 条件，没有断言退休或把条件当成已发生事实；粒度可供判断。自动 passed 仅覆盖结构与逐字依据，仍需人工语义审核。

## 案例 5：halumem-1-s3-m1-old0

旧记忆：Martin Mark is considering a career change due to health impacts from his current role.

调用：9.118 秒；返回模型 `qwen-plus-2025-12-01`；自动校验 **needs_review**。

- **u1**
  - raw_statement：Martin Mark is considering a career change
  - contextualized_statement：Martin Mark is considering a career change
  - memory_quotes：["Martin Mark is considering a career change"]
  - context_quotes：[]
  - entities：["Martin Mark"]
  - condition：null；valid_time：null
- **u2**
  - raw_statement：Martin Mark is considering a career change due to health impacts from his current role
  - contextualized_statement：Martin Mark is considering a career change due to health impacts from his current role
  - memory_quotes：["Martin Mark is considering a career change due to health impacts from his current role"]
  - context_quotes：[]
  - entities：["Martin Mark"]
  - condition："health impacts from his current role"；valid_time：null
- **u3**
  - raw_statement：health impacts from his current role
  - contextualized_statement：health impacts from his current role
  - memory_quotes：["health impacts from his current role"]
  - context_quotes：[]
  - entities：[]
  - condition：null；valid_time：null

模型 unresolved：["The pronoun 'his' is ambiguous without source context confirming antecedent; however, co-reference with 'Martin Mark' is strongly supported by grammatical and semantic proximity and is retained as resolved in entities where appropriate. No external disambiguation was needed or used, so no unresolved issue is logged per requirement."]

程序错误：[]

程序警告：["unresolved issues reported by model"]

助手语义初评：u2 保留了考虑转职与原因，u1 与 u2 重复，u3 缺少明确主体且不能独立表达完整关系。u2 将原因 health impacts 填入 condition，属于原因与适用条件混淆；unresolved 中自称未记录未决项的表述与其本身出现在 unresolved 中矛盾。

## 使用判断

本次证明文件配置及直连路径可以访问固定模型，但不能证明上一次 403 的唯一原因。五例中 1 例自动通过、3 例需复核、1 例失败；每例均需人工语义审核。当前适合使用完整错误和待复核状态做小规模、非生产判断器接口联调；不要将所有拆分单元作为已验证事实自动传递或用于更新，需先解决无效引文、原因与条件混淆和语义归属问题。
