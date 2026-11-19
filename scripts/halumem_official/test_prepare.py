import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import prepare


class InputBridgeTest(unittest.TestCase):
    def test_existing_run_builds_full_official_input(self):
        users, summary = prepare.build_inputs()
        self.assertEqual((len(users), summary['sessions']), (3, 28))
        self.assertEqual((summary['updates'], summary['questions']), (56, 75))
        sessions = [s for u in users for s in u['sessions']]
        self.assertTrue(all(isinstance(s['extracted_memories'], list) for s in sessions))
        self.assertEqual(sum('memories_from_system' in m for s in sessions for m in s['memory_points']), 56)
        self.assertEqual(sum('system_response' in q for s in sessions for q in s.get('questions', [])), 75)

    def test_missing_answer_rejected(self):
        records = prepare.read_records()
        item = next(r for r in records if r['kind'] == 'qa')
        item['stages']['answer']['status'] = 'error'
        with self.assertRaisesRegex(ValueError, 'answer'):
            prepare.build_inputs(records=records)

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'existing'
            target.mkdir()
            (target / 'marker').write_text('keep')
            with self.assertRaises(FileExistsError):
                prepare.write_bundle(target, [], {})
            self.assertEqual((target / 'marker').read_text(), 'keep')

    def test_official_cli_produces_all_task_scores_offline(self):
        users, summary = prepare.build_inputs()
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            bundle = base / 'run'
            prepare.write_bundle(bundle, users, summary)
            # Replace only the external model request; execute the real scorer in
            # its own process, including its process pools and aggregator.
            (base / 'sitecustomize.py').write_text(
                "import sys, types\n"
                "m = types.ModuleType('llms')\n"
                "def respond(prompt):\n"
                "    return {'score':'2','accuracy_score':'2',"
                "'is_included_in_golden_memories':'true',"
                "'evaluation_result':'Correct'}\n"
                "m.llm_request_for_json = respond\n"
                "sys.modules['llms'] = m\n", encoding='utf-8')
            env = dict(os.environ, PYTHONPATH=str(base))
            completed = subprocess.run(
                [sys.executable, str(prepare.OFFICIAL), '--frame', 'memzero', '--version', 'development'],
                cwd=bundle, env=env, text=True, capture_output=True, timeout=120)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            result = json.loads((bundle / 'results/memzero-development/memzero_eval_stat_result.json').read_text())
            self.assertEqual(len(result['memory_integrity_records']), 421)
            self.assertEqual(len(result['memory_accuracy_records']), 617)
            self.assertEqual(len(result['memory_update_records']), 56)
            self.assertEqual(len(result['question_answering_records']), 75)
            scores = result['overall_score']
            self.assertEqual(scores['memory_extraction_f1'], 1.0)
            self.assertEqual(scores['memory_update']['correct_update_memory_ratio(all)'], 1.0)
            self.assertEqual(scores['question_answering']['correct_qa_ratio(all)'], 1.0)


if __name__ == '__main__':
    unittest.main()
