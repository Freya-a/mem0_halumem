import json
import unittest
from pathlib import Path
from copy import deepcopy

from replay import load_case, replay_case

HERE = Path(__file__).resolve().parent


class ReplayTests(unittest.TestCase):
    def test_three_cases_match_separate_human_expectations(self):
        expected = json.loads((HERE / 'cases' / 'expected.json').read_text())
        for name, wanted in expected.items():
            with self.subTest(case=name):
                result = replay_case(load_case(name))
                self.assertEqual(result['baseline_relation'], wanted['baseline_relation'])
                self.assertEqual(result['candidate_attributes'], wanted['candidate_attributes'])
                self.assertEqual({k: v['status'] for k, v in result['comparisons'].items()}, wanted['comparisons'])
                for k, values in wanted.get('missing_contains', {}).items():
                    self.assertTrue(set(values) <= set(result['comparisons'][k]['missing']))
                if name == 'synthetic_wednesday_01':
                    row = result['upstream']['results'][0]
                    self.assertTrue(row['validation']['passed'])
                    self.assertEqual(row['validation']['semantic_correctness'], 'not_checked')
                    self.assertEqual(result['comparisons']['wednesday']['intersection']['weekdays']['days'], [2])
                    self.assertEqual(result['comparisons']['wednesday']['intersection']['valid']['start']['value'], '2026-12-01')

    def test_baseline_is_preserved_and_experiment_separate(self):
        for name in ('promotion', 'job_transition'):
            case = load_case(name)
            result = replay_case(case)
            original = json.loads((HERE / case['baseline_path']).resolve().read_text())
            experiment = json.loads((HERE / case['experiment_path']).resolve().read_text())
            self.assertEqual(result['upstream'], original['result'])
            self.assertEqual(result['experiment']['candidate'], experiment['result']['results'][0]['candidate'])
            self.assertEqual(result['baseline_source'], case['baseline_path'])

    def test_tampered_evidence_rejected(self):
        case = deepcopy(load_case('promotion'))
        case['old_units'][0]['attribute']['evidence'][0]['quote'] = 'fabricated quote'
        with self.assertRaisesRegex(ValueError, 'evidence'):
            replay_case(case)

    def test_known_scope_fields_require_evidence(self):
        for part in ('subject', 'attribute', 'weekdays', 'start', 'end'):
            with self.subTest(part=part):
                case = deepcopy(load_case('synthetic_wednesday_01'))
                unit = case['new_unit']
                field = unit['valid'][part] if part in ('start', 'end') else unit[part]
                field['evidence'] = []
                with self.assertRaisesRegex(ValueError, 'evidence'):
                    replay_case(case)

    def test_old_scope_cannot_cite_new_source_as_old_evidence(self):
        case = deepcopy(load_case('synthetic_wednesday_01'))
        quote = case['request']['new_evidence'][0]['text']
        case['old_units'][0]['attribute']['evidence'] = [{'source_id': 'new-1', 'quote': quote}]
        with self.assertRaisesRegex(ValueError, 'evidence'):
            replay_case(case)

    def test_manual_expected_results_are_not_read_by_replay(self):
        result = replay_case(load_case('synthetic_wednesday_01'))
        self.assertNotIn('expected', result)
        self.assertEqual(result['upstream_origin'], 'synthetic_mock_backend')


if __name__ == '__main__': unittest.main()
