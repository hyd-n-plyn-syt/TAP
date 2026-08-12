"""Smoke tests to confirm the Evennia test runner works with our typeclasses."""

from evennia.utils.test_resources import EvenniaTest


class CharacterStatSmokeTest(EvenniaTest):
    def test_basic_attrs(self):
        self.char1.corpus_potestas = 1
        self.assertEqual(self.char1.corpus_potestas, 1)
        self.assertEqual(self.char1.db.skills or {}, {})
        self.assertEqual(self.char1.species_key, None)
        self.assertEqual(self.char1.pose, "standing")