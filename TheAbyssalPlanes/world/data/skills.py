"""
Skill catalog for The Abyssal Planes.

Pure data module - no Evennia imports, so it can be imported anywhere.

A skill is defined by:

    key       - machine key (lowercase, underscores)
    name      - display name
    category  - grouping (combat, meta, ...)
    stats     - {sub_stat: weight} the weighted sub-stats this skill
                exercises. Weights sum to 1.0. A skill may tie to a single
                sub-stat (weight 1.0) or spread across several.
    requires  - {skill_key: min_value} prerequisites. The named skill must
                be at least `min_value` (0-1000) before this skill can be
                learned or used.
    desc      - one-line flavor/use note

Skill values run 0-1000 across 10 tiers. Tier 1 covers 0-99, tier 10
covers 900-1000. Values grow only by use; see world/systems/skills.py
for the diminishing-returns math and world/systems/growth.py for how
skills feed the uncapped statistics.
"""

# Ten tiers from first contact to mastery. 0-99 is tier 1, 900-1000 is
# tier 10 (grandmaster). TIER_COLORS holds the ANSI color code shown with
# each tier name where it is displayed.
TIER_NAMES = (
    "Novice",
    "Apprentice",
    "Journeyman",
    "Adept",
    "Expert",
    "Artisan",
    "Master",
    "High Master",
    "Archmaster",
    "Grandmaster",
)

TIER_COLORS = (
    "x",
    "r",
    "R",
    "y",
    "g",
    "G",
    "c",
    "C",
    "m",
    "W",
)

# Base skill XP awarded per use, by difficulty. Tuned numbers - see
# world/systems/skills.py for how they are tapered by rank.
DIFFICULTY_XP = {
    "trivial": 5,
    "easy": 10,
    "medium": 15,
    "hard": 25,
    "extreme": 40,
}

SKILLS = {
    # --- Corpus ---
    "dodge": {
        "key": "dodge",
        "name": "Dodge",
        "category": "corpus",
        "stats": {"corpus_reflexus": 1.0},
        "requires": {},
        "desc": "Slipping out of harm's way.",
    },
    "parry": {
        "key": "parry",
        "name": "Parry",
        "category": "corpus",
        "stats": {"corpus_reflexus": 1.0},
        "requires": {},
        "desc": "Deflecting an incoming blow with a held weapon.",
    },
    "attack": {
        "key": "attack",
        "name": "Attack",
        "category": "corpus",
        "stats": {"corpus_potestas": 1.0},
        "requires": {},
        "desc": "Striking with intent to harm, weapon in hand.",
    },
    "block": {
        "key": "block",
        "name": "Block",
        "category": "corpus",
        "stats": {"corpus_obsistis": 1.0},
        "requires": {},
        "desc": "Shielding with a held object or an arm.",
    },
    "punch": {
        "key": "punch",
        "name": "Punch",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.6, "corpus_reflexus": 0.4},
        "requires": {},
        "desc": "An unarmed, clubbing blow.",
    },
    "kick": {
        "key": "kick",
        "name": "Kick",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.7, "corpus_reflexus": 0.3},
        "requires": {},
        "desc": "A heavy leg strike.",
    },
    "headbutt": {
        "key": "headbutt",
        "name": "Headbutt",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.55, "corpus_obsistis": 0.45},
        "requires": {},
        "desc": "Driving your skull into the foe.",
    },
    "power_strike": {
        "key": "power_strike",
        "name": "Power Strike",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.8, "corpus_obsistis": 0.2},
        "requires": {"attack": 300, "punch": 300},
        "desc": "A telegraphed, crushing swing.",
    },
    "feint": {
        "key": "feint",
        "name": "Feint",
        "category": "corpus",
        "stats": {"corpus_reflexus": 0.7, "genius_reflexus": 0.3},
        "requires": {"dodge": 300, "parry": 300},
        "desc": "A false opening that baits an overcommit.",
    },
    "bash": {
        "key": "bash",
        "name": "Bash",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.8, "corpus_obsistis": 0.2},
        "requires": {},
        "desc": "Blunt force applied to doors, walls, and obstacles.",
    },
    # --- Genius ---
    "meditate": {
        "key": "meditate",
        "name": "Meditate",
        "category": "genius",
        "stats": {"genius_reflexus": 0.6, "genius_obsistis": 0.4},
        "requires": {},
        "desc": "Centering the mind; deepens rest.",
    },
    "focused_meditation": {
        "key": "focused_meditation",
        "name": "Focused Meditation",
        "category": "genius",
        "stats": {"genius_obsistis": 0.7, "genius_reflexus": 0.3},
        "requires": {"meditate": 400},
        "desc": "Meditation refined into near-trance.",
    },
    "lockpick": {
        "key": "lockpick",
        "name": "Lockpick",
        "category": "genius",
        "stats": {"genius_reflexus": 0.7, "corpus_reflexus": 0.3},
        "requires": {},
        "desc": "Manipulating a lock mechanism without the proper key.",
    },
    "awareness": {
        "key": "awareness",
        "name": "Awareness",
        "category": "genius",
        "stats": {"genius_obsistis": 0.6, "genius_reflexus": 0.4},
        "requires": {},
        "desc": "Noticing what is hidden, concealed, or out of place.",
    },
    # --- Animus ---
    "pray": {
        "key": "pray",
        "name": "Pray",
        "category": "animus",
        "stats": {"animus_potestas": 0.55, "animus_obsistis": 0.45},
        "requires": {},
        "desc": "Communion with something greater; deepens rest.",
    },
    "devoted_prayer": {
        "key": "devoted_prayer",
        "name": "Devoted Prayer",
        "category": "animus",
        "stats": {"animus_obsistis": 0.7, "animus_potestas": 0.3},
        "requires": {"pray": 400},
        "desc": "Sustained prayer that steadies the spirit.",
    },
}


def get_skill(key):
    """Return the skill dict for a key, or None."""
    if not key:
        return None
    return SKILLS.get(str(key).strip().lower())


def skill_key(name):
    """Resolve a skill key from a key or display name (case-insensitive)."""
    name = str(name).strip().lower().replace(" ", "_")
    if name in SKILLS:
        return name
    for key, skill in SKILLS.items():
        if skill["name"].lower().replace(" ", "_") == name:
            return key
    return None


def all_skills():
    """Return the full skill catalog dict."""
    return dict(SKILLS)


def categories():
    """Return the skill categories present in the catalog, sorted."""
    return sorted({skill["category"] for skill in SKILLS.values()})


def stats_for(key):
    """Return the {sub_stat: weight} mapping for a skill key, or None."""
    skill = get_skill(key)
    return skill["stats"] if skill else None


def tier_color(tier_no):
    """Return the ANSI color code letter for a 1-10 tier number."""
    idx = max(0, min(tier_no - 1, len(TIER_COLORS) - 1))
    return TIER_COLORS[idx]
