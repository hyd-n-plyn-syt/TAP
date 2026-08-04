"""
In-game changelog data.

Every major change to the game is recorded here as a numbered entry. The
'changes' command reads from this module: bare 'changes' lists what you
haven't read yet, 'changes all' shows everything, and 'changes <number>'
shows one entry in full.

To add a new change simply append a dict with the next number; the on-login
alert and the live server-start broadcast pick it up automatically.
"""

CHANGES = [
    {
        "number": 1,
        "date": "2026-07-29",
        "title": "The 5-D world grid",
        "body": (
            "Rooms were stamped with a two-tier coordinate grid: a planetary "
            "tier (planet_x / y / z) and a local subzone tier (site_x / y / z), "
            "keyed by planetary body and site. Each new room knows exactly "
            "where it sits in the world, which lets look, travel and future "
            "(weather, astronomy) features read positions off a room instead "
            "of tracking them by hand."
        ),
    },
    {
        "number": 2,
        "date": "2026-07-29",
        "title": "Exit descriptions & a clockwise direction matrix",
        "body": (
            "Exits now carry descriptions so players and staff know where a "
            "passage leads before stepping through. Room exits render in a "
            "strict clockwise order (n, ne, e, se, s, sw, w, nw, up, down, "
            "enter, leave) with multiple entrances grouped grammatically. The "
            "cardinal-direction coordinate stepping behind 'dig' was fixed so "
            "x, y, z map to the grid correctly."
        ),
    },
    {
        "number": 3,
        "date": "2026-07-30",
        "title": "Visarial meta-states, perception & manifestation",
        "body": (
            "Objects and characters gained visarial meta-states so they can "
            "exist in the physical world, the visarial world, or both at once. "
            "Characters gained 'perceive' to be aware of the other plane from "
            "where they stand, and 'manifest' to step fully across. When you "
            "halve similar names in a room, look now only shows the ones on "
            "planes you can actually see. A long-standing bug that stripped "
            "color codes while re-capitalizing room listings was also fixed."
        ),
    },
    {
        "number": 4,
        "date": "2026-08-01",
        "title": "Attributes, derived pools & the live prompt",
        "body": (
            "Nine sub-attributes (Corpus / Genius / Animus across Power, "
            "Speed and Resist) replaced a single stat line, feeding three "
            "main attributes whose derived pools (Vigor, Vim, Mens) and "
            "regen rates are computed on the fly and tracked per character. "
            "A new live prompt shows your pools in numbers, percentages or "
            "graphical bars, colored by how damaged the pools are, and "
            "toggles with 'promptmode'. New 'stats' and builder 'attset' "
            "commands were added for viewing and testing them."
        ),
    },
    {
        "number": 5,
        "date": "2026-08-02",
        "title": "Species, appearance phrases, poses & cosmic time",
        "body": (
            "Nine playable species were added, each with its own visarial "
            "nature, a persistent stat bonus, some permanently locked stat "
            "columns and hidden pools. Characters are now described by a "
            "three-word appearance phrase ('A tall and lean, refracting "
            "Visarii standing here.') tunable with setheight / setbuild / "
            "setadjective / setskin. A whitelisted pose system replaced the "
            "stock pose, and a universal 23-hour day / 28-day month / "
            "13-month year calendar with 13 ruling signs and 3 orbiting "
            "planets brought the 'time' command alive."
        ),
    },
    {
        "number": 6,
        "date": "2026-08-02",
        "title": "Skills, stat growth & rankings",
        "body": (
            "A full progression layer arrived: thirteen skills spanning "
            "categories, each tied to weighted sub-stats, with 0-1000 values "
            "across ten tiers (Novice to Grandmaster). Skills grow through "
            "'use' with diminishing returns that reward branching, and the "
            "stats they feed also grow, capped by a 14-rank ladder from "
            "'no rank' up to 'ungodly'. The 'skills' command shows what you "
            "know; builders learn or set skills with 'setskill'."
        ),
    },
    {
        "number": 7,
        "date": "2026-08-02",
        "title": "Trainers, alternate stat mains, colored tiers & a spawning area",
        "body": (
            "Trainer NPCs teach skills via the builder 'settrainer', and "
            "players learn them with 'train' once prerequisites are met. "
            "Species that lock out a main stat pivot that column to an "
            "alternate (Visarii corpus→animus, Silex animus→corpus) so no "
            "skill is wasted. Rank and tier names gained per-entry colors, "
            "and new characters now home to the Center of Creation, where a "
            "Keeper offers the fundamentals and sets the advanced skills as "
            "goals."
        ),
    },
    {
        "number": 8,
        "date": "2026-08-02",
        "title": "Visarial plane & Vim-connection model",
        "body": (
            "The engine for how things sit in the world was unified under a "
            "single 'visarial nature' on every object, controlling both the "
            "plane it occupies and its connection to Vim. Physical nature "
            "(Silex, plain stones) is 'absolutely disconnected from Vim'; "
            "visarial nature (Visarii) glows with a magenta Vim aura; "
            "dual-natured beings carry both descriptions. Perception is now "
            "per-entity and split between see and touch, so what you can "
            "perceive and what you can reach are independent. Builders can "
            "override a prop's nature with 'setnature'."
        ),
    },
    {
        "number": 9,
        "date": "2026-08-03",
        "title": "Realm-aware speech, unified states & staff tools",
        "body": (
            "Speech now follows the planes: your words only land in the realm "
            "you occupy, and a room's characters only hear you if they can "
            "see that realm. Whispering to a named target still crosses the "
            "fold. The internal state naming was unified so every creature's "
            "home realm is represented consistently, and staff gained a "
            "global 'force' that can command anyone on any plane, in any "
            "room, whether or not they can see them."
        ),
    },
    {
        "number": 10,
        "date": "2026-08-03",
        "title": "The 'changes' command",
        "body": (
            "This command was added. 'changes' lists the changes you haven't "
            "read yet; 'changes all' shows the full history; 'changes <number>' "
            "(or 'changes latest') reads one entry and marks everything up to "
            "it as read. When new changes land, they announce themselves here "
            "and at login so nothing is missed. This is change #10, the one "
            "you are reading now."
        ),
    },
]


def all_changes():
    """All changelog entries, oldest first."""
    return list(CHANGES)


def latest_number():
    """The highest change number recorded."""
    return CHANGES[-1]["number"] if CHANGES else 0


def get_change(number):
    """Return the entry with this number, or None."""
    for change in CHANGES:
        if change["number"] == number:
            return change
    return None


def unread(last_read):
    """Entries the account has not read yet (number > last_read)."""
    return [c for c in CHANGES if c["number"] > last_read]


def alert_text(last_read):
    """The login/announce alert for an account with 'last_read' changes, or
    None if it is fully caught up."""
    pending = unread(last_read)
    if not pending:
        return None
    newest = pending[-1]
    rest = len(pending) - 1
    count = f" (+{rest} more)" if rest else ""
    return (
        f"|y*** New change: #{newest['number']} |w{newest['title']}|n{count}|n\n"
        f"Type |wchanges|n to read what's new."
    )


_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def _split_date(date_str):
    year, month, day = (int(p) for p in date_str.split("-"))
    return year, month, day


def short_date(date_str):
    """Short form date for list rows, e.g. 'Aug 3'."""
    year, month, day = _split_date(date_str)
    return f"{_MONTHS[month - 1][:3]} {day}"


def full_date(date_str):
    """Long form date for a detail view, e.g. 'August 3, 2026'."""
    year, month, day = _split_date(date_str)
    return f"{_MONTHS[month - 1]} {day}, {year}"