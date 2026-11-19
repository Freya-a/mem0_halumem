# 组件二：关系判断与失效范围判断

## 目录导航

- `part1_relation_judge/`：第一部分，旧事实与新证据的关系判断，包含 v1/v2、运行脚本和测试。
- `part2_scope_judge/`：第二部分，失效范围判断，包含范围规划、可选模型、运行脚本和测试；依赖第一部分。
- `model/`、`runs/`、`examples/`：共用模型、历史运行记录和示例，仍保留在本目录。
- 范围判断的使用方法和限制见 `runs/scope_v1_20261109/REPORT.md`；关系判断 v2 见 `CONTROLLED_V2.md`。

下面是第一部分的原有说明。

# 第一部分：旧事实与新证据的候选语义关系

本目录是独立初版，不访问 Mem0、云端 API、拆分器 backend 或现有实验目录，不执行任何修改、保护范围或时间区间决策。结果是待审核候选。没有事实检索、拆分、事实更新、FactTrack 接入或时间语义评估。

## 输入与输出

输入是 UTF-8 JSON，结构见 `examples/short_case.json`：`split_result` 直接采用 v4 的 `memory_id`、`memory_text`、`facts`；每条事实保留 `fact_index`、`source_memory_id`、`raw_subfact`、`contextualized_subfact`、`evidence` 和 `pending_confirmations`。`source_context` 是 v4 所用的上下文来源列表；`new_evidence` 是包含 `source_id` 和 `text` 的非空来源列表，可携带 `source_ref`、`speaker` 等元数据；`time_info` 为调用方已有时间信息或 null，原样传入而不进行归一化或时间判断。`fact_index` 是该记忆内的事实 ID，与 `memory_id` 联合标识，输入中的不同事实必须具有不同正整数 ID。

v4 输出的每条 evidence 由 `source_type`、`source_id`、`quote`、`supports` 组成。memory 引文必须逐字出现在 `memory_text` 中；context 引文必须逐字出现在对应 `source_context.text` 中。每条事实至少有一条 memory 引文；模型输出的旧引文和候选片段必须属于该事实已有的 memory 引文，新引文须非空且逐字属于指定的新来源。原文、来源和时间信息均保留在运行记录中。程序不会验证 supports、主体、事实拆分或引文的语义支持关系。

逐事实调用模型：输出的 `candidate` 包含 ID、原始子事实、关系类别、对象/属性/条件、旧记忆中的候选影响片段、旧/新引文、理由和待确认问题。未知的对象、属性、条件和影响片段可为空；`uncertain` 必须提出至少一个问题。程序校验字段集合及类型、标签、ID、引文和片段；`validation.semantic_correctness` 始终为 `not_checked`。失败保留 `raw_output`、已解析内容（若有）和错误阶段/类型/信息，不视为无影响，也不会重试。输入错误在调用模型前返回。`status: ok` 只表示程序校验通过，不代表判断正确。

关系只选一个，提示词按下列顺序消歧：

| 标签 | 含义 |
| --- | --- |
| `uncertain` | 无法可靠判断其他类别，如对象、条件、时间或证据不足；需要问题。 |
| `historical_correction` | 新证据明确指出同一历史事实的旧表述有误；不是普通的新状态。 |
| `possible_change` | 同一对象与属性出现可能随时间/条件变化的状态，或存在待核实冲突；不代表旧事实失效。 |
| `support` | 支持或延续同一事实，没有实质性新增信息。 |
| `supplement` | 内容相容且增加相关的不同信息，本身不支持旧事实真实性或表明变化。 |
| `no_clear_impact` | 能判断没有明显相关影响；无法判断时用 `uncertain`。 |

这些类别由模型语义判断，无法靠格式校验保证类别边界或事实正确。旧事实可包含多个属性，候选片段也不构成最终修改/保护范围。

## 运行

本机已验证的环境为 `/home/shu1004/anaconda3/envs/emem_vllm/bin/python`；其他环境需要已安装兼容的 PyTorch、Transformers 和 CUDA，且硬件支持 BF16。默认 Python 当前的 PyTorch 导入因 `libcudnn.so.9` 不存在而失败。无模型检查只用标准库：

```bash
python -m unittest discover -s system/mem0_halumem_diagnosis/variants/evidence_relation_judge/part1_relation_judge -p 'test_*.py' -v
python -m unittest discover -s system/mem0_halumem_diagnosis/variants/evidence_relation_judge/part2_scope_judge -p 'test_*.py' -v
```

从工作区根目录执行一次新推理（输出路径必须不存在，绝不覆盖）：

```bash
PYTHONNOUSERSITE=1 /home/shu1004/anaconda3/envs/emem_vllm/bin/python \
  system/mem0_halumem_diagnosis/variants/evidence_relation_judge/part1_relation_judge/run_local.py \
  system/mem0_halumem_diagnosis/variants/evidence_relation_judge/examples/short_case.json \
  --output /tmp/relation_example_new.json
```

固定加载 `model/Qwen3-8B`：Hugging Face `AutoTokenizer` 和 `AutoModelForCausalLM` 使用 `local_files_only=True`，模型参数以 BF16 加载至 `cuda:0`；不自动降精度、下载或重试。每个输入事实触发一次 `generate`，批量输入会产生多次调用；模型加载失败时后续事实不会重新加载。使用贪心解码、最多生成 512 tokens。输出文件包含完整输入、模型消息、原始输出、解析结果、校验和运行信息；可能包含敏感原文，请自行选择存储位置。显存数字是 PyTorch 进程的 allocated/reserved 峰值，另列设备当时总使用量，后者包括其他进程。

也可在 Python 中调用 `relation_judge.judge(data, backend)`；backend 接收逐事实 payload 并返回原始 JSON 字符串。若输入无效或模型/解析/校验失败，程序返回错误记录，不生成替代结论。CLI 错误返回非零退出码。

## 现有项目与来源检查

- v4 的 prompt 是 `../dnd_mem0_splitter/prompt_versions/v4_boundaries_20261104/prompt.txt`，变更记录说明 JSON 格式与逐字引文规则未变；示例见该目录 `synthetic_example.json`。v4 只用上下文补足必要信息，原文事实与上下文证据分开，不证明真实身份。
- `../evidence_temporal_judge/judge.py` 的 `judge` 接收 v4 结果、上下文、新证据、时间信息和调用方注入的 fact/candidate backend；逐事实结果包括 ERASE 风格标签、applicability、temporal relation 和 modify/protect/confirm 候选。`judge_v2.py` 在注入 backend 上增加区间和 NLI 路径；其文档明确没有真实模型客户端。本组件不覆盖或调用它们，也不声称对接它们。
- ERASE 作者仓库 `external/ERASE/models/kb_model.py` 中 `retrieve_facts_to_edit` 先取相关旧事实，`edit_retrieved_facts` 将每条旧事实与新文本、时间戳送给语言模型，第一轮输出 Reinforce、Make False 或 No Change，并指示没有反驳时保留原事实；它解析失败时重复询问并最终默认 No Change。随后对 Make False 进入重写，`get_operations` 将结果转成增减/重写操作。本组件只借鉴逐事实比较和证据不足不认定失效的原则，**未复制作者代码或提示词**，不实现该重试、重写和写入流程；六类候选不能直接等同 ERASE 标签。
- 检查的 ERASE 快照未见 LICENSE/COPYING 文件，不能假定代码许可；其 `requirements.txt`、`setup.sh` 和 `KBModel.__init__` 显示还依赖 FAISS、GENRE/fairseq、sentence-transformers、实体识别及链接模型等，部分初始化会从模型名加载，可能需要下载。直接复用不适合本次离线及零环境修改约束。没有修改该仓库。

## 一次真实推理

完整输入、实际消息、原始输出、解析结果、逐项校验结果和运行统计见 `examples/short_case_run.json`；分析及环境信息见 `EXPERIMENT.md`。文件为一次真实生成的原始记录，不包含完整开发子集评估。
