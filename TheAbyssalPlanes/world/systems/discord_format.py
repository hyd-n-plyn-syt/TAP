"""
Translate Evennia color-coded text into Discord ``ansi` code blocks.

Evennia's own fallback machinery does the heavy lifting: feeding a
pipe-coded string through ``ANSI_PARSER.parse_ansi`` with
``xterm256=False, truecolor=False`` downgrades every Truecolor/XTERM256
tag to plain ANSI escapes. Those are then clamped to the original 8
ANSI foreground/background colors (30-37 / 40-47) plus reset/underline,
with the bold/hilite layer (1 / 22) stripped entirely — Discord's
renderer otherwise just makes the text bold, which looks poor. The
result still mirrors what an ANSI-only MUD client sees, while keeping
the 8-color palette where gray (30) and white (37) are distinct codes.
"""

import re

from evennia.utils.ansi import ANSI_PARSER

DISCORD_MAX_LEN = 2000

_ANSI_SEQ = re.compile(r"\033\[([0-9;]*)m")

_ALLOWED_CODES = {"", "0", "4"}
for _n in range(30, 38):
    _ALLOWED_CODES.add(str(_n))
    _ALLOWED_CODES.add(str(_n + 10))

# Bright ANSI 90-97 / 100-107 fall back to the base 8 (30-37 / 40-47)
# so gray (30) and white (37) stay distinct codes within the 8-color set.
_BRIGHT_TO_BASE = {str(n): str(n - 60) for n in range(90, 98)}
_BRIGHT_TO_BASE.update({str(n): str(n - 60) for n in range(100, 108)})

# Bold/hilite are stripped; they only affect weight on Discord.
_STRIP_CODES = {"1", "22"}


def _sanitize_sequences(text):
    """Clamp ANSI escape sequences to Discord's supported 8-color subset."""

    def _replace(m):
        raw = m.group(1)
        if raw in _STRIP_CODES:
            return ""
        if raw in _ALLOWED_CODES:
            return m.group(0)
        if raw in _BRIGHT_TO_BASE:
            return f"\033[{_BRIGHT_TO_BASE[raw]}m"
        # Compound sequence like "1;31" or "0;37" — split and filter.
        if ";" in raw:
            parts = []
            for p in raw.split(";"):
                if p in _STRIP_CODES or p == "":
                    continue
                if p in _BRIGHT_TO_BASE:
                    p = _BRIGHT_TO_BASE[p]
                if p in _ALLOWED_CODES:
                    parts.append(p)
            if not parts:
                return ""
            return f"\033[{';'.join(parts)}m"
        return ""

    return _ANSI_SEQ.sub(_replace, text)


def _escape_backticks(text):
    """Neutralize backtick runs so the payload cannot break out of the
    fenced code block."""
    return re.sub(r"`+", "'", text)


def ansi_body(text):
    """Return the sanitized, escape-coded body for a Discord ``ansi``
    block from an Evennia pipe-coded string.

    Args:
        text (str): Evennia pipe/ANSI-coded message.

    Returns:
        str: Text containing literal ESC sequences (no fences).
    """
    parsed = ANSI_PARSER.parse_ansi(text, strip_ansi=False, xterm256=False, mxp=False, truecolor=False)
    return _sanitize_sequences(_escape_backticks(parsed))


_BG = "\033[40m"


def wrap_ansi_block(body):
    """Wrap a sanitized ANSI body (from :func:`ansi_body`) into a Discord
    `````ansi`` fenced block with constant background.

    The body is expected to be the raw ``ansi_body`` output (no fences,
    no background). This function adds the Discord-only ``40`` background
    (blueish-black) and re-applies it after each reset so it persists
    across color changes, then fences and truncates to ``DISCORD_MAX_LEN``.

    Args:
        body (str): Sanitized ANSI body.

    Returns:
        str | None: Fenced block or None if body is empty.
    """
    body = body.rstrip() if body else ""
    if not body:
        return None
    if "\033[0m" in body:
        body = body.replace("\033[0m", f"\033[0m{_BG}")
    if not body.startswith(_BG):
        body = _BG + body
    wrapper = len("```ansi\n\n```")
    budget = DISCORD_MAX_LEN - wrapper - 1
    if len(body) > budget:
        body = body[:budget].rstrip() + "…"
    return f"```ansi\n{body}\n```"


def unwrap_ansi_block(fenced):
    """Reverse :func:`wrap_ansi_block` – extract raw body.

    Strips the `````ansi`` fences and the Discord-only background so the
    result can be concatenated with new ``ansi_body`` output and re-wrapped.

    Args:
        fenced (str): Fenced block as returned by :func:`wrap_ansi_block`
            or :func:`to_discord_ansi`.

    Returns:
        str | None: Raw body (no fences, no ``40`` background) or None if
            parsing fails.
    """
    if not fenced or not fenced.startswith("```ansi\n") or not fenced.endswith("\n```"):
        return None
    inner = fenced[len("```ansi\n"):-len("\n```")]
    # Remove the constant background that was added by wrap_ansi_block
    # so concatenation doesn't double-apply it.
    if inner.startswith(_BG):
        inner = inner[len(_BG):]
    # Reverse the ``0m``+BG re-application
    inner = inner.replace(f"\033[0m{_BG}", "\033[0m")
    return inner


def to_discord_ansi(text):
    """Convert an Evennia pipe-coded string into a complete Discord
    `````ansi`` fenced block, truncated to fit Discord's message limit.

    A constant black (blueish-black) background (40) is prepended for
    Discord only - the in-game display keeps its default background.
    The background is re-applied after each reset so it persists across
    color changes, emulating the terminal look.

    Returns None if there is nothing to send after conversion.
    """
    body = ansi_body(text).rstrip()
    if not body:
        return None
    return wrap_ansi_block(body)
