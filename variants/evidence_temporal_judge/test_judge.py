import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge

MEMORY = {"memory_id": "m1", "memory_text": "小李住在北京，喜欢茶。", "source_context": []}
FACTS = {"facts": [{"fact_index": 1, "source_memory_id": "m1", "raw_subfact": "小李住在北京，喜欢茶。", "contextualized_subfact": "小李住在北京，喜欢茶。", "evidence": [{"source_type": "memory", "source_id": "m1", "quote": "小李住在北京，喜欢茶", "supports": "旧记忆"}], "pending_confirmations": []}]}
EVIDENCE = [{"source_id": "new1", "text": "小李去年搬到上海，现在住在上海。"}]


def reply():
    return {"erase_label": "Make False", "applicability": "involved", "temporal_relation": "before_after", "temporal_reason": "旧住址与新住址有先后", "components": [
        {"fragment": "小李住在北京", "action": "modify", "reason": "住址变化", "new_evidence": [{"source_id": "new1", "quote": "现在住在上海"}]},
        {"fragment": "喜欢茶", "action": "protect", "reason": "新证据没有涉及茶", "new_evidence": []}]}


class JudgeTests(unittest.TestCase):
    def test_explicit_v4_splitter_and_partial_impact_provenance(self):
        seen = {}
        def factory(prompt):
            seen['hash'] = hashlib.sha256(prompt.encode()).hexdigest()
            return lambda request: copy.deepcopy(FACTS)
        split = judge.split_with_v4(MEMORY, factory)
        self.assertEqual(split['prompt']['sha256'], 'd9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3')
        self.assertEqual(seen['hash'], split['prompt']['sha256'])
        result = judge.judge(split['result'], MEMORY['source_context'], EVIDENCE, {'note': '去年锚点未提供'}, lambda req: reply(), lambda req: {'candidates': [{'source_id': 'new1', 'quote': '现在住在上海', 'reason': '新的居住信息'}]})
        self.assertEqual(result['facts'][0]['erase_label'], 'Make False')
        self.assertEqual([x['action'] for x in result['facts'][0]['components']], ['modify', 'protect'])
        self.assertEqual(result['facts'][0]['fact']['evidence'][0]['quote'], '小李住在北京，喜欢茶')
        self.assertEqual(result['new_evidence'], EVIDENCE)
        self.assertEqual(result['new_candidates']['candidates'][0]['quote'], '现在住在上海')
        self.assertEqual(result['facts'][0]['temporal_relation'], 'before_after')

    def test_uninvolved_insufficient_and_failure_are_distinct(self):
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **copy.deepcopy(FACTS)}
        def response(applicability):
            return {'erase_label': 'No Change', 'applicability': applicability, 'temporal_relation': 'unclear', 'temporal_reason': '无法判断时间', 'components': [{'fragment': '小李住在北京，喜欢茶。', 'action': 'protect' if applicability == 'uninvolved' else 'confirm', 'reason': applicability, 'new_evidence': []}]}
        candidate = lambda request: {'candidates': []}
        a = judge.judge(split, [], EVIDENCE, None, lambda req: response('uninvolved'), candidate)
        b = judge.judge(split, [], EVIDENCE, None, lambda req: response('insufficient'), candidate)
        c = judge.judge(split, [], EVIDENCE, None, lambda req: (_ for _ in ()).throw(RuntimeError('secret')), candidate)
        self.assertEqual([a['facts'][0]['status'], b['facts'][0]['status'], c['facts'][0]['status']], ['uninvolved', 'insufficient', 'failed'])
        self.assertNotIn('secret', str(c))

    def test_bad_quotes_and_inconsistent_make_false_fail_closed(self):
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **copy.deepcopy(FACTS)}
        bad = reply(); bad['components'][0]['new_evidence'][0]['quote'] = '伪造引文'
        result = judge.judge(split, [], EVIDENCE, None, lambda req: bad, lambda req: {'candidates': []})
        self.assertEqual(result['facts'][0]['status'], 'failed')
        bad = reply(); bad['applicability'] = 'insufficient'
        result = judge.judge(split, [], EVIDENCE, None, lambda req: bad, lambda req: {'candidates': []})
        self.assertEqual(result['facts'][0]['status'], 'failed')

    def test_candidate_errors_and_empty_facts_do_not_look_like_empty_result(self):
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], 'facts': []}
        result = judge.judge(split, [], EVIDENCE, None, lambda req: {}, lambda req: {'candidates': [{'source_id': 'new1', 'quote': '未出现', 'reason': 'x'}]})
        self.assertEqual(result['new_candidates']['status'], 'failed')
        self.assertEqual(result['facts'], [])

    def test_invalid_existing_quote_rejected_before_backend(self):
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **copy.deepcopy(FACTS)}
        split['facts'][0]['evidence'][0]['quote'] = '编造'
        with self.assertRaises(ValueError):
            judge.judge(split, [], EVIDENCE, None, lambda req: reply(), lambda req: {'candidates': []})

    def test_uncovered_part_is_not_silently_dropped(self):
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **copy.deepcopy(FACTS)}
        partial = reply()
        partial['components'].pop()
        result = judge.judge(split, [], EVIDENCE, None, lambda req: partial, lambda req: {'candidates': []})
        self.assertEqual(result['facts'][0]['status'], 'failed')

    def test_existing_splitter_backend_factory_receives_separate_prompt(self):
        seen = []
        def factory(prompt):
            def backend(request):
                seen.append((prompt, request))
                return {'candidates': []}
            return backend
        adapted = judge.adapt_splitter_backend(factory)
        self.assertEqual(adapted({'prompt': 'specific system prompt', 'task': 'example'}), {'candidates': []})
        self.assertEqual(seen, [('specific system prompt', {'task': 'example'})])

    def test_end_to_end_uses_v4_and_carries_prompt_provenance(self):
        result = judge.split_and_judge(MEMORY, EVIDENCE, None,
            lambda prompt: lambda request: copy.deepcopy(FACTS),
            lambda request: reply(), lambda request: {'candidates': []})
        self.assertEqual(result['splitter_prompt']['sha256'], 'd9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3')
        self.assertEqual(result['facts'][0]['status'], 'involved')

    def test_historical_relation_and_failed_fact_are_preserved_independently(self):
        facts = copy.deepcopy(FACTS)
        other = copy.deepcopy(facts['facts'][0])
        other['fact_index'] = 2
        facts['facts'].append(other)
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **facts}
        def backend(request):
            if request['fact']['fact_index'] == 2:
                return 'malformed model output'
            data = reply()
            data['temporal_relation'] = 'historical_compatible'
            data['temporal_reason'] = '两个状态可能分别成立于不同时间'
            data['components'][0]['action'] = 'confirm'
            return data
        result = judge.judge(split, [], EVIDENCE, {'note': '无日期'}, backend, lambda request: {'candidates': []})
        self.assertEqual(result['facts'][0]['temporal_relation'], 'historical_compatible')
        self.assertEqual(result['facts'][1]['status'], 'failed')
        self.assertEqual(result['facts'][1]['fact']['fact_index'], 2)

    def test_existing_openai_compatible_backend_with_offline_transport(self):
        import httpx
        from openai import OpenAI
        sys.path.insert(0, str(judge.SPLITTER_DIR))
        import real_backend
        requests = []
        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            payload = json.loads(body['messages'][1]['content'])
            content = reply() if payload['task'] == 'fact_judgment' else {'candidates': []}
            return httpx.Response(200, json={'id': 'offline', 'object': 'chat.completion', 'created': 1,
                'model': 'fake', 'choices': [{'index': 0, 'message': {'role': 'assistant', 'content': json.dumps(content)}, 'finish_reason': 'stop'}],
                'usage': {'prompt_tokens': 1, 'completion_tokens': 1, 'total_tokens': 2}})
        client = OpenAI(api_key='fake', base_url='https://offline.invalid/v1', max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False))
        self.addCleanup(client.close)
        settings = real_backend.ModelSettings(model='fake', api_key='fake', base_url='https://offline.invalid/v1')
        backend = judge.adapt_splitter_backend(lambda prompt: real_backend.OpenAICompatibleBackend(settings, prompt, client=client))
        split = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **copy.deepcopy(FACTS)}
        result = judge.judge(split, [], EVIDENCE, None, backend, backend)
        self.assertEqual(result['facts'][0]['status'], 'involved')
        self.assertEqual(result['new_candidates']['status'], 'ok')
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]['messages'][0]['content'], judge.JUDGE_PROMPT)
        self.assertEqual(requests[1]['messages'][0]['content'], judge.CANDIDATE_PROMPT)

if __name__ == '__main__':
    unittest.main()
