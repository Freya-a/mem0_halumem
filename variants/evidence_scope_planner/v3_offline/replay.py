"""Compare v2/v3 on identical saved model outputs; never call a model."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

# The old adapters and planners are read-only inputs, including their caches.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
RUN = PROJECT / 'variants/evidence_aligner/v4_scope_interface/runs/qwen_20261124_once'
V4 = RUN.parents[1]
V2 = PROJECT / 'variants/evidence_scope_planner/v2_offline/scope_planner.py'
V3 = HERE / 'scope_planner.py'
CASES = ('susan', 'promotion', 'career_history', 'transition', 'skydiving')


def fingerprint(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path}')
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def compare_same_input(args, old_planner, new_planner):
    """Deep-copy one projection to each planner and persist equality evidence."""
    baseline = copy.deepcopy(args)
    old_args = copy.deepcopy(baseline)
    new_args = copy.deepcopy(baseline)
    old_hash, new_hash = fingerprint(old_args), fingerprint(new_args)
    if old_hash != new_hash:
        raise ValueError('planner inputs differ before execution')
    v2 = old_planner.build_scope_plan(*old_args)
    v3 = new_planner.build_scope_plan(*new_args)
    return {'input_sha256': old_hash, 'v2_input_sha256': old_hash,
            'v3_input_sha256': new_hash, 'v2': v2, 'v3': v3}


def main():
    frozen_file = RUN / 'frozen_at_call/interface.py'
    guarded_file = V4 / 'interface.py'
    adapters = {'unprotected': module('v4_frozen_adapter_for_v3_replay', frozen_file),
                'guarded': module('v4_guarded_adapter_for_v3_replay', guarded_file)}
    planners = (module('v2_scope_for_v3_replay', V2), module('v3_scope_for_v3_replay', V3))
    manifest = json.loads((RUN / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') != 'completed' or manifest.get('request_attempts') != 5:
        raise ValueError('saved five-case run is incomplete')
    original_safe_manifest = json.loads((RUN / 'offline_safe/manifest.json').read_text(encoding='utf-8'))
    if (file_sha(guarded_file) != original_safe_manifest.get('adapter_sha256')
            or file_sha(V2) != original_safe_manifest.get('planner_sha256')):
        raise ValueError('guarded adapter or v2 planner differs from saved offline-safe provenance')
    output = HERE / 'results'
    output.mkdir(exist_ok=True)
    totals = {}
    for case in CASES:
        file = RUN / f'{case}.json'
        artifact = json.loads(file.read_text(encoding='utf-8'))
        raw, result = artifact.get('raw_response'), artifact.get('result') or {}
        if not isinstance(raw, str) or json.loads(raw) != result.get('parsed'):
            raise ValueError(f'{case} parsed output differs from saved response')
        payload, parsed = artifact['prepared_input'], result['parsed']
        case_data = {'case_id': case, 'model_call': False,
                     'source_artifact': str(file.relative_to(PROJECT)),
                     'source_sha256': file_sha(file),
                     'raw_response_sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
                     'raw_model_output': parsed, 'prepared_input': payload,
                     'validation': result['validation'], 'projections': {}}
        for label, adapter in adapters.items():
            args = adapter.planner_inputs(payload, parsed)
            if any(a.get('semantic_support') != 'unknown' for a in args[3]):
                raise ValueError('model semantic self-review cannot authorize planner action')
            both = compare_same_input(args, *planners)
            expected = (result['plan'] if label == 'unprotected' else
                        json.loads((RUN / 'offline_safe' / f'{case}.json').read_text())['safe_plan'])
            if both['v2'] != expected:
                raise ValueError(f'{case} {label} does not reproduce saved v2 result')
            case_data['projections'][label] = {'adapter_sha256': file_sha(frozen_file if label == 'unprotected' else guarded_file),
                                              'adapted_alignments': args[3], **both,
                                              'v2_matches_saved': True}
        (output / f'{case}.json').write_text(json.dumps(case_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        totals[case] = {p: {v: {k: len(z[v][k]) for k in ('modify','preserve','uncertain','add')}
                              for v in ('v2','v3')}
                        for p,z in case_data['projections'].items()}
        print(case, json.dumps(totals[case], ensure_ascii=False))
    summary = {'model_calls': 0, 'case_count': len(CASES),
               'source_manifest_sha256': file_sha(RUN / 'manifest.json'),
               'unprotected_adapter_sha256': file_sha(frozen_file),
               'guarded_adapter_sha256': file_sha(guarded_file),
               'v2_planner_sha256': file_sha(V2), 'v3_planner_sha256': file_sha(V3),
               'counts': totals}
    (output / 'manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
