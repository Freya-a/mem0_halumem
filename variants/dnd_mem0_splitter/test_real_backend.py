"""Offline adapter tests. MockTransport never connects to a remote model."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class RealBackendTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((BASE / "real_backend.py").is_file(), "real_backend.py 尚未实现")
        self.rb = importlib.import_module("real_backend")
        self.splitter = importlib.import_module("splitter")
        self.request = json.loads((BASE/"examples/input.json").read_text(encoding="utf-8"))
        self.response = json.loads((BASE/"examples/mock_response.json").read_text(encoding="utf-8"))
        self.settings = self.rb.ModelSettings(model="qwen-plus", api_key="fake-test-secret", base_url="https://offline.invalid/v1")
        self.prompt = self.rb.load_design_prompt(BASE/"DESIGN.md")
        self.http_requests = []

    def client(self, content=None, status=200, finish_reason="stop"):
        import httpx
        from openai import OpenAI
        if content is None:
            content = json.dumps(self.response, ensure_ascii=False)

        def handler(request):
            self.http_requests.append(request)
            if status != 200:
                return httpx.Response(status, json={"error": {"message": "failure fake-test-secret", "type": "server_error"}})
            return httpx.Response(200, json={
                "id": "offline-test", "object": "chat.completion", "created": 1,
                "model": "qwen-plus", "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": finish_reason}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            })

        client = OpenAI(api_key="fake-test-secret", base_url="https://offline.invalid/v1", max_retries=0,
                        http_client=httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=False))
        self.addCleanup(client.close)
        return client

    def test_config_missing_stops_and_never_uses_other_provider_key(self):
        with tempfile.TemporaryDirectory(dir=BASE) as temp:
            path = Path(temp)/"config.env"
            path.write_text("LLM_MODEL=qwen-plus\n", encoding="utf-8")
            with self.assertRaises(self.rb.ValidationError) as caught:
                self.rb.load_model_settings(path, environ={"DEEPSEEK_API_KEY": "unrelated-secret"})
            self.assertEqual(caught.exception.code, "missing_configuration")
            self.assertNotIn("unrelated-secret", str(caught.exception))

    def test_config_priority_aliases_and_secret_repr(self):
        with tempfile.TemporaryDirectory(dir=BASE) as temp:
            path = Path(temp)/"config.env"
            path.write_text("LLM_MODEL=file-model\nLLM_API_KEY=fake-file-secret\nLLM_BASE_URL=https://offline.invalid/v1\n", encoding="utf-8")
            settings = self.rb.load_model_settings(path, environ={"LLM_MODEL": "qwen-plus", "OPENAI_MODEL": "unused-alias"})
            self.assertEqual(settings.model, "qwen-plus")
            self.assertNotIn("fake-file-secret", repr(settings))
            path.write_text("OPENAI_MODEL=qwen-plus\nOPENAI_API_KEY=fake-alias-secret\nOPENAI_BASE_URL=https://offline.invalid/v1\n", encoding="utf-8")
            self.assertEqual(self.rb.load_model_settings(path, environ={}).model, "qwen-plus")

    def test_prompt_is_exact_design_block_and_is_sent_with_separate_input(self):
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client())
        result = self.splitter.split_memory(self.request, backend)
        self.assertEqual(result["memory_id"], "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID")
        self.assertEqual(result["memory_text"], "李娜去年没有搬到上海；王强说，如果获批，他可能明年搬去。")
        self.assertEqual(len(self.http_requests), 1)
        payload = json.loads(self.http_requests[0].content)
        self.assertEqual(payload["model"], "qwen-plus")
        self.assertEqual(payload["response_format"], {"type": "json_object"})
        self.assertEqual(payload["messages"][0], {"role": "system", "content": self.prompt})
        self.assertEqual(json.loads(payload["messages"][1]["content"]), self.request)
        design = (BASE/"DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("```text\n"+self.prompt+"\n```", design)
        self.assertNotIn("fake-test-secret", json.dumps(payload, ensure_ascii=False))

    def test_single_call_guard_prevents_second_create(self):
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client())
        backend(self.request)
        with self.assertRaises(self.rb.ValidationError) as caught:
            backend(self.request)
        self.assertEqual(caught.exception.code, "call_limit_reached")
        self.assertEqual(len(self.http_requests), 1)
        self.assertEqual(backend.call_count, 1)

    def test_http_failure_is_not_retried_and_does_not_expose_secret(self):
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client(status=500))
        with self.assertRaises(self.rb.ValidationError) as caught:
            backend(self.request)
        self.assertEqual(caught.exception.code, "model_request_failed")
        self.assertEqual(len(self.http_requests), 1)
        self.assertIn("500", str(caught.exception))
        self.assertNotIn("fake-test-secret", str(caught.exception))

    def test_malformed_and_duplicate_json_are_not_repaired(self):
        for content, code in [("```json\n{}\n```", "model_json_error"), ('{"facts":[],"facts":[]}', "duplicate_json_key")]:
            with self.subTest(content=content):
                backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client(content=content))
                with self.assertRaises(self.rb.ValidationError) as caught:
                    backend(self.request)
                self.assertEqual(caught.exception.code, code)
                self.assertEqual(backend.raw_content, content)
                self.assertEqual(backend.call_count, 1)

    def test_truncated_response_is_a_failure(self):
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client(finish_reason="length"))
        with self.assertRaises(self.rb.ValidationError) as caught:
            backend(self.request)
        self.assertEqual(caught.exception.code, "model_incomplete_response")
        self.assertIsNotNone(backend.raw_content)

    def test_original_validator_rejects_bad_quote_and_wrong_model_echo(self):
        self.response["facts"][0]["evidence"][0]["quote"] = "李娜已经搬到上海"
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client())
        with self.assertRaises(self.rb.ValidationError) as caught:
            self.splitter.split_memory(self.request, backend)
        self.assertEqual(caught.exception.code, "quote_not_found")
        self.response = {"memory_id": "wrong", "facts": []}
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client())
        with self.assertRaises(self.rb.ValidationError) as caught:
            self.splitter.split_memory(self.request, backend)
        self.assertEqual(caught.exception.code, "id_mismatch")

    def test_invalid_input_fails_before_any_request(self):
        backend = self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=self.client())
        with self.assertRaises(self.rb.ValidationError):
            self.splitter.split_memory({"memory_id": "example"}, backend)
        self.assertEqual(len(self.http_requests), 0)
        self.assertEqual(backend.call_count, 0)

    def test_sdk_clients_with_retries_are_rejected_before_request(self):
        client = self.client()
        client.max_retries = 2
        with self.assertRaises(self.rb.ValidationError) as caught:
            self.rb.OpenAICompatibleBackend(self.settings, self.prompt, client=client)
        self.assertEqual(caught.exception.code, "unsafe_client_configuration")
        self.assertEqual(len(self.http_requests), 0)

    def test_run_artifacts_keep_success_or_failure_and_refuse_overwrite(self):
        self.assertTrue((BASE/"run_real.py").is_file(), "run_real.py 尚未实现")
        runner = importlib.import_module("run_real")
        with tempfile.TemporaryDirectory(dir=BASE) as temp:
            env = Path(temp)/"config.env"
            env.write_text("LLM_MODEL=qwen-plus\nLLM_API_KEY=fake-test-secret\nLLM_BASE_URL=https://offline.invalid/v1\n", encoding="utf-8")
            for bad in (False, True):
                if bad:
                    self.response["facts"][0]["evidence"][0]["quote"] = "unmatched"
                output, report = runner.run_once(BASE/"examples/input.json", env, Path(temp)/str(bad), client=self.client(), environ={})
                folder = Path(temp)/str(bad)
                self.assertEqual(report["model_call_attempts"], 1)
                self.assertEqual(report["automatic_check"], "failed" if bad else "passed")
                self.assertEqual((folder/"result.json").exists(), not bad)
                self.assertTrue((folder/"raw_content.txt").is_file())
                self.assertIsNone(output) if bad else self.assertEqual(len(output["facts"]), 2)
                all_text = "".join(p.read_text(encoding="utf-8") for p in folder.iterdir() if p.is_file())
                self.assertNotIn("fake-test-secret", all_text)
                before = len(self.http_requests)
                with self.assertRaises(self.rb.ValidationError) as caught:
                    runner.run_once(BASE/"examples/input.json", env, folder, client=self.client(), environ={})
                self.assertEqual(caught.exception.code, "run_directory_exists")
                self.assertEqual(len(self.http_requests), before)


if __name__ == "__main__":
    unittest.main()
