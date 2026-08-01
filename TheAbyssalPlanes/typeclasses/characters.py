"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia import AttributeProperty
from evennia.contrib.rpg.health_bar import display_meter
from evennia.objects.objects import DefaultCharacter

from world.systems import stats

from .objects import ObjectParent

# Bar fill gradient (matches display_meter's default) and the "empty"
# background used when a pool is damaged: dark gray via the xterm256
# grayscale code |=e (index 235), near black but still visible.
_POOL_FILL_COLORS = ["R", "Y", "G"]
_POOL_EMPTY_BG = "=e"


def pool_color(cur, maxv):
    """Return an ANSI foreground color code for a pool value by how full it is."""
    if maxv <= 0:
        return "|R"
    pct = float(cur) / float(maxv)
    idx = int(round(len(_POOL_FILL_COLORS) * pct)) - 1
    idx = max(0, min(idx, len(_POOL_FILL_COLORS) - 1))
    return "|" + _POOL_FILL_COLORS[idx]


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    corpus_potestas = AttributeProperty(default=1, category="stat")
    corpus_reflexus = AttributeProperty(default=1, category="stat")
    corpus_obsistis = AttributeProperty(default=1, category="stat")
    genius_potestas = AttributeProperty(default=1, category="stat")
    genius_reflexus = AttributeProperty(default=1, category="stat")
    genius_obsistis = AttributeProperty(default=1, category="stat")
    animus_potestas = AttributeProperty(default=1, category="stat")
    animus_reflexus = AttributeProperty(default=1, category="stat")
    animus_obsistis = AttributeProperty(default=1, category="stat")

    @property
    def corpus(self):
        return stats.main_stat(self, "corpus")

    @property
    def genius(self):
        return stats.main_stat(self, "genius")

    @property
    def animus(self):
        return stats.main_stat(self, "animus")

    @property
    def vigor(self):
        return stats.derived_pools(self)["vigor"]

    @property
    def vigor_regen(self):
        return stats.derived_pools(self)["vigor_regen"]

    @property
    def vim(self):
        return stats.derived_pools(self)["vim"]

    @property
    def vim_regen(self):
        return stats.derived_pools(self)["vim_regen"]

    @property
    def mens(self):
        return stats.derived_pools(self)["mens"]

    @property
    def mens_regen(self):
        return stats.derived_pools(self)["mens_regen"]

    def at_object_creation(self):
        super().at_object_creation()
        self.db.visarial_state = "physical"
        self.db.promptmode = "numbers"
        self.reset_pools()

    def set_state(self, state):
        if state not in ("physical", "perceiving", "manifested"):
            return False
        self.db.visarial_state = state
        self.msg(prompt=self.get_prompt())
        return True

    @property
    def pools_current(self):
        """Return {pool: current} for the three pools, clamped to [0, max]."""
        result = {}
        for pool in stats.POOL_KEYS:
            maxv = getattr(self, pool)
            cur = self.attributes.get(f"{pool}_current")
            if cur is None:
                cur = maxv
            result[pool] = max(0, min(cur, maxv))
        return result

    def set_pool(self, pool, value):
        """Set a current pool, clamped to [0, max]. Returns the stored value."""
        if pool not in stats.POOL_KEYS:
            return None
        maxv = getattr(self, pool)
        value = max(0, min(int(value), maxv))
        self.attributes.add(f"{pool}_current", value)
        self.msg(prompt=self.get_prompt())
        return value

    def reset_pools(self):
        """Restore all current pools to their derived maximums."""
        for pool in stats.POOL_KEYS:
            self.attributes.add(f"{pool}_current", getattr(self, pool))
        self.msg(prompt=self.get_prompt())

    def get_prompt(self):
        """Build the client prompt from current pools and visarial state."""
        mode = self.db.promptmode or "numbers"
        state = self.db.visarial_state or "physical"
        state_color = {"physical": "|x", "perceiving": "|M", "manifested": "|M"}.get(
            state, "|w"
        )

        parts = []
        for pool in stats.POOL_KEYS:
            maxv = getattr(self, pool)
            cur = self.pools_current[pool]
            label = f"|w{pool.capitalize()}:|n"
            if mode == "percent":
                pct = int(round(100 * cur / maxv)) if maxv else 0
                parts.append(f"{label} {pool_color(cur, maxv)}{pct}%|n")
            elif mode == "bars":
                bar = display_meter(
                    cur,
                    maxv,
                    length=10,
                    show_values=False,
                    empty_color=_POOL_EMPTY_BG,
                )
                parts.append(f"{label} {bar}")
            else:
                parts.append(f"{label} {pool_color(cur, maxv)}{cur}/{maxv}|n")

        parts.append(f"|w[|n{state_color}{state}|n|w]|n")
        return "  ".join(parts)
