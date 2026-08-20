# world/

Game logic, data, and support modules for The Abyssal Planes. This is the
heart of the game's systems — everything that isn't a command or typeclass.

## Subdirectories

### `data/`
Pure-data rosters with no Evennia imports (importable from any context):
- `skills.py` — 19 skills in 3 categories (corpus/genius/animus), weighted stats, prerequisites, difficulty→XP table, tier names/colors.
- `species.py` — 9 playable species with visarial nature, stat bonuses, locked columns, zeroed pools.
- `appearance.py` — 1141 lines of appearance data: heights, builds, adjectives, skin tones (49 hex-mapped), eyes, hair, poses (18 whitelisted).
- `calendar.py` — Universal 23-hour/28-day/13-month calendar, 3 orbiting planets, sign-of-month math.
- `rankings.py` — 14-rank stat ladder (none→ungodly) with colors.
- `colors.py` — 47 named colors across 7 material families with Truecolor hexes.
- `items.py` — Item type data (currently furniture only).
- `materials.py` — Material → color cross-references.
- `changes.py` — Self-modifying changelog (44 entries, rewrites itself via AST).

### `systems/`
Logic modules that operate on the data:
- `stats.py` — Stat schema, derived pool formulas (Vigor/Vim/Mens + regen).
- `skills.py` — Skill value/tier math, point costs, taper curves, prerequisites, `use_skill()`, `effective_skill_stats()`.
- `growth.py` — Stat XP accumulation with rising thresholds, locked-column refusal.
- `group.py` — Group invite/join stub (in development).
- `hostility.py` — Hostility check helpers (in development).
- `tactical.py` — Tactical move stubs (ram/restrain/subdue, placeholders).

### `planets/`
Planet-specific zone content (currently empty placeholder, renamed from `zones/`).

### `tests/`
Test suites using Django's test runner:
- `_mock.py` — `MockChar`: lightweight DB-free character facade for SimpleTestCase tests.
- `test_data.py` — Skill catalog, species consistency, rankings, changelog round-trips.
- `test_systems.py` — Growth, skill advancement, effective stats, derived pools, regen.
- `test_combat.py` — Grid helpers, navigation, movement announcements, occupancy.
- `test_calendar.py` — Calendar math, local dates, formatting.
- `test_announce.py` — Movement announcement integration tests.
- `test_smoke.py` — Basic character attribute smoke test.

Run with: `& ..\evenv\Scripts\evennia.exe test --settings settings.py world.tests`

## Top-Level Modules

- `help_entries.py` — 25 file-based help topics (prompt, stats, pools, 9 species, appearance, time, planets, changes).
- `server_hooks.py` — Server start/stop/reload hooks (registered via `AT_SERVER_STARTSTOP_MODULE`).
- `discord_integration.py` — Discord webhook + bot bridge (OOC relay, announcements).
- `prototypes.py` — Stock Evennia (unused).

## Adding New Data

To add a new data roster:
1. Create a new module in `world/data/`.
2. Define your constants and helper functions.
3. Import and use from `world/systems/` or `typeclasses/`.

To add a new system:
1. Create a new module in `world/systems/`.
2. Import data from `world/data/` and operate on typeclass instances.
3. Expose functions that commands can call.
