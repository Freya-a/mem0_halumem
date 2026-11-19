import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
PLANNER=HERE.parents[1]/'part2_scope_planner'
sys.path.insert(0,str(PLANNER))
sys.path.insert(0,str(HERE))
import plan_experimental as experimental
import plan as original

class EvidenceInventoryTests(unittest.TestCase):
 def case(self,name): return json.loads((HERE/'cases'/name/'input.json').read_text())
 def test_all_input_evidence_is_visible_with_no_claim_of_link_or_novelty(self):
  case=self.case('skydiving'); p=experimental.build_plan(case['request'],case['manual_relation_result'],case['manual_annotations'])
  self.assertIn('new_evidence_inventory',p)
  inv=p['new_evidence_inventory']
  self.assertEqual([x['source_id'] for x in inv],['new-0','new-2','new-8'])
  self.assertEqual([x['text'] for x in inv],[x['text'] for x in case['request']['new_evidence']])
  self.assertTrue(all(x['independent_fact_verified'] is False and x['old_fact_relation_verified'] is False for x in inv))
  self.assertEqual([x['referenced_by_upstream'] for x in inv],[True,False,False])
 def test_existing_categories_do_not_change(self):
  case=self.case('career_history'); args=(case['request'],case['manual_relation_result'],case['manual_annotations'])
  before=original.build_plan(*args); after=experimental.build_plan(*args)
  for key in before: self.assertEqual(after[key],before[key],key)
 def test_invalid_upstream_does_not_turn_inventory_into_validated_relation(self):
  case=self.case('susan');case['manual_relation_result']['results'][0]['status']='error'
  p=experimental.build_plan(case['request'],case['manual_relation_result'],case['manual_annotations'])
  self.assertFalse(p['modify'])
  self.assertIn('new_evidence_inventory',p)
  self.assertTrue(all(not x['referenced_by_validated_upstream'] for x in p['new_evidence_inventory']))

if __name__=='__main__': unittest.main()
