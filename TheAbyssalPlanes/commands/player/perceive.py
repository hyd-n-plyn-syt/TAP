from commands.command import Command


class CmdPerceive(Command):
    key = "perceive"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="physical")

        if current == "physical":
            caller.set_state("perceiving")
            caller.msg("You begin to perceive the visarial realm.")
        elif current == "perceiving":
            caller.set_state("physical")
            caller.msg("You cease perceiving the visarial realm.")
        elif current == "manifested":
            caller.set_state("perceiving")
            caller.msg("You shift your focus to perceiving rather than manifesting.")
