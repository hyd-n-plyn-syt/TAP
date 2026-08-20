# typeclasses/

Typeclasses define the behavior of all game entities in The Abyssal Planes.
Every in-game object, character, room, exit, piece of furniture, item,
account, and channel has a corresponding typeclass.

## Files

### `objects.py` — `ObjectParent` mixin
Applied to every entity type. Defines the shared visarial model and tactical
spatial attributes. Key methods:
- `nature()` / `state()` — read visarial nature/state.
- `current_plane()` — resolve physical/visarial from nature+state.
- `is_creature`, `can_perceive`, `can_manifest` — creature-only properties.
- `can_phys_see` / `can_vis_see` / `can_phys_touch` / `can_vis_touch` — per-entity visibility flags.
- `can_speak_phys` / `can_speak_vis` / `can_hear_phys` / `can_hear_vis` — speech/hearing flags.
- `visible_to(looker)` — plane overlap test.
- `set_nature(nature)` — validate and set visarial nature.
- `get_search_candidates(...)` — plane-filtered search (Builder bypass).
- `get_display_desc(looker)` — merged base + visarial description.
- `get_search_result(...)` — fallback to appearance_paragraph matching.
- `handle_search_results(...)` — custom multimatch display names.

### `characters.py` — `Character`
778 lines. The most complex typeclass. Stores:
- 9 sub-stats (AttributeProperties, category="stat").
- Identity/flavor: species_key, appearance_height/build/adjective/skin/eyes/eye_color/hair/hair_color, pose, sign, birth_date.
- Combat: combat_target, friendly_target, action_queue, navigation, pos_x/y/z, is_flying, can_fly, etc.
- Growth: skills, skills_xp, stat_xp (category="growth").
- Pool tracking: vigor_current, vim_current, mens_current.

Key methods: `apply_species()`, `clear_species()`, `set_state()`, `set_pool()`,
`reset_pools()`, `set_appearance()`, `set_pose()`, `at_post_move()` (grid
stamping), `use_skill()`, `at_say()` (realm-aware), `get_display_name()`,
`appearance_paragraph()`, `get_prompt()`, `return_appearance()`.

### `rooms.py` — `Room`
468 lines. Grid-aware rooms with two-tier coordinate tags.
Key methods: `return_appearance()` (grid neighbor scanning + clockwise exit
rendering), `get_display_exits()` (clockwise sort + door status), 
`_grouped_room_contents()` (plane-grouped occupancy), `_things_list()`.

### `exits.py` — `Exit`
371 lines. Door mechanics: `at_traverse()` (grid-aware, autoopen),
`open_door()`/`close_door()`/`lock_door()`/`unlock_door()`, sibling sync,
`filter_visible()` (hidden exits), `_has_key()`.

### `furniture.py` — `Furniture`
236 lines. Grid-aware furniture with facing, dimensions, seats, approach_hint,
rotate, calculate_footprint. Auto-places on drop, auto-sits characters.
Color attribute defaults to bare ANSI code (`"D"` for dark-gray); materials
provide Truecolor hexes via `display_color()` in `world/systems/narrative.py`.

### `items.py` — `Item`
61 lines. Extends Furniture with multi-material Truecolor display names.

### `accounts.py` — `Account`
211 lines. `changes_seen` for changelog, Discord relay on login/disconnect,
permission-based channel colors, character slot limits.

### `channels.py` — `Channel`
54 lines. Discord relay via `at_post_msg`, white `[Channel]` prefix.

### `scripts.py` — `Script`
Stock Evennia, no customization.

## Pattern: ObjectParent Mixin

All entity types inherit from `ObjectParent` plus their Evennia default:
```python
class Character(ObjectParent, DefaultCharacter): ...
class Room(ObjectParent, DefaultRoom): ...
class Exit(ObjectParent, DefaultExit): ...
class Furniture(ObjectParent, DefaultObject): ...
```

This keeps the visarial model and tactical grid code in one place while
extending Evennia's built-in behavior.

## Modifying Behavior

To change how an entity type works:
1. Edit the corresponding file in `typeclasses/`.
2. The change applies immediately after `evennia reload`.
3. For new stored attributes, add an `AttributeProperty` to the class or
   set it in `at_object_creation`.
4. For new tags, set them in `at_object_creation` with a category.
