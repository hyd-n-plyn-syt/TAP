"""Narrative echo formatting: skin-colored pronouns and first-mention names,
matching the emote convention.

A character is introduced by its appearance phrase (whose species name is
already colored by skin tone) the first time it appears in a narrative line;
every later mention collapses to a skin-colored pronoun (he/she/it, his/her,
You), so repeated references stay short and it is always obvious who is being
indicated. Furniture and items are referenced by their material/color tint.
"""

from world.data import colors as colors_data


_DISPLAY_COLOR_FALLBACK = "D"

_PRONOUN_FALLBACK = {
    "subject": "It",
    "object": "it",
    "reflexive": "itself",
    "possessive": "Its",
    "poss_obj": "its",
}


def skin_color(entity):
    """The Truecolor hex code to color this entity's pronouns with, or 'w'."""
    c = getattr(entity, "skin_hex", None)
    return c if c else "w"


def _pronouns(entity):
    pr = getattr(entity, "pronouns", None)
    if pr:
        return pr
    gender = getattr(entity, "gender", None)
    if hasattr(entity, "_PRONOUNS"):
        return entity._PRONOUNS.get(gender, entity._PRONOUNS["neuter"])
    return _PRONOUN_FALLBACK


def colored_pronoun(entity, case="subject", sentence_start=False):
    """A skin-colored pronoun for *entity*: '|#hexHe|n' at sentence start,
    '|#hexhe|n' mid-sentence."""
    c = skin_color(entity)
    word = _pronouns(entity).get(case) or _pronouns(entity)["subject"]
    if case in ("subject", "possessive") and not sentence_start:
        word = word.lower()
    return f"|{c}{word}|n"


def colored_self(entity, sentence_start=False):
    """A skin-colored 'You'/'you' for the receiving viewer."""
    c = skin_color(entity)
    word = "You" if sentence_start else "you"
    return f"|{c}{word}|n"


def colored_poss_self(entity, sentence_start=False):
    """A skin-colored 'Your'/'your' for the receiving viewer."""
    c = skin_color(entity)
    word = "Your" if sentence_start else "your"
    return f"|{c}{word}|n"


def _lower_article(text):
    """Lowercase a leading 'A ' or 'An ' article."""
    if text.startswith("An "):
        return "an " + text[3:]
    if text.startswith("A "):
        return "a " + text[2:]
    return text


def entity_first_ref(entity, sentence_start=True):
    """First-mention name of an entity: its appearance phrase, with the
    article lowered mid-sentence. The species name inside is already colored
    by the character's skin tone."""
    name = getattr(entity, "appearance_name", None) or getattr(entity, "key", "something")
    if not sentence_start:
        name = _lower_article(name)
    return name


def narrate_refs():
    """Return a per-message reference dispatcher.

    ``ref(entity, case='subject', sentence_start=False)`` returns the
    appearance name the first time an entity is mentioned and a skin-colored
    pronoun on every later mention. One dispatcher is created per recipient
    so each line is rendered from that viewer's perspective.
    """
    seen = set()

    def ref(entity, case="subject", sentence_start=False):
        eid = id(entity)
        if eid not in seen:
            seen.add(eid)
            return entity_first_ref(entity, sentence_start)
        return colored_pronoun(entity, case=case, sentence_start=sentence_start)

    return ref


def display_color(obj):
    """The bare color-code for an object's narrative name: its first
    material's truecolor, its stored color code, or the dark-gray fallback.
    Returned WITHOUT a leading pipe so callers wrap it in ``|{code}...|n``."""
    materials = getattr(obj, "materials", None)
    if materials:
        entry = materials[0]
        if isinstance(entry, (list, tuple)) and len(entry) > 1:
            col_key = entry[1]
        else:
            col_key = entry
        hexcol = colors_data.hex_for_color(col_key)
        if hexcol:
            return hexcol
    color = getattr(obj, "color", None)
    if color:
        return color.lstrip("|") if color.startswith("|") else color
    return _DISPLAY_COLOR_FALLBACK


def _color_object_name(text, obj):
    """Wrap the noun (not the article) of a display name in the object's
    color, e.g. 'an |Doak table|n'."""
    low = text.lower()
    for art in ("an ", "a "):
        if low.startswith(art):
            return f"{text[:len(art)]}|{display_color(obj)}{text[len(art):]}|n"
    return f"|{display_color(obj)}{text}|n"


def narrative_name(obj, sentence_start=False):
    """A narrative display name: furniture and items are tinted by their
    material/color; anything else uses its plain display name."""
    if obj.is_typeclass("typeclasses.furniture.Furniture"):
        return _color_object_name(obj.get_display_name(), obj)
    return obj.get_display_name()


furniture_name = narrative_name