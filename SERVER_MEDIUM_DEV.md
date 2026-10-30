# HaluMem-Medium 开发诊断与服务器操作

本轮状态：仅完成Mac静态准备和断网dry-run；正式Mem0运行、服务器环境安装、接口连通性、全量QA、官方评分均为**未运行**。原有local_smoke/local_update_case结果、两个源码仓库均保留。当前项目根目录不是Git仓库，未创建提交。

## 固定开发集

原文件：`HaluMem/data/HaluMem-Medium.jsonl`，33,511,525字节，20用户/1,387会话。
SHA256：`486fbc130a5c8781a2af27ffa508a1d7855245137aa449c193ac4d29c45634e7`。

| 用户UUID | 来源 | 目标数 | 必需完整会话（1基时间序号） | 原始会话数组索引（0基） | 原始消息数 |
|---|---|---:|---|---|---:|
| 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f | 已调试用户Martin | 8 | 1—9 | 0—8 | 322 |
| 348492a7-cfe4-ee1d-73c3-c276d6ba8277 | seed 42补选Donald | 8 | 1—8 | 0—7 | 250 |
| 1b846c59-456e-9550-dffd-4d23f1eca81f | seed 42补选Williams | 8 | 1—11 | 0—10 | 418 |

共24个**自动初标、待人工核验**目标：6明确替换、7局部属性变化、11补充细化；涉及16个目标会话组，用户内仍有时序关联，不构成24次独立实验。正式输入28个完整会话、990条原始消息。人工已确认数为0。规则、配方和清单均由原始对话与更新标注固定，不使用Mem0失败结果筛选。开发集包含已调试用户，不能用来报告无偏总体表现。

`diagnosis/medium_dev/SELECTION_RULES.md`写明规则；`manifest.json`是固定清单与双侧对话证据；`initial_annotations.csv`供核验，`TARGETS.md`提供24项目录；`prefix_ranges.json`规定每用户前缀；`insufficient_evidence.json`单列5项；`candidate_ledger.json`记录前18会话其余更新候选的去向。旧知识语义可能比original_memories更窄，原因逐项记录。比如Golden Retriever和模拟跳伞只允许局部偏好变化，不意味着彻底取消Labrador偏好或真实跳伞风险顾虑。

一次静态复核将重复的身体活动意向替换为“事务所已获得初始客户、从兴奋到成就与释然”的清楚新事件，并排除仅由助手提及、用户未确认的meditation。先前准备草稿保存在`results/medium_dev/offline_preparation/selection_drafts/`，不用于运行；现行唯一入口是`diagnosis/medium_dev/manifest.json`。最终Donald前缀为8会话，目标会话组为16。

全数据有两处相邻会话时间重叠：用户d850d98b-ba45-3fd5-e3fa-2104b6724e10和2e36c193-a605-8cc7-70ff-80b2336d4980。均不属于所选用户；详见`data_validation.json`。所选前缀的会话时间边界和消息时间顺序已校验。

## 从Linux服务器项目根目录准备

整个项目迁移时保留`mem0_v0.1.118/`、`HaluMem/data/`、`scripts/`、`config/`和`diagnosis/`的相对目录结构。脚本以自身位置解析根目录，不包含Mac绝对路径。旧实验可另外归档，不是新运行的前置依赖；不把Mac的Qdrant/history拷进新运行。没有GPU或本地权重要求；“开源本地Mem0”指本地Python包和本地持久化，LLM/Embedding仍是已验证的兼容接口。

```bash
conda create -n mem0_halumem python=3.11 pip -y
conda run -n mem0_halumem python -m pip install -r config/requirements-medium-dev.txt
conda run -n mem0_halumem python -m pip install --no-deps -e ./mem0_v0.1.118
conda run -n mem0_halumem python -m pip check
cp -n config/medium_dev.env.example .env.server
chmod 600 .env.server
# 在服务器本地编辑 .env.server 的两个API_KEY；不要提交或粘贴到聊天。
```

已存在环境时复用，省略create。依赖表从已验证Mac环境导出，去掉机器本地pip URL、远程editable地址和打包工具；Mem0单独从本项目源码editable安装。Linux安装尚未实际验证，如pin解析或平台wheel失败，保留安装日志并解决环境问题，不自动升级到最新Mem0。安装过程需要包仓库网络；模型密钥不参与安装。

模型固定为`qwen-plus`，Embedding固定`text-embedding-v4`/1024维，两个URL为`https://dashscope.aliyuncs.com/compatible-mode/v1`；max_tokens=16384、temperature=0.5、timeout=180秒。`config/medium_dev.profile.json`保存无密钥配置及原生源码/复用脚本SHA256。模型没有提供可固定的具体修订号，不能把模型别名视为永远不变的权重。与旧脚本相比仅显式关闭SDK传输重试（max_retries=0），防止隐藏重试；不改原生提示词、top-5召回、计划执行或infer=True。

只读取`--env-file`指定文件和对应进程环境变量，进程值优先。不隐式读取HaluMem/.env或Mac的.env.local；非密钥项缺省取固定profile，填写了其他值就报错。运行日志中的配置脱敏；API keys不写入代码、命令参数或产物。

## 无模型预检和dry-run

```bash
conda run -n mem0_halumem python scripts/medium_dev_data.py
conda run -n mem0_halumem python -m py_compile scripts/medium_dev_data.py scripts/medium_dev_review.py scripts/medium_dev_run.py
conda run -n mem0_halumem python scripts/medium_dev_run.py --preflight --run-id server_preflight --env-file .env.server
conda run -n mem0_halumem python scripts/medium_dev_run.py --dry-run --run-id server_dry_run --env-file .env.server
```

预检与dry-run执行同一断网检查：校验数据、固定manifest、全部证据引用、完整前缀、时间顺序、纯dialogue输入、独立路径、源码哈希；实际import Mem0核对`mem0ai==0.1.118`及加载路径必须是当前项目的`mem0_v0.1.118/mem0/__init__.py`，并检查editable标记。import产生的身份配置留在临时目录并删除，不实例化Memory、不创建向量库或history。未填写key也可检查。进程中socket连接被禁止，既不探测接口，也不调用模型。

恢复dry-run只在临时目录用不透明假文件演练真实回滚函数：识别未提交会话、保留部分状态、恢复会话前文件、保持已提交序号、拒绝已提交产物损坏。这些是假文件，不是Qdrant或SQLite，也不是实验结果。正式Linux运行、真实异常持久化以及网络接口仍须服务器阶段验证。

输出默认`results/medium_dev/<run_id>/dry_run/`，每用户完整原始输入计划和`report.json`；根目录的`review_pending.json/.csv`全为未运行/待核实。可用`--dataset /path/to/HaluMem-Medium.jsonl`和`--output-root /path/to/new/results`迁移数据与输出路径，但数据字节和指纹必须匹配。

## 正式运行（本轮未执行）

在服务器上人工审阅初标及证据后，确定一个新的run_id并执行：

```bash
conda run --no-capture-output -n mem0_halumem python scripts/medium_dev_run.py --execute --run-id medium_dev_001 --env-file .env.server
```

默认逐用户、逐会话顺序运行；每用户独立Python子进程避免MEM0_DIR缓存串用。每用户从空库开始，完整输入首会话至最后目标会话；没有额外付费预试调用。不复用Mac记忆；不跳中间会话，不只运行目标会话，也不对每个memory point重复add。同会话所有目标共享一次add和同一组快照/实际操作。用户内按start_time排序，原始数组索引另存。原始助手消息即使含干扰也全部保留；不将标准memory_points、original_memories、persona_info或QA答案加入模型输入或预填数据库。

`--user UUID`可先运行某一选中用户。其后同run_id继续其他用户也必须加`--resume`。只有全部用户前缀完成才记为整个run完成；只完成部分用户标记partial_users_completed。

## 记录、检查点与异常恢复

`results/medium_dev/<run_id>/users/<UUID>/`各自含`qdrant/`、`history.db`、`mem0_runtime/`（包括独立migrations库）、`checkpoint.json`、加载版本/源码路径及脱敏配置。根目录保存固定manifest/profile、代码副本、精确pip freeze和运行指纹。

每个`session_XXX/`保存：

- `input.json`：完整原文、时间戳、原始索引及实际role/content输入；`target_links.json`：关联目标。
- `before.json`、`after.json`：分页全量Qdrant payload/向量与显式不限截断get_all核对。
- `observations.jsonl/.json`、`extracted_facts.json`、`recall_candidates.json`：原始提取输出、每个事实的top-5候选及真实ID/score。
- `update_model_io.json`：完整原生更新模型输入输出、临时ID→UUID映射；`full_operation_plan.json`含NONE。
- `execution_results.json`：原生操作调用及结果/异常；`actual_operations.json`、`history_all.json`：SQLite实际写入；`add_return.json`：原始add返回与只包围Memory.add调用的耗时。
- `api_calls.jsonl`：SDK实际请求、LLM原始响应、Embedding返回维度、可获得usage和耗时。缺失token字段不估算；无SDK重试。
- `verification.json`、`persistence.json`：历史重放与add返回一致、重开库核验、SQLite integrity_check、NONE派发核对；`target_operation_correspondence.json`将目标组链接到本会话实际操作，逐命题归因待人工确认。
- `rollback_before/`：会话前关闭数据库后的文件副本和校验和。错误时写`error.json`及可获取的`after_partial.json`、`history_partial.json`、`actual_operations_partial.json`，不伪装完成。

每个成功会话完成校验、关闭数据库并重新打开核对持久化后才原子提交checkpoint。resume跳过全部已提交会话，核对已提交日志哈希、上次after与当前向量状态、完整history（即使该用户已全部完成、没有新会话也核验）；数据、配置、源码或入口指纹改变就拒绝复用run。

```bash
# 仅对没有未提交会话的正常中断，或完成显式回滚后续跑：
conda run --no-capture-output -n mem0_halumem python scripts/medium_dev_run.py --execute --resume --run-id medium_dev_001 --env-file .env.server
```

如果存在started但未提交的会话、原生吞掉的ERROR、解析失败、计划执行不一致、网络异常、部分写入或提交前崩溃，普通resume立即拒绝；没有自动重试。先查看该会话日志。如果决定恢复，显式指定用户进行回滚：

```bash
# 替换UUID；只回滚该用户唯一的未提交会话。此命令不调用模型，也无需密钥。
conda run -n mem0_halumem python scripts/medium_dev_run.py --rollback-incomplete --run-id medium_dev_001 --user 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f
# 审查recovery/归档后再显式执行上面的 --execute --resume 命令。
```

回滚先验证备份和checkpoint，将异常会话及当前数据库移到`recovery/`，再恢复会话前Qdrant/history；不撤销已产生的接口费用，不重输已提交会话。恢复过程有RECOVERY_IN_PROGRESS标记，恢复中再次崩溃时停止并要求人工调查。缺少完整备份、备份损坏或历史产物损坏时不猜测恢复，保留旧run并使用新run_id。`--output-root`自定义时所有相关命令必须一致。根run锁与用户锁阻止并发写入/导出/恢复。

## 审查与导出

`review_pending.json/.csv`不根据关键词直接判定失败。它们是可再生成的待审查包；人工结论请另存为`review_decisions.json/.csv`，避免与自动包混用。再次生成前，JSON和CSV各自的旧包及其可能的人工编辑会按各文件内容哈希保存在`review_archive/`，不会丢弃。审查时先确定old_proposition在before里对应的真实ID（同义改写、组合记忆都要核实），再看召回与输入；精确文本hint只作定位线索，未精确匹配不等于未入库。所有同会话操作只是共享候选，不能全部归因给每个目标。

| 分类 | 判定前提 |
|---|---|
| 旧命题未入库 | 原始早期证据充分，但目标会话before中找不到语义相同的实际记忆；不能归因于该次更新召回或执行 |
| 召回不足 | before确认有相关ID，但原生召回/更新模型输入没有提供足够旧知识 |
| 应改未改 | before和模型输入有充分可用证据，after仍缺少预期新状态或保留过时的当前状态；依据语义，不强制UPDATE事件 |
| 越界修改 | 实际操作改动超出该目标允许属性/情境；也须排除同会话其他合法目标和对话的解释 |
| 有效知识损伤 | before确认保护命题确实存在、当前完整对话未使其失效，after却被删除或改坏 |
| 证据不足 | 原始证据、实际快照、语义对应或保护命题可评估性不足；不能强判成功或失败 |

保护命题的`actual_memory_ids`和`evaluable`须根据目标会话的真实before进一步填写。保护命题从未入库时不可评估其保留效果。旧命题与新状态可按历史时间共存；“补充细化”允许保持旧知识，原标注is_update不说明旧命题作废。同一用户内、同一会话组内的结论应联合审查，不按24个独立事件算显著性。

运行后可重复生成待审查表及官方格式适配草稿（无模型调用）：

```bash
conda run -n mem0_halumem python scripts/medium_dev_run.py --export-official --run-id medium_dev_001
```

导出`export/halumem_official_schema_partial.jsonl`保留uuid、从persona_info提取的user_name（只用于导出元数据）、已提交session原始字段、标准memory_points、按本仓库eval_memzero.py约定的extracted_memories（add返回文本）、仅add调用耗时，另附raw extracted facts和快照位置。questions被省略并明确QA未运行；没有编造system_response、context或memories_from_system。此入口只是后续评分适配桥梁，`export_status.json`明确official_scoring_ready=false。未来需单独收集官方更新检索结果，若开展QA再生成context/system_response，并审查子集适用性后才可运行官方scorer。本轮不做这些检索、QA或评分；不能将缺字段的导出交给scorer后声称官方分数。

## 本轮生成文件

- `SERVER_MEDIUM_DEV.md`：本说明。
- `diagnosis/medium_dev/SELECTION_RULES.md`、`recipes.json`、`manifest.json`、`TARGETS.md`、`initial_annotations.csv`、`prefix_ranges.json`、`insufficient_evidence.json`、`candidate_ledger.json`、`data_validation.json`：固定选样与证据。
- `scripts/medium_dev_data.py`、`medium_dev_run.py`、`medium_dev_review.py`：数据校验、离线/执行入口、待审查与导出。
- `config/medium_dev.profile.json`、`medium_dev.env.example`、`requirements-medium-dev.txt`：固定源码/模型配置、无密钥模板、可迁移依赖版本。
- `docs/superpowers/plans/2026-10-22-medium-dev.md`：任务计划与边界。
- `results/medium_dev/offline_preparation/dry_run/`、`review_pending.json/.csv`：本机断网核对产物，模型结果均为未运行。
