"""
Master material definitions linking materials to their possible colors from colors.py.
"""

MATERIALS = {
    "wood": {
        "name": "Wood",
        "colors": ["oak", "mahogany", "pine", "walnut", "ebony", "cherry", "maple", "ash"],
    },
    "metal": {
        "name": "Metal",
        "colors": ["steel", "iron", "bronze", "brass", "gold", "silver", "copper", "dark iron"],
    },
    "leather": {
        "name": "Leather",
        "colors": ["brown", "black", "tan", "reddish-brown", "dark", "chestnut", "cordovan"],
    },
    "fabric": {
        "name": "Fabric",
        "colors": ["crimson", "blue", "green", "white", "purple", "navy", "teal", "gold-thread"],
    },
    "stone": {
        "name": "Stone",
        "colors": ["grey", "granite", "marble", "slate", "sandstone", "obsidian-stone", "limestone"],
    },
    "glass": {
        "name": "Glass",
        "colors": ["clear", "smoked", "amber", "emerald", "cobalt", "ruby", "amethyst"],
    },
}


def get_material(key):
    """Return material info dict for a given key, or None."""
    if not key:
        return None
    return MATERIALS.get(str(key).strip().lower())
