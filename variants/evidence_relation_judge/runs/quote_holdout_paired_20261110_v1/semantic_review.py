"""Freeze analyst's preliminary comparison; nothing here is a human label."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
comparison=json.loads((P/'comparison.json').read_text())
notes={
(1,'*'):('两版均保留拉布拉多旧喜好，金毛为兼容新增；实验版后句“可能喜欢”可能比用户已表达的新偏好更谨慎，但前句也提到新偏好，是否构成弱化待审。','无明确退化，需复核'),
(3,'*'):('部分目标输入：寻求导师的原话未传入。两版均把支持医疗可及性的愿望与旧记忆的“首要”动机联系起来，但新引文未单独证明首要排序；非营利计划与支持兼新增的标签边界待审。','证据范围不完整；新证据是否证明首要性待审'),
(4,'*'):('两版均引用 Susan 对目标的支持；新求职情境是否构成实质新增与 support 定义有张力。实验版未带旧版的 personal/professional 条件，不能仅据此认定丢失旧事实。','支持兼新增边界待审'),
(5,'*'):('v2 的影响片段来自旧上下文而非旧记忆导致校验失败；实验版使用整条旧记忆，格式通过。两版理由均把 Daniel 的职业见解写成确认其同事身份或专业能力的持续性，新证据不单独重申身份和医疗咨询专业。','候选片段来源改善；两版新证据支持范围可能过强'),
(6,'*'):('新引文只说 Joshua 的 approach，旧上下文曾描述协作方法。实验版写成新证据确认“协作方法”，比 v2 的“方法积极影响”更具体；两句话是否指同一方法依赖跨上下文衔接，待审。','实验版条件具体化风险；需核验指代'),
(9,'*'):('两版均输出 support，保留旧的历史/传统理由；本次茶馆经历和对层次风味欣赏加深亦为给定新信息，support 与补充如何消歧待审。','支持兼新增边界待审'),
(12,'*'):('两版均保留旧压力可能发生变化而不断言消失；v2 理由说“学会授权”，原文只说有能力委派，实验版“能够委派”更贴近原文。是否完全消除具体旧压力源仍未确认。','v2 增加学习过程，实验版此点较谨慎'),
(13,'*'):('两版均由给定整体压力改善讨论旧压力；v2 问“主要原因”高于旧事实列出两个原因的强度，实验版问是否仍有具体压力更聚焦。工作生活平衡与减压归因仍应分开。','v2 追问增加主要性；范围待审'),
(15,'*'):('两版记载 Mary/Steven 的支持和新网络，但把该证据称为确认旧记忆“主要支持系统”，新引文体现支持并不单独证明主要排序；新网络是否纳入特定审核范围仍未固定。','两版新引文对主要性支持不足'),
(16,'*'):('两版都注意用户说偏好转变并未断言旧偏好完全消失；实验版追问“仍然喜欢所有古典交响乐，还是完全转向巴洛克”，旧文并未声称喜欢所有作品，且两选项过窄。巴洛克与古典交响乐不必互斥。','实验版新增全称/二选一前提风险'),
(17,'*'):('部分目标输入：已联络专业人士和参加研讨会的原话未传入。两版说仅处思考/意愿，可能弱化完整目标中的实际推进，但不能要求模型使用未提供的信息；仅据输入内容观察。','证据范围不完整；不归咎模型遗漏'),
(18,'*'):('部分目标输入：“关键顾问”为设想的原话未传入；两版均对离职或职业变化保留疑问，未断言转型完成。与原五例职业历史共用 ID，但这是更早快照的 Works 文本。','证据范围不完整；不归咎模型遗漏'),
(19,'*'):('两版区分收入可能变化，但都问是否离职“导致月收入变零”，提问可能预设零收入已发生及因果关系；新证据只说转型初期无即时收入，月度口径及生效日期未知。v2 还称旧状态是过去，缺少明确有效期。','两版提问存在时间/因果前提风险'),
(21,'*'):('部分目标输入：学习与竞选责任负担的原话未传入；两版均记录转型压力影响心理健康，均问是否需要医疗干预。该问题没有断言存在诊断或需要干预，但引入材料未提及的临床框架，必要性待审。','证据范围不完整；两版额外追问待审'),
(22,'37756be3-aaee-4e1c-b8f7-a5fed3d94890'):('Sandra：两版均把两人共同提供支持和建议的原句写成 Sandra 本人提供战略建议；人工边界仅确认集体支持，不能把每一项贡献分配给每个人。','两版集体贡献转个体风险'),
(22,'98c6916c-8aa9-4560-94ce-5697f39ac818'):('Mary：两版均将二人共同支持和战略建议写作 Mary 本人提供战略建议，且据此支持讨论政治策略；原句不逐项分配贡献，语义支持待审。','两版集体贡献转个体风险'),
(23,'37756be3-aaee-4e1c-b8f7-a5fed3d94890'):('Sandra：v2 的候选片段来自旧上下文导致校验失败；实验版将片段留空（这是允许的不定位，不能算已成功定位）。实验版把“我的人脉，包括 Sandra 和 Mary”写成“利用 Sandra 的人脉”，新原文未说人脉属于 Sandra，也未确认她已引荐。','实验版避免越源但未定位；新增人脉归属风险'),
(23,'98c6916c-8aa9-4560-94ce-5697f39ac818'):('Mary：两版都从计划利用包括 Mary 在内的人脉推及关系或角色延续；计划本身不证明 Mary 已同意引荐或实际帮助。','两版计划与实施边界待审')}
rows=[]
for unit in comparison['rows']:
 n=unit['record'];key=(n,unit['memory_id']) if n in (22,23) else (n,'*');comment,kind=notes[key]
 a=unit['versions']['v2']['facts'][0];b=unit['versions']['experimental']['facts'][0]
 rows.append({'record':n,'memory_id':unit['memory_id'],'v2_status':a['status'],'experimental_status':b['status'],'v2_relation':(a['candidate'] or {}).get('relation'),'experimental_relation':(b['candidate'] or {}).get('relation'),'coverage':'partial_target_evidence' if n in {3,17,18,21} else 'full_target_initial_screen','error_class':kind,'analysis':comment,'relation_semantics':'pending_human_review','analysis_author':'assistant_initial_screen_not_human_label'})
with (P/'semantic_review.json').open('x',encoding='utf8') as f:json.dump(rows,f,ensure_ascii=False,indent=2);f.write('\n')
lines=['# 逐子事实语义初筛','','以下为助理依据给定输入及已有人工事实边界的初步观察，**全部待人工审核**；不作为标签盲标或错误率。逐字引文匹配不证明引文支持理由。第 3、17、18、21 条目标证据范围不完整，不能用模型未见证据评分。','', '|记录 / 旧记忆|v2|实验版|初步错误分类及比较|','|---|---|---|---|']
for r in rows:
 mid=r['memory_id'];v=f"{r['v2_relation']} / {r['v2_status']}";e=f"{r['experimental_relation']} / {r['experimental_status']}"; lines.append(f"|{r['record']} / `{mid}`|{v}|{e}|{r['analysis']}|")
(P/'SEMANTIC_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('preliminary pair reviews',len(rows),'all pending human review')
