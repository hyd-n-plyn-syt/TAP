# TESTS

Test suites for The Abyssal Planes. Uses Django's test runner (via Evennia)
which builds a throwaway `test_evennia.db3` — never touches the live dev DB.

## Running Tests

From `D:\TAP\TheAbyssalPlanes`:

```powershell
# Full suite
& ..\evenv\Scripts\evennia.exe test --settings settings.py .

# World data/systems only
& ..\evenv\Scripts\evennia.exe test --settings settings.py world.tests

# Command integration only
& ..\evenv\Scripts\evennia.exe test --settings settings.py commands.tests

# Single test class or method
& ..\evenv\Scripts\evennia.exe test --settings settings.py world.tests.test_data.SkillCatalogTest
```

## Test Structure

### `world/tests/` — Data & Systems (SimpleTestCase + EvenniaTest)

| File | Tests | Coverage |
|------|-------|----------|
| `_mock.py` | — | `MockChar`: lightweight DB-free character facade for SimpleTestCase. |
| `test_data.py` | ~37 | Skill catalog well-formedness, weight rules, species consistency, rank thresholds, tier math, point-cost/taper equations, changelog round-trips. |
| `test_systems.py` | ~23 | Stat XP thresholds, locked-column refusal, use_skill advancement, effective-stat remapping, derived-pool math, regen multipliers. |
| `test_combat.py` | ~37 | Grid helpers, navigation phrases, movement announcements, occupancy checks, move allowance, group invite, `opposed_test` stub. |
| `test_calendar.py` | ~12 | Epoch anchoring, day/month/year rollover, planet orbit differences, formatting, ordinal suffixes. |
| `test_announce.py` | ~5 | Movement announcement integration (EvenniaTest). |
| `test_smoke.py` | ~1 | Basic character attribute smoke test (EvenniaTest). |

### `commands/tests/` — Command Integration (EvenniaCommandTest)

| File | Tests | Coverage |
|------|-------|----------|
| `test_commands.py` | ~45 | Skills, train, perceive, manifest, changes, addchange, removechange, emote, setnature, setcanfly, move, force, appearance builders, room visibility, Visarii/Silex plane behavior, speak/hear plane gating. |
| `test_realm_occupancy.py` | ~20 | Realm-gated look sections, per-seat plane occupancy, contest rolls, manifest contested arrivals/departures, pose realm echo filtering. |
| `test_furniture.py` | ~12 | Furniture approach rules (facing, beds, couches), rotation, arrival naming. |
| `test_timers.py` | ~10 | Movement timer (grid steps, arrival, blocking), regen timer, combat state (engage/disengage/flee/resume). |
| `test_map_renderer.py` | ~2 | Plane-aware tactical map filtering. |
| `test_mapsize.py` | ~5 | MapSize command: show, set valid, reject low/high/non-numeric. |

## Test Conventions

- **Pure data/systems** modules use `django.test.TestCase` (SimpleTestCase).
  These don't need a database and run fast.
- **Commands** use `evennia.utils.test_resources.EvenniaCommandTest` which
  creates temporary characters, rooms, and objects.
- **Integration** tests (e.g. `test_announce.py`) use `EvenniaTest` for
  full database-backed scenarios.
- The `MockChar` in `_mock.py` provides a lightweight character with the
  right AttributeProperties for data/systems tests without needing the DB.

## Coverage Notes

- **Well covered:** skill catalog, species, rankings, stat growth, skill
  advancement, effective stat remapping, calendar math, movement, commands,
  furniture approach/rotation, realm contests, plane visibility, emotes,
  appearance paragraph, timers, combat state.
- **Partially covered:** combat (grid/movement only; accuracy/damage/loop
  not tested), group system (invite/join only).
- **Not covered:** accuracy.py, damage.py, loop.py, actions.py,
  discord_integration.py, server_hooks.py, chargen EvMenu.
