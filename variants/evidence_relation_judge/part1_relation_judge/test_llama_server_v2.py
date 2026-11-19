import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import relation_judge_v2 as judge
import test_relation_judge as fixture
import run_llama_server_v2 as runner


class Server(BaseHTTPRequestHandler):
    calls = []
    content = ''
    status = 200
    def do_POST(self):
        type(self).calls.append((self.path,json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
        data = {'prompt':'rendered prompt'} if self.path == '/apply-template' else {'content':type(self).content}
        response = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(200 if self.path == '/apply-template' else type(self).status)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    def log_message(self, *_): pass


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), Server)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
    def setUp(self):
        Server.calls = []
        Server.status = 200
        self.backend = runner.LlamaServerV2(f'http://127.0.0.1:{self.server.server_port}')
    def test_valid_response_one_request_and_same_v2_messages(self):
        Server.content = json.dumps(fixture.answer(), ensure_ascii=False)
        result = judge.judge(fixture.request(), self.backend)
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([x[0] for x in Server.calls], ['/apply-template','/completion'])
        self.assertEqual(Server.calls[0][1]['messages'], self.backend.records[0]['messages'])
        self.assertEqual(Server.calls[0][1]['messages'][0]['content'], judge.SYSTEM)
        self.assertFalse(Server.calls[0][1]['chat_template_kwargs']['enable_thinking'])
        self.assertEqual(Server.calls[1][1]['prompt'], 'rendered prompt')
        self.assertEqual(result['results'][0]['raw_output'], Server.content)
    def test_raw_non_json_is_not_sanitized_or_retried(self):
        Server.content = '<think>raw</think>{"relation":"support"}'
        result = judge.judge(fixture.request(), self.backend)
        self.assertEqual([x[0] for x in Server.calls], ['/apply-template','/completion'])
        self.assertEqual(result['results'][0]['raw_output'], Server.content)
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'parse')
        self.assertEqual(self.backend.records[0]['raw_response']['content'], Server.content)
    def test_http_error_preserves_body_without_retry(self):
        Server.status = 503
        Server.content = 'temporary failure'
        result = judge.judge(fixture.request(), self.backend)
        self.assertEqual([x[0] for x in Server.calls], ['/apply-template','/completion'])
        self.assertEqual(result['results'][0]['errors'][0]['stage'], 'model')
        self.assertIn('temporary failure', self.backend.records[0]['raw_response_text'])
        self.assertEqual(self.backend.records[0]['http_status'], 503)
    def test_nonlocal_server_rejected(self):
        with self.assertRaises(ValueError): runner.LlamaServerV2('http://example.com:8080')

if __name__ == '__main__': unittest.main()
