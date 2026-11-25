"""Scope-planner interface for v4 alignment records; no network calls.

A model's rationale is a claim to be independently reviewed. It is never
converted into the v2 planner's independent semantic authorization.
"""
from __future__ import annotations

import copy

RELATIONS = {'change', 'same', 'new_information', 'supplement', 'plan', 'unrelated', 'unknown'}
MODALITIES = {'asserted', 'planned', 'unknown'}
ORDERS = {'before', 'after', 'same', 'unknown'}
FIELDS = ('unit_id', 'relation', 'old_subject', 'new_subject', 'old_attribute', 'new_attribute',
          'old_value', 'new_value', 'old_conditions', 'new_conditions', 'modality', 'old_quotes',
          'new_quotes', 'temporal_order', 'semantic_rationale', 'semantic_basis', 'uncertainties')
_UNKNOWN = {'unknown', 'none', 'null', 'n/a', '未知', '不明', '无'}


def prepare_input(artifact):
    """Select original units and source texts without upstream manual annotations."""
    payload = artifact.get('input', artifact)
    def unit(u):
        return {k: copy.deepcopy(u.get(k)) for k in ('unit_id', 'source_id', 'memory_quotes')}
    old_units = [unit(u) for u in payload['old_units']]
    memory = payload['source_texts']['memory']
    for old_unit in old_units:
        quotes = old_unit.get('memory_quotes')
        if (old_unit.get('source_id') is None and isinstance(quotes, list) and quotes
                and isinstance(memory.get('source_id'), str) and memory['source_id']
                and all(len(_spans(memory.get('text'), quote)) == 1 for quote in quotes)):
            old_unit['source_id'] = memory['source_id']
            old_unit['source_binding'] = 'unique_quote_in_old_memory'
    return {'case_id': payload.get('case_id'),
            'old_units': old_units,
            'new_units': [unit(u) for u in payload['new_units']],
            'source_texts': copy.deepcopy(payload['source_texts'])}


def _spans(text, quote):
    if not isinstance(text, str) or not isinstance(quote, str) or not quote:
        return []
    out, start = [], 0
    while True:
        pos = text.find(quote, start)
        if pos < 0:
            return out
        out.append({'start': pos, 'end': pos + len(quote)})
        start = pos + 1


def validate_output(output, payload):
    """Validate shape, source/unit binding and exact quote locations, not semantics."""
    all_errors, record_errors, checks = [], [], []
    classified = {'schema': [], 'quote': [], 'basis': [], 'coverage': []}
    def problem(message, index=None, category='schema'):
        all_errors.append(message)
        classified[category].append(message)
        if index is not None:
            record_errors[index].append(message)
    old = {u.get('unit_id'): u for u in payload.get('old_units', [])}
    new = {u.get('unit_id'): u for u in payload.get('new_units', [])}
    memory = payload.get('source_texts', {}).get('memory', {})
    all_sources = {}
    for s in [memory, *payload.get('source_texts', {}).get('messages', [])]:
        all_sources.setdefault(s.get('source_id'), []).append(s)
    if not isinstance(output, dict):
        return {'status': 'failed', 'errors': ['top-level output must be an object'],
                'schema_status': 'failed', 'schema_errors': ['top-level output must be an object'],
                'quote_status': 'not_checked', 'quote_errors': [], 'basis_status': 'not_checked', 'basis_errors': [],
                'coverage_status': 'not_checked', 'coverage_errors': [],
                'record_errors': [], 'quote_checks': [], 'coverage': {}}
    records = output.get('records')
    unmatched = output.get('unmatched_old_unit_ids')
    if not isinstance(records, list):
        problem('records must be an array'); records = []
    record_errors = [[] for _ in records]
    if not isinstance(unmatched, list) or any(not isinstance(x, str) or not x for x in unmatched):
        problem('unmatched_old_unit_ids must be an array of IDs'); unmatched = []
    if len(set(unmatched)) != len(unmatched) or any(x not in old for x in unmatched):
        problem('unmatched old IDs must be unique existing old units', category='coverage')
    mentioned_old, cited_new = set(), set()
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            problem(f'records[{i}] must be an object', i); continue
        for field in FIELDS:
            if field not in r:
                problem(f'records[{i}].{field} missing', i)
        uid = r.get('unit_id')
        relation = r.get('relation')
        if uid is not None and (not isinstance(uid, str) or uid not in old):
            problem(f'records[{i}].unit_id is not an old unit', i)
        if isinstance(uid, str) and uid in old:
            mentioned_old.add(uid)
        if not isinstance(relation, str) or relation not in RELATIONS:
            problem(f'records[{i}].relation invalid', i)
        if relation == 'new_information' and uid is not None:
            problem(f'records[{i}].new_information cannot claim a bound old unit', i)
        if relation in ('change', 'same', 'unrelated') and uid is None:
            problem(f'records[{i}].relation requires an old unit', i)
        if not isinstance(r.get('modality'), str) or r.get('modality') not in MODALITIES:
            problem(f'records[{i}].modality invalid', i)
        for f in ('old_subject', 'new_subject', 'old_attribute', 'new_attribute', 'old_value', 'new_value', 'semantic_rationale'):
            value = r.get(f)
            if value is not None and (not isinstance(value, str) or not value.strip() or value.strip().lower() in _UNKNOWN):
                problem(f'records[{i}].{f} must be nonempty text or null (unknown)', i)
        for side in ('old', 'new'):
            f = side + '_conditions'; cond = r.get(f)
            if not isinstance(cond, dict) or cond.get('kind') not in ('unknown', 'unconditional', 'same_as_old', 'finite'):
                problem(f'records[{i}].{f} invalid', i); continue
            if side == 'old' and cond['kind'] == 'same_as_old':
                problem(f'records[{i}].{f} cannot use same_as_old', i)
            if cond['kind'] == 'finite':
                dims = cond.get('dimensions')
                if not isinstance(dims, dict) or not dims or any(not isinstance(k, str) or not k or not isinstance(v, list) or not v or any(not isinstance(x, str) or not x for x in v) or len(set(v)) != len(v) for k, v in dims.items()):
                    problem(f'records[{i}].{f} finite dimensions invalid', i)
        quotes = {}
        for side, unit_map in (('old', old), ('new', new)):
            field = side + '_quotes'; items = r.get(field)
            if not isinstance(items, list):
                problem(f'records[{i}].{field} must be an array', i); items = []
            if side == 'new' and not items:
                problem(f'records[{i}].new_quotes missing', i)
            if side == 'old' and uid is not None and not items:
                problem(f'records[{i}].old_quotes missing', i)
            if side == 'old' and uid is None and items:
                problem(f'records[{i}].old_quotes cannot be linked without old unit', i)
            quotes[side] = items
            for j, q in enumerate(items):
                error, pos = None, []
                if not isinstance(q, dict):
                    error = 'quote must be an object'; q = {}
                qunit, sid, quote = q.get('unit_id'), q.get('source_id'), q.get('quote')
                u = unit_map.get(qunit) if isinstance(qunit, str) else None
                sources = all_sources.get(sid, []) if isinstance(sid, str) else []
                if not isinstance(qunit, str) or not isinstance(sid, str):
                    error = error or 'unit_id and source_id must be strings'
                if u is None or (side == 'old' and qunit != uid):
                    error = error or 'unit ID is not linked on this side'
                if u and (not sid or sid != u.get('source_id')):
                    error = error or 'source does not match linked unit'
                if not isinstance(quote, str) or not quote:
                    error = error or 'quote missing'
                elif u and not any(quote in x for x in (u.get('memory_quotes') or []) if isinstance(x, str)):
                    error = error or 'quote not contained in linked unit quote'
                if len(sources) != 1:
                    error = error or 'source missing or duplicated'
                else:
                    src = sources[0]; pos = _spans(src.get('text'), quote)
                    if side == 'old' and sid != memory.get('source_id'):
                        error = error or 'old source is not old memory'
                    if side == 'new' and (src.get('side') != 'new' or src.get('speaker') != 'user'):
                        error = error or 'new source is not a new user message'
                    if len(pos) != 1:
                        error = error or ('quote missing in source' if not pos else 'quote repeated in source')
                checks.append({'record_index': i, 'side': side, 'index': j, 'unit_id': qunit, 'source_id': sid,
                               'quote': quote, 'status': 'invalid' if error else 'valid',
                               'position': pos[0] if len(pos) == 1 and not error else None, 'reason': error})
                if error:
                    category = 'schema' if error in ('quote must be an object', 'quote missing', 'unit_id and source_id must be strings') else 'quote'
                    problem(f'records[{i}].{field}[{j}]: {error}', i, category)
                elif side == 'new':
                    cited_new.add(qunit)
        def validate_basis(items, field):
            if not isinstance(items, list):
                problem(f'records[{i}].{field} must be an array', i); return False
            valid = True
            for j, b in enumerate(items):
                if not isinstance(b, dict) or b.get('side') not in ('old', 'new'):
                    problem(f'records[{i}].{field}[{j}] side missing or invalid', i); valid = False; continue
                quote, sid, side = b.get('quote'), b.get('source_id'), b.get('side')
                ok = isinstance(sid, str) and isinstance(quote, str) and bool(quote) and any(
                    c['record_index'] == i and c['side'] == side and c['status'] == 'valid'
                    and c['source_id'] == sid and c['quote'].count(quote) == 1 for c in checks)
                if not ok:
                    problem(f'records[{i}].{field}[{j}] not bound to cited same-side source/quote', i, 'basis'); valid = False
            return valid
        validate_basis(r.get('semantic_basis'), 'semantic_basis')
        temporal = r.get('temporal_order')
        if not isinstance(temporal, dict) or not isinstance(temporal.get('relation'), str) or temporal.get('relation') not in ORDERS:
            problem(f'records[{i}].temporal_order invalid', i)
        else:
            basis = temporal.get('basis'); validate_basis(basis, 'temporal_order.basis')
            explanation = temporal.get('explanation')
            if explanation is not None and (not isinstance(explanation, str) or not explanation.strip()):
                problem(f'records[{i}].temporal_order.explanation invalid', i)
            if temporal.get('relation') != 'unknown' and (not isinstance(basis, list) or not basis or not any(isinstance(b, dict) and b.get('side') == 'new' for b in basis) or not isinstance(explanation, str) or not explanation.strip()):
                problem(f'records[{i}].temporal_order requires new-side basis and explanation', i)
        unc = r.get('uncertainties')
        if not isinstance(unc, list) or any(not isinstance(x, str) or not x.strip() for x in unc):
            problem(f'records[{i}].uncertainties must be an array of strings', i)
    unhandled_old = [x for x in old if x not in mentioned_old and x not in unmatched]
    unhandled_new = [x for x in new if x not in cited_new]
    if set(unmatched) & mentioned_old:
        problem('unmatched_old_unit_ids overlaps records', category='coverage')
    if unhandled_old:
        problem('old units unhandled: ' + ', '.join(unhandled_old), category='coverage')
    if unhandled_new:
        problem('new units lack a valid cited record: ' + ', '.join(unhandled_new), category='coverage')
    return {'status': 'failed' if all_errors else 'passed', 'errors': all_errors,
            **{name + '_status': 'failed' if problems else 'passed' for name, problems in classified.items()},
            **{name + '_errors': problems for name, problems in classified.items()},
            'record_errors': record_errors, 'quote_checks': checks,
            'coverage': {'unhandled_old_unit_ids': unhandled_old, 'unhandled_new_unit_ids': unhandled_new,
                         'unmatched_old_unit_ids': unmatched}}


def adapt_output(output, payload):
    """Map model records to planner input; never issue independent authorization."""
    validation = validate_output(output, payload)
    records = output.get('records', []) if isinstance(output, dict) else []
    if not isinstance(records, list):
        records = []
    result = []
    def safe_quotes(value):
        return [{'unit_id': q.get('unit_id') if isinstance(q.get('unit_id'), str) else None,
                 'source_id': q.get('source_id') if isinstance(q.get('source_id'), str) else None,
                 'quote': q.get('quote') if isinstance(q.get('quote'), str) else None}
                if isinstance(q, dict) else {} for q in value] if isinstance(value, list) else []

    def safe_condition(value, side):
        if not isinstance(value, dict):
            return {'kind': 'unknown'}
        kind = value.get('kind')
        if not isinstance(kind, str) or kind not in ('unknown', 'unconditional', 'same_as_old', 'finite') or (side == 'old' and kind == 'same_as_old'):
            return {'kind': 'unknown'}
        if kind == 'finite':
            dims = value.get('dimensions')
            if (not isinstance(dims, dict) or not dims or any(
                    not isinstance(k, str) or not k or not isinstance(v, list) or not v
                    or any(not isinstance(x, str) or not x for x in v) or len(set(v)) != len(v)
                    for k, v in dims.items())):
                return {'kind': 'unknown'}
        return copy.deepcopy(value)

    for i, raw in enumerate(records):
        if not isinstance(raw, dict):
            raw = {}
        a = {k: copy.deepcopy(raw.get(k)) for k in FIELDS}
        a['unit_id'] = raw.get('unit_id') if isinstance(raw.get('unit_id'), str) else None
        a['relation'] = raw.get('relation') if isinstance(raw.get('relation'), str) and raw['relation'] in RELATIONS else 'unknown'
        a['modality'] = raw.get('modality') if isinstance(raw.get('modality'), str) and raw['modality'] in MODALITIES else 'unknown'
        for field in ('old_subject', 'new_subject', 'old_attribute', 'new_attribute', 'old_value', 'new_value'):
            if not isinstance(a[field], str):
                a[field] = None
        for side in ('old', 'new'):
            a[side + '_quotes'] = safe_quotes(raw.get(side + '_quotes'))
            a[side + '_conditions'] = safe_condition(raw.get(side + '_conditions'), side)
        temporal = raw.get('temporal_order')
        if not isinstance(temporal, dict) or not isinstance(temporal.get('relation'), str) or temporal['relation'] not in ORDERS:
            a['temporal_order'] = {'relation': 'unknown', 'basis': [], 'explanation': None}
        if not isinstance(raw.get('semantic_basis'), list):
            a['semantic_basis'] = []
        if not isinstance(raw.get('uncertainties'), list):
            a['uncertainties'] = []
        else:
            a['uncertainties'] = [x for x in raw['uncertainties'] if isinstance(x, str)]
        a['semantic_support'] = 'unknown'
        a['semantic_rationale'] = raw.get('semantic_rationale')
        a['validation_errors'] = validation['record_errors'][i]
        a['missing_reasons'] = []
        a['raw_record'] = copy.deepcopy(raw)
        result.append(a)
    for uid in validation['coverage'].get('unhandled_old_unit_ids', []) + validation['coverage'].get('unmatched_old_unit_ids', []):
        result.append({'unit_id': uid, 'relation': 'unknown', 'old_quotes': [], 'new_quotes': [],
                       'semantic_support': 'unknown', 'validation_errors': [],
                       'missing_reasons': ['old unit unmatched or unhandled by alignment']})
    for uid in validation['coverage'].get('unhandled_new_unit_ids', []):
        result.append({'unit_id': None, 'relation': 'unknown', 'old_quotes': [], 'new_quotes': [],
                       'semantic_support': 'unknown', 'validation_errors': [],
                       'missing_reasons': ['new unit lacks valid cited alignment: ' + str(uid)]})
    return result


def planner_inputs(payload, output):
    memory = payload['source_texts']['memory']
    units = [{'id': u['unit_id'], 'memory_id': memory.get('source_id'), 'source_ref': memory.get('source_ref'),
              'quote': u['memory_quotes'][0] if len(u.get('memory_quotes') or []) == 1 else None,
              'fact': u['memory_quotes'][0] if len(u.get('memory_quotes') or []) == 1 else None}
             for u in payload['old_units']]
    sources = [copy.deepcopy(s) for s in payload['source_texts'].get('messages', [])
               if s.get('side') == 'new' and s.get('speaker') == 'user']
    return memory['text'], units, sources, adapt_output(output, payload)
