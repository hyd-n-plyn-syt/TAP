# The Abyssal Planes - Development Reference

Internal reference for building, running, and extending the project. This is the
technical counterpart to the public-facing `README.md` (which is an overview of
the systems added on top of Evennia). The living design/build-order document is
`GAMEPLAN.md`.

## Environment

- **Platform:** Windows / PowerShell 7.6.1 (never use bash syntax).
- **Venv:** `D:\TAP\evenv` (always active). Run Evennia commands from `D:\TAP\TheAbyssalPlanes`.
- **Server:** `evennia start|stop|reload|reboot|status|info|--log|istart|makemigrations|shell`.
- **Client (local):** telnet `localhost:4000`, website/webclient `http://localhost`.
- **Public:** MUD via telnet at `theabyssalplane.duckdns.org:4000`; website/webclient at `http://theabyssalplane.duckdns.org` (web served on port 80).
- **Repo:** https://github.com/hyd-n-plyn-syt/TAP (private).
- See `SETUP.md` for full environment bootstrap.

## Modules Utilized

### Evennia modules pulled in beyond the default lineup
- `evennia.contrib.rpg.health_bar.display_meter` — bar-style prompt (`typeclasses/characters.py`).
- `evennia.commands.default.building.CmdDig` — parent of the custom `GridDig` (`commands/building/dig.py`).
- `evennia.commands.default.muxcommand.MuxCommand` — parent of `GameMuxCommand` (`commands/command.py`), set as `COMMAND_DEFAULT_CLASS` so every stock command refreshes the prompt.
- `evennia.utils.gametime` — anchor for the universal cosmic clock (`world/data/calendar.py`).
- `evennia.utils.search.search_tag` / `evennia.utils.search.search_object` — 5D grid neighbor lookup and surface-room punching (`typeclasses/rooms.py`, `commands/building/dig.py`).
- `evennia.utils.utils.iter_to_str` — grammatical list joining in room listings.

### Project modules (custom)
- `commands/command.py` — shared `Command` base + `GameMuxCommand` (both refresh the prompt in `at_post_cmd`).
- `commands/default_cmdsets.py` — wiring for all custom commands (see `Key Files`).
- `commands/building/*` — `dig.py` (GridDig), `setorigin.py`, `attset.py`, `setskill.py`, `settrainer.py`, `setnature.py`, `force.py`.
- `commands/player/*` — `appearance.py` (setheight/setbuild/setadjective/setskin + `_find_target`), `setpose.py`, `setspecies.py`, `perceive.py`, `manifest.py`, `skills.py`, `train.py`, `time.py`, `score.py`, `promptmode.py`.
- `typeclasses/objects.py` — `ObjectParent` mixin (visarial model).
- `typeclasses/rooms.py` — grid-aware rooms.
- `typeclasses/characters.py` — stats, appearance, pose, prompt.
- `world/data/species.py`, `world/data/appearance.py`, `world/data/calendar.py`, `world/data/skills.py`, `world/data/rankings.py` — pure-data rosters.
- `world/systems/stats.py`, `world/systems/skills.py`, `world/systems/growth.py` — stat/growth models.
- `world/help_entries.py` — file-based help (attributes, pools, species, appearance, time, planets, prompt).

## Design Notes & Conventions

- **Style:** PEP 8, standard Python. Follow Evennia built-in patterns (DefaultCharacter, DefaultRoom).
- **Typeclasses:** extend Evennia defaults via the `ObjectParent` mixin pattern.
- **LSP:** `pyrightconfig.json` in the game root points Pyright at `D:\TAP\evenv` for Evennia import resolution (pre-existing LSP "unresolved import" / `db`-attribute warnings are expected noise, not real errors).
- **Skill data & system stores:** character skills/XP live in AttributeProperties (`skills`, `skills_xp`, `stat_xp`), and species-locked columns are enforced by the growth system.

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

## Visarial Plane & Vim-Connection Model (authoritative)

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

## Species & Appearance

- Species (9, in `world/data/species.py`): Terran, Virentes, Sideralis, Batrachi, Tritonii, Volucres, Pterati, Visarii, Silex. Each defines its visarial nature, a +1 stat bonus, optionally locked main-stat columns (+ `locked_alternates`), zeroed pools, and `can_perceive`/`can_manifest` (Silex sets both False).
- Silex skin tones (`SKIN_TONES` in `world/data/appearance.py`): obsidian `#41414a` (darkest — just darker than `|x` = `ANSI_HILITE + ANSI_BLACK` dark grey), flint `#54545f`, basalt `#676772`, slate `#7b7b87`, granite `#9696a1`, ash `#b9b4ac`. `slate` is shared with Pterati.
- Species remap a locked main column to an alternate (Visarii corpus→animus, Silex animus→corpus) so skills tied to the locked column still feed a stat — see `world/systems/skills.py:effective_skill_stats`.
- Birth sign + birth date are rolled at character creation.
- `setnature` (`commands/building/setnature.py`) overrides a prop's nature (or a character's, e.g. for NPCs); `setspecies` applies/clears a species. On characters nature usually comes from their species.

## Stats, Skills & Growth

- Nine sub-stats (`main x sub`: Corpus/Genius/Animus × Potestas/Reflexus/Obsistis) stored as Attributes (category `stat`); main stats = sum of their three sub-stats. Derived pools (Vigor, Vim, Mens) + regen computed on the fly (`world/systems/stats.py`); never stored. Species bonuses are persistent, applied on top of stored base values.
- Skills are 0-1000 across 10 tiers (Novice → Grandmaster). Using a skill awards skill XP and weighted sub-stat XP, with diminishing returns per tier (skill/stat tapers). `Character.use_skill()` shorthand.
- Skill prerequisites gate advanced skills; requirements display as "NN% Tier" (e.g. "0% Adept") via `requirement_str`.
- Commands: `attset` (Builder) sets base sub-stats/pools/resets pools; `score` shows the sheet; `skills` shows learned skills / detail; `setskill` (Builder) learns/sets/forces/resets; `train` lists trainers here or learns a skill; `settrainer` (Builder) designates a trainer NPC's skills.

## Pose System

- Default `pose` command was **replaced** with builder-only `setpose` (`commands/player/setpose.py`), lock `cmd:perm(Builder)`, help_category `Building`.
- `Character.set_pose(pose)` API: normalizes, validates against `POSES` whitelist in `world/data/appearance.py`, stores to `self.pose` (AttributeProperty, default `"standing"`). Combat/actions call this directly.
- `POSES`: standing, sitting, resting, laying, sleeping, kneeling, crouching, leaning, lounging, reclining, squatting, hiding, meditating, pacing, observing, guarding, praying, dreaming.
- Forms: `setpose <position>`, `setpose <position> = <target>`. Emits `${target.name} {action}.` to the room via `POSE_ACTIONS`; bare `setpose` lists current + `POSES`.
- `_find_target` (shared via `commands/player/appearance.py`) is None-location safe.

## Room Listing & Planes

- `Room._grouped_room_contents`: characters + things grouped by plane (`physical`/`visarial`), then by position. Format: `In the (physical), there's a X and a Y standing here. There's also a Z laying here. You see two bronze swords and a stone table.` Builders get `(realname)` per character.
- Things sentence lowercase when first/only sentence in a plane block, capitalized otherwise.
- Visibility is driven by `visible_to` (the `can_*_see`/`can_*_touch` flags); `filter_visible` excludes the looker.
- `return_appearance` passes `characters=...`, `things=""`. Old `get_display_characters`/`get_display_things` removed.
- Auras/disconnected lines are **not** shown in room listings — the planes already separate them; they appear on direct `look` via `get_display_desc` / `return_appearance`.

## Time & Planets

- Universal 23-hour day / 28-day month / 13-month year anchored to the cradle world Auridon; 13 ruling signs; 3 orbiting planets (Cindris, Auridon, Frostfall) with local year lengths set by orbital distance.
- `world/data/calendar.py` provides `cosmic_date`/`local_date`, sign-of-month, and `planet_key_for_location` (explicit `db.planet` or the room's `planetary_body` tag).

## Prompt System

- Prompt refreshed after every command (`at_post_cmd` on the shared base + `GameMuxCommand` as `COMMAND_DEFAULT_CLASS`).
- Modes: `numbers` / `percent` / `bars` (`promptmode` command; `display_meter` for bars).
- Shows pools (omitting zeroed ones) + current visarial state.

## Key Files

- `world/data/species.py` — 9-species roster, stat bonuses, locked stats (+ `locked_alternates`), zeroed pools, natures.
- `world/data/appearance.py` — `HEIGHTS`, `BUILDS`, `SPECIES_ADJECTIVES`, `SKIN_TONES`, `SPECIES_SKIN_TONES`, `POSES`, `valid_pose()`, helper validators.
- `world/data/skills.py` — skill catalog (keys/names/categories/weights/prereqs/difficulty→XP/tier names).
- `world/data/rankings.py` — main-stat rank ladder (none..ungodly).
- `world/data/calendar.py` — universal/local calendar math + `PLANETS`/`PLANET_ORDER` (planet-authoring: add key + orbit_days; bind rooms via `db.planet` or `planetary_body` tag).
- `world/systems/stats.py` — stat schema + derived-pool formulas.
- `world/systems/skills.py` — value/tier math, point costs, taper curves, prereqs, learn/unlearn, `use_skill`, `effective_skill_stats`.
- `world/systems/growth.py` — stat XP accumulation + thresholds, refuses species-locked columns.
- `world/help_entries.py` — file-based help entries (prompt, stats, species, appearance, pose, time, planets).
- `typeclasses/objects.py` — `ObjectParent` mixin: `nature()`/`state()` helpers, `is_creature`, `can_perceive`/`can_manifest`, the see/touch/speak/hear flags, `visible_to`, `current_plane`, `visarial_desc_text`/`format_visarial_desc`, `get_display_desc`, `set_nature`, `get_search_candidates` (plane filtering, with a Builder bypass).
- `typeclasses/rooms.py` — grid identity tags, grid-neighbor `return_appearance`, `get_display_exits` (clockwise + grouped portals), `_grouped_room_contents`, `_things_list`.
- `typeclasses/characters.py` — 9 sub-stats, species/appearance/pose/sign/birth_date AttributeProperties, `skills`/`skills_xp`/`stat_xp`, `set_pose()`, `set_state()`, `at_say()` (realm-aware say), `appearance_bits`/`appearance_phrase`, `set_appearance`, `get_prompt`, `return_appearance`.
- `commands/building/dig.py` — `GridDig` (5D grid mapping).
- `commands/building/setorigin.py` — `@setorigin` (grid origin stamp).
- `commands/building/attset.py` — base sub-stat / pool setter.
- `commands/building/setskill.py`, `settrainer.py`, `setnature.py`, `force.py` — progression / trainer / plane nature / staff force builders.
- `commands/player/setpose.py` — `CmdSetPose` + `POSE_ACTIONS`.
- `commands/player/appearance.py` — `_find_target` + `setheight`/`setbuild`/`setadjective`/`setskin`.
- `commands/player/setspecies.py`, `perceive.py`, `manifest.py`, `skills.py`, `train.py`, `time.py`, `score.py`, `promptmode.py`.
- `commands/default_cmdsets.py` — removes default `pose`, adds `GridDig`, `CmdForce` (replaces default), `CmdSetOrigin`, `CmdAttSet`, `CmdSetSkill`, `CmdSetTrainer`, `CmdSetNature`, and all player commands in `CharacterCmdSet.at_cmdset_creation`.
- `server/conf/settings.py` — `COMMAND_DEFAULT_CLASS = "commands.command.GameMuxCommand"`, `DEFAULT_HOME = "#3"`.
- `server/evennia.db3` — live DB.

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