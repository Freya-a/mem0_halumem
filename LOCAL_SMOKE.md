# Mem0 0.1.118 + HaluMem 本地最小案例

在项目根目录运行。所有 Python 和 pip 命令都通过 `conda run -n mem0_halumem` 执行。

## 环境

本轮已创建 `mem0_halumem`，Python 3.11.17；执行过：

```sh
conda create -n mem0_halumem python=3.11 pip -y
conda run -n mem0_halumem python -m pip install -e ./mem0_v0.1.118
conda run -n mem0_halumem python -m pip check
```

`mem0ai` 实际版本为 0.1.118，editable 安装指向当前 `mem0_v0.1.118`，`mem0.__file__` 指向该目录的 `mem0/__init__.py`。没有修改 Mem0 或 HaluMem 源码。

## 本地接口配置

初始发现 `HaluMem/.env copy` 的 `OPENAI_API_KEY`、`OPENAI_BASE_URL` 是占位值；其中模型名为 `gpt-4o`。OpenMemory JSON 中的 key 为 `env:` 引用，相应环境变量没有设置，不能作为可用凭据。随后按用户指定配置了阿里云百炼：LLM 为 `qwen-plus`，Embedding 为 `text-embedding-v4`，维度 1024，两个接口均为 `https://dashscope.aliyuncs.com/compatible-mode/v1`。真实凭据只保存在权限 0600 的 `.env.local`，该文件被 Git 忽略。

`.env.local` 已配置；若在其他机器复现，填写下列项目。两个接口使用该版本自带的 `openai` 适配器，因此需要 OpenAI-compatible 的 Chat Completions 和 Embeddings 接口。模型名称必须填写你已有接口实际支持、且希望本轮使用的名称。脚本不自动替换模型，也不探测其他模型。

```dotenv
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=
EMBEDDING_DIMS=
```

请仅在本地文件填写密钥。若两个接口共用 URL 或 key，仍需将对应字段分别填写。Embedding 维度须与指定模型及接口支持的 `dimensions` 参数一致。脚本将分别验证 JSON 模式的 LLM 调用和 Embedding 调用，验证失败就停止输入数据。

默认按 `HaluMem/.env copy` → `HaluMem/.env` → `.env` → `.env.local` 读取，后者覆盖同名字段，进程环境变量优先。LLM 还兼容 `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL`；Embedding 字段需显式设置。支持标准单行 `KEY=value`，含空格的值需加引号，不执行 shell 代码。

可选 `OPENAI_MAX_TOKENS`、`OPENAI_TEMPERATURE`、`OPENAI_TIMEOUT` 沿用已有文件配置；当前 HaluMem 文件对应值是 16384、0.5、180。前两项是该版本支持的 Mem0 配置，timeout 通过 SDK 的 `with_options` 设置，不作为不受支持的 Mem0 参数传入。

## 执行与复现

```sh
conda run -n mem0_halumem python scripts/local_smoke.py
```

使用其他已有本地配置文件时：

```sh
conda run -n mem0_halumem python scripts/local_smoke.py --env-file /absolute/path/to/config.env
```

`--env-file` 只读取指定文件及进程环境变量。每次执行都新建 `results/local_smoke/<run_id>/`；不会复用先前记忆。退出码 0 表示两个会话完成且核对通过，2 表示缺少配置，1 表示调用、数据或核对失败。缺配置时也保存环境、依赖、数据检查及选中的原始输入。

每个运行目录含 `reproduce.sh`、`requirements-freeze.txt`、`conda-environment.yml`、`pip-check.txt`。`reproduce.sh` 中保留本次参数及恢复精确 pip 版本的命令。首次创建环境才运行 `conda create`，已有环境直接复用。

## 数据与输入边界

数据文件 `HaluMem/data/HaluMem-Medium.jsonl` 为 33,511,525 字节，可逐行解析，20 位不同用户、1,387 个会话，非空文件、HTML 或 Git LFS 指针。脚本每次重新检查并保存 SHA-256。

固定首位用户 UUID：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f`。按 `start_time` 排序选前两个完整会话；原文件位置为从 0 开始的 0、1：

| 会话 | 原始开始时间 | 原始结束时间 | 对话消息数 |
| --- | --- | --- | --- |
| 1 | Sep 04, 2025, 18:42:18 | Sep 04, 2025, 21:12:18 | 12 |
| 2 | Sep 05, 2025, 22:32:20 | Sep 06, 2025, 01:02:20 | 8 |

每个完整会话只调用一次 `Memory.add(messages, user_id=UUID, infer=True)`。输入严格取原始 `dialogue` 的 `role` 和 `content`，保留全部用户和助手消息及原始顺序。不读取 persona、标准 memory_points、original_memories 或问答答案作为输入或预填记忆，也不注入额外系统提示。原始时间戳另存为证据；Mem0 写入时间保持该版本原生运行时行为。

## 核对与产物

- `environment.json`、`configuration.json`、`mem0_config.json`：版本、加载路径、来源、模型、源码哈希、配置；密钥脱敏。`mem0_config.json` 仅在配置完整时生成。
- `data_check.json`、`selected_input.json`：全文件检查、固定用户、会话位置及完整原始对话。
- `preflight.json`、`api_calls.jsonl`：两个接口的实际验证结果、调用耗时、请求和原生响应。LLM 响应保留模型返回名称、finish_reason、usage 等；Embedding 响应记录维度、有限性及 usage，不重复存储向量。
- `session_01/`、`session_02/`：`input.json`、`add_return.json`、`before.json`、`after.json`、`actual_operations.json`、`verification.json`。
- `qdrant/`、`history.db`、`mem0_runtime/`：该次独立本地向量数据、操作历史及运行配置；关闭图记忆和遥测。
- `final_snapshot.json`、`all_actual_operations.json`、`summary.json`、`runtime.jsonl`、`errors.json`：最终状态、实际操作、汇总及错误。

全量快照直接对 Qdrant 按 64 条分页 scroll 到 offset 为空，携带完整 payload 和向量，再与 exact count 比较；`Memory.get_all` 显式设为数据库数量 + 1，并逐项核对 ID、文本。SQLite history 为操作依据，重放 ADD/UPDATE/DELETE 后必须得到同一数据库状态，且与 add 返回的操作匹配。最终关闭并重新打开 Qdrant 核对持久化状态，执行 SQLite integrity_check。原生代码吞掉的 ERROR 也会导致该次运行不被标为完成。

LLM 和 Embedding 通过包装 SDK 的 `create` 方法观察请求、响应和耗时，原响应原样返回，不更改提取提示词、更新提示词、召回 top-k 或操作执行逻辑。可获取的 token 用量按阶段、接口分别汇总；上游未提供的信息不推算。SDK 内部重试可能产生不可见的额外用量。

本地辅助验证使用临时合成数据检查了 137 条记忆的三页读取、显式 get_all 上限 138、数据库重开及操作重放；这些不是 HaluMem 实际运行结果，不计入该用户的记忆和操作。

只有两个会话完成才能称基础流程通过；未发生 UPDATE 时不能据此判断更新保护效果。即使发生 UPDATE，这个最小案例也不足以证明更新保护有效。

## 本轮实际结果

成功结果目录：`results/local_smoke/20261022T203207+0800_a40c12d5/`。

| 会话 | 完成消息数 | 前 → 后记忆数 | ADD | UPDATE | DELETE | add 耗时 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 12 | 0 → 17 | 17 | 0 | 0 | 21.414 秒 |
| 2 | 8 | 17 → 29 | 12 | 0 | 0 | 29.971 秒 |

LLM 和 Embedding 接口均通过，所有 Embedding 调用均返回 1024 维。接口回传模型名分别是 `qwen-plus`、`text-embedding-v4`，未提供更具体的固定修订号。含独立接口验证，LLM 报告 7,805 tokens（输入 5,808、输出 1,997），Embedding 报告 360 tokens。两个 add 总耗时约 51.385 秒，首次完整运行约 55.658 秒，离线复核耗时另记于 summary。

最终 29 条持久化记忆、29 条 ADD history，与每次 add 返回及四份前后快照一致。没有发生 UPDATE 或 DELETE；仅验证基础流程，不能判断更新保护效果。

首次最终核对使用向量逐位相等，误将 Qdrant 的浮点表示差异判为失败。已检查安装版本的 Qdrant 源码：本地库在持久化时保存原始向量，写入内存时将余弦向量转换为 float32 并归一化，因此重开后的表示存在很小差异。本轮最大分量差异为 `2.9802322387695312e-08`。修正后 ID、payload、数量、维度仍严格相等；向量使用 `rel_tol=1e-6, abs_tol=1e-7`，并验证能拒绝明显的向量、内容和数量损坏。原始 `summary.initial.json`、`errors.initial.json` 和运行日志保留，`errors.json` 注明已解决。没有重复输入会话或重复付费模型调用。

仅对本轮已有证据和磁盘状态重新核对，不调用模型：

```sh
conda run -n mem0_halumem python scripts/local_smoke.py --verify-run results/local_smoke/20261022T203207+0800_a40c12d5
```

本轮依赖包括 `openai==1.109.1`、`qdrant-client==1.20.0`、`pydantic==2.14.1`、`numpy==2.4.6`；精确完整列表见成功结果目录的 `requirements-freeze.txt`。
