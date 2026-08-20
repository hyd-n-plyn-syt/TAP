"""
Damage calculation system for The Abyssal Planes.

Handles base damage, variation, armor reduction, and critical hits.
"""
import random

from world.data import skills as skill_data
from world.systems import stats


def get_damage_stats(char, skill_key):
    """Get the main stat and highest sub-stat for a skill's damage calculation.

    Returns (main_stat_name, main_stat_value, sub_stat_value, skill_stats).
    """
    skill_stats = skill_data.stats_for(skill_key)
    if not skill_stats:
        return None, 0, 0, {}

    category = skill_data.get_skill(skill_key)["category"]
    main_stat_name = category

    main_val = stats.main_stat(char, main_stat_name)

    highest_sub = 0
    for sub_name, weight in skill_stats.items():
        main, sub = sub_name.rsplit("_", 1)
        effective = stats.effective_sub_stat(char, main, sub)
        if effective > highest_sub:
            highest_sub = effective

    return main_stat_name, main_val, highest_sub, skill_stats


def calculate_variation(skill_value):
    """Calculate damage variation based on skill level.

    Returns a multiplier between floor and ceiling.
    Skill 0 = 65-100%, Skill 1000 = 85-120%.
    """
    floor = 0.65 + ((skill_value / 1000.0) * 0.20)
    ceiling = 1.00 + ((skill_value / 1000.0) * 0.20)
    return random.uniform(floor, ceiling)


def get_precursor_bonus(char, skill_key):
    """Get the damage modifier from the precursor skill.

    Returns a percentage bonus (e.g., 0.1 for +10%).
    """
    precursor_key = skill_data.precursor_for(skill_key)
    if not precursor_key:
        return 0.0

    skills = getattr(char.db, "skills", {}) or {}
    precursor_value = skills.get(precursor_key, 0)

    return precursor_value / 1000.0


def get_armor_value(target, damage_type):
    """Get the total armor value for a damage type from all equipped armor.

    Returns the sum of armor[damage_type] across all worn armor pieces.
    """
    armor_total = 0
    for obj in (target.db.worn or []):
        armor = getattr(obj.db, "armor", None)
        if armor and damage_type in armor:
            armor_total += armor[damage_type]
    return armor_total


def calculate_base_damage(char, skill_key, skill_value):
    """Calculate base damage before armor reduction.

    Returns (base_damage, damage_type, health_bar).
    """
    skill_info = skill_data.get_skill(skill_key)
    if not skill_info:
        return 0, None, None

    main_name, main_val, sub_val, _ = get_damage_stats(char, skill_key)
    if main_name is None:
        return 0, None, None

    variation = calculate_variation(skill_value)
    precursor_bonus = get_precursor_bonus(char, skill_key)

    base = (main_val + sub_val) * variation
    base *= (1.0 + precursor_bonus)

    damage_type = skill_info.get("damage_type")
    health_bar = skill_info.get("health_bar")

    return base, damage_type, health_bar


def check_critical(attacker, defender, skill_key, skill_value, attack_roll, defense_roll):
    """Check if an attack is a critical hit.

    Critical occurs when margin >= threshold.
    Threshold decreases from 20.0 at skill 0 down to 5.0 at skill 1000.
    """
    margin = attack_roll - defense_roll
    threshold = max(5.0, 20.0 - (skill_value / 50.0))

    return margin >= threshold, margin


def apply_damage(target, health_bar, damage, is_crit=False):
    """Apply damage to a health bar.

    If is_crit, armor has already been negated in the caller.
    Returns (remaining, knocked_out).
    """
    from world.data.species import resolve_pool
    effective_pool = resolve_pool(getattr(target.db, "species_key", ""), health_bar)

    current = getattr(target.db, f"{effective_pool}_current", None)
    if current is None:
        pools = target.pools_current
        current = pools.get(effective_pool, 0)

    remaining = max(0, current - damage)
    setattr(target.db, f"{effective_pool}_current", remaining)

    from world.systems.regen import ensure_regen_timer
    if getattr(target, "is_creature", False) and getattr(target, "is_injured", False):
        ensure_regen_timer(target)

    knocked_out = remaining <= 0
    return remaining, knocked_out


def calculate_final_damage(char, skill_key, skill_value, target):
    """Full damage calculation: base → armor → final.

    Returns (final_damage, is_crit, health_bar, damage_type).
    """
    base, damage_type, health_bar = calculate_base_damage(char, skill_key, skill_value)
    if base <= 0 or not health_bar:
        return 0, False, health_bar, damage_type

    armor = get_armor_value(target, damage_type)
    final = int(round(max(0, base - armor)))

    return final, False, health_bar, damage_type
