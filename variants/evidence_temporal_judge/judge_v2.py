"""FactTrack-inspired candidate-only temporal flow over validated v4/ERASE inputs.

No author modules, models, network, or storage are initialized here. Time bounds
are supplied by the caller as evidence-backed claims, never derived from record time.
"""
from __future__ import annotations

import calendar
from copy import deepcopy
from datetime import date
import importlib.util
import math
from pathlib import Path
import re

_spec = importlib.util.spec_from_file_location('_temporal_v1', Path(__file__).with_name('judge.py'))
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)


def _boundary(value):
    """Return the earliest/latest possible calendar date of a claimed boundary."""
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {'value', 'precision'}:
        raise ValueError('invalid boundary')
    raw, precision = value['value'], value['precision']
    patterns = {'year': r'\d{4}', 'month': r'\d{4}-\d{2}', 'day': r'\d{4}-\d{2}-\d{2}'}
    if precision not in patterns or not isinstance(raw, str) or not re.fullmatch(patterns[precision], raw):
        raise ValueError('invalid boundary precision')
    fields = [int(x) for x in raw.split('-')]
    year = fields[0]
    if precision == 'year':
        return date(year, 1, 1), date(year, 12, 31)
    month = fields[1]
    if precision == 'month':
        return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])
    day = date(*fields)
    return day, day


def _interval(claim):
    if not isinstance(claim, dict) or 'start' not in claim or 'end' not in claim:
        raise ValueError('missing interval boundaries')
    start, end = _boundary(claim['start']), _boundary(claim['end'])
    if start and end and start[0] > end[1]:
        raise ValueError('reversed interval')
    return start, end


def _interval_relation(old, new):
    """Compare possible closed intervals without treating unknown as infinity."""
    a, b = old
    c, d = new
    if b and c and b[1] < c[0]:
        return 'before'
    if d and a and d[1] < a[0]:
        return 'after'
    if a and b and c and d and max(a[1], c[1]) <= min(b[0], d[0]):
        return 'overlap'
    return 'unknown'


def _source_quote(quote, sources):
    v1._quotes([quote], sources)


def _old_basis(basis, fact, request, contexts):
    if not isinstance(basis, dict) or set(basis) != {'source_type', 'source_id', 'quote'}:
        raise ValueError('invalid old time basis')
    # Require the basis to be an exact quote from this fact's validated provenance.
    for item in fact['evidence']:
        if (item['source_type'] == basis['source_type'] and item['source_id'] == basis['source_id']
                and basis['quote'] and basis['quote'] in item['quote']):
            return
    raise ValueError('old time basis is not fact provenance')


def _literal_precision(boundary, quote):
    """Conservative format check only; this cannot establish event semantics."""
    parts = [int(part) for part in boundary['value'].split('-')]
    year = str(parts[0])
    if boundary['precision'] == 'year':
        return bool(re.search(r'(?<!\d)' + year + r'(?!\d)', quote))
    month = f'0?{parts[1]}' if parts[1] < 10 else str(parts[1])
    if boundary['precision'] == 'month':
        pattern = rf'(?<!\d){year}(?:-{month}(?=-\d{{1,2}}(?!\d)|[^-\d]|$)|年{month}月)'
    else:
        day = f'0?{parts[2]}' if parts[2] < 10 else str(parts[2])
        pattern = rf'(?<!\d){year}(?:-{month}-{day}(?!\d)|年{month}月{day}日)'
    return bool(re.search(pattern, quote))


def _time_check(checks, role, boundary, basis, source, fact, verifier, validate_quote):
    """Audit provenance, supported precision and injected semantic assessment separately."""
    if boundary is None:
        return True
    _boundary(boundary)
    check = {'role': role, 'boundary': deepcopy(boundary), 'basis': deepcopy(basis),
             'quote_status': 'not_checked', 'precision_status': 'not_checked',
             'semantic_status': 'not_checked'}
    checks.append(check)
    try:
        validate_quote()
    except Exception:
        check['quote_status'] = 'invalid'
        raise
    check['quote_status'] = 'matched'
    check['precision_status'] = 'matched' if _literal_precision(boundary, basis['quote']) else 'insufficient'
    if verifier is not None:
        try:
            answer = verifier({'task': 'time_support', 'role': role, 'boundary': deepcopy(boundary),
                               'basis': deepcopy(basis), 'source': deepcopy(source), 'fact': deepcopy(fact)})
            if (not isinstance(answer, dict) or set(answer) != {'status', 'reason'}
                    or answer['status'] not in ('supported', 'not_supported', 'uncertain')
                    or not isinstance(answer['reason'], str) or not answer['reason'].strip()):
                raise ValueError('invalid time support response')
            check['semantic_status'] = answer['status']
            check['semantic_reason'] = answer['reason']
        except Exception:
            check['semantic_status'] = 'failed'
    return check['precision_status'] == 'matched' and check['semantic_status'] == 'supported'


def _nli(backend, fact, evidence, impact):
    answer = backend({'task': 'pair_nli', 'old_fact': deepcopy(fact),
                      'new_evidence': deepcopy(evidence), 'impact': deepcopy(impact)})
    if not isinstance(answer, dict) or set(answer) - {'relation', 'score'} or answer.get('relation') not in ('contradiction', 'compatible', 'uncertain'):
        raise ValueError('invalid NLI response')
    score = answer.get('score')
    if score is not None and (type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= 1):
        raise ValueError('invalid NLI score')
    return deepcopy(answer)


def _block_check(new_claim, transitions, sources, source_id, fact_index, old_interval, new_interval, assess_transition):
    """Candidate nearest blocker: a supported actual transition at an exact day.

    Unlike FactTrack this is not an epsilon mutation of a world-state list.
    The input transition is a caller assertion whose semantic support needs review.
    """
    if not transitions:
        return None, False
    old_start, old_end = old_interval
    new_start, _ = new_interval
    if not isinstance(transitions, list):
        raise ValueError('transitions must be a list')
    eligible = []
    uncertain = False
    for transition in transitions:
        if not isinstance(transition, dict) or set(transition) != {'fact_index', 'source_id', 'quote', 'at', 'kind'}:
            raise ValueError('invalid transition')
        if type(transition['fact_index']) is not int or transition['fact_index'] != fact_index:
            continue
        if (transition['source_id'] != source_id or transition['kind'] != 'actual'
                or new_claim.get('kind') != 'actual'):
            continue
        if not assess_transition(transition):
            uncertain = True
            continue
        at = _boundary(transition['at'])
        if at is None or at[0] != at[1]:
            # A coarse/unknown relevant blocker might precede an exact one.
            uncertain = True
            continue
        # Do not invent either start, use a transition after the new state begins,
        # or truncate a known earlier end. Select the earliest supported blocker.
        if (not old_start or old_start[1] >= at[0] or not new_start or at[0] > new_start[0]
                or (old_end and old_end[1] < at[0])):
            continue
        eligible.append((at[0], transition))
    if not eligible:
        return None, uncertain
    _, transition = min(eligible, key=lambda pair: pair[0])
    return {'proposed_end': {**deepcopy(transition['at']), 'inclusive': False},
            'basis': {'source_id': source_id, 'quote': transition['quote']},
            'reason': '候选状态转换阻断旧状态向后延续；事件时间和语义仍需核验'}, uncertain


def _review_fact(item, time_info, sources, evidence_by_id, nli_backend, request, contexts, time_verifier):
    fact = item['fact']
    path = []
    result = {**deepcopy(item), 'path': path, 'temporal_relation': 'unclear',
              'interval_relation': 'unknown', 'intervals': None, 'nli': None,
              'interval_adjustments': [], 'temporal_reason': '时间或证据不足', 'time_checks': [],
              'impact_judgment': {key: deepcopy(item[key]) for key in
                                  ('erase_label', 'applicability', 'temporal_relation', 'temporal_reason', 'components')
                                  if key in item}}
    if item['status'] == 'failed':
        result['components'] = [{'fragment': fact['raw_subfact'], 'action': 'confirm',
                                 'reason': '逐事实判断处理失败，保留原事实待确认', 'new_evidence': []}]
        return result
    if item['applicability'] == 'uninvolved':
        result['temporal_reason'] = '证据未涉及该事实'
        return result
    try:
        if time_info is None:
            time_info = {}
        if not isinstance(time_info, dict):
            raise ValueError('time info unavailable')
        path.append('determine_interval')
        old_claim = time_info.get('facts', {}).get(str(fact['fact_index']))
        if old_claim is None:
            # Missing time is a valid unknown, not a processing failure.
            old_claim = {'start': None, 'end': None, 'basis': None}
        elif old_claim.get('basis') is None and (old_claim.get('start') is not None or old_claim.get('end') is not None):
            raise ValueError('old time lacks evidence basis')
        old_interval = _interval(old_claim)
        # Only compare the source explicitly cited in the impact judgment.
        ids = {q['source_id'] for part in item['components'] for q in part['new_evidence']}
        if len(ids) != 1:
            result['temporal_reason'] = '需要且只能选择一个有引文的证据来源进行区间比较'
            return _downgrade(result)
        source_id = next(iter(ids))
        new_claim = time_info.get('sources', {}).get(source_id)
        if new_claim is None:
            new_claim = {'start': None, 'end': None, 'basis': None, 'kind': 'unknown'}
        elif new_claim.get('basis') is None and (new_claim.get('start') is not None or new_claim.get('end') is not None):
            raise ValueError('new time lacks evidence basis')
        if new_claim.get('kind') not in ('actual', 'simulation', 'unknown'):
            raise ValueError('invalid activity kind')
        new_interval = _interval(new_claim)
        result['intervals'] = {'old': deepcopy(old_claim), 'new': deepcopy(new_claim)}
        old_basis = old_claim.get('basis')
        old_source = None
        if isinstance(old_basis, dict):
            if old_basis.get('source_type') == 'memory':
                old_source = {'source_type': 'memory', 'source_id': request['memory_id'], 'text': request['memory_text']}
            else:
                old_source = next((c for c in contexts if c.get('source_id') == old_basis.get('source_id')), None)
        new_basis = new_claim.get('basis')
        def check_old():
            _old_basis(old_basis, fact, request, contexts)
        def check_new():
            _source_quote(new_basis, sources)
            if new_basis['source_id'] != source_id:
                raise ValueError('time source mismatch')
        checks = result['time_checks']
        supported = []
        for field in ('start', 'end'):
            supported.append(_time_check(checks, 'old_' + field, old_claim[field], old_basis,
                                         old_source, fact, time_verifier, check_old))
            supported.append(_time_check(checks, 'new_' + field, new_claim[field], new_basis,
                                         evidence_by_id[source_id], fact, time_verifier, check_new))
        # FactTrack determines blocking before checking opposite-side conflicts.
        path.append('block_check')
        transitions = time_info.get('transitions', [])
        if time_info.get('transition') is not None:
            if not isinstance(transitions, list):
                raise ValueError('transitions must be a list')
            transitions = [*transitions, time_info['transition']]
        def assess_transition(transition):
            basis = {'source_id': transition['source_id'], 'quote': transition['quote']}
            return _time_check(checks, 'transition', transition['at'], basis, evidence_by_id[source_id],
                               fact, time_verifier, lambda: _source_quote(basis, sources))
        blocker, uncertain_transition = _block_check(new_claim, transitions, sources, source_id, fact['fact_index'],
                                                      old_interval, new_interval, assess_transition)
        if not all(supported) or uncertain_transition:
            result['temporal_reason'] = '时间引文的精度或事件语义依据不足，需确认'
            if any(check['semantic_status'] == 'failed' for check in checks):
                result['status'] = 'failed'
                result['error_type'] = 'TimeSupportError'
            return _downgrade(result)
        relation = _interval_relation(old_interval, new_interval)
        result['interval_relation'] = relation
        path.append('contradiction_check')
        nli = _nli(nli_backend, fact, evidence_by_id[source_id], item)
        result['nli'] = nli
        directional = item['applicability'] == 'involved' and item['erase_label'] == 'Make False'
        actual = new_claim['kind'] == 'actual'
        if not directional or not actual or nli['relation'] != 'contradiction':
            result['temporal_reason'] = '证据影响、实际活动性质或事实对冲突尚不足以支持时间结论'
            return _downgrade(result)
        if relation in ('before', 'after'):
            result['temporal_relation'] = 'historical_compatible'
            result['temporal_reason'] = ('有来源的有效区间明确不重叠，旧状态作为历史保留' if relation == 'before'
                                         else '有来源的有效区间明确不重叠，新证据描述较早时期')
            for part in result['components']:
                if part['action'] == 'modify':
                    part['action'] = 'protect'
                    part['reason'] += '；不重叠的旧状态作为历史保留'
        elif blocker is not None and item['temporal_relation'] == 'before_after':
            result['temporal_relation'] = 'before_after'
            result['temporal_reason'] = '逐事实影响、转换引文及候选阻断边界共同支持状态先后，仍需核验'
            path.append('adjustment_candidate')
            blocker['fragments'] = [part['fragment'] for part in result['components'] if part['action'] == 'modify']
            if blocker['fragments']:
                result['interval_adjustments'] = [blocker]
        elif relation == 'overlap':
            result['temporal_relation'] = 'simultaneous_conflict'
            result['temporal_reason'] = '有来源的区间明确重叠，且事实对和逐事实影响均提示冲突；并非事实已证伪'
        else:
            result['temporal_reason'] = '有效区间边界或状态转换证据不足'
            return _downgrade(result)
        return result
    except Exception as error:
        result['status'] = 'failed'
        result['error_type'] = type(error).__name__
        result['temporal_reason'] = '时间或事实对处理失败，需确认'
        return _downgrade(result)


def _downgrade(result):
    for part in result.get('components', []):
        if part['action'] == 'modify':
            part['action'] = 'confirm'
            part['reason'] += '；时间或冲突依据尚需确认'
    result['interval_adjustments'] = []
    return result


def judge(split_result, source_context, new_evidence, time_info, fact_backend, candidate_backend, nli_backend, time_verifier=None):
    """Review validated v4-shaped facts and return only isolated candidates."""
    inputs = deepcopy((split_result, source_context, new_evidence, time_info))
    split_result, source_context, new_evidence, time_info = inputs
    base = v1.judge(split_result, source_context, new_evidence, time_info, fact_backend, candidate_backend)
    sources = v1._sources(new_evidence)
    evidence_by_id = {entry['source_id']: entry for entry in new_evidence}
    request = {'memory_id': split_result['memory_id'], 'memory_text': split_result['memory_text']}
    base['facts'] = [_review_fact(item, time_info, sources, evidence_by_id, nli_backend, request, source_context, time_verifier)
                     for item in base['facts']]
    base['version'] = 'v2'
    return base


def split_and_judge(request, new_evidence, time_info, splitter_backend_factory, fact_backend, candidate_backend, nli_backend, time_verifier=None):
    split = v1.split_with_v4(request, splitter_backend_factory)
    result = judge(split['result'], request.get('source_context', []), new_evidence, time_info,
                   fact_backend, candidate_backend, nli_backend, time_verifier=time_verifier)
    result['splitter_prompt'] = split['prompt']
    return result
