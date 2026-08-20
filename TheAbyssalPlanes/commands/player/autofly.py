from evennia import Command


class CmdAutoFly(Command):
    """
    Toggle automatic flight over ground obstacles.

    When on, if your path is blocked by a ground object and you can fly,
    you will automatically take off, fly over the obstacle, and land on
    the other side.

    Usage:
      autofly
    """
    key = "autofly"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not caller.db.can_fly:
            caller.msg("You cannot fly.")
            return
        caller.db.autofly = not bool(caller.db.autofly)
        status = "on" if caller.db.autofly else "off"
        caller.msg(f"Autofly is now {status}.")
