import unittest
import json
import tempfile
from pathlib import Path
from review import digest, lookup_review, render_case, summarize, verify_saved_source


class ReviewTests(unittest.TestCase):
    def test_independent_review_must_match_exact_raw_record_hash(self):
        record = {'unit_id': 'u', 'relation': 'change'}
        reviews = {'0': {'sha256': digest(record), 'verdict': 'supported', 'reason': 'separately reviewed'}}
        self.assertEqual(lookup_review(reviews, 0, record)['verdict'], 'supported')
        changed = {'unit_id': 'u', 'relation': 'plan'}
        self.assertEqual(lookup_review(reviews, 0, changed)['verdict'], 'not_reviewed')
        self.assertEqual(lookup_review({}, 0, record)['verdict'], 'not_reviewed')

    def test_interface_success_not_counted_as_semantic_support(self):
        artifact = {'case_id': 'example', 'prepared_input': {'source_texts': {'memory': {'text': 'Old'}, 'messages': []}},
                    'call': {'status': 'passed'}, 'usage': None,
                    'result': {'status': 'passed', 'validation': {'status': 'passed', 'quote_checks': []},
                               'parsed': {'records': [{'unit_id': 'u', 'relation': 'change'}]},
                               'plan': {'modify': [], 'preserve': [], 'uncertain': [{'reason': 'semantic support missing'}],
                                        'add': [], 'quote_checks': [], 'editable_spans': [], 'protected_facts': []}}}
        stats = summarize([artifact], {})
        self.assertEqual(stats['structured_passed'], 1)
        self.assertEqual(stats['record_reviews']['not_reviewed'], 1)
        self.assertEqual(stats['record_reviews'].get('supported', 0), 0)
        report = render_case(artifact, {}, {})
        self.assertIn('semantic support missing', report)
        self.assertIn('not_reviewed', report)

    def test_request_failure_is_reported_not_counted_as_structure_failure(self):
        artifact = {'case_id': 'failed', 'call': {'status': 'request_error', 'attempts': 1}, 'result': None,
                    'raw_response': '{"error":"service unavailable"}', 'provider_response': None}
        stats = summarize([artifact], {})
        self.assertEqual(stats['model_responses'], 0)
        self.assertEqual(stats['structured_passed'], 0)
        self.assertIn('request_error', render_case(artifact, {}, {}))

    def test_provider_response_is_counted_even_if_later_processing_fails(self):
        artifact = {'case_id': 'x', 'call': {'status': 'request_error', 'attempts': 1},
                    'provider_response': {'choices': []}, 'raw_response': None, 'result': None}
        self.assertEqual(summarize([artifact], {})['model_responses'], 1)

    def test_schema_pass_and_quote_failure_are_counted_separately(self):
        artifact = {'case_id': 'x', 'call': {'status': 'failed', 'attempts': 1},
                    'provider_response': {'choices': []},
                    'result': {'validation': {'status': 'failed', 'schema_status': 'passed',
                                              'quote_status': 'failed', 'quote_checks': [{'status': 'invalid'}]},
                               'parsed': {'records': []}, 'plan': {}}}
        stats = summarize([artifact], {})
        self.assertEqual(stats['structured_passed'], 1)
        self.assertEqual(stats['quote_passed_cases'], 0)
        self.assertEqual(stats['quote_checks']['invalid'], 1)

    def test_safe_reanalysis_does_not_replace_original_plan(self):
        artifact = {'case_id':'x', 'call':{'status':'passed'}, 'prepared_input':{},
                    'result':{'parsed':{'records':[{}]}, 'validation':{},
                              'plan':{'preserve':[{'reason':'original preserve'}]}}}
        safe = {'status':'completed_offline', 'safe_plan':{'uncertain':[{'reason':'safe guard'}]},
                'provenance':{'adapter_sha256':'hash'}}
        text = render_case(artifact, {}, {}, safe)
        self.assertIn('original preserve', text)
        self.assertIn('safe guard', text)
        self.assertIn('事后离线', text)

    def test_source_ref_is_verified_against_disk_not_just_copied_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'msg.json').write_text(json.dumps({'raw_dialogue':[{'content':'原文'}]}), encoding='utf-8')
            s = {'source_id':'new-0', 'source_ref':'msg.json#/raw_dialogue/0/content', 'text':'原文'}
            self.assertEqual(verify_saved_source(s, root)['status'], 'verified')
            s['text'] = '篡改'
            self.assertEqual(verify_saved_source(s, root)['status'], 'invalid')

if __name__ == '__main__':
    unittest.main()
