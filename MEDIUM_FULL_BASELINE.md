# 本地 Mem0 v0.1.118：HaluMem-Medium 全量基线

本实验使用官方本地 Mem0 v0.1.118 的原生 `Memory.add` 和官方 HaluMem-Medium 数据。数据包括 20 个用户、1,387 个会话及 3,467 个问题。项目自己的入口负责调度、保存结果和衔接官方评分，未改动 Mem0 或 HaluMem 官方源码。

事实提取、更新决策、每个会话的问答生成和之后的评分，均使用百炼北京区 `qwen-plus-2025-12-01`、同一业务空间及 `DASHSCOPE_API_KEY`。适配器不支持显式设置 `enable_thinking`，因此沿用快照默认的非思考模式。Embedding 沿用 `text-embedding-v4`、1024 维和原有北京接口；这是向量模型。问答和评分沿用温度 0、最大输出 16384、超时 180 秒的设置；问答提示词和评分代码使用 HaluMem 官方文件。

## 密钥和离线检查

当前服务器已准备 `.env.server.medium-full`，包含 `DASHSCOPE_API_KEY`、`DASHSCOPE_WORKSPACE_ID` 和 `EMBEDDING_API_KEY`，权限为 `600`。问答和评分从同一配置中读取，无需单独复制密钥。首次迁移到其他服务器时，从 `config/medium_full.env.example` 创建并填写此文件。

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis
/home/shu1004/anaconda3/envs/mem0_halumem/bin/python scripts/medium_full.py \
  --env-file .env.server.medium-full --check
```

这会检查数据集哈希、用户/会话数、模型配置及密钥是否存在，不请求模型或验证密钥有效性。问答现在默认开启；`--without-qa` 只用于专门的写入实验，产生的结果不能用于完整 QA 指标。

## 第一步：后台运行 Mem0 并生成问答

以下命令不会覆盖已有运行；需要重新开始时换一个尚未使用过的运行名：

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis
mkdir -p results/medium_full
umask 077
nohup env -u http_proxy -u https_proxy \
  /home/shu1004/anaconda3/envs/mem0_halumem/bin/python -u scripts/medium_full.py \
  --env-file .env.server.medium-full --run-id medium_qwen_002 \
  > results/medium_full/medium_qwen_002.log 2>&1 < /dev/null &
```

该命令会处理全部会话，收集每个会话的原生 Mem0 `add` 返回、更新检索，以及基于该会话完成时记忆状态的 QA 回答。输出在 `results/medium_full/medium_qwen_002/`：

- `users/<UUID>/sessions/`：逐会话结果，包括未经修改的 `mem0_add_result`。
- `users/<UUID>/native_errors/`：Mem0 在处理会话期间记录的错误。原生 `Memory.add` 捕获错误并返回时，保留该返回并继续；不会因日志中的错误额外终止或重试。
- `mem0_native_results.jsonl`：全部会话结束后汇总的原生返回；它不是模型原始 HTTP 请求或响应。
- `memzero_eval_results.jsonl`：包含参考数据、记忆、检索和 QA 的评分输入。
- `status.json`：全部会话和汇总完成后才写入 `completed`。

查看进度：

```bash
tail -f results/medium_full/medium_qwen_002.log
cat results/medium_full/medium_qwen_002/status.json
```

SSH 断开后 `nohup` 通常会保留进程；服务器关机、重启或管理员的用户会话清理策略仍可能终止它。本机曾发现小写代理变量指向不可达的本地端口，命令清除这两个变量，保留大写代理变量。

## 第二步：准备和启动官方评分

确认上一步 `status.json` 为 `completed` 后，先执行离线准备。该步骤检查数据集哈希、用户和会话、原生返回、更新检索及全部 QA 是否齐全，检查通过才会建立新的评测目录，不调用模型：

```bash
/home/shu1004/anaconda3/envs/mem0_halumem/bin/python scripts/medium_full_evaluation.py \
  --run-id medium_qwen_002 --prepare
```

然后手动启动官方 HaluMem 评分；此步骤会产生额外模型请求和费用：

```bash
nohup env -u http_proxy -u https_proxy \
  /home/shu1004/anaconda3/envs/mem0_halumem/bin/python -u scripts/medium_full_evaluation.py \
  --env-file .env.server.medium-full --run-id medium_qwen_002 --score \
  > results/medium_full/medium_qwen_002.score.log 2>&1 < /dev/null &
```

```bash
tail -f results/medium_full/medium_qwen_002.score.log
cat results/medium_full/medium_qwen_002/halumem_evaluation/scoring_status.json
```

评分完成后：

- `halumem_evaluation/metrics.csv`：记忆提取 R、Weighted R、Target P、Acc.、FMR、F1，记忆更新 C/H/O，以及问答 C/H/O。数值是 0–1 比例；`all` 和 `valid` 两列使用官方口径；官方 F1 只有 `all`。
- `halumem_evaluation/results/memzero-full/memzero_eval_stat_result.json`：官方评分完整结果、各项分母和逐条记录。评分出现无效标签时，应同时查看分母和原始记录。

评分程序有逐用户缓存；已中断的评分可以用同一条评分命令追加 `--resume`，配置和输入必须保持一致。没有完成缓存的用户可能重新产生模型请求。

## 基线中断和实验口径

若 Mem0 在会话之间停止，用第一步命令追加 `--resume` 并把日志重定向的 `>` 改为 `>>`。若进程中断、`Memory.add` 抛出异常或后续问答阶段失败，可能已有部分记忆写入；该用户目录会保留 `incomplete.json`，程序会拒绝续跑。不要直接删除标记后重跑，需要先人工检查并恢复一致的会话前数据库，或者使用新运行名从头开始。对于 Mem0 内部记录并自行捕获的错误，外层不阻断其原生行为；错误详情会保存，供评测解释时查看。

本地 Mem0 记忆的创建时间是实际写入时间，不是原对话时间；官方托管版适配器采用不同的时间戳和自定义指令。数据原始会话顺序有五位用户出现相邻开始时间倒序；本实验按官方适配器一样保留原始顺序。这个实验是本地原生 Mem0 基线，不能称为官方托管版论文结果的完全复现。
