"""
Guided character creation menu.

Launched by CmdCharCreate after the character object is created.
Walks the player through gender, species, appearance, stat priorities,
and stat point allocation before they enter the game.
"""

from world.data import appearance, species as species_data
from world.systems import stats

# ── helpers ────────────────────────────────────────────────────────────


def _get_char(caller):
    """Return the character being created, or the last one on the account."""
    char = caller.ndb._chargen_character
    if not char and caller.account:
        chars = caller.account.characters
        if chars:
            char = chars[-1]
            caller.ndb._chargen_character = char
    return char


def _store(caller, key, value):
    """Store a chargen value on the caller's ndb."""
    menu = caller.ndb._evmenu
    if menu:
        if not hasattr(menu, "_data"):
            menu._data = {}
        menu._data[key] = value


def _load(caller, key, default=None):
    """Load a chargen value from the caller's ndb."""
    menu = caller.ndb._evmenu
    if menu and hasattr(menu, "_data"):
        return menu._data.get(key, default)
    return default


def _options_list(items):
    """Build numbered option dicts from a list of strings."""
    return [
        {"key": str(i + 1), "desc": item, "goto": ("_parse_choice", {"choice": str(i + 1), "items": items})}
        for i, item in enumerate(items)
    ]


def _parse_choice(caller, raw_string, **kwargs):
    """Shared parser: resolve a numbered choice to the actual value."""
    items = kwargs.get("items", [])
    choice = raw_string.strip()
    if not choice.isdigit():
        caller.msg("Enter a number from the list.")
        return None
    idx = int(choice) - 1
    if idx < 0 or idx >= len(items):
        caller.msg(f"Enter a number between 1 and {len(items)}.")
        return None
    return items[idx]


# ── welcome ────────────────────────────────────────────────────────────


def node_welcome(caller, raw_string, **kwargs):
    char = _get_char(caller)
    if not char:
        caller.msg("Something went wrong — no character found. Try 'charcreate <name>' again.")
        return None

    text = (
        f"|wWelcome, {char.key}.|n\n\n"
        "We will walk through your character's identity, appearance, "
        "and starting attributes step by step. You can type |wquit|n at "
        "any time to abandon this process.\n\n"
        f"Your character's name will be |w{char.key}|n. Let's begin."
    )
    options = (
        {"key": "_default", "goto": "node_gender"},
    )
    return text, options


# ── gender ─────────────────────────────────────────────────────────────


def node_gender(caller, raw_string, **kwargs):
    text = (
        "|wStep 1 — Gender|n\n\n"
        "What is your character's gender?"
    )
    options = [
        {"key": "1", "desc": "Male", "goto": ("_set_gender", {"gender": "male"})},
        {"key": "2", "desc": "Female", "goto": ("_set_gender", {"gender": "female"})},
        {"key": "3", "desc": "Neuter", "goto": ("_set_gender", {"gender": "neuter"})},
    ]
    return text, options


def _set_gender(caller, raw_string, **kwargs):
    gender = kwargs["gender"]
    char = _get_char(caller)
    if char:
        char.gender = gender
    _store(caller, "gender", gender)
    return "node_species"


# ── species ────────────────────────────────────────────────────────────


def node_species(caller, raw_string, **kwargs):
    text = (
        "|wStep 2 — Species|n\n\n"
        "Choose your character's species. Each species has a unique "
        "visarial nature, stat bonuses, and locked attributes."
    )
    items = []
    for key in species_data.species_keys():
        data = species_data.get_species(key)
        if data:
            items.append(f"{data['name']:12s}  {data['archetype']} ({data['visarial_nature'].replace('_', '-')})")
    options = _options_list(items)
    return text, options


def _set_species(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    # Extract the species key from the display string.
    species_name = value.split()[0].lower()
    # Map display names to keys.
    key_map = {data["name"].lower(): data["key"] for key in species_data.species_keys()
               if (data := species_data.get_species(key))}
    species_key = key_map.get(species_name)
    if not species_key:
        caller.msg("Invalid species. Try again.")
        return "node_species"

    char = _get_char(caller)
    if char:
        char.apply_species(species_key)
    _store(caller, "species_key", species_key)
    _store(caller, "species_name", species_data.species_name(species_key))
    return "node_height"


# ── height ─────────────────────────────────────────────────────────────


def node_height(caller, raw_string, **kwargs):
    text = (
        "|wStep 3 — Height|n\n\n"
        "Choose your character's height. Height is relative to your species."
    )
    descs = {
        "diminutive": "Barely reaching the knee of an average humanoid.",
        "short": "Noticeably shorter than most, with a compact presence.",
        "middling": "Of average height, neither towering nor slight.",
        "tall": "Taller than average, with a commanding presence.",
        "towering": "Enormous, towering over most who stand nearby.",
    }
    items = [f"{h.title()}: {descs[h]}" for h in appearance.HEIGHTS]
    options = _options_list(items)
    return text, options


def _set_height(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    height = value.split(":")[0].strip().lower()
    char = _get_char(caller)
    if char:
        char.appearance_height = height
    _store(caller, "height", height)
    return "node_build"


# ── build ──────────────────────────────────────────────────────────────


def node_build(caller, raw_string, **kwargs):
    height = _load(caller, "height", "middling")
    text = (
        "|wStep 4 — Build|n\n\n"
        f"Choose a build valid for |w{height}|n height."
    )
    builds = appearance.builds_for_height(height)
    items = [f"{b.title()}: {appearance.BUILD_DESCRIPTIONS.get(b, '')}" for b in builds]
    options = _options_list(items)
    return text, options


def _set_build(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    build = value.split(":")[0].strip().lower()
    char = _get_char(caller)
    if char:
        char.appearance_build = build
    _store(caller, "build", build)
    return "node_adjective"


# ── adjective ──────────────────────────────────────────────────────────


def node_adjective(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 5 — Adjective|n\n\n"
        "Choose a descriptor for your character from your species' list."
    )
    adjs = appearance.adjectives_for_species(species_key)
    items = list(adjs)
    options = _options_list(items)
    return text, options


def _set_adjective(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    char = _get_char(caller)
    if char:
        char.appearance_adjective = value.lower()
    _store(caller, "adjective", value.lower())
    return "node_skin"


# ── skin ───────────────────────────────────────────────────────────────


def node_skin(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 6 — Skin Colour|n\n\n"
        "Choose a skin tone from your species' palette."
    )
    skins = appearance.skins_for_species(species_key)
    items = list(skins)
    options = _options_list(items)
    return text, options


def _set_skin(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    char = _get_char(caller)
    if char:
        char.appearance_skin = value.lower()
    _store(caller, "skin", value.lower())
    return "node_eyes"


# ── eyes ───────────────────────────────────────────────────────────────


def node_eyes(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 7 — Eye Shape|n\n\n"
        "Choose an eye shape from your species' list."
    )
    eyes = appearance.eye_options(species_key)
    items = list(eyes)
    options = _options_list(items)
    return text, options


def _set_eyes(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    char = _get_char(caller)
    if char:
        char.appearance_eyes = value.lower()
    _store(caller, "eyes", value.lower())
    return "node_eye_color"


# ── eye colour ─────────────────────────────────────────────────────────


def node_eye_color(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 8 — Eye Colour|n\n\n"
        "Choose an eye colour from your species' palette."
    )
    colors = appearance.eye_color_options(species_key)
    items = list(colors)
    options = _options_list(items)
    return text, options


def _set_eye_color(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    char = _get_char(caller)
    if char:
        char.appearance_eye_color = value.lower()
    _store(caller, "eye_color", value.lower())
    return "node_hair"


# ── hair ───────────────────────────────────────────────────────────────


def node_hair(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 9 — Hair Style|n\n\n"
        "Choose a hair style from your species' list. Some species "
        "have |wnone|n as an option."
    )
    hairs = appearance.hair_options(species_key)
    items = list(hairs)
    options = _options_list(items)
    return text, options


def _set_hair(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    hair = value.lower()
    char = _get_char(caller)
    if char:
        char.appearance_hair = hair
    _store(caller, "hair", hair)
    # Skip hair colour if no hair.
    if hair == "none":
        return "node_stat_priority"
    return "node_hair_color"


# ── hair colour ────────────────────────────────────────────────────────


def node_hair_color(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    text = (
        "|wStep 10 — Hair Colour|n\n\n"
        "Choose a hair colour from your species' palette."
    )
    colors = appearance.hair_color_options(species_key)
    items = list(colors)
    options = _options_list(items)
    return text, options


def _set_hair_color(caller, raw_string, **kwargs):
    items = kwargs["items"]
    value = _parse_choice(caller, raw_string, items=items)
    if value is None:
        return None

    char = _get_char(caller)
    if char:
        char.appearance_hair_color = value.lower()
    _store(caller, "hair_color", value.lower())
    return "node_stat_priority"


# ── stat priority ──────────────────────────────────────────────────────


def node_stat_priority(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    locked = [m for m in stats.MAIN_STATS if species_data.is_locked(species_key, m)]

    text = (
        "|wStep 11 — Stat Priorities|n\n\n"
        "Arrange the three main attributes in order of importance. "
        "The |wfirst|n you choose gets |w6 points|n to distribute among "
        "its sub-stats, the |wsecond|n gets |w4 points|n, and the "
        "|wthird|n gets |w2 points|n.\n\n"
        "Each sub-stat starts at 1 and can go up to 5 at creation."
    )
    if locked:
        text += (
            f"\n\n|wNote:|n Your species has |x{', '.join(l.title() for l in locked)}|n "
            "locked at 0 — points placed there are wasted."
        )
    text += (
        "\n\nType the three stats in your preferred order, e.g. |wCorpus Genius Animus|n."
    )

    options = {"key": "_default", "goto": ("_parse_priority", {"locked": locked})}
    return text, options


def _parse_priority(caller, raw_string, **kwargs):
    locked = kwargs.get("locked", [])
    parts = raw_string.strip().lower().split()
    if len(parts) != 3:
        caller.msg("Enter exactly three stat names in order, e.g. 'Corpus Genius Animus'.")
        return None

    # Validate and normalise.
    valid = []
    for p in parts:
        if p not in stats.MAIN_STATS:
            caller.msg(f"Unknown stat '{p}'. Use Corpus, Genius, or Animus.")
            return None
        if p in valid:
            caller.msg(f"You already chose {p.title()}.")
            return None
        valid.append(p)

    _store(caller, "stat_priorities", valid)
    _store(caller, "_dist_remaining", list(valid))
    _store(caller, "_dist_points", [6, 4, 2])
    _store(caller, "_dist_idx", 0)
    _store(caller, "_dist_values", {})
    return "node_stat_dist"


# ── stat distribution (shared node, loops 3 times) ─────────────────────


def node_stat_dist(caller, raw_string, **kwargs):
    idx = _load(caller, "_dist_idx", 0)
    priorities = _load(caller, "stat_priorities", [])
    points_list = _load(caller, "_dist_points", [6, 4, 2])
    values = _load(caller, "_dist_values", {})
    species_key = _load(caller, "species_key", "")

    if idx >= 3:
        # All three priorities distributed — go to review.
        return "node_review"

    main = priorities[idx]
    points = points_list[idx]
    subs = stats.SUB_STATS

    # Build sub-stat descriptions.
    sub_labels = {
        "potestas": "Power — raw output",
        "reflexus": "Speed — agility and recovery",
        "obsistis": "Resist — toughness and endurance",
    }
    lines = []
    for sub in subs:
        locked = species_data.is_locked(species_key, main)
        label = f"  {main.title()} {sub.title():10s} — {sub_labels[sub]}"
        if locked:
            label += " |x(LOCKED)|n"
        lines.append(label)

    text = (
        f"|wStep 12 — Distribute {points} points: {main.title()}|n\n\n"
        "Distribute your points across the three sub-stats. "
        "Each starts at 1 and can reach 5. Enter three numbers "
        f"that sum to {points}, e.g. |w2 2 2|n or |w3 2 1|n.\n\n"
        + "\n".join(lines)
    )

    locked = species_data.is_locked(species_key, main)
    options = {"key": "_default", "goto": ("_parse_dist", {"main": main, "points": points, "locked": locked})}
    return text, options


def _parse_dist(caller, raw_string, **kwargs):
    main = kwargs["main"]
    points = kwargs["points"]
    locked = kwargs["locked"]
    subs = stats.SUB_STATS

    parts = raw_string.strip().split()
    if len(parts) != 3:
        caller.msg(f"Enter exactly three numbers that sum to {points}.")
        return None

    try:
        vals = [int(p) for p in parts]
    except ValueError:
        caller.msg("Enter whole numbers only.")
        return None

    if sum(vals) != points:
        caller.msg(f"The three numbers must sum to {points} (you gave {sum(vals)}).")
        return None

    for v in vals:
        if v < 0:
            caller.msg("No negative numbers.")
            return None

    # Check max 5 per sub-stat (base 1 + distributed).
    base = 1
    for v in vals:
        if base + v > 5:
            caller.msg(f"No sub-stat can exceed 5 at creation (base 1 + {v} = {base + v}).")
            return None

    if locked:
        caller.msg(
            f"|w{main.title()}|n is locked at 0 for your species — "
            "any points placed there are wasted. Are you sure? Type |wyes|n "
            "to confirm or anything else to re-enter."
        )
        _store(caller, "_pending_dist", {"main": main, "vals": vals})
        options = {"key": "_default", "goto": "_confirm_locked_dist"}
        return "", options

    # Store the values.
    values = _load(caller, "_dist_values", {})
    for i, sub in enumerate(subs):
        values[f"{main}_{sub}"] = 1 + vals[i]
    _store(caller, "_dist_values", values)

    # Advance to next priority.
    idx = _load(caller, "_dist_idx", 0) + 1
    _store(caller, "_dist_idx", idx)
    return "node_stat_dist"


def _confirm_locked_dist(caller, raw_string, **kwargs):
    raw = raw_string.strip().lower()
    pending = _load(caller, "_pending_dist")
    if not pending:
        return "node_stat_dist"

    if raw != "yes":
        caller.msg("Re-enter your distribution.")
        return "node_stat_dist"

    main = pending["main"]
    vals = pending["vals"]
    subs = stats.SUB_STATS

    values = _load(caller, "_dist_values", {})
    for i, sub in enumerate(subs):
        values[f"{main}_{sub}"] = 1 + vals[i]
    _store(caller, "_dist_values", values)

    idx = _load(caller, "_dist_idx", 0) + 1
    _store(caller, "_dist_idx", idx)
    return "node_stat_dist"


# ── review ─────────────────────────────────────────────────────────────


def node_review(caller, raw_string, **kwargs):
    char = _get_char(caller)
    species_key = _load(caller, "species_key", "")
    species_name = _load(caller, "species_name", "")
    gender = _load(caller, "gender", "neuter")
    height = _load(caller, "height", "middling")
    build = _load(caller, "build", "average")
    adjective = _load(caller, "adjective", "")
    skin = _load(caller, "skin", "")
    eyes = _load(caller, "eyes", "")
    eye_color = _load(caller, "eye_color", "")
    hair = _load(caller, "hair", "none")
    hair_color = _load(caller, "hair_color", "none")
    priorities = _load(caller, "stat_priorities", [])
    dist_values = _load(caller, "_dist_values", {})

    lines = [
        "|w═══ Character Review ═══|n\n",
        f"  |wName:|n      {char.key if char else '?'}",
        f"  |wGender:|n    {gender.title()}",
        f"  |wSpecies:|n   {species_name}",
        "",
        "  |wAppearance|n",
        f"    Height:     {height.title()}",
        f"    Build:      {build.title()}",
        f"    Adjective:  {adjective}",
        f"    Skin:       {skin}",
        f"    Eyes:       {eyes} ({eye_color})",
    ]
    if hair == "none":
        lines.append(f"    Hair:       none")
    else:
        lines.append(f"    Hair:       {hair} ({hair_color})")

    lines += [
        "",
        "  |wStat Priorities|n",
    ]
    for i, main in enumerate(priorities):
        pts = [6, 4, 2][i]
        subs = []
        for sub in stats.SUB_STATS:
            val = dist_values.get(f"{main}_{sub}", 1)
            subs.append(f"{sub.title()} {val}")
        locked = species_data.is_locked(species_key, main)
        lock_note = " |x(locked)|n" if locked else ""
        lines.append(
            f"    {i + 1}. {main.title()} ({pts} pts){lock_note}: "
            + ", ".join(subs)
        )

    text = "\n".join(lines)
    options = [
        {"key": "1", "desc": "Confirm — create this character", "goto": "node_finalize"},
        {"key": "2", "desc": "Start over from species", "goto": "node_species"},
    ]
    return text, options


# ── finalize ───────────────────────────────────────────────────────────


def node_finalize(caller, raw_string, **kwargs):
    char = _get_char(caller)
    if not char:
        caller.msg("Something went wrong. Try 'charcreate <name>' again.")
        return None

    # Apply all stored values.
    gender = _load(caller, "gender")
    species_key = _load(caller, "species_key")
    height = _load(caller, "height")
    build = _load(caller, "build")
    adjective = _load(caller, "adjective")
    skin = _load(caller, "skin")
    eyes = _load(caller, "eyes")
    eye_color = _load(caller, "eye_color")
    hair = _load(caller, "hair", "none")
    hair_color = _load(caller, "hair_color", "none")
    priorities = _load(caller, "stat_priorities", [])
    dist_values = _load(caller, "_dist_values", {})

    if gender:
        char.gender = gender
    if species_key:
        char.apply_species(species_key)
    if height:
        char.appearance_height = height
    if build:
        char.appearance_build = build
    if adjective:
        char.appearance_adjective = adjective
    if skin:
        char.appearance_skin = skin
    if eyes:
        char.appearance_eyes = eyes
    if eye_color:
        char.appearance_eye_color = eye_color
    if hair:
        char.appearance_hair = hair
    if hair_color:
        char.appearance_hair_color = hair_color

    # Set sub-stats.
    for attr, val in dist_values.items():
        setattr(char, attr, val)

    # Store priorities for future progression curves.
    char.db.stat_priorities = priorities

    # Reset pools to derived maximums.
    char.reset_pools()

    caller.msg(
        f"\n|gYour character |w{char.key}|g is ready!|n\n"
        f"Type |wic {char.key}|n to enter the game."
    )
    return None
