"""Present all 24 existing human-review rows without changing their status."""
from pathlib import Path
import collections,json
HERE=Path(__file__).resolve().parent
value=json.loads((HERE/'human_review_inventory.json').read_text(encoding='utf8'))
rows=value['rows']
classes=collections.Counter(x['review_class'] for x in rows)
main=[x for x in rows if x['review_class'] in ('接受','修订后接受')]

def clean(x):return (x or '未记录').replace('|','\\|').replace('\n','<br>')
out=['# 开发子集：24 条已确认审核记录清单','',
 '审核方法为 LLM 辅助、用户确认；确认的是资料与目标边界，并非独立盲审、系统效果或模型输出正确性。24 是审核行数。',
 f"分类：{dict(classes)}；接受/修订接受主目标 {len(main)} 条、覆盖 {len({x['session_group_id'] for x in main})} 个不同用户会话；全部 24 条覆盖 {len({x['session_group_id'] for x in rows})} 个不同用户会话。不是独立实验数。",'',
 '完整原始列（包括精确引文、保护候选、用户原结论、时间和来源）见 `human_review_inventory.json`；下表逐项保留审核分类、受支持的新内容、允许的修改范围、明确未知项。`未记录` 不等于不存在。', '',
 '|序号 / target_id|人工分类|受支持的新内容|允许修改范围|明确未知|', '|---|---|---|---|---|']
for r in rows:
 out.append('|'+str(r['number'])+' / '+clean(r['target_id'])+'|'+clean(r['review_class'])+'|'+clean(r['supported_new_state'])+'|'+clean(r['allowed_modification_scope'])+'|'+clean(r['uncertain_current_state'])+'|')
out+=['','注意：第 7、10 项是经前快照核实旧当前状态后的时间状态替换候选；第 24 项默认不是严格纠错，不能从获客计划推导“尚未获客”。重复确认和归并项不能重复计入新增语义。',
 '第 15 项新人脉补充边界仍未固定；第 20 项方法计划是关联子目标。所有保护候选是否在共同 before 中完整前存仍须核实。','','更正既有汇总的分母：19 个主目标按逐项 `session_group_id` 为 15 个不同用户会话；全部 24 条为 16 个会话。参见已有 `kpr_jsr_reconciliation_20261030_v1/REPORT.md`。']
with (HERE/'HUMAN_REVIEW_INVENTORY.md').open('x',encoding='utf8') as f:f.write('\n'.join(out)+'\n')
print('review rows',len(rows),'main',len(main),'main sessions',len({x['session_group_id'] for x in main}),'all sessions',len({x['session_group_id'] for x in rows}))
