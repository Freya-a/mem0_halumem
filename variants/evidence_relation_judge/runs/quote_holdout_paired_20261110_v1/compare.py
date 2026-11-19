"""Offline paired comparison; strict literal provenance checks do not grade semantics."""
import json,sys
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent;COMP=HERE.parents[1]
sys.path.insert(0,str(COMP/'part1_relation_judge'));import relation_judge_v2 as v2
units=json.loads((HERE/'pair_inputs.json').read_text());done=json.loads((HERE/'pair_completion.json').read_text()); rows=[]
if done['transport_failure'] or done['completed_version_units']!=done['expected_version_units']: print('WARNING: incomplete run')
for unit in units:
 ident=f"{unit['record']:02d}_{unit['memory_id']}"; paths={v:HERE/'pairs'/f'{ident}_{v}.json' for v in ['v2','experimental']}; versions={}
 for version,path in paths.items():
  if not path.exists():versions[version]={'status':'not_run'};continue
  a=json.loads(path.read_text());assert a['input']==unit['input']; results=[]
  for r in a['result']['results']:
   c=r.get('candidate'); fact=next(f for f in unit['input']['split_result']['facts'] if f['fact_index']==r['fact_index']); memq=[e['quote'] for e in fact['evidence'] if e['source_type']=='memory']; newmap={e['source_id']:e['text'] for e in unit['input']['new_evidence']}
   oq=c.get('old_quote') if isinstance(c,dict) else None;nq=c.get('new_quote') if isinstance(c,dict) else None
   old_ok=isinstance(oq,str) and bool(oq.strip()) and any(oq in q for q in memq)
   new_ok=isinstance(nq,dict) and isinstance(nq.get('quote'),str) and bool(nq['quote'].strip()) and nq.get('source_id') in newmap and nq['quote'] in newmap[nq['source_id']]
   fragment=c.get('candidate_impact_fragment') if isinstance(c,dict) else None
   match=v2.locate_fragment(unit['input']['split_result']['memory_text'],fragment,memq) if isinstance(fragment,str) else None
   results.append({'fact_index':r['fact_index'],'status':r['status'],'raw_output':r['raw_output'],'candidate':c,'validation':r['validation'],'errors':r['errors'],'old_quote_literal_match':old_ok,'new_quote_literal_match':new_ok,'fragment_match_rechecked':match,'semantic_correctness':'not_checked'})
  versions[version]={'status':a['result']['status'],'calls_attempted':a['calls_attempted'],'facts':results,'path':str(path),'seconds':[x['elapsed_seconds'] for x in a['calls']],'generation_parameters':[ {k:v for k,v in x['request'].items() if k!='prompt'} if x['request'] else None for x in a['calls']]}
 if all(versions[v]['status']!='not_run' for v in versions):
  assert versions['v2']['generation_parameters']==versions['experimental']['generation_parameters']
  assert [f['fact_index'] for f in versions['v2']['facts']]==[f['fact_index'] for f in versions['experimental']['facts']]
 rows.append({'record':unit['record'],'target_id':unit['target_id'],'memory_id':unit['memory_id'],'old_memory':unit['input']['split_result']['memory_text'],'versions':versions,'semantic_review':'pending'})
counts={}
for v in ['v2','experimental']:
 facts=[f for r in rows for f in r['versions'][v].get('facts',[])]
 counts[v]={'fact_outputs':len(facts),'format_and_provenance_pass':sum(f['status']=='ok' for f in facts),'old_quote_literal_mismatch':sum(f['candidate'] is not None and not f['old_quote_literal_match'] for f in facts),'new_quote_literal_mismatch':sum(f['candidate'] is not None and not f['new_quote_literal_match'] for f in facts),'fragment_not_located':sum(f['fragment_match_rechecked'] is not None and f['fragment_match_rechecked']['located'] is None for f in facts),'parse_fail':sum(any(e['stage']=='parse' for e in f['errors']) for f in facts),'model_fail':sum(any(e['stage']=='model' for e in f['errors']) for f in facts)}
result={'fact_units':len(rows),'counts':counts,'notes':'Mismatch classes can overlap and checks only assess literal location, not whether a quote supports a claim; malformed candidates are separately represented.','rows':rows}
with (HERE/'comparison.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(counts,ensure_ascii=False,indent=2))
