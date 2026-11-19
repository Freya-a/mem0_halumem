import json
from pathlib import Path
p=Path(__file__).resolve().parent
reviews={
'01_susan':('完整保留朋友身份、姓名/称呼和支持鼓励；一条整体输出，未把关系和支持拆成独立事实。','未见正文编造；memory 的 supports 把旧记忆未显式写出的用户主体直接写出，主体可由另列的第一人称上下文支持，但并非单凭该 memory 引文可证。','名字究竟是复合姓名还是拼接、Susan 与 ThomasSusan 的指代，以及支持的具体作用范围，需结合来源确认；模型已列姓名问题。'),
'02_skydiving':('保留不喜欢、跳伞例子、受伤风险和安全健康冲突，未丢旧记忆中的因果关系；整体仍是一条。','正文未见超出旧记忆；context supports 称原文确认因果需小心：原对话直接将高风险作为“避免”的原因，旧记忆则将它作为“不喜欢”的原因。','不能仅凭这段旧语境断言用户现在仍有同样态度；原对话 dislike 与 avoid 的因果对应需要人工判断。'),
'03_director':('保留职位和雇主；一条整体输出。','未见相对旧记忆及上下文的新增事实。','输出现在时延续了旧记忆的表达，但旧来源记录于 2025-09-05，不能仅凭此结果断言当前仍为该职称；发生时间、结束时间未明确。'),
'04_persian_cat':('完整保留波斯猫偏好及高贵、平静、优雅、历史魅力等旧记忆理由；一条整体输出，粒度较粗。','正文未见超出旧记忆；context supports 将优雅和历史都说成喜欢的直接理由偏强：原对话明确的 because 是高贵和平静，后句说猫的存在给家带来优雅和历史感。','优雅与历史感是否均应作为独立的喜欢原因，需要人工判断；历史 charm 是旧记忆概括，非原话逐字用语。'),
'05_career_history':('保留 previously、公司及高级开发职位；一条整体输出。raw 句末多一个句号，但对应的证据引文逐字匹配。','未见正文编造；context 清楚承认过去时并非由旧语境独立证明。','来源发言为 2025-09-05 的现在时，旧记忆为后来快照中的过去时；离职时间和两者时间衔接无法从单条上下文确定。')}
manifest=json.loads((p/'manifest.json').read_text())
lines=['# v8 旧记忆拆分：5 条人工审核主目标的试跑','',
'2026-11-18（Asia/Shanghai）。使用现有 v8 入口和未修改的提示词；真实模型 `qwen-plus-2025-12-01`，请求体 `enable_thinking=false`；每条最多一次请求、SDK 不重试。5 次均返回指定模型并通过既有结构、ID 与逐字引文校验，无调用错误。请求参数是客户端请求体观测，服务端内部行为不可见。','',
'五条都只产生一个子事实，复合内容整体保留，没有展示能否将其中可分别检查的成分拆开。下方语义检查是助手初审，需人工确认；逐字引文通过不证明语义支持或事实真实。本样本为定向选取，部分案例曾用于历史诊断，不能估计总体质量。未发送目标会话新证据或人工标签；只读原生运行快照和更早的用户对话，没有调用或写入 Mem0。','',
'## 检查表','',
'| 案例 / 审核主目标 | 遗漏与粒度 | 编造／证据支持 | 引文 | 待确认 |',
'|---|---|---|---|---|']
for c in manifest['cases']:
 name=c['case']; a,b,d=reviews[name]
 lines.append(f"| {name} / {c['reviewed_main_target']} | {a} | {b} | 逐字通过 | {d} |")
lines += ['','## 逐条：输入与完整拆分 JSON','']
for c in manifest['cases']:
 name=c['case']; req=json.loads((p/name/'input.json').read_text()); result=json.loads((p/name/'result.json').read_text()); ctx=req['source_context'][0]
 lines += [f"### {name}：审核主目标 {c['reviewed_main_target']}",'',f"更新前快照：`{c['before_snapshot']}#/api_snapshot/results/{c['before_snapshot_index']}`。",'', '**旧记忆原文**','',f"> {req['memory_text']}",'',f"**输入上下文**（{ctx['speaker']}，{ctx['recorded_at']}；`{ctx['source_ref']}`）",'',f"> {ctx['text']}",'','**完整拆分 JSON**','','```json',json.dumps(result,ensure_ascii=False,indent=2),'```','']
lines += ['## 复核与文件说明','',
'每个案例目录的 `input.json` 保存精确请求输入；`result.json` 为通过原有校验后的完整结果，`raw_content.txt` 为模型原始文本，`provenance.json` 保存旧快照位置与来源哈希，`request_audit.json` 保存实际客户端请求体中的模型与 thinking 参数检查，`response_metadata.json` 保存返回模型、结束原因和可获取的 token 用量。`manifest.json` 保存提示词版本及哈希、选样及来源；`batch_completion.json` 保存每次调用状态。`frozen_prompt.txt` 是本次请求前的提示词副本。','',
'来源中的记录时间只是用户发言时间，不自动等于事件发生时间。第 24 条所用的旧职业是该目标共享会话中的历史保护对象；它不是第 24 条的新增“获客”内容。第 10 条是晋升目标的更新前 Director 旧状态，而非晋升后的 Lead Director。','']
(p/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
