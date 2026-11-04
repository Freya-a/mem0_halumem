"""Offline regression tests for CLI-process proxy environment alignment."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx

from real_backend import ModelSettings, OpenAICompatibleBackend


class ProxyConfigTests(unittest.TestCase):
    def backend(self, scheme="https"):
        settings = ModelSettings(model="qwen-plus", api_key="fake-proxy-test-key",
                                 base_url=scheme+"://offline.invalid/v1")
        backend = OpenAICompatibleBackend(settings, "No request is sent in this test.")
        self.addCleanup(backend.close)
        self.assertEqual(backend.call_count, 0)
        return backend

    def selected_proxy(self, backend, scheme="https"):
        transport = backend.client._client._transport_for_url(httpx.URL(scheme+"://offline.invalid/v1"))
        proxy = getattr(transport._pool, "_proxy_url", None)
        if proxy is None:
            return None
        host = proxy.host.decode() if isinstance(proxy.host, bytes) else proxy.host
        return host, proxy.port

    def test_https_uses_uppercase_tunnel_instead_of_stale_lowercase_port(self):
        with patch.dict(os.environ, {
            "HTTP_PROXY": "http://127.0.0.1:17897",
            "HTTPS_PROXY": "http://127.0.0.1:17897",
            "http_proxy": "http://localhost:7890",
            "https_proxy": "http://localhost:7890",
        }, clear=True):
            backend = self.backend()
            self.assertEqual(self.selected_proxy(backend), ("127.0.0.1", 17897))
            self.assertEqual(os.environ["http_proxy"], "http://127.0.0.1:17897")
            self.assertEqual(os.environ["https_proxy"], "http://127.0.0.1:17897")

    def test_http_and_https_keep_their_separate_uppercase_proxy_values(self):
        with patch.dict(os.environ, {
            "HTTP_PROXY": "http://127.0.0.1:17897",
            "HTTPS_PROXY": "http://127.0.0.1:17898",
            "http_proxy": "http://localhost:7890",
            "https_proxy": "http://localhost:7890",
        }, clear=True):
            backend = self.backend("http")
            self.assertEqual(self.selected_proxy(backend, "http"), ("127.0.0.1", 17897))
            self.assertEqual(self.selected_proxy(backend, "https"), ("127.0.0.1", 17898))

    def test_lowercase_only_configuration_is_preserved(self):
        with patch.dict(os.environ, {
            "http_proxy": "http://localhost:7890",
            "https_proxy": "http://localhost:7891",
        }, clear=True):
            backend = self.backend()
            self.assertEqual(self.selected_proxy(backend), ("localhost", 7891))
            self.assertEqual(os.environ["http_proxy"], "http://localhost:7890")
            self.assertNotIn("HTTP_PROXY", os.environ)

    def test_no_proxy_bypass_is_preserved(self):
        with patch.dict(os.environ, {
            "HTTPS_PROXY": "http://127.0.0.1:17897",
            "https_proxy": "http://localhost:7890",
            "NO_PROXY": "offline.invalid",
        }, clear=True):
            backend = self.backend()
            self.assertIsNone(self.selected_proxy(backend))
            self.assertEqual(os.environ["NO_PROXY"], "offline.invalid")


if __name__ == "__main__":
    unittest.main()
