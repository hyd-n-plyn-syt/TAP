r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "The Abyssal Planes"

# Base class for all stock commands (look, get, exits, etc.). GameMuxCommand
# adds an automatic prompt refresh after every command while preserving the
# MuxCommand argument parsing the defaults rely on.
COMMAND_DEFAULT_CLASS = "commands.command.GameMuxCommand"

# Serve the website/webclient on port 80 so it's reachable at the domain root
# (the router can only open port ranges, so external 80 must hit local 80).
# 80 is the proxy port the Portal presents; 4005 is the internal web port.
WEBSERVER_PORTS = [(80, 4005)]

# Public hostname so the webclient's websocket resolves through the domain.
SERVER_HOSTNAME = "theabyssalplane.duckdns.org"

# New characters are born in the creation area, where a trainer offers the
# first skills. Must be a dbref (Evennia parses it numerically on delete).
DEFAULT_HOME = "#3"

# Run our server start/reload hooks so new changelog entries announce
# themselves to connected players (see world/server_hooks.py).
AT_SERVER_STARTSTOP_MODULE = "world.server_hooks"

######################################################################
# Channels
######################################################################

DEFAULT_CHANNELS = [
    {
        "key": "OOC",
        "aliases": ("ooc",),
        "desc": "Out-of-character discussion",
        "locks": "control:perm(Admin);listen:all();send:all()",
        "typeclass": "typeclasses.channels.Channel",
    },
    {
        "key": "MudInfo",
        "aliases": ("mudinfo",),
        "desc": "Server system messages",
        "locks": "control:perm(Admin);listen:all();send:all()",
        "typeclass": "typeclasses.channels.Channel",
    },
]

# Squelch Evennia's built-in session/connection logs so only custom announcements show
CHANNEL_MUDINFO = None
CHANNEL_CONNECTINFO = None


######################################################################
# Discord Integration
######################################################################

DISCORD_WEBHOOK_URL = (
    "https://discord.com/api/webhooks/"
    "1534640243402342600/"
    "VNoplaL6JMQnBH_orLAr3p9wrvudicXYw132UHIcvt0y1AqSlbxVVlGnIVkDhte6FIiU"
)

DISCORD_BOT_TOKEN = (
    "MTUzNDY0MjYzMjY5OTk0MDg5OA."
    "GfTOhm."
    "NNrXE4clpGbaow84GDNocgpPZ-c5VaTxwFynj0"
)

DISCORD_GUILD_ID = 1534561602924187748
DISCORD_OOC_CHANNEL_ID = 1534638558965665985

DISCORD_ALLOWED_ROLE_IDS = [
    1534635220903395478,  # lead dev
    1534661313538555994,  # dev
    1534635832764268654,  # builder
    1534643991788912760,  # adventurer
]

# Discord role → Truecolor hex for colouring sender names in-game.
# Higher-priority roles listed first; first match wins.
DISCORD_ROLE_COLORS = {
    1534635220903395478: "e67e22",  # lead dev — orange
    1534661313538555994: "e67e22",  # dev — orange
    1534635832764268654: "a84300",  # builder — dark orange
    1534649538671804548: "e74c3c",  # automatons — red (bot colour)
    1534643991788912760: "1abc9c",  # adventurer — teal
}
DISCORD_ROLE_PRIORITY = [
    1534635220903395478,  # lead dev
    1534661313538555994,  # dev
    1534635832764268654,  # builder
    1534643991788912760,  # adventurer
]
DISCORD_BOT_COLOR = "e74c3c"

DISCORD_ANNOUNCEMENTS_WEBHOOK_URL = (
    "https://discord.com/api/webhooks/"
    "1542230754669367336/"
    "-P5k7sjBa5MbplADIoFkxhE3yAAVCKDBNpq7tbfMkm58J6GsSrY57SQ4YHVOquMRa529"
)

# Suppress Evennia's default stock server restart/restarted messages
SERVER_RELOAD_INITIATE_MSG = ""
SERVER_RESTART_MSG = ""


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
