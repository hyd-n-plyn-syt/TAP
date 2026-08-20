"""Narrative echo formatting: skin-colored pronouns and first-mention names,
matching the emote convention.

A character is introduced by its appearance phrase (whose species name is
already colored by skin tone) the first time it appears in a narrative line;
every later mention collapses to a skin-colored pronoun (he/she/it, his/her,
You), so repeated references stay short and it is always obvious who is being
indicated.
"""

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