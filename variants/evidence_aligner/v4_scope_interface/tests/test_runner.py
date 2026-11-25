import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from runner import CASE_NAMES, run_cases


class FakeBackend:
    def __init__(self, failure=None, malformed=None):
        self.calls = []
        self.provider_response = None
        self.failure = failure
        self.malformed = malformed
        self.closed = False

    def __call__(self, messages):
        data = json.loads(messages[1]['content'])
        self.calls.append(data['case_id'])
        if data['case_id'] == self.failure:
            raise RuntimeError('secret must never be saved')
        text = '{broken' if data['case_id'] == self.malformed else json.dumps({'records': []})
        self.provider_response = {'model': 'qwen-plus-2025-12-01', 'usage': {'total_tokens': 42}, 'choices': []}
        return {'content': text, 'model': 'qwen-plus-2025-12-01', 'finish_reason': 'stop'}

    def close(self):
        self.closed = True


def cases():
    return [{'input': {'case_id': case, 'dummy': case}} for case in CASE_NAMES]


def prepare(artifact):
    return artifact['input']


def analyze(payload, parsed):
    return {'status': 'passed', 'parsed': parsed, 'observed_case': payload['case_id']}


class RunnerTests(unittest.TestCase):
    def test_exactly_five_requests_and_saved_responses(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = FakeBackend()
            run_dir = Path(tmp) / 'run'
            m = run_cases(cases(), run_dir, prepare=prepare, analyze=analyze,
                          backend_factory=lambda: backend, system_prompt='system')
            self.assertEqual(backend.calls, list(CASE_NAMES))
            self.assertTrue(backend.closed)
            self.assertEqual(m['request_attempts'], 5)
            self.assertEqual(m['model_responses'], 5)
            for case in CASE_NAMES:
                a = json.loads((run_dir / (case + '.json')).read_text())
                self.assertEqual(a['call']['attempts'], 1)
                self.assertEqual(a['call']['status'], 'passed')
                self.assertEqual(a['usage']['total_tokens'], 42)
                self.assertEqual(a['result']['observed_case'], case)
                self.assertEqual(json.loads(a['request']['messages'][1]['content'])['case_id'], case)
                self.assertEqual(len(a['request']['sha256']), 64)
                body = {k: v for k, v in a['request'].items() if k not in ('sha256', 'messages_sha256')}
                encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
                self.assertEqual(a['request']['sha256'], hashlib.sha256(encoded).hexdigest())
                self.assertEqual(a['raw_response'], '{"records": []}')

    def test_failure_and_bad_json_do_not_retry_or_prevent_other_cases(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend = FakeBackend(failure=CASE_NAMES[0], malformed=CASE_NAMES[1])
            path = Path(tmp) / 'run'
            manifest = run_cases(cases(), path, prepare=prepare, analyze=analyze,
                                 backend_factory=lambda: backend, system_prompt='system')
            self.assertEqual(backend.calls, list(CASE_NAMES))
            self.assertEqual(manifest['request_attempts'], 5)
            self.assertEqual(manifest['model_responses'], 4)
            err = json.loads((path / (CASE_NAMES[0] + '.json')).read_text())
            self.assertEqual(err['call']['status'], 'request_error')
            self.assertEqual(err['call']['request_transmitted'], 'unknown')
            self.assertEqual(err['call']['attempts'], 1)
            self.assertNotIn('secret must never be saved', json.dumps(err))
            self.assertEqual(json.loads((path / (CASE_NAMES[1] + '.json')).read_text())['call']['status'], 'parse_error')
            self.assertEqual(json.loads((path / (CASE_NAMES[2] + '.json')).read_text())['call']['status'], 'passed')

    def test_existing_run_never_sends_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'run'
            backend = FakeBackend()
            run_cases(cases(), path, prepare=prepare, analyze=analyze,
                      backend_factory=lambda: backend, system_prompt='system')
            with self.assertRaises(FileExistsError):
                run_cases(cases(), path, prepare=prepare, analyze=analyze,
                          backend_factory=lambda: backend, system_prompt='system')
            self.assertEqual(backend.calls, list(CASE_NAMES))

    def test_backend_init_failure_records_no_attempts(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'run'
            def failed():
                raise ValueError('sensitive credentials')
            with self.assertRaises(ValueError):
                run_cases(cases(), path, prepare=prepare, analyze=analyze,
                          backend_factory=failed, system_prompt='system')
            manifest = json.loads((path / 'manifest.json').read_text())
            self.assertEqual(manifest['status'], 'configuration_error')
            self.assertEqual(manifest['request_attempts'], 0)
            self.assertNotIn('sensitive credentials', json.dumps(manifest))

    def test_provider_response_is_not_lost_if_backend_fails_after_receiving_it(self):
        class LateFailure(FakeBackend):
            def __call__(self, messages):
                self.calls.append(json.loads(messages[1]['content'])['case_id'])
                self.provider_response = {'model': 'qwen-plus-2025-12-01',
                                          'usage': {'total_tokens': 17},
                                          'choices': [{'message': {'content': '{"records": []}'}}]}
                raise RuntimeError('failed after response')
        with tempfile.TemporaryDirectory() as tmp:
            backend = LateFailure()
            path = Path(tmp) / 'run'
            manifest = run_cases(cases(), path, prepare=prepare, analyze=analyze,
                                 backend_factory=lambda: backend, system_prompt='system')
            self.assertEqual(manifest['model_responses'], 5)
            artifact = json.loads((path / (CASE_NAMES[0] + '.json')).read_text())
            self.assertEqual(artifact['provider_response']['usage']['total_tokens'], 17)
            self.assertEqual(artifact['usage']['total_tokens'], 17)
            self.assertEqual(artifact['raw_response'], '{"records": []}')
            self.assertTrue(artifact['call']['request_transmitted'])

    def test_http_error_response_body_is_saved_without_headers_or_exception_message(self):
        class Response:
            text = '{"error":{"code":"overloaded"}}'
        class HTTPFailure(RuntimeError):
            status_code = 503
            response = Response()
        class HTTPBackend(FakeBackend):
            def __call__(self, messages):
                self.calls.append(json.loads(messages[1]['content'])['case_id'])
                raise HTTPFailure('secret in exception')
        with tempfile.TemporaryDirectory() as tmp:
            backend = HTTPBackend()
            path = Path(tmp) / 'run'
            manifest = run_cases(cases(), path, prepare=prepare, analyze=analyze,
                                 backend_factory=lambda: backend, system_prompt='system')
            self.assertEqual(manifest['request_attempts'], 5)
            artifact = json.loads((path / (CASE_NAMES[0] + '.json')).read_text())
            self.assertEqual(artifact['raw_response'], Response.text)
            self.assertTrue(artifact['call']['request_transmitted'])
            self.assertEqual(artifact['call']['error']['http_status'], 503)
            self.assertNotIn('secret in exception', json.dumps(artifact))


if __name__ == '__main__':
    unittest.main()
