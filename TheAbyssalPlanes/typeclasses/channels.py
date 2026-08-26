"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game.  Channels listed in ``world/data/discord.py``
(CHANNEL_RELAYS) are automatically relayed to their Discord webhook,
with colors translated into ```ansi code blocks so Discord shows the
same styling as the game (white brackets, base-ANSI colored channel
name, perm-colored sender names).
OOC uses cyan (|c), MudInfo uses red (|r), other channels fall back to
white (|w).
"""

import datetime

from django.conf import settings
from evennia.comms.comms import DefaultChannel

from world.data.discord import CHANNEL_RELAYS, RELAY_USERNAME

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
      - ``channel_prefix`` — white brackets (|w) with base-ANSI channel
        name: red (|r) for MudInfo, cyan (|c) for OOC.
    """

    def channel_prefix(self):
        key_lower = self.key.lower()
        if key_lower == "mudinfo":
            col = "|r"
        elif key_lower == "ooc":
            col = "|c"
        else:
            col = "|w"
        return f"|w[{col}{self.key}|n|w]|n "

    def at_post_msg(self, message, **kwargs):
        super().at_post_msg(message, **kwargs)
        senders = kwargs.get("senders", [])
        relayed = kwargs.get("relayed", False)
        if relayed:
            return

        sender = senders[0] if senders else None
        sender_name = sender.key if sender else RELAY_USERNAME

        def line_for(char):
            # mirror DefaultAccount.at_pre_channel_msg (as overridden in
            # typeclasses/accounts.py) so the comm tab shows exactly what
            # the receiver's main window shows - including perm-colored
            # sender names
            if senders:
                sender_string = ", ".join(
                    f"|#{_perm_hex(s)}{s.key}|n" for s in senders
                )
                m = message.lstrip()
                if m.startswith((":", ";")):
                    spacing = "" if m[1:].startswith((":", "'", ",")) else " "
                    body = f"{sender_string}{spacing}{m[1:]}"
                else:
                    body = f"{sender_string}: {message}"
            else:
                body = message
            return f"{self.channel_prefix()}{body}"

        from world.systems.gmcp import send_ooc_comm, send_system
        from evennia import search_object
        all_chars = search_object("", typeclass="typeclasses.characters.Character", exact=False)

        if self.key.lower() == "mudinfo":
            for char in all_chars:
                send_system(char, line_for(None))
        else:
            for char in all_chars:
                send_ooc_comm(char, sender_name, line_for(char))

        relay_setting = CHANNEL_RELAYS.get(self.key.lower())
        if not (relay_setting and getattr(settings, relay_setting, None)):
            return

        from world.discord_integration import append_to_discord_log
        from world.data.calendar import eastern_now

        # Prepend Eastern (UTC-5) timestamp for Discord only (magenta HH/MM, white colon, 24hr 00:00)
        # Bypasses Discord message timestamp since we edit a single codeblock per day
        now = eastern_now()
        ts = f"|m{now.strftime('%H')}|w:|m{now.strftime('%M')}|n"
        discord_line = f"{ts} {line_for(None)}"
        append_to_discord_log(discord_line, relay_setting)
