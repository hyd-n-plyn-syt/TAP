# SYSTEMS

Logic modules for The Abyssal Planes. These operate on the data from `world/data/`
and are called by commands and typeclasses.

## Files

### `stats.py` (84 lines)

Stat schema and derived pool formulas.

**Constants:**
- `MAIN_STATS = ("corpus", "genius", "animus")`
- `SUB_STATS = ("potestas", "reflexus", "obsistis")`
- `POOL_KEYS = ("vigor", "vim", "mens")`
- `BASE_DEFAULTS`: all nine sub-stats default 1

**Formulas** (floor division throughout):
- Pools scale by ×3 for base capacity, ×2 for flat bonuses.
- Regen = `1 + (main+obs)//6 + reflexus//4 + cross//8`, min 1/tick.
- Holding full heal near ~16 ticks.

**Functions:**
- `species_bonus(species_data, sub_stat)` — get species +1 bonus.
- `sub_stat_is_locked(species_data, sub_stat)` — is this column locked?
- `effective_sub_stat(base, species_data, sub_stat)` — base + bonus, or 0 if locked.
- `main_stat(bases, species_data, main)` — sum of 3 sub-stats.
- `derived_pools(bases, species_data)` — returns all 6 values (vigor/regen, vim/regen, mens/regen; zeroed pools pinned to 0).

### `skills.py` (225 lines)

Skill value/tier math, point costs, taper curves, prerequisites, and the core `use_skill()` function.

**Tunable constants:**
- `POINT_COST_BASE = 10.0`
- `POINT_COST_GROWTH = 0.5`
- `SKILL_TAPER_RATE = 0.15`
- `STAT_TAPER_RATE = 0.25`
- `MAX_SKILL = 1000`

**Functions:**
- `tier(value)` — 0-1000 → 1-10 tier number.
- `tier_name(value)` / `tier_colored_name(value)` — tier name with optional ANSI color.
- `requirement_str(value)` — "0% Adept" style display.
- `within_tier(value)` — 0-99 progress within current tier.
- `point_cost(tier)` — cost per skill point at this tier.
- `skill_taper(value)` — diminishing returns multiplier for skill XP.
- `stat_taper(value)` — diminishing returns multiplier for stat XP pass-through.
- `skill_value(skill_data)` — read current value from character.
- `known_skills(char)` — list of learned skills.
- `prereqs_met(char, skill_key)` / `missing_prereqs(char, skill_key)` — prerequisite checks.
- `learn_skill(char, skill_key)` — learn at 0% (Novice).
- `xp_to_next(value)` — XP needed for next skill point.
- `effective_skill_stats(char, skill_key)` — remaps locked mains to species alternates.
- `use_skill(char, key, difficulty, times)` — award XP, advance value, feed stat XP. Returns result dict.

### `growth.py` (68 lines)

Sub-stat growth with rising thresholds.

**Constants:**
- `_THRESHOLD_BASE = 5.0`
- `_THRESHOLD_PER_STAT = 3.0` (tuned)

**Functions:**
- `threshold_for(current_value)` — base + 3 × value.
- `stat_xp(char, sub_stat)` — current XP toward next raise.
- `stat_xp_to_next(char, sub_stat)` — XP needed.
- `add_stat_xp(char, sub_stat, amount)` — raise by 1 per threshold crossed; refuses locked columns. Returns `(success, gained, new_value)`.

### `group.py` (22 lines)

Group system stub (in development).

- `GroupManager.invite(sender, target)` — sets `db.group_invite`.
- `GroupManager.join(target, sender)` — moves target to sender's group.
- `toggle_autoassist(char)` — toggles `db.autoassist`.

### `narrative.py` (142 lines)

Shared narrative echo formatting: skin-colored pronouns, first-mention names, and furniture coloring.

**Functions:**
- `skin_color(entity)` — Truecolor hex for an entity's pronouns, or `'w'`.
- `colored_pronoun(entity, case, sentence_start)` — skin-colored pronoun (`'|#hexHe|n'`).
- `colored_self(entity, sentence_start)` — skin-colored `'You'`/`'you'`.
- `colored_poss_self(entity, sentence_start)` — skin-colored `'Your'`/`'your'`.
- `entity_first_ref(entity, sentence_start)` — appearance name with lowered article mid-sentence.
- `narrate_refs()` — per-message dispatcher: first mention = name, later = pronoun.
- `display_color(obj)` — bare color code for furniture/items (no leading pipe).
- `narrative_name(obj)` / `furniture_name(obj)` — color-wrapped display name for furniture.

### `hostility.py` (25 lines)

Hostility check helpers.

- `is_hostile(actor, target)` — reads `db.is_hostile`.
- `hostile_towards(actor, target)` — checks target's hostility + group hostility.

### `tactical.py` (22 lines)

Tactical move stubs (placeholders).

- `opposed_test(...)` — always returns True (placeholder for roll logic).
- `perform_ram(...)`, `perform_restrain(...)`, `perform_subdue(...)` — reference skills that don't exist yet.
