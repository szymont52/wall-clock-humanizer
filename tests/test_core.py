"""Unit tests for wall_clock_humanizer.core.

These tests are deliberately deterministic: they never touch the system
clock and they only assert on strings produced by pure functions.
"""

import unittest

from wall_clock_humanizer import Humanizer, Thresholds
from wall_clock_humanizer.core import Thresholds as CoreThresholds


class TestHumanize(unittest.TestCase):
    def setUp(self) -> None:
        self.h = Humanizer()

    def test_zero_is_now(self) -> None:
        self.assertEqual(self.h.humanize(0), "now")

    def test_past_seconds(self) -> None:
        self.assertEqual(self.h.humanize(10), "10 seconds ago")

    def test_past_minute_threshold(self) -> None:
        # At 45s the minute unit kicks in, but the count is zero
        # (45 // 60 == 0), so the humanizer falls back to seconds.
        self.assertEqual(self.h.humanize(45), "45 seconds ago")

    def test_past_singular_minute(self) -> None:
        self.assertEqual(self.h.humanize(60), "1 minute ago")

    def test_past_plural_minutes(self) -> None:
        self.assertEqual(self.h.humanize(120), "2 minutes ago")

    def test_past_hour(self) -> None:
        self.assertEqual(self.h.humanize(3600), "1 hour ago")

    def test_past_plural_hours(self) -> None:
        self.assertEqual(self.h.humanize(9000), "2 hours ago")

    def test_past_day(self) -> None:
        self.assertEqual(self.h.humanize(24 * 3600), "1 day ago")

    def test_past_plural_days(self) -> None:
        self.assertEqual(self.h.humanize(3 * 24 * 3600), "3 days ago")

    def test_past_week(self) -> None:
        self.assertEqual(self.h.humanize(7 * 24 * 3600), "1 week ago")

    def test_past_month(self) -> None:
        self.assertEqual(self.h.humanize(30 * 24 * 3600), "1 month ago")

    def test_past_year(self) -> None:
        self.assertEqual(self.h.humanize(365 * 24 * 3600), "1 year ago")

    def test_past_plural_years(self) -> None:
        self.assertEqual(self.h.humanize(2 * 365 * 24 * 3600), "2 years ago")


class TestFuture(unittest.TestCase):
    def setUp(self) -> None:
        self.h = Humanizer()

    def test_future_seconds(self) -> None:
        self.assertEqual(self.h.humanize(-10), "in 10 seconds")

    def test_future_singular_minute(self) -> None:
        self.assertEqual(self.h.humanize(-60), "in 1 minute")

    def test_future_plural_hours(self) -> None:
        self.assertEqual(self.h.humanize(-7200), "in 2 hours")

    def test_future_plural_days(self) -> None:
        self.assertEqual(self.h.humanize(-3 * 24 * 3600), "in 3 days")


class TestThresholds(unittest.TestCase):
    def test_custom_minute_threshold(self) -> None:
        # With minute threshold at 120, 60s is still seconds.
        h = Humanizer(Thresholds(minute=120))
        self.assertEqual(h.humanize(60), "60 seconds ago")
        self.assertEqual(h.humanize(120), "2 minutes ago")

    def test_custom_day_threshold(self) -> None:
        # With day threshold at 12h, the day unit is active but
        # 12h // 24h == 0, so the humanizer falls back to hours.
        h = Humanizer(Thresholds(day=12 * 3600))
        self.assertEqual(h.humanize(12 * 3600), "12 hours ago")
        self.assertEqual(h.humanize(11 * 3600), "11 hours ago")

    def test_with_thresholds_returns_new_instance(self) -> None:
        base = Humanizer()
        derived = base.with_thresholds(Thresholds(minute=100))
        self.assertIsNot(base, derived)
        # Original is unchanged.
        self.assertEqual(base.thresholds.minute, 45)
        self.assertEqual(derived.thresholds.minute, 100)

    def test_thresholds_property_is_read_only_view(self) -> None:
        h = Humanizer(Thresholds(minute=50))
        t = h.thresholds
        self.assertEqual(t.minute, 50)
        # Thresholds is frozen, so mutation raises.
        with self.assertRaises(Exception):
            t.minute = 99  # type: ignore[misc]


class TestValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.h = Humanizer()

    def test_rejects_float(self) -> None:
        with self.assertRaises(TypeError):
            self.h.humanize(1.5)  # type: ignore[arg-type]

    def test_rejects_string(self) -> None:
        with self.assertRaises(TypeError):
            self.h.humanize("10")  # type: ignore[arg-type]


class TestExportedNames(unittest.TestCase):
    def test_thresholds_alias_matches_core(self) -> None:
        self.assertIs(Thresholds, CoreThresholds)


if __name__ == "__main__":
    unittest.main()
