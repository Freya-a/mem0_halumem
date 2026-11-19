# ERASE 原始仓库下载与静态检查记录

记录日期：2026-11-03（Asia/Shanghai）。本说明独立存放于 `external/`，未写入或修改 ERASE 原仓库。

## 保存位置与下载状态

| 项目 | 记录 |
| --- | --- |
| Mem0 项目根目录 | `/home/shu1004/ld/system/mem0_halumem_diagnosis` |
| ERASE 实际保存路径 | `/home/shu1004/ld/system/mem0_halumem_diagnosis/external/ERASE` |
| 下载前状态 | `external/` 和 `external/ERASE/` 均不存在，本次新建；未覆盖既有目录 |
| 作者仓库 | <https://github.com/belindal/ERASE> |
| 本地 origin（fetch/push） | `https://github.com/belindal/ERASE.git` |
| 分支 | `main`，本地 `HEAD` 与本次克隆得到的 `origin/main` 一致 |
| 当前 commit | `b93f898780b3cf40fedd4e9a00c51af9a27688bc` |
| commit 时间 | `2024-06-19T12:13:06-04:00`（保留 Git 原时区） |
| commit 标题 | `Update README.md` |
| 下载方式 | 完整 Git 克隆，保留 `.git/`；使用 `--recurse-submodules`，未使用浅克隆或部分克隆参数 |
| 下载结果 | 成功；非浅仓库，`HEAD` 历史共 8 个 commit，当前版本含 35 个受版本控制文件，无 Git 子模块 |

首次联网因本地代理连接失败而未下载成功。最终仅在下载进程中忽略失效的小写 `http_proxy`、`https_proxy` 变量，使用已有的大写代理变量完成克隆；未修改持久代理设置或 Git 全局配置。

## 论文信息

- 论文名称：**Language Modeling with Editable External Knowledge**。
- 作者：Belinda Z. Li、Emmy Liu、Alexis Ross、Abbas Zeitoun、Graham Neubig、Jacob Andreas。
- 年份：2024。
- 论文：<https://arxiv.org/abs/2406.11830>。
- 对应关系：论文页面将代码与数据链接至 `belindal/ERASE`；仓库 [README](ERASE/README.md) 的开头及 BibTeX 给出了相同论文名称和作者。

## 许可证状态

**当前 commit 未发现明确的代码许可证，许可证类型无法确认。**

- 受版本控制文件中未发现 `LICENSE`、`LICENCE`、`COPYING`、`NOTICE` 等许可证文件。
- 对 README、Python、Shell、文本依赖清单及 HTML 模板的静态检索，未发现明确的许可证、SPDX 标识或版权授权声明。
- 本记录不为原仓库补写许可证，也不根据 GitHub 公开可访问状态或论文页面的许可信息推定代码许可。
- 这些结论限于上述 commit 的已下载内容，未确认作者是否在其他渠道提供过授权。

## 主要依赖

以下信息来自原仓库文件和静态导入检查，**未执行安装脚本、未安装或导入这些第三方包**。

### README 与安装脚本中的环境及额外依赖

| 依赖 | 原仓库声明及检查结果 |
| --- | --- |
| Python | [README](ERASE/README.md) 示例指定 `3.11` |
| PyTorch / CUDA | README 要求安装 PyTorch，示例为 `pytorch-cuda=12.1`；PyTorch 本身未固定版本，CUDA 需与机器兼容 |
| FAISS GPU | [setup.sh](ERASE/setup.sh) 指定 `faiss-gpu=1.8.0`；代码导入 `faiss` |
| GENRE | setup.sh 克隆 <https://github.com/facebookresearch/GENRE.git> 并调用模型下载脚本；未固定 commit；代码导入 `GENRE.genre.trie` |
| fairseq | setup.sh 克隆 <https://github.com/nicola-decao/fairseq> 的 `fixing_prefix_allowed_tokens_fn` 分支并以 editable 方式安装；未固定 commit |

### requirements.txt 原始清单

原始 [requirements.txt](ERASE/requirements.txt) 共 19 项，内容如下：

```text
accelerate
backoff
Flask
matplotlib
newspaper3k
nltk
numpy
mistral-common==1.0.2
openai
pandas
requests
seaborn
sentence-transformers
selenium
termcolor
tiktoken
tqdm
transformers
google
```

只有 `mistral-common==1.0.2` 固定了版本，其他 18 项未指定版本。主要涉及模型推理与表示（PyTorch、transformers、sentence-transformers、accelerate）、检索（FAISS、GENRE）、API 与分词（openai、requests、tiktoken、mistral-common）、数据处理、网页采集和 Flask 标注界面。

静态导入还出现 `regex`、`bs4` / `BeautifulSoup`，但它们未直接列入上述 requirements；是否由传递依赖提供、相应版本和兼容性均未验证。当前仓库未提供依赖锁文件。

### 未确认或未下载的外部内容

- 未克隆或安装上述 GENRE、fairseq 等额外依赖，也未下载其模型权重。
- README 描述了 TogetherAI / OpenAI API 和本地 Hugging Face 模型的运行方式；本次未调用任何模型或 API，也未验证服务、权重及凭据可用性。
- README 将 CLARK-Conversations 数据标为 `Coming soon`。本次完整保留仓库实际发布的文件，不补造作者未发布的内容。
- 未验证依赖能否成功安装、各包之间或与现有 Mem0 环境的兼容性；未运行实验或原仓库测试。

## 完整性及范围核验

- `git fsck --full --strict` 通过。
- 将当前版本全部 35 个受版本控制文件逐一按 Git blob 哈希复核，均与 `HEAD` 一致。
- ERASE 工作区 `git status --porcelain=v1 --untracked-files=all` 为空，原仓库无修改或额外未跟踪文件。
- 对下载前记录的 3,871 个既有文件或符号链接复核大小、权限、修改时间和链接目标，未发现变化；`external/` 外未发现新增文件。
- 本次项目内仅新增 `external/ERASE/` 与本说明；未安装依赖、未运行 `setup.sh`、未运行实验、未调用模型，未修改已有数据、代码、环境文件或历史结果。

## 固定版本的检查依据

- [README（当前 commit）](https://github.com/belindal/ERASE/blob/b93f898780b3cf40fedd4e9a00c51af9a27688bc/README.md)
- [requirements.txt（当前 commit）](https://github.com/belindal/ERASE/blob/b93f898780b3cf40fedd4e9a00c51af9a27688bc/requirements.txt)
- [setup.sh（当前 commit）](https://github.com/belindal/ERASE/blob/b93f898780b3cf40fedd4e9a00c51af9a27688bc/setup.sh)
