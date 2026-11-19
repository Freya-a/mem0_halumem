# 环境和来源记录

- 开始时 GPU：NVIDIA GeForce RTX 3090 Ti，24,564 MiB；基线设备占用约 367 MiB，驱动 535.309.01；`nvidia-smi` 报告驱动支持 CUDA 12.2。
- 编译器：CUDA Toolkit/nvcc 12.1.66、GCC 11.4.0；CMake 4.2.1（使用服务器已安装的独立二进制，未修改 Python 环境）。
- GGUF 发布仓库：https://huggingface.co/unsloth/Qwen3.5-27B-GGUF ，固定修订 `3221f178a6b842d04f1fb42f1c413534adcc0a6a`，文件 `Qwen3.5-27B-Q4_K_M.gguf`。
- 发布页面与 resolver 声明大小 16,740,812,704 字节、SHA-256 `84b5f7f112156d63836a01a69dc3f11a6ba63b10a23b8ca7a7efaf52d5a2d806`；模型文件通过 hf-mirror 的仓库 resolver 重定向到官方 Xet 文件获取。下载器仅在完整大小与 SHA-256 校验通过后创建正式文件。
- llama.cpp 上游 https://github.com/ggml-org/llama.cpp ，检出 `78ffbaa18533c2ed51eab2ef5ae0702330efc3e9`，源码含 QWEN35 架构。参照该检出中的 `docs/build.md` 配置 `GGML_CUDA=ON`、`CMAKE_CUDA_ARCHITECTURES=86`、`CMAKE_BUILD_TYPE=Release`、`LLAMA_CURL=OFF`、`LLAMA_BUILD_TESTS=OFF`、`LLAMA_BUILD_EXAMPLES=OFF`，生成器 Ninja，构建目标 llama-server。完整配置和编译日志保存在本目录。
- 只用于组件一；不调用组件二、不写入 Mem0，不更改驱动、系统 Python、原 Qwen3-8B 或原提示词。
- `llama-server` 构建成功，`--version` 返回 0.9.0-dev、commit 78ffbaa；`--list-devices` 枚举出 CUDA0 RTX 3090 Ti。构建时上游 Web UI 资源下载失败，构建回退为不嵌入 UI；本次使用 HTTP API，是否可用仍需实际启动验证。
- 下载过程中出现另一个已有 Python 进程占用约 820 MiB GPU 显存；没有对该进程作任何修改，实际加载前后的设备显存以启动记录为准。
