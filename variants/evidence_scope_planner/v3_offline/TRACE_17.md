# 防护后 17 项 uncertain 的逐条溯源

本文件独立读取 `variants/evidence_aligner/v4_scope_interface/runs/qwen_20261124_once/{case}.json` 中 `result.parsed.records`、`prepared_input` 及 `offline_safe/{case}.json` 中 `adapted_alignments`、`safe_plan.uncertain`，并参照同目录实验的 `human_reviews.json`；未修改原始模型结果。每项序号是 **offline_safe 的 uncertain 数组索引**（从 0 起），模型记录索引是原始 parsed records 索引（从 0 起）。同一记录可分别产生新增候选和旧项影响两个 uncertain，因此 17 项不等于 14 条模型记录。旧源的完整磁盘快照路径、用户、会话及 `new-*` 的 source_ref 见旧版 `variants/evidence_scope_planner/v2_offline/SOURCES.md` 和原始 case JSON。

类别可重叠：①模型语义错误或证据不足；②结构、引文绑定或来源问题；③模型组未向 v2 提供独立语义授权（`semantic_support=unknown`；模型自己的 rationale 与引文命中不构成授权）；④范围不可计算或条件不确定；⑤其他阻断，例如补充事实对旧项是否无影响未知。下文“首因”是该 uncertain 的真实 `reason`，不是排他原因；v2 先显示的一项错误可能遮住属性不匹配、未授权或条件问题。即使来源和引文有效，也不代表先后或主张语义得到证明。

按 17 条输出的多标签统计：①17、②9、③17、④4、⑤2，标签可重复，不能相加为 17。①包括整体关系、范围或时间未充分支持，不表示每条新事实的各个子命题均为假；③说明缺少独立认证这一共同门禁，不表示它是每项显示的首因，也不意味着通过独立审核并提供绑定依据的路径走不通。

## 证据索引（逐字引文）

- **Susan S0**：旧源 `a1332815-d6ba-4bdc-9ffa-657f7315d0ed`、`friendship` 的 `friend named ThomasSusan`；新 `new-2` 的 `Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.`。S0 的语义依据还引 `ctx-1` 的历史会话全文，但该依据未包含在关联旧单元引文中，故不能自动充当这条旧记忆的已绑定证据。
- **Susan S1**：同一旧源 `support` 的 `provides support and encouragement`；新 `new-2` 的 `Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals.`
- **Susan S2**：无旧单元；新 `new-0` 的 `my current role isn't supporting my well-being as much as I'd like`。
- **Susan S3**：无旧单元；新 `new-0` 的 `It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals.`
- **晋升 P0**：旧源 `e13b825e-7ec7-4760-821e-0581d8da5650` 的 `Historical Productions Ltd.`；新 `new-0` 的 `I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!`
- **晋升 P1**：同一旧源的 `Director`；新引文与 P0 相同。此前会话用户陈述 `I work at Historical Productions Ltd. as a Director.`（`ctx-1`）有助理解旧主体，但没有证明新晋升必然晚于这条旧记忆的**事实有效期**。
- **职业历史 C0**：旧源 `05afde13-35bd-4d26-bbae-6de427d58db1` 的 `Blockchain Tech`；新 `new-0` 的 `my consulting firm finally secured some initial clients`。旧整句是 `Previously worked as a senior developer in Blockchain Tech`。
- **职业历史 C1**：同一旧源的 `senior developer`；新引文同 C0。
- **职业历史 C2**：无旧单元；新 `new-2` 的 `MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn't have imagined.`
- **转岗 T0**：旧源 `e6ab178b-c0f9-4adb-bfb7-e4648617a950` 的 `Looking for a new job with better work-life balance`；新 `new-0` 的 `I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now.`
- **转岗 T1**：同一旧引文；新 `new-0` 的 `The balance between work and personal life is much healthier now.`
- **跳伞 K0**：旧源 `e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`、u1 的 `Dislikes extreme sports (e.g., skydiving)`；新 `new-0` 的 `Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!`，以及 `new-2` 的 `Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.`
- **跳伞 K1**：同一旧源 u2 的 `Dislikes extreme sports (e.g., skydiving) due to high injury risk`；新 `new-0` 同 K0，以及 `new-8` 的 `For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.`
- **跳伞 K2**：同一旧源 u3 的 `conflicting with commitment to safety and well-being`；新 `new-8` 同 K1。u3 本身的短引文不完整表达原句整个因果。

## 逐项追踪

| 项目 | 模型判断 → 适配与规划器拒绝 | 类别和实际含义 |
|---|---|---|
| Susan #0，S1，模型记录 1 | `supplement`、新值为帮助专注，`asserted`，旧/新条件均 `unconditional`。这是**独立新增候选**；引文与 basis 绑定有效，适配器保留原值，但 `semantic_support=unknown`。首因 `semantic support or bound basis missing`。 | ①③：新话语确实支持 Susan 鼓励和帮助专注这一子事实；旧短引文未独立说明对象，“同一时间”和无条件范围未证明；候选还缺独立授权。 |
| Susan #1，S2，模型记录 2 | `new_information`、当前角色对福祉支持不足、`asserted`；无旧单元，主引文有效，模型仍输出相对旧状态 `same`。新增分支首因 `semantic support or bound basis missing`。 | ①③：新事实本身有引文，适合单独审核；未关联旧状态却给 `same` 无比较对象，`unconditional` 未由空条件证明；独立语义授权未提供。时间字段与该新增分支的首因不可混同。 |
| Susan #2，S3，模型记录 3 | `new_information`、`planned` 寻找符合目标的新工作；适配保留原始计划和引文。首因 `upstream validation errors: records[3].temporal_order.basis[0] not bound to cited same-side source/quote`：模型时间依据含 `...` 且超出所引用短句。 | ①②③：计划子事实有依据，但将心理活动先后写成相对旧记忆 `after` 无旧参照；该依据不是逐字已绑定引文；另外缺独立语义授权。未知完成日期并非这项直接失败原因。 |
| Susan #3，S0，模型记录 0 | `same`，旧主体/值 `ThomasSusan`、新主体/值 `Susan`，称同名同友谊。首因 `upstream validation errors: records[0].semantic_basis[1] not bound to cited same-side source/quote`，即未绑定 `ctx-1`。 | ①②③：主引文能定位，ctx-1 不能冒充已关联旧单元；短引文未独立证实别名、同时性和无条件；若先修首因，v2 还会发现两侧主体/值不同和无独立授权。 |
| Susan #4，S1，模型记录 1 | 同 S1，**旧事实影响分支**。`supplement` 能否独立新增与是否影响旧事实分开；未给 `no_impact_confirmed`，首因 `impact of new information on old fact is not established`。 | ①③⑤：新支持细节不自动证明完整旧关系及范围；没有独立认证，也没有明确的旧项无影响授权。与 #0 是同一模型记录的不同动作。 |
| 晋升 #0，P0，模型记录 0 | `same` employer，旧/新值同为公司，两个主体却写成公司自身；条件 `unconditional`、时间 `same`。首因 `semantic support or bound basis missing`。 | ①③：公司名称重现有据，但主体应关联雇佣者而不是把公司当雇员，状态同时和无限定也未获证明；独立授权缺失。 |
| 晋升 #1，P1，模型记录 1 | `change`、`Director → lead director`、`asserted`，条件均 `unconditional`；模型把 `I recently got promoted` 标为新状态相对旧状态 `after`。首因 `semantic support or bound basis missing`。 | ①③：晋升已发生有据，不需要虚构日期；`recently` 仅相对发话，不单独证明晚于旧记忆事实，也不证明宽泛 Director 称谓不再成立。对这条 change，独立授权不足是实际首因，而上述时间语义仍必须单独审核。 |
| 职业历史 #0，C2，模型记录 2 | `new_information`、联系人；模型 `new_value` 为数组，违反字符串/null 契约，适配后安全值为空。首因 `upstream validation errors: records[2].new_value must be nonempty text or null (unknown)`。 | ①②③：两人帮助的子事实有据，但 `unconditional` 未证；值类型无效且缺独立语义授权。这里不应因两个名字就推断具体关系身份。 |
| 职业历史 #1，C0，模型记录 0 | `change`，旧属性 employer、新属性 current employer/business ownership，旧值 Blockchain Tech、新值 consulting firm。首因两条 `records[0].temporal_order.basis` 不在该侧关联引文内。 | ①②③：获客不证明公司所有权、当前雇主、旧雇佣结束或不兼容；完整旧句和新句前缀不属于本记录引用的短片段；新旧属性也不相同，且缺独立授权。`Previously` 与 `lately/finally` 不能自行证明两个事实的有效时序。 |
| 职业历史 #2，C1，模型记录 1 | `change`，`senior developer → founder / operator of consulting firm`；首因两条 `records[1].temporal_order.basis` 未绑定。 | ①②③：原话未给咨询公司创办者或经营者职位，也未说旧职位被取代；时间依据超出两侧引用，属性 `job title` 与 `current role` 不同，并缺独立授权。 |
| 转岗 #0，T1，模型记录 1 | `supplement`、模型称原平衡目标现在已实现；主引用有效，新增候选首因 `semantic support or bound basis missing`。 | ①③：用户只说平衡更健康，未证明目标完全实现、动机同一时点或无条件；缺独立语义认证。 |
| 转岗 #1，T0，模型记录 0 | `change`、`looking for a new job with better work-life balance → transitioned to a new role with healthier work-life balance`；主引文及字面 basis 有效，首因 `semantic support or bound basis missing`。 | ①③：`I've finally transitioned to a new role` 支持已转岗，`The balance ... is much healthier now` 支持改善；不能据 `finally` 单独证明它晚于旧记忆有效期、或从此停止找工作，更不应丢掉平衡目标。具体日期未知与比较先后未知是不同问题。 |
| 转岗 #2，T1，模型记录 1 | 同 T1，**对旧平衡目标的影响分支**；首因 `impact of new information on old fact is not established`。 | ①③⑤：新增更健康的平衡并不自动证明原目标已完全实现或失效；缺无影响确认和独立认证，与 #0 不是重复的同一个动作。 |
| 跳伞 #0，K2，模型记录 2 | `supplement`、`still prioritized`、`asserted`；这是新增候选。首因 `upstream validation errors: records[2].old_conditions cannot use same_as_old`，模型把 `same_as_old` 放在旧条件。 | ①②③④：重视安全有新引文，但不证明完整旧冲突因果或仅接受模拟；旧条件结构不合法，且 `context` 把“模拟”和“团建”当同维可选值，条件组合未证明；无独立语义授权。 |
| 跳伞 #1，K0，模型记录 0 | `change`、厌恶极限运动 → 享受模拟与更愿尝新，旧 `unconditional`、新 `finite`。首因包括 `records[0].temporal_order.basis[0] not bound...` 和 `planner_scope_unrepresentable: v2 cannot partition unconditional old scope by finite new scope`；适配器保留原条件在 `raw_record/scope_guard`，投影未知以防 v2 错将空交集当无影响。 | ①②③④：模拟不能证明真实运动偏好改变；时间依据误引未关联 `ctx-1` 并将发言日期当事实先后；旧无条件域与有限新域的剩余不能可靠枚举；缺独立授权。 |
| 跳伞 #2，K1，模型记录 1 | `change`、旧受伤风险理由 → “未说明为当前障碍、继续重视安全”；首因同 #1，但针对 `records[1]`。 | ①②③④：未再次提及不是撤回理由，模拟不是现实风险；未绑定 ctx-1、无法可靠对无条件域做有限差集，且缺独立授权。 |
| 跳伞 #3，K2，模型记录 2 | 同 K2，**旧事实影响分支**；首因仍是 `records[2].old_conditions cannot use same_as_old`，而不是 #0 的单独新增资格。 | ①②③④：旧条件非法使比较无定义；新安全优先未证明原来的全部冲突与因果，语义认证亦缺。 |

## 依据先后与状态变化的边界

晋升：`I recently got promoted to lead director ...` 明确晋升相对发言已发生；`Director` 是旧文本中的职位。二者支持存在晋升及旧职位记载，但仅凭 `recently`、记录时间或保存先后，无法证明晋升晚于旧事实有效时间；“lead director”也不必然否定广义 Director。若另有明确、可信、已关联的先后证据，可直接提供相对时间标注；不必强求具体日历日期。

转岗：`I've finally transitioned to a new role` 支持转岗已发生；`The balance between work and personal life is much healthier now` 支持现时平衡改善。旧文 `Looking for a new job with better work-life balance` 包含求职状态和平衡目标；新句不证明从此不再找其他工作，也不能只凭 `finally` 确定其与旧记忆事实有效期的先后。缺少必要关系时，旧状态的覆盖与平衡目标应分别审核，不能因没有精确日期而一概视为无法记录转岗事实。
