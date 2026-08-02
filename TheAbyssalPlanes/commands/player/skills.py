"""
Player command to view learned skills: tiers, progress, and how they exercise
your statistics.
"""
from commands.command import Command
from world.data import skills as data
from world.systems import skills


class CmdSkills(Command):
    """
    View the skills you know.

    Usage:
      skills
      skills <skill>

    Lists every skill you have learned, grouped by category, with its value
    (0-1000), progress within the current tier, and XP until the next point.
    With a skill name, shows the detail for that skill, including which
    statistics it exercises for you. Skills you have not learned are not
    shown; seek out a trainer to learn them.
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

        known = skills.known_skills(caller)
        if not known:
            caller.msg(
                "|w=== Skills ===|n\n"
                "You have not learned any skills yet. Seek out a trainer to "
                "learn the basics."
            )
            return

        lines = ["|w=== Skills ===|n"]
        for cat in data.categories():
            in_cat = [kv for kv in known if data.get_skill(kv[0])["category"] == cat]
            if not in_cat:
                continue
            lines.append(f"|w{cat.capitalize()}|n")
            for key, _ in in_cat:
                lines.append(self._line(caller, key))
        caller.msg("\n".join(lines))

    def _line(self, caller, key):
        """One listing line for a known skill."""
        skill = data.get_skill(key)
        value = skills.skill_value(caller, key)
        pct = skills.within_tier(value)
        xpnext = skills.xp_to_next(caller, key)
        return (
            f"  |w{skill['name']:16}|n {value:>4}/100 ({pct:>3}%) "
            f"|{data.tier_color(skills.tier(value))}{data.TIER_NAMES[skills.tier(value) - 1]}|n"
            f"  ({xpnext:.0f} xp to next)"
        )

    def _show_detail(self, caller, arg):
        key = data.skill_key(arg)
        skill = data.get_skill(key)
        if not skill:
            caller.msg("You don't know how to do that.")
            return
        if key not in caller.skills:
            caller.msg("You don't know how to do that.")
            return

        value = skills.skill_value(caller, key)
        stats = ", ".join(
            f"{s.replace('_', ' ').title()} ({int(w * 100)}%)"
            for s, w in skills.effective_skill_stats(caller, key).items()
        )
        lines = [
            f"|w{skill['name']}|n ({skill['category']})",
            f"  |wValue:|n {value} "
            f"|{data.tier_color(skills.tier(value))}{data.TIER_NAMES[skills.tier(value) - 1]}|n "
            f"({skills.within_tier(value)}/100 in tier)",
            f"  |wNext point:|n {skills.xp_to_next(caller, key):.0f} xp",
            f"  |wExercises:|n {stats}",
        ]
        if skill["requires"]:
            reqs = ", ".join(
                f"{data.get_skill(r)['name']} {skills.requirement_str(v)}"
                for r, v in skill["requires"].items()
            )
            lines.append(f"  |wRequires:|n {reqs}")
        if skill["desc"]:
            lines.append(f"  {skill['desc']}")
        caller.msg("\n".join(lines))
