"""
Discord relay configuration.

CHANNEL_RELAYS maps an in-game channel key (lowercase) to the name of
the settings variable holding that channel's Discord webhook URL.
Any channel listed here is relayed to Discord automatically by
typeclasses/channels.py; messages are translated into ```ansi code
blocks via world/systems/discord_format.py so in-game colors survive.

To add a new relayed channel:
    1. Add its webhook to server/conf/settings.py, e.g.
           DISCORD_GRUNT_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
    2. Add an entry below:
           "grunt": "DISCORD_GRUNT_WEBHOOK_URL",
Channels without an entry (or whose setting is missing/blank) simply
do not relay.

RELAY_USERNAME is the fallback webhook username when a message has no
identifiable sender.
"""

CHANNEL_RELAYS = {
    "ooc": "DISCORD_WEBHOOK_URL",
    "mudinfo": "DISCORD_ANNOUNCEMENTS_WEBHOOK_URL",
}

RELAY_USERNAME = "TAP"
