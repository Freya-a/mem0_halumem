import json, os, sys, time, traceback, datetime
from pathlib import Path

out = Path(__file__).resolve().parent
model_dir = Path('/home/shu1004/ld/system/mem0_halumem_diagnosis/variants/evidence_relation_judge/model/DeBERTa-v3-base-mnli-fever-anli')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
config = json.loads((model_dir/'config.json').read_text(encoding='utf-8'))
examples = [
 {'id':'support_1','category':'明确支持','premise':'Alice owns a red bicycle.','hypothesis':'Alice owns a bicycle.','expected':'entailment','reason':'拥有红色自行车蕴含拥有自行车。'},
 {'id':'support_2','category':'明确支持','premise':'The package was delivered on Monday.','hypothesis':'The package has been delivered.','expected':'entailment','reason':'周一送达蕴含已经送达。'},
 {'id':'contradiction_1','category':'明确矛盾','premise':'The light is on.','hypothesis':'The light is not on.','expected':'contradiction','reason':'同一状态的肯定和否定不能同时成立。'},
 {'id':'contradiction_2','category':'明确矛盾','premise':'No dogs are allowed inside the museum.','hypothesis':'Dogs are allowed inside the museum.','expected':'contradiction','reason':'明确禁止与允许的表述相矛盾。'},
 {'id':'unrelated_1','category':'无明显关系','premise':'The chef is cooking dinner.','hypothesis':'The train arrives at noon.','expected':'neutral','reason':'烹饪晚餐不能确定火车何时到站。'},
 {'id':'unrelated_2','category':'无明显关系','premise':'Sarah bought a blue notebook.','hypothesis':'The weather will be rainy tomorrow.','expected':'neutral','reason':'购买笔记本与明日天气没有给出可推导的关系。'},
 {'id':'temporal_1','category':'过去和现在状态变化','premise':'In 2020, Maya lived in Boston.','hypothesis':'In 2024, Maya lived in Seattle.','expected':'neutral','reason':'2020 年居住地不能确定 2024 年居住地，两条可在不同时间同时为真；需要时间信息才能判断记忆状态。'},
 {'id':'temporal_2','category':'过去和现在状态变化','premise':'In 2020, Daniel was single.','hypothesis':'Daniel is married now.','expected':'neutral','reason':'过去单身与现在结婚可以先后成立，过去的状态不确定当前状态；不能据 NLI 判定旧记忆失效。'},
]
record={'model_dir':str(model_dir),'revision':'6f5cf0a2b59cabb106aca4c287eed12e357e90eb','config_id2label':config['id2label'],'config_label2id':config['label2id'],'cases':examples,'status':'started','attempted_forward_passes':0,'completed_forward_passes':0,'offline':True,'started_at':datetime.datetime.now().astimezone().isoformat()}
def save():
 with (out/'results.json').open('w',encoding='utf-8') as f: json.dump(record,f,ensure_ascii=False,indent=2)
save()
start=time.perf_counter()
try:
 import torch, transformers, tokenizers, sentencepiece, safetensors
 from transformers import AutoTokenizer, AutoModelForSequenceClassification
 record['versions']={'python':sys.version.split()[0],'torch':torch.__version__,'transformers':transformers.__version__,'tokenizers':tokenizers.__version__,'sentencepiece':sentencepiece.__version__,'safetensors':safetensors.__version__}
 device=torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
 record['device']=str(device); record['dtype']='float32'
 if device.type=='cuda':
  torch.cuda.synchronize(device)
  record['device_name']=torch.cuda.get_device_name(device)
  free,total=torch.cuda.mem_get_info(device); record['gpu_before']={'free_bytes':free,'total_bytes':total,'allocated_bytes':torch.cuda.memory_allocated(device),'reserved_bytes':torch.cuda.memory_reserved(device)}
  torch.cuda.reset_peak_memory_stats(device)
 save()
 load_start=time.perf_counter()
 tokenizer=AutoTokenizer.from_pretrained(str(model_dir),local_files_only=True)
 model=AutoModelForSequenceClassification.from_pretrained(str(model_dir),local_files_only=True, dtype=torch.float32, use_safetensors=True)
 model.to(device); model.eval()
 if device.type=='cuda': torch.cuda.synchronize(device)
 record['load_seconds']=time.perf_counter()-load_start
 if device.type=='cuda':
  free,total=torch.cuda.mem_get_info(device); record['gpu_after_load']={'free_bytes':free,'total_bytes':total,'allocated_bytes':torch.cuda.memory_allocated(device),'reserved_bytes':torch.cuda.memory_reserved(device)}
 save()
 for case in examples:
  inputs=tokenizer(case['premise'],case['hypothesis'],return_tensors='pt',truncation=True).to(device)
  if device.type=='cuda': torch.cuda.synchronize(device)
  t=time.perf_counter(); record['attempted_forward_passes']+=1; save()
  with torch.inference_mode(): logits=model(**inputs).logits[0]
  if device.type=='cuda': torch.cuda.synchronize(device)
  elapsed=time.perf_counter()-t
  probs=torch.softmax(logits.float(),dim=-1)
  case['logits']={config['id2label'][str(i)]:float(v) for i,v in enumerate(logits.tolist())}
  case['softmax_scores']={config['id2label'][str(i)]:float(v) for i,v in enumerate(probs.tolist())}
  case['predicted_id']=int(probs.argmax().item()); case['predicted_label']=config['id2label'][str(case['predicted_id'])]
  case['forward_seconds']=elapsed; case['matches_expected']=case['predicted_label']==case['expected']
  case['manual_review_required']=case['category']=='过去和现在状态变化' or not case['matches_expected']
  record['completed_forward_passes']+=1; save(); print(case['id'],case['predicted_label'],case['softmax_scores'],flush=True)
 if device.type=='cuda':
  free,total=torch.cuda.mem_get_info(device)
  record['gpu_end']={'free_bytes':free,'total_bytes':total,'allocated_bytes':torch.cuda.memory_allocated(device),'reserved_bytes':torch.cuda.memory_reserved(device),'peak_allocated_bytes':torch.cuda.max_memory_allocated(device),'peak_reserved_bytes':torch.cuda.max_memory_reserved(device)}
 record['status']='completed'
except Exception:
 record['status']='failed'; record['error']=traceback.format_exc(); print(record['error'],file=sys.stderr,flush=True)
finally:
 record['total_seconds']=time.perf_counter()-start
 record['finished_at']=datetime.datetime.now().astimezone().isoformat()
 save()
if record['status']!='completed': sys.exit(1)
