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
- [x] Mudlet client package (`web/static/mudlet/`): Map + Communication windows, bottom prompt bar, tab-click switching, `TAP help/reset/fontsize/font/on|off/update` aliases, settings persistence (`TAP_settings.lua`), window-layout save/restore, auto-update via `installPackage(url)`.
- [x] Webclient UI plugin (`web/static/webclient/js/plugins/tap_ui.js`): TAP Map pane (text-stream frame capture + `room_map` fallback, clear-and-replace), TAP Comm pane (Local/OOC/MudInfo tabs, per-tab buffers), full ANSI parser (16-color + xterm256 + truecolor), Evennia pipe→ANSI converter, main-window font sync, saved-layout auto-heal.
- [x] GMCP payload pipeline: `world/systems/gmcp.py` converts every custom payload to ANSI server-side (`_to_ansi`); `send_map` wired into all autowhere paths (movement timers ×2, teleport, room entry, `check_autowhere`) so every client's map updates identically.
- [x] Comm parity: say/emote/OOC/MudInfo send the exact main-window line to the comm tabs (say lines from `at_say`, channel formatting mirrored in `channels.py line_for` incl. perm-colored sender names); login/logout announcements use permission-colored names.
- [x] Webclient template override (`web/templates/webclient/base.html`) with versioned script tags for cache-busting.

---

## Account / OOC Lounge / Wisp — Full Design (2026-08-26)

> Source: user plan clarifications 2026-08-26. This section is the canonical
> spec for the account main menu, OOC lounge, and wisp account-character.
> Login → new main menu; Exit → main menu → 0. No `ic` routing — menu is the
> only way to swap characters or exit.

### Overview

- **Account-level menu, first and last screen.** `Account.at_post_login`
  (`typeclasses/accounts.py:155`) is the entry point. No auto-create /
  auto-puppet on login. `server/conf/settings.py:52` sets
  `AUTO_CREATE_CHARACTER_WITH_ACCOUNT = False` and
  `AUTO_PUPPET_ON_LOGIN = False`; the `else` branch in
  `evenv/.../accounts.py:1743` is replaced by
  `EvMenu(account, "commands.account.main_menu", startnode="node_main",
  session=session)`.
- **Single puppet rule.** `MULTISESSION_MODE = 0`,
  `MAX_NR_SIMULTANEOUS_PUPPETS = 1`. The account puppets **either** one IC
  character **or** the wisp (OOC). Lounge = wisp puppet; IC = menu → choose
  character → puppet; swapping always goes `unpuppet → menu → puppet`.
- **Wisp is the account character.** Pseudo-species `wisp` (`world/data/species.py:33`
  `SPECIES["wisp"]`) with `locked_main_stats = ("corpus","genius","animus")`,
  `zeroed_pools = ("vigor","vim","mens")`, `can_perceive/can_manifest = False`.
  All 9 sub-stats read `0` via `world/systems/stats.py:42` `effective_sub_stat`
  + `derived_pools:80` hide; `growth.py` refuses XP if `is_wisp`. Wisp name
  **equals `account.key`** — this is what shows on the `OOC` channel
  (`typeclasses/accounts.py:30` `_perm_color` / `typeclasses/channels.py:49`
  `ooc` prefix). Wisp is **not deletable** (`chardelete` filters it out;
  lock `delete:false()` on `typeclasses/wisp.py`).
- **OOC lounge is Limbo `#2`.** No new room. Flag `#2` as `OOC_Room`:
  `db.is_ooc_room = True` + tag `ooc_room` (`category="room_flag"`) plus the
  existing `planetary_body` tags. All future OOC branches parent to `#2` via
  `home`. Helper `world/systems/wisp.py:is_ooc_room(room)` centralizes the
  check. `typeclasses/rooms.py:16` lounge header tweaked; no exits required —
  you arrive only via menu option 4 puppeting the wisp.
- **Wisp sees/hears/touches everything in the lounge.** Because the wisp
  **never exists in the real game** (only `#2`), it is exempt from plane
  gating there: `can_phys_see/can_vis_see/can_phys_touch/can_vis_touch`
  force-`True` when `is_wisp and is_ooc_room(location)`, and `at_say` is not
  realm-gated in that room. Outside `#2` (should never happen) normal
  `ObjectParent` rules apply.
- **Lifecycle:** `Login → Main Menu` → `4 → puppet wisp in #2 (look)` →
  `quit → unpuppet → Main Menu` → `1 → puppet IC char` → `quit → Main Menu`
  → `0 → disconnect`. `OOC` is already a channel; `ic` is removed from
  `AccountCmdSet` (`commands/default_cmdsets.py:182` `remove("ic")`) so there
  is no bypass. `quit`/`ooc`/`exit` on a puppeted char/wisp do
  `account.unpuppet_object(session)` → re-launch menu instead of disconnect;
  only menu `0` calls `disconnect_session_from_account`. Both
  `AccountCmdSet` and `CharacterCmdSet` (`commands/default_cmdsets.py:80`)
  override `quit` via `commands/account/menu_commands.py:CmdQuitToMenu`.
- **Migration for legacy same-name character.** On `at_post_login` before
  menu, if `ObjectDB.objects.filter(db_account=account,
  db_key__iexact=account.key).first()` exists and is not already a wisp
  (`not getattr(obj,"is_wisp",False)`), treat it as the wisp: `swap_typeclass`
  to `typeclasses.wisp.Wisp`, set `species_key="wisp"`, `move_to(limbo,
  quiet=True)`, and mark for wisp customization on next lounge entry. If
  multiple matches, keep the first. `db._last_puppet` is cleared if it pointed
  at the converted object.

### Main menu spec (account-level EvMenu `commands/account/main_menu.py`)

```
0) Exit the game.           → disconnect_session_from_account(session, "quit")
1) Choose a character (N)   → node_choose_list; if N==0 → msg
                              “You have no characters yet — choose 2 to create one.”
                              else numbered list of non-wisp chars (mychars style
                              commands/account/mychars.py:40 + evenv/.../accounts.py:1939
                              “(played by someone else)” handling)
2) Create a character (U/T slots used) → node_create_name → inline name prompt,
                              validate non-empty, not colliding case-insensitively
                              with existing chars, not equal to wisp name,
                              check Available via account.get_character_slots()
                              (typeclasses/accounts.py:181 3/4); if full → msg
                              “You have used all X character slots.” and stay.
                              On valid name store caller.ndb._chargen_name and
                              delegate to commands.account.chargen_menu
                              (startnode="node_welcome") with cmd_on_exit back to
                              node_main; chargen finalize no longer hints “ic <name>”.
3) Delete a character        → node_delete_list (wisp excluded) → yes/[no] confirm
                              (evenv/.../account.py:205 pattern) → characters.remove
                              + delete(); clear db._last_puppet if needed
4) Go to the lounge.         → get_or_create_wisp(account) (world/systems/wisp.py)
                              → puppet_object(session, wisp) → close menu → look in #2;
                              if wisp unconfigured (no size/color/adjective) auto-launch
                              wisp_menu (see below)
   also accept: quit/exit/q as alias for 0 when already in menu
```

- Presentation: disabled states still callable but error (“no characters yet” /
  “slots full”) and return to `node_main`; no true greyed EvMenu disable.
- Slot line on option 2 is `f"({used}/{total} slots used)"` where
  `total = account.get_character_slots()` and
  `used = len([c for c in account.characters.all() if not is_wisp(c)])`.

### Wisp data & appearance

- **Species entry:** `world/data/species.py:33` `SPECIES["wisp"]` as above.
- **Color palette:** new block `Light` in `world/data/colors.py:5`
  (`COLORS` dict: `white-light`, `gold-light`, `azure-light`, `violet-light`,
  `ember-light`, `cyan-light`, `rose-light`, `silver-light`, `ice-light`,
  `clear-light`, etc., each with Truecolor hex). Helper
  `WISP_LIGHTS = tuple(k for k in COLORS if k.endswith("-light"))` and existing
  `hex_for_color`/`colored_name` reused. Wisp uses this list for its color step;
  `appearance.py` `hex_for_name` also resolves it. Closes `|n` required to avoid
  bleed (`GAMEPLAN Client UI Notes`).
- **Appearance entries:** `world/data/appearance.py`
  - `SPECIES_ADJECTIVES["wisp"]` = 12–15 light-appropriate adjectives
    (e.g., `flickering, pulsing, steady, wavering, brilliant, dim, humming,
    cold, warm, prismatic, soft, sharp, echoing, hazy`). Descriptions in
    `SPECIES_ADJECTIVE_DESCRIPTIONS["wisp"]` (e.g., “Their light flickers like
    a candle in wind.”).
  - No height/build split. Wisp has a single trait **`size`** (5 options, same
    count as `HEIGHTS` `appearance.py:20` but wisp-named, **not tiny** — same
    relative scale as a person). Proposed:
    `WISP_SIZES = ("small","modest","middling","large","immense")` or
    `("faint","soft","middling","radiant","blazing")` — final names to be set
    in `appearance.py`; menu shows one `size` step with that list.
  - `SPECIES_SKIN_TONES["wisp"]` (or `WISP_LIGHTS` alias) = the Light palette
    above; `SKIN_TONES` gets matching hex entries so `hex_for_skin("wisp",
    tone)` works.
  - No eyes/hair sub-menus for wisp (those tables get `["none"]` or are skipped).
- **Typeclass:** `typeclasses/wisp.py:Wisp(Character)` (`is_wisp=True`),
  `at_object_creation` defaults `species_key="wisp"`, `appearance_size`,
  `appearance_adjective`, `appearance_light_color` (stored as `appearance_skin`
  alias), `gender` (`male`/`female`/`neuter`), location `#2`, locks
  `puppet:id(account.id)`, `delete:false()`. `is_injured`/`reset_pools` no-ops;
  `appearance_paragraph`/`appearance_bits` emit e.g.,
  “A radiant white-light wisp, pulsing softly, hovering here.” with light
  hex coloring the species name (mirrors `species_display_name`).
- **Helper:** `world/systems/wisp.py:get_or_create_wisp(account)` —
  finds `ObjectDB` wisp by `db_account=account` + `db_key__iexact=account.key`
  + `typeclass_path` contains `wisp`; creates via
  `evennia.create.create_object("typeclasses.wisp.Wisp", key=account.key,
  location=limbo, home=limbo, account=account)` if missing.

### Wisp customization menu (`commands/account/wisp_menu.py`)

- First lounge puppet only: if `not wisp.appearance_skin or not
  appearance_adjective or not appearance_size/gender`, auto-launch
  `EvMenu(account, "commands.account.wisp_menu", …, session=session)`.
- Nodes: `welcome → gender (male/female/neuter, chargen parity
  chargen_menu.py:69) → color (Light palette via colors.py with
  hex display) → adjective (SPECIES_ADJECTIVES["wisp"]) → size (WISP_SIZES 5)
  → review → finalize` writes directly to wisp attrs, then `look` in `#2`.
- Stores on the wisp object itself; no stat/species steps (wisp species is fixed).

### File changes (authoritative list)

- `server/conf/settings.py:52` — add `AUTO_CREATE_CHARACTER_WITH_ACCOUNT=False`,
  `AUTO_PUPPET_ON_LOGIN=False`.
- `typeclasses/accounts.py:155` — `at_post_login` migration + launch main menu;
  keep `send_gui_install` + MudInfo announce.
- `commands/account/main_menu.py` — new (see spec above).
- `commands/account/wisp_menu.py` — new (gender/color/adjective/size).
- `commands/account/chardelete.py` — new `CmdCharDelete` filtering out wisp.
- `commands/account/menu_commands.py` — new `CmdQuitToMenu`/`CmdOOCToMenu`
  (unpuppet → menu).
- `typeclasses/wisp.py` — new `Wisp`.
- `world/systems/wisp.py` — new helpers `get_or_create_wisp`, `is_wisp`,
  `is_ooc_room`.
- `world/data/species.py:33` — add `SPECIES["wisp"]`.
- `world/data/colors.py:5` — add `Light` block + `WISP_LIGHTS`.
- `world/data/appearance.py` — add `SPECIES_ADJECTIVES["wisp"]`,
  `..._DESCRIPTIONS`, `SPECIES_SKIN_TONES["wisp"]`, `WISP_SIZES` + paragraph
  branch for `is_wisp`; single `size` replaces height/build for wisp.
- `world/systems/stats.py:42` + `growth.py` — guard `is_wisp`.
- `typeclasses/characters.py:51` — `appearance_paragraph` wisp branch, `is_wisp`.
- `typeclasses/rooms.py:16` — OOC lounge header / `is_ooc_room`.
- `commands/default_cmdsets.py:167` — `AccountCmdSet: remove("ic")` (plus existing
  `remove("ooc")`), register `CmdCharDelete`/`CmdQuitToMenu`/`CmdMainMenu`;
  `CharacterCmdSet:80` override `quit`/`ooc` to go to menu.
- `commands/account/chargen_menu.py:702` — finalize returns to `main_menu`.

### Verification

- Login as fresh account → menu shows `1) … (no characters yet…)` / `2) … (0/3)`.
- `2` with full slots (3/3 or 4/4) blocks.
- `chardelete` cannot target wisp.
- `4` creates wisp named after account, runs wisp menu first time, lands in `#2`.
- `quit` from wisp or IC char returns to menu; no `ic` bypass.
- Legacy same-name char migrated to wisp on next login (swap_typeclass +
  `species_key="wisp"` + moved to `#2`).
- Tests: `evennia test --settings settings.py .` plus scratch `evennia shell`
  `ObjectDB` checks for wisp/typeclass/species/locks.

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

### Client UI Notes (Mudlet package + webclient plugin)

**Architecture**
- Mudlet package source: `web/static/mudlet/theabyssalplanes/theabyssalplanes.xml`,
  zipped to `theabyssalplanes.mpackage` next to it. After editing the XML:
  re-zip (folder → zip, renamed `.mpackage`) AND bump the `client_GUI` version
  in `world/systems/gmcp.py` so logged-in clients auto-update on next login.
  One-off `TAP update` alias does `installPackage(url)` + `resetProfile()`.
- Alias XML schema (from Mudlet's `XMLexport.cpp`): `<AliasPackage><Alias
  isActive isFolder>` with children in exact order `name, script, command,
  packageName, regex`. Keep existing ScriptPackage/TriggerPackage untouched.
- Webclient plugin: `web/static/webclient/js/plugins/tap_ui.js`, loaded in the
  `base.html` override **before `goldenlayout.js`** (its `postInit()` must
  register components before GoldenLayout's `postInit` calls `myLayout.init()`)
  and therefore also before `default_out.js` (so its `onUnknownCmd` claims our
  OOB commands first). Template override lives at
  `web/templates/webclient/base.html`.
- Offline JS testing: run the plugin under Node with stubbed
  jQuery/GoldenLayout before shipping changes — build the stub harness ad hoc
  in a gitignored scratch dir and delete it afterwards.

**Gotchas learned the hard way**
- The `v1.evennia.com` websocket wire format delivers main-window text as
  **HTML** (`parse_html`: `<div>`, `&nbsp;`, pipes as `&#124;`). Any client-side
  pattern matching must plainize first; raw `/===\` never appears literally.
- `parse_html` truecolor bleed: once a `|#hex` span opens, every later span
  inherits it until a hard reset. **Always close a `|#hex` name with `|n`
  before any other colored text** (channel lines do this; announcements must
  too). Mudlet is unaffected — telnet ANSI is stateful-correct.
- Custom GMCP payloads bypass Evennia's pipe→ANSI conversion. Always wrap
  payload strings in `_to_ansi()` (`parse_ansi(..., xterm256=True,
  truecolor=True)`) in `gmcp.py`, or clients get literal pipe codes.
- New autowhere call sites MUST call `send_map(char, map_text)` alongside
  `char.msg(map_text)` — Mudlet captures frames from its own stream, but the
  webclient pane relies on `room_map`/text capture parity.
- Browsers cache `tap_ui.js` / `goldenlayout_default_config.js` aggressively:
  bump the `?v=N` query string in `base.html` on every plugin change.
- GoldenLayout persists layout in localStorage (`evenniaGoldenLayoutSavedState`)
  and overwrites it on every state change — a broken load can poison it.
  `tap_ui.init()` auto-heals by deleting saves missing "TAP Map"/"TAP Comm".
- Channel sender-name colors come from `Account.at_pre_channel_msg` in
  `typeclasses/accounts.py` (`_perm_color` truecolor hex); `channels.py line_for`
  mirrors it via `_perm_hex`. Change both together.
- Multi-client login kicks the older session (Evennia session replacement) —
  not a bug.

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
