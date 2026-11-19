import copy
import json
import unittest

import test_relation_judge as fixture
import relation_judge_v2 as v2


class ControlledV2Tests(unittest.TestCase):
    def run_case(self, data, response):
        calls = []
        result = v2.judge(data, lambda payload: calls.append(payload) or json.dumps(response, ensure_ascii=False))
        self.assertEqual(len(calls), 1)
        return result['results'][0]

    def test_unique_case_recovery_preserves_raw_and_location(self):
        data = fixture.request()
        data['split_result']['memory_text'] = 'Previously worked here.'
        fact = data['split_result']['facts'][0]
        fact.update(raw_subfact='Previously worked here.', contextualized_subfact='Previously worked here.')
        fact['evidence'][0]['quote'] = 'Previously worked here.'
        answer = fixture.answer()
        answer.update(old_subfact=fact['raw_subfact'], old_quote=fact['raw_subfact'], candidate_impact_fragment='previously worked')
        row = self.run_case(data, answer)
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['candidate']['candidate_impact_fragment'], 'previously worked')
        self.assertEqual(row['located_candidate']['candidate_impact_fragment'], 'Previously worked')
        self.assertEqual(row['fragment_match'], {'raw':'previously worked', 'located':'Previously worked', 'method':'unique_casefold', 'start':0, 'end':17})

    def test_case_recovery_rejects_multiple_occurrences_in_entire_memory(self):
        data = fixture.request()
        data['split_result']['memory_text'] = 'Director then DIRECTOR.'
        fact = data['split_result']['facts'][0]
        fact['evidence'][0]['quote'] = 'Director then DIRECTOR.'
        answer = fixture.answer()
        answer.update(old_quote='Director', candidate_impact_fragment='director')
        row = self.run_case(data, answer)
        self.assertEqual(row['status'], 'error')
        self.assertEqual(row['errors'][0]['stage'], 'validation')
        self.assertEqual(row['fragment_match']['method'], 'ambiguous_casefold')
        self.assertIsNone(row['fragment_match']['located'])

    def test_unique_match_outside_fact_evidence_is_rejected(self):
        data = fixture.request()
        data['split_result']['memory_text'] = 'Other. Director.'
        data['split_result']['facts'][0]['evidence'][0]['quote'] = 'Other.'
        answer = fixture.answer()
        answer.update(old_quote='Other.', candidate_impact_fragment='director')
        row = self.run_case(data, answer)
        self.assertEqual(row['status'], 'error')
        self.assertEqual(row['fragment_match']['method'], 'outside_fact_evidence')

    def test_exact_fragment_and_new_quote_are_kept_separate(self):
        data = fixture.request()
        row = self.run_case(data, fixture.answer())
        self.assertEqual(row['status'], 'ok')
        self.assertEqual(row['fragment_match']['method'], 'exact')
        answer = fixture.answer()
        answer['candidate_impact_fragment'] = '用户现在住在上海。'
        row = self.run_case(data, answer)
        self.assertEqual(row['status'], 'error')
        self.assertEqual(row['fragment_match']['method'], 'not_found')

    def test_unchanged_strict_new_quote_and_failure_is_not_uncertain(self):
        answer = fixture.answer()
        answer['new_quote']['quote'] = '用户住在北京。'
        row = self.run_case(fixture.request(), answer)
        self.assertEqual(row['status'], 'error')
        self.assertEqual(row['errors'][0]['stage'], 'validation')
        self.assertEqual(row['candidate']['relation'], 'possible_change')
        result = v2.judge(fixture.request(), lambda _: 'not JSON')
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'parse')
        self.assertIsNone(result['results'][0]['candidate'])

    def test_unicode_casefold_and_non_case_changes(self):
        match = v2.locate_fragment('Straße', 'STRAẞE', ['Straße'])
        self.assertEqual((match['located'], match['method']), ('Straße', 'unique_casefold'))
        match = v2.locate_fragment('A B', 'a  b', ['A B'])
        self.assertEqual(match['method'], 'not_found')
        self.assertIsNone(match['located'])

if __name__ == '__main__':
    unittest.main()
