# 本地英文 NLI 小样本验证

时间：2026-11-06T10:38:28.427765+08:00 至 2026-11-06T10:38:34.097747+08:00

## 文件和配置

- 模型目录：`/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_relation_judge/model/DeBERTa-v3-base-mnli-fever-anli`
- 已对照前次官方仓库核验记录，10 个文件的大小及 SHA-256 均一致。revision：`6f5cf0a2b59cabb106aca4c287eed12e357e90eb`。
- 在加载前读取本地 `config.json`：`0 = entailment`、`1 = neutral`、`2 = contradiction`。
- 完全离线：设置 `HF_HUB_OFFLINE=1`、`TRANSFORMERS_OFFLINE=1`，并对分词器和模型使用 `local_files_only=True`。

## 运行指标

- 状态：completed；模型前向尝试 8 次，完成 8 次；每对事实单独一次，无预热前向。
- 环境：`/home/shu1004/anaconda3/envs/emem_vllm/bin/python`，Python 3.11.18，PyTorch 2.9.1+cu128，Transformers 4.57.3；设备 `cuda:0`，NVIDIA GeForce RTX 3090 Ti，模型计算精度 float32。
- 总耗时 5.6698 秒（含依赖导入、加载和全部样例）；分词器及模型加载和传输到 GPU 耗时 1.0818 秒。每例 forward_seconds 含计时期间写入进度 JSON 的开销，且首例含首次 GPU 执行开销，不应视为稳定纯模型延迟。
- 本进程 PyTorch 峰值 allocated 722.72 MiB，峰值 reserved 760.00 MiB；加载完成后 allocated 704.73 MiB。allocated 为张量占用，reserved 为 PyTorch 缓存分配器保留量，二者不能相加。
- 全卡加载前空闲 21127.25 MiB，结束时空闲 20313.25 MiB；全卡空闲量受其他进程影响，不等于本进程占用。
- 分词器提示未设置默认截断上限而无法截断；这些样例事后逐对统计为 14–19 tokens，低于配置的 512 位置上限。本次推理正常完成。运行环境还输出 `PYTORCH_CUDA_ALLOC_CONF` 弃用提示。

## 逐例结果

每组依次给出 premise（前提）和 hypothesis（假设）；softmax 分数顺序为 entailment / neutral / contradiction。原始 logits 与全部完整精度结果见 `results.json`。softmax 是模型输出分数，并非经过校准的正确率。

### support_1：明确支持

- 前提：Alice owns a red bicycle.
- 假设：Alice owns a bicycle.
- 预期：`entailment`。理由：拥有红色自行车蕴含拥有自行车。
- 模型：`entailment`（ID 0）；softmax `0.997845 / 0.001790 / 0.000365`；符合预期。
- 单次前向计时：0.5720 秒；输入 14 tokens。

### support_2：明确支持

- 前提：The package was delivered on Monday.
- 假设：The package has been delivered.
- 预期：`entailment`。理由：周一送达蕴含已经送达。
- 模型：`entailment`（ID 0）；softmax `0.996146 / 0.003362 / 0.000492`；符合预期。
- 单次前向计时：0.1702 秒；输入 16 tokens。

### contradiction_1：明确矛盾

- 前提：The light is on.
- 假设：The light is not on.
- 预期：`contradiction`。理由：同一状态的肯定和否定不能同时成立。
- 模型：`contradiction`（ID 2）；softmax `0.000896 / 0.000921 / 0.998183`；符合预期。
- 单次前向计时：0.0165 秒；输入 14 tokens。

### contradiction_2：明确矛盾

- 前提：No dogs are allowed inside the museum.
- 假设：Dogs are allowed inside the museum.
- 预期：`contradiction`。理由：明确禁止与允许的表述相矛盾。
- 模型：`contradiction`（ID 2）；softmax `0.002086 / 0.001067 / 0.996847`；符合预期。
- 单次前向计时：0.1088 秒；输入 18 tokens。

### unrelated_1：无明显关系

- 前提：The chef is cooking dinner.
- 假设：The train arrives at noon.
- 预期：`neutral`。理由：烹饪晚餐不能确定火车何时到站。
- 模型：`contradiction`（ID 2）；softmax `0.005583 / 0.105804 / 0.888614`；不符合预期，需人工判断。
- 单次前向计时：0.2717 秒；输入 15 tokens。

### unrelated_2：无明显关系

- 前提：Sarah bought a blue notebook.
- 假设：The weather will be rainy tomorrow.
- 预期：`neutral`。理由：购买笔记本与明日天气没有给出可推导的关系。
- 模型：`neutral`（ID 1）；softmax `0.002662 / 0.996757 / 0.000581`；符合预期。
- 单次前向计时：0.0156 秒；输入 16 tokens。

### temporal_1：过去和现在状态变化

- 前提：In 2020, Maya lived in Boston.
- 假设：In 2024, Maya lived in Seattle.
- 预期：`neutral`。理由：2020 年居住地不能确定 2024 年居住地，两条可在不同时间同时为真；需要时间信息才能判断记忆状态。
- 模型：`contradiction`（ID 2）；softmax `0.000632 / 0.456027 / 0.543342`；不符合预期，需人工判断。
- 单次前向计时：0.0159 秒；输入 19 tokens。

### temporal_2：过去和现在状态变化

- 前提：In 2020, Daniel was single.
- 假设：Daniel is married now.
- 预期：`neutral`。理由：过去单身与现在结婚可以先后成立，过去的状态不确定当前状态；不能据 NLI 判定旧记忆失效。
- 模型：`neutral`（ID 1）；softmax `0.002557 / 0.973375 / 0.024068`；符合预期；仍需人工判断时间和记忆状态。
- 单次前向计时：0.0172 秒；输入 15 tokens。

## 解读与范围

- 8 例中 6 例与人工预期标签一致。`unrelated_1` 的前提不能支持或排除火车到站时间，但模型输出 contradiction（0.8886）；不可把高分当成正确性保证。
- `temporal_1` 的不同年份居住地可先后为真，但模型输出 contradiction（0.5433，对 neutral 的 0.4560）。`temporal_2` 输出 neutral，与人工预期一致；两例都需要根据时间和业务语境判断。
- NLI 的 contradiction 是文本关系信号，不直接等于旧记忆失效；过去和现在可以是不同时间的状态，不能根据 NLI 结果直接删除或更新记忆。
- 本模型为英文 NLI 模型，这 8 个英文样例只是冒烟测试，不能代表真实业务准确率，也没有验证中文。使用中文数据前应单独评估多语言 NLI 模型及其在目标中文数据、时间表达与业务场景中的表现；本次未下载新模型。
- 无微调、云端 API 调用、依赖安装或完整开发子集运行。
