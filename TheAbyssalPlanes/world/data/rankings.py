"""
Stat ranking ladder for The Abyssal Planes.

Pure data module - no Evennia imports.

Each main stat (Corpus, Genius, Animus) is ranked by the sum of its three
sub-stats. The ladder is shared across all three mains. A fully locked
main reads a total of 0 and shows rank "none".

The numeric thresholds below are placeholders to be tuned later.
"""

# Ascending (min_total, rank_name, color) pairs. A total is mapped to the
# highest rank whose minimum it reaches. Colors use Evennia ANSI codes,
# progressing from muted gray through red/yellow/green into blinding tiers.
RANKS = (
    (0, "none", "x"),
    (1, "feeble", "r"),
    (5, "weak", "r"),
    (9, "poor", "r"),
    (13, "below average", "r"),
    (17, "average", "y"),
    (21, "good", "y"),
    (26, "impressive", "g"),
    (32, "formidable", "g"),
    (39, "legendary", "c"),
    (47, "mythic", "C"),
    (56, "divine", "m"),
    (66, "godlike", "R"),
    (81, "ungodly", "W"),
)


def rank_index(total):
    """Return the index into RANKS for a main-stat total (0-based)."""
    idx = 0
    for i, (minimum, _, _) in enumerate(RANKS):
        if total >= minimum:
            idx = i
    return idx


def rank_name(total):
    """Return the rank name for a main-stat total."""
    return RANKS[rank_index(total)][1]


def rank_color(total):
    """Return the ANSI color code letter for a main-stat total's rank."""
    return RANKS[rank_index(total)][2]


def colored_rank_name(total):
    """Return the rank name wrapped in its display color, e.g. '|g[good]|n'."""
    idx = rank_index(total)
    return f"|{RANKS[idx][2]}[{RANKS[idx][1]}]|n"


def rank_threshold(index):
    """Return the minimum total for a rank index, or None."""
    if 0 <= index < len(RANKS):
        return RANKS[index][0]
    return None
