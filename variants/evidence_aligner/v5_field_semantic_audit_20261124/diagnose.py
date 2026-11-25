"""Offline, hash-bound field attribution. No planner inputs are modified."""
from pathlib import Path
from collections import Counter
import hashlib,json
from annotations import DATA

HERE=Path(__file__).resolve().parent
V5=HERE.parent/'v5_fact_relations'
RUN=V5/'runs/qwen_20261124_once'
NAMES=('susan','promotion','career_history','transition','skydiving')
K={'facts':'事实','relations':'关系'}

def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def j(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def pretty(x):return json.dumps(x,ensure_ascii=False,indent=2)

# The following marks *unsupported* temporal/causal implications, not the
# mere presence of a valid temporal expression or a sourced causal claim.
BAD_TIME={('promotion','facts','f1'),('promotion','facts','f2'),('promotion','relations','r1'),('promotion','relations','r2'),
          ('career_history','facts','f3'),('career_history','relations','r1'),('career_history','relations','r2'),
          ('transition','facts','f1'),('transition','relations','r1'),('transition','relations','r2'),
          ('skydiving','facts','f6'),('skydiving','relations','r1'),('skydiving','relations','r2'),
          ('skydiving','relations','r3'),('skydiving','relations','r4'),('skydiving','relations','r5')}
RATIONALE_ONLY={('promotion','facts','f1'),('skydiving','facts','f3'),('skydiving','facts','f6')}
CONTRACT={('susan','facts','f6'),('susan','relations','r1'),('susan','relations','r2'),('susan','relations','r3'),('susan','relations','r4'),
          ('promotion','facts','f1'),('promotion','facts','f2'),('promotion','facts','f3'),('promotion','relations','r1'),('promotion','relations','r2'),
          ('career_history','facts','f3'),
          ('skydiving','relations','r3'),('skydiving','relations','r4'),('skydiving','relations','r5')}
# Previous review flagged unconditional without identifying comparison axes;
# reassessment is necessary, not an automatic reversal of its verdict.
RUBRIC_REVIEW={('susan','facts','f1'),('susan','facts','f2'),('susan','facts','f3'),('susan','facts','f5'),('susan','relations','r2'),
               ('promotion','facts','f1'),('promotion','facts','f2'),('promotion','facts','f3'),
               ('career_history','facts','f4'),('transition','facts','f2'),
               ('skydiving','facts','f1'),('skydiving','facts','f2'),('skydiving','facts','f3'),('skydiving','facts','f4'),('skydiving','facts','f5'),('skydiving','facts','f6')}

# Explanatory fragments from the analyst, not outputs from the model and not
# inputs to the adapter. They are intentionally not complete v5 records.
EXAMPLES={
 'susan':({'subject':'current role','attribute':'support for well-being',
           'value':"not as much as I'd like",'conditions':{'kind':'unknown'}},
          'current 已在主体中、比较对象已在值中；若尚未确定参与比较的其他轴，unknown 不会抹去这些词。找新工作的两个要求需分别核对且保留同一职位的合取。'),
 'promotion':({'subject':'I','attribute':'promotion event',
               'value':'recently promoted to lead director at Historical Productions Ltd.',
               'conditions':{'kind':'unknown'},'old_relation':'unknown','temporal_order':{'relation':'unknown'}},
              'recently 是相对话语的事件时间；与旧 Director 的先后和是否排斥另判。old_relation 为解释性标签，不是 v5 事实字段。'),
 'career_history':({'subject':'my consulting firm','attribute':'initial clients',
                    'value':'secured some initial clients','conditions':{'kind':'unknown'}},
                   '主语忠于“my consulting firm”，并不声明用户是所有者或创办者；获客事实不能由 founder/owner 的原候选改一个条件字段就得到。'),
 'transition':({'subject':'I','attribute':'career event','value':'transitioned to a new role',
                'conditions':{'kind':'unknown'},'old_relation':'unknown','temporal_order':{'relation':'unknown'}},
               '已转岗是事实事件，是否仍求职未知；不把该值改写为 no longer searching。old_relation 为说明，非事实 schema 字段。'),
 'skydiving':({'subject':'I','attribute':'simulated skydiving experience',
               'value':'tried simulated skydiving at a team-building event recently',
               'conditions':{'kind':'finite','dimensions':{'activity_mode':['simulated']}}},
              '仅在 activity_mode 是已选比较轴并约定 simulated 的规范含义时，可以给新事实 finite；旧记忆未明确同一轴取值，不能据此推断旧真实偏好改变或求出旧范围。')}


def main():
    old=load(V5/'HUMAN_REVIEW.json');manifest=load(RUN/'manifest.json');pre=load(V5/'PRECALL.json')
    prompt=(RUN/'frozen_at_call/prompt.txt').read_text(encoding='utf-8')
    if hashlib.sha256(prompt.encode()).hexdigest()!=manifest['prompt_sha256']:raise ValueError('request prompt does not match manifest')
    snapshots=RUN/'frozen_at_call'
    for original,expected in pre['files_sha256'].items():
        source=Path(original);name=source.name
        if source.parent.name=='frozen_at_call' and name=='interface.py':name='v4_frozen_interface.py'
        elif source.parent.name=='v4_scope_interface' and name=='runner.py':name='v4_runner.py'
        elif source.parent.name=='candidate_coverage_20261124':name='coverage_scope_planner.py'
        if hashlib.sha256((snapshots/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'pre-call code snapshot changed: {name}')
    cases={};rows=[]
    for case in NAMES:
        path=RUN/(case+'.json');artifact=load(path);req=artifact['request'];response=artifact['raw_response'];parsed=artifact['result']['parsed']
        if req['messages'][0]['content']!=prompt or json.loads(req['messages'][1]['content'])!=artifact['prepared_input']:
            raise ValueError(f'{case} request not bound to saved input/prompt')
        rawobj={k:v for k,v in req.items() if k not in ('sha256','messages_sha256')}
        if digest(rawobj)!=req['sha256'] or digest(req['messages'])!=req['messages_sha256']:
            raise ValueError(f'{case} request hash mismatch')
        if json.loads(response)!=parsed or hashlib.sha256(response.encode()).hexdigest()!=old['cases'][case]['raw_sha256']:
            raise ValueError(f'{case} response or prior review hash mismatch')
        provider=artifact.get('provider_response') or {}; choices=provider.get('choices') or []
        if choices and choices[0].get('message',{}).get('content')!=response:raise ValueError(f'{case} provider response mismatch')
        existing=artifact['result']['alignments']
        if any(x.get('semantic_support')!='unknown' for x in existing):raise ValueError(f'{case} semantic support is not unknown')
        assert len(parsed['facts'])==len(DATA[case]['facts']) and len(parsed['relations'])==len(DATA[case]['relations'])
        bundle={'source':artifact['prepared_input']['source_texts'],'new_units':artifact['prepared_input']['new_units'],
                'old_units':artifact['prepared_input']['old_units'],'request_sha256':req['sha256'],
                'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'facts':[],'relations':[]}
        for section in ('facts','relations'):
            for i,(model,annotation) in enumerate(zip(parsed[section],DATA[case][section])):
                prior=old['cases'][case][section][i]
                if digest(model)!=prior['sha256']:raise ValueError(f'{case}/{section}/{i} prior human review mismatch')
                typ,reco,expand,temporal,schema=annotation
                ident=model['fact_id' if section=='facts' else 'relation_id'];key=(case,section,ident)
                raw_scope=model['conditions' if section=='facts' else 'old_conditions']
                row={'case':case,'record_type':section,'index':i,'id':ident,'record_sha256':digest(model),
                     'raw_model_output':model,'prior_review':prior,
                     'core_verdict':prior['core_verdict'], 'scope_class':typ,
                     'raw_scope':raw_scope,'scope_recommendation':reco,'expansion':expand or None,
                     'temporal_causal_analysis':temporal or '未发现该记录对未证实的时间先后或因果关系作出独立断言；不表示不存在所有语义问题。',
                     'field_standard_analysis':schema or '此项未发现额外字段定义问题；整体语义仍须独立审核。',
                     'flags':{'core_not_fully_supported':prior['core_verdict']!='supported',
                              'subject_identity_value_expansion':bool(expand) and key not in RATIONALE_ONLY,
                              'rationale_only_expansion':bool(expand) and key in RATIONALE_ONLY,
                              'explicit_qualifier_missing_or_broadened':typ=='lost',
                              'unrestricted_scope_not_explicitly_proven':raw_scope.get('kind')=='unconditional',
                              'unsupported_temporal_or_causal_inference':key in BAD_TIME,
                              'concrete_schema_or_mapping_issue':key in CONTRACT,
                              'prior_scope_rubric_needs_axis_clarification':key in RUBRIC_REVIEW}}
                rows.append(row);bundle[section].append(row)
        cases[case]=bundle
    assert len(rows)==36 and sum(x['record_type']=='facts' for x in rows)==21
    assert all(x['raw_scope'].get('kind')=='unconditional' for x in rows)
    metrics=Counter()
    for x in rows:
        metrics['total']+=1;metrics[x['record_type']]+=1;metrics['scope_class.'+x['scope_class']]+=1
        metrics[f"core.{x['record_type']}.{x['core_verdict']}"]+=1
        for f,v in x['flags'].items():metrics['flag.'+f]+=bool(v)
    flag_names=['core_not_fully_supported','subject_identity_value_expansion','explicit_qualifier_missing_or_broadened',
                'unsupported_temporal_or_causal_inference','concrete_schema_or_mapping_issue']
    overlap={}
    for i,left in enumerate(flag_names):
        for right in flag_names[i+1:]:overlap[left+' & '+right]=sum(x['flags'][left] and x['flags'][right] for x in rows)
    metrics['flag.two_or_more_main_categories']=sum(sum(bool(x['flags'][k]) for k in flag_names)>=2 for x in rows)
    output={'method':'离线人工归因；保存旧审核，不改模型输出或规划器，不回填任何自动语义授权。',
            'scope_class_definitions':{'embedded':'原文明示的限定已至少部分位于 subject/attribute/value，仍需审查是否完整；不是证明无条件。',
                                       'lost':'原文明示的相关限定丢失或被扩大；不等于事实整体皆假。',
                                       'unspecified':'当前记录就相关比较范围未提供明确限定；不是证明全部适用。'},
            'metric_definition':'依据本轮逐条人工标注；一个记录可多标签。未经证明的 unconditional 是待核实，不计作必然错误。',
            'metrics':dict(metrics),'pairwise_overlap':overlap,'cases':cases}
    (HERE/'DIAGNOSIS.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    build_report(output,rows)
    print(j(dict(metrics)));print('wrote DIAGNOSIS.json and REPORT.md')


def build_report(data,rows):
    lines=[]
    def add(s=''):lines.append(s)
    add('# v5 五案：字段与语义离线归因');add('')
    add('## 边界、定义和方法');add('')
    add('本报告只读取五案原始请求、原始响应、v5 保存的审核和现有代码；不调用模型或 API，不修改旧结果、Mem0 或真实记忆。逐条核对 21 条事实与 15 条关系。模型原始输出和旧审核原样保留；本轮的字段表达建议是独立人工分析，不输入对齐器、规划器或任何授权链路。请求消息、原始响应、先前审核逐条哈希及代码快照均经校验。')
    add('')
    add('`unconditional` 在 v5 提示词中要求“证据明确无额外适用限制”；在规划器实现中，`_conditions` 把它解析为 `(None, [()])`，其含义是**对本次实际比较的条件维度没有约束**。当旧条件为 unconditional 且新条件为有限范围时，代码将有限范围视为可能重叠，但不把无限余集枚举成完整有限范围。它不是日期字段，也不会自动从 subject、attribute 或 value 中删除 `simulated`、`current`、`recently` 等文字；但是规划器不理解这些文字。如果比较所需的轴没有被结构化或声明，代码也不能自动保证这些限定被纳入范围运算。')
    add('')
    add('应区分三个情况：①原文**明确否定某个已声明比较轴的限制**时，才有证据在该轴上声称无限定，例如“所有指定门店均适用”；这不证明所有时间、主体或其他轴均无限定。②原文对该轴未提及，范围是未知，不能从空白推出无限定。③原文明确“当前”“模拟”“该次活动”等限定时，必须保留该限定；它可能已经在 subject、attribute、value 里，也可能需要在明确且可表示的比较轴上使用 finite。事件日期不明并不自动否定事件或迫使所有语义判断失败。')
    add('')
    add('旧审核全部判为 partial 或 unsupported，其中若干仅笼统说“完整 unconditional 未证”，没有指明相关比较轴；本报告原样保留该结论，并标出需澄清标准的记录。**不能据此倒推 36 条事实都是错误，也不能统一改成 unknown 后宣布正确**：例如模拟限定已在值中，但某些关系仍错误地把模拟体验推成真实偏好变化。')
    add('')
    add('统计的口径：①沿用旧审核的 core_verdict，partial 或 unsupported 计入“内核不完全受支持”；②主体、身份、取值或关系判断存在扩写，另单列仅在理由发现的扩写；③分开统计已知限定丢失/扩大、已编码、原文未提，且把所有 `unconditional` 的证据充分性列为待核实而不自动计错；④只计无依据的时间或因果推断，原话支持的因果不计；⑤记录能具体指出的 schema、映射或提示词契约边界与缺口，包括刻意保守但需解释的映射，另列旧审核标准需明确比较轴。类别允许重叠，计数基于研究者逐条标注，不是性能或准确率。')
    add('')
    m=data['metrics'];add('| 归因口径 | 记录数 / 36 | 说明 |');add('|---|---:|---|')
    labels=[('flag.core_not_fully_supported','①内核未完全支持','沿用旧审核 core_verdict；事实和关系均计'),
            ('flag.subject_identity_value_expansion','②身份、主体、取值或关系扩写','不将仅出现在理由的扩写计入此行'),
            ('flag.rationale_only_expansion','②仅在理由中发现扩写','与上一行分列'),
            ('flag.explicit_qualifier_missing_or_broadened','③原文明示限定丢失或扩大','不把已嵌入值中的限定计入此项'),
            ('flag.unrestricted_scope_not_explicitly_proven','③unconditional 未有逐轴明确的无限定证明','待核实，不等价于 36 项均错误'),
            ('flag.unsupported_temporal_or_causal_inference','④时间或因果推断缺依据','有原文支持的时间及因果不计'),
            ('flag.concrete_schema_or_mapping_issue','⑤具体 schema／映射约束或缺口','含需澄清的保守映射，不均为实现错误'),
            ('flag.prior_scope_rubric_needs_axis_clarification','⑤旧审核范围标准需澄清轴','需复核，不自动推翻旧审核'),
            ('flag.two_or_more_main_categories','至少两类主要原因重叠','主要原因只含①②③明确限定丢失④⑤具体契约')]
    for key,label,description in labels:add(f"| {label} | {m.get(key,0)} | {description} |")
    add('')
    add(f"③限定处理分类：已在主体、属性或值中表达 {m.get('scope_class.embedded',0)} 条；明示限定丢失或扩大 {m.get('scope_class.lost',0)} 条；相应比较范围未提及 {m.get('scope_class.unspecified',0)} 条。36 条原始条件字段均为 unconditional；这不等于 36 条都已被证明错误。")
    add('')
    add('| 主要原因交集 | 记录数 |');add('|---|---:|')
    cn={'core_not_fully_supported':'①内核','subject_identity_value_expansion':'②扩写','explicit_qualifier_missing_or_broadened':'③丢限定',
        'unsupported_temporal_or_causal_inference':'④无依据时序因果','concrete_schema_or_mapping_issue':'⑤契约'}
    for k,v in data['pairwise_overlap'].items():
        a,b=k.split(' & ');add(f'| {cn[a]} ∩ {cn[b]} | {v} |')
    add('')
    add('## 独立语义授权的实际来源');add('')
    add('v5 `interface.analyze()` 对每条适配结果直接设置 `semantic_support="unknown"`；`_new_basis()` 从模型选定的引文机械生成新侧依据，证明可绑定，不证明语义。规划器要求 `semantic_support="supported"` 且语义依据能绑定有效引文，才可能继续处理新增或旧关系；本轮保存的 36 个模型候选均为 unknown。v5 运行流程中 `HUMAN_REVIEW.json` 由事后报告脚本读取，不被 runner 或 adapter 读取，不能算自动授权。当前链路没有产生独立语义授权的组件：要启用该路径，需要另一个可追溯、作用于具体主张的独立审核方及其授权契约；不能把模型的 rationale、引文定位或换名后的模型判断当授权。')
    add('')
    add('另有两个实现边界：新事实新增分支在语义授权等检查通过后，会把 `new_conditions` 原样作为 scope，但不会调用 `_conditions()` 验证 unknown 范围，因此 unknown 不是自动阻止新增的保证；旧关系的范围路径则会对 unknown 标待确认。`unrelated` 还要求 `no_impact_confirmed`，v5 模型 schema 没有提供独立审核签发该字段的路径；模型所称“属性不同”不等价于旧事实已确认不受影响。')
    add('')
    add('## 最少必要修改建议（仅建议，未实施）');add('')
    add('1. **明确现有条件契约和审核口径。** 在提示词、schema 文档和审核表中列出本次要比较的维度及其证据：明确无限定、未提及和有具体限定分别处理；限定已在主体/属性/值中时标明其位置，不要求无意义地重复。只有相关轴明确且有证据时才用 unconditional。若要让代码保证这一点，需要下游共同读取和检查轴与依据，不能只加一段提示词。')
    add('2. **补充事实时间的最小表示，并明确标量与拆分。** 可增加可选、来源绑定的事件时间字段（例如相对发话已发生 / 计划 / 未知及对应引文），保持现有 `temporal_order` 专用于新旧事实有效时间比较；没有必要推断具体日期。明确 `value` 是字符串或 null；对合取要求拆成可核验子事实时保留同一实体及合取关系。现有规划器不会自动消费新增字段，未来需适配、验证与测试。')
    add('3. **在模型外定义独立授权边界。** 分开审核新事实与旧影响，绑定输入记录、引文、范围和审核者/证据；模型理由只能是候选。未获得独立授权的关系保持待确认。保留原始输出与人工作业分离，修补无关关系的 no-impact 授权表达；这不是让审核结果悄悄进入本次自动链路。')
    add('')
    for case,bundle in data['cases'].items():
        add(f'## {case}');add('')
        mem=bundle['source']['memory'];add(f"旧记忆 `{mem['source_id']}`（`{mem['source_ref']}`）：{mem['text']}");add('')
        selected={u['source_id'] for u in bundle['new_units']}
        for s in bundle['source']['messages']:
            if s['source_id'] in selected:add(f"- 选中新话语 `{s['source_id']}`（`{s['source_ref']}`）：{s['text']}")
        add('')
        example, explanation=EXAMPLES[case]
        add(f"字段表达示例（本轮人工解释片段，不是完整 v5 记录，也不输入规划器）：`{j(example)}`。{explanation}")
        add('')
        raw={x['source_id']:x for x in [mem,*bundle['source']['messages']]}
        for section in ('facts','relations'):
            add('### '+('新事实' if section=='facts' else '新旧关系'));add('')
            for row in bundle[section]:
                model=row['raw_model_output'];prev=row['prior_review'];key=row['id'];flags=row['flags']
                add(f"**{K[section]} {key}**（记录哈希 `{row['record_sha256']}`）");add('')
                add('原模型输出：');add('```json');add(pretty(model));add('```')
                if section=='facts':quotes=[('新文',q) for q in model.get('quotes',[])]
                else:
                    fact=next((f['raw_model_output'] for f in bundle['facts'] if f['id']==model.get('fact_id')),None)
                    quotes=[('旧文',q) for q in model.get('old_quotes',[])] + [('关联新事实',q) for q in (fact or {}).get('quotes',[])]
                for side,q in quotes:
                    src=raw.get(q.get('source_id'),{})
                    add(f"- {side}逐字引文 `[{q.get('source_id')}/{q.get('unit_id')}]`：{j(q.get('quote'))}；来源 `{src.get('source_ref')}`。")
                add(f"- 旧审核：`{prev['verdict']}`；内核 `{prev['core_verdict']}`；{prev['reason']}")
                add(f"- ① 内核：`{row['core_verdict']}`（旧审核分类）；不能由字段格式或本报告更改此记录的原始结论。")
                add(f"- ② 主体、身份、值或理由扩写：{row['expansion'] or '本轮未发现明确扩写；不等于已独立授权。'}")
                add(f"- ③ 条件类别 `{row['scope_class']}`，模型原字段 `{j(row['raw_scope'])}`；建议：{row['scope_recommendation']}")
                add(f"- ④ 时间或因果：{row['temporal_causal_analysis']}（无依据推断标记：{flags['unsupported_temporal_or_causal_inference']}）")
                add(f"- ⑤ 字段与审核标准：{row['field_standard_analysis']}（具体契约边界标记：{flags['concrete_schema_or_mapping_issue']}；旧审核范围口径需澄清轴：{flags['prior_scope_rubric_needs_axis_clarification']}）")
                add('')
    add('## 复核');add('')
    add('```sh');add('PYTHONDONTWRITEBYTECODE=1 python diagnose.py');add('```');add('')
    add('脚本只读取 v5 保存材料，验证请求/响应和旧审核哈希，并在本诊断目录生成 `DIAGNOSIS.json` 和本报告；不调用模型、API 或 Mem0。原审核与建议字段均不回填自动流程。')
    (HERE/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__':main()
