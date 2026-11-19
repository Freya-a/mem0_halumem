# SimpleMem 来源记录

- 论文：*SimpleMem: Efficient Lifelong Memory for LLM Agents*（ICML 2026）。
- 作者仓库：https://github.com/aiming-lab/SimpleMem.git
- 本地路径：`external/SimpleMem/`。克隆前该目录不存在；从上述仓库直接克隆。
- 下载日期：2026-11-19（Asia/Shanghai）。
- 当前分支：`main`。
- 检出 commit SHA：`db80b6a7c591e0ea730a058e9f5fc4eb06572299`。
- 代码许可证：MIT License，Copyright (c) 2025 AIMING Lab；以 `SimpleMem/LICENSE` 为准。
- 克隆后 `git status --short` 无输出，工作区干净。
- 主包阅读路径：`simplemem/core/memory_builder.py` 中的 `MemoryBuilder` 对对话做滑动窗口处理，通过 LLM 提取结构化记忆并写入向量存储；`simplemem/core/models/memory_entry.py` 中的 `MemoryEntry` 定义记忆内容、关键词及时间、地点、人物、实体、主题等元数据。仓库还包含集成及参考副本。
- 范围：仅下载和检查源码，未安装依赖、运行模型或修改其他实验文件。核查下载规模时误发了一次 GitHub 仓库元数据 API 请求；未调用模型 API。
