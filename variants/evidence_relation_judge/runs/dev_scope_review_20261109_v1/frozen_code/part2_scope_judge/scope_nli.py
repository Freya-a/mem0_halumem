"""Optional, offline DeBERTa NLI; scores are audit signals, never decisions."""
from pathlib import Path
import hashlib

MODEL = Path(__file__).resolve().parent.parent / 'model/DeBERTa-v3-base-mnli-fever-anli'
REVISION = '6f5cf0a2b59cabb106aca4c287eed12e357e90eb'
EXPECTED_WEIGHTS_SHA256 = '06d6fd89edd4f97816831626daafbdb0b029cf63bae8edc0bccab1d64e2e7707'

class LocalNLI:
    def __init__(self, model_dir=MODEL, device=None):
        self.model_dir=Path(model_dir); self.device_name=device
        self.model=None; self.error=None

    def load(self):
        if self.model is not None: return
        if self.error: raise RuntimeError(self.error)
        try:
            import torch, transformers
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            self.torch=torch
            self.versions={'torch':torch.__version__, 'transformers':transformers.__version__}
            self.device=self.device_name or ('cuda:0' if torch.cuda.is_available() else 'cpu')
            self.tokenizer=AutoTokenizer.from_pretrained(str(self.model_dir),local_files_only=True)
            model=AutoModelForSequenceClassification.from_pretrained(str(self.model_dir),local_files_only=True, dtype=torch.float32, use_safetensors=True)
            model.to(self.device); model.eval(); self.model=model
            h=hashlib.sha256()
            with (self.model_dir/'model.safetensors').open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
            self.weight_sha256=h.hexdigest()
        except Exception as exc:
            self.error=f'{type(exc).__name__}: {exc}'
            raise

    def __call__(self, premise, hypothesis):
        self.load()
        raw=self.tokenizer(premise,hypothesis,add_special_tokens=True,truncation=False)
        original_tokens=len(raw['input_ids']); limit=int(self.model.config.max_position_embeddings)
        encoded=self.tokenizer(premise,hypothesis,return_tensors='pt',truncation=True,max_length=limit).to(self.device)
        with self.torch.inference_mode(): logits=self.model(**encoded).logits[0].float()
        scores=self.torch.softmax(logits,dim=-1)
        labels=self.model.config.id2label
        logits_dict={str(labels[i]):float(x) for i,x in enumerate(logits.tolist())}
        scores_dict={str(labels[i]):float(x) for i,x in enumerate(scores.tolist())}
        return {'premise':premise,'hypothesis':hypothesis,'input_order':'old contextualized subfact -> v2 new quote',
                'model_dir':str(self.model_dir),'revision':'verified historical download '+REVISION,
                'weights_sha256':self.weight_sha256,'weights_match_recorded_revision':self.weight_sha256==EXPECTED_WEIGHTS_SHA256,
                'versions':self.versions,'device':self.device,'dtype':'float32','original_tokens':original_tokens,
                'max_tokens':limit,'truncated':original_tokens>limit,'logits':logits_dict,'softmax_scores':scores_dict,
                'predicted_label':max(scores_dict,key=scores_dict.get),
                'use':'exploratory scoring of unverified v2 pair; no effect on boundary or plan'}
