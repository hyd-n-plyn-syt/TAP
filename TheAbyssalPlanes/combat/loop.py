from evennia import DefaultScript
from evennia.objects.models import ObjectDB

from combat.grid import get_exit_coords, get_room_floor_z, is_valid_coord
from combat.movement import (
    GLOBAL_ROUND_DURATION,
    MAX_GRIDS_PER_ROUND,
    SUB_TICK_RATE,
    announce_grid_arrival,
    announce_grid_move,
    ensure_combat_loop,
    is_grid_occupied,
    mover_arrival_message,
    mover_start_message,
)
from combat.map_renderer import render_map
from world.systems import stats


class CombatLoop(DefaultScript):
    """
    A persistent script that manages combat AND movement in a room.

    Runs every second (one sub-tick of a 6-second round). On each tick it:
      1. Advances the round counter (1-6); on tick 1 it refreshes each
         actor's round movement allowance.
      2. Advances any actor navigating toward an exit coordinate by one
         grid; when they arrive, they traverse the exit.
      3. Lets each engaged combatant resolve their next queued action.
    It stops itself once nobody is moving or fighting any longer.
    """

    def at_script_creation(self):
        self.key = "combat_loop"
        self.interval = SUB_TICK_RATE
        self.persistent = False
        self.db.current_tick = 0

    def at_repeat(self, *args, **kwargs):
        room = self.obj
        if not room:
            self.stop()
            return

        tick = (self.db.current_tick or 0) + 1
        if tick > GLOBAL_ROUND_DURATION:
            tick = 1
        self.db.current_tick = tick

        if tick == 1:
            for char in room.contents:
                if getattr(char, "db", None) and getattr(char.db, "movement_used", None):
                    char.db.movement_used = 0

        # 1-minute regeneration tick (60 seconds)
        regen_secs = (self.db.regen_secs or 0) + 1
        if regen_secs >= 60:
            self.db.regen_secs = 0
            from world.data import species as species_data
            for char in room.contents:
                if not getattr(char, "is_creature", False):
                    continue
                pose = getattr(char, "pose", "standing")
                if pose == "sleeping":
                    mult = 2.0
                elif pose in ("resting", "laying", "sitting"):
                    mult = 1.5
                else:
                    mult = 1.0

                furniture_bonus = 0.0
                cx = getattr(char.db, "pos_x", 0)
                cy = getattr(char.db, "pos_y", 0)
                for obj in room.contents:
                    if obj.is_typeclass("typeclasses.furniture.Furniture"):
                        is_nearby = False
                        if hasattr(obj, "is_at_coord") and obj.is_at_coord(cx, cy):
                            is_nearby = True
                        else:
                            fx = getattr(obj.db, "pos_x", 0)
                            fy = getattr(obj.db, "pos_y", 0)
                            if max(abs(cx - fx), abs(cy - fy)) <= 1:
                                is_nearby = True
                        if is_nearby:
                            allowed = getattr(obj, "allowed_states", [])
                            pose_map = {
                                "resting": ["resting", "rest"],
                                "sleeping": ["sleeping", "sleep"],
                                "laying": ["laying", "lay"],
                                "sitting": ["sitting", "sit"],
                            }
                            match_states = pose_map.get(pose, [pose])
                            if any(st in allowed for st in match_states):
                                q = getattr(obj, "quality", 1.0)
                                furniture_bonus = max(furniture_bonus, q)

                effective_mult = mult * (1.0 + furniture_bonus)

                zeroed = species_data.zeroed_pools(char.species_key)
                for pool in stats.POOL_KEYS:
                    if pool in zeroed:
                        continue
                    base_regen = getattr(char, f"{pool}_regen", 1)
                    regen_val = int(round(base_regen * effective_mult))
                    if regen_val < 1 and base_regen > 0:
                        regen_val = 1
                    maxv = getattr(char, pool, 0)
                    cur = char.pools_current[pool]
                    if cur < maxv:
                        new_cur = min(maxv, cur + regen_val)
                        char.set_pool(pool, new_cur)
        else:
            self.db.regen_secs = regen_secs

        active = False
        for char in room.contents:
            if not getattr(char, "db", None):
                continue
            if getattr(char.db, "navigation", None):
                active = True
                self.process_navigation(char)
            if getattr(char.db, "combat_target", None):
                active = True
                self.resolve_tick(char)
            pose = getattr(char, "pose", "standing")
            if pose in ("resting", "sleeping", "laying"):
                active = True
            for pool in stats.POOL_KEYS:
                maxv = getattr(char, pool, 0)
                if char.pools_current[pool] < maxv:
                    active = True

        if not active:
            self.stop()

    def process_navigation(self, char):
        """Advance an actor one grid toward their navigation destination."""
        nav = char.db.navigation
        if not nav:
            return
        room = char.location
        if not room or room.id != self.obj.id:
            char.db.navigation = None
            return

        approach_target = getattr(char.db, "is_approaching", None)
        if approach_target:
            tx = getattr(approach_target.db, "pos_x", None)
            ty = getattr(approach_target.db, "pos_y", None)
            if tx is not None and ty is not None:
                nav["dest_x"] = int(tx)
                nav["dest_y"] = int(ty)
                char.db.navigation = nav

        used = char.db.movement_used or 0
        if used >= MAX_GRIDS_PER_ROUND:
            char.msg("|rYou have used all your movement for this round.|n")
            return

        dx = int(nav["dest_x"] - (char.db.pos_x or 0))
        dy = int(nav["dest_y"] - (char.db.pos_y or 0))
        dest_z = nav.get("dest_z")
        dz = (int(dest_z) - int(char.db.pos_z or 0)) if dest_z is not None else 0

        if dx == 0 and dy == 0 and dz == 0:
            exit_obj = None
            if nav.get("exit_dbref"):
                try:
                    exit_obj = ObjectDB.objects.get(id=nav["exit_dbref"])
                except ObjectDB.DoesNotExist:
                    exit_obj = None
            char.db.navigation = None
            if exit_obj and exit_obj.destination:
                is_door = getattr(exit_obj.db, "is_door", False)
                is_open = getattr(exit_obj.db, "is_open", False)
                if is_door and not is_open:
                    is_locked = getattr(exit_obj.db, "is_locked", False)
                    if nav.get("pending_autoopen") and (not is_locked or exit_obj._has_key(char)):
                        exit_obj.open_door(char)
                        if getattr(exit_obj.db, "is_open", False):
                            char.move_to(exit_obj.destination)
                        else:
                            char.msg("You couldn't open the door.")
                    else:
                        char.msg(f"{exit_obj.key} is closed.")
                else:
                    char.move_to(exit_obj.destination)
            else:
                char.msg(mover_arrival_message(room, nav, char))
            self._drain_nav_queue(char)
            return

        nx = char.db.pos_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        ny = char.db.pos_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        if not is_valid_coord(room, nx, ny):
            char.msg("You cannot move that way.")
            char.db.navigation = None
            self._drain_nav_queue(char)
            return

        blockers = is_grid_occupied(room, nx, ny, ignore=char)
        if blockers:
            name = getattr(blockers[0], "appearance_name", None) or blockers[0].key
            char.msg(f"You can't move there. {name} occupies that space.")
            char.db.navigation = None
            self._drain_nav_queue(char)
            return

        char.db.pos_x, char.db.pos_y = nx, ny
        if dz != 0:
            char.db.pos_z = char.db.pos_z + (1 if dz > 0 else -1)
            if char.db.pos_z <= get_room_floor_z(room):
                char.db.is_flying = False
                nav["movement_mode"] = "walking"
        
        if nav.get("movement_mode") == "takeoff":
            nav["movement_mode"] = "flying"
        
        char.db.movement_used = used + 1
        char.db.navigation = nav
        
        if char.db.is_autowhere:
            char.msg(render_map(char))
            
        if nav.get("exit_dbref"):
            announce_grid_move(char, nav)
        elif dz != 0:
            announce_grid_move(char, nav)
            if nx == nav["dest_x"] and ny == nav["dest_y"]:
                announce_grid_arrival(char, nav)
                char.msg(mover_arrival_message(room, nav, char))
                char.db.navigation = None
                self._drain_nav_queue(char)
        elif nx == nav["dest_x"] and ny == nav["dest_y"]:
            announce_grid_arrival(char, nav)
            char.msg(mover_arrival_message(room, nav, char))
            char.db.navigation = None
            self._drain_nav_queue(char)
        else:
            announce_grid_move(char, nav)

    def _drain_nav_queue(self, char):
        """Pop the next queued navigation for this character, if any."""
        from combat.grid import is_valid_coord
        room = char.location
        queue = list(getattr(char.db, "nav_queue", None) or [])
        while queue:
            next_nav = queue.pop(0)
            if "delta_x" in next_nav and "delta_y" in next_nav:
                cx = char.db.pos_x or 0
                cy = char.db.pos_y or 0
                next_nav["dest_x"] = cx + next_nav["delta_x"]
                next_nav["dest_y"] = cy + next_nav["delta_y"]
            if not is_valid_coord(room, next_nav["dest_x"], next_nav["dest_y"]):
                char.msg("Your path is blocked.")
                continue
            char.db.nav_queue = queue if queue else None
            char.db.navigation = next_nav
            if room:
                char.msg(mover_start_message(room, next_nav, char))
                ensure_combat_loop(room)
            return
        char.db.nav_queue = None

    def resolve_tick(self, char):
        """Process a single combatant's sub-tick."""
        from combat.actions import pop_action, set_actions_used
        from combat.accuracy import resolve_hit, check_range
        from combat.damage import calculate_base_damage, get_armor_value, apply_damage, check_critical
        from world.data import skills as skill_data

        action, time_cost = pop_action(char)
        if not action:
            return

        if time_cost > 0:
            used = char.db.movement_used or 0
            set_actions_used(char, used + time_cost)

        if action["type"] == "attack":
            skill_info_cost = skill_data.get_skill(action["skill"])
            if skill_info_cost:
                pool_cost = skill_info_cost.get("pool_cost", 0)
                health_bar_cost = skill_info_cost.get("health_bar")
                if pool_cost > 0 and health_bar_cost:
                    from world.data.species import resolve_pool
                    eff_pool = resolve_pool(getattr(char.db, "species_key", ""), health_bar_cost)
                    cur = getattr(char.db, f"{eff_pool}_current", None)
                    if cur is None:
                        from world.systems.stats import derived_pools
                        cur = derived_pools(char).get(eff_pool, 0)
                    setattr(char.db, f"{eff_pool}_current", max(0, cur - pool_cost))

        if action["type"] != "attack":
            return

        skill_key = action["skill"]
        target_dbref = action.get("target_dbref")
        if not target_dbref:
            return

        from evennia.objects.models import ObjectDB
        try:
            target = ObjectDB.objects.get(id=target_dbref)
        except ObjectDB.DoesNotExist:
            return

        if not target.location or target.location != char.location:
            char.msg(f"{target.key} is no longer here.")
            return

        skill_value = getattr(char.db, "skills", {}).get(skill_key, 0)

        in_range, distance = check_range(char, target, skill_key)
        if not in_range:
            skill_info_temp = skill_data.get_skill(skill_key)
            reach = skill_info_temp.get("reach", 0) if skill_info_temp else 0
            char.msg(f"{target.key} is out of range (distance {distance}, need {reach}).")
            return

        hit, attack_roll, defense_roll, is_crit = resolve_hit(char, target, skill_key, skill_value)

        skill_info = skill_data.get_skill(skill_key)
        skill_name = skill_info["name"] if skill_info else skill_key

        if not hit:
            char.msg(f"You miss {target.key} with {skill_name}.")
            if hasattr(target, "msg"):
                target.msg(f"{char.key} misses you with {skill_name}.")
            for observer in char.location.contents:
                if observer in (char, target):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(f"{char.key} misses {target.key} with {skill_name}.")
            return

        base_damage, damage_type, health_bar = calculate_base_damage(char, skill_key, skill_value)
        if base_damage <= 0 or not health_bar:
            char.msg(f"Your {skill_name} has no effect.")
            return

        armor = get_armor_value(target, damage_type) if not is_crit else 0
        final_damage = int(round(max(0, base_damage - armor)))

        if final_damage <= 0:
            char.msg(f"Your {skill_name} is blocked by {target.key}'s armor.")
            if hasattr(target, "msg"):
                target.msg(f"{char.key}'s {skill_name} is blocked by your armor.")
            for observer in char.location.contents:
                if observer in (char, target):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(f"{char.key}'s {skill_name} is blocked by {target.key}'s armor.")
            return

        remaining, knocked_out = apply_damage(target, health_bar, final_damage, is_crit)

        crit_text = " (CRITICAL)" if is_crit else ""
        char.msg(f"You hit {target.key} with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}")
        if hasattr(target, "msg"):
            target.msg(f"{char.key} hits you with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}")
        for observer in char.location.contents:
            if observer in (char, target):
                continue
            if hasattr(observer, "msg"):
                observer.msg(f"{char.key} hits {target.key} with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}")

        if knocked_out:
            target.msg(f"You are knocked out!")
            char.msg(f"You knock out {target.key}!")
            for observer in char.location.contents:
                if observer in (char, target):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(f"{target.key} is knocked out!")
