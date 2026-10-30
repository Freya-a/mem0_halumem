import json, os, pathlib, sys, tempfile, unittest
from unittest.mock import patch
from types import SimpleNamespace
ROOT=pathlib.Path('/home/shu1004/ld/system/mem0_halumem_diagnosis')
sys.path.insert(0,str(ROOT/'scripts'))
import guard, observer_guard

class FakeLLM:
 def __init__(self,replies): self.replies=iter(replies)
 def generate_response(self,**kw): return next(self.replies)

class ObserverIntegrationTest(unittest.TestCase):
 def test_native_retry_observed_as_update_with_real_mapping_and_final_plan(self):
  from mem0.memory.main import Memory
  bad=json.dumps({'memory':[{'id':'44','event':'UPDATE','text':'new'}]})
  good=json.dumps({'memory':[{'id':'0','event':'UPDATE','text':'new'}]})
  class Point:
   id='uuid';payload={'data':'old'}
   def model_dump(self,mode='json'):return {'id':self.id,'payload':self.payload}
  class Harness:
   enable_graph=False; api_version='v1.1'; config=SimpleNamespace(custom_fact_extraction_prompt=None,custom_update_memory_prompt=None)
   def __init__(self):
    self.llm=FakeLLM([json.dumps({'facts':['test']}),bad,good]); self.writes=[]
    self.embedding_model=SimpleNamespace(embed=lambda *a,**kw: [0.1])
    self.vector_store=SimpleNamespace(search=lambda **kw:[Point()])
   def _create_memory(self,*a,**kw): self.writes.append(('ADD',kw));return 'new-id'
   def _update_memory(self,**kw): self.writes.append(('UPDATE',kw));return None
   def _delete_memory(self,*a,**kw): self.writes.append(('DELETE',kw));return None
   def add(self,messages,**kw): return Memory._add_to_vector_store(self,messages,{}, {'user_id':'u'},True)
  with tempfile.TemporaryDirectory() as tmp:
   mem=Harness(); obs=observer_guard.GuardObserver(pathlib.Path(tmp)); obs.phase='case'; obs.install(mem)
   with patch('mem0.memory.main.capture_event'):
    ret=guard.guarded_add(mem,[{'role':'user','content':'test'}],audit=lambda event:obs.emit('guard_audit',**event))
   result=observer_guard.derive(pathlib.Path(tmp),obs)
   self.assertEqual([x['stage'] for x in obs.entries if x['kind']=='model_input'],['extraction','update','update'])
   self.assertEqual(result['valid_ids'],['0']); self.assertEqual(result['initial_invalid_ids'],['44']);self.assertTrue(result['retry_triggered'])
   self.assertEqual(result['final_plan_counts'],{'UPDATE':1}); self.assertEqual(ret[0]['id'],'uuid')
   self.assertEqual(mem.writes[0][1]['memory_id'],'uuid')

if __name__=='__main__':unittest.main()
