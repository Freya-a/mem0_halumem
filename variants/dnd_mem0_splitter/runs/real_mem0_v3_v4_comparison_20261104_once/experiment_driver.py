"""Isolated paired experiment; existing backend/parser/validator remain unchanged.

Exclusive marker/directories prevent accidental repeat calls. Never repair responses.
"""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE))
from real_backend import OpenAICompatibleBackend, load_model_settings, load_design_prompt
from splitter import ValidationError, split_memory, _read_json


def now():
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(path, content):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def save(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    settings = load_model_settings(BASE.parent.parent / ".env.local")
    assert settings.model == "qwen-plus"
    assert settings.generation == {} and settings.timeout == 180.0
    selected = _read_json(ROOT / "selection.json")["cases"]
    assert len(selected) == 11
    prompts = {v: (ROOT / "prompts" / (v + ".txt")).read_text() for v in ("v3", "v4")}
    hashes = {v: sha(p.encode()) for v, p in prompts.items()}
    assert sha(load_design_prompt(BASE / "DESIGN.md").encode()) == hashes["v3"]
    previous = _read_json(ROOT / "source_integrity.before.json")
    for name, expected in previous.items():
        assert sha(Path(name).read_bytes()) == expected, name
    for case in selected:
        data = (ROOT / "inputs" / (case["case_id"] + ".json")).read_bytes()
        assert sha(data) == case["input_sha256"]
    order = []
    for ordinal, case in enumerate(selected):
        for version in (("v3", "v4") if ordinal % 2 == 0 else ("v4", "v3")):
            order.append({"case_id": case["case_id"], "version": version})
    save(ROOT / "batch_attempt.json", {
        "started_at": now(), "order": order, "max_calls_total": 22,
        "max_calls_each": 1, "prompt_hashes": hashes,
        "configuration_names_and_sources": settings.provenance,
        "model": settings.model, "generation_parameters": settings.generation,
        "response_format": {"type": "json_object"}, "timeout_seconds": settings.timeout,
        "sdk_max_retries": 0, "http_follow_redirects": False,
        "unknown_service_parameters": ["default sampling parameters", "concrete model revision", "provider routing"],
        "request_contents": "Frozen version prompt + input JSON only. No review, gold labels or target-session evidence.",
    })
    journal = ROOT / "call_journal.jsonl"
    with journal.open("x", encoding="utf-8"):
        pass
    reports = []
    for position, item in enumerate(order, 1):
        case_id, version = item["case_id"], item["version"]
        directory = ROOT / "runs" / case_id / version
        directory.mkdir(parents=True, exist_ok=False)
        input_path = ROOT / "inputs" / (case_id + ".json")
        data = input_path.read_bytes()
        with (directory / "input.json").open("xb") as stream:
            stream.write(data)
        request = _read_json(input_path)
        prompt = prompts[version]
        assert sha((ROOT / "prompts" / (version + ".txt")).read_bytes()) == hashes[version]
        write(directory / "prompt.txt", prompt)
        save(directory / "attempt.json", {
            **item, "position": position, "started_at": now(), "model": settings.model,
            "max_model_calls": 1, "sdk_max_retries": 0, "http_follow_redirects": False,
            "generation_parameters": settings.generation, "response_format": {"type": "json_object"},
            "timeout_seconds": settings.timeout, "prompt_sha256": hashes[version], "input_sha256": sha(data),
        })
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**item, "position": position, "event": "starting", "at": now()}) + "\n")
            stream.flush()
        backend, result, failure = None, None, None
        try:
            backend = OpenAICompatibleBackend(settings, prompt)
            result = split_memory(request, backend)
        except ValidationError as error:
            failure = error.as_dict()
        finally:
            if backend is not None:
                backend.close()
        calls = backend.call_count if backend is not None else 0
        assert calls <= 1
        if backend is not None and isinstance(backend.raw_content, str):
            write(directory / "raw_content.txt", backend.raw_content.replace(settings.api_key, "[REDACTED]"))
        metadata = backend.response_metadata if backend is not None else {}
        save(directory / "response_metadata.json", metadata)
        report = {
            **item, "position": position, "finished_at": now(), "model": settings.model,
            "model_call_attempts": calls, "sdk_max_retries": 0,
            "automatic_check": "passed" if result is not None else "failed",
            "validation_scope": "schema, input identity and literal evidence quotes only",
            "error": failure, "semantic_review": "not performed by program",
        }
        if result is not None:
            save(directory / "result.json", result)
        save(directory / "report.json", report)
        with journal.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**item, "position": position, "event": "finished", "at": now(), "calls": calls,
                                     "automatic_check": report["automatic_check"]}) + "\n")
        reports.append(report)
        print(json.dumps({"position": position, "case_id": case_id, "version": version,
                          "calls": calls, "program": report["automatic_check"],
                          "facts": len(result["facts"]) if result is not None else None}), flush=True)
    save(ROOT / "batch_completion.json", {
        "finished_at": now(), "run_count": len(reports), "actual_calls": sum(x["model_call_attempts"] for x in reports),
        "passed": sum(x["automatic_check"] == "passed" for x in reports), "reports": reports,
    })


if __name__ == "__main__":
    main()
