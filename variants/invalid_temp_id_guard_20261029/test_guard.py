import json
import pathlib
import unittest
import guard

ROOT=pathlib.Path('/home/shu1004/ld/system/mem0_halumem_diagnosis')
RUN=ROOT/'results/medium_dev/five_case_simple_prompt_direct_20261029_v2/cases'

class GuardTests(unittest.TestCase):
    def test_real_recorded_invalid_ids_are_rejected_before_any_plan_is_returned(self):
        for label, invalid in [('B',{'44','45'}),('C',{'62'}),('target_10',{'43'})]:
            io=json.loads((RUN/label/'update_model_io.json').read_text())
            model_input=next(x for x in io if x['kind']=='model_input')
            model_output=next(x for x in io if x['kind']=='model_output')
            with self.subTest(label=label):
                errors=guard.validate_plan(model_output['raw_response'],model_input['native_temp_uuid_mapping'])
                self.assertEqual({x['id'] for x in errors if x['reason']=='unknown_id'},invalid)

    def test_valid_plan_is_returned_without_retry(self):
        raw=json.dumps({'memory':[{'id':'0','event':'UPDATE','text':'new'}, {'id':'fresh','event':'ADD','text':'added'}]})
        calls=[]
        result=guard.resolve_plan(raw,{'0':'uuid'},lambda messages: calls.append(messages),[{'role':'user','content':'original'}])
        self.assertEqual(result,raw); self.assertEqual(calls,[])

    def test_invalid_plan_retries_once_and_accepts_valid_return(self):
        invalid=json.dumps({'memory':[{'id':'44','event':'UPDATE','text':'new'}]})
        valid=json.dumps({'memory':[{'id':'0','event':'UPDATE','text':'new'}]})
        calls=[]
        def retry(messages): calls.append(messages); return valid
        self.assertEqual(guard.resolve_plan(invalid,{'0':'uuid'},retry,[{'role':'user','content':'original'}]),valid)
        self.assertEqual(len(calls),1); self.assertIn('44',calls[0][-1]['content']); self.assertIn('0',calls[0][-1]['content'])

    def test_second_invalid_plan_fails_closed(self):
        invalid=json.dumps({'memory':[{'id':'44','event':'UPDATE','text':'new'}]})
        calls=[]
        with self.assertRaises(guard.InvalidUpdatePlan):
            guard.resolve_plan(invalid,{'0':'uuid'},lambda messages:(calls.append(messages) or invalid),[{'role':'user','content':'original'}])
        self.assertEqual(len(calls),1)

    def test_bad_json_bad_events_and_unmapped_delete_fail_closed(self):
        for raw in ['broken','{}',json.dumps({'memory':[{'id':'7','event':'DELETE','text':'x'}]}),json.dumps({'memory':[{'id':'0','event':'REPLACE','text':'x'}]})]:
            with self.subTest(raw=raw): self.assertTrue(guard.validate_plan(raw,{'0':'uuid'}))

class IntegrationGuardTests(unittest.TestCase):
    class FakeLLM:
        def __init__(self, responses): self.responses=iter(responses); self.calls=[]
        def generate_response(self, **kwargs):
            self.calls.append(kwargs)
            result=next(self.responses)
            if isinstance(result,Exception): raise result
            return result
    class FakeNativeMemory:
        enable_graph=False
        def __init__(self, responses): self.llm=IntegrationGuardTests.FakeLLM(responses); self.writes=[]
        def _add_to_vector_store(self):
            self.llm.generate_response(messages=[{'role':'user','content':'extract'}])
            temp_uuid_mapping={'0':'uuid'}
            try: raw=self.llm.generate_response(messages=[{'role':'user','content':'update'}],response_format={'type':'json_object'})
            except Exception: raw=''
            for action in json.loads(raw or '{"memory":[]}')['memory']:
                self.writes.append(action)
            return {'results':self.writes}
        def add(self,messages,**kwargs): return self._add_to_vector_store()
    def test_rejection_propagates_through_native_exception_handler_without_any_writes(self):
        bad=json.dumps({'memory':[{'event':'ADD','id':'new','text':'new'}, {'event':'UPDATE','id':'44','text':'wrong'}]})
        memory=self.FakeNativeMemory(['facts',bad,bad]); events=[]
        with self.assertRaises(guard.InvalidUpdatePlan): guard.guarded_add(memory,[],audit=events.append)
        self.assertEqual(memory.writes,[]); self.assertEqual(len(memory.llm.calls),3)
    def test_valid_retry_passes_complete_plan_to_native(self):
        bad=json.dumps({'memory':[{'event':'UPDATE','id':'44','text':'wrong'}]})
        good=json.dumps({'memory':[{'event':'UPDATE','id':'0','text':'right'}]})
        memory=self.FakeNativeMemory(['facts',bad,good]); events=[]
        result=guard.guarded_add(memory,[],audit=events.append)
        self.assertEqual(result['results'][0]['id'],'0'); self.assertEqual(len(events),3)
    def test_update_transport_failure_propagates_through_native_handler(self):
        memory=self.FakeNativeMemory(['facts',ConnectionError('offline')]); events=[]
        with self.assertRaises(guard.InvalidUpdatePlan): guard.guarded_add(memory,[],audit=events.append)
        self.assertEqual(memory.writes,[])

class RealNativeIntegrationTests(unittest.TestCase):
    def test_real_native_execution_writes_nothing_if_corrected_plan_still_invalid(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from mem0.memory.main import Memory
        bad=json.dumps({'memory':[{'event':'ADD','id':'fresh','text':'new'}, {'event':'UPDATE','id':'44','text':'wrong'}]})
        llm=IntegrationGuardTests.FakeLLM([json.dumps({'facts':['fact']}),bad,bad])
        class NativeHarness:
            enable_graph=False
            api_version='v1.1'
            config=SimpleNamespace(custom_fact_extraction_prompt=None,custom_update_memory_prompt=None)
            vector_store=SimpleNamespace(search=lambda **kw: [SimpleNamespace(id='uuid',payload={'data':'old'})])
            embedding_model=SimpleNamespace(embed=lambda *a,**kw: [0.1])
            def __init__(self): self.llm=llm;self.writes=[]
            def _create_memory(self,*a,**kw): self.writes.append(('ADD',kw));return 'created'
            def _update_memory(self,*a,**kw): self.writes.append(('UPDATE',kw))
            def _delete_memory(self,*a,**kw): self.writes.append(('DELETE',kw))
            def add(self,messages,**kw): return Memory._add_to_vector_store(self,messages,{}, {'user_id':'u'},True)
        memory=NativeHarness()
        with patch('mem0.memory.main.capture_event'):
            with self.assertRaises(guard.InvalidUpdatePlan): guard.guarded_add(memory,[{'role':'user','content':'test'}],audit=lambda e:None)
        self.assertEqual(memory.writes,[])
        self.assertEqual(len(llm.calls),3)

    def test_real_native_execution_uses_corrected_valid_id(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        from mem0.memory.main import Memory
        bad=json.dumps({'memory':[{'event':'UPDATE','id':'44','text':'new'}]})
        good=json.dumps({'memory':[{'event':'UPDATE','id':'0','text':'new'}]})
        llm=IntegrationGuardTests.FakeLLM([json.dumps({'facts':['fact']}),bad,good])
        class NativeHarness:
            enable_graph=False
            api_version='v1.1'
            config=SimpleNamespace(custom_fact_extraction_prompt=None,custom_update_memory_prompt=None)
            vector_store=SimpleNamespace(search=lambda **kw: [SimpleNamespace(id='real-uuid',payload={'data':'old'})])
            embedding_model=SimpleNamespace(embed=lambda *a,**kw: [0.1])
            def __init__(self): self.llm=llm;self.writes=[]
            def _update_memory(self,**kw): self.writes.append(kw)
            def add(self,messages,**kw): return Memory._add_to_vector_store(self,messages,{}, {'user_id':'u'},True)
        memory=NativeHarness()
        with patch('mem0.memory.main.capture_event'):
            result=guard.guarded_add(memory,[{'role':'user','content':'test'}],audit=lambda e:None)
        self.assertEqual(memory.writes[0]['memory_id'],'real-uuid')
        self.assertEqual(result[0]['id'],'real-uuid')
        self.assertEqual(len(llm.calls),3)

if __name__=='__main__': unittest.main()
