from evennia import create_object
from evennia.utils.utils import iter_to_str
from world.data import items as items_data
from world.data import colors as colors_data
from world.data import appearance as appearance_data


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


def node_item_type(caller, raw_string, **kwargs):
    text = (
        "What type of item is it?\n\n"
        "|w1|n. Furniture"
    )
    options = [
        {"key": ("1", "furniture"), "desc": "Furniture", "goto": lambda c, r: _set_item_type(c, "furniture")},
    ]
    return text, options


def _set_item_type(caller, itype):
    _store(caller, "item_type", itype)
    return "node_base_name"


def node_base_name(caller, raw_string, **kwargs):
    text = "What is its base name? (e.g., bed, sword, shield):"
    return text, {"key": "_default", "goto": _handle_base_name}


def _handle_base_name(caller, raw_string, **kwargs):
    name = raw_string.strip().lower()
    if not name:
        return "node_base_name"
    _store(caller, "base_name", name)
    return "node_mat_1"


def node_mat_1(caller, raw_string, **kwargs):
    itype_key = _load(caller, "item_type", "furniture")
    itype = items_data.get_item_type(itype_key)
    mats = itype["materials"]

    text = "Choose Material 1:\n\n"
    options = []
    for idx, mat_key in enumerate(mats, 1):
        mat_info = items_data.get_material(mat_key)
        options.append({
            "key": str(idx),
            "desc": mat_info["name"],
            "goto": lambda c, r, mk=mat_key: _set_mat_1(c, mk),
        })
    return text, options


def _set_mat_1(caller, mat_key):
    _store(caller, "mat_1", mat_key)
    return "node_col_1"


def node_col_1(caller, raw_string, **kwargs):
    mat_key = _load(caller, "mat_1")
    mat_info = items_data.get_material(mat_key)
    colors = mat_info["colors"]

    text = f"Choose color for {mat_info['name']} (Material 1):\n\n"
    options = []
    for idx, col in enumerate(colors, 1):
        h = colors_data.hex_for_color(col)
        display_col = f"|{h}{col}|n" if h else col
        options.append({
            "key": str(idx),
            "desc": display_col,
            "goto": lambda c, r, cl=col: _set_col_1(c, cl),
        })
    return text, options


def _set_col_1(caller, col):
    mat_key = _load(caller, "mat_1")
    materials = [[mat_key, col]]
    _store(caller, "materials", materials)
    return "node_another_mat"


def node_another_mat(caller, raw_string, **kwargs):
    text = "Would you like to add a second material? (y/n)"
    options = [
        {"key": ("y", "yes"), "desc": "Yes", "goto": "node_mat_2"},
        {"key": ("n", "no"), "desc": "No", "goto": "node_adjective"},
    ]
    return text, options


def node_mat_2(caller, raw_string, **kwargs):
    itype_key = _load(caller, "item_type", "furniture")
    itype = items_data.get_item_type(itype_key)
    mats = itype["materials"]
    existing_mat = _load(caller, "mat_1")
    available_mats = [m for m in mats if m != existing_mat]

    text = "Choose Material 2:\n\n"
    options = []
    for idx, mat_key in enumerate(available_mats, 1):
        mat_info = items_data.get_material(mat_key)
        options.append({
            "key": str(idx),
            "desc": mat_info["name"],
            "goto": lambda c, r, mk=mat_key: _set_mat_2(c, mk),
        })
    return text, options


def _set_mat_2(caller, mat_key):
    _store(caller, "mat_2", mat_key)
    return "node_col_2"


def node_col_2(caller, raw_string, **kwargs):
    mat_key = _load(caller, "mat_2")
    mat_info = items_data.get_material(mat_key)
    colors = mat_info["colors"]

    text = f"Choose color for {mat_info['name']} (Material 2):\n\n"
    options = []
    for idx, col in enumerate(colors, 1):
        h = colors_data.hex_for_color(col)
        display_col = f"|{h}{col}|n" if h else col
        options.append({
            "key": str(idx),
            "desc": display_col,
            "goto": lambda c, r, cl=col: _set_col_2(c, cl),
        })
    return text, options


def _set_col_2(caller, col):
    mat_key = _load(caller, "mat_2")
    materials = _load(caller, "materials", [])
    materials.append([mat_key, col])
    _store(caller, "materials", materials)
    return "node_adjective"


def node_adjective(caller, raw_string, **kwargs):
    itype_key = _load(caller, "item_type", "furniture")
    itype = items_data.get_item_type(itype_key)
    adjs = itype["adjectives"]

    text = "Choose an adjective based on item type:\n\n"
    options = []
    for idx, adj in enumerate(adjs, 1):
        options.append({
            "key": str(idx),
            "desc": adj,
            "goto": lambda c, r, a=adj: _set_adjective(c, a),
        })
    return text, options


def _set_adjective(caller, adj):
    _store(caller, "adjective", adj)
    return "node_summary_1"


def node_summary_1(caller, raw_string, **kwargs):
    base_name = _load(caller, "base_name", "item")
    mats = list(_load(caller, "materials", []))
    mats.sort(key=lambda m: m[0])

    mat_display_lines = []
    mat_colored_parts = []
    for m, col_key in mats:
        h = colors_data.hex_for_color(col_key)
        colored_col = f"|{h}{col_key}|n" if h else col_key
        mat_display_lines.append(f"{colored_col} {m}")
        if h:
            mat_colored_parts.append(f"|{h}{m}|n")
        else:
            mat_colored_parts.append(m)

    mat_part = iter_to_str(mat_colored_parts, endsep=", and") if mat_colored_parts else ""
    adj = _load(caller, "adjective", "")

    parts = []
    if mat_part:
        parts.append(mat_part)
    if adj:
        parts.append(adj)
    parts.append(base_name)
    combined = " ".join(parts)
    from evennia.utils.ansi import strip_ansi
    clean_combined = strip_ansi(combined)
    art = appearance_data.article(clean_combined).lower()
    preview = f"{art} {combined}"

    text = (
        f"|w--- Core Description Summary ---|n\n"
        f"  Base Name:  {base_name}\n"
        f"  Materials:  {', '.join(mat_display_lines)}\n"
        f"  Adjective:  {adj}\n"
        f"  Preview:    |g{preview}|n\n\n"
        f"Press Enter to continue to item-type specific configuration."
    )
    itype_key = _load(caller, "item_type", "furniture")
    next_node = "node_furn_is_bed" if itype_key == "furniture" else "node_summary_2"
    return text, {"key": "_default", "goto": next_node}


def node_furn_is_bed(caller, raw_string, **kwargs):
    text = "Is this furniture a bed?"
    options = (
        {"key": ("1", "y", "yes"), "desc": "Yes (Bed)", "goto": "node_furn_bed_type"},
        {"key": ("2", "n", "no"), "desc": "No (Seating/Custom)", "goto": "node_furn_seats"},
    )
    return text, options


def node_furn_bed_type(caller, raw_string, **kwargs):
    text = "What type of bed is this?"
    options = (
        {"key": ("1", "single"), "desc": "Single Bed (1x2 space, 2 seats)", "goto": lambda c, r: _furn_set_bed(c, "1x2", 2)},
        {"key": ("2", "double"), "desc": "Double Bed (2x2 square, 4 seats)", "goto": lambda c, r: _furn_set_bed(c, "2x2", 4)},
    )
    return text, options


def _furn_set_bed(caller, dim, seats):
    _store(caller, "dimension", dim)
    _store(caller, "seats", seats)
    return "node_furn_occupies"


def node_furn_seats(caller, raw_string, **kwargs):
    text = "How many does it seat? (0 for custom dimensions like 1x1, 1x3, etc., or 1, 2, 3):"
    options = (
        {"key": "0", "desc": "Custom Dimensions", "goto": "node_furn_custom_dim"},
        {"key": ("1", "2", "3"), "desc": "1 to 3 seats", "goto": _furn_handle_seats},
    )
    return text, options


def _furn_handle_seats(caller, raw_string, **kwargs):
    val = raw_string.strip()
    if val in ("1", "2", "3"):
        seats = int(val)
        _store(caller, "seats", seats)
        _store(caller, "dimension", f"1x{seats}")
        return "node_furn_occupies"
    return "node_furn_seats"


def node_furn_custom_dim(caller, raw_string, **kwargs):
    text = "Choose custom dimension/shape:"
    options = (
        {"key": "1", "desc": "1x1", "goto": lambda c, r: _furn_set_dim(c, "1x1", 1)},
        {"key": "2", "desc": "1x2", "goto": lambda c, r: _furn_set_dim(c, "1x2", 2)},
        {"key": "3", "desc": "1x3", "goto": lambda c, r: _furn_set_dim(c, "1x3", 3)},
        {"key": "4", "desc": "2x2", "goto": lambda c, r: _furn_set_dim(c, "2x2", 4)},
    )
    return text, options


def _furn_set_dim(caller, dim, seats):
    _store(caller, "dimension", dim)
    _store(caller, "seats", seats)
    return "node_furn_occupies"


def node_furn_occupies(caller, raw_string, **kwargs):
    text = "Does this furniture block movement? (y/n)"
    options = (
        {"key": ("y", "yes"), "desc": "Yes (Blocks movement)", "goto": lambda c, r: _furn_set_occupies(c, True)},
        {"key": ("n", "no"), "desc": "No (Walk over)", "goto": lambda c, r: _furn_set_occupies(c, False)},
    )
    return text, options


def _furn_set_occupies(caller, val):
    _store(caller, "occupies_space", val)
    return "node_furn_states"


def node_furn_states(caller, raw_string, **kwargs):
    text = "What states can you do here? Choose from: sit, rest, lay, sleep (comma-separated, or press enter for default):"
    return text, {"key": "_default", "goto": _furn_handle_states}


def _furn_handle_states(caller, raw_string, **kwargs):
    val = raw_string.strip().lower()
    if not val:
        states = ["sit", "rest", "lay", "sleep", "resting", "laying", "sleeping"]
    else:
        states = [s.strip() for s in val.split(",") if s.strip()]
    _store(caller, "allowed_states", states)
    return "node_furn_quality"


def node_furn_quality(caller, raw_string, **kwargs):
    text = "What is its quality rating? (0.1 to 3.0):"
    return text, {"key": "_default", "goto": _furn_handle_quality}


def _furn_handle_quality(caller, raw_string, **kwargs):
    try:
        val = float(raw_string.strip())
        val = max(0.1, min(3.0, val))
    except ValueError:
        caller.msg("Invalid number between 0.1 and 3.0.")
        return "node_furn_quality"
    _store(caller, "quality", val)
    return "node_summary_2"


def node_summary_2(caller, raw_string, **kwargs):
    itype = _load(caller, "item_type")
    base_name = _load(caller, "base_name")
    mats = _load(caller, "materials")
    adj = _load(caller, "adjective")
    dim = _load(caller, "dimension", "1x1")
    seats = _load(caller, "seats", 1)
    occupies = _load(caller, "occupies_space", True)
    quality = _load(caller, "quality", 1.0)

    text = (
        f"|w--- Final Item Summary ---|n\n"
        f"  Type:        {itype}\n"
        f"  Base Name:   {base_name}\n"
        f"  Materials:   {mats}\n"
        f"  Adjective:   {adj}\n"
        f"  Dimension:   {dim} (Seats: {seats})\n"
        f"  Blocks Mov:  {occupies}\n"
        f"  Quality:     {quality}\n\n"
        f"Build this item? (y/n)"
    )
    options = (
        {"key": ("y", "yes"), "desc": "Build Item", "goto": "node_build"},
        {"key": ("n", "no"), "desc": "Cancel", "goto": None},
    )
    return text, options


def node_build(caller, raw_string, **kwargs):
    itype = _load(caller, "item_type", "furniture")
    base_name = _load(caller, "base_name", "item")
    mats = _load(caller, "materials", [])
    adj = _load(caller, "adjective")
    dim = _load(caller, "dimension", "1x1")
    seats = _load(caller, "seats", 1)
    occupies = _load(caller, "occupies_space", True)
    states = _load(caller, "allowed_states", ["sit", "rest", "lay", "sleep", "resting", "laying", "sleeping"])
    quality = _load(caller, "quality", 1.0)

    item = create_object(
        "typeclasses.items.Item",
        key=base_name,
        location=caller,
    )
    item.item_type = itype
    item.base_name = base_name
    item.materials = mats
    item.item_adjective = adj
    item.dimension = dim
    item.seats = seats
    item.occupies_space = occupies
    item.allowed_states = states
    item.quality = quality
    item.calculate_footprint()

    caller.msg(f"|gCreated |w{item.get_display_name()}|g and placed it in your inventory.|n")
    return None
