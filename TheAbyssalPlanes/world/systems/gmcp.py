"""
GMCP (Generic MUD Communication Protocol) server module.

Provides functions to send structured data to GMCP-capable clients
like Mudlet. Used for the WHERE map window and communication tabs.

GMCP naming convention:
    client_GUI  -> Client.GUI
    room_map    -> Room.Map
    comm_local  -> Comm.Local
    comm_OOC    -> Comm.OOC
    comm_system -> Comm.System
"""

from evennia.utils.ansi import parse_ansi
from evennia.utils.utils import make_iter

_PACKAGE_URL = "http://theabyssalplane.duckdns.org/static/mudlet/theabyssalplanes.mpackage"


def _gmcp_sessions(entity):
    """Yield sessions on *entity* (account or character) that support GMCP/OOB."""
    for session in make_iter(entity.sessions.all()):
        if session.protocol_flags.get("OOB"):
            yield session


def send_gui_install(entity):
    """
    Send Client.GUI to auto-install the Mudlet package.

    Called on login. Mudlet will download and install the package
    if the user doesn't have it or has an older version.

    Args:
        entity: An Account or Character with connected sessions.
    """
    for session in _gmcp_sessions(entity):
        session.msg(client_GUI={"version": "16", "url": _PACKAGE_URL})


def send_map(character, map_text):
    """
    Send raw ANSI map text to the WHERE window via Room.Map.

    Args:
        character: The character to send to.
        map_text: Raw ANSI output from render_map().
    """
    for session in _gmcp_sessions(character):
        session.msg(room_map={"map": _to_ansi(map_text)})


def _to_ansi(text):
    """Convert Evennia pipe codes to ANSI escapes for direct client rendering."""
    return parse_ansi(str(text), xterm256=True, truecolor=True)


def send_local_comm(character, sender_name, message):
    """
    Send a local communication (say, emote) via Comm.Local.

    Args:
        character: The character to send to.
        sender_name: Name of the sender.
        message: The message text (pipe codes converted to ANSI).
    """
    for session in _gmcp_sessions(character):
        session.msg(comm_local={"sender": sender_name, "message": _to_ansi(message)})


def send_ooc_comm(character, sender_name, message):
    """
    Send an OOC channel message via Comm.OOC.

    Args:
        character: The character to send to.
        sender_name: Name of the sender.
        message: The message text.
    """
    for session in _gmcp_sessions(character):
        session.msg(comm_OOC={"sender": sender_name, "message": _to_ansi(message)})


def send_system(character, message):
    """
    Send a system message (server, changelog) via Comm.System.

    Args:
        character: The character to send to.
        message: The message text.
    """
    for session in _gmcp_sessions(character):
        session.msg(comm_system={"message": _to_ansi(message)})
