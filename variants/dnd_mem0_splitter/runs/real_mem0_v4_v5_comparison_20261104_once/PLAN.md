# v5 Prompt and Five-Case Comparison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 冻结兼容 v4 的 v5 提示词，对指定五例各调用一次，并保存可核对的历史 v4/v5 对照。

**Architecture:** 只增加两个目录中的实验材料；复用现有 real_backend 和 splitter。历史 v4 不请求，v5 结果不得修补；程序检查与语义初审分开。

**Tech Stack:** Python 标准库、现有 OpenAI-compatible backend、现有 JSON 校验器。

**Spec:** ../../prompt_versions/v5_granularity_relations_20261104/DESIGN.md

## Global Constraints

- 新请求仅五个：运动偏好、波斯猫照料、父亲资料、瑜伽、伴侣资料；每个 v5 一次，共最多五次。v4 只复制历史响应，零新请求。
- SDK max_retries=0，HTTP follow_redirects=False；显式 generation_parameters={}，timeout=180 秒，qwen-plus。
- 不修改 parser/validator、默认 DESIGN、Mem0、历史结果；不写知识库，不运行完整开发子集。
- 失败保留原响应和诊断，不补引文、不修 JSON、不标成成功、不再次发送。

## Review Focus

- 重复执行批次或单例必须在发送请求前被排他标记拒绝。
- 引文错误必须保留失败候选，不能写 result 或自动重试。
- 输入、提示词和历史 v4 复制件必须与冻结来源字节一致。
- 正文必须保留关系与限定，不能因逐字引文通过而认定语义通过。
- 单条 supports 不得借用另一来源或把助手表述变成用户自述。

## Task 1: Freeze prompt and offline invocation checks

**Files:** prompt version directory; test_experiment_driver.py; experiment_driver.py; selection.json; source_integrity.before.json.

**Interfaces:** execute_case(root, case_id, input_bytes, prompt, settings, backend_factory) saves exclusive run evidence and returns a report; existing split_memory remains unchanged.

- [ ] Write and run offline tests for repeat rejection and invalid-quote failure preservation; observe failure before driver implementation.
- [ ] Implement only the isolated invocation wrapper, freeze v5 from v4 with diff/revision and synthetic examples, copy exact five inputs and historical v4 artifacts.
- [ ] Run the three local harness checks and existing isolated splitter/backend unit tests, with bytecode disabled; inspect output.

## Task 2: Five real calls and offline provenance audit

**Files:** batch_attempt.json; call_journal.jsonl; runs/*/v5/*; batch_completion.json; program_summary.json.

**Interfaces:** frozen selection and prompt -> exactly one existing backend invocation per selected case; saved raw -> original MockBackend replay, zero new requests.

- [ ] Confirm frozen hashes, existing-file hashes, five-case allowlist and historical explicit settings before any request.
- [ ] Execute batch once; inspect call counts and failures; do not retry.
- [ ] Recheck schema, IDs, literal quotes and saved result equality offline for both versions.

## Task 3: Semantic comparison and final review

**Files:** semantic_reviews.json; COMPARISON_REPORT.md; final_verification.json; progress.md.

**Interfaces:** original raw responses + program audit -> per-fact/per-quote semantic review and side-by-side report.

- [ ] Review all facts and supports for granularity, coverage, connections, raw boundaries, source roles and pending consistency; label every conclusion pending human confirmation.
- [ ] Generate comparison from actual saved fields, preserving failures and all original pending entries.
- [ ] Dispatch one read-only final reviewer per requesting-code-review; no model requests, configuration reads or file mutations by reviewer.
- [ ] Verify five actual requests, immutable prompt/input hashes, report extraction and all protected historical hashes; report practical limits.
