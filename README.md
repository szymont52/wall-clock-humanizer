# wall-clock-humanizer

Turns elapsed seconds into relative English text such as '3 days ago' or 'in 2 hours'.

```python
from wall_clock_humanizer import Humanizer, Thresholds

h = Humanizer()
print(h.humanize(9000))        # '2 hours ago'
print(h.humanize(-300))        # 'in 5 minutes'
print(h.humanize(0))           # 'now'

# Tune the crossover points between units:
tuned = Humanizer(Thresholds(minute=120, day=12 * 3600))
print(tuned.humanize(60))      # '60 seconds ago'
print(tuned.humanize(12 * 3600))  # '1 day ago'
```

## Why this exists

The problem is narrow: given an integer number of seconds elapsed since or
until a reference point, produce the phrase a person would actually say.
The hard part is choosing the unit, and the only sane rule is 'largest unit
whose threshold has been reached'. This library is a few dozen lines that
implement exactly that rule, with thresholds you can override.

The deliberate trade-off: there is no system-clock integration and no
natural-language parsing. You compute `elapsed = reference - then` yourself
and pass the integer in. That keeps the library pure and deterministic — no
clock, no side effects, no surprises in tests.

Sign convention: positive elapsed is the past ('N units ago'), negative is
the future ('in N units'), zero is 'now'.

## The edge you will hit

When `elapsed` lands exactly on a unit threshold the count for that unit can
be zero, which yields phrases like '0 minutes ago'. For example, with the
default `minute` threshold of 45, `humanize(45)` returns '0 minutes ago'
because 45 seconds is below 60, so the minute count is 0. This is intentional
and consistent with the rule above; if you find it awkward, raise the
threshold (e.g. `Thresholds(minute=60)`) so seconds are used up to a full
minute.
