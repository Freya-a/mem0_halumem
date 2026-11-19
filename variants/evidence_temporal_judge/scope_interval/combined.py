"""Read-only scope + existing v2 interval candidate flow; no model or storage client."""
from copy import deepcopy
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import judge_scope as scope
import judge_v2 as v2


def combine(request, split, new_evidence, scope_result, time_info=None, *, pair_assessments=None,
            time_verifier=None, nli_backend=None, backend_provenance=None):
    """Review one already-judged scope result, retaining it exactly.

    pair_assessments maps fact_index to independently sourced v1-shaped
    directional/temporal claims. Its provenance must be explicit; it is not
    inferred from scope actions. Verifier and NLI callables use v2's APIs.
    """
    request, split, new_evidence, scope_result, time_info = deepcopy(
        (request, split, new_evidence, scope_result, time_info))
    backend_provenance = deepcopy(backend_provenance or {})
    for name, backend in (('time_verifier', time_verifier), ('nli', nli_backend)):
        if backend is not None:
            info = backend_provenance.get(name)
            if (not isinstance(info, dict) or info.get('kind') not in ('simulation', 'human', 'model', 'replay')
                or not isinstance(info.get('source'), str) or not info['source'].strip()
                or (info['kind'] == 'model' and not info.get('model'))):
                raise ValueError('backend provenance required: ' + name)
    contexts = scope.base._splitter._validate_request(request)
    scope.base._splitter._validate_response(split, request, contexts)
    sources = scope.base._sources(new_evidence)
    for key in ('memory_id', 'memory_text', 'source_context'):
        if scope_result.get(key) != request[key]:
            raise ValueError('scope/request mismatch: ' + key)
    if scope_result.get('new_evidence') != new_evidence:
        raise ValueError('scope/evidence mismatch')
    items = scope_result['facts']
    if len(items) != len(split['facts']) or any(x.get('fact') != y for x, y in zip(items, split['facts'])):
        raise ValueError('scope/split facts mismatch')
    candidate = scope_result['new_candidates']
    if candidate['status'] == 'ok':
        scope.validate_candidates({'candidates': candidate['candidates']}, sources)
    elif candidate['status'] not in ('model_failed', 'parse_failed'):
        raise ValueError('invalid candidate status')
    out = {'request': request, 'split_result': split, 'new_evidence': new_evidence,
           'time_info': time_info, 'scope_result': scope_result, 'facts': [],
           'new_candidates': deepcopy(candidate), 'confirmed_valid': 0, 'evaluator_calls': []}
    for item in items:
        status, fact = item['status'], item['fact']
        result = {'fact': deepcopy(fact), 'scope': deepcopy(item), 'temporal': None,
                  'temporal_status': None, 'final': {'scope_components': deepcopy(item.get('components', [])),
                  'scope_status': status, 'temporal_candidates': [], 'semantic_support': 'not_verified'}}
        out['facts'].append(result)
        if status in ('model_failed', 'parse_failed'):
            result['temporal_status'] = 'deferred_scope_failure'
            continue
        scope.validate_fact({'applicability': item['applicability'], 'components': item['components']}, fact, sources)
        if status != item['applicability']:
            raise ValueError('scope status mismatch')
        if status == 'uninvolved':
            result['temporal_status'] = 'uninvolved'
            continue
        if status == 'insufficient':
            result['temporal_status'] = 'evidence_insufficient'
            continue
        ids = {q['source_id'] for part in item['components'] for q in part['new_evidence']}
        if len(ids) != 1:
            result['temporal_status'] = 'multiple_sources' if len(ids) > 1 else 'evidence_insufficient'
            continue
        assessment = (pair_assessments or {}).get(fact['fact_index'])
        if assessment is None:
            assessment = {'erase_label': 'No Change', 'temporal_relation': 'unclear',
                          'reason': '未提供独立事实对方向判断', 'provenance': 'not_provided'}
        if (not isinstance(assessment, dict) or set(assessment) != {'erase_label', 'temporal_relation', 'reason', 'provenance'}
                or assessment['erase_label'] not in ('Make False', 'No Change', 'Reinforce')
                or assessment['temporal_relation'] not in ('unclear', 'before_after', 'historical_compatible', 'simultaneous_conflict')
                or not isinstance(assessment['reason'], str) or not assessment['reason'].strip()
                or not isinstance(assessment['provenance'], str) or not assessment['provenance'].strip()):
            raise ValueError('invalid pair assessment')
        projected = {'fact': fact, 'status': status, 'applicability': status,
                     'erase_label': assessment['erase_label'], 'temporal_relation': assessment['temporal_relation'],
                     'temporal_reason': assessment['reason'], 'components': [
                         {k: deepcopy(p[k]) for k in ('fragment', 'action', 'reason', 'new_evidence')}
                         for p in item['components']]}
        failures = []
        def call_backend(name, backend, payload):
            entry = {'backend': name, 'provenance': deepcopy(backend_provenance[name]), 'input': deepcopy(payload)}
            out['evaluator_calls'].append(entry)
            try:
                value = backend(payload)
            except Exception as exc:
                entry['error_type'] = type(exc).__name__
                raise
            entry['output'] = deepcopy(value)
            return value
        def nli(payload):
            if nli_backend is None:
                return {'relation': 'uncertain'}
            try:
                value = call_backend('nli', nli_backend, payload)
            except Exception:
                failures.append('model_failed')
                raise
            try:
                v2._nli(lambda _: value, payload['old_fact'], payload['new_evidence'], payload['impact'])
            except Exception:
                failures.append('parse_failed')
                raise
            return value
        def verify(payload):
            try:
                value = call_backend('time_verifier', time_verifier, payload)
            except Exception:
                failures.append('model_failed')
                raise
            if (not isinstance(value, dict) or set(value) != {'status', 'reason'}
                or value['status'] not in ('supported', 'not_supported', 'uncertain')
                or not isinstance(value['reason'], str) or not value['reason'].strip()):
                failures.append('parse_failed')
            return value
        temporal = v2._review_fact(projected, time_info, sources,
                                    {e['source_id']: e for e in new_evidence}, nli,
                                    request, contexts, verify if time_verifier else None)
        result['temporal'] = temporal
        result['pair_assessment'] = assessment
        checks = temporal['time_checks']
        claims = temporal.get('intervals') or {}
        has_boundary = any(claims.get(side, {}).get(field) is not None for side in ('old', 'new') for field in ('start', 'end'))
        if failures:
            reason = failures[0]
        elif temporal['status'] == 'failed':
            reason = 'parse_failed'
        elif not has_boundary:
            reason = 'time_missing'
        elif any(c['precision_status'] == 'insufficient' for c in checks):
            reason = 'time_precision_insufficient'
        elif any(c['semantic_status'] != 'supported' for c in checks):
            reason = 'time_unverified'
        elif temporal['temporal_relation'] != 'unclear':
            reason = 'temporal_candidate'
        elif nli_backend is None or assessment['provenance'] == 'not_provided':
            reason = 'deferred_pair_assessment'
        else:
            reason = 'interval_uncertain'
        result['temporal_status'] = reason
        result['final']['temporal_candidates'] = deepcopy(temporal['interval_adjustments'])
        result['final']['temporal_relation_candidate'] = temporal['temporal_relation']
        result['final']['temporal_dependent_conclusions'] = 'candidate_unverified' if reason == 'temporal_candidate' else 'needs_confirmation'
    return out


def split_and_scope(request, new_evidence, time_info, splitter_backend_factory, fact_backend, candidate_backend,
                    **kwargs):
    """Fresh run with explicit v4 prompt; caller supplies all backends and provenance."""
    split = v2.v1.split_with_v4(request, splitter_backend_factory)
    judged = scope.judge(split['result'], request['source_context'], new_evidence, time_info, fact_backend, candidate_backend)
    result = combine(request, split['result'], new_evidence, judged, time_info, **kwargs)
    result['splitter_prompt'] = split['prompt']
    return result
