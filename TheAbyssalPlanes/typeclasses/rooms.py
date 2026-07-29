"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def at_object_creation(self):
        """Called only once, when the room object is first created."""
        super().at_object_creation()
        
        # Initialize the 5 parameters as unplaced "None" tags directly onto the base room
        self.tags.add("None", category="coord_x")
        self.tags.add("None", category="coord_y")
        self.tags.add("None", category="coord_z")
        self.tags.add("None", category="coord_p")
        self.tags.add("None", category="coord_b")
