# 五案离线回放对照

这是单记忆、选定消息的离线实验，不是全量评测。人工预期独立保存且没有传给规划器；模型组只读取已保存 v3 parsed 输出，未将人工语义填入模型结果。数字是输出条目数，不能当准确率。逐版字段、引文与模型关系见 ALIGNER_AUDIT.md，来源核对见 SOURCES.md。

## promotion

旧记忆：Works at Historical Productions Ltd. as a Director

旧记忆来源：`e13b825e-7ec7-4760-821e-0581d8da5650`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`。

选定新证据：
- new-0：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!（`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content`）

**独立人工预期**
- modify：职位细化为晋升后的 lead director
- preserve：Historical Productions Ltd. 雇主关系；Director 作为历史和可能仍成立的宽泛描述
- uncertain：准确晋升日期未知；宽泛 Director 与 lead director 的逻辑包含关系不由代码推理
- add：晋升 lead director 的事实
- missing：记录时间不是生效时间。

**人工核对的对齐输入 → 规划器**
- modify（1）：fact="job_title"; subject="user"; attribute="employment.title"; old_value="Director"; new_value="lead director"; scope={"kind": "unconditional"}; relation="change"; reason="different explicit values in overlapping scope"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- preserve（2）：fact="employer"; subject="user"; attribute="employment.employer"; old_value="Historical Productions Ltd."; new_value="Historical Productions Ltd."; scope={"kind": "unconditional"}; relation="same"; reason="unchanged or outside evidence scope"; old_quote="Historical Productions Ltd."; new_quote="lead director at Historical Productions Ltd."; old_position={"start": 9, "end": 36}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="job_title"; subject="user"; attribute="employment.title"; old_value="Director"; new_value="lead director"; scope={"kind": "unconditional"}; relation="change"; status="historical"; reason="explicitly retained as historical, not as current"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- uncertain（2）：fact="job_title"; subject="user"; attribute="employment.title"; old_value="Director"; new_value="lead director"; relation="change"; reason="晋升具体生效日期未知。"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="job_title"; subject="user"; attribute="employment.title"; old_value="Director"; new_value="lead director"; relation="change"; reason="Director 作为当前宽泛职位称谓是否仍成立无法仅靠字符串比较判断。"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- add（0）：无
- editable_spans（1）：old_quote="Director"
- protected_facts（1）：fact="job_title"; subject="user"; attribute="employment.title"; old_value="Director"; new_value="lead director"; scope={"kind": "unconditional"}; relation="change"; status="historical"; reason="explicitly retained as historical, not as current"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- 引文校验：status="valid"; old_quote="Historical Productions Ltd."; new_quote="lead director at Historical Productions Ltd."; old_position={"start": 9, "end": 36}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Director"; new_quote="promoted to lead director"; old_position={"start": 42, "end": 50}; source_id="new-0"; status=valid; old_error=None; new_error=None

**保存的 v3 模型对齐输入 → 同一规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（2）：fact="employer"; attribute="employer"; relation="unknown"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="Historical Productions Ltd."; new_quote="I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"; old_position={"start": 9, "end": 36}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]；fact="job_title"; attribute="job_title"; relation="change"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="Director"; new_quote="I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"; old_position={"start": 42, "end": 50}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json#/raw_dialogue/0/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]
- add（0）：无
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; old_quote="Historical Productions Ltd."; new_quote="I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"; old_position={"start": 9, "end": 36}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Director"; new_quote="I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!"; old_position={"start": 42, "end": 50}; source_id="new-0"; status=valid; old_error=None; new_error=None

**差异与原因：** 人工将晋升明确标为已发生的职位变化，保留雇主和历史职位；具体晋升日期未知，Director 是否作为当前宽泛称谓继续成立不能由字符串比较判断。预期中的晋升事实以 modify 的新值表达，没有另列 add。v3 有 state_change，但未提供规范化主体、值、条件，不能据此授权编辑。差异主要来自上游字段不足和结果表示方式。

## susan

旧记忆：Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement

旧记忆来源：`a1332815-d6ba-4bdc-9ffa-657f7315d0ed`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/before.json`。

选定新证据：
- new-0：I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content`）
- new-2：Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals. And Daniel's insights have really pushed me to think outside the box in my career. It's been exciting to see how these connections have opened up new possibilities.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content`）

**独立人工预期**
- modify：无
- preserve：ThomasSusan/Susan 朋友关系、支持和鼓励
- uncertain：新证据没有独立确认全名与称呼的映射；旧来源 ctx-1 可支持语境但不消除命名歧义
- add：Daniel 的见解促进职业思考；工作生活平衡及人道目标为另行表达的内容
- missing：Susan 身份跨来源仅由上下文支持；新证据未明确朋友关系变化。

**人工核对的对齐输入 → 规划器**
- modify（0）：无
- preserve（1）：fact="friend_support"; subject="user"; attribute="relationship.support"; old_value="support and encouragement"; new_value="support and encouragement"; scope={"kind": "unconditional"}; relation="same"; reason="unchanged or outside evidence scope"; old_quote="provides support and encouragement"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 60, "end": 94}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=[]
- uncertain（2）：fact="friendship"; subject="user"; attribute="relationship.friendship"; old_value="friend named ThomasSusan"; new_value="Susan provides support"; relation="unknown"; reason="新话语支持 Susan 的支持，但未独立明确重新确认朋友关系；原句仍可保留，姓名指代依据旧来源。"; old_quote="friend named ThomasSusan"; new_quote="Susan's support has indeed been invaluable."; old_position={"start": 6, "end": 30}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=[]；fact="friend_support"; subject="user"; attribute="relationship.support"; old_value="support and encouragement"; new_value="insights helped career thinking"; relation="supplement"; reason="condition kind missing or unsupported"; old_quote="provides support and encouragement"; new_quote="Daniel's insights have really pushed me to think outside the box in my career."; old_position={"start": 60, "end": 94}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=[]
- add（2）：subject="user"; attribute="career.job_search"; value="find a new job offering better work-life balance and alignment with humanitarian goals"; scope={"kind": "unknown"}; relation="plan"; status="planned"; reason="planned; not asserted as completed"; new_quote="It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="friend_support"; subject="user"; attribute="relationship.Daniel"; old_value="support and encouragement"; new_value="insights helped career thinking"; value="insights helped career thinking"; scope={"kind": "unknown"}; relation="supplement"; status="asserted"; reason="independent addition"; old_quote="provides support and encouragement"; new_quote="Daniel's insights have really pushed me to think outside the box in my career."; old_position={"start": 60, "end": 94}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=[]
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; new_quote="It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="friend named ThomasSusan"; new_quote="Susan's support has indeed been invaluable."; old_position={"start": 6, "end": 30}; source_id="new-2"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="provides support and encouragement"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 60, "end": 94}; source_id="new-2"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="provides support and encouragement"; new_quote="Daniel's insights have really pushed me to think outside the box in my career."; old_position={"start": 60, "end": 94}; source_id="new-2"; status=valid; old_error=None; new_error=None

**保存的 v3 模型对齐输入 → 同一规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（3）：attribute="career_wellbeing_alignment"; relation="unrelated"; reason="missing upstream information: upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old side lacks a single uniquely represented quote; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; new_quote="I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/0/content"; missing_reasons=["upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}", "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}", "upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}", "multiple old unit IDs; no unique unit binding", "old side lacks a single uniquely represented quote", "not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]；fact="friendship"; attribute="friendship"; relation="unknown"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="friend named ThomasSusan"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 6, "end": 30}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]；fact="friend_support"; attribute="support"; relation="supplement"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="provides support and encouragement"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 60, "end": 94}; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_007/input.json#/raw_dialogue/2/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]
- add（0）：无
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="invalid"; new_quote="I've been thinking a lot about my career lately, and I've realized that my current role isn't supporting my well-being as much as I'd like. It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."; source_id="new-0"; status=invalid; old_error=None; new_error=missing upstream information: upstream validation error: {'code': 'missing_quote', 'path': 'records[2].old_quotes', 'message': 'at least one quote required'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'friendship'}; upstream validation error: {'code': 'unit_without_quote', 'path': 'records[2].old_unit_ids', 'message': 'support'}; multiple old unit IDs; no unique unit binding; old side lacks a single uniquely represented quote; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized
- 引文校验：status="valid"; old_quote="friend named ThomasSusan"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 6, "end": 30}; source_id="new-2"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="provides support and encouragement"; new_quote="Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."; old_position={"start": 60, "end": 94}; source_id="new-2"; status=valid; old_error=None; new_error=None

**差异与原因：** 支持和鼓励并不否定朋友关系，人工组对朋友关系保守列为待确认；Daniel 与求职意向分开列出，后者保留为计划。v3 的 career_wellbeing_alignment 关联旧单元却缺旧引文，结构校验失败；人工标注和模型输出的粒度与覆盖不同，身份关联仍需核对。差异主要来自对齐及覆盖，不是范围组合减法。

## transition

旧记忆：Looking for a new job with better work-life balance

旧记忆来源：`e6ab178b-c0f9-4adb-bfb7-e4648617a950`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/before.json`。

选定新证据：
- new-0：I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content`）

**独立人工预期**
- modify：求职进展改为已经转到新职位，不断言停止任何求职
- preserve：追求较好工作生活平衡的旧目标
- uncertain：新职位名称和实际切换日期；是否继续另找工作
- add：新职位工作生活平衡改善
- missing：没有具体职位名或事实生效日期。

**人工核对的对齐输入 → 规划器**
- modify（1）：fact="transition_progress"; subject="user"; attribute="career.transition_status"; old_value="looking for a new job"; new_value="transitioned to a new role"; scope={"kind": "unconditional"}; relation="change"; reason="different explicit values in overlapping scope"; old_quote="Looking for a new job"; new_quote="I've finally transitioned to a new role"; old_position={"start": 0, "end": 21}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- preserve（1）：fact="求职时追求更好的工作生活平衡"; reason="explicit protected claim"; old_quote="better work-life balance"; old_position={"start": 27, "end": 51}
- uncertain（3）：fact="transition_progress"; subject="user"; attribute="career.transition_status"; old_value="looking for a new job"; new_value="transitioned to a new role"; relation="change"; reason="转岗后是否继续寻找工作未知；不应将转岗解释为不再求职。"; old_quote="Looking for a new job"; new_quote="I've finally transitioned to a new role"; old_position={"start": 0, "end": 21}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="transition_progress"; subject="user"; attribute="career.transition_status"; old_value="looking for a new job"; new_value="transitioned to a new role"; relation="change"; reason="职位切换的具体生效日期未知。"; old_quote="Looking for a new job"; new_quote="I've finally transitioned to a new role"; old_position={"start": 0, "end": 21}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="transition_progress"; subject="user"; attribute="career.work_life_balance"; old_value="seeks better work-life balance"; new_value="balance much healthier"; relation="supplement"; reason="condition kind missing or unsupported"; old_quote="better work-life balance"; new_quote="The balance between work and personal life is much healthier now."; old_position={"start": 27, "end": 51}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- add（1）：fact="transition_progress"; subject="user"; attribute="career.work_life_balance"; old_value="seeks better work-life balance"; new_value="balance much healthier"; value="balance much healthier"; scope={"kind": "unknown"}; relation="supplement"; status="asserted"; reason="independent addition"; old_quote="better work-life balance"; new_quote="The balance between work and personal life is much healthier now."; old_position={"start": 27, "end": 51}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- editable_spans（1）：old_quote="Looking for a new job"
- protected_facts（1）：fact="求职时追求更好的工作生活平衡"; reason="explicit protected claim"; old_quote="better work-life balance"; old_position={"start": 27, "end": 51}
- 引文校验：status="valid"; old_quote="better work-life balance"; old_position={"start": 27, "end": 51}; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Looking for a new job"; new_quote="I've finally transitioned to a new role"; old_position={"start": 0, "end": 21}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="better work-life balance"; new_quote="The balance between work and personal life is much healthier now."; old_position={"start": 27, "end": 51}; source_id="new-0"; status=valid; old_error=None; new_error=None

**保存的 v3 模型对齐输入 → 同一规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（1）：fact="transition_progress"; attribute="transition_progress"; relation="change"; reason="missing upstream information: upstream validation error: {'code': 'qualifier_anchor_provenance', 'path': 'records[0].qualifiers[0]', 'message': 'claim_quote must overlap a cited quote in its linked source'}; not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="Looking for a new job with better work-life balance"; new_quote="I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."; old_position={"start": 0, "end": 51}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=["upstream validation error: {'code': 'qualifier_anchor_provenance', 'path': 'records[0].qualifiers[0]', 'message': 'claim_quote must overlap a cited quote in its linked source'}", "not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]
- add（0）：无
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; old_quote="Looking for a new job with better work-life balance"; new_quote="I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."; old_position={"start": 0, "end": 51}; source_id="new-0"; status=valid; old_error=None; new_error=None

**差异与原因：** 转到新职位已经发生，但不能由此断言不会继续找工作；平衡目标须保留。v3 限定词引用未关联的旧来源，原结构校验失败。人工将变化理解为求职进展，具体语义及时间仍须复核；差异来自对齐和证据边界。

## career_history

旧记忆：Previously worked as a senior developer in Blockchain Tech

旧记忆来源：`05afde13-35bd-4d26-bbae-6de427d58db1`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/before.json`。

选定新证据：
- new-0：I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content`）
- new-2：MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content`）

**独立人工预期**
- modify：无
- preserve：曾在 Blockchain Tech 任 senior developer 的历史
- uncertain：具体离职或转型时间、当前雇佣关系及公司所有权细节
- add：咨询公司获得初始客户
- missing：本会话没有给出具体离职日期或直接否定历史。

**人工核对的对齐输入 → 规划器**
- modify（0）：无
- preserve（2）：fact="historical_employer"; subject="user"; attribute="career.historical_employer"; old_value="Blockchain Tech"; new_value="secured initial clients"; scope={"kind": "unconditional"}; relation="unrelated"; reason="unchanged or outside evidence scope"; old_quote="Blockchain Tech"; new_quote="my consulting firm finally secured some initial clients"; old_position={"start": 43, "end": 58}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="historical_title"; subject="user"; attribute="career.historical_title"; old_value="senior developer"; new_value="secured initial clients"; scope={"kind": "unconditional"}; relation="unrelated"; reason="unchanged or outside evidence scope"; old_quote="senior developer"; new_quote="my consulting firm finally secured some initial clients"; old_position={"start": 23, "end": 39}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- uncertain（1）：fact="historical_employer"; subject="user"; attribute="career.historical_employer"; old_value="Blockchain Tech"; new_value="secured initial clients"; relation="unrelated"; reason="具体离职或转型时间未知；咨询公司获客不证明当前雇佣关系或所有权细节。"; old_quote="Blockchain Tech"; new_quote="my consulting firm finally secured some initial clients"; old_position={"start": 43, "end": 58}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- add（1）：subject="user"; attribute="career.consulting_firm"; value="secured initial clients"; scope={"kind": "unknown"}; relation="supplement"; status="asserted"; reason="independent addition"; new_quote="my consulting firm finally secured some initial clients"; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; new_quote="my consulting firm finally secured some initial clients"; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Blockchain Tech"; new_quote="my consulting firm finally secured some initial clients"; old_position={"start": 43, "end": 58}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="senior developer"; new_quote="my consulting firm finally secured some initial clients"; old_position={"start": 23, "end": 39}; source_id="new-0"; status=valid; old_error=None; new_error=None

**保存的 v3 模型对齐输入 → 同一规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（3）：attribute="network_support"; relation="unrelated"; reason="missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; new_quote="MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."; source_id="new-2"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/2/content"; missing_reasons=["not explicitly supplied as new_subject", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]；fact="historical_employer"; attribute="employer"; relation="change"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="Blockchain Tech"; new_quote="my consulting firm"; old_position={"start": 43, "end": 58}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]；fact="historical_title"; attribute="title"; relation="change"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized"; old_quote="senior developer"; new_quote="consulting firm"; old_position={"start": 23, "end": 39}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/input.json#/raw_dialogue/0/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized"]
- add（0）：无
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="invalid"; new_quote="MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined. I'm focusing on maintaining these relationships as they are crucial for my firm's growth."; source_id="new-2"; status=invalid; old_error=None; new_error=missing upstream information: not explicitly supplied as new_subject; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized
- 引文校验：status="valid"; old_quote="Blockchain Tech"; new_quote="my consulting firm"; old_position={"start": 43, "end": 58}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="senior developer"; new_quote="consulting firm"; old_position={"start": 23, "end": 39}; source_id="new-0"; status=valid; old_error=None; new_error=None

**差异与原因：** 原文已明确是历史经历；咨询公司获客不推翻旧工作史，也不证明本人当前雇主、职位或所有权。v3 将获客与旧雇主及职位判为变化，语义证据不足；差异主要来自上游关系判断及输入覆盖。

## skydiving

旧记忆：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

旧记忆来源：`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`，`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`。

选定新证据：
- new-0：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content`）
- new-2：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/2/content`）
- new-8：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.（`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content`）

**独立人工预期**
- modify：无
- preserve：旧极限运动顾虑、受伤风险和安全福祉取向；不要推广为所有偏好已改变
- uncertain：模拟跳伞与旧极限运动的覆盖关系、当前真实跳伞偏好；u3 短引文本身不完整
- add：尝试模拟跳伞且感觉刺激；仍重视安全
- missing：没有确定的事实有效日期；模拟体验不证明真实跳伞偏好变化。

**人工核对的对齐输入 → 规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（4）：fact="Dislikes extreme sports (e.g., skydiving)"; subject="user"; attribute="preference.extreme_sports"; old_value="dislike"; new_value="enjoyed"; relation="unknown"; reason="模拟与真实跳伞是否同一适用范围、旧偏好是否改变无法确认。"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="Dislikes extreme sports (e.g., skydiving)"; subject="user"; attribute="preference.extreme_sports"; old_value="dislike"; new_value="tried and found thrilling"; relation="supplement"; reason="condition kind missing or unsupported"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content"; missing_reasons=[]；fact="Dislikes extreme sports due to high injury risk"; reason="no alignment for unit"; old_quote="Dislikes extreme sports (e.g., skydiving) due to high injury risk"; old_position={"start": 0, "end": 65}；fact="Dislikes extreme sports because it conflicts with commitment to safety and well-being"; subject="user"; attribute="safety.priority"; old_value="prioritize safety"; new_value="prioritize safety"; relation="unknown"; reason="安全优先得到新证据支持，但新证据未证明极限运动与安全福祉的完整冲突关系仍成立，u3 的短引文本身也不足以支持完整因果关系。"; old_quote="conflicting with commitment to safety and well-being"; new_quote="I still prioritize safety, of course."; old_position={"start": 67, "end": 119}; source_id="new-8"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content"; missing_reasons=[]
- add（2）：subject="user"; attribute="safety.priority"; value="prioritize safety"; scope={"kind": "unknown"}; relation="supplement"; status="asserted"; reason="independent addition"; new_quote="I still prioritize safety, of course."; source_id="new-8"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/8/content"; missing_reasons=[]；fact="Dislikes extreme sports (e.g., skydiving)"; subject="user"; attribute="experience.simulated_skydiving"; old_value="dislike"; new_value="tried and found thrilling"; value="tried and found thrilling"; scope={"kind": "unknown"}; relation="supplement"; status="asserted"; reason="independent addition"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content"; missing_reasons=[]
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; new_quote="I still prioritize safety, of course."; source_id="new-8"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="valid"; old_quote="conflicting with commitment to safety and well-being"; new_quote="I still prioritize safety, of course."; old_position={"start": 67, "end": 119}; source_id="new-8"; status=valid; old_error=None; new_error=None

**保存的 v3 模型对齐输入 → 同一规划器**
- modify（0）：无
- preserve（0）：无
- uncertain（3）：fact="Dislikes extreme sports (e.g., skydiving)"; attribute="attitude_toward_extreme_sports"; relation="change"; reason="missing upstream information: not explicitly supplied as old_subject; not explicitly supplied as new_subject; not explicitly supplied as old_value; not explicitly supplied as new_value; old_conditions not explicitly normalized; new_conditions not explicitly normalized; model missing evidence: No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; source_ref="results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json#/raw_dialogue/0/content"; missing_reasons=["not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized", "model missing evidence: No evidence that simulated skydiving implies changed attitude toward *actual* extreme sports; 'dislikes' refers to real skydiving, not simulation"]；fact="Dislikes extreme sports due to high injury risk"; attribute="reason_for_disliking_extreme_sports"; relation="change"; reason="evidence source missing or source id duplicated"; old_quote="Dislikes extreme sports (e.g., skydiving) due to high injury risk"; old_position={"start": 0, "end": 65}; missing_reasons=["new side lacks a single uniquely represented quote", "not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized", "model missing evidence: No statement retracting or qualifying that high injury risk *itself* is no longer a reason for dislike; 'still prioritize safety' affirms the original safety concern remains operative; 'simulated' explicitly limits scope — no evidence about real skydiving risk perception change"]；fact="Dislikes extreme sports because it conflicts with commitment to safety and well-being"; attribute="safety_commitment_conflict_with_extreme_sports"; relation="unknown"; reason="evidence source missing or source id duplicated"; old_quote="conflicting with commitment to safety and well-being"; old_position={"start": 67, "end": 119}; missing_reasons=["new side lacks a single uniquely represented quote", "not explicitly supplied as old_subject", "not explicitly supplied as new_subject", "not explicitly supplied as old_value", "not explicitly supplied as new_value", "old_conditions not explicitly normalized", "new_conditions not explicitly normalized", "model missing evidence: No evidence that simulated skydiving resolves or negates the conflict with safety commitment; 'still prioritize safety' confirms the commitment remains intact and unconflicted *by this activity* — but does not address whether real extreme sports would still conflict"]
- add（0）：无
- editable_spans（0）：无
- protected_facts（0）：无
- 引文校验：status="valid"; old_quote="Dislikes extreme sports (e.g., skydiving)"; new_quote="Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!"; old_position={"start": 0, "end": 41}; source_id="new-0"; status=valid; old_error=None; new_error=None
- 引文校验：status="invalid"; old_quote="Dislikes extreme sports (e.g., skydiving) due to high injury risk"; old_position={"start": 0, "end": 65}; status=invalid; old_error=None; new_error=evidence source missing or source id duplicated
- 引文校验：status="invalid"; old_quote="conflicting with commitment to safety and well-being"; old_position={"start": 67, "end": 119}; status=invalid; old_error=None; new_error=evidence source missing or source id duplicated

**差异与原因：** 新证据只证明模拟跳伞经历及安全取向，不能证明真实极限运动偏好或受伤理由改变。人工预期倾向保留旧顾虑，规划器对缺少直接支持和重叠拆分的旧关系更保守地列待确认。v3 自报缺证却仍判两项 state_change；SimpleMem 单元重叠，u3 短引文不能独立证明完整关系。差异主要来自上游对齐、证据覆盖及拆分粒度。

## 二维条件组合验证

旧范围为上海、南京两店 × 堂食、外带；新范围为上海＋外带。

修改组合：[{"服务": "外带", "门店": "上海"}]

保留组合：[{"服务": "堂食", "门店": "上海"}, {"服务": "堂食", "门店": "南京"}, {"服务": "外带", "门店": "南京"}]

## 解释和限制

借鉴的思路：按 ERASE 风格先判断再修订；参考 FactTrack 的时间有效性和重叠意识，以及 Cedar 条件的交叠与包含思路。本实现不调用、不移植以上模块，也不复用旧 part2_scope_planner；有限离散条件的组合枚举、引文校验、保守判断和适配层由本实验单独实现。

实际仅实现显式无条件、有限离散条件和明确 same_as_old；日期区间、开放域、自然语言归一化及蕴含判断不受支持，未知不能视作全域。缺少精确日期时，相对状态变更可按输入表达处理，但无法计算生效时间或自动证明历史事实。输入语义仍须人工核对，源对象的内容和标识依赖调用方；离线来源复核见 SOURCES.md。

人工预期是研究者依据原文整理的参考而非用户确认金标准。原始对齐结果可能语义错误，即使引用和结构检查通过也不构成证据有效性的证明。
