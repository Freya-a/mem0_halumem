"""Read-only integrity audit of this run, never invokes a model."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import driver


def load(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

config=load(HERE/'run_config.json'); summary=load(HERE/'run_summary.json')
prepared=driver.prepare_cases()
assert config['prompt_sha256']==sha(config['prompt_path'])
assert summary['actual_sdk_attempts']==summary['reserved_count']==9<=10
assert summary['ambiguous_attempts']==summary['failed_journal_events']==0
journal=[json.loads(line) for line in (HERE/'call_journal.jsonl').read_text().splitlines()]
assert len(journal)==18
assert [e['number'] for e in journal if e['event']=='reserved_before_request']==list(range(1,10))
assert all(e.get('attempted') is True for e in journal if e['event']=='returned')
for c in prepared:
    directory=HERE/c['name']; source=load(directory/'source_provenance.json'); raw_input=load(directory/'model_input.json')
    assert source==c['provenance']
    assert raw_input=={'split_request':c['request'],'new_evidence':c['new_evidence'],'time_info':None}
    split=load(directory/'split_result.json'); assert split['prompt']['sha256']==config['prompt_sha256']
    contexts=driver.judge._splitter._validate_request(c['request'])
    driver.judge._splitter._validate_response(split['result'],c['request'],contexts)
    output=load(directory/'judge_result.json')
    assert output['memory_id']==c['request']['memory_id'] and output['new_evidence']==c['new_evidence']
    assert len(output['facts'])==len(split['result']['facts'])
    for f in output['facts']:
        assert f['status']!='failed'
        judgement={k:v for k,v in f.items() if k not in ('fact','status')}
        driver.judge._validate_judgment(judgement,f['fact'],driver.judge._sources(c['new_evidence']))
    candidates=load(directory/'candidate_stage.json'); assert candidates.pop('status')=='ok'
    driver.judge._validate_candidates(candidates,driver.judge._sources(c['new_evidence']))
for folder in sorted((HERE/'calls').iterdir()):
    request=load(folder/'request.json'); meta=load(folder/'response_metadata.json'); parsed=load(folder/'parsed_response.json')
    assert meta['attempted'] and meta['metadata']['finish_reason']=='stop'
    assert json.loads((folder/'raw_content.txt').read_text(encoding='utf-8'))==parsed
    assert not any(k in request['input'] for k in ('human_conclusion','allowed_modification_scope','expected','review_decision'))
    if folder.name.endswith('_split'):
        assert request['system_prompt']==Path(config['prompt_path']).read_text(encoding='utf-8')
print('verified: 3 cases; 9 SDK attempts, 0 failed responses; 3 v4 prompts; quote/schema/source hashes; 9 raw responses and requests')
print('semantic correctness and reviewer confirmation are not verified by this program')
