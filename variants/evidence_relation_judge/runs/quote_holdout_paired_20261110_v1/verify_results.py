"""Read-only audit of prepared evidence, frozen prompts, calls and raw responses."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;COMP=P.parents[1];PROJECT=P.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((P/'pair_manifest.json').read_text());completion=json.loads((P/'pair_completion.json').read_text());splitmanifest=json.loads((P/'split_manifest.json').read_text());splitdone=json.loads((P/'split_completion.json').read_text());provenance=json.loads((P/'prepared_verification.json').read_text());prior=json.loads((COMP/'runs/quote_provenance_20261110_v1/manifest.json').read_text())
assert provenance['count']==18 and len(provenance['records'])==18
assert splitdone['calls_attempted']==15 and sum(x['status']=='reused_v4' for x in splitdone['results'])==1
assert splitmanifest['splitter_prompt_sha256']==sha(P/'frozen_splitter_prompt.txt')==sha(PROJECT/'variants/dnd_mem0_splitter/prompt_versions/v4_boundaries_20261104/prompt.txt')
assert splitmanifest['splitter_code_sha256']==sha(PROJECT/'variants/dnd_mem0_splitter/splitter.py')
assert manifest['v2_prompt_sha256']==sha(P/'prompt_v2.txt')==prior['v2_system_sha256']
assert manifest['experimental_prompt_sha256']==sha(P/'prompt_experimental.txt')==prior['experimental_system_sha256']
for path,digest in prior['source_sha256'].items():assert sha(Path(path))==digest
assert completion['model_calls']==36 and completion['transport_failure'] is None and completion['completed_version_units']==completion['expected_version_units']==36
units=json.loads((P/'pair_inputs.json').read_text()); assert len(units)==18
for unit in units:
 ident=f"{unit['record']:02d}_{unit['memory_id']}"; paired=[]
 for version in ['v2','experimental']:
  data=json.loads((P/'pairs'/f'{ident}_{version}.json').read_text());assert data['input']==unit['input'] and data['calls_attempted']==1 and len(data['calls'])==1
  call=data['calls'][0];assert call['generation_attempted'] and call['messages'][0]['content']==(P/f'prompt_{version}.txt').read_text();assert data['result']['results'][0]['raw_output']==call['raw_response']['content']; assert data['result']['results'][0]['validation']['semantic_correctness']=='not_checked'
  assert sha(P/'pairs'/f'{ident}_{version}_fact1.call.json')
  paired.append(call)
 assert paired[0]['messages'][1]==paired[1]['messages'][1]
 assert {k:v for k,v in paired[0]['request'].items() if k!='prompt'}=={k:v for k,v in paired[1]['request'].items() if k!='prompt'}
 assert paired[0]['template_request']['chat_template_kwargs']==paired[1]['template_request']['chat_template_kwargs']=={'enable_thinking':False}
comparison=json.loads((P/'comparison.json').read_text()); assert comparison['counts']['v2']['parse_fail']==comparison['counts']['experimental']['parse_fail']==0
report={'status':'passed','input_records':18,'executed_records':len({x['record'] for x in units}),'fact_units_per_version':len(units),'splitter_calls':15,'judge_calls':36,'source_and_prompt_hashes':'unchanged','pair_inputs_and_parameters':'equal','raw_generation_content':'preserved','semantic_correctness':'not_checked','notes':'Four executed records have partial reviewed-target evidence; see coverage_audit.json.'}
with (P/'final_verification.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(report,ensure_ascii=False))
