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
        chars = caller.account.characters.all()
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


def _options_list(items, handler):
    """Build numbered option dicts that route directly to *handler* with the resolved value."""
    return [
        {"key": str(i + 1), "desc": item, "goto": (handler, {"value": item})}
        for i, item in enumerate(items)
    ]


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
        {"key": "1", "desc": "Male", "goto": (set_gender, {"gender": "male"})},
        {"key": "2", "desc": "Female", "goto": (set_gender, {"gender": "female"})},
        {"key": "3", "desc": "Neuter", "goto": (set_gender, {"gender": "neuter"})},
    ]
    return text, options


def set_gender(caller, raw_string, **kwargs):
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
    options = _options_list(items, set_species)
    return text, options


def set_species(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_height)
    return text, options


def set_height(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_build)
    return text, options


def set_build(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_adjective)
    return text, options


def set_adjective(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_skin)
    return text, options


def set_skin(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_eyes)
    return text, options


def set_eyes(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_eye_color)
    return text, options


def set_eye_color(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_hair)
    return text, options


def set_hair(caller, raw_string, **kwargs):
    value = kwargs["value"]

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
    options = _options_list(items, set_hair_color)
    return text, options


def set_hair_color(caller, raw_string, **kwargs):
    value = kwargs["value"]

    char = _get_char(caller)
    if char:
        char.appearance_hair_color = value.lower()
    _store(caller, "hair_color", value.lower())
    return "node_stat_priority"


# ── stat priority ──────────────────────────────────────────────────────


def _unlocked_stats(species_key):
    """Return the list of main stats not locked for this species."""
    return [m for m in stats.MAIN_STATS if not species_data.is_locked(species_key, m)]


def _points_for_count(count):
    """Return the points-per-priority list for a given number of priorities."""
    if count == 2:
        return [10, 7]
    return [9, 7, 5]


def node_stat_priority(caller, raw_string, **kwargs):
    species_key = _load(caller, "species_key", "")
    unlocked = _unlocked_stats(species_key)
    count = len(unlocked)
    points = _points_for_count(count)

    if count == 3:
        text = (
            "|wStep 11 — Stat Priorities|n\n\n"
            "Arrange the three main attributes in order of importance. "
            f"The |wfirst|n you choose gets |w{points[0]} points|n to distribute among "
            f"its sub-stats, the |wsecond|n gets |w{points[1]} points|n, and the "
            f"|wthird|n gets |w{points[2]} points|n.\n\n"
            "Each sub-stat starts at 1 and can go up to 5 at creation.\n\n"
            "Type the three stats in your preferred order, e.g. |wCorpus Genius Animus|n."
        )
    else:
        locked = [m for m in stats.MAIN_STATS if species_data.is_locked(species_key, m)]
        text = (
            "|wStep 11 — Stat Priorities|n\n\n"
            f"Your species has |x{', '.join(l.title() for l in locked)}|n locked at 0, "
            f"leaving |w{count} unlocked stats|n to arrange.\n\n"
            f"The |wfirst|n you choose gets |w{points[0]} points|n, "
            f"the |wsecond|n gets |w{points[1]} points|n.\n\n"
            "Each sub-stat starts at 1 and can go up to 5 at creation.\n\n"
            f"Type the {count} stats in your preferred order, e.g. |w{' '.join(s.title() for s in unlocked)}|n."
        )

    options = {"key": "_default", "goto": (parse_priority, {"unlocked": unlocked, "count": count})}
    return text, options


def parse_priority(caller, raw_string, **kwargs):
    unlocked = kwargs.get("unlocked", stats.MAIN_STATS)
    count = kwargs.get("count", 3)
    parts = raw_string.strip().lower().split()
    if len(parts) != count:
        caller.msg(f"Enter exactly {count} stat name{'s' if count > 1 else ''} in order.")
        return None

    valid = []
    for p in parts:
        if p not in stats.MAIN_STATS:
            caller.msg(f"Unknown stat '{p}'. Use Corpus, Genius, or Animus.")
            return None
        if p not in unlocked:
            caller.msg(f"{p.title()} is locked for your species.")
            return None
        if p in valid:
            caller.msg(f"You already chose {p.title()}.")
            return None
        valid.append(p)

    points = _points_for_count(count)
    _store(caller, "stat_priorities", valid)
    _store(caller, "_dist_points", points)
    _store(caller, "_dist_idx", 0)
    _store(caller, "_dist_values", {})
    return "node_stat_dist"


# ── stat distribution (shared node, loops per priority count) ──────────


def node_stat_dist(caller, raw_string, **kwargs):
    idx = _load(caller, "_dist_idx", 0)
    priorities = _load(caller, "stat_priorities", [])
    points_list = _load(caller, "_dist_points", [9, 7, 5])
    values = _load(caller, "_dist_values", {})
    species_key = _load(caller, "species_key", "")

    if idx >= len(priorities):
        return "", {"key": "_default", "goto": "node_review"}

    main = priorities[idx]
    points = points_list[idx]
    subs = stats.SUB_STATS

    sub_labels = {
        "potestas": "Power — raw output",
        "reflexus": "Speed — agility and recovery",
        "obsistis": "Resist — toughness and endurance",
    }
    locked = species_data.is_locked(species_key, main)
    lines = []
    for sub in subs:
        label = f"  {main.title()} {sub.title():10s} — {sub_labels[sub]}"
        if locked:
            label += " |x(LOCKED)|n"
        lines.append(label)

    text = (
        f"|wStep {12 + idx} — Distribute {points} points: {main.title()}|n\n\n"
        "Distribute your points across the three sub-stats. "
        f"Each starts at 1. Enter three numbers that sum to {points}, "
        f"e.g. |w3 3 3|n or |w5 3 1|n.\n\n"
        + "\n".join(lines)
    )

    options = {"key": "_default", "goto": (parse_dist, {"main": main, "points": points, "locked": locked})}
    return text, options


def parse_dist(caller, raw_string, **kwargs):
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

    for v in vals:
        if v > 5:
            caller.msg(f"No sub-stat can exceed 5 at creation (you entered {v}).")
            return None

    if locked:
        _store(caller, "_pending_dist", {"main": main, "vals": vals})
        return "node_locked_confirm"

    values = _load(caller, "_dist_values", {})
    for i, sub in enumerate(subs):
        values[f"{main}_{sub}"] = vals[i]
    _store(caller, "_dist_values", values)

    idx = _load(caller, "_dist_idx", 0) + 1
    _store(caller, "_dist_idx", idx)
    priorities = _load(caller, "stat_priorities", [])
    if idx >= len(priorities):
        return "node_review"
    return "node_stat_dist"


# ── locked stat confirmation ──────────────────────────────────────────


def node_locked_confirm(caller, raw_string, **kwargs):
    pending = _load(caller, "_pending_dist")
    main = pending["main"] if pending else "???"
    text = (
        f"|w{main.title()}|n is locked at 0 for your species — "
        "any points placed there are wasted. Are you sure?"
    )
    options = [
        {"key": "1", "desc": "Yes, I understand", "goto": confirm_locked_dist},
        {"key": "2", "desc": "No, let me re-enter", "goto": "node_stat_dist"},
    ]
    return text, options


def confirm_locked_dist(caller, raw_string, **kwargs):
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
        values[f"{main}_{sub}"] = vals[i]
    _store(caller, "_dist_values", values)

    idx = _load(caller, "_dist_idx", 0) + 1
    _store(caller, "_dist_idx", idx)
    priorities = _load(caller, "stat_priorities", [])
    if idx >= len(priorities):
        return "node_review"
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
    points_list = _load(caller, "_dist_points", [9, 7, 5])
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
        pts = points_list[i]
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

    # Set sub-stats via Evennia attribute API for persistence.
    for attr, val in dist_values.items():
        char.attributes.add(attr, val, category="stat")

    # Store priorities for future progression curves.
    char.db.stat_priorities = priorities

    # Reset pools to derived maximums.
    char.reset_pools()

    caller.msg(
        f"\n|gYour character |w{char.key}|g is ready!|n\n"
        f"Type |wic {char.key}|n to enter the game."
    )
    return None
