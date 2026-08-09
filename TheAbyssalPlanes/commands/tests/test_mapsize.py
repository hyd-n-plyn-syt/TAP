"""Tests for the MAPSIZE command."""

from evennia.utils.test_resources import EvenniaCommandTest
from commands.player.mapsize import CmdMapSize


class MapSizeCommandTest(EvenniaCommandTest):
    def test_show_current_size(self):
        out = self.call(CmdMapSize(), "")
        self.assertIn("15", out)

    def test_set_valid_size(self):
        out = self.call(CmdMapSize(), "10")
        self.assertIn("10x10", out)
        self.assertEqual(self.account.attributes.get("map_size"), 10)

    def test_set_invalid_low_size(self):
        out = self.call(CmdMapSize(), "2")
        self.assertIn("must be between 3 and 25", out)

    def test_set_invalid_high_size(self):
        out = self.call(CmdMapSize(), "30")
        self.assertIn("must be between 3 and 25", out)

    def test_set_non_numeric_size(self):
        out = self.call(CmdMapSize(), "abc")
        self.assertIn("Please provide a number", out)
