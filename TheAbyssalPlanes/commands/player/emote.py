import re

from commands.command import GameMuxCommand


def split_quoted_segments(text):
    segments = []
    in_quote = False
    current = ""
    for char in text:
        if char == '"':
            if in_quote:
                segments.append((True, current))
                current = ""
                in_quote = False
            else:
                if current:
                    segments.append((False, current))
                current = ""
                in_quote = True
        else:
            current += char
    if current:
        segments.append((in_quote, current))
    return segments


SELF_WORDS = ("me", "self")
MY_WORDS = ("my",)


def _count_self_refs(segments):
    counts = {"me": 0, "my": 0}
    for is_quoted, segment in segments:
        if is_quoted:
            continue
        for match in re.finditer(r"@(\w+)", segment):
            word = match.group(1).lower()
            if word in SELF_WORDS:
                counts["me"] += 1
            elif word in MY_WORDS:
                counts["my"] += 1
    return counts


def parse_emote_targets(segments, caller):
    seen_words = []
    for is_quoted, segment in segments:
        if is_quoted:
            continue
        for match in re.finditer(r"@(\w+)", segment):
            word = match.group(1)
            if word not in seen_words:
                seen_words.append(word)

    if not seen_words:
        return {}, segments, {"me": 0, "my": 0}

    self_ref_counts = _count_self_refs(segments)

    targets = {}
    for word in seen_words:
        if word.lower() in SELF_WORDS or word.lower() in MY_WORDS:
            continue

        results = _resolve_target(word, caller)
        if not results:
            caller.msg(f"No one matching '@{word}' here.")
            return None, None, None
        targets[word] = results

    cleaned_segments = []
    for is_quoted, segment in segments:
        if is_quoted:
            cleaned_segments.append((is_quoted, segment))
        else:
            cleaned = re.sub(r"@(\w+)", lambda m: f"__EMOTE_{m.group(1).upper()}__", segment)
            cleaned_segments.append((is_quoted, cleaned))

    return targets, cleaned_segments, self_ref_counts


def _resolve_target(word, caller):
    """Resolve an @target word to a list of matching characters in the room.

    Searches in order: name/alias (standard search), then appearance
    fields (species, adjective, height, build) against room contents.
    """
    results = caller.search(
        word, location=caller.location, quiet=True,
    )
    if results:
        if isinstance(results, list):
            return results
        return [results]

    if not caller.location:
        return []

    word_lower = word.lower()
    matches = []
    for obj in caller.location.contents:
        if obj is caller:
            continue
        if not hasattr(obj, "species_key"):
            continue
        if (
            word_lower == (getattr(obj, "species_key", None) or "").lower()
            or word_lower in (getattr(obj, "appearance_adjective", None) or "").lower()
            or word_lower == (getattr(obj, "appearance_height", None) or "").lower()
            or word_lower == (getattr(obj, "appearance_build", None) or "").lower()
        ):
            matches.append(obj)
    return matches


def _lower_article(text):
    """Lowercase a leading 'A ' or 'An ' article."""
    if text.startswith("An "):
        return "an " + text[3:]
    if text.startswith("A "):
        return "a " + text[2:]
    return text


def _capitalize_first(text):
    """Capitalize the first alphabetic character, skipping ANSI codes."""
    i = 0
    while i < len(text):
        if text[i].isalpha():
            return text[:i] + text[i].upper() + text[i + 1:]
        i += 1
    return text


def emote_display_name(actor, looker, sentence_start=True):
    actor_plane = actor.current_plane()
    looker_plane = (
        looker.current_plane()
        if hasattr(looker, "current_plane")
        else "physical"
    )

    if actor_plane != looker_plane:
        color = "x" if actor_plane == "physical" else "M"
        prefix = f"|w(|{color}{actor_plane}|w)|n "
    else:
        prefix = ""

    if hasattr(actor, "appearance_name"):
        display_text = actor.appearance_name
    else:
        display_text = actor.key

    if not sentence_start:
        display_text = _lower_article(display_text)

    if looker.locks.check_lockstring(looker, "perm(Builder)"):
        return f"{prefix}{display_text} ({actor.name})"
    return f"{prefix}{display_text}"


def _format_target_name(target, listener, caller, actor_name, sentence_start):
    if target == caller:
        return actor_name
    return emote_display_name(target, listener, sentence_start=sentence_start)


def _resolve_target_ref(target, listener, caller, actor_name, sentence_start,
                         target_introduced):
    """Resolve a target reference with pronoun-after-first-mention logic.

    target_introduced: dict mapping target key to bool — True after the
    appearance name has been used once anywhere in the emote.
    """
    key = target.key

    if not target_introduced.get(key, False):
        target_introduced[key] = True
        return _format_target_name(
            target, listener, caller, actor_name, sentence_start,
        )

    skin = getattr(target, "skin_hex", None)
    c = skin if skin else "w"

    gender = getattr(target, "gender", None)
    if hasattr(target, "pronouns"):
        pronouns = target.pronouns
    elif gender:
        pronouns = target._PRONOUNS.get(gender, target._PRONOUNS.get("neuter", {}))
    else:
        pronouns = {"subject": "It", "object": "it", "reflexive": "itself"}

    if sentence_start:
        return f"|{c}{pronouns['subject']}|n"
    return f"|{c}{pronouns.get('object', pronouns.get('reflexive', 'it'))}|n"


def _resolve_self_ref(placeholder, caller, listener, is_self, state,
                       sentence_start, not_introduced):
    """Resolve @me/@self/@my placeholders with sentence-aware pronoun logic.

    not_introduced: mutable list [bool] — True until the appearance name has
    been used once anywhere in the emote, then set to False.
    """
    is_my = placeholder == "__EMOTE_MY__"
    key = "my" if is_my else "me"

    state[key] = state.get(key, 0) + 1
    first_use = state[key] == 1

    skin = getattr(caller, "skin_hex", None)
    c = skin if skin else "w"

    if is_my:
        if first_use and not_introduced[0]:
            if is_self:
                return f"|{c}{'Your' if sentence_start else 'your'}|n"
            if sentence_start:
                return f"{caller.appearance_name}'s"
            return f"{_lower_article(caller.appearance_name)}'s"
        if is_self:
            return f"|{c}{'Your' if sentence_start else 'your'}|n"
        if sentence_start:
            return f"|{c}{caller.pronouns['possessive']}|n"
        return f"|{c}{caller.pronouns['poss_obj']}|n"

    if not_introduced[0]:
        not_introduced[0] = False
        if is_self:
            return f"{_lower_article(caller.appearance_name)} |W(|{c}You|W)"
        if sentence_start:
            return emote_display_name(caller, listener, sentence_start=True)
        return emote_display_name(caller, listener, sentence_start=False)

    if is_self:
        if sentence_start:
            return f"|{c}You|n"
        return f"|{c}yourself|n"

    if sentence_start:
        return f"|{c}{caller.pronouns['subject']}|n"
    return f"|{c}{caller.pronouns['reflexive']}|n"


def build_emote_message(
    segments, targets, actor_name, caller, listener, hear_flag,
    self_state, is_self, starts_with_self_ref,
):
    fixed_segments = []
    for i, (is_quoted, segment) in enumerate(segments):
        if is_quoted and segment.endswith(".") and i + 1 < len(segments):
            segment = segment[:-1] + ","
        fixed_segments.append((is_quoted, segment))

    split = []
    for is_quoted, segment in fixed_segments:
        if is_quoted:
            split.append((False, True, segment))
        else:
            parts = re.split(r"(?<=[.!?])\s+", segment)
            for j, part in enumerate(parts):
                split.append((j > 0, False, part))

    not_introduced = [True]
    target_introduced = {}
    sentence_start = True
    parts = []

    for is_new_sentence, is_quoted, segment in split:
        if is_quoted:
            if getattr(listener, hear_flag, False):
                text = f'"{segment}"'
            else:
                text = '"but you can\'t hear it on this plane"'
            parts.append(text)
            sentence_start = False
        else:
            if is_new_sentence:
                self_state["me"] = 0
                self_state["my"] = 0
                sentence_start = True
                if parts:
                    parts.append(" ")

            text = segment

            first_non_ws = text.lstrip()
            placeholder_at_start = any(
                first_non_ws.startswith(ph)
                for ph in ("__EMOTE_ME__", "__EMOTE_SELF__", "__EMOTE_MY__")
            ) or any(
                first_non_ws.startswith(f"__EMOTE_{w.upper()}__")
                for w in targets
            )
            if sentence_start and not placeholder_at_start:
                sentence_start = False

            for placeholder_name in ("__EMOTE_ME__", "__EMOTE_SELF__", "__EMOTE_MY__"):
                if placeholder_name in text:
                    replacement = _resolve_self_ref(
                        placeholder_name, caller, listener, is_self,
                        self_state, sentence_start, not_introduced,
                    )
                    text = text.replace(placeholder_name, replacement)
                    sentence_start = False

            for word, target_list in targets.items():
                placeholder = f"__EMOTE_{word.upper()}__"
                target_obj = target_list[0]
                _text_ref = [text]
                _ss_ref = [sentence_start]

                def _replace_target(match, _tgt=target_obj, _t=_text_ref, _ss=_ss_ref):
                    pos = match.start()
                    end = match.end()
                    before = _t[0][:pos].rstrip()
                    at_start = _ss[0] and (not before or before[-1] in ".!?" or pos == 0)
                    suffix = match.group(1) or ""

                    introduced = target_introduced.get(_tgt.key, False)

                    if introduced and suffix == "'s":
                        skin = getattr(_tgt, "skin_hex", None)
                        c = skin if skin else "w"
                        if hasattr(_tgt, "pronouns"):
                            p = _tgt.pronouns
                        else:
                            p = {"possessive": "Its", "poss_obj": "its"}
                        poss = p["possessive"] if at_start else p.get("poss_obj", p["possessive"].lower())
                        return f"|{c}{poss}|n"

                    result = _resolve_target_ref(
                        _tgt, listener, caller, actor_name,
                        at_start, target_introduced,
                    )
                    return result + suffix

                text = re.sub(
                    re.escape(placeholder) + r"('?s?)", _replace_target, text,
                )
                sentence_start = False
            parts.append(text)
            sentence_start = False

    result = "".join(parts)
    if starts_with_self_ref:
        result = _capitalize_first(result)
    return result


class CmdEmote(GameMuxCommand):
    """|wEmote|n

    |wemote <text>|n performs an action visible to everyone in the room
    who can perceive your current plane. Quoted text within an emote is
    treated as spoken dialogue and is realm-gated the same way as the
    |wsay|n command - only listeners who can hear your current realm
    will see the quoted words; others see a muted placeholder instead.

    |w@me|n / |w@self|n inserts your appearance (first use) or a
    reflexive pronoun (himself/herself/itself) on subsequent uses.

    |w@my|n inserts a possessive reference: |wyour|n (first use to
    self), appearance + |w's|n (first use to others), or |wHis|n/|wHer|n/
    |wIts|n on subsequent uses.

    |w@target|n can be used to refer to specific characters or objects
    in the room. Targets are matched by name first, then by species,
    appearance adjective, height, or build. Multiple targets can share
    the same @name. Targets inside quotes are not allowed.

    Examples:
      |wemote waves @me hand|n
      |wemote says "Hello!" to @walker|n
      |wemote glances at @self and smiles|n
      |wemote nods at @visarii|n (matches by species)
      |wemote pats @tall on the back|n (matches by height)

    See also: |wsay|n, |wsetgender|n, |whelp|n."""

    key = "emote"
    aliases = [":"]
    locks = "cmd:all()"
    help_category = "General"
    arg_regex = None

    def parse(self):
        args = self.args
        if args and args[0] in ["'", ",", ":"]:
            pass
        elif args:
            args = args.strip()
        self.args = args

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("What do you want to do?")
            return

        segments = split_quoted_segments(self.args)

        for is_quoted, segment in segments:
            if is_quoted and "@" in segment:
                caller.msg("You can't apply a target inside of a sentence.")
                return

        targets, cleaned_segments, self_ref_counts = parse_emote_targets(
            segments, caller,
        )
        if targets is None:
            return

        has_self_ref = self_ref_counts["me"] > 0 or self_ref_counts["my"] > 0

        starts_with_self_ref = False
        if has_self_ref:
            for is_quoted, segment in cleaned_segments:
                if not is_quoted and segment.lstrip().startswith(
                    ("__EMOTE_ME__", "__EMOTE_SELF__", "__EMOTE_MY__")
                ):
                    starts_with_self_ref = True
                    break

        speaker_realm = "physical" if caller.can_speak_phys else "visarial"
        see_flag = (
            "can_phys_see"
            if speaker_realm == "physical"
            else "can_vis_see"
        )
        hear_flag = (
            "can_hear_phys"
            if speaker_realm == "physical"
            else "can_hear_vis"
        )

        audience = [
            obj
            for obj in caller.location.contents
            if obj is not caller and getattr(obj, see_flag, False)
        ]

        for listener in audience:
            actor_name = emote_display_name(caller, listener)
            self_state = {"me": 0, "my": 0}
            msg = build_emote_message(
                cleaned_segments, targets, actor_name, caller, listener,
                hear_flag, self_state, False, starts_with_self_ref,
            )
            if not has_self_ref:
                msg = msg.lstrip()
                msg = f"{actor_name} {msg}"
            listener.msg(text=(msg, {"type": "emote"}), from_obj=caller)
            from world.systems.gmcp import send_local_comm
            send_local_comm(listener, caller.key, msg)

        self_state = {"me": 0, "my": 0}
        self_msg = build_emote_message(
            cleaned_segments, targets, "You", caller, caller,
            hear_flag, self_state, True, starts_with_self_ref,
        )
        if not has_self_ref:
            self_msg = self_msg.lstrip()
            self_msg = f"You {self_msg}"
        caller.msg(text=(self_msg, {"type": "emote"}), from_obj=caller)
        from world.systems.gmcp import send_local_comm
        send_local_comm(caller, caller.key, self_msg)
