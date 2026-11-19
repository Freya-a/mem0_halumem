import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_direct import create_http_client, safe_error

class DirectRunTests(unittest.TestCase):
    def test_client_ignores_proxy_environment(self):
        with patch.dict(os.environ, {'HTTP_PROXY':'http://127.0.0.1:1', 'HTTPS_PROXY':'http://127.0.0.1:1'}):
            with create_http_client() as client:
                self.assertFalse(client.trust_env)
                self.assertFalse(client.follow_redirects)

    def test_error_chain_omits_secret_message(self):
        try:
            try:
                raise ConnectionRefusedError(111, 'secret credential example')
            except OSError as exc:
                raise RuntimeError('private url') from exc
        except RuntimeError as exc:
            data = safe_error(exc)
        self.assertEqual(data['type'], 'RuntimeError')
        self.assertEqual(data['cause_chain'][0]['type'], 'ConnectionRefusedError')
        self.assertEqual(data['cause_chain'][0]['errno'], 111)
        self.assertNotIn('secret', json.dumps(data))
        self.assertNotIn('private', json.dumps(data))

if __name__ == '__main__': unittest.main()
