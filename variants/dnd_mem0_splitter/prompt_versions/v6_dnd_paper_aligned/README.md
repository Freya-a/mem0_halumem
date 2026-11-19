# v6：DnD 思路的旧记忆拆分对照版本

v6 以 [DnDScore 论文](https://aclanthology.org/2025.emnlp-main.1205/) 中的 DnD 联合提取为思路：一次模型调用为每个子断言生成对应的去语境化版本。论文的目标是段落中的一个句子；这里的目标是一整条可能包含多个句子的 `memory_text`，可选 `source_context` 用来理解与消歧。这是针对记忆任务的改写，不是论文的原始提示词或 DnDScore 真假评分器。

字段直接采用现有基线，避免再做字段映射：

- `raw_subfact` 对应论文的子断言，只从目标旧记忆提取；可以恢复记忆内部明确共享的成分。
- `contextualized_subfact` 对应其去语境化版本；只从旧记忆和已有来源上下文补充理解该子断言所需的信息。缺少依据时保留原文并在 `pending_confirmations` 标记。
- `evidence` 保存 memory/context 的逐字引文及局部支持说明；`source_memory_id`、`fact_index` 与旧基线兼容。

新证据不输入拆分器。后续关系判断时，调用方把本模块的返回值作为 `split_result`，把原始 `source_context` 和需要比较的 `new_evidence` 分别传给 `evidence_relation_judge/part1_relation_judge/relation_judge_v2.py`。如果原记忆没有可陈述的事实，拆分结果可为 `facts: []`；当前关系判断器要求非空事实，调用方需单独处理空结果。

## 使用

在工作区根目录运行一次真实模型调用（将配置路径替换为你自己的现有配置）：

```bash
python3 -B system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v6_dnd_paper_aligned/v6_splitter.py \
  --input system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v6_dnd_paper_aligned/example_input.json \
  --env-file system/mem0_halumem_diagnosis/.env.local
```

配置和模型调用复用 `real_backend.py`，需要已安装 `openai`、`httpx`；模型成功时只向标准输出打印结果 JSON，校验或调用失败时向标准错误输出错误并返回非零状态，不修复输出或自动重试。每次命令会向配置的服务发送完整输入；自行选择是否保存输出。

输入为 JSON：`memory_id`、`memory_text` 必填；`source_context` 可省略，每项需有 `source_id`、`source_ref`、`text`，可选 `speaker`、`recorded_at`。来源与旧记忆是否真正关联由调用方提供和核实。

也可以导入 `v6_splitter.split_memory_v6(request, backend_factory)`。工厂接收 v6 提示词并返回接受请求、返回 JSON 对象的 callable；函数在返回或校验失败后调用 backend 的 `close()`（如果有）。现有 `OpenAICompatibleBackend` 可作为工厂创建的后端。

## 检验范围

```bash
python3 -B -m unittest discover -s system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v6_dnd_paper_aligned -p 'test_*.py' -v
```

程序复用原校验器，检查结构、原始输入的 ID、每条记忆引文和上下文引文的逐字归属。它不能证明原子性、覆盖率、原文关系、消歧和支持说明的语义正确，也不能保证模型一定遵守提示词。一次合成样例通过不构成质量或稳定性评估；应使用未参与提示词设计的案例与 v4/v5 做语义对照。保留原有默认入口和其他版本不变。
