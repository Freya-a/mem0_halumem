# 复用官方 HaluMem 评测

本目录将已有开发集运行结果转为官方输入格式，然后直接执行未修改的 `HaluMem/eval/evaluation.py`。评分提示词、评分函数、分类和汇总均由该官方程序完成，包括 memory integrity、memory accuracy、update、QA 和 F1。官方聚合结果位于新输出目录的 `results/memzero-development/memzero_eval_stat_result.json`，逐用户中间结果位于同目录 `tmp2/`。不将下面的项目诊断指标混入官方结果。

## 准备和运行

从项目根目录执行；输出目录必须不存在。仅准备输入，不调用模型：

```bash
python scripts/halumem_official/prepare.py /tmp/halumem_official_dev_prepared
```

正式评分需要安装 `HaluMem/pyproject.toml` 中的 eval 依赖，并按 `HaluMem/eval/.env-example` 配置评分服务。特别是 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`、`RETRY_TIMES`、`WAIT_TIME_LOWER` 和 `WAIT_TIME_UPPER` 必须由运行环境提供；温度、超时等也请明确配置。密钥不要写入命令、记录或仓库。使用包含依赖的 Python，在**另一个全新的目录**准备并启动评分：

```bash
python scripts/halumem_official/prepare.py /tmp/halumem_official_dev_run --run-official
```

也可以进入已准备目录，直接运行官方 CLI（将示例路径替换成本机项目路径）：

```bash
cd /tmp/halumem_official_dev_prepared
python /home/shu1004/ld/system/mem0_halumem_diagnosis/HaluMem/eval/evaluation.py --frame memzero --version development
```

CLI 会对全部评分环节重新请求模型，并不复用旧的更新/QA 模型评分；此数据预计 421 次 integrity、617 次 accuracy、56 次 update 和 75 次 QA，即 **1169 次基本评分请求**，重试会增加请求。它使用官方重试、并发、按用户缓存和异常处理；请求数量、费用、原始响应记录和中断恢复方式与旧 `run_eval.py` 不同。应核查输出记录中的无效评分以及实际服务商计费。运行之前确认模型和费用配置。

## 数据来源与边界

- 使用冻结开发运行的 3 用户、28 会话：477 条参考记忆（含 38 条 interference）、617 条 Mem0 add 返回记忆、56 条更新检索及 75 条问答。运行前逐会话检查数据集、输入、add 返回、快照和验证/异常记录哈希，缺失检索或答案时拒绝导出。
- 生成的 `extracted_memories` 使用本地 Mem0 的 add 返回内容，遵循官方 Mem0 适配器所用字段。更新检索和回答来自之前基于本地快照重建的结果；其时间戳为实际写库时间。四个异常会话及后续快照沿用原有记录，见原报告。
- 已有记录没有按官方 `search_duration_ms` 字段保存可直接填入的完整检索耗时，因此导出不会编造该字段；官方输出的检索耗时为零时表示未提供，不能当成真实零耗时。
- 这不是完整 Medium 数据集，也不是官方托管 Mem0 的完整运行。模型、检索、输入来源和样本范围均可能与论文不同，不可直接把结果当成论文复现。
- 官方 `evaluation.py` 在某些分母为零的输入或所有评分无效时可能抛出 `ZeroDivisionError`。本适配器保留官方行为，不伪造分数；若发生此情况，查看逐用户中间结果并记录缺失项。官方评分失败也可能产生无效标签，应检查 `valid` 和 `all` 分母。
- 输出目录包含数据集和模型回答，注意按源数据权限保存。输入构造本身没有模型调用。

## 项目额外指标

请参阅 [项目额外指标说明](CUSTOM_METRICS.md)。`all` / `valid` 在官方汇总中本来就存在；旧报告重新计算并附带了候选、失败和复核统计，它们不是新的官方指标。
