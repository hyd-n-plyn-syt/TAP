"""
Discord integration for the OOC channel and system announcements.

Sends in-game OOC messages to a Discord channel via webhook, and
receives Discord messages via a bot, relaying them to the OOC channel.
System announcements (server lifecycle, player connections) are sent
to a separate announcements channel via its own webhook.

Configuration lives in settings.py:
    DISCORD_WEBHOOK_URL
    DISCORD_ANNOUNCEMENTS_WEBHOOK_URL
    DISCORD_BOT_TOKEN
    DISCORD_GUILD_ID
    DISCORD_OOC_CHANNEL_ID
    DISCORD_ALLOWED_ROLE_IDS
"""

import datetime
import json
import threading
import urllib.request
import urllib.error

from asgiref.sync import sync_to_async
from django.conf import settings

import evennia


# ── webhook (Evennia → Discord) ────────────────────────────────────────


def _post_webhook(url, payload):
    """POST a JSON payload to *url* in a background thread."""

    def _post():
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


def send_to_discord(message, username="TAP", hex_color=None,
                    url_setting="DISCORD_WEBHOOK_URL"):
    """POST a message to a Discord webhook.  Runs in a thread to avoid
    blocking the Evennia server loop.

    Args:
        message (str): The message text.
        username (str): Sender name for the webhook avatar.
        hex_color (str, optional): Deprecated/no-op; kept for signature
            compatibility.
        url_setting (str): Name of the settings variable holding the
            webhook URL (see world/data/discord.py CHANNEL_RELAYS).
    """
    url = getattr(settings, url_setting, None)
    if not url or not message:
        return

    _post_webhook(url, {"content": message, "username": username})


# ── daily append code block (Evennia → Discord) ───────────────────────

_DAILY_LOCKS = {}
_DAILY_LOCKS_LOCK = threading.Lock()


def _get_daily_lock(relay_setting):
    with _DAILY_LOCKS_LOCK:
        if relay_setting not in _DAILY_LOCKS:
            _DAILY_LOCKS[relay_setting] = threading.Lock()
        return _DAILY_LOCKS[relay_setting]


def _eastern_today():
    # Server location Eastern (UTC-5) – fixed offset, no DST
    from world.data.calendar import eastern_today_str
    return eastern_today_str()


# Backwards compat alias
def _utc_today():
    return _eastern_today()


def _webhook_message_url(webhook_url, message_id):
    base = webhook_url.split("?")[0].rstrip("/")
    return f"{base}/messages/{message_id}"


def _discord_api_request(method, url, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "EvenniaBot/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            status = getattr(resp, "status", 200)
            if body:
                try:
                    return status, json.loads(body.decode("utf-8"))
                except Exception:
                    return status, body.decode("utf-8")
            return status, None
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = str(e)
        evennia.logger.log_err(f"Discord webhook {method} error {e.code}: {err_body} url={url}")
        return e.code, None
    except Exception as err:
        evennia.logger.log_err(f"Discord webhook {method} error: {err} url={url}")
        return None, None


def append_to_discord_log(raw_line, relay_setting):
    """Append a single pipe-coded ``raw_line`` to the per-channel daily
    `````ansi`` code block on Discord.

    Each channel (``ooc`` / ``mudinfo``) gets its own daily block
    (Eastern, UTC-5 date). Messages are concatenated inside a single
    fenced block; on overflow a new block is started for the same day
    (old block left). The webhook username is always ``TAP`` – the sender
    name lives inside the ANSI body with color. Failures restore the
    previous ``ServerConfig`` state and retry via a fresh ``POST`` so no
    line is silently lost.

    Args:
        raw_line (str): Pipe-coded line (e.g. ``|w[|cOOC|n|w]|n Bob: hi``).
        relay_setting (str): Settings key for the webhook URL.
    """
    url = getattr(settings, relay_setting, None)
    if not url or not raw_line:
        return

    def _do():
        lock = _get_daily_lock(relay_setting)
        with lock:
            def _dlog(msg):
                pass
            try:
                from evennia.server.models import ServerConfig
                from world.systems.discord_format import (
                    ansi_body,
                    wrap_ansi_block,
                    unwrap_ansi_block,
                )

                new_body_raw = ansi_body(raw_line).rstrip()
                if not new_body_raw:
                    _dlog("empty new_body_raw, abort")
                    return
                today = _utc_today()
                state_key = f"discord_log_{relay_setting}"
                state = ServerConfig.objects.conf(state_key, default=None)
                _dlog(f"state={state!r} type={type(state).__name__!r} today={today!r} state_date={state.get('date') if hasattr(state, 'get') else 'NA'!r} cmp={state.get('date') != today if hasattr(state, 'get') else 'NA'} not_state={not state} not_dict={not hasattr(state, 'get') if state is not None else 'NA'}")
                # Extra debug: check if state is dict-like (handles _SaverDict)
                try:
                    _dlog(f"isinstance dict={isinstance(state, dict)} type={type(state).__module__}.{type(state).__name__} has_get={hasattr(state, 'get')}")
                except Exception as _e:
                    _dlog(f"isinstance check fail {_e!r}")

                # New day or no state -> create fresh block with date header
                # Use hasattr check to handle Evennia's _SaverDict (not a plain dict)
                if not state or not hasattr(state, "get") or state.get("date") != today:
                    _dlog(f"new-day branch state={state!r}")
                    header_raw = ansi_body(f"|y--- {today} Eastern (UTC-5) ---|n").rstrip()
                    candidate_raw = f"{header_raw}\n{new_body_raw}" if header_raw else new_body_raw
                    fenced = wrap_ansi_block(candidate_raw)
                    if not fenced:
                        _dlog("new-day fenced is None")
                        return
                    wait_url = url + ("&" if "?" in url else "?") + "wait=true"
                    _dlog(f"POST new-day {wait_url} len={len(fenced)}")
                    status, data = _discord_api_request("POST", wait_url, {"content": fenced, "username": "TAP"})
                    _dlog(f"POST new-day status={status} data={str(data)[:300]!r}")
                    if status in (200, 201) and isinstance(data, dict) and data.get("id"):
                        ServerConfig.objects.conf(state_key, {"date": today, "message_id": str(data["id"]), "part": 1})
                        _dlog(f"stored new-day id {data['id']}")
                    else:
                        evennia.logger.log_err(f"Discord daily create failed {status} for {relay_setting} date {today}")
                    return

                # Same day – try to append to existing message
                message_id = state.get("message_id")
                part = state.get("part", 1)
                snapshot = dict(state)
                _dlog(f"same-day append part={part} message_id={message_id}")

                # Fetch existing content for verification
                fetch_url = _webhook_message_url(url, message_id)
                _dlog(f"GET {fetch_url}")
                status, data = _discord_api_request("GET", fetch_url)
                _dlog(f"GET status={status} data keys={list(data.keys()) if isinstance(data, dict) else type(data)} content_len={len(data.get('content','')) if isinstance(data, dict) else 'NA'}")
                old_raw = None
                old_fenced = None
                if status == 200 and isinstance(data, dict) and "content" in data:
                    old_fenced = data["content"]
                    old_raw = unwrap_ansi_block(old_fenced)
                    _dlog(f"unwrap old_raw len={len(old_raw) if old_raw else 'None'} fenced_len={len(old_fenced) if old_fenced else 'None'}")
                    if old_raw is None:
                        evennia.logger.log_err(f"Discord unwrap failed for {relay_setting} message {message_id}, recreating")
                        _dlog("unwrap failed -> recreate")
                        old_raw = None
                else:
                    evennia.logger.log_err(f"Discord fetch failed {status} for {relay_setting} message {message_id}, recreating")
                    _dlog(f"fetch failed status={status} -> recreate")
                    old_raw = None

                if old_raw is not None:
                    candidate_raw = old_raw.rstrip() + "\n" + new_body_raw
                    fenced = wrap_ansi_block(candidate_raw)
                    _dlog(f"candidate len={len(candidate_raw)} fenced len={len(fenced) if fenced else 'None'}")
                    if not fenced:
                        _dlog("fenced is None, abort")
                        return
                    # Overflow → start new block for same day, leave old
                    if len(fenced) > 2000:
                        _dlog(f"overflow len {len(fenced)} >2000, creating new part")
                        cont_header = ansi_body(f"|y--- {today} Eastern (UTC-5) (cont. part {part + 1}) ---|n").rstrip()
                        candidate_raw2 = f"{cont_header}\n{new_body_raw}" if cont_header else new_body_raw
                        fenced2 = wrap_ansi_block(candidate_raw2)
                        if not fenced2:
                            return
                        wait_url = url + ("&" if "?" in url else "?") + "wait=true"
                        status2, data2 = _discord_api_request("POST", wait_url, {"content": fenced2, "username": "TAP"})
                        _dlog(f"overflow POST status={status2} data={data2!r:.300}")
                        if status2 in (200, 201) and isinstance(data2, dict) and data2.get("id"):
                            ServerConfig.objects.conf(state_key, {"date": today, "message_id": str(data2["id"]), "part": part + 1})
                            _dlog(f"overflow stored new id {data2['id']}")
                        else:
                            evennia.logger.log_err(f"Discord overflow POST failed {status2} for {relay_setting}")
                            try:
                                ServerConfig.objects.conf(state_key, snapshot)
                            except Exception:
                                pass
                        return
                    # Try to PATCH existing message
                    patch_url = _webhook_message_url(url, message_id)
                    _dlog(f"PATCH {patch_url} len={len(fenced)}")
                    status_patch, _ = _discord_api_request("PATCH", patch_url, {"content": fenced})
                    _dlog(f"PATCH status={status_patch}")
                    if status_patch in (200, 204):
                        _dlog("PATCH success")
                        return
                    # PATCH failed – restore snapshot and fallback to new POST (retry)
                    evennia.logger.log_err(f"Discord PATCH failed {status_patch} for {relay_setting} message {message_id}, fallback POST")
                    _dlog(f"PATCH failed {status_patch} -> fallback POST")
                    try:
                        ServerConfig.objects.conf(state_key, snapshot)
                    except Exception:
                        pass
                    cont_header = ansi_body(f"|y--- {today} Eastern (UTC-5) (cont. part {part + 1}) ---|n").rstrip()
                    fallback_raw = f"{cont_header}\n{new_body_raw}" if cont_header else new_body_raw
                    fallback_fenced = wrap_ansi_block(fallback_raw)
                    if not fallback_fenced:
                        return
                    wait_url = url + ("&" if "?" in url else "?") + "wait=true"
                    status_f, data_f = _discord_api_request("POST", wait_url, {"content": fallback_fenced, "username": "TAP"})
                    _dlog(f"fallback POST status={status_f} data={data_f!r:.300}")
                    if status_f in (200, 201) and isinstance(data_f, dict) and data_f.get("id"):
                        ServerConfig.objects.conf(state_key, {"date": today, "message_id": str(data_f["id"]), "part": part + 1})
                        _dlog(f"fallback stored new id {data_f['id']}")
                    return
                else:
                    # Fetch failed – recreate fresh block for today (old left orphaned)
                    _dlog("old_raw is None -> recreate fresh block")
                    header_raw = ansi_body(f"|y--- {today} Eastern (UTC-5) ---|n").rstrip()
                    candidate_raw = f"{header_raw}\n{new_body_raw}" if header_raw else new_body_raw
                    fenced = wrap_ansi_block(candidate_raw)
                    if not fenced:
                        return
                    wait_url = url + ("&" if "?" in url else "?") + "wait=true"
                    status2, data2 = _discord_api_request("POST", wait_url, {"content": fenced, "username": "TAP"})
                    _dlog(f"recreate POST status={status2} data={data2!r:.300}")
                    if status2 in (200, 201) and isinstance(data2, dict) and data2.get("id"):
                        ServerConfig.objects.conf(state_key, {"date": today, "message_id": str(data2["id"]), "part": 1})
                    else:
                        evennia.logger.log_err(f"Discord recreate POST failed {status2} for {relay_setting}")
            except Exception as err:
                evennia.logger.log_trace(f"Discord daily append error for {relay_setting}: {err}")
                try:
                    with open(r"D:\TAP\discord_debug.log", "a", encoding="utf-8") as _lf:
                        _lf.write(f"{datetime.datetime.utcnow().isoformat()} [{relay_setting}] EXCEPTION {err!r}\n")
                except Exception:
                    pass

    threading.Thread(target=_do, daemon=True).start()


def send_to_mudinfo(message):
    """Send a message through the MudInfo channel in-game.

    This is the single entry point for system announcements.  The channel's
    ``at_post_msg`` hook relays the message to Discord automatically.
    """
    ch = evennia.search_channel("MudInfo")
    if ch:
        ch[0].msg(message)


def send_announcement(message, username="TAP"):
    """POST a message to the Discord announcements webhook. Runs in a
    thread to avoid blocking the Evennia server loop.

    Args:
        message (str): The message text.
        username (str): Sender name for the webhook avatar.
    """
    url = getattr(settings, "DISCORD_ANNOUNCEMENTS_WEBHOOK_URL", None)
    if not url or not message:
        return
    _post_webhook(url, {"content": message, "username": username})


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
            text = message.content or ""
            # Ignore non-text (attachments already squelched via text-only request)
            if not text.strip():
                try:
                    await message.delete()
                except Exception:
                    pass
                return

            bot_hex = getattr(settings, "DISCORD_BOT_COLOR", "e74c3c")
            role_hex = _discord_role_color(message.author)

            if role_hex:
                display_name = f"|#{role_hex}{display_name}|n"
            tag = f"|#{bot_hex}Discord|n"
            relayed_msg = f"[{tag}] {display_name}: {text}"
            await _send_to_channel(channel, relayed_msg)

            # Squelch original Discord message and mirror into same daily OOC code block
            # (game OOC already appends via channels.py, this makes Discord-origin match)
            # Include [Discord] tag so codeblock shows origin like game does
            try:
                from world.data.calendar import eastern_now

                now = eastern_now()
                ts = f"|m{now.strftime('%H')}|w:|m{now.strftime('%M')}|n"
                ooc_prefix = "|w[|cOOC|n|w]|n"
                discord_line = f"{ts} {ooc_prefix} [{tag}] {display_name}: {text}"
                append_to_discord_log(discord_line, "DISCORD_WEBHOOK_URL")
            except Exception as e:
                evennia.logger.log_err(f"Discord OOC append failed: {e}")
            try:
                await message.delete()
            except discord.Forbidden:
                evennia.logger.log_err(f"Discord delete failed: missing Manage Messages for {message.channel.id}")
            except discord.NotFound:
                pass
            except Exception as e:
                evennia.logger.log_err(f"Discord delete error: {e}")

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
