# 模块一：三案例范围判断重跑

2026-11-05 10:54:49–10:55:42（Asia/Shanghai）。复用 `scope_check_20261105_v2_prepared/` 中三例的旧记忆、新证据和既有 v4 拆分，实际发出 **6 次 SDK 请求**：每例一次事实范围判断、一次新增候选提取；0 次自动重试，0 次未明调用，0 次模型或解析失败。此次运行没有重新拆分，也没有写入 Mem0。新旧结果和机器可读的逐案并排数据分别位于各案例 `scope_result.json` 和 `comparison.json`。

**本轮实际运行的是 `judge_scope.py` 的范围判断，没有与原来的 `judge_v2.py` 区间流程串联。** 没有执行新的时间提取、真实 NLI、时间语义评估或事实对检查；也没有把原 v2 的模拟评估结果当成本轮真实模型输出。

本报告对照原 [v1 报告](../scope_check_20261105_v1/REPORT.md) 和已有人工核验记录所作的语义分析仅供用户复核，不代表用户已经确认本轮输出。人工核验内容没有进入任何本轮模型请求；v4 保存结果中原有的 `pending_confirmations` 是拆分模型生成的，不是人工标签。

## 逐案并排

| 案例 | v1 已保存结果 | 本次 `judge_scope` 结果 | 对照观察：待用户复核 |
|---|---|---|---|
| [晋升](promotion/comparison.json) | 整句 `confirm`，理由提到雇主与职位延续；没有分出修改和保护片段。 | 整句 `modify`，理由指出职位更新，同时提到公司不变；没有单独的 `protect` 项。 | **未分别列出职称修改和雇主保护**。相比 v1，这次给出了修改方向，但整句修改范围仍过宽，不能把理由中提到雇主不变当成明确保护计划。理由把 Director 说成已被取代，也需复核是否应保留其历史状态或兼容概括。新增候选引文是晋升原话；理由还涉及此前 Director 职位，该旧信息不在所引用的新片段内。 |
| [模拟跳伞](skydiving/comparison.json) | 整句 `modify`，把模拟体验作为削弱真实极限运动态度和风险顾虑的依据。 | 将不喜欢极限运动片段标为 `modify`；将受伤风险与安全承诺两段单独标为 `protect`。整体为 `involved`，没有任何 `confirm` 片段。 | **安全顾虑不再被整体标为修改，保护范围更明确；但未单列证据不足的真实活动态度。** 理由将模拟描述成低风险、无伤害或风险可忽略，原引文没有提供这些风险信息；还把模拟正面体验作为修改旧概括的理由，其范围是否成立需复核。安全优先的引文也不能单独证明旧因果关系得到强化。 |
| [职业历史](career_history/comparison.json) | 对旧职业历史标 `uninvolved` / `protect`；新增候选原文正确，但理由说到“创办或经营”咨询公司。 | 对旧职业历史标 `insufficient` / `confirm`；新增候选描述咨询公司获得首批客户、用户感到宽慰及其里程碑意义。 | 新增候选理由未再推断创办或经营，所列内容与引文表面一致。新事实判断没有提出修改旧职业史，但从 v1 的“未涉及／保护”转为“证据不足／确认”；新证据没有说明旧职位的时间或关系，对该状态差异仍需用户复核。旧上下文现在态与记忆过去态的对齐本来就有 v4 的待确认项，不能把它视为由新获客引文解决。 |

新旧引文在自动检查中均逐字属于对应来源。此检查只证明文本存在，不证明引文支持模型的动作、上下文解释、候选理由、风险估计或时间推断。三例所有结果均保留 `semantic_support: not_verified`；`protect` 不等于已确认有效，`modify` 也不是自动写入指令。

## 来源、配置和调用记录

[运行前核验](preflight.json)记录了三例记忆 ID、输入及拆分文件哈希、v4 原始请求／响应的一致性、判断器与运行器哈希。原运行的只读校验还核对了前快照、原始话语和 v4 提示词的来源哈希。执行前准备目录与旧运行匹配，执行后准备目录文件哈希保持不变；运行器只在本新目录写入输出。

- 模型：`qwen-plus`；生成参数 `{}`，由服务端默认；超时 180 秒；SDK `max_retries=0`，HTTP 重定向关闭。完整安全配置来源见 [run_config.json](run_config.json)。
- 判断提示版本：`scope_judge_20261105_v2`；[prompts.json](prompts.json) SHA-256 `569f7156e87637be76d6cfcd4023928773221cf9b725ff301b2e8b1cbcf1703b`；事实提示文本 UTF-8 SHA-256 `30b1852203c14c446562033ec6cba45ffe794dccc5bff58c0a3d1b2e7e8271c1`；候选提示文本 UTF-8 SHA-256 `d454456059d85d14631f016ebe7f7915b0f91b542b38b3e7a88cb467216bfb71`。
- 复用的 v4 提示词 SHA-256：`d9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3`；准备清单 SHA-256：`787d1b5f2c1796d0abdcc212895cd2d9dcc07314ce3a5a42afbfc7ddb55d6675`。
- 请求按以下顺序各实际调用一次；每个目录包含请求、原始模型 content、解析结果、响应元数据和 token 用量。原始 content 不是完整 HTTP 响应包。

| 编号 | 案例 | 阶段 | 实际 SDK 调用次数 | 结果 |
|---|---|---|---:|---|
| [01](calls/01_promotion_fact_judgment/) | 晋升 | 范围判断 | 1 | involved |
| [02](calls/02_promotion_new_candidates/) | 晋升 | 新增候选 | 1 | ok |
| [03](calls/03_skydiving_fact_judgment/) | 模拟跳伞 | 范围判断 | 1 | involved |
| [04](calls/04_skydiving_new_candidates/) | 模拟跳伞 | 新增候选 | 1 | ok |
| [05](calls/05_career_history_fact_judgment/) | 职业历史 | 范围判断 | 1 | insufficient |
| [06](calls/06_career_history_new_candidates/) | 职业历史 | 新增候选 | 1 | ok |

[call_journal.jsonl](call_journal.jsonl) 为请求前编号记录，[run_summary.json](run_summary.json) 汇总实际调用和状态。6 个响应均正常结束且可解析，因此本轮没有失败响应可保存。通过 [verify_run.py](verify_run.py) 的只读核验：逐个请求与准备输入、指定提示及保存结果一致，引文及输出结构检查通过，人工核验信息未混入实际请求；此脚本不核验语义。
