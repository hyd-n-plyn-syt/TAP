"""
Stat ranking ladder for The Abyssal Planes.

Pure data module - no Evennia imports.

Each main stat (Corpus, Genius, Animus) is ranked by the sum of its three
sub-stats. The ladder is shared across all three mains. A fully locked
main reads a total of 0 and shows rank "none".

The numeric thresholds below are placeholders to be tuned later.
"""

# Ascending (min_total, rank_name) pairs. A total is mapped to the highest
# rank whose minimum it reaches.
RANKS = (
    (0, "none"),
    (1, "feeble"),
    (5, "weak"),
    (9, "poor"),
    (13, "below average"),
    (17, "average"),
    (21, "good"),
    (26, "impressive"),
    (32, "formidable"),
    (39, "legendary"),
    (47, "mythic"),
    (56, "divine"),
    (66, "godlike"),
    (81, "ungodly"),
)


def rank_index(total):
    """Return the index into RANKS for a main-stat total (0-based)."""
    idx = 0
    for i, (minimum, _) in enumerate(RANKS):
        if total >= minimum:
            idx = i
    return idx


def rank_name(total):
    """Return the rank name for a main-stat total."""
    return RANKS[rank_index(total)][1]


def rank_threshold(index):
    """Return the minimum total for a rank index, or None."""
    if 0 <= index < len(RANKS):
        return RANKS[index][0]
    return None
