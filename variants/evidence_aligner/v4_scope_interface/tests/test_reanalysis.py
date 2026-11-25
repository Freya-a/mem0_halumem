import unittest
from reanalysis import make_safe_result


class FakeInterface:
    def validate_output(self, parsed, payload):
        return {'status': 'passed'}
    def planner_inputs(self, payload, parsed):
        return ('old', [], [], [{'semantic_support': 'unknown'}])


class FakePlanner:
    def build_scope_plan(self, *args):
        return {'uncertain': [{'reason': 'semantic_support unknown'}]}


class ReanalysisTests(unittest.TestCase):
    def test_safe_analysis_keeps_initial_result_and_uses_new_projection(self):
        a = {'case_id': 'sample', 'raw_response': '{"records":[]}', 'prepared_input': {},
             'result': {'parsed': {'records': []}, 'plan': {'preserve': ['original']}}}
        out = make_safe_result(a, 'filehash', 'adapterhash', 'plannerhash', FakeInterface(), FakePlanner())
        self.assertEqual(out['initial_plan'], {'preserve': ['original']})
        self.assertEqual(out['safe_plan']['uncertain'][0]['reason'], 'semantic_support unknown')
        self.assertEqual(out['provenance']['adapter_sha256'], 'adapterhash')
        self.assertFalse(out['model_call'])

    def test_reanalysis_does_not_grant_review_or_ignore_changed_response(self):
        class Unsafe(FakeInterface):
            def planner_inputs(self, payload, parsed):
                return ('old', [], [], [{'semantic_support': 'supported'}])
        a = {'case_id': 'x', 'raw_response': '{"records":[]}', 'prepared_input': {}, 'result': {'parsed': {'records': []}}}
        with self.assertRaises(ValueError): make_safe_result(a, 'a','b','c', Unsafe(), FakePlanner())
        a['raw_response'] = '{"records":[1]}'
        with self.assertRaises(ValueError): make_safe_result(a, 'a','b','c', FakeInterface(), FakePlanner())

    def test_missing_response_does_not_create_fake_plan(self):
        out = make_safe_result({'case_id':'x','raw_response':None,'result':None}, 'a','b','c', FakeInterface(), FakePlanner())
        self.assertEqual(out['status'], 'no_parsed_response')
        self.assertIsNone(out['safe_plan'])

if __name__ == '__main__': unittest.main()
