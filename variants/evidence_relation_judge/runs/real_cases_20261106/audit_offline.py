"""Additional literal diagnostics only; never repairs or changes component results."""
import json
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / 'part1_relation_judge'))
import relation_judge as r

out = {}
for name in ('skydiving','promotion','career_history'):
    artifact = json.loads((HERE/f'{name}_run.json').read_text())
    data = artifact['input']; split = data['split_result']; fact = split['facts'][0]; row = artifact['result']['results'][0]
    c = row['candidate']; old = [e['quote'] for e in fact['evidence'] if e['source_type']=='memory']; sources = {s['source_id']:s['text'] for s in data['new_evidence']}
    keys={'memory_id','fact_index','old_subfact','relation','object','attribute','conditions','candidate_impact_fragment','old_quote','new_quote','reason','confirmation_questions'}
    nq = c.get('new_quote') if isinstance(c,dict) else None
    flags = {'json_parsed_object':isinstance(c,dict), 'exact_fields':set(c)==keys,
             'memory_id':c['memory_id']==split['memory_id'], 'fact_index':type(c['fact_index']) is int and c['fact_index']==fact['fact_index'],
             'old_subfact':c['old_subfact']==fact['raw_subfact'], 'relation_label':c['relation'] in r.LABELS,
             'old_quote':bool(c['old_quote'].strip()) and any(c['old_quote'] in q for q in old),
             'candidate_fragment':not c['candidate_impact_fragment'] or any(c['candidate_impact_fragment'] in q for q in old),
             'new_quote':isinstance(nq,dict) and nq.get('source_id') in sources and bool(nq.get('quote','').strip()) and nq['quote'] in sources[nq['source_id']],
             'uncertain_question':c['relation']!='uncertain' or bool(c['confirmation_questions'])}
    out[name]={'component_status':row['status'],'component_validation':row['validation'],'component_errors':row['errors'], 'literal_diagnostics':flags, 'semantic_correctness':'not_checked'}
with (HERE/'offline_literal_audit.json').open('x',encoding='utf-8') as f:
    json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
