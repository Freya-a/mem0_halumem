# 服务器环境检查（2026-10-27）

本轮完成环境安装与离线检查，未调用模型、未构建记忆库、未运行 QA 或评分。

- Conda 环境：`/home/shu1004/anaconda3/envs/mem0_halumem`，Python 3.11.18。
- 完整安装 `config/requirements-medium-dev.txt` 原始固定版本，无需修改 pins。
- `pip install --no-deps -e ./mem0_v0.1.118` 成功；mem0ai 版本为 0.1.118。
- 实际导入：`/home/shu1004/ld/system/mem0_halumem_diagnosis/mem0_v0.1.118/mem0/__init__.py`，editable 标记为 true。
- `pip check`：No broken requirements found；14 个模块导入、三个入口编译均通过。
- 数据文件存在，33,511,525 字节，SHA256 为 `486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7`。
- 固定清单和证据校验通过：3 用户、16 目标会话组、24 项候选、28 个完整会话、990 条消息；人工已确认数仍为 0。
- preflight/dry-run 均通过，进程内阻断 socket 网络，Memory 实例 0、模型调用 0。
- 360 个既有清单、源码和结果文件的内容哈希均未改变；所有新产物使用新目录。

配置显式读取现有 `.env.local`，沿用 qwen-plus、text-embedding-v4/1024 维及 DashScope compatible-mode URL，其他参数与固定 profile 一致。缺失凭据字段为空；凭据是否有效、额度与接口连通性未验证。没有输出凭据；`.env.local` 权限从 0664 收紧至 0600，内容不变。没有创建 `.env.server`，后续仍需显式传 `--env-file .env.local`。

初次 Conda 安装因继承的代理拒绝连接而失败；仅对安装进程取消代理后成功，未修改全局代理配置。依赖安装使用服务器已配置的清华 PyPI 镜像。检查时 pip 缓存目录不可写的提示不影响依赖检查。

## 激活与最小离线试运行

```bash
source /home/shu1004/anaconda3/etc/profile.d/conda.sh
conda activate mem0_halumem
cd /home/shu1004/ld/system/mem0_halumem_diagnosis
# 每次使用全新的 run-id，避免复写已有离线产物。
python scripts/medium_dev_run.py --dry-run --run-id "server_dry_$(date +%Y%m%dT%H%M%S)_$$" --env-file .env.local
```

未来若授权接口最小试跑，可用以下既有两会话入口；它会付费调用接口并创建独立结果，本轮未执行：

```bash
python scripts/local_smoke.py --env-file .env.local
```

该两会话 smoke 不是固定开发集实验；本轮没有执行 `--execute` 或批量构库。

## 24 项初标的人工证据入口

- `diagnosis/medium_dev/TARGETS.md`：24 项索引及旧/新原文 JSON Pointer。
- `diagnosis/medium_dev/initial_annotations.csv`：逐项原始标注、双侧原文/时间戳、允许修改范围、解释限制与候选保护命题。
- `diagnosis/medium_dev/manifest.json`：同样的结构化完整证据；`targets` 中 `old_dialogue_evidence`、`new_dialogue_evidence` 包含原句和定位。
- 原始数据 `HaluMem/data/HaluMem-Medium.jsonl`：Martin 为第 1 行、Donald 为第 17 行、Williams 为第 14 行。JSON Pointer 相对于该行用户对象，sessions/dialogue/memory_points 数组索引均从 0 开始。
- 例：首项目的旧证据 `/sessions/2/dialogue/2`，新证据从 `/sessions/4/dialogue/0` 起；原始更新标注 `/sessions/4/memory_points/0`。

所有自动初标保持待人工核验；新的 review_pending 包不代表人工确认。

## 检查产物

- 本目录：`checks.json`、`pip-check.txt`、`pip-freeze.txt`、`data-check.txt`、`compile.txt`、`imports.json`、`preservation-check.json`。
- `results/medium_dev/server_preflight_20261027_01/dry_run/report.json`
- `results/medium_dev/server_setup_20261027_01/dry_run/report.json` 及每用户完整输入计划；该 run 根目录的 review_pending.json/.csv 均为未运行/待核验。
