"""
Account main menu — first/last screen on login/quit.

EvMenu on the Account (account_caller via EvMenu caller = Account).
Options:
 0 Exit
 1 Choose character (shows count, handles 0 case)
 2 Create character (shows slots, blocks when full)
 3 Delete character (wisp excluded)
 4 Go to lounge (puppet wisp in #2)
"""

from evennia.objects.models import ObjectDB
from evennia.utils.evmenu import EvMenu
from evennia.utils import create as evennia_create


def _is_wisp(obj):
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
    return False


def _non_wisp_chars(account):
    from world.systems.wisp import non_wisp_characters
    return non_wisp_characters(account)


def _slots_info(account):
    try:
        total = account.get_character_slots()
    except Exception:
        total = 3
    if total is None:
        total = 99
    used = len(_non_wisp_chars(account))
    avail = max(0, total - used) if total != 99 else 99
    return used, total, avail


def _get_lounge():
    try:
        return ObjectDB.objects.get_id(2)
    except Exception:
        return None


# ── main node ──────────────────────────────────────────────────────────


def _close_menu(caller):
    try:
        menu = getattr(caller.ndb, "_evmenu", None)
        if menu:
            menu.close_menu()
    except Exception:
        pass


def node_main(caller, raw_string, **kwargs):
    chars = _non_wisp_chars(caller)
    n = len(chars)
    used, total, avail = _slots_info(caller)
    lines = []
    lines.append("|w════════ The Abyssal Planes — Main Menu ════════|n")
    lines.append("")
    lines.append(f"|wAccount:|n {caller.key}  |wCharacters:|n {n}  |wSlots:|n {used}/{total} used")
    if n == 0:
        lines.append("|xYou have no characters yet — choose |w2|n|x to create one.|n")
    elif avail <= 0:
        lines.append(f"|rSlots full ({used}/{total}) — delete a character to make room.|n")
    lines.append("")
    lines.append("|xSelect an option below.|n")
    text = "\n".join(lines)

    # Handle raw aliases that should not go through normal number routing
    # (EvMenu will still parse them as option keys, but we also support text)
    options = (
        {"key": "0", "desc": "Exit the game.", "goto": "node_exit_confirm"},
        {"key": "1", "desc": "Choose a character.", "goto": _handle_choose},
        {"key": "2", "desc": "Create a character.", "goto": _handle_create},
        {"key": "3", "desc": "Delete a character.", "goto": "node_delete_list"},
        {"key": "4", "desc": "Go to the lounge.", "goto": "node_enter_lounge"},
    )
    return text, options


def _handle_choose(caller, raw_string, **kwargs):
    chars = _non_wisp_chars(caller)
    if not chars:
        caller.msg("|xYou have no characters yet. Choose |w2|n|x to create one.|n")
        return "node_main"
    return "node_choose_list"


def _handle_create(caller, raw_string, **kwargs):
    used, total, avail = _slots_info(caller)
    if avail <= 0:
        caller.msg(f"|rYou have used all {total} character slots.|n")
        return "node_main"
    return "node_create_name"


def node_enter_lounge(caller, raw_string, **kwargs):
    from world.systems.wisp import get_or_create_wisp, wisp_needs_setup
    # Close main menu before puppet
    _close_menu(caller)
    session = None
    try:
        sess_list = caller.sessions.all()
        if sess_list:
            session = sess_list[0]
    except Exception:
        pass
    if not session:
        try:
            if hasattr(caller.ndb, "_evmenu") and caller.ndb._evmenu:
                session = getattr(caller.ndb._evmenu, "session", None) or getattr(caller.ndb._evmenu, "_session", None)
        except Exception:
            pass
    try:
        wisp = get_or_create_wisp(caller, session=session)
    except Exception as e:
        caller.msg(f"|rCould not create your wisp: {e}. Contact staff.|n")
        try:
            from evennia.utils.evmenu import EvMenu
            EvMenu(caller, "commands.account.main_menu", startnode="node_main", session=session, auto_quit=False, auto_look=False, auto_help=False)
        except Exception:
            pass
        return None, None
    if not wisp:
        caller.msg("|rCould not create your wisp. Contact staff (check server log).|n")
        try:
            from evennia.utils.evmenu import EvMenu
            EvMenu(caller, "commands.account.main_menu", startnode="node_main", session=session, auto_quit=False, auto_look=False, auto_help=False)
        except Exception:
            pass
        return None, None
    lounge = _get_lounge()
    if lounge and wisp.location != lounge:
        try:
            wisp.location = lounge
        except Exception:
            pass
    try:
        if session:
            caller.puppet_object(session, wisp)
        else:
            for sess in caller.sessions.all():
                try:
                    caller.puppet_object(sess, wisp)
                    session = sess
                    break
                except Exception:
                    continue
    except Exception as e:
        caller.msg(f"|rCould not enter the lounge: {e}|n")
        try:
            from evennia.utils.evmenu import EvMenu
            EvMenu(caller, "commands.account.main_menu", startnode="node_main", session=session, auto_quit=False, auto_look=False, auto_help=False)
        except Exception:
            pass
        return None, None
    needs = wisp_needs_setup(wisp)
    if needs:
        try:
            from evennia.utils.evmenu import EvMenu as _EvMenu2
            _EvMenu2(wisp, "commands.account.wisp_menu", startnode="node_welcome", session=session, cmd_on_exit="look")
        except Exception as e:
            caller.msg(f"|rWisp setup failed: {e}|n")
            try:
                wisp.execute_cmd("look", session=session)
            except Exception:
                pass
    else:
        try:
            if hasattr(wisp, "get_prompt"):
                wisp.msg(prompt=wisp.get_prompt(), session=session)
        except Exception:
            pass
        try:
            if getattr(wisp.db, "is_autowhere", False):
                wisp.send_autowhere()
        except Exception:
            pass
    return None, None


def _handle_lounge(caller, raw_string, **kwargs):
    return node_enter_lounge(caller, raw_string, **kwargs)


def node_exit_confirm(caller, raw_string, **kwargs):
    text = "|rAre you sure you want to quit?|n  Type |wyes|n to disconnect, anything else to stay."
    options = {"key": "_default", "goto": _do_exit}
    return text, options


def _do_exit(caller, raw_string, **kwargs):
    if raw_string.strip().lower() in ("yes", "y", "0"):
        # Disconnect all sessions
        try:
            for sess in list(caller.sessions.all()):
                try:
                    caller.disconnect_session_from_account(sess, reason="quit")
                except Exception:
                    pass
        except Exception:
            pass
        return None
    caller.msg("Stayed at the main menu.")
    return "node_main"


# ── choose list ────────────────────────────────────────────────────────

def node_choose_list(caller, raw_string, **kwargs):
    chars = _non_wisp_chars(caller)
    if not chars:
        caller.msg("You have no characters.")
        return "node_main", ()
    # Intro only — options grid will list characters
    text = "|wChoose a character to play:|n\n\n|xSelect a number, or |wb|n|x to go back.|n"
    # Build options: 1..N -> puppet, b -> back
    opts = []
    for idx, char in enumerate(chars, start=1):
        try:
            from world.data import species as species_data
            sk = char.attributes.get("species_key", default=None)
            sname = species_data.species_name(sk) if sk else ""
        except Exception:
            sname = ""
        extra = f" ({sname})" if sname else ""
        opts.append({"key": str(idx), "desc": f"{char.key}{extra}", "goto": ("node_puppet_choice", {"char": char})})
    opts.append({"key": ("b", "back"), "desc": "Back", "goto": "node_main"})
    opts.append({"key": "_default", "goto": (_pick_char_by_name, {"chars": chars})})
    return text, opts


def node_puppet_choice(caller, raw_string, **kwargs):
    char = kwargs.get("char")
    if not char:
        return "node_choose_list", ()
    _close_menu(caller)
    session = None
    try:
        sess_list = caller.sessions.all()
        if sess_list:
            session = sess_list[0]
    except Exception:
        pass
    try:
        caller.puppet_object(session, char)
        caller.db._last_puppet = char
        # at_post_puppet already does "You become" + look; fire prompt + autowhere once at menu exit
        try:
            if hasattr(char, "get_prompt"):
                char.msg(prompt=char.get_prompt(), session=session)
        except Exception:
            pass
        try:
            if getattr(char.db, "is_autowhere", False):
                char.send_autowhere()
        except Exception:
            pass
    except Exception as e:
        caller.msg(f"|rCould not puppet {char.key}: {e}|n")
        try:
            from evennia.utils.evmenu import EvMenu
            EvMenu(caller, "commands.account.main_menu", startnode="node_choose_list", session=session, auto_quit=False, auto_look=False, auto_help=False)
        except Exception:
            pass
        return None, None
    return None, None


def _pick_char_by_name(caller, raw_string, **kwargs):
    raw = raw_string.strip()
    if not raw:
        return "node_choose_list"
    if raw.lower() in ("b", "back"):
        return "node_main"
    chars = kwargs.get("chars", [])
    for c in chars:
        if c.key.lower() == raw.lower():
            return "node_puppet_choice", {"char": c}
    if raw.isdigit():
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(chars):
                return "node_puppet_choice", {"char": chars[idx]}
        except Exception:
            pass
    caller.msg("Not a valid choice.")
    return "node_choose_list"


# ── create name ──────────────────────────────────────────────────────

def node_create_name(caller, raw_string, **kwargs):
    used, total, avail = _slots_info(caller)
    if avail <= 0:
        caller.msg(f"|rYou have used all {total} character slots.|n")
        return "node_main"
    text = (
        f"|wCreate a character|n ({used}/{total} slots used)\n\n"
        "Enter a name for your new character, or |wb|n to go back."
    )
    options = {"key": "_default", "goto": _do_create_name}
    return text, options


def _do_create_name(caller, raw_string, **kwargs):
    raw = raw_string.strip()
    if not raw:
        return "node_create_name"
    if raw.lower() in ("b", "back"):
        return "node_main"

    name = raw.split("=")[0].strip()
    if not name:
        caller.msg("You must provide a name.")
        return "node_create_name"

    # Check wisp name collision (wisp shares account key)
    if name.lower() == caller.key.lower():
        caller.msg("That name is reserved for your wisp (your account name). Choose another.")
        return "node_create_name"

    # Duplicate check among non-wisp chars (case-insensitive)
    for c in _non_wisp_chars(caller):
        if c.key.lower() == name.lower():
            caller.msg(f"You already have a character named '{name}'.")
            return "node_create_name"

    # Slot check again
    used, total, avail = _slots_info(caller)
    if avail <= 0:
        caller.msg(f"|rYou have used all {total} character slots.|n")
        return "node_main"

    caller.ndb._chargen_name = name
    caller.msg(f"Creating |w{name}|n…")
    caller.ndb._return_to_main = True
    caller.ndb._launch_chargen_pending = True
    return "node_launch_chargen"


def node_launch_chargen(caller, raw_string, **kwargs):
    # Launched from _do_create_name — actually start chargen and close this menu
    sess = None
    try:
        sess_list = caller.sessions.all()
        if sess_list:
            sess = sess_list[0]
    except Exception:
        pass
    try:
        EvMenu(caller, "commands.account.chargen_menu", startnode="node_welcome", session=sess, cmd_on_exit=None)
    except Exception as e:
        caller.msg(f"|rCould not start chargen: {e}|n")
        return "node_main", ()
    return None, None


# ── delete list ──────────────────────────────────────────────────────

def node_delete_list(caller, raw_string, **kwargs):
    chars = _non_wisp_chars(caller)
    if not chars:
        caller.msg("You have no deletable characters.")
        return "node_main", ()
    text = "|wDelete which character?|n |r(This cannot be undone!)|n\n\n|xSelect or |wb|n|x to go back.|n"
    opts = []
    for idx, char in enumerate(chars, start=1):
        opts.append({"key": str(idx), "desc": char.key, "goto": (_confirm_delete, {"char": char})})
    opts.append({"key": ("b", "back"), "desc": "Back", "goto": "node_main"})
    opts.append({"key": "_default", "goto": (_delete_by_name, {"chars": chars})})
    return text, opts


def _delete_by_name(caller, raw_string, **kwargs):
    raw = raw_string.strip()
    if raw.lower() in ("b", "back", ""):
        return "node_delete_list" if raw == "" else "node_main"
    chars = kwargs.get("chars", [])
    if raw.isdigit():
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(chars):
                return _confirm_delete(caller, raw_string, char=chars[idx])
        except Exception:
            pass
    for c in chars:
        if c.key.lower() == raw.lower():
            return _confirm_delete(caller, raw_string, char=c)
    caller.msg("Not a valid choice.")
    return "node_delete_list"


def _confirm_delete(caller, raw_string, **kwargs):
    char = kwargs.get("char")
    if not char:
        return "node_delete_list"
    # Block wisp deletion explicitly
    if _is_wisp(char):
        caller.msg("|rYou cannot delete your wisp.|n")
        return "node_delete_list"
    if char.key.lower() == caller.key.lower():
        caller.msg("|rYou cannot delete your wisp.|n")
        return "node_delete_list"
    caller.ndb._char_to_delete = char
    text = f"|rPermanently delete |w{char.key}|n|r? This cannot be undone. Type |wyes|n to confirm, anything else to cancel.|n"
    return text, {"key": "_default", "goto": _do_delete}


def _do_delete(caller, raw_string, **kwargs):
    char = getattr(caller.ndb, "_char_to_delete", None)
    if not char:
        return "node_main"
    raw = raw_string.strip().lower()
    # Clear ndb regardless
    try:
        del caller.ndb._char_to_delete
    except Exception:
        pass
    if raw not in ("yes", "y"):
        caller.msg("Deletion cancelled.")
        return "node_main"
    # Permission check
    try:
        if not char.access(caller, "delete"):
            caller.msg("You do not have permission to delete that character.")
            return "node_main"
    except Exception:
        pass
    # Block wisp again
    if _is_wisp(char):
        caller.msg("|rYou cannot delete your wisp.|n")
        return "node_main"
    key = char.key
    try:
        # Remove from playable handler then delete
        try:
            caller.characters.remove(char)
        except Exception:
            pass
        # Clear _last_puppet if needed
        try:
            if caller.db._last_puppet and caller.db._last_puppet.id == char.id:
                caller.db._last_puppet = None
        except Exception:
            pass
        char.delete()
        caller.msg(f"|gCharacter |w{key}|n|g deleted.|n")
        from evennia.utils import logger
        logger.log_sec(f"Character Deleted: {key} (Caller: {caller}).")
    except Exception as e:
        caller.msg(f"|rCould not delete {key}: {e}|n")
    return "node_main"
