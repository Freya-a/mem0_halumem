"""Run three frozen one-fact inputs through the unmodified component, once each."""
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMP = HERE.parent.parent
sys.path.insert(0, str(COMP/'part1_relation_judge'))
import relation_judge
from run_local import LocalQwen


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


manifest = json.loads((HERE/'manifest_before.json').read_text())
assert sha(HERE/'final_system_prompt.txt') == manifest['system_prompt_utf8_sha256']
assert hashlib.sha256(relation_judge.SYSTEM.encode()).hexdigest() == manifest['system_prompt_utf8_sha256']
for path, digest in manifest['code_sha256'].items():
    assert sha(path) == digest
for case in manifest['cases'].values():
    assert sha(case['prepared_input_path']) == case['prepared_input_sha256']
for name in manifest['cases']:
    assert not (HERE/(name+'_run.json')).exists()
save(HERE/'launch.json', {'driver_sha256':sha(__file__),'manifest_sha256':sha(HERE/'manifest_before.json'),'offline_env':'HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1', 'cases':list(manifest['cases']), 'prompt_matches_current':True})
backend = LocalQwen()
for name, info in manifest['cases'].items():
    assert sha(info['prepared_input_path']) == info['prepared_input_sha256']
    data = json.loads(Path(info['prepared_input_path']).read_text())
    calls_before = backend.metrics['model_calls']
    messages_before = len(backend.messages)
    result = relation_judge.judge(data, backend)
    messages = copy.deepcopy(backend.messages[messages_before:])
    assert all(m[0]['content'] == relation_judge.SYSTEM for m in messages)
    artifact = {'case':name,'input':data,'model_messages':messages,'result':result,
                'case_model_calls':backend.metrics['model_calls']-calls_before,
                'runtime_cumulative':copy.deepcopy(backend.metrics),
                'provenance_manifest_sha256':sha(HERE/'manifest_before.json')}
    save(HERE/(name+'_run.json'), artifact)
    print(json.dumps({'case':name, 'status':result['status'], 'model_calls':artifact['case_model_calls'], 'errors': [r['errors'] for r in result['results']]},ensure_ascii=False),flush=True)
save(HERE/'completion.json', {'total_model_calls':backend.metrics['model_calls'], 'prompt_unchanged':sha(HERE/'final_system_prompt.txt')==hashlib.sha256(relation_judge.SYSTEM.encode()).hexdigest(), 'code_sha256_after':{p:sha(p) for p in manifest['code_sha256']}, 'case_input_sha256_after':{name:sha(info['prepared_input_path']) for name,info in manifest['cases'].items()}})
