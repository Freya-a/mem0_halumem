# SimpleMem 代码来源与改造

- 作者仓库：<https://github.com/aiming-lab/SimpleMem.git>，本地 `../../external/SimpleMem/`，commit `db80b6a7c591e0ea730a058e9f5fc4eb06572299`。开始时 `git status --short` 无输出；未修改仓库。许可 MIT，Copyright (c) 2025 AIMING Lab；完整许可证见本目录 `LICENSE`。
- **直接摘取或改写的内容**：`simplemem/core/memory_builder.py` 的 `MemoryBuilder._build_extraction_prompt` 中任务描述及 complete coverage 等提示词措辞被摘取、改写到 `build_extraction_prompt`；`_generate_memory_entries` 的系统角色文本被复制到 `run_trial.py`。`simplemem/core/utils/llm_client.py` 的 `LLMClient.extract_json` 中空响应检查及 `json.loads` 直接解析的短代码段被保留；围栏解析是根据同一思路重写的简化实现，未直接复制作者的完整实现，也没有复用自动修复和片段搜索。
- **参考后重新编写，并非复制作者类或函数**：`simplemem/core/models/memory_entry.py` 的 `MemoryEntry` 启发了新 dataclass 中的 ID、陈述、实体和时间字段；新结构并未复制或导入作者的 Pydantic 类。`MemoryBuilder._parse_llm_response` 的解析后检查类型、逐条实例化思路启发了 `parse_and_validate`，但其实现是重新编写，并非复制或导入作者函数。新实现也未导入其向量库。因而，当前版本并未在结构化单元定义和响应解析流程上充分满足“实际复用作者代码并改造”的原始要求。
- **参考方法而非直接复用代码**：原作者用 OpenAI 兼容聊天接口发送 system/user 消息后解析 JSON；本目录实际调用使用项目的 medium-full 环境和 profile 加 OpenAI SDK，零自动重试，并保存调用记录。未使用原作者的滑动窗口、向量存储、检索器和其多层重试。
- **本任务新增**：旧记忆/上下文分源、逐字引文及多位置歧义、原文与 ID 一致性验证、未决问题、记录时间与事实有效时间区分、只消费一条旧记忆、完整试运行存档。去除原版提示词的强制消歧和绝对时间转换。逐字验证不证明语义忠实或完整。
