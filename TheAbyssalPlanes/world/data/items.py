"""
Item creation data: item types, allowed materials, and adjectives.
"""
from world.data import materials as materials_data

ITEM_TYPES = {
    "furniture": {
        "name": "Furniture",
        "materials": ["wood", "metal", "leather", "fabric", "stone", "glass"],
        "adjectives": ["sturdy", "luxurious", "simple", "ornate", "comfortable", "sleek", "weathered"],
    },
}


def get_item_type(key):
    """Return item type dict for a given key, or None."""
    if not key:
        return None
    return ITEM_TYPES.get(str(key).strip().lower())


def get_material(key):
    """Return material dict from materials.py."""
    return materials_data.get_material(key)
