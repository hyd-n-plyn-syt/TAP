"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia import AttributeProperty
from evennia.contrib.rpg.health_bar import display_meter
from evennia.objects.objects import DefaultCharacter

from world.data import appearance as appearance_data
from world.data import calendar as calendar_data
from world.data import species as species_data
from world.systems import skills as skill_systems
from world.systems import stats

from .objects import ObjectParent

# Bar fill gradient (matches display_meter's default) and the "empty"
# background used when a pool is damaged: dark gray via the xterm256
# grayscale code |=e (index 235), near black but still visible.
_POOL_FILL_COLORS = ["R", "Y", "G"]
_POOL_EMPTY_BG = "=e"

# Prompt colors for the projected visarial states. Deliberately distinct
# from the plane colors (physical |x dark gray, visarial |M magenta).
_STATE_COLORS = {"perceiving": "|y", "manifesting": "|c"}


def pool_color(cur, maxv):
    """Return an ANSI foreground color code for a pool value by how full it is."""
    if maxv <= 0:
        return "|R"
    pct = float(cur) / float(maxv)
    idx = int(round(len(_POOL_FILL_COLORS) * pct)) - 1
    idx = max(0, min(idx, len(_POOL_FILL_COLORS) - 1))
    return "|" + _POOL_FILL_COLORS[idx]


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    corpus_potestas = AttributeProperty(default=1, category="stat")
    corpus_reflexus = AttributeProperty(default=1, category="stat")
    corpus_obsistis = AttributeProperty(default=1, category="stat")
    genius_potestas = AttributeProperty(default=1, category="stat")
    genius_reflexus = AttributeProperty(default=1, category="stat")
    genius_obsistis = AttributeProperty(default=1, category="stat")
    animus_potestas = AttributeProperty(default=1, category="stat")
    animus_reflexus = AttributeProperty(default=1, category="stat")
    animus_obsistis = AttributeProperty(default=1, category="stat")

    species_key = AttributeProperty(default=None)

    appearance_height = AttributeProperty(default=None)
    appearance_build = AttributeProperty(default=None)
    appearance_adjective = AttributeProperty(default=None)
    appearance_skin = AttributeProperty(default=None)
    pose = AttributeProperty(default="standing")
    sign = AttributeProperty(default=None)
    birth_date = AttributeProperty(default=None)

    skills = AttributeProperty(default={}, category="growth")
    skills_xp = AttributeProperty(default={}, category="growth")
    stat_xp = AttributeProperty(default={}, category="growth")

    @property
    def species(self):
        """The character's species data dict, or None if none is set."""
        return species_data.get_species(self.species_key)

    @property
    def corpus(self):
        return stats.main_stat(self, "corpus")

    @property
    def genius(self):
        return stats.main_stat(self, "genius")

    @property
    def animus(self):
        return stats.main_stat(self, "animus")

    @property
    def vigor(self):
        return stats.derived_pools(self)["vigor"]

    @property
    def vigor_regen(self):
        return stats.derived_pools(self)["vigor_regen"]

    @property
    def vim(self):
        return stats.derived_pools(self)["vim"]

    @property
    def vim_regen(self):
        return stats.derived_pools(self)["vim_regen"]

    @property
    def mens(self):
        return stats.derived_pools(self)["mens"]

    @property
    def mens_regen(self):
        return stats.derived_pools(self)["mens_regen"]

    def at_object_creation(self):
        super().at_object_creation()
        self.db.promptmode = "numbers"
        data = self.species
        if data:
            self.db.visarial_nature = data["visarial_nature"]
            self.db.visarial_state = data["default_visarial_state"]
        else:
            self.db.visarial_state = "normal"
        self.reset_pools()
        if not self.sign:
            date = calendar_data.cosmic_date()
            self.sign = calendar_data.sign_of_month(date["month"])
            self.birth_date = calendar_data.format_date(date, show_clock=False)

    def apply_species(self, key):
        """Set the character's species and apply its defaults. Returns True on
        success, False if the key is unknown."""
        data = species_data.get_species(key)
        if not data:
            return False
        self.species_key = data["key"]
        self.db.visarial_nature = data["visarial_nature"]
        self.db.visarial_state = data["default_visarial_state"]
        self.reset_pools()
        return True

    def clear_species(self):
        """Remove the character's species, restoring neutral defaults."""
        self.species_key = None
        self.db.visarial_nature = "dual_natured"
        self.db.visarial_state = "normal"
        self.reset_pools()

    def set_state(self, state):
        if state not in ("normal", "perceiving", "manifested"):
            return False
        data = self.species
        if data:
            if state == "perceiving" and not data.get("can_perceive"):
                return False
            if state == "manifested" and not data.get("can_manifest"):
                return False
        self.db.visarial_state = state
        self.msg(prompt=self.get_prompt())
        return True

    @property
    def projected_state(self):
        """
        The optional prompt suffix shown when actively perceiving the other
        plane or manifesting fully into it. Returns None when simply existing
        in the creature's native plane.
        """
        state = self.state()
        if state == "perceiving":
            return "perceiving"
        if state == "manifested":
            return "manifesting"
        return None

    @property
    def pools_current(self):
        """Return {pool: current} for the three pools, clamped to [0, max]."""
        result = {}
        for pool in stats.POOL_KEYS:
            maxv = getattr(self, pool)
            cur = self.attributes.get(f"{pool}_current")
            if cur is None:
                cur = maxv
            result[pool] = max(0, min(cur, maxv))
        return result

    def set_pool(self, pool, value):
        """Set a current pool, clamped to [0, max]. Returns the stored value."""
        if pool not in stats.POOL_KEYS:
            return None
        maxv = getattr(self, pool)
        value = max(0, min(int(value), maxv))
        self.attributes.add(f"{pool}_current", value)
        self.msg(prompt=self.get_prompt())
        return value

    def reset_pools(self):
        """Restore all current pools to their derived maximums."""
        for pool in stats.POOL_KEYS:
            self.attributes.add(f"{pool}_current", getattr(self, pool))
        self.msg(prompt=self.get_prompt())

    @property
    def skin_hex(self):
        """The Truecolor hex for the character's skin tone, if valid."""
        if not (self.species_key and self.appearance_skin):
            return None
        return appearance_data.hex_for_skin(self.species_key, self.appearance_skin)

    @property
    def species_display_name(self):
        """The species name for display, colored by skin tone."""
        name = self.species["name"] if self.species else "Stranger"
        hexcol = self.skin_hex
        if hexcol:
            return f"|{hexcol}{name}|n"
        return name

    @property
    def appearance_bits(self):
        """
        (core, pose) split of the appearance phrase, used to group room
        occupants by position: e.g. ("tall and lean, refracting Visarii",
        "standing").
        """
        height = (
            appearance_data.height_phrase(self.appearance_height)
            if self.appearance_height
            else appearance_data.DEFAULT_HEIGHT
        )
        build = self.appearance_build or appearance_data.DEFAULT_BUILD
        adjective = self.appearance_adjective
        if adjective:
            middle = f"{height} and {build}, {adjective}"
        else:
            middle = f"{height} and {build}"
        core = f"{middle} {self.species_display_name}"
        return core, (self.pose or "standing")

    @property
    def appearance_phrase(self):
        """
        The three-word description shown in place of a name in rooms:
        "A tall and lithe, translucent Visarii standing here."
        """
        core, pose = self.appearance_bits
        return f"{appearance_data.article(core)} {core} {pose} here."

    def set_appearance(self, attr, value):
        """Set one appearance attribute, normalizing whitespace. Returns True
        on success, False if the value is not valid for this character."""
        value = value.strip().lower().replace("_", " ")
        if attr == "height":
            key = value.replace(" ", "_").replace("-", "_")
            if key not in appearance_data.HEIGHTS:
                return False
            value = key
        elif attr == "build":
            height = self.appearance_height or appearance_data.DEFAULT_HEIGHT
            if not appearance_data.valid_build(height, value):
                return False
        elif attr == "adjective":
            if not (self.species_key and appearance_data.valid_adjective(self.species_key, value)):
                return False
        elif attr == "skin":
            if not (self.species_key and appearance_data.valid_skin(self.species_key, value)):
                return False
        else:
            return False
        setattr(self, f"appearance_{attr}", value)
        return True

    def set_pose(self, pose):
        """
        Set a whitelisted position word for this character. Returns True on
        success, False if the pose is not in the whitelist. Shared API so
        combat and other systems can move a character into a pose without
        going through the command.
        """
        pose = (pose or "").strip().lower().replace("_", " ")
        if not appearance_data.valid_pose(pose):
            return False
        self.pose = pose
        return True

    def use_skill(self, key, difficulty="medium", times=1):
        """
        Attempt to exercise a skill, awarding XP to the skill and its linked
        statistics. The character must already know the skill. Returns the
        result dict from the growth system, or None if the skill is unknown.
        """
        return skill_systems.use_skill(self, key, difficulty=difficulty, times=times)

    def at_say(self, message, msg_self=None, msg_location=None, receivers=None,
               msg_receivers=None, **kwargs):
        """Realm-aware 'say'. A speaker's words land only in the realm they
        currently occupy; other characters in the same room only hear them if
        they perceive that realm. Whispering to an explicit target bypasses
        realm gating (you can whisper to anyone you share a room with)."""
        if kwargs.get("whisper", False) or not self.location:
            return super().at_say(
                message, msg_self=msg_self, msg_location=msg_location,
                receivers=receivers, msg_receivers=msg_receivers, **kwargs,
            )

        if self.can_speak_phys and not self.can_speak_vis:
            hear_flag = "can_hear_phys"
        elif self.can_speak_vis and not self.can_speak_phys:
            hear_flag = "can_hear_vis"
        else:
            return super().at_say(
                message, msg_self=msg_self, msg_location=msg_location,
                receivers=receivers, msg_receivers=msg_receivers, **kwargs,
            )

        audience = [
            obj
            for obj in self.location.contents
            if obj is not self and getattr(obj, hear_flag, False)
        ]
        for receiver in audience:
            receiver.msg(
                text=(f"{self.get_display_name(receiver)} says, |n\"{message}|n\"", {"type": "say"}),
                from_obj=self,
            )
        if msg_self:
            self.msg(text=("You say, |n\"{message}|n\"".format(message=message), {"type": "say"}), from_obj=self)

    @property
    def trainer_skills(self):
        """
        The list of skill keys this character can teach, or None if they are
        not a trainer. Set with the builder 'settrainer' command.
        """
        return self.attributes.get("trained_skills")

    def get_display_name(self, looker=None, **kwargs):
        """
        Characters show a plane prefix plus their appearance phrase.
        Builders/staff additionally see the real name in parentheses
        (until a remember/introduce system exists).
        """
        plane = self.current_plane()
        color = "x" if plane == "physical" else "M"
        prefix = f"|w(|{color}{plane}|w)|n"
        if looker is not None and self.locks.check_lockstring(looker, "perm(Builder)"):
            return f"{prefix} {self.appearance_phrase} ({self.name})"
        return f"{prefix} {self.appearance_phrase}"

    def get_extra_display_name_info(self, looker=None, **kwargs):
        """
        The real name already carries the identity for builders; don't append
        the database ref.
        """
        return ""

    def return_appearance(self, looker, **kwargs):
        """
        'Look' on a character: the plane prefix and name, followed by the
        appearance phrase, the long description, then any visarial aspect
        the looker can perceive. Works for self and others alike.
        """
        if not looker:
            return ""
        plane = self.current_plane()
        color = "x" if plane == "physical" else "M"
        prefix = f"|w(|{color}{plane}|w)|n"
        if self.locks.check_lockstring(looker, "perm(Builder)"):
            name = f"{prefix} {self.name}"
        else:
            name = prefix

        if not self.visible_to(looker):
            return ""

        lines = [self.appearance_phrase]
        if self.db.desc:
            lines.append(self.db.desc)
        vis = self.visarial_desc_text()
        if self.can_vis_touch and vis and looker.can_vis_see:
            lines.append(self.format_visarial_desc(vis))

        return self.format_appearance(
            self.appearance_template.format(
                name=name,
                extra_name_info=self.get_extra_display_name_info(looker, **kwargs),
                desc="\n".join(lines),
                header=self.get_display_header(looker, **kwargs),
                footer=self.get_display_footer(looker, **kwargs),
                exits="",
                characters="",
                things="",
            ),
            looker,
            **kwargs,
        )

    def get_prompt(self):
        """Build the client prompt from current pools and visarial state."""
        mode = self.db.promptmode or "numbers"
        plane = self.current_plane()
        plane_color = "|x" if plane == "physical" else "|M"
        state_text = f"{plane_color}{plane}|n"
        projected = self.projected_state
        if projected:
            state_text += f" {_STATE_COLORS.get(projected, '|W')}{projected}|n"

        zeroed = species_data.zeroed_pools(self.species_key)
        parts = []
        for pool in stats.POOL_KEYS:
            if pool in zeroed:
                continue
            maxv = getattr(self, pool)
            cur = self.pools_current[pool]
            label = f"|w{pool.capitalize()}:|n"
            if mode == "percent":
                pct = int(round(100 * cur / maxv)) if maxv else 0
                parts.append(f"{label} {pool_color(cur, maxv)}{pct}%|n")
            elif mode == "bars":
                bar = display_meter(
                    cur,
                    maxv,
                    length=10,
                    show_values=False,
                    empty_color=_POOL_EMPTY_BG,
                )
                parts.append(f"{label} {bar}")
            else:
                parts.append(f"{label} {pool_color(cur, maxv)}{cur}/{maxv}|n")

        parts.append(f"|w[|n{state_text}|w]|n")
        return "  ".join(parts)
