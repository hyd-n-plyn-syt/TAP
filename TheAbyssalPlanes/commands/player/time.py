"""
Player command to view the cosmic and local time.
"""
from commands.command import Command
from world.data import calendar


class CmdTime(Command):
    """
    View the current time.

    Usage:
      time

    Shows the universal cosmic date and clock, the sign ruling the current
    month, and (if on a mapped planet) the local date and clock for the
    world you stand on. Planetary bodies orbit Sol at different distances,
    so a local year is longer or shorter than the universal year.
    """
    key = "time"
    aliases = ["clock", "date"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller

        seconds = calendar.universal_seconds()
        cosmic = calendar.cosmic_date(seconds)
        sign = calendar.sign_of_month(cosmic["month"])

        lines = [f"|w=== The Cosmic Clock ===|n"]
        lines.append(f"|wUniversal:|n {calendar.format_date(cosmic)}")
        lines.append(f"|wSign:|n {sign}")

        location = caller.location
        planet_key = calendar.planet_key_for_location(location)
        planet = calendar.get_planet(planet_key)

        if location:
            local = calendar.local_date(planet_key, seconds)
            lines.append("")
            lines.append(f"|w=== On {planet['name']} ===|n")
            lines.append(f"|wLocal:|n {calendar.format_date(local)}")
            lines.append(f"|wNotes:|n {planet['description']}")

        caller.msg("\n".join(lines))
