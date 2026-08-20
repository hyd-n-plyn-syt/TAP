# server/

Evennia server configuration and runtime files for The Abyssal Planes.

## Structure

```
server/
├── conf/
│   ├── settings.py           Main configuration
│   └── secret_settings.py    Sensitive tokens (gitignored)
├── logs/
│   ├── server.log            Game Server log
│   ├── portal.log            Portal proxy log (internet-facing)
│   ├── lockwarnings.log      Lock system warnings
│   ├── http_requests.log     HTTP request log (usually empty)
│   └── channel_*.log         Per-channel message logs
├── evennia.db3               Live SQLite database (the entire game state)
├── server.pid / portal.pid   Process IDs (managed by launcher)
└── server.restart / portal.restart  Restart flags (managed by launcher)
```

## `conf/settings.py`

The main configuration file. Key customizations:

- `SERVERNAME = "The Abyssal Planes"`
- `COMMAND_DEFAULT_CLASS = "commands.command.GameMuxCommand"` — auto-refreshes prompt after every command.
- `DEFAULT_HOME = "#3"` — new characters spawn at Center of Creation (must be a dbref).
- `WEBSERVER_PORTS = [(80, 4005)]` — web on port 80.
- `SERVER_HOSTNAME = "theabyssalplane.duckdns.org"` — websocket resolution.
- `AT_SERVER_STARTSTOP_MODULE = "world.server_hooks"` — server lifecycle hooks.
- `DEFAULT_CHANNELS` — OOC + MudInfo channels with custom typeclass.
- `CHANNEL_MUDINFO = None` / `CHANNEL_CONNECTINFO = None` — squelch stock logs.
- Discord integration: `DISCORD_WEBHOOK_URL`, `DISCORD_BOT_TOKEN`, `DISCORD_GUILD_ID`, etc.
- `SERVER_RELOAD_INITIATE_MSG = ""` / `SERVER_RESTART_MSG = ""` — suppress stock messages.

## `conf/secret_settings.py`

Gitignored file for sensitive values (webhook tokens, bot tokens). Imported
at the end of `settings.py` via `try: from server.conf.secret_settings import *`.

## `logs/`

Log files created by the running server. Viewed with `evennia --log`.
Rotated weekly. Older logs have `_month_date` appended.

## `evennia.db3`

The SQLite database holding the entire game state (characters, objects, rooms,
accounts, attributes, tags). Deleting this file resets the game; run
`evennia migrate` to rebuild the schema.

## Gotcha

`DEFAULT_HOME` must be a dbref (e.g. `"#3"`), NOT a name. Evennia's
`clear_contents()` calls `int(settings.DEFAULT_HOME.lstrip("#"))` on every
object delete.
