import copy
import json
from pathlib import Path
import unittest

import judge_scope as scope
from test_judge import MEMORY, FACTS, EVIDENCE

SPLIT = {'memory_id': 'm1', 'memory_text': MEMORY['memory_text'], **FACTS}
OLD = [{'source_type': 'memory', 'source_id': 'm1', 'quote': '小李住在北京，喜欢茶'}]


def response(status='involved'):
    return {'applicability': status, 'components': [
        {'fragment': '小李住在北京', 'contextualized': '小李住在北京', 'action': 'modify' if status == 'involved' else 'confirm', 'reason': '住址待核验', 'old_evidence': OLD, 'new_evidence': [{'source_id': 'new1', 'quote': '现在住在上海'}]},
        {'fragment': '喜欢茶', 'contextualized': '小李喜欢茶', 'action': 'protect', 'reason': '新材料未涉及茶', 'old_evidence': OLD, 'new_evidence': []}]}


class ScopeTests(unittest.TestCase):
    def run_judge(self, fact, candidate=lambda p: {'candidates': []}):
        return scope.judge(SPLIT, [], EVIDENCE, None, fact, candidate)

    def test_composite_keeps_context_and_separate_quotes_without_claiming_semantic_proof(self):
        result = self.run_judge(lambda p: response(), lambda p: {'candidates': [{'source_id': 'new1', 'quote': '现在住在上海', 'reason': '新的住址'}]})
        item = result['facts'][0]
        self.assertEqual([p['action'] for p in item['components']], ['modify', 'protect'])
        self.assertEqual(item['components'][1]['contextualized'], '小李喜欢茶')
        self.assertEqual(item['components'][0]['old_evidence'], OLD)
        self.assertEqual(item['semantic_support'], 'not_verified')
        self.assertEqual(result['new_candidates']['semantic_support'], 'not_verified')
        self.assertEqual(result['summary']['fact_status_counts']['involved'], 1)

    def test_uninvolved_insufficient_backend_and_schema_failure_are_distinct(self):
        uninvolved = response('uninvolved')
        for part in uninvolved['components']:
            part['action'], part['new_evidence'] = 'protect', []
        results = [self.run_judge(lambda p: uninvolved), self.run_judge(lambda p: response('insufficient')),
                   self.run_judge(lambda p: (_ for _ in ()).throw(RuntimeError('secret'))),
                   self.run_judge(lambda p: {'bad': 'format'})]
        self.assertEqual([r['facts'][0]['status'] for r in results], ['uninvolved', 'insufficient', 'model_failed', 'parse_failed'])
        for r in results[1:]:
            self.assertEqual(r['summary']['confirmed_valid'], 0)
        self.assertNotIn('secret', str(results))

    def test_bad_or_missing_quotes_and_coverage_are_parse_failure(self):
        for mutate in ('new', 'old', 'coverage'):
            value = copy.deepcopy(response())
            if mutate == 'new': value['components'][0]['new_evidence'][0]['quote'] = '不存在'
            if mutate == 'old': value['components'][1]['old_evidence'] = []
            if mutate == 'coverage': value['components'].pop()
            self.assertEqual(self.run_judge(lambda p: value)['facts'][0]['status'], 'parse_failed')

    def test_saved_v1_candidates_are_not_certified_semantically(self):
        root = Path(__file__).parent / 'runs/scope_check_20261105_v1'
        saved = json.loads((root / 'career_history/candidate_stage.json').read_text())
        candidates = {'candidates': saved['candidates']}
        saved_input = json.loads((root / 'career_history/model_input.json').read_text())
        checked = scope.validate_candidates(candidates, scope.base._sources(saved_input['new_evidence']))
        self.assertIn('founding', checked['candidates'][0]['reason'])
        self.assertEqual(checked['semantic_support'], 'not_verified')

    def test_saved_skydiving_split_accepts_partial_uncertainty_and_safety_protection(self):
        root = Path(__file__).parent / 'runs/scope_check_20261105_v1/skydiving'
        inputs, split = (json.loads((root / x).read_text()) for x in ('model_input.json', 'split_result.json'))
        fact = split['result']['facts'][0]
        old = [{k: e[k] for k in ('source_type', 'source_id', 'quote')} for e in fact['evidence']]
        answer = {'applicability': 'insufficient', 'components': [
            {'fragment': 'Dislikes extreme sports (e.g., skydiving)', 'contextualized': 'User dislikes extreme sports (e.g., skydiving) due to high injury risk',
             'action': 'confirm', 'reason': 'A simulated experience does not determine the attitude to actual skydiving.',
             'old_evidence': old, 'new_evidence': [{'source_id': 'dialogue-0', 'quote': 'tried simulated skydiving'}]},
            {'fragment': 'due to high injury risk, conflicting with commitment to safety and well-being',
             'contextualized': 'User dislikes extreme sports due to high injury risk, which conflicts with their commitment to safety and well-being',
             'action': 'protect', 'reason': 'The old risk rationale is not negated.', 'old_evidence': old,
             'new_evidence': [{'source_id': 'dialogue-8', 'quote': 'I still prioritize safety'}]}]}
        result = scope.judge(split['result'], inputs['split_request']['source_context'], inputs['new_evidence'], None,
                             lambda p: answer, lambda p: {'candidates': []})
        self.assertEqual(result['facts'][0]['status'], 'insufficient')
        self.assertEqual([c['action'] for c in result['facts'][0]['components']], ['confirm', 'protect'])
        self.assertIn('due to high injury risk', result['facts'][0]['components'][1]['contextualized'])

    def test_saved_promotion_split_can_represent_employer_and_role_separately(self):
        root = Path(__file__).parent / 'runs/scope_check_20261105_v1/promotion'
        inputs, split = (json.loads((root / x).read_text()) for x in ('model_input.json', 'split_result.json'))
        fact = split['result']['facts'][0]
        old = [{k: e[k] for k in ('source_type', 'source_id', 'quote')} for e in fact['evidence']]
        quote = [{'source_id': 'dialogue-0', 'quote': 'I recently got promoted to lead director at Historical Productions Ltd.'}]
        answer = {'applicability': 'involved', 'components': [
            {'fragment': 'Works at Historical Productions Ltd.', 'contextualized': 'User works at Historical Productions Ltd. as a Director',
             'action': 'protect', 'reason': 'Employer remains present in the new statement', 'old_evidence': old, 'new_evidence': quote},
            {'fragment': 'as a Director', 'contextualized': 'User works at Historical Productions Ltd. as a Director',
             'action': 'modify', 'reason': 'Role detail may need updating while retaining the historical role', 'old_evidence': old, 'new_evidence': quote}]}
        result = scope.judge(split['result'], inputs['split_request']['source_context'], inputs['new_evidence'], None,
                             lambda p: answer, lambda p: {'candidates': []})
        self.assertEqual(result['facts'][0]['status'], 'involved')
        self.assertEqual([c['action'] for c in result['facts'][0]['components']], ['protect', 'modify'])
        self.assertIn('Historical Productions Ltd.', result['facts'][0]['components'][1]['contextualized'])

    def test_backend_parse_failure_and_candidate_failure_do_not_become_empty_success(self):
        def malformed(p): raise scope.BackendParseError()
        result = self.run_judge(malformed, malformed)
        self.assertEqual(result['facts'][0]['status'], 'parse_failed')
        self.assertEqual(result['new_candidates']['status'], 'parse_failed')
        self.assertEqual(result['summary']['confirmed_valid'], 0)


if __name__ == '__main__': unittest.main()
