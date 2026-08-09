from evennia import Command
from combat.movement import start_navigation
from combat.grid import get_room_max_z

class CmdFly(Command):
    """
    Take off and fly.
    Usage:
      fly
    """
    key = "fly"
    def func(self):
        caller = self.caller
        if not caller.db.can_fly:
            caller.msg("You cannot fly.")
            return
        if caller.db.is_flying:
            caller.msg("You are already flying.")
            return
        room = caller.location
        cz = caller.db.pos_z or 1
        tz = cz + 1
        if tz > get_room_max_z(room):
            caller.msg("You cannot fly higher than this area allows.")
            return
        caller.db.is_flying = True
        start_navigation(caller, caller.db.pos_x or 0, caller.db.pos_y or 0, z=tz, movement_mode="takeoff")

class CmdLand(Command):
    """Land on the ground."""
    key = "land"
    def func(self):
        caller = self.caller
        if not caller.db.is_flying:
            caller.msg("You are not flying.")
            return
        room = caller.location
        from combat.grid import get_room_floor_z
        floor = get_room_floor_z(room)
        cz = caller.db.pos_z or 1
        

        
        if cz <= floor:
            caller.db.is_flying = False
            return
        start_navigation(caller, caller.db.pos_x or 0, caller.db.pos_y or 0, z=floor, movement_mode="landing")
