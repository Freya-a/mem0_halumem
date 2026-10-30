#!/usr/bin/env python3
"""Read-only extraction of stratified scoring-review evidence; no API calls."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
EVAL=ROOT/'results/medium_dev/official_eval_development_20261029_v1';DATA=ROOT/'HaluMem/data/HaluMem-Medium.jsonl';RUN=ROOT/'results/medium_dev/williams_native_prefix5_20261028_v3'
H=lambda x:hashlib.sha256(x.encode()).hexdigest()
records=[json.loads(l) for l in (EVAL/'records.jsonl').open()];chosen=[]
for kind,label in [('update','Correct'),('update','Omission'),('qa','Correct'),('qa','Hallucination'),('qa','Omission')]:
 rows=sorted((x for x in records if x['kind']==kind and x['label']==label),key=lambda x:H('halumem-review-v1:'+x['id']))
 if (kind,label)==('qa','Hallucination'):
  target='qa_1b846c59-456e-9550-dffd-4d23f1eca81f_s003_q000';chosen.extend([next(x for x in rows if x['id']==target),next(x for x in rows if x['id']!=target)])
 else:chosen.extend(rows[:2])
assert len(chosen)==10
uids={x['source']['uuid'] for x in chosen};dataset={u['uuid']:u for l in DATA.open() if (u:=json.loads(l))['uuid'] in uids}
judgments=[
 ('存疑','新岗位和更健康的平衡确实出现，但“正在求职/考虑转岗”旧句仍以当前时态存在；评分理由把写库时间当成历史化证据，不能仅凭执行时间断言旧状态已标记过时。依据官方更新提示词，是否足以视为有效替代需人工统一口径。','新状态明确，旧状态时间表达不足；不等于判新状态未保存。',[(7,0),(7,2)]),
 ('存疑','新职称与雇主均被保存，“最近晋升”有新状态线索；旧 Director 文本仍以现在时存在。评分理由称旧记录已被取代，却未说明其是否已明确标为过时；Director 也可能作为职业泛称兼容，故不能仅凭共存判错。','可认可新增晋升事实，但对官方要求的替代/过时条件尚缺充分依据。',[(4,0)]),
 ('认可','检索包含对 Steven、Mary 的感谢和支持，但没有明确说明这些支持发生在该电影项目期间，官方参考的情境要素缺失；按官方严格完整性规则判部分遗漏有依据。','源会话中具体二人姓名由助手提出，用户原话仅计划表达感谢；官方参考标注的来源充分性另待核验，不把其当作用户确认。',[(8,7),(8,8),(8,9)]),
 ('存疑','检索表达了对同事朋友的感激，但没有明确说他们促进了成功；这一缺失可以支持遗漏。评分理由又称主语被误指为 user、全名缺失即不匹配，忽略这些都是同用户隔离记忆，该理由无充分依据。','分类可能合理，但理由混入不成立的主体推断；用户原话是否充分支持“促成成功”也需核对。',[(9,0),(9,2),(9,10),(9,24)]),
 ('认可','原话、参考答案和回答均为 classical music，检索第4条也明确支持；无缺失或冲突。','官方 Correct 依据充分。',[(2,22)]),
 ('存疑','回答否认失业且称经济稳定，参考答案还明确包含月收入 15700 USD；判词以“高收入”推断稳定并称没有遗漏，但收入数额不等于必然经济稳定，且严格按参考答案衡量是否省略数字值得复核。','原话另说收入使其能舒适储蓄，但评分器只可依参考和 key points 判定；不得把额外原话当评分器已有证据。',[(1,2)]),
 ('不认可','参考与 key points 只表示希望获得历史饮品推荐，没有给出具体饮品；回答称没有指定具体饮品，并不逻辑矛盾于希望获得推荐。评分器把它扩成“没有推荐存在或可能”并据此判幻觉，缺少依据。','参考答案“Recommendations for historical beverages”本身不指明饮品，回答是否应判遗漏或按未知问题处理仍待人工，不擅改官方标签。',[(3,4),(3,16)]),
 ('存疑','参考是 Unknown、证据为空；回答“未提到兄弟姐妹”是对对话提及情况的否定，并非断言没有兄弟姐妹。仅靠空 key points 不能直接证明跨全部对话的否定命题，但评分理由把两者直接等同也不充分。','可能因回答对全部对话作无证据概括而有风险；不能仅依据记忆未召回断定整段对话确实没有提及。',[]),
 ('存疑','回答没有给出参考要求的无伴侣和健康项目目标，按严格参考完整性判 Omission 有依据；然而评分理由进一步称计划“肯定尚未建立、肯定不是2025年”超出了给定证据。','标签可成立，理由中的额外确定性不能视为证据。',[(0,8),(0,10)]),
 ('无法判断','题目指向 Feb 05 的讨论，但实际按题目挂载会话检索了 Mar 01 之后的快照，命中包含随后完成转岗等信息；该结果不满足将题目日期作为知识截点的要求，不能用它认定时间合规条件下的评分。','就现有回答而言，缺少参考要点确有遗漏，但否定该日记忆的断言也值得复核；需从 Feb 05 会话后的快照重建检索和回答后再判断，本轮不重跑。',[(6,2),(6,4),(7,4),(7,8)])]
manifest=[]
for n,(x,(decision,reason,caveat,quotes)) in enumerate(zip(chosen,judgments),1):
 src=x['source'];uid=src['uuid'];idx=src['session_index_zero_based'];ordinal=src['session_ordinal_one_based'];folder=RUN/'users'/uid/f'session_{ordinal:03d}';s=dataset[uid]['sessions'][idx];field=src['memory_point'] if x['kind']=='update' else src['question'];judge=x['stages']['judge']['payload']['score']
 quoted=[]
 for si,mi in quotes:
  m=dataset[uid]['sessions'][si]['dialogue'][mi];quoted.append({'session_index_zero_based':si,'message_index_zero_based':mi,**m})
 if x['kind']=='qa':
  for e in x.get('evidence_time_check',[]):
   if e['match']=='current_or_prior':assert min(e['matching_session_indices'])<=idx
 case={'number':n,'id':x['id'],'kind':x['kind'],'automatic_label':x['label'],'selection_sha256':H('halumem-review-v1:'+x['id']),'decision_llm_assisted':decision,'review_rationale':reason,'caveat':caveat,'source':src,'session_start':s['start_time'],'session_end':s['end_time'],'source_dialogue_highlights':quoted,'source_full_session_input':str(folder/'input.json'),'relevant_complete_source_data_path':str(DATA),'retrieved_hits':x['hits'],'system_response':x['stages']['answer']['payload']['text'] if x['kind']=='qa' else None,'official_judge_result':judge,'snapshot_sha256':src['snapshot_sha256'],'snapshot_path':src['snapshot_path'],'official_record_path':str(EVAL/'records.jsonl')}
 manifest.append({'number':n,'id':x['id'],'kind':x['kind'],'label':x['label'],'selection_sha256':case['selection_sha256'],'review':decision,'case_evidence':f'case_{n:02d}.json','snapshot_sha256':case['snapshot_sha256']})
 (OUT/f'case_{n:02d}.json').write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n')
 lines=[f'# 复核 {n:02d}：{x["kind"]} / {x["label"]}',f'','**结论（LLM 辅助，尚未人工确认）：'+decision+'**', '',reason,'',caveat,'',f'来源 ID：`{x["id"]}`；原数组 `sessions[{idx}]`，会话结束 `{s["end_time"]}`；对应 after 快照 SHA-256：`{src["snapshot_sha256"]}`。','',f'[完整原始会话输入]({folder}/input.json) · [对应会话后快照]({src["snapshot_path"]}) · [本案例完整结构化证据](case_{n:02d}.json) · [原始逐项评测记录]({EVAL}/records.jsonl)','','## 官方参考 / 原始证据','', '```json',json.dumps(field,ensure_ascii=False,indent=2),'```','']
 if not quoted:lines+=['该题 reference 为 Unknown，官方 evidence 为空；没有选取能证明全体对话不存在提及的原话。完整范围可由结构化来源及数据文件查证。','']
 for q in quoted:lines += [f'- `sessions[{q["session_index_zero_based"]}]/dialogue[{q["message_index_zero_based"]}]`，{q["role"]}，{q["timestamp"]}：{q["content"]}']
 lines += ['','## 当时截点的检索结果','',f'按官方适配器规定 top {10 if x["kind"]=="update" else 20}，展示全部 {len(x["hits"])} 条；时间为写库执行时间，不是原始对话时间。','', '| 排名 | 记忆 ID | 执行时间 | 分数 | 内容 |','|---:|---|---|---:|---|']
 for i,h in enumerate(x['hits'],1):lines.append(f'| {i} | `{h["id"]}` | {h["timestamp"]} | {h["score"]:.4f} | {h["memory"].replace("|","\\|")} |')
 if x['kind']=='qa':lines+=['','## 系统回答','',x['stages']['answer']['payload']['text']]
 lines+=['','## 自动判词','',f'类别：`{x["label"]}`','',judge.get('reason',judge.get('reasoning','（无理由）')),'','## 复核意见','',f'**{decision}**：{reason}', '',f'限制：{caveat}','']
 (OUT/f'case_{n:02d}.md').write_text('\n'.join(lines))
(OUT/'selection.json').write_text(json.dumps({'selection_rule':'五类各2条；SHA-256(UTF-8("halumem-review-v1:"+id)) 字典序升序取前2；QA Hallucination 强制保留 pilot 争议题，再取其余中哈希最小1条。','method':'LLM辅助复核，不代表人工确认','cases':manifest},ensure_ascii=False,indent=2)+'\n')
(OUT/'parse_failures_original.json').write_bytes((EVAL/'parse_failures.json').read_bytes())
print('selected',len(chosen),'generated evidence files',len(chosen)*2)
