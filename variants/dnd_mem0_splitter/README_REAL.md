# 真实模型适配入口（与模拟版并存）

原有 DESIGN.md、splitter.py、README.md、测试和样例均未修改；原有九个文件的 SHA-256 与任务开始时一致。原 README.md 描述的是模拟版，本文件补充新增真实调用能力。

## 新增文件

- real_backend.py：项目配置读取、设计提示词提取、OpenAI 兼容单次调用后端。
- run_real.py：独立真实调用 CLI，复用 splitter.split_memory，保存成功或失败证据。
- test_real_backend.py：11 项离线适配器测试。
- PLAN_REAL.md：本次实施方案和范围约束。
- runs/real_20261103_once/：本次唯一真实请求的输入、提示词、尝试标记、响应元信息、失败报告和人工复核记录。

## 配置与接口

静态参考项目 scripts/local_smoke.py 的 read_env/load_settings 和模型配置，以及 mem0_v0.1.118/mem0/llms/openai.py 的 Chat Completions 用法；不导入或实例化 Mem0，不执行项目脚本。

默认只读取项目根目录 .env.local，必需名称为 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL。支持项目已有 OPENAI_BASE_URL、OPENAI_API_KEY、OPENAI_MODEL 别名，沿用同名进程变量覆盖文件、主名称优先于别名的规则。不扫描 HaluMem 配置或开发子集，不使用其他厂商密钥替代缺失配置。

当前已配置模型为 qwen-plus，已有 openai 1.100.2 与 httpx 可导入；本次未安装依赖。配置存在不代表远程服务已验证可达。OPENAI_MAX_TOKENS、OPENAI_TEMPERATURE、OPENAI_TIMEOUT 若存在则沿用；未配置生成参数时不额外指定。超时默认 180 秒，与项目脚本一致。

后端调用 client.chat.completions.create，设置 response_format 为 json_object。system 消息是 DESIGN.md 中完整 text 提示词块，user 消息只包含输入 JSON。代码不执行模型发现、不更换模型、不回退。

输入 ID 和原文由 splitter.py 的输入快照保留；模型若回显不一致的 ID 或原文会被拒绝。模型内容不剥代码块、不修补 JSON，直接沿用原有结构、ID 和逐字引文校验。

## 请求限制与文件保留

- SDK max_retries=0，HTTP 重定向关闭；每个后端实例最多尝试一次 create。
- 新入口必须指定一个尚不存在的目标子目录；已有目录报错，不重新发送请求。
- 限制作用于每个实例和运行目录，并非跨所有新目录的全局计数。本次实际只启动了一次真实请求。
- 输入、提示词和 attempt.json 在请求前保存。原始模型文本仅在收到时保存为 raw_content.txt；自动检查通过才保存 result.json。
- API 失败不保存含凭证风险的完整异常字符串、HTTP 头或响应正文，仅记录异常类型、HTTP 状态等安全信息。
- 从调用返回但未通过 JSON/来源检查的模型文本会保留，不自动重试或纠错。
- 保存文件使用排他创建，程序不覆盖原有文件。

## 本次真实调用（已经执行，不再重试）

执行命令：

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis/variants/dnd_mem0_splitter
python3 -B run_real.py --input examples/input.json --run-dir runs/real_20261103_once
```

实际结果：退出码 2；请求模型 qwen-plus；调用尝试 1 次；APIConnectionError；没有 HTTP 状态码或模型内容，未重试。该目录已存在，再次使用同一命令会在发送请求前拒绝运行。

详情见 runs/real_20261103_once/report.json、response_metadata.json 和 SEMANTIC_REVIEW.md。不存在 result.json 或 raw_content.txt，因为没有收到模型输出；这不是空事实列表，也不能解释为拆分成功。

## 离线验证

```bash
python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

34 项通过：原有 23 项加新增 11 项。新增测试通过 httpx.MockTransport 和自拟配置执行已安装 SDK，不请求真实模型、不读取 .env.local 或开发子集。测试临时文件在目标目录内创建并清理。

覆盖配置缺失与优先级、提示词精确提取、单次调用限制、HTTP 500 不重试、截断和无效 JSON、复用来源检查、失败证据保存、拒绝覆盖与敏感字段不进入日志。离线测试通过不能证明远程模型已可用，也不能替代实际语义检查。

## 当前限制

本次连接失败的底层原因未确定；安全日志没有保存完整异常链，无法仅据现有信息区分 DNS、代理、TLS 或远程服务连通性问题。为了遵守一次请求限制，本次没有再发网络探测或模型请求。

实际来源引文检查未执行，人物、时间、条件、否定和情态均没有模型输出可供人工判断。即使未来一次样例通过，也不能认为拆分效果已经可靠。

未连接或修改 Mem0、未读取或运行开发子集、未写知识库、未修改 external/、未安装依赖。输入样例中的记忆 ID 仍为手写占位，并未核查真实 ID 是否存在。
