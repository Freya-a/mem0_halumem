import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scope_planner import build_scope_plan


def sample():
    old = '两店堂食外带均为旧政策。'
    units = [{'id': 'u1', 'quote': old, 'fact': '两店两种服务的旧政策'}]
    sources = [{'source_id': 's1', 'text': '上海外带采用新政策。', 'source_ref': 'session/1'}]
    align = {'unit_id': 'u1', 'relation': 'change', 'old_subject': '店铺', 'new_subject': '店铺',
             'old_attribute': '政策', 'new_attribute': '政策', 'old_value': '旧', 'new_value': '新',
             'old_quote': old, 'new_quote': sources[0]['text'], 'source_id': 's1',
             'old_conditions': {'kind': 'finite', 'dimensions': {'城市': ['上海', '南京'], '服务': ['堂食', '外带']}},
             'new_conditions': {'kind': 'finite', 'dimensions': {'城市': ['上海'], '服务': ['外带']}}}
    return old, units, sources, [align]


class ScopePlannerTests(unittest.TestCase):
    def test_cartesian_difference(self):
        plan = build_scope_plan(*sample())
        self.assertEqual([x['scope'] for x in plan['modify']], [{'城市': '上海', '服务': '外带'}])
        self.assertCountEqual([tuple(sorted(x['scope'].items())) for x in plan['preserve']],
                              [tuple(sorted(x.items())) for x in [
                                  {'城市': '上海', '服务': '堂食'}, {'城市': '南京', '服务': '堂食'},
                                  {'城市': '南京', '服务': '外带'}]])
        self.assertTrue(plan['protected_facts'])
        self.assertEqual(plan['editable_spans'][0]['start'], 0)

    def test_same_values_in_overlap_are_preserved(self):
        args = sample()
        args[3][0]['new_value'] = '旧'
        plan = build_scope_plan(*args)
        self.assertEqual(plan['modify'], [])
        self.assertEqual(len(plan['preserve']), 4)

    def test_missing_scope_is_not_unconditional(self):
        args = sample()
        args[3][0]['new_conditions'] = None
        plan = build_scope_plan(*args)
        self.assertFalse(plan['modify'])
        self.assertIn('condition', str(plan['uncertain']).lower())

    def test_repeated_or_missing_quotes_and_bad_source_block_edits(self):
        for how in ('repeated_old', 'missing_new', 'duplicate_source'):
            old, units, sources, aligns = sample()
            if how == 'repeated_old':
                old += old
            elif how == 'missing_new':
                aligns[0]['new_quote'] = '不存在'
            else:
                sources.append(copy.deepcopy(sources[0]))
            with self.subTest(how=how):
                result = build_scope_plan(old, units, sources, aligns)
                self.assertFalse(result['modify'])
                self.assertTrue(result['uncertain'])
                self.assertFalse(result['editable_spans'])

    def test_plan_is_added_as_plan_not_as_occurred(self):
        args = sample()
        args[3][0]['relation'] = 'plan'
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertEqual(result['add'][0]['relation'], 'plan')
        self.assertTrue(result['preserve'])

    def test_conflicting_new_evidence_blocks_affected_combination(self):
        args = sample()
        args[2].append({'source_id': 's2', 'text': '上海外带采用第三种政策。', 'source_ref': 'session/2'})
        second = copy.deepcopy(args[3][0])
        second.update(source_id='s2', new_quote=args[2][1]['text'], new_value='第三种')
        args[3].append(second)
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertTrue(any('conflict' in x['reason'].lower() for x in result['uncertain']))
        self.assertEqual(len(result['preserve']), 3)

    def test_adapter_missing_reasons_block_edits(self):
        args = sample()
        args[3][0]['missing_reasons'] = ['unknown conditions']
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertIn('unknown conditions', str(result['uncertain']))

    def test_independent_plan_validates_new_source_and_preserves_plan_status(self):
        source = {'source_id': 's', 'text': '我计划下个月游泳。', 'source_ref': 'session/1'}
        claim = {'unit_id': None, 'relation': 'plan', 'new_subject': '我', 'new_attribute': '活动',
                 'new_value': '计划游泳', 'source_id': 's', 'new_quote': source['text']}
        result = build_scope_plan('以前喜欢散步。', [], [source], [claim])
        self.assertEqual(result['add'][0]['relation'], 'plan')
        self.assertFalse(result['modify'])
        claim['new_quote'] = '未出现'
        result = build_scope_plan('以前喜欢散步。', [], [source], [claim])
        self.assertFalse(result['add'])
        self.assertTrue(result['uncertain'])

    def test_unrelated_label_does_not_prove_preservation(self):
        args = sample()
        args[3][0]['relation'] = 'unrelated'
        result = build_scope_plan(*args)
        self.assertFalse(result['preserve'])
        self.assertTrue(result['uncertain'])

    def test_overlapping_unaligned_unit_prevents_edit(self):
        args = sample()
        args[1].append({'id': 'u2', 'quote': '两店堂食外带', 'fact': '旧事实'})
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertFalse(result['editable_spans'])
        self.assertTrue(result['uncertain'])

    def test_quote_with_unknown_source_ref_blocks_action(self):
        args = sample()
        del args[2][0]['source_ref']
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertIn('source_ref', str(result['uncertain']))

    def test_explicit_protected_claim_and_historical_status(self):
        args = sample()
        args[1][0]['protected_claims'] = [{'quote': '两店堂食', 'fact': '堂食范围'}]
        args[3][0]['preserve_history'] = True
        result = build_scope_plan(*args)
        self.assertTrue(any(x.get('fact') == '堂食范围' for x in result['protected_facts']))
        self.assertTrue(any(x.get('fact') == '堂食范围' for x in result['preserve']))
        self.assertTrue(any(x.get('status') == 'historical' for x in result['preserve']))

    def test_plan_add_has_explicit_status_and_unknown_reason_keeps_note(self):
        args = sample()
        args[3][0]['relation'] = 'plan'
        self.assertEqual(build_scope_plan(*args)['add'][0]['status'], 'planned')
        args[3][0]['relation'] = 'unknown'
        args[3][0]['note'] = '旧偏好是否变化仍未知'
        self.assertIn('旧偏好是否变化仍未知', str(build_scope_plan(*args)['uncertain']))

    def test_conflict_across_overlapping_units_holds_edits(self):
        args = sample()
        args[1].append({'id': 'u2', 'quote': args[0], 'fact': '重复提取的同一政策'})
        args[2].append({'source_id': 's2', 'text': '上海外带为第三政策。', 'source_ref': 'session/2'})
        claim = copy.deepcopy(args[3][0])
        claim.update(unit_id='u2', source_id='s2', new_quote=args[2][1]['text'], new_value='第三')
        args[3].append(claim)
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertTrue(any('conflict' in item['reason'] for item in result['uncertain']))

    def test_conflicting_independent_additions_are_not_asserted(self):
        sources = [{'source_id': 's1', 'text': '价格为一元', 'source_ref': 'a'},
                   {'source_id': 's2', 'text': '价格为二元', 'source_ref': 'b'}]
        adds = [{'unit_id': None, 'relation': 'supplement', 'new_subject': '商品', 'new_attribute': '价格',
                 'new_value': price, 'source_id': src['source_id'], 'new_quote': src['text'],
                 'new_conditions': {'kind': 'unconditional'}} for price, src in zip(('一元', '二元'), sources)]
        result = build_scope_plan('旧事实', [], sources, adds)
        self.assertFalse(result['add'])
        self.assertTrue(any('conflict' in item['reason'] for item in result['uncertain']))

    def test_ambiguous_other_unit_overlapping_edit_is_held(self):
        args = sample()
        args = (args[0] + ' 两店堂食', args[1], args[2], args[3])
        args[1].append({'id': 'u2', 'quote': '两店堂食', 'fact': '仍需确定的事实'})
        result = build_scope_plan(*args)
        self.assertFalse(result['modify'])
        self.assertTrue(result['uncertain'])


if __name__ == '__main__':
    unittest.main()
