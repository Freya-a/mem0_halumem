"""Manually authored, hash-bound review, separate from planner input."""
from pathlib import Path
import hashlib,json
import make_report as rpt

# Verdicts concern the *whole* model record, including its scope and temporal
# assertions. Core reflects the factual kernel separately; neither is fed back.
DATA={
'susan':{
 'facts':[
 ('partial','supported','用户称 Susan 的支持十分宝贵；完整 unconditional 适用范围没有独立证明。'),
 ('partial','supported','用户称她的鼓励帮助自己专注目标；单独作用域为 unconditional 缺充分依据。'),
 ('partial','supported','Daniel 的见解促使用户在职业上跳出固有思路；完整无条件范围未证明。'),
 ('partial','partial','用户说这些联系开辟了可能性，但将这些联系明确扩展为 Susan、Daniel 等的完整集合及无条件范围仍是推断。'),
 ('partial','supported','原话明确限定当前岗位和相对本人期望；无条件范围不应理解为永久。'),
 ('partial','supported','用户表达找兼顾平衡与人道目标的工作的计划；new_value 是数组，不符合接口标量，且两个条件没有分为独立记录。')],
 'relations':[
 ('unsupported','unsupported','评价支持珍贵与旧事实“提供支持和鼓励”不是同属性同值的 same；原话无充分依据证明两个状态在完整范围同值。'),
 ('partial','supported','鼓励帮助专注可以补充旧支持事实，但无条件旧范围及跨引文关系仍须核对；模型 supplement 被适配为旧影响 unknown。'),
 ('unsupported','unsupported','把 Susan 支持与 ThomasSusan 朋友关系判为主体完全无重叠不可靠；旧记忆完整原文明示 Susan 称呼，短旧引文不足以支持该结论。'),
 ('unsupported','unsupported','与上一条同理，功能不同不等于主体必然无关；不能单靠短旧引文认证无影响。')],
 'coverage':[
 ('Susan 的支持珍贵','present',['f1'],'结构化事实独立提出，范围仍需核对。'),
 ('Susan 的鼓励帮助专注目标','present',['f2'],'与支持评价已拆开。'),
 ('Daniel 的见解推动职业思考','present',['f3'],'v4 遗漏的 Daniel 独立提出。'),
 ('当前岗位对福祉支持不及期望','present',['f5'],'模型保留 current 和比较限定。'),
 ('寻找兼顾平衡及人道目标的工作计划','partial',['f6'],'有计划，但把两个要求写为数组且未分别独立结构化，接口校验失败。'),
 ('这些联系开辟新可能','partial',['f4'],'模型提出，但对联系集合的完整归属有推断。')],
 'comparison':'v4 未独立输出 Daniel；v5 拆出了支持、鼓励与 Daniel，但计划值仍是数组，两条 unrelated 的主体解释不可靠。旧记忆的身份指代与可编辑范围不能由新事实自动决定。'},
'promotion':{
 'facts':[
 ('partial','supported','话语在晋升语境中明确公司；当时公司关联有依据，持续现职和完整无条件范围不能由此保证。'),
 ('partial','supported','话语支持晋升为 lead director；不要将其无条件推广到所有时间。'),
 ('partial','supported','got promoted 表示发话前已发生晋升；相对旧职位有效时间仍未知，模型值未保留 recently。')],
 'relations':[
 ('partial','partial','两侧出现同公司，但同一时刻和持续雇佣不是单凭公司名与晋升话语可以独立证实；旧关系本身有原文。'),
 ('unsupported','unsupported','recently 相对发话而非旧事实有效时间；lead director 更具体也不证明宽泛 Director 失效。模型 after 和替代理由不足。')],
 'coverage':[
 ('晋升已发生','present',['f3'],'晋升事件单独提出。'),
 ('晋升职位 lead director','present',['f2'],'职位单独提出，但并不能决定旧职位覆盖。'),
 ('公司 Historical Productions Ltd.','present',['f1'],'公司关联有原话，连续雇佣与同一时刻仍需依据。'),
 ('对此晋升感到兴奋','missing',[],'发话包含主观感受，但模型未单独输出。')],
 'comparison':'v4 已提到晋升但错误推断 after 和职位替换；v5 将事件与职位分开并修正公司主体，仍重复作出同样未经支持的职位替换与先后判断。'},
'career_history':{
 'facts':[
 ('unsupported','unsupported','my consulting firm 与获客不证明用户是创办者、所有者或该公司的当前雇员。'),
 ('unsupported','unsupported','已选 new-0 引文并未说 political consulting；理由援引其他未选来源，不能借其作为该条证据。'),
 ('partial','partial','两名联系人及其关系打开机会有用户引文；合并两人，且“为公司打开”较原话更具体，未分别结构化。'),
 ('partial','supported','用户说正专注维系这些关系并认为其对公司增长重要；客观上是否确实重要及无条件范围未独立证明。')],
 'relations':[
 ('unsupported','unsupported','新事实本身的创办/所有者身份无依据，获客不证明更换雇主；旧历史本身不应删除。语义依据还引用了不在绑定旧短引文中的 Previously worked。'),
 ('unsupported','unsupported','新身份无依据；过去 senior developer 并不与新活动必然互斥，也未证明顺序或替换。所引旧时间依据未绑定，新侧时间依据缺失。')],
 'coverage':[
 ('用户所称咨询公司获得初始客户','missing',[],'事件仅出现在 f1、f2 的引文和理由中；结构化 value 是身份或领域，缺独立获客事实。'),
 ('用户因此感到宽慰与重要里程碑','missing',[],'引文存在但未独立形成事实。'),
 ('两位联系人及其关系打开机会','partial',['f3'],'两个人及其作用被合并，且为公司打开的限定比原句更具体。'),
 ('关注维系这些关系以支持公司增长','present',['f4'],'模型保留当前关注；重要性是用户主张。'),
 ('用户为创办者或所有者','unsupported',['f1'],'模型有此事实但引文不能证明，不可当作正确提取。')],
 'comparison':'v4 也把获客扩展为角色/雇主变化；v5 仍未将获客作为结构化事实，继续推断创办/所有者并引入所选引文没有的领域；联系人新增仍合并主体。'},
'transition':{
 'facts':[
 ('unsupported','unsupported','原话说转到新职位，没有说不再求职；宽慰也不证明原先求职压力已消失。'),
 ('partial','supported','用户说现在工作和生活平衡更健康；时间限定 now 有依据，unconditional 不宜扩大到其他时段。')],
 'relations':[
 ('unsupported','unsupported','已转岗不证明停止求职；finally 只确认转岗相对话语完成，不证明晚于旧记忆事实有效时间。'),
 ('unsupported','unsupported','平衡更健康不证明旧目标已完全实现或应被替换；now 也不独立证明相对旧目标的有效时间先后。')],
 'coverage':[
 ('已转到新职位','missing',[],'原话在 f1 引文，模型结构化值却变成 no longer searching，不能当作正确的已转岗事实。'),
 ('转岗带来宽慰','missing',[],'原话提到 relief，模型未独立输出；不能将原因扩展为求职结束。'),
 ('现在工作与生活的平衡更健康','present',['f2'],'单独提出并保留 now。'),
 ('已经停止求职','unsupported',['f1'],'这是模型推断，原话没有确认。')],
 'comparison':'v4 把转岗与平衡写在合并值中并暗示状态替换；v5 虽拆出平衡，反而将转岗候选结构化成未被证实的停止求职，关系 after 仍缺依据。'},
'skydiving':{
 'facts':[
 ('partial','supported','明确是最近团队活动中的模拟跳伞，不自动代表真实跳伞；unconditional 的完整范围未证实。'),
 ('partial','supported','用户明确觉得这次模拟体验刺激；不能从一次体验外推真实偏好或其他时间。'),
 ('partial','supported','用户说没想到会如此享受肾上腺素；理由声称原先预期完全不享受，比原话更强。'),
 ('partial','supported','用户说更愿尝试新事物；不应扩大为真实极限运动喜好改变。'),
 ('partial','supported','用户明确说仍优先考虑安全；该句未确认完整旧因果关系或所有时间。'),
 ('partial','supported','用户说目前享受刺激并观察后续；理由关于长期参与刺激活动的解释超出原话。')],
 'relations':[
 ('unsupported','unsupported','模拟体验与真实极限运动的旧态度之间影响未知；低风险及 after、旧事实有效时间由模型补推。'),
 ('unsupported','unsupported','选择模拟活动不证明用户认为其低风险，亦不独立证明旧受伤风险原因继续或消失；after 缺相对旧状态依据。'),
 ('partial','partial','当前仍优先安全有依据，但不能据此确认旧陈述中的完整安全与福祉因果、同一有效时间或无条件范围。'),
 ('unsupported','unsupported','觉得模拟体验刺激不证明真实跳伞厌恶消失；模型把正面体验与旧普遍偏好视为互斥缺依据，after 亦不成立。'),
 ('unsupported','unsupported','更愿尝试新事物不证明真实极限运动偏好改变；模型自行推断覆盖该领域和相对旧状态先后。')],
 'coverage':[
 ('近期团队活动中尝试模拟跳伞','present',['f1'],'模拟限定和活动上下文均保留。'),
 ('这次模拟体验刺激','present',['f2'],'与尝试事件分开，不等同真实偏好。'),
 ('肾上腺素体验超出预期','present',['f3'],'值受原话支持，但其理由把预期夸大为完全不享受。'),
 ('更愿意尝试新事物','present',['f4'],'独立记录；不证明真实极限运动偏好。'),
 ('仍优先考虑安全','present',['f5'],'独立记录；不证明旧受伤风险原因。'),
 ('目前享受刺激并观察后续','present',['f6'],'有原文，但长期参与活动的理由是推测。')],
 'comparison':'v4 将模拟体验与开放态度合并；v5 成功单独列出模拟活动、刺激、开放及安全，但仍多次把体验或开放推断为真实极限运动偏好变化，且错误推断相对旧事实 after。'}
}

def main():
 target=Path('HUMAN_REVIEW.json')
 if target.exists():raise FileExistsError('existing independent review must not be overwritten')
 cases={}
 for case,review in DATA.items():
  a=rpt.load(rpt.RUN/(case+'.json'));p=(a.get('result') or {}).get('parsed')
  if not isinstance(p,dict):raise ValueError('cannot apply prepared review to missing model response')
  entry={'raw_sha256':hashlib.sha256(a['raw_response'].encode()).hexdigest(),'facts':[],'relations':[],
         'coverage':[{'target':x[0],'verdict':x[1],'fact_ids':x[2],'reason':x[3]} for x in review['coverage']],
         'comparison':review['comparison']}
  for section in ('facts','relations'):
   if len(p[section])!=len(review[section]):raise ValueError(f'{case} {section} review count mismatch')
   for model,annotation in zip(p[section],review[section]):
    entry[section].append({'sha256':rpt.digest(model),'verdict':annotation[0],
                           'core_verdict':annotation[1],'reason':annotation[2]})
  cases[case]=entry
 target.write_text(json.dumps({'method':'研究者依据原始所选用户话语、旧记忆及既有审核，逐条独立核对；不是模型自评或用户确认金标准。verdict 衡量整条判断；core_verdict 单独记录事实内核。结果未回填规划器。','cases':cases},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('independent review saved',len(cases),'cases')
if __name__=='__main__':main()
