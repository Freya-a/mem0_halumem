# v6 DnD-aligned splitter implementation plan

Goal: provide a runnable, isolated, single-model-call memory splitter with paired atomic and decontextualized claims, compatible with existing relation judge input.

Architecture: reuse the existing splitter's request/response validation and backend boundary. A v6-specific prompt handles a full memory as the target and optional source_context as disambiguation context; the output directly uses the existing fact schema. An independent Python API and CLI bind the v6 prompt without changing existing entrypoints.

1. Write and run failing tests for paired result, prompt binding, literal provenance rejection, and invalid input handling.
2. Implement the prompt and entrypoint. No new-evidence input, automatic writes to Mem0, or changes to v3/v4/v5.
3. Run v6 tests and existing splitter, backend, and relation judge tests; document limitations and usage. No model-quality claims without a real semantic evaluation.
