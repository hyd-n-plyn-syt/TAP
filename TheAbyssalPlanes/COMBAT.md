# COMBAT

The combat engine for The Abyssal Planes. A tick-based simulation that handles
combat, grid movement, rest, and regeneration inside rooms.

## Architecture

A single `CombatLoop` script runs per room, firing every 1 second. It manages:
- **Combat resolution** (action queue → accuracy → damage → pool application)
- **Grid movement** (autonomous step-by-step navigation)
- **Rest & regeneration** (60-tick cycle with pose/furniture multipliers)

There is no separate "combat mode" — the same loop handles everything.

## Timing

| Constant | Value | Purpose |
|----------|-------|---------|
| `SUB_TICK_RATE` | 1 | Loop fires every 1 second |
| `GLOBAL_ROUND_DURATION` | 6 | A round = 6 sub-ticks = 6 seconds |
| `MAX_GRIDS_PER_ROUND` | 6 | Max grid steps per round |
| Regen cycle | 60 ticks | Regeneration pass every ~60 seconds |

## Files

### `loop.py` — `CombatLoop` (the engine)
The main `DefaultScript` subclass. Non-persistent, keyed `"combat_loop"`.
- `at_repeat()`: advances round counter (1–6), resets `movement_used` on tick 1,
  runs regen pass every 60 ticks, processes navigation and combat for each character.
- `process_navigation(char)`: one grid step toward destination. Handles approach
  re-targeting, z-climb/landing, exit traversal (autoopen with key), arrival
  messages, nav queue draining.
- `resolve_tick(char)`: pops one action from `action_queue`, adds `time_cost` to
  `movement_used`, pays `pool_cost`, resolves hit/damage/knockout for attack actions.

### `accuracy.py` — Hit resolution
- `get_attack_roll(char, skill_key, skill_value)`: skill_value + effective(category, reflexus) × 0.5.
- `get_defense_roll(char, attack_skill_key)`: best roll among melee_evasion/parry/block.
- `resolve_hit(...)`: returns (hit, attack_roll, defense_roll, is_crit). Crit when margin ≥ threshold (20 at skill 0 → 5 at skill 1000).
- `get_reach(skill_key)` / `check_range(attacker, target, skill_key)`: grid distance checks.

### `damage.py` — Damage pipeline
- `get_damage_stats(char, skill_key)`: main stat (category) + highest sub-stat.
- `calculate_variation(skill_value)`: 65–100% at skill 0 → 85–120% at skill 1000.
- `get_precursor_bonus(char, skill_key)`: precursor skill value / 1000.
- `get_armor_value(target, damage_type)`: sums `db.armor[damage_type]` over `db.worn` (currently 0 for all).
- `calculate_base_damage(...)`: (main + highest) × variation × (1 + precursor).
- `apply_damage(target, health_bar, damage, is_crit)`: species-routes pool, clamps ≥ 0.

### `actions.py` — Action queue
- `MAX_ACTION_QUEUE = 3`: max queued actions per character.
- `queue_action(char, action_type, skill_key, target)`: validates skill/prereqs/pool cost, appends to queue.
- `pop_action(char)` / `clear_action_queue(char)` / `get_queue_display(char)`.

### `grid.py` — Room grid math
- `ROOM_GRID_SIZES`: tiny(2), small(3), medium(5), large(11), huge(25), massive(51).
- `DIRECTION_OFFSETS`: 8 compass + up/down; +x=east, +y=north, +z=up.
- `get_room_grid_size(room)`, `is_valid_coord(room, x, y)`, `get_entry_coords(room, direction)`.
- `get_exit_at_coord(room, x, y)` / `get_exit_coords(room, exit_obj)`: tile↔exit mapping.
- `grid_quadrant(room, x, y)`: prose phrase for room listings ("the northern portion").
- `get_room_floor_z(room)` / `get_room_max_z(room)`: vertical bounds.

### `movement.py` — Navigation + movement helpers
- `start_navigation(actor, dest_x, dest_y, z, exit_obj, movement_mode)`: sets navigation dict.
- `ensure_combat_loop(room)`: singleton get-or-create for room's CombatLoop.
- `is_grid_occupied(room, x, y, z, ignore)`: blocking objects check.
- `move_actor(actor, x, y, z)`: direct coordinate move (opens collision menu if occupied).
- `announce_grid_move` / `announce_grid_arrival`: realm-gated observer messages.
- `find_nearest_unoccupied_coord(...)`: snap arrivals to free tile.
- `nav_eta(...)`: estimated arrival time.

### `map_renderer.py` — ASCII tactical map
- `render_map(looker)`: draws a `map_size`-wide window centered on the player.
- Symbols: `@` cyan = self, `H` red = hostile, `@` light-cyan = other characters, `+` green = exits, `X` dark-gray = items.
- Used by `where` command and `autowhere` toggle.

### `menus.py` — Collision EvMenu
`collision_menu_node` offers Sit / Ram / Restrain / Abort when moving onto
an occupied tile. All actions are message-only stubs.

### `realm_contest.py` — Realm-shove contests
When a creature manifests or withdraws across realms onto a spot already held
by another creature, both roll an opposed contest (the realm's stat + d10).
The loser is shoved off a claimed seat or a random step. Roll totals are never
revealed. `announce_crossing()` sends unified messages to the actor, occupant,
and bystanders with three perspectives. Fumbles (roll of 1) subtract 10;
exploding tens roll again.

### `queue_mgmt.py` — Manual queue handler
`QueueHandler` with `parse_input` (priority `!` prefix) and `get_next_action`.
Not wired into `CombatLoop` — parallel path for future use.

### `target.py` — Targeting helpers
`get_target_state` / `get_status_descriptor` — placeholder implementations.

### `text_engine.py` — Combat text
Single placeholder `compile_combat_text` function (unused).

## Combat Flow

1. Player types `attack <target>` (or `punch`/`kick`/`haymaker`).
2. `CmdAttack` resolves skill, locates target, calls `queue_action`.
3. `ensure_combat_loop(room)` guarantees the room has a running `CombatLoop`.
4. Loop fires every second: increments round counter, steps navigators, resolves combat.
5. `resolve_tick`: pop action → pay pool cost → verify target → range check → accuracy → damage → armor → apply → broadcast.
6. If pool hits 0: knockout messages (no real unconscious state yet).
7. Regen pass every 60th tick (pose × furniture quality).
8. Loop stops when nobody is navigating, fighting, resting, or below full pools.

## Commands

- `CmdAttack` (`attack`/`punch`/`kick`/`headbutt`/`knee`/`axehandle`/`haymaker`): queue attack action.
- `CmdApproach` (`approach`): navigate toward a target.
- `CmdMove` (`move`): grid movement (coordinates, directions, up/down, stop).
- `CmdShove` (`shove`): push target one tile (handles walls, doors, exits).
- `CmdFly` / `CmdLand`: toggle flight, z-axis movement.
- `CmdWhere` / `CmdWhereKey` / `CmdAutoWhere`: map display.

## Known Limitations

- Knockout is cosmetic only (messages, no unconscious state).
- Combat does not award skill/stat XP (`use_skill()` not called).
- Non-attack actions are silently dropped.
- Armor reads `db.worn`/`db.armor` but nothing sets these yet (Phase 4).
- `target.py` calls undefined `actor.can_see()`/`actor.can_touch()` (would crash).
- `queue_mgmt.py` is not wired into the loop.
