from commands.command import Command


class CmdPerceive(Command):
    key = "perceive"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="physical")
        data = caller.species

        if data and data.get("cannot_perceive"):
            caller.msg("Your kind cannot perceive the visarial realm.")
            return

        if data and data["visarial_nature"] == "visarial":
            if current == "perceiving":
                caller.set_state("manifested")
                caller.msg("You turn your awareness away from the physical plane.")
            elif current == "physical":
                caller.set_state("perceiving")
                caller.msg(
                    "You withdraw into the visarial realm, perceiving the physical "
                    "plane from within it."
                )
            else:
                caller.set_state("perceiving")
                caller.msg(
                    "You perceive into the physical plane without leaving the visarial realm."
                )
            return

        if current == "physical":
            caller.set_state("perceiving")
            caller.msg("You begin to perceive the visarial realm.")
        elif current == "perceiving":
            caller.set_state("physical")
            caller.msg("You cease perceiving the visarial realm.")
        elif current == "manifested":
            caller.set_state("perceiving")
            caller.msg("You shift your focus to perceiving rather than manifesting.")
