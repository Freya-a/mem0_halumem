# 单个更新目标诊断计划

Goal: 在原生 Mem0 0.1.118 中完成一个静态选中的更新标注所在完整会话。
Spec: 本轮用户请求；原运行 REPORT.md 保存在 linked_original 中。
Architecture: 离线核验历史后复制数据库续接；失败则新库重建完整历史前缀。包装调用只观察，原响应与异常原样返回。
Constraints: conda mem0_halumem；qwen-plus / text-embedding-v4；不将标注、persona、答案传给系统；不强制 UPDATE；只运行至一个目标会话结束。

- [x] 静态按固定用户、时间、标注顺序查找目标；兼容布尔值与字符串。
- [x] 核验前两完整会话、API 输入、29 条记忆、历史及磁盘；选择复制续接或新库重建。
- [x] 记录完整输入/时间、提取事实、top-5 候选 ID/score、更新模型输入输出、含 NONE 的计划、调用执行结果与异常。
- [x] 每会话全量快照、历史重放；最终重新打开数据库与 SQLite integrity_check。
- [x] 按目标新旧命题生成原文、ID、日志位置对照；证据不足标未知。

Review focus: 字符串 False 不应判真；历史输入不应重复；Qdrant 浮点容差；NONE 不在 add 返回中；标注不得污染输入。
Decision: 这是用户已授权的诊断运行，直接执行，不变更两个源码仓库或提交代码。原目录非 Git 仓库，使用独立结果目录隔离。

结果：诊断完成，保留 1 条原生无效 ID UPDATE 错误和执行器严格检查失败；没有修复原生行为或重复输入。详见 REPORT.md 与 independent_verification.json。
