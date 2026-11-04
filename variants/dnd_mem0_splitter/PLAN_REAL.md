# 真实模型适配实施计划

用户已授权：沿用现有设计与接口，在 examples/ 自拟记忆上最多进行一次真实模型请求，不自动重试。

## 方案与约束

新增 real_backend.py 和 run_real.py，复用 splitter.split_memory 的校验与原文保留机制；不修改任何原有文件。与修改 splitter.py 相比，新增入口可完整保留模拟版并便于核对原文件哈希。

已检查：scripts/local_smoke.py 的 read_env/load_settings 和模型配置构造；静态检查 mem0/llms/openai.py 的 OpenAI 兼容 Chat Completions 用法。不会导入或实例化 Mem0，也不运行这些项目脚本。

使用项目 .env.local 的 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL；与现有读取规则一致，允许同名进程变量覆盖，以及 OPENAI_BASE_URL/API_KEY/MODEL 别名。只读取这一个指定配置文件，不扫描 HaluMem 或开发子集。当前确定模型为 qwen-plus，openai 1.100.2 已安装。不打印密钥、配置全文或完整环境变量。

后端直接使用已安装 OpenAI SDK 与 httpx，max_retries=0、禁止 HTTP 重定向、每个后端对象最多执行一次 create；无探测模型请求、重试、纠错请求或模型回退。没有配置则在请求前报错。

提示词逐字提取 DESIGN.md 的 text 代码块，不改写语义规则。输入作为单独 user JSON；JSON 模式请求返回对象。原始响应不剥代码块、不修补 JSON，严格复用现有字段和 quote 校验。

每次运行要求新的目标子目录；排他创建 input.json、prompt.txt、attempt.json、raw_content.txt、response_metadata.json、report.json；只有自动校验通过才保存 result.json。失败保留原始内容和错误原因，任何原有文件都不覆盖。

## 步骤

1. 先写离线测试：配置缺失、配置优先级、单请求、SDK 不重试、返回解析、引用校验、错误保留、原输入不受模型影响。
2. 观察未实现导致的失败，再新增适配器和入口。
3. 仅运行本模块测试；HTTP 测试使用 httpx.MockTransport，不访问真实服务。
4. 配置和离线验证通过后，只执行一次 examples/input.json 真实请求。
5. 分别记录自动检查与作者人工语义判断，保存 README_REAL.md 和本次语义复核记录；核对原有九个文件哈希。

## 能力边界

quote 匹配只证明字面溯源；人物、时间、条件、否定、情态保留以及拆分完整性仍需人工判断。一次通过不说明可靠性。示例 ID 是占位，不验证真实 Mem0 ID 是否存在。不接入 Mem0、不写知识库、不改 external/、不读或运行开发子集、不安装依赖。
