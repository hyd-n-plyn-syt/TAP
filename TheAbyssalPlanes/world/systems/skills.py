"""
Skill system core.

Skill values (0-1000) live on the character's `skills` attribute as a dict
{key: int}. XP earned per use accumulates in `skills_xp` ({key: float}) and
is converted into skill points as it crosses a per-tier point cost.

Diminishing returns run on two axes at once:

  * A skill's own value is harder to raise at higher tiers - per-use XP
    tapers with rank AND the per-point cost rises with tier.
  * The stat XP it feeds its linked statistics also tapers with rank, so
    a mastered skill keeps granting growth, but slowly - nudging you to
    branch out into new skills.

Every action command that exercises a skill should call:

    result = caller.use_skill("dodge", difficulty="hard")

The `difficulty` key maps to a base XP via world.data.skills.DIFFICULTY_XP.
"""

from world.data import skills as data
from world.data import species as species_data
from world.systems import growth

# --- Tunable numbers ---
POINT_COST_BASE = 10.0      # XP needed for the first skill point (tier 1)
POINT_COST_GROWTH = 0.5     # extra point cost per tier beyond the first
SKILL_TAPER_RATE = 0.15     # per-use XP shrink per tier beyond the first
STAT_TAPER_RATE = 0.25      # stat-XP shrink per tier beyond the first
MAX_SKILL = 1000            # grandmaster cap

# --- Value / tier math ---


def tier(value):
    """Return the 1-10 tier for a skill value (0-1000)."""
    value = max(0, int(value or 0))
    return min(10, (value // 100) + 1)


def tier_name(value):
    """Return the display name of the tier a value is in."""
    return data.TIER_NAMES[tier(value) - 1]


def tier_colored_name(value):
    """Return the tier name wrapped in its display color."""
    t = tier(value)
    return f"|{data.tier_color(t)}{data.TIER_NAMES[t - 1]}|n"


def requirement_str(value):
    """
    Display a skill value as 'NN% TierName' for requirements and thresholds,
    e.g. '0% Adept', '50% Master', '30% Apprentice'.
    """
    return f"{within_tier(value)}% {tier_name(value)}"


def within_tier(value):
    """Return the 0-99 progress within the current tier."""
    return int(value or 0) % 100


def point_cost(tier_no):
    """XP required for one skill point while in a given tier."""
    return POINT_COST_BASE * (1 + POINT_COST_GROWTH * (tier_no - 1))


def skill_taper(tier_no):
    """Multiplier shrinking per-use XP as rank grows (0-1)."""
    return 1.0 / (1.0 + SKILL_TAPER_RATE * (tier_no - 1))


def stat_taper(tier_no):
    """Multiplier shrinking stat pass-through as rank grows (0-1)."""
    return 1.0 / (1.0 + STAT_TAPER_RATE * (tier_no - 1))

# --- Accessors ---


def skill_value(char, key):
    """Return a character's value for a skill (0 if never trained)."""
    return int(char.skills.get(key, 0))


def known_skills(char):
    """Return sorted [(key, value), ...] for every skill on a character."""
    return sorted(char.skills.items(), key=lambda kv: kv[0])


def prereqs_met(char, key):
    """True if the character meets the skill's prerequisites."""
    skill = data.get_skill(key)
    if not skill:
        return False
    for prereq, minimum in skill["requires"].items():
        if skill_value(char, prereq) < minimum:
            return False
    return True


def missing_prereqs(char, key):
    """Return {prereq_key: (current, needed)} for unmet prerequisites."""
    skill = data.get_skill(key)
    missing = {}
    for prereq, minimum in (skill or {}).get("requires", {}).items():
        if skill_value(char, prereq) < minimum:
            missing[prereq] = (skill_value(char, prereq), minimum)
    return missing


def learn_skill(char, key, value=None):
    """
    Add a skill to the character (starting at 0, or at `value` if given).

    Returns:
        tuple: (success, error_message) where success is False if the skill
        is unknown or its prerequisites are not met.
    """
    skill = data.get_skill(key)
    if not skill:
        return False, "Unknown skill."
    if not prereqs_met(char, key):
        reqs = ", ".join(
            f"{data.get_skill(r)['name']} {requirement_str(v)}"
            for r, v in skill["requires"].items()
        )
        return False, f"Requires: {reqs}."
    learned = dict(char.skills)
    learned[skill["key"]] = min(MAX_SKILL, max(0, int(value or 0)))
    char.skills = learned
    return True, None


def xp_to_next(char, key):
    """XP remaining before the next skill point."""
    val = skill_value(char, key)
    buf = float(char.skills_xp.get(key, 0.0))
    return point_cost(tier(val)) - buf


def effective_skill_stats(char, key):
    """
    The {sub_stat: weight} mapping a skill actually exercises for a character.

    Species with a locked main (e.g. Visarii corpus, Silex animus) exercise
    their alternate main instead, preserving the sub-stat slot and weight.
    Returns an empty dict for an unknown skill.
    """
    skill = data.get_skill(key)
    if not skill:
        return {}
    stats = {}
    for stat, weight in skill["stats"].items():
        main, sub = stat.split("_", 1)
        alt = species_data.alternate_for(char.species_key, main)
        stats[f"{alt or main}_{sub}"] = stats.get(f"{alt or main}_{sub}", 0) + weight
    return stats

# --- Use / growth ---


def use_skill(char, key, difficulty="medium", times=1):
    """
    Exercise a skill: award skill XP, advance its value, and feed the
    linked statistics.

    Args:
        char (Character): The acting character.
        key (str): Skill key.
        difficulty (str): One of data.DIFFICULTY_XP keys.
        times (int): Repeat the base award this many times (bulk use).

    Returns:
        dict or None: None if the skill is unknown. Otherwise a dict with
        success, reason (if failed), value, tier, tier_name, skill_xp and
        stat_xp (if successful).
    """
    skill = data.get_skill(key)
    if not skill:
        return None

    if key not in char.skills:
        return {"success": False, "reason": "unknown", "skill": key}

    if not prereqs_met(char, key):
        return {"success": False, "reason": "prereq", "skill": key}

    base = data.DIFFICULTY_XP.get(difficulty, 15) * max(1, int(times))
    start_tier = tier(skill_value(char, key))
    gain = base * skill_taper(start_tier)

    # Advance the skill value by converting buffered XP into points.
    skills = dict(char.skills)
    xp = dict(char.skills_xp)
    skills.setdefault(key, 0)
    buf = xp.get(key, 0.0) + gain
    while buf >= point_cost(tier(skills[key])) and skills[key] < MAX_SKILL:
        buf -= point_cost(tier(skills[key]))
        skills[key] += 1
    xp[key] = buf
    char.skills = skills
    char.skills_xp = xp

    # Feed the linked statistics (diminishing with the skill's rank). Locked
    # mains are remapped to the species' alternate (see effective_skill_stats).
    stat_total = gain * stat_taper(start_tier)
    for stat, weight in effective_skill_stats(char, key).items():
        main, sub = stat.split("_", 1)
        growth.add_stat_xp(char, main, sub, stat_total * weight)

    final = skills[key]
    return {
        "success": True,
        "skill": key,
        "value": final,
        "tier": tier(final),
        "tier_name": data.TIER_NAMES[tier(final) - 1],
        "skill_xp": gain,
        "stat_xp": stat_total,
    }
