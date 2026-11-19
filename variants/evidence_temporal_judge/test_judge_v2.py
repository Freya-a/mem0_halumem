import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge_v2 as v2
from test_judge import MEMORY, FACTS, reply

EVIDENCE = [{'source_id': 'new1', 'text': '小李在2023年1月1日搬到上海，现在住在上海。'}]


def boundary(value, precision=None):
    return {'value': value, 'precision': precision or {4: 'year', 7: 'month', 10: 'day'}[len(value)]}


def times(old_start=None, old_end=None, new_start=None, new_end=None, *, kind='actual', transition=None):
    old_quote = '北京居住状态' + ''.join(f'；{key}于{value["value"]}' for key, value in [('开始', old_start), ('结束', old_end)] if value)
    new_quote = '上海居住状态' + ''.join(f'；{key}于{value["value"]}' for key, value in [('开始', new_start), ('结束', new_end)] if value)
    return {'facts': {'1': {'start': old_start, 'end': old_end, 'basis': {'source_type': 'context', 'source_id': 'old-time', 'quote': old_quote}}},
            'sources': {'new1': {'start': new_start, 'end': new_end, 'basis': {'source_id': 'new1', 'quote': new_quote}, 'kind': kind}},
            'transition': transition}


def transition():
    return {'fact_index': 1, 'source_id': 'new1', 'quote': '2023年1月1日搬到上海', 'at': boundary('2023-01-01'), 'kind': 'actual'}


def supported_time(request):
    return {'status': 'supported', 'reason': '合成测试中显式提供的状态时间'}


def prepare(t, evidence=EVIDENCE):
    request, facts, sources = copy.deepcopy((MEMORY, FACTS, evidence))
    if t is not None:
        old_quote = t['facts']['1']['basis']['quote']
        request['source_context'] = [{'source_id': 'old-time', 'source_ref': 'synthetic', 'text': old_quote}]
        facts['facts'][0]['evidence'].append({'source_type': 'context', 'source_id': 'old-time', 'quote': old_quote, 'supports': '状态时间'})
        sources[0]['text'] += '；' + t['sources']['new1']['basis']['quote']
    return request, facts, sources


def run(t, nli=lambda request: {'relation': 'contradiction', 'score': 0.99}, impact=reply):
    request, facts, sources = prepare(t)
    return v2.split_and_judge(request, sources, t, lambda prompt: lambda request: copy.deepcopy(facts),
                              lambda request: impact(), lambda request: {'candidates': [{'source_id': 'new1', 'quote': '现在住在上海', 'reason': '新地址'}]}, nli,
                              time_verifier=supported_time)


def precision_case(old_text, new_text, new_quote, verifier=None, old_start=None, new_start=None):
    request = {'memory_id': 'precision-test', 'memory_text': old_text, 'source_context': []}
    fact = {'fact_index': 1, 'source_memory_id': request['memory_id'], 'raw_subfact': old_text,
            'contextualized_subfact': old_text, 'evidence': [{'source_type': 'memory',
            'source_id': request['memory_id'], 'quote': old_text, 'supports': '旧记忆'}], 'pending_confirmations': []}
    evidence = [{'source_id': 'new', 'text': new_text}]
    impact = {'erase_label': 'Make False', 'applicability': 'involved', 'temporal_relation': 'before_after',
              'temporal_reason': '候选变化', 'components': [{'fragment': old_text, 'action': 'modify',
              'reason': '居住地变化', 'new_evidence': [{'source_id': 'new', 'quote': new_quote}]}]}
    old_start = old_start or boundary('2020-01-01')
    new_start = new_start or boundary('2023-01-01')
    time = {'facts': {'1': {'start': old_start, 'end': None,
            'basis': {'source_type': 'memory', 'source_id': request['memory_id'], 'quote': old_text}}},
            'sources': {'new': {'start': new_start, 'end': None, 'kind': 'actual',
            'basis': {'source_id': 'new', 'quote': new_quote}}},
            'transition': {'fact_index': 1, 'source_id': 'new', 'quote': new_quote,
                           'at': new_start, 'kind': 'actual'}}
    return v2.split_and_judge(request, evidence, time, lambda prompt: lambda req: {'facts': [fact]},
        lambda req: impact, lambda req: {'candidates': []}, lambda req: {'relation': 'contradiction'},
        time_verifier=verifier)['facts'][0]


class V2Tests(unittest.TestCase):
    def test_year_only_new_evidence_does_not_prove_a_day(self):
        f = precision_case('小李从2020年1月1日起住在北京。', '小李2023年搬到上海。', '2023年搬到上海', supported_time)
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        self.assertEqual(f['components'][0]['action'], 'confirm')
        new = next(x for x in f['time_checks'] if x['role'] == 'transition')
        self.assertEqual((new['quote_status'], new['precision_status'], new['semantic_status']),
                         ('matched', 'insufficient', 'supported'))

    def test_year_only_old_start_does_not_prove_a_day(self):
        f = precision_case('小李从2020年起住在北京。', '小李2023年1月1日搬到上海。', '2023年1月1日搬到上海', supported_time)
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        old = next(x for x in f['time_checks'] if x['role'] == 'old_start')
        self.assertEqual((old['quote_status'], old['precision_status'], old['semantic_status']),
                         ('matched', 'insufficient', 'supported'))

    def test_record_date_is_not_move_date_even_when_literal_date_matches(self):
        def verifier(request):
            return {'status': 'supported' if request['role'] == 'old_start' else 'not_supported', 'reason': '日期是记录时间'}
        f = precision_case('小李从2020年1月1日起住在北京。', '2023年1月1日的记录：小李2023年搬到上海。', '2023年1月1日的记录：小李2023年搬到上海', verifier)
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        check = next(x for x in f['time_checks'] if x['role'] == 'transition')
        self.assertEqual((check['quote_status'], check['precision_status'], check['semantic_status']),
                         ('matched', 'matched', 'not_supported'))

    def test_relative_event_date_requires_a_supported_anchor(self):
        f = precision_case('小李从2020年1月1日起住在北京。', '2023年1月1日记录：小李去年搬到上海。', '2023年1月1日记录：小李去年搬到上海')
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])

    def test_explicit_dates_need_and_keep_separate_semantic_assessment(self):
        f = precision_case('小李从2020年1月1日起住在北京。', '小李2023年1月1日搬到上海。', '2023年1月1日搬到上海', supported_time)
        self.assertEqual(f['temporal_relation'], 'before_after')
        self.assertEqual(f['interval_adjustments'][0]['proposed_end']['value'], '2023-01-01')
        for check in f['time_checks']:
            self.assertEqual(check['quote_status'], 'matched')
            self.assertEqual(check['precision_status'], 'matched')
            self.assertEqual(check['semantic_status'], 'supported')

    def test_unverified_explicit_date_is_not_semantic_proof(self):
        f = precision_case('小李从2020年1月1日起住在北京。', '小李2023年1月1日搬到上海。', '2023年1月1日搬到上海')
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        self.assertTrue(any(x['semantic_status'] == 'not_checked' for x in f['time_checks']))

    def test_year_precision_is_a_range_not_an_exact_first_day(self):
        f = precision_case('小李从2020年起住在北京。', '小李2023年搬到上海。', '2023年搬到上海',
                           supported_time, old_start=boundary('2020'), new_start=boundary('2023'))
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        self.assertEqual(f['intervals']['old']['start'], boundary('2020'))
        self.assertEqual(next(x for x in f['time_checks'] if x['role'] == 'transition')['precision_status'], 'matched')

    def test_day_in_iso_evidence_can_support_a_month_precision_claim(self):
        f = precision_case('小李从2020-01-01起住在北京。', '小李2023年1月1日搬到上海。', '2023年1月1日搬到上海',
                           supported_time, old_start=boundary('2020-01'))
        check = next(x for x in f['time_checks'] if x['role'] == 'old_start')
        self.assertEqual(check['precision_status'], 'matched')
        self.assertEqual(f['temporal_relation'], 'before_after')

    def test_semantic_verifier_failure_does_not_expose_error_or_allow_adjustment(self):
        def broken(request):
            raise RuntimeError('private diagnostic')
        f = precision_case('小李从2020年1月1日起住在北京。', '小李2023年1月1日搬到上海。',
                           '2023年1月1日搬到上海', broken)
        self.assertEqual(f['status'], 'failed')
        self.assertEqual(f['interval_adjustments'], [])
        self.assertEqual(f['components'][0]['action'], 'confirm')
        self.assertNotIn('private diagnostic', str(f))

    def test_transition_adjustment_is_candidate_and_preserves_partial_fact(self):
        t = times(boundary('2020-01-01'), None, boundary('2023-01-01'), None, transition=transition())
        before = copy.deepcopy(t)
        result = run(t)
        fact = result['facts'][0]
        self.assertEqual(fact['temporal_relation'], 'before_after')
        self.assertEqual([x['action'] for x in fact['components']], ['modify', 'protect'])
        self.assertEqual(fact['interval_adjustments'][0]['proposed_end'], {'value': '2023-01-01', 'precision': 'day', 'inclusive': False})
        self.assertEqual(fact['interval_adjustments'][0]['fragments'], ['小李住在北京'])
        self.assertEqual(t, before)
        self.assertEqual(fact['fact']['evidence'][0]['source_id'], 'm1')
        self.assertEqual(fact['impact_judgment']['temporal_reason'], '旧住址与新住址有先后')
        self.assertEqual(result['new_candidates']['candidates'][0]['quote'], '现在住在上海')
        self.assertEqual(result['splitter_prompt']['sha256'], hashlib.sha256(v2.v1.V4_PROMPT.read_bytes()).hexdigest())
        self.assertEqual(fact['path'], ['determine_interval', 'block_check', 'contradiction_check', 'adjustment_candidate'])

    def test_disjoint_historical_facts_retained(self):
        t = times(boundary('2018'), boundary('2020'), boundary('2022'), boundary('2024'))
        f = run(t)['facts'][0]
        self.assertEqual(f['temporal_relation'], 'historical_compatible')
        self.assertEqual(f['interval_relation'], 'before')
        self.assertEqual(f['components'][0]['action'], 'protect')
        self.assertEqual(f['interval_adjustments'], [])

    def test_new_evidence_can_describe_an_earlier_period(self):
        t = times(boundary('2022'), boundary('2024'), boundary('2018'), boundary('2020'))
        f = run(t)['facts'][0]
        self.assertEqual(f['interval_relation'], 'after')
        self.assertEqual(f['temporal_relation'], 'historical_compatible')
        self.assertIn('新证据描述较早时期', f['temporal_reason'])
        self.assertEqual(f['components'][0]['action'], 'protect')

    def test_overlap_requires_semantic_conflict_and_evidence_impact(self):
        t = times(boundary('2020'), boundary('2024'), boundary('2022'), boundary('2023'))
        f = run(t)['facts'][0]
        self.assertEqual(f['interval_relation'], 'overlap')
        self.assertEqual(f['temporal_relation'], 'simultaneous_conflict')
        self.assertEqual(f['interval_adjustments'], [])
        f = run(t, lambda request: {'relation': 'compatible'})['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['components'][0]['action'], 'confirm')

    def test_record_time_is_not_event_time_and_unknown_bounds_are_unknown(self):
        t = times(); t['sources']['new1']['recorded_at'] = '2023-01-01'
        f = run(t)['facts'][0]
        self.assertEqual(f['interval_relation'], 'unknown')
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['components'][0]['action'], 'confirm')

    def test_precision_ambiguity_and_invalid_dates(self):
        t = times(boundary('2020'), boundary('2023'), boundary('2023-02'), boundary('2024'))
        self.assertEqual(run(t)['facts'][0]['interval_relation'], 'unknown')
        t['sources']['new1']['start'] = boundary('2023-02-30')
        self.assertEqual(run(t)['facts'][0]['status'], 'failed')

    def test_simulation_cannot_change_actual_state(self):
        t = times(boundary('2020-01-01'), None, boundary('2023-01-01'), None, kind='simulation', transition=transition())
        f = run(t)['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['components'][0]['action'], 'confirm')
        self.assertEqual(f['interval_adjustments'], [])

    def test_nli_uncertain_failure_and_invalid_quotes_fail_closed(self):
        t = times(boundary('2020'), boundary('2024'), boundary('2022'), boundary('2023'))
        f = run(t, lambda request: {'relation': 'uncertain'})['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        f = run(t, lambda request: (_ for _ in ()).throw(RuntimeError('secret')))['facts'][0]
        self.assertEqual(f['status'], 'failed')
        self.assertNotIn('secret', str(f))
        t['sources']['new1']['basis']['source_id'] = 'unknown'
        failed = run(t)['facts'][0]
        self.assertEqual(failed['status'], 'failed')
        self.assertEqual(next(x for x in failed['time_checks'] if x['role'] == 'new_start')['quote_status'], 'invalid')

    def test_strong_nli_alone_cannot_propose_modification(self):
        def impact():
            data = reply(); data['erase_label'] = 'No Change'; data['applicability'] = 'insufficient'
            data['temporal_relation'] = 'unclear'
            for p in data['components']: p['action'] = 'confirm'
            return data
        t = times(boundary('2020'), boundary('2024'), boundary('2022'), boundary('2023'))
        f = run(t, impact=impact)['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertFalse(f['interval_adjustments'])
        self.assertTrue(all(x['action'] == 'confirm' for x in f['components']))

    def test_fact_backend_failure_preserves_fact_as_confirmation_candidate(self):
        result = v2.split_and_judge(MEMORY, EVIDENCE, None, lambda p: lambda r: copy.deepcopy(FACTS),
                                    lambda r: (_ for _ in ()).throw(RuntimeError('secret')),
                                    lambda r: {'candidates': []}, lambda r: {'relation': 'contradiction'})
        f = result['facts'][0]
        self.assertEqual(f['status'], 'failed')
        self.assertEqual(f['components'][0]['action'], 'confirm')
        self.assertEqual(f['components'][0]['fragment'], MEMORY['memory_text'])
        self.assertEqual(f['path'], [])
        self.assertNotIn('secret', str(f))

    def test_transition_for_other_fact_does_not_adjust_this_fact(self):
        event = transition(); event['fact_index'] = 2
        f = run(times(boundary('2020-01-01'), None, boundary('2023-01-01'), None, transition=event))['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])

    def test_overlap_containment_and_boundary_touch(self):
        t = times(boundary('2020-01-01'), boundary('2024-01-01'), boundary('2021-01-01'), boundary('2022-01-01'))
        self.assertEqual(run(t)['facts'][0]['interval_relation'], 'overlap')
        t = times(boundary('2020-01-01'), boundary('2022-01-01'), boundary('2022-01-01'), boundary('2023-01-01'))
        self.assertEqual(run(t)['facts'][0]['interval_relation'], 'overlap')

    def test_missing_time_is_insufficient_not_a_processing_error(self):
        f = run(None)['facts'][0]
        self.assertEqual(f['status'], 'involved')
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['components'][0]['action'], 'confirm')

    def test_nearest_evidence_backed_blocker_is_a_fragment_candidate(self):
        evidence = [{'source_id': 'new1', 'text': '2022年1月1日搬到南京，2023年1月1日搬到上海，现在住在上海。'}]
        t = times(boundary('2020-01-01'), None, boundary('2023-01-01'), None)
        t['transitions'] = [transition(), {'fact_index': 1, 'source_id': 'new1', 'quote': '2022年1月1日搬到南京', 'at': boundary('2022-01-01'), 'kind': 'actual'}]
        request, facts, evidence = prepare(t, evidence)
        result = v2.split_and_judge(request, evidence, t, lambda p: lambda r: copy.deepcopy(facts),
                                    lambda r: reply(), lambda r: {'candidates': []}, lambda r: {'relation': 'contradiction'},
                                    time_verifier=supported_time)
        adjustment = result['facts'][0]['interval_adjustments'][0]
        self.assertEqual(adjustment['proposed_end']['value'], '2022-01-01')
        self.assertEqual(adjustment['basis']['quote'], '2022年1月1日搬到南京')
        self.assertEqual(adjustment['fragments'], ['小李住在北京'])

    def test_earlier_year_only_transition_prevents_a_false_exact_nearest_blocker(self):
        evidence = [{'source_id': 'new1', 'text': '2022年搬到南京，2023年1月1日搬到上海，现在住在上海。'}]
        t = times(boundary('2020-01-01'), None, boundary('2023-01-01'), None)
        t['transitions'] = [transition(), {'fact_index': 1, 'source_id': 'new1',
                           'quote': '2022年搬到南京', 'at': boundary('2022'), 'kind': 'actual'}]
        request, facts, evidence = prepare(t, evidence)
        result = v2.split_and_judge(request, evidence, t, lambda p: lambda r: copy.deepcopy(facts),
                                    lambda r: reply(), lambda r: {'candidates': []},
                                    lambda r: {'relation': 'contradiction'}, time_verifier=supported_time)
        f = result['facts'][0]
        self.assertEqual(f['temporal_relation'], 'unclear')
        self.assertEqual(f['interval_adjustments'], [])
        self.assertEqual(f['components'][0]['action'], 'confirm')

if __name__ == '__main__': unittest.main()
