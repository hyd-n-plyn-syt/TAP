from evennia import Command

_MAP_SIZES = {"small": 7, "medium": 15, "large": 25}
_SIZE_ORDER = ["small", "medium", "large"]
_SIZE_DISPLAY = {7: "Small", 15: "Medium", 25: "Large"}


class CmdMapSize(Command):
    """
    Set or display the rendered map viewport size.

    Usage:
      mapsize
      mapsize <3-25>

    Displays current size if no argument given, or sets it to the provided integer.
    Sizes must be between 3 and 25.
    Size persists across sessions.
    """
    key = "mapsize"
    aliases = ["mapsize", "ms"]
    help_category = "General"

    def func(self):
        caller = self.caller
        account = caller.account if hasattr(caller, "account") else caller
        
        if not self.args:
            current = account.attributes.get("map_size", default=15)
            caller.msg(f"Current map size is {current}x{current}.")
            return

        try:
            new_size = int(self.args.strip())
        except ValueError:
            caller.msg("Please provide a number between 3 and 25.")
            return

        if not (3 <= new_size <= 25):
            caller.msg("Map size must be between 3 and 25.")
            return

        account.attributes.add("map_size", new_size)
        caller.msg(f"Map size set to {new_size}x{new_size}.")

