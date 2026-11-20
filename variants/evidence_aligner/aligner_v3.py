"""Evidence alignment v3: verbatim claims, auditable source resolution, no memory writes."""
from __future__ import annotations

import json
from pathlib import Path

from aligner import MODEL, CHANGE_TYPES, _error, _nonempty, _prepare, extract_json
from aligner_v2 import QUALIFIER_KINDS, _spans

HERE = Path(__file__).resolve().parent
PROMPT_FILE = HERE / 'prompts' / 'alignment_v3.txt'
PROMPT_VERSION = 'alignment_v3'


def build_messages(old_units, new_units, source_texts):
    _prepare(old_units, new_units, source_texts)
    payload = {'old_units': old_units, 'new_units': new_units, 'source_texts': source_texts}
    return [{'role': 'system', 'content': PROMPT_FILE.read_text(encoding='utf-8').rstrip('\n')},
            {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False, indent=2)}]


def _empty_result(old_units, new_units):
    return {'status': 'failed', 'parsed': None, 'parse_errors': [], 'structure_errors': [],
            'coverage': {'unhandled_old_unit_ids': [u.get('unit_id') for u in old_units if isinstance(u, dict)],
                         'unhandled_new_unit_ids': [u.get('unit_id') for u in new_units if isinstance(u, dict)],
                         'unmatched_old_unit_ids': [], 'mentioned_old_unit_ids': [], 'mentioned_new_unit_ids': []},
            'source_completions': [], 'quote_locations': [], 'ambiguities': [],
            'missing_evidence': [], 'scope_review': [],
            'semantic_review': {'status': 'not_reviewed', 'findings': []}}


def parse_and_validate(raw, old_units, new_units, source_texts):
    result = _empty_result(old_units, new_units)
    sources, maps = _prepare(old_units, new_units, source_texts)
    errors = result['structure_errors']

    def error(code, path, message):
        errors.append(_error(code, path, message))

    def missing(path, message, **extra):
        result['missing_evidence'].append({'path': path, 'message': message, **extra})

    try:
        data = extract_json(raw)
    except (ValueError, TypeError, AttributeError) as exc:
        result['status'] = 'parse_error'
        result['parse_errors'].append(_error('json_parse', '$', str(exc)))
        return result
    result['parsed'] = data
    if not isinstance(data, dict):
        error('schema', '$', 'top-level value must be an object')
        return result
    records = data.get('records')
    if not isinstance(records, list):
        error('schema', 'records', 'must be an array')
        records = []
    unmatched = data.get('unmatched_old_unit_ids')
    if not isinstance(unmatched, list) or any(not _nonempty(x) for x in unmatched):
        error('schema', 'unmatched_old_unit_ids', 'must be an array of nonempty strings')
        unmatched = []
    if len(set(unmatched)) != len(unmatched):
        error('duplicate_unit_id', 'unmatched_old_unit_ids', 'duplicate ID')
    valid_unmatched = []
    for uid in unmatched:
        if uid not in maps['old']:
            error('unknown_unit_id', 'unmatched_old_unit_ids', uid)
        elif uid not in valid_unmatched:
            valid_unmatched.append(uid)
    result['coverage']['unmatched_old_unit_ids'] = valid_unmatched
    covered = {'old': set(), 'new': set()}
    mentioned = {'old': set(), 'new': set()}

    def resolve(path, quote, candidates, *, kind):
        """Record only a unique source; ambiguity is a structural blocker, not a guess."""
        source_ids = sorted({maps[side][uid]['source_id'] for side, uid in candidates})
        if not source_ids:
            return None
        if len(source_ids) > 1:
            result['ambiguities'].append({'path': path, 'candidate_source_ids': source_ids,
                                          'candidate_unit_ids': sorted({uid for _, uid in candidates})})
            error('ambiguous_source', path, 'quote maps to multiple sources')
            return None
        sid = source_ids[0]
        item = {'path': path, 'source_id': sid, 'method': 'unique_linked_unit_source',
                'matched_unit_ids': sorted({uid for _, uid in candidates}), 'kind': kind}
        result['source_completions'].append(item)
        result['quote_locations'].append({'path': path, 'source_id': sid, 'quote': quote,
                                          'spans': _spans(sources[sid]['text'], quote)})
        return sid

    for i, record in enumerate(records):
        path = f'records[{i}]'
        if not isinstance(record, dict):
            error('schema', path, 'must be an object')
            continue
        linked = {}
        for side in ('old', 'new'):
            field = side + '_unit_ids'
            ids = record.get(field)
            if not isinstance(ids, list) or any(not _nonempty(x) for x in ids):
                error('schema', path + '.' + field, 'must be an array of nonempty strings')
                ids = []
            if side == 'new' and not ids:
                error('schema', path + '.' + field, 'new IDs must not be empty')
                missing(path + '.' + field, 'new unit required')
            if len(set(ids)) != len(ids):
                error('duplicate_unit_id', path + '.' + field, 'duplicate ID')
            linked[side] = []
            for uid in ids:
                if uid not in maps[side]:
                    error('unknown_unit_id', path + '.' + field, uid)
                elif uid not in linked[side]:
                    linked[side].append(uid)
                    mentioned[side].add(uid)
        relation = record.get('relation')
        if not isinstance(relation, str) or relation not in CHANGE_TYPES:
            error('schema', path + '.relation', 'invalid relation type')
        if not _nonempty(record.get('attribute')):
            error('schema', path + '.attribute', 'must be a nonempty string')
        if relation in ('state_change', 'historical_correction', 'support') and not linked['old']:
            error('missing_old_evidence', path + '.old_unit_ids', 'relation requires an old unit and quote')
            missing(path + '.old_unit_ids', 'old comparison evidence required')
        evidence = record.get('missing_evidence')
        if not isinstance(evidence, list) or any(not _nonempty(item) for item in evidence):
            error('schema', path + '.missing_evidence', 'must be an array of nonempty strings')
        else:
            for item in evidence:
                missing(path + '.missing_evidence', item, origin='model')

        quote_data = {'old': [], 'new': []}
        for side in ('old', 'new'):
            key = side + '_quotes'
            quotes = record.get(key)
            if not isinstance(quotes, list):
                error('schema', path + '.' + key, 'must be an array of quote strings')
                quotes = []
            if (side == 'new' or linked['old']) and not quotes:
                error('missing_quote', path + '.' + key, 'at least one quote required')
                missing(path + '.' + key, 'quote required')
            if side == 'old' and not linked['old'] and quotes:
                error('schema', path + '.' + key, 'old quotes require old units')
            cited = set()
            for j, quote in enumerate(quotes):
                qpath = f'{path}.{key}[{j}]'
                if not _nonempty(quote):
                    error('schema', qpath, 'must be a nonempty quote string')
                    continue
                candidates = [(side, uid) for uid in linked[side]
                              if any(quote in unit_quote for unit_quote in maps[side][uid]['quotes'])]
                quote_data[side].append((quote, candidates))
                if not candidates:
                    error('quote_provenance', qpath, 'quote must be within a linked unit quote')
                    missing(qpath, 'verbatim evidence for linked unit not found')
                    continue
                sid = resolve(qpath, quote, candidates, kind='quote')
                if sid is not None:
                    if side == 'new' and sources[sid].get('speaker') != 'user':
                        error('non_user_new_evidence', qpath, 'new claim evidence is not from a user')
                        missing(qpath, 'user evidence required')
                        continue
                    cited.update(uid for _, uid in candidates)
            for uid in linked[side]:
                if uid not in cited:
                    error('unit_without_quote', path + '.' + side + '_unit_ids', uid)
                    missing(path + '.' + side + '_unit_ids', 'no uniquely sourced quote for unit',
                            side=side, unit_id=uid)
            covered[side].update(cited)

        qualifiers = record.get('qualifiers')
        if not isinstance(qualifiers, list):
            error('schema', path + '.qualifiers', 'must be an array')
            qualifiers = []
        for j, qualifier in enumerate(qualifiers):
            qpath = f'{path}.qualifiers[{j}]'
            if not isinstance(qualifier, dict):
                error('schema', qpath, 'must be an object')
                continue
            side, kind = qualifier.get('side'), qualifier.get('kind')
            quote, anchor = qualifier.get('quote'), qualifier.get('claim_quote')
            if side not in ('old', 'new') or not isinstance(kind, str) or kind not in QUALIFIER_KINDS:
                error('schema', qpath, 'invalid side or qualifier kind')
                continue
            if not _nonempty(quote) or not _nonempty(anchor):
                error('schema', qpath, 'quote and claim_quote are required')
                continue
            if quote not in anchor:
                error('qualifier_not_in_claim', qpath, 'qualifier must appear in claim_quote')
            candidates = []
            for cited_quote, units in quote_data[side]:
                if not (cited_quote in anchor or anchor in cited_quote):
                    continue
                for pair in units:
                    sid = maps[side][pair[1]]['source_id']
                    if anchor in sources[sid]['text'] and pair not in candidates:
                        candidates.append(pair)
            if not candidates:
                error('qualifier_anchor_provenance', qpath, 'claim_quote must overlap a cited quote in its linked source')
                missing(qpath, 'qualifier and its assertion need linked same-source evidence')
                continue
            if quote not in anchor:
                continue
            if resolve(qpath, quote, candidates, kind='qualifier') is not None:
                result['scope_review'].append({'path': qpath, 'claim_quote': anchor,
                    'reason': 'qualifier attachment and semantic scope require human review'})

    for uid in set(valid_unmatched) & mentioned['old']:
        error('conflicting_coverage', 'unmatched_old_unit_ids', uid)
    for side in ('old', 'new'):
        result['coverage']['mentioned_' + side + '_unit_ids'] = [uid for uid in maps[side] if uid in mentioned[side]]
        handled = covered[side] | (set(valid_unmatched) if side == 'old' else set())
        unhandled = [uid for uid in maps[side] if uid not in handled]
        result['coverage']['unhandled_' + side + '_unit_ids'] = unhandled
        for uid in unhandled:
            error('unhandled_unit', side + '_units', uid)
            missing(side + '_units', 'unit has no valid cited evidence or explicit unmatched status',
                    side=side, unit_id=uid)
    result['status'] = 'failed' if errors else 'passed'
    return result


def align_evidence_v3(old_units, new_units, source_texts, *, backend=None):
    try:
        messages = build_messages(old_units, new_units, source_texts)
    except (ValueError, TypeError) as exc:
        return {'status': 'input_error', 'parsed': None, 'raw_response': None, 'request_attempts': 0,
                'parse_errors': [], 'structure_errors': [_error('input', '$', str(exc))]}
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
