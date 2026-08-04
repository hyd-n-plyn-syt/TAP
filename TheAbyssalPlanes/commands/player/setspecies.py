"""
Builder command to set a character's species.
"""
from commands.command import Command
from world.data import species


class CmdSetSpecies(Command):
    """
    Set or clear a character's species.

    Usage:
      setspecies
      setspecies <species>
      setspecies none
      setspecies <species> = <target>
      setspecies none = <target>

    Examples:
      setspecies
      setspecies terran
      setspecies visarii = Test
      setspecies none

    With no argument, lists all available species. 'none' clears the
    species, restoring neutral defaults. Without a target, applies to
    yourself. Species bonuses are persistent: effective sub-stats equal
    the stored base plus the species bonus, so changing species updates
    everything immediately.
    """
    key = "setspecies"
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

        arg = lhs.strip().lower()
        if not arg:
            lines = ["|w=== Species ===|n"]
            for key in species.species_keys():
                data = species.get_species(key)
                if not data:
                    continue
                nature = data["visarial_nature"]
                lines.append(f"|w{data['name']:10}|n {data['archetype']} ({nature})")
            caller.msg("\n".join(lines))
            return

        if arg in ("none", "clear", "unset"):
            target.clear_species()
            caller.msg(f"|gCleared {target.name}'s species.|n")
            return

        data = species.get_species(arg)
        if not data:
            caller.msg(f"Unknown species '{lhs.strip()}'. Try 'setspecies' for a list.")
            return

        if not target.apply_species(arg):
            caller.msg("Could not set species.")
            return

        bonus = ", ".join(
            f"+{value} {name.replace('_', ' ').title()}"
            for name, value in data["stat_bonuses"].items()
        )
        traits = []
        if data["locked_main_stats"]:
            traits.append(
                "locked: "
                + ", ".join(main.capitalize() for main in data["locked_main_stats"])
            )
        if data["zeroed_pools"]:
            traits.append(
                "no " + ", ".join(pool.capitalize() for pool in data["zeroed_pools"])
            )
        if not data.get("can_perceive") or not data.get("can_manifest"):
            traits.append("cannot perceive or manifest into the Visarium")
        suffix = f" ({'; '.join(traits)})" if traits else ""
        caller.msg(
            f"|gSet {target.name}'s species to {data['name']} "
            f"({data['archetype']}).|n |wBonus:|n {bonus}{suffix}"
        )
