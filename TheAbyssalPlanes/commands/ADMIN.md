# ADMIN

Admin-level commands for The Abyssal Planes. Registered in `CharacterCmdSet`
(`commands/default_cmdsets.py`).

## Commands

| Command | Aliases | Lock | Description |
|---------|---------|------|-------------|
| `addchange` | `addchangelog` | `cmd:perm(Admin)` | Append a changelog entry. |
| `removechange` | `removechangelog`, `delchange` | `cmd:perm(Admin)` | Remove a changelog entry by number. |
| `@reload` | `@restart` | `cmd:perm(reload) or perm(Developer)` | Custom server reload with Discord announcement. |

## `addchange`

```
addchange <title> = <body>
```

Appends a new entry to `world/data/changes.py` with the next sequential number
and today's date. Announces the new entry live to all connected players.

The entry is persisted to the Python source file (AST rewrite), so it survives
restarts. The `changes` command picks it up automatically.

## `removechange`

```
removechange <number>
```

Removes the specified entry and renumbers all subsequent entries down by 1.
The file is rewritten automatically.

## `@reload`

Custom reload that:
1. Broadcasts an immediate colored "server is reloading" message to the
   MudInfo channel (Discord relay).
2. Waits 1.2 seconds.
3. Calls `SESSION_HANDLER.portal_restart_server()` (keeps portal/connections alive).

This replaces the default Evennia reload. The stock reload/restart messages
are suppressed in `settings.py`.
