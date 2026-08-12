from commands.command import Command
from combat.movement import ensure_combat_loop, is_grid_occupied
from combat.grid import is_valid_coord
from evennia.utils.ansi import strip_ansi


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
    tiles = _get_furniture_tiles(furn)

    free_tiles = []
    for tx, ty in tiles:
        occupants = [
            obj for obj in room.contents
            if obj is not caller
            and getattr(obj, "is_creature", False)
            and getattr(obj.db, "pos_x", None) == tx
            and getattr(obj.db, "pos_y", None) == ty
        ]
        if not occupants:
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
        if is_valid_coord(room, nx, ny) and not is_grid_occupied(room, nx, ny, ignore=caller):
            return (nx, ny)
    return None


class CmdSit(Command):
    key = "sit"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        old_loc, old_x, old_y, old_z = caller.location, caller.db.pos_x, caller.db.pos_y, caller.db.pos_z
        furn = _find_furniture(caller, self.args.strip())
        if furn:
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "sit" not in allowed and "sitting" not in allowed:
                caller.msg(f"You can't comfortably sit in {furn.get_display_name()}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.get_display_name()} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("sitting"):
            caller.msg("You cannot sit down right now.")
            return
        target_name = f" on {furn.get_display_name()}" if furn else ""
        caller.msg(f"You sit down{target_name}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} sits down{target_name}.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)
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
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "rest" not in allowed and "resting" not in allowed:
                caller.msg(f"You can't comfortably rest on {furn.get_display_name()}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.get_display_name()} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("resting"):
            caller.msg("You cannot rest right now.")
            return
        target_name = f" on {furn.get_display_name()}" if furn else ""
        caller.msg(f"You settle in to rest{target_name}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} settles in to rest{target_name}.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)
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
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "sleep" not in allowed and "sleeping" not in allowed:
                caller.msg(f"You can't comfortably sleep in {furn.get_display_name()}; you'd need a bed.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.get_display_name()} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if caller.state() != "normal":
            caller.set_state("normal")
            caller.msg("You pull your awareness back to your original plane.")
        if not caller.set_pose("sleeping"):
            caller.msg("You cannot sleep right now.")
            return
        target_name = f" on {furn.get_display_name()}" if furn else ""
        caller.msg(f"You drift off to sleep{target_name}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} falls asleep{target_name}.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)
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
            caller.msg("You are already awake and standing.")
            return
        furn = _find_furniture_under(caller)
        if furn:
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "lay" not in allowed and "laying" not in allowed:
                caller.msg(f"You can't comfortably lie on {furn.get_display_name()}.")
                return
        if not caller.set_pose("laying"):
            caller.msg("You cannot wake up right now.")
            return
        target_name = f" on {furn.get_display_name()}" if furn else " on the ground"
        caller.msg(f"You wake up and lie{target_name}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} wakes up and lies down.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)


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
            allowed = [s.lower() for s in getattr(furn, "allowed_states", [])]
            if "lay" not in allowed and "laying" not in allowed and "lie" not in allowed:
                caller.msg(f"You can't comfortably lie down on {furn.get_display_name()}.")
                return
            sx_sy = _get_furniture_seat_coord(caller, furn)
            if not sx_sy:
                caller.msg(f"{furn.get_display_name()} is fully occupied.")
                return
            sx, sy = sx_sy
            caller.db.pos_x, caller.db.pos_y = sx, sy

        if not caller.set_pose("laying"):
            caller.msg("You cannot lie down right now.")
            return
        target_name = f" on {furn.get_display_name()}" if furn else ""
        caller.msg(f"You lie down{target_name}.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} lies down{target_name}.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)
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
            caller.msg("You are fast asleep. You must WAKE up first.")
            return
        if pose == "standing":
            caller.msg("You are already standing.")
            return

        spot = _find_adjacent_free_spot(caller)
        if spot:
            caller.db.pos_x, caller.db.pos_y = spot

        if not caller.set_pose("standing"):
            caller.msg("You cannot stand up right now.")
            return
        caller.msg("You stand up.")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.appearance_name} stands up.",
                exclude=(caller,),
            )
            ensure_combat_loop(caller.location)
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
        success, msg = obj.rotate()
        caller.msg(msg)
