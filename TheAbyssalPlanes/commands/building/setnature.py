"""
Builder command to set an object's visarial nature.
"""
from commands.command import Command


class CmdSetNature(Command):
    """
    Set a target's visarial nature.

    Usage:
      setnature <nature> = <target>

    Examples:
      setnature visarial = lapis obelisk
      setnature physical = black obelisk
      setnature dual_natured = relic

    <target> must be present in the room. Nature must be one of
    'physical' (pure physical), 'visarial' (pure Visarium) or
    'dual_natured' (in physical by default, of both). With no target,
    applies to yourself. On characters the nature usually comes from
    their species; use this to override it (e.g. for NPCs or props).
    """
    key = "setnature"
    aliases = ["setplane"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        lhs, sep, rhs = self.args.partition("=")
        nature = lhs.strip().lower().replace("-", "_")
        if not nature:
            caller.msg("Usage: setnature <nature> = <target>")
            return
        if nature in ("dual", "duality", "both"):
            nature = "dual_natured"
        if nature not in ("physical", "visarial", "dual_natured"):
            caller.msg("Nature must be one of: physical, visarial, dual_natured.")
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

        if not target.set_nature(nature):
            caller.msg(f"Could not set {target.name}'s nature to {nature}.")
            return
        caller.msg(f"|gSet {target.name}'s visarial nature to |w{nature}|n.|n")