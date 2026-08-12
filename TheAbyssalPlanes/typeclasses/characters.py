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

_DIRECTION_ALIASES = {
    "north", "south", "east", "west",
    "northeast", "northwest", "southeast", "southwest",
    "n", "s", "e", "w", "ne", "nw", "se", "sw",
    "up", "down", "in", "out", "enter", "leave",
}

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
    appearance_eyes = AttributeProperty(default=None)
    appearance_eye_color = AttributeProperty(default=None)
    appearance_hair = AttributeProperty(default=None)
    appearance_hair_color = AttributeProperty(default=None)
    pose = AttributeProperty(default="standing")
    sign = AttributeProperty(default=None)
    birth_date = AttributeProperty(default=None)

    combat_target = AttributeProperty(default=None)
    friendly_target = AttributeProperty(default=None)
    manual_queue = AttributeProperty(default=[])
    preferred_moves = AttributeProperty(default=[])
    pos_x = AttributeProperty(default=0)
    pos_y = AttributeProperty(default=0)
    pos_z = AttributeProperty(default=1)
    occupies_space = AttributeProperty(default=True)
    is_flying = AttributeProperty(default=False)
    can_fly = AttributeProperty(default=False)
    is_autowhere = AttributeProperty(default=False)
    is_hostile = AttributeProperty(default=False)
    map_size = AttributeProperty(default=15)

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

    def basetype_setup(self):
        super().basetype_setup()
        self.locks.add("teleport:perm(Builder); teleport_here:perm(Builder)")

    def at_cmdset_get(self, **kwargs):
        super().at_cmdset_get(**kwargs)
        if not self.location:
            return
        self.cmdset.remove("DirectionFallbackCmdSet")
        exit_keys = set()
        exit_aliases = set()
        for obj in self.location.contents:
            if not obj.destination:
                continue
            exit_keys.add(obj.key.lower())
            for alias in (obj.aliases.all() or []):
                exit_aliases.add(alias.lower())
        all_exit_names = exit_keys | exit_aliases
        missing = _DIRECTION_ALIASES - all_exit_names
        if not missing:
            return
        from evennia import CmdSet
        from commands.player.movement import CmdDirectionFallback

        class _FallbackCmdSet(CmdSet):
            key = "DirectionFallbackCmdSet"
            priority = 0
            def at_cmdset_creation(self):
                for direction in missing:
                    cmd = type("CmdFallback_" + direction, (CmdDirectionFallback,), {
                        "key": direction,
                        "aliases": [direction],
                    })
                    self.add(cmd)
        self.cmdset.add(_FallbackCmdSet(), persistent=False)

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
        core = f"{middle} {self.species_display_name} {self.gender}"
        return core, (self.pose or "standing")

    @property
    def appearance_phrase(self):
        """
        The three-word description shown in place of a name in rooms:
        "A tall and lithe, translucent Visarii standing here."
        """
        core, pose = self.appearance_bits
        return f"{appearance_data.article(core)} {core} {pose} here."

    @property
    def appearance_name(self):
        """
        The appearance description without pose or 'here.' — used in emotes:
        "A tall and lithe, translucent Visarii"
        """
        core, _ = self.appearance_bits
        return f"{appearance_data.article(core)} {core}"

    def appearance_paragraph(self, looker):
        """Build the multi-sentence appearance paragraph shown on 'look'.

        The paragraph is generated from stored attributes: pose, height,
        build, gender, species, adjective, eyes, hair, skin.  Each
        attribute contributes a sentence; unset optional attributes are
        silently omitted.  The looker argument is accepted for future
        self-vs-other viewpoint differences.
        """
        species_key = self.species_key
        species_name = (
            self.species["name"]
            if self.species
            else "Stranger"
        )
        gender = self.gender or "neuter"

        # Opening — pose-dependent.
        pose = self.pose or "standing"
        opening = appearance_data.POSE_OPENINGS.get(pose, "Before you stands")

        # Core physical description: combined height + build with pronouns.
        height = self.appearance_height or appearance_data.DEFAULT_HEIGHT
        build_word = self.appearance_build or appearance_data.DEFAULT_BUILD

        if looker == self:
            subj, be, poss = "You", "are", "your"
        else:
            pr = self.pronouns
            subj, be, poss = pr["subject"], "is", pr["poss_obj"]

        hb_phrase = appearance_data.height_build_phrase(
            height, build_word, subj=subj, be=be, poss=poss,
        )

        parts = [f"{opening} a {gender} {species_name}."]
        if hb_phrase:
            parts.append(hb_phrase)

        # Adjective sentence.
        adjective = self.appearance_adjective
        if adjective and species_key:
            adj_descs = appearance_data.SPECIES_ADJECTIVE_DESCRIPTIONS.get(
                species_key, {}
            )
            adj_desc = adj_descs.get(adjective)
            if adj_desc:
                parts.append(adj_desc)

        # Eye sentence — shape description with embedded {color} placeholder.
        if self.appearance_eyes and species_key:
            eye_descs = appearance_data.SPECIES_EYE_DESCRIPTIONS.get(species_key, {})
            eye_desc = eye_descs.get(self.appearance_eyes)
            if eye_desc:
                if self.appearance_eye_color:
                    hexcol = appearance_data.hex_for_name(self.appearance_eye_color) or ""
                    color_tag = (
                        f"|{hexcol}{self.appearance_eye_color}|n"
                        if hexcol
                        else self.appearance_eye_color
                    )
                    eye_desc = eye_desc.replace("{color}", color_tag)
                else:
                    eye_desc = eye_desc.replace("{color}", "")
                    eye_desc = " ".join(eye_desc.split())
                parts.append(eye_desc)

        # Hair sentence — style description with embedded {color} placeholder.
        if self.appearance_hair and self.appearance_hair != "none" and species_key:
            hair_descs = appearance_data.SPECIES_HAIR_DESCRIPTIONS.get(
                species_key, {}
            )
            hair_desc = hair_descs.get(self.appearance_hair)
            if hair_desc:
                if self.appearance_hair_color and self.appearance_hair_color != "none":
                    hexcol = appearance_data.hex_for_name(self.appearance_hair_color) or ""
                    color_tag = (
                        f"|{hexcol}{self.appearance_hair_color}|n"
                        if hexcol
                        else self.appearance_hair_color
                    )
                    hair_desc = hair_desc.replace("{color}", color_tag)
                else:
                    hair_desc = hair_desc.replace("{color}", "")
                    hair_desc = " ".join(hair_desc.split())
                parts.append(hair_desc)

        # Skin tone.
        if self.appearance_skin and species_key:
            skin_tpl = appearance_data.SPECIES_SKIN_SENTENCES.get(
                species_key, "Their skin bears a {color} hue."
            )
            hexcol = self.skin_hex or ""
            color_tag = f"|{hexcol}{self.appearance_skin}|n" if hexcol else self.appearance_skin
            parts.append(skin_tpl.format(color=color_tag))

        para = " ".join(parts)

        # Pronoun replacement: swap generic 'their/Their' for the
        # character's actual gendered pronouns, or 'your/Your' for
        # self-view.
        if looker == self:
            para = para.replace("Their ", "Your ").replace("their ", "your ")
        else:
            poss = self.pronouns["possessive"]
            poss_low = self.pronouns["poss_obj"]
            para = para.replace("Their ", f"{poss} ").replace("their ", f"{poss_low} ")

        return para

    @property
    def gender(self):
        """The character's gender key: 'male', 'female', or 'neuter' (default)."""
        return self.attributes.get("gender", default="neuter")

    @gender.setter
    def gender(self, value):
        self.db.gender = value

    _PRONOUNS = {
        "male":   {"subject": "He",  "object": "him",  "possessive": "His",  "poss_obj": "his",  "reflexive": "himself"},
        "female": {"subject": "She", "object": "her",  "possessive": "Her",  "poss_obj": "her",  "reflexive": "herself"},
        "neuter": {"subject": "It",  "object": "it",   "possessive": "Its",  "poss_obj": "its",  "reflexive": "itself"},
    }

    @property
    def pronouns(self):
        """Return the pronoun dict for this character's gender."""
        return self._PRONOUNS.get(self.gender, self._PRONOUNS["neuter"])

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
        elif attr == "eyes":
            if not (self.species_key and appearance_data.valid_eye(self.species_key, value)):
                return False
        elif attr == "eye_color":
            if not (self.species_key and appearance_data.valid_eye_color(self.species_key, value)):
                return False
        elif attr == "hair":
            if not (self.species_key and appearance_data.valid_hair(self.species_key, value)):
                return False
        elif attr == "hair_color":
            if not (self.species_key and appearance_data.valid_hair_color(self.species_key, value)):
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

    def at_post_move(self, source_location, move_type="move", **kwargs):
        """
        After any move, stamp this character's grid position onto the new
        room's entry coordinate. The entry point is inferred from the exit
        just traversed: leaving via a North exit means arriving at the new
        room's South wall.
        """
        super().at_post_move(source_location, **kwargs)
        if not (self.location and source_location):
            return
        from combat.grid import get_entry_coords, get_room_grid_size
        
        entry = None
        for obj in source_location.contents:
            if not obj.destination:
                continue
            if obj.destination.id == self.location.id:
                for name in (obj.key, *(obj.aliases.all() or [])):
                    if name.lower() in ("north", "south", "east", "west"):
                        opp = {
                            "north": "south", "south": "north",
                            "east": "west", "west": "east",
                        }[name.lower()]
                        entry = get_entry_coords(self.location, opp)
                        break
                if entry:
                    break
        if entry:
            tx, ty = entry
        else:
            w, h = get_room_grid_size(self.location)
            tx, ty = w // 2, h // 2

        from combat.movement import find_nearest_unoccupied_coord
        ux, uy = find_nearest_unoccupied_coord(self.location, tx, ty, z=1, ignore=self)
        self.db.pos_x, self.db.pos_y = ux, uy
        self.db.pos_z = 1
        self.db.room_id = self.location.dbref

        if getattr(self.db, "is_autowhere", False):
            from combat.map_renderer import render_map
            self.msg(render_map(self))

    def send_autowhere(self):
        if getattr(self.db, "is_autowhere", False):
            from combat.map_renderer import render_map
            self.msg(render_map(self))

    def check_autowhere(self, old_location, old_x, old_y, old_z):
        if not getattr(self.db, "is_autowhere", False):
            return
        if (self.location != old_location
                or getattr(self.db, "pos_x", None) != old_x
                or getattr(self.db, "pos_y", None) != old_y
                or getattr(self.db, "pos_z", None) != old_z):
            from combat.map_renderer import render_map
            self.msg(render_map(self))

    def _exit_direction(self, room, target):
        """Compass direction of the exit in `room` leading to `target`, or None."""
        if not room or not target:
            return None
        from combat.grid import exit_direction
        for obj in room.contents:
            if getattr(obj, "destination", None) and obj.destination.id == target.id:
                direction = exit_direction(obj)
                if direction:
                    return direction
        return None

    def _movement_observers(self):
        """Creatures in the current room who can perceive this character."""
        if not self.location:
            return []
        return [
            obj
            for obj in self.location.contents
            if obj is not self
            and getattr(obj, "is_creature", False)
            and self.visible_to(obj)
        ]

    def announce_move_from(self, destination, msg=None, mapping=None, move_type="move", **kwargs):
        if move_type == "teleport":
            if self.location:
                phrase = self.appearance_name
                self.location.msg_contents(
                    f"{phrase}({self.name}) folds into herself and blinks out of existence.",
                    exclude=(self,),
                )
                self.msg(
                    f"{phrase}(You) is teleporting from "
                    f"{self.location.key} and heading to {destination.key}."
                )
            return
        if move_type not in ("move", "traverse") or not self.location:
            super().announce_move_from(destination, msg=msg, mapping=mapping, move_type=move_type, **kwargs)
            return
        direction = self._exit_direction(self.location, destination)
        phrase = self.appearance_name
        if direction:
            text = f"{phrase} walks away to the {direction}."
            self.msg(f"You walk to the {direction}.")
        else:
            text = f"{phrase} walks away."
        for observer in self._movement_observers():
            observer.msg(text, from_obj=self)

    def announce_move_to(self, source_location, msg=None, mapping=None, move_type="move", **kwargs):
        if move_type == "teleport":
            if self.location:
                phrase = self.appearance_name
                self.location.msg_contents(
                    f"{phrase}({self.name}) flickers into existence.",
                    exclude=(self,),
                )
            return
        if move_type not in ("move", "traverse") or not self.location:
            super().announce_move_to(source_location, msg=msg, mapping=mapping, move_type=move_type, **kwargs)
            return
        direction = self._exit_direction(self.location, source_location)
        phrase = self.appearance_name
        if direction:
            text = f"{phrase} walks in from the {direction}."
        else:
            text = f"{phrase} walks in."
        for observer in self._movement_observers():
            observer.msg(text, from_obj=self)

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
        'Look' on a character: the generated appearance paragraph followed
        immediately by the player-written desc, then any visarial aspect
        the looker can perceive.
        """
        if not looker:
            return ""

        if not self.visible_to(looker):
            return ""

        parts = [self.appearance_paragraph(looker)]
        if self.db.desc:
            parts.append(self.db.desc)
        vis = self.visarial_desc_text()
        if self.can_vis_touch and vis and looker.can_vis_see:
            parts.append(self.format_visarial_desc(vis))

        return self.format_appearance(
            self.appearance_template.format(
                name="",
                extra_name_info="",
                desc=" ".join(parts),
                header=self.get_display_header(looker, **kwargs),
                footer=self.get_display_footer(looker, **kwargs),
                exits="",
                characters="",
                things="",
            ),
            looker,
            **kwargs,
        )

    def get_status_descriptor(self):
        """
        Returns status descriptors for Vigor, Vim, Mens based on pool percentage.
        """
        # (This will bridge to combat/target.py's descriptor mapping)
        return "unharmed, mentally sound, and spiritually centered"

    def get_prompt(self):
        """Build the client prompt from current pools and visarial state, including combat state."""
        mode = self.db.promptmode or "numbers"
        # ... (Existing plane logic) ...
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
            elif mode == "immersive":
                parts.append(f"|w[|n{self.name} is {self.get_status_descriptor()}.|w]|n")
            else:
                parts.append(f"{label} {pool_color(cur, maxv)}{cur}/{maxv}|n")

        parts.append(f"|w[|n{state_text}|w]|n")
        return "  ".join(parts)

