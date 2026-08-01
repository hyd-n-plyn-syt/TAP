"""
Builder command to set a character's base sub-stat for testing.
"""
from commands.command import Command
from world.systems import stats


class CmdAttSet(Command):
    """
    Set a character's base sub-stat or current pool.

    Usage:
      attset <main> <sub> <value>
      attset <main>_<sub> <value>
      attset <pool> <value>
      attset reset
      attset <...> = <target>

    Examples:
      attset corpus reflexus 4
      attset genius_obsistis 6
      attset vigor 7
      attset reset
      attset animus potestas 3 = Other

    Base sub-stats are set directly; main stats and pools are derived and
    update automatically. Pools (vigor, vim, mens) set the current value,
    clamped to your maximum. 'reset' restores all pools to full. Without a
    target, applies to yourself.
    """
    key = "attset"
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
                "Usage: attset <main> <sub> <value> | attset <pool> <value> | attset reset"
            )
            return

        if parts[0].lower() == "reset":
            target.reset_pools()
            caller.msg(f"|gReset {target.name}'s pools to full.|n")
            return

        if len(parts) == 2 and parts[0].lower() in stats.POOL_KEYS:
            pool = parts[0].lower()
            try:
                value = int(parts[1])
            except ValueError:
                caller.msg("Value must be an integer.")
                return
            result = target.set_pool(pool, value)
            if result is None:
                caller.msg(f"Unknown pool. Choose one of: {'|'.join(stats.POOL_KEYS)}")
                return
            caller.msg(f"|gSet {pool.capitalize()} to {result} on {target.name}.|n")
            return

        if len(parts) != 3:
            caller.msg(
                "Usage: attset <main> <sub> <value> | attset <pool> <value> | attset reset"
            )
            return

        main, sub, value = (part.strip().lower() for part in parts)
        if main not in stats.MAIN_STATS or sub not in stats.SUB_STATS:
            valid = " ".join(
                f"{m} {s}" for m in stats.MAIN_STATS for s in stats.SUB_STATS
            )
            caller.msg(f"Unknown stat. Choose one of: {valid}")
            return

        try:
            value = int(value)
        except ValueError:
            caller.msg("Value must be an integer.")
            return

        if value < 1:
            caller.msg("Value must be at least 1.")
            return

        setattr(target, f"{main}_{sub}", value)
        caller.msg(
            f"|gSet {main.capitalize()} {sub.capitalize()} to {value} "
            f"on {target.name}.|n"
        )
