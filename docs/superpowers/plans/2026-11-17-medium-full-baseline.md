# Medium full local Mem0 baseline implementation plan

**Goal:** Run every Medium session with the local Mem0 v0.1.118 baseline and pinned Qwen snapshot, with credentials supplied locally and support for detached execution.

**Architecture:** Add an isolated profile and a sequential local runner using the original `Memory.add` and `Memory.search` methods. Save per-session artifacts and block unsafe automatic continuation after an interrupted session. Keep the existing evaluation code and its settings separate.

**Constraints:** Do not call model APIs or start the experiment during implementation. Keep native prompts and write logic untouched. Remove `OPENROUTER_API_KEY` after loading environment values. Use the Beijing workspace endpoint, default non-thinking mode, and the existing embedding model and dimensions.

- [ ] Write offline tests for configuration, environment precedence, complete session iteration, and interruption handling; confirm they fail before implementation.
- [ ] Implement the runner, profile and secret-free environment example; preserve source data and existing evaluation configuration.
- [ ] Document setup, `nohup`, monitoring, and interruption limits. Verify using offline tests and static checks only.
