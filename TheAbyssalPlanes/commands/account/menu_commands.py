"""
Menu routers — quit/ooc always go back to the main menu instead of disconnecting.

These are account+character commands; they unpuppet (if puppeted) and launch
the main menu. Only menu option 0 disconnects.
"""

from evennia import Command
from evennia.utils.evmenu import EvMenu


def _launch_main_menu(account, session=None):
    if not account:
        return
    # Prefer provided session, else first session
    if not session:
        try:
            sess_list = account.sessions.all()
            if sess_list:
                session = sess_list[0]
        except Exception:
            pass
    try:
        EvMenu(account, "commands.account.main_menu", startnode="node_main", session=session, cmd_on_exit=None)
    except Exception as e:
        try:
            account.msg(f"|rCould not open main menu: {e}|n", session=session)
        except Exception:
            pass


class CmdQuitToMenu(Command):
    """
    Quit back to the main menu (not disconnect).

    Usage:
      quit

    While puppeting a character or your wisp, this returns you to the main
    menu where you can choose another character, go to the lounge, or exit
    the game (menu 0). To disconnect, choose 0 from the main menu.
    """

    key = "quit"
    aliases = ["exit", "q", "logout", "logoff"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        # Determine account and session
        caller = self.caller
        account = None
        session = getattr(self, "session", None)
        # self.caller may be Character or Account depending on puppet state
        # account_caller property not set — handle both
        try:
            from evennia.utils.utils import inherits_from
            if inherits_from(caller, "evennia.accounts.accounts.DefaultAccount"):
                account = caller
            elif hasattr(caller, "account") and caller.account:
                account = caller.account
            else:
                # Try self.account provided by MuxCommand
                account = getattr(self, "account", None) or getattr(self, "caller", None)
                if account and hasattr(account, "account") and account.account:
                    account = account.account
        except Exception:
            account = getattr(self, "account", None)

        if not account:
            # Fallback: caller itself may be account
            try:
                if hasattr(caller, "sessions"):
                    account = caller
            except Exception:
                pass
        if not account:
            self.msg("You must be logged in.")
            return

        # If we are puppeting a character/wisp, unpuppet first and go to menu
        puppet = None
        try:
            puppet = account.get_puppet(session) if session else None
            if not puppet:
                # Try any puppet
                all_puppets = account.get_all_puppets()
                if all_puppets:
                    puppet = all_puppets[0]
        except Exception:
            pass

        if puppet:
            # Remember last puppet if it's not a wisp
            try:
                from world.systems.wisp import is_wisp
                if not is_wisp(puppet):
                    account.db._last_puppet = puppet
            except Exception:
                pass
            try:
                account.unpuppet_object(session if session else account.sessions.all())
            except Exception as e:
                self.msg(f"|rCould not leave character: {e}|n")
                return
            self.msg("|wReturning to the main menu…|n")
            _launch_main_menu(account, session=session)
            return
        # Already OOC — just show menu
        _launch_main_menu(account, session=session)


class CmdOOCToMenu(Command):
    """
    Go OOC — returns to the main menu.

    Usage:
      ooc

    This is the OOC lounge channel now; to go out-of-character use quit
    (which brings you to the main menu). This alias also brings you to
    the main menu.
    """

    key = "ooc"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        # Delegate to quit-to-menu
        cmd = CmdQuitToMenu()
        cmd.caller = self.caller
        cmd.session = getattr(self, "session", None)
        cmd.account = getattr(self, "account", None)
        # Reuse same logic but simplified: unpuppet → menu
        caller = self.caller
        account = getattr(self, "account", None) or getattr(caller, "account", None) or caller
        session = getattr(self, "session", None)
        # If account is Character, resolve
        try:
            from evennia.utils.utils import inherits_from
            if not inherits_from(account, "evennia.accounts.accounts.DefaultAccount"):
                if hasattr(account, "account") and account.account:
                    account = account.account
        except Exception:
            pass
        # Reuse helper
        puppet = None
        try:
            puppet = account.get_puppet(session) if session and account else None
        except Exception:
            pass
        if puppet:
            try:
                from world.systems.wisp import is_wisp
                if not is_wisp(puppet):
                    account.db._last_puppet = puppet
            except Exception:
                pass
            try:
                account.unpuppet_object(session if session else account.sessions.all())
            except Exception:
                pass
            self.msg("|wReturning to the main menu…|n")
        _launch_main_menu(account, session=session)
