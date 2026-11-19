"""List already user-confirmed boundaries outside the five sessions; do not infer labels."""
import hashlib,json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'runs/dev_scope_review_20261109_v1/human_review_inventory.json'
source=json.loads(SOURCE.read_text(encoding='utf-8'))
original=ROOT.parents[1]/'diagnosis/medium_dev/human_review.csv'
sha=hashlib.sha256(original.read_bytes()).hexdigest()
if sha!=source['source_sha256']: raise RuntimeError('frozen review source hash mismatch')
rows=source['rows']; numbers={7,8,10,14,24}
used={r['session_group_id'] for r in rows if r['number'] in numbers}
candidates=[r for r in rows if r['number'] not in numbers and r['session_group_id'] not in used]
same=[r for r in rows if r['number'] not in numbers and r['session_group_id'] in used]
if len(candidates)!=18 or any(r['reviewer']!='user' for r in candidates): raise RuntimeError('unexpected review scope')
keys=['number','target_id','session_group_id','reviewer','review_method','review_class','supported_new_state','allowed_modification_scope','uncertain_current_state','diagnostic_use','runtime_verification_status','annotation_json_pointer']
result={'source_inventory':str(SOURCE),'original_review_csv':str(original),'original_review_sha256':sha,'selection':'exclude the five target IDs and every record sharing their user/session group','excluded_five_numbers':sorted(numbers),'same_session_excluded_numbers':[x['number'] for x in same],'count':len(candidates),'distinct_session_groups':len({r['session_group_id'] for r in candidates}),'review_class_counts':dict(Counter(r['review_class'] for r in candidates)),'scope':'LLM-assisted, user-confirmed facts and evidence/update boundaries; not independent blind relationship labels or verified component-one outcomes','prior_exposure':'not used for this five-case prompt adjustment; prior research and shared users may have exposed some cases, so not a blind holdout','readiness':'candidate target rows only; verify exact before memory, evidence and compatible component-one input before future testing','rows':[{k:r.get(k) for k in keys} for r in candidates]}
for row in result['rows']:
 if row['number']==22:
  row['additional_review']={'type':'LLM辅助、用户确认的既有原生运行 D 案','conclusion':'无效临时ID导致计划操作被跳过，目标新事实未找到；不是旧知识损伤结论，也不是组件一关系标签。','source':'results/medium_dev/human_review_packets/native_case_review_v1_20261028/README.md'}
with (HERE/'holdout_inventory.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
def cell(s): return str(s or '未记录').replace('|','\\|').replace('\n',' ')
lines=['# 已确认事实边界的后续候选清单','',f"来源冻结人工审核记录，原 CSV SHA-256：`{sha}`。审核方式是 LLM 辅助、用户确认事实与更新边界；不是组件一六类标签盲标。",'',f"排除本次五条目标 7、8、10、14、24，并进一步排除与晋升同会话的第 11 条；剩余 **{len(candidates)} 条，{result['distinct_session_groups']} 个用户会话**：13 条接受/修订后接受主目标、4 条重复确认、1 条归并。重复项与归并项不得当独立新增事实或独立样本累计。",'', '这些仅表示未参与本次五例提示调整，不等于从未参加其他实验；部分共用用户、同一会话或主题。第 9、17、19 条曾列入其他实验计划，不能假定完全未曝光。构造后续评测前，须逐条核实共同 before 中实际旧记忆、证据来源与 component-one 输入；本次未运行它们。源表的 `待运行核验` 是原始记录状态，不排除其他实验曾研究同一目标。','', '|序号|目标 ID|人工审核状态|已确认的新内容|允许范围与未知|','|---:|---|---|---|---|']
for r in candidates:
 lines.append(f"|{r['number']}|`{cell(r['target_id'])}`|{cell(r['review_class'])}|{cell(r['supported_new_state'])}|{cell(r['allowed_modification_scope'])} 未知：{cell(r['uncertain_current_state'])}|")
lines+=['','对应完整记录、时间、逐字证据指针和原用户结论见 [冻结审核清单](../dev_scope_review_20261109_v1/human_review_inventory.json) 与 [原始审核 CSV](../../../../diagnosis/medium_dev/human_review.csv)；自动初标不计作人工确认。']
lines+=['','第 22 条还有独立于上述数据边界审核的 [原生运行 D 案用户确认记录](../../../../results/medium_dev/human_review_packets/native_case_review_v1_20261028/README.md)：既有运行因无效临时 ID 跳过计划操作、未找到目标新事实；这不是组件一关系标签或本实验结果，也不能因此假定其他旧内容均无损伤。']
(HERE/'HOLDOUT_INVENTORY.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'count':len(candidates),'sessions':result['distinct_session_groups'],'classes':result['review_class_counts'],'same_session_excluded':result['same_session_excluded_numbers']},ensure_ascii=False))
