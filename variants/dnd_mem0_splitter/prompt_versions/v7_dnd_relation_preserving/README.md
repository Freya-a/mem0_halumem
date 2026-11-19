# v7：保留关系的 DnD 风格旧记忆拆分器

v7 在一次模型调用中输出旧记忆的子事实和各自的去语境化版本；沿用 `raw_subfact`、`contextualized_subfact`、`evidence`、`pending_confirmations` 等旧基线字段。它借鉴 [DnDScore 论文](https://aclanthology.org/2025.emnlp-main.1205/) 的联合拆分与去语境化配对，不是论文提示词的逐字复现，也不是 DnDScore 评分器。

与 v6 相比，v7 明确要求事实正文保留原有因果、条件、时间和连接范围；保留原有谓词和情态，不从来源上下文引入额外行为；当连接无法安全拆分时保留关系段；每条引文必须连续逐字，未知事项不能与正文相矛盾。独立属性只在关系与限定不受损时拆开。提示词不能保证模型遵守这些要求，结构及逐字校验也不检查语义。

输入是 `memory_id`、`memory_text` 和可选 `source_context`；每个来源包含 `source_id`、`source_ref`、`text`，可选 `speaker`、`recorded_at`。新证据不作为拆分输入；调用方须确保来源与旧记忆实际有关。

从工作区根目录执行一次模型调用：

```bash
python3 -B system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v7_dnd_relation_preserving/v7_splitter.py \
  --input system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v6_dnd_paper_aligned/example_input.json \
  --env-file system/mem0_halumem_diagnosis/.env.local
```

复用已有 `real_backend.py` 的模型配置，需要 `openai` 和 `httpx`；实际发送完整输入到配置的模型服务。成功输出 JSON；失败向标准错误输出错误，不自动修补或重试。Python 接口为 `split_memory_v7(request, backend_factory)`，工厂接收 v7 提示词并返回后端 callable。返回值可作为 `relation_judge_v2.judge` 的 `split_result`，调用方仍须传 `source_context` 与 `new_evidence`；若 `facts` 为空，当前关系判断器会拒绝，需由调用方处理。

离线验证：

```bash
python3 -B -m unittest discover -s system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter/prompt_versions/v7_dnd_relation_preserving -p 'test_*.py' -v
```

结构通过不能证明事实语义、粒度、覆盖和依据正确。后续真实案例回归报告见对应的 `runs/v7_real_dev_20261109_01_once/REPORT.md`；v6 和原有默认入口均不改变。
