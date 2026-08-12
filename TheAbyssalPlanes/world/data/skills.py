"""
Skill catalog for The Abyssal Planes.

Pure data module - no Evennia imports, so it can be imported anywhere.

A skill is defined by:

    key       - machine key (lowercase, underscores)
    name      - display name
    category  - grouping (corpus, genius, animus)
    stats     - {sub_stat: weight} the weighted sub-stats this skill
                exercises. Weights sum to 1.0. A skill may tie to a single
                sub-stat (weight 1.0) or spread across several.
    requires  - {skill_key: min_value} prerequisites. The named skill must
                be at least `min_value` (0-1000) before this skill can be
                learned or used.
    precursor - skill key that governs this skill's damage/time modifiers
    reach     - grid distance for targeting (1=adjacent, 0=self)
    damage_type - physical, psychic, or magical
    health_bar - vigor, mens, or vim
    base_time - base seconds to execute (reduced by skill level)
    pool_cost - flat pool cost per use (optional)
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
    # --- Precursor Skills ---
    "brawling": {
        "key": "brawling",
        "name": "Brawling",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.55, "corpus_reflexus": 0.45},
        "requires": {},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
        "desc": "The foundation of unarmed combat. Governs all brawling skills.",
    },
    # --- Brawling Offense ---
    "punch": {
        "key": "punch",
        "name": "Punch",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.6, "corpus_reflexus": 0.4},
        "requires": {},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 2.0,
        "pool_cost": 2,
        "desc": "An unarmed, clubbing blow.",
    },
    "kick": {
        "key": "kick",
        "name": "Kick",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.7, "corpus_reflexus": 0.3},
        "requires": {},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 2.0,
        "pool_cost": 2,
        "desc": "A heavy leg strike.",
    },
    "headbutt": {
        "key": "headbutt",
        "name": "Headbutt",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.55, "corpus_obsistis": 0.45},
        "requires": {"punch": 100, "kick": 100},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 2.5,
        "pool_cost": 3,
        "desc": "Driving your skull into the foe.",
    },
    "knee": {
        "key": "knee",
        "name": "Knee",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.65, "corpus_reflexus": 0.35},
        "requires": {"punch": 150, "kick": 150},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 2.5,
        "pool_cost": 3,
        "desc": "A driving knee to the midsection.",
    },
    "axehandle": {
        "key": "axehandle",
        "name": "Axehandle",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.75, "corpus_obsistis": 0.25},
        "requires": {"headbutt": 200, "knee": 200},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 3.0,
        "pool_cost": 4,
        "desc": "A downward chopping strike with the forearm.",
    },
    "haymaker": {
        "key": "haymaker",
        "name": "Haymaker",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.8, "corpus_reflexus": 0.2},
        "requires": {"axehandle": 300},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 3.0,
        "pool_cost": 5,
        "desc": "A wide, powerful swing with full body weight.",
    },
    # --- Brawling Defense ---
    "melee_evasion": {
        "key": "melee_evasion",
        "name": "Melee Evasion",
        "category": "corpus",
        "stats": {"corpus_reflexus": 1.0},
        "requires": {},
        "precursor": "brawling",
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 2.0,
        "pool_cost": 0,
        "desc": "Dodging out of harm's way.",
    },
    "melee_parry": {
        "key": "melee_parry",
        "name": "Melee Parry",
        "category": "corpus",
        "stats": {"corpus_reflexus": 0.7, "corpus_obsistis": 0.3},
        "requires": {"melee_evasion": 100},
        "precursor": "brawling",
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 2.5,
        "pool_cost": 0,
        "desc": "Deflecting a blow with your arm or body.",
    },
    "melee_block": {
        "key": "melee_block",
        "name": "Melee Block",
        "category": "corpus",
        "stats": {"corpus_obsistis": 0.7, "corpus_reflexus": 0.3},
        "requires": {"melee_evasion": 100},
        "precursor": "brawling",
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 2.5,
        "pool_cost": 0,
        "desc": "Absorbing a hit with your guard up.",
    },
    "melee_feint": {
        "key": "melee_feint",
        "name": "Melee Feint",
        "category": "corpus",
        "stats": {"corpus_reflexus": 0.7, "genius_reflexus": 0.3},
        "requires": {"melee_parry": 200, "melee_block": 200},
        "precursor": "brawling",
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 1.0,
        "pool_cost": 0,
        "desc": "A false opening that baits an overcommit.",
    },
    "melee_counterattack": {
        "key": "melee_counterattack",
        "name": "Melee Counterattack",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.55, "corpus_reflexus": 0.45},
        "requires": {"melee_feint": 300},
        "precursor": "brawling",
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 3.0,
        "pool_cost": 4,
        "desc": "Striking back immediately after a successful defense.",
    },
    # --- Utility ---
    "bash": {
        "key": "bash",
        "name": "Bash",
        "category": "corpus",
        "stats": {"corpus_potestas": 0.8, "corpus_obsistis": 0.2},
        "requires": {},
        "precursor": None,
        "reach": 1,
        "damage_type": "physical",
        "health_bar": "mens",
        "base_time": 2.5,
        "pool_cost": 3,
        "desc": "Blunt force applied to doors, walls, and obstacles.",
    },
    # --- Genius ---
    "meditate": {
        "key": "meditate",
        "name": "Meditate",
        "category": "genius",
        "stats": {"genius_reflexus": 0.6, "genius_obsistis": 0.4},
        "requires": {},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
        "desc": "Centering the mind; deepens rest.",
    },
    "focused_meditation": {
        "key": "focused_meditation",
        "name": "Focused Meditation",
        "category": "genius",
        "stats": {"genius_obsistis": 0.7, "genius_reflexus": 0.3},
        "requires": {"meditate": 400},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
        "desc": "Meditation refined into near-trance.",
    },
    "lockpick": {
        "key": "lockpick",
        "name": "Lockpick",
        "category": "genius",
        "stats": {"genius_reflexus": 0.7, "corpus_reflexus": 0.3},
        "requires": {},
        "precursor": None,
        "reach": 1,
        "damage_type": None,
        "health_bar": None,
        "base_time": 3.0,
        "pool_cost": 0,
        "desc": "Manipulating a lock mechanism without the proper key.",
    },
    "awareness": {
        "key": "awareness",
        "name": "Awareness",
        "category": "genius",
        "stats": {"genius_obsistis": 0.6, "genius_reflexus": 0.4},
        "requires": {},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
        "desc": "Noticing what is hidden, concealed, or out of place.",
    },
    # --- Animus ---
    "pray": {
        "key": "pray",
        "name": "Pray",
        "category": "animus",
        "stats": {"animus_potestas": 0.55, "animus_obsistis": 0.45},
        "requires": {},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
        "desc": "Communion with something greater; deepens rest.",
    },
    "devoted_prayer": {
        "key": "devoted_prayer",
        "name": "Devoted Prayer",
        "category": "animus",
        "stats": {"animus_obsistis": 0.7, "animus_potestas": 0.3},
        "requires": {"pray": 400},
        "precursor": None,
        "reach": 0,
        "damage_type": None,
        "health_bar": None,
        "base_time": 0,
        "pool_cost": 0,
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


def precursor_for(key):
    """Return the precursor skill key for a skill, or None."""
    skill = get_skill(key)
    return skill.get("precursor") if skill else None


def time_cost(skill_value, base_time):
    """Calculate actual time cost based on skill level.

    Time decreases as skill increases: grandmaster (1000) = 50% of base.
    Always returns a whole number of seconds (minimum 1).
    """
    if base_time <= 0:
        return 0
    import math
    reduction = skill_value / 1000.0
    actual = base_time * (1.0 - reduction * 0.5)
    return max(1, math.ceil(actual))


def tier_color(tier_no):
    """Return the ANSI color code letter for a 1-10 tier number."""
    idx = max(0, min(tier_no - 1, len(TIER_COLORS) - 1))
    return TIER_COLORS[idx]
