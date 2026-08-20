from evennia import Command


class CmdAutoNavigate(Command):
    """
    Toggle automatic pathfinding around obstacles.

    Usage:
      autonavigate
    """
    key = "autonavigate"
    aliases = ["autonav"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.db.autonavigate = not bool(caller.db.autonavigate)
        status = "on" if caller.db.autonavigate else "off"
        caller.msg(f"Autonavigate is now {status}.")
