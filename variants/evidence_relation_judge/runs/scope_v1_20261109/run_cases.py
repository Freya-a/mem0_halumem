"""Offline replay, no Qwen calls and no Mem0 writes."""
import json, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent
sys.path.insert(0,str(COMP/'part2_scope_judge'))
from scope_nli import LocalNLI
from scope_planner import plan_scope

model=LocalNLI()
for name in ('promotion','skydiving','career_history'):
    request=json.loads((COMP/'runs/real_cases_20261106'/f'{name}_input.json').read_text())
    saved=json.loads((COMP/'runs/controlled_v2_20261106'/f'{name}_run.json').read_text())
    assert request == saved['input']
    result=plan_scope(request,saved['result'],nli=model)
    path=HERE/f'{name}_scope.json'
    with path.open('x',encoding='utf8') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
    row=result['results'][0]
    print(name, row['status'],row['nli'].get('status'), row['nli'].get('predicted_label'),row['nli'].get('softmax_scores'),flush=True)
