"""One-time independent, case-specific review; never passed to any planner."""
import json
from pathlib import Path
from comparison import CASES, digest
H=Path(__file__).resolve().parent
# Each note was checked against the old/new source quotations and the saved
# v4/v3 audit. A verdict applies to the whole structured action, including
# its subject, attribute, conditions and modality, not merely to a substring.
R={
'susan':{
'A':{'uncertain':[
('hold','Susan 的鼓励和专注子事实有原话支持；此记录没有独立授权，旧关系与新增应分开。'),
('hold','当前角色福祉支持不足有原话支持，但模型输出没有独立授权。'),
('hold','求职意向有原话支持；时间依据含省略号且未绑定，不能当作已完成。'),
('hold','主引文可定位，但 ctx-1 不属于该记录关联的旧单元引文，姓名映射仍须核对。'),
('hold','支持的新细节不自动证明整个旧友谊关系在所有条件下不受影响。')]},
'B':{'add':[
('partial_add','Susan 的支持和帮助专注有依据；unconditional 及该结构化关系的完整适用范围并未独立证实。'),
('correct_add','用户明确说当前角色对福祉支持不如希望；这里仅按当前角色和相对期望理解，不推定永久状态。')],
'uncertain':[
('hold','找工作是计划；模型时间依据不是逐字引用且没有旧状态可比较，暂缓是结构层结果。'),
('hold','旧单元与新话语各有引文，但 ctx-1 语义依据未绑定；不能据此直接确定名字及友谊同值。'),
('hold','新支持细节不能自动证明旧事实在所有范围都无影响。')]},
'C':{'preserve':[('supported','人工输入明确对齐 Susan 的支持和鼓励；原记忆和新用户话语均支持该子事实。')],
'add':[('correct_add','Daniel 的见解推动职业思考有对应用户原话。'),('correct_add','找更好平衡并符合人道目标的工作是计划，输出保留 planned 模态。')],
'uncertain':[('hold','Susan 与 ThomasSusan 的跨源身份、朋友关系当前状态仍须核对。')]}},
'promotion':{
'A':{'uncertain':[('hold','公司名重现，但模型把公司当主体，且没有独立语义授权。'),('hold','晋升已发生，但 recently 不证明其晚于旧记忆有效期，宽泛 Director 未必失效。')]},
'B':{'modify':[('unsupported_modify','recently 只相对发话，不证明晋升晚于旧记忆有效期；lead director 不必否定宽泛 Director。此修改缺依据，并非证明晋升为假。')],
'preserve':[('incorrect_preserve','公司名虽相同，但模型把公司本身写成 employer 主体，不能认证为用户雇主关系。')]},
'C':{'preserve':[('supported','人工输入将用户作为主体，同一公司名由旧文及晋升话语支持。')],
'uncertain':[('hold','确切晋升日未知；这不否认晋升已发生，也非所有操作都需要具体日期。'),('hold','Director 是否仍是宽泛描述不能仅靠字符串推断。'),('hold','缺独立的相对旧事实先后依据，因此不覆盖旧状态。')]}},
'career_history':{
'A':{'uncertain':[('hold','联系人是列表类型，不符合接口标量值；两人帮助的子事实原文可支持。'),('hold','公司获客不证明当前雇主、所有权或旧雇佣终止，时间依据又未绑定。'),('hold','用户未声称创办或经营公司；旧职位被替代及时间依据均未证明。')]},
'B':{'add':[('incorrect_add','my consulting firm 获客不证明用户现在以其为雇主或具有公司所有权。'),('incorrect_add','原文未证明 founder/operator 职位；不能从公司获客反推。')],
'uncertain':[('hold','联系人 new_value 为数组，不能冒充合法标量字段；两人帮助的事实有依据。'),('hold','旧新属性不一致，时间依据未绑定；获客不改变过去雇主的事实。'),('hold','时间依据未绑定且 founder/operator 不受证据支持，旧职称不应修改。')]},
'C':{'preserve':[('supported','此前 Blockchain Tech 雇主经历为旧记忆的历史事实。'),('supported','此前 senior developer 职位为旧记忆的历史事实。')],
'add':[('correct_add','用户说咨询公司获得初始客户；不由此推断用户的所有权或职位。')],
'uncertain':[('hold','离职和转型日期、现职以及所有权细节没有足够证据。')]}},
'transition':{
'A':{'uncertain':[('hold','平衡更健康有依据，但是否完全实现此前目标及适用范围未获独立授权。'),('hold','转岗已发生；是否晚于旧事实、是否停止找工作均未证明。'),('hold','新增改善与旧目标是否仍有效是两个判断；旧目标不可自动删除。')]},
'B':{'add':[('incorrect_add','原话只说平衡更健康；模型结构称原目标已实现，证据不证明达到原目标。'),('partial_add','转岗与平衡更健康都有原话支持；但以 job search status 表述容易暗示停止求职，且适用范围未核实。')],
'uncertain':[('hold','新改善不自动证明旧平衡目标失效或已完全实现。')]},
'C':{'preserve':[('supported','原句中的更好工作生活平衡目标已作为明确保护事实。')],
'add':[('correct_add','用户明确说工作和生活的平衡现在更健康；不推断目标已完全实现。')],
'uncertain':[('hold','转岗后是否继续找工作未知。'),('hold','职位切换生效的具体日期未知。'),('hold','转岗相对于旧记忆事实的先后不足以直接覆盖旧求职状态。')]}},
'skydiving':{
'A':{'uncertain':[
('hold','新话语支持重视安全，但模型 old_conditions 使用非法 same_as_old，且旧因果关系未被重新证实。'),
('hold','旧无条件范围的余域无法从模型有限候选枚举；候选模拟/团建不是已审核的完整范围。'),
('hold','模型时序依据引用未关联 ctx-1；模拟体验不能证明真实运动偏好改变。'),
('hold','同一模型记录将团建列为另一条件值，关系及条件组合均未经审核。'),
('hold','旧理由的无条件余域无法由有限候选求差；不得据空交集保留。'),
('hold','未提及风险不等于否定风险理由；旧时序依据未绑定。'),
('hold','团建不是已证实的独立互斥范围，旧时序依据未绑定。'),
('hold','旧条件非法，安全优先不证明完整旧冲突因果。')]},
'B':{'add':[('incorrect_add','“未称为当前障碍”是从未提及作出的推断；新话语不证明旧受伤风险理由已不再适用。')],
'uncertain':[
('hold','安全优先的子事实有依据，但旧侧 same_as_old 非法，完整冲突因果未被证实。'),
('hold','安全优先有原话，但自动拆出的新片段未能以模型给定属性/已绑定依据独立成立。'),
('hold','原模型旧条件无限定、新条件有限且未经审查，余域不能枚举。'),
('hold','模拟体验不能直接证明真实偏好改变；旧侧时序依据未绑定。'),
('hold','模型将团建当另一同维条件值，未证明这些组合及其时间关系。'),
('hold','旧风险理由范围的余域无法依有限候选计算。'),
('hold','安全优先不撤销原风险理由；模型旧时序依据未绑定。'),
('hold','团建条件的作用域和风险理由均不足以确定。'),
('hold','旧条件非法；新安全优先不独立证明原冲突因果。'),
('hold','模型把模拟体验与更开放两条值置于同一属性和重叠范围，v3 将它们标作潜在冲突；原文支持模拟体验子事实。'),
('hold','更愿尝新有原话，但不等于真实极限运动偏好变化；同属性候选冲突需拆解。')]},
'C':{'add':[('correct_add','用户明确说尝试模拟跳伞且觉得刺激；不推断真实跳伞偏好变化。'),('correct_add','用户明确说仍将安全放在优先位置；不推断完整旧因果。')],
'uncertain':[('hold','模拟体验与真实极限运动偏好的关系未确定。'),('hold','独立记录模拟体验不决定对原厌恶的影响。'),('hold','受伤风险理由单元没有足以决定影响的对齐记录。'),('hold','仍重视安全不足以确认旧极限运动冲突因果整体。')]}}
}
F={
'susan': {'new_subfacts':'S0 名字/朋友；S1 Susan 支持；S2 当前角色福祉；S3 求职计划；new-2 同句 Daniel 的见解被模型遗漏。','deferred':'A 暂缓支持、当前角色和求职计划；B 仍暂缓计划（无效时间依据），且没有 Daniel 候选；C 独立加入 Daniel 与计划。', 'difference':'B 不再要求独立授权，故产生两个新增候选；两项分别审核，不能据此把友情/身份设为同值。', 'human_dependency':'C 的身份、Daniel、计划拆分来自既存人工对齐；B 只复制模型字段与引用。'},
'promotion': {'new_subfacts':'同一公司名与晋升事件可从新句读取；Director 宽泛称谓、旧有效时间须另判。','deferred':'A/C 暂缓覆盖；B 提出无充分时间依据的修改，关联新值候选为避免重复被抑制，故不等于安全记录了晋升事件。','difference':'B 机械接受模型 after 和主体字段，产生错误修改候选与主体错误的保留；C 同雇主主体来自人工核对。','human_dependency':'人工 C 判断雇主不变并保留具体不确定；B 的 after 完全来自模型。'},
'career_history': {'new_subfacts':'用户说咨询公司获初始客户；MooreSandra、GonzalezMary 的联系提供帮助。旧文记的是此前技术职位。','deferred':'模型未把获客独立生成正确的结构化候选；联系人值数组未过字段检查；A/B 对旧工作变更继续暂缓。','difference':'B 从两条 change 拆出新侧候选，但继承模型臆造的当前雇主/创办经营关系，因此出现两个错误新增；C 只新增获客并保留旧历史。','human_dependency':'C 的历史保留、获客拆分和身份边界是先前人工核对；B 不借用它们。'},
 'transition': {'new_subfacts':'用户说已经转岗，且现在工作与生活的平衡更健康；旧求职目标是否停止并未说明。','deferred':'A 对旧状态及新改善均暂缓；B 的旧 change 关系在 v3 同单元聚合时未单独出现在输出中，不能误称已判断；C 保护旧平衡并记录改善。','difference':'B 产生两个新增候选，其一把更健康推为目标实现，另一事件值有依据但属性写作求职状态；C 的事实拆分来自人工。','human_dependency':'C 保护目标和单独改善是既有人工输入；原模型 after 不能由 finally 自动证实。'},
 'skydiving': {'new_subfacts':'模拟跳伞的愉快体验、更愿尝新和仍重视安全分别有原话；真实极限运动偏好与受伤理由是否改变未知。','deferred':'B 把分号分开的模型新值分别作为候选，但沿用模型同一属性/条件，两个可支持的体验子句被 v3 视为冲突，旧变化仍因 ctx-1 未绑定等待；C 独立记录模拟体验及安全优先。','difference':'B 产生一个无依据新增（未提及被解释为当前无障碍）；A 全部待确认；C 按人工事实边界新增两个子事实。','human_dependency':'模拟/真实区别与安全事实的精确拆分由 C 人工输入提供；B 没有从预期补属性。'}
}

def main():
    target=H/'AUDIT.json'
    if target.exists(): raise FileExistsError('audit already exists; compare hashes before manual review instead of rebinding')
    out={'method':'逐项独立核对已保存原文及既有审核，B 的 supported 仅为模拟门禁且不是本审核；条目哈希用于防止结果漂移。', 'cases':{}}
    for case in CASES:
        data=json.loads((H/'results'/f'{case}.json').read_text(encoding='utf-8'))
        reviewed={'findings':F[case], 'groups':{}}
        for group in ('A','B','C'):
            plan=data[group]['plan'];spec=R[case][group];actions={}
            for cat in ('modify','preserve','uncertain','add'):
                items=plan[cat];notes=spec.get(cat,[])
                if len(items)!=len(notes): raise ValueError(f'{case}/{group}/{cat}: expected {len(notes)}, got {len(items)}')
                actions[cat]=[{'index':i,'item_sha256':digest(item),'verdict':verdict,'reason':reason}
                              for i,(item,(verdict,reason)) in enumerate(zip(items,notes))]
            reviewed['groups'][group]={'plan_sha256':digest(plan),'actions':actions}
        out['cases'][case]=reviewed
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('独立逐项核对已保存，5 案 × 3 组；无数据输入规划器。')

if __name__=='__main__':main()
