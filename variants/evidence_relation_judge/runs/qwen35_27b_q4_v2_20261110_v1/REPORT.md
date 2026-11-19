# Qwen3.5-27B Q4_K_M：组件一 v2 五案例开发诊断

## 运行结论

模型成功在 RTX 3090 Ti 上加载并运行。CUDA 日志报告 **65/65 层**在 GPU；但 `token_embd.weight` 使用 CPU，模型 `CPU_Mapped` 缓冲区 **682.03 MiB**，因此不能说所有权重全部位于 GPU。模型 CUDA 缓冲区 15,272.77 MiB、KV 缓冲区 256.00 MiB、recurrent state 缓冲区 149.62 MiB，另有计算缓冲区。服务就绪耗时 3.938 秒。加载前设备总占用 1,193 MiB、加载后 17,350 MiB；本轮结束时 `llama-server` 进程占用 16,304 MiB。五例采样到设备总显存峰值 **17,500 MiB**，包含其他进程和桌面占用；每约 0.2 秒采样，可能错过短峰值，不是进程专属峰值。

五条旧子事实共实际发出五次生成请求，无自动重试。端到端每例 7.268–11.841 秒，均值 9.476 秒；1,566 个输出 token 的解码加权速度约 38.1 token/s，不包括提示处理和 HTTP 时间。一次输出一次观察，不代表其他负载或长上下文性能。四例通过 v2 结构、引文和片段校验，晋升例没有通过；这些不是语义正确率。

## 可追溯性与测试边界

- [环境、源码、模型来源与校验记录](environment.md)、[下载与 SHA-256 校验](download-verification.log)、[构建日志](cmake-build.log)；模型 SHA-256 为 `84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806`，和 [Unsloth 发布页](https://huggingface.co/unsloth/Qwen3.5-27B-GGUF/blob/main/Qwen3.5-27B-Q4_K_M.gguf) 一致，大小 16,740,812,704 字节。
- [诊断服务日志](diagnostic_server.log)包含分层和缓冲区分配；[诊断启动参数及耗时](diagnostic_server_launch.json)记录上下文 4096、单并发、`--n-gpu-layers 99` 和 `--fit off`。CUDA 12.1.66、驱动 535.309.01，独立 llama.cpp `78ffbaa18533c2ed51eab2ef5ae0702330efc3e9`，未修改驱动和现有 Python 环境。
- [本轮清单](manifest.json)记录旧输入、两种基线、判断器散列和参数；[对照数据](comparison.json)列出每个模型的标签、片段、理由和校验错误。各案例 JSON 保存全部输入、system/user 消息、模板请求与响应、完整生成请求与原始响应、解析结果、耗时及显存采样。
- 首次 OpenAI 风格聊天接口探针把**输入模板中的空 thinking 前缀**回显进 `content`，导致直接 JSON 解析失败；[首次探针原样保存](first_chat_probe/smoke_json.json)。GGUF 内置模板在 `enable_thinking=false` 时把空 `<think>...</think>` 块放入**输入**，见 [模型模板](server_props.json)和[实际渲染](rendered_template.json)。最终入口使用 `/apply-template` 渲染原消息，再通过 `/completion` 获取纯原始生成文本，未删除或修饰输出；[纯文本探针](smoke_plain.json)、[JSON 探针](smoke_json.json)及[检查结果](preflight.json)通过。模板请求不生成 token，不计为事实调用。
- 三种模型的 system/user 消息与已有 v2 基线逐字一致；Qwen3-8B 使用 BF16 Transformers 贪心解码，qwen-plus 为远程服务 `temperature=0` 和服务商默认项，Qwen3.5 是 GGUF Q4_K_M、llama.cpp、`temperature=0`、`n_predict=768`，其实际 top-k、top-p、min-p 和其他采样设置见各响应。tokenizer、模板、量化和后端不同，温度 0 不保证各方法解码完全相同。qwen-plus 别名没有锁定底层快照。不能把差异全部归因于模型能力。
- 人工记录确认的是事实和更新边界，不是本次关系标签的盲标；下述语义分析**均待人工审核**。本轮没有运行拆分器、组件二，也未写入 Mem0；五例为定向开发诊断，不估计总体准确率。

## 逐例对照

### 转岗阶段

- Qwen3-8B：`support`；qwen-plus：`possible_change`；Qwen3.5：`possible_change`，结构校验通过。
- Qwen3.5 区分旧求职阶段与已转岗的新状态，比单纯将完成转岗解释为旧的“正在找工作”得到支持更贴近材料。它询问是否已停止找工作，宜限定为本次求职阶段，不可推断以后不再寻求其他工作。输出将 Feb/Mar 用于条件表述；这些是记录时间，不足以确定转岗发生日期。候选片段是整条旧句，仍应保留带时间的求职历史。
- 记录：[Qwen3.5](job_transition.json)、[Qwen3-8B](../erase_style_comparison_20261110_v1/A_v2/job_transition.json)、[qwen-plus](../qwen_plus_v2_diagnosis_20261110_v1/job_transition.json)。

### 模拟与真实跳伞

- Qwen3-8B：`possible_change`；qwen-plus：`possible_change`；Qwen3.5：`uncertain`，结构校验通过。
- Qwen3.5 明确区分模拟体验和真实跳伞，保留仍重视安全的事实，追问真实跳伞态度；它没有像 qwen-plus 的理由那样给模拟活动补上未确认的“低风险”条件。旧事实是宽泛极限运动概括，Qwen3.5 对其与真实跳伞的对应仍需结合原文审核；`uncertain` 是否优于其他标签不由本次非盲观察裁定。
- 记录：[Qwen3.5](skydiving.json)、[Qwen3-8B](../erase_style_comparison_20261110_v1/A_v2/skydiving.json)、[qwen-plus](../qwen_plus_v2_diagnosis_20261110_v1/skydiving.json)。

### 咨询公司身份

- 三者都是 `uncertain`，Qwen3.5 结构校验通过。
- Qwen3.5 没有把“my consulting firm”直接断言为当前受雇关系，指出新旧公司关系和现职未知；Qwen3-8B 的理由把受雇于咨询公司当作事实，qwen-plus 也避免了这一断言。Qwen3.5 的问题仍涉及现职、旧角色是否结束和公司关系，不能将其理解为对旧职业历史的否定；整句候选也不代表应整体删除。
- 记录：[Qwen3.5](career_history.json)、[Qwen3-8B](../erase_style_comparison_20261110_v1/A_v2/career_history.json)、[qwen-plus](../qwen_plus_v2_diagnosis_20261110_v1/career_history.json)。

### 晋升职称与雇主

- 三者原始候选标签均为 `possible_change`；Qwen3.5 **校验失败**，因此该候选不能当作通过的判断结果。
- Qwen3.5 选出 `as a Director`，与 qwen-plus 相同且比 Qwen3-8B 的整句范围更聚焦职称；它把 `old_quote` 填成上下文的 `I work at Historical Productions Ltd. as a Director.`，而规则要求来自该事实的 memory 引文。该片段定位成功不抵消引文来源失败，未修复或重试。应保留旧 Director 历史和相同雇主，不推断确切晋升日期。
- 记录：[Qwen3.5](promotion.json)、[Qwen3-8B](../erase_style_comparison_20261110_v1/A_v2/promotion.json)、[qwen-plus](../qwen_plus_v2_diagnosis_20261110_v1/promotion.json)。

### 波斯猫：支持与新增

- Qwen3-8B：`support`；qwen-plus、Qwen3.5：`supplement`；Qwen3.5 结构校验通过。
- Qwen3.5 选 `historical charm` 并同时提到欣赏加深与实际养护挑战，较聚焦；但它自己的理由同时说支持旧原因与新增信息，而 v2 将 `supplement` 定义为新增但不本身支持旧事实。这仍是互斥标签定义的张力，不能把不同标签当成问题解决。它所选第一条引文支持观影和欣赏加深，养护挑战来自另一条证据，不能仅由所选引文验证；旧喜好及其他原因应保留。
- 记录：[Qwen3.5](persian_cats.json)、[Qwen3-8B](../erase_style_comparison_20261110_v1/A_v2/persian_cats.json)、[qwen-plus](../qwen_plus_v2_diagnosis_20261110_v1/persian_cats.json)。

## 下一步建议

值得继续用更多独立案例测试：本轮同时观察到阶段区分、模拟/真实区分及较窄候选片段，也发现晋升例的引文来源错误，以及支持兼新增的标签定义冲突。先固定任务定义，建立独立人工标签盲审，扩充引文来源、时间、身份与条件案例；记录模板、量化和推理参数并分析格式失败。不要据此报告总体准确率或直接推广到组件二。

本次诊断完成后，服务以相同模型及推理参数重新启动，附加 `--cors-origins localhost` 并保持 `127.0.0.1:18081` 监听；[当前启动记录](server_launch.json)和[当前服务日志](server.log)与上述诊断期间的记录分开保存。服务端未配置 API key，本地同机进程可访问。
