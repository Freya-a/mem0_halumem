"""Post-hoc comparison only; expectations never enter ScopePlan generation."""
import json
from pathlib import Path
from plan_replay import replay_three

HERE = Path(__file__).resolve().parent


def score():
    actual = replay_three()
    expected = json.loads((HERE / 'cases' / 'scope_plan_expectations.json').read_text())
    rows = []
    for name, groups in actual.items():
        for mode, plan in groups.items():
            spec = expected[name][mode]
            codes = {x['code'] for category in ('modify','preserve','uncertain','add') for x in plan[category]}
            checks = {f'code:{x}':x in codes for x in spec['required_codes']}
            checks['no_unapproved_modify'] = len(plan['modify']) <= spec['max_modify']
            if 'residual_weekdays' in spec:
                weekdays = {d for x in plan['preserve'] if x['code'] == 'residual_preserve'
                            for d in x['conditions']['weekdays'].get('days', [])}
                checks['residual_weekdays'] = weekdays == set(spec['residual_weekdays'])
            rows.append({'case_id':name, 'mode':mode, 'target_change':expected[name]['target_change'],
                         'checks':checks, 'checks_passed':sum(checks.values()), 'check_count':len(checks),
                         'target_change_not_emitted':not bool(plan['modify']),
                         'limitation':'Guard checks are not semantic accuracy; raw add is not an extracted or written fact.'})
    return {'rows':rows,'checks_passed':sum(x['checks_passed'] for x in rows),
            'check_count':sum(x['check_count'] for x in rows),
            'note':'Expected safety checks are post-hoc; human target history/change may be withheld by evidence gates.'}


if __name__ == '__main__': print(json.dumps(score(), ensure_ascii=False, indent=2))
