# v8 旧记忆拆分：5 条人工审核主目标的试跑

2026-11-18（Asia/Shanghai）。使用现有 v8 入口和未修改的提示词；真实模型 `qwen-plus-2025-12-01`，请求体 `enable_thinking=false`；每条最多一次请求、SDK 不重试。5 次均返回指定模型并通过既有结构、ID 与逐字引文校验，无调用错误。请求参数是客户端请求体观测，服务端内部行为不可见。

五条都只产生一个子事实，复合内容整体保留，没有展示能否将其中可分别检查的成分拆开。下方语义检查是助手初审，需人工确认；逐字引文通过不证明语义支持或事实真实。本样本为定向选取，部分案例曾用于历史诊断，不能估计总体质量。未发送目标会话新证据或人工标签；只读原生运行快照和更早的用户对话，没有调用或写入 Mem0。

## 检查表

| 案例 / 审核主目标 | 遗漏与粒度 | 编造／证据支持 | 引文 | 待确认 |
|---|---|---|---|---|
| 01_susan / 4 | 完整保留朋友身份、姓名/称呼和支持鼓励；一条整体输出，未把关系和支持拆成独立事实。 | 未见正文编造；memory 的 supports 把旧记忆未显式写出的用户主体直接写出，主体可由另列的第一人称上下文支持，但并非单凭该 memory 引文可证。 | 逐字通过 | 名字究竟是复合姓名还是拼接、Susan 与 ThomasSusan 的指代，以及支持的具体作用范围，需结合来源确认；模型已列姓名问题。 |
| 02_skydiving / 8 | 保留不喜欢、跳伞例子、受伤风险和安全健康冲突，未丢旧记忆中的因果关系；整体仍是一条。 | 正文未见超出旧记忆；context supports 称原文确认因果需小心：原对话直接将高风险作为“避免”的原因，旧记忆则将它作为“不喜欢”的原因。 | 逐字通过 | 不能仅凭这段旧语境断言用户现在仍有同样态度；原对话 dislike 与 avoid 的因果对应需要人工判断。 |
| 03_director / 10 | 保留职位和雇主；一条整体输出。 | 未见相对旧记忆及上下文的新增事实。 | 逐字通过 | 输出现在时延续了旧记忆的表达，但旧来源记录于 2025-09-05，不能仅凭此结果断言当前仍为该职称；发生时间、结束时间未明确。 |
| 04_persian_cat / 14 | 完整保留波斯猫偏好及高贵、平静、优雅、历史魅力等旧记忆理由；一条整体输出，粒度较粗。 | 正文未见超出旧记忆；context supports 将优雅和历史都说成喜欢的直接理由偏强：原对话明确的 because 是高贵和平静，后句说猫的存在给家带来优雅和历史感。 | 逐字通过 | 优雅与历史感是否均应作为独立的喜欢原因，需要人工判断；历史 charm 是旧记忆概括，非原话逐字用语。 |
| 05_career_history / 24 | 保留 previously、公司及高级开发职位；一条整体输出。raw 句末多一个句号，但对应的证据引文逐字匹配。 | 未见正文编造；context 清楚承认过去时并非由旧语境独立证明。 | 逐字通过 | 来源发言为 2025-09-05 的现在时，旧记忆为后来快照中的过去时；离职时间和两者时间衔接无法从单条上下文确定。 |

## 逐条：输入与完整拆分 JSON

### 01_susan：审核主目标 4

更新前快照：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json#/api_snapshot/results/57`。

**旧记忆原文**

> Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

**输入上下文**（user，Sep 06, 2025, 01:02:20；`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_002/input.json#/raw_dialogue/6/content [60:218]`）

> ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.

**完整拆分 JSON**

```json
{
  "memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
  "memory_text": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
      "raw_subfact": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
      "contextualized_subfact": "The user has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement.",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "a1332815-d6ba-4bdc-9ffa-657f7315d0ed",
          "quote": "Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement",
          "supports": "Old memory states the user has a friend named ThomasSusan, referred to as 'Susan', who provides support and encouragement."
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "ThomasSusan is my Friend, Susan's support and encouragement inspire me to maintain my focus on promoting well-being in both my personal and professional life.",
          "supports": "The speaker ('user') explicitly identifies ThomasSusan as 'my Friend' and refers to 'Susan's support and encouragement', confirming the user is the subject of the friendship and recipient of that support; 'Susan' is used as a referential form for ThomasSusan in this utterance."
        }
      ],
      "pending_confirmations": [
        {
          "item": "Whether 'ThomasSusan' is a single compound name (e.g., legal or preferred name) or a conflation/concatenation of two names (e.g., 'Thomas' and 'Susan')",
          "reason": "The memory text writes 'ThomasSusan' as one token without internal punctuation or explanation; the context quote repeats 'ThomasSusan' identically but does not clarify orthographic or identity intent. No source disambiguates whether this is a full name, nickname, typo, or merged reference."
        },
        {
          "item": "Whether 'provides support and encouragement' in the memory corresponds precisely to 'Susan's support and encouragement inspire me...' in context — specifically, whether the inspiration effect is part of the original factual claim or an added interpretation",
          "reason": "The memory states Susan 'provides support and encouragement' (neutral action); the context adds that this 'inspires [the user] to maintain focus on promoting well-being'. The inspirational effect is not asserted in the memory text and cannot be assumed part of the raw subfact without conflating description with consequence."
        }
      ]
    }
  ]
}
```

### 02_skydiving：审核主目标 8

更新前快照：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json#/api_snapshot/results/100`。

**旧记忆原文**

> Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

**输入上下文**（user，Sep 06, 2025, 22:52:30；`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_003/input.json#/raw_dialogue/6/content [0:169]`）

> I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.

**完整拆分 JSON**

```json
{
  "memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
  "memory_text": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
      "raw_subfact": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
      "contextualized_subfact": "User dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with their commitment to safety and well-being",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "e1d4f8f9-0520-427d-94fd-a2ac0ee69d03",
          "quote": "Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being",
          "supports": "Old memory states a dislike of extreme sports, cites high injury risk as reason, and frames this as conflicting with a commitment to safety and well-being."
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "I dislike extreme sports (such as skydiving). I avoid extreme sports because they carry a high risk of injury, which goes against my commitment to safety and well-being.",
          "supports": "Confirms the subject is the user (first-person 'I'), validates the causal link ('because'), and confirms the conflict framing ('goes against my commitment')."
        }
      ],
      "pending_confirmations": []
    }
  ]
}
```

### 03_director：审核主目标 10

更新前快照：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json#/api_snapshot/results/61`。

**旧记忆原文**

> Works at Historical Productions Ltd. as a Director

**输入上下文**（user，Sep 05, 2025, 14:42:35；`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_002/input.json#/raw_dialogue/2/content [55:107]`）

> I work at Historical Productions Ltd. as a Director.

**完整拆分 JSON**

```json
{
  "memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
  "memory_text": "Works at Historical Productions Ltd. as a Director",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
      "raw_subfact": "Works at Historical Productions Ltd. as a Director",
      "contextualized_subfact": "The user works at Historical Productions Ltd. as a Director.",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "e13b825e-7ec7-4760-821e-0581d8da5650",
          "quote": "Works at Historical Productions Ltd. as a Director",
          "supports": "Old memory states the subject works at Historical Productions Ltd. as a Director; subject is not explicitly named or pronominalized in this fragment."
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "I work at Historical Productions Ltd. as a Director.",
          "supports": "The first-person utterance by speaker 'user' directly expresses the same role and employer; used to resolve the subject of the memory fragment as the user."
        }
      ],
      "pending_confirmations": []
    }
  ]
}
```

### 04_persian_cat：审核主目标 14

更新前快照：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/before.json#/api_snapshot/results/89`。

**旧记忆原文**

> Likes Persian cats because of their regal and calm nature, elegance, and historical charm

**输入上下文**（user，Sep 06, 2025, 22:24:16；`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_003/input.json#/raw_dialogue/6/content [0:144]`）

> I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.

**完整拆分 JSON**

```json
{
  "memory_id": "eef34a57-c82a-4995-877d-66b54b9589da",
  "memory_text": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "eef34a57-c82a-4995-877d-66b54b9589da",
      "raw_subfact": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm",
      "contextualized_subfact": "User likes Persian cats because of their regal and calm nature, elegance, and historical charm",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "eef34a57-c82a-4995-877d-66b54b9589da",
          "quote": "Likes Persian cats because of their regal and calm nature, elegance, and historical charm",
          "supports": "Old memory states a liking for Persian cats grounded in three linked attributes: (1) regal and calm nature, (2) elegance, and (3) historical charm."
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "I like persian cats, because I admire the regal and calm nature of Persian cats. Their presence adds a touch of elegance and history to my home.",
          "supports": "Confirms the user as speaker; links 'regal and calm nature' directly to admiration, and 'elegance' and 'history' to the cats' presence in the home — supporting the attribution of all three qualities to Persian cats as reasons for liking them. 'History' maps to 'historical charm' in the memory text."
        }
      ],
      "pending_confirmations": []
    }
  ]
}
```

### 05_career_history：审核主目标 24

更新前快照：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json#/api_snapshot/results/3`。

**旧记忆原文**

> Previously worked as a senior developer in Blockchain Tech

**输入上下文**（user，Sep 05, 2025, 09:10:09；`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_002/input.json#/raw_dialogue/2/content [61:109]`）

> I work at Blockchain Tech as a senior developer.

**完整拆分 JSON**

```json
{
  "memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
  "memory_text": "Previously worked as a senior developer in Blockchain Tech",
  "facts": [
    {
      "fact_index": 1,
      "source_memory_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
      "raw_subfact": "Previously worked as a senior developer in Blockchain Tech.",
      "contextualized_subfact": "The user previously worked as a senior developer at Blockchain Tech.",
      "evidence": [
        {
          "source_type": "memory",
          "source_id": "05afde13-35bd-4d26-bbae-6de427d58db1",
          "quote": "Previously worked as a senior developer in Blockchain Tech",
          "supports": "Old memory states prior employment as a senior developer in Blockchain Tech."
        },
        {
          "source_type": "context",
          "source_id": "ctx-1",
          "quote": "I work at Blockchain Tech as a senior developer.",
          "supports": "The speaker (user) self-identifies as currently working at Blockchain Tech as a senior developer; this confirms the user is the subject of the role and organization, supporting attribution of the past role to the same person. It does not confirm the past-tense 'previously worked' — only that the role and company are consistent and speaker-identified."
        }
      ],
      "pending_confirmations": [
        {
          "item": "Temporal scope of 'previously worked'",
          "reason": "The memory asserts past employment, but the context shows current employment; no information is provided about when the prior role ended or whether it was the same position, a prior iteration, or a different engagement. The word 'previously' lacks anchoring time point or duration in both memory and context."
        },
        {
          "item": "Exact nature of employment relationship during the prior period",
          "reason": "Memory says 'worked as a senior developer', but does not specify full-time, contract, internal vs. client-facing, or team context. Context only confirms current role, not historical details."
        }
      ]
    }
  ]
}
```

## 复核与文件说明

每个案例目录的 `input.json` 保存精确请求输入；`result.json` 为通过原有校验后的完整结果，`raw_content.txt` 为模型原始文本，`provenance.json` 保存旧快照位置与来源哈希，`request_audit.json` 保存实际客户端请求体中的模型与 thinking 参数检查，`response_metadata.json` 保存返回模型、结束原因和可获取的 token 用量。`manifest.json` 保存提示词版本及哈希、选样及来源；`batch_completion.json` 保存每次调用状态。`frozen_prompt.txt` 是本次请求前的提示词副本。

来源中的记录时间只是用户发言时间，不自动等于事件发生时间。第 24 条所用的旧职业是该目标共享会话中的历史保护对象；它不是第 24 条的新增“获客”内容。第 10 条是晋升目标的更新前 Director 旧状态，而非晋升后的 Lead Director。
