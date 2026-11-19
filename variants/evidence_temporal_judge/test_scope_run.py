import json
from pathlib import Path
import tempfile
import unittest

import scope_run


class ScopeRunTests(unittest.TestCase):
    def test_three_saved_splits_replayed_without_split_calls_or_review_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'run'
            scope_run.prepare(root)
            seen = []
            def fake(prompt, payload):
                seen.append(payload)
                if payload['task'] == 'new_candidates':
                    response = {'candidates': []}
                else:
                    fact = payload['fact']
                    old = [{k: e[k] for k in ('source_type', 'source_id', 'quote')} for e in fact['evidence'][:1]]
                    response = {'applicability': 'insufficient', 'components': [{'fragment': fact['raw_subfact'],
                        'contextualized': fact['contextualized_subfact'], 'action': 'confirm', 'reason': '待确认',
                        'old_evidence': old, 'new_evidence': []}]}
                return response, {'attempted': True, 'raw': json.dumps(response), 'metadata': {}}
            summary = scope_run.execute(root, fake, {'model': 'offline-fake'})
            self.assertEqual(summary['actual_sdk_attempts'], 6)
            self.assertEqual(len(seen), 6)
            self.assertTrue(all(p['task'] in ('fact_judgment', 'new_candidates') for p in seen))
            self.assertNotIn('human_review', json.dumps(seen))
            for name in scope_run.CASES:
                result = json.loads((root / name / 'scope_result.json').read_text())
                self.assertEqual(result['facts'][0]['status'], 'insufficient')
                comparison = json.loads((root / name / 'comparison.json').read_text())
                self.assertIn('v1', comparison)
                self.assertIn('scope_v2', comparison)
            self.assertEqual(len(list((root / 'calls').glob('*/raw_content.txt'))), 6)
            with self.assertRaises(FileExistsError): scope_run.execute(root, fake, {'model': 'offline-fake'})

    def test_prepared_input_tampering_stops_before_any_model_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'run'
            scope_run.prepare(root)
            (root / 'promotion' / 'split_result.json').write_text('{}')
            calls = []
            with self.assertRaises(ValueError):
                scope_run.execute(root, lambda *args: calls.append(args), {'model': 'offline-fake'})
            self.assertEqual(calls, [])


if __name__ == '__main__': unittest.main()
