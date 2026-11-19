"""Read-only replay of saved v8 response through the existing validation boundary."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE))
from splitter import _read_json, MockBackend, ValidationError, split_memory

batch = _read_json(ROOT / 'batch_completion.json')
attempt = _read_json(ROOT / 'attempt.json')
hash_bytes = lambda b: hashlib.sha256(b).hexdigest()
assert hash_bytes((ROOT / 'frozen_prompt.txt').read_bytes()) == attempt['prompt_sha256']
assert len(batch['reports']) == len(attempt['cases']) == 8
assert [r['case_id'] for r in batch['reports']] == attempt['cases']
for row in batch['reports']:
    d = ROOT / row['case_id']
    record = _read_json(d / 'attempt.json')
    assert hash_bytes((d / 'input.json').read_bytes()) == record['input_sha256']
    assert (d / 'input.json').read_bytes() == (ROOT.parent / 'v6_real_dev_20261109_01_once' / row['case_id'] / 'input.json').read_bytes()
    assert record['prompt_sha256'] == attempt['prompt_sha256']
    assert row['model_calls'] == 1
    request = _read_json(d / 'input.json')
    raw = _read_json(d / 'raw_content.txt')
    try:
        result = split_memory(request, MockBackend(raw))
    except ValidationError as error:
        assert row['program_status'] == 'failed'
        assert error.code == row['error']['code'] and error.path == row['error']['path']
        assert not (d / 'result.json').exists()
    else:
        assert row['program_status'] == 'passed'
        assert result == _read_json(d / 'result.json')
        assert len(result['facts']) == row['fact_count']
assert batch['calls'] == 8
assert batch['passed'] == 8
print('Replay verified: 8 inputs, 8 single-call reports, 8 accepted, 0 rejected; results and hashes match.')
