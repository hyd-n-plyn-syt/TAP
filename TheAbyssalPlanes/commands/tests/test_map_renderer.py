"""Tests for plane-aware filtering of the tactical map renderer."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from combat.map_renderer import render_map


class MapRendererPlaneTest(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.room1.db.room_size = {"width": 5, "height": 5}
        for obj in (self.obj1, self.obj2):
            try:
                obj.delete()
            except Exception:
                pass
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.db.pos_z = 1
        self.char2.db.pos_x = 1
        self.char2.db.pos_y = 3
        self.char2.db.pos_z = 1

    def _furniture(self, key, nature, x, y):
        furn = create_object(
            "typeclasses.furniture.Furniture",
            key=key,
            location=self.room1,
            home=self.room1,
        )
        furn.db.dimension = "1x1"
        furn.db.pos_x = x
        furn.db.pos_y = y
        furn.db.visarial_nature = nature
        furn.calculate_footprint()
        return furn

    def test_physical_viewer_hides_visarial_entities(self):
        self._furniture("oak stool", "physical", 1, 1)
        self._furniture("moonstone table", "visarial", 3, 1)
        self._furniture("relic bench", "dual_natured", 4, 4)
        out = render_map(self.char1)
        self.assertEqual(out.count("@"), 2, f"self + physical char2 should show:\n{out}")
        self.assertEqual(out.count("X"), 2, f"physical + dual furniture should show:\n{out}")

    def test_manifested_viewer_sees_visarial_entities(self):
        self._furniture("oak stool", "physical", 1, 1)
        self._furniture("moonstone table", "visarial", 3, 1)
        self._furniture("relic bench", "dual_natured", 4, 4)
        self.char1.set_state("manifested")
        out = render_map(self.char1)
        self.assertEqual(out.count("@"), 1, f"physical char2 should be hidden:\n{out}")
        self.assertEqual(out.count("X"), 2, f"visarial + dual furniture should show:\n{out}")