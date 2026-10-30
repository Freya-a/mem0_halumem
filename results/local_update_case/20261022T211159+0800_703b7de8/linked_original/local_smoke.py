#!/usr/bin/env python3
"""Run exactly two HaluMem sessions through unmodified Mem0 0.1.118.

Run from the project root with:
  conda run -n mem0_halumem python scripts/local_smoke.py
Credentials are read locally; no credentials are written to results.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import importlib.metadata as md
import json
import logging
import math
import os
from pathlib import Path
import platform
import re
import shlex
import sqlite3
import subprocess
import sys
import threading
import time
import traceback
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_USER = "2f1f897e-d67f-dbc5-6a7b-b7634a9e294f"
DATE_FORMAT = "%b %d, %Y, %H:%M:%S"
SECRETS: list[str] = []


def clean(value):
    if isinstance(value, dict):
        return {k: ("<redacted>" if any(t in k.lower() for t in
                ("api_key", "authorization", "secret", "password")) else clean(v))
                for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, str):
        for secret in SECRETS:
            value = value.replace(secret, "<redacted>")
        return re.sub(r"\bsk-[A-Za-z0-9_-]+", "<redacted>", value)
    return value


def write_json(path, value):
    path.write_text(json.dumps(clean(value), ensure_ascii=False, indent=2, default=str) + "\n")


def sha256(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def usable(value):
    return bool(value and not re.fullmatch(r"[\s*<>]+", value) and not
                any(t in value.lower() for t in ("your_", "your-", "placeholder", "env:", "${")))


def read_env(path):
    result = {}
    if not path.exists():
        return result
    for n, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip().removeprefix("export ")
        if not line or line.startswith("#"):
            continue
        key, sep, raw = line.partition("=")
        if not sep or not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key.strip()):
            raise ValueError(f"Invalid environment assignment: {path}:{n}")
        tokens = shlex.split(raw, comments=True)
        if len(tokens) > 1:
            raise ValueError(f"Quote values containing spaces: {path}:{n}")
        result[key.strip()] = tokens[0] if tokens else ""
    return result


def load_settings(env_file=None):
    values, sources = {}, {}
    paths = ([Path(env_file).expanduser().resolve()] if env_file else
             [ROOT / "HaluMem/.env copy", ROOT / "HaluMem/.env", ROOT / ".env", ROOT / ".env.local"])
    if env_file and not paths[0].is_file():
        raise FileNotFoundError(f"Configuration file does not exist: {paths[0]}")
    for path in paths:
        for key, val in read_env(path).items():
            if usable(val):
                values[key], sources[key] = val, str(path)
    for key, val in os.environ.items():
        if usable(val):
            values[key], sources[key] = val, "process environment"
    aliases = {
        "LLM_BASE_URL": ("LLM_BASE_URL", "OPENAI_BASE_URL"),
        "LLM_API_KEY": ("LLM_API_KEY", "OPENAI_API_KEY"),
        "LLM_MODEL": ("LLM_MODEL", "OPENAI_MODEL"),
        "EMBEDDING_BASE_URL": ("EMBEDDING_BASE_URL",),
        "EMBEDDING_API_KEY": ("EMBEDDING_API_KEY",),
        "EMBEDDING_MODEL": ("EMBEDDING_MODEL",),
        "EMBEDDING_DIMS": ("EMBEDDING_DIMS",),
    }
    settings, provenance = {}, {}
    for target, names in aliases.items():
        for name in names:
            if usable(values.get(name)):
                settings[target] = values[name]
                provenance[target] = {"file": sources[name], "variable": name}
                break
    for key in ("LLM_API_KEY", "EMBEDDING_API_KEY"):
        if settings.get(key):
            SECRETS.append(settings[key])
    for key in ("OPENAI_MAX_TOKENS", "OPENAI_TEMPERATURE", "OPENAI_TIMEOUT"):
        if key in values:
            settings[key] = values[key]
            provenance[key] = {"file": sources[key], "variable": key}
    return settings, provenance, [key for key in aliases if key not in settings]


def inspect_data(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("Dataset missing or empty")
    with path.open("rb") as f:
        head = f.read(512).lstrip().lower()
    if head.startswith((b"<!doctype html", b"<html", b"version https://git-lfs.github.com/spec/v1")):
        raise ValueError("Dataset is HTML or a Git LFS pointer")
    ids, counts, first, blank = [], [], None, []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                blank.append(line_no)
                continue
            try:
                user = json.loads(line)
                uuid.UUID(user["uuid"])
                assert isinstance(user["sessions"], list)
            except Exception as exc:
                raise ValueError(f"Invalid dataset row {line_no}: {type(exc).__name__}") from exc
            if first is None:
                first = (line_no, user)
            ids.append(user["uuid"])
            counts.append(len(user["sessions"]))
    if not first or len(set(ids)) != len(ids) or blank:
        raise ValueError("Empty dataset, duplicate UUIDs or blank JSONL rows")
    report = {"file": str(path), "bytes": path.stat().st_size, "sha256": sha256(path),
              "all_lines_parse": True, "html_or_lfs": False, "blank_lines": blank,
              "users": len(ids), "unique_users": len(set(ids)), "sessions": sum(counts),
              "sessions_per_user": dict(zip(ids, counts)), "first_user_line": first[0]}
    return report, first[1]


def select_sessions(user):
    if user["uuid"] != EXPECTED_USER:
        raise ValueError("First user UUID changed; review the dataset before running")
    sessions = sorted(enumerate(user["sessions"]), key=lambda s: datetime.strptime(s[1]["start_time"], DATE_FORMAT))[:2]
    if len(sessions) != 2:
        raise ValueError("Two complete sessions are required")
    selected = []
    for index, session in sessions:
        dialogue = session["dialogue"]
        times = [datetime.strptime(m["timestamp"], DATE_FORMAT) for m in dialogue]
        if not times or times != sorted(times):
            raise ValueError("Dialogue timestamps are empty or out of order")
        if len(dialogue) != 2 * session["dialogue_turn_num"]:
            raise ValueError("Incomplete session: turn count mismatch")
        if times[0] != datetime.strptime(session["start_time"], DATE_FORMAT) or times[-1] != datetime.strptime(session["end_time"], DATE_FORMAT):
            raise ValueError("Incomplete session: time boundary mismatch")
        for message in dialogue:
            if message["role"] not in ("user", "assistant") or not isinstance(message["content"], str):
                raise ValueError("Unexpected role or nontext dialogue")
        selected.append({"original_session_index_zero_based": index, "start_time": session["start_time"],
                         "end_time": session["end_time"], "dialogue_turn_num": session["dialogue_turn_num"],
                         "raw_dialogue": dialogue,
                         "messages": [{"role": m["role"], "content": m["content"]} for m in dialogue]})
    return selected


def collect_points(client, collection, query_filter):
    points, offset, pages = [], None, 0
    while True:
        batch, offset = client.scroll(collection_name=collection, scroll_filter=query_filter,
                                      limit=64, offset=offset, with_payload=True, with_vectors=True)
        points.extend(p.model_dump(mode="json") for p in batch)
        pages += 1
        if offset is None:
            break
    count = client.count(collection_name=collection, count_filter=query_filter, exact=True).count
    if len(points) != count or len({str(p["id"]) for p in points}) != count:
        raise AssertionError("Paginated vector snapshot does not match exact database count")
    return sorted(points, key=lambda p: str(p["id"])), count, pages


def snapshot(memory, user_id):
    store = memory.vector_store
    query_filter = store._create_filter({"user_id": user_id})
    points, count, pages = collect_points(store.client, store.collection_name, query_filter)
    total = store.client.count(collection_name=store.collection_name, exact=True).count
    limit = max(1, count + 1)
    api = memory.get_all(user_id=user_id, limit=limit)
    api_points = api["results"]
    assert total == count, "Unexpected data from another user in this fresh collection"
    assert len(api_points) == count
    assert {str(p["id"]): p["memory"] for p in api_points} == {str(p["id"]): p["payload"]["data"] for p in points}
    return {"database_count_exact": count, "collection_count_exact": total, "scroll_page_size": 64,
            "scroll_pages": pages, "get_all_explicit_limit": limit, "not_truncated": True,
            "api_snapshot": api, "database_points_with_vectors": points}


def history_rows(path):
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute("SELECT rowid AS sequence, * FROM history ORDER BY rowid")]


def reconcile(before, after, history, add_return):
    state = {str(p["id"]): p["payload"]["data"] for p in before["database_points_with_vectors"]}
    for event in history:
        key = event["memory_id"]
        if event["event"] == "ADD":
            assert key not in state
            state[key] = event["new_memory"]
        elif event["event"] == "UPDATE":
            assert state[key] == event["old_memory"]
            state[key] = event["new_memory"]
        elif event["event"] == "DELETE":
            assert state.pop(key) == event["old_memory"]
        else:
            raise AssertionError("Unexpected history event")
    assert state == {str(p["id"]): p["payload"]["data"] for p in after["database_points_with_vectors"]}
    if add_return is not None:
        assert Counter((r["id"], r["event"]) for r in add_return["results"]) == Counter((r["memory_id"], r["event"]) for r in history)
    return {"history_replayed_matches_database": True, "return_matches_history": add_return is not None,
            "actual_operation_counts": dict(Counter(r["event"] for r in history))}


def verify_persistence(expected, persisted):
    """Compare exact IDs/payloads and cosine vectors within float32 precision.

    Qdrant local persists the input vector before normalizing its in-memory
    float32 copy; reopened vectors can differ by normal floating-point error.
    """
    assert len(expected) == len(persisted), "Persisted point count differs"
    old = {str(p["id"]): p for p in expected}
    new = {str(p["id"]): p for p in persisted}
    assert old.keys() == new.keys(), "Persisted point IDs differ"
    max_diff = 0.0
    for key, point in old.items():
        actual = new[key]
        assert {k: v for k, v in point.items() if k != "vector"} == {k: v for k, v in actual.items() if k != "vector"}, "Persisted payload/metadata differs"
        a, b = point["vector"], actual["vector"]
        assert len(a) == len(b), "Persisted vector dimension differs"
        assert all(math.isfinite(x) and math.isfinite(y) and math.isclose(x, y, rel_tol=1e-6, abs_tol=1e-7) for x, y in zip(a, b)), "Persisted vector differs beyond float32 tolerance"
        max_diff = max(max_diff, max((abs(x - y) for x, y in zip(a, b)), default=0.0))
    return {"ids_and_payloads_exact": True, "vector_relative_tolerance": 1e-6,
            "vector_absolute_tolerance": 1e-7, "max_vector_absolute_difference": max_diff,
            "count": len(persisted)}


def verify_existing_run(path):
    """Recheck a completed two-session run offline, without replaying model calls."""
    from qdrant_client import QdrantClient
    out = Path(path).expanduser().resolve()
    assert out.parent == (ROOT / "results/local_smoke").resolve(), "Use a run inside results/local_smoke"
    tick = time.perf_counter()
    report = json.loads((out / "summary.json").read_text())
    assert report["completed_sessions"] == 2, "Both sessions must already have finished"
    rows = history_rows(out / "history.db")
    for ordinal in (1, 2):
        folder = out / f"session_{ordinal:02d}"
        checks = json.loads((folder / "verification.json").read_text())
        assert checks["native_error_count"] == 0 and checks["add_error"] is None
        before = json.loads((folder / "before.json").read_text())
        after = json.loads((folder / "after.json").read_text())
        operations = json.loads((folder / "actual_operations.json").read_text())
        returned = json.loads((folder / "add_return.json").read_text())["return_value"]
        reconcile(before, after, operations, returned)
        assert before["not_truncated"] and after["not_truncated"]
    saved_rows = json.loads((out / "all_actual_operations.json").read_text())
    assert saved_rows == rows, "Actual database history changed"
    final = json.loads((out / "final_snapshot.json").read_text())
    client = QdrantClient(path=str(out / "qdrant"))
    try:
        persisted, count, pages = collect_points(client, "local_smoke", None)
        persistence = verify_persistence(final["database_points_with_vectors"], persisted)
        assert count == report["final_memory_count"]
    finally:
        client.close()
    with sqlite3.connect(f"file:{out / 'history.db'}?mode=ro", uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    errors = json.loads((out / "errors.json").read_text())
    assert all(e["message"] == "Final database verification failed" and "AssertionError" in e.get("traceback", "") for e in errors), "Unresolved errors other than the persistence comparison"
    for name in ("summary.json", "errors.json"):
        backup = out / name.replace(".json", ".initial.json")
        if not backup.exists():
            backup.write_text((out / name).read_text())
    write_json(out / "reopened_snapshot.json", {"database_count_exact": count, "scroll_pages": pages,
               "database_points_with_vectors": persisted, "persistence_comparison": persistence})
    for error in errors:
        error["resolved"] = True
        error["resolution"] = "Offline persistence verification passed with float32 vector tolerance and exact ID/payload equality. Initial overly strict vector comparison corrected; no model calls repeated."
    write_json(out / "errors.json", errors)
    report.update(status="completed", persistence_verified_after_reopen=True, persistence_comparison=persistence,
                  history_integrity_check="ok", verification_recovered=True,
                  verification_elapsed_seconds=time.perf_counter() - tick,
                  verification_harness_sha256=sha256(Path(__file__)))
    report.pop("persistence_error", None)
    report["update_protection_conclusion"] = "No UPDATE occurred. Only the basic pipeline was verified; update protection cannot be assessed." if not report["actual_operation_counts"]["UPDATE"] else "UPDATE occurred; this minimal smoke run alone does not establish update protection efficacy."
    write_json(out / "summary.json", report)
    command = "conda run -n mem0_halumem python scripts/local_smoke.py --verify-run " + shlex.quote(str(out))
    (out / "verify-existing.sh").write_text("#!/bin/zsh\nset -eu\ncd " + shlex.quote(str(ROOT)) + "\n" + command + "\n")
    print(json.dumps({"status": report["status"], "run_id": report["run_id"], "completed_sessions": 2,
                      "final_memory_count": count, "actual_operation_counts": report["actual_operation_counts"],
                      "persistence_comparison": persistence, "additional_model_calls": 0}, indent=2))
    return 0


class AuditHandler(logging.Handler):
    def __init__(self, path):
        super().__init__(logging.INFO)
        self.path, self.errors, self.phase = path, [], "setup"

    def emit(self, record):
        entry = {"time": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(), "phase": self.phase,
                 "level": record.levelname, "logger": record.name, "message": record.getMessage()}
        if record.exc_info:
            entry["traceback"] = "".join(traceback.format_exception(*record.exc_info))
        with self.path.open("a") as f:
            f.write(json.dumps(clean(entry), ensure_ascii=False) + "\n")
        if record.levelno >= logging.ERROR:
            self.errors.append(entry)


class APIAudit:
    """Observe SDK requests/responses, returning the original response untouched."""
    def __init__(self, path):
        self.path, self.phase, self.calls, self.lock = path, "preflight", [], threading.Lock()

    def wrap(self, resource, kind):
        original = resource.create

        def observed(*args, **kwargs):
            start = time.perf_counter()
            entry = {"kind": kind, "phase": self.phase, "request": kwargs}
            try:
                response = original(*args, **kwargs)
                body = response.model_dump(mode="json")
                if kind == "embedding":
                    body["data"] = [{"index": d["index"], "dimensions": len(d["embedding"]),
                                     "all_finite": all(math.isfinite(v) for v in d["embedding"])} for d in body["data"]]
                entry.update(status="ok", response=body)
                return response
            except Exception as exc:
                entry.update(status="error", error_type=type(exc).__name__, error=str(exc))
                raise
            finally:
                entry["elapsed_seconds"] = time.perf_counter() - start
                with self.lock:
                    self.calls.append(clean(entry))
                    with self.path.open("a") as f:
                        f.write(json.dumps(clean(entry), ensure_ascii=False, default=str) + "\n")
        resource.create = observed

    def summary(self):
        groups = {}
        for call in self.calls:
            group = groups.setdefault(f"{call['phase']}:{call['kind']}", {"calls": 0, "usage": {}, "models_returned": []})
            group["calls"] += 1
            response = call.get("response", {})
            model = response.get("model")
            if model and model not in group["models_returned"]:
                group["models_returned"].append(model)
            for key, val in (response.get("usage") or {}).items():
                if isinstance(val, int):
                    group["usage"][key] = group["usage"].get(key, 0) + val
        return {"groups": groups, "note": "Usage is provider-reported; unavailable fields remain absent. Hidden SDK retries are not counted separately."}


def save_dependencies(out):
    for name, command in {
        "requirements-freeze.txt": ["python", "-m", "pip", "freeze", "--all"],
        "pip-check.txt": ["python", "-m", "pip", "check"],
        "conda-environment.yml": ["conda", "env", "export", "-n", "mem0_halumem", "--no-builds"],
    }.items():
        # Explicit named environment even for subprocess Python commands.
        cmd = ["conda", "run", "-n", "mem0_halumem", *command] if command[0] == "python" else command
        done = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        (out / name).write_text(clean(done.stdout + done.stderr))
        if done.returncode:
            raise RuntimeError(f"Dependency check/export failed: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", help="Local env file; secrets never printed")
    parser.add_argument("--verify-run", help="Recheck an existing two-session result offline; no model calls")
    args = parser.parse_args()
    if os.environ.get("CONDA_DEFAULT_ENV") != "mem0_halumem" or sys.version_info[:2] != (3, 11):
        parser.error("Use conda run -n mem0_halumem python (Python 3.11)")
    if args.verify_run:
        return verify_existing_run(args.verify_run)
    run_id = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%dT%H%M%S%z") + "_" + uuid.uuid4().hex[:8]
    out = ROOT / "results/local_smoke" / run_id
    out.mkdir(parents=True, exist_ok=False)
    os.chmod(out, 0o700)
    os.environ["MEM0_DIR"] = str(out / "mem0_runtime")
    os.environ["MEM0_TELEMETRY"] = "False"
    audit = APIAudit(out / "api_calls.jsonl")
    log = AuditHandler(out / "runtime.jsonl")
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(log)
    for name in ("httpx", "httpcore", "openai"):
        logging.getLogger(name).setLevel(logging.WARNING)
    for name in ("runtime.jsonl", "api_calls.jsonl", "errors.json"):
        (out / name).touch()
    start = time.perf_counter()
    report = {"run_id": run_id, "status": "started", "completed_sessions": 0,
              "output_directory": str(out), "user_uuid": EXPECTED_USER, "sessions": []}
    memory = None
    print(f"RESULTS_DIR={out}", flush=True)
    try:
        settings, provenance, missing = load_settings(args.env_file)
        run_command = ["conda", "run", "-n", "mem0_halumem", "python", "scripts/local_smoke.py"]
        if args.env_file:
            run_command += ["--env-file", str(Path(args.env_file).expanduser().resolve())]
        (out / "reproduce.sh").write_text("#!/bin/zsh\nset -eu\ncd " + shlex.quote(str(ROOT)) +
            "\n# Fill local credentials before running. Each run gets fresh databases.\n" +
            "# Restore exact installed versions if needed:\n# " + shlex.join(["conda", "run", "-n", "mem0_halumem", "python", "-m", "pip", "install", "-r", str(out / "requirements-freeze.txt")]) +
            "\nconda run -n mem0_halumem python -m pip check\n" + shlex.join(run_command) + "\n")
        write_json(out / "configuration.json", {"settings": settings, "sources": provenance,
                   "missing_fields": missing, "provider": "openai (OpenAI-compatible API adapter)",
                   "infer": True, "custom_prompts": None, "graph_enabled": False,
                   "user_uuid": EXPECTED_USER, "vector_path": str(out / "qdrant"),
                   "history_db_path": str(out / "history.db"),
                   "dataset_facts_and_answers_used_as_input": False})
        import mem0
        from mem0 import Memory
        from mem0.memory.utils import remove_code_blocks
        environment = {"python": sys.version, "executable": sys.executable, "platform": platform.platform(),
                       "conda_environment": os.environ["CONDA_DEFAULT_ENV"], "mem0ai": md.version("mem0ai"),
                       "harness_sha256": sha256(Path(__file__)),
                       "mem0_file": mem0.__file__, "editable_install": json.loads(md.distribution("mem0ai").read_text("direct_url.json")),
                       "source_sha256": {p: sha256(ROOT / "mem0_v0.1.118" / p) for p in
                        ["mem0/memory/main.py", "mem0/memory/utils.py", "mem0/configs/prompts.py", "mem0/vector_stores/qdrant.py"]}}
        environment["source_git"] = {}
        for repo in ("mem0_v0.1.118", "HaluMem"):
            environment["source_git"][repo] = {
                "head": subprocess.check_output(["git", "-C", str(ROOT / repo), "rev-parse", "HEAD"], text=True).strip(),
                "tracked_diff": subprocess.check_output(["git", "-C", str(ROOT / repo), "diff", "--stat", "HEAD"], text=True).strip()}
        assert environment["mem0ai"] == "0.1.118"
        assert Path(mem0.__file__).resolve() == ROOT / "mem0_v0.1.118/mem0/__init__.py"
        assert environment["editable_install"]["dir_info"]["editable"]
        write_json(out / "environment.json", environment)
        save_dependencies(out)
        data_report, user = inspect_data(ROOT / "HaluMem/data/HaluMem-Medium.jsonl")
        write_json(out / "data_check.json", data_report)
        selected = select_sessions(user)
        write_json(out / "selected_input.json", {"user_uuid": user["uuid"], "dataset_line_one_based": data_report["first_user_line"], "sessions": selected})
        if missing:
            report.update(status="blocked_missing_configuration", missing_fields=missing, final_memory_count=0,
                          actual_operation_counts={"ADD": 0, "UPDATE": 0, "DELETE": 0})
            write_json(out / "preflight.json", {"llm": "not_attempted_missing_configuration", "embedding": "not_attempted_missing_configuration"})
            print("MISSING_CONFIGURATION=" + ",".join(missing), flush=True)
            return 2
        # Avoid this version's environment-based OpenRouter routing overriding explicit settings.
        os.environ.pop("OPENROUTER_API_KEY", None)
        llm = {"model": settings["LLM_MODEL"], "api_key": settings["LLM_API_KEY"], "openai_base_url": settings["LLM_BASE_URL"]}
        if "OPENAI_MAX_TOKENS" in settings:
            llm["max_tokens"] = int(settings["OPENAI_MAX_TOKENS"])
        if "OPENAI_TEMPERATURE" in settings:
            llm["temperature"] = float(settings["OPENAI_TEMPERATURE"])
        dims = int(settings["EMBEDDING_DIMS"])
        assert dims > 0
        config = {"version": "v1.1", "llm": {"provider": "openai", "config": llm},
                  "embedder": {"provider": "openai", "config": {"model": settings["EMBEDDING_MODEL"],
                     "api_key": settings["EMBEDDING_API_KEY"], "openai_base_url": settings["EMBEDDING_BASE_URL"], "embedding_dims": dims}},
                  "vector_store": {"provider": "qdrant", "config": {"collection_name": "local_smoke", "path": str(out / "qdrant"), "on_disk": True, "embedding_model_dims": dims}},
                  "history_db_path": str(out / "history.db")}
        write_json(out / "mem0_config.json", config)
        memory = Memory.from_config(config)
        assert not memory.enable_graph and memory.custom_fact_extraction_prompt is None and memory.custom_update_memory_prompt is None
        timeout = float(settings.get("OPENAI_TIMEOUT", 180))
        # Timeout is an SDK option, NOT an unsupported Mem0 config parameter.
        memory.llm.client = memory.llm.client.with_options(timeout=timeout)
        memory.embedding_model.client = memory.embedding_model.client.with_options(timeout=timeout)
        audit.wrap(memory.llm.client.chat.completions, "llm")
        audit.wrap(memory.embedding_model.client.embeddings, "embedding")
        preflight = {}
        for kind in ("llm", "embedding"):
            tick = time.perf_counter()
            try:
                if kind == "llm":
                    response = memory.llm.generate_response(messages=[{"role": "user", "content": 'Return a JSON object containing "ok": true.'}], response_format={"type": "json_object"})
                    assert json.loads(remove_code_blocks(response)).get("ok") is True
                else:
                    vector = memory.embedding_model.embed("Local interface validation.", "add")
                    assert len(vector) == dims and all(math.isfinite(v) for v in vector) and any(v != 0 for v in vector)
                preflight[kind] = {"status": "ok", "elapsed_seconds": time.perf_counter() - tick}
            except Exception as exc:
                preflight[kind] = {"status": "error", "elapsed_seconds": time.perf_counter() - tick, "error_type": type(exc).__name__, "error": str(exc)}
            write_json(out / "preflight.json", preflight)
        if any(v["status"] != "ok" for v in preflight.values()):
            raise RuntimeError("Interface validation failed; see preflight.json")
        assert snapshot(memory, EXPECTED_USER)["database_count_exact"] == 0
        for ordinal, session in enumerate(selected, 1):
            phase = f"session_{ordinal:02d}"
            audit.phase = log.phase = phase
            folder = out / phase
            folder.mkdir()
            write_json(folder / "input.json", session)
            before = snapshot(memory, EXPECTED_USER)
            write_json(folder / "before.json", before)
            old_history = history_rows(out / "history.db")
            calls_start, errors_start = len(audit.calls), len(log.errors)
            returned, add_error = None, None
            tick = time.perf_counter()
            try:
                returned = memory.add(session["messages"], user_id=EXPECTED_USER, infer=True)
            except Exception:
                add_error = traceback.format_exc()
                logging.getLogger(__name__).exception("Session add failed")
            elapsed = time.perf_counter() - tick
            write_json(folder / "add_return.json", {"return_value": returned, "error": add_error, "elapsed_seconds": elapsed})
            after = snapshot(memory, EXPECTED_USER)
            write_json(folder / "after.json", after)
            new_history = history_rows(out / "history.db")[len(old_history):]
            write_json(folder / "actual_operations.json", new_history)
            checks = reconcile(before, after, new_history, returned)
            llm_calls = [c for c in audit.calls[calls_start:] if c["kind"] == "llm"]
            assert llm_calls and all(c["status"] == "ok" for c in llm_calls)
            assert all(c["response"]["choices"][0]["finish_reason"] == "stop" for c in llm_calls), "Model output truncated or interrupted"
            facts = json.loads(remove_code_blocks(llm_calls[0]["response"]["choices"][0]["message"]["content"]))["facts"]
            assert isinstance(facts, list)
            if facts:
                assert len(llm_calls) == 2
                actions = json.loads(remove_code_blocks(llm_calls[1]["response"]["choices"][0]["message"]["content"]))["memory"]
                assert isinstance(actions, list)
            checks["native_error_count"] = len(log.errors) - errors_start
            checks["add_error"] = add_error
            checks["before_count"] = before["database_count_exact"]
            checks["after_count"] = after["database_count_exact"]
            checks["elapsed_seconds"] = elapsed
            write_json(folder / "verification.json", checks)
            report["sessions"].append(checks)
            assert not add_error and checks["native_error_count"] == 0, "Native errors recorded; session is not successful"
            report["completed_sessions"] += 1
            print(f"{phase}: memories {checks['before_count']} -> {checks['after_count']}; operations {checks['actual_operation_counts']}", flush=True)
        report["status"] = "completed"
    except Exception as exc:
        report.update(status="failed", error_type=type(exc).__name__, error=str(exc))
        logging.getLogger(__name__).exception("Smoke run failed")
        return 1
    finally:
        if memory is not None:
            try:
                final = snapshot(memory, EXPECTED_USER)
                write_json(out / "final_snapshot.json", final)
                rows = history_rows(out / "history.db")
                write_json(out / "all_actual_operations.json", rows)
                report["final_memory_count"] = final["database_count_exact"]
                counts = Counter(r["event"] for r in rows)
                report["actual_operation_counts"] = {k: counts[k] for k in ("ADD", "UPDATE", "DELETE")}
                # Close and reopen the persistent vector store to verify disk durability.
                memory.vector_store.client.close()
                from qdrant_client import QdrantClient
                reopened = QdrantClient(path=str(out / "qdrant"))
                try:
                    persisted, count, _ = collect_points(reopened, "local_smoke", None)
                finally:
                    reopened.close()
                report["persistence_comparison"] = verify_persistence(final["database_points_with_vectors"], persisted)
                report["persistence_verified_after_reopen"] = True
                with sqlite3.connect(out / "history.db") as db:
                    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
                report["history_integrity_check"] = "ok"
            except Exception as exc:
                report.update(status="failed", persistence_error=str(exc))
                logging.getLogger(__name__).exception("Final database verification failed")
            finally:
                memory.db.close()
                memory._telemetry_vector_store.client.close()
        report["elapsed_seconds"] = time.perf_counter() - start
        report["usage"] = audit.summary()
        if report["status"] != "completed":
            report["update_protection_conclusion"] = "Two-session smoke run did not complete; the pipeline and update protection are not verified."
        elif report.get("actual_operation_counts", {}).get("UPDATE", 0) == 0:
            report["update_protection_conclusion"] = "No UPDATE occurred. Only the basic pipeline was verified; update protection cannot be assessed."
        else:
            report["update_protection_conclusion"] = "UPDATE occurred; this minimal smoke run alone does not establish update protection efficacy."
        write_json(out / "errors.json", log.errors)
        write_json(out / "summary.json", report)
        print(json.dumps(clean(report), ensure_ascii=False, indent=2), flush=True)
    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
