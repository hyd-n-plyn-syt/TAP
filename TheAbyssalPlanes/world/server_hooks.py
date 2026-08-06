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
from world.discord_integration import (
    send_to_mudinfo,
    start_discord_bot,
    stop_discord_bot,
    connect_signals,
)


def _broadcast_newest():
    """Broadcast the newest change to connected players once per release."""
    latest = changes.latest_number()
    if not latest:
        return
    announced = ServerConfig.objects.conf("changes_announced", default=0)
    if announced >= latest:
        return
    entry = changes.get_change(latest)
    send_to_mudinfo(
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
    try:
        start_discord_bot()
    except Exception as err:
        evennia.logger.log_trace(f"Error starting Discord bot: {err}")
    try:
        connect_signals()
        send_to_mudinfo("Server started")
    except Exception as err:
        evennia.logger.log_trace(f"Error sending startup announcement: {err}")


def at_server_reload_start():
    """Called when a reload begins."""
    announce_new()


def at_server_stop():
    """Called on server shutdown."""
    try:
        send_to_mudinfo("Server shutting down")
    except Exception as err:
        evennia.logger.log_trace(f"Error sending shutdown announcement: {err}")
    try:
        stop_discord_bot()
    except Exception as err:
        evennia.logger.log_trace(f"Error stopping Discord bot: {err}")