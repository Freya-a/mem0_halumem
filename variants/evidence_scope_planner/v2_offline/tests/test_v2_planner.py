import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scope_planner import build_scope_plan


def example():
    old = '上海南京堂食外带旧价。'
    units = [{'id': 'u', 'memory_id': 'm', 'source_ref': 'old-ref', 'quote': old, 'fact': '旧价'}]
    sources = [{'source_id': 's', 'source_ref': 's-ref', 'speaker': 'user', 'side': 'new', 'text': '后来上海外带新价。'}]
    a = {'unit_id': 'u', 'relation': 'change', 'old_subject': '商户', 'new_subject': '商户',
         'old_attribute': '价格', 'new_attribute': '价格', 'old_value': '旧', 'new_value': '新',
         'old_quote': old, 'new_quote': '后来上海外带新价。', 'source_id': 's',
         'old_conditions': {'kind': 'finite', 'dimensions': {'城市': ['上海', '南京'], '方式': ['堂食', '外带']}},
         'new_conditions': {'kind': 'finite', 'dimensions': {'城市': ['上海'], '方式': ['外带']}},
         'modality': 'asserted', 'semantic_support': 'supported', 'semantic_basis': [{'source_id': 's', 'quote': '后来上海外带新价。', 'side': 'new'}],
         'temporal_order': {'relation': 'after', 'explanation': '新价格明确在旧价格之后', 'basis': [{'source_id': 's', 'quote': '后来上海外带新价。', 'side': 'new'}]}}
    return old, units, sources, [a]


class V2PlannerTests(unittest.TestCase):
    def test_after_with_valid_temporal_basis_modifies_only_intersection(self):
        p = build_scope_plan(*example())
        self.assertEqual([x['scope'] for x in p['modify']], [{'城市': '上海', '方式': '外带'}])
        self.assertEqual(len(p['preserve']), 3)

    def test_before_same_unknown_missing_or_invalid_basis_cannot_replace(self):
        for order in ('before', 'same', 'unknown', 'missing', 'bad_basis'):
            args = example()
            if order == 'missing':
                del args[3][0]['temporal_order']
            elif order == 'bad_basis':
                args[3][0]['temporal_order']['basis'][0]['quote'] = '不在关联引文'
            else:
                args[3][0]['temporal_order']['relation'] = order
            with self.subTest(order=order):
                p = build_scope_plan(*args)
                self.assertFalse(p['modify'])
                if order == 'before':
                    self.assertEqual(len(p['preserve']), 4)
                else:
                    self.assertTrue(p['uncertain'])

    def test_multiple_sources_validate_independently_without_cross_pairing(self):
        args = example()
        args[2].append({'source_id': 's2', 'source_ref': 's2-ref', 'speaker': 'user', 'side': 'new', 'text': '新政策适用上海外带。'})
        args[3][0]['old_quotes'] = [{'source_id': 'm', 'unit_id': 'u', 'quote': args[0]}]
        args[3][0]['new_quotes'] = [{'source_id': 's', 'quote': args[2][0]['text']},
                                    {'source_id': 's2', 'quote': args[2][1]['text']}]
        p = build_scope_plan(*args)
        self.assertEqual(len(p['modify']), 1)
        self.assertEqual(len(p['modify'][0]['new_quotes']), 2)
        args[3][0]['new_quotes'][1]['source_id'] = 'other'
        p = build_scope_plan(*args)
        self.assertFalse(p['modify'])
        self.assertTrue(p['uncertain'])

    def test_wrong_old_memory_source_is_held(self):
        args = example()
        args[3][0]['old_quotes'] = [{'source_id': 'wrong', 'unit_id': 'u', 'quote': args[0]}]
        self.assertFalse(build_scope_plan(*args)['modify'])

    def test_unknown_and_valid_disjoint_ranges_do_not_block_each_other(self):
        args = example()
        second = copy.deepcopy(args[3][0])
        second['relation'] = 'unknown'
        second['note'] = '南京外带未知'
        second['new_conditions']['dimensions']['城市'] = ['南京']
        args[3].append(second)
        p = build_scope_plan(*args)
        self.assertEqual(len(p['modify']), 1)
        self.assertTrue(any(x.get('scope') == {'城市': '南京', '方式': '外带'} for x in p['uncertain']))
        self.assertEqual(len(p['preserve']), 2)

    def test_new_information_needs_semantics_and_explicit_modality(self):
        args = example()
        a = {'unit_id': None, 'relation': 'new_information', 'source_id': 's',
             'new_quote': args[2][0]['text'], 'new_subject': '商户', 'new_attribute': '价格',
             'new_value': '新', 'semantic_support': 'supported',
             'semantic_basis': [{'source_id': 's', 'quote': args[2][0]['text'], 'side': 'new'}]}
        p = build_scope_plan(args[0], [], args[2], [a])
        self.assertFalse(p['add'])
        a['modality'] = 'planned'
        p = build_scope_plan(args[0], [], args[2], [a])
        self.assertEqual(p['add'][0]['status'], 'planned')

    def test_multiple_old_quotes_without_local_binding_are_uncertain(self):
        args = example()
        args[3][0]['old_quotes'] = [{'source_id': 'm', 'quote': '上海'}, {'source_id': 'm', 'quote': '南京'}]
        self.assertFalse(build_scope_plan(*args)['modify'])

    def test_semantic_support_needs_explicit_bound_basis(self):
        args = example()
        del args[3][0]['semantic_support']
        self.assertFalse(build_scope_plan(*args)['modify'])
        args[3][0]['semantic_support'] = 'supported'
        args[3][0]['semantic_basis'][0]['quote'] = '不是关联引文'
        self.assertFalse(build_scope_plan(*args)['modify'])

    def test_after_needs_a_supplied_relationship_explanation(self):
        args = example()
        del args[3][0]['temporal_order']['explanation']
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertTrue(result['uncertain'])

    def test_single_unknown_finite_subscope_preserves_other_combinations(self):
        args = example()
        args[3][0]['relation'] = 'unknown'
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertEqual(len(result['preserve']), 3)
        self.assertEqual(result['uncertain'][0]['scope'], {'城市': '上海', '方式': '外带'})

    def test_independent_addition_and_unrelated_preservation(self):
        args = example()
        a = args[3][0]
        a['relation'] = 'unrelated'
        a['no_impact_confirmed'] = True
        new = {'unit_id': None, 'relation': 'new_information', 'source_id': 's',
               'new_quote': args[2][0]['text'], 'new_subject': '顾客', 'new_attribute': '计划',
               'new_value': '外带', 'modality': 'planned', 'semantic_support': 'supported',
               'semantic_basis': [{'source_id': 's', 'quote': args[2][0]['text'], 'side': 'new'}]}
        args[3].append(new)
        result = build_scope_plan(*args)
        self.assertEqual(len(result['add']), 1)
        self.assertEqual(len(result['preserve']), 4)
        self.assertFalse(result['modify'])

    def test_simulated_experience_does_not_modify_real_preference(self):
        args = example()
        args[3][0]['old_conditions'] = {'kind': 'finite', 'dimensions': {'experience': ['real']}}
        args[3][0]['new_conditions'] = {'kind': 'finite', 'dimensions': {'experience': ['simulated']}}
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertEqual(result['preserve'][0]['scope'], {'experience': 'real'})

    def test_old_quote_failure_does_not_block_independent_supplement(self):
        args = example()
        a = args[3][0]
        a.update(relation='supplement', modality='asserted', old_quote='不存在',
                 validation_errors=['old quote missing or ambiguous'])
        result = build_scope_plan(*args)
        self.assertEqual(len(result['add']), 1)
        self.assertTrue(result['uncertain'])

    def test_temporal_basis_must_include_new_evidence(self):
        args = example()
        args[3][0]['temporal_order']['basis'] = [{'source_id': 'm', 'quote': args[0], 'side': 'old'}]
        self.assertFalse(build_scope_plan(*args)['modify'])

    def test_planned_change_or_non_user_source_never_authorizes_edit(self):
        for defect in ('plan', 'speaker', 'side'):
            args = example()
            if defect == 'plan':
                args[3][0]['modality'] = 'planned'
            elif defect == 'speaker':
                args[2][0]['speaker'] = 'assistant'
            else:
                args[2][0]['side'] = 'old'
            with self.subTest(defect=defect):
                result = build_scope_plan(*args)
                self.assertFalse(result['modify'])
                self.assertTrue(result['uncertain'])
                if defect != 'plan':
                    bad = [x for x in result['quote_checks'] if x['status'] == 'invalid']
                    self.assertTrue(bad)
                    self.assertIsNone(bad[0]['position'])

    def test_same_and_changed_values_from_different_units_conflict(self):
        args = example()
        args[1].append({'id': 'u2', 'memory_id': 'm', 'source_ref': 'old-ref', 'quote': args[0], 'fact': '同一事实'})
        args[2].append({'source_id': 's2', 'source_ref': 's2-ref', 'speaker': 'user', 'side': 'new', 'text': '现在仍是旧价。'})
        other = copy.deepcopy(args[3][0])
        other.update(unit_id='u2', relation='same', new_value='旧', source_id='s2',
                     new_quote='现在仍是旧价。',
                     semantic_basis=[{'source_id': 's2', 'quote': '现在仍是旧价。', 'side': 'new'}])
        args[3].append(other)
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertTrue(any('conflict' in x['reason'] for x in result['uncertain']))
        self.assertFalse(any(x.get('current_evidence_value') == '旧' for x in result['preserve']))

    def test_confirmed_no_impact_can_preserve_without_new_conditions(self):
        args = example()
        args[3][0].update(relation='unrelated', no_impact_confirmed=True, new_conditions=None)
        result = build_scope_plan(*args)
        self.assertEqual(len(result['preserve']), 4)
        self.assertFalse(result['modify'])

    def test_legacy_single_quote_requires_old_memory_id(self):
        args = example()
        del args[1][0]['memory_id']
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        invalid = [x for x in result['quote_checks'] if x['side'] == 'old' and x['status'] == 'invalid']
        self.assertTrue(invalid)
        self.assertIsNone(invalid[0]['position'])

    def test_new_scope_outside_old_scope_is_explicitly_uncertain(self):
        args = example()
        args[3][0]['old_conditions']['dimensions']['城市'] = ['上海']
        args[3][0]['new_conditions']['dimensions']['城市'] = ['上海', '南京']
        result = build_scope_plan(*args)
        self.assertEqual([x['scope'] for x in result['modify']], [{'城市': '上海', '方式': '外带'}])
        self.assertTrue(any(x.get('scope') == {'城市': '南京', '方式': '外带'}
                            and 'outside old scope' in x['reason'] for x in result['uncertain']))

    def test_protected_claim_requires_old_source_identity(self):
        args = example()
        del args[1][0]['memory_id']
        args[1][0]['protected_claims'] = [{'quote': '上海南京', 'fact': '范围'}]
        result = build_scope_plan(*args)
        self.assertFalse(result['protected_facts'])
        self.assertFalse(any(x.get('fact') == '范围' for x in result['preserve']))

    def test_multiple_unit_quotes_each_get_source_and_position_checked(self):
        args = example()
        args[1][:] = [{'id': 'u1', 'memory_id': 'm', 'quote': '上海南京', 'fact': '城市'},
                      {'id': 'u2', 'memory_id': 'm', 'quote': '堂食外带', 'fact': '方式'}]
        a = args[3][0]
        a['unit_id'] = None
        a['old_quotes'] = [{'unit_id': 'u1', 'source_id': 'm', 'quote': '上海南京'},
                           {'unit_id': 'u2', 'source_id': 'm', 'quote': '堂食外带'}]
        result = build_scope_plan(*args)
        checks = [x for x in result['quote_checks'] if x['side'] == 'old']
        self.assertEqual([x['status'] for x in checks], ['valid', 'valid'])
        self.assertEqual([x['position'] for x in checks], [{'start': 0, 'end': 4}, {'start': 4, 'end': 8}])
        self.assertFalse(result['modify'])
        self.assertTrue(result['uncertain'])

    def test_planned_same_value_does_not_assert_current_support(self):
        args = example()
        args[3][0].update(relation='same', new_value='旧', modality='planned')
        result = build_scope_plan(*args)
        self.assertFalse(any('current_evidence_value' in x for x in result['preserve']))
        self.assertTrue(result['uncertain'])

    def test_missing_speaker_or_side_does_not_imply_user_new(self):
        for key in ('speaker', 'side'):
            args = example()
            del args[2][0][key]
            with self.subTest(key=key):
                result = build_scope_plan(*args)
                self.assertFalse(result['modify'])
                self.assertTrue(result['uncertain'])


if __name__ == '__main__':
    unittest.main()
