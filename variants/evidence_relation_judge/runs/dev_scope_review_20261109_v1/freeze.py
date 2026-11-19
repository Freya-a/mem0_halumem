"""Freeze read-only evaluation inputs and current code; no model or Mem0 calls."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import csv,hashlib,json,shutil

HERE=Path(__file__).resolve().parent
COMP=HERE.parent.parent
PROJ=COMP.parent.parent
SPLITTER=PROJ/'variants/dnd_mem0_splitter'

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def save(p,obj):
 with p.open('x',encoding='utf8') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')

files=[*(COMP/'part2_scope_judge').glob('*.py'),*(COMP/'part1_relation_judge').glob('*.py'),
       SPLITTER/'splitter.py',SPLITTER/'prompt_versions/v4_boundaries_20261104/prompt.txt',
       PROJ/'diagnosis/medium_dev/human_review.csv',PROJ/'diagnosis/medium_dev/human_review_summary.md',
       PROJ/'diagnosis/medium_dev/review_versions/human_review_v1_20261028/human_review.csv',
       PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_07_evidence.json',
       PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_14_evidence.json',
       PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_08_evidence.json',
       PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_10_evidence.json',
       PROJ/'results/medium_dev/williams_native_prefix5_20261028_v3/development_diagnosis_v1/target_24_evidence.json']
for name in ('promotion','skydiving','career_history'):
 files += [COMP/'runs/real_cases_20261106'/f'{name}_input.json',COMP/'runs/controlled_v2_20261106'/f'{name}_run.json',COMP/'runs/scope_v2_20261109'/('skydiving_retry.json' if name=='skydiving' else f'{name}.json'), COMP/'runs/scope_v1_20261109/replay_v2'/f'{name}.json',PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'split_result.json',PROJ/'variants/evidence_temporal_judge/runs/scope_check_20261105_v1'/name/'source_provenance.json']
root=COMP.parents[3]
facttrack=root/'external/FactTrack/fact-track/core/contradict_detector.py'; files.append(facttrack)
model=COMP/'model/Qwen3-8B'; files.extend([model/'config.json',model/'tokenizer_config.json',model/'model.safetensors.index.json',model/'generation_config.json'])
nli=COMP/'model/DeBERTa-v3-base-mnli-fever-anli';files.extend([nli/'config.json',nli/'model.safetensors'])
files=list(dict.fromkeys(files)); digest={str(p):sha(p) for p in files}
for part in ('part1_relation_judge','part2_scope_judge'):
 dest=HERE/'frozen_code'/part;dest.mkdir(parents=True,exist_ok=False)
 for p in sorted((COMP/part).glob('*.py')):shutil.copy2(p,dest/p.name)
with (PROJ/'diagnosis/medium_dev/human_review.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
assert len(rows)==24 and digest[str(PROJ/'diagnosis/medium_dev/human_review.csv')]==digest[str(PROJ/'diagnosis/medium_dev/review_versions/human_review_v1_20261028/human_review.csv')]
save(HERE/'human_review_inventory.json',{'source':str(PROJ/'diagnosis/medium_dev/human_review.csv'),'source_sha256':digest[str(PROJ/'diagnosis/medium_dev/human_review.csv')],
 'method':'LLM辅助、用户确认；确认数据与证据边界，不等于独立金标或系统运行结果','count':len(rows),'rows':[{'number':i,**r} for i,r in enumerate(rows,1)]})
save(HERE/'manifest_before.json',{'created_at':datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'purpose':'small read-only judge evaluation; no Mem0 writes',
 'sha256':digest,'qwen_weight_files':{p.name:{'bytes':p.stat().st_size,'sha256':'not calculated in this freeze'} for p in sorted(model.glob('model-*.safetensors'))},
 'qwen_model_path':str(model),'nli_model_path':str(nli),'facttrack':str(facttrack),
 'target_selection':{'reused_existing_v4_v2':{'8':'skydiving','10':'promotion','24':'career_history'},
   'new_upstream_small_run':{'7':'job_transition','14':'persian_cats'},
   'reason':'select user-reviewed modification/protection scope with verified before memory; reuse all matching saved v4/v2, then two other confirmed events with old before text but no matching saved v4/v2'}})
print('frozen',len(files),'source items and',len(rows),'full review rows; weights sizes recorded without full hashes')
