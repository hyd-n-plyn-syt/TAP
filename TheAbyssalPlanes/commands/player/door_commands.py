from commands.command import Command


def _find_exit(caller, name):
    if not caller.location:
        return None
    name_lower = name.lower()
    for obj in caller.location.contents:
        if not obj.destination:
            continue
        if obj.key.lower() == name_lower:
            return obj
        for alias in (obj.aliases.all() or []):
            if alias.lower() == name_lower:
                return obj
    return None


class CmdOpen(Command):
    """
    Open a door.

    Usage:
      open <exit>
    """
    key = "open"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.msg("Open what?")
            return
        exit_obj = _find_exit(self.caller, self.args.strip())
        if not exit_obj:
            self.msg("You don't see that here.")
            return
        exit_obj.open_door(self.caller)


class CmdClose(Command):
    """
    Close a door.

    Usage:
      close <exit>
    """
    key = "close"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.msg("Close what?")
            return
        exit_obj = _find_exit(self.caller, self.args.strip())
        if not exit_obj:
            self.msg("You don't see that here.")
            return
        exit_obj.close_door(self.caller)


class CmdLock(Command):
    """
    Lock a door.

    Usage:
      lock <exit>
    """
    key = "lock"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.msg("Lock what?")
            return
        exit_obj = _find_exit(self.caller, self.args.strip())
        if not exit_obj:
            self.msg("You don't see that here.")
            return
        exit_obj.lock_door(self.caller)


class CmdUnlock(Command):
    """
    Unlock a door.

    Usage:
      unlock <exit>
    """
    key = "unlock"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        if not self.args:
            self.msg("Unlock what?")
            return
        exit_obj = _find_exit(self.caller, self.args.strip())
        if not exit_obj:
            self.msg("You don't see that here.")
            return
        exit_obj.unlock_door(self.caller)


class CmdAutoOpen(Command):
    """
    Toggle automatic door handling.

    Usage:
      autoopen

    When enabled, walking into a locked door you have the key for
    will automatically unlock and open it.
    """
    key = "autoopen"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        current = getattr(self.caller.db, "autoopen", False)
        new_val = not current
        self.caller.db.autoopen = new_val
        if new_val:
            self.caller.msg("You will now automatically unlock and open doors.")
        else:
            self.caller.msg("Automatic door handling disabled.")
