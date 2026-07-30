"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.search import search_tag
from evennia.utils.utils import iter_to_str
from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None.
    Modified to dynamically display surrounding grid room names on look.
    """

    def at_object_creation(self):
        """Called only once, when the room object is first created."""
        super().at_object_creation()
        self.db.visarial_desc = ""

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
                        
                        cs = str(candidate.tags.get(category="planetary_site", return_list=False)).lower()
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
            for obj in self.contents:
                if obj.destination:
                    key_lower = obj.key.lower()
                    dest = obj.destination
                    dest_name = dest.key.lower() if dest.key.islower() else dest.key
                    
                    if key_lower in ("enter", "in"):
                        inward_portals.append(dest_name)
                    elif key_lower in ("leave", "out", "exit"):
                        outward_portals.append(dest_name)

            # --- PART C: STITCH UNIFORM ORDER SENTENCE PIECES ---
            neighbor_sentences = []
            
            # Add cardinals in exact clockwise order
            for direction in direction_order:
                if direction in cardinal_matches:
                    neighbor_sentences.append(cardinal_matches[direction])

            # Add inward entrances cleanly grouped together (without trailing 'here')
            if inward_portals:
                if len(inward_portals) == 1:
                    neighbor_sentences.append(f"an entrance to {inward_portals[0]}")
                elif len(inward_portals) == 2:
                    neighbor_sentences.append(f"entrances to {inward_portals[0]} and {inward_portals[1]}")
                else:
                    numbered_in = [f"密[{i+1}] {name}" for i, name in enumerate(inward_portals)]
                    neighbor_sentences.append(f"entrances to {', '.join(numbered_in[:-1])}, and {numbered_in[-1]}")

            # Add outward exits cleanly grouped together (without trailing 'here')
            if outward_portals:
                if len(outward_portals) == 1:
                    neighbor_sentences.append(f"an exit out to {outward_portals[0]}")
                elif len(outward_portals) == 2:
                    neighbor_sentences.append(f"exits out to {outward_portals[0]} and {outward_portals[1]}")
                else:
                    numbered_out = [f"[{i+1}] {name}" for i, name in enumerate(outward_portals)]
                    neighbor_sentences.append(f"exits out to {', '.join(numbered_out[:-1])}, and {numbered_out[-1]}")

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
                characters=self.get_display_characters(looker, **kwargs),
                things=self.get_display_things(looker, **kwargs),
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

    def _match_visarial(self, looker, obj):
        state = looker.attributes.get("visarial_state", default="physical")
        nature = obj.attributes.get("visarial_nature", default="dual_natured")
        if state == "physical":
            return nature in ("physical", "dual_natured")
        elif state == "perceiving":
            return True
        return nature in ("visarial", "dual_natured")

    def get_display_characters(self, looker, **kwargs):
        characters = self.filter_visible(
            self.contents_get(content_type="character"), looker, **kwargs
        )
        characters = [char for char in characters if self._match_visarial(looker, char)]
        character_names = iter_to_str(
            (char.get_display_name(looker, **kwargs) for char in characters),
            endsep=", and",
        )
        return f"|wCharacters:|n {character_names}" if character_names else ""

    def get_display_things(self, looker, **kwargs):
        from collections import defaultdict
        from evennia.utils import ansi

        things = self.filter_visible(
            self.contents_get(content_type="object"), looker, **kwargs
        )
        things = [thing for thing in things if self._match_visarial(looker, thing)]

        grouped_things = defaultdict(list)
        for thing in things:
            grouped_things[thing.get_display_name(looker, **kwargs)].append(thing)

        thing_names = []
        for thingname, thinglist in sorted(grouped_things.items()):
            nthings = len(thinglist)
            thing = thinglist[0]
            base_key = thing.key
            raw = str(thingname)
            pos = raw.rfind(base_key)
            colored_tag = raw[:pos] if pos >= 0 else ""
            singular, plural = thing.get_numbered_name(nthings, looker, key=base_key)
            numbered_name = singular if nthings == 1 else plural
            thing_names.append(colored_tag + numbered_name)
        thing_names = iter_to_str(thing_names, endsep=", and")
        return f"|wYou see:|n {thing_names}" if thing_names else ""
