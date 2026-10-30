"""Optional isolated guard for Mem0 0.1.118; never enabled by the original runs.

Call guarded_add for one synchronous add at a time. This changes model behavior:
invalid update plans receive one correction request, then fail closed.
"""
import copy
import inspect
import json
import re

class InvalidUpdatePlan(Exception):
    """No valid update plan was available; the guarded batch was not applied."""


def _json_text(raw):
    if not isinstance(raw,str): raise ValueError('response is not text')
    stripped=raw.strip()
    match=re.match(r'^```[a-zA-Z0-9]*\n([\s\S]*?)\n```$',stripped)
    return match.group(1).strip() if match else stripped


def validate_plan(raw, mapping):
    try: obj=json.loads(_json_text(raw))
    except (ValueError,TypeError): return [{'reason':'invalid_json'}]
    if not isinstance(obj,dict) or not isinstance(obj.get('memory'),list): return [{'reason':'invalid_memory_list'}]
    problems=[]
    for index,entry in enumerate(obj['memory']):
        if not isinstance(entry,dict): problems.append({'reason':'invalid_entry','index':index}); continue
        event=entry.get('event'); key=entry.get('id')
        if event not in ('ADD','UPDATE','DELETE','NONE'): problems.append({'reason':'invalid_event','index':index}); continue
        if not isinstance(entry.get('text'),str) or not entry['text'].strip(): problems.append({'reason':'invalid_text','index':index})
        if event in ('UPDATE','DELETE') and (not isinstance(key,str) or key not in mapping):
            problems.append({'reason':'unknown_id','index':index,'id':key})
    return problems


def resolve_plan(raw, mapping, retry, messages, audit=lambda event: None):
    errors=validate_plan(raw,mapping); audit({'stage':'initial','raw_response':raw,'errors':errors})
    if not errors: return raw
    feedback=('The previous memory action plan cannot be executed. Validation errors: '
              +json.dumps(errors,ensure_ascii=False)+'\nValid existing memory IDs: '
              +json.dumps(sorted(mapping),ensure_ascii=False)
              +'\nReturn the complete corrected JSON plan. UPDATE and DELETE must use only these existing IDs. '
              'Do not guess an ID; if the correct action or existing memory is uncertain, use NONE or omit it. '
              'Preserve independently supported details and do not invent facts.')
    retry_messages=copy.deepcopy(messages)+[{'role':'assistant','content':raw},{'role':'user','content':feedback}]
    audit({'stage':'retry_request','messages':retry_messages})
    corrected=retry(retry_messages)
    errors=validate_plan(corrected,mapping); audit({'stage':'retry_response','raw_response':corrected,'errors':errors})
    if errors: raise InvalidUpdatePlan('Corrected update plan failed validation; no update plan was applied')
    return corrected


def guarded_add(memory, messages, *, audit, **kwargs):
    """Validate the entire plan before writes, retry once, and propagate rejection.

    Synchronous Mem0 0.1.118 only, graph disabled, single caller per memory object.
    The caller must provide an audit callback and separately log SDK calls/usage.
    A later non-ID write error can still cause partial writes and must be audited.
    """
    if getattr(memory,'enable_graph',False): raise ValueError('graph must be disabled')
    original=memory.llm.generate_response
    state={'failure':None,'seen_update':False}
    def wrapped(*args,**kw):
        caller=inspect.currentframe().f_back
        try:
            local=caller.f_locals
            is_update=caller.f_code.co_name=='_add_to_vector_store' and 'temp_uuid_mapping' in local
            mapping=dict(local['temp_uuid_mapping']) if is_update else None
        finally: del caller
        try: raw=original(*args,**kw)
        except Exception as exc:
            if is_update: state['failure']=exc
            raise
        if not is_update: return raw
        state['seen_update']=True
        model_messages=kw.get('messages') if 'messages' in kw else (args[0] if args else None)
        if not isinstance(model_messages,list):
            state['failure']=InvalidUpdatePlan('Cannot identify update model input; no update plan was applied')
            raise state['failure']
        def retry(retry_messages):
            if args and 'messages' not in kw: return original(retry_messages,*args[1:],**kw)
            retry_kw=dict(kw);retry_kw['messages']=retry_messages
            return original(*args,**retry_kw)
        try: return resolve_plan(raw,mapping,retry,model_messages,audit)
        except Exception as exc:
            state['failure']=exc
            raise
    memory.llm.generate_response=wrapped
    try:
        result=memory.add(messages,**kwargs)
        if state['failure'] is not None:
            raise InvalidUpdatePlan('Guard rejected the update plan or retry failed; no update plan was applied') from state['failure']
        return result
    finally: memory.llm.generate_response=original
