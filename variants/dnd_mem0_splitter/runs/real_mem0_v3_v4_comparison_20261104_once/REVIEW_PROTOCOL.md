# 配对复核协议（只用于事后复核，不进入模型输入）

全部语义判断标记“初步判断，待人工确认”；这不是人工金标准或错误率。程序通过只证明结构、ID及逐字引文匹配，不证明语义。只读取该目录及已列出的旧快照，不调用模型，不读取环境配置，不修改任何已存在文件。审查 raw_content 与 result，若失败只保留失败候选，绝不标为通过。

按同一标准检查 v3/v4。每条事实都审查人物、关系、否定、时间、条件、情态、覆盖、额外补充和 pending 一致性；每条 evidence 的 supports 都必须评估，保留原文、明确判断理由。

raw 只使用旧记忆；上下文有依据的用户/人物补足在 contextualized 可以合理，但进入 raw 仍是来源边界问题，不等于虚构人物。旧记忆内部共享 they 等允许恢复。memory supports 说“记忆记载”不等于“用户亲口说”，主体需上下文才成立时可记部分支持；明确声称该引文验证完整身份、本人承诺或事实真实性才记越界。partial 不自动计错。判断相容、建议或问题与直接确认不同。speakers=user/assistant 是发言角色，不自动决定所有命题的主体。识别出 user 语义主体与未确认用户原话可以同时成立。

正文含有来源但非必要的效果/地点等记 SUPPORTED_UNNECESSARY_ADDITION；仅 quote 含额外细节不算正文扩写。有具体未知信息记 uncertainties，不自动判错。正文与 pending 仅在同一项确定程度冲突时记 ASSERTION_PENDING_CONFLICT；不要把“原始说话人未知”误当“所有主体未知”。相对时间缺少准确事件日是未决，不自动是遗漏。未提及的条件不能臆造。

复合记忆覆盖以 raw/contextualized 事实正文是否保留各信息点及关系为准，不能只因 quote 有关键词就认为覆盖。多条不等于更好。一个事实保留全部命题时是粒度观察，不能记关键遗漏。各 coverage_units 给 input_span、raw_fact_indices、contextualized_fact_indices、status（preserved/partial/omitted/uncertain）、reason；保留关键 because/while/态度对象/受益人等关系。不要为满足数量强拆不能独立的关系。

可用问题类型：RAW_CONTEXT_LEAK、SUPPORTS_OVERREACH、ASSERTION_PENDING_CONFLICT、SUPPORTED_UNNECESSARY_ADDITION、UNSUPPORTED_ADDITION、RELATION_SCOPE_CHANGE、NEGATION_CHANGE、TEMPORAL_CHANGE、MODAL_CHANGE、OMISSION、SOURCE_ATTRIBUTION_OVERCLAIM、SUBJECT_UNRESOLVED_ASSERTION。粒度另列 granularity_observation，不把粗粒度自动算语义错误。

复核文件 JSON 结构：
{"review_label":"初步判断，待人工确认","cases":[{"case_id":"...","versions":{"v3":{"program_status":"passed/failed","summary":"...","facts":[{"fact_index":1,"observed_issue_types":[],"findings":[{"type":"...","input_span":"...","output_span":"...","reason":"..."}],"uncertainties":[],"fidelity_review":"逐项说明人物/关系/否定/时间/条件/情态和覆盖","supports":[{"evidence_index":0,"assessment":"directly_supported/partially_supported/overreach/uncertain","issue_types":[],"reason":"..."}]}],"coverage_units":[{"unit":"...","input_span":"...","raw_fact_indices":[],"contextualized_fact_indices":[],"status":"preserved/partial/omitted/uncertain","reason":"..."}],"granularity_observation":"...","uncertainties":[]},"v4":{同上}},"comparison":{"improvements":[],"persistent":[],"regressions":[],"uncertainties":[]}}]}

新复合案例注意（复核注意点，并非标准答案）：
- case08：出生日期、职业、专长可分别检查；旧记忆 specialization 与原会话 keen eye 的来源强度有差异，标待确认，不替换旧命题。不要补分享历史热情。
- case09：出生日期、退休医生、影响健康兴趣；旧记忆未指明受益者，context 有 Martin，但不能自动把 Martin 等同说话人。检查 raw 是否偷补 Martin/用户/孩子。
- case10：不喜欢摔跤、觉得太对抗作为理由、偏好团队合作和个人成长。不能只拆出理由和偏好而丢掉 because 关系或主体视角。
- case11：深度欣赏波斯猫及历史血统/王室关联、思考维持高贵外观的实际挑战、平衡历史欣赏与实际照料。区分 user 两段与 assistant 第三段回述，不把助手的 grooming、traits 或 dog 细节扩入旧事实。欣赏/思考不能自动写成拥有猫/正在照料。
