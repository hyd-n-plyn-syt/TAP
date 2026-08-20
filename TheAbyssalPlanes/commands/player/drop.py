from evennia import utils
from evennia.commands.default.general import NumberedTargetCommand
from world.systems.narrative import colored_self, narrative_name


class CmdDrop(NumberedTargetCommand):
    """
    drop something

    Usage:
      drop <obj>

    Lets you drop an object from your inventory into the
    location you are currently in. Furniture is placed at your feet
    and you sit down on it automatically.
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Drop what?")
            return

        objs = caller.search(
            self.args,
            location=caller,
            nofound_string=f"You aren't carrying {self.args}.",
            multimatch_string=f"You carry more than one {self.args}:",
            stacked=self.number,
        )
        if not objs:
            return
        objs = utils.make_iter(objs)

        for obj in objs:
            if not obj.at_pre_drop(caller):
                return

        moved = []
        for obj in objs:
            if obj.move_to(caller.location, quiet=True, move_type="drop"):
                moved.append(obj)
                obj.at_drop(caller)

        if not moved:
            self.msg("That can't be dropped.")
            return

        room = caller.location
        for obj in moved:
            drop_action = getattr(obj.db, "_drop_action", None)
            if obj.is_typeclass("typeclasses.furniture.Furniture"):
                obj_name = narrative_name(obj)
            else:
                obj_name = obj.get_numbered_name(1, caller, return_string=True)

            if drop_action:
                caller.msg(f"{colored_self(caller, True)} drop {obj_name} {drop_action}.")
                if room:
                    for observer in room.contents:
                        if observer is caller or not getattr(observer, "is_creature", False):
                            continue
                        see_item = obj.visible_to(observer)
                        see_dropper = caller.visible_to(observer)
                        if not see_item:
                            continue
                        if see_dropper:
                            observer.msg(f"{caller.appearance_name} drops {obj_name} {drop_action}.")
                        else:
                            observer.msg(f"{obj_name} appears and someone {drop_action.lstrip('and ')}.")
                obj.db._drop_action = None
            else:
                caller.msg(f"{colored_self(caller, True)} drop {obj_name}.")
                if room:
                    for observer in room.contents:
                        if observer is caller or not getattr(observer, "is_creature", False):
                            continue
                        see_item = obj.visible_to(observer)
                        see_dropper = caller.visible_to(observer)
                        if not see_item:
                            continue
                        if see_dropper:
                            observer.msg(f"{caller.appearance_name} drops {obj_name}.")
                        else:
                            observer.msg(f"{obj_name} appears.")
