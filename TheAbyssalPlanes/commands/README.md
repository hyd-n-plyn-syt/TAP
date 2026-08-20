# commands/

All custom commands for The Abyssal Planes. Commands are organized by
permission level and purpose.

## Subdirectories

### `account/`
Account-level commands (run from the OOC screen):
- `chargen.py` — `CmdCharCreate`: overrides stock charcreate with EvMenu-based guided creation.
- `chargen_menu.py` — EvMenu nodes for the chargen flow (gender → species → appearance → stats).
- `mychars.py` — `CmdMyChars`: lists all characters on the account.

### `admin/`
Admin-level commands:
- `addchange.py` — `CmdAddChange`: appends a changelog entry and announces live.
- `removechange.py` — `CmdRemoveChange`: removes a changelog entry and renumbers.
- `reload.py` — `CmdRestart`: custom @reload with Discord announcement.

### `building/`
Builder commands (lock `cmd:perm(Builder)`):
- `dig.py` — `GridDig`: 5D grid-aware room/exit creation (replaces stock @dig).
- `dig_menu.py` — `CmdDigMenu`: guided room+door creation EvMenu.
- `setorigin.py` — `CmdSetOrigin`: stamp room as planet grid origin.
- `attset.py` — `CmdAttSet`: set base sub-stats/pools.
- `setskill.py` — `CmdSetSkill`: learn/set/force/reset skills.
- `settrainer.py` — `CmdSetTrainer`: designate NPC trainers.
- `setnature.py` — `CmdSetNature`: override visarial nature.
- `setgender.py` — `CmdSetGender`: set gender for pronoun system.
- `setcanfly.py` — `CmdSetCanFly`: toggle flight capability.
- `setroomsize.py` — `CmdSetRoomSize`: set tactical grid dimensions.
- `setskill.py` — `CmdSetSkill`: manage skills on characters.
- `createfurniture.py` + `createfurniture_menu.py` — guided furniture creation.
- `createitem.py` + `createitem_menu.py` — guided item creation.
- `force.py` — `CmdForce`: global force command (replaces stock).
- `teleport.py` — `CmdBuilderTeleport`: grid-coordinate teleport.

### `player/`
Player commands (lock `cmd:all()`):
- `skills.py` — `CmdSkills`: list learned skills, detail one, or show all.
- `train.py` — `CmdTrain`: list trainers or learn a skill.
- `score.py` — `CmdScore`: character sheet (stats, pools, species).
- `time.py` — `CmdTime`: universal + local cosmic time.
- `promptmode.py` — `CmdPromptMode`: switch prompt display mode.
- `changes.py` — `CmdChanges`: browse the in-game changelog.
- `perceive.py` — `CmdPerceive`: toggle perceiving the other plane.
- `manifest.py` — `CmdManifest`: toggle manifesting in the other plane.
- `appearance.py` — Builder appearance setters (setheight/setbuild/setadjective/setskin/seteyes/seteyecolor/sethair/sethaircolor).
- `setpose.py` — `CmdSetPose`: builder pose setter.
- `setspecies.py` — `CmdSetSpecies`: builder species setter.
- `emote.py` — `CmdEmote`: realm-gated emote engine with @target/pronouns.
- `combat.py` — `CmdAttack`/`CmdApproach`/`CmdMove`/`CmdShove`: combat + grid movement.
- `door_commands.py` — `CmdOpen`/`CmdClose`/`CmdLock`/`CmdUnlock`/`CmdAutoOpen`.
- `poses.py` — `CmdSit`/`CmdRest`/`CmdSleep`/`CmdWake`/`CmdLay`/`CmdStand`/`CmdRotate`: furniture-aware poses.
- `drop.py` — `CmdDrop`: numbered, furniture-aware, plane-aware.
- `get.py` — `CmdGet`: proximity-checked, numbered.
- `fly.py` — `CmdFly`/`CmdLand`: flight commands.
- `where.py` — `CmdWhere`/`CmdWhereKey`/`CmdAutoWhere`: tactical map display.
- `grid.py` — `CmdHelpGrid`: ASCII grid reference chart.
- `mapsize.py` — `CmdMapSize`: set map viewport width (account-level).
- `movement.py` — `CmdDirectionFallback`: dynamic "can't go that way" per room.

### `crafting/`, `skills/`, `vim/`
Empty placeholder packages for future systems.

### `tests/`
Command integration tests using Evennia's `EvenniaCommandTest`.

## Adding a New Command

1. Create a new module in the appropriate subdirectory.
2. Define a class inheriting from `Command` or `GameMuxCommand`.
3. Set `key`, `aliases`, `locks`, and `help_category`.
4. Implement `func()` with your command logic.
5. Register the command in `commands/default_cmdsets.py` by importing it and adding it to the appropriate cmdset class.
