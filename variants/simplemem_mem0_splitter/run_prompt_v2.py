"""Run the same five cases with v2, leaving the baseline runner and data intact."""
import json
import run_file_priority as runner
from prompt_v2 import build_extraction_prompt_v2


def main():
    baseline = runner.HERE / 'run_20261119_file_priority'
    cases = json.loads((baseline / 'cases.json').read_text(encoding='utf-8'))
    selected = json.loads((runner.HERE / 'run/cases.json').read_text(encoding='utf-8'))
    if cases != selected or len(cases) != 5:
        raise ValueError('Baseline cases are not identical to the selected cases')
    for i, case in enumerate(cases, 1):
        recorded = json.loads((baseline / f'case_{i}.json').read_text(encoding='utf-8'))
        if recorded['input'] != {k:case[k] for k in ('memory_id','memory_text','source_context')}:
            raise ValueError('Baseline input mismatch')
    runner.RUN = runner.HERE / 'run_20261119_prompt_v2'
    runner.build_extraction_prompt = build_extraction_prompt_v2
    runner.main()

if __name__ == '__main__': main()
