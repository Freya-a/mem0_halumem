"""Replay recorded Qwen output and saved real NLI through the current planner."""
from copy import deepcopy
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent; P=COMP/'part2_scope_judge';sys.path.insert(0,str(P))
from scope_planner import plan_scope

output_dir=HERE/'final_checked';output_dir.mkdir(exist_ok=False)
files=[P/x for x in ('scope_planner.py','scope_actions.py','scope_evidence.py','scope_extract.py')]
code_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
for name in ('promotion','skydiving','career_history'):
    qwen_file=HERE/('skydiving_retry.json' if name=='skydiving' else f'{name}.json')
    qwen=json.loads(qwen_file.read_text()); raw=qwen['run_audit']['generation'][0]['raw_output']
    baseline=COMP/'runs/scope_v1_20261109/replay_v2'/f'{name}.json'
    saved=json.loads(baseline.read_text()); old_nli=deepcopy(saved['results'][0]['nli']); assert old_nli.pop('status')=='ok'
    def extract(payload): return json.loads(raw)
    def nli_replay(premise,hypothesis):
        if (premise,hypothesis)!=(old_nli['premise'],old_nli['hypothesis']): raise ValueError('saved NLI input mismatch')
        return {**old_nli,'inference_mode':'replayed_real_saved_result','source_artifact':str(baseline)}
    out=plan_scope(saved['request'],saved['relation_result'],nli=nli_replay,extractor=extract)
    out['replay_audit']={'qwen_source':str(qwen_file),'qwen_new_calls':0,'nli_source':str(baseline),'nli_new_forward_passes':0,
                         'code_sha256':code_hashes,'qwen_source_note':'recorded actual generation, parsed again without model call'}
    with (output_dir/f'{name}.json').open('x',encoding='utf8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    row=out['results'][0]
    print(name,'extract',row['extraction']['status'],row['extraction'].get('error'),'modifications',len(out['modifications']),'additions',len(out['additions']),'nli',row['nli']['status'],flush=True)
assert code_hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
