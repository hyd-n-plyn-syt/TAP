from evennia import AttributeProperty
from evennia.objects.objects import DefaultObject
from evennia.utils.utils import iter_to_str
from .objects import ObjectParent
from world.data import appearance as appearance_data
from combat.grid import is_valid_coord
from combat.movement import is_grid_occupied

CARDINAL_OFFSETS = {
    "north": (0, 1),
    "south": (0, -1),
    "east": (1, 0),
    "west": (-1, 0),
}


class Furniture(ObjectParent, DefaultObject):
    """
    Furniture objects (beds, chairs, sofas, bedrolls) that characters can sit,
    rest, lay, or sleep on, with quality ratings that boost healing rates.
    """

    quality = AttributeProperty(default=1.0)
    occupies_space = AttributeProperty(default=True)
    seats = AttributeProperty(default=1)
    dimension = AttributeProperty(default="1x1")
    allowed_states = AttributeProperty(default=["sit", "rest", "lay", "sleep", "resting", "laying", "sleeping"])
    color = AttributeProperty(default="|D")
    facing = AttributeProperty(default="north")
    extra_coords = AttributeProperty(default=[])

    def get_display_name(self, looker=None, **kwargs):
        name = self.key
        art = appearance_data.article(name).lower()
        return f"{art} {name}"

    def get_numbered_name(self, count, looker=None, key=None, **kwargs):
        name = self.get_display_name(looker, **kwargs)
        if count == 1:
            if kwargs.get("return_string"):
                return name
            return name, name
        plural = f"{count} {self.key}s"
        if kwargs.get("return_string"):
            return plural
        return name, plural

    def at_object_creation(self):
        super().at_object_creation()
        self.db.pos_x = 0
        self.db.pos_y = 0
        self.db.pos_z = 1
        self.calculate_footprint()

    def is_at_coord(self, x, y):
        """Return True if (x, y) is occupied by this furniture's footprint."""
        px = getattr(self.db, "pos_x", None)
        py = getattr(self.db, "pos_y", None)
        if px == x and py == y:
            return True
        for ex, ey in (self.db.extra_coords or []):
            if ex == x and ey == y:
                return True
        return False

    def _test_footprint(self, room, px, py, facing, ignore_char=None):
        """Test if footprint is valid. Characters do not block furniture placement; only non-character objects do."""
        dim = self.dimension or f"1x{self.seats}"
        dx, dy = CARDINAL_OFFSETS.get(facing, (0, 1))

        if dim == "2x2":
            orth_dx, orth_dy = (-dy, dx)
            tiles = [
                (px, py),
                (px + dx, py + dy),
                (px + orth_dx, py + orth_dy),
                (px + dx + orth_dx, py + dy + orth_dy),
            ]
            for tx, ty in tiles:
                if not is_valid_coord(room, tx, ty):
                    return False
                occupants = is_grid_occupied(room, tx, ty, ignore=(self, ignore_char))
                for occ in occupants:
                    if not getattr(occ, "is_creature", False):
                        return False
            return True
        else:
            length = int(dim.split("x")[1]) if "x" in dim else max(1, self.seats)
            cx, cy = px, py
            for i in range(length):
                tx, ty = (px, py) if i == 0 else (cx + dx, cy + dy)
                if i > 0:
                    cx, cy = tx, ty
                if not is_valid_coord(room, tx, ty):
                    return False
                occupants = is_grid_occupied(room, tx, ty, ignore=(self, ignore_char))
                for occ in occupants:
                    if not getattr(occ, "is_creature", False):
                        return False
            return True

    def calculate_footprint(self):
        """Calculate extra coordinates occupied based on dimension/seats and facing."""
        room = self.location
        if not room:
            self.db.extra_coords = []
            return True

        dim = self.dimension or f"1x{self.seats}"
        px = getattr(self.db, "pos_x", 0)
        py = getattr(self.db, "pos_y", 0)
        dx, dy = CARDINAL_OFFSETS.get(self.facing, (0, 1))

        if dim == "2x2":
            orth_dx, orth_dy = (-dy, dx)
            tiles = [
                (px + dx, py + dy),
                (px + orth_dx, py + orth_dy),
                (px + dx + orth_dx, py + dy + orth_dy),
            ]
            self.db.extra_coords = tiles
            return True
        else:
            length = int(dim.split("x")[1]) if "x" in dim else max(1, self.seats)
            if length <= 1:
                self.db.extra_coords = []
                return True

            extras = []
            cx, cy = px, py
            for _ in range(length - 1):
                cx += dx
                cy += dy
                extras.append((cx, cy))
            self.db.extra_coords = extras
            return True

    def at_pre_move(self, destination, move_type="move", **kwargs):
        super().at_pre_move(destination, move_type=move_type, **kwargs)
        if self.location and self.location.is_typeclass("typeclasses.characters.Character") and destination.is_typeclass("typeclasses.rooms.Room"):
            room = destination
            dropper = self.location
            px = getattr(dropper.db, "pos_x", 0)
            py = getattr(dropper.db, "pos_y", 0)

            success = False
            directions = ["north", "east", "south", "west"]
            facing_list = [self.facing] + [d for d in directions if d != self.facing]

            for f in facing_list:
                if self._test_footprint(room, px, py, f, ignore_char=dropper):
                    self.facing = f
                    self.db.pos_x = px
                    self.db.pos_y = py
                    self.db.pos_z = getattr(dropper.db, "pos_z", 1)
                    success = True
                    break

            if not success:
                dropper.msg("There is no clear space to place this furniture here.")
                return False
        return True

    def at_post_move(self, source_location, move_type="move", **kwargs):
        super().at_post_move(source_location, move_type=move_type, **kwargs)
        if not source_location or not self.location:
            return
        if source_location.is_typeclass("typeclasses.characters.Character") and self.location.is_typeclass("typeclasses.rooms.Room"):
            room = self.location
            dropper = source_location
            self.calculate_footprint()

            all_tiles = [(self.db.pos_x, self.db.pos_y)] + list(self.db.extra_coords or [])
            seated_chars = []
            for tx, ty in all_tiles:
                occupants = [
                    obj for obj in room.contents
                    if getattr(obj, "is_creature", False)
                    and getattr(obj.db, "pos_x", None) == tx
                    and getattr(obj.db, "pos_y", None) == ty
                ]
                for char in occupants:
                    old_loc, old_x, old_y, old_z = char.location, char.db.pos_x, char.db.pos_y, char.db.pos_z
                    char.db.pos_x = tx
                    char.db.pos_y = ty
                    char.set_pose("sitting")
                    char.check_autowhere(old_loc, old_x, old_y, old_z)
                    if char not in seated_chars:
                        seated_chars.append(char)

            if dropper not in seated_chars:
                fx, fy = all_tiles[0]
                old_loc, old_x, old_y, old_z = dropper.location, dropper.db.pos_x, dropper.db.pos_y, dropper.db.pos_z
                dropper.db.pos_x = fx
                dropper.db.pos_y = fy
                dropper.set_pose("sitting")
                dropper.check_autowhere(old_loc, old_x, old_y, old_z)
                seated_chars.append(dropper)

            self.db._drop_action = "and sit down on it"

    def rotate(self):
        """Rotate furniture to the next cardinal direction, if valid and unoccupied."""
        room = self.location
        dim = self.dimension or f"1x{self.seats}"
        if not room or (dim == "1x1" and self.seats <= 1):
            return False, "This furniture cannot be rotated."

        directions = ["north", "east", "south", "west"]
        current_idx = directions.index(self.facing) if self.facing in directions else 0
        px = getattr(self.db, "pos_x", 0)
        py = getattr(self.db, "pos_y", 0)

        for i in range(1, 5):
            new_facing = directions[(current_idx + i) % 4]
            if self._test_footprint(room, px, py, new_facing):
                self.facing = new_facing
                self.calculate_footprint()
                return True, f"You rotate {self.get_display_name()} to face {new_facing}."

        return False, "There is no clear space to rotate this furniture."
