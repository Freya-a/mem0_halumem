"""Render both planners' same-input replays and independent source reviews."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[2]
RUN=PROJECT/'variants/evidence_aligner/v4_scope_interface/runs/qwen_20261124_once'
V4=RUN.parents[1]
CASES=('susan','promotion','career_history','transition','skydiving')
CATS=('modify','preserve','uncertain','add')

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()

def count(plan):
    return '/'.join(str(len(plan.get(k,[]))) for k in CATS)

def brief(item):
    keys=('unit_id','fact','relation','old_value','new_value','value','scope','reason','temporal_order',
          'semantic_support','validation_errors','missing_reasons','old_quote','new_quote','old_position','new_position',
          'source_id','source_ref','memory_id','old_source_ref')
    out={k:item[k] for k in keys if k in item and item[k] not in (None,[], '')}
    for side in ('old','new'):
        if item.get(side+'_quotes'):
            out[side+'_quotes']=[{k:q[k] for k in ('unit_id','source_id','source_ref','quote','position','status','reason') if k in q} for q in item[side+'_quotes'] if isinstance(q,dict)]
    return out

def range_review(reviews,case,proj,version,plan):
    review=reviews.get(case,{}).get(proj,{}).get(version,{})
    if review.get('plan_sha256')!=digest(plan):
        return {'verdict':'not_reviewed','reason':'独立审核缺失或计划变化，须重新审核。'}
    return review

def main():
    manifest=json.loads((HERE/'results/manifest.json').read_text(encoding='utf-8'))
    models=json.loads((V4/'human_reviews.json').read_text(encoding='utf-8'))['cases']
    reviewfile=HERE/'RANGE_REVIEW.json'
    reviews=json.loads(reviewfile.read_text(encoding='utf-8')).get('cases',{}) if reviewfile.exists() else {}
    data={c:json.loads((HERE/'results'/f'{c}.json').read_text(encoding='utf-8')) for c in CASES}
    oldsum=json.loads((RUN/'review_summary.json').read_text(encoding='utf-8'))
    out=['# 五案离线范围回放对照','',
         '五案同批保存的 v4 响应分别以首次冻结的未防护适配器与后续防护适配器投影；每组内把同一输入深拷贝给 v2 与 v3，输入 SHA-256 相等。未防护组 v2 与首次保存计划完全一致，防护组 v2 与 17 条 offline_safe 结果完全一致。本次不调用模型，未注入人工预期或独立语义授权。17 条逐项追踪见 [TRACE_17.md](TRACE_17.md)。','',
         '数字为条目数，顺序为 modify / preserve / uncertain / add；可能是对同一事实的多个原因，不能当准确率。主要算法比较应看相同的未防护投影；v4 防护投影因兼容旧版会丢失可供 v3 判断的有限范围信息，两种投影不可混为一谈。','',
         '## 接口、引文与语义审核分别统计','',
         f"- 已保存响应 {oldsum['case_count']} 案；原调用 {oldsum['request_attempts']} 次，本次回放新增 {manifest['model_calls']} 次。",
         f"- 原模型字段结构通过 {oldsum['structured_passed']}/5 案；完整接口校验通过 {oldsum['complete_validation_passed']}/5 案。",
         f"- 主引文来源定位通过 {oldsum['quote_checks'].get('valid',0)}/{sum(oldsum['quote_checks'].values())} 条；依据绑定通过 {oldsum['basis_passed_cases']}/5 案。引用可定位不证明语义。"]
    verdicts=Counter()
    for c,d in data.items():
        for i,record in enumerate(d['raw_model_output']['records']):
            r=models.get(c,{}).get('records',{}).get(str(i),{})
            verdicts[r.get('verdict','not_reviewed') if r.get('sha256')==digest(record) else 'not_reviewed']+=1
    out += ['- 独立人工记录审核（按原模型记录散列绑定）：'+ '；'.join(f'{k}={v}' for k,v in sorted(verdicts.items()))+'。未输出的事实不计入该分母。','',
            '## 防护后 17 项待确认的原因', '',
            '逐条的模型判断、原引文、适配结果及 v2 拒绝原因见 [TRACE_17.md](TRACE_17.md)。按可重叠类别统计：①模型语义错误或依据不足 17 项；②字段、引文绑定或来源问题 9 项；③缺少独立语义授权 17 项；④范围无法可靠计算或条件未知 4 项；⑤其他原因 2 项。类别不互斥，不能相加得 17；某一子事实有证据，不等于整条关系和时间判断有证据。', '',
            '## 独立构造的新增和修改路径', '',
            '通用测试 `tests/test_paths.py` 不使用五案输入或预期。新增案例是用户明确说喜欢茶：没有独立授权时 add=0 且待确认；独立审核确认既有主张与引文后 add=1。修改案例是旧“房间关闭”，新文明确说“之前关闭、现在开放”：无需具体日历日期，未授权时 modify=0，独立审核绑定原有引文后 modify=1，位置为旧文中 closed。两次审核只改变独立授权标志，并未改写模型候选字段。可运行 `python -m unittest discover -s tests -p test_paths.py -v` 复验。', '',
            '## 逐案数量对照','','| 案例 | 未防护 v2 | 未防护 v3 | 防护后 v2 | 防护后 v3 |','| --- | --- | --- | --- | --- |']
    for c,d in data.items():
        p=d['projections'];out.append(f"| {c} | {count(p['unprotected']['v2'])} | {count(p['unprotected']['v3'])} | {count(p['guarded']['v2'])} | {count(p['guarded']['v3'])} |")
    out += ['', '## 逐案证据与范围结论','']
    for c,d in data.items():
        pay=d['prepared_input'];memory=pay['source_texts']['memory']; linked={u['source_id'] for u in pay['new_units']}
        v=d['validation'];out += [f'### {c}','',f"旧记忆：{memory['text']}（`{memory['source_id']}`，`{memory.get('source_ref')}`）",'','选中新证据：','']
        for src in pay['source_texts']['messages']:
            if src.get('source_id') in linked:out.append(f"- `{src['source_id']}`：{src['text']}（`{src.get('source_ref')}`）")
        expected_path=PROJECT/'variants/evidence_scope_planner/v2_offline/fixtures'/f'{c}.expected.json'
        expected=json.loads(expected_path.read_text(encoding='utf-8'))
        out += ['', f"原模型校验：schema={v.get('schema_status')}；quote={v.get('quote_status')}；basis={v.get('basis_status')}；coverage={v.get('coverage_status')}；overall={v.get('status')}。",'',
                f"已有独立人工预期（仅供比较，未输入规划器）：`{canonical(expected)}`。",'',
                f"已有独立人工整体评审：{models.get(c,{}).get('overall','未审')}。",'']
        for i,rec in enumerate(d['raw_model_output']['records']):
            rev=models.get(c,{}).get('records',{}).get(str(i),{})
            if rev.get('sha256')!=digest(rec):rev={'verdict':'not_reviewed','reason':'原模型记录与审核散列不符'}
            keys=('unit_id','relation','old_subject','new_subject','old_attribute','new_attribute','old_value','new_value','old_conditions','new_conditions','modality','old_quotes','new_quotes','temporal_order','semantic_rationale','semantic_basis','uncertainties')
            out += [f'模型记录 {i}；独立人工审核：{rev.get("verdict")}；{rev.get("reason")}。','','```json',json.dumps({k:rec.get(k) for k in keys},ensure_ascii=False,indent=2),'```','']
        for proj in ('unprotected','guarded'):
            p=d['projections'][proj]
            assert p['v2_input_sha256']==p['v3_input_sha256']
            out += [f'**{proj} 投影**：两代规划器同一输入 SHA-256 `{p["input_sha256"]}`，v2 结果与原存档一致。','']
            for ver in ('v2','v3'):
                plan=p[ver];rev=range_review(reviews,c,proj,ver,plan)
                out += [f'**{ver}**（{count(plan)}；独立范围审核：{rev.get("verdict")}）：{rev.get("reason")}','']
                for cat in CATS:
                    out.append(f'- {cat}（{len(plan.get(cat,[]))}）：')
                    for i,item in enumerate(plan.get(cat,[])):out.append(f'  - #{i} `{canonical(brief(item))}`')
                out += [f"- 可编辑位置：`{canonical(plan.get('editable_spans',[]))}`",f"- 保护事实：`{canonical([brief(x) for x in plan.get('protected_facts',[])])}`",f"- 引文检查：`{canonical(plan.get('quote_checks',[]))}`",'']
        if c in ('promotion','transition'):
            out += ['**时间说明：** 以上新引文证明事件已发生；`recently` / `finally` 不能单独确定新状态晚于旧记忆的事实有效时间。缺具体日期与先后未知是两回事；本案先后不足以授权覆盖。','']
    out += ['## 限制','', '未经独立语义授权的模型候选不会被当作已审核事实；模型组没有修改或新增，并不意味着接口无可走通路径。独立构造的通用新增及修改用例见 README。不可计算的范围必须待确认，模型拟定的有限组合不能自动视为正确；尤其跳伞模型把模拟与团建列为同一维度两个值，不足以证明是互斥分类。', '', '一个复合 unit 中不同主体或属性的多个关系可能被合并、保守误判为值冲突，产生过多待确认；当前版本不具备完整的复合事实消歧能力，需要拆分或人工复核。','']
    (HERE/'REPORT.md').write_text('\n'.join(out),encoding='utf-8')
    print('rendered',len(CASES),'cases; record audit',dict(verdicts))

if __name__=='__main__':main()
