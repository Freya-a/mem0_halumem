"""Replay saved cases without network or model calls; expected data is report-only."""
import json
from pathlib import Path

from adapter import load_aligner_case
from scope_planner import build_scope_plan

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
CASES = ('promotion', 'susan', 'transition', 'career_history', 'skydiving')
MODEL_RUN = PROJECT / 'variants/evidence_aligner/runs/v3_paired_20261120'


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2)


def main():
    results_dir = HERE / 'results'
    results_dir.mkdir(exist_ok=True)
    for case in CASES:
        data = json.loads((HERE / 'fixtures' / f'{case}.json').read_text(encoding='utf-8'))
        for unit in data['units']:
            unit['memory_id'] = data['memory_id']
            unit['source_ref'] = data['old_memory_source_ref']
        human = build_scope_plan(data['old_memory'], data['units'], data['sources'], data['alignments'])
        model = build_scope_plan(*load_aligner_case(MODEL_RUN / f'{case}.json'))
        result = {'case_id': case, 'human_alignment': human, 'saved_v3_alignment': model}
        (results_dir / f'{case}.json').write_text(dump(result) + '\n', encoding='utf-8')
        counts = lambda p: ', '.join(f'{k}={len(p[k])}' for k in ('modify', 'preserve', 'uncertain', 'add'))
        print(f'{case}: human {counts(human)}; v3 {counts(model)}')

    old = '上海、南京两家门店的堂食、外带均实行旧政策。'
    new = '上海门店的外带改用新政策。'
    units = [{'id': 'policy', 'quote': old, 'fact': '两家门店两种服务的旧政策',
              'memory_id': 'demo-memory', 'source_ref': 'synthetic:old'}]
    sources = [{'source_id': 'demo-evidence', 'text': new, 'source_ref': 'synthetic:new'}]
    alignment = [{'unit_id': 'policy', 'relation': 'change', 'old_subject': '门店',
                  'new_subject': '门店', 'old_attribute': '政策', 'new_attribute': '政策',
                  'old_value': '旧政策', 'new_value': '新政策', 'old_quote': old,
                  'new_quote': new, 'source_id': 'demo-evidence',
                  'old_conditions': {'kind': 'finite', 'dimensions': {'门店': ['上海', '南京'], '服务': ['堂食', '外带']}},
                  'new_conditions': {'kind': 'finite', 'dimensions': {'门店': ['上海'], '服务': ['外带']}}}]
    demo = build_scope_plan(old, units, sources, alignment)
    assert len(demo['modify']) == 1 and len(demo['preserve']) == 3
    (results_dir / 'multidimensional.json').write_text(dump(demo) + '\n', encoding='utf-8')
    print('multidimensional: modify=1, preserve=3 (asserted)')


if __name__ == '__main__':
    main()
