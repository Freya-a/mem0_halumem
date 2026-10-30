"""Observer adapter aware of the extra guard and retry call stack."""
import collections, copy, functools, inspect, json, time, traceback
from local_update_case import Observer
from mem0.memory.utils import remove_code_blocks
from medium_dev_run import atomic

class GuardObserver(Observer):
 def install(self,memory):
  original=memory.llm.generate_response
  super().install(memory)
  @functools.wraps(original)
  def generate(*args,**kwargs):
   frame=inspect.currentframe().f_back; native=None
   while frame:
    if frame.f_code.co_name=='_add_to_vector_store' and 'new_retrieved_facts' in frame.f_locals: native=frame; break
    frame=frame.f_back
   update=native is not None and 'temp_uuid_mapping' in native.f_locals
   mapping=copy.deepcopy(native.f_locals.get('temp_uuid_mapping',{})) if update else {}
   facts=copy.deepcopy(native.f_locals.get('new_retrieved_facts')) if update else None
   retrieved=copy.deepcopy(native.f_locals.get('retrieved_old_memory')) if update else None
   del frame,native
   messages=kwargs.get('messages',args[0] if args else None)
   stage='update' if update else 'extraction'
   self.emit('model_input',stage=stage,messages=copy.deepcopy(messages),response_format=kwargs.get('response_format'),native_temp_uuid_mapping=mapping,native_new_facts=facts,native_retrieved_old_memory=retrieved)
   tick=time.perf_counter()
   try:
    result=original(*args,**kwargs)
    try: parsed,parse_error=json.loads(remove_code_blocks(result)),None
    except Exception: parsed,parse_error=None,traceback.format_exc()
    self.emit('model_output',stage=stage,raw_response=result,parsed=parsed,parse_error=parse_error,native_temp_uuid_mapping=mapping,elapsed_seconds=time.perf_counter()-tick)
    return result
   except Exception:
    self.emit('model_exception',stage=stage,traceback=traceback.format_exc());raise
  memory.llm.generate_response=generate

def derive(folder,observer):
 entries=observer.entries; inputs=[x for x in entries if x['kind']=='model_input' and x.get('stage')=='update']; outputs=[x for x in entries if x['kind']=='model_output' and x.get('stage')=='update']; audit=[x for x in entries if x['kind']=='guard_audit'];
 mapping=inputs[0]['native_temp_uuid_mapping'] if inputs else {}; valid=sorted(mapping,key=lambda x:int(x) if x.isdigit() else x)
 initial=next((x for x in audit if x.get('stage')=='initial'),None); corrected=next((x for x in audit if x.get('stage')=='retry_response'),None); retried=any(x.get('stage')=='retry_request' for x in audit)
 accepted=(corrected if retried else initial); accepted=accepted if accepted and not accepted['errors'] else None
 def parsed(obj):
  if not obj:return None
  try:return json.loads(remove_code_blocks(obj['raw_response']))
  except Exception:return None
 initial_plan=parsed(initial); final_plan=parsed(accepted)
 def resolve(plan):
  if not isinstance(plan,dict) or not isinstance(plan.get('memory'),list):return None
  return [{'plan_index_zero_based':i,**x,'resolved_existing_memory_id':mapping.get(x.get('id')) if x.get('event') in ('UPDATE','DELETE','NONE') else None} for i,x in enumerate(plan['memory'])]
 first=resolve(initial_plan);final=resolve(final_plan)
 atomic(folder/'observations.json',entries); atomic(folder/'guard_audit.json',audit)
 atomic(folder/'update_model_io.json',[x for x in entries if x.get('stage')=='update' and x['kind'].startswith('model_')])
 atomic(folder/'extracted_facts.json',[x for x in entries if x.get('stage')=='extraction' and x['kind'].startswith('model_')])
 atomic(folder/'recall_candidates.json',[x for x in entries if x['kind'].startswith('recall_')])
 atomic(folder/'initial_plan.json',first);atomic(folder/'final_plan.json',final)
 atomic(folder/'valid_ids.json',{'valid_ids':valid,'id_to_uuid':mapping,'count':len(valid)})
 atomic(folder/'execution_results.json',[x for x in entries if x['kind'].startswith('operation_')])
 invalid=[x.get('id') for x in (initial or {}).get('errors',[]) if x.get('reason')=='unknown_id']
 result={'valid_ids':valid,'initial_invalid_ids':invalid,'initial_validation_errors':(initial or {}).get('errors'),'retry_triggered':retried,'retry_response_received':corrected is not None,'retry_validation_errors':corrected.get('errors') if corrected else None,'final_plan_counts':dict(collections.Counter(x.get('event') for x in final)) if final is not None else None,'initial_plan_counts':dict(collections.Counter(x.get('event') for x in first)) if first is not None else None,'final_plan_accepted':accepted is not None}
 atomic(folder/'guard_summary.json',result);return result
