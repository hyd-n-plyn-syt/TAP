# The Abyssal Planes — Development Reference

Internal reference for building, running, and extending the project. This is the
technical counterpart to the public-facing `README.md` (which is an overview of
the systems added on top of Evennia). The living design/build-order document is
`GAMEPLAN.md`.

## Environment

- **Platform:** Windows / PowerShell 7.6.1 (never use bash syntax).
- **Venv:** `D:\TAP\evenv` (always active). Run Evennia commands from `D:\TAP\TheAbyssalPlanes`.
- **Server:** `& ..\evenv\Scripts\evennia.exe start|stop|reload|reboot|status|info|--log|istart|makemigrations|shell`.
- **Client (local):** telnet `localhost:4000`, website/webclient `http://localhost`.
- **Public:** MUD via telnet at `theabyssalplane.duckdns.org:4000`; website/webclient at `http://theabyssalplane.duckdns.org` (web served on port 80).
- **Repo:** https://github.com/hyd-n-plyn-syt/TAP (private).
- See `SETUP.md` for full environment bootstrap.

## Directory Layout

```
D:\TAP\
├── README.md              ← GitHub front page (systems overview)
├── GAMEPLAN.md            ← Living design + build-order doc
├── DEVELOPMENT.md         ← This file (technical reference)
├── SETUP.md               ← Environment bootstrap
├── evenv/                 ← Python 3.14.6 virtualenv
└── TheAbyssalPlanes/      ← Game directory (Evennia)
    ├── combat/            ← Combat engine (loop, accuracy, damage, grid, movement, menus)
    ├── commands/          ← All commands (player/building/account/admin)
    │   ├── account/       ← charcreate, mychars, chargen EvMenu
    │   ├── admin/         ← addchange, removechange, reload
    │   ├── building/      ← dig, digmenu, attset, setskill, settrainer, force, etc.
    │   ├── crafting/      ← (empty placeholder)
    │   ├── player/        ← skills, train, score, movement, combat, poses, doors, etc.
    │   ├── skills/        ← (empty placeholder)
    │   ├── tests/         ← Command integration tests
    │   └── vim/           ← (empty placeholder)
    ├── server/
    │   ├── conf/settings.py  ← Main config (COMMAND_DEFAULT_CLASS, Discord, channels)
    │   └── logs/          ← Server logs (server.log, portal.log)
    ├── typeclasses/       ← Object, Character, Room, Exit, Furniture, Item, Account
    ├── web/               ← Website/webclient overrides (stock Evennia)
    └── world/
        ├── data/          ← Pure-data rosters (skills, species, appearance, calendar, etc.)
        ├── systems/       ← Logic modules (stats, skills, growth, group, hostility, tactical)
        ├── planets/       ← Planet-specific zone content (placeholder)
        ├── tests/         ← Data/systems unit tests + mock
        ├── discord_integration.py  ← Discord ↔ game bridge
        ├── help_entries.py         ← 25 file-based help topics
        ├── server_hooks.py         ← Server start/stop/reload hooks
        └── prototypes.py           ← Stock Evennia (unused)
```

## Modules Utilized

### Evennia modules pulled in beyond the default lineup
- `evennia.contrib.rpg.health_bar.display_meter` — bar-style prompt (`typeclasses/characters.py`).
- `evennia.commands.default.building.CmdDig` — parent of the custom `GridDig` (`commands/building/dig.py`).
- `evennia.commands.default.building.CmdTeleport` — parent of the custom `CmdBuilderTeleport` (`commands/building/teleport.py`).
- `evennia.commands.default.muxcommand.MuxCommand` — parent of `GameMuxCommand` (`commands/command.py`), set as `COMMAND_DEFAULT_CLASS` so every stock command refreshes the prompt.
- `evennia.utils.gametime` — anchor for the universal cosmic clock (`world/data/calendar.py`).
- `evennia.utils.search.search_tag` / `evennia.utils.search.search_object` — 5D grid neighbor lookup and surface-room punching (`typeclasses/rooms.py`, `commands/building/dig.py`).
- `evennia.utils.utils.iter_to_str` — grammatical list joining in room listings.

### Project modules (custom)
- `commands/command.py` — shared `Command` base + `GameMuxCommand` (both refresh the prompt in `at_post_cmd`; `GameMuxCommand` also blocks commands while sleeping).
- `commands/default_cmdsets.py` — wiring for all custom commands (see Key Files).
- `commands/building/*` — `dig.py` (GridDig), `dig_menu.py` (CmdDigMenu), `setorigin.py`, `attset.py`, `setskill.py`, `settrainer.py`, `setnature.py`, `setgender.py`, `setcanfly.py`, `setroomsize.py`, `createfurniture.py`, `createitem.py`, `force.py`, `teleport.py`.
- `commands/player/*` — `appearance.py` (setheight/setbuild/setadjective/setskin/seteyes/seteyecolor/sethair/sethaircolor + `_find_target`), `setpose.py`, `setspecies.py`, `perceive.py`, `manifest.py`, `skills.py`, `train.py`, `time.py`, `score.py`, `promptmode.py`, `changes.py`, `emote.py`, `drop.py`, `get.py`, `grid.py`, `where.py`, `movement.py` (direction fallback), `combat.py` (attack/approach/move/shove), `door_commands.py` (open/close/lock/unlock/autoopen), `fly.py`, `mapsize.py`, `poses.py` (sit/rest/sleep/wake/lay/stand/rotate).
- `commands/account/*` — `chargen.py` (CmdCharCreate override), `chargen_menu.py` (EvMenu nodes), `mychars.py`.
- `commands/admin/*` — `addchange.py`, `removechange.py`, `reload.py` (custom @reload).
- `typeclasses/objects.py` — `ObjectParent` mixin (visarial model, tactical grid, search).
- `typeclasses/rooms.py` — grid-aware rooms with tactical tile grid.
- `typeclasses/characters.py` — stats, appearance, pose, prompt, movement, combat.
- `typeclasses/exits.py` — doors, locks, breakable/hidden exits, sibling sync.
- `typeclasses/furniture.py` — furniture with grid occupancy, facing, dimensions.
- `typeclasses/items.py` — multi-material Truecolor items (extends Furniture).
- `typeclasses/accounts.py` — changelog tracking, Discord relay, permission colors.
- `typeclasses/channels.py` — Discord relay via `at_post_msg`.
- `world/data/species.py`, `world/data/appearance.py`, `world/data/calendar.py`, `world/data/skills.py`, `world/data/rankings.py`, `world/data/colors.py`, `world/data/items.py`, `world/data/materials.py`, `world/data/changes.py` — pure-data rosters.
- `world/systems/stats.py`, `world/systems/skills.py`, `world/systems/growth.py`, `world/systems/group.py`, `world/systems/hostility.py`, `world/systems/tactical.py` — stat/growth/combat models.
- `world/discord_integration.py` — Discord webhook + bot bridge.
- `world/server_hooks.py` — server start/stop/reload hooks (registered via `AT_SERVER_STARTSTOP_MODULE`).
- `world/help_entries.py` — 25 file-based help entries (prompt, stats, pools, species, appearance, time, planets, prompt, changes).

## Design Notes & Conventions

- **Style:** PEP 8, standard Python. Follow Evennia built-in patterns (DefaultCharacter, DefaultRoom).
- **Typeclasses:** extend Evennia defaults via the `ObjectParent` mixin pattern.
- **LSP:** `pyrightconfig.json` in the game root points Pyright at `D:\TAP\evenv` for Evennia import resolution.
- **Skill data & system stores:** character skills/XP live in AttributeProperties (`skills`, `skills_xp`, `stat_xp`), and species-locked columns are enforced by the growth system.
- **No comments in code** unless the task asks for them.

---

## The 5D Room Grid / Coordinate System

Rooms are stored in Django as normal Evennia objects, but each one carries eight
category tags that stamp its place in a two-tier coordinate grid. Digging is
handled by the custom `GridDig` command (replaces stock `dig`), which computes
and stamps coordinates automatically; `@setorigin` initializes a room as a
world's origin.

**Tags on every room (set in `Room.at_object_creation`):**
- `planetary_body` — planet key (e.g. `auridon`).
- `planetary_site` — subzone/site name, or `"None"` on open surface.
- `planet_x`, `planet_y`, `planet_z` — global planetary grid (surface level).
- `site_x`, `site_y`, `site_z` — local subzone grid, `"None"` on the surface.

**How `dig` maps coordinates** (`commands/building/dig.py`):
- *No exits given* — new room becomes an auto standalone grid origin for the planet named after it (0,0,0).
- `= enter;in` — punching **into** a new subzone/city: planet grid is frozen, `site_x/y/z` start at 0,0,0.
- `= leave;out` with a planet key as the room name — punching **out** to the pre-existing surface room at the matching `planetary_body` + `(planet_x, planet_y, planet_z)` (found via `search_tag`).
- Direction exits (`north/south/east/west/ne/nw/se/sw/up/down`) — the active grid steps ±1 (site grid inside a subzone, planet grid on the surface).

**`@setorigin <planet>`** — clears all eight tags on the current room and stamps
it as that planet's global origin: `planetary_body=<planet>`, `planetary_site=None`,
`planet_x/y/z=0`, `site_x/y/z=None`.

**How the grid is used**:
- `Room.return_appearance` scans neighboring rooms by grid math (direction offsets + `search_tag` on `planetary_body`, matching same site or planet grid) and renders `Nearby you can see <room> to the north and <room> to the east here.` in clockwise order, then groups structural portals (`enter`/`leave`).
- `get_display_exits` forces a strict clockwise sort matrix (n → ne → e → se → s → sw → w → nw → up → down → enter → leave) and groups multiple entrances/exits by count.
- `calendar.planet_key_for_location(room)` resolves a planet from `db.planet` (explicit) or the `planetary_body` tag.

---

## Tactical Grid & Movement

Inside each room, characters and objects occupy a tactical tile grid. The grid
is sized by the room's `room_size` attribute.

**Grid sizes** (`combat/grid.py:ROOM_GRID_SIZES`):
- tiny: 2×2, small: 3×3, medium: 5×5 (default), large: 11×11, huge: 25×25, massive: 51×51.

**Coordinate convention:** `+x = east`, `+y = north`, `+z = up`.

**Entities store `pos_x`/`pos_y`/`pos_z`** (set in `ObjectParent.at_object_creation`).
Rooms also store `pos_x`/`pos_y` for the push-back mechanic in `CmdShove`.

**Movement:**
- `CmdMove` (`commands/player/combat.py`): `MOVE <x> <y> [z]`, `MOVE <direction>` (compass, ±1 grid step), `MOVE up/down` (flight only, z-bounds), `MOVE stop`.
- `CmdApproach`: navigates toward a target's grid coords.
- `CmdShove`: pushes a target one tile (handles walls, doors, exit traversal).
- `CmdFly`/`CmdLand`: toggle flight, z-axis movement.

**Navigation system:**
- A `navigation` dict on the character (`dest_x/y/z`, `exit_dbref`, `movement_mode`, `delta_x/y`) drives autonomous step-by-step movement.
- The `CombatLoop` steps navigators one grid per sub-tick (1s), capped at `MAX_GRIDS_PER_ROUND = 6`.
- `nav_queue` holds pending movement legs.
- `at_post_move` on Character re-stamps coordinates from the traversed exit.

**Z-axis:** from `room.db.floor_z` (default 1) to `room.db.max_z` (default grid size). Only flying characters may change z; landing at floor z clears `is_flying`.

**Room features:**
- `room_size` — grid dimensions (string key or `{width, height}` dict).
- `floor_z` / `max_z` — optional builder overrides for vertical bounds.

---

## Visarial Plane & Vim-Connection Model

`visarial_nature` is the single source of truth and controls **both** the plane
an entity occupies and its Vim connection. `visarial_state` is a secondary,
per-creature toggle (`normal` / `perceiving` / `manifested`); the state never
names a plane — `current_plane()` maps it through the nature:

- `normal` — present in the native realm (physical for physical-/dual-natured,
  visarial for visarial-natured).
- `perceiving` — aware of the other realm from home (does not change plane).
- `manifested` — fully present in the opposite realm.

- **`visarial_nature` ∈ `physical` / `visarial` / `dual_natured`:**
  - `physical` (Silex, plain rocks) — IN and OF the physical. Physical desc only,
    never a custom `visarial_desc`; to a perceiver they show a dark-gray line
    *"This entity/object is absolutely disconnected from Vim."* (colored `|x`).
  - `visarial` (Visarii) — IN and OF Vim. Visarial desc only, no physical desc;
    default magenta aura *"This entity/object gives off an aura of Vim."* (`|M`).
  - `dual_natured` (Terran, most species) — IN the physical by default but OF both,
    so they carry **both** a physical and a visarial desc.
- **`is_creature`** — True on Characters (has `species`); False for plain
  objects/exits. Only creatures perceive or manifest.
- **`can_perceive`** / **`can_manifest`** — True for a creature whose species
  sets the matching capability (Silex sets both False). Gate `perceive` /
  `manifest`.
- **Perception / touch / speech / hearing flags** (on every entity,
  `typeclasses/objects.py`):
  - `can_phys_see` / `can_vis_see` — creature vision of each plane, by
    nature+state (you see your occupied plane, or both while `perceiving`).
    Disabled when pose is `"sleeping"`.
  - `can_phys_touch` / `can_vis_touch` — which plane the entity **occupies**
    (`current_plane()`).
  - `can_speak_phys` / `can_speak_vis` — which plane a creature's *voice* lands
    in (== touch; perceiving the other realm never carries your voice there).
  - `can_hear_phys` / `can_hear_vis` — which realm a creature hears (== see).
  - `visible_to(looker)` — shorthand for
    `(self.can_phys_touch and looker.can_phys_see) or (self.can_vis_touch and looker.can_vis_see)`.

| nature      | `visarial_desc` | default line        | color |
|-------------|-----------------|---------------------|-------|
| `physical`  | never           | "absolutely disconnected from Vim." | `|x` dark gray |
| `visarial`  | aura or custom  | "gives off an aura of Vim."         | `|M` magenta  |
| `dual_natured` | aura or custom | "gives off an aura of Vim."         | `|M` magenta  |

Prompt = `[{plane}]` + optional ` {projected_state}` (`perceiving` /
`manifesting`).

**Realm-aware say** — `Character.at_say` (`typeclasses/characters.py`) overrides
Evennia's default so a speaker's words only reach characters in the same room
who can hear the realm the speaker occupies (`can_hear_phys` / `can_hear_vis`);
the speaker still sees a self-echo. Whispering to a named target bypasses realm
gating. Gotcha: passing `msg_location=None` to Evennia's default does **not**
suppress the room broadcast — the default re-assigns it to a truthy fallback —
so the gated path delivers to receivers manually via `receiver.msg(...)`.

**Staff search & force** — `get_search_candidates`
(`typeclasses/objects.py`) filters search candidates by `visible_to` for normal
players, but skips the filter entirely when the searcher has `Builder` or higher
permission, so staff can find anyone regardless of plane. The custom `CmdForce`
(`commands/building/force.py`, replaces the default) searches globally
(`global_search=True`, `use_dbref=True`) so staff can force characters in any
room; it keeps Evennia's `perm(spawn) or perm(Builder)` lock and `edit` access
check on the target.

---

## Species & Appearance

- **9 species** (`world/data/species.py`): Terran, Virentes, Sideralis, Batrachi, Tritonii, Volucres, Pterati, Visarii, Silex. Each defines its visarial nature, a +1 stat bonus, optionally locked main-stat columns (+ `locked_alternates`), zeroed pools, and `can_perceive`/`can_manifest` (Silex sets both False).
- Silex skin tones (`SKIN_TONES` in `world/data/appearance.py`): obsidian `#41414a` (darkest), flint `#54545f`, basalt `#676772`, slate `#7b7b87`, granite `#9696a1`, ash `#b9b4ac`. `slate` is shared with Pterati.
- Species remap a locked main column to an alternate (Visarii corpus→animus, Silex animus→corpus) so skills tied to the locked column still feed a stat — see `world/systems/skills.py:effective_skill_stats`.
- Birth sign + birth date are rolled at character creation.
- `setnature` (`commands/building/setnature.py`) overrides a prop's nature (or a character's, e.g. for NPCs); `setspecies` applies/clears a species. On characters nature usually comes from their species.
- **Appearance data** (`world/data/appearance.py`, 1141 lines): 5 heights, 22 builds (each mapped to valid heights), 15 adjectives per species, 49 skin tones with Truecolor hexes, 6 eye shapes per species, 6 eye colours per species, 5-8 hair styles per species, 6 hair colours per species, 18 whitelisted poses.

---

## Stats, Skills & Growth

- **Nine sub-stats** (`main x sub`: Corpus/Genius/Animus × Potestas/Reflexus/Obsistis) stored as Attributes (category `stat`); main stats = sum of their three sub-stats. Derived pools (Vigor, Vim, Mens) + regen computed on the fly (`world/systems/stats.py`); never stored. Species bonuses are persistent, applied on top of stored base values.
- **Skills are 0-1000 across 10 tiers** (Novice → Grandmaster). Using a skill awards skill XP and weighted sub-stat XP, with diminishing returns per tier (skill/stat tapers). `Character.use_skill()` shorthand.
- **Skill prerequisites** gate advanced skills; requirements display as "NN% Tier" (e.g. "0% Adept") via `requirement_str`.
- **19 skills in 3 categories:**
  - **Corpus (13):** brawling (precursor, no combat), punch, kick, headbutt, knee, axehandle, haymaker (offense tree), melee_evasion, melee_parry, melee_block, melee_feint, melee_counterattack (defense tree), bash (utility).
  - **Genius (4):** meditate, focused_meditation, lockpick, awareness.
  - **Animus (2):** pray, devoted_prayer.
- Prereq chains: headbutt→punch/kick ≥100; knee≥150; axehandle≥200; haymaker≥300; melee_parry/block→melee_evasion≥100; melee_feint≥200; melee_counterattack≥300; focused_meditation→meditate≥400; devoted_prayer→pray≥400.
- **Commands:** `attset` (Builder) sets base sub-stats/pools/resets pools; `score` shows the sheet; `skills` shows learned skills / detail; `setskill` (Builder) learns/sets/forces/resets; `train` lists trainers here or learns a skill; `settrainer` (Builder) designates a trainer NPC's skills.

---

## Combat System

A tick-based combat loop runs inside rooms, sharing the same `CombatLoop`
script with grid movement, rest, and regeneration.

**Timing:**
- `SUB_TICK_RATE = 1` — loop fires every 1 second.
- `GLOBAL_ROUND_DURATION = 6` — a round is 6 sub-ticks = 6 seconds.
- `MAX_GRIDS_PER_ROUND = 6` — movement budget per round.

**Combat flow:**
1. Player types `attack <target>` (or `punch`/`kick`/`haymaker` etc.).
2. `CmdAttack` resolves the skill, locates the target, calls `queue_action`.
3. `ensure_combat_loop(room)` guarantees the room has a running `CombatLoop`.
4. Every second the loop increments its 1–6 round counter (resetting everyone's `movement_used` on tick 1), steps navigators one grid, then calls `resolve_tick` for each char with `combat_target`.
5. `resolve_tick`: pop action → pay `pool_cost` → verify target → range check → accuracy → damage → armor → apply → broadcast.
6. Regen pass every 60th tick (pose × furniture quality multiplier).

**Modules:**
- `combat/loop.py` — `CombatLoop` script (main engine).
- `combat/accuracy.py` — attack/defense roll resolution.
- `combat/damage.py` — base damage calculation, armor subtraction, pool application.
- `combat/actions.py` — action queue (max 3 per character).
- `combat/grid.py` — room grid math (sizes, coords, occupancy, quadrants).
- `combat/movement.py` — navigation system, movement messages, combat loop ensure.
- `combat/map_renderer.py` — ASCII tactical map display.
- `combat/menus.py` — collision EvMenu (placeholder actions).
- `combat/queue_mgmt.py` — manual queue handler (not wired to loop).
- `combat/target.py` — targeting helpers (placeholder).
- `combat/text_engine.py` — combat text compilation (placeholder).

**Accuracy:** attack_roll = skill_value + effective(category, reflexus) × 0.5. defense_roll = best of melee_evasion/parry/block (if learned). hit = attack > defense (strict). Crit when margin ≥ threshold (20 at skill 0 → 5 at skill 1000).

**Damage:** (main_stat + highest_sub) × variation (65–100% at skill 0, 85–120% at 1000) × (1 + precursor_bonus). Armor subtracts from final (0 if crit). Applied to species-routed health bar (Vigor/Vim/Mens via `resolve_pool`).

---

## Doors & Locks

Exits can be doors with the following `db.*` attributes (set in `Exit.at_object_creation`):
- `is_door` (False), `is_open` (False), `is_locked` (False).
- `key_id` (None) — ObjectDB id of the key object; checked in `_has_key(caller)`.
- `lockpick_dc` (0), `is_breakable` (False), `bash_dc` (0).
- `is_hidden` (False), `detect_dc` (0) — hidden exits filtered by `filter_visible` when looker's `skills["awareness"] < detect_dc`.
- `sibling_id` (None) — links paired doors; `is_open` state is synced via `_sync_door`.

**Commands:** `open`/`close`/`lock`/`unlock` (door_commands.py), `autoopen` (toggles auto-unlock-when-walking-into-locked-door if you have the key).

**`digmenu`** builder tool guides door creation interactively (door → locked → lockpick DC → inside key → breakable → hidden → detect DC).

---

## Furniture & Items

**`Furniture`** (`typeclasses/furniture.py`, extends `ObjectParent`):
- AttributeProperties: `quality` (1.0, regen multiplier), `occupies_space` (True), `seats` (1), `dimension` ("1×1"), `allowed_states` (sit/rest/lay/sleep), `color` ("|D"), `facing` ("north"), `extra_coords` ([]).
- Grid-aware: `is_at_coord(x,y)` for occupancy checks; `calculate_footprint()` computes multi-tile offsets.
- `approach_hint()` — returns (hint side, readable states) for blocked-movement messages.
- `rotate()` — cycles facing through cardinals if footprint valid.
- Auto-placement on drop: tries facings in order, places at dropper's coords, auto-sits characters standing on tiles.

**`Item`** (`typeclasses/items.py`, extends `Furniture`):
- AttributeProperties: `item_type` ("furniture"), `base_name` ("item"), `materials` ([]), `item_adjective` (None).
- `get_display_name()` — dynamic multi-material Truecolor description from `colors.py` + `materials.py`.

---

## Discord Integration

`world/discord_integration.py` (221 lines):
- **Webhooks:** `send_to_discord()` (OOC relay), `send_announcement()` (announcements channel), `send_to_mudinfo()` (system messages via MudInfo channel).
- **Bot:** `start_discord_bot()` / `stop_discord_bot()` — background `discord.py` bot listening on the OOC channel, relaying messages in-game with `[Discord]` tag and role-colored names.
- **Config:** `DISCORD_WEBHOOK_URL`, `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID`, `DISCORD_OOC_CHANNEL_ID`, `DISCORD_ALLOWED_ROLE_IDS`, `DISCORD_ROLE_COLORS`, `DISCORD_ROLE_PRIORITY`, `DISCORD_BOT_COLOR`, `DISCORD_ANNOUNCEMENTS_WEBHOOK_URL`.
- **Server hooks** (`world/server_hooks.py`): `at_server_start` starts bot + announces; `at_server_reload_start` stops bot; `at_server_stop` announces + stops bot.

---

## Changelog System

`world/data/changes.py` (781 lines, 44 entries, 2026-07-29 → present):
- Self-modifying: `append_entry()` and `remove_entry()` rewrite the file via AST.
- `CmdChanges` (`commands/player/changes.py`): bare lists unread, `all` shows full, `<number>`/`latest` reads one; marks read via `account.changes_seen`.
- `CmdAddChange` / `CmdRemoveChange` (`commands/admin/`): builder tools that persist to the data file and announce live.
- `world/server_hooks.py` broadcasts newest change on server start/reload.
- Login alert via `account.at_post_login`.

---

## Prompt System

- Prompt refreshed after every command (`at_post_cmd` on the shared base + `GameMuxCommand` as `COMMAND_DEFAULT_CLASS`).
- Modes: `numbers` / `percent` / `bars` (`promptmode` command; `display_meter` for bars).
- Shows pools (omitting zeroed ones) + current visarial state.
- Format: `[{plane}]` + optional ` {projected_state}` + pool display.

---

## Key Files

- `world/data/species.py` — 9-species roster, stat bonuses, locked stats (+ `locked_alternates`), zeroed pools, natures.
- `world/data/appearance.py` — `HEIGHTS`, `BUILDS`, `SPECIES_ADJECTIVES`, `SKIN_TONES`, `SPECIES_SKIN_TONES`, `COLOR_HEXES`, `SPECIES_EYES`, `SPECIES_EYE_COLORS`, `SPECIES_HAIR`, `SPECIES_HAIR_COLORS`, `POSES`, validators.
- `world/data/skills.py` — skill catalog (19 skills, 3 categories, keys/names/categories/weights/prereqs/difficulty→XP/tier names/colors).
- `world/data/rankings.py` — main-stat rank ladder (14 ranks, none..ungodly).
- `world/data/calendar.py` — universal/local calendar math + `PLANETS`/`PLANET_ORDER`.
- `world/data/colors.py` — 47 named colors across 7 material families with Truecolor hexes.
- `world/data/items.py` — item type data (currently furniture only).
- `world/data/materials.py` — material → color cross-references.
- `world/data/changes.py` — self-modifying changelog (44 entries).
- `world/systems/stats.py` — stat schema + derived-pool formulas.
- `world/systems/skills.py` — value/tier math, point costs, taper curves, prereqs, learn/unlearn, `use_skill`, `effective_skill_stats`.
- `world/systems/growth.py` — stat XP accumulation + thresholds, refuses species-locked columns.
- `world/systems/group.py` — group invite/join stub.
- `world/systems/hostility.py` — hostility check helpers.
- `world/systems/tactical.py` — tactical move stubs (ram/restrain/subdue).
- `world/help_entries.py` — 25 file-based help entries (prompt, stats, pools, species, appearance, time, planets, changes).
- `world/discord_integration.py` — Discord webhook + bot bridge.
- `world/server_hooks.py` — server start/stop/reload hooks (`AT_SERVER_STARTSTOP_MODULE`).
- `typeclasses/objects.py` — `ObjectParent` mixin: `nature()`/`state()` helpers, `is_creature`, `can_perceive`/`can_manifest`, the see/touch/speak/hear flags, `visible_to`, `current_plane`, `visarial_desc_text`/`format_visarial_desc`, `get_display_desc`, `set_nature`, `get_search_candidates` (plane filtering, with a Builder bypass).
- `typeclasses/rooms.py` — grid identity tags, grid-neighbor `return_appearance`, `get_display_exits` (clockwise + grouped portals), `_grouped_room_contents`, `_things_list`.
- `typeclasses/characters.py` — 9 sub-stats, species/appearance/pose/sign/birth_date AttributeProperties, `skills`/`skills_xp`/`stat_xp`, `set_pose()`, `set_state()`, `at_say()` (realm-aware say), `appearance_bits`/`appearance_phrase`, `set_appearance`, `get_prompt`, `return_appearance`.
- `typeclasses/exits.py` — door/lock/breakable/hidden attrs, `open_door`/`close_door`/`lock_door`/`unlock_door`, sibling sync, `at_traverse` (grid-aware), `filter_visible` (hidden exits).
- `typeclasses/furniture.py` — `Furniture` with grid occupancy, facing, dimensions, `approach_hint`, `rotate`, `calculate_footprint`.
- `typeclasses/items.py` — `Item` extending Furniture with multi-material Truecolor descriptions.
- `typeclasses/accounts.py` — `changes_seen`, Discord relay, permission colors.
- `typeclasses/channels.py` — Discord relay via `at_post_msg`.
- `combat/loop.py` — `CombatLoop` script (main engine).
- `combat/accuracy.py` — attack/defense roll resolution.
- `combat/damage.py` — base damage calculation, armor, pool application.
- `combat/actions.py` — action queue (max 3).
- `combat/grid.py` — room grid math, sizes, occupancy, quadrants.
- `combat/movement.py` — navigation system, movement messages, combat loop ensure.
- `combat/map_renderer.py` — ASCII tactical map display.
- `commands/building/dig.py` — `GridDig` (5D grid mapping).
- `commands/building/dig_menu.py` — `CmdDigMenu` (guided room+door creation).
- `commands/building/setorigin.py` — `@setorigin` (grid origin stamp).
- `commands/building/attset.py` — base sub-stat / pool setter.
- `commands/building/setskill.py`, `settrainer.py`, `setnature.py`, `force.py`, `setgender.py`, `setcanfly.py`, `setroomsize.py`, `teleport.py` — progression / trainer / plane nature / staff force / appearance / movement builders.
- `commands/building/createfurniture.py` + `createfurniture_menu.py` — guided furniture creation.
- `commands/building/createitem.py` + `createitem_menu.py` — guided item creation.
- `commands/player/setpose.py` — `CmdSetPose` + `POSE_ACTIONS`.
- `commands/player/appearance.py` — `_find_target` + `setheight`/`setbuild`/`setadjective`/`setskin`/`seteyes`/`seteyecolor`/`sethair`/`sethaircolor`.
- `commands/player/poses.py` — `CmdSit`/`CmdRest`/`CmdSleep`/`CmdWake`/`CmdLay`/`CmdStand`/`CmdRotate` (furniture-aware).
- `commands/player/combat.py` — `CmdAttack`/`CmdApproach`/`CmdMove`/`CmdShove`.
- `commands/player/door_commands.py` — `CmdOpen`/`CmdClose`/`CmdLock`/`CmdUnlock`/`CmdAutoOpen`.
- `commands/player/drop.py` — `CmdDrop` (numbered, furniture-aware, plane-aware).
- `commands/player/get.py` — `CmdGet` (proximity-checked, numbered).
- `commands/player/emote.py` — `CmdEmote` (realm-gated, `@target`/pronoun engine).
- `commands/player/fly.py` — `CmdFly`/`CmdLand`.
- `commands/player/where.py` — `CmdWhere`/`CmdWhereKey`/`CmdAutoWhere`.
- `commands/player/movement.py` — `CmdDirectionFallback` (dynamic per-room).
- `commands/player/setspecies.py`, `perceive.py`, `manifest.py`, `skills.py`, `train.py`, `time.py`, `score.py`, `promptmode.py`, `changes.py`, `grid.py`, `mapsize.py`.
- `commands/account/chargen.py` + `chargen_menu.py` — EvMenu-based character creation.
- `commands/account/mychars.py` — list all characters on account.
- `commands/admin/addchange.py`, `removechange.py`, `reload.py`.
- `commands/default_cmdsets.py` — removes default `pose` + `ooc`, adds all custom commands.
- `server/conf/settings.py` — `COMMAND_DEFAULT_CLASS`, `DEFAULT_HOME`, `AT_SERVER_STARTSTOP_MODULE`, Discord config, channels.

---

## Attribute & Tag Reference (Master Linking Table)

### Character Attributes

| Key | Category | Default | Purpose |
|-----|----------|---------|---------|
| `corpus_potestas` | stat | 1 | Sub-stat |
| `corpus_reflexus` | stat | 1 | Sub-stat |
| `corpus_obsistis` | stat | 1 | Sub-stat |
| `genius_potestas` | stat | 1 | Sub-stat |
| `genius_reflexus` | stat | 1 | Sub-stat |
| `genius_obsistis` | stat | 1 | Sub-stat |
| `animus_potestas` | stat | 1 | Sub-stat |
| `animus_reflexus` | stat | 1 | Sub-stat |
| `animus_obsistis` | stat | 1 | Sub-stat |
| `vigor_current` | — | (computed) | Current Vigor pool |
| `vim_current` | — | (computed) | Current Vim pool |
| `mens_current` | — | (computed) | Current Mens pool |
| `skills` | growth | {} | Learned skill → value |
| `skills_xp` | growth | {} | Skill → XP toward next point |
| `stat_xp` | growth | {} | Sub-stat → XP toward next raise |
| `species_key` | — | None | Species identifier |
| `sign` | — | None | Birth sign (rolled at creation) |
| `birth_date` | — | None | Birth date string |
| `pose` | — | "standing" | Current position word |
| `gender` | — | "neuter" | Gender (male/female/neuter) |
| `promptmode` | — | "numbers" | Prompt display mode |
| `appearance_height` | — | None | Height category |
| `appearance_build` | — | None | Build descriptor |
| `appearance_adjective` | — | None | Species adjective |
| `appearance_skin` | — | None | Skin tone name |
| `appearance_eyes` | — | None | Eye shape |
| `appearance_eye_color` | — | None | Eye colour |
| `appearance_hair` | — | None | Hair style |
| `appearance_hair_color` | — | None | Hair colour |
| `trained_skills` | — | [] | Skills this NPC teaches |
| `combat_target` | — | None | Current combat target object |
| `friendly_target` | — | None | Current friendly target |
| `action_queue` | — | [] | Queued combat actions |
| `manual_queue` | — | [] | Priority input queue |
| `preferred_moves` | — | [] | Fallback actions (placeholder) |
| `navigation` | — | None | Navigation dict (dest_x/y/z, exit_dbref, mode) |
| `nav_queue` | — | [] | Pending navigation legs |
| `movement_used` | — | 0 | Grids moved this round |
| `is_flying` | — | False | Currently airborne |
| `can_fly` | — | False | Can use fly command |
| `is_autowhere` | — | False | Auto-render map on move |
| `is_hostile` | — | False | Explicit hostility flag |
| `occupies_space` | — | True | Blocks grid movement |
| `worn` | — | [] | Equipped items (Phase 4) |
| `pos_x` | — | 0 | Tactical grid X |
| `pos_y` | — | 0 | Tactical grid Y |
| `pos_z` | — | 1 | Tactical grid Z |
| `room_id` | — | self.dbref | Current room dbref |
| `site_id` | — | "default" | Current site identifier |
| `planet_id` | — | "auridon" | Current planet identifier |
| `group` | — | None | Group reference |
| `group_invite` | — | None | Pending group invite |
| `autoassist` | — | False | Auto-assist toggle |
| `map_size` | — | 15 | Map viewport width (account) |
| `changes_seen` | — | 0 | Changelog read pointer (account) |

### Room Tags (categories)

| Category | Value | Purpose |
|----------|-------|---------|
| `planetary_body` | planet key | Which planet this room belongs to |
| `planetary_site` | site name or "None" | Subzone/city name |
| `planet_x` | string int | Global planetary X |
| `planet_y` | string int | Global planetary Y |
| `planitz` | string int | Global planetary Z |
| `site_x` | string int or "None" | Local subzone X |
| `site_y` | string int or "None" | Local subzone Y |
| `site_z` | string int or "None" | Local subzone Z |

### Room Attributes

| Key | Default | Purpose |
|-----|---------|---------|
| `room_size` | "medium" | Grid dimensions (tiny/small/medium/large/huge/massive or dict) |
| `floor_z` | 1 | Lowest traversable Z |
| `max_z` | (grid size) | Highest traversable Z |

### Exit Attributes (doors)

| Key | Default | Purpose |
|-----|---------|---------|
| `is_door` | False | Is this a door? |
| `is_open` | False | Currently open |
| `is_locked` | False | Currently locked |
| `key_id` | None | ObjectDB id of the key object |
| `lockpick_dc` | 0 | Difficulty to lockpick |
| `is_breakable` | False | Can be bashed open |
| `bash_dc` | 0 | Difficulty to bash |
| `is_hidden` | False | Hidden from look |
| `detect_dc` | 0 | Awareness skill needed to detect |
| `sibling_id` | None | Paired door on the other side |

### Furniture/Item Attributes

| Key | Default | Purpose |
|-----|---------|---------|
| `quality` | 1.0 | Regen multiplier |
| `occupies_space` | True | Blocks grid movement |
| `seats` | 1 | Number of seats |
| `dimension` | "1×1" | Grid footprint (1×1, 1×2, 2×2) |
| `allowed_states` | [sit/rest/lay/sleep] | Permitted poses |
| `color` | "|D" | Display color |
| `facing` | "north" | Orientation |
| `extra_coords` | [] | Multi-tile offsets (computed) |
| `item_type` | "furniture" | Item category |
| `base_name` | "item" | Base name |
| `materials` | [] | Material/color pairs |
| `item_adjective` | None | Modifier adjective |

---

## Test Data (Limbo, room #2)

- #1 Ohm (Visarii, normal — home is the visarial realm; may be `loc=None` when moved around via telnet).
- #46 SpecTest2 (Silex, looming), #47 SpecTest3 (Terran, standing), #58 Atum (Visarii, normal), #59 VisTest (Visarii, normal), #60 DualTest1 (Terran, standing). Visarii default state is `normal` (visarial realm); they occupy the physical only while `manifested`.
- Always re-check locations/states before shell tests.

## Evennia Gotchas (learned)

- `DefaultObject.objects` filters by typeclass and returns 0 rows. Use `from evennia.objects.objects import ObjectDB; ObjectDB.objects.all()`.
- `obj.cmdset.all()` returns the list of CMDSET objects (whose `.commands` hold command instances), NOT a flat command list. Use `{c.key for cset in obj.cmdset.all() for c in cset.commands}`.
- `CmdSetHandler.get()` takes 1 positional arg in this Evennia version.
- Evennia `appearance_template`/`return_appearance` live in `D:\TAP\evenv\Lib\site-packages\evennia\objects\objects.py` (template ~line 407, `return_appearance` ~line 1878).
- `|x` = `ANSI_HILITE + ANSI_BLACK` (bright-black / dark grey) — the "physical" coloration reference; `|M` is magenta (the "visarial" coloration).
- Shell-test pattern: write script to `C:\Users\erikl\AppData\Local\Temp\opencode\*.py`, run `Get-Content <file> -Raw | & ..\evenv\Scripts\evennia.exe shell`. Do NOT pipe multi-line here-strings (indentation/whitespace choke the console).
- `DEFAULT_HOME` must be a dbref (e.g. `"#3"`), NOT a name. Evennia's `clear_contents()` calls `int(settings.DEFAULT_HOME.lstrip("#"))` on every object delete.
- `evennia shell` mangles multi-statement pasted input. Drive it with a script file.
