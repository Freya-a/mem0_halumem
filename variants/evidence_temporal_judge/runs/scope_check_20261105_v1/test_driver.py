import importlib.util
from pathlib import Path
import tempfile
import unittest

p = Path(__file__).with_name('driver.py')
s = importlib.util.spec_from_file_location('scope_driver', p)
driver = importlib.util.module_from_spec(s)
s.loader.exec_module(driver)

class DriverTests(unittest.TestCase):
    def test_budget_stops_before_backend_and_keeps_journal(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = driver.RunRecorder(Path(tmp), maximum=1)
            seen = []
            def invoke(prompt, request):
                seen.append(request)
                return {'ok': True}, {'raw': '{"ok":true}', 'metadata': {}, 'attempted': True}
            self.assertEqual(r.call('case', 'split', 'system', {'memory_id': 'm'}, invoke), {'ok': True})
            with self.assertRaises(driver.BudgetExhausted):
                r.call('case', 'judge', 'system', {}, invoke)
            self.assertEqual(len(seen), 1)
            self.assertEqual(r.count, 1)
            self.assertEqual(len((Path(tmp)/'call_journal.jsonl').read_text().splitlines()), 2)

    def test_inputs_contain_only_selected_source_material(self):
        cases = driver.prepare_cases()
        self.assertEqual(len(cases), 3)
        for case in cases:
            self.assertEqual(set(case['request']), {'memory_id', 'memory_text', 'source_context'})
            self.assertEqual(set(case['new_evidence'][0]), {'source_id', 'text', 'speaker', 'recorded_at'})
            serialized = str((case['request'], case['new_evidence']))
            for word in ('human_conclusion', 'allowed_modification', 'review_decision', 'expected'):
                self.assertNotIn(word, serialized)

if __name__ == '__main__': unittest.main()
