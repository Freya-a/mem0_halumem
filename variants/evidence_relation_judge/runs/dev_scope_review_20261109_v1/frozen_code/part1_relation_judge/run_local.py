"""Run the candidate relation judge using the existing local Qwen3-8B only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import relation_judge

MODEL_DIR = Path(__file__).resolve().parent.parent / 'model' / 'Qwen3-8B'


class LocalQwen:
    def __init__(self, max_new_tokens=512):
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.load_error = None
        self.metrics = {'model_dir':str(MODEL_DIR), 'load_method':'AutoTokenizer/AutoModelForCausalLM.from_pretrained(local_files_only=True, torch_dtype=bfloat16), cuda:0', 'bf16_loaded':False, 'load_seconds':None, 'model_calls':0, 'generations':[], 'load_error':None}
        self.messages = []

    def load(self):
        if self.load_error:
            raise RuntimeError(self.load_error)
        if self.model is not None:
            return
        start = time.perf_counter()
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.torch = torch
            self.metrics['torch_version'] = torch.__version__
            import transformers
            self.metrics['transformers_version'] = transformers.__version__
            if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
                raise RuntimeError('CUDA or native BF16 unavailable')
            torch.cuda.reset_peak_memory_stats(0)
            self.metrics['gpu'] = torch.cuda.get_device_name(0)
            self.metrics['gpu_free_bytes_before_load'], self.metrics['gpu_total_bytes'] = torch.cuda.mem_get_info(0)
            self.tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), local_files_only=True)
            model = AutoModelForCausalLM.from_pretrained(str(MODEL_DIR), local_files_only=True, torch_dtype=torch.bfloat16)
            model.to('cuda:0').eval()
            self.model = model
            self.metrics['bf16_loaded'] = all(p.dtype == torch.bfloat16 for p in model.parameters() if p.is_floating_point())
            if not self.metrics['bf16_loaded']:
                raise RuntimeError('model floating-point parameters are not all BF16')
            self.metrics['cuda_allocated_after_load_bytes'] = torch.cuda.memory_allocated(0)
            self.metrics['cuda_reserved_after_load_bytes'] = torch.cuda.memory_reserved(0)
        except Exception as exc:
            self.load_error = f'{type(exc).__name__}: {exc}'
            self.metrics['load_error'] = self.load_error
            raise
        finally:
            self.metrics['load_seconds'] = round(time.perf_counter() - start, 3)

    def __call__(self, payload):
        self.load()
        torch = self.torch
        messages = [{'role':'system', 'content':relation_judge.SYSTEM}, {'role':'user', 'content':json.dumps(payload, ensure_ascii=False)}]
        self.messages.append(messages)
        rendered = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = self.tokenizer(rendered, return_tensors='pt').to('cuda:0')
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats(0)
        start = time.perf_counter()
        record = {'seconds':None, 'peak_allocated_bytes':None, 'peak_reserved_bytes':None, 'output_tokens':None, 'error':None}
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
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='new file; never overwritten')
    args = parser.parse_args()
    # Reserve output before model load; x prevents overwriting prior artifacts.
    with args.output.open('x', encoding='utf-8') as output:
        backend = LocalQwen()
        try:
            data = json.loads(args.input.read_text(encoding='utf-8'))
            result = relation_judge.judge(data, backend)
            artifact = {'input':data, 'model_messages':backend.messages, 'result':result, 'runtime':backend.metrics}
        except Exception as exc:
            artifact = {'input':None, 'model_messages':backend.messages, 'result':{'status':'input_error', 'errors':[{'stage':'input', 'type':type(exc).__name__, 'message':str(exc)}]}, 'runtime':backend.metrics}
        json.dump(artifact, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({'status':artifact['result']['status'], 'model_calls':backend.metrics['model_calls'], 'output':str(args.output)}, ensure_ascii=False))
    return 0 if artifact['result']['status'] == 'ok' else 1

if __name__ == '__main__':
    raise SystemExit(main())
