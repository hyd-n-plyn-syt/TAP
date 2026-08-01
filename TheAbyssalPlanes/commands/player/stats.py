from commands.command import Command
from world.systems import stats


class CmdStats(Command):
    """
    View your character's stats.

    Usage:
      stats

    Shows your nine base sub-stats, your three derived main stats
    (the sum of each category's sub-stats), and your six derived
    pools (Vigor, Vim, Mens and their regen rates).
    """
    key = "stats"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        pools = stats.derived_pools(caller)

        lines = ["|w=== Stats ===|n"]
        for main in stats.MAIN_STATS:
            lines.append(f"|w{main.capitalize():7}|n {stats.main_stat(caller, main)}")
            for sub in stats.SUB_STATS:
                value = getattr(caller, f"{main}_{sub}")
                lines.append(f"   {sub.capitalize():9} {value}")
        lines.append("")
        lines.append("|w=== Pools ===|n")
        for pool in stats.POOL_KEYS:
            maxv = getattr(caller, pool)
            cur = caller.pools_current[pool]
            lines.append(f"|w{pool.capitalize():5}|n {cur}/{maxv}")
        for key, value in pools.items():
            if key in stats.POOL_KEYS:
                continue
            label = key.replace("_", " ").title()
            lines.append(f"|w{label:11}|n {value}")

        caller.msg("\n".join(lines))
