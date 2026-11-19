"""Freeze inputs/provenance before inference. Does not run any model."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMP = HERE.parent.parent
ROOT = COMP.parents[3]
PREV = COMP.parent / 'evidence_temporal_judge/runs/scope_check_20261105_v1'
SPLITTER = COMP.parent / 'dnd_mem0_splitter'
sys.path.insert(0, str(COMP/'part1_relation_judge'))
import relation_judge as judge

spec = importlib.util.spec_from_file_location('v4_validator', SPLITTER / 'splitter.py')
v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v4)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def save(path, obj):
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def pointer(value, path):
    for key in path.strip('/').split('/'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


v4_prompt = SPLITTER / 'prompt_versions/v4_boundaries_20261104/prompt.txt'
prompt_sha = hashlib.sha256(judge.SYSTEM.encode('utf-8')).hexdigest()
with (HERE / 'final_system_prompt.txt').open('x', encoding='utf-8') as f:
    f.write(judge.SYSTEM)
model = COMP / 'model/Qwen3-8B'
manifest = {'code_sha256': {str(p): sha(p) for p in [COMP/'part1_relation_judge'/'relation_judge.py', COMP/'part1_relation_judge'/'run_local.py']}, 'system_prompt_utf8_sha256':prompt_sha,
            'v4_prompt_path':str(v4_prompt), 'v4_prompt_sha256':sha(v4_prompt), 'model_dir':str(model),
            'model_files':{p.name:{'bytes':p.stat().st_size, **({'sha256':sha(p)} if p.suffix != '.safetensors' else {})} for p in sorted(model.iterdir()) if p.is_file()}, 'cases':{}}
for name in ('skydiving','promotion','career_history'):
    d = PREV/name
    prov = json.loads((d/'source_provenance.json').read_text())
    original = json.loads((d/'model_input.json').read_text())
    split_wrapper = json.loads((d/'split_result.json').read_text())
    split = split_wrapper['result']
    assert split_wrapper['prompt']['sha256'] == manifest['v4_prompt_sha256']
    for field in ('before', 'input', 'dataset', 'human_review'):
        assert sha(prov[field+'_file']) == prov[field+'_sha256'], (name,field,'hash')
    before = json.loads(Path(prov['before_file']).read_text())
    snapshot = pointer(before, prov['snapshot_pointer'])
    req = original['split_request']
    assert (snapshot['id'], snapshot['memory'], snapshot['user_id']) == (req['memory_id'], req['memory_text'], prov['user_uuid'])
    assert split['memory_id'] == req['memory_id'] and split['memory_text'] == req['memory_text']
    source = json.loads(Path(prov['input_file']).read_text())
    assert source['user_uuid'] == prov['user_uuid']
    assert len(prov['new_evidence_pointers']) == len(original['new_evidence'])
    for path, ev in zip(prov['new_evidence_pointers'], original['new_evidence']):
        turn = pointer(source, path)
        assert ev['source_id'] == 'dialogue-' + path.split('/')[-1]
        assert (ev['text'],ev['speaker'],ev['recorded_at']) == (turn['content'],turn['role'],turn['timestamp'])
    ds_line, ds_pointer = prov['old_context_pointer'].split(', ',1)
    with Path(prov['dataset_file']).open(encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i == int(ds_line.split()[-1]):
                source_old = pointer(json.loads(line), ds_pointer)
                break
    a,b = prov['old_quote_character_range']
    assert source_old[a:b] == req['source_context'][0]['text'], (name, 'old context')
    contexts = v4._validate_request(req)
    v4._validate_response(split, req, contexts)
    assert len(split['facts']) == 1
    data = {'split_result':split, 'source_context':req['source_context'], 'new_evidence':original['new_evidence'], 'time_info':original['time_info']}
    judge.validate_request(data)
    out = HERE / (name+'_input.json')
    save(out,data)
    manifest['cases'][name] = {'prepared_input_path':str(out),'prepared_input_sha256':sha(out),
        'saved_model_input_path':str(d/'model_input.json'),'saved_model_input_sha256':sha(d/'model_input.json'),
        'saved_split_result_path':str(d/'split_result.json'),'saved_split_result_sha256':sha(d/'split_result.json'),
        'saved_provenance_path':str(d/'source_provenance.json'),'saved_provenance_sha256':sha(d/'source_provenance.json'),
        'original_provenance':prov,'checks':['v4_prompt_hash','original_file_hashes','memory_snapshot_id_text_user','new_source_pointers_text_speaker_time','old_context_pointer_and_range','v4_validator','component_input_validator','one_fact']}
save(HERE/'manifest_before.json',manifest)
print(json.dumps({'system_prompt_sha256':prompt_sha, 'code_sha256':manifest['code_sha256'], 'cases':{n:x['checks'] for n,x in manifest['cases'].items()}},ensure_ascii=False,indent=2))
