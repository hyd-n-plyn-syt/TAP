# The Abyssal Planes — Game Directory

This is the Evennia game directory for The Abyssal Planes. It contains all
game-specific code, data, and configuration. The Evennia framework itself
lives in `../evenv/`.

## Quick Start

```powershell
cd D:\TAP\TheAbyssalPlanes
& ..\evenv\Scripts\evennia.exe start
```

Connect via telnet `localhost:4000` or webclient `http://localhost`.

## Directory Structure

```
TheAbyssalPlanes/
├── combat/           Combat engine (loop, accuracy, damage, grid, movement, menus)
├── commands/         All commands
│   ├── account/      charcreate, mychars, chargen EvMenu
│   ├── admin/        addchange, removechange, reload
│   ├── building/     dig, digmenu, attset, setskill, force, createfurniture, etc.
│   ├── crafting/     (empty placeholder for future crafting commands)
│   ├── player/       skills, train, score, movement, combat, poses, doors, etc.
│   ├── skills/       (empty placeholder)
│   ├── tests/        Command integration tests
│   └── vim/          (empty placeholder)
├── server/
│   ├── conf/
│   │   ├── settings.py       Main config (COMMAND_DEFAULT_CLASS, Discord, channels)
│   │   └── secret_settings.py (gitignored) Sensitive tokens
│   └── logs/         Server logs
├── typeclasses/      Object, Character, Room, Exit, Furniture, Item, Account
├── web/              Website/webclient overrides (stock Evennia, no custom changes)
└── world/
    ├── data/         Pure-data rosters (skills, species, appearance, calendar, etc.)
    ├── systems/      Logic modules (stats, skills, growth, group, hostility)
    ├── planets/      Planet-specific zone content (placeholder)
    ├── tests/        Data/systems unit tests + mock
    ├── discord_integration.py  Discord ↔ game bridge
    ├── help_entries.py         25 file-based help topics
    └── server_hooks.py         Server start/stop/reload hooks
```

## Key Entry Points

- **Settings:** `server/conf/settings.py` — all Evennia config (command class, home, Discord, channels).
- **Command registration:** `commands/default_cmdsets.py` — every custom command is wired here.
- **Typeclasses:** `typeclasses/` — all entity behavior (Character, Room, Exit, Furniture, Item).
- **Data:** `world/data/` — pure-data modules (no Evennia imports) for skills, species, appearance, calendar.
- **Systems:** `world/systems/` — logic modules for stats, skills, growth.
- **Combat:** `combat/` — standalone package for the tick-based combat engine.
- **Tests:** `world/tests/` and `commands/tests/` — test suites run via `evennia test`.

## Running Tests

```powershell
# Full suite
& ..\evenv\Scripts\evennia.exe test --settings settings.py .

# World data/systems only
& ..\evenv\Scripts\evennia.exe test --settings settings.py world.tests

# Command integration only
& ..\evenv\Scripts\evennia.exe test --settings settings.py commands.tests
```

## Documentation

- [`../README.md`](../README.md) — GitHub front page (systems overview).
- [`../GAMEPLAN.md`](../GAMEPLAN.md) — Living design + build-order doc.
- [`../DEVELOPMENT.md`](../DEVELOPMENT.md) — Full technical reference.
- [`../SETUP.md`](../SETUP.md) — Environment bootstrap guide.
