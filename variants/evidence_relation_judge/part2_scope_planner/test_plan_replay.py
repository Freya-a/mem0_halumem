import copy
import unittest

from plan_replay import replay_three, replay_development
from replay import load_case


class PlanReplayTests(unittest.TestCase):
    def test_three_group_outputs_are_distinct_and_safe(self):
        result = replay_three()
        self.assertEqual(set(result), {'promotion','job_transition','synthetic_wednesday_01'})
        for item in result.values():
            self.assertEqual(set(item), {'structured','baseline_only'})
            for plan in item.values():
                self.assertFalse(plan['modify'])
                self.assertTrue(plan['uncertain'])
                self.assertTrue(plan['add'])
        structured = result['synthetic_wednesday_01']['structured']
        self.assertTrue(any(x['code']=='residual_preserve' for x in structured['preserve']))
        baseline = result['synthetic_wednesday_01']['baseline_only']
        self.assertTrue(all(x['attribute'] is None for x in baseline['preserve']))
        self.assertTrue(any(x['code']=='support_not_change' for x in result['job_transition']['baseline_only']['uncertain']))

    def test_baseline_group_does_not_use_structured_annotations(self):
        from plan_replay import replay_one
        case = load_case('promotion')
        before = replay_one(case)['baseline_only']
        case = copy.deepcopy(case)
        case['old_units'] = []
        case['new_unit']['attribute']['value'] = 'tampered_human_annotation'
        after = replay_one(case)['baseline_only']
        self.assertEqual(before, after)

    def test_development_includes_all_saved_baselines_and_preserves_failures(self):
        report = replay_development()
        self.assertEqual(len(report['rows']), 23)
        self.assertEqual(sum(r['upstream_status'] == 'error' for r in report['rows']), 2)
        self.assertTrue(all(not r['plan']['modify'] for r in report['rows']))
        self.assertEqual(len({r['target_id'] for r in report['rows']}), 21)
        self.assertTrue(any(r['coverage'] == 'partial_reviewed_target' for r in report['rows']))

    def test_scoring_is_posthoc_and_exposes_withheld_changes(self):
        from score_plan import score
        result = score()
        self.assertEqual(result['checks_passed'], result['check_count'])
        self.assertTrue(all(x['target_change_not_emitted'] for x in result['rows']))


if __name__ == '__main__': unittest.main()
