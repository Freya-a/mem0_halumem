"""Author the separate, human-reviewed decomposition; never planner input."""
import json
from pathlib import Path
import replay

# Each entry audits a previously emitted B action. 'extractability' describes
# the saved model structure, not whether an assertion is true.
REVIEWS=[
('susan','add',0,[
 ('supported','Susan 的支持被说成很有价值',"Susan's support has indeed been invaluable.",'combined','值与理由含此内容，但和帮助专注合并；要独立结构化需拆分。'),
 ('supported','她的鼓励帮助用户专注目标','Her encouragement helps me stay focused on my goals.','combined','已有模型值/理由包含该事实，但并非独立记录。'),
 ('unresolved','完整无条件适用范围及旧支持关系是否受影响',"Susan's support has indeed been invaluable.",'unsupported_relation','模型写 unconditional；引文不足以确立完整范围或旧事实同一关系。')]),
('susan','add',1,[
 ('supported','用户当时认为当前岗位对福祉的支持不如期望',"my current role isn't supporting my well-being as much as I'd like",'atomic','模型已有独立 new_information 值，但应保持 current 与相对期望限定。'),
 ('extension','该评价适用于所有岗位或所有时间',"my current role isn't supporting my well-being as much as I'd like",'not_asserted','这是需要排除的扩展；原模型未单独声称所有岗位或永远如此。')]),
('promotion','modify',0,[
 ('supported','发话时用户已晋升为 lead director','I recently got promoted to lead director','combined','模型 new_value 给出 lead director，事件也写在理由；晋升事件并非独立记录。'),
 ('supported','新话语将该职位与 Historical Productions Ltd. 联系起来','at Historical Productions Ltd.','combined','公司和职位同时出现于引文与模型说明；主体需从话语明确为用户。'),
 ('unresolved','该晋升是否晚于旧记忆所描述的职位有效期','I recently got promoted','unsupported_relation','模型明确写 after；recently 仅确定相对话语发生，不能证明相对旧状态的先后。'),
 ('unresolved','旧 Director 是否因此不再成立','I recently got promoted to lead director','unsupported_relation','模型声称 supersedes，但宽泛职位称谓可能仍成立，现有字段不能证明替代。')]),
('career_history','add',0,[
 ('supported','用户所称咨询公司获得了首批客户','my consulting firm finally secured some initial clients','quote_or_rationale','模型引文和语义理由提及获客，但 new_value 是公司而非获客事件；要独立结构化需重新拆分。'),
 ('extension','用户当前以该咨询公司为雇主或为公司的所有者','my consulting firm finally secured some initial clients','unsupported_relation','模型的 current employer / business ownership 是有依据不足的关系；my 不足以确定所有权或雇佣。'),
 ('unresolved','用户是否已结束 Blockchain Tech 旧工作','my consulting firm finally secured some initial clients','unsupported_relation','模型推断工作互斥和转变；获客不证明离职或新旧关系先后。')]),
('career_history','add',1,[
 ('supported','用户所称咨询公司获得了首批客户','my consulting firm finally secured some initial clients','quote_or_rationale','原模型理由和引文包含事件，结构化 new_value 却是职位；需要重新拆分。'),
 ('extension','用户是咨询公司的创办者或经营者','my consulting firm finally secured some initial clients','unsupported_relation','模型明确提出 founder/operator，但引文没有证明。'),
 ('unresolved','新活动是否替代此前 senior developer 职位','my consulting firm finally secured some initial clients','unsupported_relation','模型推断替代；没有独立事实证明职位互斥或有效时间。')]),
('transition','add',0,[
 ('supported','用户表示现在工作与个人生活平衡更健康','The balance between work and personal life is much healthier now.','combined','模型值与理由包含改善，但和旧目标实现合并；应分为独立新断言。'),
 ('extension','原来的求职平衡目标已完全实现','The balance between work and personal life is much healthier now.','unsupported_relation','模型标为 realized；更健康不证明达到旧目标或所有目标已实现。'),
 ('unresolved','更健康状态与旧目标之间的对应及持续性','The balance between work and personal life is much healthier now.','not_asserted','需要更多证据；原话没有独立确认目标实现和持续时间。')]),
('transition','add',1,[
 ('supported','用户说自己已经转到新职位',"I've finally transitioned to a new role",'combined','模型 new_value 合并了转岗与平衡改善；要单独表示事件需拆分。'),
 ('supported','用户说现在工作与生活的平衡更健康','The balance between work and personal life is much healthier now.','combined','该事实与转岗合在同一 new_value，不能把整个 job search status 当成独立事实。'),
 ('unresolved','转岗后用户是否已经停止求职',"I've finally transitioned to a new role",'unsupported_relation','模型以 job search status 和 successful transition 推断替换，原话并未说停止求职。'),
 ('unresolved','转岗相对旧求职事实有效时间是否更晚',"I've finally transitioned to a new role",'unsupported_relation','finally 相对话语表示转岗完成，不证明相对旧事实的先后。')]),
('skydiving','add',0,[
 ('supported','用户尝试了模拟跳伞并认为刺激','I tried simulated skydiving. It was quite thrilling!','quote_or_rationale','相关引文在原记录 1；该动作的 new_value 却不是体验事实；原记录 0 合并表达了模拟体验。'),
 ('supported','用户仍然优先考虑安全','I still prioritize safety, of course.','combined','原记录 1 的 new_value 将此与另一个无依据判断合并；不能把整值视为已证实。'),
 ('extension','旧受伤风险现在不再是障碍','I still prioritize safety, of course.','unsupported_relation','模型写 not stated as current barrier；没有再次提及并不证明原理由已消失。'),
 ('unresolved','模拟体验是否改变真实极限运动偏好','I tried simulated skydiving. It was quite thrilling!','unsupported_relation','模型另条 change 声称态度变化，模拟与真实活动不能自动等同。')]),
]

# Additional earlier deferred B candidate: it was not an add/modify action but
# is essential to the requested simulated-vs-real decomposition.
EXTRA={'case':'skydiving','record_index':0,'subfacts':[
 ('supported','用户尝试模拟跳伞并觉得刺激','I tried simulated skydiving. It was quite thrilling!','combined','模型 new_value 有该内容但与更愿尝新合并，属性却是极限运动态度。'),
 ('supported','用户表示更愿尝试新事物',"It's definitely made me more open to trying new things.",'combined','模型 new_value 含该内容；要保留新事物范围须单独拆分，不能换成真实极限运动偏好。'),
 ('unresolved','真实极限运动或真实跳伞偏好是否改变','I tried simulated skydiving. It was quite thrilling!','unsupported_relation','模型 change 把模拟体验联系到旧真实极限运动偏好；引文不足以确定该关系。')]} 

def describe(items,record):
    linked=record.get('new_quotes',[])
    output=[]
    for kind,claim,excerpt,extractability,explanation in items:
        matches=[{'source_id':q['source_id'],'quote':q['quote']} for q in linked if excerpt in q.get('quote','')]
        if not matches:raise ValueError(f'excerpt not in linked model quotation: {claim}: {excerpt}')
        output.append({'kind':kind,'claim':claim,'verbatim_excerpt':excerpt,'linked_quotations':matches,
                       'extractability':extractability,'explanation':explanation})
    return output

def main():
    target=replay.HERE/'MANUAL_SUBFACTS.json'
    if target.exists():raise FileExistsError('human review exists; do not silently overwrite or rebind')
    old_audit=replay.read(replay.PRIOR/'AUDIT.json');results=[]
    for case,category,index,items in REVIEWS:
        old=replay.read(replay.PRIOR/'results'/(case+'.json'))
        action=old['B']['plan'][category][index]
        binding=old_audit['cases'][case]['groups']['B']['actions'][category][index]
        if replay.cmp.digest(action)!=binding['item_sha256']:raise ValueError('prior human audit hash mismatch')
        model_index=int(action['note'].split('model_record=')[1].split(';')[0])
        record=old['raw_model_output']['records'][model_index]
        results.append({'case':case,'prior_category':category,'prior_index':index,'prior_action_sha256':binding['item_sha256'],
                        'prior_audit_verdict':binding['verdict'],'prior_audit_reason':binding['reason'],
                        'model_record_index':model_index,'subfacts':describe(items,record)})
    old=replay.read(replay.PRIOR/'results'/(EXTRA['case']+'.json'))
    rec=old['raw_model_output']['records'][EXTRA['record_index']]
    extra={'case':EXTRA['case'],'record_index':EXTRA['record_index'],'record_sha256':replay.cmp.digest(rec),
           'subfacts':describe(EXTRA['subfacts'],rec)}
    payload={'provenance':'研究者基于原始引用和既有审核逐项拆分；非模型输出、非用户确认金标准；不输入规划器。',
             'extractability_definitions':{
               'atomic':'模型有对应独立结构化记录，但其语义仍须独立审核',
               'combined':'模型在合并值或理由中明确表述，但没有可靠独立结构化子记录',
               'quote_or_rationale':'仅在引文或理由中出现，结构化值和属性未表达该子事实',
               'unsupported_relation':'模型输出该关系，但依据不足以认定正确',
               'not_asserted':'该扩展或未知关系并非模型单独输出的可靠事实'},
             'reviews':results,'extra_review':extra}
    target.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('reviewed prior actions',len(results),'plus one deferred record')

if __name__=='__main__':main()
