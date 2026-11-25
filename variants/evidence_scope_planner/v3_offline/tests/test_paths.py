"""Generic, independently reviewed interface examples, not the five cases."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from scope_planner import build_scope_plan

spec = importlib.util.spec_from_file_location('v4_model_interface_for_paths', PROJECT / 'variants/evidence_aligner/v4_scope_interface/interface.py')
interface = importlib.util.module_from_spec(spec)
spec.loader.exec_module(interface)


def source_input(old_text, old_quotes, new_text):
    return interface.prepare_input({'input': {
        'case_id': 'generic',
        'old_units': old_quotes,
        'new_units': [{'unit_id': 'n', 'source_id': 's', 'memory_quotes': [new_text]}],
        'source_texts': {'memory': {'source_id': 'm', 'text': old_text, 'source_ref': 'synthetic:memory'},
                         'messages': [{'source_id': 's', 'text': new_text, 'side': 'new', 'speaker': 'user',
                                       'source_ref': 'synthetic:user'}]}}})


def output_record(**changes):
    data = {'unit_id': None, 'relation': 'new_information', 'old_subject': None, 'new_subject': 'user',
            'old_attribute': None, 'new_attribute': 'preference', 'old_value': None, 'new_value': 'tea',
            'old_conditions': {'kind': 'unknown'}, 'new_conditions': {'kind': 'unconditional'},
            'modality': 'asserted', 'old_quotes': [],
            'new_quotes': [{'unit_id': 'n', 'source_id': 's', 'quote': 'I prefer tea.'}],
            'temporal_order': {'relation': 'unknown', 'basis': [], 'explanation': None},
            'semantic_rationale': 'The user explicitly prefers tea.',
            'semantic_basis': [{'side': 'new', 'source_id': 's', 'quote': 'I prefer tea.'}],
            'uncertainties': []}
    data.update(changes)
    return data


class EvidencePathTests(unittest.TestCase):
    def test_independent_new_fact_requires_and_accepts_separate_review(self):
        payload = source_input('', [], 'I prefer tea.')
        record = output_record()
        model_output = {'records': [record], 'unmatched_old_unit_ids': []}
        self.assertEqual(interface.validate_output(model_output, payload)['status'], 'passed')
        args = interface.planner_inputs(payload, model_output)
        before = build_scope_plan(*args)
        self.assertFalse(before['add'])
        self.assertTrue(before['uncertain'])
        # Independent reviewer read source and confirmed the exact claim; only
        # the separate authorization flag changes, not the raw model output.
        reviewed = copy.deepcopy(args)
        reviewed[3][0]['semantic_support'] = 'supported'
        after = build_scope_plan(*reviewed)
        self.assertEqual(len(after['add']), 1)
        self.assertEqual(after['add'][0]['value'], 'tea')
        self.assertEqual(model_output['records'][0], record)

    def test_explicit_later_change_needs_separate_review_not_calendar_date(self):
        new = 'The room was closed; now it is open.'
        payload = source_input('The room was closed.', [{'unit_id': 'o', 'source_id': 'm', 'memory_quotes': ['closed']}], new)
        record = output_record(unit_id='o', relation='change', old_subject='room', new_subject='room',
            old_attribute='status', new_attribute='status', old_value='closed', new_value='open',
            old_conditions={'kind': 'unconditional'}, new_conditions={'kind': 'same_as_old'},
            old_quotes=[{'unit_id':'o','source_id':'m','quote':'closed'}],
            new_quotes=[{'unit_id':'n','source_id':'s','quote':new}],
            temporal_order={'relation':'after','basis':[{'side':'new','source_id':'s','quote':new}],
                            'explanation':'The new statement explicitly orders closed before now open.'},
            semantic_rationale='Closed before, now open.',
            semantic_basis=[{'side':'new','source_id':'s','quote':new}])
        model_output = {'records':[record], 'unmatched_old_unit_ids':[]}
        self.assertEqual(interface.validate_output(model_output,payload)['status'], 'passed')
        args = interface.planner_inputs(payload,model_output)
        self.assertFalse(build_scope_plan(*args)['modify'])
        reviewed = copy.deepcopy(args)
        reviewed[3][0]['semantic_support'] = 'supported'
        plan = build_scope_plan(*reviewed)
        self.assertEqual(len(plan['modify']), 1)
        self.assertEqual(plan['modify'][0]['old_value'], 'closed')
        self.assertEqual(plan['modify'][0]['new_value'], 'open')
        self.assertEqual(plan['editable_spans'][0]['old_quote'], 'closed')


if __name__ == '__main__':
    unittest.main()
