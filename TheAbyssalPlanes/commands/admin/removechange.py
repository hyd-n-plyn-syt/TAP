"""
Admin command to remove an entry from the in-game changelog.
"""
from commands.command import Command
from world.data import changes


class CmdRemoveChange(Command):
    """
    Remove an entry from the in-game changelog and renumber the rest.

    Usage:
      removechange <number>

    Removes the specified change entry from the changelog and shifts the
    numbers of all subsequent entries down so that numbering remains
    continuous. The updated changelog is written back to world/data/changes.py.
    """
    key = "removechange"
    aliases = ["removechangelog", "delchange"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        arg = self.args.strip()
        if not arg:
            caller.msg("Usage: removechange <number>")
            return
        try:
            number = int(arg.lstrip("#"))
        except ValueError:
            caller.msg("Usage: removechange <number>")
            return
        try:
            removed = changes.remove_entry(number)
        except ValueError as err:
            caller.msg(f"|r{err}|n")
            return
        caller.msg(
            f"|gRemoved change #{number} \"{removed['title']}\". "
            "Remaining changes have been renumbered.|n"
        )
