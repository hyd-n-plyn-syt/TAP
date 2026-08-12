"""
Accuracy calculation system for The Abyssal Planes.

Handles attack rolls, defense rolls, and critical hit checks.
"""
from world.data import skills as skill_data
from world.systems import stats


def get_attack_roll(char, skill_key, skill_value):
    """Calculate the attacker's accuracy roll.

    Attack Roll = skill_value + (main_stat_reflexus * 0.5)
    """
    skill_info = skill_data.get_skill(skill_key)
    if not skill_info:
        return 0

    category = skill_info["category"]
    reflexus = stats.effective_sub_stat(char, category, "reflexus")

    return skill_value + (reflexus * 0.5)


def get_defense_roll(char, attack_skill_key):
    """Calculate the defender's best applicable defense roll.

    Returns the highest value among applicable defensive skills.
    """
    skills = getattr(char.db, "skills", {}) or {}

    defense_skills = ["melee_evasion", "melee_parry", "melee_block"]
    best_roll = 0

    for def_skill in defense_skills:
        def_value = skills.get(def_skill, 0)
        if def_value <= 0:
            continue

        skill_info = skill_data.get_skill(def_skill)
        if not skill_info:
            continue

        reflexus = stats.effective_sub_stat(char, "corpus", "reflexus")
        obsistis = stats.effective_sub_stat(char, "corpus", "obsistis")

        roll = 0
        for stat_name, weight in skill_info["stats"].items():
            main, sub = stat_name.rsplit("_", 1)
            if sub == "reflexus":
                roll += reflexus * weight
            elif sub == "obsistis":
                roll += obsistis * weight

        roll += def_value

        if roll > best_roll:
            best_roll = roll

    return best_roll


def resolve_hit(attacker, defender, skill_key, skill_value):
    """Resolve an attack: roll accuracy, roll defense, determine hit/miss.

    Returns (hit, attack_roll, defense_roll, is_crit).
    """
    from combat.damage import check_critical

    attack_roll = get_attack_roll(attacker, skill_key, skill_value)
    defense_roll = get_defense_roll(defender, skill_key)

    hit = attack_roll > defense_roll
    is_crit, margin = check_critical(attacker, defender, skill_key, skill_value, attack_roll, defense_roll)

    return hit, attack_roll, defense_roll, is_crit


def get_reach(skill_key):
    """Get the reach distance for a skill."""
    skill_info = skill_data.get_skill(skill_key)
    if not skill_info:
        return 0
    return skill_info.get("reach", 0)


def check_range(attacker, target, skill_key):
    """Check if target is within reach of the attack.

    Returns (in_range, distance).
    """
    ax = getattr(attacker.db, "pos_x", None) or 0
    ay = getattr(attacker.db, "pos_y", None) or 0
    tx = getattr(target.db, "pos_x", None) or 0
    ty = getattr(target.db, "pos_y", None) or 0

    distance = max(abs(ax - tx), abs(ay - ty))
    reach = get_reach(skill_key)

    return distance <= reach, distance
