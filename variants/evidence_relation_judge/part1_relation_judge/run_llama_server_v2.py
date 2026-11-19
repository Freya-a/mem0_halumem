"""Run component-one v2 against a loopback llama-server, preserving raw responses."""
import argparse
import json
import subprocess
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

import relation_judge_v2 as judge


class LlamaServerV2:
    def __init__(self, base_url='http://127.0.0.1:18081', max_tokens=768, timeout=300):
        url = urlsplit(base_url)
        if url.scheme != 'http' or url.hostname not in ('localhost', '127.0.0.1', '::1') or url.username or url.password or url.path not in ('', '/') or url.query or url.fragment:
            raise ValueError('llama-server URL must be a loopback HTTP origin')
        self.url = base_url.rstrip('/')
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.records = []
        self.opener = build_opener(ProxyHandler({}))

    def __call__(self, payload):
        messages = [{'role':'system','content':judge.SYSTEM}, {'role':'user','content':json.dumps(payload, ensure_ascii=False)}]
        template_request = {'messages':messages, 'chat_template_kwargs':{'enable_thinking':False}}
        record = {'messages':messages, 'template_request':template_request, 'template_response_text':None, 'request':None, 'generation_attempted':False, 'raw_response_text':None, 'raw_response':None, 'http_status':None, 'elapsed_seconds':None, 'gpu_device_used_mib_peak_sampled':None, 'gpu_samples':0, 'error':None}
        self.records.append(record)
        stop = threading.Event()
        def monitor():
            while not stop.is_set():
                try:
                    p = subprocess.run(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits','-i','0'], capture_output=True, text=True, timeout=2, check=True)
                    value = int(p.stdout.strip())
                    record['gpu_device_used_mib_peak_sampled'] = max(record['gpu_device_used_mib_peak_sampled'] or 0, value)
                    record['gpu_samples'] += 1
                except (ValueError, OSError, subprocess.SubprocessError):
                    pass
                stop.wait(0.2)
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        start = time.perf_counter()
        try:
            body = json.dumps(template_request, ensure_ascii=False).encode('utf-8')
            with self.opener.open(Request(self.url + '/apply-template', data=body, headers={'Content-Type':'application/json'}), timeout=self.timeout) as response:
                record['template_response_text'] = response.read().decode('utf-8')
            prompt = json.loads(record['template_response_text'])['prompt']
            if not isinstance(prompt, str): raise ValueError('template returned no prompt')
            request = {'prompt':prompt, 'temperature':0, 'n_predict':self.max_tokens, 'stream':False}
            record['request'] = request
            body = json.dumps(request, ensure_ascii=False).encode('utf-8')
            record['generation_attempted'] = True
            with self.opener.open(Request(self.url + '/completion', data=body, headers={'Content-Type':'application/json'}), timeout=self.timeout) as response:
                record['http_status'] = response.status
                record['raw_response_text'] = response.read().decode('utf-8')
            record['raw_response'] = json.loads(record['raw_response_text'])
            content = record['raw_response'].get('content')
            if not isinstance(content, str):
                raise ValueError('server returned no text content')
            return content
        except Exception as exc:
            if isinstance(exc, HTTPError):
                record['http_status'] = exc.code
                record['raw_response_text'] = exc.read().decode('utf-8', errors='replace')
            record['error'] = {'type':type(exc).__name__, 'message':str(exc)}
            raise
        finally:
            record['elapsed_seconds'] = round(time.perf_counter() - start, 3)
            stop.set()
            thread.join(timeout=3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--url', default='http://127.0.0.1:18081')
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding='utf-8'))
    with args.output.open('x', encoding='utf-8') as output:
        backend = LlamaServerV2(args.url)
        result = judge.judge(data, backend)
        json.dump({'input':data, 'model_calls':sum(r['generation_attempted'] for r in backend.records), 'calls':backend.records, 'result':result}, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({'status':result['status'], 'model_calls':sum(r['generation_attempted'] for r in backend.records), 'output':str(args.output)}, ensure_ascii=False))
    return 0 if result['status'] == 'ok' else 1

if __name__ == '__main__':
    raise SystemExit(main())
