"""
Cosmic calendar and planetary time system for The Abyssal Planes.

Pure data + math module. The universal cosmic clock is derived from
Evennia's gametime, anchored to the goldilocks world at the center of
the system. It runs on a 23-hour day, 28-day month, 13-month year.

Planetary bodies orbit Sol at different distances, so their local
years are shorter (inner worlds) or longer (outer worlds) than the
universal year. The goldilocks world's year matches the universal
calendar exactly.
"""

# --- Universal cosmic calendar ---
# A universal day is 23 hours. A universal month is 28 days.
# A universal year is 13 months (364 days). One sign per month.
HOURS_PER_DAY = 23
DAYS_PER_MONTH = 28
MONTHS_PER_YEAR = 13
SECONDS_PER_DAY = HOURS_PER_DAY * 3600
SECONDS_PER_YEAR = SECONDS_PER_DAY * DAYS_PER_MONTH * MONTHS_PER_YEAR

# Year number given to the founding of the universal calendar.
CALENDAR_START_YEAR = 10000

MONTHS = (
    "Kindre", "Veldis", "Orde", "Solune", "Myr", "Haelt", "Riven",
    "Kas", "Dorrin", "Vesper", "Thalam", "Aurune", "Varn",
)

SIGNS = (
    "The Warden", "The Lantern", "The Harrow", "The Loom", "The Veil",
    "The Hearth", "The Thorn", "The Quill", "The Anvil", "The Tide",
    "The Crown", "The Ember", "The Shroud",
)

# --- Planetary bodies ---
# Each planet's local year length (in universal days) is set by its
# orbital distance from Sol: nearer worlds orbit faster (shorter years),
# distant worlds orbit slower (longer years). The goldilocks world in the
# middle matches the universal year exactly.
PLANETS = {
    "cindris": {
        "name": "Cindris",
        "description": "a scorched inner world",
        "orbit_days": 182,
        "placeholder": True,
    },
    "auridon": {
        "name": "Auridon",
        "description": "the cradle world at the heart of the system",
        "orbit_days": 364,
        "placeholder": True,
    },
    "frostfall": {
        "name": "Frostfall",
        "description": "a frozen world on the far edge of Sol's light",
        "orbit_days": 728,
        "placeholder": True,
    },
}

# Planet keys in order of orbital distance from Sol (inner to outer).
PLANET_ORDER = ("cindris", "auridon", "frostfall")

DEFAULT_PLANET = "auridon"


def universal_seconds():
    """Current universal time as a float number of cosmic seconds."""
    from evennia.utils import gametime

    return gametime.gametime(absolute=True)


def cosmic_date(seconds=None):
    """
    Break a universal timestamp into (year, month, day, hour, minute,
    second) on the universal calendar, anchored to the goldilocks world.

    Args:
        seconds (float, optional): Universal time. Defaults to now.

    Returns:
        dict: Keys 'year', 'month', 'day', 'hour', 'minute', 'second'.
    """
    if seconds is None:
        seconds = universal_seconds()

    total_seconds = max(0, int(seconds))
    year = CALENDAR_START_YEAR + total_seconds // SECONDS_PER_YEAR
    rem = total_seconds % SECONDS_PER_YEAR
    month = rem // (SECONDS_PER_DAY * DAYS_PER_MONTH)
    rem %= SECONDS_PER_DAY * DAYS_PER_MONTH
    day = rem // SECONDS_PER_DAY
    rem %= SECONDS_PER_DAY
    hour = rem // 3600
    rem %= 3600
    minute = rem // 60
    second = rem % 60

    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
    }


def local_date(planet_key, seconds=None):
    """
    Break a universal timestamp into a local date for a given planet.

    Local years are sized by the planet's orbital distance from Sol.
    Months are still 28 universal days, so a world with a 182-day year
    has a shorter local year than the universal one, and so on.

    Args:
        planet_key (str): Key into PLANETS.
        seconds (float, optional): Universal time. Defaults to now.

    Returns:
        dict: Keys 'year', 'month', 'day', 'hour', 'minute', 'second'.
    """
    planet = get_planet(planet_key)
    if seconds is None:
        seconds = universal_seconds()

    total_seconds = max(0, int(seconds))
    orbit_days = planet["orbit_days"]

    days_into_epoch = total_seconds // SECONDS_PER_DAY
    hour = (total_seconds % SECONDS_PER_DAY) // 3600
    minute = (total_seconds % 3600) // 60
    second = total_seconds % 60

    year = CALENDAR_START_YEAR + days_into_epoch // orbit_days
    day_of_year = days_into_epoch % orbit_days
    month = min(MONTHS_PER_YEAR - 1, day_of_year // DAYS_PER_MONTH)
    day = day_of_year % DAYS_PER_MONTH

    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
        "second": second,
    }


def format_clock(hour, minute, second=0):
    """Format universal-clock time (23-hour day)."""
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def format_date(date_dict, show_clock=True):
    """
    Format a date dict as a display string.

    Example: "the 3rd Day of Orde, in the Year 10058"
    """
    ordinal = ordinal_suffix(date_dict["day"] + 1)
    month_name = MONTHS[date_dict["month"]]
    out = f"the {date_dict['day'] + 1}{ordinal} Day of {month_name}, in the Year {date_dict['year']}"
    if show_clock:
        out += f" ({format_clock(date_dict['hour'], date_dict['minute'], date_dict['second'])})"
    return out


def ordinal_suffix(n):
    """Return the ordinal suffix for a number (1st, 2nd, 3rd, ...)."""
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def sign_of_month(month_index):
    """Return the sign name for a month index (0-based)."""
    return SIGNS[month_index % MONTHS_PER_YEAR]


def sign_of_date(seconds=None):
    """Return the sign ruling the month of a given universal time."""
    return sign_of_month(cosmic_date(seconds)["month"])


def get_planet(planet_key):
    """Return a planet dict, defaulting to the goldilocks world."""
    return PLANETS.get(planet_key, PLANETS[DEFAULT_PLANET])


def planet_key_for_location(location):
    """
    Resolve which planet a room is on.

    Priority:
      1. An explicit `db.planet` set on the room (builders).
      2. The `planetary_body` grid tag matching a known planet key.
      3. Defaults to the goldilocks world.

    Args:
        location (Room): The room to look up.

    Returns:
        str: A key into PLANETS.
    """
    if location:
        if getattr(location, "db", None) and location.db.planet:
            key = str(location.db.planet).strip().lower().replace(" ", "_")
            if key in PLANETS:
                return key
        body = location.tags.get(category="planetary_body", return_list=True)
        for tag in body:
            key = str(tag).strip().lower().replace(" ", "_")
            if key in PLANETS:
                return key
    return DEFAULT_PLANET
