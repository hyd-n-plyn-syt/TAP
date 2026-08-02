"""
Player command to view a character's score: species, attributes and pools.
"""
from commands.command import Command
from world.data import rankings
from world.systems import stats


class CmdScore(Command):
    """
    View your character's score.

    Usage:
      score

    Shows your species (and its bonuses), your nine sub-stats with their
    effective values, your three derived main stats, and your six derived
    pools (Vigor, Vim, Mens and their regen rates). Main-stat columns a
    species locks at 0 are omitted, as are pools a species cannot use.
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
        attr_lines = []
        for main in stats.MAIN_STATS:
            if stats.sub_stat_is_locked(caller, main):
                continue
            value = stats.main_stat(caller, main)
            rank = rankings.rank_name(value)
            attr_lines.append(f"|w{main.capitalize():7}|n {value} |W[{rank}]|n")
            for sub in stats.SUB_STATS:
                base = getattr(caller, f"{main}_{sub}")
                effective = stats.effective_sub_stat(caller, main, sub)
                display = str(effective)
                if effective != base:
                    display += f" |g(+{effective - base})|n"
                attr_lines.append(f"   {sub.capitalize():9} {display}")
        if attr_lines:
            lines.append("|w=== Attributes ===|n")
            lines.extend(attr_lines)

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
