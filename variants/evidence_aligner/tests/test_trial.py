import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    import run_alignment_trial
    import qwen_backend
except ModuleNotFoundError as exc:
    if exc.name not in {'run_alignment_trial', 'qwen_backend'}:
        raise
    run_alignment_trial = qwen_backend = None


class TrialTests(unittest.TestCase):
    def test_trial_module_exists(self):
        self.assertIsNotNone(run_alignment_trial, 'the five-case trial must be implemented')

    @unittest.skipIf(run_alignment_trial is None, 'implementation not yet available')
    def test_fixed_cases_preserve_all_selected_sources_and_full_round(self):
        cases = run_alignment_trial.load_cases()
        self.assertEqual([case['case_id'] for case in cases],
                         ['susan', 'promotion', 'career_history', 'transition', 'skydiving'])
        for case in cases:
            selected = set(case['provenance']['selected_new_source_ids'])
            self.assertTrue(selected <= {u['source_id'] for u in case['new_units']})
            self.assertGreater(len(case['source_texts']['messages']), len(selected))
            self.assertIn('assistant', {m['speaker'] for m in case['source_texts']['messages']})
        sky = cases[-1]
        self.assertEqual([u['unit_id'] for u in sky['old_units']], ['u1', 'u2', 'u3'])
        self.assertEqual(sky['provenance']['old_unit_origin'], 'simplemem_prompt_v2')

    @unittest.skipIf(qwen_backend is None, 'implementation not yet available')
    def test_request_uses_json_temperature_zero_once(self):
        calls = []
        class Completions:
            def create(self, **kwargs):
                calls.append(kwargs)
                class Msg:
                    content = '{"records":[]}'
                class Choice:
                    message = Msg()
                    finish_reason = 'stop'
                class Response:
                    model = 'qwen-plus-2025-12-01'
                    choices = [Choice()]
                    def model_dump(self, **kwargs):
                        return {'model': self.model}
                return Response()
        class Client:
            class chat:
                completions = Completions()
        backend = qwen_backend.QwenBackend(client=Client())
        response = backend([{'role': 'user', 'content': 'test'}])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['model'], 'qwen-plus-2025-12-01')
        self.assertEqual(calls[0]['temperature'], 0)
        self.assertEqual(calls[0]['response_format'], {'type': 'json_object'})
        self.assertEqual(response['content'], '{"records":[]}')

    @unittest.skipIf(qwen_backend is None, 'implementation not yet available')
    def test_sdk_automatic_retries_are_disabled(self):
        class Http:
            def close(self):
                pass
        with patch('qwen_backend.dotenv_values', return_value={'DASHSCOPE_API_KEY': 'test-key',
                                                                'DASHSCOPE_WORKSPACE_ID': 'ws-test'}), \
             patch('qwen_backend.create_http_client', return_value=Http()), \
             patch('qwen_backend.OpenAI') as client_factory:
            backend = qwen_backend.QwenBackend()
            self.assertEqual(client_factory.call_args.kwargs['max_retries'], 0)
            backend.close()


if __name__ == '__main__':
    unittest.main()
