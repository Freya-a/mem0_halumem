# v8：结合 v4 边界和 v7 关系约束的拆分器

v8 使用冻结 v4 提示词为基底，补充保留因果、条件、时间及 `while` 等关系的规则，并明确要求不把未决析取拆为两个确定分支。沿用 DnD 思路：一次模型调用为每个旧子事实生成一个去语境化配对；沿用现有 schema、ID、引文与待确认项。

输入为 `memory_id`、`memory_text` 和可选 `source_context`。每个上下文含 `source_id`、`source_ref`、`text`，可选 `speaker`、`recorded_at`；来源与记忆的关联由调用方提供。新证据不进入拆分器。输入输出与 `relation_judge_v2` 的 `split_result` 兼容；空 `facts` 当前需要由调用方单独处理。

运行（工作区根目录）：

```bash
python3 -B system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v8_v4_v7_combined/v8_splitter.py \
  --input system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v6_dnd_paper_aligned/example_input.json \
  --env-file system/mem0_halumem_diagnosis/.env.local
```

该命令向配置的模型服务发送输入，模型固定为 `qwen-plus-2025-12-01`，不受配置文件或进程环境中的模型名影响；服务地址、密钥及其他参数仍由配置提供。依赖现有 `openai`、`httpx` 与项目后端；无自动重试或修补。Python 接口 `split_memory_v8(request, backend_factory)` 接受调用方自定义的后端，其模型由调用方决定。原版本和默认入口不变。

测试：

```bash
python3 -B -m unittest discover -s system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v8_v4_v7_combined -p 'test_*.py' -v
```

现有校验只验证结构、ID 和逐字引文，无法保证事实原子性、完整性、逻辑关系、来源支持或现实真假。真实案例试验见 [回归报告](../../runs/v8_real_dev_20261109_01_once/REPORT.md) 与 [v4/v8 新案例对照](../../runs/v8_v4_unseen_cases_20261109_01_once/REPORT.md)；请先阅读限制，再决定如何使用结果。
