"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.search import search_tag
from evennia.utils.utils import iter_to_str
from combat.grid import grid_quadrant
from world.data import appearance as appearance_data
from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None.
    Modified to dynamically display surrounding grid room names on look.
    """

    def at_object_creation(self):
        """Called only once, when the room object is first created."""
        super().at_object_creation()

        # Identity tags
        self.tags.add("None", category="planetary_body")
        self.tags.add("None", category="planetary_site")

        # Global planetary coordinate grid
        self.tags.add("None", category="planet_x")
        self.tags.add("None", category="planet_y")
        self.tags.add("None", category="planet_z")

        # Inner subzone local coordinate grid
        self.tags.add("None", category="site_x")
        self.tags.add("None", category="site_y")
        self.tags.add("None", category="site_z")

    def return_appearance(self, looker, **kwargs):
        """
        Main callback used by 'look'. Intercepts layout generation to title-case 
        lowercase headers, respect manual capitalization, and sort everything clock-wise.
        """
        if not looker:
            return ""

        # 1. Capitalization Rule: Fetch the room's display name
        raw_name = self.get_display_name(looker, **kwargs)
        header_name = raw_name if not raw_name.islower() else raw_name.title()

        # 2. Extract current room's location data for neighbor scanning
        body = self.tags.get(category="planetary_body", return_list=False)
        site = self.tags.get(category="planetary_site", return_list=False)

        px = self.tags.get(category="planet_x", return_list=False)
        py = self.tags.get(category="planet_y", return_list=False)
        pz = self.tags.get(category="planet_z", return_list=False)

        sx = self.tags.get(category="site_x", return_list=False)
        sy = self.tags.get(category="site_y", return_list=False)
        sz = self.tags.get(category="site_z", return_list=False)

        distance_string = ""
        
        if body and str(body).lower() != "none":
            body_str = str(body).lower()
            site_str = str(site).lower()
            
            # Strict Master Clockwise Order Matrix for sorting everything uniformly
            direction_order = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest", "up", "down", "enter", "leave"]
            
            # Temporary sorting buckets
            cardinal_matches = {}
            inward_portals = []
            outward_portals = []

            # --- PART A: SCAN CARDINAL DIRECTIONS VIA GRID MATH ---
            if site_str != "none":
                has_coords = sx and sy and sz and "none" not in (str(sx).lower(), str(sy).lower(), str(sz).lower())
            else:
                has_coords = px and py and pz and "none" not in (str(px).lower(), str(py).lower(), str(pz).lower())

            if has_coords:
                offsets = {
                    "north": (0, 1, 0), "south": (0, -1, 0),
                    "east": (1, 0, 0), "west": (-1, 0, 0),
                    "northeast": (1, 1, 0), "northwest": (-1, 1, 0),
                    "southeast": (1, -1, 0), "southwest": (-1, -1, 0),
                    "up": (0, 0, 1), "down": (0, 0, -1)
                }

                candidates = search_tag(category="planetary_body")

                for direction, (dx, dy, dz) in offsets.items():
                    target_room = None
                    for candidate in candidates:
                        if candidate.typeclass_path != "typeclasses.rooms.Room":
                            continue

                        cb = str(candidate.tags.get(category="planetary_body", return_list=False) or "").lower()
                        if cb != body_str:
                            continue

                        cs = str(candidate.tags.get(category="planetary_site", return_list=False) or "").lower()
                        if cs != site_str:
                            continue

                        if site_str != "none":
                            cx = candidate.tags.get(category="site_x", return_list=False)
                            cy = candidate.tags.get(category="site_y", return_list=False)
                            cz = candidate.tags.get(category="site_z", return_list=False)
                            if cx and cy and cz and str(cx) == str(int(sx) + dx) and str(cy) == str(int(sy) + dy) and str(cz) == str(int(sz) + dz):
                                target_room = candidate
                                break
                        else:
                            cx = candidate.tags.get(category="planet_x", return_list=False)
                            cy = candidate.tags.get(category="planet_y", return_list=False)
                            cz = candidate.tags.get(category="planet_z", return_list=False)
                            if cx and cy and cz and str(cx) == str(int(px) + dx) and str(cy) == str(int(py) + dy) and str(cz) == str(int(pz) + dz):
                                target_room = candidate
                                break

                    if target_room:
                        room_key_name = target_room.key.lower() if target_room.key.islower() else target_room.key
                        cardinal_matches[direction] = f"{room_key_name} to the {direction}"

            # --- PART B: SCAN VISIBLE PORTAL EXITS IN ROOM CONTENTS ---
            cardinal_exit_directions = {
                "north": "north", "n": "north",
                "south": "south", "s": "south",
                "east": "east", "e": "east",
                "west": "west", "w": "west",
                "northeast": "northeast", "ne": "northeast",
                "northwest": "northwest", "nw": "northwest",
                "southeast": "southeast", "se": "southeast",
                "southwest": "southwest", "sw": "southwest",
                "up": "up", "down": "down",
            }
            for obj in self.contents:
                if obj.destination:
                    key_lower = obj.key.lower()
                    dest = obj.destination
                    dest_name = dest.key.lower() if dest.key.islower() else dest.key
                    is_door = getattr(obj.db, "is_door", False)
                    door_status = ""
                    if is_door:
                        if getattr(obj.db, "is_locked", False):
                            door_status = "locked "
                        elif not getattr(obj.db, "is_open", False):
                            door_status = "closed "
                        else:
                            door_status = "open "

                    if key_lower in ("enter", "in"):
                        inward_portals.append((dest_name, door_status))
                    elif key_lower in ("leave", "out", "exit"):
                        outward_portals.append((dest_name, door_status))
                    elif key_lower in cardinal_exit_directions:
                        direction = cardinal_exit_directions[key_lower]
                        if direction not in cardinal_matches:
                            cardinal_matches[direction] = f"{dest_name} to the {direction}"

            # --- PART C: STITCH UNIFORM ORDER SENTENCE PIECES ---
            neighbor_sentences = []
            
            # Add cardinals in exact clockwise order
            for direction in direction_order:
                if direction in cardinal_matches:
                    neighbor_sentences.append(cardinal_matches[direction])

            # Add inward entrances cleanly grouped together (without trailing 'here')
            if inward_portals:
                if len(inward_portals) == 1:
                    name, status = inward_portals[0]
                    neighbor_sentences.append(f"the {status}entrance to {name}")
                elif len(inward_portals) == 2:
                    n1, s1 = inward_portals[0]
                    n2, s2 = inward_portals[1]
                    neighbor_sentences.append(f"the {s1}entrance to {n1} and the {s2}entrance to {n2}")
                else:
                    parts = [f"the {s}entrance to {n}" for n, s in inward_portals]
                    neighbor_sentences.append(f"entrances to {', '.join(parts[:-1])}, and {parts[-1]}")

            # Add outward exits cleanly grouped together (without trailing 'here')
            if outward_portals:
                if len(outward_portals) == 1:
                    name, status = outward_portals[0]
                    neighbor_sentences.append(f"the {status}exit to {name}")
                elif len(outward_portals) == 2:
                    n1, s1 = outward_portals[0]
                    n2, s2 = outward_portals[1]
                    neighbor_sentences.append(f"the {s1}exit to {n1} and the {s2}exit to {n2}")
                else:
                    parts = [f"the {s}exit to {n}" for n, s in outward_portals]
                    neighbor_sentences.append(f"exits to {', '.join(parts[:-1])}, and {parts[-1]}")

            # --- PART D: BUILD STITCHED LAYOUT WITH SINGLE FINAL 'HERE' ---
            if neighbor_sentences:
                if len(neighbor_sentences) == 1:
                    distance_string = f"\nNearby you can see {neighbor_sentences[0]} here."
                elif len(neighbor_sentences) == 2:
                    distance_string = f"\nNearby you can see {neighbor_sentences[0]} and {neighbor_sentences[1]} here."
                else:
                    distance_string = f"\nNearby you can see {', '.join(neighbor_sentences[:-1])}, and {neighbor_sentences[-1]} here."

        # 4. Inject into description space and populate Evennia's appearance template
        base_desc = self.get_display_desc(looker, **kwargs)
        full_desc = f"{base_desc}{distance_string}"

        return self.format_appearance(
            self.appearance_template.format(
                name=header_name,
                extra_name_info=self.get_extra_display_name_info(looker, **kwargs),
                desc=full_desc,
                header=self.get_display_header(looker, **kwargs),
                footer=self.get_display_footer(looker, **kwargs),
                exits=self.get_display_exits(looker, **kwargs),
                characters=self._grouped_room_contents(looker, **kwargs),
                things="",
            ),
            looker,
            **kwargs,
        )

    def get_display_exits(self, looker, **kwargs):
        """
        Overrides Evennia's default exit block layout to force a strict 
        clockwise sorting rule and cleanly group duplicate structural portals by count.
        """
        visible_exits = [ex for ex in self.contents if ex.destination and ex.access(looker, "view")]
        if not visible_exits:
            return ""

        # Master matrix index to enforce perfect clockwise hierarchy alignment
        sort_matrix = {
            "north": 1, "n": 1,
            "northeast": 2, "ne": 2,
            "east": 3, "e": 3,
            "southeast": 4, "se": 4,
            "south": 5, "s": 5,
            "southwest": 6, "sw": 6,
            "west": 7, "w": 7,
            "northwest": 8, "nw": 8,
            "up": 9, "u": 9,
            "down": 10, "d": 10,
            "enter": 11, "in": 11,
            "leave": 12, "out": 12, "exit": 12
        }

        # Track occurrences of structural portal aliases to group them by count later
        enter_count = 0
        leave_count = 0
        final_exit_tokens = []
        processed_keys = set()

        # Count total structural portal instances currently active in the room contents
        for ex in visible_exits:
            key_lower = ex.key.lower()
            if key_lower in ("enter", "in"):
                enter_count += 1
            elif key_lower in ("leave", "out", "exit"):
                leave_count += 1

        # Sort all available exits by looking up their primary keys against our sort matrix ranking
        sorted_exits = sorted(visible_exits, key=lambda x: sort_matrix.get(x.key.lower(), 100))

        # Build clean string tokens sequentially matching the exact clockwise layout
        for ex in sorted_exits:
            key_lower = ex.key.lower()
            display_name = ex.get_display_name(looker, **kwargs)

            is_door = getattr(ex.db, "is_door", False)
            if is_door:
                if getattr(ex.db, "is_locked", False):
                    display_name += " |w[|rlocked|w]|n"
                elif not getattr(ex.db, "is_open", False):
                    display_name += " |w[|yclosed|w]|n"
                else:
                    display_name += " |w[|gopen|w]|n"

            # Case A: Handle grouped inward entries if multiples exist
            if key_lower in ("enter", "in"):
                if "enter_grouped" in processed_keys:
                    continue
                if enter_count > 1:
                    final_exit_tokens.append(f"{enter_count} places to enter")
                else:
                    final_exit_tokens.append(display_name)
                processed_keys.add("enter_grouped")

            # Case B: Handle grouped outward exits if multiples exist
            elif key_lower in ("leave", "out", "exit"):
                if "leave_grouped" in processed_keys:
                    continue
                if leave_count > 1:
                    final_exit_tokens.append(f"{leave_count} places to leave")
                else:
                    final_exit_tokens.append(display_name)
                processed_keys.add("leave_grouped")

            # Case C: Standard distinct cardinal direction vectors
            else:
                final_exit_tokens.append(display_name)

        # Stitch everything together into a flawless grammatical list string
        if len(final_exit_tokens) == 1:
            return f"|wExits:|n {final_exit_tokens[0]}"
        elif len(final_exit_tokens) == 2:
            return f"|wExits:|n {final_exit_tokens[0]} and {final_exit_tokens[1]}"
        else:
            return f"|wExits:|n {', '.join(final_exit_tokens[:-1])}, and {final_exit_tokens[-1]}"

    def _grouped_room_contents(self, looker, **kwargs):
        """
        List the characters and things the looker can perceive, grouped into a
        single plane section. The section names the realm(s) the looker is in
        and aware of:
            In the (physical), ...
            In the (visarial), ...
            In the (physical and visarial), ...
        The normal / perceiving / manifested states decide which section
        renders: manifesting shows only the visarial, resting shows only the
        physical, and perceiving shows both realms as one combined list.
        Dual-natured objects appear once, in whichever section is shown, since
        they are present in both realms.
        Builders additionally see each character's real name in parentheses.
        """
        from collections import OrderedDict

        chars = [
            char
            for char in self.filter_visible(
                self.contents_get(content_type="character"), looker, **kwargs
            )
            if not hasattr(char, "visible_to") or char.visible_to(looker)
        ]
        things = [
            thing
            for thing in self.filter_visible(
                self.contents_get(content_type="object"), looker, **kwargs
            )
            if not hasattr(thing, "visible_to") or thing.visible_to(looker)
        ]

        visible_planes = []
        if getattr(looker, "can_phys_see", False):
            visible_planes.append("physical")
        if getattr(looker, "can_vis_see", False):
            visible_planes.append("visarial")

        if (not chars and not things) or not visible_planes:
            return ""

        is_builder = looker is not None and self.locks.check_lockstring(
            looker, "perm(Builder)"
        )

        plane_tokens = [
            f"|x{plane}" if plane == "physical" else f"|M{plane}"
            for plane in visible_planes
        ]
        label = f"|w({' and '.join(plane_tokens)}|w)|n"

        furnitures = [
            t for t in things if t.is_typeclass("typeclasses.furniture.Furniture")
        ]
        occupied_furnitures = set()
        for furn in furnitures:
            occupancies = furn.occupied_seats_by_plane()
            if any(set(visible_planes) & planes for planes in occupancies.values()):
                occupied_furnitures.add(furn)

        unoccupied_things = [
            t for t in things
            if not (t.is_typeclass("typeclasses.furniture.Furniture") and t in occupied_furnitures)
        ]

        by_quadrant_pos = OrderedDict()
        for char in chars:
            quadrant = grid_quadrant(self, char.db.pos_x, char.db.pos_y)
            if char.db.is_flying:
                key = (f"in the air above {quadrant}", "flying", None)
            else:
                pose = char.pose or "standing"
                assigned_furn = None
                cx = getattr(char.db, "pos_x", 0)
                cy = getattr(char.db, "pos_y", 0)
                for furn in furnitures:
                    if (cx, cy) in furn.footprint_tiles() and furn.allows_pose(pose):
                        assigned_furn = furn
                        break
                key = (quadrant, pose, assigned_furn)
            by_quadrant_pos.setdefault(key, []).append(char)

        sentences = []
        for index, ((quadrant_or_air, position, furn), pos_chars) in enumerate(
            by_quadrant_pos.items()
        ):
            entries = []
            for char in pos_chars:
                core, _ = char.appearance_bits
                entry = f"{appearance_data.article(core).lower()} {core}"
                if is_builder:
                    entry += f" ({char.name})"
                entries.append(entry)
            lead = "there's" if index == 0 else "There's also"

            if furn:
                furn_name = furn.get_display_name(looker, **kwargs)
                if len(pos_chars) > 1:
                    phrase = f"{position} together on {furn_name} in {quadrant_or_air}"
                else:
                    phrase = f"{position} on {furn_name} in {quadrant_or_air}"
            else:
                phrase = (
                    f"{position} {quadrant_or_air}"
                    if position == "flying"
                    else f"{position} in {quadrant_or_air}"
                )
            sentences.append(
                f"{lead} {iter_to_str(entries, endsep=', and')} {phrase} here."
            )

        if unoccupied_things:
            things_sentence = f"you see {self._things_list(unoccupied_things, looker, **kwargs)}."
            if sentences:
                things_sentence = things_sentence[0].upper() + things_sentence[1:]
            sentences.append(things_sentence)

        return f"In the {label}, {' '.join(sentences)}"

    def _things_list(self, things, looker, **kwargs):
        """Join one plane's things into a clean, counted list, each tagged
        with its grid quadrant."""
        from collections import OrderedDict

        grouped = OrderedDict()
        for thing in things:
            name = thing.get_display_name(looker, **kwargs)
            facing = getattr(thing.db, "facing", None)
            if facing:
                name += f" (facing {facing})"
            quadrant = grid_quadrant(self, thing.db.pos_x, thing.db.pos_y)
            grouped.setdefault((quadrant, name), []).append(thing)

        entries = []
        for (quadrant, name), lst in grouped.items():
            thing = lst[0]
            nthings = len(lst)
            singular, plural = thing.get_numbered_name(nthings, looker, key=thing.key)
            facing = getattr(thing.db, "facing", None)
            if facing:
                singular += f" (facing {facing})"
                plural = f"{nthings} {thing.key}s (facing {facing})"
            label = singular if nthings == 1 else plural
            entries.append(f"{label} in {quadrant}")
        return iter_to_str(entries, endsep=", and")
