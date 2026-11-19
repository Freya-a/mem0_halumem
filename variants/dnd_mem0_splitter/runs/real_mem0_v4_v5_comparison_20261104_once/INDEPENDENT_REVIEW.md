# Independent read-only final review

Reviewer: fresh-context agent `/root/v5_final_review`, using requesting-code-review; no network calls, configuration reads, subagents or file mutations.

## Returned verdict

Verdict: reporting correction required; experiment integrity passes review.

Critical: none.

Important:
- `COMPARISON_REPORT.md:387,391,398,403` carries historical “两版” statements into the current v4/v5 comparison. “Both have two facts” and “both cite only memory” are false for v5, which has three facts and context evidence. The source is historical-review reuse at `compile_reviews.py:163–172`. Minimal remedy: explicitly identify these statements as referring to historical v3/v4, including corresponding JSON/CSV review text. Preserve every model field, historical artifact, and frozen prompt; no rerun needed.

Minor: none.

Verified directly:
- Read all ten saved raw responses and corresponding inputs.
- All 487 protected-file hashes match.
- All five v5 prompt copies match the frozen revision; inputs match historical v4 byte-for-byte.
- Historical baseline copies match original artifacts.
- Five recorded v5 calls, zero new v4 calls/retries; guards prevent repeat execution before backend creation.
- All 22 facts and 41 evidence entries are preserved in comparison/review artifacts.
- Sports contains the sole nonliteral quote; its whole result remains rejected without `result.json`.
- Program outcomes remain separate from preliminary semantic judgments pending human confirmation.

The substantive semantic review is fair: it identifies the missing Persian `while` relationship, sports ambiguity and quote failure, father tense issue, yoga source limitations, and partner specialization overreach without confusing assistant attribution with user self-report.

Declined to judge:
- Whether father’s `was` entails an ended state; the evidence does not establish that.
- A unique causal attachment for sports `and prefers`; both readings remain possible.
- Provider-internal retries/defaults beyond the recorded client behavior.
- Expected prompt failures as implementation defects requiring prompt edits or reruns.

## Executor disposition

Confirmed the reporting defect against actual v5 artifacts. Added a reporting regression check, observed its failure, then explicitly qualified inherited pair references as historical v3/v4 before attaching actual model fields. Regenerated only new report/review artifacts; prior draft preserved in review_drafts/pre_review. No model response, tested prompt, input, program acceptance decision or protected historical file changed. No rerun requested.

Declined-to-judge rulings: keep father tense and sports causal attachment uncertain; record only observable SDK/client retry behavior and unknown provider defaults; preserve prompt failures as experiment observations without modifying/retesting the frozen prompt.
