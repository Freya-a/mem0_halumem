"""Offline audit of frozen paired inputs, prompts, responses and outcomes."""
from pathlib import Path
import hashlib
import sys
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent
sys.path.insert(0,str(BASE))
from splitter import _read_json, MockBackend, ValidationError, split_memory
sha=lambda data: hashlib.sha256(data).hexdigest()
m=_read_json(ROOT/'manifest.json'); batch=_read_json(ROOT/'batch_completion.json'); launch=_read_json(ROOT/'attempt.json')
assert len(m['cases'])==3 and len(batch['reports'])==6 and batch['calls']==6
assert sha((ROOT/'prompts/v8.txt').read_bytes())==m['prompts_sha256']['v8']
assert sha((ROOT/'prompts/v4.txt').read_bytes())==m['prompts_sha256']['v4']
assert sha((ROOT/'prompts/v8.txt').read_bytes())==_read_json(ROOT.parent/'v8_real_dev_20261109_01_once/attempt.json')['prompt_sha256']
assert len(launch['order'])==6
for case in m['cases']:
    path=ROOT/'inputs'/f"{case['case']}.json"
    assert sha(path.read_bytes())==case['input_sha256']
    req=_read_json(path); assert req==_read_json(Path(case['origin']))['input']
    for version in ('v4','v8'):
        d=ROOT/case['case']/version; report=_read_json(d/'report.json'); start=_read_json(d/'attempt.json')
        assert report['model_calls']==1 and start['input_sha256']==case['input_sha256']
        assert start['prompt_sha256']==m['prompts_sha256'][version]
        try: result=split_memory(req,MockBackend(_read_json(d/'raw_content.txt')))
        except ValidationError as e:
            assert report['program_status']=='failed' and report['error']['code']==e.code and not (d/'result.json').exists()
        else:
            assert report['program_status']=='passed' and result==_read_json(d/'result.json') and len(result['facts'])==report['fact_count']
assert batch['passed']==sum(r['program_status']=='passed' for r in batch['reports'])
print(f"Replay verified: 3 exact inputs, 6 single-call reports, {batch['passed']} accepted; prompt and input hashes match.")
