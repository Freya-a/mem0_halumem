"""Render saved replay data; human review is read-only, never used by engines."""
import json
import hashlib
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
CASES=('promotion','susan','transition','career_history','skydiving')
VERSIONS=('v1','v2','v3')
PLANNERS=('planner_v1','planner_v2')
ACTIONS=('modify','preserve','uncertain','add','editable_spans','protected_facts')
COMMENTS={
'promotion':'两侧均显示同一雇主且新证据明确晋升，旧职位历史和宽泛称谓应保护；记录时间或 recently 本身不能确定与旧快照的事实先后。无日历日期并非事件未发生；先后无法证明时暂缓当前值编辑。',
'susan':'旧记忆支持朋友与鼓励；新证据支持 Susan 的帮助但不单独确认全名映射。Daniel 的见解和求职目标可独立表述，目标不能升级为已完成。',
'transition':'确实已转至新角色，但新句不证明已停止任何求职，平衡目标仍须保护。旧侧 lately 若来自旧上下文应保持对应 source_id；记录时间不自动等于事实生效时间。',
'career_history':'旧文已是历史经历，咨询公司获客不推翻历史雇主与职称，也不证明当前正式角色或所有权。v1/v3 的历史项 state_change 缺证；模型与人工覆盖的新增内容不同。',
'skydiving':'新句为模拟体验，不足以否定真实极限运动态度及受伤风险理由；仍重视安全也不能单独证明完整冲突关系。真实 SimpleMem 单元重叠、u3 的短引文只覆盖部分关系。'}


def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True)
def item_hash(item):
    return hashlib.sha256(j(item).encode('utf-8')).hexdigest()


def entries(plan):
    for category in ACTIONS:
        for i,item in enumerate(plan.get(category, [])):
            yield category,i,item


def plan_lines(out, title, plan, reviews, prefix):
    out.append('**'+title+'**')
    for category in ACTIONS:
        xs=plan.get(category,[])
        out.append(f'- {category}（{len(xs)}）：')
        for i,x in enumerate(xs):
            key='|'.join((*prefix,category,str(i)))
            review=reviews.get(key,{'verdict':'not_reviewed','reason':'尚未逐条人工审核。'})
            if review.get('item_sha256') != item_hash(x):
                review={'verdict':'not_reviewed','reason':'无匹配审核或输出已变化；须重新人工核对。'}
            out.append(f'  - #{i} {j(x)}；人工审核：{j(review)}')
    checks=plan.get('quote_checks',[])
    out.append(f'- 规划器引文检查（{len(checks)} 项，可能包含其他阻断原因，不等于独立逐字匹配率）：{j(checks)}')
    out.append('')


def main():
    review=json.loads((HERE/'SEMANTIC_REVIEW.json').read_text(encoding='utf-8'))
    all_results={case:json.loads((HERE/'results'/f'{case}.json').read_text(encoding='utf-8')) for case in CASES}
    out=['# 离线五案：三版对齐器与两代范围规划器', '',
         '两组人工对齐分别用各自目录 fixtures；模型组为五案 × 三版保存结果，分别输入两代适配器和规划器，均在本机离线运行。人工预期与独立语义审核不参与规划器输入。人工审核标准及标签定义见 [SEMANTIC_CRITERIA.md](SEMANTIC_CRITERIA.md)，来源见 [SOURCES.md](../v1_offline/SOURCES.md)。输入字段和人工标注变化会影响结果，不能将差异全归因于程序。', '',
         '下列计数均非准确率：原始记录以 parsed.records 为分母；原始引用以每条 old_quotes/new_quotes 中每个元素为分母。源唯一有效要求来源可消歧、该 side 正确、原始磁盘路径可核对且引文在指定来源内唯一；它不证明引文支持语义。列表保留是适配器 resolved_*_quotes 含原引文文本；列表来源解析要求引文和 source_id 均保留；标量文本列只计 old_quote/new_quote 文本投影；标量来源有效列还核对 source_id、侧别、原始磁盘及唯一命中。v1 多引文可能保留在元数据列表但被标量规划器丢弃，v2 列表可送下游，来源绑定错误仍须暂缓。原模型未产生的引文不计入分母，另列缺引文的记录。', '']
    agg={}
    for version in VERSIONS:
      for engine in PLANNERS:
        counts=Counter();records=0;missing=0;missing_old=0;projected=0;model_actions=Counter()
        for res in all_results.values():
          m=res['models'][version]; records+=m['raw_record_count'];e=m['engines'][engine]
          counts.update(e['counts']); projected += e.get('projected_record_count',0)
          model_actions.update({k:len(e['plan'].get(k,[])) for k in ('modify','preserve','uncertain','add')})
          raw=[x for x in e['projection'] if x.get('raw_record') is not None]
          missing+=sum(not (x['raw_record'].get('new_quotes') or []) for x in raw)
          missing_old+=sum(bool(x['raw_record'].get('old_unit_ids')) and not (x['raw_record'].get('old_quotes') or []) for x in raw)
        agg[(version,engine)]=(records,missing,missing_old,counts,projected,model_actions)
    all_actions = []
    for case, res in all_results.items():
        for engine, plan in res['human_alignment'].items():
            all_actions.extend((case, 'human', engine, cat, i, item) for cat, i, item in entries(plan))
        for version, model in res['models'].items():
            for engine, values in model['engines'].items():
                all_actions.extend((case, version, engine, cat, i, item) for cat, i, item in entries(values['plan']))
    matched = sum(1 for case,g,e,c,i,item in all_actions if review['output_reviews'].get('|'.join((case,g,e,c,str(i))),{}).get('item_sha256') == item_hash(item))
    out += [f'规划器动作和位置输出审核分母 {len(all_actions)}，匹配人工审核 {matched}，未审核或结果变化 {len(all_actions)-matched}；原模型记录以每版 parsed 记录总数为分母，逐记录标注列在各案。', '']
    model_verdicts = {version: Counter(row['verdict'] for case in CASES for row in review['records'][case][version]) for version in VERSIONS}
    action_verdicts = {}
    for case,g,e,c,i,item in all_actions:
        key='|'.join((case,g,e,c,str(i)))
        annotation=review['output_reviews'].get(key,{})
        verdict=annotation.get('verdict','not_reviewed') if annotation.get('item_sha256') == item_hash(item) else 'not_reviewed'
        group='human' if g=='human' else 'model'
        action_verdicts.setdefault((e,group,c),Counter())[verdict]+=1
    out += ['## 独立人工审核统计', '', '以下按每一条输出计数，评语来自独立人工审核，审查分母及逐条结论固定在 SEMANTIC_REVIEW.json；同一语义事实跨版本或保护位置会重复计数。判断用于研究，不是准确率；缺失的事实不在输出分母中。', '', '| 原模型版本 | 原记录总数 | supported | partial_or_unknown | unsupported |', '|---|---:|---:|---:|---:|']
    for version,counts in model_verdicts.items():
        out.append(f"| {version} | {sum(counts.values())} | {counts['supported']} | {counts['partial_or_unknown']} | {counts['unsupported']} |")
    out += ['', '规划器动作（modify、preserve、uncertain、add）的分母与位置（editable_spans、protected_facts）分别列出，避免混算；appropriate_with_limit 的具体限制见逐条评语。', '', '| 规划器 | 组 | 类别 | 总条数 | 审核结论及条数 |', '|---|---|---|---:|---|']
    for (engine,group,category),counts in sorted(action_verdicts.items()):
        out.append(f"| {engine} | {group} | {category} | {sum(counts.values())} | {', '.join(f'{k}={v}' for k,v in sorted(counts.items()))} |")
    out.append('')
    out+=['## 客观接口与引文统计','', '| 模型 | 规划器 | 原记录 | 已投影记录 | 缺新引文记录 | 有旧单元但缺旧引文 | 原引文 | 来源唯一有效 | 列表文本保留 | 列表来源解析 | 标量文本 | 标量来源有效 | 列表未解析 |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for (v,p),(n,m,mo,c,projected,acts) in agg.items():
        out.append(f"| {v} | {p} | {n} | {projected} | {m} | {mo} | {c['raw_quotes']} | {c['unique_correct_side_on_disk']} | {c['list_text_retained']} | {c['list_resolved_with_source']} | {c['scalar_projection']} | {c['scalar_source_valid']} | {c['source_unresolved_in_list']} |")
    out += ['', '模型组实际规划条目数：已投影并不表示可以操作；条件、相对先后或人工语义依据缺失时应当暂缓。', '', '| 模型 | 规划器 | modify | preserve | uncertain | add |', '|---|---|---:|---:|---:|---:|']
    for (v,p),(_,_,_,_,_,acts) in agg.items():
        out.append(f"| {v} | {p} | {acts['modify']} | {acts['preserve']} | {acts['uncertain']} | {acts['add']} |")
    out+=['','每项原引文及具体解析结果保存在 results/{case}.json 的 quote_audit；未解析原因及源头错误保存在对应 projection 和 plan。', '']
    for case in CASES:
        d=json.loads((HERE/'fixtures'/f'{case}.json').read_text(encoding='utf-8'))
        expect=json.loads((HERE/'fixtures'/f'{case}.expected.json').read_text(encoding='utf-8'))
        res=all_results[case]
        out += [f'## {case}','',f"旧记忆：{d['old_memory']}",f"来源：`{d['memory_id']}`，`{d['old_memory_source_ref']}`。",'', '新证据：']
        for s in d['sources']:out.append(f"- {s['source_id']}：{s['text']}（`{s['source_ref']}`）")
        out += ['','人工独立预期：'+j({k:expect[k] for k in ('modify','preserve','uncertain','add','missing')}),'']
        for engine in PLANNERS:plan_lines(out,'人工对齐输入 → '+engine,res['human_alignment'][engine],review['output_reviews'],(case,'human',engine))
        for version in VERSIONS:
            model=res['models'][version]
            out += [f'### 保存的模型 {version}（原结构状态 {model["upstream_status"]}；记录 {model["raw_record_count"]}）','',f'来源：`{model["artifact"]}`。','']
            for r in review['records'][case][version]:out.append(f"- 原记录 #{r['record_index']} 独立语义审核：{r['verdict']}；{r['reason']}")
            out.append('')
            for engine in PLANNERS:
                e=model['engines'][engine]
                out.append('引文客观计数 '+engine+'：'+j(e['counts']))
                plan_lines(out,version+' → '+engine,e['plan'],review['output_reviews'],(case,version,engine))
        out+=['差异和限制：'+COMMENTS[case], '']
    demo=json.loads((HERE/'results'/'multidimensional.json').read_text(encoding='utf-8'))
    out += ['## 多维条件组合验证', '', '合成新证据明确说明此前旧政策、现在上海外带改为新政策；逐组合计算结果：', '', '修改：'+j([x['scope'] for x in demo['modify']]), '', '保留：'+j([x['scope'] for x in demo['preserve']]), '']
    out+=['## 范围与限制','','人工判断是研究者根据引文作出的初评，不能自动证明真实世界事实；`not_reviewed` 明确表示尚未完成逐项人工核对。模型输出中缺少的事实及由不同拆分粒度导致的遗漏，不能由逐条正确数反映。已有材料选取部分新对话，不代表全会话或全量数据。具体源文件、快照、上下文及 SimpleMem 覆盖差异见 SOURCES.md。','',
          '方法借鉴先判断后修订、时间有效性与条件重叠的思路；未调用或移植 ERASE、FactTrack、Cedar 的模块。日期区间和自然语言蕴含依赖上游明确标注；未知时间顺序不能从记录时间补成先后。','']
    (HERE/'REPORT.md').write_text('\n'.join(out),encoding='utf-8')
    (HERE/'results'/'interface_counts.json').write_text(j({v:{p:{'records':n,'missing_new_quotes_records':m,'missing_old_quotes_records':mo,'projected_records':projected,'planner_actions':dict(acts),**dict(c)} for (vv,p),(n,m,mo,c,projected,acts) in agg.items() if vv==v} for v in VERSIONS})+'\n',encoding='utf-8')

if __name__=='__main__':main()
