import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'part1_relation_judge'))
sys.path.insert(0,str(HERE))
import relation_judge_v2 as v2
import experimental_judge as experiment

BASE=ROOT/'runs/qwen35_27b_q4_v2_20261110_v1/promotion.json'

class SourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=json.loads(BASE.read_text(encoding='utf-8'))
    def evaluate(self, answer, data=None):
        return experiment.judge(deepcopy(data or self.baseline['input']),lambda _:json.dumps(answer,ensure_ascii=False))
    def test_prompt_extends_original_without_changing_labels_or_validator(self):
        self.assertTrue(experiment.SYSTEM.startswith(v2.SYSTEM))
        self.assertGreater(len(experiment.SYSTEM),len(v2.SYSTEM))
        self.assertIs(experiment.judge,v2.judge)
        self.assertEqual(experiment.LABELS,v2.LABELS)
    def test_context_quote_still_fails_without_modification(self):
        c=self.baseline['result']['results'][0]['candidate']
        result=self.evaluate(c)['results'][0]
        self.assertEqual(result['candidate']['old_quote'],c['old_quote'])
        self.assertEqual(result['errors'][0]['message'],'old_quote not found in this fact memory evidence')
        self.assertEqual(result['status'],'error')
    def test_memory_quote_passes_identical_validator(self):
        c=deepcopy(self.baseline['result']['results'][0]['candidate'])
        c['old_quote']=self.baseline['input']['split_result']['facts'][0]['evidence'][0]['quote']
        row=self.evaluate(c)['results'][0]
        self.assertEqual(row['status'],'ok')
        self.assertTrue(row['validation']['passed'])
        self.assertEqual(row['validation']['semantic_correctness'],'not_checked')
    def test_request_without_memory_evidence_fails_before_call(self):
        data=deepcopy(self.baseline['input'])
        data['split_result']['facts'][0]['evidence']=[e for e in data['split_result']['facts'][0]['evidence'] if e['source_type']=='context']
        called=[]
        result=experiment.judge(data,lambda p:called.append(p))
        self.assertEqual(result['status'],'input_error')
        self.assertEqual(called,[])

if __name__=='__main__': unittest.main()
