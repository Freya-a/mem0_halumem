# v9：面向局部修改的旧记忆拆分

本版本是当前后续实验的固定基线。提示词、入口、共享校验器及模型后端的文件指纹记录于 [`../../v9_baseline.sha256`](../../v9_baseline.sha256)；在 `variants/dnd_mem0_splitter/` 下运行 `sha256sum -c v9_baseline.sha256` 可检查文件是否变化。该清单是人工核验工具，不是运行时自动拦截，也不能锁定远端模型服务或 Python 依赖。

v9 以 `v8_v4_v7_combined/prompt.txt` 为基础，增加可独立修改或保留的事实拆分原则；保留原有语义关系、字段、旧记忆逐字引文和 `splitter.py` 校验器。必要的共享关系和限定应重复，不能安全拆开的因果、条件及析取应整体保留。模型结果仍须人工检查。

CLI 读取指定输入及 env 文件；固定 `qwen-plus-2025-12-01` 并发送 `enable_thinking=false`，SDK 不重试。

五案对照使用的其他配置为未显式指定 temperature 和 max_tokens、超时 180 秒；CLI 仍可能从 env 文件或进程环境读取这些可选参数。要比较同一配置，应检查实际请求和运行记录，而不是仅凭版本名判断。

```bash
python3 -B variants/dnd_mem0_splitter/prompt_versions/v9_local_update/v9_splitter.py --input <input.json> --env-file .env.local
```

Python 接口 `split_memory_v9(request, backend_factory)` 复用已有校验器，调用方负责传入模型和生成参数；CLI 对上述模型和参数有固定约束。仅验证结构与逐字引文，不能证明拆分完整或语义正确。

已知限制：v9 的职业复合声明没有分别定位雇主和职位；时间边界及引文支持范围仍须人工核查。不要把输出直接用作自动范围判断或 Mem0 写入依据。
