"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from commands.building.dig import GridDig
from commands.building.dig_menu import CmdDigMenu
from commands.building.createfurniture import CmdCreateFurniture
from commands.building.createitem import CmdCreateItem
from commands.building.setorigin import CmdSetOrigin
from commands.building.attset import CmdAttSet
from commands.building.setskill import CmdSetSkill
from commands.building.settrainer import CmdSetTrainer
from commands.building.setnature import CmdSetNature
from commands.building.setcanfly import CmdSetCanFly
from commands.building.setgender import CmdSetGender
from commands.building.force import CmdForce
from commands.building.teleport import CmdBuilderTeleport
from commands.admin.addchange import CmdAddChange
from commands.admin.removechange import CmdRemoveChange
from commands.admin.reload import CmdRestart
from commands.player.perceive import CmdPerceive
from commands.player.manifest import CmdManifest
from commands.player.skills import CmdSkills
from commands.player.train import CmdTrain
from commands.player.appearance import (
    CmdSetAdjective,
    CmdSetBuild,
    CmdSetHeight,
    CmdSetSkin,
    CmdSetEyes,
    CmdSetEyeColor,
    CmdSetHair,
    CmdSetHairColor,
)
from commands.player.time import CmdTime
from commands.player.score import CmdScore
from commands.player.changes import CmdChanges
from commands.player.setspecies import CmdSetSpecies
from commands.player.promptmode import CmdPromptMode
from commands.player.poses import CmdRest, CmdSleep, CmdWake, CmdLay, CmdStand, CmdSit, CmdRotate
from commands.player.drop import CmdDrop
from commands.player.emote import CmdEmote
from commands.player.setpose import CmdSetPose
from commands.player.door_commands import CmdOpen, CmdClose, CmdLock, CmdUnlock, CmdAutoOpen
from commands.player.movement import CmdDirectionFallback
from commands.building.setroomsize import CmdSetRoomSize
from commands.player.combat import CmdApproach, CmdMove, CmdShove, CmdAttack
from commands.player.fly import CmdFly, CmdLand
from commands.player.where import CmdWhere, CmdWhereKey, CmdAutoWhere
from commands.player.mapsize import CmdMapSize
from commands.player.grid import CmdHelpGrid
from evennia import CmdSet


class DirectionFallbackCmdSet(CmdSet):
    key = "DirectionFallbackCmdSet"
    priority = 50

    def at_cmdset_creation(self):
        self.add(CmdDirectionFallback)


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        # The default 'pose' only whispered a line to the room and never set
        # a position; replace it with the whitelisted builder 'setpose'.
        self.remove("pose")
        self.add(GridDig)  # This replaces the default engine @dig globally
        self.add(CmdDigMenu)  # Interactive build menu for rooms and exits
        self.add(CmdCreateFurniture)
        self.add(CmdCreateItem)
        self.add(CmdForce)  # Replaces the default 'force' (global, plane-agnostic)
        self.add(CmdBuilderTeleport)  # Lowers default teleport from Admin to Builder
        self.add(CmdSetOrigin)
        self.add(CmdAttSet)
        self.add(CmdSetSkill)
        self.add(CmdSetTrainer)
        self.add(CmdSetNature)
        self.add(CmdSetCanFly)
        self.add(CmdSetGender)
        self.add(CmdFly)
        self.add(CmdLand)
        self.add(CmdWhere)
        self.add(CmdWhereKey)
        self.add(CmdAutoWhere)
        self.add(CmdHelpGrid)
        self.add(CmdAddChange)
        self.add(CmdRemoveChange)
        self.add(CmdRestart)
        self.add(CmdPerceive)
        self.add(CmdManifest)
        self.add(CmdSkills)
        self.add(CmdTrain)
        self.add(CmdSetHeight)
        self.add(CmdSetBuild)
        self.add(CmdSetAdjective)
        self.add(CmdSetSkin)
        self.add(CmdSetEyes)
        self.add(CmdSetEyeColor)
        self.add(CmdSetHair)
        self.add(CmdSetHairColor)
        self.add(CmdSetPose)
        self.add(CmdTime)
        self.add(CmdScore)
        self.add(CmdChanges)
        self.add(CmdSetSpecies)
        self.add(CmdPromptMode)
        self.add(CmdRest)
        self.add(CmdSleep)
        self.add(CmdWake)
        self.add(CmdLay)
        self.add(CmdStand)
        self.add(CmdSit)
        self.add(CmdRotate)
        self.add(CmdDrop)
        self.add(CmdEmote)
        self.add(CmdSetRoomSize)
        self.add(CmdApproach)
        self.add(CmdMove)
        self.add(CmdShove)
        self.add(CmdAttack)
        self.add(CmdOpen)
        self.add(CmdClose)
        self.add(CmdLock)
        self.add(CmdUnlock)
        self.add(CmdAutoOpen)


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        self.remove("ooc")
        from commands.account.chargen import CmdCharCreate
        from commands.account.mychars import CmdMyChars
        self.add(CmdCharCreate)
        self.add(CmdMyChars)
        self.add(CmdMapSize)


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
