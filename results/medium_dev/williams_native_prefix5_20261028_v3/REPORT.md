# 原生 Mem0 最小试跑结果

2026-10-28；run_id：`williams_native_prefix5_20261028_v3`。

已到指定用户 `1b846c59-456e-9550-dffd-4d23f1eca81f` 的原始 `sessions[4]` 结束并停止。仅该用户，完整原始前缀5会话、150消息，每会话一次原生 infer=True add；消息数依次12、8、32、38、60。没有运行 sessions[5]、其他用户、QA、评分或改进模块。

## 审核及输入边界

24/24审核记录及当前层与版本副本逐字节一致；已验证版本 SHA256SUMS、规范化payload指纹及所有绑定的来源哈希。版本为 `human_review_v1_20261028`，指纹 `adcec5002d99bc4500f86ef00b37991d58b85ccafc786e84c71a6152b45f87e4`。副本在 `human_review_version/`。冻结原始清单和运行器没有改动；TARGETS.md 中旧的“待人工核验”是原始快照状态，当前审核状态按独立人工审核层解释。

环境为 mem0_halumem / Python 3.11，editable mem0ai==0.1.118 加载本项目源码。沿用 .env.local 中已验证配置：qwen-plus，text-embedding-v4 / 1024，temperature=0.5，max_tokens=16384，timeout=180，SDK重试0。密钥未写入产物。原生提示词、top-5检索、更新计划和执行逻辑未修改。

独立 Qdrant、history.db、mem0_runtime；首会话before确认为空库。逐会话 input.json 与原数据的全部 dialogue role/content 相等，observations.jsonl 中实际 add 输入逐项相等。memory_points、original_memories、人工审核答案、保护标签、persona和QA没有拼入模型消息，没有预填知识。审核副本和 target_links 仅用于离线证据关联。

## 晋升目标结论（LLM运行后语义核查，供用户复核）

| 检查 | 观察与结论 |
|---|---|
| 更新前旧具体职称 | 确实存在：`e13b825e-7ec7-4760-821e-0581d8da5650`，`Works at Historical Productions Ltd. as a Director`。这是雇主关联具体职称，不只是泛指导演职业。 |
| 原生召回 | 晋升事实查询中旧记忆排名第一，score=0.7885431127502496，进入更新模型输入；临时ID为5。不能归因为旧知识未入库或召回缺失。 |
| 更新后新具体职称 | ADD：`2570a550-4b52-43fc-b5c4-079261785a1a`，`Recently promoted to lead director at Historical Productions Ltd`。整体知识明确表达最近晋升后为Lead Director。 |
| 旧职称处理 | 旧ID发生UPDATE，但 old_memory==new_memory，文本没有变化；另增晋升事实。不是把旧职称直接替换为新职称。旧记录未明确标成历史、未绑定原对话时间，时间组织仍有不足；不因Director一词继续出现判失败，也不声称已实现显式历史化。 |
| 雇主 | 前后均保留Historical Productions Ltd，新晋升记忆也保留同一雇主。 |
| 保护内容损失 | 目标会话before共72条，after84条；72条旧ID及其文本逐字不变，无删除或文本缩减。新增12条；14次UPDATE均为相同文本重写。没有观察到该会话造成已有保护内容删除或改坏。 |

端到端晋升新状态已保存，整体知识可表达当前Lead Director；不将操作名UPDATE当成功条件。严格“旧当前记录显式历史化”不能判为完成。没有开展下游QA，所以不能据此声称实际回答一定正确或时间冲突完全消除。

## 保护候选核对

以下均按目标会话真实before核对，after文本相同：

| 保护范围 | 实际before记忆ID／说明 |
|---|---|
| 雇主 | e13b825e-7ec7-4760-821e-0581d8da5650 |
| 电影行业身份 | e6112994-45c2-43d2-86d8-7c8d978f690e：Is a filmmaker |
| 历史真实性及协作 | f71eebcd-d556-436f-97be-a8dca4c99de9：Goal is to create historically accurate films；199dfd83-57fc-4c71-ba24-e78ac99fd607：Collaborates with set dressers to create period settings。原先“meticulous”细节没有作为独立事实完整入库，不能归因于本会话损失。 |
| 电影偏好 | 251a7c03-38f9-4be3-bb6b-bf041bee2222（历史剧）、098837c8-4b33-4fda-81ef-bcaae08089ac（年代片）、28ad9a5b-27d9-4ace-b034-8d6efc5709c8（科幻大片顾虑） |
| 此前Director历史 | 旧职称文本仍存在，但before及after均无原对话日期的显式历史限定；保护的是已存内容，不把此前未形成的历史标注算本次损失。 |
| 学历专业 | 1fd623c5-30e6-4b18-8b4e-2969cb10aab2（Bachelor）、7a85fc34-7cea-4f18-9a00-c03c7ec689c4（Film Studies），分条存储 |
| 父亲职业 | 0682fdb0-5fc9-40a0-9913-6396cab3b675：retired history professor |

其他饮品、宠物、音乐及Mary/Steven关系支持等已有文本也全部保留。上述保留结论只针对第5会话前后，不证明早期提取完整或整个前缀从未损伤信息。旧收入75000和储蓄207000原文保留；未把助手提出的90000/250000写入。保留旧数值不等于认证它们仍为当前事实。

## 运行异常与记录策略

1. v1首次抽取请求被沙箱阻断：Operation not permitted；0已提交会话，0实际写入。目录 `../williams_native_prefix5_20261028_v1/`完整保留。
2. v2沙箱外启动遇失效代理：Connection refused；0已提交会话，0实际写入。目录 `../williams_native_prefix5_20261028_v2/`完整保留。无密钥直连端点检查HTTP401证实端点可达；v3仅对dashscope.aliyuncs.com设置NO_PROXY，不改变模型地址或模型配置。
3. v3第2会话更新模型生成旧映射外的临时ID19执行UPDATE；旧映射仅0–14。Mem0原生捕获KeyError '19'，跳过该操作，继续14次ADD并正常返回。严格运行器保存完整after/history后拒绝提交。日志见 session_002/runtime.jsonl、full_operation_plan.json、update_model_io.json、error.json。
4. 为完成用户指定的观测范围，外层 `code/continue_observed.py` 对该已正常返回的native add核验API成功、history重放、快照与持久化后，提交“带原生异常”的观测检查点，保持实际库状态继续。没有重跑、回滚、修复该UPDATE，也没有修改原生实现。原运行器拒绝记录原封保留于error.json，额外记录observed_anomaly.json。该政策属于外层异常观测处理的明确变化，不声称严格运行器全流程通过。第3、4、5会话均通过原严格检查。

Mem0自身created_at/updated_at保留宿主原生时区（-07:00），外层日志为Asia/Shanghai；它们是执行时间，不是原对话事件日期。没有将确认时间伪装成准确晋升日期。

## 产物与检查点

- `verification_summary.json`：5会话消息计数、快照计数、实际操作数、API调用数、异常与输入校验。
- `target_before_after.md` / `.json`：目标会话全部72条before、84条after及文本差异；实际操作在JSON中。
- `users/<UUID>/session_001` 至 `session_005`：完整快照（含向量）、召回候选、更新模型输入输出、全计划、实际操作、API审计、history、持久化结果和会话前回滚副本。
- `users/<UUID>/checkpoint.json`：completed_ordinal=5，5会话产物哈希已核验；当前持久库与最后after及history一致；无未提交会话。后续起点为原始sessions[5]（第6会话）。
- `console.log`保留原严格运行器拒绝；`continuation.log`记录异常观测提交与指定边界停止。`status.json`明确completed_with_native_anomalies。

本轮到此停止。下面仅保存未来续跑命令，不执行；它会继续该用户剩余完整前缀直至sessions[10]，需要后续用户指令：

```bash
cd /home/shu1004/ld/system/mem0_halumem_diagnosis
NO_PROXY=dashscope.aliyuncs.com no_proxy=dashscope.aliyuncs.com conda run --no-capture-output -n mem0_halumem python scripts/medium_dev_run.py --execute --resume --run-id williams_native_prefix5_20261028_v3 --user 1b846c59-456e-9550-dffd-4d23f1eca81f --env-file .env.local
```

此命令复用原run_record与检查点，跳过已提交5会话；第2会话带异常标记必须随结果解释保留，不能把整个run改称无异常成功。若未来另有原生异常，原严格运行器仍会停止，需要依据新日志再判断。
