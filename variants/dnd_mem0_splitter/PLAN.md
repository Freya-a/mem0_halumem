# 独立 DnD Mem0 拆分模拟器实施计划

> 执行方式：当前会话直接实施，测试先行，不委派模型或子代理。

**Goal:** 在指定目录内实现只有手写模拟后端的独立拆分接口和严格来源校验。

**Architecture:** 输入快照由程序保留；可调用后端仅提供候选 facts。验证所有候选后再组装输出。CLI 只读 JSON 文件，成功写 stdout，失败写 stderr 并退出 2。

**Tech Stack:** Python 标准库；不安装依赖。

**Spec:** DESIGN.md 与用户本次范围要求。

## 全局约束

- 不连接或修改 Mem0，不写知识库，不调用模型或读取 API 密钥。
- 不读取或运行开发子集，不修改 external/。
- 只在用户指定 variants/dnd_mem0_splitter/ 内新增文件，不覆盖已有文件。
- 该位置不是 Git 仓库；直接按指定目录实现，不创建 worktree、分支或提交。
- 所有创建使用排他创建；执行使用 python3 -B，避免生成字节码缓存。
- 验证范围仅为本独立模块及自拟数据；不运行项目级测试以免越过开发子集限制。

## Review Focus

- ID 和原文不能被后端修改或覆盖；测试缺失顶层回显、错误回显和后端修改参数。
- 引文必须匹配所声明的具体来源；测试记忆引文、上下文引文和未知来源。
- 非空必填字段、明确的列表类型、连续整数序号；拒绝 bool 伪装序号。
- 上下文可省略，source_id 不可重复；事实不能只有上下文依据。
- CLI 失败时不输出部分成功结果；重复 JSON 键不应被静默吞掉。

## Task 1：保存设计、自拟样本与先行测试

- [ ] 排他创建 DESIGN.md，保存讨论中的设计、完整提示词及手写示例。
- [ ] 创建 examples/input.json、mock_response.json、mock_response_bad_quote.json。
- [ ] 创建 test_splitter.py，运行本模块 unittest，观察实现缺失导致失败。

## Task 2：实现并验证独立程序

- [ ] 实现 splitter.py：ValidationError、FactBackend 协议、MockBackend、split_memory(request, backend)、CLI。
- [ ] 以输入快照组装结果；校验候选字段、ID、序号、来源及逐字引文，拒绝错误。
- [ ] 运行本模块完整 unittest，再运行正常和引文不匹配 CLI 示例。
- [ ] 创建 README.md 和 VERIFICATION.md，记录命令、实际结果、能力边界及自检。

## 实施决定

- 保留 DESIGN.md 中的完整提示词；后端接口只要求返回 facts。若额外回显 memory_id 或 memory_text，必须一致，否则报错，不静默忽略。
- 首版不自动执行提示词、不自动拆分文本；模拟响应由调用方手写提供。
- 校验能证明字段与来源文本的结构关系，不能证明语义忠实性、完整覆盖、指代正确性、上下文可靠性或现实真实性。
- 无 Mem0 查询，因此无法确认输入 ID 是否真实存在；由调用方保证。
- 当前工作只有新增文件，不进行外部集成；按用户要求自检，不另行调用模型审查。
