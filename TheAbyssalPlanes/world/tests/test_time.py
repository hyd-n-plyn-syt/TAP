"""Unit tests for the universal-time round primitives."""

from django.test import SimpleTestCase

from world.systems import time as utime


class TimeRoundTest(SimpleTestCase):
    def test_round_number_buckets(self):
        self.assertEqual(utime.round_number(0), 0)
        self.assertEqual(utime.round_number(5), 0)
        self.assertEqual(utime.round_number(6), 1)
        self.assertEqual(utime.round_number(59), 9)

    def test_seconds_into_round(self):
        self.assertEqual(utime.seconds_into_round(12), 0)
        self.assertEqual(utime.seconds_into_round(17), 5)
        self.assertEqual(utime.seconds_into_round(0), 0)

    def test_round_start(self):
        self.assertEqual(utime.round_start(12), 12)
        self.assertEqual(utime.round_start(17), 12)
        self.assertEqual(utime.round_start(6), 6)

    def test_next_round_start(self):
        self.assertEqual(utime.next_round_start(12), 18)
        self.assertEqual(utime.next_round_start(17), 18)

    def test_rounds_elapsed_never_negative(self):
        self.assertEqual(utime.rounds_elapsed(100, seconds=100), 0)
        self.assertEqual(utime.rounds_elapsed(100, seconds=50), 0)
        self.assertEqual(utime.rounds_elapsed(100, seconds=124), 4)

    def test_regen_rounds_elapsed(self):
        self.assertEqual(utime.regen_rounds_elapsed(0, seconds=59), 0)
        self.assertEqual(utime.regen_rounds_elapsed(0, seconds=60), 1)
        self.assertEqual(utime.regen_rounds_elapsed(60, seconds=121), 1)