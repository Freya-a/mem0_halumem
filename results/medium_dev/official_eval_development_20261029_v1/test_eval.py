import unittest
import engine

class Tests(unittest.TestCase):
 def test_parser_is_official_strict(self):
  self.assertEqual(engine.parse_score('```json\n{"evaluation_result":"Correct"}\n```')['evaluation_result'],'Correct')
  with self.assertRaises(ValueError): engine.parse_score('{"evaluation_result":"Correct"}')
 def test_denominators_keep_failed_separate(self):
  rows=[{'retrieval':'ok','hits':[1], 'judge':'ok','label':'Correct'}, {'retrieval':'ok','hits':[], 'judge':'missing','label':None}, {'retrieval':'error','hits':None,'judge':'missing','label':None}, {'retrieval':'ok','hits':[1],'judge':'error','label':None}, {'retrieval':'ok','hits':[1],'judge':'ok','label':'Other'}]
  m=engine.metrics(rows,'update')
  self.assertEqual((m['candidates'],m['retrieved'],m['empty'],m['scoring_attempted'],m['official_all'],m['valid']), (5,4,1,3,3,2))
  self.assertEqual(m['counts']['Correct'],1)
 def test_qa_empty_still_is_official_denominator(self):
  m=engine.metrics([{'retrieval':'ok','hits':[], 'judge':'ok','label':'Correct'}], 'qa')
  self.assertEqual((m['empty'],m['official_all'],m['valid']),(1,1,1))
 def test_no_resume_of_uncertain_call(self):
  self.assertFalse(engine.may_execute('started'))
  self.assertFalse(engine.may_execute('ok'))
  self.assertFalse(engine.may_execute('error'))
  self.assertTrue(engine.may_execute(None))
 def test_answer_prompt_does_not_use_answer_or_evidence(self):
  record={'question':'Question?', 'answer':'SECRET_REFERENCE', 'evidence':[{'memory_content':'SECRET_EVIDENCE'}]}
  prompt=engine.answer_prompt('ONLY_CONTEXT',record)
  self.assertIn('Question?',prompt)
  self.assertNotIn('SECRET_REFERENCE',prompt)
  self.assertNotIn('SECRET_EVIDENCE',prompt)

 def test_pilot_is_matched_by_content_not_dataset_index_field(self):
  items=[('id','update','{"memory_point_index_zero_based": 1, "memory_point": {"index": 2, "memory_content": "tea"}}')]
  self.assertEqual(engine.find_pilot_update(items,{'index':2,'memory_content':'tea'}),'id')
