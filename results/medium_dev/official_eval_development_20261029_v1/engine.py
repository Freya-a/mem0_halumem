import sys, re, json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'HaluMem/eval'))
from prompts import PROMPT_MEMZERO

def parse_score(text):
 m=re.search(r'```json\s*(\{.*?\})\s*```',text,re.DOTALL)
 if not m: raise ValueError('No JSON block found in model output')
 return json.loads(m.group(1).strip())

def may_execute(status):return status is None

def answer_prompt(context,qa):return PROMPT_MEMZERO.format(context=context,question=qa['question'])

def metrics(rows,kind):
 labels=['Correct','Hallucination','Omission']+(['Other'] if kind=='update' else [])
 if kind=='update': eligible=[r for r in rows if r['retrieval']=='ok' and bool(r['hits'])]
 else: eligible=list(rows)
 valid=[r for r in eligible if r['judge']=='ok' and r['label'] in labels]
 counts=Counter(r['label'] for r in valid)
 return {'candidates':len(rows),'retrieved':sum(r['retrieval']=='ok' for r in rows),'empty':sum(r['retrieval']=='ok' and not r['hits'] for r in rows),'retrieval_failed_or_unknown':sum(r['retrieval']!='ok' for r in rows),'scoring_attempted':sum(r['judge'] in ('ok','error','started') for r in rows),'scoring_completed':sum(r['judge']=='ok' for r in rows),'official_all':len(eligible),'valid':len(valid),'counts':{k:counts[k] for k in labels},'ratio_all':{k:counts[k]/len(eligible) if eligible else None for k in labels},'ratio_valid':{k:counts[k]/len(valid) if valid else None for k in labels}}

def find_pilot_update(items,source):
 matches=[i for i,k,s in items if k=='update' and json.loads(s)['memory_point']==source]
 if len(matches)!=1:raise ValueError('Pilot update must match exactly one original source')
 return matches[0]
