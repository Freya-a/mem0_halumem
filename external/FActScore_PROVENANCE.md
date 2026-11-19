# FActScore 原始仓库来源与静态检查记录

检查日期：2026-11-03（Asia/Shanghai）。本说明位于 FActScore 仓库之外；代码结论限定于下述当前检出 commit。

## 论文与作者仓库

- 论文名称：**FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation**。
- 作者（按论文 PDF 首页署名）：Sewon Min、Kalpesh Krishna、Xinxi Lyu、Mike Lewis、Wen-tau Yih、Pang Wei Koh、Mohit Iyyer、Luke Zettlemoyer、Hannaneh Hajishirzi。
- 发表信息：EMNLP 2023，页码 12076–12100；DOI：`10.18653/v1/2023.emnlp-main.741`。
- [ACL Anthology 论文条目](https://aclanthology.org/2023.emnlp-main.741/)；[论文 PDF](https://aclanthology.org/2023.emnlp-main.741.pdf)；[arXiv:2305.14251](https://arxiv.org/abs/2305.14251)。
- 作者仓库：[shmsw25/FActScore](https://github.com/shmsw25/FActScore)。论文 PDF 第 1 页（印刷页码 12076）脚注 1 给出此地址；原仓库 `README.md:8` 也说明这是论文官方发布。
- 本次使用作者仓库，没有使用第三方复现。论文没有在上述来源中固定源码 commit，**不能确认当前 commit 与论文实验所用版本完全相同**。

## 实际路径、下载与版本状态

| 项目 | 检查结果 |
| --- | --- |
| 首次检查 | 项目根目录的 `external/` 已存在，其中有 ERASE、FactTrack 及其说明；`external/FActScore/` 不存在（也不是已有符号链接） |
| 本次操作 | 完整 Git 克隆至指定目录，保留 `.git`、历史、远程分支引用和标签；没有使用浅克隆、部分克隆或单分支限制 |
| 项目内路径 | `external/FActScore/` |
| 实际绝对路径 | `/home/shu1004/ld/system/mem0_halumem_diagnosis/external/FActScore/` |
| 本说明路径 | `/home/shu1004/ld/system/mem0_halumem_diagnosis/external/FActScore_PROVENANCE.md` |
| origin（fetch / push） | `https://github.com/shmsw25/FActScore.git` |
| 当前分支 / 上游 | `main` / `origin/main` |
| HEAD commit | `f28272deffcf33efc1f1117d5479c10bb75221a9` |
| commit 链接 | [f28272d](https://github.com/shmsw25/FActScore/commit/f28272deffcf33efc1f1117d5479c10bb75221a9) |
| 提交者时间 | `2025-04-13T16:41:02-04:00` |
| 提交消息 | `Update download_data.py` |
| HEAD tree | `74fcb29e2557a3ec6017bdecafa4a0d64fd6c395` |
| 工作区 | 干净；`git status --porcelain=v1 --untracked-files=all --ignored` 输出为空 |
| 历史完整性 | `--is-shallow-repository` 为 `false`；本地全部引用可达的提交共 63 个；未发现本地 partial clone / promisor / filter 配置 |
| 检出文件完整性 | HEAD 有 18 个受跟踪文件（12 个 Python 文件）；逐文件按原始字节计算 Git blob 哈希，18 个均与 HEAD 一致 |
| Git 对象完整性 | `git fsck --full` 退出码为 0，无错误输出 |
| 子模块 / Git LFS | HEAD 无 `.gitmodules`、无 gitlink，18 个文件均不是 Git LFS 指针 |

成功执行的克隆命令如下。命令级选项和移除代理的操作仅作用于下载子进程，没有修改全局 Git 配置或现有环境配置：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy GIT_TERMINAL_PROMPT=0 git -c http.proxy= -c core.hooksPath=/dev/null -c core.autocrlf=false clone --recurse-submodules -- https://github.com/shmsw25/FActScore.git /home/shu1004/ld/system/mem0_halumem_diagnosis/external/FActScore
```

第一次使用现有代理设置的克隆尝试因 `localhost:7890` 连接被拒绝而失败；确认目标路径无残留后，才使用上述直连命令重试。成功后没有重复克隆、拉取更新、切换分支或改写历史。

## 许可证状态

- 当前 commit 的根目录 [LICENSE](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/LICENSE) 包含完整 **MIT License**，版权行为 `Copyright (c) 2023 Sewon Min`。
- [pyproject.toml:6](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/pyproject.toml#L6) 同样声明 `license = "MIT"`；[GitHub 仓库元数据](https://api.github.com/repos/shmsw25/FActScore)在检查时识别为 SPDX `MIT`。
- `factscore/clm.py:1–5`、`factscore/utils.py:1–5` 还保留 Facebook 的文件级版权注释，指向源码树根目录的 LICENSE；这些原始声明均已保留。
- 上述是仓库代码的许可声明。外部数据、模型权重、第三方依赖的许可证没有逐项核查，不能据此推定都采用 MIT。

## 主要依赖（仅静态识别，未安装）

版本栏按原始 [pyproject.toml:9–18](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/pyproject.toml#L9) 原样记录，属于声明的约束，不是本次解析或验证过的安装版本。

| 依赖 | pyproject.toml 声明 | 用途 / 代表性位置（相对于 FActScore/） |
| --- | --- | --- |
| Python | `^3.7.1` | 项目运行版本声明 |
| `torch` | `^1.13.0` | 模型推理和张量运算；`factscore/clm.py:12`、`factscore/npm.py:2` |
| `sentence-transformers` | `^2.2.2` | GTR 检索编码器；`factscore/retrieval.py:126–131` |
| `transformers` | `^4.29.2` | LLaMA、RoBERTa、NPM 模型和 tokenizer；`factscore/clm.py:16–17`、`factscore/npm.py:5`、`factscore/retrieval.py:47–48` |
| `openai` | `^0.27.7` | 原子事实生成及 ChatGPT 验证；`factscore/openai_lm.py:27–45,49–98` |
| `rank-bm25` / 导入名 `rank_bm25` | `^0.2.2` | 拆分演示检索与 BM25 段落检索；`factscore/atomic_facts.py:10,32–33,148–151`、`factscore/retrieval.py:9` |
| `spacy` | `^3.5.3` | 实体识别与事实后处理；`factscore/atomic_facts.py:22,203–230,232–289` |
| `pysqlite-binary` | `^0.5.0` | 原依赖清单中的 SQLite 相关发行包；源码 `factscore/retrieval.py:5` 实际导入 `sqlite3` |
| `nltk` | `^3.8.1` | 句子切分；`factscore/atomic_facts.py:8,13,53–54` |
| `poetry-core` | 构建系统 requires；未固定版本 | `pyproject.toml:20–22` |
| `numpy` | 未在 pyproject 中直接声明 | 多处静态导入，如 `factscore/atomic_facts.py:2`、`factscore/factscorer.py:4` |
| `tqdm` | 未在 pyproject 中直接声明 | 进度条；`factscore/factscorer.py:8`、`factscore/clm.py:13` |
| `pandas` | 未在 pyproject 中直接声明 | 可选 ACL 语料预处理；`preprocessing/preprocess_acl.py:1`；该脚本读取 Parquet，实际引擎依赖未确认 |

原始 [requirements.txt](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/requirements.txt) 的有效条目只有 `torch`、`sentence_transformers`、`transformers`、`pysqlite3`、`openai`、`rank_bm25`、`spacy`，均未固定版本；其中 SQLite 发行包名称与 pyproject 中的 `pysqlite-binary` 不同，且没有列出 `nltk`。第 9–11 行版本内容都是注释，不构成安装约束。HEAD 没有依赖锁文件。因此，**两份依赖清单不完全一致，不能当作已验证、可复现的环境锁定方案**；本次未补齐、升级或安装依赖，也未检查与现有 Mem0 环境的兼容性。

## 原子事实拆分代码位置与输出含义

**结论：当前 commit 的拆分器正常生成分支（`cost_estimate=None`）提供“句子文本 → 原子事实字符串列表”的对应关系及段落的句子索引；没有返回原文中的精确字符、字节或 token 起止位置。高层评分入口还会展平事实，丢弃句子分组和段落索引。**

| 代码位置 | 静态检查结果 |
| --- | --- |
| [factscore/atomic_facts.py:20–42](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L20) | `AtomicFactGenerator`；`run()` 按换行拆段、对段落做 `strip()` 并丢弃空段，然后交给段落处理函数 |
| [factscore/atomic_facts.py:44–93](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L44) | `get_atomic_facts_from_paragraph()` 使用 NLTK `sent_tokenize()`，修正句子切分，构建 `(sent, atoms[sent])`；正常生成分支返回 `(atomic_facts_pairs, para_breaks)` |
| [factscore/atomic_facts.py:96–145](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L96) | `get_init_atomic_facts_from_sentence()` 用 BM25 选演示、构造拆分提示、调用 `self.openai_lm.generate(prompt)`，返回以句子文本为键的事实列表字典（也补入演示字典中的条目） |
| [factscore/atomic_facts.py:154–163](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L154) | `text_to_sentences()` 将生成文本按 `- ` 切成事实字符串并清理；没有对齐原文跨度 |
| [factscore/atomic_facts.py:232–289](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L232) | `postprocess_atomic_facts()` 可合并单词句子、过滤重复或不完整事实、修正数字实体文本，并更新段落句子索引；返回仍是句子与事实列表的配对 |
| [factscore/atomic_facts.py:298–334](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/atomic_facts.py#L298) | `detect_initials()` / `fix_sentence_splitter()` 修正人名首字母等断句，可用空格拼接句子，没有维护原文位置映射 |
| [factscore/factscorer.py:128–152](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L128) | `FactScorer.get_score()` 创建拆分器；第 151 行忽略 `para_breaks`，第 152 行将各句事实展平为字符串列表 |
| [factscore/factscorer.py:199–207,261](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L199) | 最终评分输出含汇总指标与 `decisions`；每个事实决策仅有 `atom` 和 `is_supported`，没有来源句子或原文跨度 |
| [factscore/factscorer.py:339–345](https://github.com/shmsw25/FActScore/blob/f28272deffcf33efc1f1117d5479c10bb75221a9/factscore/factscorer.py#L339) | `--use_atomic_facts` 从外部数据的 `annotations` / `model-atomic-facts` 读取 `atom["text"]` 并展平；这里没有读取或输出位置字段 |

下列仅为根据源码整理的结构示意，**不是本次模型调用或运行产生的输出**：

```text
AtomicFactGenerator.run(generation, cost_estimate=None)
  -> (
       [(sentence_text_0, [fact_text_0, fact_text_1, ...]),
        (sentence_text_1, [fact_text_2, ...]), ...],
       [下一段首句在配对列表中的索引, ...]
     )
```

`para_breaks` 在每个后续非空段开始时记录当前句子总数（第 47–49 行），后处理可重新计算该索引（第 248–249 行）。它是分段所用的**句子列表索引**，不是字符、字节、token 偏移，也不是单个事实在句中的跨度。若显式启用 `cost_estimate` 分支，函数返回的是成本估计数值，不是上述配对结构。

原文换行与段首段尾空白已被处理；修复断句和后处理还可能拼接句子、改写事实。事实通过生成模型产生，不能假定是原文的连续子串。spaCy 虽然内部有实体对象，该文件只利用实体文本与标签做后处理，没有把实体位置导出为事实的原文位置。不能仅凭返回句子文本或事后字符串查找，断言获得了无歧义的精确事实位置。

此结论来自当前检出版本的返回语句、调用链和数据结构阅读，不是实际样本运行验证；没有逐一审查其他远程分支或历史版本。外部发布数据包未下载，因此**无法确认这些外部数据文件是否还含其他位置字段**；现有读取逻辑和拆分器返回接口没有提供这样的保证。

## 仓库外资源与运行条件（本次均未获取或触发）

完整克隆的是作者发布的 **Git 仓库及其受跟踪文件与历史**，并不意味着实验所需外部资源已齐备。

- `factscore/download_data.py:137–139` 另行下载 `demos.zip`、`data.zip`、`enwiki-20230401.db`；这些资源不在当前 HEAD 树内。README 给出 [Google Drive 资源目录](https://drive.google.com/drive/folders/1kFey69z8hGXScln01mVxrOhrqgM62X7I?usp=sharing)。本次未下载或核验外部包内容、访问状态、许可证和校验和。
- 拆分器在 `factscore/atomic_facts.py:24–30` 读取 `demos/demons.json`（默认人物传记设置）；该演示文件不在当前 Git 树内。
- spaCy 的 `en_core_web_sm` 由 `factscore/atomic_facts.py:22` 加载；README 第 35 行要求另行下载。`factscore/atomic_facts.py:17` 在模块导入时调用 `nltk.download("punkt")`。本次**没有导入该模块**，没有触发这些资源下载。
- 原子拆分默认使用 `OpenAIModel("InstructGPT")`（`factscore/atomic_facts.py:26`）；代码通过旧版 `openai.Completion.create` 调用默认 `text-davinci-003`（`factscore/openai_lm.py:75–87`）。这不是只靠规则即可完成的事实拆分；本次没有调用模型、读取密钥或验证 API 可用性。
- 完整评分还涉及检索模型；默认 GTR 路径加载 `sentence-transformers/gtr-t5-large`（`factscore/retrieval.py:112–131`）；建库路径引用 `roberta-large`（第 47–48 行）。可选 Inst-LLAMA 恢复路径依赖原始 LLaMA 7B 权重及 `kalpeshk2011/instruct-llama-7b-wdiff`（`factscore/download_data.py:68–99`）。这些权重及其许可均未获取或验证。
- 实际安装兼容性、模型服务可用性、拆分质量、输出样本、评分和论文结果都未验证；没有据静态检查声称实验可运行。

## 原有内容保留与操作边界

- 项目中新增加的内容仅为 `external/FActScore/` 和本说明；没有向 FActScore 内添加说明、补丁或适配文件，没有拆分或组合模块。
- 下载前记录项目内 3911 个已有文件或文件符号链接的元数据（不含各仓库 `.git` 内部文件）；写说明前复核，未发现缺失或类型/权限、大小、修改时间、链接目标变化。完成时再次核对。此为元数据核对，不是对已有数据集和结果逐字节重新计算哈希。
- ERASE 的原 HEAD 为 `b93f898780b3cf40fedd4e9a00c51af9a27688bc`；FactTrack 的原 HEAD 为 `8b09d7fa5a805aa45a0d87a376d255665bd69460`；两者检查前后工作区均干净、HEAD 未变。
- 保留已有 ERASE、FactTrack、Mem0（`mem0_v0.1.118/`）、HaluMem、数据集、诊断文件及实验结果；没有编辑当前 `diagnosis/medium_dev/manifest.json`。
- 没有运行 pip/Conda/venv 安装或环境变更，没有导入/执行 FActScore 模块、测试、预处理、下载数据脚本或实验，没有调用推理 API、加载权重或生成模型输出。
- 核验仅使用 Git 状态和对象完整性检查、文件字节哈希、文本阅读/搜索、Python 标准库 AST 静态解析及已有文件元数据比对；本次不包含任何实验结论。
