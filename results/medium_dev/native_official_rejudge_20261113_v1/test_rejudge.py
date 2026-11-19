import copy
import unittest

import rejudge


class RejudgeTest(unittest.TestCase):
    def test_original_inputs_match_exactly_seven_unique_invalid_records(self):
        baseline, cases = rejudge.load_cases()
        self.assertEqual([c['kind'] for c in cases].count('accuracy'), 6)
        self.assertEqual([c['kind'] for c in cases].count('update'), 1)
        self.assertEqual(len({(c['section'], c['record_index']) for c in cases}), 7)
        self.assertEqual(cases[-1]['input_index'], 3)
        self.assertEqual(len(cases[-1]['args'][0].splitlines()), 10)

    def test_merge_preserves_invalid_and_other_while_replacing_valid(self):
        baseline, cases = rejudge.load_cases()
        original = copy.deepcopy(baseline)
        results = [{'status': 'error'} for _ in cases]
        results[0] = {'status': 'valid', 'normalized': {'accuracy_score': 2, 'is_included_in_golden_memories': 'true'}}
        results[-1] = {'status': 'valid', 'normalized': {'evaluation_result': 'Other'}}
        merged = rejudge.merge_results(baseline, cases, results)
        self.assertEqual(baseline, original)
        self.assertEqual(merged[cases[0]['section']][cases[0]['record_index']]['memory_accuracy_score'], 2)
        self.assertIsNone(merged[cases[1]['section']][cases[1]['record_index']]['memory_accuracy_score'])
        self.assertEqual(sum(x['memory_update_type'] == 'Other' for x in merged['memory_update_records']), 2)
        self.assertEqual(sum(x['memory_update_type'] is None for x in merged['memory_update_records']), 0)


if __name__ == '__main__':
    unittest.main()
