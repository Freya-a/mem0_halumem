"""Read-only structural audit; never invokes a model or judges semantics."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1]))
import scope_run
import judge_scope

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = scope_run.validate_prepared(ROOT)
config, summary, preflight = (read(ROOT / f) for f in ('run_config.json', 'run_summary.json', 'preflight.json'))
assert config['request_limit'] == 6 and config['sdk_max_retries'] == 0 and not config['http_follow_redirects']
assert config['v4_split_reused'] and config['v4_prompt_sha256'] == sha(scope_run.scope.base.V4_PROMPT) == manifest['v4_prompt_sha256']
assert config['prepared_manifest_sha256'] == sha(ROOT/'prepared_manifest.json') == preflight['prepared_manifest_sha256']
assert config['prompt_sha256'] == sha(ROOT/'prompts.json') == preflight['prompts_json_sha256']
assert preflight['runner_sha256'] == sha(ROOT.parents[1]/'scope_run.py')
assert preflight['judge_scope_sha256'] == sha(ROOT.parents[1]/'judge_scope.py')
assert summary['reserved_count'] == summary['actual_sdk_attempts'] == 6 and summary['ambiguous_attempts'] == 0
journal = [json.loads(line) for line in (ROOT/'call_journal.jsonl').read_text().splitlines()]
assert len(journal) == 6
for index, case in enumerate(scope_run.CASES):
    folder = ROOT/case
    inputs, split, result, comparison = (read(folder/f) for f in ('model_input.json','split_result.json','scope_result.json','comparison.json'))
    request = inputs['split_request']
    assert result['memory_id'] == request['memory_id'] == split['result']['memory_id']
    assert result['memory_text'] == request['memory_text'] == split['result']['memory_text']
    assert result['new_evidence'] == inputs['new_evidence'] and result['source_context'] == request['source_context']
    assert comparison['scope_v2']['fact_judgments'] == result['facts'] and comparison['scope_v2']['new_candidates'] == result['new_candidates']
    assert comparison['v1']['fact_judgments'] == read(folder/'judge_result.json')['facts']
    assert comparison['v1']['new_candidates'] == read(folder/'candidate_stage.json')
    for offset, task in enumerate(('fact_judgment','new_candidates'),1):
        number = index*2+offset
        entry = journal[number-1]
        assert entry['number'] == number and entry['case'] == case and entry['task'] == task
        call = ROOT/'calls'/f'{number:02d}_{case}_{task}'
        saved, meta, parsed = (read(call/f) for f in ('request.json','response_metadata.json','parsed_response.json'))
        assert meta['attempted'] and not meta.get('error_type') and meta['metadata']['finish_reason'] == 'stop'
        assert json.loads((call/'raw_content.txt').read_text()) == parsed
        expected = ({'task': task, **request, 'fact': split['result']['facts'][0], 'new_evidence': inputs['new_evidence'], 'time_info': inputs['time_info']}
                    if task == 'fact_judgment' else {'task': task, 'new_evidence': inputs['new_evidence'], 'time_info': inputs['time_info'], 'old_facts': split['result']['facts']})
        assert saved['input'] == expected
        assert saved['system_prompt'] == (judge_scope.FACT_PROMPT if task == 'fact_judgment' else judge_scope.CANDIDATE_PROMPT)
        if task == 'fact_judgment':
            judge_scope.validate_fact(parsed, split['result']['facts'][0], judge_scope.base._sources(inputs['new_evidence']))
        else:
            judge_scope.validate_candidates(parsed, judge_scope.base._sources(inputs['new_evidence']))
    assert result['facts'][0]['semantic_support'] == result['new_candidates']['semantic_support'] == 'not_verified'
print('PASS: 3 saved v4 splits, 6 SDK attempts, 6 requests/responses, exact input and prompt alignment, schema and literal quotes; no retries')
print('NOT VERIFIED: semantic support, truth, correctness of scope, or user review')
