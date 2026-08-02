"""
Builder command to designate an NPC as a trainer of specific skills.
"""
from commands.command import Command
from world.data import skills as data


class CmdSetTrainer(Command):
    """
    Designate an NPC here as a trainer of the listed skills.

    Usage:
      settrainer <target> = <skill1, skill2, ...>
      settrainer <target>
      settrainer <target> = none

    Examples:
      settrainer Master Wu = attack, dodge, parry, punch, kick
      settrainer Master Wu = power_strike, feint
      settrainer Master Wu = none

    The target must be present in the room. Skills accept keys or display
    names and must exist in the catalog. 'none' (or an empty list) removes
    the target's trainer status. With no '=', lists the skills the target
    currently trains in.
    """
    key = "settrainer"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        lhs, sep, rhs = self.args.partition("=")
        target = None
        target_name = lhs.strip().lower()
        if not target_name:
            caller.msg("Usage: settrainer <target> = <skill1, skill2, ...>")
            return
        for obj in caller.location.contents:
            if obj.name.lower() == target_name:
                target = obj
                break
        if not target:
            caller.msg(f"Could not find '{lhs.strip()}' here.")
            return

        if not sep:
            trained = target.attributes.get("trained_skills")
            if not trained:
                caller.msg(f"{target.name} is not a trainer.")
            else:
                names = ", ".join(
                    data.get_skill(k)["name"] if data.get_skill(k) else k
                    for k in trained
                )
                caller.msg(f"{target.name} trains in: {names}")
            return

        rhs = rhs.strip().lower()
        if not rhs or rhs in ("none", "none.", "clear", "remove"):
            target.attributes.remove("trained_skills")
            caller.msg(f"|r{target.name} is no longer a trainer.|n")
            return

        keys = []
        for item in rhs.split(","):
            item = item.strip()
            if not item:
                continue
            key = data.skill_key(item)
            if not key:
                caller.msg(f"Unknown skill '{item}'. No changes made.")
                return
            keys.append(key)

        if not keys:
            caller.msg("No valid skills given. No changes made.")
            return

        target.attributes.add("trained_skills", keys)
        names = ", ".join(data.get_skill(k)["name"] for k in keys)
        caller.msg(f"|g{target.name} now trains in: {names}|n")
