from commands.command import Command


class CmdPerceive(Command):
    key = "perceive"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        current = caller.attributes.get("visarial_state", default="normal")
        data = caller.species

        if not caller.can_perceive:
            caller.msg("Your kind cannot perceive the visarial realm.")
            return

        if data and data["visarial_nature"] == "visarial":
            if current == "perceiving":
                caller.set_state("normal")
                caller.msg("You turn your awareness away from the physical plane.")
            elif current == "normal":
                caller.set_state("perceiving")
                caller.msg(
                    "You begin to perceive the physical plane from within the visarial realm."
                )
            else:
                caller.set_state("perceiving")
                caller.msg(
                    "You withdraw to the visarial realm, perceiving the physical plane."
                )
            return

        if current == "normal":
            caller.set_state("perceiving")
            caller.msg("You begin to perceive the visarial realm.")
        elif current == "perceiving":
            caller.set_state("normal")
            caller.msg("You cease perceiving the visarial realm.")
        elif current == "manifested":
            caller.set_state("perceiving")
            caller.msg("You shift your focus to perceiving rather than manifesting.")
