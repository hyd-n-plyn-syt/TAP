from evennia.commands.default.building import CmdTeleport


class CmdBuilderTeleport(CmdTeleport):
    """
    Teleport to another location.

    Usage:
      teleport <target>
      teleport <target> = <destination>

    Switches:
      quiet - don't echo leave/arrival messages

    Teleport yourself (or, with =, another object) to a target location.
    """
    key = "teleport"
    aliases = ["tp"]
    locks = "cmd:perm(Builder)"
