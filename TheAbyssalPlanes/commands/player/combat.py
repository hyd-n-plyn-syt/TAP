from evennia import Command

from combat.grid import CANONICAL_DIRECTION, DIRECTION_OFFSETS, get_room_floor_z, get_room_max_z, is_valid_coord
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


class CmdMove(Command):
    """
    Move within the grid.
    Usage:
        MOVE <x> <y> [z]
        MOVE <direction>    -- N, S, E, W, NE, NW, SE, SW (one grid)
        MOVE <up|down>      -- fly vertically (requires flight)
        MOVE stop           -- cancel current movement
    """
    key = "move"

    def func(self):
        parts = self.args.strip().split()
        if not parts:
            self.caller.msg("Usage: MOVE <x> <y> [z] | MOVE <direction> | MOVE up | MOVE down | MOVE stop")
            return

        arg = parts[0].lower()
        if arg == "stop":
            self._stop()
        elif arg in DIRECTION_OFFSETS:
            self._move_direction(arg)
        else:
            self._move_coords(parts)

    def _stop(self):
        caller = self.caller
        caller.db.is_approaching = None
        if not getattr(caller.db, "navigation", None) and not getattr(caller.db, "nav_queue", None):
            caller.msg("You aren't moving.")
            return
        caller.db.navigation = None
        caller.db.nav_queue = None
        caller.msg("You stop moving.")

    def _move_direction(self, direction):
        caller = self.caller
        caller.db.is_approaching = None
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

        from combat.grid import exit_direction, get_exit_coords
        canonical = CANONICAL_DIRECTION.get(direction, direction)
        for obj in room.contents:
            if not getattr(obj, "destination", None):
                continue
            if exit_direction(obj) == canonical:
                coords = get_exit_coords(room, obj)
                if coords and (int(cx), int(cy)) == (int(coords[0]), int(coords[1])):
                    obj.at_traverse(caller, obj.destination)
                    return

        tx, ty = cx + dx, cy + dy
        if not is_valid_coord(room, tx, ty):
            caller.msg("You cannot move that way.")
            return
        mode = "flying" if caller.db.is_flying else "walking"
        start_navigation(caller, tx, ty, movement_mode=mode, delta_x=dx, delta_y=dy)

    def _move_coords(self, parts):
        caller = self.caller
        caller.db.is_approaching = None
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


class CmdShove(Command):
    """
    Shove a character or object in the opposite direction from you.
    Usage:
        SHOVE <target>
    """
    key = "shove"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Shove what?")
            return
        caller = self.caller
        room = caller.location
        if not room:
            return
        results = caller.search(self.args.strip(), quiet=True)
        target = results[0] if results else None
        through_exit = None
        if not target:
            from combat.grid import get_entry_coords
            from combat.movement import is_grid_occupied
            for obj in room.contents:
                if not getattr(obj, "destination", None):
                    continue
                dest_room = obj.destination
                if not dest_room:
                    continue
                return_exit = None
                for r_obj in dest_room.contents:
                    if getattr(r_obj, "destination", None) == room:
                        return_exit = r_obj
                        break
                if not return_exit:
                    continue
                entry = get_entry_coords(dest_room, return_exit.key)
                if not entry:
                    continue
                blockers = is_grid_occupied(dest_room, entry[0], entry[1])
                for b in blockers:
                    match = self.args.strip().lower()
                    if (match in b.key.lower()
                            or match in (getattr(b, "appearance_name", None) or "").lower()
                            or match in (getattr(b.db, "species_key", None) or "").lower()):
                        target = b
                        through_exit = obj
                        break
                if target:
                    break
            if not target:
                caller.msg(f"Could not find '{self.args.strip()}'.")
                return
        if target == caller:
            caller.msg("You can't shove yourself.")
            return
        if through_exit:
            from combat.grid import get_exit_at_coord as _get_exit, get_entry_coords, get_room_grid_size
            dest_room = through_exit.destination
            return_exit = None
            for obj in dest_room.contents:
                if obj.destination == room:
                    return_exit = obj
                    break

            if not return_exit:
                caller.msg("The way is blocked.")
                return

            entry = get_entry_coords(dest_room, return_exit.key)
            if not entry:
                caller.msg("The way is blocked.")
                return

            blockers = is_grid_occupied(dest_room, entry[0], entry[1], mover=target)
            if not blockers:
                caller.msg(f"{target.key} isn't there anymore.")
                return

            entry_x, entry_y = entry
            dx = entry_x - (room.db.pos_x or 0) if hasattr(room.db, "pos_x") else 0
            dy = entry_y - (room.db.pos_y or 0) if hasattr(room.db, "pos_y") else 0
            from combat.grid import exit_direction
            edir = exit_direction(through_exit)
            OFFSETS = {
                "north": (0, 1), "south": (0, -1),
                "east": (1, 0), "west": (-1, 0),
                "northeast": (1, 1), "northwest": (-1, 1),
                "southeast": (1, -1), "southwest": (-1, -1),
            }
            push_x, push_y = OFFSETS.get(edir, (0, 1))

            dw, dh = get_room_grid_size(dest_room)
            landing_x = entry_x + push_x
            landing_y = entry_y + push_y

            if not (0 <= landing_x < dw and 0 <= landing_y < dh):
                landing_x = entry_x
                landing_y = entry_y

            blockers_land = is_grid_occupied(dest_room, landing_x, landing_y, ignore=target, mover=target)
            if blockers_land:
                blocker_name = getattr(blockers[0], "appearance_name", None) or blockers[0].key
                caller.msg(f"{blocker_name} is in the way.")
                return

            target_name = getattr(target, "appearance_name", None) or target.key
            caller.msg(f"You shove {target_name} through the {through_exit.key}.")
            if hasattr(target, "msg"):
                direction = ""
                if push_x > 0 and push_y > 0: direction = "northeast"
                elif push_x > 0 and push_y < 0: direction = "southeast"
                elif push_x < 0 and push_y > 0: direction = "northwest"
                elif push_x < 0 and push_y < 0: direction = "southwest"
                elif push_x > 0: direction = "east"
                elif push_x < 0: direction = "west"
                elif push_y > 0: direction = "north"
                elif push_y < 0: direction = "south"
                target.msg(f"You are shoved {direction}.")

            target.db.pos_x = landing_x
            target.db.pos_y = landing_y
            return

        if not getattr(target.db, "pos_x", None) and not getattr(target.db, "pos_y", None):
            caller.msg(f"{target.key} has no position.")
            return

        cx = caller.db.pos_x or 0
        cy = caller.db.pos_y or 0
        tx = target.db.pos_x or 0
        ty = target.db.pos_y or 0

        dx = tx - cx
        dy = ty - cy
        if dx == 0 and dy == 0:
            caller.msg("You're on top of each other. Use a direction instead.")
            return

        push_x = 0
        push_y = 0
        if dx > 0: push_x = 1
        elif dx < 0: push_x = -1
        if dy > 0: push_y = 1
        elif dy < 0: push_y = -1

        dest_x = tx + push_x
        dest_y = ty + push_y

        from combat.grid import is_valid_coord, get_exit_at_coord, get_entry_coords, get_room_grid_size, exit_direction
        from combat.movement import is_grid_occupied

        target_exit = get_exit_at_coord(room, tx, ty)
        if target_exit and target_exit.destination:
            edir = exit_direction(target_exit)
            aligned = False
            if edir == "north" and push_y > 0: aligned = True
            elif edir == "south" and push_y < 0: aligned = True
            elif edir == "east" and push_x > 0: aligned = True
            elif edir == "west" and push_x < 0: aligned = True
            elif edir == "northeast" and push_x > 0 and push_y > 0: aligned = True
            elif edir == "northwest" and push_x < 0 and push_y > 0: aligned = True
            elif edir == "southeast" and push_x > 0 and push_y < 0: aligned = True
            elif edir == "southwest" and push_x < 0 and push_y < 0: aligned = True

            is_door = getattr(target_exit.db, "is_door", False)
            is_open = getattr(target_exit.db, "is_open", False)
            if aligned and is_door and not is_open:
                target_name = getattr(target, "appearance_name", None) or target.key
                door_name = f"{target_exit.key} door"
                caller.msg(f"You shove {target_name} into the {door_name}.")
                if hasattr(target, "msg"):
                    target.msg(f"You are shoved into the {door_name}.")
                return

            if aligned:
                dest_room = target_exit.destination
                target_name = getattr(target, "appearance_name", None) or target.key
                caller.msg(f"You shove {target_name} through the {target_exit.key}.")
                if hasattr(target, "msg"):
                    direction = ""
                    if push_x > 0 and push_y > 0: direction = "northeast"
                    elif push_x > 0 and push_y < 0: direction = "southeast"
                    elif push_x < 0 and push_y > 0: direction = "northwest"
                    elif push_x < 0 and push_y < 0: direction = "southwest"
                    elif push_x > 0: direction = "east"
                    elif push_x < 0: direction = "west"
                    elif push_y > 0: direction = "north"
                    elif push_y < 0: direction = "south"
                    target.msg(f"You are shoved {direction}.")

                return_exit = None
                for obj in dest_room.contents:
                    if obj.destination == room:
                        return_exit = obj
                        break

                if return_exit:
                    entry = get_entry_coords(dest_room, return_exit.key)
                    if entry:
                        blockers = is_grid_occupied(dest_room, entry[0], entry[1], mover=target)
                        if blockers:
                            blocker_name = getattr(blockers[0], "appearance_name", None) or blockers[0].key
                            caller.msg(f"{blocker_name} is blocking the way on the other side.")
                            return

                        entry_x, entry_y = entry
                        landing_x = entry_x + push_x
                        landing_y = entry_y + push_y
                        dw, dh = get_room_grid_size(dest_room)
                        if 0 <= landing_x < dw and 0 <= landing_y < dh:
                            target.db.pos_x = landing_x
                            target.db.pos_y = landing_y
                        else:
                            target.db.pos_x = entry_x
                            target.db.pos_y = entry_y
                    else:
                        target.db.pos_x = 0
                        target.db.pos_y = 0
                else:
                    target.db.pos_x = 0
                    target.db.pos_y = 0

                target.move_to(dest_room)
                return

        if not is_valid_coord(room, dest_x, dest_y):
            name = getattr(target, "appearance_name", None) or target.key
            caller.msg(f"You shove {name} into the wall.")
            return

        blockers = is_grid_occupied(room, dest_x, dest_y, ignore=target, mover=target)
        if blockers:
            blocker_name = getattr(blockers[0], "appearance_name", None) or blockers[0].key
            target_name = getattr(target, "appearance_name", None) or target.key
            caller.msg(f"You shove {target_name} into {blocker_name}.")
            return

        target.db.pos_x = dest_x
        target.db.pos_y = dest_y
        target_name = getattr(target, "appearance_name", None) or target.key
        caller.msg(f"You shove {target_name}.")
        if hasattr(target, "msg"):
            direction = ""
            if push_x > 0 and push_y > 0: direction = "northeast"
            elif push_x > 0 and push_y < 0: direction = "southeast"
            elif push_x < 0 and push_y > 0: direction = "northwest"
            elif push_x < 0 and push_y < 0: direction = "southwest"
            elif push_x > 0: direction = "east"
            elif push_x < 0: direction = "west"
            elif push_y > 0: direction = "north"
            elif push_y < 0: direction = "south"
            target.msg(f"You are shoved {direction}.")


class CmdAttack(Command):
    """
    Attack a target with a combat skill.
    Usage:
        ATTACK <target>
        ATTACK <skill> <target>
    Queues up to 3 actions. Actions consume time from your 6-second round.
    """
    key = "attack"
    aliases = ["punch", "kick", "headbutt", "knee", "axehandle", "haymaker"]
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Attack what?")
            return

        caller = self.caller
        room = caller.location
        if not room:
            return

        skill_key = self.cmdstring.lower()
        if skill_key == "attack":
            skill_key = "punch"
            target_name = self.args.strip()
        else:
            target_name = self.args.strip()

        from world.data.skills import get_skill
        skill_info = get_skill(skill_key)
        if not skill_info:
            self.msg(f"Unknown skill: {skill_key}")
            return

        results = caller.search(target_name, quiet=True)
        target = results[0] if results else None
        if not target:
            self.msg(f"Could not find '{target_name}'.")
            return

        if target == caller:
            self.msg("You can't attack yourself.")
            return

        from combat.actions import queue_action
        success, msg = queue_action(caller, "attack", skill_key, target)
        self.msg(msg)

        if success:
            from combat.timers import engage_combat
            engage_combat(caller, target)
            caller.db.combat_target = target
