"""Review-only ScopePlan over sourced candidate scopes; never performs writes."""
import json
from copy import deepcopy
from dataclasses import asdict
from datetime import date, timedelta

from replay import _jsonable, _scope, _sources
from scope import Bound, Field, Interval, Scope, Weekdays, compare
import relation_judge_v2 as relation_v2


def _serialize(value):
    return json.loads(json.dumps(value, ensure_ascii=False, default=_jsonable))


def _conditions(scope):
    return _serialize({'subject':asdict(scope.subject), 'weekdays':asdict(scope.weekdays), 'valid':asdict(scope.valid)})


def _item(mid, idx, old_quote, new_quote, attr, conditions, reason, **extra):
    return {'old_fact_id':{'memory_id':mid, 'fact_index':idx}, 'old_quote':old_quote,
            'new_evidence':[deepcopy(new_quote)] if new_quote else [], 'attribute':attr,
            'conditions':conditions, 'reason':reason, **extra}


def _weekday_set(w):
    return set(range(7)) if w.kind == 'all' else set(w.days)


def _nonempty(interval, days):
    if not days:
        return False
    if interval.start.kind == interval.end.kind == 'known':
        lo, hi = interval.start.value, interval.end.value
        if lo > hi:
            return False
        return any((d - lo.weekday()) % 7 <= (hi - lo).days for d in days)
    return True


def _residual(old, new, intersect):
    """Old minus complete intersection, expressed as disjoint day/closed-date slices."""
    all_old = _weekday_set(old.weekdays)
    affected = _weekday_set(intersect.weekdays)
    residual = []
    rest = all_old - affected
    if rest:
        residual.append(Scope(old.subject, old.attribute, Weekdays.known(rest, old.weekdays.evidence), old.valid))
    days = Weekdays.known(affected, old.weekdays.evidence + new.weekdays.evidence)
    start, end = intersect.valid.start, intersect.valid.end
    if start.kind == 'known' and start.value > date.min:
        before = Bound('known', start.value - timedelta(days=1), start.evidence)
        if old.valid.start.kind == 'unbounded' or old.valid.start.value <= before.value:
            iv = Interval(old.valid.start, before)
            if _nonempty(iv, affected): residual.append(Scope(old.subject, old.attribute, days, iv))
    if end.kind == 'known' and end.value < date.max:
        after = Bound('known', end.value + timedelta(days=1), end.evidence)
        if old.valid.end.kind == 'unbounded' or old.valid.end.value >= after.value:
            iv = Interval(after, old.valid.end)
            if _nonempty(iv, affected): residual.append(Scope(old.subject, old.attribute, days, iv))
    return residual


def _validated(request, row, fact):
    if row.get('status') != 'ok' or row.get('validation', {}).get('passed') is not True:
        raise ValueError('upstream status or validation failed')
    split = request['split_result']
    candidate = row.get('candidate')
    if json.loads(row['raw_output']) != candidate:
        raise ValueError('raw candidate and parsed candidate differ')
    quotes = [e['quote'] for e in fact['evidence'] if e['source_type'] == 'memory']
    match = relation_v2.locate_fragment(split['memory_text'], candidate['candidate_impact_fragment'], quotes)
    if match['located'] is None:
        raise ValueError('upstream fragment not located in old fact')
    located = deepcopy(candidate)
    located['candidate_impact_fragment'] = match['located']
    relation_v2.v1.validate_candidate(located, split, fact, {x['source_id']:x['text'] for x in request['new_evidence']})
    if row.get('old_subfact') != fact['raw_subfact']:
        raise ValueError('upstream fact mismatch')
    return candidate, match


def build_plan(request, relation_result, annotations=None):
    """Produce evidence-bearing, review-only proposals; annotations never come from expectations."""
    relation_v2.v1.validate_request(request)
    split = request['split_result']; mid = split['memory_id']; sources = _sources(request)
    output = {'status':'needs_review','mode':'structured' if annotations is not None else 'baseline_only',
              'upstream_original':deepcopy(relation_result),
              'modify':[], 'preserve':[], 'uncertain':[], 'add':[], 'errors':[]}
    protections, modifications = [], []
    unknown_scope = Scope(Field.unknown(), Field.unknown(), Weekdays.unknown(), Interval(Bound.unknown(), Bound.unknown()))
    for fact in split['facts']:
        idx = fact['fact_index']; fid = (mid, idx)
        old_quotes = [e['quote'] for e in fact['evidence'] if e['source_type']=='memory' and e['source_id']==mid]
        old_quote = old_quotes[0]
        rows = [r for r in relation_result.get('results', []) if (r.get('memory_id'),r.get('fact_index')) == fid]
        try:
            if len(rows) != 1: raise ValueError('missing or duplicate upstream row')
            candidate, match = _validated(request, rows[0], fact)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            src = request['new_evidence'][0]
            raw_ref = {'source_id':src['source_id'], 'quote':src['text']}
            output['uncertain'].append(_item(mid, idx, old_quote, raw_ref, None, {'status':'unknown'},
                    '上游结果未通过验证；仅保留请求中的新证据原文，不能采信上游关系或片段。', code='upstream_error', detail=str(exc), new_evidence_origin='request'))
            output['errors'].append({'old_fact_id':{'memory_id':mid,'fact_index':idx}, 'code':'upstream_error', 'detail':str(exc)})
            if annotations is not None:
                hold = _item(mid, idx, old_quote, raw_ref, None, {'status':'unknown'}, '上游失败，暂时保护旧引文。', code='hold_provisional', old_fragment=old_quote)
                output['preserve'].append(hold)
                protections.append((hold, unknown_scope))
            continue
        old_quote = next(q for q in old_quotes if candidate['old_quote'] in q)
        new_quote = candidate['new_quote']; label = candidate['relation']
        base = lambda attr, conditions, reason, **extra: _item(mid, idx, old_quote, new_quote, attr, conditions, reason, **extra)
        new_scope = _scope(annotations['new_unit'], request, sources, 'new') if annotations is not None else None
        new_attr = new_scope.attribute.value if new_scope else None
        new_conditions = _conditions(new_scope) if new_scope else {'status':'unknown'}
        output['add'].append(base(new_attr, new_conditions, '原始新引文供候选复核；未验证新颖性、语义拆分或是否应新增。',
                                  text=new_quote['quote'], code='raw_evidence_candidate'))
        if label == 'possible_change':
            output['uncertain'].append(base(new_attr, new_conditions, 'possible_change 是候选关系，不足以证明明确纠正或授权修改。', code='possible_change'))
        elif label == 'support':
            output['uncertain'].append(base(new_attr, new_conditions, 'support 只表示上游的支持候选，不能证明同一状态持续或触发修改；新旧阶段仍待复核。', code='support_not_change'))
        elif label != 'historical_correction':
            output['uncertain'].append(base(new_attr, new_conditions, '关系标签本身不足以证明明确纠正及修改范围。', code='relation_not_correction', relation=label))
        if annotations is None:
            output['uncertain'].append(base(None, {'status':'unknown'}, '组件一的自由文本属性和候选片段未提供经过验证的属性单元及条件边界。',
                                            code='attribute_unlocalized', upstream_attribute=candidate['attribute'], candidate_fragment=candidate['candidate_impact_fragment']))
            output['uncertain'].append(base(None, {'status':'unknown'}, '有效时间和条件范围未由带来源的结构化输入确定；记录时间不得作为生效时间。', code='boundary_unknown'))
            output['preserve'].append(base(None, {'status':'unknown'}, '未能安全划分范围，暂时保护原文以待复核；不声称原状态无限期有效。', code='hold_provisional', old_fragment=old_quote))
            continue
        units = annotations['old_units']
        # Derived diagnostic views are not independent old facts. Other units,
        # including different scopes of one attribute, are all processed.
        unique = set()
        for unit in units:
            if annotations.get('scope_unit_roles', {}).get(unit['name']) == 'derived_view':
                continue
            if (len(split['facts']) > 1 and unit.get('fact_index') != idx) or (len(split['facts']) == 1 and unit.get('fact_index', idx) != idx):
                continue
            old_scope = _scope(unit, request, sources, 'old')
            attr = old_scope.attribute.value
            key = json.dumps([attr, _conditions(old_scope)], sort_keys=True, ensure_ascii=False)
            if key in unique: continue
            unique.add(key)
            memtext = split['memory_text']
            attr_refs = unit['attribute'].get('evidence', [])
            old_fragments = [x['quote'] for x in attr_refs if x['source_id'] == mid
                             and memtext.count(x['quote']) == 1 and any(x['quote'] in q for q in old_quotes)]
            old_fragment = old_fragments[0] if len(old_fragments) == 1 else None
            unit_quote = next((q for q in old_quotes if old_fragment and old_fragment in q), old_quote)
            def unit_base(attribute, conditions, reason, **extra):
                return _item(mid, idx, unit_quote, new_quote, attribute, conditions, reason, **extra)
            def add_preserve(part, reason, code):
                item = unit_base(attr, _conditions(part), reason, code=code, old_fragment=old_fragment)
                output['preserve'].append(item)
                protections.append((item, part))
            result = compare(old_scope, new_scope)
            cond = _conditions(old_scope)
            if result.status == 'disjoint':
                add_preserve(old_scope, '结构化候选范围与新属性或条件不相交；保留该旧范围，语义映射仍需复核。', 'disjoint_preserve')
                continue
            if result.status == 'overlap' and result.intersection_complete:
                for part in _residual(old_scope, new_scope, result.intersection):
                    add_preserve(part, '从旧范围减去确定的交集后，保留该不相交部分；日期端点按闭区间推导。', 'residual_preserve')
            else:
                output['uncertain'].append(base(attr, cond, '无法确定完整交集或其有效边界，不能生成完整修改范围。',
                                                code='boundary_unknown', missing=list(result.missing), overlap_status=result.status))
            if label != 'historical_correction' or result.status != 'overlap' or not result.intersection_complete:
                if result.status == 'overlap' and result.intersection_complete:
                    inter = result.intersection
                    interscope = Scope(inter.subject, inter.attribute, inter.weekdays, inter.valid)
                    output['uncertain'].append(base(attr, _conditions(interscope), '该相交范围可能受影响，但尚无明确纠正依据，不能修改。', code='scope_overlap_unconfirmed'))
                else:
                    add_preserve(old_scope, '修改条件未满足；暂时保留该旧范围供复核，不把未知端点填成确定日期。', 'hold_provisional')
                continue
            correction = annotations.get('correction', {})
            correction_quote = correction.get('quote'); correction_source = correction.get('source_id')
            if not (correction.get('status') == 'explicit_verified' and correction.get('old_attribute') == attr
                    and correction_source == new_quote['source_id'] and correction_quote
                    and correction_quote in sources.get(correction_source, '') and new_quote['quote'] in correction_quote
                    and correction.get('reason')):
                output['uncertain'].append(base(attr, cond, '缺少针对该属性且有新证据来源的明确纠正确认。', code='correction_unverified'))
                add_preserve(old_scope, '纠正依据未确认，暂时保护旧范围。', 'hold_provisional')
                continue
            frag = match['located']
            refs = unit['attribute'].get('evidence', [])
            fragments = [x['quote'] for x in refs if x['source_id']==mid and x['quote'] in frag and memtext.count(x['quote']) == 1]
            if match['start'] is None or len(fragments) != 1:
                output['uncertain'].append(base(attr, cond, '候选片段不能唯一定位到有来源的旧属性。', code='attribute_unlocalized'))
                add_preserve(old_scope, '属性范围未唯一定位，暂时保护旧范围。', 'hold_provisional')
                continue
            inter = result.intersection
            interscope = Scope(inter.subject, inter.attribute, inter.weekdays, inter.valid)
            item = unit_base(attr, _conditions(interscope), '有外部确认的明确纠正和完整相交边界；仅提出该属性交集的最小范围供人工审核。',
                                          old_fragment=fragments[0], correction_evidence={'source_id':correction_source,'quote':correction_quote},
                                          code='explicit_correction_candidate')
            output['modify'].append(item)
            modifications.append((item, interscope))
        if not unique:
            output['uncertain'].append(base(None, {'status':'unknown'}, '没有可规划的旧属性范围，不能据此判断修改或保留。', code='old_scope_missing'))
            hold = base(None, {'status':'unknown'}, '旧范围缺失，暂时保护原文供复核。', code='hold_provisional', old_fragment=old_quote)
            output['preserve'].append(hold)
            protections.append((hold, unknown_scope))
    # Check across all subfacts of the same memory, not merely within one row.
    for edit, edit_scope in modifications:
        start = split['memory_text'].find(edit['old_fragment'])
        end = start + len(edit['old_fragment'])
        conflicts = []
        for protected, protected_scope in protections:
            neutral = Field.known('same')
            a = Scope(neutral, neutral, edit_scope.weekdays, edit_scope.valid)
            b = Scope(neutral, neutral, protected_scope.weekdays, protected_scope.valid)
            if compare(a, b).status == 'disjoint':
                continue
            fragment = protected.get('old_fragment')
            position = split['memory_text'].find(fragment) if fragment and split['memory_text'].count(fragment) == 1 else -1
            if position < 0 or (start < position + len(fragment) and position < end):
                conflicts.append(protected['attribute'])
        if conflicts:
            output['modify'].remove(edit)
            issue = deepcopy(edit)
            issue.update(code='protection_overlap', reason='修改片段与受保护文本及条件可能重叠，无法安全拆分。', conflicting_attributes=conflicts)
            output['uncertain'].append(issue)
    active = [(item, scope) for item, scope in modifications if any(item is x for x in output['modify'])]
    overlapping = set()
    for i, (left, left_scope) in enumerate(active):
        left_start = split['memory_text'].find(left['old_fragment'])
        for j in range(i + 1, len(active)):
            right, right_scope = active[j]
            right_start = split['memory_text'].find(right['old_fragment'])
            text_overlap = left_start < right_start + len(right['old_fragment']) and right_start < left_start + len(left['old_fragment'])
            neutral = Field.known('same')
            a = Scope(neutral, neutral, left_scope.weekdays, left_scope.valid)
            b = Scope(neutral, neutral, right_scope.weekdays, right_scope.valid)
            if text_overlap and compare(a, b).status != 'disjoint':
                overlapping.update((i, j))
    for i in sorted(overlapping):
        edit = active[i][0]
        output['modify'].remove(edit)
        issue = deepcopy(edit)
        issue.update(code='modification_overlap', reason='多个修改候选的旧文本和条件可能重叠，需联合复核。')
        output['uncertain'].append(issue)
    # Review-only inventory; no inference of novelty or a relation to an old fact.
    raw_refs = {row.get('candidate', {}).get('new_quote', {}).get('source_id')
                for row in relation_result.get('results', [])
                if isinstance(row.get('candidate'), dict)
                and isinstance(row['candidate'].get('new_quote'), dict)}
    validated_refs = {ref['source_id'] for item in output['add']
                      for ref in item.get('new_evidence', [])}
    output['new_evidence_inventory'] = [
        {'source_id': src['source_id'], 'text': src['text'],
         'speaker': src.get('speaker'), 'recorded_at': src.get('recorded_at'),
         'source_ref': src.get('source_ref'),
         'referenced_by_upstream': src['source_id'] in raw_refs,
         'referenced_by_validated_upstream': src['source_id'] in validated_refs,
         'independent_fact_verified': False, 'old_fact_relation_verified': False}
        for src in request['new_evidence']]
    return output
