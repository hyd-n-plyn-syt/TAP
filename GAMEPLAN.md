# The Abyssal Planes - Gameplan

Living document tracking the design and build order. Build phase statuses are
kept current as work happens.

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
  skills list, and trainer listings. Ready to reuse anywhere.
- **Skills start unlearned.** Characters begin with no skills and pick up the
  first ones from a trainer in the creation area (`Center of Creation`, the
  new-character home via DEFAULT_HOME).
- **Trainers.** A builder designates an NPC with `settrainer <target> = s1, s2`
  (stored as `trained_skills`). Players use `train` to list trainers here or
  `train <skill>` to learn it (0%, Novice) if prerequisites are met.
- **Requirements show as percent-of-tier**, e.g. "Attack 0% Adept", "Meditate
  0% Expert", "50% Master" - never raw 300/400 numbers.

## Fixed Decisions (locked)

- **meditate / pray** are skills AND poses, usable only if the skill is known;
  the skill level scales their effectiveness (regen quality).
- **Regen is tick-based + rest-based.** Ticks run on a ~30s interval tied to the
  universal calendar so all tick systems advance together. Resting, sleeping,
  meditating, and praying give different regen values.
- **Injuries** (flags, to be designed) modify regen rates; some healing methods
  are special-cased.
- **Offline:** A character only receives persistent regen while logged out in a
  LOGOUT-capable room. Logging out anywhere else drops them unconscious where
  they stand. They wake where their body is, even if dragged, and keep receiving
  regen while unconscious. DRAG/CARRY to a LOGOUT room + TUCK IN by another
  player enables a full logout. (Roaming mobs carrying people to inns is a
  later-phase stretch.)
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

## Build Phases

### Phase 1 - Skills, Growth, Rankings (status: DONE)

Foundation of the whole progression system.

- [x] `world/data/skills.py` - skill catalog: keys, names, categories, weighted
  stats, prerequisites, difficulty->XP table, 10 tier names.
- [x] `world/data/rankings.py` - main-stat rank ladder.
- [x] `world/systems/growth.py` - stat XP accumulation + thresholds, refuses
  species-locked columns.
- [x] `world/systems/skills.py` - value/tier math, point costs, taper curves,
  prereq checks, learn/unlearn, `use_skill()` feeding skill + linked stats.
- [x] Character wiring: `skills`, `skills_xp`, `stat_xp` AttributeProperties and
  a `use_skill()` shorthand (`typeclasses/characters.py`).
- [x] Commands: `skills` (view all / detail, `commands/player/skills.py`) and
  `setskill` (builder learn/set/force/reset, `commands/building/setskill.py`),
  registered in the character + building cmdsets.
- [x] `score` now shows each main stat's rank.
- [x] Species alternate mains: skills exercising a locked stat column feed the
  species' alternate main instead (Visarii corpus->animus, Silex animus->corpus),
  via `effective_skill_stats()`.
- [x] Colored stat ranks (score) and colored skill tiers (skills list, trainer
  listings); `requirement_str()` shows thresholds as "NN% Tier" everywhere.
- [x] `train` (players list trainers / learn a skill at 0%, gated by prereqs)
  and `settrainer` (builder designates a trainer's skills). Registered in the
  character cmdsets.
- [x] New characters home to `Center of Creation` (DEFAULT_HOME="#3"), with a
  trainer NPC (Keeper Solenn) offering the fundamentals and the advanced skills
  as goals.
- [ ] Additional player-facing *use* actions for combat/meta skills (Phase 3/5).

### Phase 2 - Regen, Rest, Time

- Regen tick (~30s) tied to the universal calendar tick.
- Resting / sleeping / meditating / praying poses drive rest-based regen with
  different rates; meditate/pray scale with their skill levels.
- LOGOUT / REST room attribute markers.
- Offline regen, unconscious-on-bad-logout, DRAG/CARRY + TUCK IN handling.
- Injuries scaffold: flags + rate modifiers + special healing hooks.

### Phase 3 - Combat

- Combat loop: attack/parry/dodge/block resolution driven by the matching
  skills, accuracy scaled by skill tier, damage from stat pools.
- Turn/economy: stamina (Vim/Vigor) costs; cooldowns for advanced skills.
- Facing/position (pose) interaction; knockout via pool depletion.
- Training dummies / sparring to practice skills safely.

### Phase 4 - Items & Equipment

- Item typeclass: weapons/armor carrying stat/skill modifiers.
- Worn/wielded slots; item affects effective skill checks and damage.
- Containers, loot, currencies; shopkeeper NPCs.

### Phase 5 - Custom Character Creation

- Replace stock creation with a guided flow: species pick, appearance, starting
  skills, sign/birth date.
- Player-visible skill learning path (teachers, trainers, practice).

### Phase 6 - World, NPCs, Content & Polish

- Grid expansion, zones, population, roaming mobs (incl. carrying unconscious
  players to inns).
- GMCP/Mudlet client integration for bars/prompts.
- Sound, accessibility, onboarding; tuning of all placeholder numbers.

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
- Main-stat rank ladder and all stat thresholds are placeholder numbers marked
  for tuning.

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
