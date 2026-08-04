"""
Appearance system for The Abyssal Planes.

Pure data module - no Evennia imports. Drives the three-word character
description shown in rooms ("A tall and lithe, translucent Visarii") plus
the skin-tone Truecolor highlight on the species name.

    height   - one of five height categories (relative to the species)
    build    - a single-word descriptor, valid only for certain heights
    adjective- a single-word descriptor chosen from the species' own list
    skin     - a named tone from the species' palette, mapped to a hex color
"""

# Ordered height categories; stored by key, displayed by label.
HEIGHTS = ("short", "below_average", "average", "above_average", "tall")

HEIGHT_LABELS = {
    "short": "Short",
    "below_average": "Below Average",
    "average": "Average",
    "above_average": "Above Average",
    "tall": "Tall",
}

# The word used inside the room description phrase, e.g.
# "A tall and lithe, translucent Visarii standing here."
HEIGHT_PHRASE = {
    "short": "short",
    "below_average": "below-average",
    "average": "average",
    "above_average": "above-average",
    "tall": "tall",
}

# Fallbacks used when a character's height/build is unset.
DEFAULT_HEIGHT = "average"
DEFAULT_BUILD = "average"


def height_phrase(height):
    """Return the phrase word for a height key."""
    return HEIGHT_PHRASE.get(height, HEIGHT_PHRASE["average"])

# Single-word builds and the heights each is valid for.
BUILDS = {
    "petite": ("short",),
    "compact": ("short", "below_average"),
    "squat": ("short", "below_average"),
    "delicate": ("short", "below_average"),
    "stocky": ("short", "below_average", "average"),
    "thick": ("short", "below_average", "average"),
    "wiry": ("short", "below_average", "average", "above_average"),
    "slender": ("below_average", "average", "above_average"),
    "svelte": ("below_average", "average", "above_average"),
    "lean": ("average", "above_average", "tall"),
    "lithe": ("average", "above_average", "tall"),
    "athletic": ("average", "above_average", "tall"),
    "muscular": ("average", "above_average", "tall"),
    "broad": ("average", "above_average", "tall"),
    "heavy": ("average", "above_average", "tall"),
    "rangy": ("above_average", "tall"),
    "lanky": ("above_average", "tall"),
    "willowy": ("above_average", "tall"),
    "brawny": ("above_average", "tall"),
    "burly": ("above_average", "tall"),
    "hulking": ("tall",),
    "statuesque": ("tall",),
}

# Appearance descriptors unique to each species.
SPECIES_ADJECTIVES = {
    "terran": [
        "weathered", "rugged", "plain", "comely", "freckled", "ruddy",
        "sallow", "sun-bronzed", "unremarkable", "striking", "scarred",
        "hardy", "coarse", "bland", "battered",
    ],
    "virentes": [
        "ethereal", "luminous", "ageless", "fair", "radiant", "serene",
        "unblemished", "graceful", "moonlit", "bright", "flawless",
        "gentle", "silken", "pristine", "willow-pale",
    ],
    "sideralis": [
        "still", "serene", "unblinking", "glabrous", "glossy", "cool",
        "far-eyed", "silent", "unruffled", "pale", "sleek", "alien",
        "composed", "vast", "quiet",
    ],
    "batrachi": [
        "warty", "mottled", "damp", "bulbous", "mud-dark", "dew-slick",
        "mossy", "thick-hided", "blotched", "heavy-lidded", "sloped",
        "wide-mawed", "flecked", "greasy", "muddy",
    ],
    "tritonii": [
        "striped", "glossy", "vivid", "slick", "bright-banded",
        "poison-bright", "dark", "wet-shining", "patterned", "iridescent",
        "sleek", "smooth", "gleaming", "flashy", "banded",
    ],
    "volucres": [
        "feathered", "fierce", "sharp-eyed", "beaked", "downy", "predatory",
        "keen", "winged", "wind-worn", "hooked", "regal", "darting",
        "taloned", "far-sighted", "proud",
    ],
    "pterati": [
        "leathery", "nocturnal", "dark", "fanged", "soft-furred", "silent",
        "pale-eyed", "winged", "shadowed", "sleek", "velvet", "hooked",
        "angular", "muted", "deep-eyed",
    ],
    "visarii": [
        "translucent", "crystalline", "faceted", "prismatic", "shimmering",
        "glassy", "luminous", "violet-tinged", "glittering", "hollow",
        "weightless", "sharp", "geometric", "refracting", "echoing",
    ],
    "silex": [
        "obsidian", "chiseled", "craggy", "sparking", "stone-skinned",
        "flinty", "dark", "honed", "jagged", "unyielding", "rock-rough",
        "hard", "edged", "black", "forged",
    ],
}

# Named skin tones mapped to Truecolor hex values (24-bit).
SKIN_TONES = {
    "alabaster": "#f5e6d3",
    "porcelain": "#f8d5b8",
    "ivory": "#f0d5b0",
    "fair": "#ecc9a8",
    "peach": "#f3c3a0",
    "tan": "#c98d5f",
    "bronze": "#a06a3f",
    "olive": "#b09a6b",
    "copper": "#b87333",
    "caramel": "#c68b59",
    "brown": "#7a4a2b",
    "sienna": "#9a5b2f",
    "umber": "#5d3a1e",
    "mocha": "#6f4e37",
    "ebony": "#3b2a20",
    "midnight": "#241c16",
    "moonlit": "#e8f0ec",
    "lily-white": "#fdfcfa",
    "mint": "#cfe3d8",
    "sage": "#b7c9a8",
    "cerulean": "#1f8ec7",
    "azure": "#3a7bbf",
    "sapphire": "#2b4f9e",
    "indigo": "#2a2a72",
    "void-blue": "#141b3d",
    "marsh-green": "#5f7a3a",
    "moss-green": "#6b8e4e",
    "swamp-dark": "#3d5230",
    "mud-brown": "#6b4f2e",
    "olive-drab": "#6f7a3a",
    "brackish": "#4d5d3a",
    "jet-black": "#11141a",
    "abyss": "#0a0c10",
    "ink": "#151820",
    "charcoal": "#26282c",
    "pale-grey": "#d8d4cc",
    "ash": "#b9b4ac",
    "slate": "#7b7b87",
    "violet": "#8a7fd8",
    "amethyst": "#9b6fc0",
    "orchid": "#b78ac9",
    "lilac": "#c4b0e0",
    "purple-haze": "#6a5acd",
    "ghost-violet": "#a99ad4",
    "obsidian": "#41414a",
    "flint": "#54545f",
    "basalt": "#676772",
    "granite": "#9696a1",
    "stone-grey": "#8a8d93",
}

# The skin tones each species may choose from.
SPECIES_SKIN_TONES = {
    "terran": [
        "alabaster", "porcelain", "ivory", "fair", "peach", "tan", "bronze",
        "olive", "copper", "caramel", "brown", "sienna", "umber", "mocha",
        "ebony", "midnight",
    ],
    "virentes": ["alabaster", "ivory", "moonlit", "lily-white", "mint", "sage"],
    "sideralis": ["cerulean", "azure", "sapphire", "indigo", "void-blue", "midnight"],
    "batrachi": [
        "marsh-green", "moss-green", "swamp-dark", "mud-brown", "olive-drab",
        "brackish",
    ],
    "tritonii": ["jet-black", "abyss", "ink", "charcoal", "midnight"],
    "volucres": ["alabaster", "porcelain", "ivory", "fair", "pale-grey", "ash"],
    "pterati": ["alabaster", "ash", "pale-grey", "charcoal", "slate"],
    "visarii": ["violet", "amethyst", "orchid", "lilac", "purple-haze", "ghost-violet"],
    "silex": ["obsidian", "flint", "basalt", "slate", "granite", "ash"],
}


def builds_for_height(height):
    """Return the builds valid for a given height key."""
    return tuple(build for build, heights in BUILDS.items() if height in heights)


def valid_build(height, build):
    """Return True if a build is valid for a given height key."""
    return height in BUILDS.get(build, ())


def adjectives_for_species(species_key):
    """Return the adjective list for a species key."""
    return tuple(SPECIES_ADJECTIVES.get(species_key, ()))


def valid_adjective(species_key, word):
    """Return True if a word is a valid adjective for the species."""
    return word in adjectives_for_species(species_key)


def skins_for_species(species_key):
    """Return the skin-tone list for a species key."""
    return tuple(SPECIES_SKIN_TONES.get(species_key, ()))


def valid_skin(species_key, tone):
    """Return True if a tone is valid for the species."""
    return tone in skins_for_species(species_key)


def hex_for_skin(species_key, tone):
    """Return the Truecolor hex for a tone, if valid for the species."""
    if not valid_skin(species_key, tone):
        return None
    return SKIN_TONES[tone]


def height_label(height):
    """Return the display label for a height key."""
    return HEIGHT_LABELS.get(height, str(height).title())


def article(word):
    """Return 'An' or 'A' based on the first letter of a word."""
    if word and word[0].lower() in "aeiou":
        return "An"
    return "A"

# Whitelisted position words a character may adopt. The pose closes the
# appearance phrase ("... Visarii standing here.") and groups room
# occupants by position. Set via the builder 'setpose' command today; combat
# and other systems will drive it later through Character.set_pose().
POSES = (
    "standing", "sitting", "resting", "laying", "sleeping",
    "kneeling", "crouching", "leaning", "lounging", "reclining",
    "squatting", "hiding", "meditating", "pacing", "observing",
    "guarding", "praying", "dreaming",
)


def valid_pose(pose):
    """Return True if the pose is a whitelisted position word."""
    return pose in POSES
