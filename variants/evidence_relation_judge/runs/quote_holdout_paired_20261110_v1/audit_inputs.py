"""Create traceable source audit from frozen prepared input and observed upstream results."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
rows=json.loads((P/'prepared.json').read_text());splitplan=json.loads((P/'split_plan.json').read_text());reviews=json.loads((P/'split_review.json').read_text()); result=[]
prior={4:'同一旧记忆曾用于拆分器 v3/v4 比较；本轮复用已保存 v4。',9:'曾列入 stage_progression 计划；是否实际运行该计划未知。',17:'曾列入 stage_progression 计划；是否实际运行该计划未知。',19:'曾列入 stage_progression 计划；是否实际运行该计划未知。',18:'与原五例 career_history 共用旧记忆 ID，但本次是更早快照的 Works...，原五例为 Previously worked...；该 ID 曾用于拆分器及判断器实验。',22:'同一会话曾作为原生 Mem0 的 D 案进行用户确认复核；不是组件一关系标签。'}
lines=['# 18 条候选逐项输入和来源核查','', '人工事实/边界为 LLM 辅助、用户确认；组件一六类关系标签均未获人工确认。旧快照是对应会话前快照，材料来源与选取路径在 [prepared.json](prepared.json)、[discovery.json](discovery.json)；文本和角色记录来自固定 HaluMem 数据集，不把自动初标作为人工结论。全部候选与原五例共用三位用户，不能称独立留出集。 用户映射：`2f1f897e-d67f-dbc5-6a7b-b7634a9e294f` = Martin Mark；`1b846c59-456e-9550-dffd-4d23f1eca81f` = Williams Daniel；`348492a7-cfe4-ee1d-73c3-c276d6ba8277` = Donald Smith。','', '前期判断器提示词调整仅涉及 7、8、10、14、24；本次 18 条不含这些会话。第 20 条归并，第 2 条因上游将 director 误写为董事长而排除；其余为助理初筛、待人工复核。先前实验的非出现性无法证实，未找到直接记录的标“未知”，不是“从未使用”。','']
for row in rows:
 n=row['number']; mems=[]
 for mem in row['old_memory_records']:
  x=dict(mem)
  if 'split_key' in mem:
   art=json.loads((P/'split_results'/f"{mem['split_key']}.json").read_text());x['split_status']=art['status'];x['split_result']=art.get('result');x['split_review']=reviews[mem['split_key']];x['split_artifact']=str(P/'split_results'/f"{mem['split_key']}.json")
  mems.append(x)
 exposure=prior.get(n,'未知；本次检索相关拆分器和判断器历史产物，未据此证明从未参与其他实验。')
 if n==23:exposure='第 22 条同样选取这两条旧记忆，但为另一新会话；与原五例共用用户。其他实验曝光未知。'
 out={'number':n,'target_id':row['target_id'],'user_uuid':row['user_uuid'],'session_index':row['session_index'],'human_review':row['human_review'],'relation_label_status':'pending_human_review','old_snapshot':row['old_snapshot'],'old_snapshot_sha256':row['old_snapshot_sha256'],'old_memories_and_splits':mems,'old_context':row['source_context'],'new_evidence':row['new_evidence'],'review_role':row.get('review_role'),'relatedness_note':row['relatedness_note'],'prior_exposure':exposure,'eligibility':('merged_excluded' if row['eligibility']=='merged_excluded' else 'input_unusable' if any(not a.get('split_review',{}).get('usable',False) for a in mems) else 'eligible')}
 result.append(out)
 human=row['human_review'];lines += [f"## {n} · {row['target_id']}",'',f"- 人工审核：{human['review_class']}；关系标签：待人工审核。",f"- 事实与边界：{human['supported_new_state']}；{human['allowed_modification_scope']}。",f"- 明确未知：{human['uncertain_current_state']}。",f"- 会话与历史：{row['relatedness_note']}；{exposure}",f"- 旧快照：`{row['old_snapshot']}`（SHA-256 `{row['old_snapshot_sha256']}`）。"]
 for mem in mems:
  lines.append(f"- 旧记忆 `{mem['id']}`：{mem['memory']}")
  if 'split_result' in mem:
   art=Path(mem['split_artifact']);lines.append(f"  - 拆分 `{mem['split_status']}`；审查：{mem['split_review']['reason']}；[原拆分记录](split_results/{art.name})。")
   for f in (mem['split_result'] or {}).get('facts',[]):lines.append(f"  - 子事实 {f['fact_index']}：`{f['raw_subfact']}`；上下文版：{f['contextualized_subfact']}；待确认：{json.dumps(f['pending_confirmations'],ensure_ascii=False)}。")
  else:lines.append('  - 未执行拆分：该行人工归并，不另计独立测试。')
 for ctx in row['source_context']:lines.append(f"- 旧上下文 `{ctx['source_id']}`（{ctx['speaker']}，记录于 {ctx['recorded_at']}，`{ctx['source_ref']}`）：{ctx['text']}")
 for ev in row['new_evidence']:lines.append(f"- 新证据 `{ev['source_id']}`（{ev['speaker']}，记录于 {ev['recorded_at']}，`{ev['source_ref']}`）：{ev['text']}")
 lines.append('')
coverage_path=P/'coverage_audit.json'
if coverage_path.exists():
 coverage={x['record']:x for x in json.loads(coverage_path.read_text())}
 for row in result:
  if row['number'] in coverage: row['eligibility']='partial_target_evidence_already_run'; row['coverage_limitation']=coverage[row['number']]
 lines+=['','## 已运行输入的事后覆盖审计','','第 3、17、18、21 条遗漏与人工确认目标有关的部分同会话来源，详见 [覆盖限制](COVERAGE_LIMITS.md)。这四条结果只对应实际发送的证据子集，不能评估完整目标；未补跑。','']
with (P/'input_audit.json').open('x',encoding='utf8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
(P/'INPUT_AUDIT.md').write_text('\n'.join(lines),encoding='utf8')
print('audited records',len(result))
