import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from splitter import parse_and_validate

MEM = 'Alice likes tea and coffee. She avoids milk.'
CTX = 'Alice is the speaker.'
def unit(**changes):
    u = dict(unit_id='u1', raw_statement='Alice likes tea and coffee', contextualized_statement='Alice likes tea and coffee', memory_quotes=['Alice likes tea', 'coffee'], context_quotes=[], entities=['Alice'], condition=None, valid_time=None)
    u.update(changes)
    return u

def response(units=None, **kw):
    d = dict(memory_id='m1', original_text=MEM, units=units if units is not None else [unit()], unresolved=[])
    d.update(kw)
    return json.dumps(d)

class ValidationTests(unittest.TestCase):
    def check(self, raw, mem=MEM, ctx=CTX):
        return parse_and_validate(raw, 'm1', mem, ctx)
    def test_valid_multi_quote_and_null_time(self):
        result = self.check(response())
        self.assertEqual(result['status'], 'passed')
        self.assertIsNone(result['parsed']['units'][0]['valid_time'])
    def test_nonexistent_quote_fails(self):
        result = self.check(response([unit(memory_quotes=['invented'])]))
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(any('memory_quotes' in x for x in result['errors']))
    def test_repeated_quote_is_ambiguous(self):
        mem = 'tea and tea'
        result = self.check(json.dumps(dict(memory_id='m1',original_text=mem,units=[unit(memory_quotes=['tea'])],unresolved=[])),mem)
        self.assertEqual(result['status'], 'needs_review')
        self.assertTrue(any('ambiguous' in x for x in result['warnings']))
    def test_context_quote_must_match(self):
        result = self.check(response([unit(context_quotes=['Bob'])]))
        self.assertEqual(result['status'], 'failed')
    def test_contextualized_change_without_evidence_is_review(self):
        result = self.check(response([unit(raw_statement='She avoids milk', contextualized_statement='Alice avoids milk', memory_quotes=['She avoids milk'])]))
        self.assertEqual(result['status'], 'needs_review')
    def test_unresolved_reference_is_review(self):
        result = self.check(response([unit(raw_statement='She avoids milk', contextualized_statement='She avoids milk', memory_quotes=['She avoids milk'])],unresolved=['Who is She?']))
        self.assertEqual(result['status'], 'needs_review')
    def test_bad_json_fails(self):
        self.assertEqual(self.check('{not json')['status'], 'failed')
    def test_missing_required_field_fails(self):
        u = unit(); del u['condition']
        self.assertEqual(self.check(response([u]))['status'], 'failed')
    def test_duplicate_or_empty_unit_id_fails(self):
        self.assertEqual(self.check(response([unit(), unit()]))['status'], 'failed')
        self.assertEqual(self.check(response([unit(unit_id=' ')]))['status'], 'failed')
    def test_memory_id_and_original_must_match(self):
        self.assertEqual(self.check(response(memory_id='other'))['status'], 'failed')
        self.assertEqual(self.check(response(original_text='other'))['status'], 'failed')
    def test_json_fenced_is_accepted(self):
        self.assertEqual(self.check('```json\n'+response()+'\n```')['status'], 'passed')
    def test_empty_units_and_bad_types_fail(self):
        self.assertEqual(self.check(response([]))['status'], 'failed')
        self.assertEqual(self.check(response([unit(memory_quotes='tea')]))['status'], 'failed')
    def test_context_quote_multiple_occurrences_review(self):
        self.assertEqual(self.check(response([unit(context_quotes=['Alice'])]),ctx='Alice and Alice')['status'], 'needs_review')

if __name__ == '__main__': unittest.main()
