"""Replay a v4 request and full v2 result to a new review-only JSON file."""
import argparse
import json
from pathlib import Path
from scope_planner import plan_scope


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path)
    parser.add_argument('relation_result',type=Path,help='v2 result or saved artifact containing result')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--nli',action='store_true',help='run local DeBERTa; disabled by default')
    parser.add_argument('--extract-qwen',action='store_true',help='run local Qwen extraction; disabled by default')
    parser.add_argument('--max-new-tokens',type=int,default=1600,help='Qwen generation limit (default: 1600)')
    args=parser.parse_args()
    if args.max_new_tokens <= 0: parser.error('--max-new-tokens must be positive')
    request=json.loads(args.request.read_text(encoding='utf8'))
    relation=json.loads(args.relation_result.read_text(encoding='utf8'))
    if 'result' in relation: relation=relation['result']
    model=None
    if args.nli:
        from scope_nli import LocalNLI
        model=LocalNLI()
    extractor=None
    if args.extract_qwen:
        from scope_extract import LocalScopeExtractor
        extractor=LocalScopeExtractor(max_new_tokens=args.max_new_tokens)
    with args.output.open('x',encoding='utf8') as f:
        result=plan_scope(request,relation,nli=model,extractor=extractor)
        if extractor is not None:
            result['extraction_runtime']={'metrics':extractor.metrics,'messages':extractor.messages}
        json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps({'status':result['status'],'output':str(args.output)},ensure_ascii=False))
    return 1 if result['status']=='input_error' else 0

if __name__=='__main__': raise SystemExit(main())
