import importlib
import json
import unittest

import test_relation_judge as fixtures


class ImprovedContractTests(unittest.TestCase):
    def test_mixed_candidate_passes_existing_contract_without_semantic_claim(self):
        try:
            judge = importlib.import_module('relation_judge_v4')
        except ModuleNotFoundError:
            self.fail('independent improved judge is missing')
        answer = fixtures.answer()
        answer.update(relation='uncertain', reason='已有内容受支持；另外有新增信息。',
                      confirmation_questions=['如何分别记录支持和新增信息？'])
        calls = []
        result = judge.judge(fixtures.request(), lambda p: calls.append(p) or json.dumps(answer, ensure_ascii=False))
        self.assertEqual(len(calls), 1)
        row = result['results'][0]
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['located_candidate'], answer)
        self.assertEqual(row['validation']['semantic_correctness'], 'not_checked')

    def test_invalid_quote_remains_an_error_without_retry(self):
        try:
            judge = importlib.import_module('relation_judge_v4')
        except ModuleNotFoundError:
            self.fail('independent improved judge is missing')
        answer = fixtures.answer()
        answer['new_quote']['quote'] = '不存在的引文'
        calls = []
        result = judge.judge(fixtures.request(), lambda p: calls.append(p) or json.dumps(answer, ensure_ascii=False))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'validation')
        self.assertEqual(result['results'][0]['status'], 'error')

if __name__ == '__main__':
    unittest.main()
