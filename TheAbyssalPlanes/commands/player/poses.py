from commands.command import Command
from combat.movement import is_grid_occupied
from world.systems.regen import ensure_regen_timer
from world.systems.narrative import colored_self
from combat.grid import is_valid_coord
from evennia.utils.ansi import strip_ansi

OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}

PERPENDICULAR = {"north": "east", "south": "west", "east": "north", "west": "south"}


def _get_furniture_tiles(furn):
    fx = getattr(furn.db, "pos_x", 0)
    fy = getattr(furn.db, "pos_y", 0)
    return [(fx, fy)] + list(furn.db.extra_coords or [])


def _find_furniture_under(caller):
    room = caller.location
    if not room:
        return None
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)
    for obj in room.contents:
        if obj.is_typeclass("typeclasses.furniture.Furniture"):
            if (cx, cy) in _get_furniture_tiles(obj):
                return obj
    return None


def _find_furniture(caller, arg):
    room = caller.location
    if not room:
        return None
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)

    if arg:
        obj = caller.search(arg, candidates=room.contents)
        if obj and obj.is_typeclass("typeclasses.furniture.Furniture"):
            tiles = _get_furniture_tiles(obj)
            near = any(max(abs(cx - tx), abs(cy - ty)) <= 1 for tx, ty in tiles)
            if near:
                return obj
            caller.msg(f"{obj.key} is too far away. You need to be right next to it.")
            return None
        return None

    best_obj = None
    min_dist = 999
    for obj in room.contents:
        if obj.is_typeclass("typeclasses.furniture.Furniture"):
            tiles = _get_furniture_tiles(obj)
            for tx, ty in tiles:
                dist = max(abs(cx - tx), abs(cy - ty))
                if dist <= 1 and dist < min_dist:
                    min_dist = dist
                    best_obj = obj
    return best_obj


def _get_furniture_seat_coord(caller, furn):
    room = caller.location
    if not room:
        return getattr(caller.db, "pos_x", 0), getattr(caller.db, "pos_y", 0)
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)

    caller_planes = set(getattr(caller, "planes_occupied", ()) or ())
    occupancies = furn.occupied_seats_by_plane()

    free_tiles = []
    for tx, ty in furn.footprint_tiles():
        if not (caller_planes & occupancies.get((tx, ty), frozenset())):
            free_tiles.append((tx, ty))

    if not free_tiles:
        return None

    free_tiles.sort(key=lambda t: abs(t[0] - cx) + abs(t[1] - cy))
    return free_tiles[0]


def _find_adjacent_free_spot(caller):
    room = caller.location
    if not room:
        return None
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)

    # Cardinal directions first (N, E, S, W), then diagonals
    cardinals = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    for dx, dy in cardinals + diagonals:
        nx, ny = cx + dx, cy + dy
        if is_valid_coord(room, nx, ny) and not is_grid_occupied(room, nx, ny, ignore=caller, mover=caller):
            return (nx, ny)
    return None


def _is_bed(furn):
    return bool(getattr(furn, "is_bed", False))


def _is_near(caller, obj):
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)
    ox = getattr(obj.db, "pos_x", 0)
    oy = getattr(obj.db, "pos_y", 0)
    return max(abs(cx - ox), abs(cy - oy)) <= 1


def _announce_pose(caller, text):
    """Echo a pose change to the creatures that can actually observe the
    caller - same realm, perceiving it, and awake (see visible_to)."""
    for observer in caller._movement_observers():
        observer.msg(text, from_obj=caller)


def _check_furniture_approach(caller, furn):
    cx = getattr(caller.db, "pos_x", 0)
    cy = getattr(caller.db, "pos_y", 0)
    tiles = _get_furniture_tiles(furn)
    if not tiles:
        return True
    tx, ty = min(tiles, key=lambda t: abs(cx - t[0]) + abs(cy - t[1]))
    dx = cx - tx
    dy = cy - ty
    if dx == 0 and dy == 0:
        return True
    if abs(dx) >= abs(dy):
        approach = "east" if dx > 0 else "west"
    else:
        approach = "north" if dy > 0 else "south"
    facing = getattr(furn.db, "facing", "north")
    if _is_bed(furn):
        side_a = PERPENDICULAR.get(facing, facing)
        return approach == side_a or approach == OPPOSITE.get(side_a)
    return approach == facing


class CmdSit(Command):
    key = "sit"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        furn = _find_furniture(caller, self.args.strip())
        if furn:
            if not _check_furniture_approach(caller, furn):
                hint, _ = furn.approach_hint()
                caller.msg(f"{colored_self(caller, True)} need to approach {furn.appearance_name} from {hint} to sit on it.")
                return
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "sit" not in allowed and "sitting" not in allowed:
                caller.msg(f"{colored_self(caller, True)} can't comfortably sit in {furn.appearance_name}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.appearance_name} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("sitting"):
            caller.msg(f"{colored_self(caller, True)} cannot sit down right now.")
            return
        target_name = f" on {furn.appearance_name}" if furn else ""
        caller.msg(f"{colored_self(caller, True)} sit down{target_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} sits down{target_name}.")
            ensure_regen_timer(caller)
        caller.check_autowhere(old_loc, old_x, old_y, old_z)


class CmdRest(Command):
    key = "rest"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        furn = _find_furniture(caller, self.args.strip())
        if furn:
            if not _check_furniture_approach(caller, furn):
                hint, _ = furn.approach_hint()
                caller.msg(f"{colored_self(caller, True)} need to approach {furn.appearance_name} from {hint} to rest on it.")
                return
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "rest" not in allowed and "resting" not in allowed:
                caller.msg(f"{colored_self(caller, True)} can't comfortably rest on {furn.appearance_name}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.appearance_name} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("resting"):
            caller.msg(f"{colored_self(caller, True)} cannot rest right now.")
            return
        target_name = f" on {furn.appearance_name}" if furn else ""
        caller.msg(f"{colored_self(caller, True)} settle in to rest{target_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} settles in to rest{target_name}.")
            ensure_regen_timer(caller)
        caller.check_autowhere(old_loc, old_x, old_y, old_z)


class CmdSleep(Command):
    key = "sleep"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        furn = _find_furniture(caller, self.args.strip())
        if furn:
            if not _check_furniture_approach(caller, furn):
                hint, _ = furn.approach_hint()
                caller.msg(f"{colored_self(caller, True)} need to approach {furn.appearance_name} from {hint} to sleep on it.")
                return
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "sleep" not in allowed and "sleeping" not in allowed:
                caller.msg(f"{colored_self(caller, True)} can't comfortably sleep in {furn.appearance_name}; you'd need a bed.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.appearance_name} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if caller.state() != "normal":
            caller.set_state("normal")
            caller.msg(f"{colored_self(caller, True)} pull your awareness back to your original plane.")
        if not caller.set_pose("sleeping"):
            caller.msg(f"{colored_self(caller, True)} cannot sleep right now.")
            return
        target_name = f" on {furn.appearance_name}" if furn else ""
        caller.msg(f"{colored_self(caller, True)} drift off to sleep{target_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} falls asleep{target_name}.")
            ensure_regen_timer(caller)
        caller.check_autowhere(old_loc, old_x, old_y, old_z)


class CmdWake(Command):
    key = "wake"
    aliases = ["awaken", "wakeup"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        pose = getattr(caller, "pose", "standing")
        if pose not in ("sleeping", "resting", "laying", "sitting"):
            caller.msg(f"{colored_self(caller, True)} are already awake and standing.")
            return
        furn = _find_furniture_under(caller)
        if furn:
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "lay" not in allowed and "laying" not in allowed:
                caller.msg(f"{colored_self(caller, True)} can't comfortably lie on {furn.appearance_name}.")
                return
        if not caller.set_pose("laying"):
            caller.msg(f"{colored_self(caller, True)} cannot wake up right now.")
            return
        target_name = f" on {furn.appearance_name}" if furn else " on the ground"
        caller.msg(f"{colored_self(caller, True)} wake up and lie{target_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} wakes up and lies down.")
            ensure_regen_timer(caller)


class CmdLay(Command):
    key = "lay"
    aliases = ["lie"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        furn = _find_furniture(caller, self.args.strip())
        if furn:
            if not _check_furniture_approach(caller, furn):
                hint, _ = furn.approach_hint()
                caller.msg(f"{colored_self(caller, True)} need to approach {furn.appearance_name} from {hint} to lie on it.")
                return
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "lay" not in allowed and "laying" not in allowed and "lie" not in allowed:
                caller.msg(f"{colored_self(caller, True)} can't comfortably lie down on {furn.appearance_name}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.appearance_name} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("laying"):
            caller.msg(f"{colored_self(caller, True)} cannot lie down right now.")
            return
        target_name = f" on {furn.appearance_name}" if furn else ""
        caller.msg(f"{colored_self(caller, True)} lie down{target_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} lies down{target_name}.")
            ensure_regen_timer(caller)
        caller.check_autowhere(old_loc, old_x, old_y, old_z)


class CmdStand(Command):
    key = "stand"
    aliases = ["getup"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        pose = getattr(caller, "pose", "standing")
        if pose == "sleeping":
            caller.msg(f"{colored_self(caller, True)} are fast asleep. You must WAKE up first.")
            return
        if pose == "standing":
            caller.msg(f"{colored_self(caller, True)} are already standing.")
            return

        spot = _find_adjacent_free_spot(caller)
        furn = _find_furniture_under(caller)
        if spot:
            caller.db.pos_x, caller.db.pos_y = spot

        if not caller.set_pose("standing"):
            caller.msg(f"{colored_self(caller, True)} cannot stand up right now.")
            return
        from_name = f" from {furn.appearance_name}" if furn else ""
        caller.msg(f"{colored_self(caller, True)} stand up{from_name}.")
        if caller.location:
            _announce_pose(caller, f"{caller.appearance_name} stands up{from_name}.")
            ensure_regen_timer(caller)
        caller.check_autowhere(old_loc, old_x, old_y, old_z)


class CmdRotate(Command):
    key = "rotate"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        arg = self.args.strip()
        if not arg:
            caller.msg("Usage: rotate <furniture>")
            return
        obj = caller.search(arg, candidates=caller.location.contents if caller.location else [])
        if not obj or not obj.is_typeclass("typeclasses.furniture.Furniture"):
            caller.msg(f"Could not find furniture '{arg}' here.")
            return
        if not obj.visible_to(caller):
            caller.msg(f"Could not find furniture '{arg}' here.")
            return
        if not _is_near(caller, obj):
            caller.msg(f"{obj.appearance_name} is too far away. You need to be right next to it.")
            return
        success, msg = obj.rotate(viewer=caller)
        caller.msg(msg)
