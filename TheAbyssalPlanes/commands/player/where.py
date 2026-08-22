from evennia import Command
from combat.map_renderer import render_map

class CmdWhere(Command):
    """
    View the local area grid map.
    Usage:
      where
    """
    key = "where"
    help_category = "General"

    def func(self):
        map_text = render_map(self.caller)
        self.caller.msg(map_text)
        from world.systems.gmcp import send_map
        send_map(self.caller, map_text)

class CmdWhereKey(Command):
    """
    View the map legend.
    Usage:
      wherekey
    """
    key = "wherekey"
    help_category = "General"

    def func(self):
        self.caller.msg("""
### MAP KEY
|c@|n : You (Player)
|rH|n : Hostile Entity
|C P|n : Other Player
|g+|n : Exit
|D X|n : Object
|n #|n : Terrain (Base Tile)
|n ~|n : Liquid
|n | or - |n : Wall
""")

class CmdAutoWhere(Command):
    """
    Toggle automatic map display when moving.

    Usage:
      autowhere
    """
    key = "autowhere"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.db.is_autowhere = not bool(caller.db.is_autowhere)
        status = "on" if caller.db.is_autowhere else "off"
        caller.msg(f"Autowhere is now {status}.")

