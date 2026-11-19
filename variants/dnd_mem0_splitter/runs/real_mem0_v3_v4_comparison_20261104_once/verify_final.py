"""Read-only verification of history, calls, frozen prompts and report coverage."""
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent.parent
sys.path.insert(0, str(BASE))
from real_backend import load_model_settings, load_design_prompt
from splitter import MockBackend, _read_json, split_memory


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    previous = _read_json(ROOT / "source_integrity.before.json")
    for name, expected in previous.items():
        assert sha(Path(name)) == expected, name
    provenance = _read_json(ROOT / "source_provenance.json")["checkpoint_hashes_verified"]
    for name, expected in provenance.items():
        assert sha(Path(name)) == expected, name
    selection = _read_json(ROOT / "selection.json")["cases"]
    batch = _read_json(ROOT / "batch_completion.json")
    assert batch["actual_calls"] == batch["run_count"] == batch["passed"] == 22
    prompts = {v: sha(ROOT / "prompts" / (v + ".txt")) for v in ("v3", "v4")}
    assert prompts["v3"] == "28a8aec27d8e15c440ca3e1fb95c1dff3ad25eddb2e3c8cd7bb2700a3450731e"
    assert prompts["v4"] == "d9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3"
    assert hashlib.sha256(load_design_prompt(BASE / "DESIGN.md").encode()).hexdigest() == prompts["v3"]
    revision = BASE / "prompt_versions/v4_boundaries_20261104"
    assert sha(revision / "prompt.txt") == prompts["v4"]
    assert sha(revision / "parent_v3_prompt.txt") == prompts["v3"]
    example = _read_json(revision / "synthetic_example.json")
    split_memory(example["input"], MockBackend(example["output"]))
    start = _read_json(ROOT / "batch_attempt.json")
    journal = [json.loads(line) for line in (ROOT / "call_journal.jsonl").read_text().splitlines()]
    assert len(journal) == 44
    assert len({(e["case_id"], e["version"]) for e in start["order"]}) == 22
    for position, item in enumerate(start["order"], 1):
        events = [e for e in journal if e["case_id"] == item["case_id"] and e["version"] == item["version"]]
        assert [e["event"] for e in events] == ["starting", "finished"]
        assert events[1]["calls"] == 1
        assert events[0]["position"] == position == events[1]["position"]
    total_facts = total_quotes = 0
    review = _read_json(ROOT / "semantic_reviews.json")["cases"]
    for selected, reviewed in zip(selection, review):
        cid = selected["case_id"]
        assert cid == reviewed["case_id"]
        source_input = ROOT / "inputs" / (cid + ".json")
        assert sha(source_input) == selected["input_sha256"]
        if selected["cohort"] == "regression_7":
            assert source_input.read_bytes() == Path(selected["prior_input_source"]).read_bytes()
        for version in ("v3", "v4"):
            directory = ROOT / "runs" / cid / version
            assert (directory / "input.json").read_bytes() == source_input.read_bytes()
            assert sha(directory / "prompt.txt") == prompts[version]
            attempt = _read_json(directory / "attempt.json")
            assert attempt["model"] == "qwen-plus" and attempt["max_model_calls"] == 1
            assert attempt["generation_parameters"] == {} and attempt["sdk_max_retries"] == 0
            assert attempt["http_follow_redirects"] is False and attempt["timeout_seconds"] == 180.0
            assert attempt["response_format"] == {"type": "json_object"}
            result = _read_json(directory / "result.json")
            replay = split_memory(_read_json(source_input), MockBackend(_read_json(directory / "raw_content.txt")))
            assert replay == result
            semantic = reviewed["versions"][version]
            assert len(semantic["facts"]) == len(result["facts"])
            for fact, audit in zip(result["facts"], semantic["facts"]):
                assert fact["fact_index"] == audit["fact_index"]
                assert [e["evidence_index"] for e in audit["supports"]] == list(range(len(fact["evidence"])))
                total_facts += 1
                total_quotes += len(fact["evidence"])
            indices = {f["fact_index"] for f in result["facts"]}
            for unit in semantic["coverage_units"]:
                assert set(unit["raw_fact_indices"]) <= indices
                assert set(unit["contextualized_fact_indices"]) <= indices
        assert (ROOT / "reviews" / (cid + ".md")).exists()
    with (ROOT / "fact_review.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == total_facts
    with (ROOT / "supports_review.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == total_quotes
    settings = load_model_settings(BASE.parent.parent / ".env.local")
    all_new = sorted([p for p in ROOT.rglob("*") if p.is_file()] + [p for p in revision.rglob("*") if p.is_file()])
    secret = settings.api_key.encode()
    assert all(secret not in p.read_bytes() for p in all_new), "Secret found; value hidden."
    assert all(x not in (revision / "prompt.txt").read_text() for x in [c["memory_id"] for c in selection])
    verification = {
        "status": "passed", "existing_files_unchanged": len(previous),
        "historical_checkpoint_hashes_rechecked": len(provenance), "versions": prompts,
        "v3_default_DESIGN_unchanged": True, "paired_inputs_identical": 11,
        "original_regression_inputs_byte_identical": 7, "new_real_compound_inputs": 4,
        "real_model_calls": 22, "one_call_per_version_case": True, "sdk_retries": 0,
        "raw_responses_preserved": 22, "native_validator_offline_replay_passed": 22,
        "accepted_facts_reviewed": total_facts, "supports_reviewed": total_quotes,
        "CSV_coverage_verified": True, "synthetic_example_native_validation": "passed",
        "new_artifacts_secret_scan": "passed; secret values never printed",
        "additional_real_calls_for_verification": 0,
        "semantic_verdict": "AI preliminary only; awaiting human confirmation",
        "no_Mem0_or_KB_mutation_or_full_subset_execution": True,
    }
    save(ROOT / "final_verification.json", verification)
    paths = sorted([p for p in ROOT.rglob("*") if p.is_file()] + [p for p in revision.rglob("*") if p.is_file()])
    save(ROOT / "artifact_manifest.json", {str(p.relative_to(Path.cwd())): sha(p) for p in paths})
    print(json.dumps(verification, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
