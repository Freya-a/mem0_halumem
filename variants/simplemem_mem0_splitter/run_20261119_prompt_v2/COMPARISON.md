# SimpleMem 拆分提示词：五案例前后对照

## 范围和方法

两版使用相同五条 `memory_id`、完整旧记忆及 `source_context`；两次输入均为 null。v2 在原提示词后追加针对引文、归属、粒度、原因/条件、指代和时间的指令；其余模型、温度、上限、系统提示词、直接连接和程序校验相同。保留两版实际消息，分别在各自 `case_N.json` 的 `request.messages`。两版每条各一次；这是温度 0.1 下各一次的小样本对照，多个指令同时变化，不能排除生成随机性或将变化归因于某条指令。

以下表格两列按各版本自己的单元编号顺序并排，**同一行不表示两个单元语义一一对应**。每条均显示原始模型文本；模型原始响应、解析结果、校验和引文偏移保留在各运行的 JSON 中。助手语义初评不是人工验收。

基准自动校验：{"failed": 1, "needs_review": 3, "passed": 1}；v2：{"failed": 1, "needs_review": 1, "passed": 3}。基准 17 个 memory_quote 命中 16 个，v2 15 个命中 14 个，均无多次命中；这是逐字检查，不是语义正确率。

v2 使用 `qwen-plus-2025-12-01`，调用 5 次、收到 5 次响应、失败 0 次，总耗时 48.785 秒；每例各一次，SDK 自动重试 0。

## 案例 1：halumem-1-s4-m1-old1

旧记忆：Martin Mark Pets I like Dogs, especially Labradors reason: I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit.

实际来源上下文：null

自动状态：基准 **failed**；v2 **failed**。

| 基准版本 | v2 版本 |
| --- | --- |
| **"u1"**<br>raw_statement: "Martin Mark Pets I like Dogs, especially Labradors"<br>contextualized_statement: "Martin Mark likes dogs, especially Labradors"<br>memory_quotes: ["Martin Mark Pets I like Dogs, especially Labradors"]<br>context_quotes: []<br>entities: ["Martin Mark", "Dogs", "Labradors"]<br>condition: null<br>valid_time: null | **"u1"**<br>raw_statement: "Martin Mark likes dogs."<br>contextualized_statement: "Martin Mark likes dogs."<br>memory_quotes: ["Martin Mark Pets I like Dogs"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u2"**<br>raw_statement: "I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit."<br>contextualized_statement: "The speaker loves Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps the speaker stay fit."<br>memory_quotes: ["I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit."]<br>context_quotes: []<br>entities: ["Labradors"]<br>condition: null<br>valid_time: null | **"u2"**<br>raw_statement: "Martin Mark likes Labradors especially."<br>contextualized_statement: "Martin Mark likes Labradors especially."<br>memory_quotes: ["I like Dogs, especially Labradors"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u3"**<br>raw_statement: "Labradors are friendly"<br>contextualized_statement: "Labradors are friendly (according to the speaker)"<br>memory_quotes: ["they are friendly"]<br>context_quotes: []<br>entities: ["Labradors"]<br>condition: null<br>valid_time: null | **"u3"**<br>raw_statement: "Martin Mark loves Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps him stay fit."<br>contextualized_statement: "Martin Mark loves Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps him stay fit."<br>memory_quotes: ["reason: I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit."]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u4"**<br>raw_statement: "Labradors are loyal"<br>contextualized_statement: "Labradors are loyal (according to the speaker)"<br>memory_quotes: ["they are loyal"]<br>context_quotes: []<br>entities: ["Labradors"]<br>condition: null<br>valid_time: null | **"u4"**<br>raw_statement: "Martin Mark believes Labradors are friendly."<br>contextualized_statement: "Martin Mark believes Labradors are friendly."<br>memory_quotes: ["they are friendly"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u5"**<br>raw_statement: "Labradors are great companions for outdoor activities like jogging"<br>contextualized_statement: "Labradors are great companions for outdoor activities like jogging (according to the speaker)"<br>memory_quotes: ["great companions for outdoor activities like jogging"]<br>context_quotes: []<br>entities: ["Labradors", "jogging"]<br>condition: null<br>valid_time: null | **"u5"**<br>raw_statement: "Martin Mark believes Labradors are loyal."<br>contextualized_statement: "Martin Mark believes Labradors are loyal."<br>memory_quotes: ["they are ... loyal"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u6"**<br>raw_statement: "Jogging helps me stay fit"<br>contextualized_statement: "Jogging helps the speaker stay fit (according to the speaker)"<br>memory_quotes: ["which helps me stay fit"]<br>context_quotes: []<br>entities: ["jogging"]<br>condition: null<br>valid_time: null | **"u6"**<br>raw_statement: "Martin Mark believes Labradors are great companions for outdoor activities like jogging."<br>contextualized_statement: "Martin Mark believes Labradors are great companions for outdoor activities like jogging."<br>memory_quotes: ["great companions for outdoor activities like jogging"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| — | **"u7"**<br>raw_statement: "Martin Mark believes jogging helps him stay fit."<br>contextualized_statement: "Martin Mark believes jogging helps him stay fit."<br>memory_quotes: ["which helps me stay fit"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |

| 项目 | 基准版本 | v2 版本 |
| --- | --- | --- |
| unresolved | ["Pronoun 'I' is ambiguous without source context; assumed to refer to Martin Mark but not explicitly confirmed in text.", "The phrase 'Martin Mark Pets' is syntactically unclear — could be a name + category label, a typo, or a compound identifier; no disambiguating context provided.", "No explicit indication whether 'Martin Mark' is one person (e.g., full name) or two people (e.g., Martin and Mark); 'Pets' may be a category tag or part of a title."] | ["The referent of 'Martin Mark' is ambiguous — it may be a single person's full name, two separate names, or a typo; no disambiguating context is provided.", "The pronoun 'me' in 'I love Labradors...' and 'helps me stay fit' is not explicitly resolved to 'Martin Mark' in the text; while strongly implied, the memory does not state that 'I' refers to 'Martin Mark', so the identity of the speaker remains formally unresolved.", "The phrase 'Martin Mark Pets' lacks grammatical clarity — it may be a label, a category header, or a malformed phrase; its syntactic role and semantic contribution are unresolved."] |
| 程序 errors | ["units[3].memory_quotes[0] not found verbatim in source"] | ["units[4].memory_quotes[0] not found verbatim in source"] |
| 程序 warnings | ["unresolved issues reported by model", "units[0]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[1]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[2]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[3]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[4]: changed contextualized_statement without context quotes; check whether disambiguation was used", "units[5]: changed contextualized_statement without context quotes; check whether disambiguation was used"] | ["unresolved issues reported by model"] |

**助手初评：**基准 u4 引文 `they are loyal` 未逐字出现；新版 u5 的 `they are ... loyal` 仍未逐字出现，省略号不是原文的一部分，因此两版均失败。新版 u4–u7 使用 “Martin Mark believes” 增加观点形式，但身份并未由上下文确认，且其 unresolved 明确说 I/me 未确认，却在多个单元确定为 Martin Mark，矛盾比基准更广；“believes”是否精准表达原本列出的喜爱理由也须审核。新版 u3 与 u4–u7 重复多项内容，u7 的短引文单独不能确定 which 的先行词。没有明显丢掉主要文本内容；主体确认和证据充分性仍是问题。

## 案例 2：halumem-1-s9-m2-old0

旧记忆：Martin Mark Games I dislike Violent video games reason: I avoid violent video games because they promote aggression, which is contrary to my values of peace and well-being.

实际来源上下文：null

自动状态：基准 **needs_review**；v2 **needs_review**。

| 基准版本 | v2 版本 |
| --- | --- |
| **"u1"**<br>raw_statement: "I dislike violent video games."<br>contextualized_statement: "I dislike violent video games."<br>memory_quotes: ["I dislike Violent video games"]<br>context_quotes: []<br>entities: ["I", "violent video games"]<br>condition: null<br>valid_time: null | **"u1"**<br>raw_statement: "I dislike violent video games."<br>contextualized_statement: "I dislike violent video games."<br>memory_quotes: ["I dislike Violent video games"]<br>context_quotes: []<br>entities: []<br>condition: null<br>valid_time: null |
| **"u2"**<br>raw_statement: "I avoid violent video games because they promote aggression."<br>contextualized_statement: "I avoid violent video games because they promote aggression."<br>memory_quotes: ["I avoid violent video games because they promote aggression"]<br>context_quotes: []<br>entities: ["I", "violent video games", "aggression"]<br>condition: null<br>valid_time: null | **"u2"**<br>raw_statement: "I avoid violent video games because they promote aggression."<br>contextualized_statement: "I avoid violent video games because they promote aggression."<br>memory_quotes: ["I avoid violent video games because they promote aggression"]<br>context_quotes: []<br>entities: []<br>condition: null<br>valid_time: null |
| **"u3"**<br>raw_statement: "Violent video games promote aggression."<br>contextualized_statement: "Violent video games promote aggression."<br>memory_quotes: ["they promote aggression"]<br>context_quotes: []<br>entities: ["violent video games", "aggression"]<br>condition: null<br>valid_time: null | **"u3"**<br>raw_statement: "Violent video games promote aggression, which is contrary to my values of peace and well-being."<br>contextualized_statement: "Violent video games promote aggression, which is contrary to my values of peace and well-being."<br>memory_quotes: ["they promote aggression, which is contrary to my values of peace and well-being"]<br>context_quotes: []<br>entities: []<br>condition: null<br>valid_time: null |
| **"u4"**<br>raw_statement: "Promoting aggression is contrary to my values of peace and well-being."<br>contextualized_statement: "Promoting aggression is contrary to my values of peace and well-being."<br>memory_quotes: ["which is contrary to my values of peace and well-being"]<br>context_quotes: []<br>entities: ["aggression", "peace", "well-being", "my values"]<br>condition: null<br>valid_time: null | — |
| **"u5"**<br>raw_statement: "My values include peace and well-being."<br>contextualized_statement: "My values include peace and well-being."<br>memory_quotes: ["my values of peace and well-being"]<br>context_quotes: []<br>entities: ["peace", "well-being", "my values"]<br>condition: null<br>valid_time: null | — |

| 项目 | 基准版本 | v2 版本 |
| --- | --- | --- |
| unresolved | ["The identity of 'I' is not explicitly named in the memory; 'Martin Mark Games' appears at the beginning but is not grammatically or semantically linked to the first-person statements — it may be a misformatted name, a title, a system tag, or unrelated metadata. No source context is provided to resolve this.", "The phrase 'Martin Mark Games' cannot be reliably assigned as an entity related to the speaker or content without disambiguating context.", "Capitalization of 'Violent video games' is inconsistent with standard noun phrasing and may reflect tagging or formatting artifact rather than intentional proper noun usage."] | ["The identity of 'I' is not explicitly named in the memory; 'Martin Mark Games' appears at the beginning but is ambiguous — it could be a name, a title, a misformatted list, or unrelated text. No verbatim support links 'Martin Mark Games' to the speaker of 'I'.", "Capitalization of 'Violent video games' is inconsistent with standard noun phrasing; it may reflect emphasis or formatting artifact, but no context clarifies intent.", "'Martin Mark Games' is not syntactically integrated into the declarative clauses and lacks grammatical connection to the subsequent 'I' statements; its semantic role (e.g., speaker identifier, topic label, error) is unresolved."] |
| 程序 errors | [] | [] |
| 程序 warnings | ["unresolved issues reported by model"] | ["unresolved issues reported by model"] |

**助手初评：**两版均保留否定偏好和避免的原因，主要内容仍可见。新版由五单元变为三单元，减少了部分重复，但新版 u3 仍把“暴力游戏促进攻击性”写成未加说话者归属的陈述，尽管句中出现 my values，不能保证读者将前半句理解为个人观点；u2 与 u3 也重复该内容。新版不再单独提取价值观，是否影响独立判断需视后续判断器需求评估。I 的身份两版均保留未决；大小写提示并不一定是有意义的语义未决项。

## 案例 3：halumem-1-s11-m1-old1

旧记忆：[Sep 06, 2025, 22:43:36][Persona Memory]Martin Mark Movies I like to watch Documentaries reason: I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.

实际来源上下文：null

自动状态：基准 **needs_review**；v2 **passed**。

| 基准版本 | v2 版本 |
| --- | --- |
| **"u1"**<br>raw_statement: "Martin Mark Movies I like to watch Documentaries"<br>contextualized_statement: "Martin Mark likes to watch documentaries."<br>memory_quotes: ["Martin Mark Movies I like to watch Documentaries"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null | **"u1"**<br>raw_statement: "Martin Mark likes to watch documentaries."<br>contextualized_statement: "Martin Mark likes to watch documentaries."<br>memory_quotes: ["Martin Mark Movies I like to watch Documentaries"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u2"**<br>raw_statement: "I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge."<br>contextualized_statement: "I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge."<br>memory_quotes: ["I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge."]<br>context_quotes: []<br>entities: []<br>condition: null<br>valid_time: null | **"u2"**<br>raw_statement: "Martin Mark enjoys documentaries because they are informative and provide real-world insights, which complement his thirst for knowledge."<br>contextualized_statement: "Martin Mark enjoys documentaries because they are informative and provide real-world insights, which complement his thirst for knowledge."<br>memory_quotes: ["I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge."]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |

| 项目 | 基准版本 | v2 版本 |
| --- | --- | --- |
| unresolved | ["Pronoun 'I' in 'I enjoy documentaries...' is not disambiguated to a specific person in the absence of source context; 'Martin Mark' is named but not explicitly equated with 'I'.", "The phrase 'Martin Mark Movies' is ambiguous — it may be a name, a title, or a malformed phrase (e.g., intended as 'Martin Mark: Movies I like to watch'); no source context supports resolution."] | [] |
| 程序 errors | [] | [] |
| 程序 warnings | ["unresolved issues reported by model", "units[0]: changed contextualized_statement without context quotes; check whether disambiguation was used"] | [] |

**助手初评：**两版均保留偏好及信息性、现实洞见和求知欲之间的整体关系；新版没有拆开各理由，粒度基本未变。基准 u1 将 I 归为 Martin Mark，但 u2 保留 I 并在 unresolved 中报告不确定；新版 u1、u2 全部确定为 Martin Mark，同时 unresolved 为空。原始文本采用姓名、分类和第一人称混排格式，关联看似合理但没有提供额外上下文；不能仅凭自动 passed 认定消歧可靠，这是相对于基准未决提示减少的语义风险。记录前缀未被当作 valid_time，两版均为 null。

## 案例 4：halumem-1-s16-m3-old0

旧记忆：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.

实际来源上下文：null

自动状态：基准 **passed**；v2 **passed**。

| 基准版本 | v2 版本 |
| --- | --- |
| **"u1"**<br>raw_statement: "Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."<br>contextualized_statement: "Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."<br>memory_quotes: ["Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."]<br>context_quotes: []<br>entities: ["Martin"]<br>condition: "even if he retires from his current role"<br>valid_time: null | **"u1"**<br>raw_statement: "Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."<br>contextualized_statement: "Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."<br>memory_quotes: ["Martin desires to continue contributing to healthcare initiatives even if he retires from his current role."]<br>context_quotes: []<br>entities: ["Martin"]<br>condition: "even if he retires from his current role"<br>valid_time: null |

| 项目 | 基准版本 | v2 版本 |
| --- | --- | --- |
| unresolved | [] | [] |
| 程序 errors | [] | [] |
| 程序 warnings | [] | [] |

**助手初评：**两版单元、引用、condition、时间和未决项均一致，保留 desire 与 even if，没有声称已经退休。even if 带让步意味，condition 字段的下游解释不能简化为仅在退休发生时才有该愿望。没有发现明显遗漏或新增。

## 案例 5：halumem-1-s3-m1-old0

旧记忆：Martin Mark is considering a career change due to health impacts from his current role.

实际来源上下文：null

自动状态：基准 **needs_review**；v2 **passed**。

| 基准版本 | v2 版本 |
| --- | --- |
| **"u1"**<br>raw_statement: "Martin Mark is considering a career change"<br>contextualized_statement: "Martin Mark is considering a career change"<br>memory_quotes: ["Martin Mark is considering a career change"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null | **"u1"**<br>raw_statement: "Martin Mark is considering a career change."<br>contextualized_statement: "Martin Mark is considering a career change."<br>memory_quotes: ["Martin Mark is considering a career change"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u2"**<br>raw_statement: "Martin Mark is considering a career change due to health impacts from his current role"<br>contextualized_statement: "Martin Mark is considering a career change due to health impacts from his current role"<br>memory_quotes: ["Martin Mark is considering a career change due to health impacts from his current role"]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: "health impacts from his current role"<br>valid_time: null | **"u2"**<br>raw_statement: "Martin Mark is considering a career change due to health impacts from his current role."<br>contextualized_statement: "Martin Mark is considering a career change due to health impacts from his current role."<br>memory_quotes: ["Martin Mark is considering a career change due to health impacts from his current role."]<br>context_quotes: []<br>entities: ["Martin Mark"]<br>condition: null<br>valid_time: null |
| **"u3"**<br>raw_statement: "health impacts from his current role"<br>contextualized_statement: "health impacts from his current role"<br>memory_quotes: ["health impacts from his current role"]<br>context_quotes: []<br>entities: []<br>condition: null<br>valid_time: null | — |

| 项目 | 基准版本 | v2 版本 |
| --- | --- | --- |
| unresolved | ["The pronoun 'his' is ambiguous without source context confirming antecedent; however, co-reference with 'Martin Mark' is strongly supported by grammatical and semantic proximity and is retained as resolved in entities where appropriate. No external disambiguation was needed or used, so no unresolved issue is logged per requirement."] | [] |
| 程序 errors | [] | [] |
| 程序 warnings | ["unresolved issues reported by model"] | [] |

**助手初评：**新版 u2 把原因留在陈述中，condition 改为 null，修复了基准把原因填入 condition 的问题；残缺的基准 u3 消失，矛盾的 unresolved 也消失。新版仍同时输出简化的考虑转职 u1 和包含原因的 u2，存在包含关系与冗余；是否需要两项取决于后续独立判断需求。his 与 Martin Mark 的联系有语法支持；是否需要保留不确定性仍由来源约定和人工审核决定，不能因为没有 unresolved 就认定一定正确。

## 是否保留 v2

建议**保留为实验版本，不替换基准或用于自动更新**。新版在案例 5 改善了原因与条件的区分、去掉残句，程序状态通过数增加；但案例 1 仍有无效引文与重复，且不确定身份被更广泛地写为确定身份；案例 3 的程序通过掩盖了待确认的身份推断，案例 2 仍有无归属观点风险。证据不足以断言 v2 总体语义质量优于基准。后续应扩展案例、预设人工标注标准并独立审核；对 failed、needs_review 和即使 passed 但存在语义风险的输出都不要直接作为已验证事实写入记忆。
