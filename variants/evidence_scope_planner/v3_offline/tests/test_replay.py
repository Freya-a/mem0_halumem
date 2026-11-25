import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from replay import compare_same_input, fingerprint


class Planner:
    def __init__(self, marker):
        self.marker = marker
    def build_scope_plan(self, old, units, sources, alignments):
        return {'modify': [], 'preserve': [], 'uncertain': [], 'add': [],
                'received': {'old': old, 'units': units, 'sources': sources, 'alignments': alignments},
                'marker': self.marker}


class MutatingPlanner(Planner):
    def build_scope_plan(self, old, units, sources, alignments):
        alignments[0]['changed'] = True
        return super().build_scope_plan(old, units, sources, alignments)


class ReplayTests(unittest.TestCase):
    def test_same_input_copied_and_hashed_for_two_planners(self):
        args = ('old', [{'id': 'u'}], [{'source_id': 's'}], [{'unit_id': 'u'}])
        before = copy.deepcopy(args)
        result = compare_same_input(args, Planner('old'), Planner('new'))
        self.assertEqual(args, before)
        self.assertEqual(result['v2']['received'], result['v3']['received'])
        self.assertEqual(result['input_sha256'], fingerprint(args))

    def test_caller_and_other_planner_isolated_from_mutation(self):
        args = ('old', [{'id': 'u'}], [{'source_id': 's'}], [{'unit_id': 'u'}])
        result = compare_same_input(args, MutatingPlanner('old'), Planner('new'))
        self.assertNotIn('changed', args[3][0])
        self.assertNotIn('changed', result['v3']['received']['alignments'][0])
        self.assertEqual(result['input_sha256'], fingerprint(args))


if __name__ == '__main__':
    unittest.main()
