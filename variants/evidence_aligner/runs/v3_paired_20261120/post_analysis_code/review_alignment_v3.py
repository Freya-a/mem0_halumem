"""Combine deterministic structure checks with separately supplied semantic review.

This does not change saved model responses or make semantic decisions automatically.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from run_alignment_trial import _read, _save


def summarize_case(case_id, result, review):
    findings = review.get('findings', []) if isinstance(review, dict) else []
    semantic_errors = [f for f in findings if f.get('judgment') == 'error']
    accepted = {'error', 'supported', 'supported_with_limits'}
    needs_review = [f for f in findings if f.get('judgment') not in accepted]
    reviewed = isinstance(review, dict)
    coverage = result.get('coverage', {})
    unhandled = any(coverage.get('unhandled_' + side + '_unit_ids') for side in ('old', 'new'))
    attention = (not reviewed or result.get('status') != 'passed' or semantic_errors or needs_review
                 or result.get('missing_evidence') or result.get('ambiguities') or unhandled)
    return {'case_id': case_id, 'structural_status': result.get('status'),
            'structure_errors': result.get('structure_errors', []),
            'parse_errors': result.get('parse_errors', []),
            'semantic_review_status': 'reviewed_nonblind' if reviewed else 'not_reviewed',
            'semantic_errors': semantic_errors, 'human_judgment_needed': needs_review,
            'other_semantic_findings': [f for f in findings if f.get('judgment') in {'supported', 'supported_with_limits'}],
            'missing_evidence': result.get('missing_evidence', []), 'coverage': coverage,
            'ambiguities': result.get('ambiguities', []), 'scope_review': result.get('scope_review', []),
            'source_completion_count': len(result.get('source_completions', [])),
            'overall_status': 'requires_attention' if attention else 'reviewed_without_identified_errors'}


def collect_review(run_dir):
    run = Path(run_dir)
    manifest = _read(run / 'manifest.json')
    audit = _read(run / 'semantic_audit.json')
    reviews = {}
    for case in audit.get('cases', []):
        uid = case['case_id']
        if uid in reviews:
            raise ValueError(f'duplicate semantic review: {uid}')
        reviews[uid] = case
    cases = []
    for item in manifest['cases']:
        uid = item['case_id']
        artifact = _read(run / (uid + '.json'))
        if artifact.get('result') is None:
            raise ValueError(f'case has no result: {uid}')
        cases.append(summarize_case(uid, artifact['result'], reviews.pop(uid, None)))
    if reviews:
        raise ValueError('semantic review contains unknown case IDs')
    structure_counts = Counter(error['code'] for case in cases for error in case['structure_errors'])
    semantic_counts = Counter(finding['type'] for case in cases for finding in case['semantic_errors'])
    return {'review_method': audit.get('method'), 'source_manifest': 'manifest.json',
            'source_semantic_audit': 'semantic_audit.json',
            'summary': {'case_count': len(cases), 'structure_error_counts': dict(sorted(structure_counts.items())),
                        'semantic_error_counts': dict(sorted(semantic_counts.items())),
                        'semantic_error_findings': sum(semantic_counts.values()),
                        'cases_requiring_attention': sum(c['overall_status'] == 'requires_attention' for c in cases)},
            'cases': cases}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    args = parser.parse_args()
    bundle = collect_review(args.run_dir)
    _save(args.run_dir / 'reviewed_results.json', bundle)
    print(bundle['summary'])


if __name__ == '__main__':
    main()
