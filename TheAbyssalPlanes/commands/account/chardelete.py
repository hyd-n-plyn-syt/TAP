"""
chardelete for the main menu — wisp excluded.

Usage: chardelete <name> (rarely used directly; main menu option 3 is primary).
"""

from evennia import Command
from evennia.utils.evmenu import get_input
from evennia.utils import logger


def _is_wisp(obj, account=None):
    if not obj:
        return False
    if getattr(obj, "is_wisp", False):
        return True
    try:
        tc = getattr(obj, "typeclass_path", "") or ""
        if "wisp" in tc.lower():
            return True
        if getattr(obj.db, "species_key", None) == "wisp":
            return True
    except Exception:
        pass
    if account and obj.key.lower() == account.key.lower():
        # Same name as account is wisp — be conservative and check species too
        try:
            if getattr(obj.db, "species_key", None) == "wisp":
                return True
            # If it has wisp tag, block
            if obj.tags.get("wisp", category="account") or obj.tags.get("ooc_wisp", category="account"):
                return True
        except Exception:
            pass
    return False


class CmdCharDelete(Command):
    """
    Delete one of your characters (cannot delete your wisp).

    Usage:
      chardelete <name>

    Permanently deletes a character. The wisp (your account character) cannot
    be deleted.
    """

    key = "chardelete"
    aliases = ["deletechar", "delchar"]
    locks = "cmd:pperm(Player)"
    help_category = "General"
    account_caller = True

    def func(self):
        account = self.account
        if not account:
            self.msg("You must be logged in.")
            return
        if not self.args:
            self.msg("Usage: chardelete <name>")
            return

        name = self.args.strip()
        # Block wisp name
        if name.lower() == account.key.lower():
            self.msg("|rYou cannot delete your wisp.|n")
            return

        # Find match among non-wisp characters
        from world.systems.wisp import non_wisp_characters

        candidates = [c for c in non_wisp_characters(account) if c.key.lower() == name.lower()]
        if not candidates:
            self.msg("You have no such character to delete.")
            return
        if len(candidates) > 1:
            self.msg("Multiple matches — contact staff.")
            return

        char = candidates[0]
        if _is_wisp(char, account):
            self.msg("|rYou cannot delete your wisp.|n")
            return
        if not char.access(account, "delete"):
            self.msg("You do not have permission to delete that character.")
            return

        caller = self.caller  # Account

        def _callback(caller_inner, prompt, result):
            if result.strip().lower() not in ("yes", "y"):
                caller_inner.msg("Deletion cancelled.")
                try:
                    del caller_inner.ndb._char_to_delete
                except Exception:
                    pass
                return
            delobj = getattr(caller_inner.ndb, "_char_to_delete", None)
            if not delobj:
                caller_inner.msg("Nothing to delete.")
                return
            if _is_wisp(delobj, caller_inner):
                caller_inner.msg("|rYou cannot delete your wisp.|n")
                try:
                    del caller_inner.ndb._char_to_delete
                except Exception:
                    pass
                return
            key = delobj.key
            try:
                try:
                    caller_inner.characters.remove(delobj)
                except Exception:
                    pass
                try:
                    if getattr(caller_inner.db, "_last_puppet", None) and caller_inner.db._last_puppet.id == delobj.id:
                        caller_inner.db._last_puppet = None
                except Exception:
                    pass
                delobj.delete()
                caller_inner.msg(f"|gCharacter |w{key}|n|g deleted.|n")
                logger.log_sec(f"Character Deleted: {key} (Caller: {caller_inner}).")
            except Exception as e:
                caller_inner.msg(f"|rCould not delete {key}: {e}|n")
            try:
                del caller_inner.ndb._char_to_delete
            except Exception:
                pass

        caller.ndb._char_to_delete = char
        prompt = f"|rPermanently delete |w{char.key}|n|r? This cannot be undone. Type |wyes|n to confirm, anything else to cancel.|n"
        get_input(caller, prompt, _callback)
