# ACCOUNT

Account-level commands for The Abyssal Planes. Run from the OOC screen.
Registered in `AccountCmdSet` (`commands/default_cmdsets.py`).

## Commands

| Command | Aliases | Lock | Description |
|---------|---------|------|-------------|
| `charcreate` | — | `cmd:pperm(Player)` | Override of stock Evennia charcreate. Starts the EvMenu guided creation flow. |
| `mychars` | `characters`, `chars` | `cmd:pperm(Player)` | List all characters on the account with their species. |
| `mapsize` | `ms` | `cmd:all()` | Display or set the tactical map viewport width (3–25). Stored on account (`map_size`). |

## Chargen Flow

`charcreate <name>` walks through:
1. Gender (male/female/neuter)
2. Species (with `?N` help for each)
3. Height (diminutive → towering)
4. Build (validated against height)
5. Adjective (species-specific)
6. Skin tone (species palette with hex display)
7. Eye shape (species-specific)
8. Eye colour (species palette)
9. Hair style (species-specific)
10. Hair colour (species palette)
11. Stat priorities (locked column awareness)
12. Per-stat point distribution (sums to priority points)
13. Review → Confirm

On finalize:
- Creates the character via `account.create_character`
- Applies all appearance attributes
- Applies species (visarial nature, stat bonuses, locks, zeroed pools)
- Sets stat distribution (category="stat" sub-stats)
- Stores `stat_priorities`
- Tells the player to `ic <name>`

## Removed Default Commands

The `ooc` command is removed from `AccountCmdSet` (it was redundant).
