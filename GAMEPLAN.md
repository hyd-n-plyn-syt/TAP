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
  Skills tied to a locked column can still be *learned* but their stat XP is
  refused; skills that mix mains still feed the unlocked ones.

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
- [x] Verified live (evennia shell): learn/use, tier math, double taper,
  stat growth, prereq gating, unknown-skill refusal, locked-column refusal.
- [ ] Player-facing way to *learn* basic skills (see Phase 5).

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
- Main-stat rank ladder and all stat thresholds are placeholder numbers marked
  for tuning.
