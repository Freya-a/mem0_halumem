# 一条合成短案例记录（2026-11-06）

输入见 `examples/short_case.json`，完整消息和输出见 `examples/short_case_run.json`。旧记忆为“用户住在北京。”，新证据为用户发言“我现在住在上海。”；旧事实和新证据均无明确事件日期，`time_info` 为 null。事实和 ID 为合成数据，结构模仿 v4，不宣称由 v4 模型实际拆分。

先运行标准库单元测试，覆盖结构、身份、错误标签、旧/新引文和候选片段不匹配、模型异常、重复事实 ID，以及待确认问题。然后仅运行一次本地生成，未重试。测试后发现应该强制新引文非空，因此对提示词与校验器补充了该约束并做离线回归；该次真实调用的原始提示词允许新引文缺失，具体内容原样保存在运行记录 `model_messages`，与最终提示词有这一处差异。该案例本身提供了非空且匹配的新引文，生成输出已在最终校验器上离线复核；没有再次调用模型。

- 模型：`/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_relation_judge/model/Qwen3-8B`，`local_files_only=True`，AutoTokenizer/AutoModelForCausalLM，先 BF16 加载后移至 CUDA 0，所有浮点参数为 BF16。加载 13.081 秒。
- 环境：`emem_vllm`，PyTorch 2.9.1+cu128，Transformers 4.57.3，RTX 3090 Ti。默认 Python 中 PyTorch 报 `ImportError: libcudnn.so.9: cannot open shared object file`；没有安装或更改环境。运行时有 torch_dtype 废弃、未使用采样参数及已有 allocator 环境变量的警告。
- 实际 `generate` 调用 1 次，7.267 秒，173 个输出 token，EOS 正常结束。PyTorch CUDA 峰值 allocated 16,555,158,528 字节（15.42 GiB），reserved 16,630,415,360 字节（15.49 GiB）；生成结束设备总使用量 19,962,396,672 字节（18.59 GiB，包含其他进程），不是本进程独占显存。
- 模型输出 `uncertain`；对象“用户”、属性“居住地”、候选片段“用户住在北京。”，旧引文“用户住在北京。”、新引文“我现在住在上海。”；给出两个确认问题。完整原始 JSON 和解析结构见运行记录。
- 程序检查通过仅说明字段、标签、ID 和引文/片段逐字匹配，不能证明语义判断正确。`uncertain` 在缺少旧事实有效时间时是保守可接受的候选；模型理由称两者“存在冲突”可能误导：北京可能是过去居住地，上海是现在居住地，并未证明同一时段发生矛盾，可能只是变化。发言角色支持将“我”联系到用户，但未独立验证身份。模型的问题也未直接询问旧北京事实的时间范围。该例不够证明标签稳定性、覆盖性或语义准确率。
