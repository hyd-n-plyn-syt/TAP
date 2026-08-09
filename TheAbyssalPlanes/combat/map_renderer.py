"""
Map Renderer for the movement grid.
"""
from combat.grid import grid_quadrant, get_room_grid_size, get_room_floor_z, get_exit_coords
from world.systems.hostility import hostile_towards

def get_symbol_and_color(obj, looker):
    if obj == looker: return "@", "|c"
    # Check explicitly for the hostiltiy flag
    if hostile_towards(looker, obj): return "H", "|r"
    if obj.is_typeclass("typeclasses.characters.Character"): return "@", "|C"
    if obj.destination: return "+", "|g"
    if obj.is_typeclass("typeclasses.objects.Object"): return "X", "|D"
    return "#", "|n"

def render_map(looker):
    room = looker.location
    size = get_room_grid_size(room)
    cx, cy = looker.db.pos_x or 0, looker.db.pos_y or 0
    
    account = looker.account if hasattr(looker, "account") else looker
    radius = (account.attributes.get("map_size", default=15)) // 2
    view_size = radius * 2 + 1
    
    row_width = 2 * view_size
    frame = f"|Y/{'=' * (row_width + 1)}\\|n"
    bottom_frame = f"|Y\\{'=' * (row_width + 1)}/|n"
    
    exit_map = {}
    for obj in room.contents:
        if obj.destination:
            coords = get_exit_coords(room, obj)
            if coords:
                exit_map[coords] = obj
    
    output = [frame]
    for iy in range(cy + radius, cy - radius - 1, -1):
        row = ["|Y| |n"]
        for ix in range(cx - radius, cx + radius + 1):
            sym, col = " ", "|n"
            if 0 <= ix < size and 0 <= iy < size:
                sym, col = "#", "|n"
                tile_obj = None
                for obj in room.contents:
                    if obj.destination: continue
                    if getattr(obj.db, "pos_x", None) == ix and getattr(obj.db, "pos_y", None) == iy:
                        if obj == looker:
                            tile_obj = obj
                            break
                        if not tile_obj or (hostile_towards(looker, obj) and not hostile_towards(looker, tile_obj)):
                            tile_obj = obj
                if not tile_obj and (ix, iy) in exit_map and (ix, iy) != (0, 0):
                    tile_obj = exit_map[(ix, iy)]
                if tile_obj:
                    sym, col = get_symbol_and_color(tile_obj, looker)
            row.append(f"{col}{sym} |n")
        row.append("|Y| |n")
        output.append("".join(row))
    output.append(bottom_frame)
    return "\n".join(output)
