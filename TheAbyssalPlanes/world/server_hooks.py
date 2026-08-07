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


def connect_account_signals():
    """Connect account creation signal to auto-subscribe new accounts to MudInfo."""
    try:
        from evennia.server.signals import SIGNAL_ACCOUNT_POST_CREATE
        from evennia import ChannelDB

        def _on_account_create(sender, **kwargs):
            mudinfo = ChannelDB.objects.get_channel("MudInfo") or ChannelDB.objects.get_channel("mudinfo")
            if mudinfo and not mudinfo.has_connection(sender):
                mudinfo.connect(sender)

        SIGNAL_ACCOUNT_POST_CREATE.connect(_on_account_create, sender=None)
    except Exception as err:
        evennia.logger.log_trace(f"Error connecting account create signal: {err}")


import threading


def at_server_start():
    """Called on every server startup (cold, reload, reset)."""
    try:
        start_discord_bot()
    except Exception as err:
        evennia.logger.log_trace(f"Error starting Discord bot: {err}")
    try:
        connect_account_signals()
    except Exception as err:
        evennia.logger.log_trace(f"Error connecting account signals: {err}")
    try:
        from evennia import AccountDB, ChannelDB
        mudinfo = ChannelDB.objects.get_channel("MudInfo") or ChannelDB.objects.get_channel("mudinfo")
        if mudinfo:
            for acct in AccountDB.objects.all():
                if not mudinfo.has_connection(acct):
                    mudinfo.connect(acct)
    except Exception as err:
        evennia.logger.log_trace(f"Error auto-subscribing accounts to MudInfo: {err}")

    def _delayed_announce():
        try:
            send_to_mudinfo("|000**|105The server has s|104t|103a|102r|103t|104e|105d|100!|000**|n")
            announce_new()
        except Exception as err:
            evennia.logger.log_trace(f"Error sending startup announcement: {err}")

    threading.Timer(2.0, _delayed_announce).start()


def at_server_reload_start():
    """Called when a reload begins."""
    try:
        stop_discord_bot()
    except Exception as err:
        evennia.logger.log_trace(f"Error stopping Discord bot: {err}")


def at_server_stop():
    """Called on server shutdown."""
    try:
        send_to_mudinfo("|000**|105The server is s|104h|103ut|102t|101in|102g d|103o|104w|105n|100.|000**|n")
        import time
        time.sleep(0.3)
    except Exception as err:
        evennia.logger.log_trace(f"Error sending shutdown announcement: {err}")
    try:
        stop_discord_bot()
    except Exception as err:
        evennia.logger.log_trace(f"Error stopping Discord bot: {err}")