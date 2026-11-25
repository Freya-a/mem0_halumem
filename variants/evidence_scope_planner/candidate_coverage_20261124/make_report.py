"""Render trace and human decomposition with strict input/review bindings."""
import json
from collections import Counter
from pathlib import Path
import replay

HERE=replay.HERE

def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def clean(s):return str(s).replace('\n',' ').replace('|','\\|')
def main():
    manifest=replay.read(HERE/'results/manifest.json')
    if manifest['prior_audit_sha256']!=replay.sha(replay.PRIOR/'AUDIT.json') or manifest['prior_report_sha256']!=replay.sha(replay.PRIOR/'REPORT.md') or manifest['planner_sha256']!=replay.sha(HERE/'scope_planner.py'):
        raise ValueError('source artifacts changed since replay')
    manual=replay.read(HERE/'MANUAL_SUBFACTS.json')
    data={c:replay.read(HERE/'results'/(c+'.json')) for c in replay.cmp.CASES}
    for case, result in data.items():
        raw_path=replay.cmp.RUN/(case+'.json')
        raw=replay.read(raw_path)
        if (replay.sha(raw_path)!=result['raw_sha256']
                or raw['result']['parsed']!=result['raw_model_output']
                or raw['prepared_input']['source_texts']['memory']!=result['old_memory']
                or raw['prepared_input']['source_texts']['messages']!=result['sources']):
            raise ValueError(f'{case}: replay source or model output changed')
        for group in 'ABC':
            current=result['groups'][group]; plan=current['new_plan']
            if len(plan['candidate_coverage'])!=len(current['inputs']):
                raise ValueError(f'{case}/{group}: candidate count changed')
            for cov in plan['candidate_coverage']:
                if not cov['judgments']:raise ValueError('candidate has no judgments')
                for judgment in cov['judgments']:
                    if not judgment['outputs']:raise ValueError('candidate has no output')
                    for ref in judgment['outputs']:
                        item=plan[ref['category']][ref['index']]
                        if (item.get('candidate_index'),item.get('judgment_kind')) != (cov['candidate_index'],judgment['kind']):
                            raise ValueError(f'{case}/{group}: coverage pointer mismatch')
    original_audit=replay.read(replay.PRIOR/'AUDIT.json')
    for r in manual['reviews']:
        prior=replay.read(replay.PRIOR/'results'/(r['case']+'.json'))
        item=prior['B']['plan'][r['prior_category']][r['prior_index']]
        binding=original_audit['cases'][r['case']]['groups']['B']['actions'][r['prior_category']][r['prior_index']]
        if replay.cmp.digest(item)!=r['prior_action_sha256'] or r['prior_action_sha256']!=binding['item_sha256']:
            raise ValueError('human review refers to different prior action')
        record=prior['raw_model_output']['records'][r['model_record_index']]
        for sub in r['subfacts']:
            if not sub['linked_quotations'] or any(q not in [{'source_id':x['source_id'],'quote':x['quote']} for x in record['new_quotes']] or sub['verbatim_excerpt'] not in q['quote'] for q in sub['linked_quotations']):
                raise ValueError('manual subfact quotation not linked to raw model record')
    extra=manual['extra_review'];xrec=data[extra['case']]['raw_model_output']['records'][extra['record_index']]
    if replay.cmp.digest(xrec)!=extra['record_sha256']:raise ValueError('extra model record changed')
    for sub in extra['subfacts']:
        if not sub['linked_quotations'] or any(q not in [{'source_id':x['source_id'],'quote':x['quote']} for x in xrec['new_quotes']] or sub['verbatim_excerpt'] not in q['quote'] for q in sub['linked_quotations']):
            raise ValueError('extra subfact quotation not linked to raw model record')
    expected={(c,k,i) for c in data for k in ('modify','add') for i,_ in enumerate(data[c]['groups']['B']['old_plan'][k])}
    reviewed={(x['case'],x['prior_category'],x['prior_index']) for x in manual['reviews']}
    if reviewed!=expected:raise ValueError(f'manual review incomplete: missing {expected-reviewed}, extra {reviewed-expected}')
    lines=[]
    def add(x=''):lines.append(x)
    add('# 候选事实拆分与覆盖检查：离线五案')
    add('')
    add('## 范围与结论')
    add('')
    add('本次只读取 v4 已保存的五次原始响应及既有 v3 授权对照，未调用模型或 API，未写真实记忆或 Mem0。新版本保留 v3 条件和时间计算及 A/B/C 输入政策；B 的 `semantic_support=supported` 仅是原实验中的模型候选兼容标记，不构成独立语义授权。覆盖通过不代表事实正确，更不表示可以执行写入；五案仅用于开发诊断。')
    add('')
    add('定位到的缺口：转岗 B 的两条旧关系都落入 `job_search` 同一范围；记录 1 是 supplement，v3 将它的新事实另行输出，但对旧事实影响设置了 `impact of new information on old fact is not established`。进入范围单元时，原 v3 的 `if uncertain` 仅输出带理由的记录 1，然后 `continue`，因此同格的记录 0 `change` 被跳过。修复后，每条受该范围阻塞的关系均单独输出 `uncertain`；记录 0 的原因是 `scope decision blocked by another unresolved overlapping candidate`。这是聚合阻塞的程序原因，不是已经完成时间或语义审核。')
    add('')
    add('新规划器给每个输入分配 `candidate_index`，分别追踪 `old_relation` 和 `new_claim`；A/B 原始关系和 B 原有投影的新侧子候选都在账本中。每个子判断必须指向最终 `modify/preserve/uncertain/add` 的具体索引；聚合中没有独立结果时，保守补 `uncertain`，并阻止与该未决同单元范围重叠的编辑。输出项中没有输入候选来源的受保护事实仍单独保留，不冒充候选判断。该机制追踪已给出的输入，不能证明自然语言中所有潜在事实都被模型提出，也不能保证每个候选内部所有自然语言子事实已自动拆开。')
    add('')
    add('人工审核与程序回放严格分开：下文“人工子判断”只写在 `MANUAL_SUBFACTS.json`，不进入规划器。`atomic` 表示模型已有单独结构化内容，`combined` 表示仅在合并值/理由中明确，`quote_or_rationale` 表示仅在引文或理由中出现，`unsupported_relation` 表示模型确实声称但引文不足以证明，`not_asserted` 表示不能从模型输出确认该关系。对于后四种，自动链路不能凭人工审核当作已生成的独立事实；需要人工重新对齐，或将来通过重新模型拆分并审核取得独立候选。本次没有进行模型重拆。')
    add('')
    add('| 案例 | 旧 B 修改/保留/待确认/新增 | 新 B 修改/保留/待确认/新增 | 新 B 候选 / 子判断 / 已映射子判断 |')
    add('|---|---:|---:|---:|')
    for c,d in data.items():
        g=d['groups']['B'];n=lambda z:'/'.join(str(z[k]) for k in ('modify','preserve','uncertain','add'))
        mapped=sum(bool(jd['outputs']) for cv in g['new_plan']['candidate_coverage'] for jd in cv['judgments'])
        add(f"| {c} | {n(g['old_counts'])} | {n(g['new_counts'])} | {g['candidate_count']} / {g['judgment_count']} / {mapped} |")
    add('')
    add('B 总计 22 条输入候选、25 项可追踪子判断，全部关联最终输出。A/C 的输入及覆盖见逐案账本。这里的子判断是程序中原有关系与新增路径、及旧 B 已有的新侧投影，不是对复杂自然语言的完整人工拆分。')
    add('')
    add('晋升 B 新增数从 0 变 1 与聚合修复无关：原对照脚本在 v3 运行后抑制与修改来自同一模型记录的新增候选；本次为保留每个输入的明确去向，不再执行该对照后处理，保留新侧候选 `add`，同时标明它与该条修改语义重叠。此候选是模型原文投影而非独立授权，不能与修改一起当成已批准的两次写入；新职位话语有依据，但旧职位替换与时间仍不成立。')
    add('')
    differences=[f"{c}/{g}: {','.join(d['groups'][g]['changed_categories'])}" for c,d in data.items()
                 for g in 'ABC' if d['groups'][g]['changed_categories']]
    add('逐字段比较（忽略新增追踪字段）后的不同输出类别：'+('；'.join(differences) or '无')+'；其余案例组的原有输出内容一致。')
    add('')
    for c,d in data.items():
        add(f'## {c}')
        add('')
        add(f"旧记忆（`{d['old_memory']['source_id']}`，`{d['old_memory']['source_ref']}`）：{d['old_memory']['text']}")
        add('')
        add('### 保存的模型原始记录与逐字引文')
        add('')
        for i,rec in enumerate(d['raw_model_output']['records']):
            add(f'**模型记录 {i}（完整保存字段）**')
            add('')
            add('```json');add(json.dumps(rec,ensure_ascii=False,indent=2));add('```')
            for q in [q for q in d['validation']['quote_checks'] if q['record_index']==i]:
                source=d['old_memory'] if q['source_id']==d['old_memory']['source_id'] else next((s for s in d['sources'] if s['source_id']==q['source_id']),{})
                add(f"- `{q['side']}/{q['source_id']}/{q['unit_id']}`：{q['status']}，位置 `{j(q.get('position'))}`，来源 `{source.get('source_ref')}`；逐字引文：\u300c{clean(q['quote'])}\u300d。")
            add('')
        add('### B 组每个输入候选及子判断的最终去向')
        add('')
        g=d['groups']['B'];p=g['new_plan']
        for cov in p['candidate_coverage']:
            a=g['inputs'][cov['candidate_index']]
            add(f"- 输入 {cov['candidate_index']}：`{cov['note']}`；关系 `{a.get('relation')}`，旧/新值 `{j(a.get('old_value'))}` → `{j(a.get('new_value'))}`。")
            for jd in cov['judgments']:
                refdesc=[]
                for ref in jd['outputs']:
                    x=p[ref['category']][ref['index']]
                    refdesc.append(f"`{ref['category']}[{ref['index']}]`（{clean(x.get('reason'))}；范围 `{j(x.get('scope'))}`）")
                add(f"  - `{jd['kind']}` → "+'；'.join(refdesc))
        add('')
        add('### 原 B 修改和新增的人工子判断')
        add('')
        for r in [r for r in manual['reviews'] if r['case']==c]:
            prior=replay.read(replay.PRIOR/'results'/(c+'.json'))['B']['plan'][r['prior_category']][r['prior_index']]
            add(f"**原 B `{r['prior_category']}[{r['prior_index']}]`；模型记录 {r['model_record_index']}**。原候选主体 `{j(prior.get('subject'))}`，属性 `{j(prior.get('attribute'))}`，旧值 `{j(prior.get('old_value'))}`，新值 `{j(prior.get('new_value'))}`；此前审核：{r['prior_audit_reason']}")
            add('')
            for q in prior.get('new_quotes',[]):add(f"- 原动作关联的新引文 `{q['source_id']}`（{q['status']}，`{q.get('source_ref')}`，`{j(q.get('position'))}`）：\u300c{clean(q['quote'])}\u300d。")
            for sub in r['subfacts']:
                labels={'supported':'原文支持','extension':'无依据扩展','unresolved':'关系仍需确认'}
                add(f"- **{labels[sub['kind']]}**：{sub['claim']}。逐字依据 \u300c{clean(sub['verbatim_excerpt'])}\u300d；模型可得性 `{sub['extractability']}`：{sub['explanation']}")
            add('')
        if extra['case']==c:
            add(f"**补查：原 B 待确认的模型记录 {extra['record_index']}（模拟与真实活动）**")
            add('')
            for sub in extra['subfacts']:
                add(f"- **{'原文支持' if sub['kind']=='supported' else '关系仍需确认'}**：{sub['claim']}；逐字依据 \u300c{clean(sub['verbatim_excerpt'])}\u300d；`{sub['extractability']}`：{sub['explanation']}")
            add('')
        if c=='promotion':
            add('本次额外显露的 `B add[0]` 是旧对照抑制的 `new_subfact`，值为 `lead director`，与上述 `modify[0]` 来自同一模型记录。发话者晋升及新职位由引文支持；覆盖旧职位的先后关系不因此成立。')
            add('')
        add('### A、C 组覆盖及新旧数量')
        add('')
        for group in ('A','C'):
            gg=d['groups'][group];q=gg['new_plan']
            add(f"- {group} 旧 `{j(gg['old_counts'])}` → 新 `{j(gg['new_counts'])}`；输入 {gg['candidate_count']} 条，子判断 {gg['judgment_count']} 项。")
            for cv in q['candidate_coverage']:
                desc=[]
                for jd in cv['judgments']:
                    desc.append(jd['kind']+' → '+', '.join(f"{r['category']}[{r['index']}]" for r in jd['outputs']))
                add(f"  - 输入 {cv['candidate_index']}（`{cv['relation']}`）："+'；'.join(desc))
        add('')
    add('## 验证、复现及剩余限制')
    add('')
    add('新增测试覆盖同范围待确认阻塞并列关系、新旧子判断分别追踪、重复候选、相互冲突候选、缺失单元和二维条件组合；另对新规划器运行既有 v3 范围及接口测试。覆盖账本断言最终索引存在，回放校验保存原始响应、旧输入重建及旧人工审核动作哈希。')
    add('')
    add('```sh')
    add('PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v')
    add('PYTHONDONTWRITEBYTECODE=1 python replay.py')
    add('PYTHONDONTWRITEBYTECODE=1 python make_report.py')
    add('```')
    add('')
    add('尚不能自动完成自然语言的语义蕴含、拆句、否定和隐含时序审核。模型若只把获客放在引文或理由里、把转岗和平衡写成一个值、或将模拟体验绑定真实极限运动态度，必须经人工重新对齐或未来重拆并审核；现有程序不能用上面的人工子判断补写模型输出。即使逐个候选均有去向，也不意味着模型覆盖了原文所有事实。覆盖后备机制不会自动把多条等价候选认作同一输出：被聚合成单个代表的其他候选会保守待确认，可能阻止本可完成的编辑；需要进一步实现并验证安全的等价合并。')
    add('')
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('report written; all eight prior actions and extra simulated-experience record reviewed')

if __name__=='__main__':main()
