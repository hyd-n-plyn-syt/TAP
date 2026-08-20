from evennia import Command


class CmdWalk(Command):
    """
    Set your movement speed to walk.

    Usage:
      walk
    """
    key = "walk"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        self.caller.db.move_speed = "walk"
        self.caller.msg("You will now walk. (3 seconds per tile)")


class CmdJog(Command):
    """
    Set your movement speed to jog.

    Usage:
      jog
    """
    key = "jog"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        self.caller.db.move_speed = "jog"
        self.caller.msg("You will now jog. (2 seconds per tile)")


class CmdRun(Command):
    """
    Set your movement speed to run.

    Usage:
      run
    """
    key = "run"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        self.caller.db.move_speed = "run"
        self.caller.msg("You will now run. (1 second per tile)")
