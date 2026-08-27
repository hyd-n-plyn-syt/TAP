"""
Wisp customization EvMenu.

Caller is the puppeted wisp OR the account (we support both). We resolve
the wisp object via helpers and write attributes directly onto it.
Flow: welcome → gender → color → adjective → size → review → finalize
"""

from evennia.utils.ansi import strip_ansi
from world.data import appearance
from world.data.colors import WISP_LIGHTS, hex_for_color


def _resolve_wisp(caller):
    """Return the wisp object for caller (account or wisp)."""
    # If caller is already a wisp
    if getattr(caller, "is_wisp", False):
        return caller
    # Try to get wisp via helpers
    try:
        from world.systems.wisp import get_wisp, get_or_create_wisp
        w = get_wisp(caller)
        if w:
            return w
        # If caller is Character, try its account
        acct = getattr(caller, "account", None)
        if acct:
            w2 = get_wisp(acct)
            if w2:
                return w2
            return get_or_create_wisp(acct)
    except Exception:
        pass
    # Fallback: caller itself if it looks like wisp
    try:
        if getattr(caller.db, "species_key", None) == "wisp":
            return caller
    except Exception:
        pass
    return caller


def _store(caller, key, value):
    menu = getattr(caller.ndb, "_evmenu", None)
    if menu is not None:
        if not hasattr(menu, "_data"):
            menu._data = {}
        menu._data[key] = value


def _load(caller, key, default=None):
    menu = getattr(caller.ndb, "_evmenu", None)
    if menu and hasattr(menu, "_data"):
        return menu._data.get(key, default)
    return default


def _options_list(items, handler):
    return [
        {"key": str(i + 1), "desc": item, "goto": (handler, {"value": item})}
        for i, item in enumerate(items)
    ]


# ── welcome ──────────────────────────────────────────────────────────

def node_welcome(caller, raw_string, **kwargs):
    wisp = _resolve_wisp(caller)
    name = getattr(wisp, "key", getattr(caller, "key", "wisp"))
    text = (
        f"|wWelcome, {name}.|n\n\n"
        "Your wisp is your OOC self — a ball of light that lives only in the "
        "OOC lounge (Limbo #2). It has no stats. We will set its gender, light "
        "color, adjective, and size.\n\n"
        "|xPress Enter to continue...|n"
    )
    options = ({"key": "_default", "goto": "node_gender"},)
    return text, options


# ── gender ───────────────────────────────────────────────────────────

def node_gender(caller, raw_string, **kwargs):
    text = "|wStep 1 — Gender|n\n\nWhat is your wisp's gender?"
    options = [
        {"key": "1", "desc": "Male", "goto": (set_gender, {"gender": "male"})},
        {"key": "2", "desc": "Female", "goto": (set_gender, {"gender": "female"})},
        {"key": "3", "desc": "Neuter", "goto": (set_gender, {"gender": "neuter"})},
    ]
    return text, options


def set_gender(caller, raw_string, **kwargs):
    gender = kwargs["gender"]
    wisp = _resolve_wisp(caller)
    try:
        wisp.db.gender = gender
        wisp.gender = gender
    except Exception:
        pass
    _store(caller, "gender", gender)
    return "node_color"


# ── color (light) ────────────────────────────────────────────────────

def node_color(caller, raw_string, **kwargs):
    text = "|wStep 2 — Light Color|n\n\nChoose the color of your wisp's light."
    items = []
    for key in WISP_LIGHTS:
        h = hex_for_color(key)
        if h:
            items.append(f"|{h}{key}|n")
        else:
            items.append(key)
    options = _options_list(items, set_color)
    return text, options


def set_color(caller, raw_string, **kwargs):
    value = strip_ansi(kwargs["value"]).strip().lower()
    wisp = _resolve_wisp(caller)
    try:
        wisp.appearance_skin = value
        wisp.db.appearance_skin = value
    except Exception:
        try:
            wisp.attributes.add("appearance_skin", value)
        except Exception:
            pass
    _store(caller, "color", value)
    return "node_adjective"


# ── adjective ────────────────────────────────────────────────────────

def node_adjective(caller, raw_string, **kwargs):
    text = "|wStep 3 — Adjective|n\n\nChoose a descriptor for your wisp's light."
    adjs = appearance.adjectives_for_species("wisp")
    items = list(adjs)
    options = _options_list(items, set_adjective)
    return text, options


def set_adjective(caller, raw_string, **kwargs):
    value = kwargs["value"].lower()
    wisp = _resolve_wisp(caller)
    try:
        wisp.appearance_adjective = value
        wisp.db.appearance_adjective = value
    except Exception:
        try:
            wisp.attributes.add("appearance_adjective", value)
        except Exception:
            pass
    _store(caller, "adjective", value)
    return "node_size"


# ── size ─────────────────────────────────────────────────────────────

def node_size(caller, raw_string, **kwargs):
    text = "|wStep 4 — Size|n\n\nChoose your wisp's size. Same scale as a person — not tiny."
    items = []
    for s in appearance.WISP_SIZES:
        desc = appearance.WISP_SIZE_DESCRIPTIONS.get(s, "")
        items.append(f"{s.title()}: {desc}")
    options = _options_list(items, set_size)
    return text, options


def set_size(caller, raw_string, **kwargs):
    value = kwargs["value"]
    size = value.split(":")[0].strip().lower()
    wisp = _resolve_wisp(caller)
    try:
        wisp.db.appearance_size = size
        wisp.appearance_size = size
        # Also mirror to appearance_height for any legacy code expecting height
        wisp.attributes.add("appearance_size", size)
    except Exception:
        pass
    _store(caller, "size", size)
    return "node_review"


# ── review ───────────────────────────────────────────────────────────

def node_review(caller, raw_string, **kwargs):
    wisp = _resolve_wisp(caller)
    gender = _load(caller, "gender", getattr(wisp.db, "gender", "neuter"))
    color = _load(caller, "color", getattr(wisp.db, "appearance_skin", "white-light"))
    adjective = _load(caller, "adjective", getattr(wisp.db, "appearance_adjective", "soft"))
    size = _load(caller, "size", getattr(wisp.db, "appearance_size", appearance.DEFAULT_WISP_SIZE))

    h = hex_for_color(color) or ""
    color_tag = f"|{h}{color}|n" if h else color

    lines = [
        "|w═══ Wisp Review ═══|n\n",
        f"  |wGender:|n    {gender.title()}",
        f"  |wColor:|n     {color_tag}",
        f"  |wAdjective:|n {adjective}",
        f"  |wSize:|n      {size.title()}",
        "",
        f"  {wisp.key} — a {size} {adjective} wisp of {color} light.",
    ]
    text = "\n".join(lines)
    options = [
        {"key": "1", "desc": "Confirm", "goto": "node_finalize"},
        {"key": "2", "desc": "Start over", "goto": "node_gender"},
    ]
    return text, options


def node_finalize(caller, raw_string, **kwargs):
    wisp = _resolve_wisp(caller)
    gender = _load(caller, "gender")
    color = _load(caller, "color")
    adjective = _load(caller, "adjective")
    size = _load(caller, "size")

    if gender:
        try:
            wisp.db.gender = gender
            wisp.gender = gender
        except Exception:
            pass
    if color:
        try:
            wisp.appearance_skin = color
            wisp.db.appearance_skin = color
            wisp.attributes.add("appearance_skin", color)
        except Exception:
            pass
        # Also mirror to colors for skin_hex
        try:
            from world.data.appearance import SKIN_TONES
            # Ensure hex lookup works (already added light hexes to SKIN_TONES)
            pass
        except Exception:
            pass
    if adjective:
        try:
            wisp.appearance_adjective = adjective
            wisp.db.appearance_adjective = adjective
        except Exception:
            pass
    if size:
        try:
            wisp.db.appearance_size = size
            wisp.appearance_size = size
            wisp.attributes.add("appearance_size", size)
        except Exception:
            pass

    # Ensure pose is hovering
    try:
        wisp.pose = "hovering"
        wisp.db.pose = "hovering"
    except Exception:
        pass

    # Ensure wisp is still flagged correctly
    try:
        wisp.species_key = "wisp"
        wisp.db.visarial_nature = "dual_natured"
        wisp.tags.add("wisp", category="account")
        wisp.tags.add("ooc_wisp", category="account")
    except Exception:
        pass

    caller.msg("\n|gYour wisp is ready!|n\n")
    try:
        # Show look
        sess = None
        try:
            sess = caller.sessions.all()[0] if hasattr(caller, "sessions") else None
            if not sess and hasattr(caller, "account"):
                sess = caller.account.sessions.all()[0] if caller.account else None
        except Exception:
            pass
        # If caller is account, need to show via wisp
        if hasattr(caller, "puppet_object"):
            # caller is account
            pass
        # Execute look on wisp
        wisp.execute_cmd("look", session=sess)
    except Exception:
        pass
    return None
