"""
Discord integration for the OOC channel.

Sends in-game OOC messages to a Discord channel via webhook, and
receives Discord messages via a bot, relaying them to the OOC channel.

Configuration lives in settings.py:
    DISCORD_WEBHOOK_URL
    DISCORD_BOT_TOKEN
    DISCORD_GUILD_ID
    DISCORD_OOC_CHANNEL_ID
    DISCORD_ALLOWED_ROLE_IDS
"""

import json
import threading
import urllib.request
import urllib.error

from asgiref.sync import sync_to_async
from django.conf import settings

import evennia


# ── webhook (Evennia → Discord) ────────────────────────────────────────


def send_to_discord(message, username="Server", hex_color=None):
    """POST a message to the Discord webhook.  Runs in a thread to avoid
    blocking the Evennia server loop.

    Args:
        message (str): The message text.
        username (str): Sender name for the webhook avatar.
        hex_color (str, optional): 6-digit hex colour for the embed sidebar.
    """
    url = getattr(settings, "DISCORD_WEBHOOK_URL", None)
    if not url:
        return

    def _post():
        payload = {
            "content": message,
            "username": username,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EvenniaBot/1.0",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except Exception as err:
            evennia.logger.log_err(f"Discord webhook error: {err}")

    threading.Thread(target=_post, daemon=True).start()


# ── bot (Discord → Evennia) ────────────────────────────────────────────

_bot_thread = None
_bot_loop = None
_bot_client = None


def _get_allowed_role_ids():
    return set(getattr(settings, "DISCORD_ALLOWED_ROLE_IDS", []))


def start_discord_bot():
    """Start the Discord bot in a background thread."""
    global _bot_thread, _bot_loop, _bot_client

    token = getattr(settings, "DISCORD_BOT_TOKEN", None)
    if not token:
        return

    import asyncio
    import discord

    allowed_roles = _get_allowed_role_ids()
    guild_id = getattr(settings, "DISCORD_GUILD_ID", None)
    ooc_channel_id = getattr(settings, "DISCORD_OOC_CHANNEL_ID", None)

    @sync_to_async
    def _find_channel(name):
        result = evennia.search_channel(name)
        return result[0] if result else None

    @sync_to_async
    def _send_to_channel(channel, msg):
        channel.msg(msg, senders=None, relayed=True)

    def _discord_role_color(member):
        """Return the Truecolor hex for a Discord member's highest matching role."""
        colors = getattr(settings, "DISCORD_ROLE_COLORS", {})
        priority = getattr(settings, "DISCORD_ROLE_PRIORITY", [])
        member_ids = {r.id for r in member.roles}
        for rid in priority:
            if rid in member_ids:
                return colors.get(rid, None)
        return None

    class OOCBot(discord.Client):
        def __init__(self):
            intents = discord.Intents.default()
            intents.message_content = True
            super().__init__(intents=intents)

        async def on_ready(self):
            evennia.logger.log_msg(f"Discord bot connected as {self.user}")
            for guild in self.guilds:
                evennia.logger.log_msg(f"  Guild: {guild.name} (id={guild.id})")

        async def on_message(self, message):
            if message.author == self.user:
                return
            if message.guild and message.guild.id != guild_id:
                return
            if message.channel.id != ooc_channel_id:
                return

            author_roles = {r.id for r in getattr(message.author, "roles", [])}
            if not author_roles & allowed_roles:
                evennia.logger.log_msg(f"Discord: {message.author} lacks allowed roles")
                return

            channel = await _find_channel("OOC")
            if not channel:
                evennia.logger.log_err("Discord: could not find OOC channel")
                return

            display_name = message.author.display_name
            text = message.content

            bot_hex = getattr(settings, "DISCORD_BOT_COLOR", "e74c3c")
            role_hex = _discord_role_color(message.author)

            if role_hex:
                display_name = f"|#{role_hex}{display_name}|n"
            tag = f"|#{bot_hex}Discord|n"
            relayed_msg = f"[{tag}] {display_name}: {text}"
            await _send_to_channel(channel, relayed_msg)

    def _run_bot():
        global _bot_loop, _bot_client
        _bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_bot_loop)
        _bot_client = OOCBot()
        _bot_client.run(token)

    _bot_thread = threading.Thread(target=_run_bot, daemon=True)
    _bot_thread.start()


def stop_discord_bot():
    """Gracefully close the Discord bot connection."""
    global _bot_client
    if _bot_client and not _bot_client.is_closed():
        import asyncio
        future = asyncio.run_coroutine_threadsafe(_bot_client.close(), _bot_loop)
        try:
            future.result(timeout=5)
        except Exception:
            pass
