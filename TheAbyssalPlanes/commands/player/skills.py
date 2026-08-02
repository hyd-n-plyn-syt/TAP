"""
Player command to view skills: tiers, progress, and prerequisites.
"""
from commands.command import Command
from world.data import skills as data
from world.systems import skills


class CmdSkills(Command):
    """
    View your skills.

    Usage:
      skills
      skills <skill>

    Lists every known skill grouped by category, with its value (0-1000),
    progress within the current tier, and XP until the next point.
    Untrained advanced skills show their requirements. With a skill name,
    shows the detail for that skill, including the statistics it exercises.
    """
    key = "skills"
    aliases = ["skill"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        arg = self.args.strip()

        if arg:
            self._show_detail(caller, arg)
            return

        lines = ["|w=== Skills ===|n"]
        for cat in data.categories():
            lines.append(f"|w{cat.capitalize()}|n")
            for key, skill in data.all_skills().items():
                if skill["category"] != cat:
                    continue
                lines.append(self._line(caller, skill))
        caller.msg("\n".join(lines))

    def _line(self, caller, skill):
        """One listing line for a skill."""
        key = skill["key"]
        value = skills.skill_value(caller, key)
        known = key in caller.skills

        if not known:
            missing = skills.missing_prereqs(caller, key)
            if missing:
                reqs = ", ".join(
                    f"{data.get_skill(r)['name']} {needed}"
                    for r, (_, needed) in missing.items()
                )
                return f"  |r{skill['name']:16}|n |r[locked - requires {reqs}]|n"
            return f"  |w{skill['name']:16}|n |Wuntrained|n"

        t = skills.tier(value)
        pct = skills.within_tier(value)
        xpnext = skills.xp_to_next(caller, key)
        return (
            f"  |w{skill['name']:16}|n {value:>4}/100 ({pct:>3}%) "
            f"|w{data.TIER_NAMES[t - 1]}|n  ({xpnext:.0f} xp to next)"
        )

    def _show_detail(self, caller, arg):
        key = data.skill_key(arg)
        skill = data.get_skill(key)
        if not skill:
            caller.msg(f"Unknown skill '{arg}'.")
            return

        value = skills.skill_value(caller, key)
        t = skills.tier(value)
        stats = ", ".join(
            f"{s.replace('_', ' ').title()} ({int(w * 100)}%)"
            for s, w in skill["stats"].items()
        )
        lines = [
            f"|w{skill['name']}|n ({skill['category']})",
            f"  |wValue:|n {value} - {data.TIER_NAMES[t - 1]} "
            f"({skills.within_tier(value)}/100 in tier)",
        ]
        if key in caller.skills:
            lines.append(f"  |wNext point:|n {skills.xp_to_next(caller, key):.0f} xp")
        else:
            lines.append(f"  |wState:|n |Wuntrained|n")
        lines.append(f"  |wExercises:|n {stats}")
        if skill["requires"]:
            reqs = ", ".join(
                f"{data.get_skill(r)['name']} {v}" for r, v in skill["requires"].items()
            )
            lines.append(f"  |wRequires:|n {reqs}")
        if skill["desc"]:
            lines.append(f"  {skill['desc']}")
        caller.msg("\n".join(lines))
