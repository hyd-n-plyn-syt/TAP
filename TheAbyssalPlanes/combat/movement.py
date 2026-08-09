import math

from evennia.utils.evmenu import EvMenu

from combat.grid import (
    exit_direction,
    get_exit_at_coord,
    get_room_grid_size,
    get_altitude_phrase,
    grid_quadrant,
    is_valid_coord,
)

SUB_TICK_RATE = 1
GLOBAL_ROUND_DURATION = 6
MAX_GRIDS_PER_ROUND = 5

def get_move_allowance(actions_taken):
    """
    Calculate grid movement allowance based on actions taken in the round.
    Base allowance: 5 grids (30ft).
    Each action reduces allowance by half (rounded down).
    """
    allowance = 5
    for _ in range(actions_taken):
        allowance = math.floor(allowance / 2)
    return max(0, allowance)


def is_grid_occupied(room, x, y):
    """Checks if the grid point is at full occupancy (2+ entities).

    Exits are excluded - they are traversal objects, not occupiers.
    """
    occupants = [
        obj for obj in room.contents
        if not getattr(obj, "destination", None)
        and getattr(obj.db, "pos_x", None) == x
        and getattr(obj.db, "pos_y", None) == y
    ]
    return len(occupants) >= 2


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

    if is_grid_occupied(room, x, y):
        EvMenu(actor, "combat.menus", startnode="collision_menu_node")
        return False, "That space is occupied."

    actor.db.pos_x = x
    actor.db.pos_y = y
    if z is not None:
        actor.db.pos_z = z
    return True, f"You move to {x}, {y}."


def ensure_combat_loop(room):
    """Make sure the room has exactly one running CombatLoop script. Returns it."""
    existing = room.scripts.get(key="combat_loop")
    kept = None
    for script in existing:
        if kept is None and getattr(script, "db_is_active", False):
            kept = script
            continue
        script.delete()
    if kept is not None:
        return kept
    return room.scripts.add("combat.loop.CombatLoop", key="combat_loop")


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
    excluding the mover themselves, or None."""
    dest_x, dest_y = nav["dest_x"], nav["dest_y"]
    for obj in room.contents:
        if obj is mover:
            continue
        if getattr(obj, "destination", None):
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


def nav_eta(nav, pos_x, pos_y, pos_z=None):
    """Estimated seconds to reach a navigation destination, assuming a
    full round is available (5 grids of movement, then a 1s round pause
    between each completed chunk). Best-effort estimate only."""
    dist = max(
        abs(nav["dest_x"] - pos_x),
        abs(nav["dest_y"] - pos_y),
    )
    if nav.get("dest_z") is not None and pos_z is not None:
        dist = max(dist, abs(int(nav["dest_z"]) - int(pos_z)))
    if dist == 0:
        return 0
    pauses = (dist - 1) // MAX_GRIDS_PER_ROUND
    return dist + pauses


def mover_start_message(room, nav, mover):
    """The message a mover sees when beginning navigation."""
    occupant = _nav_target_occupant(room, nav, mover=mover)
    target = getattr(occupant, "appearance_name", None) or occupant.key if occupant else describe_nav_target(room, nav, mover=mover)
    eta = nav_eta(
        nav,
        mover.db.pos_x or 0,
        mover.db.pos_y or 0,
        getattr(mover.db, "pos_z", None) or 1,
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


def start_navigation(actor, dest_x, dest_y, z=None, exit_obj=None, movement_mode="walking"):
    """
    Begin autonomous grid navigation toward a destination coordinate. If an
    exit object is supplied, reaching the destination traverses it. The
    CombatLoop moves the actor one grid per sub-tick, capped at the round's
    movement allowance.
    """
    room = actor.location
    nav = {
        "dest_x": int(dest_x),
        "dest_y": int(dest_y),
        "dest_z": int(z) if z is not None else None,
        "exit_dbref": exit_obj.id if exit_obj else None,
        "movement_mode": movement_mode,
    }
    actor.db.navigation = nav
    if room:
        actor.msg(mover_start_message(room, nav, actor))
        ensure_combat_loop(room)
    return True
