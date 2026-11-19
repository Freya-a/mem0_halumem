"""Handwritten synthetic A/B integration example; zero external calls."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_combined import fixture
import combined

request, split, evidence, scope, times, pair = fixture()
provenance = {'time_verifier': {'kind': 'simulation', 'source': str(HERE / 'controlled_replay.py')},
              'nli': {'kind': 'simulation', 'source': str(HERE / 'controlled_replay.py')}}
result = combined.combine(request, split, evidence, scope, times, pair_assessments=pair,
    time_verifier=lambda _: {'status': 'supported', 'reason': '手写合成案例假设事件和日期一致'},
    nli_backend=lambda _: {'relation': 'contradiction', 'score': 0.99}, backend_provenance=provenance)
output = {'origin': '全部输入、拆分、scope、方向判断、时间语义和NLI均为手写模拟，不是v4或任何模型运行结果',
          'A_simulated_scope': scope, 'B_combined': result}
with Path(sys.argv[1]).open('x', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2); f.write('\n')
