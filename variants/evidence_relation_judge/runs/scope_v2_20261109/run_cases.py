"""Run three saved cases, optional Qwen extraction, and replay actual saved NLI scores."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

RUN=Path(__file__).resolve().parent
COMP=RUN.parent.parent
PART2=COMP/'part2_scope_judge'
sys.path.insert(0,str(PART2))
from scope_extract import LocalScopeExtractor, SYSTEM
from scope_planner import plan_scope


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    extractor=LocalScopeExtractor(max_new_tokens=1100)
    for name in ('promotion','skydiving','career_history'):
        saved=json.loads((COMP/'runs/scope_v1_20261109/replay_v2'/f'{name}.json').read_text())
        original_input=json.loads((COMP/'runs/real_cases_20261106'/f'{name}_input.json').read_text())
        assert saved['request']==original_input
        nli=deepcopy(saved['results'][0]['nli'])
        assert nli.pop('status')=='ok'
        def replay(premise,hypothesis):
            if (premise,hypothesis)!=(nli['premise'],nli['hypothesis']): raise ValueError('saved NLI inputs differ')
            return {**nli,'inference_mode':'replayed_real_saved_result',
                    'source_artifact':str(COMP/'runs/scope_v1_20261109/replay_v2'/f'{name}.json')}
        before=extractor.metrics['model_calls']
        result=plan_scope(saved['request'],saved['relation_result'],nli=replay,extractor=extractor)
        result['run_audit']={'input':str(COMP/'runs/real_cases_20261106'/f'{name}_input.json'),
            'v2_saved':str(COMP/'runs/controlled_v2_20261106'/f'{name}_run.json'),
            'qwen_calls_this_case':extractor.metrics['model_calls']-before,
            'nli_new_forward_passes':0,'nli_replay':'saved real output; input checked',
            'extractor_prompt':SYSTEM,'model_messages':deepcopy(extractor.messages[before:]),
            'generation':deepcopy(extractor.metrics['generations'][before:]),
            'model_metrics':deepcopy(extractor.metrics),'code_sha256':{p.name:sha(p) for p in (PART2/'scope_planner.py',PART2/'scope_actions.py',PART2/'scope_evidence.py',PART2/'scope_extract.py')}}
        output=RUN/f'{name}.json'
        with output.open('x',encoding='utf8') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
        row=result['results'][0]
        print(name,'extraction',row['extraction']['status'],'nli',row['nli']['status'],'mods',len(row['modifications']),'additions',len(result['additions']),flush=True)

if __name__=='__main__':main()
