"""Deterministic scope operations over explicit upstream semantic annotations.

Offsets are zero-based, end-exclusive Python Unicode character offsets. A finite
condition describes a Cartesian product; an absent condition is never a wildcard.
"""
from itertools import product


def _locate(text, quote):
    if not isinstance(text, str) or not isinstance(quote, str) or not quote:
        return None, 'quote missing or invalid'
    starts = []
    start = 0
    while True:
        pos = text.find(quote, start)
        if pos < 0:
            break
        starts.append(pos)
        start = pos + 1
    if not starts:
        return None, 'quote not found in designated source'
    if len(starts) != 1:
        return None, 'quote repeated and cannot be uniquely located'
    return {'start': starts[0], 'end': starts[0] + len(quote)}, None


def _conditions(condition):
    if not isinstance(condition, dict):
        raise ValueError('condition missing or invalid')
    kind = condition.get('kind')
    if kind == 'unconditional':
        return None, [()]
    if kind != 'finite':
        raise ValueError('condition kind missing or unsupported')
    dimensions = condition.get('dimensions')
    if not isinstance(dimensions, dict) or not dimensions:
        raise ValueError('finite condition requires nonempty dimensions')
    names = sorted(dimensions)
    values = []
    count = 1
    for name in names:
        items = dimensions[name]
        if not isinstance(name, str) or not isinstance(items, list) or not items or any(not isinstance(x, str) or not x for x in items):
            raise ValueError('finite condition requires named nonempty string value lists')
        if len(set(items)) != len(items):
            raise ValueError('duplicate finite condition value')
        count *= len(items)
        if count > 10000:
            raise ValueError('finite condition exceeds 10000 combinations')
        values.append(items)
    return names, list(product(*values))


def _scope(names, cell):
    return dict(zip(names, cell)) if names else {'kind': 'unconditional'}


def _may_overlap(left, right):
    """Only explicit disjoint values prove non-overlap; unknown stays possible."""
    def dimensions(scope):
        if not isinstance(scope, dict) or scope.get('kind') in ('unknown', 'same_as_old'):
            return None
        if scope.get('kind') == 'unconditional':
            return {}
        if scope.get('kind') == 'finite':
            return scope.get('dimensions')
        if 'kind' in scope:
            return None
        return scope
    a, b = dimensions(left), dimensions(right)
    if not isinstance(a, dict) or not isinstance(b, dict):
        return True
    for key in a.keys() & b.keys():
        av = a[key] if isinstance(a[key], list) else [a[key]]
        bv = b[key] if isinstance(b[key], list) else [b[key]]
        if not av or not bv or any(not isinstance(x, str) for x in av + bv):
            return True
        if set(av).isdisjoint(bv):
            return False
    return True


def build_scope_plan(old_memory, old_units, evidence_sources, alignments):
    """Produce an offline plan; all semantic fields must come from the caller.

    See README for the annotation contract. No inference from quoted prose is
    attempted. Repeated quotes, IDs and conflicting claims prevent edits.
    """
    out = {k: [] for k in ('modify', 'preserve', 'uncertain', 'add',
                            'editable_spans', 'protected_facts', 'quote_checks')}
    sources = {}
    for source in evidence_sources:
        sources.setdefault(source.get('source_id'), []).append(source)
    units = {}
    for unit in old_units:
        units.setdefault(unit.get('id'), []).append(unit)
    grouped = {uid: [] for uid in units}
    for a in alignments:
        uid = a.get('unit_id')
        if uid is None:
            matches = sources.get(a.get('source_id'), [])
            pos, error = (None, 'evidence source missing or source id duplicated') if len(matches) != 1 or not a.get('source_id') else _locate(matches[0].get('text'), a.get('new_quote'))
            if len(matches) == 1 and not matches[0].get('source_ref'):
                error = error or 'evidence source_ref missing'
            if a.get('missing_reasons'):
                error = error or 'missing upstream information: ' + '; '.join(map(str, a['missing_reasons']))
            if a.get('relation') not in ('supplement', 'plan'):
                error = error or 'independent fact requires supplement or plan relation'
            if any(not a.get(k) for k in ('new_subject', 'new_attribute', 'new_value')):
                error = error or 'new subject, attribute, or value missing for independent addition'
            base = {'unit_id': None, 'relation': a.get('relation'), 'source_id': a.get('source_id'),
                    'source_ref': matches[0].get('source_ref') if len(matches) == 1 else None,
                    'new_quote': a.get('new_quote'), 'new_position': pos,
                    'subject': a.get('new_subject'), 'attribute': a.get('new_attribute'),
                    'value': a.get('new_value'), 'scope': a.get('new_conditions'),
                    'missing_reasons': a.get('missing_reasons', [])}
            out['quote_checks'].append({'unit_id': None, 'source_id': a.get('source_id'),
                                        'new_quote': a.get('new_quote'), 'new_position': pos,
                                        'status': 'invalid' if error else 'valid', 'new_error': error})
            if error:
                out['uncertain'].append({**base, 'reason': error})
            else:
                out['add'].append({**base, 'status': 'planned' if a['relation'] == 'plan' else 'asserted', 'reason': 'planned; not asserted as completed' if a['relation'] == 'plan' else 'independent addition'})
        elif uid not in grouped:
            out['uncertain'].append({'unit_id': uid, 'reason': 'alignment references unknown unit',
                                     'missing_reasons': a.get('missing_reasons', []), 'note': a.get('note')})
        else:
            grouped[uid].append(a)

    for uid, unit_group in units.items():
        unit = unit_group[0]
        unit_pos, unit_error = _locate(old_memory, unit.get('quote'))
        if uid is None or len(unit_group) != 1:
            unit_error = 'unit id missing or duplicated'
        if unit_error:
            out['quote_checks'].append({'unit_id': uid, 'status': 'invalid', 'reason': unit_error})
            out['uncertain'].append({'unit_id': uid, 'fact': unit.get('fact'), 'old_quote': unit.get('quote'),
                                     'old_position': unit_pos, 'reason': unit_error})
            continue
        protected_invalid = False
        for claim in unit.get('protected_claims', []):
            claim_pos, claim_error = _locate(old_memory, claim.get('quote'))
            if not claim_error and not (unit_pos['start'] <= claim_pos['start'] and claim_pos['end'] <= unit_pos['end']):
                claim_error = 'protected quote outside unit'
            out['quote_checks'].append({'unit_id': uid, 'kind': 'protected_claim', 'old_quote': claim.get('quote'),
                                        'old_position': claim_pos, 'status': 'invalid' if claim_error else 'valid',
                                        'old_error': claim_error})
            if claim_error:
                protected_invalid = True
                out['uncertain'].append({'unit_id': uid, 'fact': claim.get('fact'), 'old_quote': claim.get('quote'),
                                         'old_position': claim_pos, 'reason': claim_error})
            else:
                protected = {'unit_id': uid, 'fact': claim.get('fact'), 'old_quote': claim['quote'],
                             'old_position': claim_pos, 'reason': 'explicit protected claim',
                             'memory_id': unit.get('memory_id'), 'old_source_ref': unit.get('source_ref')}
                if protected not in out['protected_facts']:
                    out['protected_facts'].append(protected)
                    out['preserve'].append(protected)
        candidates = grouped[uid]
        if not candidates:
            out['uncertain'].append({'unit_id': uid, 'fact': unit.get('fact'), 'old_quote': unit.get('quote'),
                                     'old_position': unit_pos, 'reason': 'no alignment for unit'})
            continue

        valid = []
        blocked = protected_invalid
        for index, a in enumerate(candidates):
            old_pos, old_error = _locate(old_memory, a.get('old_quote'))
            if not old_error and not (unit_pos['start'] <= old_pos['start'] and old_pos['end'] <= unit_pos['end']):
                old_error = 'old quote is outside its designated unit'
            source_list = sources.get(a.get('source_id'), [])
            if len(source_list) != 1 or not a.get('source_id'):
                new_pos, new_error = None, 'evidence source missing or source id duplicated'
            else:
                new_pos, new_error = _locate(source_list[0].get('text'), a.get('new_quote'))
                if not source_list[0].get('source_ref'):
                    new_error = new_error or 'evidence source_ref missing'
            check = {'unit_id': uid, 'alignment_index': index, 'old_quote': a.get('old_quote'),
                     'source_id': a.get('source_id'), 'new_quote': a.get('new_quote'),
                     'old_position': old_pos, 'new_position': new_pos,
                     'status': 'invalid' if old_error or new_error else 'valid',
                     'old_error': old_error, 'new_error': new_error}
            out['quote_checks'].append(check)
            base = {'unit_id': uid, 'fact': unit.get('fact'), 'relation': a.get('relation'),
                    'old_quote': a.get('old_quote'), 'new_quote': a.get('new_quote'),
                    'old_position': old_pos, 'new_position': new_pos, 'source_id': a.get('source_id'),
                    'source_ref': source_list[0].get('source_ref') if len(source_list) == 1 else None,
                    'old_value': a.get('old_value'), 'new_value': a.get('new_value'),
                    'subject': a.get('old_subject'), 'attribute': a.get('old_attribute'),
                    'memory_id': unit.get('memory_id'), 'old_source_ref': unit.get('source_ref'),
                    'missing_reasons': a.get('missing_reasons', []), 'note': a.get('note'),
                    'time_note': a.get('time_note')}
            reason = old_error or new_error
            relation = a.get('relation')
            if not reason and a.get('missing_reasons'):
                reason = 'missing upstream information: ' + '; '.join(map(str, a['missing_reasons']))
            if not reason and relation not in ('change', 'same', 'supplement', 'plan', 'unrelated', 'unknown'):
                reason = 'relation missing or unsupported'
            if not reason and relation == 'unknown':
                reason = a.get('reason') or a.get('note') or 'alignment relation unknown'
            if not reason and relation == 'unrelated' and not a.get('no_impact_confirmed'):
                reason = 'unrelated label alone does not establish preservation'
            if not reason and relation in ('change', 'same'):
                fields = ('old_subject', 'new_subject', 'old_attribute', 'new_attribute', 'old_value', 'new_value')
                if any(a.get(x) is None or a.get(x) == '' for x in fields):
                    reason = 'subject, attribute, or value missing'
                elif a['old_subject'] != a['new_subject'] or a['old_attribute'] != a['new_attribute']:
                    reason = 'subject or attribute mismatch; relationship requires confirmation'
                elif relation == 'same' and a['old_value'] != a['new_value']:
                    reason = 'same relation conflicts with different values'
            if not reason and relation in ('supplement', 'plan') and any(not a.get(x) for x in ('new_subject', 'new_attribute', 'new_value')):
                reason = 'new subject, attribute, or value missing for independent addition'
            if not reason and relation in ('supplement', 'plan'):
                out['add'].append({**base, 'subject': a['new_subject'], 'attribute': a['new_attribute'],
                                   'value': a['new_value'], 'scope': a.get('new_conditions'),
                                   'status': 'planned' if relation == 'plan' else 'asserted',
                                   'reason': 'independent addition' if relation == 'supplement' else 'planned; not asserted as completed'})
            try:
                names, old_cells = _conditions(a.get('old_conditions')) if not reason else (None, [])
                if not reason and relation in ('change', 'same'):
                    new_cond = a.get('new_conditions')
                    if isinstance(new_cond, dict) and new_cond.get('kind') == 'same_as_old':
                        new_names, new_cells = names, old_cells
                    else:
                        new_names, new_cells = _conditions(new_cond)
                    if names is None and new_names is not None:
                        reason = 'finite new condition cannot define remainder of unconditional old condition'
                    elif names is not None and new_names is not None and names != new_names:
                        reason = 'condition dimensions differ; overlap cannot be determined'
                else:
                    new_names, new_cells = None, []
            except ValueError as exc:
                reason = str(exc)
            if reason:
                out['uncertain'].append({**base, 'reason': reason})
                if relation not in ('supplement', 'plan') or old_error or new_error:
                    blocked = True
                continue
            for uncertainty in a.get('uncertainties', []):
                out['uncertain'].append({**base, 'reason': uncertainty})
            valid.append((a, base, names, old_cells, new_names, new_cells))

        # If any input for a unit is invalid, its potential overlap is unknown.
        if blocked:
            continue
        if not valid:
            continue
        names, old_cells = valid[0][2:4]
        if any(item[2] != names or set(item[3]) != set(old_cells) for item in valid):
            out['uncertain'].append({'unit_id': uid, 'fact': unit.get('fact'),
                                     'reason': 'inconsistent old conditions across alignments'})
            continue
        assignments = {cell: [] for cell in old_cells}
        for a, base, _, _, new_names, new_cells in valid:
            rel = a['relation']
            if rel not in ('change', 'same'):
                continue
            if a.get('preserve_history'):
                out['preserve'].append({**base, 'scope': a.get('old_conditions'), 'status': 'historical',
                                        'reason': 'explicitly retained as historical, not as current'})
            covered = set(old_cells) if new_names is None else set(old_cells) & set(new_cells)
            for cell in covered:
                assignments[cell].append((a, base))
            if names is not None and new_names is not None:
                for cell in sorted(set(new_cells) - set(old_cells)):
                    out['add'].append({**base, 'value': a['new_value'], 'scope': _scope(names, cell),
                                       'reason': 'new evidence outside old finite scope'})

        for cell in old_cells:
            claims = assignments[cell]
            values = {a['new_value'] for a, _ in claims}
            if len(values) > 1:
                out['uncertain'].append({**claims[0][1], 'scope': _scope(names, cell),
                                         'reason': 'conflicting evidence values for the same scope',
                                         'conflicting_claims': [b for _, b in claims]})
                continue
            base = claims[0][1] if claims else valid[0][1]
            entry = {**base, 'scope': _scope(names, cell)}
            if claims and claims[0][0]['old_value'] != claims[0][0]['new_value']:
                out['modify'].append({**entry, 'reason': 'different explicit values in overlapping scope'})
            else:
                out['preserve'].append({**entry, 'reason': 'unchanged or outside evidence scope'})

    # Conflicting assertions across units or independent additions cannot be
    # silently selected. Unknown scope is treated as potentially overlapping.
    actions = [('modify', x) for x in out['modify']] + [('add', x) for x in out['add'] if x.get('status') != 'planned']
    conflicting = set()
    for i, (left_kind, left) in enumerate(actions):
        for j in range(i + 1, len(actions)):
            right_kind, right = actions[j]
            if not left.get('subject') or not left.get('attribute'):
                continue
            if (left['subject'], left['attribute']) != (right.get('subject'), right.get('attribute')):
                continue
            lv = left.get('new_value') if left_kind == 'modify' else left.get('value')
            rv = right.get('new_value') if right_kind == 'modify' else right.get('value')
            if lv is not None and rv is not None and lv != rv and _may_overlap(left.get('scope'), right.get('scope')):
                conflicting.update((i, j))
    if conflicting:
        for i in sorted(conflicting):
            kind, item = actions[i]
            out[kind].remove(item)
            out['uncertain'].append({**item, 'reason': 'conflicting or potentially conflicting new evidence in overlapping scope'})

    # An unresolved overlapping split unit may contain facts that the proposed
    # textual edit would destroy. Hold that edit rather than guessing.
    held = []
    for item in out['modify']:
        pos = item['old_position']
        for uncertain in out['uncertain']:
            if uncertain.get('unit_id') == item['unit_id']:
                continue
            other = uncertain.get('old_position')
            overlaps = other and pos['start'] < other['end'] and other['start'] < pos['end']
            # Repeated quotes have no chosen position, but any occurrence in
            # the edit still signals a potentially affected unresolved unit.
            quote = uncertain.get('old_quote')
            if not other and isinstance(quote, str) and quote:
                start = old_memory.find(quote)
                while start != -1:
                    if pos['start'] < start + len(quote) and start < pos['end']:
                        overlaps = True
                        break
                    start = old_memory.find(quote, start + 1)
            if overlaps:
                held.append(item)
                out['uncertain'].append({**item, 'reason': 'editable span overlaps unresolved unit',
                                         'overlapping_unit_id': uncertain.get('unit_id')})
                break
    out['modify'] = [item for item in out['modify'] if item not in held]
    for item in out['modify']:
        span = {'unit_id': item['unit_id'], **item['old_position'], 'old_quote': item['old_quote']}
        if span not in out['editable_spans']:
            out['editable_spans'].append(span)
    for item in out['preserve']:
        pos = item.get('old_position')
        if pos and item not in out['protected_facts'] and any(pos['start'] < s['end'] and s['start'] < pos['end'] for s in out['editable_spans']):
            out['protected_facts'].append(item)
    return out
