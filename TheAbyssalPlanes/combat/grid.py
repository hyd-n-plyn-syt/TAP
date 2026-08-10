ROOM_GRID_SIZES = {
    "tiny": 2,
    "small": 3,
    "medium": 5,
    "large": 11,
    "huge": 25,
    "massive": 51
}

# Grid offsets for one-step directional movement. x grows east, y grows
# north, z grows upward.
DIRECTION_OFFSETS = {
    "north": (0, 1, 0), "n": (0, 1, 0),
    "south": (0, -1, 0), "s": (0, -1, 0),
    "east": (1, 0, 0), "e": (1, 0, 0),
    "west": (-1, 0, 0), "w": (-1, 0, 0),
    "northeast": (1, 1, 0), "ne": (1, 1, 0),
    "northwest": (-1, 1, 0), "nw": (-1, 1, 0),
    "southeast": (1, -1, 0), "se": (1, -1, 0),
    "southwest": (-1, -1, 0), "sw": (-1, -1, 0),
    "up": (0, 0, 1), "u": (0, 0, 1),
    "down": (0, 0, -1), "d": (0, 0, -1),
}

CANONICAL_DIRECTION = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down",
}

def get_room_grid_size(room):
    """Return (width, height) for the room's grid."""
    size_key = room.db.room_size or "medium"
    if isinstance(size_key, str):
        s = ROOM_GRID_SIZES.get(size_key, 5)
        return (s, s)
    try:
        w = size_key.get("width", 5)
        h = size_key.get("height", 5)
        return (w, h)
    except (AttributeError, TypeError):
        return (5, 5)

def is_valid_coord(room, x, y):
    w, h = get_room_grid_size(room)
    return 0 <= x < w and 0 <= y < h

def get_entry_coords(room, direction):
    w, h = get_room_grid_size(room)
    cx = w // 2
    cy = h // 2
    
    mapping = {
        "north": (cx, h - 1),
        "south": (cx, 0),
        "east": (w - 1, cy),
        "west": (0, cy),
        "northeast": (w - 1, h - 1),
        "northwest": (0, h - 1),
        "southeast": (w - 1, 0),
        "southwest": (0, 0)
    }
    return mapping.get(direction.lower(), None)

def get_exit_at_coord(room, x, y):
    """
    Checks if a grid coordinate corresponds to an exit.
    """
    for obj in room.contents:
        if obj.destination: # Is an exit
            ex_x, ex_y = get_entry_coords(room, obj.key)
            if ex_x == x and ex_y == y:
                return obj
    return None


def exit_direction(exit_obj):
    """
    Return the cardinal/ordinal direction of an exit ('north', 'northeast', ...)
    based on its key and aliases, or None if it has no compass direction.
    """
    names = [exit_obj.key]
    if hasattr(exit_obj.aliases, "all"):
        names.extend(exit_obj.aliases.all())
    
    compass = (
        "north", "south", "east", "west",
        "northeast", "northwest", "southeast", "southwest"
    )
    for name in names:
        if name.lower() in compass:
            return name.lower()
    return None


def get_exit_coords(room, exit_obj):
    """
    The grid coordinate a room's exit sits at, derived from its direction.
    Returns None for non-directional exits.
    """
    direction = exit_direction(exit_obj)
    if not direction:
        return None
    return get_entry_coords(room, direction)


def get_altitude_phrase(z):
    """Phrase describing a Z-level."""
    if z <= 1: return "on the ground"
    if z == 2: return "above"
    if z == 3: return "far above"
    return "very far above"


def grid_quadrant(room, x, y):
    """Compass quadrant phrase."""
    if x is None or y is None:
        return "the center of the area"
    x, y = int(x), int(y)
    w, h = get_room_grid_size(room)
    cx = w // 2
    cy = h // 2
    north = y >= cy + 1
    south = y <= cy - 1
    east = x >= cx + 1
    west = x <= cx - 1
    if north and east: return "the northeast portion of the area"
    if north and west: return "the northwest portion of the area"
    if south and east: return "the southeast portion of the area"
    if south and west: return "the southwest portion of the area"
    if north: return "the northern portion of the area"
    if south: return "the southern portion of the area"
    if east: return "the eastern portion of the area"
    if west: return "the western portion of the area"
    return "the center of the area"


def get_room_floor_z(room):
    """
    The lowest z-level movement may reach in a room. Defaults to 1 (the base
    floor); a builder may override via room.db.floor_z.
    """
    override = getattr(room.db, "floor_z", None)
    if override is not None:
        return int(override)
    return 1


def get_room_max_z(room):
    """
    The highest z-level movement may reach in a room. Defaults to the room's
    grid size (the same count of positions X and Y span); a builder may
    override via room.db.max_z.
    """
    override = getattr(room.db, "max_z", None)
    if override is not None:
        return int(override)
    w, h = get_room_grid_size(room)
    return max(w, h)
