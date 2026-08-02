"""
Stat schema and derived-stat formulas.

The nine base sub-stats (main x sub) are stored as Attributes on characters
under the "stat" category. Main stats are the sum of their three sub-stats.
Derived pools (Vigor, Vim, Mens) and their regen rates are computed on the
fly and are never stored.

Species bonuses are applied persistently: the effective value of a sub-stat
is its stored base plus any species bonus. A species may also lock a whole
main-stat column (forced to 0) and/or pin a derived pool to 0.

Pool formulas scale the baseline engine by 3 and the flat capacity bonuses
by 2. Regen formulas floor-divide the same engine by 6, Reflexus by 4 and
the cross-stat by 8, and guarantee a minimum recovery of 1 per tick. This
holds the full-heal ratio near a constant ~16 ticks at any stat level.

All division in the derived formulas uses floor division (integer).
"""

from world.data import species

MAIN_STATS = ("corpus", "genius", "animus")
SUB_STATS = ("potestas", "reflexus", "obsistis")

POOL_KEYS = ("vigor", "vim", "mens")

BASE_DEFAULTS = {f"{main}_{sub}": 1 for main in MAIN_STATS for sub in SUB_STATS}


def _species_key(char):
    """Return the character's stored species key (or None)."""
    db = getattr(char, "db", None)
    if db is None:
        return None
    return getattr(db, "species_key", None)


def species_bonus(char, main, sub):
    """Return the persistent species bonus for a sub-stat (0 if none)."""
    return species.stat_bonus(_species_key(char), f"{main}_{sub}")


def sub_stat_is_locked(char, main):
    """Return True if the whole main-stat column is locked at 0."""
    return species.is_locked(_species_key(char), main)


def zero_pools(char):
    """Return the tuple of derived pools pinned to 0 for this character."""
    return species.zeroed_pools(_species_key(char))


def effective_sub_stat(char, main, sub):
    """Return the effective sub-stat: stored base + species bonus, or 0 if the
    main-stat column is locked."""
    if sub_stat_is_locked(char, main):
        return 0
    return getattr(char, f"{main}_{sub}") + species_bonus(char, main, sub)


def main_stat(char, main):
    """Return the value of a main stat (the sum of its three effective sub-stats)."""
    if main not in MAIN_STATS:
        raise ValueError(f"Unknown main stat: {main}")
    return sum(effective_sub_stat(char, main, sub) for sub in SUB_STATS)


def derived_pools(char):
    """Compute all six derived pools for a character and return them as a dict.
    Pools pinned to 0 by the character's species are returned as 0."""
    corpus = main_stat(char, "corpus")
    genius = main_stat(char, "genius")
    animus = main_stat(char, "animus")

    cp = effective_sub_stat(char, "corpus", "potestas")
    cr = effective_sub_stat(char, "corpus", "reflexus")
    co = effective_sub_stat(char, "corpus", "obsistis")
    gp = effective_sub_stat(char, "genius", "potestas")
    gr = effective_sub_stat(char, "genius", "reflexus")
    go = effective_sub_stat(char, "genius", "obsistis")
    ap = effective_sub_stat(char, "animus", "potestas")
    ar = effective_sub_stat(char, "animus", "reflexus")
    ao = effective_sub_stat(char, "animus", "obsistis")

    pools = {
        "vigor": ((corpus + co) * 3) + ((cp + go) * 2),
        "vigor_regen": 1 + ((corpus + co) // 6) + (cr // 4) + (go // 8),
        "vim": ((animus + ao) * 3) + ((ap + go) * 2),
        "vim_regen": 1 + ((animus + ao) // 6) + (ar // 4) + (go // 8),
        "mens": ((genius + go) * 3) + ((gp + co) * 2),
        "mens_regen": 1 + ((genius + go) // 6) + (gr // 4) + (co // 8),
    }
    for pool in zero_pools(char):
        pools[pool] = 0
        pools[f"{pool}_regen"] = 0
    return pools
