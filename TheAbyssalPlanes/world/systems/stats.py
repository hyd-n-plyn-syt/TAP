"""
Stat schema and derived-stat formulas.

The nine base sub-stats (main x sub) are stored as Attributes on characters
under the "stat" category. Main stats are the sum of their three sub-stats.
Derived pools (Vigor, Vim, Mens) and their regen rates are computed on the
fly and are never stored.

Pool formulas scale the baseline engine by 3 and the flat capacity bonuses
by 2. Regen formulas floor-divide the same engine by 6, Reflexus by 4 and
the cross-stat by 8, and guarantee a minimum recovery of 1 per tick. This
holds the full-heal ratio near a constant ~16 ticks at any stat level.

All division in the derived formulas uses floor division (integer).
"""

MAIN_STATS = ("corpus", "genius", "animus")
SUB_STATS = ("potestas", "reflexus", "obsistis")

POOL_KEYS = ("vigor", "vim", "mens")

BASE_DEFAULTS = {f"{main}_{sub}": 1 for main in MAIN_STATS for sub in SUB_STATS}


def main_stat(char, main):
    """Return the value of a main stat (the sum of its three sub-stats)."""
    if main not in MAIN_STATS:
        raise ValueError(f"Unknown main stat: {main}")
    return sum(getattr(char, f"{main}_{sub}") for sub in SUB_STATS)


def derived_pools(char):
    """Compute all six derived pools for a character and return them as a dict."""
    corpus = main_stat(char, "corpus")
    genius = main_stat(char, "genius")
    animus = main_stat(char, "animus")

    cp = char.corpus_potestas
    cr = char.corpus_reflexus
    co = char.corpus_obsistis
    gp = char.genius_potestas
    gr = char.genius_reflexus
    go = char.genius_obsistis
    ap = char.animus_potestas
    ar = char.animus_reflexus
    ao = char.animus_obsistis

    return {
        "vigor": ((corpus + co) * 3) + ((cp + go) * 2),
        "vigor_regen": 1 + ((corpus + co) // 6) + (cr // 4) + (go // 8),
        "vim": ((animus + ao) * 3) + ((ap + go) * 2),
        "vim_regen": 1 + ((animus + ao) // 6) + (ar // 4) + (go // 8),
        "mens": ((genius + go) * 3) + ((gp + co) * 2),
        "mens_regen": 1 + ((genius + go) // 6) + (gr // 4) + (co // 8),
    }
