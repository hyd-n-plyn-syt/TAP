"""
Builder command to toggle a character's can_fly flag.
"""
from commands.command import Command


class CmdSetCanFly(Command):
    """
    Toggle whether a target is capable of flight.

    Usage:
      setcanfly [on|off] = <target>
      setcanfly

    With no value, toggles the current flag. With no target, applies to
    yourself. Only characters with can_fly=True can use the FLY command.
    """
    key = "setcanfly"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        lhs, sep, rhs = self.args.partition("=")
        value = lhs.strip().lower()
        if value in ("on", "true", "1", "yes"):
            can_fly = True
        elif value in ("off", "false", "0", "no"):
            can_fly = False
        elif not value:
            can_fly = None
        else:
            caller.msg("Usage: setcanfly [on|off] = <target>")
            return

        if sep:
            target = None
            target_name = rhs.strip().lower()
            for obj in caller.location.contents:
                if obj.name.lower() == target_name:
                    target = obj
                    break
            if not target:
                caller.msg(f"Could not find '{rhs.strip()}' here.")
                return
        else:
            target = caller

        if can_fly is None:
            can_fly = not bool(getattr(target.db, "can_fly", False))
        target.db.can_fly = can_fly
        state = "can fly" if can_fly else "cannot fly"
        caller.msg(f"|gSet {target.name}'s flight capability to |w{state}|n.|n")
