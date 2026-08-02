"""
Builder command to set a character's position (pose).

The position word closes the character's room description ("... Visarii
standing here.") and groups occupants by position in the room listing.
This is a temporary builder tool; positions will later be driven by
actions and combat, which should use Character.set_pose() directly.
"""
from commands.command import Command
from commands.player.appearance import _find_target
from world.data import appearance

POSE_ACTIONS = {
    "standing": "stands up",
    "sitting": "sits down",
    "resting": "settles in to rest",
    "laying": "lies down",
    "sleeping": "falls asleep",
    "kneeling": "kneels down",
    "crouching": "crouches down",
    "leaning": "leans",
    "lounging": "lounges",
    "reclining": "reclines",
    "squatting": "squats down",
    "hiding": "hides",
    "meditating": "meditates",
    "pacing": "paces",
    "observing": "observes",
    "guarding": "stands guard",
    "praying": "prays",
    "dreaming": "drifts into a dream",
}


class CmdSetPose(Command):
    """
    Set a character's position.

    Usage:
      setpose
      setpose <position>
      setpose <position> = <target>

    With no argument, shows the current position and the positions you may
    choose from. The position closes the character's description and groups
    occupants in a room.
    """
    key = "setpose"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        lhs, sep, rhs = self.args.partition("=")
        target = _find_target(caller, rhs.strip() if sep else "")
        if not target:
            caller.msg(f"Could not find '{rhs.strip()}' here.")
            return

        pose = lhs.strip().lower().replace("_", " ")
        if not pose:
            valid = ", ".join(f"|w{p}|n" for p in appearance.POSES)
            caller.msg(
                f"|wCurrent position of {target.name}:|n {target.pose or 'standing'}\n"
                f"|wAvailable positions:|n {valid}"
            )
            return

        if not target.set_pose(pose):
            valid = ", ".join(f"|w{p}|n" for p in appearance.POSES)
            caller.msg(
                f"'{lhs.strip()}' is not a valid position.\n"
                f"|wAvailable positions:|n {valid}"
            )
            return

        if caller.location:
            action = POSE_ACTIONS.get(pose, "takes a new position")
            caller.location.msg_contents(f"|w{target.name}|n {action}.")
        caller.msg(f"|gSet {target.name}'s position to |w'{target.pose}'|n.")
