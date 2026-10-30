# 五案例简单保护提示对照：运行失败记录

**结论：本次对照没有得到有效模型输出，无法判断简单保护提示的效果。** 2026-10-29 10:14（中国标准时间）五案分别执行一次 `Memory.add`，均在首次事实抽取请求时发生 `APIConnectionError`。底层 `httpx` 栈显示通过 HTTP 代理建立连接时 `Connection refused`；进程环境中 HTTP/HTTPS 代理设置为本机地址。每案独立副本的完整前后快照一致，history 无新操作。失败后的旧细节仍在仅反映未发生更新，不能视作保护提示成功。未修补或重试；原生基线未重跑。

## 五案例对照

原生列指原有一次已观察结果；简单提示列指这次失败后状态。引用的基线 `after.json` 是完整快照，各案复制目录含 `before.json`、`after.json`、`input.json`、`api_calls.jsonl`、`observations.jsonl`、`actual_operations.json`、`status.json` 和 `persistence.json`。原生判断 A/B/C 沿用 LLM 辅助、用户确认的[冻结定向复核](../human_review_packets/native_case_review_v1_20261028/README.md)；本次失败状态根据程序和快照记录判断，并非用户确认的效果评审。

| 案例 | 原生新信息与旧细节／状态 | 简单提示组：新信息、旧细节与状态 | 实际操作与计划（基线 → 本次） | 证据 |
|---|---|---|---|---|
| A | 保存团建模拟跳伞和开放态度；高受伤风险的具体历史理由部分损失，一般安全顾虑仍在；对所有极限运动的扩写需谨慎。 | 新会话未成功处理；旧高受伤风险仍在未改变的快照中，提示效果未知。 | ADD 5、UPDATE 15、DELETE 1、计划 NONE 1 → 无写入；无更新计划、抽取连接失败。 | [原生完整 after](../williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/after.json) · [本次状态](cases/A/status.json) · [本次快照](cases/A/after.json) · [操作](cases/A/actual_operations.json) |
| B | 保存波斯猫历史血统、王室关联和养护考虑；纪录片体验是否明确绑定待判。平静性情细节损失，优雅是否等价保留未知。 | 新会话未成功处理；旧波斯猫性情细节仍在未改变的快照中，提示效果未知。 | ADD 15、UPDATE 8、DELETE 0、计划 NONE 30 → 无写入；无更新计划、抽取连接失败。 | [原生完整 after](../williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_007/after.json) · [本次状态](cases/B/status.json) · [本次快照](cases/B/after.json) · [操作](cases/B/actual_operations.json) |
| C | 保存咨询公司获得首批客户；Blockchain Tech 历史雇主与高级开发职级损失，宽泛技术经历仍在。 | 新会话未成功处理；历史雇主与职级仍在未改变的快照中，提示效果未知。 | ADD 11、UPDATE 12、DELETE 0、计划 NONE 38 → 无写入；无更新计划、抽取连接失败。 | [原生完整 after](../williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_008/after.json) · [本次状态](cases/C/status.json) · [本次快照](cases/C/after.json) · [操作](cases/C/actual_operations.json) |
| 第 7 条 | 已保存转岗及改善的工作生活平衡；旧求职语句仍以现在时表述，未明确历史化，时间消歧待判。 | 新会话未成功处理；原求职状态留在未改变的快照中，新旧状态能否清楚表达未知。 | ADD 9、UPDATE 23、DELETE 0、计划 NONE 15 → 无写入；无更新计划、抽取连接失败。 | [原生完整 after](../williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_008/after.json) · [本次状态](cases/target_7/status.json) · [本次快照](cases/target_7/after.json) · [操作](cases/target_7/actual_operations.json) |
| 第 10 条 | 已保存最近晋升 Lead Director；旧 Director 表述未显式历史化。Director 可能是兼容的宽泛称谓，不能仅凭共存判错，时间消歧待判。 | 新会话未成功处理；原 Director 状态留在未改变的快照中，新旧状态能否清楚表达未知。 | ADD 12、UPDATE 14、DELETE 0、计划 NONE 25 → 无写入；无更新计划、抽取连接失败。 | [原生完整 after](../williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/after.json) · [本次状态](cases/target_10/status.json) · [本次快照](cases/target_10/after.json) · [操作](cases/target_10/actual_operations.json) |

基线 NONE 是模型计划中的不操作项，不是 DELETE 或失败；基线五案日志未记录 ERROR/WARNING。本次没有生成事实抽取结果或更新计划，因而不能把空计划称为模型选择跳过。每案 `status.json` 保存完整异常，`api_calls.jsonl` 包含开始与错误两条记录；未知是否实际到达远端，应以服务端账单为准。

## 配置与调用

已验证 `mem0ai==0.1.118` 使用 `custom_update_memory_prompt` **替换**默认更新提示；本次配置完整值逐字等于默认提示加冻结附加段。原始、对照和差异分别为 [original_update_prompt.txt](original_update_prompt.txt)、[control_update_prompt.txt](control_update_prompt.txt)、[prompt.diff](prompt.diff)，对照 SHA-256 为 `076baeb2afa9d8c4a0c87c7e24d7037a284793af17fc09e557ad08fbbb53389b`。只配置通用补充，不输入人工答案、保护候选或预期结果；抽取、top-5 检索、写库逻辑仍为原生。由于抽取失败，**实际更新模型输入未组装或发送**；不能宣称服务端使用了保护提示。五案源会话与独立复制备份分别校验，见 [preflight.json](preflight.json) 和各案 `preflight.json`。启动前核验了源代码、源备份、复制品、历史、向量、输入与凭据存在性；启动后复核五案源备份及基线引用文件哈希未变。

| 案例 | 本次 LLM SDK 尝试 / 成功 | 本次 embedding SDK 尝试 / 成功 | LLM 请求耗时（秒） | 本次服务返回 token / 费用 |
|---|---:|---:|---:|---|
| A | 1 / 0 | 0 / 0 | 0.00496 | 未返回 / 未知 |
| B | 1 / 0 | 0 / 0 | 0.00470 | 未返回 / 未知 |
| C | 1 / 0 | 0 / 0 | 0.00501 | 未返回 / 未知 |
| 第 7 条 | 1 / 0 | 0 / 0 | 0.00483 | 未返回 / 未知 |
| 第 10 条 | 1 / 0 | 0 / 0 | 0.00464 | 未返回 / 未知 |
| 合计 | **5 / 0** | **0 / 0** | — | 未返回 / 未知 |

调用的配置模型为 `qwen-plus` 和 `text-embedding-v4`（1024 维），temperature 0.5，max_tokens 16384，timeout 180 秒，SDK 重试 0；每案实际调用开始时间及错误见各案 `api_calls.jsonl`，会话耗时见 `status.json`。本次无模型返回值、版本、token 或费用，不能将未知用量当成零账单。原生五案共 LLM 10、embedding 147 次，服务返回的模型名称分别为 `qwen-plus` 和 `text-embedding-v4`，LLM 未返回 `system_fingerprint`；本次没有任何返回版本，无法确认同一后端版本。即使未来成功，模型别名可变、温度非零、历史调用与新调用有时间差，单次差异不能确定归因于提示。

这五案按既有表现定向选取，属于开发探索，不代表总体损伤率，也没有运行全数据集、官方全量评分、ACE 或新算法。修复代理或网络后若要继续，应先审阅失败记录，并以新的独立运行目录和明确的新运行记录开展；本次失败记录不得覆盖或静默重放。
