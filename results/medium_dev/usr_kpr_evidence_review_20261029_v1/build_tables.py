import json,csv,re,collections,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
BASE=D.parent/'williams_native_prefix5_20261028_v3'/'development_diagnosis_v1'
obs=json.loads((BASE/'protection_observations.json').read_text())
dec={x['number']:x for x in json.loads((BASE/'target_decisions.json').read_text())['targets']}
evi={i:json.loads((BASE/f'target_{i:02}_evidence.json').read_text()) for i in range(1,25)}
primary={1,3,4,7,8,9,10,11,12,13,14,16,17,18,19,21,22,23,24}
user=lambda n: 'Martin' if n<=8 else 'Williams' if n<=16 else 'Donald'
link=lambda n:f'../williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_{n:02}_evidence.json'
esc=lambda x:str(x).replace('|','\\|').replace('\n','<br>')
source=lambda n,idx:f'{link(n)}（`review.candidate_protections[{idx-1}]`；`before` / `after`）'
# Conservative, individually defined atomic facts. Match the text of complete propositions and
# independently assert that required memory strings occur in both snapshots.
def select(x):
 p=x['proposition']; n=x['target_number']; owner=user(n)
 exact={
 'Martin喜欢猫':('Martin喜欢猫',['Likes cats because']),
 'Martin喜欢鹦鹉':('Martin喜欢鹦鹉',['Likes parrots because']),
 'Martin不喜欢蛇等爬行动物':('Martin不喜欢蛇等爬行动物',['Dislikes reptiles, like snakes']),
 'Martin’s highest education is Bachelor in Public Health.':('Martin最高学历Bachelor，专业Public Health',['Highest education level is Bachelor','Major is Public Health']),
 'Martin’s father is a retired doctor.':('Martin父亲是退休医生',['retired doctor']),
 'Martin describes his physical condition as normal with no chronic diseases.':('Martin身体状况正常且无慢性病',['Physical condition is normal, no chronic diseases']),
 'Williams’s highest education is Bachelor in Film Studies.':('Williams最高学历Bachelor，专业Film Studies',['Highest education level is Bachelor','Major is Film Studies']),
 'Williams’s father is a retired history professor.':('Williams父亲是退休历史教授',['retired history professor']),
 'Williams likes 1920s jazz for its historical and cultural significance.':('Williams喜欢1920年代爵士乐及其历史文化意义',['1920s jazz']),
 'Donald’s highest education is Master in Political Science.':('Donald最高学历Master，专业Political Science',['Highest education level is Master','Major is Political Science']),
 'Donald has two children.':('Donald有两个孩子',['Has two children']),
 'Donald describes his physical condition as normal with no chronic diseases.':('Donald身体状况正常且无慢性病',['Physical condition is normal with no chronic diseases']),
 }
 # Additional individually checked full candidate propositions and their exact supporting text.
 by_id={
 (3,1):'Primary career motivation is improving healthcare access for underserved communities',
 (3,4):'Current role is Director at Huaxin Consulting',
 (3,5):'Financial stability is secondary to humanitarian goals and personal well-being',
 (10,1):'Works at Historical Productions Ltd. as a Director',
 (10,2):'Is a filmmaker',
 (11,4):'Works at Historical Productions Ltd. as a Director',
 (8,6):'Dislikes boxing due to its aggressive nature and potential for physical harm',
 (8,7):'Dislikes wrestling because finds it too confrontational and prefers sports emphasizing teamwork and personal growth',
 (8,8):'Dislikes automobile racing due to environmental impact and lack of physical engagement',
 (9,2):'Dislikes energy drinks because they are too sweet, artificial, and lack authenticity and historical roots',
 (9,3):'Dislikes bubble tea because of the unappealing texture of tapioca pearls and its overly commercialized nature',
 (14,2):'Dislikes parrots because of their constant noise and chatter',
 (14,3):'Likes greyhounds because of their noble history and gentle demeanor, fitting for a soothing lifestyle',
 (14,4):'Likes tortoises because their slow, deliberate movements symbolize the passage of time and history',
 (14,5):'Likes British Shorthair cats because of their calm, collected nature and historical charm',
 (16,1):'Likes classical symphonies because of their complexity, historical significance, and authentic auditory experience',
 (16,3):'Dislikes auto-tuned pop music because it lacks authenticity and depth',
 }
 term=by_id.get((n,x['candidate_index']))
 if term and all(any(term in v for v in snap.values()) for snap in (x['before_matches'],x['after_matches'])):
  fact = 'Williams在Historical Productions Ltd.工作' if (n,x['candidate_index']) in [(10,1),(11,4)] else p
  return fact,[term]
 if p in exact:
  fact,need=exact[p]; b=x['before_matches']; a=x['after_matches']
  if all(any(t.lower() in v.lower() for v in b.values()) and any(t.lower() in v.lower() for v in a.values()) for t in need):
   return fact,need
 return None
# Explicit contextual duplicates beyond identical propositions: not silently merged.
manual_groups={(3,1):'Martin-医疗可及性目标',(2,4):'Martin-医疗可及性目标',(3,2):'Martin-建立全球健康倡议',(2,5):'Martin-建立全球健康倡议',(7,11):'Martin-建立全球健康倡议及医疗可及性（复合，部分重叠）',(8,3):'Martin-瑜伽柔韧与思维清晰',(8,4):'Martin-瑜伽柔韧与思维清晰',(1,6):'Martin-瑜伽柔韧与思维清晰',(21,4):'Donald-支持亲属政治事业目标',(21,5):'Donald-支持亲属政治事业目标',(17,1):'Donald-支持亲属政治事业目标',(18,4):'Donald-支持亲属政治事业目标',(20,4):'Donald-支持亲属政治事业目标',(22,1):'Donald-Sandra旧关系',(23,1):'Donald-Sandra旧关系',(24,4):'Donald-Sandra旧关系（部分重叠）',(22,2):'Donald-Mary旧关系',(23,2):'Donald-Mary旧关系',(24,5):'Donald-Mary旧关系（部分重叠）',(17,4):'Donald-Blockchain Tech高级开发历史',(18,1):'Donald-Blockchain Tech高级开发历史',(20,1):'Donald-Blockchain Tech高级开发历史',(24,2):'Donald-职业、收入、储蓄（复合；见拆分表）'}
groups=collections.defaultdict(list)
for x in obs:
 k=(x['target_number'],x['candidate_index']); s=select(x)
 key=manual_groups.get(k,(s[0] if s else user(k[0])+'-'+x['proposition'].strip()))
 groups[key].append(f'{k[0]}/{k[1]}')

def prot_evidence(n,idx):
 try:
  a=json.loads(evi[n]['review']['candidate_protections']); item=a[idx-1]
  ev=item.get('evidence',{}); ptr=ev.get('json_pointer') or item.get('evidence_json_pointer',''); quote=ev.get('quote',''); date=ev.get('timestamp') or item.get('evidence_timestamp','')
  return ptr,date,quote
 except (ValueError,IndexError,TypeError):return '','',''
def refs(vals,terms=None):
 items=[(k,v) for k,v in vals.items() if terms is None or any(t.lower() in v.lower() for t in terms)]
 return '<br>'.join(f'`{k}` {esc(v)}' for k,v in items) or '未定位（不能据此断言完整快照不存在）'

lines=['# USR 核验表：19 个主目标','', '冻结审核限定的是证据与目标，并未人工确认运行结果。新证据列逐字摘录目标证据文件中 `original_target.new_dialogue_evidence`；预期核心取冻结审核 `review.supported_new_state`。after 列为原诊断选出的相关记忆，完整快照见每项目标 JSON 的 `after`。所有现有运行后语义判断仍需人工核对。','', '|编号 / 用户 / 冻结范围|新证据（原始会话 JSON pointer，0 起始）|预期核心|更新后相关记忆（ID / 文本）|现有判断、严格核验与限制|证据|','|---|---|---|---|---|---|']
for n in sorted(primary):
 x=evi[n]; d=dec[n]; r=x['review']; new=x['original_target'].get('new_dialogue_evidence',[])
 # Include frozen core evidence that was added during human review (e.g. target 18 dialogue/24).
 try:
  core=json.loads(r.get('core_evidence') or 'null')
  for c in (core if isinstance(core,list) else [core] if isinstance(core,dict) else []):
   z=c.get('evidence',{})
   if z.get('quote') and not any(t.get('json_pointer')==z.get('json_pointer') for t in new): new.append(z)
 except (ValueError,TypeError): pass
 news='<br>'.join(f'`{z.get("json_pointer","")}` [{z.get("role","")}] {esc(z.get("quote",""))}' for z in new) or '原目标记录未列出新证据；请查冻结审核与完整会话'
 role='严格纠错条件候选' if n in (7,10) else '总体更新；冻结审核排除严格纠错'
 judge={'full':'原诊断完整','partial':'原诊断部分覆盖','missing':'原诊断未保存','not_saved':'原诊断未保存'}.get(d['verdict']['state'],d['verdict']['state'])
 if n in (7,10): judge+='；旧当前状态未显式历史化，严格成功待人工确认'
 else: judge+='；核心完整性待人工最终确认'
 note=esc(d['verdict']['note']+' 限制：'+d['verdict']['unknown'])
 if n in (7,10):
  note+='。更新前相关旧记忆：'+refs(d['old_related_memory'])
 lines.append(f'|{n} / {user(n)}<br>{role}|{news}|{esc(r["supported_new_state"])}|{refs(d["new_related_memory"])}|{judge}。{note}|[目标 {n:02d}]({link(n)})；[原诊断](../williams_native_prefix5_20261028_v3/development_diagnosis_v1/NATIVE_MEM0_DIAGNOSIS.md#target-{n})|')
(D/'USR.md').write_text('\n'.join(lines)+'\n')
rows=[]
for x in obs:
 n=x['target_number']; idx=x['candidate_index']; k=(n,idx); sel=select(x)
 key=manual_groups.get(k,(sel[0] if sel else user(n)+'-'+x['proposition'].strip()))
 ptr,date,quote=prot_evidence(n,idx)
 scope='主目标' if n in primary else '重复确认/归并目标；不纳入19主目标试算'
 if sel:
  fact,terms=sel; before='完整：列出的事实要素均有明确文本'; valid='应保留（以原审核候选和新会话未撤销为暂定依据；时间有效性仍可复核）'; after='完整保留（文本证据）'; reason='逐一对照指定文本，不凭匹配数量判断'; b=refs(x['before_matches'],terms); a=refs(x['after_matches'],terms)
 else:
  fact=x['proposition']; before='待核验：匹配片段不能证明完整'; valid='待核验：当前有效或历史保留范围'; after='无法判断'; reason='复合命题、时间或关系需逐项拆分；以下是定位器结果，可能含无关文本'; b=refs(x['before_matches']);a=refs(x['after_matches'])
 if x['before_coverage']=='not_located_before':
  before='未定位相关前存量；完整性无法判断'; valid='待核验'; after='无法判断；不计更新损伤'; reason='未定位不等于数据库确定没有；须全文核查'
 if k in [(8,2),(14,1),(24,2)]:
  before='复合候选：见拆分表';valid='部分要素应按历史事实保护，见拆分表';after='部分损伤线索，见拆分表；待人工确认';reason='原诊断及完整快照显示部分要素缩减，不能把候选整体直接计一项'
 if k==(7,11): before='部分：改善医疗可及性已存；建立倡议未由匹配证明';after='完整候选无法判断；不将建立倡议计为本次损伤';reason='理解全球健康倡议不等于建立倡议'
 if k in [(10,5),(11,5)]:before='旧Director职位已存，但没有明确日期或历史语气';valid='应作为历史保留，时间表示规则待确认';after='旧文字仍为当前语气；历史时间完整性待确认';reason='新Lead Director与旧Director共存，不能直接算带时间历史完整'
 rows.append(dict(id=f'{n}/{idx}',scope=scope,owner=user(n),fact=fact,duplicate=key+'；同组 '+', '.join(groups[key]),before=before,retain=valid,after=after,reason=reason,before_text=b,after_text=a,pointer=ptr,date=date,quote=quote,source=source(n,idx)))
with (D/'KPR_候选索引.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
L=['# KPR 候选核验表','', '共覆盖冻结审核的 176 个「目标×候选」行；只有主目标行属于 19 目标工作范围。其他目标作关联与重复追踪。定位器可能匹配无关词，未进行完整语义核验的行标记为无法判断；不要将其算成损伤或完整保留。相同组只表示文本完全相同或已人工标注的重叠，不表示所有语义重复均已识别。不同会话的同一事实是不同时间的保护机会；同一会话多个目标不要重复计数。','', '完整快照和冻结候选在每个目标 JSON 的 `before`、`after` 和 `review.candidate_protections`；每行保留 ID 和原文。以下新对话来源 pointer 为原始用户数据中的位置，引用的冻结副本含文本时同时展示原文。日期不自动等于已存入记忆。','']
for row in rows:
 L += [f'## {row["id"]} · {row["owner"]}',f'- 范围：{row["scope"]}；事实／候选：{row["fact"]}',f'- 重复或归属：{row["duplicate"]}',f'- 更新前完整性：{row["before"]}；仍应保留：{row["retain"]}',f'- 更新后：{row["after"]}。{row["reason"]}',f'- 新旧对照：before：{row["before_text"]}<br>after：{row["after_text"]}',f'- 来源：[{row["source"]}]({link(int(row["id"].split("/")[0]))})；原始对话 pointer：`{row["pointer"] or "未在冻结候选中提供"}`；时间：{row["date"] or "未提供"}'+(f'；原话：{esc(row["quote"])}' if row['quote'] else ''),'']
(D/'KPR_逐候选.md').write_text('\n'.join(L))
# Explicit atomic breakdown of material composite cases. Quotes copied from source snapshots.
splits=[
 ('8/2','此前回避极限运动及安全顾虑','e1d4f8f9-0520-427d-94fd-a2ac0ee69d03','完整','历史应保留','完整保留历史回避及一般安全顾虑'),
 ('8/2','此前回避的具体理由：高受伤风险','e1d4f8f9-0520-427d-94fd-a2ac0ee69d03','完整','历史原因应保留','损失/错误线索：after 仅有安全顾虑，原诊断检查完整after未找到高受伤风险；待人工确认'),
 ('14/1','喜爱波斯猫及高贵／历史魅力','eef34a57-c82a-4995-877d-66b54b9589da','完整','应保留','大体保留；高贵、历史关联是否等价历史魅力待确认'),
 ('14/1','波斯猫平静特质是喜爱理由','eef34a57-c82a-4995-877d-66b54b9589da','完整','应保留','损失线索：after 未显式保留 calm；原诊断检查完整after未补回；待人工确认'),
 ('14/1','波斯猫优雅是喜爱理由','eef34a57-c82a-4995-877d-66b54b9589da','完整','应保留','无法判断：regal appearance 与 elegance 是否足够等价待确认'),
 ('24/2','曾任 Blockchain Tech 高级开发人员','05afde13-35bd-4d26-bbae-6de427d58db1','完整（职业、雇主、职级；无精确日期）','历史应保留','部分损伤：仅 Formerly worked in technology，雇主及高级职位丢失线索，待人工确认'),
 ('24/2','转型前月收入 17,000 美元','46374680-0009-4625-a3a7-f2b4e329a7b5','完整（数额、月收入、转型前；未显式日期）','作为历史应保留','完整保留上述要素；确切日期另待确认'),
 ('24/2','储蓄 16,800 美元','31884358-05ca-4517-bc84-2a7f5fdad0c8','完整（数额与储蓄关系；未显式日期）','按历史保留，不推断仍是当前余额','完整保留数额和储蓄关系；历史时间标记待确认'),
]
S=['# 复合候选拆分核验','', '以下只对所列具体要素判断，不能以局部结果替代复合候选。更新前后直接取完整快照对应 ID；时间要求按各行明确说明。','', '|来源|具体事实|更新前|仍应保留|更新后|before 原文|after 原文|','|---|---|---|---|---|---|---|']
for ident,fact,mid,b,v,a in splits:
 n=int(ident.split('/')[0]); x=evi[n]; S.append(f'|[{ident}]({link(n)})|{fact}|{b}|{v}|{a}|`{mid}` {esc(x["before"].get(mid,"不存在"))}|`{mid}` {esc(x["after"].get(mid,"不存在"))}|')
(D/'KPR_拆分事实.md').write_text('\n'.join(S)+'\n')
# Count only the directly assessed atomic proposition rows within primary targets, deduplicated within same session.
selected=[r for r in rows if r['scope']=='主目标' and r['after']=='完整保留（文本证据）']
uniq={}
for r in selected:
 n=int(r['id'].split('/')[0]); key=(evi[n]['review']['session_group_id'],r['fact']);uniq.setdefault(key,[]).append(r['id'])
counts={'all_candidates':len(rows),'primary_candidate_rows':sum(r['scope']=='主目标' for r in rows),'other_candidate_rows':sum(r['scope']!='主目标' for r in rows),'strict_selected_rows':len(selected),'strict_selected_unique_case_fact':len(uniq),'primary_undetermined_rows':sum(r['scope']=='主目标' and r['after']=='无法判断' for r in rows),'selected_groups':[{ 'session':s,'fact':f,'candidate_rows':v} for (s,f),v in uniq.items()]}
(D/'COUNTS.json').write_text(json.dumps(counts,ensure_ascii=False,indent=2)+'\n')
# Inputs are indexed by SHA, so the output is reproducible without touching source.
paths=[BASE/'target_decisions.json',BASE/'protection_observations.json',BASE/'NATIVE_MEM0_DIAGNOSIS.md']+[BASE/f'target_{i:02}_evidence.json' for i in range(1,25)]
(D/'SOURCE_SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(D.parent))+'\n' for p in paths))
print(json.dumps({k:v for k,v in counts.items() if k!='selected_groups'},ensure_ascii=False))
