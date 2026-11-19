"""One explicit retry after the 1,100-token truncated skydiving extraction."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent; P=COMP/'part2_scope_judge';sys.path.insert(0,str(P))
import scope_extract
from scope_planner import plan_scope

scope_extract.SYSTEM += ' Keep output compact: each field has at most one quote, each quote is an exact substring of at most 8 words; omit empty field_evidence keys; concise reason and new_facts. Preserve each distinct new source.'
extractor=scope_extract.LocalScopeExtractor(max_new_tokens=1600)
old=json.loads((COMP/'runs/scope_v1_20261109/replay_v2/skydiving.json').read_text())
nli=deepcopy(old['results'][0]['nli']); assert nli.pop('status')=='ok'
def replay(premise,hypothesis):
    if (premise,hypothesis)!=(nli['premise'],nli['hypothesis']): raise ValueError('saved NLI inputs differ')
    return {**nli,'inference_mode':'replayed_real_saved_result','source_artifact':str(COMP/'runs/scope_v1_20261109/replay_v2/skydiving.json')}
source_hash={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (P/'scope_planner.py',P/'scope_actions.py',P/'scope_evidence.py',P/'scope_extract.py')}
result=plan_scope(old['request'],old['relation_result'],nli=replay,extractor=extractor)
result['run_audit']={'retry_of':'runs/scope_v2_20261109/skydiving.json','retry_reason':'Qwen output truncated at 1100 tokens and JSON parse failed',
    'qwen_calls_this_case':1,'nli_new_forward_passes':0,'extractor_prompt':scope_extract.SYSTEM,'model_messages':extractor.messages,
    'generation':extractor.metrics['generations'],'model_metrics':extractor.metrics,'code_sha256_at_start':source_hash}
with (HERE/'skydiving_retry.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
r=result['results'][0]; print('skydiving retry',r['extraction']['status'],r['extraction'].get('error'),'nli',r['nli']['status'],flush=True)
