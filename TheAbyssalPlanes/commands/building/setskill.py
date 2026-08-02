"""
Builder command to manage skills for testing: learn, unlearn, and set values.
"""
from commands.command import Command
from world.data import skills as data
from world.systems import skills


class CmdSetSkill(Command):
    """
    Learn or manipulate a character's skills for testing.

    Usage:
      setskill <skill> [= <target>]           learn <skill>
      setskill <skill> <value> [= <target>]   set the skill's value directly
      setskill <skill> reset [= <target>]     forget the skill

    Examples:
      setskill punch
      setskill attack 800
      setskill feint = Bob
      setskill kick reset

    Advanced skills require their prerequisites unless this command is used;
    builders may bypass requirements by appending 'force':
      setskill power_strike force
    """
    key = "setskill"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        lhs, sep, rhs = self.args.partition("=")
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

        parts = lhs.split()
        if not parts:
            caller.msg(
                "Usage: setskill <skill> [value] [force] [= target]"
            )
            return

        force = "force" in parts
        parts = [p for p in parts if p != "force"]

        key = data.skill_key(parts[0])
        skill = data.get_skill(key)
        if not skill:
            caller.msg(
                f"Unknown skill '{parts[0]}'. Try: "
                f"{', '.join(sorted(data.all_skills()))}"
            )
            return

        if len(parts) >= 2 and parts[1].lower() == "reset":
            if key in target.skills:
                del target.skills[key]
                caller.msg(f"|r{target.name} forgot {skill['name']}.|n")
            else:
                caller.msg(f"{target.name} doesn't know {skill['name']}.")
            return

        if len(parts) >= 2:
            try:
                value = int(parts[1])
            except ValueError:
                caller.msg("Value must be an integer.")
                return
            value = max(0, min(1000, value))
            if value == 0:
                if key in target.skills:
                    del target.skills[key]
                caller.msg(f"|r{target.name} forgot {skill['name']}.|n")
                return
            target.skills[key] = value
            caller.msg(
                f"|gSet {skill['name']} to {value} "
                f"({data.TIER_NAMES[skills.tier(value) - 1]}) on {target.name}.|n"
            )
            return

        if key in target.skills:
            caller.msg(f"{target.name} already knows {skill['name']}.")
            return

        missing = skills.missing_prereqs(target, key)
        if missing and not force:
            reqs = ", ".join(
                f"{data.get_skill(r)['name']} {needed}"
                for r, (_, needed) in missing.items()
            )
            caller.msg(
                f"|rRequires {reqs}. Append 'force' to bypass.|n"
            )
            return

        target.skills[key] = 0
        if missing:
            caller.msg(
                f"|g{target.name} learned {skill['name']} "
                f"(requirements bypassed).|n"
            )
        else:
            caller.msg(f"|g{target.name} learned {skill['name']}.|n")
