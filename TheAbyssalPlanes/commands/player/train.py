"""
Player command to learn skills from trainers.
"""
from commands.command import Command
from world.data import skills as data
from world.systems import skills


class CmdTrain(Command):
    """
    Learn a skill from a trainer nearby.

    Usage:
      train
      train <skill>

    With no arguments, lists the trainers here and the skills each can
    teach you. With a skill name, asks a trainer here to teach it to you;
    you learn it at Novice and raise it by using it. Advanced skills
    show their requirements - you must meet them before you can learn.
    """
    key = "train"
    locks = "cmd:all()"
    help_category = "General"

    def trainers_in_room(self, caller):
        """The Characters in the room who can train, in contents order."""
        result = []
        for obj in caller.location.contents:
            if getattr(obj, "trainer_skills", None):
                result.append(obj)
        return result

    def func(self):
        caller = self.caller
        arg = self.args.strip()

        trainers = self.trainers_in_room(caller)
        if not trainers:
            caller.msg("There's no one here who can train you.")
            return

        if not arg:
            self._list_trainers(caller, trainers)
            return

        key = data.skill_key(arg)
        if not key:
            caller.msg("You don't know how to do that.")
            return

        trainer = next((t for t in trainers if key in t.trainer_skills), None)
        if not trainer:
            caller.msg("No one here can teach you that.")
            return

        known = getattr(caller.db, "skills", None) or {}
        if key in known:
            caller.msg(f"You already know how to {data.get_skill(key)['name'].lower()}.")
            return

        missing = skills.missing_prereqs(caller, key)
        if missing:
            reqs = ", and ".join(
                f"{data.get_skill(r)['name']} {skills.requirement_str(needed)}"
                for r, (_, needed) in missing.items()
            )
            caller.msg(
                f"|rYou need {reqs} to learn "
                f"{data.get_skill(key)['name']}.|n"
            )
            return

        known[key] = 1
        caller.db.skills = known
        caller.msg(
            f"|g{trainer.name} teaches you the fundamentals of "
            f"{data.get_skill(key)['name']} (Novice).|n"
        )

    def _list_trainers(self, caller, trainers):
        lines = []
        for trainer in trainers:
            lines.append(f"|w{trainer.name} trains in:|n")
            for key in trainer.trainer_skills:
                skill = data.get_skill(key)
                if not skill:
                    continue
                line = f"  {skill['name']}"
                if skill["requires"]:
                    reqs = ", ".join(
                        f"{data.get_skill(r)['name']} {skills.requirement_str(v)}"
                        for r, v in skill["requires"].items()
                    )
                    line += f" |w(requires {reqs})|n"
                lines.append(line)
            lines.append("")
        caller.msg("\n".join(lines))
