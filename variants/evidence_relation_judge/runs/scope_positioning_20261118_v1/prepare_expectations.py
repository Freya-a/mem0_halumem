import json
from pathlib import Path
p=Path(__file__).resolve().parent

def E(text,*refs): return {'scope':text,'evidence':[{'source_id':sid,'quote':q} for sid,q in refs]}
spec={
'susan':{
'old_statement':'Martin 有 ThomasSusan（称 Susan）这一朋友，提供支持和鼓励。',
'new_statement':'Martin 正寻找更平衡的工作；同一会话称 Susan 的支持与鼓励帮助其保持目标专注。两句话的求职情境关联沿用已审核目标，但不归因 Daniel 的贡献。',
'modify':[E('无证据要求删除或替换旧朋友关系／旧支持；如表达新的求职情境，可在原支持上补充，具体存储方式待确认。',('old',"Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"),('new-2',"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."))],
'preserve':[E('保留朋友身份、Susan 的支持与鼓励，不改写为仅在本次求职中存在。',('old',"Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"))],
'uncertain':[E('旧支持开始/结束时间、是否专属求职、ThomasSusan 名字的真实构成均未知；不能确定接受 offer 或完成转岗。',('old',"Has a friend named ThomasSusan (referred to as 'Susan') who provides support and encouragement"),('new-0',"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."))],
'add':[E('候选独立新增：Susan 的支持、鼓励帮助用户保持目标专注的求职情境；原关系与新增情境可合并或分开，不自动判定必须写一条。',('new-0',"It's crucial for me to find a new job that offers a better work-life balance and aligns with my humanitarian goals."),('new-2',"Susan's support has indeed been invaluable. Her encouragement helps me stay focused on my goals."))]},
'promotion':{
'old_statement':'Williams 在 Historical Productions Ltd. 担任 Director。',
'new_statement':'用户自述最近升为同一公司的 lead director。',
'modify':[E('职位局部应作为同次晋升的旧具体职称进行历史化候选；不据此修改公司；如何表示历史及准确边界待确认。',('old','Works at Historical Productions Ltd. as a Director'),('new-0','I recently got promoted to lead director at Historical Productions Ltd.'))],
'preserve':[E('保留 Historical Productions Ltd. 雇主及旧 Director 的历史事实。',('old','Works at Historical Productions Ltd. as a Director'),('new-0','I recently got promoted to lead director at Historical Productions Ltd.'))],
'uncertain':[E('准确晋升生效日、旧职位失效日及完整有效期未知；不把发言记录日充当事件日。',('new-0','I recently got promoted to lead director at Historical Productions Ltd.'))],
'add':[E('候选独立新增：在该公司升为 lead director，保留 recently。',('new-0','I recently got promoted to lead director at Historical Productions Ltd.'))]},
'career_history':{
'old_statement':'Donald 曾在 Blockchain Tech 担任 senior developer；旧原话在较早来源中为当时现在时。',
'new_statement':'用户表示咨询公司获得一些首批客户、感到宽慰并视为里程碑；另称 MooreSandra、GonzalezMary 的人脉提供了集体帮助。',
'modify':[E('新获客证据未推翻旧技术职业历史；无证据要求修改或删除这条旧职业事实。',('old','Previously worked as a senior developer in Blockchain Tech'),('new-0','my consulting firm finally secured some initial clients'))],
'preserve':[E('保留曾任 senior developer 及 Blockchain Tech 两项职业历史，不把职业细节泛化掉。',('old','Previously worked as a senior developer in Blockchain Tech'))],
'uncertain':[E('旧岗位准确开始/结束时间、获客日、客户数和身份未知；获客不证明之前没有客户，也不证明具体当前雇佣身份。',('old','Previously worked as a senior developer in Blockchain Tech'),('new-0','my consulting firm finally secured some initial clients'))],
'add':[E('候选独立新增：公司已获一些首批客户、用户因此感到宽慰并视为里程碑。',('new-0',"I've been feeling quite relieved lately because my consulting firm finally secured some initial clients. It's a significant milestone for me.")),E('候选另记：MooreSandra 与 GonzalezMary 的人脉作用按集体归因，不把具体行动分别安给每人。',('new-2','MooreSandra and GonzalezMary were indeed instrumental. Their connections opened doors I couldn\'t have imagined.'))]},
    'transition':{
'old_statement':'Martin 正寻找更有工作生活平衡的新工作。',
'new_statement':'用户称已完成转到新岗位，工作生活平衡更健康。',
'modify':[E('已审核的同次转岗进度可提出旧求职阶段历史化候选；不推出今后不再寻找其他机会。',('old','Looking for a new job with better work-life balance'),('new-0',"I've finally transitioned to a new role"))],
'preserve':[E('保留此前寻找更平衡工作的历史与工作生活平衡诉求。',('old','Looking for a new job with better work-life balance'))],
'uncertain':[E('转岗具体日期、新雇主、新职称、组织性质及是否离开旧公司未知；新旧描述属于同一转岗的映射来自既有审核，具体存储决策待确认。',('new-0',"I've finally transitioned to a new role"),('old','Looking for a new job with better work-life balance'))],
'add':[E('候选独立新增：用户自述完成新岗位转变，工作生活平衡更健康。',('new-0',"I've finally transitioned to a new role, and it's been a huge relief. The balance between work and personal life is much healthier now."))]},
'skydiving':{
'old_statement':'Martin 不喜欢极限运动，包括跳伞；旧记忆给出受伤风险与安全健康原则的关系。',
'new_statement':'用户近期尝试并享受模拟跳伞，因此更愿意尝试新事物，并表示仍优先考虑安全。',
'modify':[E('不要求以模拟体验覆盖或否定整个旧风险理由；旧泛化的当前适用范围需要具体限定，修改方案待确认。',('old','Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being'),('new-0','I tried simulated skydiving'))],
'preserve':[E('保留旧高受伤风险、安全健康承诺及其历史语境，不将旧偏好无条件视为当前适用。',('old','Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being'),('new-8','I still prioritize safety, of course.'))],
'uncertain':[E('真实跳伞当前态度、模拟体验准确日期及旧广泛偏好当前范围未知；模拟活动不等同于真实跳伞。',('new-0','I tried simulated skydiving'),('old','Dislikes extreme sports (e.g., skydiving)'))],
'add':[E('候选独立新增：近期团建尝试模拟跳伞并觉得刺激。',('new-0','Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!')),E('候选独立新增：用户意外享受肾上腺素感，并更愿意尝试新事物。',('new-2',"the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.")),E('保留当前陈述：目前仍将安全放在首位；与旧安全原则可能重复，需去重。',('new-8','I still prioritize safety, of course.'))]}}
for name,expected in spec.items():
 d=p/'cases'/name;c=json.loads((d/'input.json').read_text());req=c['request'];texts={'old':req['split_result']['memory_text']};texts.update({x['source_id']:x['text'] for x in req['new_evidence']});texts.update({x['source_id']:x['text'] for x in req['source_context']})
 for cat in ('modify','preserve','uncertain','add'):
  for item in expected[cat]:
   for ref in item['evidence']:
    assert ref['source_id'] in texts and ref['quote'] in texts[ref['source_id']],(name,cat,ref)
 expected['status']='助手依据原文和已确认审核边界整理的候选预期，非用户确认金标准'
 expected['time_policy']='实际生效/失效边界和条件，如无原文明示均为 unknown；来源 recorded_at 不作为有效日期。'
 with (d/'expected.json').open('x',encoding='utf-8') as f:json.dump(expected,f,ensure_ascii=False,indent=2);f.write('\n')
 print(name,'quotes verified')
