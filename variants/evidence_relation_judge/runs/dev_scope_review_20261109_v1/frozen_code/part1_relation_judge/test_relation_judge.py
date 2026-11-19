import copy
import json
import unittest

import relation_judge as r


def request():
    return {"split_result": {"memory_id": "m1", "memory_text": "用户住在北京。", "facts": [{"fact_index": 1, "source_memory_id": "m1", "raw_subfact": "用户住在北京。", "contextualized_subfact": "用户住在北京。", "evidence": [{"source_type": "memory", "source_id": "m1", "quote": "用户住在北京。", "supports": "原文"}], "pending_confirmations": []}]}, "source_context": [], "new_evidence": [{"source_id": "n1", "text": "用户现在住在上海。"}], "time_info": None}


def answer():
    return {"memory_id": "m1", "fact_index": 1, "old_subfact": "用户住在北京。", "relation": "possible_change", "object": "用户", "attribute": "住所", "conditions": "现在", "candidate_impact_fragment": "住在北京", "old_quote": "用户住在北京。", "new_quote": {"source_id": "n1", "quote": "用户现在住在上海。"}, "reason": "地点不同，可能发生变化。", "confirmation_questions": []}


class Tests(unittest.TestCase):
    def test_valid_candidate_and_one_call(self):
        calls = []
        result = r.judge(request(), lambda payload: calls.append(payload) or json.dumps(answer(), ensure_ascii=False))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['results'][0]['status'], 'ok')
        self.assertEqual(result['results'][0]['candidate'], answer())
        self.assertTrue(result['results'][0]['validation']['passed'])

    def test_invalid_model_output_recorded_without_retry(self):
        for raw in ['no json', json.dumps({**answer(), 'relation': 'false'}), json.dumps({**answer(), 'fact_index': 2}), json.dumps({**answer(), 'old_quote': '上海'}), json.dumps({**answer(), 'new_quote': {'source_id':'n1','quote':'北京'}})]:
            calls = []
            result = r.judge(request(), lambda payload: calls.append(payload) or raw)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result['results'][0]['status'], 'error')
            self.assertEqual(result['results'][0]['raw_output'], raw)
            self.assertTrue(result['results'][0]['errors'])

    def test_backend_error_and_invalid_input(self):
        def fail(_):
            raise RuntimeError('model unavailable')
        result = r.judge(request(), fail)
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'model')
        bad = request()
        bad['split_result']['facts'][0]['evidence'][0]['quote'] = '不存在'
        result = r.judge(bad, lambda _: self.fail('invalid input called model'))
        self.assertEqual(result['status'], 'input_error')

    def test_uncertain_requires_question_and_quote_provenance(self):
        bad = answer()
        bad.update(relation='uncertain', confirmation_questions=[])
        result = r.judge(request(), lambda _: json.dumps(bad))
        self.assertEqual(result['results'][0]['status'], 'error')
        bad = answer()
        bad['candidate_impact_fragment'] = '上海'
        result = r.judge(request(), lambda _: json.dumps(bad))
        self.assertEqual(result['results'][0]['status'], 'error')

    def test_missing_new_quote_is_rejected(self):
        bad = answer()
        bad['new_quote'] = {'source_id': '', 'quote': ''}
        result = r.judge(request(), lambda _: json.dumps(bad))
        self.assertEqual(result['results'][0]['status'], 'error')
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'validation')

    def test_failed_fact_does_not_hide_next_fact(self):
        data = request()
        second = copy.deepcopy(data['split_result']['facts'][0])
        second['fact_index'] = 2
        data['split_result']['facts'].append(second)
        calls = []
        def backend(payload):
            calls.append(payload['fact']['fact_index'])
            if payload['fact']['fact_index'] == 1:
                raise RuntimeError('failed first')
            return json.dumps({**answer(), 'fact_index': 2})
        result = r.judge(data, backend)
        self.assertEqual(calls, [1, 2])
        self.assertEqual([x['status'] for x in result['results']], ['error', 'ok'])

    def test_duplicate_fact_ids_rejected_before_call(self):
        data = request()
        data['split_result']['facts'].append(copy.deepcopy(data['split_result']['facts'][0]))
        self.assertEqual(r.judge(data, lambda _: self.fail('called'))['status'], 'input_error')

if __name__ == '__main__':
    unittest.main()
