# Medium full evaluation integration plan

**Goal:** Collect native Mem0 results and session-time QA across all Medium data, then prepare and score complete inputs using the unchanged HaluMem evaluator.

**Architecture:** Keep the local Mem0 runner and official evaluator separate. An offline bridge verifies run completion, source data, update retrievals and all QA answers, then writes a fresh official directory. An explicitly invoked scoring command runs the official evaluator and exports the requested metric mapping.

**Constraints:** Use `qwen-plus-2025-12-01` for Mem0, QA and judging, preserving the existing QA/judge temperature and token settings and original evaluator; do not launch APIs or experiments during preparation. Preserve raw native outputs and isolate credentials. Reject incomplete or modified runs and protect existing evaluation directories.

- [x] Test incomplete/mutated input rejection, exact official packaging, all/valid mapping, and the default QA mode.
- [x] Implement the offline bridge and explicit scoring entry; reuse local credentials without printing them.
- [x] Verify the official scorer offline using representative inputs and fake model outputs; document manual background commands and limitations.
