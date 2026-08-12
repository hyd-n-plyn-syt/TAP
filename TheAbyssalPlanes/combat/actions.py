"""
Action system for The Abyssal Planes.

Manages the combat action queue, time costs, pool costs, and resolution.
"""
from world.data import skills as skill_data


MAX_ACTION_QUEUE = 3


def get_actions_remaining(char):
    """Get remaining movement/action budget for the round.

    Returns seconds remaining (0-6).
    """
    return getattr(char.db, "movement_used", 0)


def set_actions_used(char, seconds):
    """Set the movement/action budget used this round."""
    char.db.movement_used = seconds


def can_perform_action(char, skill_key):
    """Check if a character can perform an action.

    Returns (can_perform, reason).
    """
    skills = getattr(char.db, "skills", {}) or {}
    skill_value = skills.get(skill_key, 0)

    if skill_key not in skills:
        return False, f"You don't know {skill_key}."

    skill_info = skill_data.get_skill(skill_key)
    if not skill_info:
        return False, "Unknown skill."

    for req_key, req_val in skill_info.get("requires", {}).items():
        req_val_got = skills.get(req_key, 0)
        if req_val_got < req_val:
            return False, f"Requires {req_key} at {req_val}."

    pool = skill_info.get("pool_cost", 0)
    health_bar = skill_info.get("health_bar")
    if pool > 0 and health_bar:
        from world.data.species import resolve_pool
        effective_pool = resolve_pool(getattr(char.db, "species_key", ""), health_bar)
        current = getattr(char.db, f"{effective_pool}_current", None)
        if current is None:
            from world.systems.stats import derived_pools
            pools = derived_pools(char)
            current = pools.get(effective_pool, 0)
        if current < pool:
            return False, f"Not enough {effective_pool}. Need {pool}, have {current}."

    return True, "OK"


def queue_action(char, action_type, skill_key, target=None):
    """Add an action to the character's action queue.

    Returns (success, message).
    """
    queue = list(getattr(char.db, "action_queue", None) or [])

    if len(queue) >= MAX_ACTION_QUEUE:
        return False, f"Action queue is full (max {MAX_ACTION_QUEUE})."

    can_do, reason = can_perform_action(char, skill_key)
    if not can_do:
        return False, reason

    skill_info = skill_data.get_skill(skill_key)
    skill_value = getattr(char.db, "skills", {}).get(skill_key, 0)
    actual_time = skill_data.time_cost(skill_value, skill_info["base_time"])

    action = {
        "type": action_type,
        "skill": skill_key,
        "target_dbref": target.id if target else None,
        "time_cost": actual_time,
    }

    queue.append(action)
    char.db.action_queue = queue

    return True, f"Queued {skill_info['name']} ({actual_time}s)."


def pop_action(char):
    """Pop the next action from the queue.

    Returns (action, time_cost) or (None, 0).
    """
    queue = list(getattr(char.db, "action_queue", None) or [])
    if not queue:
        return None, 0

    action = queue.pop(0)
    char.db.action_queue = queue if queue else None

    return action, action.get("time_cost", 0)


def clear_action_queue(char):
    """Clear the action queue."""
    char.db.action_queue = None


def get_queue_display(char):
    """Return a formatted string of the action queue."""
    queue = getattr(char.db, "action_queue", None) or []
    if not queue:
        return "No actions queued."

    lines = []
    for i, action in enumerate(queue, 1):
        skill_info = skill_data.get_skill(action["skill"])
        name = skill_info["name"] if skill_info else action["skill"]
        time = action.get("time_cost", 0)
        lines.append(f"  {i}. {name} ({time}s)")

    return "\n".join(lines)
