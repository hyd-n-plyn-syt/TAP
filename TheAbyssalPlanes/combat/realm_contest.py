"""Realm-shove contests.

When a creature manifests or withdraws across realms onto a spot already
held by another creature in that realm, both roll an opposed contest (the
realm's stat plus a d10). The loser is shoved off a claimed seat if one is
underfoot, otherwise shoved a random step.

A roll of 1 is a fumble and subtracts 10 from the total; a roll of 10
explodes and rolls again, so a run of 10s keeps climbing while a follow-up
1 claws back past it. Zeroed-stat species stay in the running because the
dice can carry them even when their stat is 0.

Manifesting and withdrawing also announce themselves to observers: the
actor blinks into existence (folding outward from a point) or blinks out of
existence (folding inward before vanishing). When contested, the sighting
instead embeds the shove: both parties' presence snaps into place at the
same spot and the loser is shoved a direction. The roll totals are never
revealed.
"""

import random

from combat.grid import is_valid_coord
from combat.movement import find_nearest_unoccupied_coord, is_grid_occupied
from world.systems.narrative import (
    colored_pronoun,
    colored_poss_self,
    colored_self,
    entity_first_ref,
)

_NEIGHBOR_DIRS = [
    (dx, dy)
    for dx in (-1, 0, 1)
    for dy in (-1, 0, 1)
    if (dx, dy) != (0, 0)
]

_POSE_VERBS = {
    "standing": ("stand", "stands"),
    "sitting": ("sit", "sits"),
    "resting": ("rest", "rests"),
    "laying": ("lie", "lies"),
    "sleeping": ("sleep", "sleeps"),
}


def contest_roll(stat_value):
    """Roll a d10 against *stat_value*. A 1 is a fumble and subtracts 10
    from the total; a 10 explodes, adding 10 and rolling again, so a string
    of 10s keeps climbing (while a follow-up 1 claws back past it)."""
    total = int(stat_value)
    while True:
        roll = random.randint(1, 10)
        if roll == 1:
            total -= 10
        else:
            total += roll
        if roll != 10:
            break
    return total


def _compass_dir(x1, y1, x2, y2):
    """A compass word for the offset (x2-x1, y2-y1), or None if on the same
    spot ('north', 'southeast', etc.)."""
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return None
    ns = "north" if dy > 0 else "south" if dy < 0 else ""
    ew = "east" if dx > 0 else "west" if dx < 0 else ""
    return (ns + ew) or None


def _pose_verbs(actor):
    """(base, third-person) present-tense verbs for the actor's pose."""
    pose = (getattr(actor, "pose", None) or "standing").lower()
    return _POSE_VERBS.get(pose, ("stand", "stands"))


def _furniture_at(room, x, y):
    """Furniture whose footprint covers (x, y), or None."""
    if not room:
        return None
    for obj in room.contents:
        if obj.is_typeclass("typeclasses.furniture.Furniture"):
            if (x, y) in obj.footprint_tiles():
                return obj
    return None


def _shove_spot(loser, x, y, z):
    """A free destination for the loser, chosen at random among the 8
    surrounding valid tiles, falling back to the nearest unoccupied
    coordinate when none are free."""
    room = loser.location
    dirs = list(_NEIGHBOR_DIRS)
    random.shuffle(dirs)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if is_valid_coord(room, nx, ny) and not is_grid_occupied(
            room, nx, ny, z=z, ignore=loser, mover=loser
        ):
            return nx, ny
    return find_nearest_unoccupied_coord(
        room, x, y, z=z, ignore=loser, mover=loser
    )


def _shove_loser(loser, x, y, z):
    """Physically displace the loser. Returns a clause describing the shove:
    'off the seat' when a seat was claimed underfoot, else 'back a step'."""
    room = loser.location
    furn = _furniture_at(room, x, y)
    if furn is not None:
        pose = (getattr(loser, "pose", None) or "standing").lower()
        if furn.allows_pose(pose) and pose != "standing":
            old_loc, old_x, old_y, old_z = (
                loser.location,
                loser.db.pos_x,
                loser.db.pos_y,
                loser.db.pos_z,
            )
            loser.set_pose("standing")
            nx, ny = _shove_spot(loser, x, y, z)
            loser.db.pos_x, loser.db.pos_y = nx, ny
            loser.check_autowhere(old_loc, old_x, old_y, old_z)
            from world.systems.regen import ensure_regen_timer

            ensure_regen_timer(loser)
            return "off the seat"
    nx, ny = _shove_spot(loser, x, y, z)
    loser.db.pos_x, loser.db.pos_y = nx, ny
    loser.check_autowhere(
        loser.location, x, y, getattr(loser.db, "pos_z", z)
    )
    return "back a step"


def resolve_realm_conflict(character):
    """After *character* crosses realms, hold a contest if another creature
    already occupies the character's spot in that realm. The loser is shoved
    off a claimed seat or a random step.

    Returns a dict describing the contest (winner, loser, occupant, plane,
    shove direction, whether a seat was involved) or None when the spot was
    free. Roll totals are never returned - only the winner decides the
    shove."""
    room = character.location
    if not room:
        return None
    x = getattr(character.db, "pos_x", None)
    y = getattr(character.db, "pos_y", None)
    z = getattr(character.db, "pos_z", 1)
    if x is None or y is None:
        return None

    blockers = is_grid_occupied(room, x, y, z=z, ignore=character, mover=character)
    occupant = next(
        (obj for obj in blockers if getattr(obj, "is_creature", False)), None
    )
    if occupant is None:
        return None

    plane = character.current_plane()
    stat_key = "corpus" if plane == "physical" else "animus"
    char_total = contest_roll(getattr(character, stat_key) or 0)
    occ_total = contest_roll(getattr(occupant, stat_key) or 0)

    # A tie favors the one already there: the newcomer fails to hold ground.
    if occ_total < char_total:
        winner, loser = character, occupant
    else:
        winner, loser = occupant, character

    clause = _shove_loser(loser, x, y, z)
    dir_word = _compass_dir(
        x, y, int(loser.db.pos_x or x), int(loser.db.pos_y or y)
    ) or "aside"

    return {
        "winner": winner,
        "loser": loser,
        "occupant": occupant,
        "plane": plane,
        "dir": dir_word,
        "off_seat": clause == "off the seat",
    }


def _echo_uncontested(actor, arrival):
    """The observer sighting for a clean manifest/unmanifest crossing - what
    onlookers in the realm see. Realm is known to them, so never named. The
    actor's name appears once; its pronouns are skin-colored."""
    base_verb, s_verb = _pose_verbs(actor)
    subj = colored_pronoun(actor, "subject")
    poss = colored_pronoun(actor, "possessive")
    name = actor.appearance_name
    if arrival:
        return (
            f"{name} blinks into existence in an instant, seeming to fold "
            f"outward from a singular point in the center of where {subj} now "
            f"{s_verb}."
        )
    return (
        f"{name} blinks out of existence in an instant, seeming to fold "
        f"inward into a single point in the center of {poss} being before "
        f"vanishing entirely."
    )


def announce_crossing(character, arrival, old_observers, result):
    """Send the manifest/unmanifest echoes to the actor and to both realms'
    onlookers, or (when contested) the unified contest message to the actor,
    occupant, and witnesses."""
    new_plane = character.current_plane()
    left = "visarial" if new_plane == "physical" else "physical"
    verb = "start" if arrival else "stop"
    action_realm = new_plane if arrival else left

    departed = _echo_uncontested(character, arrival=False)
    for observer in old_observers:
        observer.msg(departed, from_obj=character)

    new_observers = character._movement_observers()
    if result is None:
        character.msg(
            f"{colored_self(character, True)} {verb} manifesting in the "
            f"{action_realm} realm, seemingly folding into the center of "
            f"{colored_poss_self(character)} being within the {left} realm, and "
            f"folding back out into the {new_plane} realm."
        )
        arrived = _echo_uncontested(character, arrival=True)
        for observer in new_observers:
            observer.msg(arrived, from_obj=character)
        return

    winner, loser = result["winner"], result["loser"]
    occupant = result["occupant"]
    dir_word = result["dir"]
    plane = result["plane"]
    aspect = "body" if plane == "physical" else "spirit"
    clause = "off the seat" if result["off_seat"] else "back a step"

    # 1. Message to character (Actor)
    if character is winner:
        msg_char = (
            f"{colored_self(character, True)} start to fold into the center of "
            f"{colored_poss_self(character)} being within the {left} realm, "
            f"manifesting into the same space as {occupant.appearance_name} in "
            f"the {plane} realm. {colored_poss_self(character, True)} {aspect} "
            f"proves to be stronger, forcing {loser.pronouns['object']} to the "
            f"{dir_word} ({clause})."
        )
    else:
        msg_char = (
            f"{colored_self(character, True)} start to fold into the center of "
            f"{colored_poss_self(character)} being within the {left} realm, "
            f"attempting to manifest into the same space as {winner.appearance_name} "
            f"in the {plane} realm. {winner.appearance_name}'s {aspect} proves "
            f"to be stronger, forcing {colored_self(character)} to the "
            f"{dir_word} ({clause})."
        )
    character.msg(msg_char, from_obj=character)

    # 2. Message to occupant (if occupant is not character)
    if occupant and occupant is not character:
        if occupant is winner:
            msg_occ = (
                f"{entity_first_ref(character, True)} starts to manifest in the "
                f"{plane} realm, appearing in the exact same space as "
                f"{colored_self(occupant)}. {colored_poss_self(occupant, True)} {aspect} "
                f"proves to be stronger, forcing {character.pronouns['object']} "
                f"to the {dir_word} ({clause})."
            )
        else:
            msg_occ = (
                f"{entity_first_ref(character, True)} starts to manifest in the "
                f"{plane} realm, appearing in the exact same space as "
                f"{colored_self(occupant)}. {entity_first_ref(character)}'s {aspect} "
                f"proves to be stronger, forcing {colored_self(occupant)} "
                f"to the {dir_word} ({clause})."
            )
        occupant.msg(msg_occ, from_obj=character)

    # 3. Message to other new_observers (bystanders)
    bystanders = [
        obs for obs in new_observers
        if obs is not character and obs is not occupant
    ]
    if bystanders:
        msg_bystander = (
            f"{entity_first_ref(character, True)} starts to manifest in the "
            f"{plane} realm, appearing in the exact same space as "
            f"{entity_first_ref(occupant)}. {winner.appearance_name}'s {aspect} "
            f"proves to be stronger, forcing {loser.appearance_name} "
            f"to the {dir_word} ({clause})."
        )
        for obs in bystanders:
            obs.msg(msg_bystander, from_obj=character)