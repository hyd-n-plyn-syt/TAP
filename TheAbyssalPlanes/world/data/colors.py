"""
Master color definitions with Truecolor hex codes and display helpers.
"""

COLORS = {
    # Woods
    "oak": {"name": "oak", "hex": "#c8955c"},
    "mahogany": {"name": "mahogany", "hex": "#4a2511"},
    "pine": {"name": "pine", "hex": "#d4b886"},
    "walnut": {"name": "walnut", "hex": "#5c4033"},
    "ebony": {"name": "ebony", "hex": "#272522"},
    "cherry": {"name": "cherry", "hex": "#6b2d2f"},
    "maple": {"name": "maple", "hex": "#e0b084"},
    "ash": {"name": "ash", "hex": "#b2b2b2"},

    # Metals
    "steel": {"name": "steel", "hex": "#b0c4de"},
    "iron": {"name": "iron", "hex": "#434b4d"},
    "bronze": {"name": "bronze", "hex": "#cd7f32"},
    "brass": {"name": "brass", "hex": "#b5a642"},
    "gold": {"name": "gold", "hex": "#ffd700"},
    "silver": {"name": "silver", "hex": "#c0c0c0"},
    "copper": {"name": "copper", "hex": "#b87333"},
    "dark iron": {"name": "dark iron", "hex": "#2f3538"},

    # Leathers
    "brown": {"name": "brown", "hex": "#8b4513"},
    "black": {"name": "black", "hex": "#1a1a1a"},
    "tan": {"name": "tan", "hex": "#d2b48c"},
    "reddish-brown": {"name": "reddish-brown", "hex": "#a52a2a"},
    "dark": {"name": "dark", "hex": "#2d2d2d"},
    "chestnut": {"name": "chestnut", "hex": "#954535"},
    "cordovan": {"name": "cordovan", "hex": "#893f45"},

    # Fabrics
    "crimson": {"name": "crimson", "hex": "#dc143c"},
    "blue": {"name": "blue", "hex": "#1e90ff"},
    "green": {"name": "green", "hex": "#2e8b57"},
    "white": {"name": "white", "hex": "#f8f8ff"},
    "purple": {"name": "purple", "hex": "#800080"},
    "navy": {"name": "navy", "hex": "#000080"},
    "teal": {"name": "teal", "hex": "#008080"},
    "gold-thread": {"name": "gold-thread", "hex": "#daa520"},

    # Stones
    "grey": {"name": "grey", "hex": "#808080"},
    "granite": {"name": "granite", "hex": "#676767"},
    "marble": {"name": "marble", "hex": "#f0f0f5"},
    "slate": {"name": "slate", "hex": "#708090"},
    "sandstone": {"name": "sandstone", "hex": "#deb887"},
    "obsidian-stone": {"name": "obsidian-stone", "hex": "#1c1c24"},
    "limestone": {"name": "limestone", "hex": "#e3dac9"},

    # Glass
    "clear": {"name": "clear", "hex": "#e0f7fa"},
    "smoked": {"name": "smoked", "hex": "#4a4a4a"},
    "amber": {"name": "amber", "hex": "#ffbf00"},
    "emerald": {"name": "emerald", "hex": "#50c878"},
    "cobalt": {"name": "cobalt", "hex": "#0047ab"},
    "ruby": {"name": "ruby", "hex": "#e0115f"},
    "amethyst": {"name": "amethyst", "hex": "#9966cc"},

    # Light (wisp palette)
    "white-light": {"name": "white-light", "hex": "#f8f8ff"},
    "gold-light": {"name": "gold-light", "hex": "#ffd700"},
    "azure-light": {"name": "azure-light", "hex": "#87ceeb"},
    "violet-light": {"name": "violet-light", "hex": "#b19cd9"},
    "ember-light": {"name": "ember-light", "hex": "#ff6a33"},
    "cyan-light": {"name": "cyan-light", "hex": "#7ff0da"},
    "rose-light": {"name": "rose-light", "hex": "#ffb6d9"},
    "silver-light": {"name": "silver-light", "hex": "#d8dde6"},
    "ice-light": {"name": "ice-light", "hex": "#c9f0ff"},
    "clear-light": {"name": "clear-light", "hex": "#eaffff"},
    "amber-light": {"name": "amber-light", "hex": "#ffbf6b"},
    "crimson-light": {"name": "crimson-light", "hex": "#ff6b6b"},
}

WISP_LIGHTS = tuple(k for k in COLORS if k.endswith("-light"))


def get_color(key):
    """Return color info dict for a given key, or None."""
    if not key:
        return None
    return COLORS.get(str(key).strip().lower())


def hex_for_color(key):
    """Return Truecolor hex string for a color key, or None."""
    c = get_color(key)
    return c["hex"] if c else None


def colored_name(key):
    """Return color name wrapped in its Truecolor display tag."""
    c = get_color(key)
    if not c:
        return str(key)
    return f"|{c['hex']}{c['name']}|n"
