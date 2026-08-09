from evennia import DefaultScript
from evennia.objects.models import ObjectDB

from combat.grid import get_exit_coords, get_room_floor_z
from combat.movement import (
    GLOBAL_ROUND_DURATION,
    MAX_GRIDS_PER_ROUND,
    SUB_TICK_RATE,
    announce_grid_arrival,
    announce_grid_move,
    is_grid_occupied,
    mover_arrival_message,
)
from combat.map_renderer import render_map


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
                char.move_to(exit_obj.destination)
            else:
                char.msg(mover_arrival_message(room, nav, char))
            return

        nx = char.db.pos_x + (1 if dx > 0 else -1 if dx < 0 else 0)
        ny = char.db.pos_y + (1 if dy > 0 else -1 if dy < 0 else 0)

        if is_grid_occupied(room, nx, ny):
            char.msg("Your path is blocked.")
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
        elif nx == nav["dest_x"] and ny == nav["dest_y"]:
            announce_grid_arrival(char, nav)
            char.msg(mover_arrival_message(room, nav, char))
            char.db.navigation = None
        else:
            announce_grid_move(char, nav)

    def resolve_tick(self, char):
        """Process a single combatant's sub-tick."""
        pass
