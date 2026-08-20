# The Abyssal Planes — Gameplan

Living document tracking the design and build order. Build phase statuses are
kept current as work happens.

---

## Core Design

- **Levelless growth.** No XP levels. Characters grow solely by using skills;
  there is nothing to "bank" or spend on a level-up.
- **Skills (0-1000, 10 tiers).** Tier 1 = 0-99 ... Tier 10 (Grandmaster) =
  900-1000. A skill's value rises only through use.
- **Everything is a skill.** All actions tie to a skill; every skill ties to
  weighted sub-stat(s) (weights sum to 1.0). Some skills exercise a single
  sub-stat, others spread across several (even across mains, e.g. Feint =
  corpus_reflexus + genius_reflexus).
- **Skills raise stats.** Using a skill slowly feeds its linked sub-stats, which
  are uncapped.
- **Advanced skills are gated** by prerequisites (skill at a rank/percentile),
  e.g. Power Strike requires Attack 300 and Punch 300.
- **Diminishing returns on both axes.** Per-use skill XP tapers per tier AND the
  per-point XP cost rises per tier; stat pass-through also tapers per tier. A
  mastered skill still grows, but slowly - nudging players to branch out.
- **Stats uncapped, with rank ladders.** A main statistic (Corpus / Genius /
  Animus) = the sum of its three sub-stats. Ranks run "none" (locked races) ->
  "feeble" -> ... -> "ungodly". Rank thresholds are placeholders to tune later.
- **Species lock certain mains at 0** (e.g. Visarii corpus, Silex animus).
  Locked columns never gain XP and stay at 0; their pools are zeroed/hidden.
  Skills tied to a locked column normally get no stat XP, BUT locked species
  remap that column to an alternate main (Visarii corpus -> animus, Silex
  animus -> corpus; see `locked_alternates` in world/data/species.py), so the
  skill still exercises a meaningful stat.
- **Ranks and tiers are colored.** Stat ranks (none -> ungodly) and skill
  tiers (Novice -> Grandmaster) each have an ANSI color shown on score, the
  skills list, and trainer listings.
- **Skills start unlearned.** Characters begin with no skills and pick up the
  first ones from a trainer in the creation area (`Center of Creation`, the
  new-character home via DEFAULT_HOME).
- **Trainers.** A builder designates an NPC with `settrainer <target> = s1, s2`
  (stored as `trained_skills`). Players use `train` to list trainers here or
  `train <skill>` to learn it (0%, Novice) if prerequisites are met.
- **Requirements show as percent-of-tier**, e.g. "Attack 0% Adept", "Meditate
  0% Expert", "50% Master" - never raw 300/400 numbers.

---

## Completed

<!-- Checked off as work finishes. Brief one-liners only — details moved above. -->

- [x] Skill catalog with 19 skills across 3 categories (corpus/genius/animus), weighted stats, prerequisites, difficulty→XP table, 10 tier names with colors.
- [x] Stat growth system: XP accumulation + thresholds, refuses species-locked columns, diminishing returns.
- [x] Main-stat rank ladder (none→ungodly, 14 ranks, colored) + tier math + `requirement_str` ("0% Adept" style).
- [x] 9 playable species with visarial nature, persistent +1 stat bonus, locked columns + alternate mains, zeroed pools, perceive/manifest capability.
- [x] Appearance system: height/build/adjective/skin/eyes/eye colour/hair/hair colour, 49 skin tones, species-specific palettes, generated multi-sentence descriptions.
- [x] Whitelisted pose system: 18 positions, `setpose` (builder) + `sit`/`rest`/`sleep`/`wake`/`lay`/`stand`/`rotate` (player, furniture-aware).
- [x] Visarial plane & Vim-connection model: `visarial_nature` (physical/visarial/dual_natured), `visarial_state` (normal/perceiving/manifested), per-entity see/touch/speak/hear flags, plane-gated room listings.
- [x] 5D room grid: two-tier coordinate tags (planet + site), `dig`/`setorigin`, clockwise exit rendering, portal grouping.
- [x] Tactical tile grid: `pos_x/y/z` on entities, `room_size` (tiny→massive), z-axis, compass movement, flying.
- [x] Trainers + `train`/`settrainer`, colored tiers, prerequisite gating, spawn at Center of Creation.
- [x] `score` showing species, sub-stats, derived mains, pools, regen rates, rank ladders.
- [x] Live prompt with `numbers`/`percent`/`bars` modes, gradient colors, plane/state display.
- [x] `skills` command (list learned, detail per skill, `skills all` for full catalog).
- [x] `attset` builder command for stat/pool manipulation and testing.
- [x] Cosmic calendar: 23-hour day, 28-day month, 13-month year, 3 orbiting planets, `time` command.
- [x] `perceive`/`manifest` commands gated by species capabilities.
- [x] Realm-aware say (`at_say` override) + realm-gated emote engine (`@target`/pronoun system).
- [x] Guided character creation: `charcreate` EvMenu (gender→species→appearance→stat priorities→distribution).
- [x] `mychars` command listing all characters on an account.
- [x] Doors & locks: `is_door`, open/close/lock/unlock, key objects, lockpick DC, breakable walls, hidden exits, sibling sync.
- [x] `digmenu` builder tool: guided room creation with door/lock/hidden/breakable setup.
- [x] Furniture system: `Furniture` typeclass with grid occupancy, facing, dimensions, seats, allowed states, quality (regen multiplier), `createfurniture` EvMenu.
- [x] Item system: `Item` typeclass with multi-material Truecolor descriptions, `createitem` EvMenu.
- [x] Combat loop: `CombatLoop` script (1s tick, 6s round), action queue (max 3), attack/parry/dodge/block accuracy, base damage (skill category + sub-stat), armor subtraction, pool damage, knockout messages.
- [x] Grid movement: `move` command, `approach`/`shove`, `CmdMove`/`CmdShove`/`CmdApproach`, navigation system, `fly`/`land`.
- [x] `where` map renderer: ASCII tactical grid display, `wherekey` legend, `autowhere` toggle.
- [x] Changelog: `changes` command (unread/all/single), `addchange`/`removechange` (Admin), 44 entries, login alerts, server-start broadcast.
- [x] Discord bridge: OOC relay, announcements channel, server lifecycle messages, role-based coloring.
- [x] `GameMuxCommand` base: prompt refresh after every command, sleeping-command block.
- [x] Direction fallbacks: dynamic per-room "cannot move" messages for missing exits.
- [x] Test suite: ~115 world tests + command integration tests across 8 files.
- [x] File-based help entries: 25 topics (stats, pools, species, appearance, time, planets, prompt).

---

## Remaining

<!-- Active design direction. Full detail lives here for reference. -->

### Phase 3 — Combat (in progress)

The attack/damage/accuracy core is built. Missing pieces:

- **Knockout state.** Currently cosmetic (messages only, no actual unconscious/defeat state). Need a knockout flag, timeout, and wake-up mechanics.
- **`use_skill()` integration.** Combat does not award skill/stat XP yet — the usage-based progression doesn't trigger during combat resolution. Need `use_skill()` called on hit.
- **Non-attack actions.** The combat loop silently drops anything that isn't an `"attack"` action type. Need action-type dispatch for parry, dodge, block, feint, counterattack, meditate, pray, etc.
- **Armor & worn gear.** `get_armor_value` reads `db.worn` + `db.armor` but nothing sets these yet. Depends on Phase 4 item equip system.
- **Ranged/weapon skills.** All 19 skills are reach-1 brawling. Need ranged skill categories, weapon objects, reach mechanics, and damage-type variety.
- **Precursor skill effects.** The precursor system (e.g. brawling feeds all combat skills) is defined but precursor bonus is only damage — extend to accuracy, time cost, etc.
- **Status descriptors.** `combat/target.py` has placeholder status text ("mentally sound"/"distraught") disconnected from actual pools. Need proper mapping per pool.
- **Training dummies / sparring.** Practice targets that don't fight back, for skill grinding without risk.

### Phase 4 — Items & Equipment (in progress)

Furniture and items typeclasses are built. Missing pieces:

- **Worn equipment.** Weapon/armor slots, `worn` list on characters, equip/unequip commands.
- **Stat/skill modifiers.** Items that grant stat bonuses or skill modifiers when equipped.
- **Containers.** Items that hold other items (bags, chests).
- **Loot.** Dropped items from defeated enemies or found in the world.
- **Currencies & shops.** Money system, shopkeeper NPCs, buy/sell.
- **Crafting.** The `commands/crafting/` package exists as an empty placeholder — needs design.

### Phase 5 — Custom Character Creation (in progress)

EvMenu chargen is fully functional. Missing pieces:

- **Starting skills.** New characters currently start with no skills; need a way to grant 1-2 starting skills during chargen (species-based or player choice).
- **Birth sign selection.** Sign is auto-rolled at creation; could be offered as a choice or kept random.

### Phase 6 — World, NPCs, Content & Polish (planned)

- Grid expansion, zones, population, roaming mobs (incl. carrying unconscious players to inns).
- GMCP/Mudlet client integration for bars/prompts.
- Sound, accessibility, onboarding; tuning of all placeholder numbers.
- `world/planets/` — planet-specific zone content (currently empty placeholder).
- Group system completion (invite/join exists; shared hostility, group combat, party mechanics needed).
- Hostility system (flag exists, but `hostile_towards` logic is a stub).
- Tactical moves (`ram`/`restrain`/`subdue`) — defined in `world/systems/tactical.py` as stubs.
- Injuries scaffold: flags + rate modifiers + special healing hooks.
- LOGOUT / REST room attribute markers for offline regen.
- Offline regen, unconscious-on-bad-logout, DRAG/CARRY + TUCK IN handling.

---

## Fixed Decisions (locked)

- **meditate / pray** are skills AND poses, usable only if the skill is known;
  the skill level scales their effectiveness (regen quality).
- **Regen is tick-based + rest-based.** Ticks run on a ~1s interval (CombatLoop)
  with a 60-tick regen pass; resting, sleeping, meditating, and praying give
  different regen values. Furniture quality multiplies the rate.
- **Injuries** (flags, to be designed) modify regen rates; some healing methods
  are special-cased.
- **Offline:** A character only receives persistent regen while logged out in a
  LOGOUT-capable room. Logging out anywhere else drops them unconscious where
  they stand. They wake where their body is, even if dragged, and keep receiving
  regen while unconscious. DRAG/CARRY to a LOGOUT room + TUCK IN by another
  player enables a full logout.
- **Room features live on attributes** (a room can be both a REST room and a
  LOGOUT room), not tags.
- **charcreate links characters to accounts** (stock Evennia). NPCs are separate
  standalone objects.
- **Planethemes:** perceiving = yellow, manifesting = cyan; physical plane = dark
  gray, visarial = magenta (prompt/score).
- **Object/entity planes & vim connection:** `visarial_nature` controls both the
  plane and the Vim connection. *Physical-natured* (Silex, plain rocks) are IN and
  OF the physical - physical desc only, never a custom `visarial_desc`, and to a
  perceiver they show a dark-gray 'absolutely disconnected from Vim' line.
  *Visarial-natured* (Visarii) are IN and OF Vim - visarial desc only, no physical
  desc (a magenta Vim aura by default). *Dual-natured* are IN physical by default
  but OF both, so they carry both a physical and a visarial desc. Only creatures
  (`is_creature`) perceive or manifest; plain objects are fixed to their
  nature's plane. Visibility is driven by four per-entity flags (`can_phys_see`,
  `can_vis_see`, `can_phys_touch`, `can_vis_touch`) so see/touch can be controlled
  independently; speech and hearing mirror it (`can_speak_*`/`can_hear_*`, wired
  into `Character.at_say`). Builders set a prop's nature with the `setnature`
  command, and staff `force`/search bypass plane and location.

---

## Current System Notes

- Skill tier names: Novice, Apprentice, Journeyman, Adept, Expert, Artisan,
  Master, High Master, Archmaster, Grandmaster.
- Skill XP by difficulty: trivial 5 / easy 10 / medium 15 / hard 25 / extreme 40.
- Point cost = 10 * (1 + 0.5 * (tier-1)); skill taper 0.15/tier; stat taper
  0.25/tier. All tunable in `world/systems/skills.py`.
- Stat threshold = 5 + 3 * current_value (`world/systems/growth.py`).
- `use_skill(char, key, difficulty, times)` returns a result dict; refuses
  unknown skills (reason "unknown") and unmet prereqs (reason "prereq").
- `requirement_str(value)` renders a skill value as "NN% Tier" (e.g. "0% Adept",
  "50% Master") for prerequisites and thresholds.
- Trainers store their offered skills in the `trained_skills` attribute (set by
  `settrainer`); Characters expose it as `trainer_skills`.
- Combat loop: 1s tick, 6s round, 6 max grids/round, 60s regen cycle.
- Damage: (main_stat + highest_sub) × variation × (1 + precursor_bonus).
- Crit threshold: 20.0 at skill 0 → 5.0 at skill 1000 (margin ≥ threshold).
- In-game changelog: 44 entries (`world/data/changes.py`), 2026-07-29 → present.
- Main-stat rank ladder and all stat thresholds are placeholder numbers marked
  for tuning.

---

## Automated Tests

- Evennia runs the test suite with Django's test runner, which builds a
  throwaway database and exercises the game against it.
- **Run everything:**
  `evennia test --settings settings.py .`
- Run one group (e.g. data/systems or command integration):
  `evennia test --settings settings.py world.tests`
  `evennia test --settings settings.py commands.tests`
- Test locations: `TheAbyssalPlanes/world/tests/` (pure-data + mock snippets
  for world/data and world/systems) and `TheAbyssalPlanes/commands/tests/`
  (evennia integration via `EvenniaCommandTest`). Pure modules use
  `django.test.SimpleTestCase`; DB-backed `EvenniaTest` for commands.
- The runner never touches the live game DB (it creates `test_evennia.db3`),
  so tests are safe to run against a running dev server.
- Core/game tests are distinct from Evennia's own suite (`evennia test evennia`).
- Suite is at ~334 tests (125 data/systems + 209 command integration) and passing.
