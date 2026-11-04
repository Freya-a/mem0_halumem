"""Only synthetic data; all validations exercise the real splitter or CLI."""

import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parent


class SplitterTests(unittest.TestCase):
    def setUp(self):
        self.request = json.loads((BASE / "examples/input.json").read_text(encoding="utf-8"))
        self.response = json.loads((BASE / "examples/mock_response.json").read_text(encoding="utf-8"))

    def module(self):
        self.assertTrue((BASE / "splitter.py").is_file(), "splitter.py 尚未实现")
        return importlib.import_module("splitter")

    def split(self, request=None, response=None):
        module = self.module()
        return module.split_memory(
            self.request if request is None else request,
            module.MockBackend(self.response if response is None else response),
        )

    def reject(self, code, request=None, response=None):
        module = self.module()
        with self.assertRaises(module.ValidationError) as caught:
            self.split(request=request, response=response)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def cli(self, response="mock_response.json", input_path=None):
        return subprocess.run(
            [sys.executable, "-B", str(BASE / "splitter.py"),
             "--input", str(input_path or BASE / "examples/input.json"),
             "--mock-response", str(BASE / "examples" / response)],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_success_keeps_input_identity_and_handwritten_claims(self):
        result = self.split()
        self.assertEqual(result["memory_id"], "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID")
        self.assertEqual(result["memory_text"], "李娜去年没有搬到上海；王强说，如果获批，他可能明年搬去。")
        self.assertEqual(len(result["facts"]), 2)
        self.assertEqual(result["facts"][1]["raw_subfact"], "王强说，如果获批，他可能明年搬去。")
        self.assertEqual(result["facts"][1]["contextualized_subfact"], "王强说，如果获批，王强可能明年搬到上海。")
        self.assertEqual(result["facts"][1]["evidence"][1]["source_id"], "ctx-1")
        self.assertEqual(len(result["facts"][1]["pending_confirmations"]), 2)

    def test_omitted_source_context_and_empty_facts_are_valid(self):
        request = {"memory_id": "example-empty", "memory_text": "你搬过家吗？"}
        self.assertEqual(self.split(request, {"facts": []}), {
            "memory_id": "example-empty", "memory_text": "你搬过家吗？", "facts": [],
        })

    def test_no_context_is_needed_for_memory_only_evidence(self):
        del self.request["source_context"]
        self.response["facts"] = self.response["facts"][:1]
        self.assertEqual(len(self.split()["facts"]), 1)

    def test_whitespace_in_input_is_preserved(self):
        self.request["memory_id"] = "  example-id  "
        self.request["memory_text"] = "  李娜去年没有搬到上海。\n"
        self.response["facts"] = self.response["facts"][:1]
        self.response["facts"][0]["source_memory_id"] = "  example-id  "
        self.response["facts"][0]["evidence"][0]["source_id"] = "  example-id  "
        result = self.split()
        self.assertEqual(result["memory_id"], "  example-id  ")
        self.assertEqual(result["memory_text"], "  李娜去年没有搬到上海。\n")

    def test_backend_cannot_mutate_the_authoritative_input(self):
        module = self.module()
        original = copy.deepcopy(self.request)

        def changing_backend(request):
            request["memory_id"] = "changed"
            request["memory_text"] = "changed"
            request["source_context"][0]["text"] = "changed"
            return copy.deepcopy(self.response)

        result = module.split_memory(self.request, changing_backend)
        self.assertEqual(result["memory_id"], "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID")
        self.assertEqual(result["memory_text"], "李娜去年没有搬到上海；王强说，如果获批，他可能明年搬去。")
        self.assertEqual(self.request, original)

    def test_optional_backend_echo_must_match_input(self):
        self.response["memory_id"] = self.request["memory_id"]
        self.response["memory_text"] = self.request["memory_text"]
        self.assertEqual(self.split()["memory_id"], "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID")
        self.response["memory_id"] = "different"
        self.reject("id_mismatch")
        self.response["memory_id"] = self.request["memory_id"]
        self.response["memory_text"] = "different"
        self.reject("text_mismatch")

    def test_required_input_fields_and_types(self):
        for field in ("memory_id", "memory_text"):
            request = copy.deepcopy(self.request)
            del request[field]
            with self.subTest(field=field, kind="missing"):
                self.reject("missing_field", request=request)
            for value, code in ((" ", "invalid_value"), (None, "invalid_type"), (7, "invalid_type")):
                request[field] = value
                with self.subTest(field=field, value=value):
                    self.reject(code, request=request)
        self.reject("invalid_type", request=[])

    def test_context_fields_types_and_duplicate_ids(self):
        for value in (None, "context", {}):
            request = copy.deepcopy(self.request)
            request["source_context"] = value
            with self.subTest(value=value):
                self.reject("invalid_type", request=request)
        self.request["source_context"].append(copy.deepcopy(self.request["source_context"][0]))
        self.reject("duplicate_source_id")
        self.request["source_context"].pop()
        for field in ("source_id", "source_ref", "text"):
            request = copy.deepcopy(self.request)
            del request["source_context"][0][field]
            with self.subTest(field=field):
                self.reject("missing_field", request=request)

    def test_optional_context_metadata_is_accepted(self):
        self.request["source_context"][0].update(speaker="王强", recorded_at="2025-05-02T10:00:00+08:00")
        self.assertEqual(len(self.split()["facts"]), 2)

    def test_required_response_and_fact_fields(self):
        self.reject("missing_field", response={})
        self.reject("invalid_type", response={"facts": {}})
        for field in ("fact_index", "source_memory_id", "raw_subfact", "contextualized_subfact", "evidence", "pending_confirmations"):
            response = copy.deepcopy(self.response)
            del response["facts"][0][field]
            with self.subTest(field=field):
                self.reject("missing_field", response=response)
        self.response["facts"][0]["raw_subfact"] = " "
        self.reject("invalid_value")

    def test_fact_id_and_memory_evidence_id_must_match(self):
        self.response["facts"][0]["source_memory_id"] = "wrong"
        self.reject("id_mismatch")
        self.response["facts"][0]["source_memory_id"] = self.request["memory_id"]
        self.response["facts"][0]["evidence"][0]["source_id"] = "wrong"
        self.reject("id_mismatch")

    def test_fact_indexes_are_continuous_integers(self):
        for value in (0, 2, True, 1.0, "1"):
            self.response["facts"][0]["fact_index"] = value
            with self.subTest(value=value):
                self.reject("invalid_fact_index")

    def test_memory_quote_must_match_exactly(self):
        self.response["facts"][0]["evidence"][0]["quote"] = "李娜去年已经搬到上海"
        self.reject("quote_not_found")

    def test_context_quote_must_match_declared_source(self):
        self.request["source_context"].append({
            "source_id": "ctx-2", "source_ref": "示例会话/message-8", "text": "王强可能明年搬去。",
        })
        self.response["facts"][1]["evidence"][1]["source_id"] = "ctx-2"
        self.reject("quote_not_found")

    def test_unknown_context_and_source_type_are_rejected(self):
        self.response["facts"][1]["evidence"][1]["source_id"] = "unknown"
        self.reject("unknown_source")
        self.response["facts"][1]["evidence"][1]["source_id"] = "ctx-1"
        self.response["facts"][1]["evidence"][1]["source_type"] = "web"
        self.reject("invalid_value")

    def test_evidence_and_confirmation_schemas(self):
        cases = [
            ("evidence", [], "invalid_value"),
            ("evidence", None, "invalid_type"),
            ("evidence", [{}], "missing_field"),
            ("pending_confirmations", {}, "invalid_type"),
            ("pending_confirmations", [{}], "missing_field"),
            ("pending_confirmations", [{"item": "年份", "reason": " "}], "invalid_value"),
        ]
        for field, value, code in cases:
            response = copy.deepcopy(self.response)
            response["facts"][0][field] = value
            with self.subTest(field=field, value=value):
                self.reject(code, response=response)
        self.response["facts"][0]["evidence"][0]["quote"] = ""
        self.reject("invalid_value")

    def test_context_only_fact_is_rejected(self):
        self.response["facts"][1]["evidence"] = self.response["facts"][1]["evidence"][1:]
        self.reject("missing_memory_evidence")

    def test_unknown_fields_are_not_silently_dropped(self):
        self.response["facts"][0]["typo_field"] = "unexpected"
        self.reject("unexpected_field")
        del self.response["facts"][0]["typo_field"]
        self.request["source_contexts"] = []
        self.reject("unexpected_field")

    def test_returned_objects_do_not_alias_caller_data(self):
        module = self.module()
        result = module.split_memory(self.request, lambda request: self.response)
        result["facts"][0]["evidence"][0]["quote"] = "changed"
        self.assertEqual(self.response["facts"][0]["evidence"][0]["quote"], "李娜去年没有搬到上海")

    def test_cli_success_writes_only_the_result_to_stdout(self):
        process = self.cli()
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        result = json.loads(process.stdout)
        self.assertEqual(len(result["facts"]), 2)
        self.assertEqual(result["memory_id"], "EXAMPLE_ONLY_NOT_A_REAL_MEM0_ID")

    def test_cli_bad_quote_has_no_partial_success_output(self):
        process = self.cli("mock_response_bad_quote.json")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertTrue(process.stderr.startswith("{"), process.stderr)
        error = json.loads(process.stderr)["error"]
        self.assertEqual(error["code"], "quote_not_found")
        self.assertEqual(error["path"], "$.facts[1].evidence[1].quote")

    def test_cli_duplicate_keys_and_malformed_json_are_errors(self):
        with tempfile.TemporaryDirectory(prefix="test-json-", dir=BASE) as temp:
            input_path = Path(temp) / "input.json"
            for content, code in [
                ('{"memory_id":"a","memory_id":"b","memory_text":"hello"}', "duplicate_json_key"),
                ('{', "json_error"),
            ]:
                with input_path.open("w", encoding="utf-8") as stream:
                    stream.write(content)
                process = self.cli(input_path=input_path)
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, "")
                self.assertTrue(process.stderr.startswith("{"), process.stderr)
                self.assertEqual(json.loads(process.stderr)["error"]["code"], code)

    def test_cli_missing_file_is_an_explicit_error(self):
        process = self.cli(input_path=BASE / "does-not-exist.json")
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertTrue(process.stderr.startswith("{"), process.stderr)
        self.assertEqual(json.loads(process.stderr)["error"]["code"], "io_error")


if __name__ == "__main__":
    unittest.main()
