import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import run_alignment_v3
except ModuleNotFoundError as exc:
    if exc.name != 'run_alignment_v3':
        raise
    run_alignment_v3 = None


class PairedV3Tests(unittest.TestCase):
    def test_runner_exists(self):
        self.assertIsNotNone(run_alignment_v3, 'v3 paired runner has not yet been implemented')

    @unittest.skipIf(run_alignment_v3 is None, 'v3 runner missing')
    def test_all_five_inputs_and_user_messages_match_both_previous_runs(self):
        cases = run_alignment_v3.load_paired_cases()
        self.assertEqual([p['input']['case_id'] for p in cases],
                         ['susan', 'promotion', 'career_history', 'transition', 'skydiving'])
        for pair in cases:
            self.assertTrue(pair['input_validation']['all_equal'])
            self.assertEqual(pair['input_validation']['v1_input_sha256'], pair['input_validation']['v2_input_sha256'])
            self.assertEqual(pair['input_validation']['v2_user_content_sha256'], pair['input_validation']['v3_user_content_sha256'])

    @unittest.skipIf(run_alignment_v3 is None, 'v3 runner missing')
    def test_changed_v2_user_message_or_input_is_rejected(self):
        pair = run_alignment_v3.load_paired_cases()[0]
        changed = copy.deepcopy(pair['v2'])
        changed['request']['messages'][1]['content'] += ' '
        with self.assertRaises(ValueError):
            run_alignment_v3.verify_pair(pair['v1'], changed, pair['input'])
        changed = copy.deepcopy(pair['v2'])
        changed['input']['new_units'][0]['raw_statement'] += ' changed'
        with self.assertRaises(ValueError):
            run_alignment_v3.verify_pair(pair['v1'], changed, pair['input'])

    @unittest.skipIf(run_alignment_v3 is None, 'v3 runner missing')
    def test_five_cases_called_once_and_saved_with_raw_response_and_usage(self):
        cases = run_alignment_v3.load_paired_cases()
        calls = []
        class Backend:
            provider_response = None
            def __call__(self, messages):
                calls.append(messages)
                self.provider_response = {'model': run_alignment_v3.MODEL,
                                          'usage': {'prompt_tokens': 3, 'completion_tokens': 2, 'total_tokens': 5}}
                return {'model': run_alignment_v3.MODEL,
                        'content': '{"records": [], "unmatched_old_unit_ids": []}'}
            def close(self):
                pass
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / 'run'
            manifest = run_alignment_v3.run_paired(cases, run, backend_factory=Backend)
            self.assertEqual(len(calls), 5)
            self.assertEqual(manifest['request_attempts'], 5)
            self.assertEqual(manifest['model_responses'], 5)
            for pair in cases:
                artifact = json.loads((run / (pair['input']['case_id'] + '.json')).read_text())
                self.assertEqual(artifact['call']['attempts'], 1)
                self.assertEqual(artifact['raw_response'], '{"records": [], "unmatched_old_unit_ids": []}')
                self.assertEqual(artifact['usage']['total_tokens'], 5)
                self.assertEqual(artifact['input'], pair['input'])
            with self.assertRaises(FileExistsError):
                run_alignment_v3.run_paired(cases, run, backend_factory=Backend)
            self.assertEqual(len(calls), 5)


if __name__ == '__main__':
    unittest.main()
