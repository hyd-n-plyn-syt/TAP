"""
Custom Command to initialize a room as a planetary 5D grid origin.
"""
from evennia import Command

class CmdSetOrigin(Command):
    """
    Initializes an unassigned room as a 5D grid origin point.

    Usage:
      @setorigin <planetary_body_name>

    Examples:
      @setorigin earth
      @setorigin mars

    This purges the default 'None' tags on your current location 
    and sets its coordinates to the global 0,0,0 starting position 
    for the specified planet sphere.
    """
    key = "@setorigin"
    aliases = ["setorigin"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        location = caller.location

        if not self.args:
            caller.msg("Usage: @setorigin <planetary_body_name>")
            return

        body_name = self.args.strip().lower()

        # Purge all 8 default initialization tags
        location.tags.clear(category="planetary_body")
        location.tags.clear(category="planetary_site")
        location.tags.clear(category="planet_x")
        location.tags.clear(category="planet_y")
        location.tags.clear(category="planet_z")
        location.tags.clear(category="site_x")
        location.tags.clear(category="site_y")
        location.tags.clear(category="site_z")

        # Stamp the clean base origin parameters
        location.tags.add(body_name, category="planetary_body")
        location.tags.add("None", category="planetary_site")
        location.tags.add("0", category="planet_x")
        location.tags.add("0", category="planet_y")
        location.tags.add("0", category="planet_z")
        location.tags.add("None", category="site_x")
        location.tags.add("None", category="site_y")
        location.tags.add("None", category="site_z")

        caller.msg(
            f"|g[SUCCESS] {location.name} (#{location.id}) initialized as 5D grid origin!\n"
            f"Planetary Body: {body_name}\n"
            f"Global Coordinates: (0, 0, 0)\n"
            f"Local Site Grid:    (None, None, None)|n"
        )