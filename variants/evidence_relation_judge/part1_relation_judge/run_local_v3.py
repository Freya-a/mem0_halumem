"""Run v3 relation prompt on saved input; writes only a new audit artifact."""
import argparse
import json
from pathlib import Path
from relation_judge_v3 import LocalQwenV3,judge


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--max-new-tokens',type=int,default=768);args=p.parse_args()
    if args.max_new_tokens<=0:p.error('--max-new-tokens must be positive')
    data=json.loads(args.input.read_text(encoding='utf8'));model=LocalQwenV3(max_new_tokens=args.max_new_tokens)
    with args.output.open('x',encoding='utf8') as f:
        result=judge(data,model)
        json.dump({'input':data,'result':result,'model_messages':model.messages,'runtime':model.metrics},f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':result['status'],'model_calls':model.metrics['model_calls'],'output':str(args.output)}))
    return 0 if result['status']=='ok' else 1
if __name__=='__main__':raise SystemExit(main())
