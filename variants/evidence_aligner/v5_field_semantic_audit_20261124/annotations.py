"""Manual attribution, for offline reporting only; never used as planner input.

Tuple: scope class, recommended expression, expansion, time/causality, review/schema issue.
Empty strings mean no issue identified in that category, not proof of correctness.
"""
DATA={
'susan':{
'facts':[
('unspecified','保留 Susan／support／invaluable；原文没说支持在任何比较维度上均无限制，若要做范围运算而未声明轴则条件未知。','','','原审核只说完整无条件范围未证明；没有指出具体轴，不能把它等价为事实内核错误。'),
('unspecified','保留 Susan 的鼓励帮助用户专注其目标；原文未声明适用范围，待比较轴确定后再判断。','','','上一轮没有指明哪一个范围轴使该断言过宽，不能仅凭完整范围未证实否认内核。'),
('embedded','保留主体 Daniel、其见解、用户职业思考；career 已在 value 中，其他比较维度未知，不要丢掉 career。','','','职业限定已由值表达；不必机械认为没有条件轴就将该内核判错。'),
('unspecified','保留原句指称 these connections；集合的确切成员待确认，未提及的范围轴未知。','把 these connections 写为 Susan、Daniel、etc. 的具体集合超出单句可证范围；前文可提供指代线索但不证明集合完整。','','代词解消与适用条件是不同问题；unconditional 不会修复主体集合扩写。'),
('embedded','保留 subject=current role、比较对象 as much as I would like；当前角色已在主体中，时间持续区间未给出。','','','current 已在 subject 中；unconditional 不是代码自动把 subject 改为所有岗位，但未知其他范围时仍不应证明所有比较维度无限制。'),
('embedded','分别表示同一个期望新工作需要更好平衡、符合人道目标；两项必须保留合取，modality=planned。','','','模型 value 为数组；v4 校验要求标量字符串，但 v5 提示词未明确写出 value 的类型，也未说明拆开后需保留同一工作的合取。')],
'relations':[
('unspecified','旧支持事实与新支持评价属性不同；不应填 same，旧影响可暂记 unknown；旧范围轴未说明。','把“支持有价值”当成与“提供支持和鼓励”同值；可以补充评价，但 same 的精确同属性同值要求未满足。','','schema 的 same 需要相同主体、属性和值；自然语言“相容”不等于该枚举的 same。'),
('unspecified','Susan 的鼓励可补充功能细节；保持 supplement 并将其对旧断言的影响单独设 unknown，比较范围未说明。','','','模型 supplement 被 v5 适配成旧影响 unknown；旧审核认为范围未证，但未指出具体比较维度。'),
('unspecified','旧文完整记忆明确 ThomasSusan referred to as Susan；属性不同不等于主体不同，关系及无影响仍需判断。','模型理由断言主体无交集，但完整旧文提供 Susan 的称呼；不能据短引文断言身份不相关。','','模型把 unrelated 当属性不同；规划器 unrelated 表示旧事实无影响并需要 no_impact_confirmed，两个定义未对齐。'),
('unspecified','旧朋友关系与鼓励功能分别判断；完整旧文包含 Susan 指称，旧范围轴未说明。','模型说 no shared semantic content，不能由属性不同推出关系主体和旧影响均无关。','','unrelated 在提示词中不够区分“不同属性”和“可证明无旧影响”，规划器需要额外确认。')]
},
'promotion':{
'facts':[
('lost','表达用户在所述晋升语境中与 Historical Productions Ltd. 的雇佣关联；其后持续期未给出；为关系比较单列事件时间。','从晋升时 at 公司推断不受时间限定的 current employment 过强。','晋升在发话前 recently，不能证明当前雇佣连续或晚于旧事实。','现有 schema 没有事实有效时间与相对发话事件时间分开的字段；unconditional 也不能表达这个差异。'),
('lost','表达最近晋升所得 lead director，保留该事件与公司和相对发话的时间；职位何时起止未知。','','理由将最近晋升推成发话时仍担任；所引文字未明确给出持续区间。recently 不决定相对旧职位事实的先后。','条件维度与职位值中的时间语义界限没有明确，旧审核须列明所担心的时间轴。'),
('lost','表达用户最近晋升至 lead director、关联该公司；晋升目标和 recently 未在此条值中体现。','','仅可判断事件在发话前最近发生；相对旧事实顺序未知。','事实与事件时间缺少专用字段；若跨事实引用目标职位，需明确事件关联而非假装同条已含。')],
'relations':[
('unspecified','两侧公司名称相同可保留为公司名一致；持续雇佣及同一有效时间分别未知。','名称重复本身不证明整个雇佣关系的持续与同刻成立。','same 时间假设和持续雇佣未被新旧有效期证实。','same 值相同与同一有效时间是不同判断；缺少明确有效时间表示。'),
('unspecified','新话语中的晋升事件可记录；Director 是否仍为宽泛称谓、是否应覆盖、相对旧事实先后均待确认。','更具体的 lead director 不必否定旧的 Director；不能推断替代。','recently 只相对发话，不证明新状态晚于旧记忆事实的有效时间。','change 需要值排他和时序证据；引文可定位不验证这些语义。')]
},
'career_history':{
'facts':[
('unspecified','所选原句支持“用户所称咨询公司获得初始客户”；没有单独结构化该事件，条件轴未明确。','my consulting firm 不证明 founder、owner 或本人雇员身份。','','核心身份错误，不能通过调整 unconditional 或单纯补日期修复。'),
('unspecified','选中的 new-0 只说 consulting firm 获客；政治咨询领域不在该引文内，不可使用未选来源冒充其直接证据。','模型给出 political consulting，引用却没有；其他对话仅为上下文，不能当成该条已绑定证据。','','逐字引文存在与能够支持取值是两项检查；当前校验只证明前者。'),
('lost','两位联系人各自作用如可确认需分别表达；仅保留他们很有帮助、其关系打开原话所说的机会，是否为公司未知。','模型把两个人合为一条，并把“为我打开想不到的门”具体化为“为公司打开”。','','同一引文中的并列主体是否拆分及复数事实如何绑定，schema 和提示词需说清。'),
('embedded','保留用户当前专注维持这些关系，以及用户认为其对公司增长重要；current focus 已在属性中。','','','主观判断应标记为用户观点；当前时点已编码，不能只凭 unconditional 就认定主体条件全丢。')],
'relations':[
('lost','旧记忆是以前在 Blockchain Tech 工作的历史；保持该历史，获客不证明新雇主身份或对旧历史的影响。','咨询公司获客不能证明 founder、owner、现雇主切换。','finally、lately 不能证明获客与旧历史有效期先后或工作不兼容。','旧单元短引文仅 Blockchain Tech，模型 semantic_basis 引用 Previously worked 不在绑定旧引文中；旧记忆上下文可见但不能假装该引文已绑定。'),
('lost','旧 senior developer 是历史职位；没有证据证明新活动替代该历史或二者排他。','把 founder/owner 当已确认职位且假定与 senior developer 不兼容。','过去工作语句不能独立证明新职位时间先后或排他；时间依据仅旧侧且超出已绑定引文。','旧侧历史限定在完整旧文而非指定短引文中；关系需要合规绑定，不应从其他单元补造引用。')]
},
'transition':{
'facts':[
('lost','应独立表达用户已转到新职位及 relief；是否继续求职未知。该模型值没有正确承载已转岗事实。','no longer searching 并非原话；转岗与停止求职不是同一事实。','finally 表明转岗相对话语已完成，不能证明停止求职或原求职压力解除。','改 conditions 为 unknown 也不会修复错误取值；需要重拆事实并单独查证。'),
('embedded','保留用户 now 评价工作与个人生活的平衡更健康；now 已出现在 value，起止时间未知。','','','原审核提醒不推广到其他时段是合理的；但 now 已在 value，unconditional 并非代码自动将该词删除。')],
'relations':[
('lost','旧求职事实与“已转岗”分开；停止求职未知，旧求职是否失效未知。','新值 no longer searching 无依据；将转岗等同结束求职是实质错误。','finally 表示转岗相对话语已经发生，不证明相对旧求职有效期的 after。','change 的旧新值要有相同属性并有可审核的相对生效次序；主引文存在不能补足语义。'),
('embedded','更健康的当前平衡是新评价；旧目标是否实现或停止、适用范围与先后均待确认。','把平衡变健康写为旧求职目标已完全实现并被替代，证据不足。','now 只锚定该话语当前，不证明它发生在旧目标有效期之后。','原值是 expectation，新值是当前评价，属性不同；关系不能只按字符串比较。')]
},
'skydiving':{
'facts':[
('embedded','保留 simulated、team-building event、recently 与已尝试；这些限制都在 attribute/value 中。','','recently 仅相对新话语；没有给具体事件日期或相对旧事实次序。','原审核称无条件范围未证，但模拟、团建和最近均已编码；不能把 unconditional 一律读作体验适用于真实活动。'),
('embedded','保留“对这次 simulated skydiving 感到 thrilling”；模拟限定已在 attribute，需绑定同次体验。','','','模型值没明说是哪一次但属性限定模拟；事件引用需要维持关联，不能笼统判为所有真实跳伞体验。'),
('embedded','保留对这次 adrenaline rush 没想到会如此享受；不是原以为完全不享受。','模型 rationale 把“不曾料到这么享受”扩大为先前预计不享受。','前后预期程度比较由原话支持，不支持“先前完全不享受”。','值本身较准确，错误主要在 rationale；不能因条件而掩盖该区别。'),
('embedded','保留更愿意尝试新事物，和此体验的关联；新事物不自动等同真实极限运动。','','用户说 it made me 更开放，体验与开放程度的自述因果有原话；不推断和旧记忆的时间顺序。','事件触发因果可以有依据，不能把所有因果都当成幻觉。'),
('embedded','保留用户 still prioritize safety；still 是用户自述的延续，实际完整有效期和过去对应旧断言的范围未知。','','still 支持相对发话的延续，不自动证明恰与旧事实相同时间段。','safety 已在 attribute/value；以前审核需要明确具体比较维度，不能一概等同所有时间。'),
('embedded','保留 for now、enjoying thrill、seeing where it takes me；限定已在 value。','理由扩展为对长期参与 thrill-seeking activities 的非承诺立场，原话未明确长期计划。','for now 仅表明说话时暂时状态，不证明长期计划。','既有 value 已包含时间限定；应区分支持的原值和超出原文的 rationale。')],
'relations':[
('embedded','新事实只涉及模拟体验；旧 u1 实际是否包含模拟、态度是否变化均未知。旧句未显式给出模拟/真实条件，不能凭空补全。','把模拟作为旧态度可确认的细化，并称其低风险，原文没有证明。','recently 与发话时间不能证明晚于旧事实；模型提及会话日期不等于事实生效时间。','supplement 被投影为旧影响 unknown，保留原始关系；新事实模拟限定在关联事实属性和值内，旧范围仍未知。'),
('embedded','旧风险理由是否仍适用未知；新事实是一次模拟活动，不能据此确认对旧原因的影响。','认为选择模拟是基于对低伤害风险的认识与风险规避，原句没有此因果。','recently 不能证明相对旧事实的 after；选择模拟的动机也未给出。','对于模拟活动的限定已在引用事实中；用户对风险的主观判断并未作为独立事实给出。'),
('unspecified','新证据仅支持仍优先安全；旧 u3 的安全与福祉及冲突因果整体是否相同待确认。','把安全优先扩展为安全和福祉的完整旧冲突理由持续不变。','still 支持延续，但不足以建立和旧事实完全同一有效时间。','旧 value 含 well-being、冲突关系，新 value 仅 safety；same 的同属性同值要求未满足。'),
('embedded','保留模拟活动刺激这一体验；该体验与真实跳伞偏好是否矛盾或覆盖旧厌恶未知。','把觉得模拟刺激推成真实跳伞厌恶被否定。','recently 不证明晚于旧态度有效期。','刺激是体验评价而非相同属性上的偏好反值；关联事实含模拟限定，不应在旧比较中丢失。'),
('embedded','保留更愿尝试新事物，但其是否覆盖真实极限运动及旧偏好未知。','把一般尝新开放度扩大为极限运动喜好改变。','made me 支持体验使人更开放的自述，不证明体验晚于旧记忆事实的有效时间。','属性“尝试新事物”与“极限运动偏好”不是自动同一属性。')]
}}
