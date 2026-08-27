"""
Appearance system for The Abyssal Planes.

Pure data module - no Evennia imports. Drives the character description
shown in rooms ("A tall and lithe, translucent Visarii") plus the
expanded paragraph shown when a player looks at a character.

    height    - one of five height categories (relative to the species)
    build     - a single-word descriptor, valid only for certain heights
    adjective - a single-word descriptor chosen from the species' own list
    skin      - a named tone from the species' palette, mapped to a hex color
    eyes      - eye shape descriptor, per-species valid list
    eye_color - eye color descriptor, per-species valid list
    hair      - hair style descriptor, per-species valid list
    hair_color- hair color descriptor, per-species valid list
"""

# ── Height ────────────────────────────────────────────────────────────

HEIGHTS = ("diminutive", "short", "middling", "tall", "towering")

HEIGHT_LABELS = {
    "diminutive": "Diminutive",
    "short": "Short",
    "middling": "Middling",
    "tall": "Tall",
    "towering": "Towering",
}

HEIGHT_PHRASE = {
    "diminutive": "diminutive",
    "short": "short",
    "middling": "middling",
    "tall": "tall",
    "towering": "towering",
}

DEFAULT_HEIGHT = "middling"
DEFAULT_BUILD = "average"

# ── Wisp size (single combined height/build for ball-of-light) ──────
# Same relative scale as a person — not tiny. 5 options, matching HEIGHTS count.
WISP_SIZES = ("small", "modest", "middling", "large", "immense")
WISP_SIZE_LABELS = {
    "small": "Small",
    "modest": "Modest",
    "middling": "Middling",
    "large": "Large",
    "immense": "Immense",
}
WISP_SIZE_DESCRIPTIONS = {
    "small": "Compact and close, a tight mote of light.",
    "modest": "Modest in breadth, steady and contained.",
    "middling": "Balanced and even, neither faint nor overwhelming.",
    "large": "Broad and generous, filling the space around it.",
    "immense": "Immense and encompassing, a vast bloom of light.",
}
DEFAULT_WISP_SIZE = "middling"


def wisp_size_label(size):
    return WISP_SIZE_LABELS.get(size, str(size).title())


def valid_wisp_size(size):
    return size in WISP_SIZES


def height_phrase(height=""):
    """Return the phrase word for a height key, defaulting to the
    DEFAULT_HEIGHT phrase for unknown or unset heights."""
    return HEIGHT_PHRASE.get(height, HEIGHT_PHRASE[DEFAULT_HEIGHT])


def height_label(height):
    """Return the display label for a height key."""
    return HEIGHT_LABELS.get(height, str(height).title())


HEIGHT_DESCRIPTIONS = {
    "diminutive": "Barely reaching the knee of an average humanoid.",
    "short": "Noticeably shorter than most, with a compact presence.",
    "middling": "Of average height, neither towering nor slight.",
    "tall": "Taller than average, with a commanding presence.",
    "towering": "Enormous, towering over most who stand nearby.",
}

# ── Build ─────────────────────────────────────────────────────────────

BUILDS = {
    "petite": ("diminutive",),
    "compact": ("diminutive", "short"),
    "squat": ("diminutive", "short"),
    "delicate": ("diminutive", "short"),
    "stocky": ("diminutive", "short", "middling"),
    "thick": ("diminutive", "short", "middling"),
    "wiry": ("diminutive", "short", "middling", "tall"),
    "slender": ("short", "middling", "tall"),
    "svelte": ("short", "middling", "tall"),
    "lean": ("middling", "tall", "towering"),
    "lithe": ("middling", "tall", "towering"),
    "athletic": ("middling", "tall", "towering"),
    "muscular": ("middling", "tall", "towering"),
    "broad": ("middling", "tall", "towering"),
    "heavy": ("middling", "tall", "towering"),
    "rangy": ("tall", "towering"),
    "lanky": ("tall", "towering"),
    "willowy": ("tall", "towering"),
    "brawny": ("tall", "towering"),
    "burly": ("tall", "towering"),
    "hulking": ("towering",),
    "statuesque": ("towering",),
}

BUILD_DESCRIPTIONS = {
    "petite": "Small-framed and delicately proportioned.",
    "compact": "Tightly built, every inch purposeful.",
    "squat": "Low and broad, rooted to the ground.",
    "delicate": "Fine-boned and fragile in appearance.",
    "stocky": "Thick-set and sturdy, built to endure.",
    "thick": "Heavy of frame, with a solid, dense build.",
    "wiry": "Lean and sinewy, all tendon and tension.",
    "slender": "Gracefully narrow, with a refined silhouette.",
    "svelte": "Sleek and elegant, with a fluid grace.",
    "lean": "Lean of frame, with little waste upon their form.",
    "lithe": "Lithe and fluid, moving with easy grace.",
    "athletic": "Athletic and well-proportioned, honed by activity.",
    "muscular": "Powerfully built, with thick cords of muscle.",
    "broad": "Broad of shoulder and wide of stance.",
    "heavy": "Heavy and substantial, with a weighty presence.",
    "rangy": "Long-limbed and loose-jointed, covering ground easily.",
    "lanky": "Awkwardly tall and thin, all limbs and angles.",
    "willowy": "Tall and slender, swaying like a reed in wind.",
    "brawny": "Thick with muscle, a brute strength apparent.",
    "burly": "Massive and solid, built for heavy labor.",
    "hulking": "Immensely large, casting a shadow over all around.",
    "statuesque": "Tall and stately, carved as if from living stone.",
}

# ── Combined height + build descriptions ──────────────────────────────

_HEIGHT_BUILD = {
    ("diminutive", "petite"):
        "{subj} {be} barely knee-high, small-framed and delicately proportioned.",
    ("diminutive", "compact"):
        "{subj} {be} barely knee-high, tightly built and every inch purposeful.",
    ("diminutive", "squat"):
        "{subj} {be} barely knee-high, low and broad, rooted to the ground.",
    ("diminutive", "delicate"):
        "{subj} {be} barely knee-high, fine-boned and fragile in appearance.",
    ("diminutive", "stocky"):
        "{subj} {be} barely knee-high, thick-set and sturdy, built to endure.",
    ("diminutive", "thick"):
        "{subj} {be} barely knee-high, heavy of frame with a solid, dense build.",

    ("short", "compact"):
        "{subj} {be} noticeably shorter than most, tightly built and every inch purposeful.",
    ("short", "squat"):
        "{subj} {be} noticeably shorter than most, low and broad, rooted to the ground.",
    ("short", "delicate"):
        "{subj} {be} noticeably shorter than most, fine-boned and fragile in appearance.",
    ("short", "stocky"):
        "{subj} {be} noticeably shorter than most, thick-set and sturdy, built to endure.",
    ("short", "thick"):
        "{subj} {be} noticeably shorter than most, heavy of frame with a solid, dense build.",
    ("short", "wiry"):
        "{subj} {be} noticeably shorter than most, lean and sinewy, all tendon and tension.",
    ("short", "slender"):
        "{subj} {be} noticeably shorter than most, gracefully narrow with a refined silhouette.",
    ("short", "svelte"):
        "{subj} {be} noticeably shorter than most, sleek and elegant with a fluid grace.",

    ("middling", "stocky"):
        "{subj} {be} of average height, thick-set and sturdy, built to endure.",
    ("middling", "thick"):
        "{subj} {be} of average height, heavy of frame with a solid, dense build.",
    ("middling", "wiry"):
        "{subj} {be} of average height, lean and sinewy, all tendon and tension.",
    ("middling", "slender"):
        "{subj} {be} of average height, gracefully narrow with a refined silhouette.",
    ("middling", "svelte"):
        "{subj} {be} of average height, sleek and elegant with a fluid grace.",
    ("middling", "lean"):
        "{subj} {be} of average height, lean of frame with little waste upon {poss} form.",
    ("middling", "lithe"):
        "{subj} {be} of average height, lithe and fluid, moving with easy grace.",
    ("middling", "athletic"):
        "{subj} {be} of average height, athletic and well-proportioned, honed by activity.",
    ("middling", "muscular"):
        "{subj} {be} of average height, powerfully built with thick cords of muscle.",
    ("middling", "broad"):
        "{subj} {be} of average height, broad of shoulder and wide of stance.",
    ("middling", "heavy"):
        "{subj} {be} of average height, heavy and substantial with a weighty presence.",

    ("tall", "wiry"):
        "{subj} {be} taller than average with a commanding presence, lean and sinewy, all tendon and tension.",
    ("tall", "slender"):
        "{subj} {be} taller than average with a commanding presence, gracefully narrow with a refined silhouette.",
    ("tall", "svelte"):
        "{subj} {be} taller than average with a commanding presence, sleek and elegant with a fluid grace.",
    ("tall", "lean"):
        "{subj} {be} taller than average with a commanding presence, lean of frame with little waste upon {poss} form.",
    ("tall", "lithe"):
        "{subj} {be} taller than average with a commanding presence, lithe and fluid, moving with easy grace.",
    ("tall", "athletic"):
        "{subj} {be} taller than average with a commanding presence, athletic and well-proportioned, honed by activity.",
    ("tall", "muscular"):
        "{subj} {be} taller than average with a commanding presence, powerfully built with thick cords of muscle.",
    ("tall", "broad"):
        "{subj} {be} taller than average with a commanding presence, broad of shoulder and wide of stance.",
    ("tall", "heavy"):
        "{subj} {be} taller than average with a commanding presence, heavy and substantial with a weighty presence.",
    ("tall", "rangy"):
        "{subj} {be} taller than average with a commanding presence, long-limbed and loose-jointed, covering ground easily.",
    ("tall", "lanky"):
        "{subj} {be} taller than average with a commanding presence, awkwardly tall and thin, all limbs and angles.",
    ("tall", "willowy"):
        "{subj} {be} taller than average with a commanding presence, tall and slender, swaying like a reed in wind.",
    ("tall", "brawny"):
        "{subj} {be} taller than average with a commanding presence, thick with muscle, a brute strength apparent.",
    ("tall", "burly"):
        "{subj} {be} taller than average with a commanding presence, massive and solid, built for heavy labor.",
    ("tall", "hulking"):
        "{subj} {be} taller than average with a commanding presence, immensely large and casting a shadow over all around.",
    ("tall", "statuesque"):
        "{subj} {be} taller than average with a commanding presence, tall and stately, carved as if from living stone.",

    ("towering", "lean"):
        "{subj} {be} enormous, towering over most, lean of frame with little waste upon {poss} form.",
    ("towering", "lithe"):
        "{subj} {be} enormous, towering over most, lithe and fluid, moving with easy grace.",
    ("towering", "athletic"):
        "{subj} {be} enormous, towering over most, athletic and well-proportioned, honed by activity.",
    ("towering", "muscular"):
        "{subj} {be} enormous, towering over most, powerfully built with thick cords of muscle.",
    ("towering", "broad"):
        "{subj} {be} enormous, towering over most, broad of shoulder and wide of stance.",
    ("towering", "heavy"):
        "{subj} {be} enormous, towering over most, heavy and substantial with a weighty presence.",
    ("towering", "rangy"):
        "{subj} {be} enormous, towering over most, long-limbed and loose-jointed, covering ground easily.",
    ("towering", "lanky"):
        "{subj} {be} enormous, towering over most, awkwardly tall and thin, all limbs and angles.",
    ("towering", "willowy"):
        "{subj} {be} enormous, towering over most, tall and slender, swaying like a reed in wind.",
    ("towering", "brawny"):
        "{subj} {be} enormous, towering over most, thick with muscle, a brute strength apparent.",
    ("towering", "burly"):
        "{subj} {be} enormous, towering over most, massive and solid, built for heavy labor.",
    ("towering", "hulking"):
        "{subj} {be} enormous, towering over most, immensely large and casting a shadow over all around.",
    ("towering", "statuesque"):
        "{subj} {be} enormous, towering over most, tall and stately, carved as if from living stone.",
}

# Fallback for unmapped combos: separate height + build.
_HEIGHT_BUILD_DEFAULT = (
    "{height_desc} {build_frag}"
)

_BUILD_FRAGMENTS = {
    "petite": "Small-framed and delicately proportioned.",
    "compact": "Tightly built, every inch purposeful.",
    "squat": "Low and broad, rooted to the ground.",
    "delicate": "Fine-boned and fragile in appearance.",
    "stocky": "Thick-set and sturdy, built to endure.",
    "thick": "Heavy of frame, with a solid, dense build.",
    "wiry": "Lean and sinewy, all tendon and tension.",
    "slender": "Gracefully narrow, with a refined silhouette.",
    "svelte": "Sleek and elegant, with a fluid grace.",
    "lean": "lean of frame, with little waste upon {poss} form.",
    "lithe": "Lithe and fluid, moving with easy grace.",
    "athletic": "Athletic and well-proportioned, honed by activity.",
    "muscular": "Powerfully built, with thick cords of muscle.",
    "broad": "Broad of shoulder and wide of stance.",
    "heavy": "Heavy and substantial, with a weighty presence.",
    "rangy": "Long-limbed and loose-jointed, covering ground easily.",
    "lanky": "Awkwardly tall and thin, all limbs and angles.",
    "willowy": "Tall and slender, swaying like a reed in wind.",
    "brawny": "Thick with muscle, a brute strength apparent.",
    "burly": "Massive and solid, built for heavy labor.",
    "hulking": "Immensely large, casting a shadow over all around.",
    "statuesque": "Tall and stately, carved as if from living stone.",
}


def builds_for_height(height):
    """Return the builds valid for a given height key."""
    return tuple(build for build, heights in BUILDS.items() if height in heights)


def valid_build(height, build):
    """Return True if a build is valid for a given height key."""
    return height in BUILDS.get(build, ())


def height_build_phrase(height, build, subj="It", be="is", poss="its"):
    """Return a combined height + build description using the given pronouns.

    *subj* and *be* should match the viewer context (e.g. ``"You"``,
    ``"are"`` for self-view, or ``"He"``, ``"is"`` for third-person).
    *poss* is the possessive determiner (``"his"``, ``"her"``, ``"your"``,
    ``"its"``).
    """
    height = height or DEFAULT_HEIGHT
    build = build or DEFAULT_BUILD

    # If no build is set, use just the height description.
    if build == DEFAULT_BUILD:
        h_desc = HEIGHT_DESCRIPTIONS.get(height, "")
        if h_desc:
            # Strip trailing period; lowercase first word (it's mid-sentence).
            h_desc = h_desc.rstrip(".")
            return f"{subj} {be} {h_desc[0].lower() + h_desc[1:]}"
        return ""

    key = (height, build)
    template = _HEIGHT_BUILD.get(key)
    if template:
        return template.format(subj=subj, be=be, poss=poss)

    # Fallback: compose from separate height and build pieces.
    h_desc = HEIGHT_DESCRIPTIONS.get(height, "")
    frag = _BUILD_FRAGMENTS.get(build, "")
    if "{poss}" in frag:
        frag = frag.format(poss=poss)
    # Strip trailing period from height desc so the combined sentence flows.
    if h_desc and frag:
        h_desc = h_desc.rstrip(".")
        # Lowercase first word since this is mid-sentence.
        h_desc = h_desc[0].lower() + h_desc[1:]
        return f"{h_desc}, {frag[0].lower() + frag[1:]}"
    if h_desc:
        h_desc = h_desc.rstrip(".")
        return f"{subj} {be} {h_desc[0].lower() + h_desc[1:]}"
    return frag

# ── Adjective ─────────────────────────────────────────────────────────

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
    "wisp": [
        "flickering", "pulsing", "steady", "wavering", "brilliant",
        "dim", "humming", "cold", "warm", "prismatic",
        "soft", "sharp", "echoing", "hazy", "lambent",
    ],
}

SPECIES_ADJECTIVE_DESCRIPTIONS = {
    "terran": {
        "weathered": "Their face carries the quiet weight of years spent outdoors.",
        "rugged": "Hard lines and sun-darkened skin speak of a life lived rough.",
        "plain": "An unremarkable face, easily lost in a crowd.",
        "comely": "Pleasant of feature, with an easy, approachable charm.",
        "freckled": "A scatter of freckles dusts their cheeks and brow.",
        "ruddy": "A healthy flush warms their cheeks.",
        "sallow": "Sickly pale, with a yellowish tint to their skin.",
        "sun-bronzed": "Deep golden-brown skin speaks of long days under open sky.",
        "unremarkable": "Nothing about their features particularly stands out.",
        "striking": "Sharp, memorable features that draw the eye.",
        "scarred": "Old scars mark their skin, each one a story.",
        "hardy": "A tough, resilient look — built to weather any storm.",
        "coarse": "Rough skin and blunt features give a hard impression.",
        "bland": "A flat, expressionless face, revealing little.",
        "battered": "Bruises and cuts suggest recent unpleasantness.",
    },
    "virentes": {
        "ethereal": "They seem almost too perfect to be real, like a waking dream.",
        "luminous": "A soft, inner light plays just beneath their skin.",
        "ageless": "No mark of time touches their flawless features.",
        "fair": "Pale and fine-featured, with an almost porcelain quality.",
        "radiant": "They seem to glow with a quiet, inner beauty.",
        "serene": "A deep calm rests in their expression, undisturbed by worry.",
        "unblemished": "Not a single mark mars their immaculate skin.",
        "graceful": "Every line of their form speaks of effortless elegance.",
        "moonlit": "Their skin carries a pale, silvery sheen, as if lit from without.",
        "bright": "Vivid and alive, they seem brighter than the room around them.",
        "flawless": "Impossibly perfect, as if sculpted by a master artisan.",
        "gentle": "Soft features and a warm expression put others at ease.",
        "silken": "Their skin has the smooth, lustrous quality of fine silk.",
        "pristine": "Untouched and immaculate, as if freshly made.",
        "willow-pale": "Pale and slender, swaying gently even when still.",
    },
    "sideralis": {
        "still": "Perfectly, unnervingly still, as if carved from living space.",
        "serene": "A vast, ancient calm fills their expression.",
        "unblinking": "Their eyes remain open, unblinking, fixed on something distant.",
        "glabrous": "Smooth and hairless, their skin has a polished, alien sheen.",
        "glossy": "A dark, reflective gloss covers their skin like lacquer.",
        "cool": "Their skin carries a faint, perpetual coolness.",
        "far-eyed": "Their gaze seems focused on something far beyond the here and now.",
        "silent": "They move and exist with an absolute, profound silence.",
        "unruffled": "Nothing seems to disturb their deep, ancient composure.",
        "pale": "Washed-out and faint, as if not entirely present in this world.",
        "sleek": "Streamlined and smooth, built for the void between stars.",
        "alien": "Fundamentally other — their proportions and movements feel wrong.",
        "composed": "Utterly self-possessed, beyond the reach of mortal anxiety.",
        "vast": "Something vast and old looks out through their eyes.",
        "quiet": "A deep, resonant quiet surrounds them, muffling the world.",
    },
    "batrachi": {
        "warty": "Rough, bumpy skin covers their broad frame.",
        "mottled": "Patches of dark and light mottle their hide.",
        "damp": "A perpetual sheen of moisture glistens on their skin.",
        "bulbous": "Rounded, bulging features dominate their wide face.",
        "mud-dark": "Dark as river mud, blending into the mire.",
        "dew-slick": "A glistening film of moisture coats their skin.",
        "mossy": "Patches of moss cling to their damp, rough hide.",
        "thick-hided": "Hide so thick it seems almost armored.",
        "blotched": "Irregular blotches of color pattern their skin.",
        "heavy-lidded": "Thick, heavy lids droop over their large eyes.",
        "sloped": "A broad, sloping forehead leads to a wide, flat nose.",
        "wide-mawed": "An enormous mouth stretches nearly ear to ear.",
        "flecked": "Tiny flecks of brighter color dot their dark skin.",
        "greasy": "An oily sheen coats their slick, damp skin.",
        "muddy": "Caked with dried mud, they look freshly risen from the bog.",
    },
    "tritonii": {
        "striped": "Vivid stripes of color band their sleek skin.",
        "glossy": "A wet, glossy sheen covers their streamlined form.",
        "vivid": "Bright, almost garish colors paint their skin.",
        "slick": "Impossibly smooth and slick, as if coated in oil.",
        "bright-banded": "Broad bands of bright color ring their limbs and torso.",
        "poison-bright": "Colors so bright they seem to warn of danger.",
        "dark": "Deep, muted tones cloak their form in shadow.",
        "wet-shining": "Their skin gleams as if perpetually wet.",
        "patterned": "Intricate patterns etch across their skin like living tattoos.",
        "iridescent": "Colors shift and ripple across their skin with every movement.",
        "sleek": "Streamlined and hydrodynamic, built for swift movement through water.",
        "smooth": "Impossibly smooth, with no scales or roughness.",
        "gleaming": "Their skin gleams with an inner, opalescent light.",
        "flashy": "Dazzling colors flash across their skin with each gesture.",
        "banded": "Bold, contrasting bands of color encircle their body.",
    },
    "volucres": {
        "feathered": "Soft feathers cloak their form in layers of down and quill.",
        "fierce": "A sharp, predatory intensity burns in their gaze.",
        "sharp-eyed": "Bright, piercing eyes miss nothing.",
        "beaked": "A sharp, curved beak replaces a conventional mouth.",
        "downy": "Soft, fluffy down covers their skin like warm plumage.",
        "predatory": "Every line of their body speaks of the hunt.",
        "keen": "Alert and watchful, their senses are razor-sharp.",
        "winged": "Broad wings fold against their back, ready for flight.",
        "wind-worn": "Weathered by high-altitude winds, their feathers are frayed.",
        "hooked": "A sharp, hooked beak and talons mark them as a predator.",
        "regal": "Tall and proud, with the bearing of natural authority.",
        "darting": "Quick, restless movements betray a restless energy.",
        "taloned": "Sharp, curved talons serve as both hands and weapons.",
        "far-sighted": "Their keen eyes can spot movement from great distances.",
        "proud": "Head held high, they carry themselves with unmistakable pride.",
    },
    "pterati": {
        "leathery": "Tough, leathery skin stretches over their lean frame.",
        "nocturnal": "Dark-adapted eyes and pale skin mark them as creatures of the night.",
        "dark": "Darkness clings to them — dark skin, dark eyes, dark intent.",
        "fanged": "Prominent fangs protrude from their narrow jaw.",
        "soft-furred": "A coat of fine, soft fur covers their body.",
        "silent": "They move without a sound, ghosts in the dark.",
        "pale-eyed": "Unusually pale eyes stand out against their dark features.",
        "winged": "Bat-like wings fold against their back when not in use.",
        "shadowed": "Shadows seem to gather about them, even in bright light.",
        "sleek": "Sleek and streamlined, built for swift, silent movement.",
        "velvet": "Their skin or fur has the soft, dark sheen of velvet.",
        "hooked": "A sharp, hooked nose and claws mark their predatory nature.",
        "angular": "Sharp angles and hard edges define their gaunt features.",
        "muted": "Dull, muted tones cloak them in near-invisibility.",
        "deep-eyed": "Large, deep-set eyes hold a unsettling depth.",
    },
    "visarii": {
        "translucent": "Their translucent body reveals faint inner luminescence.",
        "crystalline": "Crystalline facets catch and scatter the light.",
        "faceted": "Sharp facets rim their form like cut glass.",
        "prismatic": "Prismatic flashes dance across their surface.",
        "shimmering": "A constant shimmer ripples across their skin.",
        "glassy": "Their surface has the smooth sheen of polished glass.",
        "luminous": "A soft glow emanates from within their form.",
        "violet-tinged": "A violet tint suffuses their translucent frame.",
        "glittering": "Glittering points of light dot their crystalline flesh.",
        "hollow": "Hollow spaces within their form echo faintly.",
        "weightless": "They seem to defy gravity, barely touching the ground.",
        "sharp": "Every edge of their form is precise and angular.",
        "geometric": "Geometric patterns etch across their surface.",
        "refracting": "Their crystalline form refracts light in shifting patterns.",
        "echoing": "A faint resonance hums from within their hollow frame.",
    },
    "silex": {
        "obsidian": "Dark as volcanic glass, their skin drinks the light.",
        "chiseled": "Sharp, chiseled lines define their stony features.",
        "craggy": "Rough, craggy textures cover their stone flesh.",
        "sparking": "Tiny sparks flicker across their rough surface.",
        "stone-skinned": "Thick stone plates form a natural armor.",
        "flinty": "Hard and sharp-edged, like freshly struck flint.",
        "dark": "Deep, matte black — a void in the light.",
        "honed": "Every edge is worn smooth and sharp, like a well-used blade.",
        "jagged": "Jagged, uneven planes break across their form.",
        "unyielding": "Hard as the mountain itself, they bend for nothing.",
        "rock-rough": "Rough as raw granite, abrasive to the touch.",
        "hard": "Solid and unyielding, a wall of living stone.",
        "edged": "Sharp edges line their form like the facets of a blade.",
        "black": "Deep, absolute black — the color of the deepest stone.",
        "forged": "They look as if forged in fire, not born.",
    },
    "wisp": {
        "flickering": "Their light flickers gently, waxing and waning like a candle in wind.",
        "pulsing": "A slow pulse travels through their glow, brightening and dimming in rhythm.",
        "steady": "Their light holds steady and even, unwavering and calm.",
        "wavering": "Their glow wavers softly at the edges, never quite still.",
        "brilliant": "They blaze with a brilliant, almost piercing intensity.",
        "dim": "A dim, muted glow clings to their form, subdued and gentle.",
        "humming": "A faint hum seems to resonate from within their light.",
        "cold": "Their light carries a crisp, cool cast, like moon on snow.",
        "warm": "A warm, amber-tinged glow radiates from their center.",
        "prismatic": "Prismatic flecks dance through their light, scattering color.",
        "soft": "Their glow is soft and diffused, gentle on the eyes.",
        "sharp": "A sharp, focused brilliance cuts clearly through the air.",
        "echoing": "Their light seems to echo faintly, as if reflecting off unseen surfaces.",
        "hazy": "A hazy nimbus softens their edges, blurring into the air.",
        "lambent": "A lambent sheen plays across their surface, smooth and quiet.",
    },
}

# ── Skin ──────────────────────────────────────────────────────────────

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
    # Wisp light palette (also in world/data/colors.py)
    "white-light": "#f8f8ff",
    "gold-light": "#ffd700",
    "azure-light": "#87ceeb",
    "violet-light": "#b19cd9",
    "ember-light": "#ff6a33",
    "cyan-light": "#7ff0da",
    "rose-light": "#ffb6d9",
    "silver-light": "#d8dde6",
    "ice-light": "#c9f0ff",
    "clear-light": "#eaffff",
    "amber-light": "#ffbf6b",
    "crimson-light": "#ff6b6b",
}

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
    "wisp": [
        "white-light", "gold-light", "azure-light", "violet-light",
        "ember-light", "cyan-light", "rose-light", "silver-light",
        "ice-light", "clear-light", "amber-light", "crimson-light",
    ],
}


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


# Extended colour palette for eyes, hair, and other features.  Maps
# lower-case colour names to Truecolor hex strings.
COLOR_HEXES = {
    "black": "#1a1a1a",
    "white": "#ffffff",
    "gray": "#9a9a9a",
    "grey": "#9a9a9a",
    "silver": "#dcdcdc",
    "gold": "#eab020",
    "amber": "#e0a030",
    "brown": "#9a6a3a",
    "dark brown": "#6a4020",
    "red": "#d04040",
    "deep red": "#a02020",
    "orange": "#e89030",
    "dull orange": "#c08040",
    "yellow": "#f0e060",
    "green": "#50b050",
    "dark green": "#3a7a3a",
    "blue": "#4080e0",
    "pale blue": "#a0c0e0",
    "ice blue": "#c0e0f0",
    "cyan": "#50c0e0",
    "teal": "#40a0a0",
    "emerald": "#40c080",
    "violet": "#b0a0f0",
    "deep violet": "#7060c0",
    "pink": "#f0b0c0",
    "rose": "#e09090",
    "clear": "#e0f0f8",
    "ember": "#e05030",
    "hazel": "#b09050",
    "blonde": "#f0d880",
    "auburn": "#b05020",
    "strawberry": "#d09070",
    "platinum": "#e8e8f0",
    "moonlit": "#f0f8f0",
    "mud": "#8a7040",
    "stone": "#a0a090",
    "charcoal": "#505058",
    "obsidian": "#40404a",
    "flint": "#686878",
}


def hex_for_name(name):
    """Return the Truecolor hex for any named colour, checking the
    extended palette first, then the skin-tone master list."""
    if name:
        h = COLOR_HEXES.get(name.lower())
        if h:
            return h
    return SKIN_TONES.get(name)


def color_list_with_hex(names):
    """Return a comma-separated string of colour names each highlighted
    with its Truecolor hex, followed by the hex as literal text.
    Example: '|#b0a0f0violet|n (#b0a0f0), |#dcdcdc silver|n (#dcdcdc)'"""
    parts = []
    for name in names:
        h = hex_for_name(name)
        if h:
            parts.append(f"|{h}{name}|n ({h})")
        else:
            parts.append(name)
    return ", ".join(parts)

# ── Eyes ──────────────────────────────────────────────────────────────

SPECIES_EYES = {
    "terran": ["narrow", "round", "almond", "hooded", "wide", "deep-set"],
    "virentes": ["almond", "large", "luminous", "narrow", "serene", "bright"],
    "sideralis": ["unblinking", "vast", "narrow", "round", "far-seeing", "dark"],
    "batrachi": ["bulbous", "large", "narrow", "heavy-lidded", "glowing", "gold"],
    "tritonii": ["round", "large", "narrow", "lidless", "bright", "slitted"],
    "volucres": ["round", "fierce", "narrow", "golden", "piercing", "keen"],
    "pterati": ["large", "round", "narrow", "pale", "glowing", "red"],
    "visarii": ["narrow", "round", "angular", "hollow", "luminous", "faceted"],
    "silex": ["narrow", "deep-set", "glowing", "narrow", "chiseled", "flinty"],
}

SPECIES_EYE_DESCRIPTIONS = {
    "terran": {
        "narrow": "Narrow {color} eyes regard the world with quiet scrutiny.",
        "round": "Wide, round {color} eyes miss nothing.",
        "almond": "Almond-shaped {color} eyes give them a contemplative air.",
        "hooded": "Heavy lids shadow their {color} gaze.",
        "wide": "Wide, open {color} eyes hold an eager, curious light.",
        "deep-set": "Deep-set {color} eyes peer from beneath a heavy brow.",
    },
    "virentes": {
        "almond": "Perfectly almond-shaped {color} eyes gleam with quiet intelligence.",
        "large": "Large, expressive {color} eyes hold a gentle warmth.",
        "luminous": "Their {color} eyes glow with a soft, inner light.",
        "narrow": "Narrow, elegant {color} eyes hold an ancient wisdom.",
        "serene": "Calm, serene {color} eyes reflect a deep inner peace.",
        "bright": "Bright, vivid {color} eyes sparkle with quiet vitality.",
    },
    "sideralis": {
        "unblinking": "Unblinking {color} eyes stare fixed on something far beyond this place.",
        "vast": "Vast, depthless {color} eyes hold the silence of deep space.",
        "narrow": "Narrow, calculating {color} eyes assess with cold precision.",
        "round": "Round, dark {color} eyes reflect distant stars.",
        "far-seeing": "Their far-seeing {color} gaze pierces the veil of distance itself.",
        "dark": "Dark, fathomless {color} eyes reveal nothing of their thoughts.",
    },
    "batrachi": {
        "bulbous": "Bulbous {color} eyes protrude from their broad, flat face.",
        "large": "Enormous {color} eyes dominate their wide features.",
        "narrow": "Small, narrow {color} eyes peer out from beneath heavy brows.",
        "heavy-lidded": "Heavy lids droop over their drowsy {color} eyes.",
        "glowing": "Faintly glowing {color} eyes cut through the murk.",
        "gold": "Bright golden {color} eyes shine with an amphibian gleam.",
    },
    "tritonii": {
        "round": "Round, unblinking {color} eyes adapted for the deep.",
        "large": "Large, reflective {color} eyes catch every glimmer of light.",
        "narrow": "Narrow, slitted {color} eyes give them a reptilian look.",
        "lidless": "Lidless {color} eyes stare with unsettling permanence.",
        "bright": "Bright, vivid {color} eyes shimmer with aquatic brilliance.",
        "slitted": "Vertical slits split their luminous {color} irises.",
    },
    "volucres": {
        "round": "Round, sharp {color} eyes scan with predatory precision.",
        "fierce": "Fierce, burning {color} eyes miss nothing.",
        "narrow": "Narrow, calculating {color} eyes fix on movement.",
        "golden": "Golden {color} eyes burn like captured sunlight.",
        "piercing": "A piercing {color} gaze that seems to look through you.",
        "keen": "Keen {color} eyes track every flicker of motion.",
    },
    "pterati": {
        "large": "Enormous {color} eyes drink in every photon of available light.",
        "round": "Round, dark-adapted {color} eyes gleam in the gloom.",
        "narrow": "Narrow, calculating {color} eyes watch from the shadows.",
        "pale": "Pale, luminous {color} eyes glow faintly in the dark.",
        "glowing": "Softly glowing {color} eyes pierce the darkness.",
        "red": "Red-tinged {color} eyes burn with nocturnal hunger.",
    },
    "visarii": {
        "narrow": "Narrow {color} eyes gleam with an inner luminescence.",
        "round": "Round, crystalline {color} eyes reflect and refract the light.",
        "angular": "Sharp, angular {color} eye-sockets frame glowing crystal lenses.",
        "hollow": "Hollow {color} eye-sockets pulse with faint inner light.",
        "luminous": "Luminous {color} eyes glow like captured starlight.",
        "faceted": "Faceted {color} eyes catch the light like cut gems.",
    },
    "silex": {
        "narrow": "Narrow {color} eyes glow like embers in dark stone.",
        "deep-set": "Deep-set {color} eyes burn with a slow, smoldering fire.",
        "glowing": "Glowing {color} eyes peer from the darkness of their stony face.",
        "chiseled": "Chiseled {color} eye-sockets frame a hard, flinty gaze.",
        "flinty": "Flinty {color} eyes strike sparks when they catch the light.",
    },
}

# ── Eye colour ────────────────────────────────────────────────────────

SPECIES_EYE_COLORS = {
    "terran": ["brown", "hazel", "green", "blue", "gray", "amber"],
    "virentes": ["silver", "gold", "pale green", "ice blue", "violet", "white"],
    "sideralis": ["black", "silver", "void-blue", "white", "gold", "deep violet"],
    "batrachi": ["gold", "green", "amber", "brown", "red", "yellow"],
    "tritonii": ["silver", "cyan", "emerald", "violet", "gold", "black"],
    "volucres": ["gold", "amber", "yellow", "orange", "brown", "red"],
    "pterati": ["red", "silver", "pale blue", "violet", "white", "pink"],
    "visarii": ["violet", "silver", "white", "pale blue", "clear", "rose"],
    "silex": ["ember", "amber", "white", "red", "gold", "dull orange"],
}

SPECIES_EYE_COLOR_DESCRIPTIONS = {
    "terran": {
        "brown": "Warm brown eyes hold a steady, grounded gaze.",
        "hazel": "Hazel eyes shift between green and gold in the light.",
        "green": "Vivid green eyes sparkle with quiet intelligence.",
        "blue": "Clear blue eyes hold the depth of open sky.",
        "gray": "Gray eyes watch with calm, measured assessment.",
        "amber": "Amber eyes glow with a warm, golden light.",
    },
    "virentes": {
        "silver": "Silver eyes gleam with an ethereal, moonlit sheen.",
        "gold": "Golden eyes burn with a quiet, ancient fire.",
        "pale green": "Pale green eyes shimmer like sunlight through leaves.",
        "ice blue": "Ice-blue eyes hold a cold, crystalline beauty.",
        "violet": "Violet eyes glow with a soft, otherworldly light.",
        "white": "Pure white eyes radiate a gentle, inner glow.",
    },
    "sideralis": {
        "black": "Black eyes reflect the void between stars.",
        "silver": "Silver eyes gleam with the light of distant suns.",
        "void-blue": "Deep void-blue eyes hold the silence of deep space.",
        "white": "White eyes glow with the light of a thousand distant stars.",
        "gold": "Gold eyes burn with the fury of a newborn sun.",
        "deep violet": "Deep violet eyes hold the mystery of the cosmos.",
    },
    "batrachi": {
        "gold": "Bright gold eyes gleam with a predatory intelligence.",
        "green": "Green eyes glow faintly in the damp darkness.",
        "amber": "Amber eyes shimmer with a warm, amphibian gleam.",
        "brown": "Deep brown eyes hold a quiet, patient watchfulness.",
        "red": "Red-tinged eyes burn with an unsettling inner fire.",
        "yellow": "Bright yellow eyes fix on you with unblinking focus.",
    },
    "tritonii": {
        "silver": "Silver eyes gleam like polished mercury.",
        "cyan": "Cyan eyes shimmer with the colors of tropical seas.",
        "emerald": "Emerald eyes flash with vivid, aquatic brilliance.",
        "violet": "Violet eyes hold the depth of the midnight ocean.",
        "gold": "Gold eyes burn with an ancient, tidal power.",
        "black": "Black eyes reflect the lightless abyss below.",
    },
    "volucres": {
        "gold": "Golden eyes burn with the fierce light of a raptor.",
        "amber": "Amber eyes glow with a warm, predatory intensity.",
        "yellow": "Bright yellow eyes miss nothing from their high perch.",
        "orange": "Orange eyes burn like sunset caught in glass.",
        "brown": "Rich brown eyes hold a keen, searching intelligence.",
        "red": "Red-tinged eyes flash with a fierce, hunting light.",
    },
    "pterati": {
        "red": "Red eyes glow like embers in the darkness.",
        "silver": "Silver eyes gleam with a pale, nocturnal light.",
        "pale blue": "Pale blue eyes shimmer with a ghostly luminescence.",
        "violet": "Violet eyes glow faintly in the shadows.",
        "white": "White eyes radiate a soft, otherworldly glow.",
        "pink": "Pale pink eyes catch the faintest glimmer of light.",
    },
    "visarii": {
        "violet": "Violet eyes glow with a soft, prismatic light.",
        "silver": "Silver eyes gleam like polished crystal.",
        "white": "White eyes radiate a pure, crystalline glow.",
        "pale blue": "Pale blue eyes shimmer like ice catching sunlight.",
        "clear": "Clear as glass, their eyes reveal the light within.",
        "rose": "Rose-tinted eyes catch the light in soft, warm flashes.",
    },
    "silex": {
        "ember": "Ember eyes glow with the heat of the forge.",
        "amber": "Amber eyes burn like trapped sunlight in dark stone.",
        "white": "White eyes glow with a stark, unyielding light.",
        "red": "Red eyes smolder with a slow, volcanic fire.",
        "gold": "Gold eyes gleam like veins of precious metal in rock.",
        "dull orange": "Dull orange eyes pulse with a deep, subterranean heat.",
    },
}

# ── Hair ──────────────────────────────────────────────────────────────

SPECIES_HAIR = {
    "terran": ["cropped", "long", "wild", "braided", "shaved", "tied back", "curly", "straight"],
    "virentes": ["flowing", "braided", "tied back", "cropped", "silken", "loose", "adorned"],
    "sideralis": ["none", "sleek", "closely cropped", "smooth", "slicked back"],
    "batrachi": ["none", "mohawk", "ridge", "bristled", "craggy"],
    "tritonii": ["flowing", "finned", "slicked", "none", "braided", "crest"],
    "volucres": ["feathered crest", "plumed", "slicked", "none", "crested", "wild"],
    "pterati": ["sleek", "none", "furred crest", "spiked", "cropped", "wild"],
    "visarii": ["none", "crystalline shards", "faceted crest", "crystal spires", "smooth"],
    "silex": ["none", "stone ridges", "jagged crest", "chiseled", "cracked", "smooth"],
}

SPECIES_HAIR_DESCRIPTIONS = {
    "terran": {
        "cropped": "Close-cropped {color} hair frames their practical features.",
        "long": "Long {color} hair falls past their shoulders in a loose cascade.",
        "wild": "Wild, untamed {color} hair frames their face like a storm.",
        "braided": "Neat {color} braids gather their hair in an orderly fashion.",
        "shaved": "A shaved head reveals the shape of their skull.",
        "tied back": "{color} hair pulled back in a tight tail keeps it from their eyes.",
        "curly": "Tight {color} curls spring about their head in a lively mass.",
        "straight": "Straight, even {color} hair falls in a neat, orderly fashion.",
    },
    "virentes": {
        "flowing": "Long {color} hair flows like liquid silk about their shoulders.",
        "braided": "Intricate {color} braids weave through their hair like living vines.",
        "tied back": "{color} hair gathered at the nape reveals an elegant neckline.",
        "cropped": "Short, neat {color} hair frames their fine-boned features.",
        "silken": "Impossibly smooth {color} hair shimmers with an inner light.",
        "loose": "Loose {color} hair frames their face in soft, gentle waves.",
        "adorned": "Their {color} hair is adorned with delicate, living blossoms.",
    },
    "sideralis": {
        "none": "Bare of hair, their smooth scalp gleams like polished stone.",
        "sleek": "Sleek, close-lying {color} hair adds to their streamlined form.",
        "closely cropped": "{color} hair cropped close to the skull, minimal and precise.",
        "smooth": "A smooth, hairless head reflects the starlight.",
        "slicked back": "{color} hair slicked back, revealing a broad, smooth brow.",
    },
    "batrachi": {
        "none": "Hairless, their mottled hide stretches unbroken over a broad skull.",
        "mohawk": "A ridge of coarse {color} hair stands stiff along their crown.",
        "ridge": "A hard, bony ridge replaces conventional hair.",
        "bristled": "Short, stiff {color} bristles sprout from their scalp.",
        "craggy": "Rough, craggy {color} growths crown their broad head.",
    },
    "tritonii": {
        "flowing": "Long, flowing {color} fins trail from their scalp like living hair.",
        "finned": "Broad, fan-like {color} fins replace hair along their crown.",
        "slicked": "{color} hair slicked flat, streamlined for swift movement.",
        "none": "Bare of hair, their smooth scalp is hydrodynamic.",
        "braided": "Tendrils of {color} fin are woven into neat, flowing braids.",
        "crest": "A tall, rigid {color} fin crests along the top of their head.",
    },
    "volucres": {
        "feathered crest": "A tall crest of stiff {color} feathers rises from their crown.",
        "plumed": "Soft, {color} plumes adorn their head and neck.",
        "slicked": "{color} feathers slicked flat, streamlined for flight.",
        "none": "Bare of feathers, their sleek skull is smooth and aerodynamic.",
        "crested": "A sharp, pointed crest of {color} feathers crowns their head.",
        "wild": "Wild, ruffled {color} feathers frame their fierce features.",
    },
    "pterati": {
        "sleek": "Sleek {color} fur lies flat and smooth along their scalp.",
        "none": "Hairless, their pale scalp stretches tight over sharp bone.",
        "furred crest": "A crest of soft {color} fur rises along the back of their head.",
        "spiked": "Stiff, spiked {color} fur stands in sharp tufts.",
        "cropped": "Close-cropped {color} fur keeps a neat, practical profile.",
        "wild": "Wild, untamed {color} fur bristles about their angular features.",
    },
    "visarii": {
        "none": "Bare of adornment, their crystalline skull is smooth and sharp.",
        "crystalline shards": "Shards of {color} crystal jut from their crown like frozen flames.",
        "faceted crest": "A crest of faceted {color} crystal rises from their scalp.",
        "crystal spires": "Tall {color} crystal spires reach upward from their head.",
        "smooth": "A smooth, polished {color} crystalline surface crowns their form.",
    },
    "silex": {
        "none": "Bare of growth, their stone skull is rough and unyielding.",
        "stone ridges": "Rough {color} stone ridges run along their scalp like natural armor.",
        "jagged crest": "A jagged crest of sharp {color} stone rises from their crown.",
        "chiseled": "{color} chiseled grooves pattern their stony scalp.",
        "cracked": "Deep {color} cracks run through the stone of their skull.",
        "smooth": "Unusually smooth {color} stone crowns their dark, heavy form.",
    },
}

# ── Hair colour ───────────────────────────────────────────────────────

SPECIES_HAIR_COLORS = {
    "terran": ["black", "brown", "blonde", "red", "gray", "white", "auburn", "strawberry"],
    "virentes": ["silver", "gold", "white", "pale green", "moonlit", "platinum"],
    "sideralis": ["black", "silver", "void-blue", "white", "midnight"],
    "batrachi": ["none", "dark green", "brown", "mud", "black", "olive"],
    "tritonii": ["blue", "green", "silver", "violet", "teal", "black"],
    "volucres": ["white", "black", "brown", "red", "gold", "grey"],
    "pterati": ["black", "dark brown", "grey", "silver", "white"],
    "visarii": ["clear", "violet", "silver", "white", "rose", "ice blue"],
    "silex": ["black", "dark grey", "charcoal", "stone", "obsidian", "flint"],
}

SPECIES_HAIR_COLOR_DESCRIPTIONS = {
    "terran": {
        "black": "Jet-black hair frames their dark features.",
        "brown": "Rich brown hair falls in warm, earthy tones.",
        "blonde": "Golden-blonde hair catches the light like spun wheat.",
        "red": "Fiery red hair burns like a living flame.",
        "gray": "Gray-streaked hair speaks of years and experience.",
        "white": "White hair gleams like fresh snow in sunlight.",
        "auburn": "Deep auburn hair holds warm, coppery highlights.",
        "strawberry": "Strawberry-blonde hair shimmers with warm, rosy tones.",
    },
    "virentes": {
        "silver": "Silver hair gleams with a soft, moonlit sheen.",
        "gold": "Golden hair shimmers like captured sunlight.",
        "white": "Pure white hair cascades like a waterfall of light.",
        "pale green": "Pale green hair shimmers like sunlight through new leaves.",
        "moonlit": "Hair the color of moonlight on still water.",
        "platinum": "Platinum hair gleams with an almost metallic brilliance.",
    },
    "sideralis": {
        "black": "Black hair absorbs all light, a void against their skin.",
        "silver": "Silver hair gleams like starlight on dark stone.",
        "void-blue": "Deep void-blue hair holds the color of deep space.",
        "white": "White hair glows faintly against their dark form.",
        "midnight": "Midnight-dark hair blends into the void.",
    },
    "batrachi": {
        "none": "No hair to color — their hide speaks for itself.",
        "dark green": "Dark green bristles cling to their damp scalp.",
        "brown": "Muddy brown bristles sprout in rough patches.",
        "mud": "Hair the color of river mud, stiff and coarse.",
        "black": "Black bristles stand stiff against their mottled hide.",
        "olive": "Olive-drab bristles blend with their swampy tones.",
    },
    "tritonii": {
        "blue": "Vivid blue fins trail like living ribbons.",
        "green": "Emerald-green fins shimmer with aquatic brilliance.",
        "silver": "Silver fins catch the light like polished metal.",
        "violet": "Violet fins flow with a deep, oceanic hue.",
        "teal": "Teal fins shimmer with the colors of tropical waters.",
        "black": "Dark fins blend into the deep ocean shadows.",
    },
    "volucres": {
        "white": "White feathers gleam like fresh snow.",
        "black": "Dark feathers gleam with an iridescent sheen.",
        "brown": "Rich brown feathers provide warm, earthy camouflage.",
        "red": "Red feathers blaze like a living flame.",
        "gold": "Golden feathers shimmer like captured sunlight.",
        "grey": "Grey feathers blend with storm clouds and stone.",
    },
    "pterati": {
        "black": "Jet-black fur absorbs the light, deepening their shadow.",
        "dark brown": "Dark brown fur lies sleek and smooth.",
        "grey": "Grey fur blends with the stone and shadow.",
        "silver": "Silver fur gleams faintly in the dim light.",
        "white": "White fur stands stark against their dark features.",
    },
    "visarii": {
        "clear": "Clear crystal crowns their head, catching and scattering light.",
        "violet": "Violet crystal shards glow with a soft, inner light.",
        "silver": "Silver crystal gleams like polished mirror.",
        "white": "White crystal radiates a pure, clean glow.",
        "rose": "Rose-tinted crystal catches the light in warm, pink flashes.",
        "ice blue": "Ice-blue crystal shimmers with a cold, crystalline beauty.",
    },
    "silex": {
        "black": "Black stone crowns their head, dark and unyielding.",
        "dark grey": "Dark grey stone blends with their matte-black form.",
        "charcoal": "Charcoal-dark stone absorbs the light.",
        "stone": "Natural stone tones crown their heavy, chiseled form.",
        "obsidian": "Obsidian-dark stone gleams with a glassy sheen.",
        "flint": "Flint-grey stone sparks when it catches the light.",
    },
}

# Per-species skin sentence templates.  {color} is replaced with the
# skin tone name wrapped in its Truecolor hex code.
SPECIES_SKIN_SENTENCES = {
    "terran": "Their skin bears a {color} hue.",
    "virentes": "Their skin carries a {color} sheen.",
    "sideralis": "Their skin holds a {color} tint.",
    "batrachi": "Their hide is marked with {color} tones.",
    "tritonii": "Their skin shimmers with {color} patterns.",
    "volucres": "Their feathers carry a {color} tint.",
    "pterati": "Their fur carries a {color} sheen.",
    "visarii": "Their crystalline surface catches {color} light.",
    "silex": "Their stone flesh carries {color} undertones.",
    "wisp": "Their light glows with a {color} radiance.",
}

# ── Pose ──────────────────────────────────────────────────────────────

POSES = (
    "standing", "sitting", "resting", "laying", "sleeping",
    "kneeling", "crouching", "leaning", "lounging", "reclining",
    "squatting", "hiding", "meditating", "pacing", "observing",
    "guarding", "praying", "dreaming", "hovering",
)

POSE_OPENINGS = {
    "standing": "Before you stands",
    "sitting": "Before you sits",
    "resting": "Before you rests",
    "laying": "Before you lies",
    "sleeping": "Before you lies, deep in slumber",
    "kneeling": "Before you kneels",
    "crouching": "Before you crouches",
    "leaning": "Before you leans",
    "lounging": "Before you lounges",
    "reclining": "Before you reclines",
    "squatting": "Before you squats",
    "hiding": "Partially hidden,",
    "meditating": "Before you sits, lost in meditation",
    "pacing": "Before you paces",
    "observing": "Before you stands, watching intently",
    "guarding": "Before you stands, ever vigilant",
    "praying": "Before you kneels in quiet prayer",
    "dreaming": "Before you lies, adrift in dreams",
    "hovering": "Before you hovers",
}


def valid_pose(pose):
    """Return True if the pose is a whitelisted position word."""
    return pose in POSES

# ── Article helper ────────────────────────────────────────────────────


def article(word):
    """Return 'An' or 'A' based on the first letter of a word."""
    if word and word[0].lower() in "aeiou":
        return "An"
    return "A"


# ── Option-list helpers for builder commands ──────────────────────────


def eye_options(species_key):
    """Return the eye-shape options for a species key."""
    return tuple(SPECIES_EYES.get(species_key, ()))


def valid_eye(species_key, word):
    """Return True if a word is a valid eye shape for the species."""
    return word in eye_options(species_key)


def eye_color_options(species_key):
    """Return the eye-colour options for a species key."""
    return tuple(SPECIES_EYE_COLORS.get(species_key, ()))


def valid_eye_color(species_key, word):
    """Return True if a word is a valid eye colour for the species."""
    return word in eye_color_options(species_key)


def hair_options(species_key):
    """Return the hair-style options for a species key."""
    return tuple(SPECIES_HAIR.get(species_key, ()))


def valid_hair(species_key, word):
    """Return True if a word is a valid hair style for the species."""
    return word in hair_options(species_key)


def hair_color_options(species_key):
    """Return the hair-colour options for a species key."""
    return tuple(SPECIES_HAIR_COLORS.get(species_key, ()))


def valid_hair_color(species_key, word):
    """Return True if a word is a valid hair colour for the species."""
    return word in hair_color_options(species_key)
