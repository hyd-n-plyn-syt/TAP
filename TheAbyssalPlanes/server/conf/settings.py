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


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
