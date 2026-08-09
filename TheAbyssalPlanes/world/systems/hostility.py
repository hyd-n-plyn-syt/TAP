"""
Logic for checking if entities are hostile towards one another.
"""
from world.systems.group import GroupManager

def is_hostile(actor, target):
    """Checks if target is explicitly marked as hostile."""
    return getattr(target.db, "is_hostile", False)

def hostile_towards(actor, target):
    """
    Checks if target is hostile towards actor or actor's group.
    """
    if is_hostile(actor, target):
        return True
        
    # Group check
    target_group = getattr(target.db, "group", None)
    if not target_group:
        return False
        
    # If the target is in a group, are they attacking the actor?
    # This logic assumes group members share hostiles
    return getattr(target_group.db, "is_hostile", False)

