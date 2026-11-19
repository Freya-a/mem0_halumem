"""Compile human-readable comparison from untouched fields and explicit AI review.

No service calls, configuration reads, output repairs or acceptance overrides.
"""
import csv
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
HISTORY = ROOT.parent / 'real_mem0_v3_v4_comparison_20261104_once'
LABEL = '初步判断，待人工确认'
NAMES = {'case_10_sports_preferences': '运动偏好', 'case_11_persian_care': '波斯猫照料',
         'case_09_father_profile': '父亲资料', 'case_03_assistant_yoga': '瑜伽',
         'case_08_partner_profile': '伴侣资料'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def qualify_historical_review(value):
    """Name the old v3/v4 pair before adding any actual model fields."""
    if isinstance(value, str):
        return re.sub(r'两版(?:本)?', lambda match: '历史 v3/v4 ' + match.group(), value)
    if isinstance(value, list):
        return [qualify_historical_review(item) for item in value]
    if isinstance(value, dict):
        return {key: qualify_historical_review(item) for key, item in value.items()}
    return value


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def support(index, assessment, reason, issues=None):
    return {'evidence_index': index, 'assessment': assessment,
            'issue_types': issues or [], 'reason': reason}


def finding(kind, before, after, reason):
    return {'type': kind, 'input_span': before, 'output_span': after, 'reason': reason}


def fact(index, fidelity, supports, findings=None, uncertainties=None):
    findings = findings or []
    return {'fact_index': index, 'observed_issue_types': sorted({f['type'] for f in findings}),
            'findings': findings, 'uncertainties': uncertainties or [],
            'fidelity_review': fidelity, 'supports': supports}


def v5_reviews(actual):
    """Explicit post-response judgments; never sent as model input."""
    r = {}
    cid = 'case_10_sports_preferences'
    r[cid] = {
        'summary': '拆成态度及明确理由、另一运动偏好两条候选；第二条 context 引文含虚构省略号，整份候选被原校验器拒绝，不能视为成功输出。',
        'granularity_observation': '候选 1→2，独立偏好可分别观察，不能安全消除的 because 附着歧义未写 pending；程序失败使本次无可接受拆分结果。',
        'relationship_review': '不喜欢←觉得太对抗这一明确 because 关系及 finds 主观看法仍在事实1；and prefers 是否也属于 because 范围仍不确定，拆分候选没有标记此点。',
        'uncertainties': ['and prefers 与 dislikes 高层并列或受 because 管辖，两种解释未排除；不按确定因果遗漏计错。',
                          '这是失败候选的语义观察，不能计入已接受 v5 事实的质量结论。'],
        'facts': [
            fact(1, '不喜欢、摔跤对象、主观对抗性理由和 because 保留；raw 未补用户，正文补足用户有第一人称来源；无条件/时间/情态新增。', [
                support(0, 'directly_supported', 'memory 引文直接表达态度及理由，supports 明确主体省略。'),
                support(1, 'overreach', '主体和明确因果有源；for clarity 将名词重复解释为表达目的，来源未直接说明该目的。', ['SUPPORTS_OVERREACH'])],
                [finding('SUPPORTS_OVERREACH', actual[cid]['facts'][0]['evidence'][1]['quote'],
                         actual[cid]['facts'][0]['evidence'][1]['supports'], '重复可见，但为了清晰这一修辞目的并非来源明确表述。')],
                ['because 对后续偏好的附着范围仍未确定。']),
            fact(2, '候选正文保留对强调 teamwork 和 personal growth 的运动的偏好，未声称实际参与；raw 只来自旧记忆。', [
                support(0, 'directly_supported', 'memory 引文直接表达运动偏好及两项特征。'),
                support(1, 'uncertain', '声明的 quote 含 I ... prefer，输入没有这一连续逐字片段；原输入确有第一人称偏好，但不能用修补后的引文替其通过。')],
                uncertainties=['第二条 context 引文逐字检查失败，pending=[] 没有记录原句连接范围歧义。'])]}

    cid = 'case_11_persian_care'
    r[cid] = {
        'summary': '仍为三条，端点信息覆盖，但 while 连接持续未进入正文。删除 v4 把 ctx-2 反思直接升级为平衡活动的 supports，新增直接用户归属待确认；ctx-3 支持说明仍依赖跨片段语境。',
        'granularity_observation': '3→3；不能因条数相同认为已保留关系，也不能为更多条数继续拆散关系段。',
        'relationship_review': '事实2反思与事实3平衡被分别陈述，raw/补充正文均没有 while 或等价联系。引文/待确认不能补回正文中缺失的关系。',
        'uncertainties': ['balancing 的具体归属仍主要来自 assistant 的 dog preferences 类比；用户直接说欣赏和反思，未直接自述这一平衡活动。',
                          '不能由 practical care requirements 推断拥有猫、实际养猫或已经实施照料。',
                          '新增 pending 部分强调 balances/balancing 的字面措辞；应区分命题是否用户自述，而非要求词形完全相同。'],
        'facts': [
            fact(1, '欣赏态度、波斯猫对象、历史血统及王室联系保留；raw 无用户补入，正文补用户有明确第一人称来源。', [
                support(0, 'directly_supported', '准确说明 memory 记录的欣赏及主体省略。'),
                support(1, 'directly_supported', '所选完整引文含 Persian cats 和 my admiration，直接支持主体及欣赏内容。')]),
            fact(2, '反思实际挑战和维持波斯猫高贵外观的对象保留；与平衡活动的 while 联系在拆分后缺失，集中记在事实3。', [
                support(0, 'directly_supported', '所选片段直接表达反思与挑战，并明确片段内主体/指代省略。'),
                support(1, 'partially_supported', 'I do reflect 可支持用户主体；their 的 cats 指代不在该截短引文中，supports 明说依赖 ctx-1，不能把其当此引文直接表达。')]),
            fact(3, 'raw 仍仅取旧记忆，正文没有扩入 grooming/traits/dogs；平衡端点保留，但与反思的 while 关系丢失。', [
                support(0, 'directly_supported', 'memory 片段记录平衡活动；supports 对该局部片段的主体、对象和范围缺口有说明。'),
                support(1, 'partially_supported', '引文直接显示 assistant 对 you 的归属和 dog 类比；说明又使用 ctx-1/ctx-2 及未选入 quote 的 ctx-3 开头将对象联系到猫，局部支持边界仍需人工检查。它没有宣称用户直接自述，故不自动判直接自述越界。')],
                [finding('RELATION_SCOPE_CHANGE',
                    'reflects on the practical challenges of maintaining their regal appearance while balancing historical admiration with practical care requirements',
                    actual[cid]['facts'][2]['raw_subfact'], '两个端点分别出现，但正文不再明示 while 的联接；与 v4 持续相同问题。')],
                ['模型记录 Direct user self-attribution of the verb balances；具体命题的直接用户来源及类比适用范围仍待确认。'])]}

    cid = 'case_09_father_profile'
    r[cid] = {
        'summary': '同样三条，出生、退休医生、激发健康兴趣均覆盖；Martin 只进入补充正文。去掉 v4 对已由 context 解决的受益人省略 pending，但 was 的时间定位仍未改进。',
        'granularity_observation': '3→3，三个不同资料点仍可分别判断，未增加无依据事实。',
        'relationship_review': '同一 Father 的出生/职业/影响关系及 Martin 受益人保留；不存在原文明确条件或因果被拆丢的观察。职业片段新增过去式定位仍未决。',
        'uncertainties': ['retired doctor 无时态，was a retired doctor 是否仅沿用叙述过去时无法确定；不据此推断已故或状态结束。',
                          'Martin 的真实身份及与用户/Father 的额外关系未知，正文没有额外声称。'],
        'facts': [
            fact(1, '父亲和出生日期完整保留；补标点不改变事实。', [support(0, 'directly_supported', '引文直接记载父亲出生日期。')]),
            fact(2, '职业与退休描述保留；was 给无时态原片段加过去定位，暂列时间范围未决而不确定判 TEMPORAL_CHANGE。', [
                support(0, 'partially_supported', 'retired doctor 直接表达职业/退休描述；Father 的同位归属依赖同一旧句其他文字，且该 quote 不支持 was 的具体时间范围。')],
                uncertainties=['新规则要求无时态片段不强补时态，但本次仍出现 was，pending=[] 未披露。']),
            fact(3, 'Father inspired interest in health 的影响关系保留；Martin 来自 context，未进入 raw，没有把 Martin 等同用户。', [
                support(0, 'partially_supported', '片段 who inspired interest in health 直接表达影响，Father 先行词需同一旧句，supports 准确指出受益人省略。'),
                support(1, 'directly_supported', 'context 明确给出 Martin 的健康兴趣，足以补足受益人；不证明额外身份。')])]}

    cid = 'case_03_assistant_yoga'
    r[cid] = {
        'summary': '保持一条，完整保留 practices or is open to 的析取及健康/转变目的；待确认更明确区分原始说话人、析取分支和 transition 范围。',
        'granularity_observation': '1→1，不能将不确定析取拆成两条肯定行为，保持同一关系段合理。',
        'relationship_review': 'or 的不确定性以及 for supporting 的目的关系均保留；没有把 assistant 的 could 建议改成用户已实践。',
        'uncertainties': ['没有用户直接确认练瑜伽或愿意尝试；用户可为语义讨论对象，但这不等同于用户态度已经直接核实。',
                          'practices/open 两分支和 transition 范围仍未知。',
                          'transition pending 中列出的其他领域只是模型列举的可能解释，不能当作新的健康/身份事实。'],
        'facts': [fact(1, 'raw 原样保留旧记忆；补充正文只加用户及标点，仍是析取，不变成两条确定事实。', [
            support(0, 'directly_supported', '旧记忆确实记载瑜伽实践或开放态度及两个目的；supports 未声称用户直接说过。'),
            support(1, 'partially_supported', '用户直接谈工作和身心状态、希望换工作；active engagement 稍强，不能据此确认已完成转变或瑜伽态度。'),
            support(2, 'partially_supported', '准确标明 assistant 建议且不能证明瑜伽态度；所选短 quote 直接含 transition，personal health 需同一来源未选入的上一句，局部范围不完全。')],
            uncertainties=['原始说话人、实践/开放分支、transition 范围分列 pending，没有新增确定承诺。'])]}

    cid = 'case_08_partner_profile'
    r[cid] = {
        'summary': '2→3，日期、职业与专长分开，raw 未补 user，正文用 My Partner 补足关系；但 fact3 supports 把 keen eye 与 specializing 直接判为同义并确认一致，新增明确支持范围越界。',
        'granularity_observation': '职业和专长现在可分别判断，属于粒度改善；不等于专业专长的来源强度已经验证。',
        'relationship_review': '出生、策展人职业和历史文物专长仍归属于同一 Partner，没有变成用户本人的出生/职业。旧资料的专业专长与来源的鉴赏眼光强度差异未记录 pending。',
        'uncertainties': ['keen eye 表示鉴赏眼光，不直接证明 specializing 的专业专长；需核实旧总结依据，不能改写旧命题消除差异。',
                          'Partner 真实姓名/身份未知；My Partner 只用于补足与用户的关系。',
                          'is/specializes 体现当前时态，旧职业同位描述没有明确时态；按与父亲相同标准记时间范围待确认，不据此确定判错。'],
        'facts': [
            fact(1, '出生日期保留，raw 只有旧称谓 Partner；补充用户的伴侣关系有 My Partner 依据。', [
                support(0, 'directly_supported', 'memory 引文直接给出伴侣出生日期。'),
                support(1, 'directly_supported', 'My Partner 加 user 来源直接支持用户的伴侣关系，不是伴侣等同用户。')]),
            fact(2, '职业单独列出；与专长拆分后可分别判断，未新增其他职业、地点或热爱历史内容。', [
                support(0, 'partially_supported', 'art curator 直接表达职业，Partner 归属依赖同一旧句；引文本身无明确时态。'),
                support(1, 'partially_supported', '所选片段直接给职业，My Partner 在同一输入 source 的未选片段；supports 指出同一主体依赖，不能把它当局部 quote 字面含有。')],
                uncertainties=['is 的当前定位需与无时态旧描述区分，暂不自动记时间错误。']),
            fact(3, '专长旧命题保留，没有用 keen eye 替换 raw；但其 context supports 将较弱描述升级为专业专长并宣称已确认一致。', [
                support(0, 'directly_supported', 'memory 确实明确记载 specialization domain，不能因此证明原用户已作同强度表述。'),
                support(1, 'overreach', 'keen eye 不等同 specializing；stylistic variant 和 alignment confirmed 超出了引文对鉴赏眼光的直接支持。', ['SUPPORTS_OVERREACH'])],
                [finding('SUPPORTS_OVERREACH', actual[cid]['facts'][2]['evidence'][1]['quote'],
                    actual[cid]['facts'][2]['evidence'][1]['supports'], '一般鉴赏眼光被升级为专业专长，直接认定两种表述同义且已确认一致。')],
                ['pending=[] 没有记录来源强度差异。'])]}
    return r


def text_cell(value):
    return html.escape(str(value), quote=False).replace('|', '&#124;').replace('\n', '<br>')


def fact_cell(value):
    if value is None:
        return '—'
    parts = ['<b>raw</b><br>' + text_cell(value['raw_subfact']),
             '<b>补充正文</b><br>' + text_cell(value['contextualized_subfact'])]
    for index, evidence in enumerate(value['evidence']):
        parts.extend(['<b>引文 ' + str(index) + ' · ' + evidence['source_type'] + '/' + text_cell(evidence['source_id']) + '</b><br>' + text_cell(evidence['quote']),
                      '<b>supports 原文</b><br>' + text_cell(evidence['supports'])])
    parts.append('<b>模型 pending_confirmations 原文</b><br>' + text_cell(json.dumps(value['pending_confirmations'], ensure_ascii=False, indent=2)))
    return '<br><br>'.join(parts)


def main():
    selection = load(ROOT / 'selection.json')['cases']
    program = load(ROOT / 'program_summary.json')
    old_reviews = {c['case_id']: c['versions']['v4'] for c in load(HISTORY / 'semantic_reviews.json')['cases']}
    actual = {c['case_id']: load(ROOT / 'runs' / c['case_id'] / 'v5/raw_content.txt') for c in selection}
    judgments = v5_reviews(actual)
    compiled, data, fact_rows, support_rows = [], [], [], []
    for selected in selection:
        cid = selected['case_id']
        inp = load(ROOT / 'inputs' / (cid + '.json'))
        baseline = load(ROOT / 'baseline_v4' / cid / 'raw_content.txt')
        review4 = qualify_historical_review(old_reviews[cid])
        review4['review_source'] = 'Historical saved v4 per-fact review reused, with current granularity/relationship comparison added separately.'
        review4['relationship_review'] = {
            'case_10_sports_preferences': '整句保留明确 because 和原有 and 附着歧义；单条覆盖所有信息，独立运动偏好未单列。',
            'case_11_persian_care': '欣赏/反思/平衡三个端点保留，while 在拆分正文中丢失。',
            'case_09_father_profile': '出生/退休医生/激发健康兴趣及 Martin 受益人保留；was 的时间范围仍未决。',
            'case_03_assistant_yoga': 'or 析取和健康/转变目的保持，不能拆成两条确定事实。',
            'case_08_partner_profile': '同一 Partner 的日期、职业与专长保留，职业/专长合为一条。'}[cid]
        review5 = judgments[cid]
        report5 = load(ROOT / 'runs' / cid / 'v5/report.json')
        review5['program_status'] = report5['automatic_check']
        review5['semantic_status'] = LABEL
        # Carry literal fields into every review row so judgments are auditable.
        for version, response, review in [('v4', baseline, review4), ('v5', actual[cid], review5)]:
            assert len(response['facts']) == len(review['facts'])
            for f, rf in zip(response['facts'], review['facts']):
                assert f['fact_index'] == rf['fact_index']
                assert len(f['evidence']) == len(rf['supports'])
                rf['actual_raw_subfact'] = f['raw_subfact']
                rf['actual_contextualized_subfact'] = f['contextualized_subfact']
                rf['model_pending_confirmations'] = f['pending_confirmations']
                fact_rows.append({'case_id': cid, 'version': version, 'fact_index': f['fact_index'],
                    'program_status': review['program_status'], 'raw': f['raw_subfact'], 'contextualized': f['contextualized_subfact'],
                    'issue_types': ','.join(rf['observed_issue_types']), 'fidelity_review': rf['fidelity_review'],
                    'uncertainties': json.dumps(rf['uncertainties'], ensure_ascii=False), 'review_label': LABEL})
                for evidence, rs in zip(f['evidence'], rf['supports']):
                    rs['actual_evidence'] = evidence
                    support_rows.append({'case_id': cid, 'version': version, 'fact_index': f['fact_index'],
                        'evidence_index': rs['evidence_index'], **evidence, 'assessment': rs['assessment'],
                        'reason': rs['reason'], 'review_label': LABEL})
        comparison = {'granularity': review5['granularity_observation'],
            'relations_v4': review4['relationship_review'], 'relations_v5': review5['relationship_review'],
            'scope': 'Candidate semantic observations are retained even on program failure; never accepted as result.'}
        compiled.append({'case_id': cid, 'name': NAMES[cid], 'memory_id': inp['memory_id'],
                         'review_label': LABEL, 'versions': {'v4': review4, 'v5': review5}, 'comparison': comparison})
        data.append({'case_id': cid, 'name': NAMES[cid], 'input': inp, 'v4': baseline,
                     'v5_candidate': actual[cid], 'v5_program_report': report5,
                     'v5_accepted': report5['automatic_check'] == 'passed'})
    save(ROOT / 'semantic_reviews.json', {'review_label': LABEL, 'not_human_gold': True, 'cases': compiled})
    save(ROOT / 'comparison_data.json', {'source_policy': 'Exact parsed saved model fields; presentation adds no model facts.', 'cases': data})
    for filename, rows in [('fact_review.csv', fact_rows), ('supports_review.csv', support_rows)]:
        with (ROOT / filename).open('x', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    out = ['# v4 / v5 五案例实际输出对比', '',
        '**全部语义判断：初步判断，待人工确认。** 程序通过只证明结构、ID、来源编号和引文逐字匹配，不证明语义正确。', '',
        'v5 已在请求前冻结。五例各请求 qwen-plus 一次，共5次；SDK重试0、HTTP重定向关闭、timeout=180秒、显式 generation_parameters={}。v4 全部来自历史保存结果，新增请求0。五例已参与提示词设计，是定向回归观察，不能当作独立泛化或稳定性结论。', '',
        '结果：v4 程序5/5、10条接受事实；v5 程序4/5、12条候选/10条接受事实。运动偏好的2条是被拒绝的候选，未生成 result.json，不修补、不重试。', '',
        '| 程序检查 | 历史 v4 | 本轮 v5 |', '| --- | --- | --- |']
    for label, key in [('通过案例', 'program_passed'), ('候选事实', 'candidate_facts'), ('接受事实', 'accepted_facts'),
                       ('逐字引文通过', 'literal_quotes_passed'), ('引文总数', 'literal_quotes_total'), ('有合格 memory 引文的候选事实', 'facts_with_memory_passed')]:
        out.append('| ' + label + ' | ' + str(program['versions']['v4'][key]) + ' | ' + str(program['versions']['v5'][key]) + ' |')
    out += ['', '## 语义初审概览（待人工确认）', '',
        '| 案例 | v4 → v5 候选数 | 本轮主要观察 |', '| --- | --- | --- |',
        '| 运动偏好 | 1 → 2（v5整份失败） | 明确 because 保留；and 范围未标待确认；仍推断重复目的；引文含虚构省略号。 |',
        '| 波斯猫照料 | 3 → 3 | while 连接仍丢失；去掉原 ctx-2 活动升级说明，新增直接自述 pending；跨片段支持范围仍需确认。 |',
        '| 父亲资料 | 3 → 3 | Martin 仅在补充正文；去掉已解决指代的冗余 pending；was 的时间定位仍未解决。 |',
        '| 瑜伽 | 1 → 1 | 保留 or，不强拆；直接来源、析取分支、transition 范围分开待确认。 |',
        '| 伴侣资料 | 2 → 3 | 职业/专长拆开；新增将 keen eye 等同 specializing 的 supports 越界，来源强度差异仍未披露。 |', '',
        '下面所有 raw、正文、quote、supports、模型 pending 均直接取自保存响应，未作语法修正。并排按各版本 fact_index 排列，不代表同一行必然完全等价。初审意见另列。历史 v4 初审中提及“历史 v3/v4 两版”的文字只描述上一轮，不描述本轮 v5。']
    for datum, reviewed in zip(data, compiled):
        cid = datum['case_id']
        out += ['', '## ' + NAMES[cid] + ' · ' + cid, '', 'memory_id：`' + datum['input']['memory_id'] + '`', '',
            '[v4 原始响应](baseline_v4/' + cid + '/raw_content.txt) · [v5 原始响应](runs/' + cid + '/v5/raw_content.txt)', '',
            '### 同一条旧记忆原文', '', '```text', datum['input']['memory_text'], '```', '', '### 实际输入上下文', '']
        for ctx in datum['input'].get('source_context', []):
            out += ['`' + ctx['source_id'] + '` · speaker=`' + ctx.get('speaker', 'unspecified') + '` · recorded_at=`' + ctx.get('recorded_at', 'unspecified') + '`', '',
                    '```text', ctx['text'], '```', '', '来源：`' + ctx['source_ref'] + '`', '']
        out += ['### 实际拆分事实、全部引文与支持说明', '', '| 编号 | v4（历史实际响应） | v5（本轮实际候选） |', '| --- | --- | --- |']
        old, new = datum['v4']['facts'], datum['v5_candidate']['facts']
        for i in range(max(len(old), len(new))):
            out.append('| ' + str(i + 1) + ' | ' + fact_cell(old[i] if i < len(old) else None) + ' | ' + fact_cell(new[i] if i < len(new) else None) + ' |')
        out += ['', '### 程序检查与关系保留对照', '', '| 项目 | v4 | v5 |', '| --- | --- | --- |',
            '| 程序状态 | ' + reviewed['versions']['v4']['program_status'] + ' | ' + datum['v5_program_report']['automatic_check'] + ' |',
            '| 校验错误 | 无 | ' + text_cell(json.dumps(datum['v5_program_report']['error'], ensure_ascii=False)) + ' |',
            '| 正文关系初审 | ' + text_cell(reviewed['versions']['v4']['relationship_review']) + ' | ' + text_cell(reviewed['versions']['v5']['relationship_review']) + ' |',
            '| 粒度初审 | ' + text_cell(reviewed['versions']['v4']['granularity_observation']) + ' | ' + text_cell(reviewed['versions']['v5']['granularity_observation']) + ' |', '',
            '### 逐事实/逐 supports 语义初审（待人工确认）', '']
        for version in ['v4', 'v5']:
            rv = reviewed['versions'][version]
            out += ['**' + version + '**：' + rv['summary'], '']
            for f in rv['facts']:
                out += ['- 事实 ' + str(f['fact_index']) + '：' + f['fidelity_review']]
                for issue in f['findings']:
                    out += ['  - ' + issue['type'] + '：' + issue['reason']]
                for s in f['supports']:
                    out += ['  - 引文 ' + str(s['evidence_index']) + '：`' + s['assessment'] + '`；' + s['reason']]
                for uncertainty in f['uncertainties']:
                    out += ['  - 待确认：' + (json.dumps(uncertainty, ensure_ascii=False) if isinstance(uncertainty, dict) else uncertainty)]
            out += ['', '**报告另列未决项：**', '']
            for u in rv['uncertainties']:
                out.append('- ' + (json.dumps(u, ensure_ascii=False) if isinstance(u, dict) else u))
    out += ['', '## 解释边界与文件', '',
        '不能据本轮宣布 v5 全面优于 v4：独立资料的粒度有所改善，但关系保留没有稳定改善，局部 supports 仍会越界，并新增一例逐字引文失败。v5 保持冻结，不用本轮结果再次调词或补跑。', '',
        '默认 DESIGN.md、parser/validator/backend、v4 及更早版本和历史结果均由 source_integrity.before.json/final_verification.json 核对。不导入或调用 Mem0，不写知识库，不运行完整开发子集。', '',
        '[程序摘要](program_summary.json) · [逐字引文表](literal_quote_checks.csv) · [逐事实初审](fact_review.csv) · [逐支持说明初审](supports_review.csv) · [完整语义初审](semantic_reviews.json) · [精确字段对照](comparison_data.json) · [五次调用记录](batch_completion.json) · [v5 提示词](../../prompt_versions/v5_granularity_relations_20261104/prompt.txt)']
    with (ROOT / 'COMPARISON_REPORT.md').open('x', encoding='utf-8') as stream:
        stream.write('\n'.join(out) + '\n')
    print(json.dumps({'cases': len(compiled), 'facts_reviewed': len(fact_rows), 'supports_reviewed': len(support_rows),
                      'review_label': LABEL, 'new_model_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    main()
