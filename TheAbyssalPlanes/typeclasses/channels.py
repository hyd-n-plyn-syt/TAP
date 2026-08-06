"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game.  The OOC channel overrides at_post_msg to relay
outgoing messages to Discord via webhook.  The channel name is always
shown in white (|w).
"""

from evennia.comms.comms import DefaultChannel
from evennia.utils.ansi import strip_ansi

from world.discord_integration import send_announcement, send_to_discord

import evennia


def _perm_hex(account):
    """Return a Truecolor hex string for *account* based on permission level."""
    if account.is_superuser:
        return "e67e22"
    perms = account.permissions.all()
    if "developer" in perms:
        return "e67e22"
    if "builder" in perms:
        return "a84300"
    return "1abc9c"


class Channel(DefaultChannel):
    r"""
    Base channel class.  The OOC channel adds Discord relay.

    Overrides:
      - ``channel_prefix`` — channel name is always |w (white).
    """

    def channel_prefix(self):
        return f"[|w{self.key}|n] "

    def at_post_msg(self, message, **kwargs):
        super().at_post_msg(message, **kwargs)
        senders = kwargs.get("senders", [])
        relayed = kwargs.get("relayed", False)
        if relayed:
            return
        clean = strip_ansi(message).strip()
        if self.key.lower() == "mudinfo":
            send_announcement(clean)
        else:
            sender = senders[0] if senders else None
            sender_name = sender.key if sender else "Server"
            hex_color = _perm_hex(sender) if sender else None
            send_to_discord(clean, username=sender_name, hex_color=hex_color)
