"""A lightweight character stand-in for pure (DB-free) unit tests.

The world/systems modules only need a few attribute-style fields from a
character: the stored `skills` / `skills_xp` / `stat_xp` dicts, the nine
sub-stat base values, and the `species_key`. This mock provides those so
the pure math in world/systems and world/data can be tested without evennia.
"""


class MockChar:
    """Minimal facade standing in for a Character in unit tests.

    All systems read `species_key` directly off the character, so the mock
    only needs that one field alongside the stat and growth dicts.
    """

    def __init__(self, species_key=None):
        self.species_key = species_key
        self.skills = {}
        self.skills_xp = {}
        self.stat_xp = {}
        for main in ("corpus", "genius", "animus"):
            for sub in ("potestas", "reflexus", "obsistis"):
                setattr(self, f"{main}_{sub}", 1)