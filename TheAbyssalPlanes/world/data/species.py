"""
Species roster for The Abyssal Planes.

Pure data module - no Evennia imports, so it can be imported anywhere.
Each species is defined by:

    key                 - machine key used to store on the character
    name                - display name
    archetype           - colloquial one-line label (human, elf, orc, ...)
    aliases             - alternate lookup/help names
    visarial_nature     - "dual_natured", "visarial" or "physical"
    default_visarial_state - starting visarial state; all species except the
                          Visarii start "physical"
    stat_bonuses        - {sub_stat: bonus} persistent modifiers added on top
                          of the base sub-stat (effective = base + bonus)
    locked_main_stats   - main stats permanently locked at 0 (all sub-stats
                          under them read as 0)
    locked_alternates   - {locked_main: substitute_main}: when a skill
                          exercises a sub-stat under a locked main, it instead
                          feeds the substitute main (same sub-stat slot). Only
                          present on species with locked mains; other species
                          need no entry.
    zero_pools          - derived pools pinned to 0 (max and regen); also
                          hidden from the prompt
    cannot_perceive     - cannot perceive or manifest into the visarial realm
    description         - flavor text
"""

SPECIES = {
    "terran": {
        "key": "terran",
        "name": "Terran",
        "archetype": "standard human",
        "aliases": ["human", "humanoid"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"genius_obsistis": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Terra-born, versatile, and balanced. They are the standard, "
            "adaptable middle-ground species of the material world. Classic, "
            "flesh-and-blood humanoids with varied physical builds and "
            "complexions. They populate all ends of whatever planetary body "
            "they are on, constantly seeking expansion."
        ),
    },
    "virentes": {
        "key": "virentes",
        "name": "Virentes",
        "archetype": "standard elf",
        "aliases": ["elf", "elven"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"genius_potestas": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Lithe, flawless humanoids with an ethereal elegance. They are "
            "distinct from the crystalline Visarii because they are entirely "
            "flesh-and-blood, possessing a vibrant, radiant life force that "
            "makes them look perpetually youthful. They naturally excel in "
            "the Genius (Mind) column. Because of their immense lifespans, "
            "they use their superior cognitive focus and deep memories "
            "(Memoria) to master complex skills and strategies, acting as "
            "highly disciplined scholars, tacticians, or precision marksmen."
        ),
    },
    "sideralis": {
        "key": "sideralis",
        "name": "Sideralis",
        "archetype": "space elf",
        "aliases": ["space elf", "sideral"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"animus_obsistis": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "An ancient branch of humanoids that evolved to live, travel, and "
            "survive in the vacuum of space. Exceptionally tall, graceful "
            "humanoids with dense, rubberized skin that ranges from a vibrant "
            "cerulean to a midnight blue nearly as dark as the void. They "
            "possess long, tapered ears that sweep back along the sides of "
            "their heads, and lack hair of any sort due to adaptation to the "
            "void. Their eyes are large, expressive, and lack any visible "
            "sclera, with irises that range greatly in color. They are stoic "
            "and unyielding. Living in the quiet, frozen void between worlds "
            "has given them absolute control over their internal spirit. They "
            "do not flicker or shake under pressure."
        ),
    },
    "batrachi": {
        "key": "batrachi",
        "name": "Batrachi",
        "archetype": "toad-men",
        "aliases": ["toad man", "toad", "batrachian"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"corpus_potestas": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Massive, broad-shouldered, and stocky creatures with dense, "
            "warty hide that ranges from deep marsh-green to muddy brown. "
            "They possess powerful hind legs and wide, imposing frames. They "
            "dominate wetlands, swamps, and subterranean lakes. They lean "
            "heavily into the Corpus column, using their immense physical "
            "mass to soak up damage. Because amphibians absorb elements "
            "through their skin, they are hyper-sensitive to environmental "
            "energy; they can physically feel ripples and vibrations bleeding "
            "out from the Visarium whenever magic is cast nearby."
        ),
    },
    "tritonii": {
        "key": "tritonii",
        "name": "Tritonii",
        "archetype": "newt-men",
        "aliases": ["newt man", "newt", "triton"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"corpus_reflexus": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Slender, highly agile amphibian humanoids who represent the "
            "swift, toxic, and predatory side of the waterways. Sleek, "
            "long-tailed humanoids with smooth, glossy skin that displays "
            "striking, bright warning patterns - such as vibrant yellow, "
            "orange, or violet stripes against pitch-black flesh. They act as "
            "lethal scouts, skirmishers, and rogues who are equally dangerous "
            "on land and in deep water. They naturally excel in the Corpus "
            "Reflexus (Agilitas) slot. They rely on their blinding swimming "
            "speeds, nimble land movement, and natural skin toxicity to "
            "execute fast hit-and-run ambushes before vanishing back into "
            "rivers or mangroves."
        ),
    },
    "volucres": {
        "key": "volucres",
        "name": "Volucres",
        "archetype": "bird-men",
        "aliases": ["bird man", "bird", "volucre"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"animus_reflexus": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Elegant and predatory, resembling falcons or eagles. They live "
            "on high, wind-swept spires where the physical atmosphere thins "
            "out and physically brushes against the upper ether of the "
            "planetary bodies, making them natural masters of sky-tracking "
            "and ranged combat."
        ),
    },
    "pterati": {
        "key": "pterati",
        "name": "Pterati",
        "archetype": "bat-men",
        "aliases": ["bat man", "bat", "pterat"],
        "visarial_nature": "dual_natured",
        "default_visarial_state": "physical",
        "stat_bonuses": {"genius_reflexus": 1},
        "locked_main_stats": (),
        "zero_pools": (),
        "cannot_perceive": False,
        "description": (
            "Darker, stealthier, and more nocturnal than the Volucres. "
            "Instead of pure flapping flight, they excel at high-speed diving "
            "and silent gliding. They are perfect for traditional rogue or "
            "assassin archetypes, dropping down out of the dark sky "
            "completely undetected. They also possess a natural "
            "echo-location, giving them sight despite conditions."
        ),
    },
    "visarii": {
        "key": "visarii",
        "name": "Visarii",
        "archetype": "crystal elf",
        "aliases": ["crystal elf", "crystal"],
        "visarial_nature": "visarial",
        "default_visarial_state": "manifested",
        "stat_bonuses": {"animus_potestas": 1},
        "locked_main_stats": ("corpus",),
        "locked_alternates": {"corpus": "animus"},
        "zero_pools": ("vigor",),
        "cannot_perceive": False,
        "description": (
            "Sleek, sharp, and geometric humanoids made of a translucent, "
            "violet-tinged crystalline form. In the physical world they exist "
            "only as floating, translucent silhouettes or violet vapors with "
            "no physical mass. Their Corpus is locked permanently at 0 - "
            "physical weapons pass right through them, and they cannot "
            "physically lift real-world objects unless they use magic. Their "
            "Animus, however, is immense. They have no Vigor, dying instead "
            "when their Vim and Mens reach 0."
        ),
    },
    "silex": {
        "key": "silex",
        "name": "Silex",
        "archetype": "flint-like orc",
        "aliases": ["orc", "flint orc", "stone orc"],
        "visarial_nature": "physical",
        "default_visarial_state": "physical",
        "stat_bonuses": {"corpus_obsistis": 1},
        "locked_main_stats": ("animus",),
        "locked_alternates": {"animus": "corpus"},
        "zero_pools": ("vim",),
        "cannot_perceive": True,
        "description": (
            "Somewhat large humanoids with rough, chiseled, matte-black stone "
            "flesh. When they clash in battle, their rocky skin literally "
            "strikes sparks. Their Animus is locked permanently at 0, meaning "
            "they have 0 Vim and cannot see the Visarium. However, they "
            "possess unmatched Corpus stats. Spells shatter harmlessly "
            "against their obsidian frames, making them the ultimate "
            "anti-magic shock troops and master earth-workers."
        ),
    },
}

_ORDER = tuple(SPECIES)


def species_keys():
    """Return all species keys in definition order."""
    return _ORDER


def get_species(key):
    """Return the species data dict for a key, or None."""
    if not key:
        return None
    return SPECIES.get(key.strip().lower())


def species_name(key):
    """Return the display name for a species key, or the key itself."""
    data = get_species(key)
    return data["name"] if data else key


def stat_bonus(key, sub_stat):
    """Return the persistent bonus for a given sub-stat, or 0."""
    data = get_species(key)
    if not data:
        return 0
    return data["stat_bonuses"].get(sub_stat, 0)


def is_locked(key, main_stat):
    """Return True if a main stat is locked at 0 for the species."""
    data = get_species(key)
    return bool(data and main_stat in data["locked_main_stats"])


def alternate_for(key, main_stat):
    """
    Return the substitute main stat for a locked main, or None.

    A skill exercising a sub-stat under a locked main feeds the substitute
    main instead (same sub-stat slot). Returns None if the main is not locked
    or the species has no alternate defined.
    """
    data = get_species(key)
    if not data:
        return None
    return data.get("locked_alternates", {}).get(main_stat)


def zeroed_pools(key):
    """Return the tuple of pools pinned to 0 for the species."""
    data = get_species(key)
    return data["zero_pools"] if data else ()
