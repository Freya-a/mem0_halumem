"""Run review-only stage planner using a full v2/v3 relation result."""
import argparse
import json
from pathlib import Path
from scope_planner_v2 import plan_scope


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request',type=Path);parser.add_argument('relation_result',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--stage-qwen',action='store_true',help='enable local Qwen stage extraction')
    parser.add_argument('--nli',action='store_true',help='enable local NLI (auxiliary only)')
    parser.add_argument('--max-new-tokens',type=int,default=1000)
    args=parser.parse_args()
    if args.max_new_tokens<=0:parser.error('--max-new-tokens must be positive')
    request=json.loads(args.request.read_text(encoding='utf8')); relation=json.loads(args.relation_result.read_text(encoding='utf8'))
    if 'result' in relation:relation=relation['result']
    stage=None;nli=None
    if args.stage_qwen:
        from stage_extract import LocalStageExtractor
        stage=LocalStageExtractor(max_new_tokens=args.max_new_tokens)
    if args.nli:
        from scope_nli import LocalNLI
        nli=LocalNLI()
    with args.output.open('x',encoding='utf8') as f:
        out=plan_scope(request,relation,stage_extractor=stage,nli=nli)
        if stage is not None:out['stage_runtime']={'metrics':stage.metrics,'messages':stage.messages}
        json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':out['status'],'historicalizations':len(out['historicalizations']),'output':str(args.output)},ensure_ascii=False))
    return 1 if out['status']=='input_error' else 0

if __name__=='__main__':raise SystemExit(main())
