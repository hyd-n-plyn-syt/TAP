import math
from collections import deque

from evennia.utils.evmenu import EvMenu

from combat.grid import (
    exit_direction,
    get_exit_at_coord,
    get_altitude_phrase,
    get_room_grid_size,
    grid_quadrant,
    is_valid_coord,
)
from world.systems.time import MAX_GRIDS_PER_ROUND

SPEED_TICKS = {"walk": 3, "jog": 2, "run": 1}
SPEED_GROUND_VERBS = {"walk": "walks", "jog": "jogs", "run": "runs"}
SPEED_GROUND_VERB_START = {"walk": "walking", "jog": "jogging", "run": "running"}
SPEED_FLY_VERBS = {"walk": "flies slowly", "jog": "flies briskly", "run": "flies recklessly"}
SPEED_FLY_VERB_START = {"walk": "flying slowly", "jog": "flying briskly", "run": "flying recklessly"}
SPEED_FLY_OVER = {"walk": "flies slowly over", "jog": "flies briskly over", "run": "flies recklessly over"}

_DIRECTION_FROM_DELTA = {
    (0, 1): "north", (0, -1): "south",
    (1, 0): "east", (-1, 0): "west",
    (1, 1): "northeast", (-1, 1): "northwest",
    (1, -1): "southeast", (-1, -1): "southwest",
}

_DIRECTION_OFFSETS = {
    "north": (0, 1), "south": (0, -1),
    "east": (1, 0), "west": (-1, 0),
    "northeast": (1, 1), "northwest": (-1, 1),
    "southeast": (1, -1), "southwest": (-1, -1),
}

_POSSESSIVE_DIR = {
    "north": "its", "south": "its", "east": "its", "west": "its",
    "northeast": "its", "northwest": "its", "southeast": "its", "southwest": "its",
    "up": "its", "down": "its",
}

_TOWARD_PHRASE = {
    "north": "toward you", "south": "toward you",
    "east": "toward you", "west": "toward you",
    "northeast": "toward you", "northwest": "toward you",
    "southeast": "toward you", "southwest": "toward you",
    "up": "upward", "down": "downward",
}

_AWAY_PHRASE = {
    "north": "away from you", "south": "away from you",
    "east": "away from you", "west": "away from you",
    "northeast": "away from you", "northwest": "away from you",
    "southeast": "away from you", "southwest": "away from you",
    "up": "upward", "down": "downward",
}

def get_move_allowance(actions_taken):
    """
    Calculate grid movement allowance based on actions taken in the round.
    Base allowance: 6 grids (36ft).
    Each action reduces allowance by half (rounded down).
    """
    allowance = 6
    for _ in range(actions_taken):
        allowance = math.floor(allowance / 2)
    return max(0, allowance)


def _planes_overlap(mover, obj):
    """Whether two entities share at least one occupied realm plane. When
    either side has no plane data (stock objects), treat as overlapping."""
    if mover is None:
        return True
    m = getattr(mover, "planes_occupied", None)
    if not m:
        return True
    o = getattr(obj, "planes_occupied", None)
    if not o:
        return True
    return bool(set(m) & set(o))


def capitalize_display_name(text):
    """Capitalize the first visible character of a display name, skipping
    any leading ANSI color codes. Used where a name starts a sentence."""
    if not text:
        return text
    i = 0
    n = len(text)
    while i + 1 < n and text[i] == "|":
        i += 2
    if i >= n:
        return text
    return text[:i] + text[i].upper() + text[i + 1 :]


def is_grid_occupied(room, x, y, z=None, ignore=None, mover=None):
    """Return list of occupants blocking (x, y, z) for the *mover*'s realm.

    Occupancy is realm-aware, with two slots (physical and visarial). A mover
    only collides with occupants present in the same realm(s) it occupies, so a
    physical and a manifested creature can freely share a tile while a
    dual-natured object blocks both realms. Pass *mover* to scope the check to
    that entity's planes; without it all realm occupants count.

    Only objects with ``occupies_space`` True count.  Exits are always
    excluded.  Pass *ignore* to exclude a specific object or collection of objects
    (the mover itself, furniture, etc.) from the check.  When *z* is None the z-axis is not checked.
    """
    ignore_list = []
    if ignore is not None:
        if isinstance(ignore, (list, tuple, set)):
            ignore_list = list(ignore)
        else:
            ignore_list = [ignore]

    mover_planes = None
    if mover is not None:
        planes = getattr(mover, "planes_occupied", None)
        mover_planes = set(planes) if planes else {"physical", "visarial"}

    occupants = []
    for obj in room.contents:
        if obj in ignore_list:
            continue
        if getattr(obj, "destination", None):
            continue
        if not getattr(obj, "occupies_space", False):
            continue

        matched = False
        if hasattr(obj, "is_at_coord"):
            matched = obj.is_at_coord(x, y)
        else:
            matched = (getattr(obj.db, "pos_x", None) == x and getattr(obj.db, "pos_y", None) == y)

        if not matched:
            continue

        if z is not None and getattr(obj.db, "pos_z", None) != z:
            continue
        if mover_planes is not None:
            planes = getattr(obj, "planes_occupied", None)
            obj_planes = set(planes) if planes else {"physical", "visarial"}
            if not (mover_planes & obj_planes):
                continue
        occupants.append(obj)
    return occupants


def move_actor(actor, x, y, z=None):
    """
    Move an actor to a grid coordinate within the current room. Returns
    (success, message). This never traverses exits - room transitions are
    handled by the navigation system via standard direction commands.
    """
    room = actor.location
    if not room:
        return False, "You are not anywhere."
    if not is_valid_coord(room, x, y):
        return False, "That coordinate is out of bounds."

    if is_grid_occupied(room, x, y, z=z, ignore=actor, mover=actor):
        EvMenu(actor, "combat.menus", startnode="collision_menu_node")
        return False, "That space is occupied."

    actor.db.pos_x = x
    actor.db.pos_y = y
    if z is not None:
        actor.db.pos_z = z
    return True, f"You move to {x}, {y}."


def describe_nav_target(room, nav, mover=None):
    """
    A phrase describing where a navigation is heading, for the "moves
    toward ..." observer message. Resolves in order: the exit being
    traversed ("the northern exit"), an occupant of the destination grid
    ("a person or object description"), or a quadrant of the area
    ("the northwest portion of the area"). The mover itself is never
    treated as the target.
    """
    dest_x, dest_y = nav["dest_x"], nav["dest_y"]
    exit_obj = None
    if nav.get("exit_dbref"):
        from evennia.objects.models import ObjectDB
        try:
            exit_obj = ObjectDB.objects.get(id=nav["exit_dbref"])
        except ObjectDB.DoesNotExist:
            exit_obj = None
    if exit_obj:
        direction = exit_direction(exit_obj)
        if direction:
            return f"the {direction} exit"

    if nav.get("dest_z") is not None and mover is not None:
        mover_z = getattr(getattr(mover, "db", None), "pos_z", None)
        if mover_z is not None:
            dz = int(nav["dest_z"]) - int(mover_z)
            if dz > 0:
                return "the air above"
            if dz < 0:
                return "the area below"

    occupants = [
        obj
        for obj in room.contents
        if obj is not mover
        and not getattr(obj, "destination", None)
        and _planes_overlap(mover, obj)
        and getattr(obj.db, "pos_x", None) == dest_x
        and getattr(obj.db, "pos_y", None) == dest_y
    ]
    if occupants:
        occupant = occupants[0]
        desc = getattr(occupant, "appearance_name", None)
        if not desc:
            desc = occupant.key
        return desc

    return grid_quadrant(room, dest_x, dest_y)


def _nav_target_occupant(room, nav, mover=None):
    """The creature or object sitting on the navigation's destination grid,
    present in the mover's realm, excluding the mover themselves, or None."""
    dest_x, dest_y = nav["dest_x"], nav["dest_y"]
    for obj in room.contents:
        if obj is mover:
            continue
        if getattr(obj, "destination", None):
            continue
        if not _planes_overlap(mover, obj):
            continue
        if getattr(obj.db, "pos_x", None) == dest_x and getattr(obj.db, "pos_y", None) == dest_y:
            return obj
    return None


def announce_grid_move(char, nav):
    room = char.location
    if not (room and nav): return
    target = describe_nav_target(room, nav, mover=char)
    occupant = _nav_target_occupant(room, nav, mover=char)
    
    mode = nav.get("movement_mode", "walking")
    if mode == "takeoff": verb = f"takes off flying in {target}"
    elif mode == "landing": verb = f"descends toward {target}"
    elif mode == "flying": verb = f"flies toward {target}"
    else: verb = f"moves toward {target}"

    appearance = char.appearance_name

    for observer in room.contents:
        if observer is char or not getattr(observer, "is_creature", False) or not char.visible_to(observer): continue
        if occupant is observer:
            observer.msg(f"{appearance} {verb.replace(target, 'you')}.", from_obj=char)
        else:
            observer.msg(f"{appearance} {verb}.", from_obj=char)


def announce_grid_arrival(char, nav):
    room = char.location
    if not (room and nav): return
    
    # State-aware arrival targets
    target = describe_nav_target(room, nav, mover=char)
    occupant = _nav_target_occupant(room, nav, mover=char)
    
    mode = nav.get("movement_mode", "walking")
    if mode == "takeoff":
        # Target describes the "in the air above..." area
        verb = f"hovers above {target}"
    elif mode == "landing":
        verb = f"lands in {target}"
    elif mode == "flying":
        verb = f"flies into {target}"
    else:
        verb = f"arrives in {target}"

    appearance = char.appearance_name
    
    if occupant:
        for observer in room.contents:
            if observer is char or not getattr(observer, "is_creature", False) or not char.visible_to(observer): continue
            if occupant is observer:
                observer.msg(f"{appearance} arrives beside you.", from_obj=char)
            else:
                observer.msg(f"{appearance} arrives beside {target}.", from_obj=char)
        return
    text = f"{appearance} {verb}."
    for observer in room.contents:
        if observer is char or not getattr(observer, "is_creature", False) or not char.visible_to(observer): continue
        observer.msg(text, from_obj=char)


def nav_eta(nav, pos_x, pos_y, pos_z=None, speed="walk"):
    """Estimated seconds to reach a navigation destination. Accounts for
    movement speed tier (walk=3s/tile, jog=2s/tile, run=1s/tile) and
    1-second pauses between each completed round of 6 grids."""
    step_every = SPEED_TICKS.get(speed, 3)
    dist = max(
        abs(nav["dest_x"] - pos_x),
        abs(nav["dest_y"] - pos_y),
    )
    if nav.get("dest_z") is not None and pos_z is not None:
        dist = max(dist, abs(int(nav["dest_z"]) - int(pos_z)))
    if dist == 0:
        return 0
    movement_secs = dist * step_every
    pauses = (dist - 1) // MAX_GRIDS_PER_ROUND
    return movement_secs + pauses


def mover_start_message(room, nav, mover):
    """The message a mover sees when beginning navigation."""
    occupant = _nav_target_occupant(room, nav, mover=mover)
    target = getattr(occupant, "appearance_name", None) or occupant.key if occupant else describe_nav_target(room, nav, mover=mover)
    speed = getattr(mover.db, "move_speed", "walk") or "walk"
    eta = nav_eta(
        nav,
        mover.db.pos_x or 0,
        mover.db.pos_y or 0,
        getattr(mover.db, "pos_z", None) or 1,
        speed=speed,
    )
    seconds = "second" if eta == 1 else "seconds"
    mode = nav.get("movement_mode", "walking")
    if mode == "takeoff": return f"You take off, rising into the air toward {target}. Arrive in about {eta} {seconds}."
    if mode == "landing": return f"You descend toward {target}. Arrive in about {eta} {seconds}."
    if mode == "flying": return f"You begin flying toward {target}. Arrive in about {eta} {seconds}."
    return f"You begin moving toward {target}. Arrive in about {eta} {seconds}."


def mover_arrival_message(room, nav, mover):
    """The message a mover sees when they arrive at their navigation destination."""
    occupant = _nav_target_occupant(room, nav, mover=mover)
    if occupant:
        return f"You arrive beside {getattr(occupant, 'appearance_name', None) or occupant.key}."
    target = describe_nav_target(room, nav, mover=mover)
    mode = nav.get("movement_mode", "walking")
    z = nav.get("dest_z") or mover.db.pos_z or 1
    alt = get_altitude_phrase(z)
    if mode == "takeoff": return f"You arrive in the air {alt} {target}."
    if mode == "landing": return f"You have landed in {target}."
    if mode == "flying": return f"You arrive {alt} {target}."
    return f"You arrive in {target}."


def start_navigation(actor, dest_x, dest_y, z=None, exit_obj=None, movement_mode="walking", delta_x=None, delta_y=None):
    """
    Begin autonomous grid navigation toward a destination coordinate. If an
    exit object is supplied, reaching the destination traverses it. A
    per-character MovementTimer (cloned from the universal clock) moves the
    actor one grid per second, capped at the round's movement allowance.

    If the actor already has an active navigation, the new one is appended
    to their nav_queue and will start automatically when the current one
    completes.

    delta_x/delta_y: if provided, the queued destination will be
    recalculated relative to the character's position at drain time.
    """
    pose = getattr(actor, "pose", None) or "standing"
    if pose != "standing":
        actor.msg("You cannot move while resting, sleeping, or laying. You must stand up first.")
        return False

    room = actor.location
    nav = {
        "dest_x": int(dest_x),
        "dest_y": int(dest_y),
        "dest_z": int(z) if z is not None else None,
        "exit_dbref": exit_obj.id if exit_obj else None,
        "movement_mode": movement_mode,
    }
    if delta_x is not None and delta_y is not None:
        nav["delta_x"] = int(delta_x)
        nav["delta_y"] = int(delta_y)
    if getattr(actor.db, "navigation", None):
        queue = list(getattr(actor.db, "nav_queue", None) or [])
        queue.append(nav)
        actor.db.nav_queue = queue
        actor.msg("Queued.")
    else:
        actor.db.navigation = nav
        if room:
            actor.msg(mover_start_message(room, nav, actor))
            from combat.timers import ensure_movement_timer
            ensure_movement_timer(actor)
    return True


def find_nearest_unoccupied_coord(room, start_x, start_y, z=1, ignore=None, mover=None):
    """Find the nearest coordinate to (start_x, start_y) in room that is free
    in the mover's realm (see ``is_grid_occupied``)."""
    from combat.grid import get_room_grid_size, is_valid_coord
    w, h = get_room_grid_size(room)

    if is_valid_coord(room, start_x, start_y) and not is_grid_occupied(room, start_x, start_y, z=z, ignore=ignore, mover=mover):
        return start_x, start_y

    max_dist = max(w, h)
    for d in range(1, max_dist + 1):
        candidates = []
        for dx in range(-d, d + 1):
            for dy in range(-d, d + 1):
                if max(abs(dx), abs(dy)) == d:
                    nx, ny = start_x + dx, start_y + dy
                    if is_valid_coord(room, nx, ny) and not is_grid_occupied(room, nx, ny, z=z, ignore=ignore, mover=mover):
                        candidates.append((nx, ny))
        if candidates:
            candidates.sort(key=lambda t: abs(t[0] - start_x) + abs(t[1] - start_y))
            return candidates[0]
    return start_x, start_y


def direction_from_delta(dx, dy):
    """Return a compass direction string from a grid delta, or None for zero."""
    return _DIRECTION_FROM_DELTA.get((dx, dy))


def find_path(room, sx, sy, gx, gy, z=None, ignore=None, mover=None):
    """BFS shortest path from (sx,sy) to (gx,gy) on the room grid.

    Returns ``(path, blockers)`` where *path* is a list of ``(x,y)`` tuples
    (including start) and *blockers* is the list of occupant objects at the
    goal tile (empty if reachable).  If the goal is occupied and
    *approach_target* is the mover (i.e. the char IS the approach target),
    the path ends at the nearest free neighbor of the goal.
    """
    w, h = get_room_grid_size(room)
    if not (is_valid_coord(room, sx, sy) and is_valid_coord(room, gx, gy)):
        return [], []

    if sx == gx and sy == gy:
        return [(sx, sy)], []

    visited = set()
    visited.add((sx, sy))
    parent = {}
    queue = deque([(sx, sy)])
    goal_blockers = []

    while queue:
        cx, cy = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                if is_grid_occupied(room, nx, ny, z=z, ignore=ignore, mover=mover):
                    continue
                parent[(nx, ny)] = (cx, cy)
                if nx == gx and ny == gy:
                    path = []
                    cur = (gx, gy)
                    while cur is not None:
                        path.append(cur)
                        cur = parent.get(cur)
                    path.reverse()
                    return path, []
                queue.append((nx, ny))

    goal_blockers = is_grid_occupied(room, gx, gy, z=z, ignore=ignore, mover=mover)
    if goal_blockers:
        best, best_dist = None, float("inf")
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = gx + dx, gy + dy
                if (nx, ny) not in parent:
                    continue
                if is_grid_occupied(room, nx, ny, z=z, ignore=ignore, mover=mover):
                    continue
                dist = abs(nx - sx) + abs(ny - sy)
                if dist < best_dist:
                    best, best_dist = (nx, ny), dist
        if best:
            path = []
            cur = best
            while cur is not None:
                path.append(cur)
                cur = parent.get(cur)
            path.reverse()
            return path, goal_blockers

    return [], goal_blockers


def _toward_or_away(observer, char, dx, dy):
    """'toward you' / 'away from you' / None based on observer position relative to move."""
    if not observer or not char:
        return None
    ox = getattr(observer.db, "pos_x", None)
    oy = getattr(observer.db, "pos_y", None)
    cx = getattr(char.db, "pos_x", None)
    cy = getattr(char.db, "pos_y", None)
    if ox is None or oy is None or cx is None or cy is None:
        return None
    rel_x = int(ox) - int(cx)
    rel_y = int(oy) - int(cy)
    toward_x = (dx > 0 and rel_x > 0) or (dx < 0 and rel_x < 0)
    toward_y = (dy > 0 and rel_y > 0) or (dy < 0 and rel_y < 0)
    away_x = (dx > 0 and rel_x < 0) or (dx < 0 and rel_x > 0)
    away_y = (dy > 0 and rel_y < 0) or (dy < 0 and rel_y > 0)
    if toward_x or toward_y:
        return "toward you"
    if away_x or away_y:
        return "away from you"
    return None


def _possessive_dir(entity, direction):
    """Colored 'his/her/its' + direction for observer echoes."""
    from world.systems.narrative import colored_pronoun
    poss = colored_pronoun(entity, "poss_obj")
    return f"{poss} {direction}"


def _adjacent_entities(room, gx, gy, z, mover=None):
    """Visible creatures and objects within Chebyshev 1 of (gx,gy), excluding the mover."""
    from world.systems.narrative import entity_first_ref
    entities = []
    for obj in room.contents:
        if obj is mover:
            continue
        if getattr(obj, "destination", None):
            continue
        if not getattr(obj, "occupies_space", False):
            continue
        ox = getattr(obj.db, "pos_x", None)
        oy = getattr(obj.db, "pos_y", None)
        if ox is None or oy is None:
            continue
        if max(abs(int(ox) - gx), abs(int(oy) - gy)) > 1:
            continue
        if z is not None:
            oz = getattr(obj.db, "pos_z", None)
            if oz is not None and int(oz) != int(z):
                continue
        if getattr(obj, "is_creature", False):
            entities.append(entity_first_ref(obj, sentence_start=False))
        else:
            entities.append(getattr(obj, "appearance_name", None) or obj.key)
    return entities


def _format_next_to(entities):
    """'a Foo, a Bar, and a Baz' from a list of display-name strings."""
    if not entities:
        return ""
    if len(entities) == 1:
        return entities[0]
    return ", ".join(entities[:-1]) + ", and " + entities[-1]


def move_observer_echo(char, direction, speed, observer):
    """Direction-based, observer-relative move echo."""
    from world.systems.narrative import colored_pronoun
    dx, dy = _DIRECTION_OFFSETS.get(direction, (0, 0))
    toward = _toward_or_away(observer, char, dx, dy)
    if toward is None:
        toward = "away from you"
    poss = _possessive_dir(char, direction)
    verb = SPEED_GROUND_VERBS.get(speed, "moves")
    if getattr(char.db, "is_flying", False):
        verb = SPEED_FLY_VERBS.get(speed, "flies")
    name = getattr(char, "appearance_name", None) or char.key
    return f"{name} {verb} to {poss}, {toward}."


def move_mover_echo(char, direction, speed, target_desc=None):
    """Mover's own view when starting movement."""
    verb = SPEED_GROUND_VERB_START.get(speed, "moving")
    if getattr(char.db, "is_flying", False):
        verb = SPEED_FLY_VERB_START.get(speed, "flying")
    if target_desc:
        return f"You begin {verb} toward {target_desc}."
    return f"You begin {verb} toward the {direction}."


def arrival_observer_echo(char, nav, observer):
    """Arrival echo: quadrant + next-to list, per-observer visibility."""
    from world.systems.narrative import entity_first_ref
    room = char.location
    ax = char.db.pos_x or 0
    ay = char.db.pos_y or 1
    az = nav.get("dest_z") or getattr(char.db, "pos_z", None) or 1
    quad = grid_quadrant(room, ax, ay)
    adjacent = _adjacent_entities(room, ax, ay, az, mover=char)
    visible_adjacent = [e for e in adjacent if char.visible_to(observer)] if hasattr(char, "visible_to") else adjacent
    name = getattr(char, "appearance_name", None) or char.key
    mode = nav.get("movement_mode", "walking")
    if mode == "takeoff":
        verb = "hovers above"
    elif mode == "landing":
        verb = "lands in"
    elif mode == "flying":
        verb = "arrives in"
    else:
        verb = "arrives in"
    text = f"{name} {verb} {quad}"
    if visible_adjacent:
        text += f" next to {_format_next_to(visible_adjacent)}"
    text += "."
    return text


def arrival_mover_echo(char, nav):
    """Mover's arrival message: quadrant + next-to list."""
    room = char.location
    ax = char.db.pos_x or 0
    ay = char.db.pos_y or 1
    az = nav.get("dest_z") or getattr(char.db, "pos_z", None) or 1
    quad = grid_quadrant(room, ax, ay)
    adjacent = _adjacent_entities(room, ax, ay, az, mover=char)
    mode = nav.get("movement_mode", "walking")
    if mode == "takeoff":
        text = f"You arrive in the air {quad}."
    elif mode == "landing":
        text = f"You have landed {quad}."
    elif mode == "flying":
        text = f"You arrive in the air {quad}."
    else:
        text = f"You arrive in {quad}"
        if adjacent:
            text += f" next to {_format_next_to(adjacent)}"
        text += "."
    return text


def detour_observer_echo(char, direction, speed, obstacle):
    """'{PERSONDESC} {speed_verb} around {colored_obj} to the {dir}.'"""
    from world.systems.narrative import colored_pronoun
    name = getattr(char, "appearance_name", None) or char.key
    verb = SPEED_GROUND_VERBS.get(speed, "moves")
    if getattr(char.db, "is_flying", False):
        verb = SPEED_FLY_VERBS.get(speed, "flies")
    obs_name = getattr(obstacle, "appearance_name", None) or obstacle.key
    return f"{name} {verb} around {obs_name} to the {direction}."


def detour_mover_echo(char, direction, speed, obstacle):
    """'You {speed_verb} around {colored_obj} to the {dir}.'"""
    verb = SPEED_GROUND_VERB_START.get(speed, "moving")
    if getattr(char.db, "is_flying", False):
        verb = SPEED_FLY_VERB_START.get(speed, "flying")
    obs_name = getattr(obstacle, "appearance_name", None) or obstacle.key
    return f"You {verb} around {obs_name} to the {direction}."


def stuck_blockers_message(blockers):
    """'The way is blocked by a Foo, a Bar, and a Baz.'"""
    names = []
    for b in blockers[:5]:
        if getattr(b, "is_creature", False):
            from world.systems.narrative import entity_first_ref
            names.append(entity_first_ref(b, sentence_start=False))
        else:
            names.append(getattr(b, "appearance_name", None) or b.key)
    if not names:
        return "The way is blocked."
    return f"The way is blocked by {_format_next_to(names)}."


def blocked_with_hint(blockers, has_autonav):
    """Blocked message, optionally hinting at AUTONAVIGATE."""
    msg = stuck_blockers_message(blockers)
    if has_autonav:
        return msg
    return f"{msg}\nType AUTONAVIGATE to route around obstacles."
