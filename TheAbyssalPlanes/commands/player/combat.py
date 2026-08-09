from evennia import Command

from combat.grid import DIRECTION_OFFSETS, get_room_floor_z, get_room_max_z, is_valid_coord
from combat.movement import start_navigation
from combat.queue_mgmt import QueueHandler


class CmdCombatAction(Command):
    """
    Hostile combat action trigger.
    Usage:
        <skill> <target>
    """
    key = "combat_action"

    def func(self):
        # Dynamically named skill
        skill = self.cmdstring
        target = self.args.strip()

        # 1. Update target if provided
        if target:
            found = self.caller.search(target)
            if found:
                self.caller.db.combat_target = found

        # 2. Queue the action
        QueueHandler(self.caller).parse_input(skill)
        self.caller.msg(f"Queued {skill} on {self.caller.db.combat_target}.")


class CmdApproach(Command):
    """
    Approach a target.
    Usage:
        APPROACH <target>
        APPROACH
    """
    key = "approach"

    def func(self):
        target = self.caller.db.combat_target
        if self.args.strip():
            found = self.caller.search(self.args.strip())
            if not found:
                self.caller.msg("You don't see that here.")
                return
            target = found
        if not target:
            self.caller.msg("You are not approaching anyone.")
            return
        self.caller.db.combat_target = target
        self.caller.db.is_approaching = target
        
        tx = getattr(target.db, "pos_x", None)
        ty = getattr(target.db, "pos_y", None)
        if tx is None or ty is None:
            self.caller.msg(f"{target.name} has no position.")
            return
        
        mode = "flying" if self.caller.db.is_flying else "walking"
        start_navigation(self.caller, tx, ty, movement_mode=mode)
        self.caller.msg(f"You start approaching {target.name}.")


class CmdMove(Command):
    """
    Move within the grid.
    Usage:
        MOVE <x> <y> [z]
        MOVE <direction>    -- N, S, E, W, NE, NW, SE, SW (one grid)
        MOVE <up|down>      -- fly vertically (requires flight)
    """
    key = "move"

    def func(self):
        parts = self.args.strip().split()
        if not parts:
            self.caller.msg("Usage: MOVE <x> <y> [z] | MOVE <direction> | MOVE up | MOVE down")
            return

        if parts[0].lower() in DIRECTION_OFFSETS:
            self._move_direction(parts[0].lower())
        else:
            self._move_coords(parts)

    def _move_direction(self, direction):
        caller = self.caller
        room = caller.location
        dx, dy, dz = DIRECTION_OFFSETS[direction]
        cx = caller.db.pos_x or 0
        cy = caller.db.pos_y or 0

        if dz:
            if not caller.db.is_flying:
                caller.msg("You need to be flying to move up or down.")
                return
            tz = (caller.db.pos_z or 1) + dz
            if tz < get_room_floor_z(room):
                caller.msg("You cannot go below the base floor level.")
                return
            if tz > get_room_max_z(room):
                caller.msg("You cannot fly higher than this area allows.")
                return
            start_navigation(caller, cx, cy, z=tz, movement_mode="flying")
            return

        tx, ty = cx + dx, cy + dy
        if not is_valid_coord(room, tx, ty):
            caller.msg("You cannot move that way.")
            return
        mode = "flying" if caller.db.is_flying else "walking"
        start_navigation(caller, tx, ty, movement_mode=mode)

    def _move_coords(self, parts):
        caller = self.caller
        try:
            x, y = int(parts[0]), int(parts[1])
            z = int(parts[2]) if len(parts) > 2 else None
        except (ValueError, IndexError):
            caller.msg("Coordinates must be numbers: MOVE <x> <y> [z]")
            return

        if not is_valid_coord(caller.location, x, y):
            caller.msg("That coordinate is out of bounds.")
            return

        if z is not None:
            if z < get_room_floor_z(caller.location):
                caller.msg("You cannot go below the base floor level.")
                return
            if z > get_room_max_z(caller.location):
                caller.msg("You cannot fly higher than this area allows.")
                return

        mode = "flying" if caller.db.is_flying else "walking"
        start_navigation(caller, x, y, z=z, movement_mode=mode)
