"""
Player command to view a character's score: species, attributes and pools.
"""
from commands.command import Command
from world.systems import stats


class CmdScore(Command):
    """
    View your character's score.

    Usage:
      score

    Shows your species (and its bonuses), your nine sub-stats with their
    effective values, your three derived main stats, and your six derived
    pools (Vigor, Vim, Mens and their regen rates). Pools a species cannot
    use are omitted.
    """
    key = "score"
    aliases = ["stats"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        pools = stats.derived_pools(caller)
        data = caller.species
        zeroed = stats.zero_pools(caller)

        lines = ["|w=== Score ===|n"]
        if data:
            nature = data["visarial_nature"]
            lines.append(
                f"|wSpecies:|n {data['name']} ({data['archetype']}) - {nature}"
            )
            bonus = ", ".join(
                f"+{v} {name.replace('_', ' ').title()}"
                for name, v in data["stat_bonuses"].items()
            )
            lines.append(f"|wBonus:|n {bonus}")
        else:
            lines.append("|wSpecies:|n none set")

        if caller.sign:
            lines.append(f"|wSign:|n {caller.sign}")
        if caller.birth_date:
            lines.append(f"|wBorn:|n {caller.birth_date}")

        lines.append("")
        lines.append("|w=== Attributes ===|n")
        for main in stats.MAIN_STATS:
            locked = bool(data and main in data["locked_main_stats"])
            suffix = "  |r[locked 0]|n" if locked else ""
            value = stats.main_stat(caller, main)
            lines.append(f"|w{main.capitalize():7}|n {value}{suffix}")
            for sub in stats.SUB_STATS:
                base = getattr(caller, f"{main}_{sub}")
                effective = stats.effective_sub_stat(caller, main, sub)
                if locked:
                    lines.append(f"   {sub.capitalize():9} 0 |r(locked)|n")
                else:
                    display = str(effective)
                    if effective != base:
                        display += f" |g(+{effective - base})|n"
                    lines.append(f"   {sub.capitalize():9} {display}")

        lines.append("")
        lines.append("|w=== Pools ===|n")
        for pool in stats.POOL_KEYS:
            if pool in zeroed:
                continue
            maxv = getattr(caller, pool)
            cur = caller.pools_current[pool]
            lines.append(f"|w{pool.capitalize():5}|n {cur}/{maxv}")
        for key, value in pools.items():
            if key in stats.POOL_KEYS:
                continue
            if key.replace("_regen", "") in zeroed:
                continue
            label = key.replace("_", " ").title()
            lines.append(f"|w{label:11}|n {value}")

        caller.msg("\n".join(lines))
