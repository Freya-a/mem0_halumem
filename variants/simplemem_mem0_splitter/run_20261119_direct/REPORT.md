# SimpleMem 拆分器：直连复试

## 连接与配置

原运行保存在 `../run/`，原 manifest 未覆盖。上次仅记下 APIConnectionError，未保存异常链，无法事后证明其唯一原因。本次检查到服务器进程使用的 HTTP 和 HTTPS 代理都指向服务器自己的回环地址，TCP 连接均被拒绝（errno 111）；用户说明代理运行在本地电脑。目标地址来自 `config/medium_full_qwen_plus_20251201.json`，workspace 来自 `.env.server.medium-full`；结构检查合格。服务器直接连接时 DNS 解析、TCP 连接和 TLS 证书验证均通过（TLS 1.3）。这些检查没有发起模型请求。

本轮以独立 `httpx.Client(trust_env=False)` 禁用当前客户端的环境代理，未更改系统设置；OpenAI SDK `max_retries=0`，HTTP 自动重定向关闭。请求到达 HTTPS 端点后收到 HTTP 403，错误码 `access_denied`；第 1 例没有收到模型响应，按要求停止。不能仅凭 403 判断是密钥、工作区、模型权限或其他访问策略所致。

只比较配置来源而未输出凭据：进程环境和 `.env.server.medium-full` 的 `DASHSCOPE_API_KEY` 均存在但不相同。本次调用沿用旧拆分器优先读取进程环境的规则，同时从文件取 workspace；项目 `scripts/medium_full.py` 的环境加载函数则以文件覆盖进程环境。凭据和 workspace 可能不匹配，是值得核查的原因，不是已证实结论。本轮未尝试更换凭据或再次请求。无模型响应、无解析结果，不能判断模型是否可用。脱敏检查细节见 `connectivity_diagnostic.json`；错误类型和异常链见 `case_1.json` 和 `manifest.json`。

## 调用计数与结果

- 固定请求模型：`qwen-plus-2025-12-01`；尝试 1 次，HTTP 403 失败 1 次，收到模型响应 0 次；其余 4 例未发送。第 1 次耗时 0.576 秒；无自动重试。
- 15 项离线程序测试通过，包含代理隔离和错误脱敏；它们不代表模型拆分成功。
- 真实输出的解析、逐字引文检查和语义分析均无法进行，也没有人工验收。

## 五例状态

以下列出完整旧记忆；每例的全部模型子事实、引文、条件、时间与未决项均为 **无结果**。待审点仅说明收到输出后应核查的内容，不是拆分结果。

1. **请求失败**：Martin Mark Pets I like Dogs, especially Labradors reason: I love Labradors because they are friendly, loyal, and great companions for outdoor activities like jogging, which helps me stay fit.  
   待审：偏好、友善忠诚、运动陪伴、保持健康及其关系。
2. **未请求**：Martin Mark Games I dislike Violent video games reason: I avoid violent video games because they promote aggression, which is contrary to my values of peace and well-being.  
   待审：否定偏好、避免的原因和价值观，不将陈述者的理由直接当客观事实。
3. **未请求**：[Sep 06, 2025, 22:43:36][Persona Memory]Martin Mark Movies I like to watch Documentaries reason: I enjoy documentaries because they are informative and provide real-world insights, which complement my thirst for knowledge.  
   待审：记录时间与事实有效时间、偏好和原因。
4. **未请求**：Martin desires to continue contributing to healthcare initiatives even if he retires from his current role.  
   待审：愿望与 even if 条件，不能断言已经退休。
5. **未请求**：Martin Mark is considering a career change due to health impacts from his current role.  
   待审：考虑这一不确定状态、工作对健康的影响及其原因关系。

## 后续

当前只适合无模型响应的接口格式联调，尚不适合判断拆分质量或开展真实拆分输出的判断器接口试验。应先核查工作区权限和凭据来源；项目 medium-full 的文件优先规则可作为下一轮独立试验的配置候选，但目前未经请求验证。按照本轮“第一例失败即停止”的要求，本轮不再尝试。
