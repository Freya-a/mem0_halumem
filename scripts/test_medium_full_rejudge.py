import copy
import importlib.util
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).parent))
path = Path(__file__).with_name('medium_full_rejudge.py')
if path.exists():
    spec = importlib.util.spec_from_file_location('medium_full_rejudge', path)
    rejudge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rejudge)
else:
    rejudge = None


class RejudgeTests(unittest.TestCase):
    def test_exists(self):
        self.assertIsNotNone(rejudge)

    @unittest.skipIf(rejudge is None, 'not implemented')
    def test_jobs_only_include_invalid_records(self):
        baseline = {'memory_integrity_records': [{'is_valid': True}, {'is_valid': False}],
                    'memory_accuracy_records': [{'is_valid': False}],
                    'memory_update_records': [{'is_valid': True}],
                    'question_answering_records': [{'is_valid': False}]}
        self.assertEqual(rejudge.invalid_jobs(baseline), [('memory_integrity_records', 1),
            ('memory_accuracy_records', 0), ('question_answering_records', 0)])

    @unittest.skipIf(rejudge is None, 'not implemented')
    def test_accuracy_arguments_reproduce_official_format(self):
        s = {'dialogue': [{'timestamp':'t','role':'user','content':'u'}, {'timestamp':'t','role':'assistant','content':'a'}],
             'memory_points': [{'memory_source':'primary','memory_content':'gold'}, {'memory_source':'interference','memory_content':'decoy'}],
             'extracted_memories':['candidate']}
        rec={'memory_content':'candidate'}
        self.assertEqual(rejudge.case_args('memory_accuracy_records',rec,s),
                         ('[t]user: u\n[t]assistant: a\n', 'gold', 'candidate'))

    @unittest.skipIf(rejudge is None, 'not implemented')
    def test_merge_only_replaces_successful_scores(self):
        original={'memory_accuracy_records':[{'memory_accuracy_score':None,'is_included_in_golden_memories':'false','is_valid':False},
                                               {'memory_accuracy_score':2,'is_valid':True}]}
        old=copy.deepcopy(original)
        rows=[('memory_accuracy_records',0,json.dumps({'memory_accuracy_score':1,'is_included_in_golden_memories':'true'}))]
        merged=rejudge.merge_scores(original,rows)
        self.assertEqual(original,old)
        self.assertEqual(merged['memory_accuracy_records'][0]['memory_accuracy_score'],1)
        self.assertEqual(merged['memory_accuracy_records'][0]['is_included_in_golden_memories'],'true')
        self.assertEqual(merged['memory_accuracy_records'][1],old['memory_accuracy_records'][1])

    @unittest.skipIf(rejudge is None, 'not implemented')
    def test_rejects_invalid_labels(self):
        with self.assertRaises(ValueError):rejudge.normalize('question_answering_records',{'evaluation_result':'invented'})


if __name__ == '__main__': unittest.main()
