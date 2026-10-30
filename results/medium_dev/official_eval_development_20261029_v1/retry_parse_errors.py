#!/usr/bin/env python3
"""Explicit one-time retry of invalid official JSON, preserving all original calls."""
import json,time,fcntl
from openai import OpenAI
import engine,run_eval

def main():
 with (run_eval.OUT/'run.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  run_eval.prepare();env=run_eval.environment();client=OpenAI(api_key=env['LLM_API_KEY'],base_url=env['LLM_BASE_URL'],timeout=180,max_retries=0)
  with run_eval.db() as c:
   rows=c.execute("SELECT id FROM stages WHERE stage='judge' AND status='parse_error'").fetchall()
  for (ident,) in rows:
   with run_eval.db() as c:
    previous=c.execute("SELECT request FROM calls WHERE item=? AND stage='judge' AND status='ok' ORDER BY id DESC LIMIT 1",(ident,)).fetchone();request=json.loads(previous[0])
    c.execute("UPDATE stages SET status='started' WHERE id=? AND stage='judge'",(ident,))
    call_id=c.execute("INSERT INTO calls(item,stage,origin,status,request,started) VALUES(?,?,?,?,?,?)",(ident,'judge','development_retry','started',run_eval.enc(request),run_eval.now())).lastrowid
   start=time.monotonic()
   try:
    res=client.chat.completions.create(model=env['LLM_MODEL'],messages=[{'role':'user','content':request['prompt']}],temperature=0,max_tokens=16384)
    elapsed=time.monotonic()-start;raw=res.choices[0].message.content or '';payload={'raw':raw}
    try:payload['score']=engine.parse_score(raw);status='ok'
    except (ValueError,json.JSONDecodeError) as e:payload['type']=type(e).__name__;status='parse_error'
    with run_eval.db() as c:
     c.execute("UPDATE calls SET status='ok',response=?,usage=?,model=?,request_id=?,elapsed=? WHERE id=?",(run_eval.enc({'raw':raw}),run_eval.enc(res.usage.model_dump() if res.usage else None),res.model,getattr(res,'_request_id',None),elapsed,call_id))
     c.execute('UPDATE stages SET status=?,payload=? WHERE id=? AND stage=?',(status,run_eval.enc(payload),ident,'judge'))
    print('parse retry',ident,status,flush=True)
   except Exception as e:
    err={'type':type(e).__name__,'status_code':getattr(e,'status_code',None),'message':'Request failed; sensitive exception text withheld.'}
    with run_eval.db() as c:
     c.execute("UPDATE calls SET status='error',elapsed=?,error_type=?,error_code=? WHERE id=?",(time.monotonic()-start,err['type'],str(err['status_code']),call_id))
     c.execute("UPDATE stages SET status='error',payload=? WHERE id=? AND stage='judge'",(run_eval.enc(err),ident))
    print('parse retry failed',ident,err['type'],flush=True)
if __name__=='__main__':main()
