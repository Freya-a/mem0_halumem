import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
sys.path.insert(0, str(BASE))


def load_v9():
    target = HERE / 'v9_splitter.py'
    if not target.exists():
        return None
    spec = importlib.util.spec_from_file_location('test_v9', target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V9Tests(unittest.TestCase):
    def test_v9_uses_own_prompt_and_existing_quote_validation(self):
        from splitter import ValidationError
        v9 = load_v9()
        self.assertIsNotNone(v9, 'v9 entry is missing')
        seen = []
        request = {'memory_id': 'm', 'memory_text': 'Likes blue cups.'}
        response = {'facts': [{'fact_index': 1, 'source_memory_id': 'm',
                               'raw_subfact': 'Likes blue cups.', 'contextualized_subfact': 'Likes blue cups.',
                               'evidence': [{'source_type': 'memory', 'source_id': 'm',
                                             'quote': 'not in memory', 'supports': 'test'}],
                               'pending_confirmations': []}]}
        def factory(prompt):
            seen.append(prompt)
            return lambda _: response
        with self.assertRaises(ValidationError) as caught:
            v9.split_memory_v9(request, factory)
        self.assertEqual(caught.exception.code, 'quote_not_found')
        self.assertEqual(seen[0], (HERE / 'prompt.txt').read_text())
        self.assertNotEqual(seen[0], (HERE.parent / 'v8_v4_v7_combined' / 'prompt.txt').read_text())

    def test_cli_sends_requested_model_and_thinking_false_without_retry(self):
        import httpx
        from openai import OpenAI
        from unittest.mock import patch
        import real_backend
        import tempfile
        v9 = load_v9()
        self.assertIsNotNone(v9, 'v9 entry is missing')
        calls = []
        def handler(request):
            calls.append(json.loads(request.content))
            return httpx.Response(200, json={'id': 'offline', 'object': 'chat.completion', 'created': 1,
                'model': v9.MODEL, 'choices': [{'index': 0, 'message': {'role': 'assistant',
                'content': '{"facts": []}'}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}})
        client = OpenAI(api_key='offline', base_url='https://offline.invalid/v1', max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False))
        self.addCleanup(client.close)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp/'input.json').write_text('{"memory_id":"m","memory_text":"text"}')
            (tmp/'env').write_text('LLM_MODEL=other\nLLM_API_KEY=offline\nLLM_BASE_URL=https://offline.invalid/v1\n')
            real = real_backend.OpenAICompatibleBackend
            with patch.dict('os.environ', {'LLM_MODEL': 'other'}, clear=True), \
                 patch.object(real_backend, 'OpenAICompatibleBackend', side_effect=lambda s, p: real(s, p, client=client)), \
                 patch('sys.stdout'):
                self.assertEqual(v9.main(['--input', str(tmp/'input.json'), '--env-file', str(tmp/'env')]), 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]['model'], 'qwen-plus-2025-12-01')
        self.assertIs(calls[0]['enable_thinking'], False)
        self.assertEqual(client.max_retries, 0)

if __name__ == '__main__':
    unittest.main()
