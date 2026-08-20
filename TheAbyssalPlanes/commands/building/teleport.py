from evennia.commands.default.building import CmdTeleport
from combat.movement import find_nearest_unoccupied_coord
from combat.grid import is_valid_coord


class CmdBuilderTeleport(CmdTeleport):
    """
    Teleport to another location or specific coordinates.

    Usage:
      teleport <target>
      teleport <x> <y> [z]
      teleport <target> = <destination>
      teleport <target> = <x> <y> [z]

    Switches:
      quiet - don't echo leave/arrival messages
    """
    key = "teleport"
    aliases = ["tp"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        parts = args.split("=")
        lhs = parts[0].strip()
        rhs = parts[1].strip() if len(parts) > 1 else ""

        # Case 1: teleport x y [z]
        if not rhs:
            coord_parts = lhs.split()
            if len(coord_parts) in (2, 3) and all(p.lstrip("-").isdigit() for p in coord_parts):
                x = int(coord_parts[0])
                y = int(coord_parts[1])
                z = int(coord_parts[2]) if len(coord_parts) == 3 else 1

                room = caller.location
                if not room:
                    caller.msg("You are not anywhere.")
                    return
                if not is_valid_coord(room, x, y):
                    caller.msg("That coordinate is out of bounds.")
                    return

                target_coord = find_nearest_unoccupied_coord(room, x, y, z=z, ignore=caller, mover=caller)
                caller.db.pos_x, caller.db.pos_y = target_coord
                caller.db.pos_z = z
                caller.msg(f"You teleport to coordinates ({target_coord[0]}, {target_coord[1]}, {z}).")
                if caller.db.is_autowhere:
                    from combat.map_renderer import render_map
                    caller.msg(render_map(caller))
                return

        # Case 2: teleport target = x y [z]
        if rhs:
            coord_parts = rhs.split()
            if len(coord_parts) in (2, 3) and all(p.lstrip("-").isdigit() for p in coord_parts):
                x = int(coord_parts[0])
                y = int(coord_parts[1])
                z = int(coord_parts[2]) if len(coord_parts) == 3 else 1

                target_obj = caller.search(lhs)
                if not target_obj:
                    return
                room = caller.location
                if not room:
                    caller.msg("You are not anywhere.")
                    return
                if not is_valid_coord(room, x, y):
                    caller.msg("That coordinate is out of bounds.")
                    return

                target_coord = find_nearest_unoccupied_coord(room, x, y, z=z, ignore=target_obj, mover=target_obj)
                target_obj.db.pos_x, target_obj.db.pos_y = target_coord
                target_obj.db.pos_z = z
                caller.msg(f"Teleported {target_obj.name} to ({target_coord[0]}, {target_coord[1]}, {z}).")
                if hasattr(target_obj, "msg"):
                    target_obj.msg(f"You have been teleported to ({target_coord[0]}, {target_coord[1]}, {z}).")
                return

        super().func()
