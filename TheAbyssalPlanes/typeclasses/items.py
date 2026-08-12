from evennia import AttributeProperty
from evennia.utils.utils import iter_to_str
from evennia.utils.ansi import strip_ansi
from .furniture import Furniture
from world.data import appearance as appearance_data
from world.data import colors as colors_data


class Item(Furniture):
    """
    General item class supporting multi-material truecolor descriptions, adjectives,
    and item-type specific behaviors (like Furniture).
    """

    item_type = AttributeProperty(default="furniture")
    base_name = AttributeProperty(default="item")
    materials = AttributeProperty(default=[])  # list of [material_name, color_key]
    item_adjective = AttributeProperty(default=None)

    def get_display_name(self, looker=None, **kwargs):
        """
        Dynamic description format:
        a <material 1 colored>, <material 2 colored>, [and] <adjective> <base_name>
        Materials are sorted alphabetically. Color is applied directly to the material name.
        """
        mats = list(self.materials or [])
        mats.sort(key=lambda m: m[0])

        mat_strings = []
        for mat_name, col_key in mats:
            hexcol = colors_data.hex_for_color(col_key) or ""
            if hexcol:
                colored_mat = f"|{hexcol}{mat_name}|n"
            else:
                colored_mat = mat_name
            mat_strings.append(colored_mat)

        mat_part = ""
        if mat_strings:
            mat_part = iter_to_str(mat_strings, endsep=", and")

        adj = self.item_adjective or ""
        base = self.base_name or self.key

        parts = []
        if mat_part:
            parts.append(mat_part)
        if adj:
            parts.append(adj)
        parts.append(base)

        combined = " ".join(parts)
        clean_combined = strip_ansi(combined)
        art = appearance_data.article(clean_combined).lower()
        return f"{art} {combined}"

    def get_numbered_name(self, count, looker=None, key=None, **kwargs):
        name = self.get_display_name(looker, **kwargs)
        if kwargs.get("return_string"):
            return name
        return name, name
