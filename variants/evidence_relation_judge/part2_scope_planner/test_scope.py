import unittest
from datetime import date

from scope import Bound, Evidence, Interval, Weekdays, Field, Scope, compare


class ScopeTests(unittest.TestCase):
    def setUp(self):
        self.subject = Field.known('user')
        self.attribute = Field.known('work_location')

    def scope(self, days, start, end):
        return Scope(self.subject, self.attribute, days, Interval(start, end))

    def test_wednesday_from_effective_date_and_monday_disjoint(self):
        old = self.scope(Weekdays.known({0, 2}), Bound.known('2026-01-01'), Bound.unbounded())
        new = self.scope(Weekdays.known({2}), Bound.known('2026-12-01'), Bound.unbounded())
        r = compare(old, new)
        self.assertEqual(r.status, 'overlap')
        self.assertEqual(r.intersection.weekdays.days, frozenset({2}))
        self.assertEqual(r.intersection.valid.start.value, date(2026, 12, 1))
        self.assertEqual(r.intersection.valid.end.kind, 'unbounded')
        monday = self.scope(Weekdays.known({0}), Bound.known('2026-01-01'), Bound.unbounded())
        self.assertEqual(compare(monday, new).status, 'disjoint')

    def test_complete_containment(self):
        outer = self.scope(Weekdays.all(), Bound.known('2026-01-01'), Bound.known('2026-12-31'))
        inner = self.scope(Weekdays.all(), Bound.known('2026-03-01'), Bound.known('2026-04-01'))
        r = compare(outer, inner)
        self.assertEqual(r.status, 'overlap')
        self.assertEqual(r.intersection.valid, inner.valid)

    def test_missing_effective_date_stays_unknown_and_observation_is_not_start(self):
        old = self.scope(Weekdays.all(), Bound.unknown(), Bound.unknown())
        new = Scope(self.subject, self.attribute, Weekdays.all(), Interval(Bound.unknown(), Bound.unknown()), observation='2026-03-01')
        r = compare(old, new)
        self.assertEqual(r.status, 'unknown')
        self.assertIn('old.valid.start', r.missing)
        self.assertIn('new.valid.start', r.missing)
        self.assertEqual(new.valid.start.kind, 'unknown')

    def test_known_disjoint_overrides_unknown(self):
        a = self.scope(Weekdays.known({0}), Bound.unknown(), Bound.unknown())
        b = self.scope(Weekdays.known({2}), Bound.unknown(), Bound.unknown())
        self.assertEqual(compare(a, b).status, 'disjoint')

    def test_closed_endpoint_touch_and_calendar_filter(self):
        a = self.scope(Weekdays.all(), Bound.known('2026-12-01'), Bound.known('2026-12-02'))
        b = self.scope(Weekdays.known({2}), Bound.known('2026-12-02'), Bound.known('2026-12-03'))
        self.assertEqual(compare(a, b).status, 'overlap')
        tuesday = self.scope(Weekdays.known({1}), Bound.known('2026-12-02'), Bound.known('2026-12-02'))
        self.assertEqual(compare(a, tuesday).status, 'disjoint')

    def test_known_separate_intervals_and_different_attribute(self):
        a = self.scope(Weekdays.all(), Bound.known('2026-01-01'), Bound.known('2026-01-31'))
        b = self.scope(Weekdays.all(), Bound.known('2026-02-01'), Bound.unknown())
        self.assertEqual(compare(a, b).status, 'disjoint')
        c = Scope(self.subject, Field.known('employer'), Weekdays.all(), Interval(Bound.unknown(), Bound.unknown()))
        self.assertEqual(compare(a, c).status, 'disjoint')

    def test_unknown_weekday_returns_partial_evidence_not_known_intersection(self):
        a = self.scope(Weekdays.unknown(), Bound.unbounded(), Bound.unbounded())
        b = self.scope(Weekdays.known({2}), Bound.unbounded(), Bound.unbounded())
        r = compare(a, b)
        self.assertEqual(r.status, 'unknown')
        self.assertIsNone(r.intersection)
        self.assertIn('old.weekdays', r.missing)
        self.assertEqual(r.possible_weekdays, frozenset({2}))

    def test_intersection_retains_field_weekday_and_effective_date_sources(self):
        old_ref = Evidence('old', 'Mondays and Wednesdays')
        new_ref = Evidence('new', 'Wednesdays from December 1')
        old = Scope(Field.known('user', [old_ref]), Field.known('work_location', [old_ref]),
                    Weekdays.known({0, 2}, [old_ref]),
                    Interval(Bound.unbounded([old_ref]), Bound.unbounded([old_ref])))
        new = Scope(Field.known('user', [new_ref]), Field.known('work_location', [new_ref]),
                    Weekdays.known({2}, [new_ref]),
                    Interval(Bound.known('2026-12-01', [new_ref]), Bound.unbounded([new_ref])))
        intersection = compare(old, new).intersection
        self.assertEqual(intersection.subject.evidence, (old_ref, new_ref))
        self.assertEqual(intersection.attribute.evidence, (old_ref, new_ref))
        self.assertEqual(intersection.weekdays.evidence, (old_ref, new_ref))
        self.assertEqual(intersection.valid.start.evidence, (new_ref,))

    def test_unknown_endpoint_does_not_become_known_constraint(self):
        old = self.scope(Weekdays.all(), Bound.unknown(), Bound.unbounded())
        new = self.scope(Weekdays.all(), Bound.known('2026-12-01'), Bound.unbounded())
        result = compare(old, new)
        self.assertEqual(result.status, 'unknown')
        self.assertIsNone(result.intersection)
        self.assertEqual(result.known_time_constraints, (('not_before', '2026-12-01'),))
        self.assertIn('old.valid.start', result.missing)

    def test_shared_known_start_proves_partial_intersection_despite_unknown_ends(self):
        a = self.scope(Weekdays.all(), Bound.known('2026-12-01'), Bound.unknown())
        b = self.scope(Weekdays.all(), Bound.known('2026-12-01'), Bound.unknown())
        result = compare(a, b)
        self.assertEqual(result.status, 'overlap')
        self.assertFalse(result.intersection_complete)
        self.assertEqual(result.intersection.valid.start.value, date(2026, 12, 1))
        self.assertEqual(result.intersection.valid.end.value, date(2026, 12, 1))
        self.assertIn('old.valid.end', result.missing)
        self.assertIn('new.valid.end', result.missing)

    def test_shared_known_start_does_not_prove_a_nonmatching_weekday(self):
        a = self.scope(Weekdays.known({2}), Bound.known('2026-12-01'), Bound.unknown())
        b = self.scope(Weekdays.known({2}), Bound.known('2026-12-01'), Bound.unknown())
        self.assertEqual(compare(a, b).status, 'unknown')

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError): Weekdays.known(set())
        with self.assertRaises(ValueError): Weekdays.known({7})
        with self.assertRaises(ValueError): Interval(Bound.known('2026-03-01'), Bound.known('2026-02-01'))
        with self.assertRaises(ValueError): Bound.known('2026-01-01T00:00:00')


if __name__ == '__main__': unittest.main()
