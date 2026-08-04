"""
Server start/stop hooks.

Registered via ``AT_SERVER_STARTSTOP_MODULE`` in settings so that every
start and reload announces newly added changes to connected players (the
on-login alert in ``typeclasses/accounts.py`` covers everyone else).
"""

import evennia
from evennia.server.models import ServerConfig

from world.data import changes


def _announce_new():
    """Broadcast the newest change to connected players once per release."""
    latest = changes.latest_number()
    if not latest:
        return
    announced = ServerConfig.objects.conf("changes_announced", default=0)
    if announced >= latest:
        return
    entry = changes.get_change(latest)
    evennia.SESSION_HANDLER.announce_all(
        f"|y*** New change: #{entry['number']} |w{entry['title']}|n|n"
        f"Type |wchanges|n to read what's new."
    )
    ServerConfig.objects.conf("changes_announced", latest)


def _announce():
    try:
        _announce_new()
    except Exception as err:  # never let a startup hook take the server down
        evennia.logger.log_trace(f"Error announcing changes: {err}")


def at_server_start():
    """Called on every server startup (cold, reload, reset)."""
    _announce()


def at_server_reload_start():
    """Called when a reload begins."""
    _announce()