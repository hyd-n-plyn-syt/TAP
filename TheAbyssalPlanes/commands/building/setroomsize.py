from evennia import Command

class CmdSetRoomSize(Command):
    """
    Set the size of the current room for grid combat.
    Usage:
        SETROOMSIZE <size>
        SETROOMSIZE CUSTOM <width> <height>
    """
    key = "setroomsize"
    locks = "perm(Builder)"

    def func(self):
        args = self.args.strip().lower().split()
        if not args:
            self.caller.msg("Usage: SETROOMSIZE <size> OR SETROOMSIZE CUSTOM <width> <height>")
            return

        if args[0] == "custom":
            if len(args) != 3:
                self.caller.msg("Usage: SETROOMSIZE CUSTOM <width> <height>")
                return
            try:
                width = int(args[1])
                height = int(args[2])
            except ValueError:
                self.caller.msg("Width and height must be integers.")
                return

            if not (1 <= width <= 25 and 1 <= height <= 25):
                 self.caller.msg("Dimensions must be between 1 and 25.")
                 return

            self.caller.location.db.room_size = {"width": width, "height": height}
            self.caller.msg(f"Room size set to {width}x{height}.")
            return

        size = args[0]
        if size not in ["tiny", "small", "medium", "large", "huge", "massive"]:
            self.caller.msg("Invalid size. Choose: tiny, small, medium, large, huge, massive.")
            return
        self.caller.location.db.room_size = size
        self.caller.msg(f"Room size set to {size}.")
