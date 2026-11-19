"""Offline replay and literal provenance audit, not semantic validation."""
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent.parent))
from splitter import MockBackend, ValidationError, _read_json, split_memory


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    completion = _read_json(ROOT / "batch_completion.json")
    runs, quote_rows = [], []
    for report in completion["reports"]:
        cid, version = report["case_id"], report["version"]
        directory = ROOT / "runs" / cid / version
        request = _read_json(directory / "input.json")
        replay, failure, candidate = None, None, None
        try:
            candidate = _read_json(directory / "raw_content.txt")
            replay = split_memory(request, MockBackend(candidate))
        except ValidationError as error:
            failure = error.as_dict()
        facts = candidate.get("facts", []) if isinstance(candidate, dict) else []
        fact_checks = []
        for index, fact in enumerate(facts):
            sources = {"memory:" + request["memory_id"]: request["memory_text"]}
            sources.update({"context:" + c["source_id"]: c["text"] for c in request.get("source_context", [])})
            checks = []
            for eindex, evidence in enumerate(fact.get("evidence", [])):
                quote = evidence.get("quote")
                source_key = str(evidence.get("source_type")) + ":" + str(evidence.get("source_id"))
                source = sources.get(source_key)
                check = {
                    "evidence_index": eindex, "source_type": evidence.get("source_type"),
                    "source_id": evidence.get("source_id"), "quote": quote,
                    "nonempty": isinstance(quote, str) and bool(quote.strip()),
                    "source_declared": source is not None,
                    "exact_substring": isinstance(quote, str) and bool(quote.strip()) and source is not None and quote in source,
                }
                checks.append(check)
                quote_rows.append({"case_id": cid, "version": version, "fact_index": fact.get("fact_index"), **check})
            memories = [c for c in checks if c["source_type"] == "memory"]
            fact_checks.append({
                "fact_index": fact.get("fact_index"), "consecutive_index": type(fact.get("fact_index")) is int and fact["fact_index"] == index + 1,
                "source_memory_id_match": fact.get("source_memory_id") == request["memory_id"],
                "memory_evidence_count": len(memories),
                "memory_id_and_quote_check": bool(memories) and all(c["source_id"] == request["memory_id"] and c["exact_substring"] for c in memories),
                "all_quotes_match": all(c["exact_substring"] for c in checks), "evidence_checks": checks,
            })
        passed = replay is not None
        assert passed == (report["automatic_check"] == "passed")
        result_path = directory / "result.json"
        assert result_path.exists() == passed
        if passed:
            assert replay == _read_json(result_path)
        audit = {
            "case_id": cid, "version": version, "program_status": "passed" if passed else "failed",
            "strict_JSON_and_existing_validator_replay": passed, "replay_error": failure,
            "saved_result_equals_replay": passed, "candidate_fact_count": len(facts),
            "accepted_fact_count": len(replay["facts"]) if passed else 0,
            "raw_response_preserved": (directory / "raw_content.txt").exists(),
            "memory_id_echo_matches_if_present": candidate.get("memory_id", request["memory_id"]) == request["memory_id"] if isinstance(candidate, dict) else False,
            "memory_text_echo_matches_if_present": candidate.get("memory_text", request["memory_text"]) == request["memory_text"] if isinstance(candidate, dict) else False,
            "facts": fact_checks, "semantic_correctness": "not determined by this audit",
            "failed_candidate_policy": "Raw response stays available; no result.json on failure, no evidence repair, no acceptance override.",
            "additional_real_model_calls": 0,
        }
        save(directory / "program_checks.json", audit)
        runs.append(audit)
    versions = {}
    for version in ("v3", "v4"):
        group = [a for a in runs if a["version"] == version]
        quotes = [q for q in quote_rows if q["version"] == version]
        versions[version] = {
            "case_count": len(group), "program_passed": sum(a["program_status"] == "passed" for a in group),
            "candidate_facts": sum(a["candidate_fact_count"] for a in group),
            "accepted_facts": sum(a["accepted_fact_count"] for a in group),
            "memory_evidence": sum(q["source_type"] == "memory" for q in quotes),
            "context_evidence": sum(q["source_type"] == "context" for q in quotes),
            "literal_quotes_total": len(quotes), "literal_quotes_passed": sum(q["exact_substring"] for q in quotes),
            "facts_with_memory_passed": sum(f["memory_id_and_quote_check"] for a in group for f in a["facts"]),
        }
    save(ROOT / "program_summary.json", {"versions": versions, "runs": runs, "additional_real_calls": 0})
    with (ROOT / "literal_quote_checks.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(quote_rows[0]))
        writer.writeheader()
        writer.writerows(quote_rows)
    print(json.dumps(versions, ensure_ascii=False))


if __name__ == "__main__":
    main()
