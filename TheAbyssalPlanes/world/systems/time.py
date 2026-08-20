"""
Universal-time round primitives.

The universal clock (Evennia's gametime, via
``world.data.calendar.universal_seconds``) advances one cosmic second per
real second and is the single master heartbeat for the entire game.
Individual systems (combat, movement, regen) do NOT run their own clocks.
Instead each one records an *anchor* universal second and derives its own
rounds by diffing against the live clock — every system clones its own
timer from the same source, so all of them agree on when a round starts,
what round it is, and what second it currently is.

Combat and movement share a 6-second round; regen uses a separate
60-second regen round so combat can never interfere with it.
"""

from world.data.calendar import universal_seconds

COMBAT_ROUND_SECONDS = 6
REGEN_ROUND_SECONDS = 60

MAX_GRIDS_PER_ROUND = COMBAT_ROUND_SECONDS


def now():
    """Current universal time in cosmic seconds."""
    return universal_seconds()


def round_number(seconds=None):
    """The serial number of the current 6-second combat round."""
    if seconds is None:
        seconds = now()
    return int(seconds) // COMBAT_ROUND_SECONDS


def seconds_into_round(seconds=None):
    """How far into the current round we are (0 through 5)."""
    if seconds is None:
        seconds = now()
    return int(seconds) % COMBAT_ROUND_SECONDS


def round_start(seconds=None):
    """Universal second at which the current round began."""
    if seconds is None:
        seconds = now()
    return int(seconds) - (int(seconds) % COMBAT_ROUND_SECONDS)


def next_round_start(seconds=None):
    """Universal second at which the next round begins."""
    return round_start(seconds) + COMBAT_ROUND_SECONDS


def rounds_elapsed(anchor, seconds=None):
    """Number of full 6-second rounds that have passed since *anchor*."""
    if seconds is None:
        seconds = now()
    return max(
        0,
        int(seconds) // COMBAT_ROUND_SECONDS - int(anchor) // COMBAT_ROUND_SECONDS,
    )


def regen_rounds_elapsed(anchor, seconds=None):
    """Number of full 60-second regen rounds that have passed since *anchor*."""
    if seconds is None:
        seconds = now()
    return max(
        0,
        int(seconds) // REGEN_ROUND_SECONDS - int(anchor) // REGEN_ROUND_SECONDS,
    )