# 代理端口冲突修复记录

日期：2026-11-03（Asia/Shanghai）。

## 原因与修改

当前执行环境的大写 HTTP_PROXY/HTTPS_PROXY 指向 http://127.0.0.1:17897，小写 http_proxy/https_proxy 指向 http://localhost:7890。HTTPX 原先选中小写配置的 7890，该本地端口拒绝连接；17897 本地端口可连接。

修改 real_backend.py：在创建真实 HTTP 客户端前，若大写 HTTP_PROXY 或 HTTPS_PROXY 非空，就将该值复制到当前进程对应的小写变量。只在拆分器进程生效，不写 shell 配置、VS Code settings.json 或项目 .env.local。端口未硬编码；本环境选中 17897 是因为大写变量当前配置如此。

大写未配置时保留小写行为；HTTP 与 HTTPS 分别对齐。NO_PROXY、ALL_PROXY 和 TLS 设置不改动，继续交由 HTTPX 处理。注入的模拟客户端不走该环境对齐路径。SDK max_retries=0、单次请求限制、原有提示词及来源校验不变。

## 备份与文件

修改前 real_backend.py 保存在 backups/proxy_fix_20261103/real_backend.py，所有原有文件哈希保存在同目录 before_sha256.json。最终比对确认，本次开始时已有文件中只有 real_backend.py 改变；原有设计、模拟版、样例和上次真实调用记录均未改变。

新增 test_proxy_config.py 和本文档。没有覆盖备份或历史运行记录。

## 验证

先写代理回归测试：修复前 2 项失败，实际误选 localhost:7890；另 2 项已有行为通过。

修复后执行：

```bash
python3 -B -m unittest discover -s . -p 'test_*.py' -v
```

实际结果：38 项测试全部通过。覆盖大小写冲突、分别处理 HTTP/HTTPS、仅小写配置、NO_PROXY 绕过，以及原有模拟和真实适配器离线测试。

随后在当前环境只创建 HTTP 客户端、不调用 create，确认 HTTPS 实际代理为 127.0.0.1:17897，调用计数 0。本地 TCP 检查确认该端口可连接。未向外部服务发送探测请求，未验证完整远端链路。

本次新增真实模型调用 0 次；上次 1 次连接失败记录保持不变。没有安装依赖、接入 Mem0、读取开发子集、写入知识库或修改 external/。
