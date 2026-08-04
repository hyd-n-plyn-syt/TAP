"""
Builder commands to set a character's appearance.
"""
from commands.command import Command
from world.data import appearance


def _find_target(caller, rhs):
    """Resolve a target character by name in the caller's location."""
    if not rhs:
        return caller
    name = rhs.strip().lower()
    loc = caller.location
    if loc is None:
        return None
    for obj in loc.contents:
        if obj.name.lower() == name:
            return obj
    return None
class CmdAppearanceBase(Command):
    """Shared logic for the appearance-setting commands."""

    locks = "cmd:perm(Builder)"
    help_category = "Building"

    attr = None
    options_verb = "value"

    def list_options(self, caller, target) -> str:
        """Return a help line of valid options for this character."""
        return ""

    def func(self):
        caller = self.caller
        lhs, sep, rhs = self.args.partition("=")
        target = _find_target(caller, rhs.strip() if sep else "")

        if not target:
            caller.msg(f"Could not find '{rhs.strip()}' here.")
            return

        if not target.species:
            caller.msg(f"{target.name} has no species set; set one first with 'setspecies'.")
            return

        arg = lhs.strip().lower().replace("_", " ")
        if not arg:
            current = getattr(target, f"appearance_{self.attr}", None)
            lines = [f"|w=== {target.name}'s {self.attr} ===|n"]
            lines.append(f"|wCurrent:|n {current or 'unset'}")
            options = self.list_options(caller, target)
            if options:
                lines.append(options)
            caller.msg("\n".join(lines))
            return

        if arg in ("none", "clear", "unset"):
            setattr(target, f"appearance_{self.attr}", None)
            caller.msg(f"|gCleared {target.name}'s {self.attr}.|n")
            return

        if not target.set_appearance(self.attr, arg):
            options = self.list_options(caller, target)
            msg = f"Invalid {self.attr} '{lhs.strip()}'"
            if options:
                msg += f".\n{options}"
            caller.msg(msg)
            return

        caller.msg(
            f"|gSet {target.name}'s {self.attr} to |w'{getattr(target, f'appearance_{self.attr}')}'|n."
        )


class CmdSetHeight(CmdAppearanceBase):
    """
    Set a character's height category.

    Usage:
      setheight
      setheight <height>
      setheight <height> = <target>
      setheight none

    Valid heights: diminutive, short, middling, tall, towering.
    Height is relative to the character's species, so a "middling" Terran
    differs from a "middling" Volucres. Height is set first; the build is
    validated against it.
    """
    key = "setheight"
    attr = "height"

    def list_options(self, caller, target):
        labels = ", ".join(
            f"|w{h.replace('_', '-')}|n" for h in appearance.HEIGHTS
        )
        return f"|wValid:|n {labels}"


class CmdSetBuild(CmdAppearanceBase):
    """
    Set a character's build.

    Usage:
      setbuild
      setbuild <build>
      setbuild <build> = <target>
      setbuild none

    The build is a single-word descriptor validated against the character's
    height: you cannot be tall and squat, nor short and statuesque. Run
    'setbuild' with no argument to see the options valid for the current
    height.
    """
    key = "setbuild"
    attr = "build"

    def list_options(self, caller, target):
        height = target.appearance_height or appearance.DEFAULT_HEIGHT
        builds = appearance.builds_for_height(height)
        return (
            f"|wValid for height '{height}':|n "
            + ", ".join(f"|w{b}|n" for b in builds)
        )


class CmdSetAdjective(CmdAppearanceBase):
    """
    Set a character's species descriptor.

    Usage:
      setadjective
      setadjective <adjective>
      setadjective <adjective> = <target>
      setadjective none

    The adjective is drawn from the character's species list. Run
    'setadjective' with no argument to see the options for the species.
    """
    key = "setadjective"
    attr = "adjective"

    def list_options(self, caller, target):
        adj = appearance.adjectives_for_species(target.species_key)
        return "|wValid for this species:|n " + ", ".join(f"|w{a}|n" for a in adj)


class CmdSetSkin(CmdAppearanceBase):
    """
    Set a character's skin tone.

    Usage:
      setskin
      setskin <tone>
      setskin <tone> = <target>
      setskin none

    The skin tone is a named color from the character's species palette; it
    colors the species name in the character's description. Run 'setskin'
    with no argument to see the tones available to the species.
    """
    key = "setskin"
    attr = "skin"

    def list_options(self, caller, target):
        skins = appearance.skins_for_species(target.species_key)
        return "|wValid tones:|n " + appearance.color_list_with_hex(skins)


class CmdSetEyes(CmdAppearanceBase):
    """
    Set a character's eye shape.

    Usage:
      seteyes
      seteyes <shape>
      seteyes <shape> = <target>
      seteyes none

    The eye shape is drawn from the character's species list. Run
    'seteyes' with no argument to see the options for the species.
    """
    key = "seteyes"
    attr = "eyes"

    def list_options(self, caller, target):
        opts = appearance.eye_options(target.species_key)
        return "|wValid for this species:|n " + ", ".join(f"|w{o}|n" for o in opts)


class CmdSetEyeColor(CmdAppearanceBase):
    """
    Set a character's eye colour.

    Usage:
      seteyecolor
      seteyecolor <colour>
      seteyecolor <colour> = <target>
      seteyecolor none

    The eye colour is drawn from the character's species list. Run
    'seteyecolor' with no argument to see the options for the species.
    """
    key = "seteyecolor"
    attr = "eye_color"

    def list_options(self, caller, target):
        opts = appearance.eye_color_options(target.species_key)
        return "|wValid for this species:|n " + appearance.color_list_with_hex(opts)


class CmdSetHair(CmdAppearanceBase):
    """
    Set a character's hair style.

    Usage:
      sethair
      sethair <style>
      sethair <style> = <target>
      sethair none

    The hair style is drawn from the character's species list. Run
    'sethair' with no argument to see the options for the species.
    """
    key = "sethair"
    attr = "hair"

    def list_options(self, caller, target):
        opts = appearance.hair_options(target.species_key)
        return "|wValid for this species:|n " + ", ".join(f"|w{o}|n" for o in opts)


class CmdSetHairColor(CmdAppearanceBase):
    """
    Set a character's hair colour.

    Usage:
      sethaircolor
      sethaircolor <colour>
      sethaircolor <colour> = <target>
      sethaircolor none

    The hair colour is drawn from the character's species list. Run
    'sethaircolor' with no argument to see the options for the species.
    """
    key = "sethaircolor"
    attr = "hair_color"

    def list_options(self, caller, target):
        opts = appearance.hair_color_options(target.species_key)
        return "|wValid for this species:|n " + appearance.color_list_with_hex(opts)
