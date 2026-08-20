# PLAYER

Player commands for The Abyssal Planes. All registered in `CharacterCmdSet`
(`commands/default_cmdsets.py`). Lock: `cmd:all()` unless noted.

## Core

| Command | Aliases | Description |
|---------|---------|-------------|
| `skills` | `skill` | List learned skills (grouped by category), detail one (`skills <skill>`), or show full catalog (`skills all`). |
| `train` | — | List trainers in the room, or learn a skill from one (`train <skill>`). |
| `score` | `stats` | Character sheet: species, sub-stats, derived mains, pools, regen, rank. |
| `time` | `clock`, `date` | Universal cosmic date/clock + local planet date. |
| `promptmode` | `pmode` | Switch prompt display: `numbers`/`percent`/`bars`. Bare cycles. |
| `changes` | `changelog`, `news` | Browse changelog: bare=unread, `all`=full, `<number>`=one entry. |

## Perception & Planes

| Command | Description |
|---------|-------------|
| `perceive` | Toggle perceiving the other plane (yellow). Gated by species. |
| `manifest` | Toggle manifesting in the other plane (cyan). Gated by species. |

## Movement & Grid

| Command | Description |
|---------|-------------|
| `move` | Grid movement: `move <x> <y> [z]`, `move <direction>`, `move up/down` (flight), `move stop`. |
| `approach` | Navigate toward a target's grid position. |
| `shove` | Push a target one tile (handles walls, doors, exit traversal). |
| `fly` | Take off into flight (requires `can_fly`). |
| `land` | Land from flight. |
| `where` | Render the local tactical map. |
| `wherekey` | Print the map legend. |
| `autowhere` | Toggle auto-map display on movement. |
| `grid` | Print a colored ASCII coordinate grid reference. |
| `mapsize` | Set/display map viewport width (account-level). |

## Combat

| Command | Aliases | Description |
|---------|---------|-------------|
| `attack` | `punch`, `kick`, `headbutt`, `knee`, `axehandle`, `haymaker` | Queue a combat attack using the named skill. |

## Poses (Furniture-Aware)

| Command | Aliases | Description |
|---------|---------|-------------|
| `sit` | — | Sit down (optionally `sit <furniture>`). |
| `rest` | — | Settle in to rest. |
| `sleep` | — | Drift off to sleep (bed-type furniture or ground). |
| `wake` | `awaken`, `wakeup` | Wake from sleeping/resting/laying. |
| `lay` | `lie` | Lie down. |
| `stand` | `getup` | Stand up, mentioning the furniture you're rising from (refused while sleeping). |
| `rotate` | — | Rotate adjacent furniture. |

## Doors

| Command | Description |
|---------|-------------|
| `open` | Open a door-exit. |
| `close` | Close a door-exit. |
| `lock` | Lock a door-exit (requires key). |
| `unlock` | Unlock a door-exit (requires key). |
| `autoopen` | Toggle auto-unlock-when-walking into a locked door. |

## Items & Emotes

| Command | Aliases | Description |
|---------|---------|-------------|
| `get` | `grab` | Pick up an object (proximity-checked, numbered). |
| `drop` | — | Drop an object (furniture-aware, plane-aware). |
| `emote` | `:` | Realm-gated emote engine. `@target` resolves by name/species/height/build; `@me`/`@self`/`@my` for pronouns; quoted text is realm-gated speech. |

## Builder (in Player CmdSet)

These are registered in `CharacterCmdSet` but locked `cmd:perm(Builder)`:
- `setpose`, `setspecies`, `setheight`, `setbuild`, `setadjective`, `setskin`,
  `seteyes`, `seteyecolor`, `sethair`, `sethaircolor`

See [BUILDING.md](BUILDING.md) for full details.
