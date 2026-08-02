"""A lightweight character stand-in for pure (DB-free) unit tests.

The world/systems modules only need a few attribute-style fields from a
character: the stored `skills` / `skills_xp` / `stat_xp` dicts, the nine
sub-stat base values, and the `species_key`. This mock provides those so
the pure math in world/systems and world/data can be tested without evennia.
"""

from types import SimpleNamespace


class MockChar:
    """Minimal facade standing in for a Character in unit tests.

    Mirrors both access patterns the systems use: direct `.species_key`
    (skills) and the attribute-handler proxy `char.db.species_key` (stats).
    """

    def __init__(self, species_key=None):
        self.species_key = species_key
        self.db = SimpleNamespace(species_key=species_key)
        self.skills = {}
        self.skills_xp = {}
        self.stat_xp = {}
        for main in ("corpus", "genius", "animus"):
            for sub in ("potestas", "reflexus", "obsistis"):
                setattr(self, f"{main}_{sub}", 1)