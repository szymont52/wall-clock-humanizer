# wall_clock_humanizer
# Core implementation of wall-clock humanization.

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Thresholds:
    """Thresholds (in seconds) at which each unit becomes active.

    A unit is chosen when abs(elapsed) is >= that unit's threshold AND
    below the next unit's threshold (or there is no next unit).

    Defaults approximate natural speech: once a minute has elapsed you
    stop counting seconds, once an hour has elapsed you stop counting
    minutes, and so on.
    """

    minute: int = 45
    hour: int = 90
    day: int = 22 * 3600
    week: int = 7 * 24 * 3600
    month: int = 30 * 24 * 3600
    year: int = 365 * 24 * 3600


# Internal lookup table ordering largest-to-smallest so that the first
# match wins. Each entry pairs the threshold attribute name (on
# Thresholds) with the divisor that converts seconds into that unit.
_UNITS = [
    ("year", 365 * 24 * 3600),
    ("month", 30 * 24 * 3600),
    ("week", 7 * 24 * 3600),
    ("day", 24 * 3600),
    ("hour", 3600),
    ("minute", 60),
]


class Humanizer:
    """Render elapsed seconds as relative English text.

    Example::

        h = Humanizer()
        h.humanize(9000)      # '2 hours ago'
        h.humanize(-300)      # 'in 5 minutes'
        h.humanize(0)         # 'now'

    Pass a custom Thresholds to change the crossover points between
    units. For instance, raising ``minute`` to 120 makes the humanizer
    keep saying "N seconds ago" until two minutes have elapsed.
    """

    def __init__(self, thresholds: Thresholds | None = None) -> None:
        # Copy so callers cannot mutate our internal state after
        # construction by hanging on to the object they passed in.
        self._thresholds = thresholds if thresholds is not None else Thresholds()

    @property
    def thresholds(self) -> Thresholds:
        """A copy of the active thresholds; mutating it has no effect."""
        return self._thresholds

    def with_thresholds(self, thresholds: Thresholds) -> "Humanizer":
        """Return a new Humanizer using the given thresholds.

        The original is left untouched, which makes it cheap to derive a
        tuned humanizer from a default one without risking shared state.
        """
        return Humanizer(replace(self._thresholds, **thresholds.__dict__))

    def humanize(self, elapsed: int) -> str:
        """Turn ``elapsed`` seconds into a phrase such as '3 days ago'.

        Positive ``elapsed`` is the past; negative is the future; zero
        is 'now'.
        """
        if not isinstance(elapsed, int):
            raise TypeError(f"elapsed must be int, got {type(elapsed).__name__}")

        if elapsed == 0:
            return "now"

        future = elapsed < 0
        seconds = abs(elapsed)

        for name, divisor in _UNITS:
            threshold = getattr(self._thresholds, name)
            if seconds >= threshold:
                count = seconds // divisor
                if count > 0:
                    return self._format(future, count, name)

        return self._format(future, seconds, "second")

    @staticmethod
    def _format(future: bool, count: int, unit: str) -> str:
        """Build the final phrase.

        Singular/plural is handled by appending 's' to the unit name
        whenever count != 1. This is simpler and lighter than a lookup
        table of irregular plurals; 'week', 'day', 'hour', 'minute' and
        'second' all pluralise with a plain 's', so a table would add
        code for no real gain.
        """
        noun = unit if count == 1 else unit + "s"
        if future:
            return f"in {count} {noun}"
        return f"{count} {noun} ago"
