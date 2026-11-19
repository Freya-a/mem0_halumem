# 影响范围判断：三条真实案例与一条补充案例

本目录是**人工整理的候选输入（由助手按接口映射，未经人工确认）**，不是人工金标准。没有调用模型、关系判断器或影响范围判断器，也没有执行更新。`*_request.json` 仅做字段映射和索引编号，原文、拆分器陈述与引用未改写；`*_provenance.json` 保留拆分器原始响应、解析结果及修复前后校验。`source_context: []` 表示拆分器原输入为 null；新增证据只在后续候选请求中提供。

三个请求仅经现有判断器的无模型 `validate_request` 做结构和逐字来源检查，不证明语义正确。范围判断阶段还依赖关系判断结果；此处没有伪造该结果。旧记忆隐含主体且本次没有提供旧来源上下文，现有阶段判断的身份依据门槛可能导致待确认。新证据的记录时间不是事实有效时间。所有建议仅供你审核，未放入请求文件。

## 极限运动与模拟跳伞

旧记忆：Dislikes extreme sports (e.g., skydiving) due to high injury risk, conflicting with commitment to safety and well-being

原生 memory ID：`e1d4f8f9-0520-427d-94fd-a2ac0ee69d03`；来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/before.json`；目标：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f:s008:m000`。

原试验程序状态：**passed**；离线复查：**passed**。

原始知识单元（raw_statement 与 contextualized_statement 分别照录）：

- **u1** raw：Dislikes extreme sports (e.g., skydiving)
  - contextualized：Dislikes extreme sports (e.g., skydiving)
  - memory_quotes：["Dislikes extreme sports (e.g., skydiving)"]；context_quotes：[]
  - condition：null；valid_time：null；entities：[]
- **u2** raw：Dislikes extreme sports due to high injury risk
  - contextualized：Dislikes extreme sports due to high injury risk
  - memory_quotes：["Dislikes extreme sports (e.g., skydiving) due to high injury risk"]；context_quotes：[]
  - condition：null；valid_time：null；entities：[]
- **u3** raw：Dislikes extreme sports because it conflicts with commitment to safety and well-being
  - contextualized：Dislikes extreme sports because it conflicts with commitment to safety and well-being
  - memory_quotes：["conflicting with commitment to safety and well-being"]；context_quotes：[]
  - condition：null；valid_time：null；entities：[]

模型 unresolved：[]

离线错误：[]；警告：[]

**新证据：**

- `dataset-s8-dialogue-0`：Hey, I recently had an interesting experience at a team-building event where I tried simulated skydiving. It was quite thrilling!
  - 来源：`dataset line 1, /sessions/8/dialogue/0/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json`；说话者 `user`，记录时间 `Apr 10, 2026, 10:40:32`。
- `dataset-s8-dialogue-2`：Yeah, the adrenaline rush was something I didn't expect to enjoy so much. It's definitely made me more open to trying new things.
  - 来源：`dataset line 1, /sessions/8/dialogue/2/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json`；说话者 `user`，记录时间 `Apr 10, 2026, 10:48:20`。
- `dataset-s8-dialogue-8`：For now, I'm just enjoying the thrill and seeing where it takes me. I still prioritize safety, of course.
  - 来源：`dataset line 1, /sessions/8/dialogue/8/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/2f1f897e-d67f-dbc5-6a7b-b7634a9e294f/session_009/input.json`；说话者 `user`，记录时间 `Apr 10, 2026, 10:57:54`。

**助手建议的修改候选：**建议仅把 u1 涉及跳伞的范围列为待判断候选：新体验是模拟跳伞，可能需要补充情境而非替换旧偏好；不得断言所有极限运动偏好发生改变。

**助手建议的保留候选：**建议保留 u2 中受伤风险以及 u3 的安全、福祉取向；旧的真实跳伞及其他极限运动顾虑至少作为历史记录保留。

**待确认：**模拟跳伞是否落在旧记忆所称极限运动之内、旧偏好当前是否仍成立、u3 单独引文能否支撑完整关系，均待确认；新证据不证明否定或取消旧事实。

## 工作压力下降

旧记忆：Experiences stress due to historical accuracy demands and tight production schedules

原生 memory ID：`4ffee399-c31f-4827-b5fc-5c661baf1fc9`；来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/before.json`；目标：`1b846c59-456e-9550-dffd-4d23f1eca81f:s005:m000`。

原试验程序状态：**needs_review**；离线复查：**needs_review**。

原始知识单元（raw_statement 与 contextualized_statement 分别照录）：

- **u1** raw：Experiences stress due to historical accuracy demands and tight production schedules
  - contextualized：Experiences stress due to historical accuracy demands and tight production schedules
  - memory_quotes：["Experiences stress due to historical accuracy demands and tight production schedules"]；context_quotes：[]
  - condition：null；valid_time：null；entities：[]

模型 unresolved：["Subject of 'Experiences stress' is unspecified (e.g., who or what experiences stress)", "No explicit identification of the agent or entity subject to historical accuracy demands and tight production schedules", "No temporal specification (e.g., when this stress occurs or occurred)", "No clarification whether 'historical accuracy demands' and 'tight production schedules' are concurrent, independent, or jointly causal"]

离线错误：[]；警告：["unresolved issues reported by model"]

**新证据：**

- `dataset-s5-dialogue-0`：Since my promotion to lead director at Historical Productions Ltd., I've noticed a significant improvement in my mental health. The ability to delegate tasks has reduced my stress levels and allowed me to focus more on my projects.
  - 来源：`dataset line 14, /sessions/5/dialogue/0/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/input.json`；说话者 `user`，记录时间 `Mar 15, 2026, 13:53:58`。
- `dataset-s5-dialogue-14`：Delegating tasks has been key to reducing stress and improving my mental health. It's been a significant change since becoming lead director.
  - 来源：`dataset line 14, /sessions/5/dialogue/14/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_006/input.json`；说话者 `user`，记录时间 `Mar 15, 2026, 14:31:44`。

**助手建议的修改候选：**建议把 u1 中“压力状态”的当前表述作为变化候选，并补充其相对于之前下降，保持新证据的程度和限定。

**助手建议的保留候选：**建议保留历史上的压力以及历史准确性要求、紧张制作日程这两个既有原因，作为历史事实或待确认的现状，而不是直接删除。

**待确认：**新证据未说明两种旧压力来源是否已消失或仍造成压力，不能推断压力归零、完全康复或任何一个原因已消失；复合单元需要内部划分。

## Blockchain Tech 与职业转型意向

旧记忆：Works at Blockchain Tech as a senior developer

原生 memory ID：`05afde13-35bd-4d26-bbae-6de427d58db1`；来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/before.json`；目标：`348492a7-cfe4-ee1d-73c3-c276d6ba8277:s003:m003`。

原试验程序状态：**failed**；离线复查：**needs_review**。

原始知识单元（raw_statement 与 contextualized_statement 分别照录）：

- **u1** raw：Works at Blockchain Tech as a senior developer
  - contextualized：Works at Blockchain Tech as a senior developer
  - memory_quotes：["Works at Blockchain Tech as a senior developer"]；context_quotes：[]
  - condition：null；valid_time：null；entities：[{"type": "organization", "name": "Blockchain Tech", "disambiguation_support": "explicit name in memory"}, {"type": "job_title", "name": "senior developer", "disambiguation_support": "explicit title in memory"}]

模型 unresolved：["The subject (who 'works') is not explicitly named — pronoun or referent is missing; identity of the person is unresolved.", "No temporal scope (e.g., current, past, future) is specified — tense is ambiguous (present habitual vs. present continuous vs. generic fact)."]

离线错误：[]；警告：["unresolved issues reported by model", "units[0].entities[0] normalized from object; review retained original metadata", "units[0].entities[1] normalized from object; review retained original metadata"]

**新证据：**

- `dataset-s3-dialogue-0`：I've been thinking a lot about my career transition from technology to political consulting. It's a big change, but it feels like the right move to better support my relative's political ambitions.
  - 来源：`dataset line 17, /sessions/3/dialogue/0/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/input.json`；说话者 `user`，记录时间 `Nov 10, 2025, 18:05:35`。
- `dataset-s3-dialogue-2`：The idea of directly advising political campaigns really excites me. I want to be more involved in shaping strategies that will help my relative win elections and establish a legislative legacy.
  - 来源：`dataset line 17, /sessions/3/dialogue/2/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/input.json`；说话者 `user`，记录时间 `Nov 10, 2025, 18:10:01`。
- `dataset-s3-dialogue-12`：My problem-solving skills and experience in technology will help me analyze data effectively and develop impactful strategies.
  - 来源：`dataset line 17, /sessions/3/dialogue/12/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/348492a7-cfe4-ee1d-73c3-c276d6ba8277/session_004/input.json`；说话者 `user`，记录时间 `Nov 10, 2025, 18:26:34`。

**助手建议的修改候选：**建议将 u1 的当前雇主和职位是否需要时态限定列为待确认范围，并添加“考虑从技术转向政治咨询、想要直接为政治竞选提供建议”的意向。

**助手建议的保留候选：**建议保留 Blockchain Tech 与 senior developer 的原有关系作为历史记录；技术经验仍有新证据支撑。

**待确认：**新证据没有确定离职、已完成转型或获得正式政治顾问头衔；现时雇主和职位是否变化不能确定。旧输出实体对象经离线名称转换后仍为待复核；对象原文已保留。

## 补充的真实局部变化候选（尚未拆分）

原生旧记忆：Works at Historical Productions Ltd. as a Director

memory ID：`e13b825e-7ec7-4760-821e-0581d8da5650`；来源：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/before.json`；目标：`1b846c59-456e-9550-dffd-4d23f1eca81f:s004:m000`。

新证据：I recently got promoted to lead director at Historical Productions Ltd. It's quite exciting!

来源：`dataset line 14, /sessions/4/dialogue/0/content`；原生运行会话输入：`results/medium_dev/williams_native_prefix5_20261028_v3/users/1b846c59-456e-9550-dffd-4d23f1eca81f/session_005/input.json`；说话者 `user`，记录时间 `Feb 01, 2026, 18:47:19`。

助手建议：更新候选是当前职位的具体层级 Director → lead director；保留候选是 Historical Productions Ltd. 雇主关系和原 Director 职位的历史记录。新职位是 Director 的更具体类型，“Director”这个宽泛描述也可能仍然为真，不能仅凭晋升断言旧句每部分都错误。该例尚无本轮拆分输出，未构造成判断器请求或标为金标准。
