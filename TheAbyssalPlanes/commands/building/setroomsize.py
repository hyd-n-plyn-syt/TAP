from evennia import Command

class CmdSetRoomSize(Command):
    """
    Set the size of the current room for grid combat.
    Usage:
        SETROOMSIZE <size>
    """
    key = "setroomsize"
    locks = "perm(Builder)"

    def func(self):
        size = self.args.strip().lower()
        if size not in ["tiny", "small", "medium", "large", "huge", "massive"]:
            self.caller.msg("Invalid size. Choose: tiny, small, medium, large, huge, massive.")
            return
        self.caller.location.db.room_size = size
        self.caller.msg(f"Room size set to {size}.")
