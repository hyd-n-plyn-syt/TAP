"""
Override the stock charcreate command to start the guided character
creation menu.
"""

from evennia import Command
from evennia.objects.models import ObjectDB
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
        args = self.args.strip()
        if not args:
            self.msg("Usage: charcreate <name>")
            return

        name = args.split("=")[0].strip()
        if not name:
            self.msg("You must provide a name for your character.")
            return

        account = self.account
        if not account:
            self.msg("You must be logged in to create a character.")
            return

        existing = ObjectDB.objects.filter(
            db_account=account, db_typeclass_path__contains="characters"
        ).values_list("db_key", flat=True)
        for char_name in existing:
            if char_name.lower() == name.lower():
                self.msg(f"You already have a character named '{name}'.")
                return

        self.caller.ndb._chargen_name = name
        self.msg(f"Creating {name}...")
        EvMenu(
            self.caller,
            "commands.account.chargen_menu",
            startnode="node_welcome",
            session=self.session,
            cmd_on_exit="look",
        )
