"""Controlled v2 local Qwen runner; same loading and decoding parameters as v1."""
import argparse
import json
from pathlib import Path
import time

import relation_judge_v2 as judge
from run_local import LocalQwen


class LocalQwenV2(LocalQwen):
    def __call__(self, payload):
        self.load()
        torch = self.torch
        messages = [{'role':'system','content':judge.SYSTEM}, {'role':'user','content':json.dumps(payload, ensure_ascii=False)}]
        self.messages.append(messages)
        rendered = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = self.tokenizer(rendered, return_tensors='pt').to('cuda:0')
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats(0)
        start = time.perf_counter()
        record = {'seconds':None,'peak_allocated_bytes':None,'peak_reserved_bytes':None,'output_tokens':None,'error':None}
        self.metrics['generations'].append(record)
        self.metrics['model_calls'] += 1
        try:
            with torch.inference_mode():
                output = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens, do_sample=False, pad_token_id=self.tokenizer.eos_token_id)
            torch.cuda.synchronize()
            tokens = output[0, inputs['input_ids'].shape[1]:]
            record['output_tokens'] = len(tokens)
            record['terminated_at_eos'] = bool(len(tokens) and tokens[-1].item() == self.tokenizer.eos_token_id)
            return self.tokenizer.decode(tokens, skip_special_tokens=True)
        except Exception as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            raise
        finally:
            record['seconds'] = round(time.perf_counter() - start, 3)
            record['peak_allocated_bytes'] = torch.cuda.max_memory_allocated(0)
            record['peak_reserved_bytes'] = torch.cuda.max_memory_reserved(0)
            free, total = torch.cuda.mem_get_info(0)
            record['device_used_bytes_at_end'] = total - free


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    with args.output.open('x', encoding='utf-8') as output:
        backend = LocalQwenV2()
        try:
            data = json.loads(args.input.read_text(encoding='utf-8'))
            result = judge.judge(data,backend)
            artifact = {'input':data,'model_messages':backend.messages,'result':result,'runtime':backend.metrics}
        except Exception as exc:
            artifact = {'input':None,'model_messages':backend.messages,'result':{'status':'input_error','errors':[{'stage':'input','type':type(exc).__name__,'message':str(exc)}]},'runtime':backend.metrics}
        json.dump(artifact, output, ensure_ascii=False,indent=2)
        output.write('\n')
    print(json.dumps({'status':artifact['result']['status'],'model_calls':backend.metrics['model_calls'],'output':str(args.output)},ensure_ascii=False))
    return 0 if artifact['result']['status']=='ok' else 1

if __name__ == '__main__':
    raise SystemExit(main())
