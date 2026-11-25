# 对齐器五案输出审计

此文依据各版本已保存的 parsed 原始模型输出自动整理，逐条保留双方引文与关系；不将结构通过当作语义通过。三版输入按 v3 运行记录核对一致。v1 提示词位于 `evidence_aligner/aligner.py` 的 SYSTEM，v2/v3 分别位于 `prompts/alignment_v2.txt`、`prompts/alignment_v3.txt`。

v1 每条包含 IDs、attribute、change_type、old_value、new_claim、双侧带 source_id 引文、conditions、time_expressions、event_date、unknowns；v2 为 old/new_claim（subject、object、attribute、statement、qualifiers、event_date）、target_relation、change_type、双侧引文、change_evidence、解释和 unknowns；v3 为 IDs、attribute、relation、字符串双侧引文、qualifiers（side、kind、quote、claim_quote）和 missing_evidence，来源与位置由验证器推导。空限定词不能作为适用于全域的证据。

v3 事后 `runs/v3_paired_20261120/semantic_audit.json` 非盲人工审核，指出职业历史的 state_change 不由获客证实；跳伞把模拟体验和安全优先错误用于真实极限运动及受伤理由的变化；Susan 关联旧单元却缺旧引文；转岗旧 `lately` 来自未关联来源。请参见 `evidence_aligner/runs/v3_paired_20261120/REPORT.md`。

## susan

### v1

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `friendship`；关系 `support`；旧单元 `['friendship']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"}]
  - 新引文：[{"source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."}]
- 记录 1：属性 `support_context`；关系 `supplement`；旧单元 `['support']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}]
  - 新引文：[{"source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."}]
  - unknowns: ["Daniel's identity or relationship status (e.g., friend, colleague, mentor) is not specified in user's own words"]
- 记录 2：属性 `career_status`；关系 `plan`；旧单元 `[]`，新单元 `['unsplit-new-0']`。
  - 旧引文：[]
  - 新引文：[{"source_id": "new-0", "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."}]
  - time_expressions: ["lately"]
  - unknowns: ["Current employer name", "Current job title", "Timeline for job search completion", "Whether any applications or interviews have occurred yet"]

### v2

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `relationship`；关系 `support`，target_relation `same`；旧单元 `['friendship']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "friend named ThomasSusan"}]
  - 新引文：[{"source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."}]
- 记录 1：属性 `support`；关系 `support`，target_relation `same`；旧单元 `['support']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed", "quote": "provides support and encouragement"}]
  - 新引文：[{"source_id": "new-2", "quote": "Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities."}]
- 记录 2：属性 `well-being_support_from_role`；关系 `no_clear_change`，target_relation `different`；旧单元 `['friendship', 'support']`，新单元 `['unsplit-new-0']`。
  - 旧引文：[{"source_id": "ctx-1", "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life."}]
  - 新引文：[{"source_id": "new-0", "quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."}]
  - unknowns: ["Whether the user previously held a view about their current role’s support for well-being"]

### v3

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `friendship`；关系 `support`；旧单元 `['friendship']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["friend named ThomasSusan"]
  - 新引文：["Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."]
- 记录 1：属性 `support`；关系 `supplement`；旧单元 `['support']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["provides support and encouragement"]
  - 新引文：["Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."]
- 记录 2：属性 `career_wellbeing_alignment`；关系 `new_information`；旧单元 `['friendship', 'support']`，新单元 `['unsplit-new-0']`。
  - 旧引文：[]
  - 新引文：["I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."]
  - qualifiers: [{"side": "new", "kind": "time", "quote": "lately", "claim_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like."}]

## promotion

### v1

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `job_title`；关系 `state_change`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Director"}]
  - 新引文：[{"source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}]
  - time_expressions: [{"source_id": "new-0", "quote": "recently"}]
- 记录 1：属性 `employer`；关系 `no_clear_change`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Historical Productions Ltd."}]
  - 新引文：[{"source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}]
  - time_expressions: [{"source_id": "new-0", "quote": "recently"}]

### v2

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `employer`；关系 `support`，target_relation `same`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Historical Productions Ltd."}]
  - 新引文：[{"source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}]
- 记录 1：属性 `job_title`；关系 `state_change`，target_relation `partially_overlapping`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e13b825e-7ec7-4760-821e-0581d8da5650", "quote": "Director"}]
  - 新引文：[{"source_id": "new-0", "quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}]

### v3

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `employer`；关系 `no_clear_change`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["Historical Productions Ltd."]
  - 新引文：["I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"]
- 记录 1：属性 `job_title`；关系 `state_change`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["Director"]
  - 新引文：["I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"]
  - qualifiers: [{"side": "new", "kind": "time", "quote": "recently", "claim_quote": "I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"}]

## career_history

### v1

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `employer`；关系 `state_change`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Blockchain Tech"}]
  - 新引文：[{"source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}]
  - time_expressions: [{"source_id": "new-0", "quote": "lately"}]
- 记录 1：属性 `title`；关系 `state_change`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "senior developer"}]
  - 新引文：[{"source_id": "new-0", "quote": "my consulting firm finally secured some initial clients"}]
  - time_expressions: [{"source_id": "new-0", "quote": "lately"}]
  - unknowns: ["exact title or role name in the consulting firm"]
- 记录 2：属性 `client_milestone`；关系 `new_information`；旧单元 `[]`，新单元 `['manually_mapped_new']`。
  - 旧引文：[]
  - 新引文：[{"source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}]
  - time_expressions: [{"source_id": "new-0", "quote": "lately"}]
- 记录 3：属性 `network_contact_effectiveness`；关系 `new_information`；旧单元 `[]`，新单元 `['unsplit-new-2']`。
  - 旧引文：[]
  - 新引文：[{"source_id": "new-2", "quote": "MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."}]

### v2

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `historical_employer`；关系 `new_information`，target_relation `different`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "Blockchain Tech"}]
  - 新引文：[{"source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}]
  - unknowns: ["start date of consulting firm", "end date of Blockchain Tech employment"]
- 记录 1：属性 `historical_title`；关系 `new_information`，target_relation `different`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "05afde13-35bd-4d26-bbae-6de427d58db1", "quote": "senior developer"}]
  - 新引文：[{"source_id": "new-0", "quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}]
  - unknowns: ["whether senior developer role has ended", "current formal title at consulting firm"]

### v3

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `employer`；关系 `state_change`；旧单元 `['employer']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["Blockchain Tech"]
  - 新引文：["my consulting firm"]
  - qualifiers: [{"side": "new", "kind": "time", "quote": "lately", "claim_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}]
- 记录 1：属性 `title`；关系 `state_change`；旧单元 `['title']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["senior developer"]
  - 新引文：["consulting firm"]
  - qualifiers: [{"side": "new", "kind": "time", "quote": "lately", "claim_quote": "I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me."}]
- 记录 2：属性 `network_support`；关系 `new_information`；旧单元 `[]`，新单元 `['unsplit-new-2']`。
  - 旧引文：[]
  - 新引文：["MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."]

## transition

### v1

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `transition_progress`；关系 `state_change`；旧单元 `['job_search']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance"}]
  - 新引文：[{"source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}]
  - time_expressions: [{"source_id": "new-0", "quote": "finally"}]

### v2

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `transition_progress`；关系 `state_change`，target_relation `different`；旧单元 `['job_search']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e6ab178b-c0f9-4adb-bfb7-e4648617a950", "quote": "Looking for a new job with better work-life balance"}]
  - 新引文：[{"source_id": "new-0", "quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}]

### v3

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `transition_progress`；关系 `state_change`；旧单元 `['job_search']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["Looking for a new job with better work-life balance"]
  - 新引文：["I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."]
  - qualifiers: [{"side": "old", "kind": "time", "quote": "lately", "claim_quote": "I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."}, {"side": "new", "kind": "time", "quote": "finally", "claim_quote": "I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."}]

## skydiving

### v1

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `attitude_toward_extreme_sports`；关系 `state_change`；旧单元 `['u1']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"}]
  - 新引文：[{"source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}]
  - time_expressions: [{"source_id": "new-0", "quote": "recently"}]
- 记录 1：属性 `reason_for_disliking_extreme_sports`；关系 `state_change`；旧单元 `['u2']`，新单元 `['manually_mapped_new', 'unsplit-new-2', 'unsplit-new-8']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"}]
  - 新引文：[{"source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}, {"source_id": "new-2", "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."}, {"source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
  - conditions: [{"source_id": "new-8", "quote": "For now"}]
  - time_expressions: [{"source_id": "new-0", "quote": "recently"}]
- 记录 2：属性 `commitment_to_safety_and_well_being`；关系 `support`；旧单元 `['u3']`，新单元 `['unsplit-new-8']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being"}]
  - 新引文：[{"source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
  - conditions: [{"source_id": "new-8", "quote": "For now"}]
  - time_expressions: [{"source_id": "new-8", "quote": "For now"}]

### v2

结构状态：`failed`；未匹配旧单元：`[]`。

- 记录 0：属性 `attitude`；关系 `supplement`，target_relation `partially_overlapping`；旧单元 `['u1']`，新单元 `['manually_mapped_new']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving)"}]
  - 新引文：[{"source_id": "new-0", "quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}]
- 记录 1：属性 `reason_for_attitude`；关系 `support`，target_relation `partially_overlapping`；旧单元 `['u2']`，新单元 `['manually_mapped_new', 'unsplit-new-2', 'unsplit-new-8']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk"}]
  - 新引文：[{"source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
- 记录 2：属性 `reason_for_attitude`；关系 `support`，target_relation `partially_overlapping`；旧单元 `['u3']`，新单元 `['unsplit-new-8']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "conflicting with commitment to safety and well-being"}]
  - 新引文：[{"source_id": "new-8", "quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
- 记录 3：属性 `attitude`；关系 `supplement`，target_relation `different`；旧单元 `['u1', 'u2', 'u3']`，新单元 `['unsplit-new-2']`。
  - 旧引文：[{"source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03", "quote": "Dislikes extreme sports (e.g., skydiving)"}]
  - 新引文：[{"source_id": "new-2", "quote": "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things."}]

### v3

结构状态：`passed`；未匹配旧单元：`[]`。

- 记录 0：属性 `attitude_toward_extreme_sports`；关系 `state_change`；旧单元 `['u1']`，新单元 `['manually_mapped_new']`。
  - 旧引文：["Dislikes extreme sports (e.g., skydiving)"]
  - 新引文：["Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"]
  - qualifiers: [{"side": "new", "kind": "simulation", "quote": "simulated", "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}, {"side": "new", "kind": "time", "quote": "recently", "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}]
  - missing_evidence: ["No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"]
- 记录 1：属性 `reason_for_disliking_extreme_sports`；关系 `state_change`；旧单元 `['u2']`，新单元 `['manually_mapped_new', 'unsplit-new-2', 'unsplit-new-8']`。
  - 旧引文：["Dislikes extreme sports (e.g., skydiving) due to high injury risk"]
  - 新引文：["Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.", "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."]
  - qualifiers: [{"side": "new", "kind": "simulation", "quote": "simulated", "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}, {"side": "new", "kind": "time", "quote": "recently", "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}, {"side": "new", "kind": "plan", "quote": "For now", "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}, {"side": "new", "kind": "negation", "quote": "still prioritize safety", "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
  - missing_evidence: ["No statement retracting or qualifying that high injury risk *itself* is no longer a reason for dislike; 'still prioritize safety' affirms the original safety concern remains operative; 'simulated' explicitly limits scope — no evidence about real skydiving risk perception change"]
- 记录 2：属性 `safety_commitment_conflict_with_extreme_sports`；关系 `no_clear_change`；旧单元 `['u3']`，新单元 `['manually_mapped_new', 'unsplit-new-8']`。
  - 旧引文：["conflicting with commitment to safety and well-being"]
  - 新引文：["Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!", "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."]
  - qualifiers: [{"side": "new", "kind": "simulation", "quote": "simulated", "claim_quote": "Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"}, {"side": "new", "kind": "plan", "quote": "For now", "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}, {"side": "new", "kind": "negation", "quote": "still prioritize safety", "claim_quote": "For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course."}]
  - missing_evidence: ["No evidence that simulated skydiving resolves or negates the conflict with safety commitment; 'still prioritize safety' confirms the commitment remains intact and unconflicted *by this activity* — but does not address whether real extreme sports would still conflict"]
