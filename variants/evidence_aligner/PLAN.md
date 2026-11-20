# Evidence aligner implementation plan

Goal: align all supplied new units with the attributes of one old memory in one model request, preserving verbatim provenance and uncertainty. Scope ends before scope planning or Mem0 writes.

1. Test the public `align_evidence(old_units, new_units, source_texts)` contract, one-call behavior, JSON/ID/coverage/provenance validation, and malformed inputs using an offline backend.
2. Implement the aligner with existing splitter JSON parsing, relation-judge quote location, and existing Qwen configuration/client. Do not infer event dates from recording timestamps.
3. Adapt the previously fixed five cases, recording manual versus SimpleMem origins. Pass every fixed unit and the complete original session; add clearly identified unsplit source units for selected evidence that was absent from the old manual mapping.
4. Run offline tests and a no-network preflight, then run each case at most once with JSON mode, temperature zero, and retries disabled. Persist input, messages, raw provider response, parsing, all errors and coverage.
5. Independently inspect the five responses, especially completed job transition and simulated skydiving, and save a case-by-case semantic review without rewriting model outputs.

Review focus: wrong-side or wrong-unit citations, nonexistent or duplicated IDs, unexamined units, absent event dates, explicit correction versus future intention, and partial or failed provider responses.
