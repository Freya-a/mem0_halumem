# 代码与方法来源

检查范围为本地仓库当前 checkout；下列哈希可用 `git -C external/<repo> rev-parse HEAD` 验证。两仓库均未发现明确的项目级许可证文件，README 中也未发现许可声明；没有确认复制或公开再分发权限。这里的来源标记不等于授权判断，不应声称已获许可。请在公开复制或发布相关材料前由权利人确认权限。

| 来源 | 原文件 / 函数 | 新模块对应位置 | 复用和修改 |
|---|---|---|---|
| [ERASE](https://github.com/belindal/ERASE), `b93f898780b3cf40fedd4e9a00c51af9a27688bc` | `models/kb_model.py`, `KBModel.edit_retrieved_facts`, 逐条循环及 `Reinforce` / `Make False` / `No Change` 分类 | `judge.py`: `JUDGE_PROMPT`, `judge`, `_validate_judgment` | 依据原代码适配逐事实模型分类流程和三个原标签，输入改为 v4 事实、旧记忆、可追溯引文、新来源和已有时间；保留方向性但不假设旧事实一定真实。对无效输出失败关闭，不沿用原代码重试后回退 `no change`，避免把错误伪装为未涉及。分离并排除随后的 rewrite、KB 更新；新增片段候选及证据校验。该部分是源代码流程和提示思路的改写，没有直接导入或调用作者函数，也没有声称逐字复制了整个函数。 |
| [FactTrack](https://github.com/cogito233/fact-track), `8b09d7fa5a805aa45a0d87a376d255665bd69460` | `fact-track/core/contradict_detector.py`, `ContradictDetector_StatusPersistence.fact_decompose` | `judge.py`: `JUDGE_PROMPT` 的前态、后态和跨事件不变状态 | 适配原函数区分 pre/post/static 的提示方法，但由 v4 负责旧记忆拆分，时间状态仅在有证据时作为判断候选。没有调用作者函数、没有沿用按标题和编号解析文本的代码，也不强迫推测转换或把不确定内容改成断言。 |
| FactTrack，同一 commit | 同文件 `contradict_check`；`fact-track/utils/huggingface_api.py` 的 `huggingface_UnitContradictScore` | `judge.py`: `JUDGE_PROMPT` 中的事实对冲突/历史相容分类 | 借鉴先看事实对是否冲突，再结合时间范围的思路；由注入 backend 给出候选，未直接复用 NLI、GPT 二次确认、阈值、权重或作者函数，不能当作作者 contradiction score。 |
| FactTrack，同一 commit | 同文件 `interval_blockCheck`, `interval_contradictCheck`, `interval_insert`; `fact-track/core/state_checker.py`, `fact_decompose` | `judge.py`: 时间关系枚举和要求证据与理由 | 借鉴有效范围与重叠才构成同时冲突的原则；无事件时序、锚点不足时为 `unclear`。没有调用或逐字复制这些函数，未复用其故事位置数值、区间收缩、索引数据结构或区间公式；没有真实日期换算。 |
| 本项目现有 splitter | `variants/dnd_mem0_splitter/splitter.py`, `split_memory`, `_validate_request`, `_validate_response`；`real_backend.py`, `OpenAICompatibleBackend.__call__` 接口 | `split_with_v4`, `judge`, `adapt_splitter_backend` | **直接调用**现有的拆分与引文验证函数；v4 prompt 显式读取。模型接口兼容现有“prompt 绑定 + request 字典返回字典”的一次性 backend 工厂，实际模型客户端由调用方提供。没有修改原默认入口。 |

## 不直接调用作者函数的原因

ERASE 的目标方法绑定 KB 对象、时间戳、其他相关事实和 `query_lm_fn`，同一方法继续对 `Make False` 进行改写；模块导入还依赖 transformers、faiss、sentence-transformers 和 GENRE 等。为了严格隔离分类和改写，没有实例化或调用它。

FactTrack 的 `contradict_detector.py` 在导入时读取 `BASE_PATH` 并导入 `gpt_api` 与 `huggingface_api`；后者在模块末尾立即 `load_models()`，可能下载并保存 Contriever，并要求本地微调 NLI `models/results_18k`；前者在导入时创建 OpenAI client。检测器初始化还会创建/覆盖日志并加载模型；区间函数依赖 embeddings、模型、全局状态和故事坐标。`env.yml` 本地只有 `[y/N]:`，不能作为完整依赖清单。本地没有上述微调模型目录。本次没有导入这些模块、加载或下载权重、初始化检测器或运行作者函数。上述限制是依据源码及本地路径检查，并非声称在任意环境均无法调用。
