"""
Per-character combat and movement timers for The Abyssal Planes.

Both timers ride on a character's own script handler and clone their
rounds from the universal clock (``world.systems.time``) rather than
running independent wall-clock loops. A character in one room and a
character in another still agree on when rounds begin and end, and both
timers follow their subject across room transitions.

Combat and movement share the 6-second round and the per-round movement
budget; regen runs on its own separate 60-second timer
(``world.systems.regen``) so combat never interferes with it.

Combat states (``char.db.combat_state``):
    idle            -- can fight, not currently engaged
    non_combat      -- cannot fight back (can still be hurt/regenerate)
    in_combat       -- actively fighting someone in the same room
    fled_combat     -- left the room mid-fight
    fled_from_combat-- a combatant you were fighting left the room

Per-engagement detail lives in ``char.engagements`` (a dict keyed by the
partner's dbref) so a busy brawl where one person flees can track each
relationship independently. A fleer has a 5-round (30s) grace measured in
universal rounds: if they reunite in the same room within that window the
fight resumes; otherwise the engagement dissolves.
"""

from evennia import DefaultScript
from evennia.objects.models import ObjectDB

from combat.grid import get_exit_coords, get_room_floor_z, is_valid_coord
from combat.map_renderer import render_map
from combat.movement import (
    SPEED_TICKS,
    announce_grid_arrival,
    announce_grid_move,
    arrival_mover_echo,
    arrival_observer_echo,
    blocked_with_hint,
    capitalize_display_name,
    detour_mover_echo,
    detour_observer_echo,
    direction_from_delta,
    find_path,
    is_grid_occupied,
    move_mover_echo,
    move_observer_echo,
    mover_arrival_message,
    mover_start_message,
)
from world.systems import stats
from world.systems.time import (
    MAX_GRIDS_PER_ROUND,
    now,
    round_number,
    rounds_elapsed,
)

COMBAT_STATES = ("idle", "non_combat", "in_combat", "fled_combat", "fled_from_combat")
FLEE_GRACE_ROUNDS = 5


# ---------------------------------------------------------------------------
# Combat state machine
# ---------------------------------------------------------------------------


def combat_capable(char):
    """True if a creature can fight back (not flagged non_combat)."""
    return getattr(char, "combat_state", "idle") != "non_combat"


def set_non_combat(char):
    """Permanently flag a creature as unable to fight. They can still be
    hurt and regenerated, just never attack back."""
    if not getattr(char, "db", None):
        return
    char.db.combat_state = "non_combat"
    char.engagements = {}
    for script in list(char.scripts.get(key="combat_timer")):
        try:
            script.stop()
        except Exception:
            pass


def refresh_combat_state(char):
    """Recompute the dominant combat_state from the engagement dict."""
    if not getattr(char, "db", None):
        return
    if getattr(char, "combat_state", "idle") == "non_combat":
        return
    engs = getattr(char, "engagements", None) or {}
    if not engs:
        char.db.combat_state = "idle"
        return
    if any(eng.get("state") == "in_combat" for eng in engs.values()):
        char.db.combat_state = "in_combat"
    elif any(eng.get("state") == "fled_from_combat" for eng in engs.values()):
        char.db.combat_state = "fled_from_combat"
    else:
        char.db.combat_state = "fled_combat"


def engage_combat(char, target):
    """Mutual combat engagement between two combat-capable creatures.

    Non-combat targets are skipped (they take damage but never gain a
    combat state). Each engaged fighter gets a CombatTimer.
    """
    if not getattr(char, "is_creature", False) or not getattr(target, "is_creature", False):
        return
    if not combat_capable(char) or not combat_capable(target):
        return
    changed = False
    engs = dict(getattr(char, "engagements", None) or {})
    if engs.get(str(target.id), {}).get("state") != "in_combat":
        engs[str(target.id)] = {"state": "in_combat"}
        char.engagements = engs
        changed = True
    t_engs = dict(getattr(target, "engagements", None) or {})
    if t_engs.get(str(char.id), {}).get("state") != "in_combat":
        t_engs[str(char.id)] = {"state": "in_combat"}
        target.engagements = t_engs
        changed = True
    if changed:
        refresh_combat_state(char)
        refresh_combat_state(target)
    ensure_combat_timer(char)
    ensure_combat_timer(target)


def disengage_combat(char, target=None):
    """End char's combat engagement with *target* (all if target is None).

    Removes it in both directions so neither side keeps a stale entry.
    """
    if not getattr(char, "db", None):
        return
    engs = dict(getattr(char, "engagements", None) or {})
    if target is None:
        engs = {}
    else:
        engs.pop(str(target.id), None)
    char.engagements = engs
    refresh_combat_state(char)
    if target is not None and getattr(target, "db", None):
        t_engs = dict(getattr(target, "engagements", None) or {})
        t_engs.pop(str(char.id), None)
        target.engagements = t_engs
        refresh_combat_state(target)


def mark_flee(char, old_location):
    """A creature just switched rooms while in combat.

    They become ``fled_combat``; combatants left in the old room become
    ``fled_from_combat``. Both sides start a 5-round grace clock.
    """
    if not getattr(char, "is_creature", False):
        return
    engs = dict(getattr(char, "engagements", None) or {})
    fled = False
    for dbid in list(engs):
        if engs[dbid].get("state") == "in_combat":
            engs[dbid]["state"] = "fled_combat"
            engs[dbid]["fled_since"] = now()
            fled = True
    if not fled:
        return
    char.engagements = engs
    refresh_combat_state(char)
    if not old_location:
        return
    for obj in old_location.contents:
        if (
            obj is char
            or not getattr(obj, "is_creature", False)
            or not getattr(obj, "db", None)
        ):
            continue
        other = dict(getattr(obj, "engagements", None) or {})
        entry = other.get(str(char.id))
        if entry and entry.get("state") == "in_combat":
            entry["state"] = "fled_from_combat"
            entry["fled_since"] = now()
            obj.engagements = other
            refresh_combat_state(obj)
            ensure_combat_timer(obj)


def check_engagement_resume(char):
    """Called each tick: reunite fled pairs in the same room, or let the
    5-round grace expire and dissolve the engagement."""
    engs = dict(getattr(char, "engagements", None) or {})
    changed = False
    for dbid, eng in list(engs.items()):
        if eng.get("state") not in ("fled_combat", "fled_from_combat"):
            continue

        partner = None
        try:
            partner = ObjectDB.objects.get(id=int(dbid))
        except (ObjectDB.DoesNotExist, TypeError, ValueError):
            partner = None

        if not partner or not partner.location or partner.location != char.location:
            if eng.get("fled_since") is not None and rounds_elapsed(eng["fled_since"]) >= FLEE_GRACE_ROUNDS:
                del engs[dbid]
                changed = True
                if (
                    getattr(char.db, "combat_target", None)
                    and getattr(char.db, "combat_target").id == int(dbid)
                ):
                    char.db.combat_target = None
                from combat.actions import clear_action_queue
                clear_action_queue(char)
            continue

        paired = dict(getattr(partner, "engagements", None) or {})
        if str(char.id) not in paired:
            del engs[dbid]
            changed = True
            continue

        pe = paired[str(char.id)]
        if pe.get("state") != "in_combat":
            pe["state"] = "in_combat"
            pe.pop("fled_since", None)
            partner.engagements = paired
            refresh_combat_state(partner)
        eng["state"] = "in_combat"
        eng.pop("fled_since", None)
        changed = True

    if changed:
        char.engagements = engs
        refresh_combat_state(char)


# ---------------------------------------------------------------------------
# Timer management
# ---------------------------------------------------------------------------


def _ensure_script(char, key, classpath):
    """Make sure a character has exactly one running script of *key*."""
    existing = list(char.scripts.get(key=key))
    active = [s for s in existing if getattr(s, "db_is_active", False)]
    for script in existing:
        if script not in active:
            try:
                script.delete()
            except Exception:
                pass
    if active:
        return active[0]
    return char.scripts.add(classpath, key=key)


def ensure_combat_timer(char):
    """Make sure *char* has exactly one running CombatTimer."""
    return _ensure_script(char, "combat_timer", "combat.timers.CombatTimer")


def ensure_movement_timer(char):
    """Make sure *char* has exactly one running MovementTimer."""
    return _ensure_script(char, "movement_timer", "combat.timers.MovementTimer")


# ---------------------------------------------------------------------------
# CombatTimer
# ---------------------------------------------------------------------------


class CombatTimer(DefaultScript):
    """
    Per-combatant round timer, cloned from the universal clock.

    Runs while the character is in any combat state, has a live combat
    target, or still has queued hostile actions. Each 6-second universal
    round it refreshes the character's movement budget and resolves the
    next queued action. The fleer/fled-from resume and 5-round grace
    expiry are applied every tick.
    """

    def at_script_creation(self):
        self.key = "combat_timer"
        self.interval = 1
        self.persistent = True
        self.db.last_round = None

    def is_valid(self):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return False
        state = getattr(char, "combat_state", "idle")
        if state in ("in_combat", "fled_combat", "fled_from_combat"):
            return True
        return bool(getattr(char.db, "combat_target", None)) or bool(
            getattr(char.db, "action_queue", None)
        )

    def at_repeat(self, *args, **kwargs):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return
        if not getattr(char, "is_creature", False):
            return
        check_engagement_resume(char)
        current_round = round_number(now())
        if self.db.last_round != current_round:
            self.db.last_round = current_round
            char.db.movement_used = 0
        if getattr(char.db, "action_queue", None):
            self._resolve_tick(char)

    def _resolve_tick(self, char):
        from combat.actions import clear_action_queue, pop_action, set_actions_used
        from combat.accuracy import check_range, resolve_hit
        from combat.damage import (
            apply_damage,
            calculate_base_damage,
            check_critical,
            get_armor_value,
        )
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
                    eff_pool = resolve_pool(
                        getattr(char.db, "species_key", ""), health_bar_cost
                    )
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

        try:
            target = ObjectDB.objects.get(id=target_dbref)
        except ObjectDB.DoesNotExist:
            return

        if not target.location or target.location != char.location:
            engage = (getattr(char, "engagements", None) or {}).get(str(target.id))
            if engage and engage.get("state") != "in_combat":
                return
            char.msg(f"{target.key} is no longer here.")
            disengage_combat(char, target)
            if (
                getattr(char.db, "combat_target", None)
                and getattr(char.db, "combat_target").id == target.id
            ):
                char.db.combat_target = None
            clear_action_queue(char)
            return

        engage_combat(char, target)

        skill_value = getattr(char.db, "skills", {}).get(skill_key, 0)

        in_range, distance = check_range(char, target, skill_key)
        if not in_range:
            skill_info_temp = skill_data.get_skill(skill_key)
            reach = skill_info_temp.get("reach", 0) if skill_info_temp else 0
            char.msg(f"{target.key} is out of range (distance {distance}, need {reach}).")
            return

        hit, attack_roll, defense_roll, is_crit = resolve_hit(
            char, target, skill_key, skill_value
        )

        skill_info = skill_data.get_skill(skill_key)
        skill_name = skill_info["name"] if skill_info else skill_key

        if not hit:
            char.msg(f"You miss {target.key} with {skill_name}.")
            if hasattr(target, "msg"):
                target.msg(f"{char.key} misses you with {skill_name}.")
            for observer in char.location.contents:
                if observer in (char, target) or not getattr(observer, "is_creature", False):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(f"{char.key} misses {target.key} with {skill_name}.")
            return

        base_damage, damage_type, health_bar = calculate_base_damage(
            char, skill_key, skill_value
        )
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
                if observer in (char, target) or not getattr(observer, "is_creature", False):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(
                        f"{char.key}'s {skill_name} is blocked by {target.key}'s armor."
                    )
            return

        remaining, knocked_out = apply_damage(target, health_bar, final_damage, is_crit)

        crit_text = " (CRITICAL)" if is_crit else ""
        char.msg(
            f"You hit {target.key} with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}"
        )
        if hasattr(target, "msg"):
            target.msg(
                f"{char.key} hits you with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}"
            )
        for observer in char.location.contents:
            if observer in (char, target) or not getattr(observer, "is_creature", False):
                continue
            if hasattr(observer, "msg"):
                observer.msg(
                    f"{char.key} hits {target.key} with {skill_name} for {final_damage:.0f} {damage_type} damage!{crit_text}"
                )

        if knocked_out:
            target.msg(f"You are knocked out!")
            char.msg(f"You knock out {target.key}!")
            for observer in char.location.contents:
                if observer in (char, target) or not getattr(observer, "is_creature", False):
                    continue
                if hasattr(observer, "msg"):
                    observer.msg(f"{target.key} is knocked out!")
            disengage_combat(char, target)
            disengage_combat(target, char)
            if (
                getattr(char.db, "combat_target", None)
                and getattr(char.db, "combat_target").id == target.id
            ):
                char.db.combat_target = None


# ---------------------------------------------------------------------------
# MovementTimer
# ---------------------------------------------------------------------------


class MovementTimer(DefaultScript):
    """
    Per-navigator grid movement timer, cloned from the universal clock.

    Advances a character one grid per universal second, capped at the
    6-grid per-round allowance. The allowance refreshes at each universal
    round boundary, so a navigator and a combatant in the same room agree
    on when it resets. Self-stops when navigation and the queue are empty.
    """

    def at_script_creation(self):
        self.key = "movement_timer"
        self.interval = 1
        self.persistent = True
        self.db.last_round = None
        self.db_start_delay = True

    def is_valid(self):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return False
        return bool(getattr(char.db, "navigation", None)) or bool(
            getattr(char.db, "nav_queue", None)
        )

    def at_repeat(self, *args, **kwargs):
        char = self.obj
        if not char or not getattr(char, "db", None):
            return
        if not getattr(char, "is_creature", False):
            return
        current_round = round_number(now())
        if self.db.last_round != current_round:
            self.db.last_round = current_round
            char.db.movement_used = 0
        if getattr(char.db, "navigation", None):
            self._process_navigation(char)

    def _process_navigation(self, char):
        nav = char.db.navigation
        if not nav:
            return
        room = char.location
        if not room:
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

        is_autonav = getattr(char.db, "autonavigate", False)
        is_autofly = getattr(char.db, "autofly", False)
        speed = getattr(char.db, "move_speed", "walk") or "walk"
        is_flying = getattr(char.db, "is_flying", False)

        if is_flying:
            step_every = SPEED_TICKS.get(speed, 3)
        else:
            step_every = SPEED_TICKS.get(speed, 3)

        step_count = nav.get("step_count", 0) + 1
        nav["step_count"] = step_count
        char.db.navigation = nav

        if step_count < step_every:
            return

        nav["step_count"] = 0
        char.db.navigation = nav

        used = char.db.movement_used or 0
        if used >= MAX_GRIDS_PER_ROUND:
            char.msg("|rYou have used all your movement for this round.|n")
            return

        if not nav.get("path") and is_autonav:
            sx = char.db.pos_x or 0
            sy = char.db.pos_y or 0
            dest_z = nav.get("dest_z")
            z_check = int(dest_z) if dest_z is not None else (int(char.db.pos_z or 1) if is_flying else None)
            path, blockers = find_path(
                room, sx, sy, nav["dest_x"], nav["dest_y"],
                z=z_check, ignore=char, mover=char,
            )
            if path and len(path) > 1:
                nav["path"] = path[1:]
                char.db.navigation = nav
            elif blockers:
                if is_autofly and not is_flying and char.db.can_fly:
                    from combat.grid import get_room_max_z
                    cz = char.db.pos_z or 1
                    tz = cz + 1
                    if tz <= get_room_max_z(room):
                        char.db.is_flying = True
                        nav["movement_mode"] = "takeoff"
                        nav["dest_z"] = tz
                        nav["fly_landing_z"] = char.db.pos_z or 1
                        char.db.navigation = nav
                        char.msg("You take off, rising into the air to fly over the obstacle.")
                        ensure_movement_timer(char)
                        return
                char.msg(blocked_with_hint(blockers, is_autonav))
                char.db.navigation = None
                self._drain_nav_queue(char)
                return
            else:
                char.msg("You cannot reach that destination.")
                char.db.navigation = None
                self._drain_nav_queue(char)
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
                char.msg(arrival_mover_echo(char, nav))
                for observer in room.contents:
                    if observer is char or not getattr(observer, "is_creature", False):
                        continue
                    if not char.visible_to(observer):
                        continue
                    observer.msg(arrival_observer_echo(char, nav, observer), from_obj=char)
            self._drain_nav_queue(char)
            return

        nx = char.db.pos_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        ny = char.db.pos_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        if not is_valid_coord(room, nx, ny):
            char.msg("You cannot move that way.")
            char.db.navigation = None
            self._drain_nav_queue(char)
            return

        cur_z = int(char.db.pos_z or 1)
        z_check = cur_z if is_flying else None
        blockers = is_grid_occupied(room, nx, ny, z=z_check, ignore=char, mover=char)

        if blockers:
            if dz == 0 and nx == nav["dest_x"] and ny == nav["dest_y"]:
                char.msg(arrival_mover_echo(char, nav))
                for observer in room.contents:
                    if observer is char or not getattr(observer, "is_creature", False):
                        continue
                    if not char.visible_to(observer):
                        continue
                    observer.msg(arrival_observer_echo(char, nav, observer), from_obj=char)
                char.db.navigation = None
                self._drain_nav_queue(char)
                return
            if is_autonav and not is_flying:
                route = find_path(
                    room, char.db.pos_x or 0, char.db.pos_y or 0,
                    nav["dest_x"], nav["dest_y"],
                    z=z_check, ignore=char, mover=char,
                )
                if route[0] and len(route[0]) > 1:
                    next_x, next_y = route[0][1]
                    ndx = next_x - (char.db.pos_x or 0)
                    ndy = next_y - (char.db.pos_y or 0)
                    direction = direction_from_delta(ndx, ndy) or "forward"
                    observer_msg = detour_observer_echo(char, direction, speed, blockers[0])
                    mover_msg = detour_mover_echo(char, direction, speed, blockers[0])
                    char.msg(mover_msg)
                    for observer in room.contents:
                        if observer is char or not getattr(observer, "is_creature", False):
                            continue
                        if not char.visible_to(observer):
                            continue
                        observer.msg(observer_msg, from_obj=char)
                    char.db.pos_x, char.db.pos_y = next_x, next_y
                    used = char.db.movement_used or 0
                    char.db.movement_used = used + 1
                    if char.db.is_autowhere:
                        map_text = render_map(char)
                        char.msg(map_text)
                        from world.systems.gmcp import send_map
                        send_map(char, map_text)
                    return
                if is_autofly and char.db.can_fly:
                    from combat.grid import get_room_max_z
                    tz = cur_z + 1
                    if tz <= get_room_max_z(room):
                        char.db.is_flying = True
                        nav["movement_mode"] = "takeoff"
                        nav["dest_z"] = tz
                        nav["fly_landing_z"] = cur_z
                        char.db.navigation = nav
                        char.msg("You take off, rising into the air to fly over the obstacle.")
                        ensure_movement_timer(char)
                        return
            char.msg(blocked_with_hint(blockers, is_autonav))
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
            map_text = render_map(char)
            char.msg(map_text)
            from world.systems.gmcp import send_map
            send_map(char, map_text)

        direction = direction_from_delta(
            nx - (char.db.pos_x or 0) + (1 if dx > 0 else -1 if dx < 0 else 0),
            ny - (char.db.pos_y or 0) + (1 if dy > 0 else -1 if dy < 0 else 0),
        ) or "forward"

        move_obs = move_observer_echo(char, direction, speed, None)
        move_mv = move_mover_echo(char, direction, speed)

        if nav.get("exit_dbref"):
            for observer in room.contents:
                if observer is char or not getattr(observer, "is_creature", False):
                    continue
                if not char.visible_to(observer):
                    continue
                observer.msg(move_obs, from_obj=char)
            char.msg(move_mv)
        elif dz != 0:
            for observer in room.contents:
                if observer is char or not getattr(observer, "is_creature", False):
                    continue
                if not char.visible_to(observer):
                    continue
                observer.msg(move_obs, from_obj=char)
            char.msg(move_mv)
            if nx == nav["dest_x"] and ny == nav["dest_y"]:
                char.msg(arrival_mover_echo(char, nav))
                for observer in room.contents:
                    if observer is char or not getattr(observer, "is_creature", False):
                        continue
                    if not char.visible_to(observer):
                        continue
                    observer.msg(arrival_observer_echo(char, nav, observer), from_obj=char)
                char.db.navigation = None
                self._drain_nav_queue(char)
        elif nx == nav["dest_x"] and ny == nav["dest_y"]:
            char.msg(arrival_mover_echo(char, nav))
            for observer in room.contents:
                if observer is char or not getattr(observer, "is_creature", False):
                    continue
                if not char.visible_to(observer):
                    continue
                observer.msg(arrival_observer_echo(char, nav, observer), from_obj=char)
            char.db.navigation = None
            self._drain_nav_queue(char)
        else:
            for observer in room.contents:
                if observer is char or not getattr(observer, "is_creature", False):
                    continue
                if not char.visible_to(observer):
                    continue
                observer.msg(move_obs, from_obj=char)
            char.msg(move_mv)

    def _drain_nav_queue(self, char):
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
                ensure_movement_timer(char)
            return
        char.db.nav_queue = None