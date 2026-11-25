"""Loss-aware adapter for saved evidence_aligner artifacts; no model calls.

Every model record stays intact and its quote/source/unit bindings are checked
independently. Scope, chronological ordering and semantic support are not
invented from prose, empty lists, or relative time words.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

_RELATIONS = {'state_change': 'change', 'historical_correction': 'change',
              'plan': 'plan', 'supplement': 'supplement', 'support': 'unknown',
              'no_clear_change': 'unknown', 'uncertain': 'unknown',
              'unrelated': 'unrelated'}


def detect_version(record):
    return 'v3' if 'relation' in record else 'v2' if 'old_claim' in record else 'v1'


def adapt_aligner_output(artifact, version=None):
    """Adapt a complete saved case; never treat a model relation as verification."""
    payload, result = artifact['input'], artifact['result']
    parsed = result.get('parsed') or {}
    memory = payload['source_texts']['memory']
    source_lists = {}
    for src in [memory, *payload['source_texts'].get('messages', [])]:
        source_lists.setdefault(src.get('source_id'), []).append(src)
    old = {u['unit_id']: u for u in payload['old_units']}
    new = {u['unit_id']: u for u in payload['new_units']}
    errors = (result.get('structure_errors') or []) + (result.get('validation_errors') or []) + (result.get('parse_errors') or [])
    adapted = []
    for i, record in enumerate(parsed.get('records', [])):
        v = version or detect_version(record)
        old_ids, new_ids = record.get('old_unit_ids') or [], record.get('new_unit_ids') or []
        validation_errors = []
        missing_reasons = []
        for error in errors:
            path = error.get('path', '') if isinstance(error, dict) else ''
            match = re.match(r'^records\[(\d+)\]', path)
            if match and int(match.group(1)) == i:
                validation_errors.append(copy.deepcopy(error))
        for side, ids, units in [('old', old_ids, old), ('new', new_ids, new)]:
            for uid in ids:
                if uid not in units:
                    validation_errors.append(f'{side} linked unit not found: {uid}')

        def resolve_quotes(side):
            units, ids = (old, old_ids) if side == 'old' else (new, new_ids)
            out = []
            for item in record.get(side + '_quotes') or []:
                quote = item.get('quote') if isinstance(item, dict) else item
                explicit = item.get('source_id') if isinstance(item, dict) else None
                if not isinstance(quote, str) or not quote:
                    validation_errors.append(f'{side} quote malformed or empty')
                    out.append({'source_id': explicit, 'quote': quote})
                    continue
                matches = []
                for uid in ids:
                    unit = units.get(uid, {})
                    sid = unit.get('source_id') or (memory.get('source_id') if side == 'old' else None)
                    if sid and (explicit is None or sid == explicit) and any(quote in q for q in unit.get('memory_quotes', []) if isinstance(q, str)):
                        matches.append((uid, sid))
                sids = {sid for _, sid in matches}
                sid = next(iter(sids)) if len(sids) == 1 else None
                ref = {'source_id': sid, 'quote': quote}
                if explicit is not None and explicit != sid:
                    ref['reported_source_id'] = explicit
                if len(matches) == 1:
                    ref['unit_id'] = matches[0][0]
                else:
                    validation_errors.append(f'{side} quote missing or ambiguous linked-unit binding: {quote}')
                srcs = source_lists.get(sid, [])
                if sid is None or len(srcs) != 1 or quote not in srcs[0].get('text', ''):
                    validation_errors.append(f'{side} quote missing or ambiguous in designated source: {quote}')
                    ref['source_id'] = None
                elif srcs[0]['text'].find(quote, srcs[0]['text'].find(quote) + 1) >= 0:
                    validation_errors.append(f'{side} quote repeated in designated source: {quote}')
                if sid is not None and len(srcs) == 1 and side == 'old' and sid != memory.get('source_id'):
                    validation_errors.append('old quote source does not match memory source')
                elif sid is not None and len(srcs) == 1 and side == 'new' and (srcs[0].get('side') != 'new' or srcs[0].get('speaker') != 'user'):
                    validation_errors.append('new quote source is not a new user message')
                out.append(ref)
            if (ids or side == 'new') and not out:
                validation_errors.append(f'{side} quote missing')
            bound = {q.get('unit_id') for q in out}
            for uid in ids:
                if uid not in bound:
                    validation_errors.append(f'{side} linked unit lacks unambiguous quote: {uid}')
            return out

        old_quotes, new_quotes = resolve_quotes('old'), resolve_quotes('new')
        if v == 'v2':
            oc, nc = record.get('old_claim') or {}, record.get('new_claim') or {}
            old_subject, new_subject = oc.get('subject'), nc.get('subject')
            old_attribute, new_attribute = oc.get('attribute'), nc.get('attribute')
            old_value = new_value = None
        else:
            old_subject = new_subject = None
            old_attribute = record.get('attribute') if old_ids else None
            new_attribute = record.get('attribute')
            old_value = record.get('old_value') if v == 'v1' else None
            new_value = None
        relation = record.get('relation') if v == 'v3' else record.get('change_type')
        if relation == 'new_information':
            normalized_relation = 'new_information' if not old_ids else 'unknown'
            if old_ids:
                missing_reasons.append('new_information is linked to an old unit; independence requires confirmation')
        else:
            normalized_relation = _RELATIONS.get(relation, 'unknown')
        for field, val in [('old_subject', old_subject), ('new_subject', new_subject),
                           ('old_attribute', old_attribute), ('new_attribute', new_attribute),
                           ('old_value', old_value), ('new_value', new_value)]:
            if val is None and (old_ids or not field.startswith('old_')):
                missing_reasons.append('not explicitly supplied as ' + field)
        missing_reasons += ['old_conditions not explicitly normalized', 'new_conditions not explicitly normalized'] if old_ids else ['new_conditions not explicitly normalized']
        old_one = old_quotes[0] if len(old_quotes) == 1 else {}
        new_one = new_quotes[0] if len(new_quotes) == 1 else {}
        unknowns = list(record.get('unknowns') or []) + list(record.get('missing_evidence') or [])
        adapted.append({
            'unit_id': old_ids[0] if len(old_ids) == 1 else None,
            'old_unit_ids': copy.deepcopy(old_ids), 'new_unit_ids': copy.deepcopy(new_ids),
            'relation': normalized_relation, 'upstream_relation': relation,
            'old_subject': old_subject, 'new_subject': new_subject,
            'old_attribute': old_attribute, 'new_attribute': new_attribute,
            'old_value': old_value, 'new_value': new_value,
            'old_quote': old_one.get('quote'), 'new_quote': new_one.get('quote'),
            'source_id': new_one.get('source_id'), 'old_quote_source_id': old_one.get('source_id'),
            'old_quotes': old_quotes, 'new_quotes': new_quotes,
            'resolved_old_quotes': copy.deepcopy(old_quotes), 'resolved_new_quotes': copy.deepcopy(new_quotes),
            'old_conditions': None, 'new_conditions': None,
            'temporal_order': {'relation': 'unknown', 'basis': []}, 'semantic_support': 'unknown',
            'qualifiers': copy.deepcopy(record.get('qualifiers', [])),
            'old_qualifiers': copy.deepcopy((record.get('old_claim') or {}).get('qualifiers', [])) if v == 'v2' else [],
            'new_qualifiers': copy.deepcopy((record.get('new_claim') or {}).get('qualifiers', [])) if v == 'v2' else [],
            'conditions': copy.deepcopy(record.get('conditions', [])),
            'time_expressions': copy.deepcopy(record.get('time_expressions', [])),
            'old_claim': copy.deepcopy(record.get('old_claim')), 'new_claim': copy.deepcopy(record.get('new_claim')),
            'unknowns': unknowns, 'validation_errors': validation_errors,
            'missing_reasons': missing_reasons,
            'upstream_structure_errors': copy.deepcopy([e for e in validation_errors if isinstance(e, dict)]),
            'upstream_version': v, 'upstream_target_relation': record.get('target_relation'),
            'raw_record': copy.deepcopy(record),
        })
    coverage = result.get('coverage') or {}
    unmatched = parsed.get('unmatched_old_unit_ids') or []
    unhandled_old = coverage.get('unhandled_old_unit_ids') or coverage.get('uncovered_old_unit_ids') or []
    for uid in dict.fromkeys([*unmatched, *unhandled_old]):
        reasons = []
        if uid in unmatched:
            reasons.append('model explicitly marked old unit unmatched; this does not verify the fact')
        if uid in unhandled_old:
            reasons.append('upstream old unit unhandled or uncovered')
        qs = old.get(uid, {}).get('memory_quotes') or []
        adapted.append({'unit_id': uid, 'relation': 'unknown', 'old_quote': qs[0] if len(qs) == 1 else None,
                        'new_quote': None, 'source_id': None, 'old_conditions': None, 'new_conditions': None,
                        'missing_reasons': reasons, 'validation_errors': [], 'upstream_coverage': True,
                        'temporal_order': {'relation': 'unknown', 'basis': []}, 'semantic_support': 'unknown'})
    unhandled_new = coverage.get('unhandled_new_unit_ids') or coverage.get('uncovered_new_unit_ids') or []
    for uid in unhandled_new:
        adapted.append({'unit_id': None, 'relation': 'unknown', 'old_quote': None, 'new_quote': None,
                        'source_id': None, 'old_conditions': None, 'new_conditions': None,
                        'missing_reasons': ['upstream new unit unhandled or uncovered: ' + str(uid)],
                        'validation_errors': [], 'unhandled_new_unit_id': uid, 'upstream_coverage': True,
                        'temporal_order': {'relation': 'unknown', 'basis': []}, 'semantic_support': 'unknown'})
    global_errors = [e for e in errors if not (isinstance(e, dict) and re.match(r'^records\[(\d+)\]', e.get('path', '')))]
    if global_errors:
        adapted.append({'unit_id': None, 'relation': 'unknown', 'old_quote': None, 'new_quote': None,
                        'source_id': None, 'old_conditions': None, 'new_conditions': None,
                        'missing_reasons': ['upstream non-record-specific error: ' + str(global_errors)],
                        'validation_errors': [], 'upstream_coverage': True,
                        'temporal_order': {'relation': 'unknown', 'basis': []}, 'semantic_support': 'unknown'})
    return adapted


def load_aligner_case(path):
    """Return old text, old units, all new-user sources, and adapted records."""
    artifact = json.loads(Path(path).read_text(encoding='utf-8'))
    payload, memory = artifact['input'], artifact['input']['source_texts']['memory']
    old_units = [{'id': u['unit_id'], 'memory_id': memory.get('source_id'), 'source_ref': memory.get('source_ref'),
                  'quote': u['memory_quotes'][0] if len(u.get('memory_quotes', [])) == 1 else None,
                  'fact': u.get('raw_statement')} for u in payload['old_units']]
    sources = [copy.deepcopy(s) for s in payload['source_texts'].get('messages', [])
               if s.get('side') == 'new' and s.get('speaker') == 'user']
    return memory['text'], old_units, sources, adapt_aligner_output(artifact)
