from evennia import Command


class CmdDirectionFallback(Command):
    key = "direction_fallback"
    aliases = [
        "north", "south", "east", "west",
        "northeast", "northwest", "southeast", "southwest",
        "n", "s", "e", "w", "ne", "nw", "se", "sw",
        "up", "down", "in", "out", "enter", "leave",
    ]
    locks = "cmd:all()"
    auto_help = False

    def func(self):
        self.caller.msg("You cannot move in that direction.")
