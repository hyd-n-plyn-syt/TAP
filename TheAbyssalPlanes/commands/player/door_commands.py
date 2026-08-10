from commands.command import Command


def _find_exit(caller, name):
    if not caller.location:
        return None
    name_lower = name.lower()

    if name_lower == "door":
        from combat.grid import get_exit_coords
        px = getattr(caller.db, "pos_x", None)
        py = getattr(caller.db, "pos_y", None)
        best = None
        best_dist = None
        for obj in caller.location.contents:
            if not getattr(obj, "destination", None):
                continue
            if not getattr(obj.db, "is_door", False):
                continue
            coords = get_exit_coords(caller.location, obj)
            if not coords:
                best = obj
                break
            if px is None or py is None:
                best = obj
                break
            dist = abs(int(px) - int(coords[0])) + abs(int(py) - int(coords[1]))
            if best_dist is None or dist < best_dist:
                best = obj
                best_dist = dist
        return best

    for obj in caller.location.contents:
        if not obj.destination:
            continue
        if obj.key.lower() == name_lower:
            return obj
        for alias in (obj.aliases.all() or []):
            if alias.lower() == name_lower:
                return obj
    return None


def _at_exit(caller, exit_obj):
    """Return True if the caller is standing at the exit's grid coordinate."""
    from combat.grid import get_exit_coords
    coords = get_exit_coords(caller.location, exit_obj)
    if not coords:
        return True
    px = getattr(caller.db, "pos_x", None)
    py = getattr(caller.db, "pos_y", None)
    if px is None or py is None:
        return True
    return (int(px), int(py)) == (int(coords[0]), int(coords[1]))


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
        if not _at_exit(self.caller, exit_obj):
            self.msg("You need to be right at the door to do that.")
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
        if not _at_exit(self.caller, exit_obj):
            self.msg("You need to be right at the door to do that.")
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
        if not _at_exit(self.caller, exit_obj):
            self.msg("You need to be right at the door to do that.")
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
        if not _at_exit(self.caller, exit_obj):
            self.msg("You need to be right at the door to do that.")
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
