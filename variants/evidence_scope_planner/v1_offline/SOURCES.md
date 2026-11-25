# 材料核对与限制

这是离线材料检查；没有调用模型。`fixtures/*.json` 是依据已保存原文与来源上下文新整理的人工对齐输入，`*.expected.json` 是单独保存、未输入规划器的人工期望；二者都不是用户确认的金标准。五案材料的集中入口是 `variants/evidence_aligner/runs/prepared_20261120/{case}.json` 的 `input`。完整文件路径相对于项目根目录。引文通过在来源对话中的逐字唯一命中检查，不能因此证明语义关系正确。五案 `before.json` 中 `api_snapshot.results` 与 `database_points_with_vectors` 的对应条目，ID、用户与旧记忆文本一致；下列会话目录的 `input.json#/raw_dialogue/N/content` 是新话语。说话者均为用户，记录时间是发言记录时间，不等于事实生效时间。

| 案例 | memory_id | user_id | 旧记忆快照及新证据会话 | 选中的新用户对话 | 旧来源上下文 |
|---|---|---|---|---|---|
| skydiving | e1d4f8f9-0520-427d-94fd-a2ac0ee69d03 | 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f | session_009 | 0、2、8；2026-04-10 | session_003 对话 6，明确用户不喜欢极限运动及安全原因 |
| promotion | e13b825e-7ec7-4760-821e-0581d8da5650 | 1b846c59-456e-9550-dffd-4d23f1eca81f | session_005 | 0；2026-02-01 | session_002 对话 2，用户说自己是 Historical Productions Ltd. Director |
| transition | e6ab178b-c0f9-4adb-bfb7-e4648617a950 | 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f | session_008 | 0；2026-03-01 | session_007 对话 0，用户寻找更好的工作生活平衡和人道目标 |
| susan | a1332815-d6ba-4bdc-9ffa-657f7315d0ed | 2f1f897e-d67f-dbc5-6a7b-b7634a9e294f | session_007 | 0、2；2026-02-05 | session_002 对话 6，同一段有 ThomasSusan 是朋友和 Susan 的支持，但名字指代仍有歧义 |
| career_history | 05afde13-35bd-4d26-bbae-6de427d58db1 | 348492a7-cfe4-ee1d-73c3-c276d6ba8277 | session_008 | 0、2；2026-01-05 | session_002 对话 2，用户自述在 Blockchain Tech 任 senior developer |

所有 session 均在 `results/medium_dev/williams_native_prefix5_20261028_v3/users/{user_id}/` 下，旧快照为对应目录 `before.json`。`prepared_20261120` 保存了 `ctx-1` 的精确 source_ref 和片段、所有入选新话语及整场对话。已逐个打开这些 `input.json` 核对上表选中话语和 `ctx-1` 的来源指针、逐字唯一命中；其余消息只是上下文，并非经过拆分的完整新证据。身份“user”根据同一用户目录的历史和新用户对话确定，旧记忆本身一般省略语法主体，不应根据用户 ID 猜姓名。

`simplemem_mem0_splitter/run_native_mem0_prompt_v2_20261119/` 和 `offline_entity_recheck_20261119/` 覆盖五条原生记忆，与本五案并非一一相同。只有 skydiving 的旧内容和 ID 均匹配（case_2），本回放沿用其三个单元及原引文；它们相互重叠，u3 仅引用 `conflicting with commitment to safety and well-being`，不能独立支撑拆分器所写的完整因果句。career_history 有相同 ID 的 case_5，但其更早 session_004 旧文本是 `Works at Blockchain Tech as a senior developer`，本案 session_008 是 `Previously worked as a senior developer in Blockchain Tech`，因此不能直接把旧拆分套进本案。其余 promotion、transition、susan 未发现同文同 ID 的现有 SimpleMem 拆分。本回放从 prepared 案例中沿用先前人工映射的拆分单元；这是来源缺口，不应称为拆分器结果。`scope_trial_inputs_20261119/REPORT.md` 中的 career_transition 意向是更早另一情境，不等于本次 career_history 的新证据。

适用条件只在所对应的单一命题没有额外限定时人工标为 unconditional，而不是宣称该人所有时间、所有事项均如此；补充、无关和无法判断的跨命题对应均标 unknown。`same_as_old` 表示相同命题的适用条件沿用旧侧，不填具体日历时间。新用户话语包含“recently”“finally”等相对表述，不足以指定精确生效日。模拟跳伞与真实跳伞的范围关系未确定，不能用新体验推翻旧偏好；晋升不证明原宽泛 Director 表述为假；完成转岗不必然证明以后不再求职；新近咨询公司客户不推翻此前技术职位。模型未提供的身份、逻辑蕴含、日期以及事实变化不得自动补齐。`fixtures/*.expected.json` 进一步列出了各案的未决事项。
