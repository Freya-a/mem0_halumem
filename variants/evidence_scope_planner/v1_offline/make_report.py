"""Render a human-readable comparison from separate saved inputs/results."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES = ('promotion', 'susan', 'transition', 'career_history', 'skydiving')
COMMENTS = {
    'promotion': '人工将晋升明确标为已发生的职位变化，保留雇主和历史职位；具体晋升日期未知，Director 是否作为当前宽泛称谓继续成立不能由字符串比较判断。预期中的晋升事实以 modify 的新值表达，没有另列 add。v3 有 state_change，但未提供规范化主体、值、条件，不能据此授权编辑。差异主要来自上游字段不足和结果表示方式。',
    'susan': '支持和鼓励并不否定朋友关系，人工组对朋友关系保守列为待确认；Daniel 与求职意向分开列出，后者保留为计划。v3 的 career_wellbeing_alignment 关联旧单元却缺旧引文，结构校验失败；人工标注和模型输出的粒度与覆盖不同，身份关联仍需核对。差异主要来自对齐及覆盖，不是范围组合减法。',
    'transition': '转到新职位已经发生，但不能由此断言不会继续找工作；平衡目标须保留。v3 限定词引用未关联的旧来源，原结构校验失败。人工将变化理解为求职进展，具体语义及时间仍须复核；差异来自对齐和证据边界。',
    'career_history': '原文已明确是历史经历；咨询公司获客不推翻旧工作史，也不证明本人当前雇主、职位或所有权。v3 将获客与旧雇主及职位判为变化，语义证据不足；差异主要来自上游关系判断及输入覆盖。',
    'skydiving': '新证据只证明模拟跳伞经历及安全取向，不能证明真实极限运动偏好或受伤理由改变。人工预期倾向保留旧顾虑，规划器对缺少直接支持和重叠拆分的旧关系更保守地列待确认。v3 自报缺证却仍判两项 state_change；SimpleMem 单元重叠，u3 短引文不能独立证明完整关系。差异主要来自上游对齐、证据覆盖及拆分粒度。',
}


def fmt_item(x):
    fields = ('fact', 'subject', 'attribute', 'old_value', 'new_value', 'value', 'scope', 'relation', 'status', 'reason', 'old_quote', 'new_quote', 'old_position', 'source_id', 'source_ref', 'missing_reasons')
    return '; '.join(f'{k}={json.dumps(x[k], ensure_ascii=False)}' for k in fields if x.get(k) is not None)


def section(out, title, plan):
    out.append(f'**{title}**')
    for key in ('modify', 'preserve', 'uncertain', 'add', 'editable_spans', 'protected_facts'):
        entries = plan[key]
        out.append(f'- {key}（{len(entries)}）：' + ('；'.join(fmt_item(x) or json.dumps(x, ensure_ascii=False) for x in entries) if entries else '无'))
    for c in plan['quote_checks']:
        out.append(f"- 引文校验：{fmt_item(c)}; status={c.get('status')}; old_error={c.get('old_error')}; new_error={c.get('new_error')}")
    if not plan['quote_checks']:
        out.append('- 引文校验：无可核验的完整引用对；见 uncertain。')
    out.append('')


def main():
    out = ['# 五案离线回放对照', '',
           '这是单记忆、选定消息的离线实验，不是全量评测。人工预期独立保存且没有传给规划器；模型组只读取已保存 v3 parsed 输出，未将人工语义填入模型结果。数字是输出条目数，不能当准确率。逐版字段、引文与模型关系见 ALIGNER_AUDIT.md，来源核对见 SOURCES.md。', '']
    for case in CASES:
        inp = json.loads((HERE / 'fixtures' / f'{case}.json').read_text(encoding='utf-8'))
        expected = json.loads((HERE / 'fixtures' / f'{case}.expected.json').read_text(encoding='utf-8'))
        res = json.loads((HERE / 'results' / f'{case}.json').read_text(encoding='utf-8'))
        out += [f'## {case}', '', f"旧记忆：{inp['old_memory']}", '', f"旧记忆来源：`{inp['memory_id']}`，`{inp['old_memory_source_ref']}`。", '', '选定新证据：']
        for s in inp['sources']:
            out.append(f"- {s['source_id']}：{s['text']}（`{s.get('source_ref')}`）")
        out += ['', '**独立人工预期**']
        for k in ('modify', 'preserve', 'uncertain', 'add', 'missing'):
            out.append(f"- {k}：{'；'.join(expected[k]) if expected[k] else '无'}")
        out.append('')
        section(out, '人工核对的对齐输入 → 规划器', res['human_alignment'])
        section(out, '保存的 v3 模型对齐输入 → 同一规划器', res['saved_v3_alignment'])
        out += ['**差异与原因：** ' + COMMENTS[case], '']
    demo = json.loads((HERE / 'results' / 'multidimensional.json').read_text(encoding='utf-8'))
    out += ['## 二维条件组合验证', '',
            '旧范围为上海、南京两店 × 堂食、外带；新范围为上海＋外带。', '',
            '修改组合：' + json.dumps([x['scope'] for x in demo['modify']], ensure_ascii=False), '',
            '保留组合：' + json.dumps([x['scope'] for x in demo['preserve']], ensure_ascii=False), '',
            '## 解释和限制', '',
            '借鉴的思路：按 ERASE 风格先判断再修订；参考 FactTrack 的时间有效性和重叠意识，以及 Cedar 条件的交叠与包含思路。本实现不调用、不移植以上模块，也不复用旧 part2_scope_planner；有限离散条件的组合枚举、引文校验、保守判断和适配层由本实验单独实现。', '',
            '实际仅实现显式无条件、有限离散条件和明确 same_as_old；日期区间、开放域、自然语言归一化及蕴含判断不受支持，未知不能视作全域。缺少精确日期时，相对状态变更可按输入表达处理，但无法计算生效时间或自动证明历史事实。输入语义仍须人工核对，源对象的内容和标识依赖调用方；离线来源复核见 SOURCES.md。', '',
            '人工预期是研究者依据原文整理的参考而非用户确认金标准。原始对齐结果可能语义错误，即使引用和结构检查通过也不构成证据有效性的证明。', '']
    (HERE / 'REPORT.md').write_text('\n'.join(out), encoding='utf-8')

if __name__ == '__main__':
    main()
