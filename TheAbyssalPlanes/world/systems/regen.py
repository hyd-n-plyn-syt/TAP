"""
Regeneration system for The Abyssal Planes.

Regen is decoupled from combat entirely. A creature regenerates on its own
per-character ``RegenTimer`` script, which clones a 60-second regen round
from the universal clock. The timer lives on the *character* (not the
room), so it follows them across room transitions and keeps applying even
while they are offline-capable later on. It only runs while the character
is injured (any non-zeroed pool below its maximum).

The per-round recovery math is shared with the rest of the game and was
moved out of the old room-scoped combat loop, so nothing else ever runs on
the regen timer.
"""

from evennia import DefaultScript

from world.data import species as species_data
from world.systems import stats
from world.systems.time import now, regen_rounds_elapsed

POSE_MULTIPLIERS = {
    "sleeping": 2.0,
    "resting": 1.5,
    "laying": 1.5,
    "sitting": 1.5,
}

_POSE_STATE_LOOKUP = {
    "resting": ["resting", "rest"],
    "sleeping": ["sleeping", "sleep"],
    "laying": ["laying", "lay"],
    "sitting": ["sitting", "sit"],
}


def regen_factors(char):
    """Return (pose_multiplier, furniture_bonus) for a character where they are."""
    pose = getattr(char, "pose", "standing")
    mult = POSE_MULTIPLIERS.get(pose, 1.0)
    furniture_bonus = 0.0
    room = char.location
    if not room:
        return mult, furniture_bonus
    cx = getattr(char.db, "pos_x", 0)
    cy = getattr(char.db, "pos_y", 0)
    for obj in room.contents:
        if not obj.is_typeclass("typeclasses.furniture.Furniture"):
            continue
        is_nearby = False
        if hasattr(obj, "is_at_coord") and obj.is_at_coord(cx, cy):
            is_nearby = True
        else:
            fx = getattr(obj.db, "pos_x", 0)
            fy = getattr(obj.db, "pos_y", 0)
            if max(abs(cx - fx), abs(cy - fy)) <= 1:
                is_nearby = True
        if not is_nearby:
            continue
        allowed = getattr(obj, "allowed_states", [])
        match_states = _POSE_STATE_LOOKUP.get(pose, [pose])
        if any(st in allowed for st in match_states):
            furniture_bonus = max(furniture_bonus, getattr(obj, "quality", 1.0))
    return mult, furniture_bonus


def apply_regen(char):
    """Apply one regen round of recovery to a character.

    Pose multiplier x (1 + furniture quality), with a minimum recovery of
    1 per pool (when the base rate is positive). Pools a species cannot
    have are skipped. Returns a dict {pool: new_current_value} of pools
    that changed.
    """
    mult, furniture_bonus = regen_factors(char)
    effective = mult * (1.0 + furniture_bonus)
    zeroed = species_data.zeroed_pools(char.species_key)
    changed = {}
    for pool in stats.POOL_KEYS:
        if pool in zeroed:
            continue
        base_regen = getattr(char, f"{pool}_regen", 1)
        regen_val = int(round(base_regen * effective))
        if regen_val < 1 and base_regen > 0:
            regen_val = 1
        maxv = getattr(char, pool, 0)
        cur = char.pools_current[pool]
        if cur < maxv:
            new_cur = min(maxv, cur + regen_val)
            char.set_pool(pool, new_cur)
            changed[pool] = new_cur
    return changed


class RegenTimer(DefaultScript):
    """
    Per-character regen ticker, cloned from the universal clock.

    Starts when a character becomes injured and stops itself (via
    ``is_valid``) the instant every pool is back to full. Applies one
    regen round per 60 cosmic seconds.
    """

    def at_script_creation(self):
        self.key = "regen_timer"
        self.interval = 1
        self.persistent = True
        self.db.anchor = now()

    def is_valid(self):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return False
        return bool(getattr(char, "is_injured", False))

    def at_repeat(self, *args, **kwargs):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return
        anchor = self.db.anchor
        if not anchor:
            self.db.anchor = now()
            return
        elapsed = regen_rounds_elapsed(anchor)
        if elapsed < 1:
            return
        self.db.anchor = now()
        if not getattr(char, "is_injured", False):
            self.stop()
            return
        apply_regen(char)
        if not getattr(char, "is_injured", False):
            self.stop()
            return


def ensure_regen_timer(char):
    """Make sure *char* has exactly one running RegenTimer script."""
    existing = list(char.scripts.get(key="regen_timer"))
    active = [s for s in existing if getattr(s, "db_is_active", False)]
    for script in existing:
        if script not in active:
            try:
                script.delete()
            except Exception:
                pass
    if active:
        return active[0]
    return char.scripts.add("world.systems.regen.RegenTimer", key="regen_timer")