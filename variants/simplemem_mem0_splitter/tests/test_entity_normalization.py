import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from splitter import parse_and_validate

MEMORY = 'Works at Blockchain Tech as a senior developer'

def answer(entities, quotes=None):
    return json.dumps({'memory_id':'m1','original_text':MEMORY,'units':[{
        'unit_id':'u1','raw_statement':MEMORY,'contextualized_statement':MEMORY,
        'memory_quotes':quotes if quotes is not None else [MEMORY], 'context_quotes':[],
        'entities':entities,'condition':None,'valid_time':None}], 'unresolved':[]})

class EntityNormalizationTests(unittest.TestCase):
    def parse(self, entities, quotes=None):
        return parse_and_validate(answer(entities,quotes),'m1',MEMORY,None)

    def test_names_are_normalized_but_original_objects_and_metadata_remain_auditable(self):
        objects=[{'type':'organization','name':'Blockchain Tech','disambiguation_support':'explicit name in memory'},
                 {'type':'job_title','name':'senior developer','disambiguation_support':'explicit title in memory'}]
        result=self.parse(objects)
        self.assertEqual(result['status'],'needs_review')
        self.assertEqual(result['parsed']['units'][0]['entities'],objects)
        self.assertEqual(result['validated_units'][0]['entities'],['Blockchain Tech','senior developer'])
        self.assertEqual([x['original'] for x in result['entity_normalizations']],objects)
        self.assertEqual([x['normalized'] for x in result['entity_normalizations']],['Blockchain Tech','senior developer'])
        self.assertTrue(any('normaliz' in x for x in result['warnings']))

    def test_missing_or_unclear_names_fail_without_dropping_original(self):
        for value in ({'type':'person'}, {'name':None}, {'name':'  '}, {'name':5}, ['nested'], 7):
            with self.subTest(value=value):
                result=self.parse(['Blockchain Tech',value])
                self.assertEqual(result['status'],'failed')
                self.assertEqual(result['parsed']['units'][0]['entities'][1],value)
                self.assertTrue(any('entities' in e for e in result['errors']))
                self.assertEqual(result['validated_units'],[])

    def test_quote_mismatch_remains_failure_when_entity_is_normalized(self):
        result=self.parse([{'name':'Blockchain Tech'}], ['not in source'])
        self.assertEqual(result['status'],'failed')
        self.assertTrue(any('memory_quotes' in e for e in result['errors']))
        self.assertEqual(result['parsed']['units'][0]['entities'],[{'name':'Blockchain Tech'}])

    def test_original_string_entities_pass_without_conversion(self):
        result=self.parse(['Blockchain Tech'])
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['validated_units'][0]['entities'],['Blockchain Tech'])
        self.assertEqual(result['entity_normalizations'],[])

if __name__=='__main__': unittest.main()
