"""Run strict v5 once per frozen input after discovering v4 label expansion."""
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
PART1 = HERE.parent.parent / 'part1_relation_judge'
sys.path.insert(0, str(PART1))
import relation_judge_v5 as v5
from run_local_v5 import LocalQwenV5

NAMES = ('job_transition', 'persian_cats', 'skydiving', 'career_history', 'promotion')
def save(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()
def main():
    inputs = json.loads((HERE / 'inputs.json').read_text(encoding='utf-8'))
    directory = HERE / 'v5'
    directory.mkdir(exist_ok=False)
    (directory / 'system_prompt.txt').write_text(v5.SYSTEM, encoding='utf-8')
    save(directory / 'manifest.json', {'started_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'python':sys.executable,'python_version':platform.python_version(), 'max_new_tokens':768,
        'generation':{'do_sample':False,'pad_token_id':'tokenizer.eos_token_id','enable_thinking':False,
                      'other_generate_options':'model generation_config and transformers defaults'},
        'v5_code_sha256':{str(p):sha(p) for p in (PART1/'relation_judge_v5.py',PART1/'run_local_v5.py')},
        'prior_manifest': '../manifest.json', 'input_sha256':sha(HERE/'inputs.json'),
        'no_retry':True,'no_mem0_write':True,'design_after_v4_results':True,
        'model_load_note':'same path and loading method; second process and separate model load'})
    backend = LocalQwenV5(max_new_tokens=768)
    start = time.perf_counter()
    records = []
    for name in NAMES:
        begin = time.perf_counter()
        m = len(backend.messages); g = len(backend.metrics['generations']); c = backend.metrics['model_calls']
        print(name, 'v5 start', flush=True)
        result = v5.judge(deepcopy(inputs[name]), backend)
        gens = deepcopy(backend.metrics['generations'][g:])
        for item in gens:
            item['length_limit_reached_without_eos'] = (item.get('output_tokens') == 768 and not item.get('terminated_at_eos',False)) if item.get('output_tokens') is not None else None
        artifact = {'case':name,'version':'v5','input':inputs[name],'model_messages':deepcopy(backend.messages[m:]),
                    'result':result,'model_calls':backend.metrics['model_calls']-c,'generations':gens,
                    'case_wall_seconds':round(time.perf_counter()-begin,3),'max_new_tokens':768,'no_retry':True}
        save(directory / f'{name}.json', artifact)
        record = {k:artifact[k] for k in ('case','version','model_calls','generations','case_wall_seconds')}
        record['status'] = result['status']
        records.append(record)
        print(json.dumps(record,ensure_ascii=False),flush=True)
    save(directory/'completion.json', {'finished_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
          'elapsed_seconds':round(time.perf_counter()-start,3),'runtime':backend.metrics,'cases':records,
          'no_retry':True,'no_mem0_write':True})
if __name__ == '__main__':main()
