"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

Exits support door/lock, breakable wall, and hidden exit mechanics via
attributes set during creation (see commands/building/dig_menu.py):

    is_door, is_open, is_locked, key_id, lockpick_dc,
    is_breakable, bash_dc, is_hidden, detect_dc, sibling_id

Traversal checks is_open before allowing movement.  Traversal failures
check the caller's inventory for a key (locked doors) and reference
lockpick/bash/awareness skills for contextual messages.
"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exit.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.is_door = False
        self.db.is_open = False
        self.db.is_locked = False
        self.db.key_id = None
        self.db.lockpick_dc = 0
        self.db.is_breakable = False
        self.db.bash_dc = 0
        self.db.is_hidden = False
        self.db.detect_dc = 0
        self.db.sibling_id = None

    def at_traverse(self, traversing_object, target_location, **kwargs):
        is_door = getattr(self.db, "is_door", False)
        is_open = getattr(self.db, "is_open", False)
        if is_door and not is_open:
            self.at_failed_traverse(traversing_object, **kwargs)
            return
        super().at_traverse(traversing_object, target_location, **kwargs)

    def _has_key(self, caller):
        key_id = getattr(self.db, "key_id", None)
        if not key_id:
            return False
        from evennia.objects.objects import ObjectDB
        try:
            key = ObjectDB.objects.get(id=key_id)
            return key in caller.contents
        except ObjectDB.DoesNotExist:
            return False

    def open_door(self, caller):
        is_door = getattr(self.db, "is_door", False)
        if not is_door:
            caller.msg("That's not a door.")
            return
        if getattr(self.db, "is_open", False):
            caller.msg("It's already open.")
            return
        if getattr(self.db, "is_locked", False):
            if self._has_key(caller):
                self.db.is_locked = False
                sibling = self._get_sibling()
                if sibling:
                    sibling.db.is_locked = False
                caller.msg(f"You unlock and open {self.key}.")
            else:
                caller.msg(f"{self.key} is locked.")
                return
        else:
            caller.msg(f"You open {self.key}.")
        self.db.is_open = True
        if self.location:
            for char in self.location.contents_get(content_type="character"):
                if char != caller:
                    char.msg(f"{caller.key} opens {self.key}.")
        sibling = self._get_sibling()
        if sibling:
            sibling.db.is_open = True
            if sibling.location:
                for char in sibling.location.contents_get(content_type="character"):
                    char.msg(f"{sibling.key} opens from the other side.")
        self._sync_door()

    def close_door(self, caller):
        is_door = getattr(self.db, "is_door", False)
        if not is_door:
            caller.msg("That's not a door.")
            return
        if not getattr(self.db, "is_open", False):
            caller.msg("It's already closed.")
            return
        self.db.is_open = False
        caller.msg(f"You close {self.key}.")
        if self.location:
            for char in self.location.contents_get(content_type="character"):
                if char != caller:
                    char.msg(f"{caller.key} closes {self.key}.")
        sibling = self._get_sibling()
        if sibling and sibling.location:
            for char in sibling.location.contents_get(content_type="character"):
                char.msg(f"{sibling.key} closes from the other side.")
        self._sync_door()

    def _get_sibling(self):
        sibling_id = getattr(self.db, "sibling_id", None)
        if not sibling_id:
            return None
        from evennia.objects.objects import ObjectDB
        try:
            return ObjectDB.objects.get(id=sibling_id)
        except ObjectDB.DoesNotExist:
            return None

    def _sync_door(self):
        sibling = self._get_sibling()
        if sibling:
            sibling.db.is_open = self.db.is_open

    def lock_door(self, caller):
        is_door = getattr(self.db, "is_door", False)
        if not is_door:
            caller.msg("That's not a door.")
            return
        if getattr(self.db, "is_locked", False):
            caller.msg(f"{self.key} is already locked.")
            return
        if not self._has_key(caller):
            caller.msg("You don't have the key.")
            return
        was_open = getattr(self.db, "is_open", False)
        self.db.is_locked = True
        self.db.is_open = False
        sibling = self._get_sibling()
        if sibling:
            sibling.db.is_locked = True
            sibling.db.is_open = False
        if was_open:
            caller.msg(f"You close and lock {self.key}.")
        else:
            caller.msg(f"You lock {self.key}.")
        if self.location:
            for char in self.location.contents_get(content_type="character"):
                if char != caller:
                    if was_open:
                        char.msg(f"{caller.key} closes and locks {self.key}.")
                    else:
                        char.msg(f"{caller.key} locks {self.key}.")
        if sibling and sibling.location:
            for char in sibling.location.contents_get(content_type="character"):
                char.msg(f"{sibling.key} locks from the other side.")

    def unlock_door(self, caller):
        is_door = getattr(self.db, "is_door", False)
        if not is_door:
            caller.msg("That's not a door.")
            return
        if not getattr(self.db, "is_locked", False):
            caller.msg(f"{self.key} is already unlocked.")
            return
        if not self._has_key(caller):
            caller.msg("You don't have the key.")
            return
        self.db.is_locked = False
        sibling = self._get_sibling()
        if sibling:
            sibling.db.is_locked = False
        caller.msg(f"You unlock {self.key}.")
        if self.location:
            for char in self.location.contents_get(content_type="character"):
                if char != caller:
                    char.msg(f"{caller.key} unlocks {self.key}.")
        if sibling and sibling.location:
            for char in sibling.location.contents_get(content_type="character"):
                char.msg(f"{sibling.key} unlocks from the other side.")

    def at_failed_traverse(self, traversing_object, **kwargs):
        is_locked = getattr(self.db, "is_locked", False)
        is_breakable = getattr(self.db, "is_breakable", False)

        if is_locked:
            if self._has_key(traversing_object):
                autoopen = getattr(traversing_object.db, "autoopen", False)
                if autoopen:
                    self.open_door(traversing_object)
                    if not getattr(self.db, "is_open", False):
                        return
                    super().at_traverse(traversing_object, self.destination, **kwargs)
                    return
                else:
                    traversing_object.msg(
                        f"{self.key} is locked. You could unlock it, or "
                        f"type |wautoopen|n to toggle automatic door handling."
                    )
                    return

            skills = traversing_object.db.skills or {}
            has_lockpick = "lockpick" in skills
            has_bash = "bash" in skills

            if has_lockpick and has_bash:
                traversing_object.msg(
                    f"{self.key} is locked. You could try to pick the lock "
                    f"or bash it down."
                )
            elif has_lockpick:
                traversing_object.msg(
                    f"{self.key} is locked. You might be able to pick it "
                    f"if you had a lockpick."
                )
            elif has_bash:
                traversing_object.msg(
                    f"{self.key} is locked. You could try to bash it down."
                )
            else:
                traversing_object.msg(f"{self.key} is locked.")
            return

        if is_breakable:
            skills = traversing_object.db.skills or {}
            if "bash" in skills:
                traversing_object.msg(
                    f"{self.key} is solid. You need to bash through it."
                )
            else:
                traversing_object.msg(
                    f"{self.key} is solid. There's nothing you can do about it."
                )
            return

        traversing_object.msg(
            f"{self.key} is closed. Type |wopen {self.key}|n to open it, "
            f"or |wautoopen|n to toggle automatic door handling."
        )

    @classmethod
    def filter_visible(cls, obj_list, looker, **kwargs):
        visible = []
        for obj in obj_list:
            if obj == looker:
                continue
            if getattr(obj.db, "is_hidden", False) and getattr(obj.db, "detect_dc", 0) > 0:
                skills = getattr(looker.db, "skills", None) or {}
                awareness = skills.get("awareness", 0)
                if awareness >= obj.db.detect_dc:
                    visible.append(obj)
                continue
            if obj.access(looker, "view") and obj.access(looker, "search", default=True):
                visible.append(obj)
        return visible
