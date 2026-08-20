from evennia import utils
from evennia.commands.default.general import NumberedTargetCommand


class CmdGet(NumberedTargetCommand):
    """
    pick up something

    Usage:
      get <obj>

    Picks up an object from your location and puts it in your inventory.
    You must be standing next to or on the same tile as the object.
    """

    key = "get"
    aliases = "grab"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def _is_near(self, caller, obj):
        cx = getattr(caller.db, "pos_x", 0)
        cy = getattr(caller.db, "pos_y", 0)
        if hasattr(obj, "is_at_coord"):
            if obj.is_at_coord(cx, cy):
                return True
            tiles = []
            px = getattr(obj.db, "pos_x", None)
            py = getattr(obj.db, "pos_y", None)
            if px is not None and py is not None:
                tiles.append((px, py))
            for ex, ey in (getattr(obj.db, "extra_coords", None) or []):
                tiles.append((ex, ey))
            return any(max(abs(cx - tx), abs(cy - ty)) <= 1 for tx, ty in tiles)
        ox = getattr(obj.db, "pos_x", None)
        oy = getattr(obj.db, "pos_y", None)
        if ox is None or oy is None:
            return True
        return max(abs(cx - ox), abs(cy - oy)) <= 1

    def _is_on(self, caller, obj):
        cx = getattr(caller.db, "pos_x", 0)
        cy = getattr(caller.db, "pos_y", 0)
        if hasattr(obj, "is_at_coord") and obj.is_at_coord(cx, cy):
            return True
        ox = getattr(obj.db, "pos_x", None)
        oy = getattr(obj.db, "pos_y", None)
        if ox is None or oy is None:
            return False
        return cx == ox and cy == oy

    def func(self):
        caller = self.caller

        if not self.args:
            self.msg("Get what?")
            return
        objs = caller.search(self.args, location=caller.location, stacked=self.number)
        if not objs:
            return
        objs = utils.make_iter(objs)

        if len(objs) == 1 and caller == objs[0]:
            self.msg("You can't get yourself.")
            return

        for obj in objs:
            if getattr(obj, "is_creature", False):
                continue
            if not self._is_near(caller, obj):
                name = obj.get_display_name(caller)
                caller.msg(f"{name} is too far away. You need to be right next to it.")
                return
            if self._is_on(caller, obj):
                name = obj.get_display_name(caller)
                caller.msg(f"You'll need to stand up from {name} first.")
                return

        for obj in objs:
            if not obj.access(caller, "get"):
                if obj.db.get_err_msg:
                    self.msg(obj.db.get_err_msg)
                else:
                    self.msg("You can't get that.")
                return
            if not obj.at_pre_get(caller):
                return

        moved = []
        for obj in objs:
            if obj.move_to(caller, quiet=True, move_type="get"):
                moved.append(obj)
                obj.at_get(caller)

        if not moved:
            self.msg("That can't be picked up.")
        else:
            obj_name = moved[0].get_numbered_name(len(moved), caller, return_string=True)
            caller.location.msg_contents(f"$You() $conj(pick) up {obj_name}.", from_obj=caller)
