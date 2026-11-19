"""Freeze previously collected splitter inputs, and the two prompts, before comparison."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
PREVIOUS=BASE.parent / 'evidence_temporal_judge/runs/scope_check_20261105_v1/calls'
V8_REGRESSION=ROOT.parent / 'v8_real_dev_20261109_01_once'
CASES={'promotion':'01_promotion_split','skydiving':'02_skydiving_split','career_history':'03_career_history_split'}
def sha(b): return hashlib.sha256(b).hexdigest()
def save(p, obj):
    with p.open('x', encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
def main():
    prompt_paths={'v4':BASE/'prompt_versions/v4_boundaries_20261104/prompt.txt',
                  'v8':BASE/'prompt_versions/v8_v4_v7_combined/prompt.txt'}
    prompts={k:p.read_bytes() for k,p in prompt_paths.items()}
    assert sha(prompts['v8']) == json.loads((V8_REGRESSION/'attempt.json').read_text())['prompt_sha256']
    (ROOT/'prompts').mkdir()
    for version, data in prompts.items():
        with (ROOT/'prompts'/f'{version}.txt').open('xb') as f: f.write(data)
    (ROOT/'inputs').mkdir()
    records=[]
    previous_ids={json.loads(p.read_text())['memory_id'] for p in (ROOT.parent/'real_mem0_v3_v4_comparison_20261104_once/inputs').glob('*.json')}
    for name, call in CASES.items():
        path=PREVIOUS/call/'request.json'
        request=json.loads(path.read_text())['input']
        assert set(request) <= {'memory_id','memory_text','source_context'}
        assert request['memory_id'] not in previous_ids
        path_out=ROOT/'inputs'/f'{name}.json'
        save(path_out,request)
        records.append({'case':name,'origin':str(path),'input_sha256':sha(path_out.read_bytes())})
    save(ROOT/'manifest.json',{'created_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
        'cases':records,'prompts_sha256':{k:sha(v) for k,v in prompts.items()},
        'selection':'pre-existing downstream splitter inputs, not in the 11 earlier v3/v4 development cases; selected after v8 prompt frozen',
        'limits':'previously used in downstream experiments, not a random sample; v4 is an existing baseline and no claim that these cases are unknown to v4 development generally'})
if __name__=='__main__': main()
