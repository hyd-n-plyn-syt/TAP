# BUILDING

Builder commands for The Abyssal Planes. All locked `cmd:perm(Builder)`
unless noted. Registered in `CharacterCmdSet` (`commands/default_cmdsets.py`).

## Room Creation

| Command | Aliases | Description |
|---------|---------|-------------|
| `dig` | — | 5D grid-aware room/exit creation. No exits → standalone origin. `= enter;in` → subzone. `= leave;out` → surface. Direction exits shift grid. |
| `digmenu` | `digm` | Guided room creation EvMenu: name → indoor/outdoor → fly/height → size → direction → return exit → door/lock/hidden/breakable → review → finalize. |
| `@setorigin` | `setorigin` | Stamp current room as a planet's grid origin (0,0,0). |

## Stats & Skills

| Command | Description |
|---------|-------------|
| `attset` | Set base sub-stats (`attset main sub value` or `attset main_sub value`), current pools (`attset <pool> value`), or reset pools (`attset reset`). |
| `setskill` | Learn/set/force/reset skills on a target. Append `force` to bypass prerequisites. |
| `settrainer` | Designate an NPC as a trainer: `settrainer <target> = s1, s2`. `= none` clears. Bare lists taught skills. |

## Species & Nature

| Command | Aliases | Description |
|---------|---------|-------------|
| `setspecies` | — | Set/clear species on a target. Bare lists 9 available. `none` restores defaults. |
| `setnature` | `setplane` | Override visarial nature (`physical`/`visarial`/`dual_natured`). |

## Appearance

| Command | Description |
|---------|-------------|
| `setheight` | Set height category (diminutive/short/middling/tall/towering). |
| `setbuild` | Set build descriptor (validated against current height). |
| `setadjective` | Set species adjective. |
| `setskin` | Set skin tone (shows hex colors). |
| `seteyes` | Set eye shape. |
| `seteyecolor` | Set eye colour (shows hex colors). |
| `sethair` | Set hair style. |
| `sethaircolor` | Set hair colour (shows hex colors). |
| `setgender` | Set gender (male/female/neuter). Used by pronoun system. |

All appearance commands support `= <target>` and `none`/`clear` to reset.
Bare (no value) lists current + valid options for the character.

## Movement & Transport

| Command | Aliases | Description |
|---------|---------|-------------|
| `teleport` | `tp` | Teleport self/target to room/dbref/coordinates. Grid-coord support. |
| `setcanfly` | — | Toggle flight capability on a target (`on`/`off`/bare toggle). |
| `setroomsize` | — | Set tactical grid size (`tiny`/`small`/`medium`/`large`/`huge`/`massive` or `CUSTOM <w> <h>`). |

## Furniture & Items

| Command | Description |
|---------|-------------|
| `createfurniture` | Guided EvMenu to build furniture: name, bed/seating, dimensions, seats, occupies-space, allowed states, color, quality. |
| `createitem` | Guided EvMenu to build items: type, name, materials+colors, adjective, furniture-specific options. |

## Staff

| Command | Aliases | Description |
|---------|---------|-------------|
| `force` | `@force` | Force any object to execute a command. Global search, plane-agnostic. Lock: `perm(spawn) or perm(Builder)`. |
| `addchange` | `addchangelog` | Append a changelog entry: `addchange <title> = <body>`. Announces live. Lock: `perm(Admin)`. |
| `removechange` | `removechangelog`, `delchange` | Remove a changelog entry by number. Renumbering is automatic. Lock: `perm(Admin)`. |
| `@reload` | `@restart` | Custom reload with Discord announcement. Lock: `perm(reload) or perm(Developer)`. |
