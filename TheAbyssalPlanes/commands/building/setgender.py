from commands.command import GameMuxCommand

GENDERS = ("male", "female", "neuter")


class CmdSetGender(GameMuxCommand):
    """
    Set a character's gender for emote pronouns.

    Usage:
      setgender <male|female|neuter>
      setgender <male|female|neuter> = <target>

    Sets the gender used by the emote system for pronoun substitution
    (He/She/It, His/Her/Its). Defaults to neuter if unset.

    Bare (no argument) shows the target's current gender.
    """
    key = "setgender"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: setgender <male|female|neuter> [= <target>]")
            return

        lhs, rhs = self.lhs, self.rhs
        target = None

        if rhs:
            target_name = rhs.strip().lower()
            for obj in caller.location.contents:
                if obj.name.lower() == target_name:
                    target = obj
                    break
            if not target:
                caller.msg(f"Could not find '{target_name}' here.")
                return
        else:
            target = caller

        gender = (lhs or "").strip().lower()
        if gender == "none":
            target.db.gender = "neuter"
            caller.msg(f"|gReset {target.name}'s gender to neuter.|n")
            return

        if gender not in GENDERS:
            caller.msg(f"Gender must be one of: {', '.join(GENDERS)}.")
            return

        target.db.gender = gender
        caller.msg(f"|gSet {target.name}'s gender to {gender}.|n")
