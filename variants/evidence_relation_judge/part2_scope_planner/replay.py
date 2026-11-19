"""Replay preserved v2 outputs, with explicit, separately supplied scope annotations."""
import json
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path

from scope import Bound, Evidence, Field, Interval, Scope, Weekdays, compare

HERE = Path(__file__).resolve().parent
PART1 = HERE.parent / 'part1_relation_judge'
sys.path.insert(0, str(PART1))
import relation_judge_v2  # Existing validator and injected backend; no model.


def load_case(name):
    if name not in ('promotion', 'job_transition', 'synthetic_wednesday_01'):
        raise ValueError('unknown case')
    return json.loads((HERE / 'cases' / (name + '.json')).read_text())


def _sources(request):
    split = request['split_result']
    sources = {split['memory_id']: split['memory_text']}
    for item in request.get('source_context', []) + request['new_evidence']:
        if item['source_id'] in sources:
            raise ValueError('duplicate evidence source')
        sources[item['source_id']] = item['text']
    return sources


def _refs(items, sources, allowed, *, required=False):
    if required and not items:
        raise ValueError('known scope field requires evidence')
    refs = []
    for item in items:
        sid, quote = item['source_id'], item['quote']
        if not quote or sid not in allowed or sid not in sources or quote not in sources[sid]:
            raise ValueError('evidence quote/source mismatch')
        refs.append(Evidence(sid, quote))
    return tuple(refs)


def _field(data, sources, allowed):
    return Field.unknown() if data.get('value') is None else Field.known(data['value'], _refs(data.get('evidence', []), sources, allowed, required=True))


def _bound(data, sources, allowed):
    refs = _refs(data.get('evidence', []), sources, allowed, required=data['kind'] != 'unknown')
    if data['kind'] == 'known': return Bound.known(data['value'], refs)
    if data['kind'] == 'unbounded': return Bound.unbounded(refs)
    if data['kind'] == 'unknown': return Bound.unknown()
    raise ValueError('invalid boundary')


def _weekdays(data, sources, allowed):
    refs = _refs(data.get('evidence', []), sources, allowed, required=data['kind'] != 'unknown')
    if data['kind'] == 'known': return Weekdays.known(data['days'], refs)
    if data['kind'] == 'all': return Weekdays.all(refs)
    if data['kind'] == 'unknown': return Weekdays.unknown()
    raise ValueError('invalid weekdays')


def _scope(data, request, sources, side):
    allowed = ({request['split_result']['memory_id']} | {x['source_id'] for x in request.get('source_context', [])}
               if side == 'old' else {x['source_id'] for x in request['new_evidence']})
    observation = data.get('observation')
    obs_value, obs_refs = None, ()
    if observation is not None:
        items = request.get('source_context', []) + request['new_evidence']
        matches = [x for x in items if x['source_id'] == observation['source_id']]
        if len(matches) != 1 or observation['source_id'] not in allowed or matches[0].get('recorded_at') != observation['value']:
            raise ValueError('observation source/time mismatch')
        obs_value = observation['value']
        obs_refs = (Evidence(observation['source_id'], matches[0]['text']),)
    return Scope(_field(data['subject'], sources, allowed), _field(data['attribute'], sources, allowed),
                 _weekdays(data['weekdays'], sources, allowed),
                 Interval(_bound(data['valid']['start'], sources, allowed), _bound(data['valid']['end'], sources, allowed)),
                 obs_value, obs_refs)


def _jsonable(value):
    if isinstance(value, date): return value.isoformat()
    if isinstance(value, (set, frozenset)): return sorted(value)
    raise TypeError(type(value).__name__)


def replay_case(case):
    if case['case_id'] == 'synthetic_wednesday_01':
        request = case['request']
        result = relation_judge_v2.judge(request, lambda _: json.dumps(case['mock_candidate'], ensure_ascii=False))
        origin, baseline_source = 'synthetic_mock_backend', None
        experiment = None
    else:
        original = json.loads((HERE / case['baseline_path']).resolve().read_text())
        request, result = original['input'], original['result']
        origin, baseline_source = 'saved_baseline_v2', case['baseline_path']
        experimental = json.loads((HERE / case['experiment_path']).resolve().read_text())
        experiment = {'source': case['experiment_path'], 'candidate': experimental['result']['results'][0]['candidate'],
                      'status': experimental['result']['results'][0]['status']}
    sources = _sources(request)
    if len(result['results']) != 1:
        raise ValueError('replay expects one original fact')
    row = result['results'][0]
    if row['status'] != 'ok' or not row['validation']['passed']:
        raise ValueError('upstream result is not validated')
    split = request['split_result']; fact = split['facts'][0]
    relation_judge_v2.v1.validate_candidate(row['candidate'], split, fact, {x['source_id']: x['text'] for x in request['new_evidence']})
    fragment = row['candidate']['candidate_impact_fragment']
    old_scopes = [(unit, _scope(unit, request, sources, 'old')) for unit in case['old_units']]
    new_scope = _scope(case['new_unit'], request, sources, 'new')
    attributes = []
    for unit, _ in old_scopes:
        # This reports annotated attribute quotes literally covered by a candidate;
        # it is not a semantic extractor and never upgrades the upstream label.
        if any(ref['source_id'] == split['memory_id'] and ref['quote'] in fragment
               for ref in unit['attribute'].get('evidence', [])):
            attributes.append(unit['name'])
    comparisons = {unit['name']: asdict(compare(scope, new_scope)) for unit, scope in old_scopes}
    output = {'case_id':case['case_id'], 'origin':case['origin'], 'baseline_source':baseline_source,
              'upstream_origin':origin, 'upstream':result, 'experiment':experiment,
              'baseline_relation':row['candidate']['relation'], 'candidate_fragment':fragment,
              'candidate_attributes':attributes, 'comparisons':comparisons,
              'annotated_old_scopes':{unit['name']:asdict(scope) for unit, scope in old_scopes},
              'annotated_new_scope':asdict(new_scope), 'limits':case['limits'],
              'interpretation':'Literal and structured candidate comparison only; no semantic verification, validity inference or write.'}
    return json.loads(json.dumps(output, ensure_ascii=False, default=_jsonable))


def main():
    names = sys.argv[1:] or ['promotion', 'synthetic_wednesday_01', 'job_transition']
    print(json.dumps([replay_case(load_case(name)) for name in names], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
