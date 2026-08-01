from commands.command import Command

VALID_MODES = ("numbers", "percent", "bars")


class CmdPromptMode(Command):
    """
    Set the style of your prompt.

    Usage:
      promptmode
      promptmode <numbers|percent|bars>

    With no argument the prompt mode cycles. The prompt shows your three
    pools (Vigor, Vim, Mens) as well as your current visarial state.

      numbers  - Vigor: 16/16  Vim: 16/16  Mens: 16/16
      percent  - Vigor: 100%   Vim: 100%   Mens: 100%
      bars     - Vigor: [##########]  Vim: [##########]  Mens: [##########]
    """
    key = "promptmode"
    aliases = ["pmode"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()

        if not arg:
            current = caller.db.promptmode or VALID_MODES[0]
            if current in VALID_MODES:
                idx = VALID_MODES.index(current)
            else:
                idx = -1
            arg = VALID_MODES[(idx + 1) % len(VALID_MODES)]

        if arg not in VALID_MODES:
            caller.msg(f"Usage: promptmode [{'|'.join(VALID_MODES)}] (no argument cycles).")
            return

        caller.db.promptmode = arg
        caller.msg(f"Prompt mode set to |w{arg}|n.")
