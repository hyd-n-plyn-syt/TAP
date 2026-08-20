from evennia import create_object


def _store(caller, key, value):
    menu = caller.ndb._evmenu
    if menu:
        if not hasattr(menu, "_data"):
            menu._data = {}
        menu._data[key] = value


def _load(caller, key, default=None):
    menu = caller.ndb._evmenu
    if menu and hasattr(menu, "_data"):
        return menu._data.get(key, default)
    return default


def node_name(caller, raw_string, **kwargs):
    text = "What is the furniture's name? (e.g., brown leather couch):"
    return text, {"key": "_default", "goto": _handle_name}


def _handle_name(caller, raw_string, **kwargs):
    name = raw_string.strip().lower()
    if not name:
        return "node_name"
    _store(caller, "name", name)
    return "node_is_bed"


def node_is_bed(caller, raw_string, **kwargs):
    text = "Is this a bed?"
    options = (
        {"key": ("1", "y", "yes"), "desc": "Yes (Bed)", "goto": "node_bed_type"},
        {"key": ("2", "n", "no"), "desc": "No (Seating/Custom)", "goto": "node_seats"},
    )
    return text, options


def node_bed_type(caller, raw_string, **kwargs):
    text = "What type of bed is this?"
    options = (
        {"key": ("1", "single"), "desc": "Single Bed (1x2 space, 2 seats)", "goto": lambda c, r: _set_bed(c, "1x2", 2)},
        {"key": ("2", "double"), "desc": "Double Bed (2x2 square, 4 seats)", "goto": lambda c, r: _set_bed(c, "2x2", 4)},
    )
    return text, options


def _set_bed(caller, dim, seats):
    _store(caller, "dimension", dim)
    _store(caller, "seats", seats)
    _store(caller, "is_bed", True)
    return "node_occupies_space"


def node_seats(caller, raw_string, **kwargs):
    text = (
        "How many does it seat? (0 for custom dimensions like 1x1, 1x3, etc., or 1, 2, 3):\n"
        "(Max 3 for non-beds)"
    )
    options = (
        {"key": "0", "desc": "Custom Dimensions", "goto": "node_custom_dim"},
        {"key": ("1", "2", "3"), "desc": "1 to 3 seats", "goto": _handle_seats_choice},
    )
    return text, options


def _handle_seats_choice(caller, raw_string, **kwargs):
    val = raw_string.strip()
    if val in ("1", "2", "3"):
        seats = int(val)
        _store(caller, "seats", seats)
        _store(caller, "dimension", f"1x{seats}")
        _store(caller, "is_bed", False)
        return "node_occupies_space"
    return "node_seats"


def node_custom_dim(caller, raw_string, **kwargs):
    text = "Choose custom dimension/shape:"
    options = (
        {"key": "1", "desc": "1x1", "goto": lambda c, r: _set_dim(c, "1x1", 1)},
        {"key": "2", "desc": "1x2", "goto": lambda c, r: _set_dim(c, "1x2", 2)},
        {"key": "3", "desc": "1x3", "goto": lambda c, r: _set_dim(c, "1x3", 3)},
        {"key": "4", "desc": "2x2", "goto": lambda c, r: _set_dim(c, "2x2", 4)},
    )
    return text, options


def _set_dim(caller, dim, seats):
    _store(caller, "dimension", dim)
    _store(caller, "seats", seats)
    _store(caller, "is_bed", False)
    return "node_occupies_space"


def node_occupies_space(caller, raw_string, **kwargs):
    text = (
        "Does this furniture block movement? (y/n)\n"
        "(Yes for solid furniture like sofas and beds that you collide with;\n"
        " No for bedrolls and rugs that you can walk over.)"
    )
    options = (
        {"key": ("y", "yes"), "desc": "Yes (Blocks movement)", "goto": lambda c, r: _set_occupies(c, True)},
        {"key": ("n", "no"), "desc": "No (Walk over)", "goto": lambda c, r: _set_occupies(c, False)},
    )
    return text, options


def _set_occupies(caller, val):
    _store(caller, "occupies_space", val)
    return "node_states"


def node_states(caller, raw_string, **kwargs):
    text = (
        "What states can you do here? Choose from: sit, rest, lay, sleep\n"
        "(Enter comma-separated states, e.g. 'sit, rest', or press enter for default):"
    )
    return text, {"key": "_default", "goto": _handle_states}


def _handle_states(caller, raw_string, **kwargs):
    val = raw_string.strip().lower()
    if not val:
        states = ["sit", "rest", "lay", "sleep", "resting", "laying", "sleeping"]
    else:
        states = [s.strip() for s in val.split(",") if s.strip()]
    _store(caller, "allowed_states", states)
    return "node_color"


def node_color(caller, raw_string, **kwargs):
    text = (
        "Does it have a special color?\n"
        "Enter any ANSI/Truecolor code (e.g. |r or #ff0000).\n"
        "Type 'color ansi', 'color truecolor', or 'color xterm256' to view color tables.\n"
        "Press Enter to use default dark gray (|D):"
    )
    return text, {"key": "_default", "goto": _handle_color}


def _handle_color(caller, raw_string, **kwargs):
    val = raw_string.strip()
    if not val:
        _store(caller, "color", "|D")
        return "node_quality"

    if val.lower().startswith("color"):
        from evennia.commands.default.account import CmdColorTest
        cmd = CmdColorTest()
        cmd.caller = caller
        sessions = caller.sessions.all()
        if sessions:
            cmd.session = sessions[0]
        cmd.args = val[5:].strip()
        try:
            cmd.func()
        except Exception:
            pass
        return "node_color"

    if val.startswith("|") or val.startswith("#") or len(val) <= 10:
        _store(caller, "color", val)
        return "node_quality"

    caller.msg("Invalid color format. Please enter an ANSI code (e.g. |r) or Truecolor hex (e.g. #ff0000), or type 'color ansi' / 'color truecolor' to view options.")
    return "node_color"


def node_quality(caller, raw_string, **kwargs):
    text = "What is its quality rating? (0.1 to 3.0, representing 10%–300% increased overall regen):"
    return text, {"key": "_default", "goto": _handle_quality}


def _handle_quality(caller, raw_string, **kwargs):
    try:
        val = float(raw_string.strip())
        val = max(0.1, min(3.0, val))
    except ValueError:
        caller.msg("Invalid number. Please enter a value between 0.1 and 3.0.")
        return "node_quality"

    _store(caller, "quality", val)
    return "node_create"


def node_create(caller, raw_string, **kwargs):
    name = _load(caller, "name", "furniture")
    dim = _load(caller, "dimension", "1x1")
    seats = _load(caller, "seats", 1)
    occupies = _load(caller, "occupies_space", True)
    states = _load(caller, "allowed_states", ["sit", "rest", "lay", "sleep", "resting", "laying", "sleeping"])
    color = _load(caller, "color", "|D")
    quality = _load(caller, "quality", 1.0)

    typeclass = (
        "typeclasses.furniture.Bed"
        if _load(caller, "is_bed", False)
        else "typeclasses.furniture.Furniture"
    )
    furn = create_object(
        typeclass,
        key=name,
        location=caller,
    )
    furn.dimension = dim
    furn.seats = seats
    furn.occupies_space = occupies
    furn.allowed_states = states
    furn.color = color
    furn.quality = quality
    furn.calculate_footprint()

    caller.msg(f"|gCreated |w{name}|g and placed it in your inventory.|n")
    return None
