# Execution ledger — PLAN.md

Ruling: 用户已明确授权设计、修改提示词和五次调用，按该请求连续执行，不追加设计确认关卡；取舍和结果保留为可审阅文件。

Ruling: 当前目录不是 Git 仓库；无法建立 worktree 或提交，改用两个全新目录、排他创建与 487 个既有文件的 SHA-256 基线隔离本次工作。风险是没有 Git 提交记录，由保存的原文、差异和哈希记录替代。

Pre-flight: Task 1 produces frozen prompt/input/selection consumed by Task 2; Task 2 produces untouched raw/report artifacts consumed by Task 3. No schema change or shared mutable production implementation.

Task 1: invocation safeguards RED (3 expected missing-driver failures) -> GREEN (3/3); three synthetic examples pass unchanged validator. Prompt and five inputs now frozen; full existing unit checks pending.

Task 1: complete — existing isolated unit suite 38/38, new invocation checks 3/3, original validator synthetic examples 3/3. Protected baseline 487/487 unchanged. Task 2: five-call batch started once, PTY session 25875; do not restart driver.

Task 2: complete — exactly five v5 requests, zero new v4 requests, zero retries. Program v4 5/5 with 18/18 literal quotes; v5 4/5 with 22/23 literal quotes. Sports rejected with quote_not_found and no result.json; preserved unmodified.

Task 3: 22 actual/candidate facts and 41 supports reviewed; full side-by-side report generated. Final read-only independent review dispatched.

Ruling: 设计/协议文件在请求前保存，但未单独记录请求前哈希；最终只声明提示词与输入的请求前哈希证据，设计/协议仅记录最终哈希，不补造历史冻结证明。风险是设计/协议缺少独立的请求前哈希标记，不影响已冻结模型输入的可核对性。

Final: fixed historical-pair reference ambiguity — reporting regression RED→GREEN, new suite 4/4 and existing suite 38/38. Model fields, frozen prompt, program outcomes and historical files unchanged.

Final: Ruling: 父亲 was 不足以证明状态终止、运动偏好 and prefers 无唯一因果附着，继续列待人工确认，不替用户确定。风险是两种关系解释尚未消歧。

Final: Ruling: 只报告现有 SDK/client 无重试；提供商内部重试和默认采样/具体模型修订不可由本地记录验证，明确未知，不声称全链路确定性。

Final: Ruling: 本轮提示词失误属于实验结果，不在看到输出后改写冻结 v5 或补跑；否则会破坏用户每例一次的实验边界。

Task 3: complete — one independent read-only review, one reporting correction pass, final existing 38/38 and new 4/4 tests pass. Final read-only checks verify 487/487 protected files unchanged and 5/0/0 v5/new-v4/retry counts. All outputs retained, no deferred minor findings.
