# SimpleMem 改造的独立旧记忆拆分器

输入为 `memory_id`（非空字符串）、`memory_text`（旧记忆原文）及 `source_context`（可选字符串或 null）。`build_extraction_prompt` 生成模型输入；`parse_and_validate(response, memory_id, memory_text, source_context)` 返回包含 `parsed` 原始解析对象、`validated_units`、`status`、`errors`、`warnings`、`quote_locations` 和 `semantic_check` 的校验记录。模型对象包含 `memory_id`、`original_text`、`units` 和 `unresolved`；每个单元包含 `unit_id`、`raw_statement`、`contextualized_statement`、`memory_quotes`、`context_quotes`、`entities`、`condition` 和 `valid_time`。引文位置为从零开始、右开区间的 Python 字符偏移，多次命中列出所有位置并标记待检查。

`passed` 仅表示程序可检查的结构和逐字引文通过，不代表语义正确；`needs_review` 表示存在未决事项或定位等警告；`failed` 表示解析、结构或引文检查失败。逐字命中不能证明子事实忠实、完整或无幻觉；必须逐案审核。空单元、缺字段、重复单元 ID 不视为成功。两种陈述不同但未给上下文引文时保守标记检查，不代表这种改写一定有问题。

依赖 Python、`openai` 和 `python-dotenv`。只运行离线测试：

```bash
python -m unittest discover -s variants/simplemem_mem0_splitter/tests -v
```

`run_trial.py` 读取项目的 medium-full 配置和环境，仅使用固定模型 `qwen-plus-2025-12-01`，不调用 embedding；SDK 的 `max_retries=0`。这是一次性试验：先保存完整输入和请求，再依次调用至多 5 次，遇到接口异常或返回模型不符立即停止；`run/manifest.json` 存在时拒绝再次运行。密钥只在本地运行中交给 SDK，不写日志。每个 `run/case_N.json` 保存完整输入、构造后的消息、原始响应、模型名、耗时、失败信息和校验结果；`run/cases.json` 保存完整案例和数据定位。运行将产生付费请求。

作者仓库、MIT 许可、具体复制改造的代码、仅参考的思路和新增功能详见 [SOURCE.md](SOURCE.md)。本程序不写 Mem0 或向量库，也不调用关系判断器。

实体字段的兼容解析：原始 `parsed` 保持模型返回不变；`entities` 中原有非空字符串保持不变，对含非空字符串 `name` 的对象，在 `validated_units` 中使用其名称字符串，并在 `entity_normalizations` 记录单元位置、原始完整对象及转换结果。每次对象转换产生待复核警告；原始对象的类型、依据等元信息只保存在原始解析结果和转换记录中，不写入 Mem0。没有可确认名称或类型不合要求的项仍报错；转换不证明名称、类型或依据的语义正确。逐字引文校验不受此兼容处理影响。
