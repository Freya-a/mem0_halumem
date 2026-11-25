import unittest
import importlib.util
from pathlib import Path
from interface import prepare_input, validate_output, adapt_output, planner_inputs


def artifact():
    return {'input': {'old_units': [{'unit_id': 'o', 'source_id': 'm', 'memory_quotes': ['Director'], 'upstream_manual_unit': {'answer': 'do not use'}, 'raw_statement': 'title'}],
                      'new_units': [{'unit_id': 'n', 'source_id': 's', 'memory_quotes': ['I got promoted.'], 'upstream_manual_unit': {'answer': 'do not use'}}],
                      'source_texts': {'memory': {'source_id': 'm', 'text': 'Works as Director', 'source_ref': 'old'},
                                       'messages': [{'source_id': 's', 'side': 'new', 'speaker': 'user', 'text': 'I got promoted.', 'source_ref': 'new'},
                                                    {'source_id': 'a', 'side': 'new', 'speaker': 'assistant', 'text': 'I got promoted.', 'source_ref': 'other'}]}}}


def record():
    return {'unit_id': 'o', 'relation': 'change', 'old_subject': 'user', 'new_subject': 'user', 'old_attribute': 'title', 'new_attribute': 'title', 'old_value': 'Director', 'new_value': None,
            'old_conditions': {'kind': 'unknown'}, 'new_conditions': {'kind': 'unknown'}, 'modality': 'asserted',
            'old_quotes': [{'unit_id': 'o', 'source_id': 'm', 'quote': 'Director'}],
            'new_quotes': [{'unit_id': 'n', 'source_id': 's', 'quote': 'I got promoted.'}],
            'temporal_order': {'relation': 'unknown', 'basis': [], 'explanation': '相对于旧状态的先后未知'},
            'semantic_rationale': '晋升已发生，但未知旧状态时序',
            'semantic_basis': [{'side': 'new', 'source_id': 's', 'quote': 'I got promoted.'}],
            'uncertainties': ['新职位名称未知']}


class InterfaceTests(unittest.TestCase):
    def test_preparation_removes_manual_mapping_but_keeps_full_context(self):
        p = prepare_input(artifact())
        self.assertNotIn('upstream_manual_unit', p['old_units'][0]); self.assertNotIn('raw_statement', p['old_units'][0])
        self.assertEqual(len(p['source_texts']['messages']), 2)

    def test_missing_old_source_can_only_be_bound_by_unique_exact_old_quote(self):
        a=artifact(); del a['input']['old_units'][0]['source_id']
        p=prepare_input(a); self.assertEqual(p['old_units'][0]['source_id'],'m')
        self.assertEqual(p['old_units'][0]['source_binding'],'unique_quote_in_old_memory')
        a['input']['source_texts']['memory']['text']='Director Director'
        self.assertIsNone(prepare_input(a)['old_units'][0]['source_id'])
        a['input']['source_texts']['memory']['text']='Director'
        a['input']['old_units'][0]['source_id']='wrong'
        self.assertEqual(prepare_input(a)['old_units'][0]['source_id'],'wrong')

    def test_valid_structure_does_not_require_date_and_does_not_self_approve(self):
        p = prepare_input(artifact()); out = {'records':[record()], 'unmatched_old_unit_ids':[]}
        result = validate_output(out, p); self.assertEqual(result['status'], 'passed', result)
        a = adapt_output(out, p)[0]; self.assertEqual(a['semantic_support'], 'unknown')
        self.assertEqual(a['semantic_rationale'], record()['semantic_rationale'])
        self.assertEqual(a['temporal_order']['relation'], 'unknown')
        old, units, sources, aligned = planner_inputs(p, out)
        self.assertEqual(old, 'Works as Director'); self.assertEqual(units[0]['memory_id'], 'm'); self.assertEqual(len(sources),1)

    def test_source_and_linked_unit_must_match(self):
        p=prepare_input(artifact()); r=record(); r['new_quotes'][0]['source_id']='a'
        v=validate_output({'records':[r],'unmatched_old_unit_ids':[]},p)
        self.assertEqual(v['status'],'failed'); self.assertEqual(v['schema_status'],'passed'); self.assertEqual(v['quote_status'],'failed'); self.assertTrue(v['record_errors'][0]); self.assertEqual(adapt_output({'records':[r],'unmatched_old_unit_ids':[]},p)[0]['semantic_support'],'unknown')

    def test_repeated_quote_and_unrelated_basis_rejected(self):
        a=artifact(); a['input']['source_texts']['messages'][0]['text']='I got promoted. I got promoted.';p=prepare_input(a)
        v=validate_output({'records':[record()],'unmatched_old_unit_ids':[]},p)
        self.assertEqual(v['status'],'failed'); self.assertTrue(any(c.get('status')!='valid' for c in v['quote_checks']))

    def test_missing_field_or_fake_unknown_values_are_not_silently_coerced(self):
        p=prepare_input(artifact()); r=record(); del r['modality']
        self.assertEqual(validate_output({'records':[r],'unmatched_old_unit_ids':[]},p)['status'],'failed')
        r=record(); r['new_value']='unknown'
        self.assertEqual(validate_output({'records':[r],'unmatched_old_unit_ids':[]},p)['status'],'failed')

    def test_no_cross_source_basis_and_no_unmatched_new_evidence(self):
        p=prepare_input(artifact()); r=record();r['semantic_basis']=[{'side':'new','source_id':'a','quote':'I got promoted.'}]
        self.assertEqual(validate_output({'records':[r],'unmatched_old_unit_ids':[]},p)['status'],'failed')
        self.assertEqual(validate_output({'records':[],'unmatched_old_unit_ids':['o']},p)['status'],'failed')

    def test_malformed_container_fields_report_instead_of_crashing(self):
        p=prepare_input(artifact())
        planner_path=Path(__file__).resolve().parents[3]/'evidence_scope_planner/v2_offline/scope_planner.py'
        spec=importlib.util.spec_from_file_location('v2_planner_malformed',planner_path)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for field, value in (('relation', []), ('unit_id', []), ('modality', {}),
                             ('old_conditions', {'kind': []}), ('temporal_order', {'relation': [], 'basis': [], 'explanation':None})):
            with self.subTest(field=field):
                r=record(); r[field]=value; output={'records':[r],'unmatched_old_unit_ids':[]}
                self.assertEqual(validate_output(output,p)['status'],'failed')
                self.assertTrue(validate_output(output,p)['errors'])
                args=planner_inputs(p,output)
                self.assertEqual(len(args[3]),2 if field == 'unit_id' else 1)
                self.assertEqual(args[3][0]['raw_record'][field],value)
                plan=mod.build_scope_plan(*args)
                self.assertFalse(plan['modify']); self.assertTrue(plan['uncertain'])
        r=record();r['new_quotes'][0]['source_id']=[]
        out={'records':[r],'unmatched_old_unit_ids':[]}
        self.assertEqual(validate_output(out,p)['status'],'failed')
        self.assertFalse(mod.build_scope_plan(*planner_inputs(p,out))['modify'])

    def test_real_planner_requires_independent_review_then_accepts_valid_case(self):
        a=artifact(); text='I used to be Director; now I am lead director.'
        a['input']['new_units'][0]['memory_quotes']=[text]
        a['input']['source_texts']['messages'][0]['text']=text
        p=prepare_input(a); r=record(); r['new_value']='lead director'
        r['old_conditions']={'kind':'unconditional'}; r['new_conditions']={'kind':'same_as_old'}
        r['new_quotes']=[{'unit_id':'n','source_id':'s','quote':text}]
        r['semantic_basis']=[{'side':'new','source_id':'s','quote':text}]
        r['temporal_order']={'relation':'after','basis':[{'side':'new','source_id':'s','quote':text}], 'explanation':'用户明确说旧职位在前、现在的新职位在后。'}
        out={'records':[r],'unmatched_old_unit_ids':[]}; self.assertEqual(validate_output(out,p)['status'],'passed')
        planner_path=Path(__file__).resolve().parents[3]/'evidence_scope_planner/v2_offline/scope_planner.py'
        spec=importlib.util.spec_from_file_location('v2_planner_integration',planner_path)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        args=planner_inputs(p,out); result=mod.build_scope_plan(*args)
        self.assertFalse(result['modify']); self.assertTrue(result['uncertain'])
        # Only this independent review flag is changed; no semantic field is fabricated.
        args[3][0]['semantic_support']='supported'
        reviewed=mod.build_scope_plan(*args)
        self.assertEqual(len(reviewed['modify']),1)
        self.assertEqual(reviewed['modify'][0]['old_quote'],'Director')

    def test_unconditional_old_finite_new_does_not_become_unconditional_preserve(self):
        p=prepare_input(artifact()); r=record()
        r['old_conditions']={'kind':'unconditional'}
        r['new_conditions']={'kind':'finite','dimensions':{'context':['simulated']}}
        out={'records':[r],'unmatched_old_unit_ids':[]}
        self.assertEqual(validate_output(out,p)['status'],'passed')
        args=planner_inputs(p,out)
        self.assertEqual(args[3][0]['raw_record']['new_conditions'],r['new_conditions'])
        self.assertEqual(args[3][0]['new_conditions'],{'kind':'unknown'})
        self.assertTrue(any('unconditional' in str(e) and 'finite' in str(e) for e in args[3][0]['validation_errors']))
        planner_path=Path(__file__).resolve().parents[3]/'evidence_scope_planner/v2_offline/scope_planner.py'
        spec=importlib.util.spec_from_file_location('v2_planner_finite_guard',planner_path)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        plan=mod.build_scope_plan(*args)
        self.assertFalse(plan['preserve']); self.assertFalse(plan['modify']); self.assertTrue(plan['uncertain'])

    def test_mismatched_finite_dimensions_do_not_become_full_preserve(self):
        p=prepare_input(artifact()); r=record()
        r['old_conditions']={'kind':'finite','dimensions':{'activity':['real']}}
        r['new_conditions']={'kind':'finite','dimensions':{'setting':['simulated']}}
        out={'records':[r],'unmatched_old_unit_ids':[]}
        self.assertEqual(validate_output(out,p)['status'],'passed')
        args=planner_inputs(p,out)
        self.assertEqual(args[3][0]['raw_record']['new_conditions'],r['new_conditions'])
        self.assertEqual(args[3][0]['new_conditions'],{'kind':'unknown'})
        self.assertTrue(any('dimensions' in str(e) for e in args[3][0]['validation_errors']))
        planner_path=Path(__file__).resolve().parents[3]/'evidence_scope_planner/v2_offline/scope_planner.py'
        spec=importlib.util.spec_from_file_location('v2_planner_dimension_guard',planner_path)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        plan=mod.build_scope_plan(*args)
        self.assertFalse(plan['preserve']); self.assertFalse(plan['modify']); self.assertTrue(plan['uncertain'])

    def test_guarded_supplement_cannot_add_with_lost_finite_scope(self):
        p=prepare_input(artifact()); r=record()
        r['relation']='supplement'; r['new_value']='observed event'
        r['old_conditions']={'kind':'unconditional'}
        r['new_conditions']={'kind':'finite','dimensions':{'context':['simulated']}}
        out={'records':[r],'unmatched_old_unit_ids':[]}
        self.assertEqual(validate_output(out,p)['status'],'passed')
        args=planner_inputs(p,out); args[3][0]['semantic_support']='supported'
        planner_path=Path(__file__).resolve().parents[3]/'evidence_scope_planner/v2_offline/scope_planner.py'
        spec=importlib.util.spec_from_file_location('v2_planner_supplement_guard',planner_path)
        mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        plan=mod.build_scope_plan(*args)
        self.assertFalse(plan['add']); self.assertFalse(plan['modify']); self.assertTrue(plan['uncertain'])
        self.assertEqual(args[3][0]['raw_record']['new_conditions'],r['new_conditions'])

if __name__=='__main__': unittest.main()
