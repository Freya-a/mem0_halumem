# STALE / CUPMem 来源记录

核查日期：2026-11-09（Asia/Shanghai）。

- 论文：STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?，https://arxiv.org/abs/2605.06527 。论文附录 G 明确将 https://github.com/icedreamc/STALE 列为代码地址，说明匿名发布了 CUPMem 实现。
- 仓库：`STALE/`，origin 为 https://github.com/icedreamc/STALE.git；本次检查前 external 下未发现 STALE/CUPMem 目录或相应现有 git remote，随后克隆。
- 检查时 HEAD：`ea7d391103a151927cd29d2f01d87597a782bdcb`；克隆后 `git status --short` 无输出。
- 代码许可证：MIT，Copyright (c) 2026 Hanxiang Chao；见 `STALE/LICENSE`。论文附录列出的数据集许可证为 CC BY 4.0，与代码许可证分别记录。
- 关键阅读路径：`cup_mem/memory/models.py`、`memory/schema.py`、`write/writer.py`、`write/delta_extractor.py`、`write/update_resolver.py`、`write/invalidation_resolver.py`、`write/invalidation_lanes.py`、`write/invalidation_judge.py`、`write/stale_linker.py`、`store_layer/in_memory.py`、`store_layer/transitions.py`、`prompt_lib/templates.py`。
- 范围：只检查源码，未执行 CUPMem、调用模型、写入 Mem0 或运行完整开发子集。原代码的状态更新以 `ProfileItem.value` 整条为单位，不保证复合文本内部其他事实的原子保护。

## TrustMem 来源核查

指 Tianyu Yang 等人的 *TrustMem: Learning Trustworthy Memory Consolidation for LLM Agents with Long-Term Memory*（arXiv:2606.25161），https://arxiv.org/html/2606.25161 。截至本次核查，论文 HTML 正文及作者主页 https://tianyu-yang-anna.github.io/ 均未发现该论文的作者代码仓库链接；搜索未找到可确认作者来源的实现。结论：**暂未找到**。未下载同名其他项目；这不证明作者代码不存在或将来不会公开。
