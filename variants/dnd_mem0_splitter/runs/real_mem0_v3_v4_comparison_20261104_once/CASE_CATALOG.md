# 输入与快照来源

现有7条输入逐字复用；新增4条复合记忆来自可靠更新前快照，ID/文本在 API、数据库和历史写入/after 链中核验。波斯猫旧记忆经历史 UPDATE 得到本次文本，未把最初 ADD 的不同文本冒充当前文本。

## case_01_multi_person

- 类型：regression_7
- ID：`130bf22c-9e71-4ad2-bf51-43bac36ab2c8`
- 选择理由：两名具名人物与不同关系标签；对应旧来源包含 user 发言和 assistant 对人物关系的描述。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_011/before.json#/api_snapshot/results/13`
- 输入 SHA256：`f1c73922f8456e52f55e9ad8f5d34ac8405a5e2d2f2d3962753ad06232a4a33b`

旧记忆原文：

```text
Grateful towards colleagues like Steven and friends like Mary
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`May 20, 2026, 09:04:14`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_009/input.json#/raw_dialogue/8/content [characters 0:108, zero-based, end exclusive]`

```text
Maintaining these relationships is crucial. I'll ensure to keep in touch and express my gratitude regularly.
```

- `ctx-2`；speaker=`assistant`；recorded_at=`May 20, 2026, 09:04:14`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_009/input.json#/raw_dialogue/9/content [characters 160:289, zero-based, end exclusive]`

```text
Your gratitude towards colleagues like Steven and friends like Mary highlights the importance of having a strong support network.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_02_subject_and_roster

- 类型：regression_7
- ID：`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`
- 选择理由：旧记忆省略拥有朋友的主体并保留姓名和别称；实际对应的同一条旧 user 发言还包含其他人物及工作细节。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/51`
- 输入 SHA256：`f083e846a03596b965f520932a82d10c865ad0cff0626138b9f4dfe5cfacf0d4`

旧记忆原文：

```text
Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 06, 2025, 01:02:20`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [characters 0:590, zero-based, end exclusive]`

```text
Of course. I have several important friends and colleagues: ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life. MartinezDaniel is my Colleague, Daniel's expertise in healthcare consulting challenges me to push boundaries and innovate in our projects, significantly impacting my career growth. WilliamsJoshua is my Colleague, Joshua's collaborative approach and insights into healthcare management enhance our team's effectiveness, positively influencing my work and leadership style.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_03_assistant_yoga

- 类型：regression_7
- ID：`992ae849-3f40-4ffe-a2ec-16e20959ca86`
- 选择理由：旧记忆含 practices or is open to；生成会话中有 assistant 的 yoga 表述，需检查来源角色和命题范围。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json#/api_snapshot/results/58`
- 输入 SHA256：`84eca2d3bf486c4800f5d838e1c2348114d04b1f755dd6825715598dfc45d9bf`

旧记忆原文：

```text
Practices or is open to yoga for supporting personal health and transition
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Feb 05, 2026, 17:13:15`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content [characters 0:255, zero-based, end exclusive]`

```text
I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.
```

- `ctx-2`；speaker=`assistant`；recorded_at=`Feb 05, 2026, 17:15:18`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/3/content [characters 327:523, zero-based, end exclusive]`

```text
As you continue exploring job opportunities, remember the importance of balancing professional responsibilities with personal health. Practices like yoga could support this transition effectively.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_04_negative_relative

- 类型：regression_7
- ID：`30a88f0c-d4b8-4089-95b2-82938e45558c`
- 选择理由：否定偏好与清醒负责的理由，包含 relative；原始饮料偏好发言还提到能量饮料、绿茶和汽水。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/before.json#/api_snapshot/results/17`
- 输入 SHA256：`7250a40e1c913ade52bf584fa01d3ebec018936344f39a02d3d6ef1524863f48`

旧记忆原文：

```text
Does not like drinking alcoholic drinks because they need to stay clear-headed and responsible while supporting their relative
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 06, 2025, 14:02:33`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_003/input.json#/raw_dialogue/10/content [characters 0:548, zero-based, end exclusive]`

```text
I don't like to drink energy drinks. I avoid energy drinks because they make me jittery and unable to concentrate on supporting my relative. I like to drink green tea for its calming effect, helping me stay focused and composed during stressful situations. I don't like to drink soda due to its excessive sweetness and lack of nutritional value, which doesn't align with my health-conscious lifestyle. I don't like to drink alcoholic drinks. I avoid alcoholic drinks because I need to stay clear-headed and responsible while supporting my relative.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_05_relative_time

- 类型：regression_7
- ID：`2570a550-4b52-43fc-b5c4-079261785a1a`
- 选择理由：recently 与职位变化及机构；原始 user 发言带记录时间和额外感受，可检查时间解释及补充范围。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json#/api_snapshot/results/11`
- 输入 SHA256：`8d250d627b9458919978ea3b602fbb9fd39872d4017cdc21889d75ea1868508a`

旧记忆原文：

```text
Recently promoted to lead director at Historical Productions Ltd
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Feb 01, 2026, 18:47:19`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content [characters 0:92, zero-based, end exclusive]`

```text
I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_06_plan_possibility

- 类型：regression_7
- ID：`0618a2ca-e7d0-483f-b80a-335124dbb075`
- 选择理由：包含计划及 possibly 的不同作用范围；对应旧会话含 assistant 问句和 user 对创作控制的回应。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json#/api_snapshot/results/1`
- 输入 SHA256：`5965490cd567f378a87fd699505737b9faacaf85e9820a01bc2f76287e6c9e00`

旧记忆原文：

```text
Plans to initiate groundbreaking historical dramas and possibly science fiction dramas
```

实际发送的来源上下文：

- `ctx-1`；speaker=`assistant`；recorded_at=`Feb 01, 2026, 18:47:19`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/1/content [characters 350:536, zero-based, end exclusive]`

```text
I'm curious how you plan to use this opportunity to initiate groundbreaking historical dramas and perhaps even science fiction dramas. How do you feel about the increased responsibility?
```

- `ctx-2`；speaker=`user`；recorded_at=`Feb 01, 2026, 18:48:19`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/2/content [characters 0:135, zero-based, end exclusive]`

```text
The idea of having more creative control is thrilling. I can push for higher authenticity in my work, which is what I've always wanted.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_07_no_children

- 类型：regression_7
- ID：`40c29476-81a2-477d-9e75-a2a3a92d46c7`
- 选择理由：简短否定状态；旧 user 家庭介绍可提供主体线索，同时含父母和关系状态等额外内容。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/20`
- 输入 SHA256：`5ea58b92e383b9d609c1b60425c9129262d0735bcbc1e60a39902588708f8272`

旧记忆原文：

```text
No children
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 04, 2025, 19:38:09`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_001/input.json#/raw_dialogue/8/content [characters 0:87, zero-based, end exclusive]`

```text
Good, let me introduce my family. Both parents are alive, no_relationship, No children.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_08_partner_profile

- 类型：new_compound_4
- ID：`a0890e00-0564-4490-8e5b-15b02025e910`
- 选择理由：同一关系对象同时含出生日期、职业和专长等可分别核查的信息。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_004/before.json#/api_snapshot/results/40`
- 输入 SHA256：`08b006bbeccbac3a3fbc1faed0ccd84612dc1636c29acfa11be53e90bea41011`

旧记忆原文：

```text
Partner was born on 1980-06-16, art curator specializing in historical artifacts
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 04, 2025, 10:49:29`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_001/input.json#/raw_dialogue/8/content [characters 280:398, zero-based, end exclusive]`

```text
My Partner was born on 1980-06-16, Art curator with a keen eye for historical artifacts, shares a passion for history.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_09_father_profile

- 类型：new_compound_4
- ID：`bde67e08-ad3b-476a-9874-0368cc33de71`
- 选择理由：同一人物含出生日期、退休职业状态及对健康兴趣的影响，需保留各自关系与主体。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/62`
- 输入 SHA256：`1ad8dd0cff7b94f0cdaeb3b7861a4104c13a845c020c9b422c5c8554180d120f`

旧记忆原文：

```text
Father was born on 1963-08-02, retired doctor who inspired interest in health
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 04, 2025, 19:38:09`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_001/input.json#/raw_dialogue/8/content [characters 88:178, zero-based, end exclusive]`

```text
My Father was born on 1963-08-02, Retired doctor who inspired Martin's interest in health.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_10_sports_preferences

- 类型：new_compound_4
- ID：`4f51947c-5cb3-419e-a04e-1142410c0b9e`
- 选择理由：同一句含不喜欢、态度理由及另一类运动偏好，适合区分覆盖与细分粒度。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_005/before.json#/api_snapshot/results/25`
- 输入 SHA256：`c9c6e86ac5fd86065713b65424a70553340bf252e5ea5561bde7f2203e002a67`

旧记忆原文：

```text
Dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Sep 06, 2025, 22:52:30`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json#/raw_dialogue/6/content [characters 294:422, zero-based, end exclusive]`

```text
I dislike wrestling, because I find wrestling too confrontational and prefer sports that emphasize teamwork and personal growth.
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。

## case_11_persian_care

- 类型：new_compound_4
- ID：`eef34a57-c82a-4995-877d-66b54b9589da`
- 选择理由：较长旧记忆并列欣赏、历史关联、实际照料挑战及平衡考虑；已找到对应旧 UPDATE 和当时会话。
- 更新前快照：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_008/before.json#/api_snapshot/results/102`
- 输入 SHA256：`9d7a3cca063a8d181261a227b17fe341f05f09c1953823a0d7a2c1e5922a988a`

旧记忆原文：

```text
Has a deep admiration for Persian cats and their historical lineage and association with royalty, and reflects on the practical challenges of maintaining their regal appearance while balancing historical admiration with practical care requirements
```

实际发送的来源上下文：

- `ctx-1`；speaker=`user`；recorded_at=`Apr 10, 2026, 11:06:07`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/input.json#/raw_dialogue/0/content [characters 0:185, zero-based, end exclusive]`

```text
I recently attended a film festival and watched a fascinating documentary about Persian cats. It really deepened my admiration for their historical lineage and association with royalty.
```

- `ctx-2`；speaker=`user`；recorded_at=`Apr 10, 2026, 11:15:58`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/input.json#/raw_dialogue/2/content [characters 0:178, zero-based, end exclusive]`

```text
The history of Persian cats aligns perfectly with my interest in historical authenticity. However, I do reflect on the practical challenges of maintaining their regal appearance.
```

- `ctx-3`；speaker=`assistant`；recorded_at=`Apr 10, 2026, 11:15:58`
  来源：`system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/input.json#/raw_dialogue/3/content [characters 0:434, zero-based, end exclusive]`

```text
Maintaining the regal appearance of Persian cats can indeed be a challenge, requiring regular grooming and care. Your strategic thinking and perfectionist traits likely help you navigate these responsibilities effectively. It's similar to how you consider dog preferences, balancing historical admiration with practical care requirements. How do these traits influence your approach to integrating pet preferences into your lifestyle?
```

来源验证细节见 selection.json 和 source_provenance.json。未将目标会话的新证据、人工标注或复核说明发送给模型。
