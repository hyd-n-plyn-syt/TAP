"""
Interactive build menu for creating rooms and exits.

Launched by CmdDigMenu.  Walks the builder through room name,
direction, return exit, door/lock/hidden/breakable options before
creating everything in one shot.

Coordinate logic mirrors commands/building/dig.py.
"""

from evennia import Command, create_object
from evennia.utils.evmenu import EvMenu

# ── helpers ────────────────────────────────────────────────────────────


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


def _title_words(text):
    return text.strip().title()


def _check_exit_collision(room, direction):
    if not room:
        return None
    direction_lower = direction.lower()
    for obj in room.contents:
        if not obj.destination:
            continue
        key_lower = obj.key.lower()
        if key_lower == direction_lower or key_lower.startswith(direction_lower + "-"):
            return obj
        for alias in obj.aliases.all():
            if alias.lower() == direction_lower:
                return obj
    return None


def _calc_target_coords(location, direction, room_name):
    tags = {}
    for cat in ("planetary_body", "planetary_site"):
        tags[cat] = str(location.tags.get(category=cat, return_list=False) or "None")
    for cat in ("planet_x", "planet_y", "planet_z", "site_x", "site_y", "site_z"):
        val = location.tags.get(category=cat, return_list=False)
        tags[cat] = int(val) if val is not None and str(val).lower() != "none" else 0

    data = {
        "body": tags["planetary_body"],
        "site": tags["planetary_site"],
        "px": tags["planet_x"], "py": tags["planet_y"], "pz": tags["planet_z"],
        "sx": tags["site_x"], "sy": tags["site_y"], "sz": tags["site_z"],
    }

    if direction == "in":
        data["site"] = room_name
        data["sx"] = 0
        data["sy"] = 0
        data["sz"] = 0
    elif direction in DIRECTION_MAP:
        info = DIRECTION_MAP[direction]
        if tags["planetary_site"].lower() != "none":
            data["sx"] += info["dx"]
            data["sy"] += info["dy"]
            data["sz"] += info["dz"]
        else:
            data["px"] += info["dx"]
            data["py"] += info["dy"]
            data["pz"] += info["dz"]

    return data


def _find_surface_room(location):
    from evennia.utils.search import search_tag

    body = location.tags.get(category="planetary_body", return_list=False)
    if not body:
        return None
    px = location.tags.get(category="planet_x", return_list=False)
    py = location.tags.get(category="planet_y", return_list=False)
    pz = location.tags.get(category="planet_z", return_list=False)

    candidates = search_tag(tag=str(body), category="planetary_body")
    for c in candidates:
        if c.typeclass_path != "typeclasses.rooms.Room":
            continue
        cb = c.tags.get(category="planetary_body", return_list=False)
        cs = c.tags.get(category="planetary_site", return_list=False)
        cpx = c.tags.get(category="planet_x", return_list=False)
        cpy = c.tags.get(category="planet_y", return_list=False)
        cpz = c.tags.get(category="planet_z", return_list=False)
        if (str(cb).lower() == str(body).lower()
                and str(cs).lower() == "none"
                and str(cpx) == str(px)
                and str(cpy) == str(py)
                and str(cpz) == str(pz)):
            return c
    return None


def _set_exit_attrs(exit_obj, data):
    exit_obj.db.is_door = data.get("is_door", False)
    exit_obj.db.is_open = data.get("is_open", False)
    exit_obj.db.is_locked = data.get("is_locked", False)
    exit_obj.db.lockpick_dc = data.get("lockpick_dc", 0)
    exit_obj.db.is_breakable = data.get("is_breakable", False)
    exit_obj.db.bash_dc = data.get("bash_dc", 0)
    exit_obj.db.is_hidden = data.get("is_hidden", False)
    exit_obj.db.detect_dc = data.get("detect_dc", 0)

    if data.get("is_hidden"):
        exit_obj.locks.add("view:false()")
        exit_obj.locks.add("search:false()")


def _create_key(caller, exit_obj):
    key_name = f"Key to {exit_obj.key}"
    key = create_object(
        "typeclasses.objects.Object",
        key=key_name,
        location=caller,
    )
    key.db.desc = "A simple metal key."
    key.db.exit_id = exit_obj.id
    exit_obj.db.key_id = key.id
    return key


# ── direction data ─────────────────────────────────────────────────────

DIRECTION_MAP = {
    "north":     {"dx": 0,  "dy": 1,  "dz": 0,  "return": "south",     "aliases": ["n"]},
    "south":     {"dx": 0,  "dy": -1, "dz": 0,  "return": "north",     "aliases": ["s"]},
    "east":      {"dx": 1,  "dy": 0,  "dz": 0,  "return": "west",      "aliases": ["e"]},
    "west":      {"dx": -1, "dy": 0,  "dz": 0,  "return": "east",      "aliases": ["w"]},
    "northeast": {"dx": 1,  "dy": 1,  "dz": 0,  "return": "southwest", "aliases": ["ne"]},
    "northwest": {"dx": -1, "dy": 1,  "dz": 0,  "return": "southeast", "aliases": ["nw"]},
    "southeast": {"dx": 1,  "dy": -1, "dz": 0,  "return": "northwest", "aliases": ["se"]},
    "southwest": {"dx": -1, "dy": -1, "dz": 0,  "return": "northeast", "aliases": ["sw"]},
    "up":        {"dx": 0,  "dy": 0,  "dz": 1,  "return": "down",      "aliases": []},
    "down":      {"dx": 0,  "dy": 0,  "dz": -1, "return": "up",        "aliases": []},
    "in":        {"dx": 0,  "dy": 0,  "dz": 0,  "return": "out",       "aliases": ["enter"]},
    "out":       {"dx": 0,  "dy": 0,  "dz": 0,  "return": "in",        "aliases": ["leave"]},
}

RETURN_ALIAS_MAP = {
    "north": ["n"], "south": ["s"], "east": ["e"], "west": ["w"],
    "northeast": ["ne"], "northwest": ["nw"], "southeast": ["se"], "southwest": ["sw"],
    "up": [], "down": [], "in": ["in", "enter"], "out": ["out", "leave"],
}

DIRECTION_LIST = list(DIRECTION_MAP.keys())

YES_NO = {"y": True, "yes": True, "n": False, "no": False}

# ── nodes ──────────────────────────────────────────────────────────────


def node_welcome(caller, raw_string, **kwargs):
    text = (
        "|wBuild Menu|n\n\n"
        "This menu will walk you through creating a new room and exit. "
        "You can type |wquit|n at any time to cancel.\n\n"
        "Press |wEnter|n to begin."
    )
    options = ({"key": "_default", "goto": "node_room_name"},)
    return text, options

# ── room name ──────────────────────────────────────────────────────────

def node_room_name(caller, raw_string, **kwargs):
    text = "|wStep 1 — Room Name|n\n\nWhat is the name of the new room?"
    options = ({"key": "_default", "goto": (parse_room_name, {})},)
    return text, options


def parse_room_name(caller, raw_string, **kwargs):
    name = _title_words(raw_string)
    if not name:
        caller.msg("You must provide a room name.")
        return None
    _store(caller, "room_name", name)
    return "node_indoor"


# ── direction ──────────────────────────────────────────────────────────


def node_direction(caller, raw_string, **kwargs):
    text = "|wStep 2 — Direction|n\n\nWhich direction should the exit lead?"
    options = []
    for i, d in enumerate(DIRECTION_LIST, 1):
        desc = d.title()
        if DIRECTION_MAP[d]["aliases"]:
            desc += f" ({', '.join(DIRECTION_MAP[d]['aliases'])})"
        options.append({"key": str(i), "desc": desc, "goto": (parse_direction, {"direction": d})})
    options.append({"key": "_default", "goto": (parse_direction, {})})
    return text, options


def parse_direction(caller, raw_string, **kwargs):
    direction = kwargs.get("direction", "").strip().lower()
    if not direction:
        try:
            idx = int(raw_string.strip()) - 1
            if 0 <= idx < len(DIRECTION_LIST):
                direction = DIRECTION_LIST[idx]
        except (ValueError, IndexError):
            pass
    if direction not in DIRECTION_MAP:
        caller.msg("Invalid direction. Choose a number from the list.")
        return None
    _store(caller, "direction", direction)
    location = caller.location
    collision = _check_exit_collision(location, direction)
    if collision:
        _store(caller, "collision", collision.key)
    else:
        _store(caller, "collision", None)
    return "node_return"


# ── return exit ────────────────────────────────────────────────────────


def node_return(caller, raw_string, **kwargs):
    direction = _load(caller, "direction")
    collision = _load(caller, "collision")
    text = "|wStep 3 — Return Exit|n\n\n"
    if collision:
        text += (
            f"|yWarning:|n An exit named '|w{collision}|n' already exists "
            f"in that direction. You can still continue.\n\n"
        )
    if direction == "out":
        text += "Make a return exit? |r(Not available for outward transitions)|n"
        options = ({"key": "_default", "goto": "node_door"},)
        return text, options
    text += "Make a return exit? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_return, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_return, {"value": False})},
        {"key": "_default", "goto": (parse_return, {})},
    )
    return text, options


def parse_return(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "has_return", value)
    if value:
        direction = _load(caller, "direction", "north")
        ret_dir = DIRECTION_MAP[direction]["return"]
        _store(caller, "return_name", ret_dir.title())
        _store(caller, "return_aliases", RETURN_ALIAS_MAP.get(ret_dir, []))
        return "node_door"
    return "node_door"


# ── room size prompt ───────────────────────────────────────────────────

def node_room_size_type(caller, raw_string, **kwargs):
    text = (
        "|wStep 1d — Room Size|n\n\n"
        "Select a room size category:\n"
        "1: Tiny\n2: Small\n3: Medium\n4: Large\n5: Huge\n6: Massive\n7: Custom"
    )
    options = (
        {"key": "1", "goto": (parse_room_size_type, {"value": "tiny"})},
        {"key": "2", "goto": (parse_room_size_type, {"value": "small"})},
        {"key": "3", "goto": (parse_room_size_type, {"value": "medium"})},
        {"key": "4", "goto": (parse_room_size_type, {"value": "large"})},
        {"key": "5", "goto": (parse_room_size_type, {"value": "huge"})},
        {"key": "6", "goto": (parse_room_size_type, {"value": "massive"})},
        {"key": "7", "goto": "node_room_size_custom"},
    )
    return text, options

def parse_room_size_type(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    _store(caller, "room_size", value)
    return "node_direction"

def node_room_size_custom(caller, raw_string, **kwargs):
    text = "|wStep 1e — Custom Room Size|n\n\nWidth and Height? (e.g., '10 3')"
    options = ({"key": "_default", "goto": (parse_room_size_custom, {})},)
    return text, options

def parse_room_size_custom(caller, raw_string, **kwargs):
    args = raw_string.split()
    if len(args) == 2:
        try:
            width, height = int(args[0]), int(args[1])
            _store(caller, "room_size", {"width": width, "height": height})
            return "node_direction"
        except ValueError:
            pass
    caller.msg("Provide width and height (e.g., '10 3').")
    return None

# ── indoor ─────────────────────────────────────────────────────────────

def node_indoor(caller, raw_string, **kwargs):
    text = "|wStep 1a — Indoor|n\n\nIs this room indoors? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_indoor, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_indoor, {"value": False})},
        {"key": "_default", "goto": (parse_indoor, {})},
    )
    return text, options

def parse_indoor(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "is_indoor", value)
    if not value:
        _store(caller, "room_height", 4)
        return "node_room_size_type"
    return "node_can_fly"

# ── can fly ────────────────────────────────────────────────────────────

def node_can_fly(caller, raw_string, **kwargs):
    text = "|wStep 1b — Fly|n\n\nCan you fly inside this room? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_can_fly, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_can_fly, {"value": False})},
        {"key": "_default", "goto": (parse_can_fly, {})},
    )
    return text, options

def parse_can_fly(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "can_fly", value)
    if not value:
        _store(caller, "room_height", 1)
        return "node_room_size_type"
    return "node_fly_height"

# ── fly height ─────────────────────────────────────────────────────────

def node_fly_height(caller, raw_string, **kwargs):
    text = (
        "|wStep 1c — Flight Height|n\n\n"
        "How high can you fly in this room?\n"
        "1: Above\n"
        "2: High Above\n"
        "3: Very High Above"
    )
    options = (
        {"key": "1", "desc": "Above", "goto": (parse_fly_height, {"value": 2})},
        {"key": "2", "desc": "High Above", "goto": (parse_fly_height, {"value": 3})},
        {"key": "3", "desc": "Very High Above", "goto": (parse_fly_height, {"value": 4})},
    )
    return text, options

def parse_fly_height(caller, raw_string, **kwargs):
    height = kwargs.get("value")
    _store(caller, "room_height", height)
    return "node_room_size_type"


def node_door(caller, raw_string, **kwargs):
    text = "|wStep 4 — Door|n\n\nIs there a door? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_door, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_door, {"value": False})},
        {"key": "_default", "goto": (parse_door, {})},
    )
    return text, options


def parse_door(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "is_door", value)
    if value:
        return "node_locked"
    return "node_breakable"


# ── locked ─────────────────────────────────────────────────────────────


def node_locked(caller, raw_string, **kwargs):
    text = "|wStep 4a — Locked|n\n\nIs the door locked? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_locked, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_locked, {"value": False})},
        {"key": "_default", "goto": (parse_locked, {})},
    )
    return text, options


def parse_locked(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "is_locked", value)
    if value:
        return "node_lockpick_dc"
    return "node_hidden"


# ── lockpick dc ────────────────────────────────────────────────────────


def node_lockpick_dc(caller, raw_string, **kwargs):
    text = "|wStep 4b — Lock Pick Difficulty|n\n\nLock pick difficulty (0-1000)?"
    options = ({"key": "_default", "goto": (parse_lockpick_dc, {})},)
    return text, options


def parse_lockpick_dc(caller, raw_string, **kwargs):
    try:
        value = int(raw_string.strip())
    except ValueError:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    if not 0 <= value <= 1000:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    _store(caller, "lockpick_dc", value)
    return "node_inside_key"


# ── inside key (locked door only) ──────────────────────────────────────


def node_inside_key(caller, raw_string, **kwargs):
    has_return = _load(caller, "has_return", False)
    if not has_return:
        _store(caller, "inside_key", False)
        return "node_can_bash"
    text = "|wStep 4b — Inside Key|n\n\nDoes the return exit also require a key? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_inside_key, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_inside_key, {"value": False})},
        {"key": "_default", "goto": (parse_inside_key, {})},
    )
    return text, options


def parse_inside_key(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "inside_key", value)
    return "node_can_bash"


# ── can bash (locked door only) ────────────────────────────────────────


def node_can_bash(caller, raw_string, **kwargs):
    text = "|wStep 4c — Bash Option|n\n\nCan the door also be bashed? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_can_bash, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_can_bash, {"value": False})},
        {"key": "_default", "goto": (parse_can_bash, {})},
    )
    return text, options


def parse_can_bash(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "can_bash_door", value)
    if value:
        return "node_bash_dc"
    return "node_hidden"


# ── bash dc (shared between door and wall) ─────────────────────────────


def node_bash_dc(caller, raw_string, **kwargs):
    from_door = _load(caller, "is_door", False)
    if from_door:
        text = "|wStep 4d — Bash Difficulty|n\n\nBash difficulty for the door (0-1000)?"
    else:
        text = "|wStep 4b — Bash Difficulty|n\n\nBreak difficulty for the wall (0-1000)?"
    options = ({"key": "_default", "goto": (parse_bash_dc, {})},)
    return text, options


def parse_bash_dc(caller, raw_string, **kwargs):
    try:
        value = int(raw_string.strip())
    except ValueError:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    if not 0 <= value <= 1000:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    _store(caller, "bash_dc", value)
    return "node_hidden"


# ── breakable wall (non-door only) ────────────────────────────────────


def node_breakable(caller, raw_string, **kwargs):
    text = "|wStep 4b — Breakable Wall|n\n\nIs there a breakable wall here? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_breakable, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_breakable, {"value": False})},
        {"key": "_default", "goto": (parse_breakable, {})},
    )
    return text, options


def parse_breakable(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "is_breakable", value)
    if value:
        return "node_bash_dc"
    return "node_hidden"


# ── hidden ─────────────────────────────────────────────────────────────


def node_hidden(caller, raw_string, **kwargs):
    text = "|wStep 5 — Hidden|n\n\nIs this exit hidden? (y/n)"
    options = (
        {"key": "y", "desc": "Yes", "goto": (parse_hidden, {"value": True})},
        {"key": "n", "desc": "No", "goto": (parse_hidden, {"value": False})},
        {"key": "_default", "goto": (parse_hidden, {})},
    )
    return text, options


def parse_hidden(caller, raw_string, **kwargs):
    value = kwargs.get("value")
    if value is None:
        answer = raw_string.strip().lower()
        if answer not in YES_NO:
            caller.msg("Please enter y or n.")
            return None
        value = YES_NO[answer]
    _store(caller, "is_hidden", value)
    if value:
        return "node_detect_dc"
    return "node_review"


# ── detect dc ──────────────────────────────────────────────────────────


def node_detect_dc(caller, raw_string, **kwargs):
    text = "|wStep 5a — Detection Difficulty|n\n\nDetection difficulty for Awareness (0-1000)?"
    options = ({"key": "_default", "goto": (parse_detect_dc, {})},)
    return text, options


def parse_detect_dc(caller, raw_string, **kwargs):
    try:
        value = int(raw_string.strip())
    except ValueError:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    if not 0 <= value <= 1000:
        caller.msg("Please enter a number between 0 and 1000.")
        return None
    _store(caller, "detect_dc", value)
    return "node_review"


# ── review ─────────────────────────────────────────────────────────────


def node_review(caller, raw_string, **kwargs):
    room_name = _load(caller, "room_name", "???")
    direction = _load(caller, "direction", "???")
    has_return = _load(caller, "has_return", False)
    return_name = _load(caller, "return_name", "")
    is_door = _load(caller, "is_door", False)
    is_locked = _load(caller, "is_locked", False)
    lockpick_dc = _load(caller, "lockpick_dc", 0)
    is_breakable = _load(caller, "is_breakable", False)
    bash_dc = _load(caller, "bash_dc", 0)
    is_hidden = _load(caller, "is_hidden", False)
    detect_dc = _load(caller, "detect_dc", 0)
    collision = _load(caller, "collision", None)

    text = "|wBuild Summary|n\n\n"
    text += f"  Room:         |w{room_name}|n\n"
    text += f"  Direction:    |w{direction.title()}|n\n"

    if has_return:
        text += f"  Return exit:  |w{return_name}|n\n"
    elif direction != "out":
        text += "  Return exit:  |wn|n\n"
    else:
        text += "  Return exit:  |rN/A (outward)|n\n"

    text += f"  Door:         {'|wy|n' if is_door else '|wn|n'}\n"
    if is_door:
        text += f"  Locked:       {'|wy|n' if is_locked else '|wn|n'}\n"
        if is_locked:
            text += f"  Lock pick DC: |w{lockpick_dc}|n\n"
            if has_return:
                inside_key = _load(caller, "inside_key", False)
                text += f"  Inside key:   {'|wy|n' if inside_key else '|wn|n'}\n"
            can_bash = _load(caller, "can_bash_door", False)
            text += f"  Can bash:     {'|wy|n' if can_bash else '|wn|n'}\n"
            if can_bash:
                text += f"  Bash DC:      |w{bash_dc}|n\n"
    else:
        text += f"  Breakable:    {'|wy|n' if is_breakable else '|wn|n'}\n"
        if is_breakable:
            text += f"  Bash DC:      |w{bash_dc}|n\n"

    text += f"  Hidden:       {'|wy|n' if is_hidden else '|wn|n'}\n"
    if is_hidden:
        text += f"  Detect DC:    |w{detect_dc}|n\n"

    if collision:
        text += f"\n  |rCannot build:|n An exit '|w{collision}|n' already exists in that direction.\n"

    if collision:
        options = (
            {"key": "1", "desc": "Go Back", "goto": "node_direction"},
            {"key": "_quit", "desc": "Quit", "goto": "node_quit"},
        )
    else:
        options = (
            {"key": "1", "desc": "Confirm", "goto": "node_finalize"},
            {"key": "2", "desc": "Start Over", "goto": "node_welcome"},
            {"key": "_quit", "desc": "Quit", "goto": "node_quit"},
        )
    return text, options


def node_quit(caller, raw_string, **kwargs):
    caller.msg("|yBuild cancelled.|n")
    return None


# ── finalize ───────────────────────────────────────────────────────────


def node_finalize(caller, raw_string, **kwargs):
    location = caller.location
    if not location:
        caller.msg("|rYou have no location.|n")
        return None

    room_name = _load(caller, "room_name", "???")
    direction = _load(caller, "direction")
    has_return = _load(caller, "has_return", False)
    return_name = _load(caller, "return_name", "")
    return_aliases = _load(caller, "return_aliases", [])
    is_door = _load(caller, "is_door", False)
    is_locked = _load(caller, "is_locked", False)
    lockpick_dc = _load(caller, "lockpick_dc", 0)
    can_bash_door = _load(caller, "can_bash_door", False)
    is_breakable = _load(caller, "is_breakable", False)
    bash_dc = _load(caller, "bash_dc", 0)
    is_hidden = _load(caller, "is_hidden", False)
    detect_dc = _load(caller, "detect_dc", 0)
    inside_key = _load(caller, "inside_key", False)

    fwd_exit_attrs = {
        "is_door": is_door, "is_open": False, "is_locked": is_locked, "lockpick_dc": lockpick_dc,
        "is_breakable": is_breakable, "bash_dc": bash_dc,
        "is_hidden": is_hidden, "detect_dc": detect_dc,
    }
    ret_exit_attrs = {
        "is_door": is_door, "is_open": False,
        "is_locked": inside_key if is_locked else False,
        "lockpick_dc": lockpick_dc,
        "is_breakable": is_breakable, "bash_dc": bash_dc,
        "is_hidden": is_hidden, "detect_dc": detect_dc,
    }

    fwd_name = direction.title()
    fwd_aliases = DIRECTION_MAP[direction]["aliases"]

    lines = []

    if direction == "out":
        surface = _find_surface_room(location)
        if not surface:
            caller.msg("|rCould not find a surface room at the current coordinates.|n")
            return None
        fwd_exit = create_object(
            "typeclasses.exits.Exit", key=fwd_name, aliases=fwd_aliases,
            location=location, destination=surface,
        )
        _set_exit_attrs(fwd_exit, fwd_exit_attrs)
        if is_locked:
            _create_key(caller, fwd_exit)
        lines.append(f"|gExit:|n {fwd_exit.name} (#{fwd_exit.id}) -> {surface.name}")
        if is_locked:
            lines.append(f"|gKey:|n Key to {fwd_exit.name} placed in your inventory.")
    else:
        coords = _calc_target_coords(location, direction, room_name)
        new_room = create_object(
            "typeclasses.rooms.Room", key=room_name,
        )
        for cat, val in [
            ("planetary_body", coords["body"]),
            ("planetary_site", coords["site"]),
            ("planet_x", str(coords["px"])),
            ("planet_y", str(coords["py"])),
            ("planet_z", str(coords["pz"])),
            ("site_x", str(coords["sx"])),
            ("site_y", str(coords["sy"])),
            ("site_z", str(coords["sz"])),
        ]:
            new_room.tags.clear(category=cat)
            new_room.tags.add(val, category=cat)
        
        room_height = _load(caller, "room_height", 1)
        new_room.db.room_height = room_height
        
        room_size = _load(caller, "room_size", "medium")
        if isinstance(room_size, dict):
            new_room.db.room_size = room_size
            lines.append(f"  Height ({room_height}) Size ({room_size['width']}x{room_size['height']})")
        else:
            new_room.db.room_size = room_size
            lines.append(f"  Height ({room_height}) Size ({room_size})")

        fwd_exit = create_object(
            "typeclasses.exits.Exit", key=fwd_name, aliases=fwd_aliases,
            location=location, destination=new_room,
        )
        _set_exit_attrs(fwd_exit, fwd_exit_attrs)
        lines.append(f"|gForward:|n {fwd_exit.name} (#{fwd_exit.id}) -> {new_room.name}")

        if has_return:
            ret_exit = create_object(
                "typeclasses.exits.Exit", key=return_name, aliases=return_aliases,
                location=new_room, destination=location,
            )
            _set_exit_attrs(ret_exit, ret_exit_attrs)
            lines.append(f"|gReturn:|n {ret_exit.name} (#{ret_exit.id}) -> {location.name}")

            if is_door:
                fwd_exit.db.sibling_id = ret_exit.id
                ret_exit.db.sibling_id = fwd_exit.id

        if is_locked:
            key = _create_key(caller, fwd_exit)
            if has_return and inside_key:
                ret_exit.db.key_id = key.id
            lines.append(f"|gKey:|n Key to {fwd_exit.name} placed in your inventory.")

    text = "|g[BUILD COMPLETE]|n\n\n" + "\n".join(lines)
    return text


# ── command ────────────────────────────────────────────────────────────


class CmdDigMenu(Command):
    """
    Interactive build menu for rooms and exits.

    Usage:
      digmenu
      digm

    Opens a guided menu that walks you through creating a room,
    exit, return exit, door/lock, breakable wall, and hidden
    exit options.
    """
    key = "digmenu"
    aliases = ["digm"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        if not self.caller.location:
            self.msg("You have no location to dig from.")
            return
        EvMenu(
            self.caller,
            "commands.building.dig_menu",
            startnode="node_welcome",
            session=self.session,
        )
