"""V3 relation prompt: generic stage disambiguation, retaining v2 output contract."""
import relation_judge_v2 as v2
from run_local import LocalQwen
import json
import time

SYSTEM=v2.SYSTEM+'''
阶段消歧：判断当前阶段是否沿用，而非某个目标过去是否有合理性。若来源支持同一对象、同一事项从待办、计划、申请或进行中发展到已经完成、获批或转为后续阶段，不能仅因目标实现就标 support；优先 possible_change，若同一事项或完成状态无法确认则 uncertain。相同主体不等于同一事项，相似词不等于互斥；事件仍在筹划或可能发生不能当已完成。一次体验加深原有爱好可以是 supplement，不等于旧喜好失效。保留旧事实的历史和未受影响条件；记录时间不是事件发生时间。以上均为语义候选，不是事实判决。'''


def judge(data,backend):
    """Use the v2 parser/validator; backend must use SYSTEM and return raw JSON."""
    return v2.judge(data,backend)


class LocalQwenV3(LocalQwen):
    def __call__(self,payload):
        self.load();torch=self.torch
        messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}]
        self.messages.append(messages)
        rendered=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
        inputs=self.tokenizer(rendered,return_tensors='pt').to('cuda:0');t=time.perf_counter()
        record={'seconds':None,'output_tokens':None,'terminated_at_eos':False,'raw_output':None,'error':None}
        self.metrics['generations'].append(record);self.metrics['model_calls']+=1
        try:
            with torch.inference_mode():output=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,do_sample=False,pad_token_id=self.tokenizer.eos_token_id)
            tokens=output[0,inputs['input_ids'].shape[1]:]
            record['output_tokens']=len(tokens);record['terminated_at_eos']=bool(len(tokens) and tokens[-1].item()==self.tokenizer.eos_token_id)
            record['raw_output']=self.tokenizer.decode(tokens,skip_special_tokens=True)
            return record['raw_output']
        except Exception as exc:
            record['error']=f'{type(exc).__name__}: {exc}';raise
        finally:record['seconds']=round(time.perf_counter()-t,3)
