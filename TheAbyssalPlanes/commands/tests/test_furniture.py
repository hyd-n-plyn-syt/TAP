"""Tests for furniture facing/approach rules and approach naming."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from combat.movement import mover_arrival_message
from commands.player.poses import _check_furniture_approach


class FurnitureApproachTest(EvenniaCommandTest):
    def _make(self, dimension, facing, x=2, y=2):
        furn = create_object(
            "typeclasses.furniture.Furniture",
            key="test furniture",
            location=self.room1,
        )
        furn.db.dimension = dimension
        furn.db.facing = facing
        furn.db.pos_x = x
        furn.db.pos_y = y
        furn.calculate_footprint()
        return furn

    def _place(self, x, y):
        self.char1.db.pos_x = x
        self.char1.db.pos_y = y

    def test_couch_lies_perpendicular_to_facing(self):
        furn = self._make("1x3", "north", x=2, y=2)
        self.assertEqual(
            set(furn.db.extra_coords), {(3, 2), (4, 2)}
        )
        self.assertEqual(furn.db.facing, "north")

    def test_couch_front_allows_sit(self):
        furn = self._make("1x3", "north", x=2, y=2)
        self._place(3, 3)
        self.assertTrue(_check_furniture_approach(self.char1, furn))

    def test_couch_ends_are_sides_and_reject_sit(self):
        furn = self._make("1x3", "north", x=2, y=2)
        self._place(5, 2)
        self.assertFalse(_check_furniture_approach(self.char1, furn))
        self._place(1, 2)
        self.assertFalse(_check_furniture_approach(self.char1, furn))

    def test_couch_hint_names_front(self):
        furn = self._make("1x3", "north", x=2, y=2)
        hint, _ = furn.approach_hint()
        self.assertEqual(hint, "the north")

    def test_chair_front_only(self):
        furn = self._make("1x1", "north", x=2, y=2)
        self._place(2, 3)
        self.assertTrue(_check_furniture_approach(self.char1, furn))
        self._place(2, 1)
        self.assertFalse(_check_furniture_approach(self.char1, furn))

    def test_single_tile_can_rotate(self):
        furn = self._make("1x1", "north", x=2, y=2)
        ok, _ = furn.rotate()
        self.assertTrue(ok)
        self.assertEqual(furn.db.facing, "east")

    def test_2x2_rotates_in_place(self):
        furn = self._make("2x2", "north", x=2, y=2)
        tiles = {(2, 2), (3, 2), (2, 3), (3, 3)}
        self.assertEqual({(2, 2)} | set(furn.db.extra_coords), tiles)
        ok, _ = furn.rotate()
        self.assertTrue(ok)
        self.assertEqual(furn.db.facing, "east")
        self.assertEqual({(2, 2)} | set(furn.db.extra_coords), tiles)

    def test_bed_enters_from_sides(self):
        furn = self._make("1x2", "north", x=2, y=2)
        self.assertEqual(set(furn.db.extra_coords), {(2, 3)})
        self.assertTrue(furn.is_bed)
        self._place(3, 2)
        self.assertTrue(_check_furniture_approach(self.char1, furn))
        self._place(1, 3)
        self.assertTrue(_check_furniture_approach(self.char1, furn))

    def test_bed_foot_and_head_blocked(self):
        furn = self._make("1x2", "north", x=2, y=2)
        self._place(2, 4)
        self.assertFalse(_check_furniture_approach(self.char1, furn))
        self._place(2, 1)
        self.assertFalse(_check_furniture_approach(self.char1, furn))

    def test_bed_hint_names_sides(self):
        furn = self._make("1x2", "north", x=2, y=2)
        hint, _ = furn.approach_hint()
        self.assertEqual(hint, "the east or west")

    def test_bed_subtype_enters_from_sides(self):
        furn = create_object(
            "typeclasses.furniture.Bed",
            key="test bed",
            location=self.room1,
        )
        furn.db.dimension = "1x2"
        furn.db.facing = "north"
        furn.db.pos_x = 2
        furn.db.pos_y = 2
        furn.calculate_footprint()
        self.assertTrue(furn.is_bed)
        self.assertEqual(set(furn.db.extra_coords), {(2, 3)})
        self._place(3, 2)
        self.assertTrue(_check_furniture_approach(self.char1, furn))
        self._place(2, 4)
        self.assertFalse(_check_furniture_approach(self.char1, furn))

    def test_arrival_uses_full_display_name(self):
        furn = self._make("1x1", "north", x=3, y=2)
        furn.key = "oak table"
        self._place(2, 2)
        nav = {
            "dest_x": 3,
            "dest_y": 2,
            "dest_z": None,
            "exit_dbref": None,
            "movement_mode": "walking",
        }
        msg = mover_arrival_message(self.room1, nav, self.char1)
        self.assertIn("an oak table", msg)
        self.assertNotIn("You arrive beside oak table", msg)

    def test_capitalize_display_name(self):
        from combat.movement import capitalize_display_name

        self.assertEqual(capitalize_display_name("a leather armchair"), "A leather armchair")
        self.assertEqual(capitalize_display_name("an oak bed"), "An oak bed")
        self.assertEqual(capitalize_display_name("A tall Visarii"), "A tall Visarii")
        self.assertEqual(capitalize_display_name(""), "")