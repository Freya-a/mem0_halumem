# 五案证据对齐试跑与语义复核

这是一轮开发性试跑，不是独立盲测；语义栏为助手根据原文对实际模型输出的复核，并非用户确认的金标准。每案各一次请求，共 **5 次请求、5 次响应**，均返回 `qwen-plus-2025-12-01`；温度 0、JSON 输出、自动重试 0。没有重新调用任何案例。

程序校验 **3 案 passed、2 案 failed**；5 案均解析为 JSON，ID 覆盖检查没有发现未提及单元。覆盖只说明关联 ID 或未匹配声明存在，不保证相关属性完整或语义正确。Susan 有 3 个校验错误，跳伞有 6 个；完整明细见各案例 JSON。职业历史虽然字面校验通过，却有明显语义错误。

| 旧记忆 | 新证据 | 模型对齐属性 | 模型变化类型 | 限定词及引文 | 语义是否正确 |
|---|---|---|---|---|---|
| Susan 是朋友，提供支持与鼓励。 | Susan 的支持帮助保持目标专注；另有 Daniel 的建议及寻找新工作的陈述。 | `friendship`、`support_context`；求职另列为独立 `career_status`。 | `support`、`supplement`、`plan` | 旧：`provides support and encouragement`；新：`Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.`；求职时词 `lately`。 | **部分**：支持和求职意向的大方向有依据，但 friendship 记录引用了超出该旧单元证据范围的整句，且把 Daniel 的内容与 Susan 支持并在同一新主张中；`time_expressions` 写成字符串而非来源引文对象。程序 failed。 |
| 在 Historical Productions Ltd. 任 Director。 | 最近升为该公司的 lead director。 | `job_title`、`employer` | 职位 `state_change`；雇主 `no_clear_change`。 | 旧：`Director`；新：`I recently got promoted to lead director at Historical Productions Ltd.`；限定词 `recently`；事件日期 `null`。 | **是**：明确为已升任，且没有把公司变更或具体日期编造出来。程序 passed。 |
| 曾在 Blockchain Tech 任 senior developer。 | 咨询公司取得一些初始客户；两人的人脉带来帮助。 | `employer`、`title`；另列 `client_milestone`、`network_contact_effectiveness`。 | 前两项均 `state_change`；后两项 `new_information`。 | 旧：`Blockchain Tech`、`senior developer`；新：`my consulting firm finally secured some initial clients`；模型列 `lately`，原文中它修饰感到宽慰。 | **否**：获客不证明旧雇主或旧职位发生替换，也不证明 `founder/owner of consulting firm`；`lately` 不能直接当作获客时间。独立获客和两人关系记录基本有据。程序虽 passed，不能据此接受语义。 |
| 正寻找工作与生活更平衡的新工作。 | 用户称终于转到新岗位，工作生活平衡如今健康得多。 | `transition_progress` | `state_change` | 旧：`Looking for a new job with better work-life balance`；新：`I've finally transitioned to a new role`；模型列 `finally`，事件日期 `null`。 | **部分**：正确识别已转岗，没有说仍在找工作；但新主张没有单独表达工作生活平衡改善，也未把 `now` 列为时间词。程序 passed。 |
| 不喜欢极限运动（例如跳伞），理由是受伤风险及安全和福祉。 | 团建时体验**模拟跳伞**感到刺激；更愿意尝试新事物，现阶段仍重视安全。 | `attitude_toward_extreme_sports`、`reason_for_disliking_extreme_sports`、`commitment_to_safety_and_well_being`。 | 前两项 `state_change`，安全承诺为 `support`。 | 旧：`Dislikes extreme sports (e.g., skydiving) due to high injury risk`；新：`I tried simulated skydiving. It was quite thrilling!`、`For now`、`I still prioritize safety`；日期 `null`。 | **否**：虽然引文和新主张保留 `simulated`，模型却将真实极限运动态度与风险理由标为 `state_change`，证据不足；模拟限定词也没有进入该记录的 `conditions`。安全优先的支持有据。三个旧引文均超出各自单元的引用范围，程序 failed。 |

原始输入、完整消息、响应和错误分别保存在 [Susan](susan.json)、[晋升](promotion.json)、[职业历史](career_history.json)、[转岗](transition.json)、[跳伞](skydiving.json)；[运行清单](manifest.json) 保存请求计数和每案状态。[离线重校验](offline_revalidation.json) 使用试跑后加固的校验器且没有调用模型；原结果未被覆盖。

数据与单元来源见各案 `input.provenance`：跳伞的三个旧单元来自新版 SimpleMem；其余四案旧单元和每案已有的新单元是先前人工固定映射，另补的选定消息单元未细分。完整会话均传入，但其余会话消息不等于已拆分的新单元。
