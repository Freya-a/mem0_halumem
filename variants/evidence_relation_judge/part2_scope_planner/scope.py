"""Evidence-carrying calendar scope intersections; no inference or memory writes."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class Evidence:
    source_id: str
    quote: str

    def __post_init__(self):
        if not self.source_id or not self.quote:
            raise ValueError('evidence requires a source and a quote')


@dataclass(frozen=True)
class Field:
    value: Optional[str]
    evidence: tuple[Evidence, ...] = ()

    @classmethod
    def known(cls, value, evidence=()):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('field value required')
        return cls(value, tuple(evidence))

    @classmethod
    def unknown(cls):
        return cls(None)


@dataclass(frozen=True)
class Bound:
    kind: str
    value: Optional[date] = None
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self):
        if self.kind not in ('known', 'unknown', 'unbounded'):
            raise ValueError('invalid boundary kind')
        if self.kind == 'known':
            if type(self.value) is not date:
                raise ValueError('known boundary requires a date')
        elif self.value is not None:
            raise ValueError('non-known boundary cannot have a date')

    @classmethod
    def known(cls, value, evidence=()):
        if not isinstance(value, str):
            raise ValueError('boundary requires ISO calendar date')
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError('boundary requires ISO calendar date') from exc
        if parsed.isoformat() != value:
            raise ValueError('boundary requires canonical ISO date')
        return cls('known', parsed, tuple(evidence))

    @classmethod
    def unknown(cls):
        return cls('unknown')

    @classmethod
    def unbounded(cls, evidence=()):
        return cls('unbounded', evidence=tuple(evidence))


@dataclass(frozen=True)
class Interval:
    """Closed date boundaries; unbounded is explicit, unknown is unresolved."""
    start: Bound
    end: Bound

    def __post_init__(self):
        if self.start.kind == self.end.kind == 'known' and self.start.value > self.end.value:
            raise ValueError('interval start after end')


@dataclass(frozen=True)
class Weekdays:
    kind: str
    days: frozenset[int] = frozenset()
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self):
        if self.kind not in ('known', 'all', 'unknown'):
            raise ValueError('invalid weekday scope')
        if self.kind == 'known':
            if not self.days or any(type(x) is not int or x not in range(7) for x in self.days):
                raise ValueError('weekday set must contain integers 0..6')
        elif self.days:
            raise ValueError('all and unknown have no explicit weekday set')

    @classmethod
    def known(cls, days, evidence=()):
        return cls('known', frozenset(days), tuple(evidence))

    @classmethod
    def all(cls, evidence=()):
        return cls('all', evidence=tuple(evidence))

    @classmethod
    def unknown(cls):
        return cls('unknown')


@dataclass(frozen=True)
class Scope:
    subject: Field
    attribute: Field
    weekdays: Weekdays
    valid: Interval
    observation: Optional[str] = None
    observation_evidence: tuple[Evidence, ...] = ()


@dataclass(frozen=True)
class Intersection:
    subject: Field
    attribute: Field
    weekdays: Weekdays
    valid: Interval


@dataclass(frozen=True)
class Comparison:
    status: str
    intersection: Optional[Intersection]
    missing: tuple[str, ...]
    possible_weekdays: Optional[frozenset[int]]
    known_time_constraints: tuple[tuple[str, str], ...] = ()
    reason: str = ''
    intersection_complete: bool = False


def _present_weekday(start, end, days):
    # A weekly set repeats every seven days; no need to iterate a long interval.
    for weekday in days:
        delta = (weekday - start.weekday()) % 7
        if delta <= (end - start).days:
            return True
    return False


def compare(old: Scope, new: Scope) -> Comparison:
    """Compare canonical fields and calendar scopes; labels are not verdicts.

    Only caller-provided canonical subject/attribute values are compared. Quotes
    and semantic equivalence must be checked separately by the caller.
    """
    missing = []
    for name in ('subject', 'attribute'):
        a, b = getattr(old, name), getattr(new, name)
        if a.value is not None and b.value is not None and a.value != b.value:
            return Comparison('disjoint', None, (), None, reason=f'{name} differs')
        if a.value is None: missing.append('old.' + name)
        if b.value is None: missing.append('new.' + name)

    all_days = frozenset(range(7))
    def possible_days(w):
        return w.days if w.kind == 'known' else all_days
    days = possible_days(old.weekdays) & possible_days(new.weekdays)
    if not days:
        return Comparison('disjoint', None, (), days, reason='weekday sets disjoint')
    for name, item in (('old', old.weekdays), ('new', new.weekdays)):
        if item.kind == 'unknown': missing.append(name + '.weekdays')

    starts = [s.valid.start for s in (old, new)]
    ends = [s.valid.end for s in (old, new)]
    known_starts = [x.value for x in starts if x.kind == 'known']
    known_ends = [x.value for x in ends if x.kind == 'known']
    lower = max(known_starts) if known_starts else None
    upper = min(known_ends) if known_ends else None
    constraints = tuple((k, v.isoformat()) for k, v in (('not_before', lower), ('not_after', upper)) if v is not None)
    if lower is not None and upper is not None:
        if lower > upper or not _present_weekday(lower, upper, days):
            return Comparison('disjoint', None, (), days, constraints, 'no calendar date can intersect')

    for side, scope in (('old', old), ('new', new)):
        for part in ('start', 'end'):
            if getattr(scope.valid, part).kind == 'unknown':
                missing.append(f'{side}.valid.{part}')
    if missing:
        # An unknown end cannot precede a known start in a nonempty interval,
        # and similarly for an unknown start and known end. Thus a known
        # endpoint can sometimes prove a point of overlap without inventing the
        # missing boundary. Unknown subjects/attributes/weekdays still prevent
        # a definite witness.
        def guaranteed(interval, point):
            start, end = interval.start, interval.end
            lower_ok = start.kind == 'unbounded' or (start.kind == 'known' and start.value <= point)
            upper_ok = end.kind == 'unbounded' or (end.kind == 'known' and point <= end.value)
            if start.kind == 'known' and start.value == point and end.kind == 'unknown':
                upper_ok = True
            if end.kind == 'known' and end.value == point and start.kind == 'unknown':
                lower_ok = True
            return lower_ok and upper_ok

        dimensions_known = not any('.valid.' not in item for item in missing)
        witnesses = sorted(set(known_starts + known_ends))
        if dimensions_known:
            for point in witnesses:
                if point.weekday() in days and guaranteed(old.valid, point) and guaranteed(new.valid, point):
                    refs = tuple(e for b in starts + ends if b.kind == 'known' for e in b.evidence)
                    point_bound = Bound('known', point, refs)
                    subset = Intersection(
                        Field.known(old.subject.value, old.subject.evidence + new.subject.evidence),
                        Field.known(old.attribute.value, old.attribute.evidence + new.attribute.evidence),
                        Weekdays.known({point.weekday()}, old.weekdays.evidence + new.weekdays.evidence),
                        Interval(point_bound, point_bound))
                    return Comparison('overlap', subset, tuple(missing), days, constraints,
                                      'a single date is guaranteed; remaining boundaries are unresolved')
        return Comparison('unknown', None, tuple(missing), days, constraints, 'scope or validity boundary missing')

    def chosen(bounds, values, position):
        if not values:
            return Bound.unbounded(tuple(e for b in bounds for e in b.evidence))
        value = max(values) if position == 'start' else min(values)
        evidence = tuple(e for b in bounds if b.kind == 'known' and b.value == value for e in b.evidence)
        return Bound('known', value, evidence)
    start = chosen(starts, known_starts, 'start')
    end = chosen(ends, known_ends, 'end')
    weekday_evidence = old.weekdays.evidence + new.weekdays.evidence
    weekdays = Weekdays.all(weekday_evidence) if days == all_days else Weekdays.known(days, weekday_evidence)
    subject = Field.known(old.subject.value, old.subject.evidence + new.subject.evidence)
    attribute = Field.known(old.attribute.value, old.attribute.evidence + new.attribute.evidence)
    return Comparison('overlap', Intersection(subject, attribute, weekdays, Interval(start, end)), (), days, constraints,
                      intersection_complete=True)
