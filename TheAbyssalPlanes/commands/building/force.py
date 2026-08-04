"""
Staff command to force an object to execute a command.
Overrides the default 'force' to search globally and across planes, so
staff can command anyone no matter where they are or whether they can
see them.
"""
from commands.command import GameMuxCommand


class CmdForce(GameMuxCommand):
    """
    Forces an object to execute a command.

    Usage:
      force <object>=<command string>

    Examples:
      force prism=say Over here!
      force bob=get stick
      force #58=say test

    Searches the whole world (not just the current room) and ignores
    planar visibility, so staff can order characters they cannot see.
    """
    key = "force"
    aliases = ["@force"]
    locks = "cmd:perm(spawn) or perm(Builder)"
    help_category = "Building"
    perm_used = "edit"

    def func(self):
        caller = self.caller
        if not self.lhs or not self.rhs:
            caller.msg("You must provide a target and a command string to execute.")
            return
        targ = caller.search(self.lhs, global_search=True, use_dbref=True)
        if not targ:
            return
        if not targ.access(caller, self.perm_used):
            caller.msg(f"You don't have permission to force {targ} to execute commands.")
            return
        targ.execute_cmd(self.rhs)
        caller.msg(f"You have forced {targ} to: {self.rhs}")
