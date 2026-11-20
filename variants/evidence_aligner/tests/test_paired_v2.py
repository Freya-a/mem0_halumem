import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import run_alignment_v2
except ModuleNotFoundError as exc:
    if exc.name != 'run_alignment_v2':
        raise
    run_alignment_v2 = None


class PairedReplayTests(unittest.TestCase):
    def test_runner_exists(self):
        self.assertIsNotNone(run_alignment_v2, 'paired v2 runner must be implemented')

    @unittest.skipIf(run_alignment_v2 is None, 'implementation not yet available')
    def test_all_five_inputs_and_exact_user_messages_match_saved_v1(self):
        pairs = run_alignment_v2.load_paired_cases()
        self.assertEqual([p['input']['case_id'] for p in pairs],
                         ['susan', 'promotion', 'career_history', 'transition', 'skydiving'])
        for pair in pairs:
            checks = run_alignment_v2.verify_pair(pair['v1'], pair['input'])
            self.assertTrue(checks['all_equal'])
            self.assertEqual(checks['v1_user_content_sha256'], checks['v2_user_content_sha256'])
            self.assertEqual(checks['v1_input_sha256'], checks['v2_input_sha256'])

    @unittest.skipIf(run_alignment_v2 is None, 'implementation not yet available')
    def test_changed_unit_or_source_fails_pairing_before_any_call(self):
        pair = run_alignment_v2.load_paired_cases()[0]
        changed = copy.deepcopy(pair['input'])
        changed['new_units'][0]['raw_statement'] += ' changed'
        with self.assertRaises(ValueError):
            run_alignment_v2.verify_pair(pair['v1'], changed)
        changed = copy.deepcopy(pair['input'])
        changed['source_texts']['messages'][0]['text'] += ' changed'
        with self.assertRaises(ValueError):
            run_alignment_v2.verify_pair(pair['v1'], changed)

    @unittest.skipIf(run_alignment_v2 is None, 'implementation not yet available')
    def test_usage_preserves_provider_fields_and_missing_usage(self):
        usage = {'prompt_tokens': 12, 'completion_tokens': 34, 'total_tokens': 46,
                 'prompt_tokens_details': {'cached_tokens': 3}}
        self.assertEqual(run_alignment_v2.get_usage({'usage': usage}), usage)
        self.assertIsNone(run_alignment_v2.get_usage({'choices': []}))


if __name__ == '__main__':
    unittest.main()
