import importlib
import json
import unittest
import test_relation_judge as fixtures

class MixedGuardTests(unittest.TestCase):
    def test_mixed_relation_is_reported_without_relabeling_as_existing_category(self):
        try:
            judge = importlib.import_module('relation_judge_v5')
        except ModuleNotFoundError:
            self.fail('strict mixed relation guard is missing')
        answer = fixtures.answer()
        answer.update(relation='mixed_unrepresentable', reason='支持旧喜好；另外增加观看纪录片的经历。')
        calls = []
        result = judge.judge(fixtures.request(), lambda p: calls.append(p) or json.dumps(answer, ensure_ascii=False))
        row = result['results'][0]
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['status'], 'partial_or_error')
        self.assertEqual(row['status'], 'error')
        self.assertEqual(row['candidate']['relation'], 'mixed_unrepresentable')
        self.assertEqual(row['mixed_relation']['status'], 'unrepresentable_in_v2_schema')
        self.assertFalse(row['validation']['passed'])
        self.assertEqual(row['validation']['semantic_correctness'], 'not_checked')

    def test_ordinary_candidate_still_passes_v2_contract(self):
        try:
            judge = importlib.import_module('relation_judge_v5')
        except ModuleNotFoundError:
            self.fail('strict mixed relation guard is missing')
        answer = fixtures.answer()
        result = judge.judge(fixtures.request(), lambda p: json.dumps(answer, ensure_ascii=False))
        self.assertEqual(result['results'][0]['status'], 'ok')
        self.assertNotIn('mixed_relation', result['results'][0])

if __name__ == '__main__':
    unittest.main()
