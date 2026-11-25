"""Loss-aware adapters for saved evidence_aligner v1/v2/v3 artifacts.

No manual annotations or interpretations are used. Empty qualifier arrays are
not converted into unconditional scope. Source bindings are independently
checked against the saved input units and source texts.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

_RELATIONS = {
    'state_change': 'change', 'historical_correction': 'change',
    'plan': 'plan', 'supplement': 'supplement', 'new_information': 'unrelated',
    'support': 'unknown', 'no_clear_change': 'unknown', 'uncertain': 'unknown',
}


def detect_version(record):
    if 'relation' in record:
        return 'v3'
    if 'old_claim' in record:
        return 'v2'
    return 'v1'


def adapt_aligner_output(artifact, version=None):
    """Return planner alignment records; retain originals and loss diagnostics.

    Input is the complete saved per-case artifact, not just parsed output.
    A single simplified quote is supplied only when its provenance is unique.
    Multiple old IDs/quotes or new quotes remain in raw data and are deferred.
    """
    payload = artifact['input']
    result = artifact['result']
    parsed = result.get('parsed') or {}
    memory = payload['source_texts']['memory']
    sources = {s['source_id']: s for s in [memory, *payload['source_texts'].get('messages', [])]}
    old = {u['unit_id']: u for u in payload['old_units']}
    new = {u['unit_id']: u for u in payload['new_units']}
    errors = (result.get('structure_errors') or []) + (result.get('validation_errors') or []) + (result.get('parse_errors') or [])
    adapted = []
    for i, record in enumerate(parsed.get('records', [])):
        record_version = version or detect_version(record)
        reasons = []
        old_ids = record.get('old_unit_ids') or []
        new_ids = record.get('new_unit_ids') or []
        relevant_errors = []
        for error in errors:
            path = error.get('path', '') if isinstance(error, dict) else ''
            match = re.match(r'^records\[(\d+)\]', path)
            if not match or int(match.group(1)) == i:
                relevant_errors.append(copy.deepcopy(error))
                reasons.append('upstream validation error: ' + str(error))
        if len(old_ids) > 1:
            reasons.append('multiple old unit IDs; no unique unit binding')
        if any(uid not in old for uid in old_ids) or any(uid not in new for uid in new_ids):
            reasons.append('linked unit ID not found in input')

        def quotes(side):
            qlist = record.get(side + '_quotes') or []
            units = old if side == 'old' else new
            ids = old_ids if side == 'old' else new_ids
            resolved = []
            for q in qlist:
                quote = q.get('quote') if isinstance(q, dict) else q
                explicit_id = q.get('source_id') if isinstance(q, dict) else None
                if not isinstance(quote, str) or not quote:
                    reasons.append(side + ' quote is empty or malformed')
                    continue
                candidates = set()
                for uid in ids:
                    unit = units.get(uid, {})
                    sid = unit.get('source_id') or (memory['source_id'] if side == 'old' else None)
                    if sid and any(quote in uq for uq in unit.get('memory_quotes', []) if isinstance(uq, str)):
                        candidates.add(sid)
                if explicit_id is not None:
                    candidates &= {explicit_id}
                if len(candidates) != 1:
                    reasons.append(side + ' quote has missing, ambiguous, or mismatched linked-unit source: ' + quote)
                    resolved.append({'quote': quote, 'source_id': None})
                    continue
                sid = next(iter(candidates))
                source = sources.get(sid)
                if source is None or quote not in source.get('text', ''):
                    reasons.append(side + ' quote absent from source: ' + quote)
                    sid = None
                elif side == 'old' and sid != memory['source_id']:
                    reasons.append('old quote does not refer to old memory')
                    sid = None
                elif side == 'new' and (source.get('side') != 'new' or source.get('speaker') != 'user'):
                    reasons.append('new quote source is not a new user message')
                    sid = None
                resolved.append({'quote': quote, 'source_id': sid})
            if len(resolved) != 1:
                if ids or side == 'new':
                    reasons.append(side + ' side lacks a single uniquely represented quote')
                return None, None, resolved
            return resolved[0]['quote'], resolved[0]['source_id'], resolved

        old_quote, old_sid, old_quotes = quotes('old')
        new_quote, new_sid, new_quotes = quotes('new')
        if record_version == 'v2':
            oc = record.get('old_claim') or {}
            nc = record.get('new_claim') or {}
            old_subject, new_subject = oc.get('subject'), nc.get('subject')
            old_attribute, new_attribute = oc.get('attribute'), nc.get('attribute')
            # object and statement are preserved in raw_record, but are not
            # necessarily an attribute value and therefore cannot fill value.
            old_value = new_value = None
        else:
            old_subject = new_subject = None
            old_attribute = record.get('attribute') if old_ids else None
            new_attribute = record.get('attribute')
            old_value = record.get('old_value') if record_version == 'v1' else None
            new_value = None
        relation = record.get('relation') if record_version == 'v3' else record.get('change_type')
        for name, value in [('old_subject', old_subject), ('new_subject', new_subject),
                            ('old_attribute', old_attribute), ('new_attribute', new_attribute),
                            ('old_value', old_value), ('new_value', new_value)]:
            if value is None and (old_ids or not name.startswith('old_')):
                reasons.append('not explicitly supplied as ' + name)
        reasons.extend(['old_conditions not explicitly normalized', 'new_conditions not explicitly normalized'])
        if record.get('missing_evidence'):
            reasons.extend('model missing evidence: ' + str(x) for x in record['missing_evidence'])
        if record.get('unknowns'):
            reasons.extend('model unknown: ' + str(x) for x in record['unknowns'])
        adapted.append({
            'unit_id': old_ids[0] if len(old_ids) == 1 else None,
            'relation': _RELATIONS.get(relation, 'unknown'),
            'old_subject': old_subject, 'new_subject': new_subject,
            'old_attribute': old_attribute, 'new_attribute': new_attribute,
            'old_value': old_value, 'new_value': new_value,
            'old_quote': old_quote, 'new_quote': new_quote, 'source_id': new_sid,
            'old_conditions': None, 'new_conditions': None,
            'missing_reasons': reasons,
            'upstream_version': record_version, 'upstream_relation': relation,
            'upstream_target_relation': record.get('target_relation'),
            'upstream_structure_errors': relevant_errors,
            'old_quote_source_id': old_sid, 'resolved_old_quotes': old_quotes,
            'resolved_new_quotes': new_quotes, 'raw_record': copy.deepcopy(record),
        })
    # Coverage is metadata, not a model record. Expose explicitly rather than
    # silently treating unmentioned or unmatched units as verified facts.
    coverage = result.get('coverage') or {}
    unmatched = parsed.get('unmatched_old_unit_ids') or []
    unhandled_old = coverage.get('unhandled_old_unit_ids') or coverage.get('uncovered_old_unit_ids') or []
    for uid in dict.fromkeys([*unmatched, *unhandled_old]):
        reasons = []
        if uid in unmatched:
            reasons.append('model explicitly marked old unit unmatched; this does not verify the fact')
        if uid in unhandled_old:
            reasons.append('upstream old unit unhandled or uncovered')
        unit = old.get(uid, {})
        unit_quotes = unit.get('memory_quotes') or []
        adapted.append({'unit_id': uid, 'relation': 'unknown',
                        'old_subject': None, 'new_subject': None,
                        'old_attribute': None, 'new_attribute': None,
                        'old_value': None, 'new_value': None,
                        'old_quote': unit_quotes[0] if len(unit_quotes) == 1 else None,
                        'new_quote': None, 'source_id': None,
                        'old_conditions': None, 'new_conditions': None,
                        'missing_reasons': reasons, 'upstream_coverage': True})
    unhandled_new = coverage.get('unhandled_new_unit_ids') or coverage.get('uncovered_new_unit_ids') or []
    for uid in unhandled_new:
        adapted.append({'unit_id': None, 'relation': 'unknown',
                        'old_quote': None, 'new_quote': None, 'source_id': None,
                        'old_conditions': None, 'new_conditions': None,
                        'missing_reasons': ['upstream new unit unhandled or uncovered: ' + str(uid)],
                        'unhandled_new_unit_id': uid, 'upstream_coverage': True})
    if not parsed.get('records') and errors and not adapted:
        adapted.append({'unit_id': None, 'relation': 'unknown', 'old_quote': None,
                        'new_quote': None, 'source_id': None, 'old_conditions': None,
                        'new_conditions': None, 'missing_reasons': ['upstream parse or validation errors: ' + str(errors)],
                        'upstream_coverage': True})
    return adapted


def load_aligner_case(path):
    """Load a saved artifact and return the four arguments to build_scope_plan."""
    artifact = json.loads(Path(path).read_text(encoding='utf-8'))
    payload = artifact['input']
    memory = payload['source_texts']['memory']
    old_units = [{'id': u['unit_id'],
                  'quote': u['memory_quotes'][0] if len(u.get('memory_quotes', [])) == 1 else None,
                  'fact': u.get('raw_statement'), 'memory_id': memory.get('source_id'),
                  'source_ref': memory.get('source_ref')} for u in payload['old_units']]
    evidence_sources = [copy.deepcopy(s) for s in payload['source_texts'].get('messages', [])
                        if s.get('side') == 'new' and s.get('speaker') == 'user']
    return memory['text'], old_units, evidence_sources, adapt_aligner_output(artifact)
