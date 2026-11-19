"""Offline safeguards only; never read real configuration or contact a service."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from real_backend import ModelSettings


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ROOT / 'experiment_driver.py').exists(),
                        'isolated driver has not been implemented')
        spec = importlib.util.spec_from_file_location('v5_experiment_driver', ROOT / 'experiment_driver.py')
        self.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.driver)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.settings = ModelSettings('offline-only', 'not-a-real-key', 'http://invalid.local')
        self.request = {'memory_id': 'synthetic-id', 'memory_text': 'No blue ink'}
        self.data = (json.dumps(self.request) + '\n').encode()
        self.candidate = {'facts': [{'fact_index': 1, 'source_memory_id': 'synthetic-id',
            'raw_subfact': 'No blue ink', 'contextualized_subfact': 'No blue ink',
            'evidence': [{'source_type': 'memory', 'source_id': 'synthetic-id',
                          'quote': 'No blue ink', 'supports': 'Old memory records this restriction.'}],
            'pending_confirmations': []}]}
        self.created = []

    def factory(self, settings, prompt):
        parent = self
        class OfflineBackend:
            call_count = 0
            response_metadata = {'offline': True}
            raw_content = None
            def __call__(self, request):
                self.call_count += 1
                self.raw_content = json.dumps(parent.candidate, ensure_ascii=False)
                return json.loads(self.raw_content)
            def close(self):
                pass
        backend = OfflineBackend()
        self.created.append(backend)
        return backend

    def execute(self):
        return self.driver.execute_case(self.root, 'synthetic', self.data,
                                        'synthetic prompt', self.settings, self.factory)

    def test_repeat_rejected_before_backend_creation(self):
        self.execute()
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertEqual(len(self.created), 1)
        self.assertEqual(self.created[0].call_count, 1)

    def test_invalid_quote_retains_failure_without_retry_or_result(self):
        self.candidate['facts'][0]['evidence'][0]['quote'] = 'invented quote'
        report = self.execute()
        directory = self.root / 'runs/synthetic/v5'
        self.assertEqual(report['automatic_check'], 'failed')
        self.assertEqual(report['error']['code'], 'quote_not_found')
        self.assertEqual(self.created[0].call_count, 1)
        self.assertFalse((directory / 'result.json').exists())
        self.assertEqual(json.loads((directory / 'raw_content.txt').read_text()), self.candidate)

    def test_success_preserves_input_and_response_without_repairs(self):
        report = self.execute()
        directory = self.root / 'runs/synthetic/v5'
        self.assertEqual(report['automatic_check'], 'passed')
        self.assertEqual((directory / 'input.json').read_bytes(), self.data)
        self.assertEqual((directory / 'raw_content.txt').read_text(), self.created[0].raw_content)
        saved = json.loads((directory / 'result.json').read_text())
        self.assertEqual(saved['facts'], self.candidate['facts'])
        self.assertEqual(self.created[0].call_count, 1)


if __name__ == '__main__':
    unittest.main()
