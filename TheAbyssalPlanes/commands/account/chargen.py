"""
Override the stock charcreate command to start the guided character
creation menu.
"""

from evennia import Command
from evennia.utils.evmenu import EvMenu


class CmdCharCreate(Command):
    """
    Create a new character and enter the guided chargen flow.

    Usage:
      charcreate <name>

    The character is created and you are walked through gender, species,
    appearance, and stat allocation before entering the game.
    """
    key = "charcreate"
    locks = "cmd:pperm(Player)"
    help_category = "General"
    account_caller = True

    def func(self):
        if not self.args:
            self.msg("Usage: charcreate <name>")
            return

        name = self.lhs.strip()
        if not name:
            self.msg("You must provide a name for your character.")
            return

        account = self.account
        if not account:
            self.msg("You must be logged in to create a character.")
            return

        # Check if this name is already taken by one of the account's characters.
        for char in account.characters:
            if char.key.lower() == name.lower():
                self.msg(f"You already have a character named '{name}'.")
                return

        new_char, errors = account.create_character(
            key=name, description="This is a character.", ip=self.session.address
        )
        if errors:
            self.msg(errors)
        if not new_char:
            return

        self.msg(f"Creating {new_char.key}...")
        EvMenu(
            self.caller,
            "commands.account.chargen_menu",
            startnode="node_welcome",
            session=self.session,
            cmd_on_exit="look",
        )
