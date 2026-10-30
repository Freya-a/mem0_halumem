#!/usr/bin/env python3
import sqlite3,json,statistics,collections,hashlib,os
from pathlib import Path
from datetime import datetime
import engine
OUT=Path(__file__).resolve().parent;ROOT=engine.ROOT;DB=OUT/'checkpoints.sqlite3'; RUN=ROOT/'results/medium_dev/williams_native_prefix5_20261028_v3';DATA=ROOT/'HaluMem/data/HaluMem-Medium.jsonl'
def dump(p,o):
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,p)
def pct(x):return '—' if x is None else f'{100*x:.2f}%'
def labelstatus(s):return s if s else 'not_started'
with sqlite3.connect(DB) as c:
 c.row_factory=sqlite3.Row
 items=[dict(r) for r in c.execute('select * from items order by kind,id')]
 stages={}
 for r in c.execute('select * from stages'):stages[(r['id'],r['stage'])]={'status':r['status'],'payload':json.loads(r['payload']) if r['payload'] else None}
 calls=[dict(r) for r in c.execute('select * from calls order by id')]
for c in calls:
 for k in ('request','response','usage'):c[k]=json.loads(c[k]) if c[k] else None
 if c['stage']=='embedding' and c['response'] and 'vector' in c['response']:
  vector=c['response'].pop('vector');c['response']['vector_dimensions']=len(vector);c['response']['vector_sha256']=hashlib.sha256(json.dumps(vector,separators=(',',':')).encode()).hexdigest()
with (OUT/'api_calls.jsonl').open('w') as f:
 for c in calls:f.write(json.dumps(c,ensure_ascii=False)+'\n')
users={json.loads(i['source'])['uuid'] for i in items}
dataset={u['uuid']:u for l in DATA.open() if (u:=json.loads(l))['uuid'] in users}
records=[];review=[];errorlist=[];emptylist=[]
for item in items:
 ident=item['id'];kind=item['kind'];src=json.loads(item['source']);st={k:stages.get((ident,k),{'status':'not_started','payload':None}) for k in ('embedding','retrieval','answer','judge')}
 hits=(st['retrieval']['payload'] or {}).get('hits');j=st['judge']['payload'] or {};label=(j.get('score') or {}).get('evaluation_result');valids=['Correct','Hallucination','Omission']+(['Other'] if kind=='update' else [])
 rec={'id':ident,'kind':kind,'source':src,'stages':st,'model_calls':[c['id'] for c in calls if c['item']==ident],'retrieval':st['retrieval']['status'],'hits':hits,'judge':st['judge']['status'],'label':label}
 # Every item's lookup is at its own session-after snapshot; no later snapshot is consulted.
 flags=[]
 if st['retrieval']['status']=='ok' and not hits:flags.append('empty_retrieval');emptylist.append(ident)
 for stage,x in st.items():
  if x['status'] in ('error','parse_error','started'):
   flags.append(f"{stage}:{x['status']}");errorlist.append({'id':ident,'stage':stage,**x})
 if st['judge']['status']=='ok' and label not in valids:flags.append('invalid_judge_label')
 if label and label!='Correct':flags.append('non_correct_judgment_review')
 if ident=='qa_1b846c59-456e-9550-dffd-4d23f1eca81f_s003_q000':flags.append('pilot_reasoning_disputed_review')
 if kind=='qa':
  evidence=src['question']['evidence'];u=dataset[src['uuid']];idx=src['session_index_zero_based'];positions=[]
  for ev in evidence:
   text=ev['memory_content'];matches=[n for n,s in enumerate(u['sessions']) if any(m.get('memory_content')==text for m in s.get('memory_points',[]))]
   if not matches:positions.append({'memory_content':text,'match':'no_exact_match'})
   elif min(matches)>idx:positions.append({'memory_content':text,'match':'future_only','matching_session_indices':matches});flags.append('evidence_exact_match_future_only')
   else:positions.append({'memory_content':text,'match':'current_or_prior','matching_session_indices':matches})
  rec['evidence_time_check']=positions
  if any(x['match']=='no_exact_match' for x in positions):flags.append('evidence_source_not_exactly_matched_review')
 rec['review_flags']=flags
 if flags:review.append({'id':ident,'flags':flags,'label':label,'question_or_update':src['question']['question'] if kind=='qa' else src['memory_point']['memory_content']})
 records.append(rec)
with (OUT/'records.jsonl').open('w') as f:
 for r in records:f.write(json.dumps(r,ensure_ascii=False)+'\n')
dump(OUT/'errors.json',errorlist);dump(OUT/'empty_retrievals.json',emptylist);dump(OUT/'manual_review.json',review)
metrics={k:engine.metrics([r for r in records if r['kind']==k],k) for k in ['update','qa']}
for k in ('update','qa'):
 m=metrics[k];rs=[r for r in records if r['kind']==k]
 m['embedding_attempted']=sum(r['stages']['embedding']['status']!='not_started' for r in rs)
 m['retrieval_attempted']=sum(r['stages']['retrieval']['status']!='not_started' for r in rs)
 m['answer_generated']=sum(r['stages']['answer']['status']=='ok' for r in rs) if k=='qa' else None
 m['judge_api_attempted']=sum(r['stages']['judge']['status'] in ('ok','error','started','parse_error') for r in rs)
 m['judge_response_received']=sum(r['stages']['judge']['status'] in ('ok','parse_error') for r in rs)
 m['scoring_attempted']=m['judge_api_attempted']
 m['scoring_completed']=m['judge_response_received']
 m['invalid_judge_label']=sum(r['judge']=='ok' and r['label'] not in (['Correct','Hallucination','Omission']+(['Other'] if k=='update' else [])) for r in rs)
 m['item_with_error_or_uncertain']=len({e['id'] for e in errorlist if e['id'].startswith(k+'_')})
 m['unresolved_without_judgment']=sum(r['judge'] not in ('ok','parse_error') for r in rs)
 if k=='qa':m['actual_official_input_records_with_answer']=m['answer_generated']

parse_failures=[]
for call in calls:
 if call['stage']=='judge' and call['status']=='ok' and call['response'] and 'raw' in call['response']:
  try:engine.parse_score(call['response']['raw'])
  except (ValueError,json.JSONDecodeError) as e:parse_failures.append({'call_id':call['id'],'item':call['item'],'error_type':type(e).__name__,'raw':call['response']['raw']})
dump(OUT/'parse_failures.json',parse_failures)
usage={};latency={}
for origin in ('development','development_retry','pilot','combined'):
 subset=[x for x in calls if origin=='combined' or x['origin']==origin]
 u={'attempts':len(subset),'successful':sum(x['status']=='ok' for x in subset),'errors':sum(x['status']=='error' for x in subset),'unknown_started':sum(x['status']=='started' for x in subset),'by_stage':{},'tokens':{'prompt_tokens':0,'completion_tokens':0,'total_tokens':0},'usage_missing':0,'fee':None}
 for x in subset:
  d=u['by_stage'].setdefault(x['stage'],{'attempts':0,'success':0,'errors':0,'started':0,'prompt_tokens':0,'completion_tokens':0,'total_tokens':0});d['attempts']+=1
  d['success' if x['status']=='ok' else 'errors' if x['status']=='error' else 'started']+=1
  if x['status']=='ok' and not x['usage']:u['usage_missing']+=1
  for key in u['tokens']:
   val=(x['usage'] or {}).get(key) or 0;u['tokens'][key]+=val;d[key]+=val
 usage[origin]=u
 for stage in ('embedding','answer','judge'):
  a=sorted(x['elapsed'] for x in subset if x['stage']==stage and x['elapsed'] is not None)
  if a:latency[origin+':'+stage]={'n':len(a),'sum_seconds':sum(a),'mean_seconds':statistics.mean(a),'median_seconds':statistics.median(a),'p95_seconds':a[min(len(a)-1,__import__('math').ceil(.95*len(a))-1)],'max_seconds':max(a)}
summary={'metrics':metrics,'calls':usage,'latency':latency,'manual_review_count':len(review),'empty_retrieval_count':len(emptylist),'error_count':len(errorlist),'historical_json_parse_failures':len(parse_failures),'timestamp_utc':datetime.utcnow().isoformat()+'Z'};dump(OUT/'summary.json',summary)
rows=[]
for k,title in [('update','官方更新分类'),('qa','官方 QA 分类')]:
 m=metrics[k];rows.append(f"### {title}\n\n候选 {m['candidates']}；embedding 已尝试 {m['embedding_attempted']}；完成检索 {m['retrieved']}，空检索 {m['empty']}，检索未完成 {m['retrieval_failed_or_unknown']}；评分调用已尝试 {m['judge_api_attempted']}、收到响应 {m['judge_response_received']}；有效标签 {m['valid']}；存在错误或未确定状态的条目 {m['item_with_error_or_uncertain']}。" + (f"QA 回答已生成 {m['answer_generated']}。" if k=='qa' else '')+f"\n\n| 分类 | 数量 | all 分母 {m['official_all']} | valid 分母 {m['valid']} |\n|---|---:|---:|---:|\n"+'\n'.join(f"| {key} | {num} | {pct(m['ratio_all'][key])} | {pct(m['ratio_valid'][key])} |" for key,num in m['counts'].items()))
reviewlines=['# 待人工复核清单','',f'共 {len(review)} 条；本清单为筛查队列，所有自动判词均未经逐项人工确认。','', '| ID | 分类 | 标记 |','|---|---|---|']+[f"| {x['id']} | {x['label'] or '无'} | {', '.join(x['flags'])} |" for x in review]
(OUT/'MANUAL_REVIEW.md').write_text('\n'.join(reviewlines)+'\n')
report=f'''# HaluMem 开发前缀更新和问答评测

2026-10-29；结果仅覆盖已运行的 3 用户、28 会话、990 条消息。开发集包含调试过的用户，不是无偏整体估计。逐条原标注及来源、匹配快照哈希、检索 ID/分数/时间、回答、评分和完整理由见 `records.jsonl`；模型请求、响应、usage 和延迟见 `api_calls.jsonl`；可断点续跑的原始状态在 `checkpoints.sqlite3`。二者含实验数据，按原数据权限处理。

## 指标与分母

{chr(10).join(rows)}

更新 all 分母为成功检索且非空的更新候选数，对应官方 `evaluation.py` 对非空 `memories_from_system` 的筛选；检索失败的候选资格未知，单列而非假定空或非空。官方代码会把空检索更新点导向 integrity 而不是 update，本报告不冒充已完成 integrity。QA all 分母列完整 75 道候选；如果回答尚未生成，这相当于固定候选范围的保守覆盖分母，不能伪称官方 CLI 已接受了缺失 `system_response` 的输入。valid 只含官方规定标签。各类 all 比例以该分母相除，失败不会填分，也不会悄悄消失；空检索、无响应、无效标签的数量须与指标一起看。

评分使用官方 `eval_tools.py` 提示词和 JSON 代码块解析规则，原生 Mem0 运行未按官方托管 Mem0 的自定义提取指令运行；使用本地 Mem0 快照和本地 Qdrant cosine 重建查询，更新 top 10、QA top 20。每题严格使用其挂载会话处理后的同一用户快照，不读取最终库或未来会话库。embedding 是现在对查询重算，模型别名不能固定权重，与原运行期间检索并非同一次调用。直接使用官方提示词分类、按其公式单独聚合，**没有运行官方完整 extraction/update/QA CLI**；官方完整聚合还依赖 extraction 和其他分母，不能声称其已全部复现。

回答模型和评分模型均为 qwen-plus（temperature=0、max_tokens=16384），embedding 为 text-embedding-v4/1024。官方 README 只是以 gpt-4o 作配置示例，代码使用环境变量；本地文档没有确定论文评分模型的精确版本。**qwen-plus 和本地检索都是协议调整，不能宣称完全复现论文分数。**QA 回答 prompt 只由官方模板、问题和检索内容构成，参考答案、题目 evidence 和人工保护标签不输入回答模型；答案及 evidence 仅在评分时供官方评分 prompt 使用。

快照的 `created_at` 是 Mem0 实际运行时间，并非对话发生时间；沿用官方上下文格式保存该原始值，可能影响新旧状态及时间推理，不能解释为事件日期。四个会话曾有原生吞掉的操作异常并以观测检查点继续：Williams session 002、011；Martin session 006；Donald session 006。没有重放或修复这些会话，相关限制对其后快照同样适用。

小测原报告把目标数据字段 `index=2` 误写作 `memory_points[2]`；该目标实际数组下标为 **1**，新清单按完整原标注匹配，原小测报告未修改。

## 空检索、错误和人工复核

空检索 {len(emptylist)} 条，详见 `empty_retrievals.json`；当前出错或未确定阶段记录 {len(errorlist)} 条，详见 `errors.json`。另有历史 JSON 解析失败 {len(parse_failures)} 次，原始响应保存在 `parse_failures.json` 和调用记录中，补试单独计数；唯一未解析条目两次响应都含无效的 JSON 转义，未从中提取标签填分。待人工复核 {len(review)} 条，见 `MANUAL_REVIEW.md` 和 `manual_review.json`：包括非 Correct 分类、错误/未确定、无效标签，以及题目 evidence 未与原始 memory point 文本精确匹配或仅匹配后续会话等情况。精确匹配只是线索，不能证明语义来源或自动断定未来泄漏；推断需人工核对。未列入筛查清单的模型评分也没有逐一人工确认。

## 调用、延迟和费用

模型调用记录和计算详见 `summary.json`、`api_calls.jsonl`。小测 2 条及其 5 次调用原样复用，单列 pilot；本轮新增调用按 development 单列，解析失败后的补试单列 development_retry，combined 为各项之和，避免重复计数。

| 范围 | 调用尝试 | 成功 | 错误 | 在途未确定 | prompt tokens | completion tokens | total tokens | usage 缺失 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
'''
for key in ('development','development_retry','pilot','combined'):
 u=usage[key];report+=f"| {key} | {u['attempts']} | {u['successful']} | {u['errors']} | {u['unknown_started']} | {u['tokens']['prompt_tokens']} | {u['tokens']['completion_tokens']} | {u['tokens']['total_tokens']} | {u['usage_missing']} |\n"
report+='\n| 范围/阶段 | 次数 | 平均延迟秒 | 中位数秒 | P95 秒 | 最大秒 |\n|---|---:|---:|---:|---:|---:|\n'
for key,v in latency.items():report+=f"| {key} | {v['n']} | {v['mean_seconds']:.2f} | {v['median_seconds']:.2f} | {v['p95_seconds']:.2f} | {v['max_seconds']:.2f} |\n"
report+='''\n延迟为客户端单次调用耗时，包含网络等待，并发时各项耗时之和不是墙钟时间。服务响应未提供金额，本报告不推算费用；实际扣费以服务商账单为准。SDK 自动重试为 0，每次真实调用均有单条记录。\n
## 知识保护诊断（与官方评分分开）

24 项是人工选取的诊断目标，并非全部官方样本，也不是 24 次独立实验。现有 LLM 辅助诊断把 24 条分为 19 个主目标、4 条重复确认和 1 条归并；主目标核心完整保存 6/19、部分覆盖 12/19、未保存 1/19；可定位的保护候选中确认部分损伤 3/167。这些是原诊断的独立口径、尚需用户逐项复核，不进入上面的官方分母或用作模型回答输入。详见 `../williams_native_prefix5_20261028_v3/development_diagnosis_v1/NATIVE_MEM0_DIAGNOSIS.md`。\n
## 续跑

在本目录运行 `conda run --no-capture-output -n mem0_halumem python run_eval.py --workers 8`，已完成步骤不重复调用。每次调用前先落盘 started；中断时结果未知的 started 不会被自动重试，以免重复计费，须核对后单独处置。错误也不会静默重试。原输入与代码指纹变化会拒绝续跑。执行 `conda run -n mem0_halumem python export_report.py` 可重新汇总当前状态。切勿改变原库、备份或审核。\n'''
(OUT/'REPORT.md').write_text(report)
print(json.dumps(summary,ensure_ascii=False,indent=2))
