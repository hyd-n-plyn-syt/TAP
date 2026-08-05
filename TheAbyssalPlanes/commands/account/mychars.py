"""
List all characters on this account.
"""

from evennia import Command
from world.data import species as species_data


class CmdMyChars(Command):
    """
    List all characters you have created.

    Usage:
      mychars

    Shows each character's name, species, and whether they have been
    introduced to the game yet.
    """
    key = "mychars"
    aliases = ["characters", "chars"]
    locks = "cmd:pperm(Player)"
    help_category = "General"
    account_caller = True

    def func(self):
        account = self.account
        if not account:
            self.msg("You must be logged in.")
            return

        chars = account.characters.all()
        if not chars:
            self.msg("You have no characters. Use |wcharcreate <name>|n to make one.")
            return

        lines = ["|wYour characters:|n"]
        for char in chars:
            sname = species_data.species_name(char.species_key) if char.species_key else ""
            species_str = f" ({sname})" if sname else ""
            lines.append(f"  |w{char.key}|n{species_str}")
        self.msg("\n".join(lines))
