"""Tests for world/data/calendar.py pure math (using explicit timestamps)."""

from django.test import SimpleTestCase

from world.data import calendar

ONE_DAY = calendar.SECONDS_PER_DAY  # 23h in seconds


class CalendarMathTest(SimpleTestCase):
    def test_epoch_starts_anchor_year(self):
        date = calendar.cosmic_date(0)
        self.assertEqual(date["year"], calendar.CALENDAR_START_YEAR)
        self.assertEqual((date["month"], date["day"], date["hour"]), (0, 0, 0))

    def test_one_day_advances_day(self):
        day1 = calendar.cosmic_date(0)
        day2 = calendar.cosmic_date(ONE_DAY)
        self.assertEqual(day2["day"], day1["day"] + 1)

    def test_month_rollover(self):
        date = calendar.cosmic_date(ONE_DAY * calendar.DAYS_PER_MONTH)
        self.assertEqual(date["month"], 1)
        self.assertEqual(date["day"], 0)

    def test_year_rollover(self):
        date = calendar.cosmic_date(calendar.SECONDS_PER_YEAR)
        self.assertEqual(date["year"], calendar.CALENDAR_START_YEAR + 1)
        self.assertEqual(date["month"], 0)

    def test_second_components(self):
        date = calendar.cosmic_date(ONE_DAY + 3600 + 2 * 60 + 3)
        self.assertEqual(date["day"], 1)
        self.assertEqual(date["hour"], 1)
        self.assertEqual(date["minute"], 2)
        self.assertEqual(date["second"], 3)

    def test_negative_seconds_clamped(self):
        date = calendar.cosmic_date(-10)
        self.assertEqual(date["year"], calendar.CALENDAR_START_YEAR)


class LocalDateTest(SimpleTestCase):
    def test_auridon_matches_universal(self):
        self.assertEqual(
            calendar.local_date("auridon", ONE_DAY * 500),
            calendar.cosmic_date(ONE_DAY * 500),
        )

    def test_inner_planet_shorter_year(self):
        cindris = calendar.local_date("cindris", calendar.SECONDS_PER_YEAR)
        universal = calendar.cosmic_date(calendar.SECONDS_PER_YEAR)
        # 364 universal days is 2 full Cindris years (182-day orbit)
        self.assertEqual(cindris["year"], universal["year"] + 1)

    def test_unknown_planet_defaults_to_auridon(self):
        self.assertEqual(calendar.get_planet("nope")["name"], "Auridon")


class FormattingTest(SimpleTestCase):
    def test_ordinal_suffix(self):
        self.assertEqual(calendar.ordinal_suffix(1), "st")
        self.assertEqual(calendar.ordinal_suffix(2), "nd")
        self.assertEqual(calendar.ordinal_suffix(3), "rd")
        self.assertEqual(calendar.ordinal_suffix(11), "th")
        self.assertEqual(calendar.ordinal_suffix(21), "st")

    def test_format_date_includes_clock(self):
        out = calendar.format_date(
            {"year": 10058, "month": 2, "day": 2, "hour": 6, "minute": 30, "second": 0},
            show_clock=True,
        )
        self.assertIn("Year 10058", out)
        self.assertIn("06:30:00", out)

    def test_sign_of_month(self):
        self.assertEqual(calendar.sign_of_month(0), calendar.SIGNS[0])
        self.assertEqual(calendar.sign_of_month(13), calendar.SIGNS[0])  # wraps