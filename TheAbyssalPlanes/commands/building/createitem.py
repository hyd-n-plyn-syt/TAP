from commands.command import Command
from evennia.utils.evmenu import EvMenu


class CmdCreateItem(Command):
    """
    Create a new custom item interactively.

    Usage:
      createitem
    """
    key = "createitem"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        EvMenu(self.caller, "commands.building.createitem_menu", startnode="node_item_type")
