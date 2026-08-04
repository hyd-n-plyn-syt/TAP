"""
Server start/stop hooks.

Registered via ``AT_SERVER_STARTSTOP_MODULE`` in settings so that every
start and reload announces newly added changes to connected players (the
on-login alert in ``typeclasses/accounts.py`` covers everyone else). The
builder 'addchange' command calls ``announce_new()`` directly so an entry
is broadcast the moment it is written.
"""

import evennia
from evennia.server.models import ServerConfig

from world.data import changes


def _broadcast_newest():
    """Broadcast the newest change to connected players once per release."""
    latest = changes.latest_number()
    if not latest:
        return
    announced = ServerConfig.objects.conf("changes_announced", default=0)
    if announced >= latest:
        return
    entry = changes.get_change(latest)
    evennia.SESSION_HANDLER.announce_all(
        f"|y*** New change: #{entry['number']} |w{entry['title']}|n|n\n"
        f"Type |wchanges|n to read what's new."
    )
    ServerConfig.objects.conf("changes_announced", latest)


def announce_new():
    """Announce the newest unannounced change; never raises."""
    try:
        _broadcast_newest()
    except Exception as err:  # keep a failure from taking the server down
        evennia.logger.log_trace(f"Error announcing changes: {err}")


def at_server_start():
    """Called on every server startup (cold, reload, reset)."""
    announce_new()


def at_server_reload_start():
    """Called when a reload begins."""
    announce_new()