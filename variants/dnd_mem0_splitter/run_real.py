#!/usr/bin/env python3
"""Independent one-shot real splitter entry; original mock CLI remains untouched."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

from real_backend import OpenAICompatibleBackend, load_design_prompt, load_model_settings
from splitter import ValidationError, _read_json, split_memory

BASE = Path(__file__).resolve().parent
PROJECT = BASE.parent.parent


def _write(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def _write_json(path: Path, value: object) -> None:
    _write(path, json.dumps(value, ensure_ascii=False, indent=2)+"\n")


def run_once(input_path: Path, env_file: Path, run_dir: Path, *, client=None, environ=None):
    """Validate one synthetic input with one candidate call; keep success/failure artifacts."""
    settings = load_model_settings(env_file, environ=environ)
    prompt = load_design_prompt(BASE/"DESIGN.md")
    request = _read_json(input_path)
    run_dir = run_dir.resolve()
    if not run_dir.is_relative_to(BASE) or run_dir == BASE:
        raise ValidationError("invalid_run_directory", "$run_dir", "Run artifacts must be inside the splitter directory.")
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise ValidationError("run_directory_exists", "$run_dir", "Existing run directory is never reused or overwritten.") from None
    _write_json(run_dir/"input.json", request)
    _write(run_dir/"prompt.txt", prompt)
    _write_json(run_dir/"attempt.json", {
        "started_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "model": settings.model,
        "max_model_calls": 1,
        "sdk_max_retries": 0,
        "http_follow_redirects": False,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "configuration_names_and_sources": settings.provenance,
        "generation_parameters": settings.generation,
        "timeout_seconds": settings.timeout,
    })
    backend = None
    result, failure = None, None
    try:
        backend = OpenAICompatibleBackend(settings, prompt, client=client)
        result = split_memory(request, backend)
    except ValidationError as error:
        failure = error.as_dict()
    finally:
        if backend is not None:
            backend.close()
    if backend is not None and isinstance(backend.raw_content, str):
        # Only the model's content is retained, never HTTP headers or credentials.
        _write(run_dir/"raw_content.txt", backend.raw_content.replace(settings.api_key, "[REDACTED]"))
    metadata = backend.response_metadata if backend is not None else {}
    _write_json(run_dir/"response_metadata.json", metadata)
    report = {
        "model": settings.model,
        "model_call_attempts": backend.call_count if backend is not None else 0,
        "sdk_max_retries": 0,
        "automatic_check": "passed" if result is not None else "failed",
        "validation_scope": "schema, input identity and literal evidence quotes only",
        "error": failure,
        "semantic_review": "not performed by program",
    }
    if result is not None:
        _write_json(run_dir/"result.json", result)
    _write_json(run_dir/"report.json", report)
    return result, report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="One real splitting request using existing project model configuration; no retries.")
    parser.add_argument("--input", type=Path, default=BASE/"examples/input.json")
    parser.add_argument("--env-file", type=Path, default=PROJECT/".env.local")
    parser.add_argument("--run-dir", type=Path, required=True, help="New directory within variants/dnd_mem0_splitter/.")
    args = parser.parse_args(argv)
    try:
        result, report = run_once(args.input, args.env_file, args.run_dir)
    except ValidationError as error:
        print(json.dumps({"error": error.as_dict()}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    except OSError:
        print(json.dumps({"error": {"code": "artifact_io_error", "message": "Cannot create/write artifacts; inspect the new run directory. Do not repeat the model call."}}), file=sys.stderr)
        return 2
    if result is None:
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
