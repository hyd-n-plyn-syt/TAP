"""
In-game changelog data.

Every major change to the game is recorded here as a numbered entry. The
'changes' command reads from this module: bare 'changes' lists what you
haven't read yet, 'changes all' shows everything, and 'changes <number>'
shows one entry in full.

To add a new change simply append a dict with the next number; the on-login
alert and the live server-start broadcast pick it up automatically. The
builder 'addchange' command appends entries for you (numbering and dating
them) and writes them back to this file.
"""

import ast
import datetime

CHANGES_FILE = __file__

CHANGES = [
    {
        "number": 1,
        "date": "2026-07-29",
        "title": "The 5-D world grid",
        "body": (
            "Rooms were stamped with a two-tier coordinate grid: a planetary tier "
            "(planet_x / y / z) and a local subzone tier (site_x / y / z), keyed by "
            "planetary body and site. Each new room knows exactly where it sits in the "
            "world, which lets look, travel and future (weather, astronomy) features "
            "read positions off a room instead of tracking them by hand."
        ),
    },
    {
        "number": 2,
        "date": "2026-07-29",
        "title": "Exit descriptions & a clockwise direction matrix",
        "body": (
            "Exits now carry descriptions so players and staff know where a passage "
            "leads before stepping through. Room exits render in a strict clockwise "
            "order (n, ne, e, se, s, sw, w, nw, up, down, enter, leave) with multiple "
            "entrances grouped grammatically. The cardinal-direction coordinate "
            "stepping behind 'dig' was fixed so x, y, z map to the grid correctly."
        ),
    },
    {
        "number": 3,
        "date": "2026-07-30",
        "title": "Visarial meta-states, perception & manifestation",
        "body": (
            "Objects and characters gained visarial meta-states so they can exist in "
            "the physical world, the visarial world, or both at once. Characters gained "
            "'perceive' to be aware of the other plane from where they stand, and "
            "'manifest' to step fully across. When you halve similar names in a room, "
            "look now only shows the ones on planes you can actually see. A "
            "long-standing bug that stripped color codes while re-capitalizing room "
            "listings was also fixed."
        ),
    },
    {
        "number": 4,
        "date": "2026-08-01",
        "title": "Attributes, derived pools & the live prompt",
        "body": (
            "Nine sub-attributes (Corpus / Genius / Animus across Power, Speed and "
            "Resist) replaced a single stat line, feeding three main attributes whose "
            "derived pools (Vigor, Vim, Mens) and regen rates are computed on the fly "
            "and tracked per character. A new live prompt shows your pools in numbers, "
            "percentages or graphical bars, colored by how damaged the pools are, and "
            "toggles with 'promptmode'. New 'stats' and builder 'attset' commands were "
            "added for viewing and testing them."
        ),
    },
    {
        "number": 5,
        "date": "2026-08-02",
        "title": "Species, appearance phrases, poses & cosmic time",
        "body": (
            "Nine playable species were added, each with its own visarial nature, a "
            "persistent stat bonus, some permanently locked stat columns and hidden "
            "pools. Characters are now described by a three-word appearance phrase ('A "
            "tall and lean, refracting Visarii standing here.') tunable with setheight "
            "/ setbuild / setadjective / setskin. A whitelisted pose system replaced "
            "the stock pose, and a universal 23-hour day / 28-day month / 13-month year "
            "calendar with 13 ruling signs and 3 orbiting planets brought the 'time' "
            "command alive."
        ),
    },
    {
        "number": 6,
        "date": "2026-08-02",
        "title": "Skills, stat growth & rankings",
        "body": (
            "A full progression layer arrived: thirteen skills spanning categories, "
            "each tied to weighted sub-stats, with 0-1000 values across ten tiers "
            "(Novice to Grandmaster). Skills grow through 'use' with diminishing "
            "returns that reward branching, and the stats they feed also grow, capped "
            "by a 14-rank ladder from 'no rank' up to 'ungodly'. The 'skills' command "
            "shows what you know; builders learn or set skills with 'setskill'."
        ),
    },
    {
        "number": 7,
        "date": "2026-08-02",
        "title": "Trainers, alternate stat mains, colored tiers & a spawning area",
        "body": (
            "Trainer NPCs teach skills via the builder 'settrainer', and players learn "
            "them with 'train' once prerequisites are met. Species that lock out a main "
            "stat pivot that column to an alternate (Visarii corpus→animus, Silex "
            "animus→corpus) so no skill is wasted. Rank and tier names gained per-entry "
            "colors, and new characters now home to the Center of Creation, where a "
            "Keeper offers the fundamentals and sets the advanced skills as goals."
        ),
    },
    {
        "number": 8,
        "date": "2026-08-02",
        "title": "Visarial plane & Vim-connection model",
        "body": (
            "The engine for how things sit in the world was unified under a single "
            "'visarial nature' on every object, controlling both the plane it occupies "
            "and its connection to Vim. Physical nature (Silex, plain stones) is "
            "'absolutely disconnected from Vim'; visarial nature (Visarii) glows with a "
            "magenta Vim aura; dual-natured beings carry both descriptions. Perception "
            "is now per-entity and split between see and touch, so what you can "
            "perceive and what you can reach are independent. Builders can override a "
            "prop's nature with 'setnature'."
        ),
    },
    {
        "number": 9,
        "date": "2026-08-03",
        "title": "Realm-aware speech, unified states & staff tools",
        "body": (
            "Speech now follows the planes: your words only land in the realm you "
            "occupy, and a room's characters only hear you if they can see that realm. "
            "Whispering to a named target still crosses the fold. The internal state "
            "naming was unified so every creature's home realm is represented "
            "consistently, and staff gained a global 'force' that can command anyone on "
            "any plane, in any room, whether or not they can see them."
        ),
    },
    {
        "number": 10,
        "date": "2026-08-03",
        "title": "The 'changes' command",
        "body": (
            "This command was added. 'changes' lists the changes you haven't read yet; "
            "'changes all' shows the full history; 'changes <number>' (or 'changes "
            "latest') reads one entry and marks everything up to it as read. When new "
            "changes land, they announce themselves here and at login so nothing is "
            "missed. This is change #10, the one you are reading now."
        ),
    },
    {
        "number": 11,
        "date": "2026-08-03",
        "title": "Added the 'addchange' command",
        "body": (
            "The 'addchange' command was added. This command adds a new change to the "
            "list, applying time, date, and the newest number on the list before "
            "announcing it to the entire server. This is of course restricted to "
            "builder and above, and meant for significant changes only."
        ),
    },
    {
        "number": 12,
        "date": "2026-08-04",
        "title": "Added a builder setgender command",
        "body": (
            "There's now a setgender command for builders. The choices for now are "
            "male, female, and neuter. The first two are obvious. The third describes "
            "something without gender. Using SETGENDER CHOICE, where choice is one of "
            "the three options will set your gender. SETGENDER CHOICE = NAME, will set "
            "a character's gender."
        ),
    },
    {
        "number": 13,
        "date": "2026-08-04",
        "title": "Added an EMOTE command",
        "body": (
            "There is now a fully functional, fairly robust emote command in place. You "
            "can target others and yourself with @target, speak by utilizing quotation "
            "marks, and even declare possessive nouns for yourself with @my. There are "
            "many more examples, and much more thorough directions in HELP EMOTE."
        ),
    },
    {
        "number": 14,
        "date": "2026-08-04",
        "title": "Expanded character appearance system",
        "body": (
            "Looking at a character now shows a detailed, multi-sentence paragraph "
            "describing their appearance instead of a short phrase. The paragraph is "
            "auto-generated from stored attributes: height, build, species, gender, "
            "adjective, eyes, eye colour, hair, hair colour, and skin tone. Each "
            "attribute contributes a sentence; unset attributes are silently omitted. "
            "Pose determines the opening line (e.g. 'Before you stands...' vs 'Before "
            "you sits...'). Four new builder commands were added: seteyes, seteyecolor, "
            "sethair, and sethaircolor. The manual 'desc' is still appended after the "
            "generated paragraph for extra player-written flair."
        ),
    },
    {
        "number": 15,
        "date": "2026-08-04",
        "title": "Guided character creation system",
        "body": (
            "New characters are now created through a step-by-step menu: choose gender, "
            "species, then each appearance option (height, build, adjective, skin "
            "colour, eyes, eye colour, hair, hair colour). Finally, you order the three "
            "main attributes by priority and distribute bonus points (6/4/2) across "
            "their sub-stats. The 'charcreate' command replaces the stock Evennia flow, "
            "and a new 'mychars' command lists all characters on your account."
        ),
    },
    {
        "number": 16,
        "date": "2026-08-05",
        "title": "Builder teleport & custom messages",
        "body": (
            "The teleport command was lowered to Builder permission. Characters now "
            "have teleport locks that control who can teleport to or from them, "
            "defaulting to Admin and above. A new builder 'teleport' command delivers "
            "custom source, destination, and self messages when moving characters "
            "between rooms."
        ),
    },
    {
        "number": 17,
        "date": "2026-08-05",
        "title": "Doors, locks, hidden exits & the build menu",
        "body": (
            "Exits gained a full door system: open, close, lock, unlock, and an "
            "autoopen toggle. Locked doors require a matching key; each locked door "
            "creates one key shared between its two sides. Hidden exits are invisible "
            "until spotted, gated by the new 'awareness' skill. Doors can be breakable, "
            "gated by the new 'bash' skill. The new 'digm' (digmenu) command launches "
            "an interactive build menu for creating rooms and exits with all these "
            "options step by step."
        ),
    },
    {
        "number": 18,
        "date": "2026-08-05",
        "title": "Direction fallbacks",
        "body": (
            "Typing a cardinal direction where no exit exists now attempts to find and "
            "use an exit in that direction, rather than just saying 'no exit'. Exits "
            "named 'north', 'south', etc. (or their aliases 'n', 's', etc.) are "
            "detected dynamically and offered to the player."
        ),
    },
    {
        "number": 19,
        "date": "2026-08-05",
        "title": "Discord ↔ game OOC integration",
        "body": (
            "The OOC channel is now two-way with Discord. In-game OOC messages appear "
            "in the Discord #OOC channel, and messages sent in Discord appear in-game "
            "with a [Discord] tag. Sender names are coloured by permission level both "
            "ways: orange for developers, dark orange for builders, teal for players. "
            "The OOC command was removed; use 'ooc <message>' or the channel alias "
            "instead."
        ),
    },
    {
        "number": 20,
        "date": "2026-08-05",
        "title": "New skills: lockpick, bash, awareness",
        "body": (
            "Three new skills were added to support the door system. 'lockpick' lets "
            "you try to pick a locked door. 'bash' lets you force a door open by brute "
            "strength. 'awareness' lets you detect hidden exits in a room. All three "
            "gate their respective door interactions."
        ),
    },
    {
        "number": 21,
        "date": "2026-08-05",
        "title": "Appearance-based targeting",
        "body": (
            "Any word from a character's appearance description can now be used to "
            "target them. When multiple characters share the same description, Evennia "
            "shows numbered labels like [virentes-1] and [virentes-2] so you can select "
            "a specific one. The search checks name, aliases, then appearance paragraph "
            "words in order."
        ),
    },
    {
        "number": 22,
        "date": "2026-08-05",
        "title": "Character creation improvements",
        "body": (
            "The chargen menu now shows a welcome screen with 'Press ENTER to "
            "continue...' before starting. Skin, eye, and hair colour options are "
            "displayed in their actual colour so you can see what you're choosing. "
            "Species help entries can be browsed with the '?N' command at any species "
            "prompt, showing a full description, nature, stat bonus, and locked traits."
        ),
    },
    {
        "number": 23,
        "date": "2026-08-05",
        "title": "Account and permission fixes",
        "body": (
            "Character slots were overridden: players get 3, builders and above get 4. "
            "The 'mychars' command was fixed to work with the account system. The "
            "'charcreate' command now defers character creation until the final step. "
            "Permission checks now use lowercase strings and account-level lookups. The "
            "OOC channel name is displayed in white, and sender names are coloured by "
            "permission level in-game."
        ),
    },
    {
        "number": 24,
        "date": "2026-08-06",
        "title": "Added REMOVECHANGE and added to Discord Bot",
        "body": (
            "Successfully added the CHANGES command to the Discord announce bot. They "
            "will now dump into the 'system' channel on the official Discord server. "
            "Also added in a REMOVECHANGES command, and elevated both to admin level "
            "permissions."
        ),
    },
    {
        "number": 25,
        "date": "2026-08-06",
        "title": "SKILLS ALL added to the SKILLS command",
        "body": (
            "The new SKILLS ALL option of the SKILLS command will list all skills that "
            "are coded, or at the very least defined in the game. Not all of them have "
            "function yet, and there are still an absolute ton to come."
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


def _q(text):
    """A double-quoted Python string literal with quotes/backslashes escaped."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _wrap_string(text, width=74):
    """Split a body into lines of roughly 'width' characters on word bounds."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        candidate = f"{cur} {word}".strip()
        if len(candidate) > width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = candidate
    if cur:
        lines.append(cur)
    return lines


def _serialize(entry):
    """Render one entry as Python source in the style of CHANGES."""
    chunks = _wrap_string(entry["body"])
    if len(chunks) == 1:
        body_block = [f'        "body": {_q(chunks[0])},']
    else:
        body_block = ['        "body": (']
        for chunk in chunks[:-1]:
            body_block.append(f"            {_q(chunk + ' ')}")
        body_block.append(f"            {_q(chunks[-1])}")
        body_block.append("        ),")
    block = [
        "    {",
        f'        "number": {entry["number"]},',
        f'        "date": {_q(entry["date"])},',
        f'        "title": {_q(entry["title"])},',
    ] + body_block + ["    },"]
    return "\n".join(block)


def _insert(entry_block, source):
    """Insert a serialized entry before the closing bracket of CHANGES."""
    tree = ast.parse(source)
    end = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CHANGES" for t in node.targets
        ):
            end = node.value.end_lineno
            break
    if end is None:
        raise ValueError("Could not locate the CHANGES list.")
    lines = source.splitlines()
    lines[end - 1:end - 1] = [entry_block]
    return "\n".join(lines) + "\n"


def append_entry(title, body, filepath=None):
    """Append a new, auto-numbered change dated today, persisting it to the
    changelog file and to the in-memory list. Returns the new entry. Pass a
    custom 'filepath' (tests) to avoid touching the real file."""
    title = " ".join(str(title).strip().split())
    body = " ".join(str(body).strip().split())
    if not title:
        raise ValueError("A title is required.")
    if not body:
        raise ValueError("A body is required.")
    entry = {
        "number": latest_number() + 1,
        "date": datetime.date.today().isoformat(),
        "title": title,
        "body": body,
    }
    path = filepath or CHANGES_FILE
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(_insert(_serialize(entry), source))
    CHANGES.append(entry)
    return entry


def remove_entry(number, filepath=None):
    """Remove change #number, renumber remaining entries sequentially from 1,
    and persist changes to the changelog file and in-memory list.
    Returns the removed entry."""
    found = None
    for entry in CHANGES:
        if entry["number"] == number:
            found = entry
            break
    if not found:
        raise ValueError(f"There is no change #{number}.")

    CHANGES.remove(found)
    for i, entry in enumerate(CHANGES, start=1):
        entry["number"] = i

    path = filepath or CHANGES_FILE
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    assign_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CHANGES" for t in node.targets
        ):
            assign_node = node
            break
    if assign_node is None:
        raise ValueError("Could not locate the CHANGES list.")

    entries_code = "\n".join([_serialize(e) for e in CHANGES])
    new_changes_block = f"CHANGES = [\n{entries_code}\n]"

    lines = source.splitlines()
    start_line = assign_node.lineno - 1
    end_line = assign_node.end_lineno
    lines[start_line:end_line] = [new_changes_block]

    new_source = "\n".join(lines) + "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_source)

    return found

