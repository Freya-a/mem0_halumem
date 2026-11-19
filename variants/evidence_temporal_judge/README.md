# 证据影响与时间关系判断器（初版）

本文件描述保留的 v1。独立 v2 原型及其离线示例见 [README_V2.md](README_V2.md)，作者代码适配和授权状态见 [PROVENANCE_V2.md](PROVENANCE_V2.md)。

本目录只产生**候选**，不修改证据、记忆或知识库。唯一需要执行的入口是 Python 函数；没有默认真实模型入口。模型调用通过可注入的 callable 完成；本次只用手写响应验证。实现采用标准库，调用现有 splitter 的 Python 验证逻辑。

## 接口与流程

`split_and_judge(request, new_evidence, time_info, splitter_backend_factory, fact_backend, candidate_backend)` 先将固定的 v4 文件全文交给 `splitter_backend_factory(prompt)`，调用现有 `split_memory`，再逐事实判断，并单独识别新增候选。返回 `splitter_prompt.path`（运行时解析的绝对路径）和 `sha256`（实际读入字节），不改现有默认入口。拆分器失败时直接抛出其 `ValidationError`，不会假装拆分结果为空。调用方若已有 v4 结果，也可以调用 `judge(split_result, source_context, new_evidence, time_info, fact_backend, candidate_backend)`；该低层接口只验证结构与引用，不能证明该结果是由 v4 产生的。

- `request` 是现有 splitter 的输入：`memory_id`、`memory_text` 和可选 `source_context`；`split_result` 是其 `{memory_id, memory_text, facts}` 输出。
- `new_evidence` 是数组，例如 `[{"source_id":"new-1", "text":"...", "source_ref":"..."}]`；ID 不重复。附加的来源、记录时间等字段原样传递和返回。`time_info` 是调用方已有的 JSON 值，可以是 `null`；记录时间不是自动的事件时间锚点。
- 每个判断 backend 接收字典，含 `task`、`prompt`、原始材料及时间信息，返回解析后的 JSON 对象。`adapt_splitter_backend(factory)` 可把现有 `OpenAICompatibleBackend` 一次性实例工厂接到该接口：它为每次请求绑定该请求的 system prompt，并在完成后关闭 backend。拆分也需要单独的实例。故一次完整流程最多需要一次拆分、每条事实一次判断、一次新增候选调用；模块不会自行读取配置、创建客户端或发请求。
- 一条判断返回 `erase_label`（`Reinforce`、`Make False`、`No Change`）、`applicability`（`involved`、`uninvolved`、`insufficient`）、`temporal_relation`（`before_after`、`historical_compatible`、`simultaneous_conflict`、`unclear`）、`temporal_reason`、`components`。组件依次为 `{fragment, action, reason, new_evidence:[{source_id, quote}]}`，其中 `fragment` 必须按原序逐字覆盖 `raw_subfact` 的全部非空白、非标点文字；`action` 为 `modify`（修改候选）、`protect`（保护）、`confirm`（待确认）。这让一个旧事实的不同部分分别处理，不静默遗漏部分内容。允许的分段并不能保证语义上拆分得正确。
- `Make False` 保留 ERASE 的“更不可能”方向标签，不表示事实已证实失效；`modify` 同样只是供人工或后续流程审查的候选，不包含自动改写。`No Change` 配合 `uninvolved` 和 `insufficient` 区分未涉及与证据不足；有问题的响应、引文、backend 异常单独返回 `failed` 和异常类型，不输出异常内容。每条失败保留完整原事实，其他事实继续处理。
- 涉及事实、非 `unclear` 时间关系及修改候选要求逐字新证据引文。旧证据由拆分器原验证器检查并保留；每条新引文必须属于指定来源文本。新增候选为 `{source_id, quote, reason}`，候选就是新证据的原文片段，不能改写。候选识别失败是 `new_candidates.status=failed`，与成功但空数组不同。
- 程序验证引文存在及结构一致性，不验证引文的语义支持、时间先后、因果、事实真实性、旧事实拆分完整性或新增候选的独立性。时间分类及理由都只是模型候选，绝不可当作自动裁决。

示例和完整响应格式见 [test_judge.py](test_judge.py)，均为自拟数据。离线运行：

```bash
python -m unittest discover -s variants/evidence_temporal_judge -p 'test_*.py' -v
```

实际 v4 路径：`variants/dnd_mem0_splitter/prompt_versions/v4_boundaries_20261104/prompt.txt`；本次字节 SHA-256：`d9cc40259ac447e09cad93b775d7f0ff67fc9bb42443e18264b75f39b37067f3`。运行时报告实际路径与哈希，不强制将未来变更伪装成这个哈希。

## 实现取舍

先检查本地依赖和作者代码后，选择提取单事实分类流程、隔离自动改写和外部初始化；FactTrack 使用可检查的前态、后态、静态与重叠思想，不搬运故事坐标或其 NLI 阈值。比直接导入检测器更容易隔离副作用，但也因此尚未运行作者模型，也不等同于复现实验结果。具体逐项来源、改动和授权状态见 [PROVENANCE.md](PROVENANCE.md)。
