# HaluMem-Medium 开发诊断准备 Implementation Plan

Goal: 固定约3用户、20—30个有原始对话证据的更新目标，准备Linux顺序输入和审计入口，本轮不运行模型。
Architecture: 标准库离线选样与验证；沿用已有 local_smoke 快照/API审计及 local_update_case.Observer；正式执行每用户独立进程和数据库，逐会话提交检查点。
Tech Stack: Python 3.11, Conda mem0_halumem, editable Mem0 0.1.118, Qdrant local, SQLite。
Spec: 本轮用户请求；已明确授权完成实现及离线检查。当前根目录不是Git仓库，不创建提交或改动两个源码仓库。

## Global Constraints
- 所有模型输入仅含当前完整原始dialogue的role/content；infer=True；从用户首会话到最后目标，不跳会话。
- 保留已调试用户，其他UUID排序后random.Random(42).sample补足3用户。
- is_update只是候选入口；旧命题必须有早期原始用户对话支持，新命题须有当前原始对话支持。
- 所有初标待人工核验；补充与局部变化不得推断全面失效。
- 无模型/QA/评分/服务器登录；只静态数据校验、语法检查及断网dry-run。

## Review Focus
- 同会话相关目标共享输入和操作，不能独立计数实验。
- SDK隐藏重试和Mem0吞错：记录错误并阻止提交检查点。
- 会话部分写入或崩溃：拒绝普通resume；显式回滚到会话前副本并保留异常产物。
- 空事实及NONE必须保留，缺usage不估算。
- 可迁移路径、源码哈希、数据哈希、配置指纹、已提交快照与history一致性。

## Tasks
- [x] 离线规则先落盘，证据配方、固定manifest/CSV/不足证据表/前缀和排除账本；验证引用、时间和数量。
- [x] 准备服务器配置、版本约束、预检、dry-run、顺序运行、恢复和审查导出入口。
- [x] 断网dry-run验证泄露边界/完整前缀/检查点与恢复约束；编译代码；记录未运行状态与命令。

验证证据：数据校验通过；3个新脚本py_compile通过；断网preflight/dry-run通过，24目标/16会话组，前缀9+8+11，990消息；自定义输出目录dry-run通过；模型调用0、Memory实例0。正式服务器安装、模型、QA和评分未运行。
