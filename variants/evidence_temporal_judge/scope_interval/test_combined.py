import copy
import hashlib
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import combined


def fixture():
    old = '小李从2020年1月1日起住在北京，喜欢茶。'
    new = '小李2023年1月1日搬到上海。'
    fact = {'fact_index': 1, 'source_memory_id': 'm', 'raw_subfact': old,
            'contextualized_subfact': old, 'evidence': [{'source_type': 'memory', 'source_id': 'm', 'quote': old, 'supports': '旧事实'}], 'pending_confirmations': []}
    request = {'memory_id': 'm', 'memory_text': old, 'source_context': []}
    split = {'memory_id': 'm', 'memory_text': old, 'facts': [fact]}
    sources = [{'source_id': 'n', 'text': new}]
    parts = [{'fragment': '小李从2020年1月1日起住在北京', 'contextualized': '住在北京', 'action': 'modify', 'reason': '迁居', 'old_evidence': [{'source_type': 'memory', 'source_id': 'm', 'quote': old}], 'new_evidence': [{'source_id': 'n', 'quote': new}]},
             {'fragment': '喜欢茶', 'contextualized': '喜欢茶', 'action': 'protect', 'reason': '未涉及', 'old_evidence': [{'source_type': 'memory', 'source_id': 'm', 'quote': old}], 'new_evidence': []}]
    scope = {'memory_id': 'm', 'memory_text': old, 'source_context': [], 'new_evidence': sources, 'time_info': None, 'prompt_version': 'test', 'facts': [{'fact': fact, 'status': 'involved', 'applicability': 'involved', 'components': parts, 'semantic_support': 'not_verified'}], 'new_candidates': {'status': 'ok', 'candidates': [], 'semantic_support': 'not_verified'}, 'summary': {}}
    day = lambda v: {'value': v, 'precision': 'day'}
    times = {'facts': {'1': {'start': day('2020-01-01'), 'end': None, 'basis': {'source_type': 'memory', 'source_id': 'm', 'quote': old}}}, 'sources': {'n': {'start': day('2023-01-01'), 'end': None, 'kind': 'actual', 'basis': {'source_id': 'n', 'quote': new}}}, 'transitions': [{'fact_index': 1, 'source_id': 'n', 'quote': new, 'at': day('2023-01-01'), 'kind': 'actual'}]}
    pair = {1: {'erase_label': 'Make False', 'temporal_relation': 'before_after', 'reason': '手写受控测试', 'provenance': 'synthetic'}}
    return request, split, sources, scope, times, pair


def run(t='valid', verifier=True, nli=True):
    request, split, sources, scope, times, pair = fixture()
    if t == 'missing': times = None
    if t == 'coarse': times['sources']['n']['basis']['quote'] = sources[0]['text'] = '小李2023年搬到上海。'; scope['new_evidence'] = sources; scope['facts'][0]['components'][0]['new_evidence'][0]['quote'] = sources[0]['text']; times['transitions'][0]['quote'] = sources[0]['text']
    tv = (lambda p: {'status': 'supported', 'reason': '手写模拟'}) if verifier is True else verifier
    nb = (lambda p: {'relation': 'contradiction', 'score': .99}) if nli is True else nli
    return combined.combine(request, split, sources, scope, times, pair_assessments=pair, time_verifier=tv, nli_backend=nb, backend_provenance={'time_verifier': {'kind': 'simulation', 'source': 'test'}, 'nli': {'kind': 'simulation', 'source': 'test'}})

class CombinedTests(unittest.TestCase):
    def test_supported_transition_is_candidate_and_scope_stays_intact(self):
        r = run(); f = r['facts'][0]
        self.assertEqual([x['action'] for x in f['scope']['components']], ['modify', 'protect'])
        self.assertEqual(f['temporal']['temporal_relation'], 'before_after')
        self.assertEqual(f['temporal']['interval_adjustments'][0]['proposed_end']['value'], '2023-01-01')
        self.assertEqual(f['final']['scope_components'], f['scope']['components'])

    def test_missing_time_does_not_erase_scope_candidate(self):
        f = run('missing')['facts'][0]
        self.assertEqual(f['temporal_status'], 'time_missing')
        self.assertEqual(f['final']['scope_components'][0]['action'], 'modify')
        self.assertEqual(f['temporal']['interval_adjustments'], [])

    def test_insufficient_precision_and_unverified_time_are_distinct(self):
        self.assertEqual(run('coarse')['facts'][0]['temporal_status'], 'time_precision_insufficient')
        self.assertEqual(run(verifier=None)['facts'][0]['temporal_status'], 'time_unverified')

    def test_multiple_sources_are_not_silently_merged(self):
        request, split, sources, scope, times, pair = fixture()
        sources.append({'source_id': 'n2', 'text': '她也喜欢茶。'})
        scope['new_evidence'] = copy.deepcopy(sources)
        scope['facts'][0]['components'][1]['new_evidence'] = [{'source_id': 'n2', 'quote': '她也喜欢茶。'}]
        f = combined.combine(request, split, sources, scope, times, pair_assessments=pair)['facts'][0]
        self.assertEqual(f['temporal_status'], 'multiple_sources')
        self.assertEqual(f['final']['scope_components'][1]['action'], 'protect')

    def test_pair_error_and_malformed_response_are_distinct(self):
        def fail(_): raise RuntimeError('secret')
        self.assertEqual(run(nli=fail)['facts'][0]['temporal_status'], 'model_failed')
        self.assertEqual(run(nli=lambda _: {'relation': 'bogus'})['facts'][0]['temporal_status'], 'parse_failed')
        self.assertNotIn('secret', str(run(nli=fail)))

    def test_unknown_interval_does_not_invent_conflict(self):
        request, split, sources, scope, times, pair = fixture()
        times['transitions'] = []
        r = combined.combine(request, split, sources, scope, times, pair_assessments=pair, time_verifier=lambda _: {'status': 'supported', 'reason': '测试'}, nli_backend=lambda _: {'relation': 'contradiction'}, backend_provenance={'time_verifier': {'kind': 'simulation', 'source': 'test'}, 'nli': {'kind': 'simulation', 'source': 'test'}})
        self.assertEqual(r['facts'][0]['temporal']['interval_relation'], 'unknown')
        self.assertEqual(r['facts'][0]['temporal']['temporal_relation'], 'unclear')

    def test_scope_failures_remain_distinct(self):
        for status in ('model_failed', 'parse_failed'):
            request, split, sources, scope, times, pair = fixture()
            scope['facts'][0] = {'fact': split['facts'][0], 'status': status, 'error_type': 'Error'}
            f = combined.combine(request, split, sources, scope, times)['facts'][0]
            self.assertEqual(f['temporal_status'], 'deferred_scope_failure')
            self.assertEqual(f['scope']['status'], status)

    def test_evaluator_calls_require_provenance_and_keep_inputs_outputs(self):
        request, split, sources, scope, times, pair = fixture()
        with self.assertRaises(ValueError):
            combined.combine(request, split, sources, scope, times, time_verifier=lambda _: {'status': 'supported', 'reason': 'x'})
        r = run()
        self.assertEqual(r['evaluator_calls'][0]['provenance']['kind'], 'simulation')
        self.assertEqual(r['evaluator_calls'][0]['input']['task'], 'time_support')
        self.assertEqual(r['evaluator_calls'][0]['output']['status'], 'supported')
        self.assertEqual(r['evaluator_calls'][-1]['input']['task'], 'pair_nli')

    def test_time_verifier_errors_preserve_scope_and_cause(self):
        def fail(_): raise RuntimeError('private')
        for verifier, status in ((fail, 'model_failed'), (lambda _: {'status': 'wrong'}, 'parse_failed')):
            f = run(verifier=verifier)['facts'][0]
            self.assertEqual(f['temporal_status'], status)
            self.assertEqual(f['scope']['components'][0]['action'], 'modify')
            self.assertEqual(f['temporal']['interval_adjustments'], [])

    def test_fresh_path_uses_explicit_v4_prompt(self):
        request, split, sources, saved, times, pair = fixture()
        prompts = []
        def factory(prompt):
            prompts.append(prompt)
            return lambda _: {'facts': copy.deepcopy(split['facts'])}
        item = saved['facts'][0]
        r = combined.split_and_scope(request, sources, None, factory,
            lambda _: {'applicability': item['applicability'], 'components': item['components']},
            lambda _: {'candidates': []})
        prompt_path = combined.v2.v1.V4_PROMPT
        self.assertEqual(prompts, [prompt_path.read_text(encoding='utf-8')])
        self.assertEqual(r['splitter_prompt']['sha256'], hashlib.sha256(prompt_path.read_bytes()).hexdigest())
        self.assertEqual(r['facts'][0]['scope']['components'][0]['action'], 'modify')

    def test_rejects_different_memory_or_scope_provenance(self):
        request, split, sources, scope, times, pair = fixture()
        scope['memory_id'] = 'other'
        with self.assertRaises(ValueError): combined.combine(request, split, sources, scope, times)

if __name__ == '__main__': unittest.main()
