# 模块一：证据影响范围判断（scope v2）

本版本单独实现于 `judge_scope.py`，保留 `judge.py`、`judge_v2.py` 和旧运行。只接收已经保存的拆分结果，不调用拆分器、不写入记忆，也不实现时间提取、NLI 或区间实验。提示版本是 `scope_judge_20261105_v2`，这里的 scope v2 是三案例范围实验的版本名，与原有的时间判断 `judge_v2.py` 不是同一个实现。

## 变更与边界

- 要求对复合事实按原文顺序输出覆盖全部非标点文字的片段；每个片段同时输出含主语、条件和原有关系的 `contextualized` 候选、`modify` / `protect` / `confirm`、理由，以及分别列出的旧／新引文。`protect` 是保留供审查，不是已证实有效；`modify` 不是自动改写或事实已失效。片段可各自待确认或保护。
- 提示模型区分模拟和真实活动、一次体验与一般态度，保留未被新证据否定的风险顾虑及其因果关系；真实活动态度证据不足时待确认。不能把记录时间当事件时间。
- 新增候选仍以新来源原文为候选，提示要求其理由仅依该引文、保留限定条件，不能推断未陈述的创办行为等内容。原始引文存在性可程序检查，但理由、上下文表述以及语义是否真的受引文支持均只能人工核验。所有成功结果都标记 `semantic_support: not_verified`；这些提示不是语义验证器，不能保证模型不会越界。
- 逐事实状态区分 `involved`、`uninvolved`、`insufficient`、`model_failed` 和 `parse_failed`；后者包括模型内容解析／未正常结束或结构与引文验证失败，`error_type` 只保留安全的类别，不记录异常正文。失败保留旧事实，绝不计为已确认有效。新增候选的失败也与成功空数组区分。
- 旧引文必须对应该拆分事实已有的 `evidence`；新引文必须逐字属于指定的新来源。程序还检查片段顺序、覆盖和动作／状态的一致性。它不检查上下文表述是否忠实、语义支持、事实真伪或 v4 切分语义质量。

## 离线验证

在 `system/mem0_halumem_diagnosis` 下运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s variants/evidence_temporal_judge -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python variants/evidence_temporal_judge/runs/scope_check_20261105_v1/verify_run.py
```

本轮 43 项测试通过，包含模拟的部分影响、跳伞事实中待确认与安全保护并存、引文／覆盖失败、状态区分、旧候选越界理由仍为未验证，以及使用三个已保存 v4 结果的模拟运行。后者的 6 次是模拟函数调用，不是真实 SDK 请求。旧运行完整性脚本还核对了原三例来源、v4 提示词和 9 次旧 SDK 请求。模拟响应是手写的，测试只说明程序能接收并分类这些响应，**不说明模型会生成这些正确片段**；已保存的旧候选测试也刻意说明即使含有“founding”的理由，逐字引文检查仍会通过，必须人工复核。

## 已准备的三案例判断重跑

准备目录为 `runs/scope_check_20261105_v2_prepared/`；它复制原三例的模型输入、v4 结果、来源信息和 v1 判断／候选，记录每个文件 SHA-256 以及固定的 v4 提示词 SHA-256 `d9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3`，并记录两份实际判断提示。准备不调用模型。本轮实际新 SDK 调用次数为 **0**，尚无真实新模型结果或真实的 v1／新版本对照。

三例每例各 1 个已保存事实；将来执行至多 6 次 SDK 请求：3 次事实判断和 3 次新增候选，不做拆分、重试或重定向。准备时验证拆分结构；执行前检查副本和原目录哈希、提示词版本，输入改变则拒绝执行。执行时每次先落盘请求及编号，再保存可用的原始模型 content、响应元数据和解析结果，完成后按实际 SDK 调用数汇总；若进程中断而未生成汇总，须从日志核对，预留而无元数据的调用次数不明确。每案 `scope_result.json` 是新候选，`comparison.json` 并排保存 v1 与新版本结果并标记等待用户复核。模型配置及实际提示、调用次数会在执行时记录；不会保存 API 密钥。人工核验只在对照中引用旧报告，不进入模型请求。

真实重跑命令（会调用当前 `.env.local` 或环境中配置的模型，最多 6 次；只能执行一次）：

```bash
PYTHONDONTWRITEBYTECODE=1 python variants/evidence_temporal_judge/scope_run.py --execute variants/evidence_temporal_judge/runs/scope_check_20261105_v2_prepared
```

准备目录生成后，模型配置以实际执行时读取为准，并非假定与 v1 一致。结果的语义正确性和修改／保护范围仍须由用户逐案复核。
