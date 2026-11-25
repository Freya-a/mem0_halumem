"""Render offline report; require a separately authored, hash-bound review."""
from pathlib import Path
from collections import Counter
import hashlib,json
import interface
HERE=Path(__file__).resolve().parent
RUN=HERE/'runs/qwen_20261124_once'
OLD=HERE.parent/'v4_scope_interface/runs/qwen_20261124_once'
COVERAGE=interface.ROOT/'variants/evidence_scope_planner/candidate_coverage_20261124'
NAMES=('susan','promotion','career_history','transition','skydiving')

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def fmt(x):return str(x).replace('\n',' ').replace('|','\\|')
def counts(p):return {k:len(p[k]) for k in ('modify','preserve','uncertain','add')}

def main():
    manifest=load(RUN/'manifest.json');reviews=load(HERE/'HUMAN_REVIEW.json'); prior=load(HERE.parent/'v4_scope_interface/human_reviews.json')
    for path, expected_hash in load(HERE/'PRECALL.json')['files_sha256'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected_hash:
            raise ValueError(f'pre-call implementation changed: {path}')
    if manifest['request_attempts']>5:raise ValueError('request limit exceeded')
    out=[]
    def add(s=''):out.append(s)
    add('# v5 新事实拆分与关系对齐：五案实验');add('')
    add('## 方法和边界');add('')
    add('五案输入与保存的 v4 输入一致；每次仅一请求、自动重试为零。facts 是模型提出的新事实，relations 单独引用事实与旧单元。适配后每项事实和每项旧关系成为独立规划器候选；模型语义理由不等于独立审核，默认 semantic_support 为 unknown。未调用 Mem0，也未写真实记忆。五案用于开发诊断，不是论文准确率或用户确认金标准。')
    add('')
    add('结构校验、逐字引文及来源校验、人工语义判断是不同结果。引文可定位并不证明其支持模型的全部推断。下文人工判断来自对原文和既有审核的独立核对，只写在 HUMAN_REVIEW.json，不作为模型输出、也不回填到规划器。完整回复、请求配置、耗时和可得用量保存在 runs 目录；人工预期作为比较材料，不输入模型或规划器。')
    add('')
    add('v4 的严格 A 与本次 v5 默认计划都要求独立语义授权；旧 B 是放开该门槛的候选实验，其动作数量不能与本次默认计划直接比较。`supplement` 关系在适配时投影为旧影响 unknown（原始 relation 保留），以免对已经独立输出的新事实再次制造一条新增。')
    add('')
    add(f"本次请求尝试 **{manifest['request_attempts']}**，收到模型响应 **{manifest['model_responses']}**；状态 `{manifest['status']}`。模型 `{manifest['model']}`，temperature `{manifest['temperature']}`，JSON 对象格式，最大生成 `{manifest['max_tokens']}` tokens，自动重试 `{manifest['automatic_retries']}`。")
    total=Counter()
    for case in manifest['cases']:
        for key in ('prompt_tokens','completion_tokens','total_tokens'):
            if isinstance((case.get('usage') or {}).get(key),int):total[key]+=(case['usage'][key])
    add(f"可获得的合计用量：输入 {total['prompt_tokens']}，输出 {total['completion_tokens']}，总计 {total['total_tokens']} tokens；无返回用量的请求不计入总数。")
    add('')
    add('下表的 passed/failed 是收到回复后的接口总校验状态，不是请求是否成功；具体结构、引文和依据绑定分列。')
    add('')
    add('| 案例 | 接口状态/秒 | token 输入/输出/总计 | 结构 | 引文定位 | 依据绑定 | 模型事实/关系 | 完整支持的事实/关系 |')
    add('|---|---|---|---|---|---|---|---|')
    cases={};metrics=Counter()
    for name in NAMES:
        a=load(RUN/(name+'.json'));cases[name]=a
        call=a['call'];usage=a.get('usage') or {};r=a.get('result') or {};v=r.get('validation') or {}; human=reviews['cases'][name]
        if human['raw_sha256']!=hashlib.sha256((a.get('raw_response') or '').encode()).hexdigest():raise ValueError(f'{name}: reviewed response changed')
        parsed=r.get('parsed')
        if parsed is None:
            facts=[];relations=[]
        else:
            if json.loads(a['raw_response'])!=parsed:raise ValueError(f'{name}: parsed differs from response')
            if interface.analyze(a['prepared_input'],parsed)!=r:
                raise ValueError(f'{name}: offline reanalysis differs from saved result')
            facts=parsed.get('facts',[]) if isinstance(parsed.get('facts'),list) else []
            relations=parsed.get('relations',[]) if isinstance(parsed.get('relations'),list) else []
            for alignment in r['alignments']:
                if alignment.get('semantic_support')!='unknown':raise ValueError('model self-authorized semantics')
            for candidate in r['plan']['candidate_coverage']:
                if not candidate['judgments']:raise ValueError('candidate has no judgment')
                for judgment in candidate['judgments']:
                    if not judgment['outputs']:raise ValueError('candidate has no output')
                    for ref in judgment['outputs']:
                        item=r['plan'][ref['category']][ref['index']]
                        if (item.get('candidate_index'),item.get('judgment_kind'))!=(candidate['candidate_index'],judgment['kind']):
                            raise ValueError('candidate output pointer mismatch')
        for key,seq in [('facts',facts),('relations',relations)]:
            hr=human[key]
            if len(hr)!=len(seq):raise ValueError(f'{name}: missing {key} independent review')
            for i,item in enumerate(seq):
                if hr[i]['sha256']!=digest(item):raise ValueError(f'{name}: stale review {key}[{i}]')
        for component in ('schema','quote','basis','coverage'):
            metrics[component+'_passed']+=int(v.get(component+'_status')=='passed')
        supported_f=sum(x['verdict']=='supported' for x in human['facts']);supported_r=sum(x['verdict']=='supported' for x in human['relations'])
        metrics['facts']+=len(facts);metrics['facts_supported']+=supported_f;metrics['relations']+=len(relations);metrics['relations_supported']+=supported_r
        metrics['fact_core_supported']+=sum(x['core_verdict']=='supported' for x in human['facts'])
        metrics['fact_partial']+=sum(x['verdict']=='partial' for x in human['facts'])
        metrics['relation_partial']+=sum(x['verdict']=='partial' for x in human['relations'])
        add(f"| {name} | {call.get('status')} / {call.get('elapsed_seconds')} | {usage.get('prompt_tokens','—')}/{usage.get('completion_tokens','—')}/{usage.get('total_tokens','—')} | {v.get('schema_status','未检查')} | {v.get('quote_status','未检查')} | {v.get('basis_status','未检查')} | {len(facts)}/{len(relations)} | {supported_f}/{supported_r} |")
    add('')
    add(f"独立审核：事实 {metrics['facts_supported']}/{metrics['facts']} 条、旧关系 {metrics['relations_supported']}/{metrics['relations']} 条完整受支持；事实内核受支持 {metrics['fact_core_supported']}/{metrics['facts']}，整条部分支持的事实 {metrics['fact_partial']} 条、关系 {metrics['relation_partial']} 条。完整判断按模型同时给出的值、来源、条件、理由和时间关系审查；只证实核心事实不能消除其他未证实字段。结构通过 {metrics['schema_passed']}/5，引文定位通过 {metrics['quote_passed']}/5，这些数字只反映五案与所选审核标准，不是准确率。")
    add('')
    for name in NAMES:
        a=cases[name];h=reviews['cases'][name];p=a['prepared_input'];r=a.get('result') or {};v=r.get('validation') or {};parsed=r.get('parsed');old=load(OLD/(name+'.json')); old_review=prior['cases'][name];baseline=load(COVERAGE/'results'/(name+'.json'))
        add(f'## {name}');add('')
        m=p['source_texts']['memory'];add(f"旧记忆 `{m['source_id']}`（`{m['source_ref']}`）：{m['text']}");add('')
        selected={u['source_id'] for u in p['new_units']}
        for s in p['source_texts']['messages']:
            if s['source_id'] in selected:add(f"- 新证据 `{s['source_id']}`（`{s['source_ref']}`）：{s['text']}")
        add('')
        add(f"v4：结构 `{old['result']['validation']['schema_status']}`，引文 `{old['result']['validation']['quote_status']}`，依据绑定 `{old['result']['validation']['basis_status']}`；严格 A 计划 `{j(counts(baseline['groups']['A']['old_plan']))}`；放开授权的 B 候选计划 `{j(counts(baseline['groups']['B']['old_plan']))}`。既有审核：{old_review['overall']}")
        add('')
        add('原人工预期（非模型输入、非用户确认金标准）：')
        expected=load(interface.ROOT/'variants/evidence_scope_planner/v2_offline/fixtures'/(name+'.expected.json'))
        for k in ('modify','preserve','uncertain','add'):add(f"- {k}: {'；'.join(expected.get(k,[])) or '无'}")
        add('')
        add('事实提取完整性：')
        for t in h['coverage']:
            add(f"- **{t['verdict']}**：{t['target']}；模型事实 `{j(t['fact_ids'])}`。{t['reason']}")
        add('')
        if parsed is None:
            add('本案没有可解析的模型对象；无法进行候选回放或逐项语义审核。');add('');continue
        facts=parsed.get('facts',[]) if isinstance(parsed.get('facts'),list) else []
        rels=parsed.get('relations',[]) if isinstance(parsed.get('relations'),list) else []
        add(f"v5 自动校验：结构 `{v.get('schema_status')}`，引文 `{v.get('quote_status')}`，依据绑定 `{v.get('basis_status')}`，单元覆盖 `{v.get('coverage_status')}`。错误：`{j(v.get('errors'))}`。")
        add('')
        for section,records in [('facts',facts),('relations',rels)]:
            add('### '+('新事实：独立语义审核' if section=='facts' else '旧关系：独立语义审核'));add('')
            if not records:add('无。');add('')
            for i,rec in enumerate(records):
                hrec=h[section][i];origin_index=i if section=='facts' else len(facts)+i
                add(f"**{section}[{i}]**：`{j(rec)}`")
                add('')
                checks=[q for q in v.get('quote_checks',[]) if q['record_index']==origin_index]
                for q in checks:
                    source=m if q['source_id']==m['source_id'] else next((s for s in p['source_texts']['messages'] if s['source_id']==q['source_id']),{})
                    add(f"- 引文 `{q['side']}/{q['source_id']}/{q['unit_id']}`：`{q['status']}`，位置 `{j(q['position'])}`，来源 `{source.get('source_ref')}`，逐字「{fmt(q['quote'])}」。{q.get('reason') or ''}")
                add(f"- 独立审核 **{hrec['verdict']}**（事实或关系内核 `{hrec['core_verdict']}`）：{hrec['reason']}")
                plan=r['plan'];coverage=plan['candidate_coverage'][origin_index]
                for jd in coverage['judgments']:
                    dest=[]
                    for ref in jd['outputs']:
                        item=plan[ref['category']][ref['index']]
                        dest.append(f"{ref['category']}[{ref['index']}]（{fmt(item.get('reason'))}）")
                    add(f"- 输出去向 `{jd['kind']}`："+'；'.join(dest))
                add('')
        plan=r['plan'];add(f"规划结果：`{j(counts(plan))}`；可编辑位置 `{j(plan['editable_spans'])}`。")
        extras=plan['candidate_coverage'][len(facts)+len(rels):]
        for cv in extras:
            add(f"- 适配器补充的缺失单元候选 `{cv['candidate_index']}`：`{j(cv['judgments'])}`。")
        add('')
        add(f"对比与限制：{h['comparison']}");add('')
    add('## 复现与限制');add('')
    add('离线复核不调用模型：');add('```sh');add('PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v');add('PYTHONDONTWRITEBYTECODE=1 python make_report.py');add('```');add('')
    add('事实完整性按本报告逐案列出的人工核对目标判断，不能保证枚举源对话中的全部细节。人工语义审核不改变默认计划；如需安全执行更新，仍需要单独的授权和写入方案。本次不把有依据的新事实等同于允许修改旧事实。')
    (HERE/'REPORT.md').write_text('\n'.join(out)+'\n',encoding='utf-8')
    print('wrote REPORT.md',j(dict(metrics)))
if __name__=='__main__':main()
