# 复核 02：update / Correct

**结论（LLM 辅助，尚未人工确认）：存疑**

新职称与雇主均被保存，“最近晋升”有新状态线索；旧 Director 文本仍以现在时存在。评分理由称旧记录已被取代，却未说明其是否已明确标为过时；Director 也可能作为职业泛称兼容，故不能仅凭共存判错。

可认可新增晋升事实，但对官方要求的替代/过时条件尚缺充分依据。

来源 ID：`update_1b846c59-456e-9550-dffd-4d23f1eca81f_s004_m000`；原数组 `sessions[4]`，会话结束 `Feb 01, 2026, 21:17:19`；对应 after 快照 SHA-256：`1ff29e7b96ed0e9f86140154ed29f2c73e4f496e8b610365429933f5db62ba1f`。

[完整原始会话输入](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json) · [对应会话后快照](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/after.json) · [本案例完整结构化证据](case_02.json) · [原始逐项评测记录](/home/shu1004/ld/system/mem0_halumem_diagnosis/results/medium_dev/official_eval_development_20261029_v1/records.jsonl)

## 官方参考 / 原始证据

```json
{
  "index": 1,
  "memory_content": "Williams Daniel's career_status updated job_title from \"Director\" to \"Lead Director\" at Historical Productions Ltd.",
  "memory_type": "Persona Memory",
  "memory_source": "secondary",
  "is_update": "True",
  "original_memories": [
    "Williams Daniel's job title is Director"
  ],
  "timestamp": "Feb 01, 2026, 21:17:19",
  "importance": 0.75
}
```

- `sessions[4]/dialogue[0]`，user，Feb 01, 2026, 18:47:19：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

## 当时截点的检索结果

按官方适配器规定 top 10，展示全部 10 条；时间为写库执行时间，不是原始对话时间。

| 排名 | 记忆 ID | 执行时间 | 分数 | 内容 |
|---:|---|---|---:|---|
| 1 | `2570a550-4b52-43fc-b5c4-079261785a1a` | 2026-10-27T23:41:45.187008-07:00 | 0.6441 | Recently promoted to lead director at Historical Productions Ltd |
| 2 | `e13b825e-7ec7-4760-821e-0581d8da5650` | 2026-10-27T23:38:18.636327-07:00 | 0.6173 | Works at Historical Productions Ltd. as a Director |
| 3 | `565d80ae-05a6-4d8e-a5e4-81659d32caca` | 2026-10-27T23:38:18.744569-07:00 | 0.4988 | Colleague: JacksonWilliam (administrative skills help keep productions running smoothly) |
| 4 | `eee03dd5-d84c-4a87-a5b0-afba59162367` | 2026-10-27T23:38:18.727572-07:00 | 0.4896 | Friend: WilliamsRichard (fellow director, inspires innovative storytelling) |
| 5 | `b4c92aa8-44f5-48ff-a94d-137e67f02293` | 2026-10-27T23:38:18.708401-07:00 | 0.4638 | Colleague: SmithSteven (expert in set design, shares passion for historical detail) |
| 6 | `4ffee399-c31f-4827-b5fc-5c661baf1fc9` | 2026-10-27T23:38:18.690128-07:00 | 0.4273 | Experiences stress due to historical accuracy demands and tight production schedules |
| 7 | `76b41491-9d4b-4443-8877-0c6227a79aba` | 2026-10-27T23:37:45.714054-07:00 | 0.4008 | Name is Williams |
| 8 | `924d86c9-298a-4566-8e2a-d5d83f7874ae` | 2026-10-27T23:38:18.718370-07:00 | 0.3893 | Friend: WilliamsMary (provides emotional support and encourages breaks) |
| 9 | `c95cbc1b-30a6-43e6-99e3-df3d3e41eaab` | 2026-10-27T23:37:45.854637-07:00 | 0.3785 | Plans to direct 10 award-winning historical films |
| 10 | `f71eebcd-d556-436f-97be-a8dca4c99de9` | 2026-10-27T23:37:45.837032-07:00 | 0.3752 | Goal is to create historically accurate films |

## 自动判词

类别：`Correct`

The Target Memory for Update specifies that 'Williams Daniel's career_status updated job_title from "Director" to "Lead Director" at Historical Productions Ltd.' The Generated Memories includes a memory: '2026-10-27T23:41:45.187008-07:00: Recently promoted to lead director at Historical Productions Ltd'. This correctly reflects the update — it captures the promotion, the new title ('lead director'), the company ('Historical Productions Ltd'), and implies replacement of the prior role. Although the name 'Williams Daniel' is not explicitly stated in that entry (only 'Williams' appears elsewhere), the context strongly links it (e.g., 'Name is Williams' and 'Works at Historical Productions Ltd. as a Director' earlier), and 'lead director' is a direct, accurate synonym/upgrade of 'Director' at the same company. No factual contradiction exists; no key information (new title, company, promotion event) is missing. The original 'Director' memory remains present but is superseded by the newer, more specific 'lead director' entry — consistent with typical memory updating where old facts persist unless explicitly deprecated.

## 复核意见

**存疑**：新职称与雇主均被保存，“最近晋升”有新状态线索；旧 Director 文本仍以现在时存在。评分理由称旧记录已被取代，却未说明其是否已明确标为过时；Director 也可能作为职业泛称兼容，故不能仅凭共存判错。

限制：可认可新增晋升事实，但对官方要求的替代/过时条件尚缺充分依据。
