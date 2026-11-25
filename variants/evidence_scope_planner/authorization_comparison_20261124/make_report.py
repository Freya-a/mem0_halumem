"""Render a hash-bound, independently reviewed comparison without model calls."""
from collections import Counter
import json
from pathlib import Path
import comparison as cmp

HERE=Path(__file__).resolve().parent
REVIEW=cmp.PROJECT/'variants/evidence_aligner/v4_scope_interface/human_reviews.json'
LABEL={'correct_add':'新增有依据','incorrect_add':'新增无充分依据','partial_add':'部分有依据，限定或属性有问题',
       'unsupported_modify':'修改无充分依据','incorrect_preserve':'保留项的主体错误',
       'hold':'暂缓','supported':'有依据'}

def j(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def quote(s):
    return str(s).replace('\n',' ').replace('|','\\|')

def qdetails(quotes):
    if not quotes: return '无'
    return '；'.join(f"{q.get('side','?')} {q.get('source_id')} / {q.get('unit_id')}，{q.get('status')}，位置 {j(q.get('position'))}，来源 `{q.get('source_ref')}`，原文「{quote(q.get('quote'))}」" for q in quotes)

def main():
    audit=load(HERE/'AUDIT.json'); old_reviews=load(REVIEW); manifest=load(HERE/'results/manifest.json')
    data={c:load(HERE/'results'/f'{c}.json') for c in cmp.CASES}
    totals={g:Counter() for g in 'ABC'}
    # Fail closed on drift: never silently recycle an assessment after replay.
    for c,r in data.items():
        for i,rec in enumerate(r['raw_model_output']['records']):
            old=old_reviews['cases'][c]['records'][str(i)]
            if cmp.digest(rec)!=old['sha256']: raise ValueError(f'{c} record {i} changed since old independent review')
        for g in 'ABC':
            ar=audit['cases'][c]['groups'][g];plan=r[g]['plan']
            if cmp.digest(plan)!=ar['plan_sha256']: raise ValueError(f'{c}/{g} plan changed since independent audit')
            for category in ('modify','preserve','uncertain','add'):
                items=plan[category]; reviews=ar['actions'][category]
                if len(items)!=len(reviews): raise ValueError(f'{c}/{g}/{category} length changed')
                for idx,(item,review) in enumerate(zip(items,reviews)):
                    if review['index']!=idx or cmp.digest(item)!=review['item_sha256']:
                        raise ValueError(f'{c}/{g}/{category}/{idx} changed')
                    totals[g][review['verdict']]+=1
    out=[]
    def add(x=''):out.append(x)
    add('# 离线授权方式对照：五案开发诊断')
    add('')
    add('## 边界和结果')
    add('')
    add('本报告只读取五次已保存模型响应，没有调用模型或 API，没有写入 Mem0 或真实记忆。五案用于开发诊断，不是论文准确率，也不是用户确认的金标准。三组调用同一份 v3 `build_scope_plan()`；A 的结果逐案与原 v3 unprotected 保存结果逐字节结构比对一致。C 的旧记忆及所选新证据文本、来源与模型所用案例一致，但 C 使用独立的人工对齐和人工事实拆分。')
    add('')
    add('A 保持 v3 的独立语义授权门槛；B 仅在主引文可定位且绑定来源/单元后，将模型判断作为候选送入同一规划器，并保留规划器原有来源、范围、模态和时间检查；C 使用现有人工核对对齐输入。B 为适配 v3 的布尔门槛而写入内部 `semantic_support=supported`，这个值在 B **只表示模型候选**，不是独立授权，也不是语义正确证明；v3 原样输出的“independent evidence-supported”“evidenced later state”等理由在 B 亦不能当作独立审核结论。B 的任何动作都不能直接写入真实记忆。')
    add('')
    add('B 对每个原有关系保留独立候选；对于模型 `change`，另从同一条模型记录投影新侧断言，不从预期或外部上下文补事实。仅按原 `new_value` 中字面分号拆分，后续部分必须在已绑定的新引文中逐字出现；`same_as_old` 仅在模型本身提供明确旧条件时继承，否则标未知。新事实独立评估无需证明与旧事实的时间先后；旧关系仍保留原有的时间/范围检查。若同一模型记录已经提出修改，重复的新增会单列为抑制项。仅为旧状态关系所需的错误不会自动污染独立新断言，但其新侧引文及语义依据仍须通过绑定校验。')
    add('')
    add('自动结果给出引用可定位、字段及规划动作；下文每条的正确性判断由研究者依据原文和既有审核另行人工核对，未用于生成 A/B 规划。已有人工预期与 C 同为人工材料，不能作独立模型输出或未经审定的真值。`AUDIT.json` 将每条核对绑定到计划与动作哈希；报告生成时检查哈希及原模型逐条审核哈希，结果变动必须重新核对。')
    add('')
    add('| 案例 | A 修改/保留/待确认/新增 | B 修改/保留/待确认/新增 | C 修改/保留/待确认/新增 |')
    add('|---|---:|---:|---:|')
    for c,r in data.items():
        n=lambda g:'/'.join(str(len(r[g]['plan'][k])) for k in ('modify','preserve','uncertain','add'))
        add(f'| {c} | {n("A")} | {n("B")} | {n("C")} |')
    add('')
    add('| 人工逐项判断 | A | B | C |')
    add('|---|---:|---:|---:|')
    for code,name in [('correct_modify','正确修改'),('unsupported_modify','错误或无充分依据的修改'),('correct_add','正确新增'),('incorrect_add','错误或无充分依据的新增'),('partial_add','新增部分有依据、完整候选不可直接接受'),('incorrect_preserve','保留项主体有误')]:
        add(f'| {name} | '+ ' | '.join(str(totals[g][code]) for g in 'ABC')+' |')
    add('')
    add('这些是人工对**产生的动作**的判断，不是模型事实覆盖率；“错误或无充分依据”表示当前材料不授权该完整动作，并非断言其现实中必假。B 另有转岗原始关系未进入任何输出分类，不能用 0 修改或新增数量掩盖。A/B 使用原 v3 未加附加保护投影，skydiving A 为 8 条待确认；与 v3 报告另列的 protected 投影的 4 条不可混数。')
    add('')
    for c,r in data.items():
        a=audit['cases'][c]; p=r['prepared_input']; records=r['raw_model_output']['records']; source=p['source_texts']; selected=set()
        def gather(obj):
            if isinstance(obj,dict):
                if isinstance(obj.get('source_id'),str):selected.add(obj['source_id'])
                for v in obj.values():gather(v)
            elif isinstance(obj,list):
                for v in obj:gather(v)
        gather(records);gather(r['C']['alignments'])
        add(f'## {c}')
        add('')
        add(f"旧记忆（`{source['memory']['source_id']}`，`{source['memory']['source_ref']}`）：{source['memory']['text']}")
        add('')
        add('关联的新证据及来源上下文（仅列模型或 C 引用到的来源；完整保存内容见每案结果的 `prepared_input`）：')
        add('')
        for s in source['messages']:
            if s['source_id'] in selected:
                add(f"- `{s['source_id']}`（{s.get('speaker')}，`{s.get('source_ref')}`）：{s['text']}")
        add('')
        exp=r['expected'];add('已有人工预期（保留原预期，可能比本轮谨慎审核更积极，不是规划输入）：')
        for k in ('modify','preserve','uncertain','add','missing'):add(f"- {k}：{'；'.join(exp.get(k,[])) or '无'}")
        add('')
        add('模型原始各条关系及此前独立逐条审核：')
        add('')
        for i,rec in enumerate(records):
            rev=old_reviews['cases'][c]['records'][str(i)]
            qs=[q for q in r['validation']['quote_checks'] if q['record_index']==i]
            add(f"- 记录 {i}：关系 `{rec.get('relation')}`，单元 `{rec.get('unit_id')}`；主体/属性/值 `{j([rec.get('old_subject'),rec.get('old_attribute'),rec.get('old_value')])}` → `{j([rec.get('new_subject'),rec.get('new_attribute'),rec.get('new_value')])}`；条件 `{j([rec.get('old_conditions'),rec.get('new_conditions')])}`；时序 `{j(rec.get('temporal_order'))}`；模型理由：{rec.get('semantic_rationale')}；模型未知项 `{j(rec.get('uncertainties'))}`。")
            for q in qs:
                sid=q.get('source_id'); found=source['memory'] if sid==source['memory']['source_id'] else next((s for s in source['messages'] if s['source_id']==sid),{})
                add(f"  - 引文 `{q.get('side')}/{sid}/{q.get('unit_id')}`：{q.get('status')}，位置 `{j(q.get('position'))}`，`{found.get('source_ref')}`：「{quote(q.get('quote'))}」；{q.get('reason') or '定位通过'}。")
            add(f"  - 既有独立审核 `{rev['verdict']}`：{rev['reason']}")
            if r['validation']['record_errors'][i]:add(f"  - 自动接口问题：`{j(r['validation']['record_errors'][i])}`。")
        add('')
        add('B 的新侧候选及未输出关系（每条仍是模型候选，`validation_errors` 与引文检查只检验结构和绑定）：')
        add('')
        derived=[x for x in r['B']['alignments'] if 'candidate=new_subfact' in (x.get('note') or '')]
        if not derived:add('- 本案无从 change 投影的新侧候选。')
        for x in derived:
            add(f"- `{x.get('note')}`：主体 `{j(x.get('new_subject'))}`，属性 `{j(x.get('new_attribute'))}`，值 `{j(x.get('new_value'))}`，条件 `{j(x.get('new_conditions'))}`，模态 `{j(x.get('modality'))}`，新引文 `{j(x.get('new_quotes'))}`，语义依据 `{j(x.get('semantic_basis'))}`，校验错误 `{j(x.get('validation_errors'))}`。")
        for x in r['B']['relation_coverage']:
            if not x['relation_emitted']:add(f"- 原关系记录 {x['record_index']} 未单独出现在任何动作中：{x['reason']}。此为输出覆盖缺口，不等同已经拒绝或接受修改。")
        for x in r['B']['suppressed_duplicate_adds']:
            add(f"- 抑制的重复新增：`{x['item'].get('note')}` / `{j(x['item'].get('new_value'))}`；{x['reason']}。")
        add('')
        for g in 'ABC':
            plan=r[g]['plan'];add(f'### {g} 组：实际计划及人工核对')
            add('')
            for category in ('modify','preserve','uncertain','add'):
                items=plan[category];reviews=a['groups'][g]['actions'][category]
                add(f'**{category}**（{len(items)}）')
                add('')
                if not items:add('无。');add('');continue
                for idx,(item,review) in enumerate(zip(items,reviews)):
                    add(f"{idx+1}. `{item.get('unit_id')}` / `{item.get('relation')}`：旧值 `{j(item.get('old_value'))}` → 新值 `{j(item.get('new_value'))}`；主体 `{j(item.get('subject'))}`，属性 `{j(item.get('attribute'))}`，范围 `{j(item.get('scope'))}`。")
                    add(f"   规划器理由：{item.get('reason')}；缺失 `{j(item.get('missing_reasons'))}`；校验错误 `{j(item.get('validation_errors'))}`；未知项 `{j(item.get('unknowns'))}`。")
                    add(f"   引文：{qdetails(item.get('old_quotes',[])+item.get('new_quotes',[]))}。")
                    add(f"   人工判断：**{LABEL.get(review['verdict'],review['verdict'])}**。{review['reason']}")
                add('')
            add(f"可编辑位置：`{j(plan.get('editable_spans',[]))}`；保护事实：`{j(plan.get('protected_facts',[]))}`。")
            add('')
        f=a['findings'];add('### 差异与仍需处理')
        add('')
        add(f"- 子事实及依据：{f['new_subfacts']}")
        add(f"- 应处理但暂缓或未覆盖：{f['deferred']}")
        add(f"- A/B 差异及风险：{f['difference']}")
        add(f"- 人工依赖及 C 的诊断作用：{f['human_dependency']}")
        add('')
    add('## 复现与限制')
    add('')
    add('本次验证：本目录 6 项接口与候选隔离测试通过；原 v3 测试集 40 项通过；五案 A 结果均与既存 v3 未加附加保护的结果一致。测试通过只说明这些程序检查通过，不代表 B 的候选经语义授权。')
    add('')
    add('在本目录运行：')
    add('```sh')
    add('PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v')
    add('PYTHONDONTWRITEBYTECODE=1 python comparison.py')
    add('PYTHONDONTWRITEBYTECODE=1 python make_report.py')
    add('```')
    add('')
    add('自动链路能够校验引文位置、来源和显式范围/时序字段，不能验证自然语言蕴含关系，也不能把观察到的发话时间变成事实生效时间。B 的分号拆分保留模型属性，可能让不同子事实共享错误属性并触发虚假冲突；新增判断也可能因模型语义猜测而错误。C 的主体、条件、语义支持及事实拆分来自既有人工作业，不能归功于自动流程。需要单独人工语义审核及完整关系覆盖后才能讨论后续写入。')
    add('')
    add('机器可读结果：`results/*.json`；人工判断：`AUDIT.json`；原逐条审核：`../../evidence_aligner/v4_scope_interface/human_reviews.json`；既有 v3 报告：`../v3_offline/REPORT.md`。')
    (HERE/'REPORT.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    print('wrote REPORT.md; audited verdict totals:',j({g:dict(totals[g]) for g in 'ABC'}))

if __name__=='__main__':main()
