"""Offline replay of the same planner on structured and baseline-only inputs."""
import json
import sys
from collections import Counter
from pathlib import Path

from plan import build_plan
from replay import load_case
import relation_judge_v2

HERE = Path(__file__).resolve().parent
RUNS = HERE.parent / 'runs'
THREE = ('promotion', 'synthetic_wednesday_01', 'job_transition')
DEV_TARGETS = {
    'promotion':'1b846c59-456e-9550-dffd-4d23f1eca81f:s004:m000',
    'job_transition':'2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s007:m000',
    'skydiving':'2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008:m000',
    'persian_cats':'1b846c59-456e-9550-dffd-4d23f1eca81f:s006:m000',
    'career_history':'348492a7-cfe4-ee1d-73c3-c276d6ba8277:s007:m006',
}


def _read(path):
    return json.loads(path.read_text())


def _base(case):
    if case['case_id'] == 'synthetic_wednesday_01':
        req = case['request']
        rel = relation_judge_v2.judge(req, lambda _: json.dumps(case['mock_candidate'], ensure_ascii=False))
        return req, rel
    data = _read((HERE / case['baseline_path']).resolve())
    return data['input'], data['result']


def replay_one(case):
    request, relation = _base(case)
    structured = build_plan(request, relation, case)
    baseline = build_plan(request, relation)
    source = case.get('baseline_path', 'cases/synthetic_wednesday_01.json:mock_backend')
    structured['upstream_source'] = source
    baseline['upstream_source'] = source
    return {'structured':structured, 'baseline_only':baseline}


def replay_three():
    return {name:replay_one(load_case(name)) for name in THREE}


def replay_development():
    rows = []
    review_dir = RUNS / 'dev_scope_review_20261109_v1'
    for name, target_id in DEV_TARGETS.items():
        path = review_dir / (name + '_result.json')
        data = _read(path)
        plan = build_plan(data['request'], data['relation_result'])
        rows.append({'target_id':target_id, 'input_path':str(path.relative_to(HERE.parent)),
                     'coverage':'partial_reviewed_target' if name == 'career_history' else 'reviewed_target_input',
                     'upstream_status':'error' if plan['errors'] else 'ok', 'plan':plan})
    paired = RUNS / 'quote_holdout_paired_20261110_v1'
    partial_records = {x['record'] for x in _read(paired / 'coverage_audit.json')}
    for path in sorted((paired / 'pairs').glob('*_v2.json')):
        data = _read(path)
        plan = build_plan(data['input'], data['result'])
        rows.append({'target_id':data['target_id'], 'record':data['record'], 'input_path':str(path.relative_to(HERE.parent)),
                     'coverage':'partial_reviewed_target' if data['record'] in partial_records else 'reviewed_target_input',
                     'upstream_status':'error' if plan['errors'] else 'ok', 'plan':plan})
    errors = Counter(x['code'] for row in rows for x in row['plan']['uncertain'])
    return {'scope':'five documented original cases plus all 18 saved paired v2 fact units; no inferred inputs',
            'target_count':len({r['target_id'] for r in rows}), 'fact_rows':len(rows),
            'upstream_ok':sum(r['upstream_status']=='ok' for r in rows),
            'upstream_error':sum(r['upstream_status']=='error' for r in rows),
            'partial_input_rows':sum(r['coverage']=='partial_reviewed_target' for r in rows),
            'issue_counts':dict(sorted(errors.items())), 'rows':rows}


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else 'three'
    if kind == 'three': data = replay_three()
    elif kind == 'development': data = replay_development()
    else: raise SystemExit('usage: python plan_replay.py [three|development]')
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == '__main__': main()
