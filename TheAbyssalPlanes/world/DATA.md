# DATA

Pure-data modules for The Abyssal Planes. These contain no Evennia imports
(except `calendar.py` which wraps `evennia.utils.gametime`) and are safe
to import from any context including tests.

## Files

### `skills.py` (403 lines)

The skill catalog. 19 skills across 3 categories:

**Corpus (13):**
- Brawling (precursor, no combat stat) — punch, kick, headbutt, knee, axehandle, haymaker (offense tree with prereq chains)
- Melee evasion, parry, block, feint, counterattack (defense tree)
- Bash (utility, door/obstacle)

**Genius (4):**
- Meditate, focused_meditation (focused_meditation requires meditate ≥ 400)
- Lockpick, awareness

**Animus (2):**
- Pray, devoted_prayer (devoted_prayer requires pray ≥ 400)

Each skill defines: `key`, `name`, `category`, `stats` (weighted sub-stats summing to 1.0), `requires` (prereq dict), `precursor`, `reach`, `damage_type`, `health_bar`, `base_time`, `pool_cost`, `desc`.

Key data:
- `TIER_NAMES`: Novice → Grandmaster (10 tiers)
- `TIER_COLORS`: ANSI color per tier
- `DIFFICULTY_XP`: trivial=5, easy=10, medium=15, hard=25, extreme=40
- `get_skill()`, `skill_key()`, `all_skills()`, `categories()`, `stats_for()`, `time_cost()`, `tier_color()`

### `species.py` (317 lines)

9 playable species:

| Key | Archetype | +1 Bonus | Locked Main | Alternate | Zeroed Pools | Nature |
|-----|-----------|----------|-------------|-----------|--------------|--------|
| terran | Human | genius_obsistis | — | — | — | dual_natured |
| virentes | Elf | genius_potestas | — | — | — | dual_natured |
| sideralis | Space elf | animus_obsistis | — | — | — | dual_natured |
| batrachi | Toad-men | corpus_potestas | — | — | — | dual_natured |
| tritonii | Newt-men | corpus_reflexus | — | — | — | dual_natured |
| volucres | Bird-men | animus_reflexus | — | — | — | dual_natured |
| pterati | Bat-men | genius_reflexus | — | — | — | dual_natured |
| visarii | Crystal elf | animus_potestas | corpus | corpus→animus | vigor | visarial |
| silex | Flint orc | corpus_obsistis | animus | animus→corpus | vim | physical |

Key functions: `get_species()`, `stat_bonus()`, `is_locked()`, `alternate_for()`, `zeroed_pools()`, `resolve_pool()` (routes zeroed pool to substitute).

### `appearance.py` (1141 lines)

Appearance data and validators:
- `HEIGHTS`: 5 categories (diminutive → towering)
- `BUILDS`: 22 build words mapped to valid heights
- `SPECIES_ADJECTIVES`: 9 species × 15 adjectives
- `SKIN_TONES`: 49 hex-mapped tones (alabaster → stone-grey, includes fantasy tones)
- `SPECIES_SKIN_TONES`: per-species subsets
- `COLOR_HEXES`: 43-color palette for eyes/hair
- `SPECIES_EYES`, `SPECIES_EYE_COLORS`, `SPECIES_HAIR`, `SPECIES_HAIR_COLORS`
- `POSES`: 18 whitelisted position words

Functions: `height_phrase()`, `height_build_phrase()` (pronoun-aware), `hex_for_skin()`, `valid_pose()`, `color_list_with_hex()`, etc.

### `calendar.py` (220 lines)

Universal calendar: 23-hour day, 28-day month, 13-month year.
- `MONTHS`: Kindre, Veldis, Orde, Solune, Myr, Haelt, Riven, Kas, Dorrin, Vesper, Thalam, Aurune, Varn
- `SIGNS`: The Warden → The Shroud (13 signs)
- `PLANETS`: cindris (182-day orbit), auridon (364-day, DEFAULT), frostfall (728-day)
- `cosmic_date()`, `local_date()`, `format_clock()`, `format_date()`, `sign_of_month()`
- `planet_key_for_location(room)`: resolves planet from `db.planet` or `planetary_body` tag

### `rankings.py` (63 lines)

14-rank stat ladder: none(0) → feeble(1) → weak(5) → poor(9) → below average(13) → average(17) → good(21) → impressive(26) → formidable(32) → legendary(39) → mythic(47) → divine(56) → godlike(66) → ungodly(81). Each has a color. Thresholds are placeholders.

### `colors.py` (83 lines)

47 named colors across 7 material families (woods, metals, leathers, fabrics, stones, glass) with Truecolor hexes. Functions: `get_color()`, `hex_for_color()`, `colored_name()`.

### `items.py` (24 lines)

Item type data. Currently only `furniture` type with materials (wood, metal, leather, fabric, stone, glass) and 7 adjectives. Functions: `get_item_type()`, `get_material()`.

### `materials.py` (37 lines)

Material → color cross-references (wood has 8 colors, metal 8, etc.). Delegates to `colors.py`.

### `changes.py` (781 lines)

Self-modifying changelog. 44 entries (2026-07-29 → present).
- `CHANGES` list of dicts: `{number, date, title, body}`
- `append_entry(title, body)`: auto-numbers, dates today, rewrites file via AST.
- `remove_entry(number)`: removes + renumbers, rewrites file.
- `alert_text()`, `unread()`, `all_changes()`, `get_change()`: query helpers.

The file rewrites itself when entries are added/removed by the `addchange`/`removechange` commands.
