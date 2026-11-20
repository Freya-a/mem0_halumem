"""V2 claim-by-claim evidence alignment with deterministic provenance checks."""
from __future__ import annotations

import json
from pathlib import Path

from aligner import (MODEL, CHANGE_TYPES, _DATE, _empty_result, _error, _nonempty,
                     _prepare, extract_json, locate_fragment)

HERE = Path(__file__).resolve().parent
PROMPT_FILE = HERE / 'prompts' / 'alignment_v2.txt'
PROMPT_VERSION = 'alignment_v2'
TARGET_RELATIONS = {'same', 'partially_overlapping', 'different', 'unknown'}
QUALIFIER_KINDS = {'time', 'condition', 'negation', 'plan', 'simulation', 'other'}


def build_messages(old_units, new_units, source_texts):
    _prepare(old_units, new_units, source_texts)
    payload = {'old_units': old_units, 'new_units': new_units, 'source_texts': source_texts}
    return [{'role': 'system', 'content': PROMPT_FILE.read_text(encoding='utf-8').rstrip('\n')},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, indent=2)}]


def _spans(source, quote):
    result, start = [], 0
    while (position := source.find(quote, start)) != -1:
        result.append([position, position + len(quote)])
        start = position + 1
    return result


def parse_and_validate(raw, old_units, new_units, source_texts):
    result = _empty_result(old_units, new_units)
    result['quote_locations'] = []
    sources, maps = _prepare(old_units, new_units, source_texts)
    errors = result['validation_errors']
    try:
        data = extract_json(raw)
    except (ValueError, TypeError, AttributeError) as exc:
        result['status'] = 'parse_error'
        result['parse_errors'].append(_error('json_parse', '$', str(exc)))
        return result
    result['parsed'] = data
    if not isinstance(data, dict):
        errors.append(_error('schema', '$', 'top-level value must be an object'))
        return result
    records, unmatched = data.get('records'), data.get('unmatched_old_unit_ids')
    if not isinstance(records, list):
        errors.append(_error('schema', 'records', 'must be an array'))
        records = []
    if not isinstance(unmatched, list) or any(not _nonempty(u) for u in unmatched):
        errors.append(_error('schema', 'unmatched_old_unit_ids', 'must be an array of nonempty strings'))
        unmatched = []
    considered = {'old': set(), 'new': set()}
    for uid in unmatched:
        if uid not in maps['old']:
            errors.append(_error('unknown_unit_id', 'unmatched_old_unit_ids', uid))
        else:
            considered['old'].add(uid)
    if len(set(unmatched)) != len(unmatched):
        errors.append(_error('duplicate_unit_id', 'unmatched_old_unit_ids', 'duplicate ID'))
    result['coverage']['unmatched_old_unit_ids'] = [u for u in unmatched if u in maps['old']]
    linked_old = set()

    for index, record in enumerate(records):
        path = f'records[{index}]'
        if not isinstance(record, dict):
            errors.append(_error('schema', path, 'must be an object'))
            continue
        linked = {}
        for side in ('old', 'new'):
            key = side + '_unit_ids'
            ids = record.get(key)
            if not isinstance(ids, list) or any(not _nonempty(uid) for uid in ids) or (side == 'new' and not ids):
                errors.append(_error('schema', path + '.' + key, 'must be an ID array; new IDs must not be empty'))
                ids = []
            if len(set(ids)) != len(ids):
                errors.append(_error('duplicate_unit_id', path + '.' + key, 'duplicate ID'))
            linked[side] = [uid for uid in ids if uid in maps[side]]
            for uid in ids:
                if uid not in maps[side]:
                    errors.append(_error('unknown_unit_id', path + '.' + key, uid))
            considered[side].update(linked[side])
        linked_old.update(linked['old'])

        change = record.get('change_type')
        if not isinstance(change, str) or change not in CHANGE_TYPES:
            errors.append(_error('schema', path + '.change_type', 'invalid change type'))
        if change in ('state_change', 'historical_correction') and not linked['old']:
            errors.append(_error('missing_old_claim_for_change', path + '.old_unit_ids',
                                 'a change or correction needs an old claim to compare'))
        target = record.get('target_relation')
        if not isinstance(target, str) or target not in TARGET_RELATIONS:
            errors.append(_error('schema', path + '.target_relation', 'invalid target relation'))
        if not _nonempty(record.get('relation_explanation')):
            errors.append(_error('schema', path + '.relation_explanation', 'must be a nonempty string'))
        unknowns = record.get('unknowns')
        if not isinstance(unknowns, list) or any(not _nonempty(item) for item in unknowns):
            errors.append(_error('schema', path + '.unknowns', 'must be an array of nonempty strings'))

        def check_quote(item, side, item_path, *, within_unit):
            if not isinstance(item, dict) or not _nonempty(item.get('source_id')) or not _nonempty(item.get('quote')):
                errors.append(_error('schema', item_path, 'source_id and quote required'))
                return []
            sid, quote = item['source_id'], item['quote']
            matching = []
            if sid in sources and sources[sid]['side'] == side:
                for uid in linked[side]:
                    unit = maps[side][uid]
                    if unit['source_id'] != sid:
                        continue
                    if within_unit:
                        if locate_fragment(sources[sid]['text'], quote, unit['quotes'])['method'] == 'exact':
                            matching.append(uid)
                    elif quote in sources[sid]['text']:
                        matching.append(uid)
            spans = _spans(sources[sid]['text'], quote) if sid in sources else []
            result['quote_locations'].append({'path': item_path, 'source_id': sid, 'quote': quote,
                                              'spans': spans, 'matched_unit_ids': matching})
            if not matching:
                errors.append(_error('quote_provenance', item_path, 'quote not found in the linked source/units on the correct side'))
            return matching

        cited = {'old': set(), 'new': set()}
        quote_lists = {}
        for side in ('old', 'new'):
            key = side + '_quotes'
            quotes = record.get(key)
            if not isinstance(quotes, list):
                errors.append(_error('schema', path + '.' + key, 'must be an array'))
                quotes = []
            if (side == 'new' or linked['old']) and not quotes:
                errors.append(_error('schema', path + '.' + key, 'quote required'))
            if side == 'old' and not linked['old'] and quotes:
                errors.append(_error('schema', path + '.' + key, 'independent new fact cannot cite old units'))
            quote_lists[side] = quotes
            for qindex, quote in enumerate(quotes):
                cited[side].update(check_quote(quote, side, f'{path}.{key}[{qindex}]', within_unit=True))
            for uid in linked[side]:
                if uid not in cited[side]:
                    errors.append(_error('unit_without_quote', path + '.' + side + '_unit_ids', uid))

        for side in ('old', 'new'):
            key = side + '_claim'
            claim = record.get(key)
            if side == 'old' and not linked['old']:
                if key not in record or claim is not None:
                    errors.append(_error('schema', path + '.' + key, 'independent new fact requires null'))
                continue
            if not isinstance(claim, dict):
                errors.append(_error('schema', path + '.' + key, 'must be an object'))
                continue
            for field in ('subject', 'attribute', 'statement'):
                if not _nonempty(claim.get(field)):
                    errors.append(_error('schema', f'{path}.{key}.{field}', 'must be a nonempty string'))
            if 'object' not in claim or (claim['object'] is not None and not _nonempty(claim['object'])):
                errors.append(_error('schema', f'{path}.{key}.object', 'must be null or a nonempty string'))
            qualifiers = claim.get('qualifiers')
            if not isinstance(qualifiers, list):
                errors.append(_error('schema', f'{path}.{key}.qualifiers', 'must be an array'))
                qualifiers = []
            for qindex, qualifier in enumerate(qualifiers):
                qpath = f'{path}.{key}.qualifiers[{qindex}]'
                kind = qualifier.get('kind') if isinstance(qualifier, dict) else None
                if not isinstance(kind, str) or kind not in QUALIFIER_KINDS:
                    errors.append(_error('schema', qpath + '.kind', 'invalid qualifier kind'))
                check_quote(qualifier, side, qpath, within_unit=False)
            if 'event_date' not in claim:
                errors.append(_error('schema', f'{path}.{key}.event_date', 'field is required'))
            date = claim.get('event_date')
            if date is not None and (not _nonempty(date) or not _DATE.fullmatch(date)
                    or not any(isinstance(q, dict) and isinstance(q.get('quote'), str) and date in q['quote']
                               for q in quote_lists[side])):
                errors.append(_error('unsupported_event_date', f'{path}.{key}.event_date',
                                     'must appear as a date in a quote on this claim side'))

        evidence = record.get('change_evidence')
        if not isinstance(evidence, list):
            errors.append(_error('schema', path + '.change_evidence', 'must be an array'))
            evidence = []
        if change == 'state_change' and not evidence:
            errors.append(_error('missing_change_evidence', path + '.change_evidence', 'state_change requires new evidence'))
        for eindex, item in enumerate(evidence):
            epath = f'{path}.change_evidence[{eindex}]'
            check_quote(item, 'new', epath, within_unit=True)
            if (not isinstance(item, dict) or not _nonempty(item.get('source_id')) or not _nonempty(item.get('quote'))
                    or not any(isinstance(q, dict) and q.get('source_id') == item['source_id']
                               and isinstance(q.get('quote'), str) and item['quote'] in q['quote']
                               for q in quote_lists['new'])):
                errors.append(_error('change_evidence_not_in_new_quote', epath, 'must be within a cited new quote'))

    for uid in set(unmatched) & linked_old:
        errors.append(_error('conflicting_coverage', 'unmatched_old_unit_ids', uid))
    for side in ('old', 'new'):
        missing = [uid for uid in maps[side] if uid not in considered[side]]
        result['coverage']['uncovered_' + side + '_unit_ids'] = missing
        for uid in missing:
            errors.append(_error('uncovered_unit', side + '_units', uid))
    result['status'] = 'failed' if errors else 'passed'
    return result


def align_evidence_v2(old_units, new_units, source_texts, *, backend=None):
    try:
        messages = build_messages(old_units, new_units, source_texts)
    except (ValueError, TypeError) as exc:
        return {'status': 'input_error', 'parsed': None, 'raw_response': None, 'request_attempts': 0,
                'parse_errors': [], 'validation_errors': [_error('input', '$', str(exc))]}
    owns_backend = backend is None
    if owns_backend:
        try:
            from qwen_backend import QwenBackend
            backend = QwenBackend()
        except Exception as exc:
            result = _empty_result(old_units, new_units)
            result.update(status='configuration_error', raw_response=None, request_attempts=0,
                          configuration_error={'type': type(exc).__name__})
            return result
    try:
        response = backend(messages)
    except Exception as exc:
        result = _empty_result(old_units, new_units)
        result.update(status='request_error', raw_response=None, request_attempts=1,
                      request_error={'type': type(exc).__name__})
        return result
    finally:
        if owns_backend:
            backend.close()
    raw = response.get('content') if isinstance(response, dict) else None
    result = parse_and_validate(raw, old_units, new_units, source_texts)
    result.update(raw_response=raw, request_attempts=1,
                  returned_model=response.get('model') if isinstance(response, dict) else None)
    return result
