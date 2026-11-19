import copy
import json
import unittest
from pathlib import Path

from replay import load_case, replay_case
from plan import build_plan

HERE = Path(__file__).resolve().parent


def synthetic():
    case = load_case('synthetic_wednesday_01')
    output = replay_case(case)
    return case, output['upstream']


def control():
    case, relation = synthetic()
    case = copy.deepcopy(case)
    request = case['request']
    text = ('Correction: my old work-from-home rule was wrong from December 1, 2026 onward. '
            'I work from the office on Wednesdays only; my Monday arrangement remains unchanged.')
    request['new_evidence'][0]['text'] = text
    source = 'new-1'
    unit = case['new_unit']
    for f in ('subject', 'attribute', 'weekdays'):
        unit[f]['evidence'] = [{'source_id': source, 'quote': text}]
    for f in ('start', 'end'):
        unit['valid'][f]['evidence'] = [{'source_id': source, 'quote': text}]
    case['correction'] = {'status':'explicit_verified', 'source_id':source, 'quote':text,
                          'old_attribute':'work_location', 'reason':'Explicitly corrects the previous rule for the specified Wednesday range.'}
    candidate = relation['results'][0]['candidate']
    candidate['relation'] = 'historical_correction'
    candidate['candidate_impact_fragment'] = 'work from home'
    candidate['new_quote'] = {'source_id':source, 'quote':text}
    relation['results'][0]['located_candidate'] = copy.deepcopy(candidate)
    relation['results'][0]['raw_output'] = json.dumps(candidate)
    return case, relation


class ScopePlanTests(unittest.TestCase):
    def test_correction_modifies_only_wednesday_after_boundary_and_preserves_remainder(self):
        case, relation = control()
        plan = build_plan(case['request'], relation, case)
        self.assertEqual(len(plan['modify']), 1)
        edit = plan['modify'][0]
        self.assertEqual(edit['attribute'], 'work_location')
        self.assertEqual(edit['conditions']['weekdays']['days'], [2])
        self.assertEqual(edit['conditions']['valid']['start']['value'], '2026-12-01')
        self.assertEqual(edit['old_fragment'], 'work from home')
        preserved = [p['conditions'] for p in plan['preserve'] if p['attribute'] == 'work_location']
        self.assertTrue(any(p['weekdays']['days'] == [0] for p in preserved))
        self.assertTrue(any(p['weekdays']['days'] == [2] and p['valid']['end']['value'] == '2026-11-30' for p in preserved))
        self.assertTrue(plan['add'])

    def test_possible_change_cannot_authorize_modification(self):
        case, relation = synthetic()
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('possible_change', {x['code'] for x in plan['uncertain']})
        self.assertFalse(any(x['code'] == 'hold_provisional' for x in plan['preserve']))
        affected = [x for x in plan['uncertain'] if x['code'] == 'scope_overlap_unconfirmed']
        self.assertEqual(affected[0]['conditions']['weekdays']['days'], [2])

    def test_missing_boundary_does_not_modify_or_invent_date(self):
        case, relation = control()
        case['new_unit']['valid']['start'] = {'kind':'unknown'}
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('boundary_unknown', {x['code'] for x in plan['uncertain']})
        self.assertNotIn('2026-12-01', json.dumps([x['conditions'] for x in plan['modify']]))

    def test_correction_without_explicit_structured_evidence_never_modifies(self):
        case, relation = control()
        del case['correction']
        self.assertFalse(build_plan(case['request'], relation, case)['modify'])

    def test_overbroad_candidate_cannot_be_used_without_structured_attribute_mapping(self):
        case = load_case('promotion')
        data = json.loads((HERE / case['baseline_path']).resolve().read_text())
        plan = build_plan(data['input'], data['result'])
        self.assertFalse(plan['modify'])
        self.assertIn('attribute_unlocalized', {x['code'] for x in plan['uncertain']})
        self.assertTrue(any(x['reason'] for x in plan['uncertain']))

    def test_support_never_authorizes_modification(self):
        case = load_case('job_transition')
        data = json.loads((HERE / case['baseline_path']).resolve().read_text())
        plan = build_plan(data['input'], data['result'])
        self.assertFalse(plan['modify'])
        self.assertIn('support_not_change', {x['code'] for x in plan['uncertain']})

    def test_all_items_have_required_provenance_and_scope_fields(self):
        case, relation = control()
        case2, relation2 = synthetic()
        plans = [build_plan(case['request'], relation, case), build_plan(case2['request'], relation2, case2)]
        for category in ('modify','preserve','uncertain','add'):
            rows = [row for plan in plans for row in plan[category]]
            self.assertTrue(rows, category)
            for row in rows:
                self.assertTrue({'old_fact_id','old_quote','new_evidence','attribute','conditions','reason'} <= row.keys())
                self.assertTrue(row['old_quote'])
                self.assertTrue(row['new_evidence'])
                self.assertTrue(row['reason'])

    def test_bad_upstream_fails_closed(self):
        case, relation = control()
        relation['results'][0]['status'] = 'error'
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('upstream_error', {x['code'] for x in plan['uncertain']})
        self.assertEqual(plan['uncertain'][0]['new_evidence'][0]['quote'], case['request']['new_evidence'][0]['text'])

    def test_original_component_result_is_preserved(self):
        case, relation = synthetic()
        original = copy.deepcopy(relation)
        plan = build_plan(case['request'], relation, case)
        self.assertEqual(plan['upstream_original'], original)
        self.assertEqual(relation, original)

    def test_overlapping_protected_attribute_blocks_edit(self):
        case, relation = control()
        duplicate = copy.deepcopy(case['old_units'][0])
        duplicate['name'] = 'different_attribute_same_text'
        duplicate['attribute']['value'] = 'other_attribute'
        case['old_units'].append(duplicate)
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('protection_overlap', {x['code'] for x in plan['uncertain']})

    def test_modify_old_quote_must_cover_modified_fragment(self):
        case, relation = control()
        fact = case['request']['split_result']['facts'][0]
        mid = case['request']['split_result']['memory_id']
        fact['evidence'] = [
            {'source_type':'memory', 'source_id':mid, 'quote':'Mondays'},
            {'source_type':'memory', 'source_id':mid, 'quote':'work from home'},
        ]
        candidate = relation['results'][0]['candidate']
        candidate['old_quote'] = 'work from home'
        relation['results'][0]['raw_output'] = json.dumps(candidate)
        relation['results'][0]['located_candidate'] = copy.deepcopy(candidate)
        plan = build_plan(case['request'], relation, case)
        self.assertEqual(len(plan['modify']), 1)
        self.assertIn(plan['modify'][0]['old_fragment'], plan['modify'][0]['old_quote'])

    def test_missing_structured_old_unit_is_uncertain(self):
        case, relation = control()
        case['old_units'] = []
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('old_scope_missing', {x['code'] for x in plan['uncertain']})

    def test_cross_fact_protection_blocks_overlapping_edit(self):
        case, relation = control()
        case['old_units'][0]['fact_index'] = 1
        second = copy.deepcopy(case['old_units'][0])
        second.update(name='other_fact', fact_index=2)
        second['attribute']['value'] = 'other_attribute'
        case['old_units'].append(second)
        fact = copy.deepcopy(case['request']['split_result']['facts'][0])
        fact['fact_index'] = 2
        case['request']['split_result']['facts'].append(fact)
        row = copy.deepcopy(relation['results'][0])
        row['fact_index'] = 2
        for key in ('candidate', 'located_candidate'):
            row[key]['fact_index'] = 2
        row['raw_output'] = json.dumps(row['candidate'])
        relation['results'].append(row)
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertIn('protection_overlap', {x['code'] for x in plan['uncertain']})

    def test_untagged_structured_units_cannot_apply_to_multiple_facts(self):
        case, relation = control()
        fact = copy.deepcopy(case['request']['split_result']['facts'][0])
        fact['fact_index'] = 2
        case['request']['split_result']['facts'].append(fact)
        row = copy.deepcopy(relation['results'][0])
        row['fact_index'] = 2
        for key in ('candidate', 'located_candidate'):
            row[key]['fact_index'] = 2
        row['raw_output'] = json.dumps(row['candidate'])
        relation['results'].append(row)
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertEqual(sum(x['code'] == 'old_scope_missing' for x in plan['uncertain']), 2)

    def test_overlapping_edits_on_two_facts_are_not_duplicated(self):
        case, relation = control()
        case['old_units'][0]['fact_index'] = 1
        second = copy.deepcopy(case['old_units'][0])
        second.update(name='other_fact', fact_index=2)
        case['old_units'].append(second)
        fact = copy.deepcopy(case['request']['split_result']['facts'][0])
        fact['fact_index'] = 2
        case['request']['split_result']['facts'].append(fact)
        row = copy.deepcopy(relation['results'][0])
        row['fact_index'] = 2
        for key in ('candidate', 'located_candidate'):
            row[key]['fact_index'] = 2
        row['raw_output'] = json.dumps(row['candidate'])
        relation['results'].append(row)
        plan = build_plan(case['request'], relation, case)
        self.assertFalse(plan['modify'])
        self.assertEqual(sum(x['code'] == 'modification_overlap' for x in plan['uncertain']), 2)
