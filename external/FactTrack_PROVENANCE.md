# FactTrack 原始仓库来源与静态检查记录

检查日期：2026-11-03（Asia/Shanghai）。本说明位于 FactTrack 仓库之外。

## 论文与作者仓库

- 论文名称：**FactTrack: Time-Aware World State Tracking in Story Outlines**（PDF 标题排作 FACTTRACK）。
- 作者：Zhiheng Lyu、Kevin Yang、Lingpeng Kong、Daniel Klein（按论文 PDF 首页署名）。
- 发表信息：NAACL 2025，Long Papers，页码 2825–2848。
- [论文条目](https://aclanthology.org/2025.naacl-long.144/)；DOI：`10.18653/v1/2025.naacl-long.144`。
- [论文正文 PDF](https://aclanthology.org/2025.naacl-long.144.pdf)：已核对第 1 页（印刷页码 2825）脚注 1，作者在此给出代码和数据仓库 `https://github.com/cogito233/fact-track`。
- 作者仓库：[cogito233/fact-track](https://github.com/cogito233/fact-track)。本次直接克隆此仓库，没有使用第三方复现或替代实现。
- 论文脚注没有固定 commit，无法确认下述 commit 与论文实验使用的代码版本完全相同。

## 本地保存与版本

| 项目 | 实际检查结果 |
| --- | --- |
| 首次检查 | `diagnosis/external/FactTrack/` 不存在，其父目录 `diagnosis/external/` 也不存在 |
| 操作记录 | 首次完整克隆至 `diagnosis/external/FactTrack/`；随后按用户要求整体移动至项目根目录下的 `external/`，保留 `.git` 和历史 |
| 项目内路径 | `external/FactTrack/` |
| 实际绝对路径 | `/home/shu1004/ld/system/mem0_halumem_diagnosis/external/FactTrack/` |
| origin（fetch / push） | `https://github.com/cogito233/fact-track.git` |
| 本地分支 / 上游 | `main` / `origin/main` |
| HEAD commit | `8b09d7fa5a805aa45a0d87a376d255665bd69460` |
| commit 链接 | [8b09d7f](https://github.com/cogito233/fact-track/commit/8b09d7fa5a805aa45a0d87a376d255665bd69460) |
| commit 时间 | `2024-07-03T15:34:51+00:00`（提交者时间） |
| commit 消息 | `init commit` |
| HEAD tree | `f7a7a800d90e86bcf66992f58c8996b560b71754` |
| 工作区 | 干净；包含全部未跟踪项和忽略项的状态检查也为空 |
| 历史 | 非浅克隆；本地全部引用可达的提交共 2 个；未使用 depth、filter 或 single-branch 限制 |
| 文件完整性 | HEAD 共 58 个受跟踪文件（其中 53 个 Python 文件）；逐文件原始字节计算 Git blob 哈希，58 个均与 HEAD 一致 |
| Git 对象检查 | `git fsck --full` 退出码为 0，无错误输出 |
| 子模块 / Git LFS | 无 `.gitmodules`，HEAD 无 gitlink 项；58 个文件中没有 Git LFS 指针 |

首次克隆时执行的命令如下；目标路径为移动前的位置。两个 `-c` 选项仅作用于该命令，未写入全局配置：

```bash
git -c core.hooksPath=/dev/null -c core.autocrlf=false clone --recurse-submodules -- https://github.com/cogito233/fact-track.git /home/shu1004/ld/system/mem0_halumem_diagnosis/diagnosis/external/FactTrack
```

第一次尝试因环境代理 `localhost:7890` 连接被拒绝而失败，失败后目标目录没有残留。直连探测成功后，仅对下载子进程移除 HTTP/HTTPS/ALL 代理环境变量并完成克隆，没有更改现有代理配置。

## 许可证状态

- 在当前 commit 的全部受跟踪路径中，没有发现 `LICENSE`、`COPYING`、`NOTICE` 等项目级许可证文件；README 没有项目级许可声明。
- [GitHub 仓库元数据](https://api.github.com/repos/cogito233/fact-track)在检查时返回 `license: null`。
- 有一个文件级声明：[fact-track/utils/llama_api_vLLM.py](https://github.com/cogito233/fact-track/blob/8b09d7fa5a805aa45a0d87a376d255665bd69460/fact-track/utils/llama_api_vLLM.py)第 1–2 行标明 Meta 版权，并指向 **Llama 2 Community License Agreement**。仓库没有附带该协议全文。
- 因此，**无法确认整个 FactTrack 项目的统一许可证**，不能将该文件的许可声明推广为全项目许可证；本次也未确认外部数据、模型及各第三方依赖的许可。

## 主要依赖：仅静态识别

README 第 14–18 行引用 `env.yml` 创建 Conda 环境。但当前原始 [env.yml](https://github.com/cogito233/fact-track/blob/8b09d7fa5a805aa45a0d87a376d255665bd69460/env.yml)只有 7 字节 `[y/N]: `（尾部一个空格，无换行），与 HEAD 中的原文件一致，并非本次下载损坏。它没有提供有效的 Conda 环境依赖清单。仓库也未提供 `requirements.txt`、`pyproject.toml`、`setup.py` 或依赖锁文件。

以下包根据 53 个 Python 文件的静态导入识别；没有导入或执行这些文件。路径相对于 `FactTrack/`。包名与导入名不同时单独注明。

| 包 / 导入名 | 代码中的用途 | 代表性证据 |
| --- | --- | --- |
| `torch`（PyTorch） | 模型推理、NLI 训练、CUDA 操作 | `fact-track/utils/gpt_api.py:9`；`fact-track/nli/finetuning_NLI.py:2` |
| `transformers` | tokenizer、预训练模型和 Trainer | `fact-track/utils/huggingface_api.py:12`；`fact-track/nli/finetuning_NLI.py:1` |
| `openai` | OpenAI 客户端 | `fact-track/utils/gpt_api.py:11` |
| `vllm` | LLaMA 推理 | `fact-track/utils/llama_api_vLLM.py:7` |
| `huggingface-hub` / `huggingface_hub` | Hugging Face 模型资源工具导入 | `fact-track/utils/llama_chat_api_vLLM.py:1` |
| `tiktoken` | token 计数 | `fact-track/utils/gpt_token.py:1` |
| `pandas` | 表格、事实对和标注数据处理 | `fact-track/core/contradict_detector.py:1` |
| `numpy` | 数值处理 | `fact-track/analyze/convert_dataTemplate.py:3` |
| `scipy` | 余弦距离及统计计算 | `fact-track/utils/huggingface_api.py:60`；`fact-track/oddAnno/scoreVis_pos.py:6` |
| `scikit-learn` / `sklearn` | NLI 评估指标 | `fact-track/nli/finetuning_NLI.py:119` |
| `datasets` | NLI 数据集构造 | `fact-track/nli/finetuning_NLI_data.py:37` |
| `requests` | Together 模型接口的 HTTP 请求 | `fact-track/utils/llama32K_api.py:3` |
| `ray` | 数据清理模块中的分布式计算相关导入 | `fact-track/analyze/dataStructure_cleaning.py:4` |
| `fire` | LLaMA 工具模块中的命令行库导入 | `fact-track/utils/llama_api_vLLM.py:4` |
| `tqdm` | 进度显示 | `fact-track/ablation/reCheck_factPair.py:4` |

这些依赖的精确版本、Python 版本、CUDA 版本、完整传递依赖及与现有 Mem0 环境的兼容性均未确认；上表不是经过安装验证的环境清单，不同功能分支可能只涉及其中一部分。

另有代码引用 `llama_api`、`chatGPT_API`、`chatGPT_contradictDetector_factDecompose`，但当前完整 Git 树没有对应模块文件；是否需要作者仓库外的旧代码或路径配置无法确认。本次未补齐或修改。

## 仓库外资源与未确认事项

README 第 32–36 行另列四个 Google Drive 资源，它们不属于当前 Git 树中的文件：

- [Premise](https://drive.google.com/file/d/1X-MGuToTBVB_wBk0wFgCFIjPBXaHt8hM/view?usp=sharing)
- [Model](https://drive.google.com/file/d/1W0oe1KkaXUlqQZd5uc7s0AsVkPYoaJjl/view?usp=sharing)
- [Data Generated](https://drive.google.com/file/d/150qsMNI2lmLrsFIfiGwNyxqwZdiJXS5O/view?usp=sharing)
- [Data Analisis](https://drive.google.com/file/d/1XQXv3fGscLEp1dyvNrIqrB6H4miJLWZi/view?usp=sharing)（原 README 拼写）

本次未下载或验证这些外部资源的可访问性、内容、版本、许可证和校验和，也未下载 Hugging Face 模型或其他权重。因此，已保存的是完整原始 **Git 仓库**，尚不能确认复现实验所需的外部资源齐备。

静态代码还引用 `facebook/contriever`、本地微调 NLI 目录 `models/results_18k`、训练基座 `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli`，以及作者机器上的 LLaMA 权重路径。部分模块使用 `BASE_PATH`、`OPENAI_API_KEY`、`TOGETHER_API_KEY`；本次没有设置、读取其凭据值或验证这些运行条件。

## 本次操作边界

- 原始克隆与仓库外的本说明文件现位于项目根目录的 `external/`；首次克隆在 `diagnosis/external/`，随后已整体移动。
- 没有编辑 FactTrack 原项目、添加补丁、改写提交、切换版本或向其中放入本说明。
- 没有安装依赖、创建 Conda/venv 环境或更改现有 Mem0 环境。
- 没有运行 FactTrack 脚本、测试或实验，没有调用模型或推理 API，也没有加载模型权重。
- 验证仅涉及 Git 元数据与对象完整性、文件原始字节比对、文本搜索和 Python AST 静态解析；未验证实验可运行性或论文结果。
