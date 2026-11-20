# Evidence aligner v3 implementation plan

**Goal:** preserve the five paired inputs and Qwen snapshot while reducing generated paraphrases, binding scope qualifiers to quoted assertions, and distinguishing structural defects, evidence gaps, and human semantic findings.

**Design / architecture:** Each record links old/new unit ID arrays, one attribute, one relation type, and verbatim quote strings on each side. Independent new assertions have no old IDs or quotes. A unit can occur in several records. Qualifiers carry side, kind, exact qualifier and exact claim anchor; their sources are resolved from linked units and citations. Source IDs and offsets are program-derived only when there is one possible source; ambiguous provenance is reported, never guessed. Preserve the untouched parsed and raw model output alongside the derived result. The validator reports missing/invalid citations, unknown and uncovered IDs, reported missing evidence and semantic-review flags separately. Semantic entailment and qualifier scope are not represented as automatically proven.

**Constraints:** Existing v1/v2 code and inputs remain unchanged. Five v3 requests at most and exactly one attempt per case, no retry, qwen-plus-2025-12-01, temperature 0, JSON mode, 8192 max tokens. Before each request compare the full input and the exact user-message bytes against both v1 and v2. Save requests, raw/provider responses, usage, validator output, source mapping audit, frozen code, attempts and hashes. Do not write memories.

## Review focus

- Claim anchor/qualifier side, source and literal provenance; context qualifiers outside the cited unit must be flagged for human review.
- Same fragment present in multiple sources must produce ambiguity, no arbitrary source ID.
- Invalid or missing per-unit quotes must not count as successfully handled coverage.
- Compound units may be cited by several records; mention coverage does not prove assertion coverage.
- Actual old/new evidence, not the recording timestamp, must justify each relation; program checks cannot establish semantic entailment.

## Tasks

1. Record reproducible v2 offline validator results and manually inspect every raw response; document all error codes, dependent errors, prompt/schema mismatches, known semantic problems and input provenance.
2. Write meaningful offline tests first for source resolution and ambiguity, claim anchor and qualifier provenance, uncovered units, malformed JSON, independent new claims, compound units, evidence gaps and one-call behavior. Implement `aligner_v3.py` and a prompt with concrete valid JSON examples. Run v1/v2/v3 tests.
3. Add a paired runner that verifies both earlier versions' exact inputs/user messages, freezes code, persists artifacts incrementally and records usage and attempt counts. Preflight and dry-run locally; replay v2 responses through a separate diagnostic adapter only where transformation is explicit and auditable, never silently fixing model claims.
4. After offline diagnosis and verification, call the same snapshot once per case; audit each response against selected user quotes and compare the three named error families plus other errors, omissions and unresolved judgments. Report actual attempts and usage, plus tests and limitations.
