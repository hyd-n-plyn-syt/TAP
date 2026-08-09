"""
Custom reload/restart command to broadcast the reload message immediately.
"""
from commands.command import Command
from world.discord_integration import send_to_mudinfo
import evennia
import time


class CmdRestart(Command):
    """
    Reload the server.

    Usage:
      @reload
      @restart

    Reloads the server game code, keeping portal and connections alive.
    """
    key = "@reload"
    aliases = ["@restart"]
    locks = "cmd:perm(reload) or perm(Developer)"
    help_category = "System"

    def func(self):
        send_to_mudinfo("|000**|105The server is r|104e|103l|102o|101a|102d|103i|104n|105g|100!|000**|n")
        time.sleep(1.2)
        evennia.SESSION_HANDLER.portal_restart_server()
