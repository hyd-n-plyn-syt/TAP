from commands.command import Command
from evennia.utils.evmenu import EvMenu


class CmdCreateFurniture(Command):
    """
    Create a new piece of furniture interactively.

    Usage:
      createfurniture
    """
    key = "createfurniture"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        EvMenu(self.caller, "commands.building.createfurniture_menu", startnode="node_name")
