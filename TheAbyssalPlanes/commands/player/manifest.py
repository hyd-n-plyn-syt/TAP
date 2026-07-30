from commands.command import Command


class CmdManifest(Command):
    key = "manifest"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="physical")

        if current == "physical":
            caller.set_state("manifested")
            caller.msg("You manifest into the visarial realm.")
        elif current == "manifested":
            caller.set_state("physical")
            caller.msg("You withdraw from the visarial realm.")
        elif current == "perceiving":
            caller.set_state("manifested")
            caller.msg("You manifest fully, your perception becoming reality.")
