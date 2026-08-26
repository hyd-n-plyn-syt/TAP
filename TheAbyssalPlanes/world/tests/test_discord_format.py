"""Unit tests for the Evennia -> Discord ANSI translation."""

from django.test import SimpleTestCase

from world.systems.discord_format import (
    DISCORD_MAX_LEN,
    ansi_body,
    to_discord_ansi,
)


class AnsiBodyTest(SimpleTestCase):
    def test_plain_text_untouched(self):
        self.assertEqual(ansi_body("hello world"), "hello world")

    def test_basic_pipe_color(self):
        body = ansi_body("|rred|n")
        self.assertIn("\x1b[31m", body)
        self.assertIn("red", body)
        self.assertIn("\x1b[0m", body)

    def test_bright_pipe_color_no_bold(self):
        body = ansi_body("|rbright|n")
        self.assertNotIn("\x1b[1m", body)
        self.assertNotIn("\x1b[22m", body)
        self.assertIn("\x1b[31m", body)

    def test_dark_pipe_color_no_bold(self):
        body = ansi_body("|Rdark|n")
        self.assertNotIn("\x1b[1m", body)
        self.assertNotIn("\x1b[22m", body)
        self.assertIn("\x1b[31m", body)

    def test_gray_and_white_distinct_codes(self):
        gray_body = ansi_body("|xgray|n")
        white_body = ansi_body("|wwhite|n")
        # Original 8 ANSI: 30 = gray/black, 37 = white — must stay distinct.
        self.assertIn("\x1b[30m", gray_body)
        self.assertIn("\x1b[37m", white_body)
        self.assertNotIn("\x1b[37m", gray_body)
        self.assertNotIn("\x1b[30m", white_body)
        self.assertNotIn("\x1b[1m", gray_body)
        self.assertNotIn("\x1b[1m", white_body)

    def test_truecolor_falls_back_to_ansi16(self):
        body = ansi_body("|#e67e22orange|n")
        self.assertNotIn("#e67e22", body)
        self.assertTrue(any(f"\x1b[{c}m" in body for c in range(30, 38)))

    def test_xterm256_falls_back_to_ansi16(self):
        body = ansi_body("|503teal|n")
        self.assertNotIn("|503", body)
        self.assertTrue(any(f"\x1b[{c}m" in body for c in range(30, 38)))

    def test_greyscale_falls_back_to_ansi16(self):
        body = ansi_body("|=cgray|n")
        self.assertNotIn("|=c", body)
        self.assertTrue(any(f"\x1b[{c}m" in body for c in range(30, 38)))

    def test_backticks_neutralized(self):
        body = ansi_body("code ``` breakout")
        self.assertNotIn("`", body)


class ToDiscordAnsiTest(SimpleTestCase):
    def test_wraps_in_ansi_fence(self):
        out = to_discord_ansi("[|wOOC|n] |#1abc9cBob|n: hi")
        self.assertIsNotNone(out)
        self.assertTrue(out.startswith("```ansi\n"))
        self.assertTrue(out.endswith("\n```"))

    def test_empty_message_returns_none(self):
        self.assertIsNone(to_discord_ansi(""))
        self.assertIsNone(to_discord_ansi("   "))

    def test_truncation_respects_discord_limit(self):
        out = to_discord_ansi("|rx" * 5000)
        self.assertIsNotNone(out)
        self.assertLessEqual(len(out), DISCORD_MAX_LEN)
        self.assertTrue(out.endswith("…\n```"))
