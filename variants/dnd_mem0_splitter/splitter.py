#!/usr/bin/env python3
"""Standalone, standard-library-only splitter boundary; CLI uses handwritten JSON.

This module does not infer facts. FactBackend is an extension point, not an
implemented model client. No Mem0, network, keys, or dataset access is included.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
from typing import Any, Protocol


class ValidationError(ValueError):
    """A rejected input or candidate result with a machine-readable location."""

    def __init__(self, code: str, path: str, message: str):
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"{code} at {path}: {message}")

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


class FactBackend(Protocol):
    """Future call boundary: validated input -> candidate {facts: [...]}.

    Optional memory_id/memory_text echoes must match. A real model client and
    prompt execution are deliberately absent from this version.
    """

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]: ...


class MockBackend:
    """Return a supplied handwritten response; perform no text inference."""

    def __init__(self, response: dict[str, Any]):
        self._response = deepcopy(response)

    def __call__(self, request: dict[str, Any]) -> dict[str, Any]:
        return deepcopy(self._response)


def _object(value: Any, path: str, required: tuple[str, ...],
            optional: tuple[str, ...] = ()) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError("invalid_type", path, "Expected a JSON object.")
    for key in required:
        if key not in value:
            raise ValidationError("missing_field", f"{path}.{key}", "Required field is missing.")
    for key in value:
        if key not in required and key not in optional:
            raise ValidationError("unexpected_field", f"{path}.{key}", "Field is not in the v1 schema.")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("invalid_type", path, "Expected a string.")
    if not value.strip():
        raise ValidationError("invalid_value", path, "String must not be empty or whitespace-only.")
    # Validate presence without trimming or normalizing authoritative text/IDs.
    return value


def _list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError("invalid_type", path, "Expected a JSON array.")
    return value


def _validate_request(request: Any) -> dict[str, str]:
    _object(request, "$", ("memory_id", "memory_text"), ("source_context",))
    _string(request["memory_id"], "$.memory_id")
    _string(request["memory_text"], "$.memory_text")
    contexts = {}
    for index, context in enumerate(_list(request.get("source_context", []), "$.source_context")):
        path = f"$.source_context[{index}]"
        _object(context, path, ("source_id", "source_ref", "text"), ("speaker", "recorded_at"))
        for key in context:
            _string(context[key], f"{path}.{key}")
        source_id = context["source_id"]
        if source_id in contexts:
            raise ValidationError("duplicate_source_id", f"{path}.source_id", "Context IDs must be unique.")
        contexts[source_id] = context["text"]
    return contexts


def _validate_response(response: Any, request: dict[str, Any], contexts: dict[str, str]) -> None:
    _object(response, "$", ("facts",), ("memory_id", "memory_text"))
    if "memory_id" in response and response["memory_id"] != request["memory_id"]:
        raise ValidationError("id_mismatch", "$.memory_id", "Backend echo differs from input memory_id.")
    if "memory_text" in response and response["memory_text"] != request["memory_text"]:
        raise ValidationError("text_mismatch", "$.memory_text", "Backend echo differs from input memory_text.")
    fields = ("fact_index", "source_memory_id", "raw_subfact", "contextualized_subfact",
              "evidence", "pending_confirmations")
    for index, fact in enumerate(_list(response["facts"], "$.facts")):
        path = f"$.facts[{index}]"
        _object(fact, path, fields)
        if type(fact["fact_index"]) is not int or fact["fact_index"] != index + 1:
            raise ValidationError("invalid_fact_index", f"{path}.fact_index",
                                  "Expected consecutive integer indexes starting at 1; bool is not allowed.")
        for key in ("source_memory_id", "raw_subfact", "contextualized_subfact"):
            _string(fact[key], f"{path}.{key}")
        if fact["source_memory_id"] != request["memory_id"]:
            raise ValidationError("id_mismatch", f"{path}.source_memory_id", "Fact must refer to input memory_id.")
        evidence_list = _list(fact["evidence"], f"{path}.evidence")
        if not evidence_list:
            raise ValidationError("invalid_value", f"{path}.evidence", "At least one memory evidence item is required.")
        has_memory_evidence = False
        for evidence_index, evidence in enumerate(evidence_list):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            _object(evidence, evidence_path, ("source_type", "source_id", "quote", "supports"))
            for key in evidence:
                _string(evidence[key], f"{evidence_path}.{key}")
            if evidence["source_type"] == "memory":
                if evidence["source_id"] != request["memory_id"]:
                    raise ValidationError("id_mismatch", f"{evidence_path}.source_id",
                                          "Memory evidence must refer to input memory_id.")
                source_text = request["memory_text"]
                has_memory_evidence = True
            elif evidence["source_type"] == "context":
                if evidence["source_id"] not in contexts:
                    raise ValidationError("unknown_source", f"{evidence_path}.source_id",
                                          "Context evidence refers to an unknown input source_id.")
                source_text = contexts[evidence["source_id"]]
            else:
                raise ValidationError("invalid_value", f"{evidence_path}.source_type", "Expected memory or context.")
            if evidence["quote"] not in source_text:
                raise ValidationError("quote_not_found", f"{evidence_path}.quote",
                                      "Quote is not an exact substring of the declared input source.")
        if not has_memory_evidence:
            raise ValidationError("missing_memory_evidence", f"{path}.evidence",
                                  "Each fact must include evidence from memory_text.")
        for confirmation_index, confirmation in enumerate(
                _list(fact["pending_confirmations"], f"{path}.pending_confirmations")):
            confirmation_path = f"{path}.pending_confirmations[{confirmation_index}]"
            _object(confirmation, confirmation_path, ("item", "reason"))
            for key in confirmation:
                _string(confirmation[key], f"{confirmation_path}.{key}")


def split_memory(request: dict[str, Any], backend: FactBackend) -> dict[str, Any]:
    """Validate one memory and candidate facts, then assemble an owned result.

    The backend receives a separate copy so it cannot mutate the authoritative
    snapshot. Validation is structural and checks literal provenance only;
    it cannot prove semantic fidelity, completeness, or factual truth.
    """
    snapshot = deepcopy(request)
    contexts = _validate_request(snapshot)
    response = deepcopy(backend(deepcopy(snapshot)))
    _validate_response(response, snapshot, contexts)
    facts = response["facts"]
    for fact in facts:
        # IDs have already been checked; construct authoritative IDs ourselves.
        fact["source_memory_id"] = snapshot["memory_id"]
    return {
        "memory_id": snapshot["memory_id"],
        "memory_text": snapshot["memory_text"],
        "facts": facts,
    }


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("duplicate_json_key", "$", f"Duplicate JSON key: {key!r}.")
        result[key] = value
    return result


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object)
    except OSError as error:
        raise ValidationError("io_error", str(path), str(error)) from error
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValidationError("json_error", str(path), str(error)) from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate handwritten old-memory subfacts; no model or Mem0 access.")
    parser.add_argument("--input", required=True, type=Path, help="One input memory JSON file.")
    parser.add_argument("--mock-response", required=True, type=Path, help="Handwritten candidate response JSON file.")
    args = parser.parse_args(argv)
    try:
        request = _read_json(args.input)
        response = _read_json(args.mock_response)
        result = split_memory(request, MockBackend(response))
    except ValidationError as error:
        print(json.dumps({"error": error.as_dict()}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
