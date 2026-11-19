"""Make an auditable human-readable case report; judgments are analyst proposals."""
from pathlib import Path
import csv,json
HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent;PROJ=COMP.parent.parent
rows=list(csv.DictReader((PROJ/'diagnosis/medium_dev/human_review.csv').open(encoding='utf-8-sig',newline='')))
cases=[
 ('job_transition',7,'新 v4 / 新 v2 / 新 NLI',
  '过度保守 / 局部候选遗漏（初步分析）',
  '这次转岗已完成，旧求职阶段应与当前状态区分。v2 的 support 将完成转岗解释为支持仍在找工作，语义上不恰当。第二部分将关系保为 unknown，并没有直接采纳 support，但仍整体保护未限定时态的旧句，未提出历史化候选；已有原文新增可表达新角色，不能据此判端到端更新失败。完整来源与其拆分句子并列，存在重复写入风险。'),
 ('promotion',10,'已有 v4 / 已有 v2 / 历史 NLI 回放',
  '合理待确认与过度保守并存（初步分析）',
  '用户确认当前具体职位为 lead director、Director 保留历史，精确晋升日未知；将两个职位关系完全留待确认过于保守，但不能以消息时间关闭旧职位。第二部分比 v2 整句定位多了雇主局部保护候选，仍未提出职位历史化候选；原文新增包含新职称，不等于已执行更新。'),
 ('skydiving',8,'已有 v4 / 已有 v2 / 历史 NLI 回放',
  '合理待确认；局部保护未分解（初步分析）',
  '用户确认的是模拟跳伞体验、更开放与安全优先，真实跳伞当前态度不明；ADD 或并存均可合理，不能把无修改直接计为失败。第二部分保护整句，因此高伤害风险和安全承诺文字均包含在保护候选中，但没有单独定位这些理由；它也未自行消除针对已明确安全陈述的重复问题。'),
 ('persian_cats',14,'新 v4 / 新 v2 / 新 NLI',
  '合理保护；结构化新增缺口和重复风险（初步分析）',
  '审核确认纪录片加深历史渊源和王室关联的欣赏，同时旧平静性情和其他理由应保留。v2 support 忽略新增细节；第二部分将旧整句保护并多给 Persian cats 片段，新事实抽取列出看纪录片与历史真实性，却未单独抽出“欣赏加深”。dialogue-0 原始完整句候选含该内容，不能称证据或所有候选完全遗漏；原始句和抽取句相互包含，存在重复候选风险。'),
 ('career_history',24,'已有 v4 / 已有 v2 / 历史 NLI 回放',
  '合理保护；待确认问题存在无依据前提（初步分析）',
  '用户确认已获一些首批客户及宽慰；历史 Blockchain Tech 与高级职级应保护。此输入没有提供相关朋友的 dialogue-2，不能把该关系未输出归咎于判断器。v2 理由和问题把 my consulting firm 升级为当前受雇，新抽取也把 employment 用作属性，程序仅标未核验，不能据此认定其事实正确。')]

def fmt(s):return str(s).replace('\n','<br>')
out=['# 冻结判断器：逐案例输入、输出及人工对照','',
 '程序字段与模型候选从本轮结果逐字摘录；“初步分析”是本次依据已确认目标所做的研究者判断，并非用户对本轮输出的确认。所有结果都是候选，没有执行写入。','']
for name,num,mode,label,analysis in cases:
 d=json.loads((HERE/f'{name}_result.json').read_text(encoding='utf8'));r=d['results'][0];v=r['relation']['upstream_candidate'];human=rows[num-1]
 out += [f'## 目标 {num} — {name}', '',f'- 数据模式：{mode}。完整机器结果：[{name}_result.json]({name}_result.json)。',
 f"- 人工目标 ID：`{human['target_id']}`；审核：{human['review_class']}（LLM 辅助、用户确认）。",
 f"- 人工确认新状态：{fmt(human['supported_new_state'])}", f"- 人工允许范围：{fmt(human['allowed_modification_scope'])}",f"- 人工未定：{fmt(human['uncertain_current_state'])}",
 f"- 旧记忆 ID：`{r['memory_id']}`；全文：`{r['memory_text']}`。",
 f"- 组件一 v4 子事实 #{r['fact_index']}：`{r['old_fact']['raw_subfact']}`；上下文版本：`{r['old_fact']['contextualized_subfact']}`。",'- 输入的新证据（原文及来源记录时间；时间不是事件有效期）：']
 for item in d['request']['new_evidence']:
  out.append(f"  - `{item['source_id']}` / {item.get('speaker')} / {item.get('recorded_at')}：{item['text']}")
 out += [f"- 仅第一部分：`{v['relation']}`；候选旧范围 `{v['candidate_impact_fragment']}`，定位 `{r['fragment_match_rechecked']['start']}:{r['fragment_match_rechecked']['end']}`；新引用 `{v['new_quote']['source_id']}`；理由：{v['reason']}",
   f"- 第一部分问题（未作语义校验）：{json.dumps(v['confirmation_questions'],ensure_ascii=False)}。",
   f"- 加入第二部分：局部修改候选 {len(r['modifications'])} 条：{json.dumps(r['modifications'],ensure_ascii=False)}。",
   f"- 保护候选：{json.dumps([{'kind':x.get('kind','whole_fact'),'text':x['text'],'span':x.get('span')} for x in r['protected']],ensure_ascii=False)}。",
   f"- 待确认：{json.dumps(r['pending'],ensure_ascii=False)}。",
   f"- 新增候选 {len(d['additions'])} 条："]
 for item in d['additions']:
  out.append(f"  - {item['text']}；种类 `{','.join(item['kinds'])}`；引文来源 `{','.join(sorted({x['source_id'] for x in item['evidence_refs']}))}`。")
 ext=r['extraction'];nli=r['nli'];time=r['time']
 out += [f"- 第二部分模型抽取：`{ext['status']}`；字段/新命题均未证明语义；抽出的新命题：{json.dumps(ext.get('new_fact_candidates',[]),ensure_ascii=False)}。",
   f"- NLI：`{nli['status']}`；premise=`{nli.get('premise')}` → hypothesis=`{nli.get('hypothesis')}`；softmax={json.dumps(nli.get('softmax_scores'),ensure_ascii=False)}；{'历史真实推理结果回放' if nli.get('inference_mode') else '本次本地真实前向'}。",
   f"- 时间：旧上下文和新消息记录时间={json.dumps(time['recorded_times'],ensure_ascii=False)}；相对词={json.dumps(time['expressions'],ensure_ascii=False)}；有效期关系 `{time['interval_relation']}`；FactTrack `{r['facttrack']['status']}`：{r['facttrack'].get('reason','')}。",
   f'- 本轮对照分类：**{label}**。{analysis}', '']
with (HERE/'CASES.md').open('x',encoding='utf8') as f:f.write('\n'.join(out)+'\n')
print('wrote',len(cases),'cases')
