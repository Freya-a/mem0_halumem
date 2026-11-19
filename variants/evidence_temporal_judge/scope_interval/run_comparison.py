"""Reproduce the three fixed-input comparisons, offline and without overwriting."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
PROJECT = BASE.parents[1]
sys.path.insert(0, str(HERE))
import combined

SOURCE = BASE / 'runs/scope_check_20261105_v2_run'
V1 = BASE / 'runs/scope_check_20261105_v1'
V4 = combined.scope.base.V4_PROMPT
EXPECTED_V4 = 'd9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3'
CASES = ('promotion', 'skydiving', 'career_history')


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def main(target):
    target = Path(target).resolve()
    if target.exists(): raise FileExistsError(target)
    for directory in (V1, SOURCE):
        subprocess.run([sys.executable, str(directory / 'verify_run.py')], cwd=directory, check=True)
    if sha(V4) != EXPECTED_V4: raise ValueError('v4 prompt changed')
    preflight = read(SOURCE / 'preflight.json')
    originals = {}
    outputs = {}
    for name in CASES:
        folder = SOURCE / name
        paths = [folder / f for f in ('model_input.json', 'split_result.json', 'scope_result.json', 'source_provenance.json')]
        inputs, split, prior, provenance = (read(p) for p in paths)
        if split['prompt'] != {'path': str(V4), 'sha256': sha(V4)}: raise ValueError('split prompt mismatch')
        if sha(paths[0]) != preflight['cases'][name]['input_sha256'] or sha(paths[1]) != preflight['cases'][name]['split_sha256']:
            raise ValueError('source input/split checksum mismatch')
        result = combined.combine(inputs['split_request'], split['result'], inputs['new_evidence'], prior, inputs['time_info'])
        result['splitter_prompt'] = split['prompt']
        result['provenance'] = {'scope_result': str(paths[2]), 'scope_result_sha256': sha(paths[2]),
          'split_result': str(paths[1]), 'split_result_sha256': sha(paths[1]), 'model_input': str(paths[0]),
          'model_input_sha256': sha(paths[0]), 'source_provenance': str(paths[3]), 'source_provenance_sha256': sha(paths[3]),
          'scope_model_and_calls': str(SOURCE / 'run_config.json'), 'new_model_calls': 0,
          'time_verifier': 'not provided', 'pair_assessment': 'not provided',
          'nli': 'no model; v2 receives a deterministic uncertain placeholder only if reached'}
        originals[name] = {str(p): sha(p) for p in paths}
        outputs[name] = result
    target.mkdir(parents=True)
    for name, result in outputs.items():
        (target / name).mkdir()
        save(target / name / 'comparison.json', {'A_scope_only': result['scope_result'], 'B_combined': result})
    config = {'created_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
       'scope_source': str(SOURCE), 'scope_source_config': str(SOURCE / 'run_config.json'),
       'scope_source_config_sha256': sha(SOURCE / 'run_config.json'), 'prior_scope_calls': 6,
       'new_sdk_attempts': 0, 'new_retries': 0, 'splitter_prompt': {'path': str(V4), 'sha256': sha(V4)},
       'combined_code_sha256': sha(HERE / 'combined.py'), 'v2_code_sha256': sha(BASE / 'judge_v2.py'),
       'scope_code_sha256': sha(BASE / 'judge_scope.py'), 'originals': originals,
       'case_temporal_status': {k: [f['temporal_status'] for f in v['facts']] for k,v in outputs.items()},
       'time_accounting': {'cases_with_usable_event_time': 0, 'cases_without_usable_event_time': 3,
                           'cases_with_judgment_failure': 0},
       'note': 'All three inputs have time_info null. Counts overlap in general; this run has no failures.'}
    save(target / 'manifest.json', config)
    print(json.dumps(config['case_temporal_status'], ensure_ascii=False))


if __name__ == '__main__':
    if len(sys.argv) != 2: raise SystemExit('Usage: python run_comparison.py NEW_RUN_DIR')
    main(sys.argv[1])
