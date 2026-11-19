"""Collect existing v2 results without assigning semantic truth labels."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
LOCAL=ROOT/'runs/erase_style_comparison_20261110_v1/A_v2'
CLOUD=ROOT/'runs/qwen_plus_v2_diagnosis_20261110_v1'
NAMES=['job_transition','persian_cats','skydiving','career_history','promotion']
result={}
for name in NAMES:
    row={}
    for tag,base in [('qwen3_8b',LOCAL),('qwen_plus',CLOUD),('qwen35_27b_q4',HERE)]:
        path=base/f'{name}.json'
        if not path.exists():
            row[tag]={'status':'not_run'}
            continue
        data=json.loads(path.read_text(encoding='utf-8'))
        item=data['result']['results'][0]
        c=item.get('candidate') or {}
        if not isinstance(c,dict): c={}
        row[tag]={'status':item['status'],'relation':c.get('relation'),'fragment':c.get('candidate_impact_fragment'),'new_quote':c.get('new_quote'),'reason':c.get('reason'),'confirmation_questions':c.get('confirmation_questions'),'validation':item.get('validation'),'errors':item.get('errors'),'source':str(path)}
    result[name]=row
with (HERE/'comparison.json').open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
