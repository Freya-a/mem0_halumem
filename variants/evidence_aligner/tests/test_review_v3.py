import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import review_alignment_v3
except ModuleNotFoundError as exc:
    if exc.name != 'review_alignment_v3':
        raise
    review_alignment_v3 = None


class ReviewTests(unittest.TestCase):
    def test_module_exists(self):
        self.assertIsNotNone(review_alignment_v3, 'semantic and structural review combiner is missing')

    @unittest.skipIf(review_alignment_v3 is None, 'review combiner missing')
    def test_structural_pass_does_not_hide_semantic_error_or_unresolved_review(self):
        result = {'status': 'passed', 'structure_errors': [], 'parse_errors': [],
                  'coverage': {'unhandled_new_unit_ids': []}, 'missing_evidence': [],
                  'ambiguities': [], 'source_completions': []}
        review = {'findings': [
            {'type': 'unsupported_relation', 'judgment': 'error', 'path': 'records[0]'},
            {'type': 'scope', 'judgment': 'needs_human_review', 'path': 'records[1]'}]}
        report = review_alignment_v3.summarize_case('example', result, review)
        self.assertEqual(report['structural_status'], 'passed')
        self.assertEqual(report['overall_status'], 'requires_attention')
        self.assertEqual(report['semantic_errors'][0]['type'], 'unsupported_relation')
        self.assertEqual(report['human_judgment_needed'][0]['type'], 'scope')

    @unittest.skipIf(review_alignment_v3 is None, 'review combiner missing')
    def test_missing_review_stays_unreviewed(self):
        result = {'status': 'passed', 'structure_errors': [], 'parse_errors': [], 'coverage': {},
                  'missing_evidence': [], 'ambiguities': [], 'source_completions': []}
        report = review_alignment_v3.summarize_case('example', result, None)
        self.assertEqual(report['semantic_review_status'], 'not_reviewed')
        self.assertEqual(report['overall_status'], 'requires_attention')

    @unittest.skipIf(review_alignment_v3 is None, 'review combiner missing')
    def test_actual_five_case_review_preserves_errors_and_coverage(self):
        run = Path(__file__).resolve().parents[1] / 'runs' / 'v3_paired_20261120'
        bundle = review_alignment_v3.collect_review(run)
        self.assertEqual(len(bundle['cases']), 5)
        by_id = {case['case_id']: case for case in bundle['cases']}
        self.assertEqual(by_id['career_history']['structural_status'], 'passed')
        self.assertGreaterEqual(len(by_id['career_history']['semantic_errors']), 2)
        self.assertGreaterEqual(len(by_id['susan']['structure_errors']), 1)
        self.assertIn('unhandled_new_unit_ids', by_id['susan']['coverage'])


if __name__ == '__main__':
    unittest.main()
