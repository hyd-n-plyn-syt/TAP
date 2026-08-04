from commands.command import Command


class CmdManifest(Command):
    key = "manifest"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="normal")
        data = caller.species

        if not caller.can_manifest:
            caller.msg("Your kind cannot manifest into the visarial realm.")
            return

        if data and data["visarial_nature"] == "visarial":
            if current == "manifested":
                caller.set_state("normal")
                caller.msg("You withdraw your crystalline form back into the visarial realm.")
            else:
                caller.set_state("manifested")
                caller.msg("You project your crystalline form into the physical plane.")
            caller.msg(prompt=caller.get_prompt())
            return

        if current == "normal":
            caller.set_state("manifested")
            caller.msg("You manifest into the visarial realm.")
        elif current == "manifested":
            caller.set_state("normal")
            caller.msg("You withdraw from the visarial realm.")
        elif current == "perceiving":
            caller.set_state("manifested")
            caller.msg("You manifest fully, your perception becoming reality.")
