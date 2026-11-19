"""One invocation per old fact/version, one shared Qwen instance; no Mem0."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
COMP = HERE.parent.parent
PART1 = COMP / 'part1_relation_judge'
SOURCE = COMP / 'runs' / 'dev_scope_review_20261109_v1'
sys.path.insert(0, str(PART1))
import relation_judge_v2 as v2
import relation_judge_v4 as v4
from run_local_v2 import LocalQwenV2

NAMES = ('job_transition', 'persian_cats', 'skydiving', 'career_history', 'promotion')

def save(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    requests = {n: json.loads((SOURCE / f'{n}_result.json').read_text(encoding='utf-8'))['request'] for n in NAMES}
    for name, request in requests.items():
        assert len(request['split_result']['facts']) == 1, name
    for version in ('v2', 'v4'):
        (HERE / version).mkdir(exist_ok=False)
        (HERE / version / 'system_prompt.txt').write_text((v2.SYSTEM if version == 'v2' else v4.SYSTEM), encoding='utf-8')
    save(HERE / 'inputs.json', requests)
    paths = [PART1 / n for n in ('relation_judge.py', 'relation_judge_v2.py', 'relation_judge_v4.py', 'run_local.py', 'run_local_v2.py', 'run_local_v4.py')]
    model_dir = COMP / 'model' / 'Qwen3-8B'
    paths += sorted(p for p in model_dir.iterdir() if p.is_file())
    manifest = {'started_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                'python': sys.executable, 'python_version': platform.python_version(),
                'no_retry': True, 'no_mem0_write': True, 'max_new_tokens': 768,
                'generation': {'do_sample': False, 'pad_token_id': 'tokenizer.eos_token_id', 'enable_thinking': False,
                               'other_generate_options': 'model generation_config and transformers defaults'},
                'order': ['v2 then v4 for each case, sequentially'], 'sha256': {str(p): sha(p) for p in paths},
                'source_files_sha256': {n: sha(SOURCE / f'{n}_result.json') for n in NAMES}}
    save(HERE / 'manifest.json', manifest)
    backend = LocalQwenV2(max_new_tokens=768)
    totals = []
    overall_start = time.perf_counter()
    for name in NAMES:
        for version, judge in (('v2', v2), ('v4', v4)):
            t = time.perf_counter()
            before_calls = backend.metrics['model_calls']
            before_gen = len(backend.metrics['generations'])
            before_messages = len(backend.messages)
            original_system = v2.SYSTEM
            print(f'{name} {version} start', flush=True)
            try:
                # The unmodified v2 runner reads v2.SYSTEM at call time; restore
                # it after each sequential call. Everything else is identical.
                if version == 'v4':
                    v2.SYSTEM = v4.SYSTEM
                result = judge.judge(deepcopy(requests[name]), backend)
            finally:
                v2.SYSTEM = original_system
            gens = deepcopy(backend.metrics['generations'][before_gen:])
            for g in gens:
                g['length_limit_reached_without_eos'] = (g.get('output_tokens') == 768 and not g.get('terminated_at_eos', False)) if g.get('output_tokens') is not None else None
            artifact = {'case': name, 'version': version, 'input': requests[name],
                        'model_messages': deepcopy(backend.messages[before_messages:]), 'result': result,
                        'model_calls': backend.metrics['model_calls'] - before_calls,
                        'generations': gens, 'case_wall_seconds': round(time.perf_counter()-t, 3),
                        'no_retry': True, 'max_new_tokens': 768}
            save(HERE / version / f'{name}.json', artifact)
            totals.append({'case': name, 'version': version, 'status': result['status'],
                           'calls': artifact['model_calls'], 'generations': gens, 'case_wall_seconds': artifact['case_wall_seconds']})
            print(json.dumps(totals[-1], ensure_ascii=False), flush=True)
    save(HERE / 'completion.json', {'finished_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
         'elapsed_seconds': round(time.perf_counter()-overall_start, 3), 'runtime': backend.metrics, 'cases': totals,
         'no_retry': True, 'no_mem0_write': True})

if __name__ == '__main__':
    main()
