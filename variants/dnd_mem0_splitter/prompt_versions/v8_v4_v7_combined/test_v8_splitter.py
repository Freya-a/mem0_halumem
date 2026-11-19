import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('dnd_v8_splitter', HERE / 'v8_splitter.py')
v8 = importlib.util.module_from_spec(spec) if spec.loader and (HERE / 'v8_splitter.py').exists() else None
if v8:
    spec.loader.exec_module(v8)


class SplitterV8Tests(unittest.TestCase):
    def setUp(self):
        self.request = {'memory_id': 'm1', 'memory_text': '偏好素色杯子，也喜欢茶。',
                        'source_context': [{'source_id': 'c1', 'source_ref': 'chat/1',
                                            'text': '我偏好素色杯子，也喜欢茶。', 'speaker': 'user'}]}
        self.response = {'facts': [
            {'fact_index': 1, 'source_memory_id': 'm1', 'raw_subfact': '偏好素色杯子',
             'contextualized_subfact': '用户偏好素色杯子',
             'evidence': [{'source_type': 'memory', 'source_id': 'm1', 'quote': '偏好素色杯子', 'supports': '记忆中的偏好'},
                          {'source_type': 'context', 'source_id': 'c1', 'quote': '我偏好素色杯子', 'supports': '用于指代消歧'}],
             'pending_confirmations': []},
            {'fact_index': 2, 'source_memory_id': 'm1', 'raw_subfact': '喜欢茶',
             'contextualized_subfact': '用户喜欢茶',
             'evidence': [{'source_type': 'memory', 'source_id': 'm1', 'quote': '喜欢茶', 'supports': '记忆中的偏好'},
                          {'source_type': 'context', 'source_id': 'c1', 'quote': '我偏好素色杯子，也喜欢茶', 'supports': '用于指代消歧'}],
             'pending_confirmations': []}]}

    def test_cli_sends_fixed_model_despite_file_and_environment_settings(self):
        import httpx
        from openai import OpenAI
        import real_backend

        requests = []
        def handler(request):
            requests.append(json.loads(request.content))
            return httpx.Response(200, json={
                'id': 'test', 'object': 'chat.completion', 'created': 1,
                'model': 'qwen-plus-2025-12-01',
                'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': '{"facts": []}'},
                             'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2},
            })

        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            input_path, env_path = temp_path / 'input.json', temp_path / 'config.env'
            input_path.write_text(json.dumps(self.request, ensure_ascii=False), encoding='utf-8')
            env_path.write_text('LLM_MODEL=file-model\nLLM_API_KEY=test-key\n'
                                'LLM_BASE_URL=https://offline.invalid/v1\n', encoding='utf-8')
            client = OpenAI(api_key='test-key', base_url='https://offline.invalid/v1', max_retries=0,
                            http_client=httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False))
            self.addCleanup(client.close)
            backend_class = real_backend.OpenAICompatibleBackend
            with patch.dict(os.environ, {'LLM_MODEL': 'env-model', 'OPENAI_MODEL': 'other-model'}, clear=True), \
                 patch.object(real_backend, 'OpenAICompatibleBackend',
                              side_effect=lambda settings, prompt: backend_class(settings, prompt, client=client)), \
                 patch('sys.stdout'):
                self.assertEqual(v8.main(['--input', str(input_path), '--env-file', str(env_path)]), 0)
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]['model'], 'qwen-plus-2025-12-01')

    def test_joint_output_passes_pair_and_context_to_baseline_schema(self):
        self.assertIsNotNone(v8, 'v8 implementation is missing')
        seen = []
        def factory(prompt):
            def backend(request):
                seen.append((prompt, request))
                return copy.deepcopy(self.response)
            return backend
        result = v8.split_memory_v8(self.request, factory)
        self.assertEqual([(f['raw_subfact'], f['contextualized_subfact']) for f in result['facts']],
                         [('偏好素色杯子', '用户偏好素色杯子'), ('喜欢茶', '用户喜欢茶')])
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][1], self.request)
        self.assertIn('raw_subfact', seen[0][0])
        self.assertIn('contextualized_subfact', seen[0][0])

    def test_invalid_context_quote_is_rejected(self):
        self.assertIsNotNone(v8, 'v8 implementation is missing')
        self.response['facts'][0]['evidence'][1]['quote'] = '我……杯子'
        with self.assertRaises(v8.ValidationError) as caught:
            v8.split_memory_v8(self.request, lambda prompt: lambda request: self.response)
        self.assertEqual(caught.exception.code, 'quote_not_found')

    def test_new_evidence_cannot_be_used_as_disambiguation_input(self):
        self.assertIsNotNone(v8, 'v8 implementation is missing')
        request = dict(self.request, new_evidence=[{'source_id': 'n', 'text': '用户喜欢花杯'}])
        with self.assertRaises(v8.ValidationError) as caught:
            v8.split_memory_v8(request, lambda prompt: lambda request: self.response)
        self.assertEqual(caught.exception.code, 'unexpected_field')

    def test_split_result_is_accepted_by_relation_judge_v2(self):
        self.assertIsNotNone(v8, 'v8 implementation is missing')
        import json
        import sys
        relation_dir = HERE.parents[2] / 'evidence_relation_judge' / 'part1_relation_judge'
        sys.path.insert(0, str(relation_dir))
        import relation_judge_v2
        split = v8.split_memory_v8(self.request, lambda prompt: lambda _: self.response)
        data = {'split_result': split, 'source_context': self.request['source_context'],
                'new_evidence': [{'source_id': 'n1', 'text': '用户也喜欢茶。'}]}
        def judge_backend(payload):
            fact = payload['fact']
            old_quote = fact['evidence'][0]['quote']
            return json.dumps({'memory_id': 'm1', 'fact_index': fact['fact_index'],
                'old_subfact': fact['raw_subfact'], 'relation': 'uncertain',
                'object': '', 'attribute': '', 'conditions': '',
                'candidate_impact_fragment': old_quote, 'old_quote': old_quote,
                'new_quote': {'source_id': 'n1', 'quote': '用户也喜欢茶'},
                'reason': '需要进一步比较', 'confirmation_questions': ['是否对应？']}, ensure_ascii=False)
        result = relation_judge_v2.judge(data, judge_backend)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['results']), 2)
        self.assertTrue(all(row['validation']['passed'] for row in result['results']))

    def test_no_context_may_leave_a_claim_unresolved(self):
        self.assertIsNotNone(v8, 'v8 implementation is missing')
        request = {'memory_id': 'm1', 'memory_text': '偏好素色杯子。'}
        fact = copy.deepcopy(self.response['facts'][0])
        fact['contextualized_subfact'] = fact['raw_subfact']
        fact['evidence'] = fact['evidence'][:1]
        fact['pending_confirmations'] = [{'item': '主体', 'reason': '旧记忆未说明'}]
        result = v8.split_memory_v8(request, lambda prompt: lambda _: {'facts': [fact]})
        self.assertEqual(result['facts'][0]['pending_confirmations'][0]['item'], '主体')


if __name__ == '__main__':
    unittest.main()
