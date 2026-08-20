from commands.command import Command
from combat.realm_contest import announce_crossing, resolve_realm_conflict


class CmdManifest(Command):
    key = "manifest"
    locks = "cmd:all()"
    help_category = "General"

    def _cross(self, caller, new_state, arrival):
        old_observers = caller._movement_observers()
        caller.set_state(new_state)
        result = resolve_realm_conflict(caller)
        announce_crossing(caller, arrival, old_observers, result)

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="normal")
        data = caller.species

        if not caller.can_manifest:
            caller.msg("Your kind cannot manifest into the visarial realm.")
            return

        if data and data["visarial_nature"] == "visarial":
            if current == "manifested":
                self._cross(caller, "normal", arrival=False)
            else:
                self._cross(caller, "manifested", arrival=True)
            return

        if current == "manifested":
            self._cross(caller, "normal", arrival=False)
        else:
            self._cross(caller, "manifested", arrival=True)