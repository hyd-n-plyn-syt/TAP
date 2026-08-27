"""
Stat growth.

The nine sub-stats are uncapped. Using skills feeds them experience
("stat XP"), which accumulates on the character's `stat_xp` attribute
(a dict {main_sub: float}). Each time the accumulated XP passes a rising
threshold the stored base sub-stat increases by one. Higher sub-stats
take more XP, so growth slows but never stops.

Main-stat columns locked by a species (e.g. Visarii corpus, Silex animus)
never gain XP and stay at 0.
"""

from world.systems.stats import sub_stat_is_locked

# Threshold to raise a sub-stat by one: base + per-point scaling. Tuned
# numbers; "better values later".
_THRESHOLD_BASE = 5.0
_THRESHOLD_PER_STAT = 3.0


def threshold_for(value):
    """Stat XP required to raise a sub-stat from `value` to `value + 1`."""
    return _THRESHOLD_BASE + _THRESHOLD_PER_STAT * value


def stat_xp(char, main, sub):
    """Current accumulated stat XP for a sub-stat."""
    return float(char.stat_xp.get(f"{main}_{sub}", 0.0))


def stat_xp_to_next(char, main, sub):
    """Stat XP still needed to raise the sub-stat by one."""
    base = getattr(char, f"{main}_{sub}")
    return max(0.0, threshold_for(base) - stat_xp(char, main, sub))


def add_stat_xp(char, main, sub, amount):
    """
    Grant stat XP to a sub-stat, raising the stored base by one for every
    full threshold crossed.

    Returns:
        tuple: (success, gained, new_value) where success is False if the
        main-stat column is locked (nothing was gained), gained is the
        number of +1 raises, and new_value is the resulting base (or None
        if locked).
    """
    if getattr(char, "is_wisp", False):
        return False, 0, None
    if sub_stat_is_locked(char, main):
        return False, 0, None

    key = f"{main}_{sub}"
    base = getattr(char, f"{main}_{sub}")
    acc = stat_xp(char, main, sub) + amount

    gained = 0
    while acc >= threshold_for(base):
        acc -= threshold_for(base)
        base += 1
        gained += 1

    xp = dict(char.stat_xp)
    xp[key] = acc
    char.stat_xp = xp

    if gained:
        setattr(char, f"{main}_{sub}", base)
    return True, gained, base
