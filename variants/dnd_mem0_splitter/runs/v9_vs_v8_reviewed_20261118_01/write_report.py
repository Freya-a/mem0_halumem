import json
from pathlib import Path
p=Path(__file__).resolve().parent
reviews={
'01_susan':('v9 将朋友关系与支持拆为两条，相比 v8 的一条更便于分别更新；支持条保留 ThomasSusan/Susan 与受支持者。','未发现正文漏掉旧事实。v9 的 memory supports 说引文本身确定“用户”是朋友，超出该引文：主体需上下文支持。姓名是否为拼接等仍未证实，v8 有待确认项，v9 的待确认项却为空，须人工核查。'),
'02_skydiving':('两版都是一条；将不喜欢、受伤风险和安全健康冲突保持一起合理，局部原因改动时应在该关系内处理，避免变成无条件断言。','旧记忆的否定和因果保留。原对话的 because 直接关联 avoid，而不是直接将其写成 dislike 的原因；v9 supports 将 avoid 称为行为后果，来源未明确说明是“不喜欢”的后果，解释可能越界。'),
'03_director':('两版都是一条。保留公司与职位的关系是合理的，但 v9 未实现雇主与职位分别维护的目标；若职位改变，需要修改整条并保留公司。','旧文本的雇主和职位均在。上下文是 2025-09-05 的自述，v9 没有记录现在时的时间锚点或待确认项，不能据此认定当前职位；可分别形成带相同工作关系和时间边界的条目，但不能随意延长状态。'),
'04_persian_cat':('两版都是一条。原因与喜欢保持相连是合理的；多种理由无法分别修改，后续若拆分仍须保留各理由与喜欢的因果及其作用范围。','旧记忆各项理由均保留。用户原话明确的 because 与高贵、平静相连；优雅和历史说的是猫给家带来的效果，v9 supports 将其全部表述为确认喜欢的理由偏强，需人工确认。'),
'05_career_history':('两版都是一条，保留过去时间和具体公司与职位。雇主和职位不能单独维护，v9 未在此实现可分别修改的粒度。','旧事实和 previously 保留，时间起止待确认。v9 的第二个 pending 称上下文缺少大小写一致性，但两处 Blockchain Tech 大小写实际上相同；这是待确认理由中的无依据描述，不应采信。')}
def cell(s): return str(s).replace('|','\\|').replace('\n','<br>')
def fact_cell(f):
 pieces=[f"**#{f['fact_index']} raw:** {cell(f['raw_subfact'])}",f"**contextualized:** {cell(f['contextualized_subfact'])}"]
 for e in f['evidence']:
  pieces.append(f"**引文 [{cell(e['source_type'])}/{cell(e['source_id'])}]:** “{cell(e['quote'])}”<br>**supports:** {cell(e['supports'])}")
 pc=f['pending_confirmations']
 if not pc: pieces.append('**待确认：** []')
 else:
  for x in pc: pieces.append(f"**待确认：** {cell(x['item'])}<br>**原因：** {cell(x['reason'])}")
 return '<br><br>'.join(pieces)
def read(path): return json.loads(path.read_text())
m=read(p/'manifest.json'); batch=read(p/'batch_completion.json')
lines=['# v8 / v9：5 条旧记忆逐案对照','',
'本试验逐字复用 5 组既有 v8 输入；每组 v9 仅一次 `qwen-plus-2025-12-01` 请求，`enable_thinking=false`，SDK 重试关闭。5 次均返回指定模型并通过原有结构、ID、逐字引文检查；完整调用记录见 `batch_completion.json`。本报告中的语义检查为助手初审，需人工确认；引文逐字匹配不证明 supports 或语义正确。','',
'5 条中 v8 均为 1 条，v9 只有 Susan 案拆为 2 条，其余仍为 1 条。样本是定向选取且部分曾用于设计，不是独立总体评估，也不能从单次输出计算可靠率。v8 和 v9 虽使用同一模型与输入，调用时间不同，模型服务和采样仍可能变化。未修改提示词来追逐本次结果。','',
'## 检查汇总','','| 案例 / 主目标 | v8 → v9 数量 | 局部更新与粒度 | 遗漏、语义及待确认 |','|---|---:|---|---|']
for c in m['cases']:
 d=p/c['case']; v8=read(d/'v8_result.json'); r=d/'v9_result.json'; v9=read(r) if r.exists() else None; a,b=reviews[c['case']]
 lines.append(f"| {c['case']} / {c['target']} | {len(v8['facts'])} → {len(v9['facts']) if v9 else '失败'} | {a} | {b} |")
lines+=['','## 逐案并排：全部原始及补足子事实、引文和待确认项','']
for c in m['cases']:
 d=p/c['case']; req=read(d/'input.json'); v8=read(d/'v8_result.json'); path=d/'v9_result.json'; v9=read(path) if path.exists() else None; ctx=req['source_context'][0]; a,b=reviews[c['case']]
 lines += [f"### {c['case']} · 审核主目标 {c['target']}",'',f"**旧记忆：** {req['memory_text']}",'',f"**相同输入上下文：** {ctx['speaker']}，{ctx['recorded_at']}：{ctx['text']}",'',f"**上下文来源：** `{ctx['source_ref']}`",'', '| v8 全部子事实 | v9 全部子事实 |','|---|---|']
 one=[fact_cell(f) for f in v8['facts']]; two=[fact_cell(f) for f in v9['facts']] if v9 else ['调用或校验失败，见本案例 report.json 与 raw_content.txt。']
 for i in range(max(len(one),len(two))): lines.append(f"| {one[i] if i<len(one) else '—'} | {two[i] if i<len(two) else '—'} |")
 lines += ['',f'**局部更新：** {a}','',f'**语义检查：** {b}','','完整原始 JSON： [v8]('+c['case']+'/v8_result.json) · [v9]('+c['case']+'/v9_result.json)；原始模型内容见 `raw_content.txt`。','']
lines+=['## 可追溯性','',
'`manifest.json` 包含输入 SHA-256、模型、提示词版本和哈希；每个目录的 `input.json` 为原运行文件逐字节复制，`provenance.json` 保留快照与原始对话来源。`request_audit.json` 核对了实际客户端请求体的模型、thinking 参数、提示词哈希和输入；`response_metadata.json` 与 `report.json` 保存返回模型及错误。`frozen_prompt.txt` 为调用前冻结的 v9 提示词。服务端内部执行细节不由客户端审计证明。','',
'目标 24 对应的是该会话的旧职业保护对象，并非获客新事实。来源记录时间是发言时间，不自动是事件发生时间。没有导入、调用或写入 Mem0；没有运行完整数据集。','']
(p/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
