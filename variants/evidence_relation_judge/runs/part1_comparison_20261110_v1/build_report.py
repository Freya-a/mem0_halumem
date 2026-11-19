"""Render the saved requests, human-reviewed boundaries and candidate outputs."""
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'dev_scope_review_20261109_v1'
inputs=json.loads((HERE/'inputs.json').read_text(encoding='utf8'))
reviews=json.loads((SOURCE/'human_review_inventory.json').read_text(encoding='utf8'))['rows']
by_num={x['number']:x for x in reviews}
names=[('job_transition',7,'转岗'),('persian_cats',14,'波斯猫'),('skydiving',8,'跳伞'),('career_history',24,'职业历史'),('promotion',10,'晋升')]
complete=json.loads((HERE/'completion.json').read_text(encoding='utf8'))
strict=json.loads((HERE/'v5/completion.json').read_text(encoding='utf8'))
analyses={
'job_transition':'v2 将已转岗当作对仍在找工作的支持；v4/v5 虽识别阶段差异，却标 historical_correction 并称旧陈述需要更正。人工记录认为旧求职历史真实，仅当前阶段推进；按本次规则可能是 possible_change，但标签仍待人工确认。v4/v5 还询问材料已明确的内容。',
'persian_cats':'v2 和 v5 标 support，理由涉及更钦佩，但没有清楚分开旧喜好受到支持与观看纪录片、欣赏加深的新增；v4 标 supplement 并说欣赏进一步加深，但未明确同时支持旧喜好，且有重复或不必要问题。三者均未按所提混合策略完整表达；标签待人工确认。对品种历史不作外部事实验证。',
'skydiving':'三版均标 possible_change，理由均由模拟体验推到对广义极限运动态度可能变化；这超出可确认的模拟体验边界，真实跳伞当前态度未知。三版虽提到安全优先，却重复询问该已明确内容；旧片段均为整句。标签待确认。',
'career_history':'三版理由都将“我的咨询公司”推成当前受雇，v4 还称咨询师，提问也带入该前提，故未解决身份推断。v5 还指出旧上下文与 previously 的时态待核，但不能据此认定现实冲突。此输入无其他朋友对话；标签待确认。',
'promotion':'三版均标 possible_change，attribute 为 position，理由集中于 Director 至 lead director，v2/v4 明说同一公司；但三版候选旧片段均为包括雇主的整句，未局部分开职称。准确晋升日期未知，标签待确认。'}

def js(x):return json.dumps(x,ensure_ascii=False)
out=['# 组件一：五个定向案例的受控对照','',
'## 结论与范围','',
'本次比较 v2 与严格版 v5；v4 是在复查标签含义前完成的探索版本，保留全部原始结果。五例为定向开发案例；v5 在看过 v4 部分结果后制定，非盲测，不能计算或声称总体准确率。人工审核确认的是事实及允许更新边界，**不是本次六标签的独立盲标**；下述标签优劣是研究者暂定分析，需人工确认。','',
'范围只涉及组件一；未修改拆分器、组件二，未调用或写入 Mem0。组件一输出是待审核候选，不执行更新。','',
'## 接口、方案与改动','',
'- v2 六个标签：support（支持，无实质新增）、possible_change（同一对象属性可能随时间或条件变化或存在未定冲突）、historical_correction（明确纠正同一历史事实）、supplement（相容新增但本身不支持旧事实）、no_clear_impact（可判断无明显影响）、uncertain（证据等不足，无法可靠判其他类别）。后四种和前两种均保留原始含义。',
'- 候选字段为 memory_id、fact_index、old_subfact、relation、object、attribute、conditions、candidate_impact_fragment、old_quote、new_quote、reason、confirmation_questions；字段必须完全匹配。v2 以每旧子事实一次模型调用，不重试。校验请求与来源、标签/字段类型、身份、旧片段定位、新旧引文；旧片段仅允许唯一大小写修正。格式和字面引文匹配**不能证明语义正确**。',
'- 组件二 `scope_planner.py` 重新执行 v1 的严格 candidate 校验、复核 v2 原始片段定位，要求 upstream status/validation 均成功，传播 confirmation_questions，另行提取和审阅范围；`scope_planner_v2.py` 的独立阶段抽取有独立门控。新增候选字段、新标签或改含义会影响组件二；它并不把上游标签作为已经验证的事实。',
'- v4 在 v2 的提示词后增加阶段、混合、属性、活动、身份、时间规则；程序结构、输出和校验不变。但 v4 将纯粹的单标签表达不足映射为 uncertain，扩展了原有证据不足场景，不能视作严格保留标签语义，因而只留作探索结果。',
'- v5 将清楚的“既支持又新增、且无纠错或阶段变化”标为模型内部保留符 `mixed_unrepresentable`，理由分别描述两部分；v2 原校验拒绝该标记，结果保留为 `partial_or_error`／上游 error，并附未验证 sidecar。这不是新增合法标签，也不会把它映射成其他既有标签。普通候选结构不变；组件二对混合行走已有上游错误路径，不能自动处理新增和支持，也不会得到有效的普通候选。若未来要机器处理两种关系，需明确扩展接口与组件二；这次没有修改。',
'- v5 的混合拦截只在模型自己输出该保留符时起作用，**不能保证识别混合证据**。阶段变化优先 possible_change；同对象不同属性单独比较；模拟与真实活动分开；理由不得从“我的公司”推断雇佣、职务或所有权；记录时间不代替事件时间。上述是提示要求，不是程序保证。',
'- 变更：新增 `relation_judge_v4.py` / `run_local_v4.py`、`relation_judge_v5.py` / `run_local_v5.py`、相应契约测试与本次运行脚本；v5 新增的程序逻辑仅在模型选中混合保留符时附加未验证 sidecar，沿用 v2 错误处理。单线程运行适配器临时替换 v2 提示词，finally 恢复，不支持并发线程。','',
'## 受控设置与实际执行','',
'- 五个请求逐字取自既有 `dev_scope_review_20261109_v1/*_result.json` 的 request，每例恰好一个旧子事实。输入、完整提示词、完整模型消息、原始响应、解析/校验/错误和耗时均保存在本目录；见 `inputs.json`、`manifest.json`、各版本目录和 completion 文件。',
'- v2 与 v4 在同一进程使用同一模型实例，依次每例先 v2 再 v4。v5 因发现 v4 的标签语义问题而在独立进程重新加载相同路径的本地 Qwen3-8B；Python、模型加载方式、BF16、cuda:0、贪心 `do_sample=False`、`enable_thinking=False`、上限 768 和原始输入相同。两次进程不是同一实例，也非随机化顺序；共享 GPU 上存在其他进程，耗时并非严格性能基准。',
'- Transformers 提示 temperature、top_p、top_k 在当前生成模式下可能被忽略，两组设置一致。generation_config 与模型文件、代码的 SHA-256 见 manifest；未设置其他生成参数时沿用模型和库默认值。',
 f"- 前一进程模型加载 {complete['runtime']['load_seconds']} 秒，含加载累计 {complete['elapsed_seconds']} 秒；v5 加载 {strict['runtime']['load_seconds']} 秒，含加载累计 {strict['elapsed_seconds']} 秒。每案例每版真实调用一次：v2 5 次、v4 5 次、v5 5 次，共 15 次，无自动重试；v4 是额外探索，不充作 v5 的重试。模型调用时间与显存见各文件。",'']
out+=['|案例|版本|调用|状态|生成 token|秒|到达 EOS|上限截断迹象|','|---|---|---:|---|---:|---:|---|---|']
for name,_,_ in names:
 for version in ('v2','v4','v5'):
  d=json.loads((HERE/version/f'{name}.json').read_text(encoding='utf8')); gen=d['generations']; g=gen[0] if gen else {}
  out.append(f"|{name}|{version}|{d['model_calls']}|{d['result']['status']}|{g.get('output_tokens')}|{g.get('seconds')}|{g.get('terminated_at_eos')}|{g.get('length_limit_reached_without_eos')}|")
out+=['','15 次真实输出均解析并通过既有格式／引文校验，均以 EOS 结束，未出现长度上限截断；这不证明语义正确。v5 五例均未输出混合保留符，因此没有真实触发混合拦截；该错误路径仅由合成契约测试验证。截断判定记录为生成达到 768 且末 token 非 EOS；解析/校验错误按各 JSON 原样保留，不自动重试。','',
'## 逐案例：事实边界、原文和候选','',
'各项输出均为模型候选；以下关系和理由正确性均待人工确认。新证据所列 recorded_at 是消息记录时间，不是事件发生时间。', '']
for name,num,title in names:
 req=inputs[name]; h=by_num[num]; fact=req['split_result']['facts'][0]
 out += [f'### {title} / {name}（人工记录 {num}）','',f"- 旧子事实：`{fact['raw_subfact']}`。", f"- 人工确认新状态：{h['supported_new_state']}",f"- 允许范围：{h['allowed_modification_scope']}",f"- 人工未知：{h['uncertain_current_state']}",'- 新证据：']
 for ev in req['new_evidence']:out.append(f"  - `{ev['source_id']}` / `{ev.get('recorded_at')}`：{ev['text']}")
 for version in ('v2','v4','v5'):
  d=json.loads((HERE/version/f'{name}.json').read_text(encoding='utf8'));row=d['result']['results'][0]; c=row.get('candidate')
  out += ['',f'**{version}**（状态 `{row["status"]}`）：']
  if c:
   out += [f"- 关联与条件：object={js(c.get('object'))}；attribute={js(c.get('attribute'))}；conditions={js(c.get('conditions'))}。",
     f"- 关系：`{c.get('relation')}`；旧片段原始={js(c.get('candidate_impact_fragment'))}；定位={js(row.get('fragment_match'))}。",
     f"- 旧引文：{js(c.get('old_quote'))}；新引文：{js(c.get('new_quote'))}。",
     f"- 理由：{c.get('reason')}；问题：{js(c.get('confirmation_questions'))}。"]
  else:out.append(f"- 无解析候选；原始响应：{js(row.get('raw_output'))}。")
  out.append(f"- 校验：{js(row.get('validation'))}；错误：{js(row.get('errors'))}。")
 out += ['',f"**初步比较（待确认）：** {analyses[name]}",'']
out += ['## 尚需组件二和上游处理','',
'- 组件二负责独立核实同一主体、对象、属性和事件关系，提出局部保护、阶段历史化/相对时序及新增候选并去重；记录时间不能直接作为有效期。此次没有运行或修改组件二，也未证明端到端更新效果。其既有实现对错误行停止上游采用，并保留待审；对一般阶段历史化需依赖已有的独立提取及门控。',
'- 上游拆分器可能把职称与雇主、旧偏好和多种理由合在同一个子事实，增加局部范围选择难度；职业历史输入中 memory 的 previously 与旧来源当时现在时的对齐待定，拆分器自带 contextualized_subfact 和 supports 均为上游候选，不是新增证据；选取哪些对话也会影响可判断范围。此次冻结已有拆分，不将缺失关系归咎于组件一。','']
(HERE/'REPORT.md').write_text('\n'.join(out),encoding='utf8')
