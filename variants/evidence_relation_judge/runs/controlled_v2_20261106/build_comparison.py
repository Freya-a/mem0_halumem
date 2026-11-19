"""Create side-by-side report from preserved runs; makes no model calls."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'real_cases_20261106'
manifest=json.loads((HERE/'manifest_before.json').read_text())
notes={
'skydiving':'''模型仍以模拟跳伞令人兴奋作为“对极限运动态度可能变化”的理由，存在从模拟活动推广到真实极限运动的风险；没有说用户真的跳伞，且确实提到仍重视安全。尽管如此，它仍把安全是否保持作为问题，未充分利用已给出的安全陈述。模型引用的新证据仅为 dialogue-0，理由中“仍优先安全”实际来自另一个输入 dialogue-8，单一新引文不能单独支持理由的全部内容。片段从新文本错填改成完整旧事实，但没有说明为何不能缩小，也包含安全部分；通过字面检查不意味着该范围或关系准确。''',
'promotion':'''两个版本都输出职位可能变化，改进版理由更明确说同一公司；这在文字表达上更清楚地区分了雇主，但候选片段依旧覆盖整句，含未显示变化的雇主，没有实现更细的定位，也没有解释为何整句必要。`Director` 与 `lead director` 的关系仍可确认，不应从片段直接决定修改范围。''',
'career_history':'''两个版本都主动输出 uncertain。改进版通过唯一大小写匹配恢复旧原文，但这只修复形式，不能证明语义正确。新证据只说“my consulting firm”取得客户，可以表示与咨询公司有关，但不能单凭这句话确定其为该公司“current employment”或存在特定“current role”；改进版理由和两个问题均把这些作为前提，有超出证据的问题。它也不再明确询问原 v4 标出的旧记忆过去时与旧上下文现在时的对齐问题。'''
}
comparison={}
for name in ('skydiving','promotion','career_history'):
    before=json.loads((OLD/f'{name}_run.json').read_text()); after=json.loads((HERE/f'{name}_run.json').read_text())
    assert before['input']==after['input']
    b=before['result']['results'][0]; a=after['result']['results'][0]
    comparison[name]={'input':after['input'], 'v1':{'raw_output':b['raw_output'],'candidate':b['candidate'],'located_fragment':None if b['status']!='ok' else b['candidate']['candidate_impact_fragment'],'fragment_match':'v1_unavailable','status':b['status'],'validation':b['validation'],'errors':b['errors']}, 'v2':{'raw_output':a['raw_output'],'candidate':a['candidate'],'located_fragment':a['fragment_match']['located'] if a['fragment_match'] else None,'fragment_match':a['fragment_match'],'status':a['status'],'validation':a['validation'],'errors':a['errors']},'preliminary_analysis':notes[name]}
with (HERE/'comparison.json').open('x',encoding='utf-8') as f: json.dump(comparison,f,ensure_ascii=False,indent=2);f.write('\n')


def cell(value):
    if isinstance(value, (dict,list)):
        value=json.dumps(value,ensure_ascii=False)
    if value is None:return '无'
    return str(value).replace('|','\\|').replace('\n','<br>')

out=['''# 受控改进版：三个已保存真实案例对照

本报告的语义判断是待用户确认的初步分析。每例各使用同一输入、同一个本地 Qwen3-8B 权重目录，v1 和 v2 都是 BF16、CUDA 0、无采样、最多 512 新 token、关闭 thinking、每例调用一次且无重试。实际运行的系统提示词和完整输入在各自运行 JSON 中。模型配置、索引哈希及模型权重文件大小与前次一致；没有重新计算完整权重哈希，不能据此证明权重字节未变。动态显存和耗时可能不同。

v2 追加提示词与大小写唯一定位，保留六种标签和原始引文校验；因此这是联合干预，不可仅凭前后对照把语义差异归因给单独一项改动。旧版和新版的运行前代码、提示词、输入和模型文件标识见 `manifest_before.json`，旧版提示词 SHA-256 `''',manifest['v1_prompt_sha256'],'''`，新版 `''',manifest['v2_prompt_sha256'],'''`。采样参数没有变化。程序校验不验证语义。

以下“原始输出”格中的文本是原始输出字符串的 JSON 转义表示（包括 `\\n`），可从 `comparison.json` 或对应 `*_run.json` 原样读取；原始输出的内容没有被恢复逻辑改写。旧版失败时“定位结果”记为无，不把离线回放伪装成当时结果。
''']
for name,vals in comparison.items():
    b=vals['v1']; a=vals['v2']; bc=b['candidate']; ac=a['candidate']; inputs=vals['input']
    out.append('\n## '+name+'\n\n')
    out.append('旧事实：'+cell(inputs['split_result']['facts'][0]['raw_subfact'])+'\n\n')
    out.append('新证据：'+cell([{'source_id':x['source_id'],'text':x['text']} for x in inputs['new_evidence']])+'\n\n')
    rows=[('关系类别',bc['relation'],ac['relation']),('模型原始片段',bc['candidate_impact_fragment'],ac['candidate_impact_fragment']),
          ('程序定位后片段',b['located_fragment'],a['located_fragment']),('定位方式',b['fragment_match'],a['fragment_match']),
          ('旧引文',bc['old_quote'],ac['old_quote']),('新引文',bc['new_quote'],ac['new_quote']),
          ('校验结果',{'status':b['status'],'validation':b['validation'],'errors':b['errors']},{'status':a['status'],'validation':a['validation'],'errors':a['errors']}),
          ('模型理由',bc['reason'],ac['reason']),('待确认问题',bc['confirmation_questions'],ac['confirmation_questions']),
          ('完整原始输出（JSON 转义字符串）',json.dumps(b['raw_output'],ensure_ascii=False),json.dumps(a['raw_output'],ensure_ascii=False))]
    out.append('| 字段 | 原版 | 改进版 |\n| --- | --- | --- |\n')
    for title,left,right in rows:out.append('| '+title+' | '+cell(left)+' | '+cell(right)+' |\n')
    out.append('\n**初步分析，待用户确认：** '+notes[name]+'\n')
    old=json.loads((OLD/f'{name}_run.json').read_text())['runtime_cumulative']['generations'][-1]
    new=json.loads((HERE/f'{name}_run.json').read_text())['runtime_cumulative']['generations'][-1]
    out.append(f"\n运行：原版 {old['seconds']} 秒、峰值 allocated {old['peak_allocated_bytes']/1024**3:.2f} GiB；改进版 {new['seconds']} 秒、峰值 allocated {new['peak_allocated_bytes']/1024**3:.2f} GiB。各一次调用。\n")
out.append('''
## 观察和限制

- 三例中原版有两例因候选片段失败，改进版三例均通过程序校验；这是这三个开发案例的观察，不是准确率。改进版跳伞由模型复制了旧事实而通过；职业历史由唯一大小写恢复通过。
- 为区分两种改动，`baseline_output_offline_replay.json` 将原版已保存输出离线交给新校验逻辑：职业历史的大小写被唯一恢复；跳伞的新证据片段仍被拒绝。回放无模型调用，也不替代原版当时的失败结果。
- 三例各只有一个旧子事实。不能由此推断跨多个独立旧事实的误判率，也不能确认局部片段、证据关联或待确认问题的普遍效果。引文匹配只证明字面归属。
- 未重新拆分、更新 Mem0、运行完整开发集或接入时间组件/FactTrack。原版代码和运行记录保持不变。
''')
(HERE/'REPORT.md').write_text(''.join(out),encoding='utf-8')
