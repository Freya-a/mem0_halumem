# 本地最小案例运行报告

- 运行 ID：20261022T203207+0800_a40c12d5；状态 completed。
- 环境：Conda mem0_halumem，Python 3.11.17，mem0ai 0.1.118；pip check 通过。
- Mem0 加载路径：/Users/freya/Documents/git-folder/mem0_halumem_diagnosis/mem0_v0.1.118/mem0/__init__.py。
- 模型：qwen-plus / text-embedding-v4；百炼兼容接口，实测 Embedding 为 1024 维。接口未提供更具体的模型修订号。
- 数据：33,511,525 字节，逐行 JSON 解析通过，20 位不同用户、1,387 个会话；非空、非 HTML、非 Git LFS 指针。
- 固定用户：2f1f897e-d67f-dbc5-6a7b-b7634a9e294f。
- 会话原始位置 0、1，分别输入全部 12、8 条原始对话消息；未将标准记忆、persona 或问答答案用作输入。
- 会话 1：0 → 17 条记忆，ADD 17，UPDATE 0，DELETE 0；add 耗时 21.414 秒。
- 会话 2：17 → 29 条记忆，ADD 12，UPDATE 0，DELETE 0；add 耗时 29.971 秒。
- 最终：29 条记忆，实际 ADD 29 / UPDATE 0 / DELETE 0。
- 快照由分页 scroll、exact count、显式 limit 的 get_all 互相核对，未截断；add 返回、SQLite history 和最终磁盘状态一致。
- 持久化复核通过，SQLite integrity_check 为 ok。Qdrant 内存与磁盘浮点差异最大 2.98e-08，已修正初版核对过严的误报；原始错误日志保留并标记解决，模型调用及原生 Mem0 处理无错误。
- 接口报告 Token 用量（含接口测试）：LLM 7,805（输入 5,808 / 输出 1,997），Embedding 360。首次运行耗时 55.658 秒，离线核对耗时另见 summary.json。
- 没有 UPDATE；本次仅验证基础流程，不能据此判断更新保护效果。

复现新运行（新数据库，会调用模型）：

```sh
conda run -n mem0_halumem python scripts/local_smoke.py
```

仅离线核对本轮结果（不调用模型）：

```sh
conda run -n mem0_halumem python scripts/local_smoke.py --verify-run results/local_smoke/20261022T203207+0800_a40c12d5
```

完整依赖在 requirements-freeze.txt 和 conda-environment.yml；参数在 configuration.json / mem0_config.json；原始输入、返回、操作及全量快照在 selected_input.json 和 session_01/、session_02/；详细调用和用量见 api_calls.jsonl、summary.json。
