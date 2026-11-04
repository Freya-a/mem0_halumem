# 独立旧记忆事实拆分器：模拟初版

Python 3.10+，仅使用标准库。当前环境验证版本为 Python 3.12.7。没有真实模型客户端、Mem0 客户端或 API 密钥读取逻辑。

本版验证“输入 → 手写候选响应 → 校验 → 输出”的接口流程，**不会自动从任意文本生成事实**。全部示例为手写自拟数据，不是模型运行结果；示例 ID 不是真实 Mem0 ID。

## 文件

- DESIGN.md：已讨论的输入、输出、完整提示词、手写输入与期望输出，以及 DnD 借鉴和 Mem0 新增部分。
- PLAN.md：实现计划和范围约束。
- splitter.py：Python 接口、手写模拟后端、字段/来源校验及命令行程序。
- test_splitter.py：本模块 23 项测试，包含 CLI 验证。
- examples/input.json：自拟输入。
- examples/mock_response.json：手写正常候选响应，仅含 facts。
- examples/mock_response_bad_quote.json：只把上下文引文中的“上海”改为“北京”的错误响应。
- VERIFICATION.md：实际验证命令、退出码和完整示例输出。

## 运行模拟验证

在目标目录运行：

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter
python3 -B splitter.py --input examples/input.json --mock-response examples/mock_response.json
```

成功：退出码 0，完整设计 JSON 写入 stdout，stderr 为空。输出两条事实，顶层 ID 和原文由程序从输入保留，不要求模拟响应提供。

运行引文不匹配的情况：

```bash
python3 -B splitter.py --input examples/input.json --mock-response examples/mock_response_bad_quote.json
```

预期失败：退出码 2，stdout 为空；stderr 输出结构化错误，code 为 quote_not_found，path 为 $.facts[1].evidence[1].quote。程序不会修正“北京”，也不会输出部分成功结果。

运行本模块全部测试：

```bash
python3 -B -m unittest discover -s . -p test_splitter.py -v
```

也可以从任意工作目录运行：

```bash
python3 -B -m unittest discover -s /home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter -p test_splitter.py -v
```

程序只读取显式指定的输入文件和手写响应文件，运行时不保存结果、不修改输入。测试仅使用 examples/ 与内存中的自拟变体；临时 JSON 在本目录下的独立临时子目录中创建并自动清理。`-B` 避免创建 Python 字节码缓存。

## Python 接口与未来模型调用接口

在本目录可导入：

```python
from splitter import MockBackend, split_memory

result = split_memory(input_dict, MockBackend(handwritten_response_dict))
```

`FactBackend` 是可调用对象协议：接收一份已验证输入的独立副本，返回候选 JSON 对象，必填字段为 facts。这里没有实现真实模型调用或自动执行 DESIGN.md 中提示词的逻辑。

后端可额外回显 memory_id 和 memory_text；若与输入不一致会报错。每条候选事实必须有匹配的 source_memory_id，程序核对后再从原输入写入该字段。顶层 ID 和文本始终来自程序保存的输入快照；后端修改收到的参数不会改掉这份快照。

## 校验约定

- 必填字段与非空字符串、对象/数组类型、从 1 开始的连续整数序号；bool 不被当作整数序号。
- 输入 source_context 可省略，但显式提供时必须是数组，不能是 null。每项需有 source_id、source_ref、text；speaker、recorded_at 可选。
- 上下文 source_id 唯一；来源类型仅允许 memory 或 context。
- 每条事实至少包含一条原记忆依据；source_memory_id 与所有 memory 依据的 source_id 必须匹配输入 ID。
- context 依据必须指向输入中存在的 source_id。
- 所有 quote 必须是所声明来源文本的非空逐字子串；不做去空格、大小写或 Unicode 归一化。
- pending_confirmations 必须是数组；每项包含非空 item、reason；允许空数组。
- 未约定字段和重复 JSON 键明确拒绝，避免静默丢弃或覆盖。
- facts 可为空；程序无法自行判断“没有事实”是否在语义上正确。
- 验证失败抛出 ValidationError；CLI 输出含 code、path、message 的错误 JSON，退出码 2。

## 当前能力边界

- 不自动拆分文本，不执行提示词，不调用真实模型，也没有 Mem0 集成。
- 不验证输入 ID 是否真实存在于 Mem0；真实 ID 与可靠上下文必须由调用方提供。
- 引文匹配只证明文字出现在指定来源中，不能证明它支持候选命题或 supports 的解释。
- 不自动保证人物指代、时间、条件、否定、情态得到忠实保留；这些目前是提示词要求及人工复核项目。
- 不能证明拆分完整、不重复、粒度合适，也不能发现所有应标记但未标记的待确认项。
- 不核验现实真实性、来源可靠性或来源冲突，不提供原文字符位置映射。
- 尚无模型质量评估，不能认定优于 FActScore。

本次只新增目标目录文件；未连接或修改 Mem0，未修改 external/，未读取或运行开发子集，未写入知识库，未安装依赖。
