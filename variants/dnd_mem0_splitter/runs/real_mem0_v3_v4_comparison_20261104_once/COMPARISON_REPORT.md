# v3 / v4 真实旧记忆配对测试

**初步判断，待人工确认。全部语义复核由 AI 完成，未经过人工最终确认。**

使用相同输入对现有7条案例和新增4条复合记忆各测试 v3/v4 一次。旧7条是提示词调整所依据的回归样本，新增4条是不同旧记忆探针；不能将回归改善当独立泛化结果。

v4 只调整 raw 来源边界、单条 supports 的支持范围及正文与待确认一致性；未修改解析器/校验器/输出结构。v3 默认 DESIGN.md 保留，v4 见 [新版本](../../prompt_versions/v4_boundaries_20261104/CHANGELOG.md)。

运行：qwen-plus；两版本各11次，共22次真实请求；每版本/案例1次；SDK重试0，HTTP自动跳转false；response_format=json_object，timeout=180秒；显式 generation_parameters={}。温度、token上限、seed、具体模型修订和服务端路由未能确认。版本按案例交错并轮换先后，实际顺序见 [调用记录](batch_attempt.json) 和 [完成记录](batch_completion.json)。同输入、同显式参数不能保证服务端确定性，单轮差异仅为观察。

程序检查：

| 版本 | 案例通过 | 接受事实 | 逐字引文 | memory 引文事实 |
| --- | --- | --- | --- | --- |
| v3 | 11/11 | 17 | 31/31 | 17 |
| v4 | 11/11 | 16 | 31/31 | 16 |

上述仅检查格式、ID、来源编号及引文逐字匹配。supports 语义、覆盖和身份归属由下述初审检查，不能由程序通过推出正确。失败候选应保留 raw_content、失败状态和诊断，禁止自动补引文、改标或写成通过结果。

逐案例结果（类型计数有重叠）：

| 案例/明细 | 队列 | v3事实/问题 | v4事实/问题 |
| --- | --- | --- | --- |
| [case_01_multi_person](reviews/case_01_multi_person.md) | regression_7 | 1 / ASSERTION_PENDING_CONFLICT、RAW_CONTEXT_LEAK、RELATION_SCOPE_CHANGE | 1 / 未观察到明确项 |
| [case_02_subject_and_roster](reviews/case_02_subject_and_roster.md) | regression_7 | 1 / RAW_CONTEXT_LEAK、RELATION_SCOPE_CHANGE、SUPPORTED_UNNECESSARY_ADDITION | 1 / 未观察到明确项 |
| [case_03_assistant_yoga](reviews/case_03_assistant_yoga.md) | regression_7 | 1 / RAW_CONTEXT_LEAK | 1 / 未观察到明确项 |
| [case_04_negative_relative](reviews/case_04_negative_relative.md) | regression_7 | 1 / 未观察到明确项 | 1 / 未观察到明确项 |
| [case_05_relative_time](reviews/case_05_relative_time.md) | regression_7 | 1 / 未观察到明确项 | 1 / 未观察到明确项 |
| [case_06_plan_possibility](reviews/case_06_plan_possibility.md) | regression_7 | 1 / SUPPORTS_OVERREACH | 1 / 未观察到明确项 |
| [case_07_no_children](reviews/case_07_no_children.md) | regression_7 | 1 / RAW_CONTEXT_LEAK | 1 / 未观察到明确项 |
| [case_08_partner_profile](reviews/case_08_partner_profile.md) | new_compound_4 | 2 / 未观察到明确项 | 2 / 未观察到明确项 |
| [case_09_father_profile](reviews/case_09_father_profile.md) | new_compound_4 | 3 / 未观察到明确项 | 3 / 未观察到明确项 |
| [case_10_sports_preferences](reviews/case_10_sports_preferences.md) | new_compound_4 | 2 / 未观察到明确项 | 1 / SUPPORTS_OVERREACH |
| [case_11_persian_care](reviews/case_11_persian_care.md) | new_compound_4 | 3 / RELATION_SCOPE_CHANGE | 3 / RELATION_SCOPE_CHANGE、SUPPORTS_OVERREACH |

语义问题类型按案例统计（非人工错误率；同一案例可多类型）：

| 类型 | v3 | v4 |
| --- | --- | --- |
| ASSERTION_PENDING_CONFLICT | 1 | 0 |
| RAW_CONTEXT_LEAK | 4 | 0 |
| RELATION_SCOPE_CHANGE | 3 | 1 |
| SUPPORTED_UNNECESSARY_ADDITION | 1 | 0 |
| SUPPORTS_OVERREACH | 1 | 2 |

按队列区分：

| 队列 | 版本 | 观察到问题案例 | 有具体未决案例 | 事实数 |
| --- | --- | --- | --- | --- |
| regression_7 | v3 | 5 | 6 | 7 |
| regression_7 | v4 | 0 | 6 | 7 |
| new_compound_4 | v3 | 1 | 4 | 10 |
| new_compound_4 | v4 | 2 | 4 | 9 |

全部22份输出及每条事实均待人工确认；有具体未决项的案例另列，不等于错误。partial supports 不自动记错；单条事实合并多个已覆盖信息点也不自动记遗漏。复合覆盖的逐信息点判断见 [coverage_review.csv](coverage_review.csv)。

[输入、上下文与来源](CASE_CATALOG.md) · [selection.json](selection.json) · [历史来源核验](source_provenance.json) · [程序细项](program_summary.json) · [逐事实表](fact_review.csv) · [逐引文支持表](supports_review.csv) · [语义汇总](semantic_summary.json) · [综合判断与下一步建议](ASSESSMENT.md)

本轮未调用 Mem0、不写知识库、不执行新旧事实关系判断或完整开发子集；未把新证据、标注或初审结果写入模型输入，未改写任何模型响应。保留 v1/v2/v3 和全部历史文件，最终完整性核验见 final_verification.json。
