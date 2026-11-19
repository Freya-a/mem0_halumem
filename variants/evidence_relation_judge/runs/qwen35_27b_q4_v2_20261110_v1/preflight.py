"""Preserve two smoke-test responses and gate the real-case run."""
import json
import time
from pathlib import Path
from urllib.request import build_opener, ProxyHandler, Request
HERE=Path(__file__).resolve().parent
opener=build_opener(ProxyHandler({}))

def request(messages):
    template_request={'messages':messages,'chat_template_kwargs':{'enable_thinking':False}}
    template_body=json.dumps(template_request,ensure_ascii=False).encode()
    with opener.open(Request('http://127.0.0.1:18081/apply-template',data=template_body,headers={'Content-Type':'application/json'}),timeout=30) as response:
        template_raw=response.read().decode()
    params={'prompt':json.loads(template_raw)['prompt'],'temperature':0,'n_predict':256,'stream':False}
    started=time.perf_counter()
    data=json.dumps(params,ensure_ascii=False).encode()
    with opener.open(Request('http://127.0.0.1:18081/completion',data=data,headers={'Content-Type':'application/json'}),timeout=300) as response:
        raw=response.read().decode()
    result=json.loads(raw)
    return {'template_request':template_request,'template_response_raw':template_raw,'request':params,'raw_http_response':raw,'response':result,'elapsed_seconds':round(time.perf_counter()-started,3)}

def visible(row):
    content=row['response'].get('content')
    return content if isinstance(content,str) else ''

def no_thinking(row):
    content=visible(row)
    return bool(content) and '<think>' not in content and '</think>' not in content

# These two endpoints inspect server properties and formatting without generating tokens.
with opener.open('http://127.0.0.1:18081/props',timeout=30) as response:
    props=response.read().decode('utf-8')
json.loads(props)
(HERE/'server_props.json').write_text(props,encoding='utf-8')
template_input={'messages':[{'role':'user','content':'请只回复：测试成功'}],'chat_template_kwargs':{'enable_thinking':False}}
template_request=Request('http://127.0.0.1:18081/apply-template',data=json.dumps(template_input,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
with opener.open(template_request,timeout=30) as response:
    rendered=response.read().decode('utf-8')
json.loads(rendered)
(HERE/'rendered_template.json').write_text(rendered,encoding='utf-8')
plain=request(template_input['messages'])
(HERE/'smoke_plain.json').write_text(json.dumps(plain,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
js=request([{'role':'system','content':'只输出一个 JSON 对象，不要 Markdown。'},{'role':'user','content':'输出一个对象，字段 ok 为 true。'}])
(HERE/'smoke_json.json').write_text(json.dumps(js,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
try:
    obj=json.loads(visible(js))
    json_ok=isinstance(obj,dict) and obj.get('ok') is True
except (ValueError,TypeError):
    json_ok=False
state={'plain_text_ok':bool(visible(plain)), 'json_no_thinking_ok':json_ok and no_thinking(js), 'plain_no_thinking':no_thinking(plain), 'json_parse_ok':json_ok, 'note':'No cleanup of returned content; raw server responses retained. Preflight is a simple probe, not proof that thinking can never appear.'}
with (HERE/'preflight.json').open('x',encoding='utf-8') as f:
    json.dump(state,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(state,ensure_ascii=False),flush=True)
