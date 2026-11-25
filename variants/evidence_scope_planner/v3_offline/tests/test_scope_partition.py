import copy
import unittest
from test_v2_planner import example
from scope_planner import build_scope_plan

class PartitionTests(unittest.TestCase):
    def test_unconditional_old_finite_new_intersection_and_unrepresentable_remainder(self):
        old, units, sources, alignments = example()
        a = alignments[0]
        a['old_conditions'] = {'kind':'unconditional'}
        result = build_scope_plan(old, units, sources, alignments)
        self.assertEqual([x['scope'] for x in result['modify']], [{'城市':'上海','方式':'外带'}])
        self.assertEqual(result['preserve'], [])
        self.assertTrue(any(x.get('scope') == {'kind':'unknown'} and 'remainder' in x['reason'].lower() for x in result['uncertain']))
        self.assertTrue(result['editable_spans'])
        self.assertTrue(any(x.get('protected_scope') == 'unrepresented_remainder'
                            and x.get('scope') == {'kind':'unknown'}
                            and x.get('old_quote') == old for x in result['protected_facts']))

    def test_unconditional_and_finite_with_missing_semantic_support_does_not_modify(self):
        args = example(); args[3][0]['old_conditions'] = {'kind':'unconditional'}
        del args[3][0]['semantic_support']
        result = build_scope_plan(*args)
        self.assertFalse(result['modify']); self.assertFalse(result['preserve'])
        self.assertTrue(any(x.get('scope') == {'城市':'上海','方式':'外带'} for x in result['uncertain']))
        self.assertTrue(any('remainder' in x['reason'].lower() for x in result['uncertain']))

    def test_unknown_old_range_cannot_prove_intersection(self):
        args = example(); args[3][0]['old_conditions'] = {'kind':'unknown'}
        result = build_scope_plan(*args)
        self.assertFalse(result['modify']); self.assertFalse(result['preserve'])
        self.assertTrue(result['uncertain'])
        self.assertTrue(any('condition' in x['reason'].lower() for x in result['uncertain']))

    def test_mismatched_dimension_names_never_compare_equal_tuples(self):
        args = example()
        args[3][0]['old_conditions'] = {'kind':'finite','dimensions':{'city':['上海']}}
        args[3][0]['new_conditions'] = {'kind':'finite','dimensions':{'service':['外带']}}
        result=build_scope_plan(*args)
        self.assertFalse(result['modify']); self.assertFalse(result['preserve'])
        self.assertTrue(any('dimension' in x['reason'].lower() for x in result['uncertain']))

    def test_unrestricted_finite_records_with_different_axes_stay_uncertain(self):
        args=example();a=args[3][0];a['old_conditions']={'kind':'unconditional'}
        b=copy.deepcopy(a);b['new_conditions']={'kind':'finite','dimensions':{'city':['上海']}}
        args[3].append(b);result=build_scope_plan(*args)
        self.assertFalse(result['modify']);self.assertFalse(result['preserve']);self.assertTrue(result['uncertain'])

    def test_unreviewed_finite_scope_cannot_prove_remainder_unaffected(self):
        for defect in ('semantic', 'source', 'validation'):
            args=example(); a=args[3][0]
            if defect=='semantic': a['semantic_support']='unknown'
            elif defect=='source': a['source_id']='not-a-source'
            else: a['validation_errors']=['unverified model scope binding']
            with self.subTest(defect=defect):
                result=build_scope_plan(*args)
                self.assertFalse(result['modify']); self.assertFalse(result['preserve'])
                self.assertEqual(len(result['uncertain']),4)
                self.assertTrue(all('scope' in x and 'unknown' not in x['scope'].values() for x in result['uncertain']))

    def test_edit_span_protects_uncertain_combination_inside_same_old_sentence(self):
        args=example(); other=copy.deepcopy(args[3][0]); other['relation']='unknown'
        other['new_conditions']['dimensions']['城市']=['南京']
        args[3].append(other); plan=build_scope_plan(*args)
        self.assertEqual(len(plan['modify']),1)
        target={'城市':'南京','方式':'外带'}
        self.assertTrue(any(x.get('scope')==target for x in plan['uncertain']))
        self.assertFalse(any(x.get('scope')==target for x in plan['preserve']))
        self.assertTrue(any(x.get('scope')==target and x.get('status')=='uncertain'
                            and x.get('protected_scope')=='uncertain' for x in plan['protected_facts']))

    def test_edit_span_protects_uncertain_overlapping_other_unit(self):
        args=example();args[1].append({'id':'u2','memory_id':'m','source_ref':'old-ref','quote':args[0],'fact':'另一单元'})
        other=copy.deepcopy(args[3][0]);other['unit_id']='u2';other['relation']='unknown'
        other['old_attribute']=other['new_attribute']='服务范围'
        other['new_conditions']['dimensions']['城市']=['南京'];args[3].append(other)
        plan=build_scope_plan(*args);target={'城市':'南京','方式':'外带'}
        self.assertEqual(len(plan['modify']),1)
        self.assertTrue(any(x.get('unit_id')=='u2' and x.get('scope')==target
                            and x.get('status')=='uncertain' and x.get('protected_scope')=='uncertain'
                            for x in plan['protected_facts']))

    def test_change_cannot_conflict_with_derived_preserve_of_other_unit(self):
        args=example();args[1].append({'id':'u2','memory_id':'m','source_ref':'old-ref','quote':args[0],'fact':'另一单元'})
        other=copy.deepcopy(args[3][0]);other['unit_id']='u2';other['relation']='unknown'
        other['new_conditions']['dimensions']['城市']=['南京'];args[3].append(other)
        plan=build_scope_plan(*args);target={'城市':'上海','方式':'外带'}
        self.assertFalse(any(x.get('scope')==target for x in plan['modify']))
        self.assertFalse(any(x.get('unit_id')=='u2' and x.get('scope')==target for x in plan['preserve']))
        self.assertTrue(any('conflict' in x['reason'] for x in plan['uncertain']))

    def test_missing_alignment_quote_uses_unit_quote_to_hold_overlapping_edit(self):
        args=example();args[1].append({'id':'u2','memory_id':'m','source_ref':'old-ref','quote':args[0],'fact':'另一单元'})
        other=copy.deepcopy(args[3][0]);other.update(unit_id='u2',relation='unknown',old_quote=None)
        other['old_attribute']=other['new_attribute']='另一属性'
        other['new_conditions']['dimensions']['城市']=['南京'];args[3].append(other)
        plan=build_scope_plan(*args)
        self.assertFalse(plan['modify']);self.assertFalse(plan['editable_spans'])
        self.assertTrue(any('overlaps unresolved' in x['reason'] for x in plan['uncertain']))

    def test_repeated_unresolved_unit_quote_checks_all_possible_positions(self):
        old,units,sources,alignments=example();old='甲'+old+'乙'+old
        units[0]['quote']='甲上海南京堂食外带旧价。';alignments[0]['old_quote']=units[0]['quote']
        units.append({'id':'u2','memory_id':'m','source_ref':'old-ref','quote':'上海南京堂食外带旧价。','fact':'重复单元'})
        other=copy.deepcopy(alignments[0]);other.update(unit_id='u2',relation='unknown',old_quote='上海南京堂食外带旧价。')
        other['old_attribute']=other['new_attribute']='另一属性'
        other['new_conditions']['dimensions']['城市']=['南京'];alignments.append(other)
        plan=build_scope_plan(old,units,sources,alignments)
        self.assertFalse(plan['modify']);self.assertFalse(plan['editable_spans'])
        self.assertTrue(any(x.get('side')=='old' and x.get('unit_id')=='u2'
                            and x.get('status')=='invalid' and x.get('position') is None for x in plan['quote_checks']))

    def test_mixed_dimension_key_types_are_uncertain_not_a_crash(self):
        args=example();args[3][0]['old_conditions']={'kind':'finite','dimensions':{'城市':['上海'],1:['外带']}}
        plan=build_scope_plan(*args)
        self.assertFalse(plan['modify']);self.assertFalse(plan['preserve']);self.assertTrue(plan['uncertain'])
