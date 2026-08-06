"""
Admin command to add an entry to the in-game changelog.
"""
from commands.command import Command
from world.data import changes
from world.server_hooks import announce_new


class CmdAddChange(Command):
    """
    Add a new entry to the in-game changelog.

    Usage:
      addchange <title> = <body>

    Appends a new entry numbered one above the latest, dated today, and
    writes it into world/data/changes.py so it survives reloads and becomes
    part of the codebase. The change is announced immediately to everyone
    connected; it also appears in 'changes' and on login until read.
    """
    key = "addchange"
    aliases = ["addchangelog"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        lhs, sep, rhs = self.args.partition("=")
        if not sep or not lhs.strip() or not rhs.strip():
            caller.msg("Usage: addchange <title> = <body>")
            return
        try:
            entry = changes.append_entry(lhs.strip(), rhs.strip())
        except ValueError as err:
            caller.msg(f"|r{err}|n")
            return
        announce_new()
        caller.msg(
            f"|gAdded change #{entry['number']} \"{entry['title']}\".|n\n"
            "It is now announced to everyone connected and will appear in "
            "'changes' until read."
        )
