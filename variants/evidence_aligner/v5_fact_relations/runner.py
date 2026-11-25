"""Bounded five-case run with old fsync/no-retry runner and new interface."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
import interface
HERE=Path(__file__).resolve().parent
ALIGNER=HERE.parent
spec=importlib.util.spec_from_file_location('v4_one_shot_runner',ALIGNER/'v4_scope_interface/runner.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execute',action='store_true');parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args();cases=runner.load_fixed_cases();prompt=(HERE/'prompt.txt').read_text(encoding='utf-8')
    if not args.execute:
        for x in cases:interface.prepare_input(x)
        print(json.dumps({'status':'offline_preflight','case_count':len(cases),'model_calls':0}));return
    sys.path.insert(0,str(ALIGNER))
    from qwen_backend import QwenBackend
    runner.run_cases(cases,args.run_dir,prepare=interface.prepare_input,analyze=interface.analyze,
                     backend_factory=QwenBackend,system_prompt=prompt)
if __name__=='__main__':main()
