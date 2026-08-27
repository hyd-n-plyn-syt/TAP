"""
Wisp — the OOC account character.

Ball of light, pseudo-species "wisp". Shares the account's name, lives only
in the OOC lounge (Limbo #2, flagged OOC_Room). All stats zeroed/locked,
all pools zeroed. Customized via size / light color / adjective / gender.
"""

from evennia import AttributeProperty

from world.data import appearance as appearance_data

from .characters import Character


class Wisp(Character):
    """
    OOC wisp. Not deletable, not counted toward character slots, never in the
    real game world.
    """

    is_wisp = True

    # Reuse Character's appearance fields; for wisp "skin" is light color,
    # "height" stores size (small/modest/middling/large/immense).
    appearance_size = AttributeProperty(default="middling")

    def at_object_creation(self):
        super().at_object_creation()
        # Force wisp species/nature regardless of caller kwargs.
        self.species_key = "wisp"
        self.db.visarial_nature = "dual_natured"
        self.db.visarial_state = "normal"
        # Zero all pools (species already hides them, but clear currents too).
        for pool in ("vigor", "vim", "mens"):
            self.attributes.add(f"{pool}_current", 0)
        # Locks: only owning account can puppet; no one can delete.
        try:
            acct = self.account
            if acct:
                self.locks.add(f"puppet:id({acct.id}) or perm(Developer)")
        except Exception:
            pass
        self.locks.add("delete:false()")
        self.tags.add("wisp", category="account")
        self.tags.add("ooc_wisp", category="account")

    def basetype_setup(self):
        super().basetype_setup()
        self.locks.add("puppet:id(1) or perm(Developer)")
        self.locks.add("delete:false()")

    # ── plane overrides — wisp in OOC lounge sees/hears/touches everything ──

    def _is_in_ooc_lounge(self):
        try:
            loc = self.location
            if not loc:
                return False
            if getattr(loc.db, "is_ooc_room", False):
                return True
            if loc.tags.get("ooc_room", category="room_flag"):
                return True
            # Fallback: id 2 is always OOC_Room
            if getattr(loc, "id", None) == 2:
                return True
        except Exception:
            pass
        return False

    @property
    def can_phys_see(self):
        if self._is_in_ooc_lounge():
            return True
        return super().can_phys_see

    @property
    def can_vis_see(self):
        if self._is_in_ooc_lounge():
            return True
        return super().can_vis_see

    @property
    def can_phys_touch(self):
        if self._is_in_ooc_lounge():
            return True
        return super().can_phys_touch

    @property
    def can_vis_touch(self):
        if self._is_in_ooc_lounge():
            return True
        return super().can_vis_touch

    @property
    def planes_occupied(self):
        if self._is_in_ooc_lounge():
            return ("physical", "visarial")
        return super().planes_occupied

    def visible_to(self, looker):
        if self._is_in_ooc_lounge():
            return True
        return super().visible_to(looker)

    # ── display ──

    @property
    def species_display_name(self):
        name = "Wisp"
        hexcol = self.skin_hex
        if hexcol:
            return f"|{hexcol}{name}|n"
        return name

    @property
    def appearance_bits(self):
        size = getattr(self.db, "appearance_size", None) or getattr(self, "appearance_size", None) or appearance_data.DEFAULT_WISP_SIZE
        if not appearance_data.valid_wisp_size(size):
            size = appearance_data.DEFAULT_WISP_SIZE
        adjective = self.appearance_adjective or "soft"
        core = f"{size} {adjective} {self.species_display_name} {self.gender}"
        return core, (self.pose or "hovering")

    @property
    def appearance_phrase(self):
        core, pose = self.appearance_bits
        return f"{appearance_data.article(core)} {core} {pose} here."

    def appearance_paragraph(self, looker):
        # Wisp-specific paragraph: size + adjective + light color + gender
        species_key = "wisp"
        gender = self.gender or "neuter"
        pose = self.pose or "hovering"
        if looker == self:
            subj, be, poss = "You", "are", "your"
        else:
            pr = self.pronouns
            subj, be, poss = pr["subject"], "is", pr["poss_obj"]

        parts = []
        opening = appearance_data.POSE_OPENINGS.get(pose, "Before you drifts")
        parts.append(f"{opening} a {gender} wisp.")

        size = getattr(self.db, "appearance_size", None) or self.appearance_size or appearance_data.DEFAULT_WISP_SIZE
        size_desc = appearance_data.WISP_SIZE_DESCRIPTIONS.get(size, "")
        if size_desc:
            # Make pronoun-aware: size_desc is neutral; prepend subj
            parts.append(f"{subj} {be.lower() if subj=='You' else 'is'} {size_desc[0].lower()+size_desc[1:]}" if size_desc else "")

        adj = self.appearance_adjective
        if adj:
            adj_descs = appearance_data.SPECIES_ADJECTIVE_DESCRIPTIONS.get(species_key, {})
            adj_desc = adj_descs.get(adj)
            if adj_desc:
                parts.append(adj_desc)

        skin = self.appearance_skin
        if skin:
            hexcol = self.skin_hex or ""
            color_tag = f"|{hexcol}{skin}|n" if hexcol else skin
            # Use species skin sentence if present, else generic
            skin_tpl = appearance_data.SPECIES_SKIN_SENTENCES.get(species_key, "Their light bears a {color} hue.")
            parts.append(skin_tpl.format(color=color_tag))

        para = " ".join(p for p in parts if p)
        if looker == self:
            para = para.replace("Their ", "Your ").replace("their ", "your ")
        else:
            poss_cap = self.pronouns["possessive"]
            poss_low = self.pronouns["poss_obj"]
            para = para.replace("Their ", f"{poss_cap} ").replace("their ", f"{poss_low} ")
        return para

    def set_appearance(self, attr, value):
        # Wisps only support size/adjective/skin/gender/pose
        value = value.strip().lower().replace("_", " ")
        if attr == "size":
            key = value.replace(" ", "_").replace("-", "_")
            if key not in appearance_data.WISP_SIZES:
                return False
            self.db.appearance_size = key
            self.appearance_size = key
            return True
        if attr in ("adjective", "skin", "color", "light"):
            # map color/light -> skin
            if attr in ("color", "light"):
                attr = "skin"
            if attr == "adjective":
                if not appearance_data.valid_adjective("wisp", value):
                    return False
                self.appearance_adjective = value
                return True
            if attr == "skin":
                if not appearance_data.valid_skin("wisp", value):
                    return False
                self.appearance_skin = value
                return True
        # delegate other attrs to Character but block height/build/eyes/hair
        if attr in ("height", "build", "eyes", "eye_color", "hair", "hair_color"):
            return False
        return super().set_appearance(attr, value)

    def get_prompt(self):
        # OOC prompt — no pools
        plane = self.current_plane()
        plane_color = "|x" if plane == "physical" else "|M"
        state_text = f"{plane_color}{plane}|n"
        # Show OOC tag clearly
        return f"|w[|n{state_text} |wOOC|n|w]|n"
