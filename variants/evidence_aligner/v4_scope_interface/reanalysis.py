"""Reproject saved replies offline through current interface without retrying calls."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
CASES = ('susan', 'promotion', 'career_history', 'transition', 'skydiving')


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def make_safe_result(artifact, artifact_sha, adapter_sha, planner_sha, interface, planner):
    raw, result = artifact.get('raw_response'), artifact.get('result') or {}
    parsed = result.get('parsed')
    output = {'case_id': artifact.get('case_id'), 'model_call': False,
              'provenance': {'artifact_sha256': artifact_sha, 'adapter_sha256': adapter_sha,
                             'planner_sha256': planner_sha,
                             'raw_response_sha256': sha256_bytes(raw.encode('utf-8')) if isinstance(raw, str) else None},
              'initial_plan': copy.deepcopy(result.get('plan')), 'safe_plan': None,
              'adapted_alignments': None, 'validation': None}
    if not isinstance(raw, str) or not isinstance(parsed, dict):
        output['status'] = 'no_parsed_response'
        return output
    if json.loads(raw) != parsed:
        raise ValueError('saved parsed result does not match raw_response')
    payload = artifact['prepared_input']
    output['validation'] = interface.validate_output(parsed, payload)
    args = interface.planner_inputs(payload, parsed)
    if any(a.get('semantic_support') != 'unknown' for a in args[3]):
        raise ValueError('reanalysis must never inject independent semantic approval')
    output['adapted_alignments'] = copy.deepcopy(args[3])
    output['safe_plan'] = planner.build_scope_plan(*args)
    output['status'] = 'completed_offline'
    return output


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description='Pure offline reanalysis of saved replies')
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    target = run / 'offline_safe'
    source_manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    if source_manifest.get('status') != 'completed':
        raise ValueError('original model run must be completed before reanalysis')
    adapter_file = HERE / 'interface.py'
    planner_file = PROJECT / 'variants/evidence_scope_planner/v2_offline/scope_planner.py'
    adapter = load_module('offline_v4_adapter', adapter_file)
    planner = load_module('offline_v2_planner', planner_file)
    adapter_sha = sha256_bytes(adapter_file.read_bytes())
    planner_sha = sha256_bytes(planner_file.read_bytes())
    out = []
    for name in CASES:
        file = run / f'{name}.json'
        raw = file.read_bytes()
        artifact = json.loads(raw)
        out.append(make_safe_result(artifact, sha256_bytes(raw), adapter_sha, planner_sha, adapter, planner))
    target.mkdir(exist_ok=False)
    for entry in out:
        (target / (entry['case_id'] + '.json')).write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {'status': 'completed_offline', 'model_calls': 0, 'case_count': len(out),
               'original_manifest_sha256': sha256_bytes((run / 'manifest.json').read_bytes()),
               'adapter_sha256': adapter_sha, 'planner_sha256': planner_sha,
               'cases': [{'case_id': x['case_id'], 'status': x['status']} for x in out]}
    (target / 'manifest.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__':
    main()
