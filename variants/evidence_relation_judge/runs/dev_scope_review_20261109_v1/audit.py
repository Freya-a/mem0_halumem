"""Read-only reproducibility, alignment, source and version checks for five cases."""
from pathlib import Path
from copy import deepcopy
import hashlib,json,sys
HERE=Path(__file__).resolve().parent;COMP=HERE.parent.parent;PROJ=COMP.parent.parent
sys.path[:0]=[str(COMP/'part2_scope_judge'),str(COMP/'part1_relation_judge'),str(PROJ/'variants/dnd_mem0_splitter')]
from scope_planner import plan_scope
from splitter import _validate_request,_validate_response

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf8'))
def pointer(obj,path):
 for item in path.strip('/').split('/'):obj=obj[int(item)] if isinstance(obj,list) else obj[item]
 return obj

frozen=load(HERE/'manifest_before.json'); files=frozen['sha256'];checks=[]
for path,digest in files.items():
 assert sha(Path(path))==digest,path
for part in ('part1_relation_judge','part2_scope_judge'):
 for f in (HERE/'frozen_code'/part).glob('*.py'):assert sha(f)==sha(COMP/part/f.name),str(f)
for name in ('job_transition','promotion','skydiving','persian_cats','career_history'):
 result=load(HERE/f'{name}_result.json');request=result['request']; split=request['split_result']; rows=result['results'];rr=result['relation_result']
 if name in ('job_transition','persian_cats'):
  upstream=load(HERE/f'{name}_v2.json');prepared=load(HERE/f'{name}_prepared.json');raw=result['evaluation_audit']['scope_generations'][0]['raw_output']
  assert upstream['input']==request and upstream['result']==rr
  evidence=load(Path(prepared['old_before_source']));assert evidence['before'][split['memory_id']]==split['memory_text']
  assert evidence['target_id']==prepared['target_id'] and evidence['original_target']['user_uuid']==prepared['user_uuid']
  assert sha(Path(prepared['dataset']))==prepared['dataset_sha256']
  line=evidence['original_target']['dataset_line_one_based']
  with Path(prepared['dataset']).open(encoding='utf8') as f:
   data=next(json.loads(x) for i,x in enumerate(f,1) if i==line)
  assert data['uuid']==prepared['user_uuid']
  for item,ev in zip(request['source_context'],evidence['original_target']['old_dialogue_evidence']):
   turn=pointer(data,ev['json_pointer']);assert (item['text'],item['speaker'],item['recorded_at'])==(ev['quote'],turn['role'],turn['timestamp']) and item['text'] in turn['content']
  for item,ev in zip(request['new_evidence'],evidence['original_target']['new_dialogue_evidence']):
   turn=pointer(data,ev['json_pointer']);assert (item['text'],item['speaker'],item['recorded_at'])==(ev['quote'],turn['role'],turn['timestamp']) and item['text'] in turn['content']
  origin='new_local_qwen'
 else:
  upstream=load(COMP/'runs/controlled_v2_20261106'/f'{name}_run.json');assert upstream['input']==request and upstream['result']==rr
  prov=load(PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'source_provenance.json')
  snap=load(Path(prov['before_file']));entry=pointer(snap,prov['snapshot_pointer'])
  assert (entry['id'],entry['memory'],entry['user_id'])==(split['memory_id'],split['memory_text'],prov['user_uuid'])
  assert sha(Path(prov['before_file']))==prov['before_sha256']
  assert sha(Path(prov['input_file']))==prov['input_sha256']
  session=load(Path(prov['input_file']))
  assert len(prov['new_evidence_pointers'])==len(request['new_evidence'])
  for path,item in zip(prov['new_evidence_pointers'],request['new_evidence']):
   turn=pointer(session,path);assert (item['text'],item['speaker'],item['recorded_at'])==(turn['content'],turn['role'],turn['timestamp'])
  line_text,ds_pointer=prov['old_context_pointer'].split(', ',1)
  with Path(prov['dataset_file']).open(encoding='utf8') as f:
   data=next(json.loads(x) for i,x in enumerate(f,1) if i==int(line_text.split()[-1]))
  assert data['uuid']==prov['user_uuid']
  a,b=prov['old_quote_character_range'];assert request['source_context'][0]['text']==pointer(data,ds_pointer)[a:b]
  v4=load(PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'split_result.json')['result'];assert v4==split
  qwen=load(COMP/'runs/scope_v2_20261109'/('skydiving_retry.json' if name=='skydiving' else f'{name}.json'));raw=qwen['run_audit']['generation'][0]['raw_output']
  origin='reused_saved_qwen'
 contexts=_validate_request({'memory_id':split['memory_id'],'memory_text':split['memory_text'],'source_context':request['source_context']})
 _validate_response(split,{'memory_id':split['memory_id'],'memory_text':split['memory_text'],'source_context':request['source_context']},contexts)
 assert len(rows)==len(split['facts'])==1 and len(rr['results'])==1
 for row,fact in zip(rows,split['facts']):
  assert row['memory_id']==split['memory_id']==fact['source_memory_id']
  assert row['fact_index']==fact['fact_index']==row['upstream']['full_row']['fact_index']
  assert row['upstream']['full_row']['old_subfact']==fact['raw_subfact']
  candidate=row['upstream']['full_row']['located_candidate'];source={x['source_id']:x['text'] for x in request['new_evidence']}
  assert candidate['new_quote']['source_id'] in source and candidate['new_quote']['quote'] in source[candidate['new_quote']['source_id']]
  nli=deepcopy(row['nli']);assert nli.pop('status')=='ok'
  def extractor(payload):return json.loads(raw)
  def score(premise,hypothesis):
   assert (premise,hypothesis)==(nli['premise'],nli['hypothesis'])
   return nli
  replay=plan_scope(request,rr,extractor=extractor,nli=score)
  original={k:v for k,v in result.items() if k!='evaluation_audit'}
  assert replay==original,(name,'replay differs')
  checks.append({'case':name,'v4_v2_origin':origin,'memory_id':split['memory_id'],'fact_index':fact['fact_index'],
    'v4_structure_and_source_quotes':'passed','v2_input_identity_and_new_quote':'passed','source_before_match':'passed',
    'planner_replay_exact':'passed','nli_status':row['nli']['status'],'nli_inference_mode':row['nli'].get('inference_mode','new_forward'),
    'facttrack':row['facttrack']['status'],'modifications':len(row['modifications']),'additions':len(result['additions'])})
result={'status':'passed','frozen_files_checked':len(files),'source_and_model_hash_changes':[],'frozen_code_copies_match':True,'cases':checks,
 'model_weight_limitation':'Qwen safetensor sizes and metadata recorded, full weights SHA256 not calculated','semantic_correctness':'not assessed by these program checks'}
with (HERE/'audit_verified.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
