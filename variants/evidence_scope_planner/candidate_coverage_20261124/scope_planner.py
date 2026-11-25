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
    if any(not isinstance(name, str) or not name for name in dimensions):
        raise ValueError('finite condition requires named nonempty string dimensions')
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


def _basis_valid(basis, old_quotes, new_quotes, require_new=False):
    """Require evidence to be a unique, validated part of an associated quote."""
    if not isinstance(basis, list) or not basis:
        return False
    saw_new = False
    for item in basis:
        if not isinstance(item, dict) or item.get('side') not in ('old', 'new'):
            return False
        refs = old_quotes if item['side'] == 'old' else new_quotes
        found = [q for q in refs if q.get('status') == 'valid'
                 and q.get('source_id') == item.get('source_id')
                 and isinstance(item.get('quote'), str) and item['quote']
                 and item['quote'] in q['quote']
                 and q['quote'].count(item['quote']) == 1]
        if not found:
            return False
        saw_new |= item['side'] == 'new'
    return not require_new or saw_new


def build_scope_plan(old_memory, old_units, evidence_sources, alignments):
    """Process only supplied alignment judgments; never infer semantics or chronology."""
    out = {k: [] for k in ('modify', 'preserve', 'uncertain', 'add',
                           'editable_spans', 'protected_facts', 'quote_checks')}
    sources, units = {}, {}
    for source in evidence_sources:
        sources.setdefault(source.get('source_id'), []).append(source)
    for unit in old_units:
        units.setdefault(unit.get('id'), []).append(unit)
    aligned = set()
    records = {}
    unrestricted_units = set()
    candidate_bases = {}

    for index, a in enumerate(alignments):
        uid = a.get('unit_id')
        matches = units.get(uid, []) if uid is not None else []
        unit = matches[0] if len(matches) == 1 else None
        if unit:
            aligned.add(uid)
        old_list = a.get('old_quotes')
        new_list = a.get('new_quotes')
        if old_list is None:
            old_list = [{'source_id': unit.get('memory_id') if unit else None,
                         'quote': a.get('old_quote'), 'unit_id': uid}] if uid is not None else []
        if new_list is None:
            new_list = [{'source_id': a.get('source_id'), 'quote': a.get('new_quote')}]
        if not isinstance(old_list, list):
            old_list = []
        if not isinstance(new_list, list):
            new_list = []
        old_checked, new_checked = [], []
        unit_pos, unit_error = _locate(old_memory, unit.get('quote')) if unit else (None, 'unit missing or duplicated')
        for side, items, checked in [('old', old_list, old_checked), ('new', new_list, new_checked)]:
            for q in items:
                q = q if isinstance(q, dict) else {}
                sid, quote = q.get('source_id'), q.get('quote')
                if side == 'old':
                    pos, error = _locate(old_memory, quote)
                    q_units = units.get(q.get('unit_id'), []) if uid is None else matches
                    q_unit = q_units[0] if len(q_units) == 1 else None
                    q_pos, q_error = _locate(old_memory, q_unit.get('quote')) if q_unit else (None, 'unit missing or duplicated')
                    if not q_unit:
                        error = error or 'old unit missing or duplicated'
                    elif q_error:
                        error = error or q_error
                    elif uid is not None and q.get('unit_id') not in (None, uid):
                        error = error or 'old quote unit_id mismatch'
                    elif not q_unit.get('memory_id') or sid != q_unit.get('memory_id'):
                        error = error or 'old quote source_id does not match unit memory_id'
                    elif not error and not (q_pos['start'] <= pos['start'] and pos['end'] <= q_pos['end']):
                        error = 'old quote outside its designated unit'
                    ref = q_unit.get('source_ref') if q_unit else None
                else:
                    sm = sources.get(sid, [])
                    pos, error = _locate(sm[0].get('text'), quote) if len(sm) == 1 and sid else (None, 'evidence source missing or duplicated')
                    if len(sm) == 1 and not sm[0].get('source_ref'):
                        error = error or 'evidence source_ref missing'
                    if len(sm) == 1 and sm[0].get('speaker') != 'user':
                        error = error or 'evidence speaker missing or not user'
                    if len(sm) == 1 and sm[0].get('side') != 'new':
                        error = error or 'evidence source side missing or not new'
                    ref = sm[0].get('source_ref') if len(sm) == 1 else None
                entry = {'side': side, 'unit_id': q.get('unit_id', uid), 'source_id': sid, 'quote': quote,
                         'position': None if error else pos, 'source_ref': ref, 'status': 'invalid' if error else 'valid', 'reason': error}
                checked.append(entry)
                out['quote_checks'].append({'alignment_index': index, **entry})
        old_ok = bool(old_checked) and all(q['status'] == 'valid' for q in old_checked)
        new_ok = bool(new_checked) and all(q['status'] == 'valid' for q in new_checked)
        base = {'candidate_index': index, 'judgment_kind': 'old_relation',
                'unit_id': uid, 'fact': unit.get('fact') if unit else None, 'relation': a.get('relation'),
                'subject': a.get('old_subject'), 'attribute': a.get('old_attribute'),
                'old_value': a.get('old_value'), 'new_value': a.get('new_value'),
                'old_quotes': old_checked, 'new_quotes': new_checked,
                'old_quote': old_checked[0]['quote'] if len(old_checked) == 1 else None,
                'old_position': old_checked[0]['position'] if len(old_checked) == 1 else None,
                'new_quote': new_checked[0]['quote'] if len(new_checked) == 1 else None,
                'new_position': new_checked[0]['position'] if len(new_checked) == 1 else None,
                'source_id': new_checked[0]['source_id'] if len(new_checked) == 1 else None,
                'source_ref': new_checked[0]['source_ref'] if len(new_checked) == 1 else None,
                'memory_id': unit.get('memory_id') if unit else None,
                'old_source_ref': unit.get('source_ref') if unit else None,
                'note': a.get('note'), 'time_note': a.get('time_note'),
                'missing_reasons': a.get('missing_reasons', []), 'validation_errors': a.get('validation_errors', []),
                'unknowns': a.get('unknowns', []), 'temporal_order': a.get('temporal_order'),
                'old_conditions': a.get('old_conditions'), 'new_conditions': a.get('new_conditions'),
                'semantic_support': a.get('semantic_support'), 'semantic_basis': a.get('semantic_basis')}
        addition_kind = a.get('relation') in ('new_information', 'supplement', 'plan')
        if uid is not None or not addition_kind:
            candidate_bases[(index, 'old_relation')] = base
        reason = None
        if a.get('validation_errors'):
            reason = 'upstream validation errors: ' + str(a['validation_errors'])
        elif a.get('missing_reasons'):
            reason = 'missing upstream information: ' + '; '.join(map(str, a['missing_reasons']))
        elif not new_ok:
            reason = 'new quote or source invalid or missing'
        elif uid is not None and not old_ok:
            reason = 'old quote or source invalid or missing'
        elif uid is not None and len(old_checked) != 1:
            reason = 'multiple old quotes lack a unique local action binding'
        elif uid is not None and unit is None:
            reason = 'alignment references missing or duplicated unit'
        relation = a.get('relation')
        semantic = (a.get('semantic_support') == 'supported'
                    and _basis_valid(a.get('semantic_basis'), old_checked, new_checked, require_new=True))
        if relation in ('new_information', 'supplement', 'plan'):
            # A new claim stands on its own evidence; a bad old binding is not
            # permission to infer an impact on that old fact.
            # Only explicitly old-side validation defects can be separated;
            # global or unclassified errors remain blockers.
            def old_only(error):
                if isinstance(error, dict):
                    return '.old_' in str(error.get('path', ''))
                return isinstance(error, str) and (error.startswith('old ') or error.startswith('old_'))
            add_errors = [e for e in a.get('validation_errors', []) if not old_only(e)]
            add_missing = [e for e in a.get('missing_reasons', []) if not old_only(e)]
            add_reason = None
            if not new_ok:
                add_reason = 'new quote or source invalid or missing'
            elif add_errors:
                add_reason = 'upstream validation errors: ' + str(add_errors)
            elif add_missing:
                add_reason = 'missing upstream information: ' + '; '.join(map(str, add_missing))
            if not semantic:
                add_reason = add_reason or 'semantic support or bound basis missing'
            if any(not a.get(k) for k in ('new_subject', 'new_attribute', 'new_value')):
                add_reason = add_reason or 'new subject, attribute or value missing'
            modality = a.get('modality')
            if modality not in ('asserted', 'planned'):
                add_reason = add_reason or 'explicit modality missing'
            if relation == 'plan' and modality != 'planned':
                add_reason = add_reason or 'plan requires planned modality'
            add_base = {**base, 'subject': a.get('new_subject'), 'attribute': a.get('new_attribute'),
                        'value': a.get('new_value'), 'scope': a.get('new_conditions'), 'status': modality,
                        'judgment_kind': 'new_claim'}
            candidate_bases[(index, 'new_claim')] = add_base
            if add_reason:
                out['uncertain'].append({**add_base, 'reason': add_reason})
            else:
                out['add'].append({**add_base, 'reason': 'independent evidence-supported addition'})
            if uid is None:
                continue
            # Addition does not decide what happened to the old claim.
            if not a.get('no_impact_confirmed'):
                reason = reason or 'impact of new information on old fact is not established'
            relation = 'unrelated'
        if uid is None:
            if relation not in ('new_information', 'supplement', 'plan'):
                out['uncertain'].append({**base, 'reason': reason or 'no old unit and no independently supported addition'})
            continue
        if relation not in ('change', 'same', 'unrelated', 'unknown'):
            reason = reason or 'unsupported relation'
        if relation == 'unknown':
            reason = reason or a.get('reason') or a.get('note') or 'alignment relation unknown'
        if relation == 'unrelated' and not a.get('no_impact_confirmed'):
            reason = reason or 'unrelated label does not establish preservation'
        if relation in ('change', 'same', 'unrelated') and not semantic:
            reason = reason or 'semantic support or bound basis missing'
        if relation in ('change', 'same'):
            fields = ('old_subject', 'new_subject', 'old_attribute', 'new_attribute', 'old_value', 'new_value')
            if any(a.get(k) is None or a.get(k) == '' for k in fields):
                reason = reason or 'subject, attribute or value missing'
            elif a['old_subject'] != a['new_subject'] or a['old_attribute'] != a['new_attribute']:
                reason = reason or 'subject or attribute mismatch'
            elif relation == 'same' and a['old_value'] != a['new_value']:
                reason = reason or 'same relation has conflicting values'
        if relation == 'change' and a.get('old_value') != a.get('new_value') and a.get('modality') != 'asserted':
            reason = reason or 'change requires asserted rather than planned or unknown modality'
        if relation == 'same' and a.get('modality') == 'planned':
            reason = reason or 'planned evidence does not assert current same value'
        names = old_cells = new_names = new_cells = None
        try:
            names, old_cells = _conditions(a.get('old_conditions'))
            nc = a.get('new_conditions')
            if relation == 'unrelated' and a.get('no_impact_confirmed'):
                new_names, new_cells = names, old_cells
            elif isinstance(nc, dict) and nc.get('kind') == 'same_as_old':
                new_names, new_cells = names, old_cells
            else:
                new_names, new_cells = _conditions(nc)
            if names is not None and new_names is not None and names != new_names:
                raise ValueError('condition dimensions differ')
        except ValueError as exc:
            # A partially computed right-hand side cannot be compared after
            # parsing/partition failure: v2 retained it and turned an invalid
            # comparison into an empty intersection and an invented preserve.
            new_names, new_cells = None, None
            reason = (reason + '; scope: ' if reason else '') + str(exc)
            base['scope_error'] = str(exc)
        temporal = a.get('temporal_order') or {}
        temporal_relation = temporal.get('relation') if isinstance(temporal, dict) else None
        if relation == 'change' and a.get('old_value') != a.get('new_value'):
            if temporal_relation not in ('before', 'after', 'same'):
                reason = reason or 'temporal order unknown'
            elif not _basis_valid(temporal.get('basis'), old_checked, new_checked, require_new=True):
                reason = reason or 'temporal basis missing or not bound to associated quotes'
            elif not isinstance(temporal.get('explanation'), str) or not temporal['explanation'].strip():
                reason = reason or 'temporal relationship explanation missing'
            elif temporal_relation == 'same':
                reason = reason or 'conflicting different values at same time'
        # A proposed finite condition cannot prove its complement unaffected
        # until its scope/semantics and linked citations have independent
        # support. A timing unknown alone does not invalidate an otherwise
        # independently supported condition, but an invalid cited basis does.
        scope_trusted = bool(semantic and new_ok and old_ok
                             and not a.get('validation_errors') and not a.get('missing_reasons'))
        if isinstance(temporal, dict) and temporal.get('basis') and not _basis_valid(temporal.get('basis'), old_checked, new_checked, require_new=True):
            scope_trusted = False
        rec = {'a': a, 'base': base, 'reason': reason, 'names': names, 'old_cells': old_cells,
               'new_names': new_names, 'new_cells': new_cells, 'relation': relation,
               'temporal_relation': temporal_relation, 'scope_trusted': scope_trusted}
        records.setdefault(uid, []).append(rec)
        for note in a.get('uncertainties', []):
            out['uncertain'].append({**base, 'reason': note})

    for uid, group in units.items():
        unit = group[0]
        unit_pos, unit_error = _locate(old_memory, unit.get('quote'))
        if len(group) != 1:
            unit_error = 'unit id duplicated'
        if uid not in aligned or unit_error:
            out['uncertain'].append({'unit_id': uid, 'fact': unit.get('fact'), 'old_quote': unit.get('quote'),
                                     'old_position': unit_pos, 'reason': unit_error or 'no alignment for unit'})
        for claim in unit.get('protected_claims', []):
            pos, err = _locate(old_memory, claim.get('quote'))
            if not unit.get('memory_id'):
                err = err or 'old memory_id missing'
            if not err and (unit_error or not (unit_pos['start'] <= pos['start'] and pos['end'] <= unit_pos['end'])):
                err = 'protected quote outside unit or unit invalid'
            if err:
                pos = None
            out['quote_checks'].append({'unit_id': uid, 'side': 'old', 'kind': 'protected_claim',
                                        'quote': claim.get('quote'), 'position': pos,
                                        'status': 'invalid' if err else 'valid', 'reason': err})
            entry = {'unit_id': uid, 'fact': claim.get('fact'), 'old_quote': claim.get('quote'),
                     'old_position': pos, 'memory_id': unit.get('memory_id'), 'old_source_ref': unit.get('source_ref')}
            if err:
                out['uncertain'].append({**entry, 'reason': err})
            else:
                entry['reason'] = 'explicit protected claim'
                out['protected_facts'].append(entry)
                out['preserve'].append(entry)
        recs = records.get(uid, [])
        if not recs:
            continue
        known = [r for r in recs if r['old_cells'] is not None]
        if not known:
            for r in recs:
                out['uncertain'].append({**r['base'], 'reason': r['reason'] or 'old condition missing'})
            continue
        names, cells = known[0]['names'], known[0]['old_cells']
        old_range_is_finite = names is not None
        if any(r['names'] != names or set(r['old_cells']) != set(cells) for r in known):
            for r in recs:
                out['uncertain'].append({**r['base'], 'reason': 'inconsistent old condition across alignments'})
            continue
        # `unconditional` means the old claim has no restriction on the
        # compared dimensions. It is not a finite one-cell universe. Finite
        # new cells therefore overlap it, but the rest cannot be enumerated.
        finite = [r for r in recs if r['new_names'] is not None and r['new_cells'] is not None]
        if names is None and finite:
            comparison_names = finite[0]['new_names']
            if any(r['new_names'] != comparison_names for r in finite):
                for r in recs:
                    out['uncertain'].append({**r['base'], 'scope': {'kind': 'unknown'},
                                             'reason': 'finite new condition dimensions differ; overlap and remainder cannot be determined'})
                continue
            names = comparison_names
            cells = sorted({cell for r in finite for cell in r['new_cells']})
            unrestricted_units.add(uid)
            out['uncertain'].append({**known[0]['base'], 'scope': {'kind': 'unknown'},
                                     'reason': 'unconditional old scope remainder cannot be enumerated relative to proposed finite conditions',
                                     # These are solely upstream proposals: an
                                     # unreviewed model may have malformed or
                                     # semantically unsupported dimensions.
                                     'candidate_new_cells': [_scope(names, cell) for cell in cells]})
        assignments = {cell: [] for cell in cells}
        for r in recs:
            if old_range_is_finite and r['new_names'] is not None and not r['scope_trusted']:
                # Do not use an unaudited finite candidate to exclude other
                # old combinations from possible impact.
                covered = set(cells)
                r['reason'] = (r['reason'] + '; ' if r['reason'] else '') + 'candidate scope not independently supported'
            elif r['old_cells'] is None or r['new_cells'] is None:
                covered = set(cells)
            elif r['new_names'] is None:
                covered = set(cells)
            else:
                covered = set(cells) & set(r['new_cells'])
            for cell in covered:
                assignments[cell].append(r)
            if r['new_names'] is not None and r['new_cells'] is not None and r['names'] == r['new_names']:
                for cell in sorted(set(r['new_cells']) - set(cells)):
                    out['uncertain'].append({**r['base'], 'scope': _scope(names, cell),
                                             'reason': 'evidence outside old scope; independent addition not established'})
        for cell in cells:
            claims = assignments[cell]
            uncertain = [r for r in claims if r['reason']]
            if uncertain:
                # An unresolved overlapping claim blocks a decision for all
                # other claims in this cell; it does not make them disappear.
                for r in claims:
                    reason = r['reason'] or 'scope decision blocked by another unresolved overlapping candidate'
                    out['uncertain'].append({**r['base'], 'scope': _scope(names, cell), 'reason': reason})
                continue
            active = [r for r in claims if r['relation'] in ('change', 'same') and r['temporal_relation'] != 'before']
            new_values = {r['a'].get('new_value') for r in active}
            base = (claims[0] if claims else known[0])['base']
            if len(new_values) > 1:
                out['uncertain'].append({**base, 'scope': _scope(names, cell), 'reason': 'conflicting evidence values for same scope',
                                         'conflicting_claims': [r['base'] for r in active]})
            elif active and active[0]['a'].get('old_value') != active[0]['a'].get('new_value'):
                selected = active[0]
                out['modify'].append({**selected['base'], 'scope': _scope(names, cell),
                                      'reason': 'different values and evidenced later state'})
                if selected['a'].get('preserve_history'):
                    h = {**selected['base'], 'scope': _scope(names, cell), 'status': 'historical',
                         'reason': 'explicitly retained as history, not as current'}
                    out['preserve'].append(h)
            else:
                evidence_same = next((r for r in active if r['a'].get('new_value') == r['a'].get('old_value')), None)
                if evidence_same:
                    out['preserve'].append({**evidence_same['base'], 'scope': _scope(names, cell),
                                            'current_evidence_value': evidence_same['a']['new_value'],
                                            'reason': 'same value supported by new evidence'})
                else:
                    out['preserve'].append({**base, 'scope': _scope(names, cell),
                                            'reason': 'unchanged, earlier evidence, or outside evidence scope'})

    # Conservative completeness backstop for all input judgments, including
    # unsupported/missing units and aggregation branches which select one
    # representative. Never silently treat a representative as proof of the
    # other input's decision.
    action_categories = ('modify', 'preserve', 'uncertain', 'add')
    emitted = {(item.get('candidate_index'), item.get('judgment_kind'))
               for category in action_categories for item in out[category]}
    for key, base in candidate_bases.items():
        if key not in emitted:
            out['uncertain'].append({**base, 'scope': {'kind': 'unknown'},
                'reason': 'coverage backstop: candidate judgment received no separate decision in scope aggregation'})

    # A fallback for an unresolved old relation may overlap an otherwise
    # editable claim in the very same unit. v3's later check only covers
    # different units, so hold such edits explicitly.
    for item in list(out['modify']):
        for held in out['uncertain']:
            if (held.get('reason', '').startswith('coverage backstop:')
                    and held.get('judgment_kind') == 'old_relation'
                    and held.get('unit_id') is not None
                    and held.get('unit_id') == item.get('unit_id')
                    and _may_overlap(item.get('scope'), held.get('scope'))):
                out['modify'].remove(item)
                out['uncertain'].append({**item, 'reason': 'edit blocked by unresolved same-unit candidate coverage'})
                break

    # Across independent sources/units, disagreement in possibly overlapping
    # scope blocks asserted actions. A planned claim is not a current state.
    actions = ([('modify', x) for x in out['modify']]
               + [('add', x) for x in out['add'] if x.get('status') != 'planned']
               + [('preserve', x) for x in out['preserve']
                  if x.get('status') != 'historical'
                  and (x.get('current_evidence_value') is not None or x.get('old_value') is not None)])
    bad = set()
    for i, (kind, left) in enumerate(actions):
        for j in range(i + 1, len(actions)):
            other_kind, right = actions[j]
            if not left.get('subject') or not left.get('attribute'):
                continue
            if (left['subject'], left['attribute']) != (right.get('subject'), right.get('attribute')):
                continue
            lv = left.get('new_value') if kind == 'modify' else left.get('current_evidence_value', left.get('old_value')) if kind == 'preserve' else left.get('value')
            rv = right.get('new_value') if other_kind == 'modify' else right.get('current_evidence_value', right.get('old_value')) if other_kind == 'preserve' else right.get('value')
            if lv is not None and rv is not None and lv != rv and _may_overlap(left.get('scope'), right.get('scope')):
                bad.update((i, j))
    for i in sorted(bad):
        kind, entry = actions[i]
        out[kind].remove(entry)
        out['uncertain'].append({**entry, 'reason': 'conflicting or potentially conflicting new evidence'})
    # Hold edits overlapping an unresolved *different* unit unless the
    # uncertain scope is explicitly disjoint.
    for item in list(out['modify']):
        pos = item.get('old_position')
        if not pos:
            out['modify'].remove(item)
            out['uncertain'].append({**item, 'reason': 'no unique local old quote'})
            continue
        for uncertain in out['uncertain']:
            if uncertain.get('unit_id') in (None, item['unit_id']):
                continue
            other = uncertain.get('old_position')
            quote = uncertain.get('old_quote')
            overlaps = bool(other and pos['start'] < other['end'] and other['start'] < pos['end'])
            if not other:
                # Missing or repeated alignment quotes cannot bypass the
                # safety check: test *all* possible original unit locations,
                # but never manufacture a unique position for the output.
                candidates = [quote] + [x.get('quote') for x in units.get(uncertain.get('unit_id'), [])]
                for candidate in candidates:
                    if not isinstance(candidate, str) or not candidate:
                        continue
                    start = old_memory.find(candidate)
                    while start != -1:
                        if pos['start'] < start + len(candidate) and start < pos['end']:
                            overlaps = True
                            break
                        start = old_memory.find(candidate, start + 1)
                    if overlaps:
                        break
            # Ambiguous/unverified quote locations cannot safely serve as an
            # editing protection even when condition scopes appear disjoint.
            if overlaps and (not other or _may_overlap(item.get('scope'), uncertain.get('scope'))):
                out['modify'].remove(item)
                out['uncertain'].append({**item, 'reason': 'edit overlaps unresolved other unit'})
                break
    for item in out['modify']:
        pos = item['old_position']
        span = {'unit_id': item['unit_id'], **pos, 'old_quote': item['old_quote']}
        if span not in out['editable_spans']:
            out['editable_spans'].append(span)
    # Editing the same textual fragment must not discard an unrestricted
    # claim's unenumerated remainder. This is a retention constraint, not a
    # fabricated enumeration or a claim that the remainder was verified.
    for uid in unrestricted_units:
        modified = [x for x in out['modify'] if x['unit_id'] == uid]
        if modified:
            protected = {**modified[0], 'scope': {'kind': 'unknown'},
                         'protected_scope': 'unrepresented_remainder',
                         'known_modified_scopes': [x['scope'] for x in modified],
                         'reason': 'retain the old assertion outside the authorised finite changes; remainder is not enumerable'}
            out['protected_facts'].append(protected)
    for item in out['preserve']:
        pos = item.get('old_position')
        if pos and item not in out['protected_facts'] and any(pos['start'] < s['end'] and s['start'] < pos['end'] for s in out['editable_spans']):
            out['protected_facts'].append(item)
    # A short sentence may contain both an editable finite combination and a
    # different unresolved one. Protect the latter as uncertain; this is an
    # editing constraint and must not be promoted to a known true fact.
    for item in out['uncertain']:
        pos = item.get('old_position')
        if pos and any(pos['start'] < s['end'] and s['start'] < pos['end']
                       for s in out['editable_spans']):
            protected = {**item, 'scope': item.get('scope') or {'kind': 'unknown'},
                         'status': 'uncertain', 'protected_scope': 'uncertain',
                         'reason': 'do not destroy the unresolved old claim when editing this span',
                         'uncertainty_reason': item.get('reason')}
            if protected not in out['protected_facts']:
                out['protected_facts'].append(protected)
    coverage = []
    for index, alignment in enumerate(alignments):
        judgments = []
        for candidate_index, kind in candidate_bases:
            if candidate_index != index:
                continue
            outputs = [{'category': category, 'index': position}
                       for category in action_categories
                       for position, item in enumerate(out[category])
                       if item.get('candidate_index') == index and item.get('judgment_kind') == kind]
            if not outputs:
                raise RuntimeError('candidate coverage invariant failed')
            judgments.append({'kind': kind, 'outputs': outputs})
        if not judgments:
            raise RuntimeError('candidate has no tracked judgments')
        coverage.append({'candidate_index': index, 'note': alignment.get('note'),
                         'relation': alignment.get('relation'), 'judgments': judgments})
    out['candidate_coverage'] = coverage
    return out
