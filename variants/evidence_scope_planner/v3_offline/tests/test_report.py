import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from make_report import digest, range_review, count


class ReportTests(unittest.TestCase):
    def test_review_must_match_current_plan_hash(self):
        plan = {'modify': [], 'preserve': [], 'uncertain': [{'reason':'未确认'}], 'add': []}
        audit = {'case': {'guarded': {'v3': {'plan_sha256': digest(plan), 'verdict':'reviewed', 'reason':'人工检查'}}}}
        self.assertEqual(range_review(audit, 'case', 'guarded', 'v3', plan)['verdict'], 'reviewed')
        plan['uncertain'].append({'reason':'new'})
        self.assertEqual(range_review(audit, 'case', 'guarded', 'v3', plan)['verdict'], 'not_reviewed')
        self.assertEqual(count(plan), '0/0/2/0')

if __name__=='__main__':
    unittest.main()
