"""Run strict v5 sequentially with the unmodified v2 Qwen generator."""
import argparse
import json
from pathlib import Path
import relation_judge_v2 as v2
import relation_judge_v5 as v5
from run_local_v2 import LocalQwenV2

class LocalQwenV5(LocalQwenV2):
    def __call__(self, payload):
        previous = v2.SYSTEM
        try:
            v2.SYSTEM = v5.SYSTEM
            return super().__call__(payload)
        finally:
            v2.SYSTEM = previous

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--max-new-tokens', type=int, default=768)
    args = parser.parse_args()
    if args.max_new_tokens <= 0:
        parser.error('--max-new-tokens must be positive')
    data = json.loads(args.input.read_text(encoding='utf-8'))
    backend = LocalQwenV5(max_new_tokens=args.max_new_tokens)
    with args.output.open('x', encoding='utf-8') as output:
        result = v5.judge(data, backend)
        json.dump({'input': data, 'model_messages': backend.messages, 'result': result,
                   'runtime': backend.metrics, 'max_new_tokens': args.max_new_tokens,
                   'no_retry': True}, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({'status': result['status'], 'model_calls': backend.metrics['model_calls'], 'output': str(args.output)}))
    return 0 if result['status'] == 'ok' else 1

if __name__ == '__main__':
    raise SystemExit(main())
