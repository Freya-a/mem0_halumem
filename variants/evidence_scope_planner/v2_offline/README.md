# 离线影响范围规划器 v2

本目录独立于 `../v1_offline`。它不调用模型/API、不读写 Mem0，也不修改已保存的对齐器产物。Python 标准库即可运行：

```bash
python -m unittest discover -s tests -v
python replay.py
python make_report.py
```

`replay.py` 在内存中分别加载旧版和新版代码，对五案三版已保存模型结果及两版人工输入回放，输出本目录 `results/`。人工输入在 `fixtures/`；模型输出不借用人工输入或预期。`SEMANTIC_CRITERIA.md` 与 `SEMANTIC_REVIEW.json` 保存独立人工语义核查及口径；最终报告分开列接口/引文接收、计划结果和人工审核。来源背景及历史限制见 `../v1_offline/SOURCES.md`。

`adapter.load_aligner_case(path)` 返回 `build_scope_plan(old_memory, old_units, evidence_sources, alignments)` 的四个参数。模型关系 `new_information` 是独立新增候选，和 `unrelated`（旧事实无关）或 `unknown` 不同。适配记录保留原始模型字段、双侧引文列表、各自 source_id、单元绑定、限定词、未知项和校验错误。多引用不得推断交叉配对；没有足够信息时标待确认。

调用方为有证据的事实提供 `semantic_support='supported'` 与 `semantic_basis=[{'side':'new','source_id':...,'quote':...}]`；它是上游关于特定动作的语义审核，不是引用逐字匹配结果，也不能仅从模型 relation 推导。独立新增还需主体、属性、值、模态和有效新证据；计划使用 `modality='planned'`。当前模型输出没有独立语义审核字段，适配器不会补造，因而模型组可保守地只产生待确认。对仅与旧事实无关的断言，保留旧事实还要明确 `no_impact_confirmed` 及可核验依据。

涉及不同值的状态变化通过 `temporal_order={'relation':'before|after|same|unknown','basis':[...], 'explanation':'...'}` 表达新状态相对旧状态的先后及其证据；上述 relation 是四个字符串之一。依据必须绑定已关联的新引文，不能只依赖记录时间；调用方负责判断引用是否确实支持所标注先后。没有具体日期本身不妨碍有依据的先后判断，未知/同一时间的冲突不应覆盖旧事实，早于旧事实的新证据不能覆盖旧状态。`unknown` 或空条件不是无条件；有限离散多维条件按组合求交、差。引文位置是 Unicode 字符零基、左闭右开。

本实验的新证据来源必须显式携带 `speaker='user'` 和 `side='new'`；缺失或不符时不授权动作。接口不理解自然语言，不保证上游语义标签正确；source_ref 的实际文件真实性由调用方核验。模型 `new_claim`、object、限定词和日期原文保留供后续审阅，不能自动改写为主体、值或有效日期。未知相对顺序、模拟/真实覆盖范围、条件或来源均保持不确定，不能为了获得编辑范围而补齐。精确日期区间和开放域范围运算不在本版支持范围。
