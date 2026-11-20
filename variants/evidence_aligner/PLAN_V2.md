# Evidence aligner v2 plan

Goal: compare separately stated old and new claims, their targets and attributes, and the evidence for any claimed change; retain v1 and replay its exact saved inputs once each.

1. Add offline contract tests for claim-specific qualifiers, target and attribute fields, state-change evidence, exact quote locations, input coverage and malformed output.
2. Add a standalone v2 prompt and validator, reusing v1 input validation, exact quote provenance, JSON parser and the existing Qwen backend. Never change the model response to make validation pass.
3. Read each v1 artifact as the authoritative input; compare canonical hashes of the entire input, all three input components, and the exact user-message bytes before each call. Save prompt version and checks before a request.
4. Run each fixed case at most once with identical Qwen settings. Persist attempts, raw response, provider response, parsed result, validation and token usage; never retry.
5. Audit each original and v2 claim against the raw evidence, report structure separately from semantics, and identify both repairs and new errors.

The prior split limitations remain: only selected messages have input units, while the entire session remains contextual evidence. No scope computation or Mem0 write occurs.
