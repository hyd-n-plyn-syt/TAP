"""
Custom Dig Command for Double-Tier Grid Mapping.
Handles planet_x/y/z and site_x/y/z coordinate structures.
"""
from evennia.commands.default.building import CmdDig
from evennia import search_object

class GridDig(CmdDig):
    """
    build new rooms and connect them to the current location

    Usage:
      dig[/switches] <roomname>[;alias;alias...][:typeclass]
            [= <exit_to_there>[;alias][:typeclass]]
               [, <exit_to_here>[;alias][:typeclass]]

    Switches:
       tel or teleport - move yourself to the new room

    Examples:
       # Standard expansion on the open planet surface (shifts planet_x/y/z):
       dig North Plains = north;n, south;s

       # Digging into a new subzone/city (freezes planet grid, starts site_x/y/z at 0,0,0):
       dig City of Brass = enter;in, leave;out

       # Standard expansion inside a subzone (shifts site_x/y/z only; keeps planet flags):
       dig Market Square = east;e, west;w

       # Linking an exit back out to the pre-existing planet surface room:
       dig planetary_body = leave;out
    """

    def func(self):
        """ Do the digging, calculate coordinates, and apply tags. """
        caller = self.caller
        location = caller.location
        
        # 1. Grab raw identity and coordinate tags from the origin location room
        orig_body = location.tags.get(category="planetary_body", return_list=False)
        orig_site = location.tags.get(category="planetary_site", return_list=False)

        orig_px = location.tags.get(category="planet_x", return_list=False)
        orig_py = location.tags.get(category="planet_y", return_list=False)
        orig_pz = location.tags.get(category="planet_z", return_list=False)

        orig_sx = location.tags.get(category="site_x", return_list=False)
        orig_sy = location.tags.get(category="site_y", return_list=False)
        orig_sz = location.tags.get(category="site_z", return_list=False)

        if not self.lhs:
            string = "Usage: dig[/teleport] <roomname>[;alias;alias...][:parent] [= <exit_there>"
            string += "[;alias;alias..][:parent]] "
            string += "[, <exit_back_here>[;alias;alias..][:parent]]"
            caller.msg(string)
            return

        room = self.lhs_objs[0]
        if not room["name"]:
            caller.msg("You must supply a target room name.")
            return

        body = str(orig_body) if orig_body else "None"
        site = str(orig_site) if orig_site else "None"
        px, py, pz = str(orig_px), str(orig_py), str(orig_pz)
        sx, sy, sz = str(orig_sx), str(orig_sy), str(orig_sz)

        # Extract exit name typed by the builder from the list safely
        exit_dir = ""
        if self.rhs_objs:
            to_exit = self.rhs_objs[0]
            if to_exit["name"]:
                exit_dir = to_exit["name"].strip().lower()

        # --- OUTWARD TRANSITION LOGIC (PUNCHING OUT TO SURFACE) ---
        if exit_dir in ("leave", "out", "exit"):
            target_planet = room["name"].strip().lower()
            
            # Fix: Import search_tag to query database purely by the 5D tag index layout
            from evennia.utils.search import search_tag
            
            # Find any room using the Room typeclass that possesses ALL 5 coordinate tag keys
            candidates = search_tag(tag=target_planet, category="planetary_body")
            target_surface_room = None
            
            for candidate in candidates:
                # Filter down to find the specific one that also matches our location flags
                if candidate.typeclass_path != "typeclasses.rooms.Room":
                    continue
                cb = candidate.tags.get(category="planetary_body", return_list=False)
                cs = candidate.tags.get(category="planetary_site", return_list=False)
                cpx = candidate.tags.get(category="planet_x", return_list=False)
                cpy = candidate.tags.get(category="planet_y", return_list=False)
                cpz = candidate.tags.get(category="planet_z", return_list=False)
                
                if (str(cb).lower() == target_planet and str(cs).lower() == "none" and 
                    str(cpx) == px and str(cpy) == py and str(cpz) == pz):
                    target_surface_room = candidate
                    break
            
            if not target_surface_room:
                caller.msg(f"|r[GRID-DIG] Error: Could not find a surface room on body '{target_planet}' at physical coordinates ({px}, {py}, {pz}).|n")
                return

            # Create only the exit leading out to the discovered surface room
            exit_typeclass, errors = self.get_object_typeclass(
                obj_type="exit", typeclass=to_exit["option"], method=self.method_type
            )
            if errors: self.msg("|rError creating exit:|n %s" % errors); return
            
            new_to_exit, errors = exit_typeclass.create(
                to_exit["name"],
                location=location,
                destination=target_surface_room,
                aliases=to_exit["aliases"],
                report_to=caller,
                caller=caller,
                method=self.method_type,
            )
            if new_to_exit:
                caller.msg(f"|g[GRID-DIG SUCCESS] Connected outward exit '{new_to_exit.name}' directly to pre-existing surface room: {target_surface_room.name} (#{target_surface_room.id}) at ({px}, {py}, {pz}) on {target_planet}.|n")
            
            if "teleport" in self.switches:
                caller.move_to(target_surface_room, move_type="teleport")
            return

        # --- STANDARD CREATION LOGIC PATHWAYS (GENERATING A NEW ROOM) ---
        # Create room via native initializer
        room_typeclass, errors = self.get_object_typeclass(
            obj_type="room", typeclass=room["option"], method=self.method_type
        )
        if errors: self.msg("|rError creating room:|n %s" % errors); return
        new_room, errors = room_typeclass.create(
            room["name"], aliases=room["aliases"], report_to=caller, caller=caller, method=self.method_type,
        )
        if errors: self.msg("|rError creating room:|n %s" % errors); return
        if not new_room: return

        # AUTOMATIC STANDALONE ORIGIN RULE: No exits specified at all
        if not self.rhs_objs:
            body = room["name"].lower().replace(" ", "_")
            site = "None"
            px, py, pz = "0", "0", "0"
            sx, sy, sz = "None", "None", "None"
            caller.msg(f"|y[GRID-DIG] No exits specified. Automatically initializing room as standalone grid origin for body '{body}' at (0,0,0)!|n")

        # TRANSITION PATHWAY A: Entering a brand-new subzone from the main surface
        elif exit_dir in ("enter", "in"):
            site = str(room["name"])
            sx, sy, sz = "0", "0", "0"
            caller.msg(f"|y[GRID-DIG] Instantiating subzone! Site Name set to: '{site}' at local (0,0,0).|n")

        # TRANSITION PATHWAY C: Standard map navigation adjustments
        else:
            if site.lower() != "none":
                isx = int(sx) if sx.lower() != "none" else 0
                isy = int(sy) if sy.lower() != "none" else 0
                isz = int(sz) if sz.lower() != "none" else 0
                if exit_dir in ("north", "n"): isy += 1
                elif exit_dir in ("south", "s"): isy -= 1
                elif exit_dir in ("east", "e"): isx += 1
                elif exit_dir in ("west", "w"): isx -= 1
                elif exit_dir in ("up", "u"): isz += 1
                elif exit_dir in ("down", "d"): isz -= 1
                sx, sy, sz = str(isx), str(isy), str(isz)
            else:
                if px.lower() != "none" and py.lower() != "none" and pz.lower() != "none":
                    ipx, ipy, ipz = int(px), int(py), int(pz)
                    if exit_dir in ("north", "n"): ipy += 1
                    elif exit_dir in ("south", "s"): ipy -= 1
                    elif exit_dir in ("east", "e"): ipx += 1
                    elif exit_dir in ("west", "w"): ipx -= 1
                    elif exit_dir in ("up", "u"): ipz += 1
                    elif exit_dir in ("down", "d"): ipz -= 1
                    px, py, pz = str(ipx), str(ipy), str(ipz)


        # Wipe out default tags from the new room
        new_room.tags.clear(category="planetary_body")
        new_room.tags.clear(category="planetary_site")
        new_room.tags.clear(category="planet_x")
        new_room.tags.clear(category="planet_y")
        new_room.tags.clear(category="planet_z")
        new_room.tags.clear(category="site_x")
        new_room.tags.clear(category="site_y")
        new_room.tags.clear(category="site_z")

        # Stamp the parameters
        new_room.tags.add(body, category="planetary_body")
        new_room.tags.add(site, category="planetary_site")
        new_room.tags.add(px, category="planet_x")
        new_room.tags.add(py, category="planet_y")
        new_room.tags.add(pz, category="planet_z")
        new_room.tags.add(sx, category="site_x")
        new_room.tags.add(sy, category="site_y")
        new_room.tags.add(sz, category="site_z")

        caller.msg(
            f"|g[GRID-DIG SUCCESS]\n"
            f"Identity: Body={body}, Site={site}\n"
            f"Global Planet Grid: ({px}, {py}, {pz})\n"
            f"Local Site Grid:   ({sx}, {sy}, {sz})|n"
        )

        # [Native Exit Creation Logic Parsing]
        if self.rhs_objs:
            to_exit = self.rhs_objs[0]
            if to_exit["name"] and location:
                exit_typeclass, errors = self.get_object_typeclass(obj_type="exit", typeclass=to_exit["option"], method=self.method_type)
                new_to_exit, errors = exit_typeclass.create(to_exit["name"], location=location, destination=new_room, aliases=to_exit["aliases"], report_to=caller, caller=caller, method=self.method_type)
                if new_to_exit: caller.msg(f"Created Exit: {new_to_exit.name} -> {new_room.name}")

        if len(self.rhs_objs) > 1:
            back_exit = self.rhs_objs[1]
            if back_exit["name"] and location:
                exit_typeclass, errors = self.get_object_typeclass(obj_type="exit", typeclass=back_exit["option"], method=self.method_type)
                if errors:
                    self.msg("|rError creating exit:|n %s" % errors)
                if not exit_typeclass:
                    return
                new_back_exit, errors = exit_typeclass.create(
                    back_exit["name"],
                    location=new_room,
                    destination=location,
                    aliases=back_exit["aliases"],
                    report_to=caller,
                    caller=caller,
                    method=self.method_type,
                )
                if errors:
                    self.msg("|rError creating exit:|n %s" % errors)
                if not new_back_exit:
                    return
                if new_back_exit: 
                    caller.msg(f"Created Back Exit: {new_back_exit.name} -> {location.name}")

        if "teleport" in self.switches:
            caller.move_to(new_room, move_type="teleport")
