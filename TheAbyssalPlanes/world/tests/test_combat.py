from django.test import SimpleTestCase
from combat.grid import (
    DIRECTION_OFFSETS,
    exit_direction,
    get_entry_coords,
    get_exit_coords,
    get_room_floor_z,
    get_room_grid_size,
    get_room_max_z,
    grid_quadrant,
)
from combat.movement import (
    announce_grid_arrival,
    announce_grid_move,
    describe_nav_target,
    get_move_allowance,
    is_grid_occupied,
    mover_arrival_message,
    mover_start_message,
    nav_eta,
)
from world.systems.group import GroupManager
from world.systems.tactical import opposed_test
from world.tests._mock import MockChar


class MockExit:
    key = "north"
    destination = object()

    def __init__(self, key="north"):
        self.key = key
        self.aliases = type("Aliases", (), {"all": lambda self: []})()


class MockRoom:
    def __init__(self, room_size="small"):
        self.db = type("db", (), {"room_size": room_size})()
        self.contents = []


class MockOccupant:
    def __init__(self, x, y, key="thing", appearance_name=None):
        self.key = key
        self.appearance_name = appearance_name
        self.db = type("db", (), {"pos_x": x, "pos_y": y})()


class GridHelpersTest(SimpleTestCase):
    def test_direction_offsets(self):
        self.assertEqual(DIRECTION_OFFSETS["north"], (0, 1, 0))
        self.assertEqual(DIRECTION_OFFSETS["nw"], (-1, 1, 0))
        self.assertEqual(DIRECTION_OFFSETS["up"], (0, 0, 1))
        self.assertEqual(DIRECTION_OFFSETS["down"], (0, 0, -1))

    def test_quadrant_northwest(self):
        self.assertEqual(
            grid_quadrant(MockRoom(room_size="large"), 0, 10),
            "the northwest portion of the area",
        )

    def test_quadrant_southeast(self):
        self.assertEqual(
            grid_quadrant(MockRoom(room_size="large"), 10, 0),
            "the southeast portion of the area",
        )

    def test_quadrant_plain_north(self):
        self.assertEqual(
            grid_quadrant(MockRoom(room_size="large"), 5, 10),
            "the northern portion of the area",
        )

    def test_quadrant_center(self):
        self.assertEqual(
            grid_quadrant(MockRoom(room_size="large"), 5, 5),
            "the center of the area",
        )

    def test_quadrant_none_coords(self):
        self.assertEqual(
            grid_quadrant(MockRoom(room_size="large"), None, None),
            "the center of the area",
        )

    def test_floor_z_default(self):
        self.assertEqual(get_room_floor_z(MockRoom()), 1)

    def test_floor_z_builder_override(self):
        room = MockRoom()
        room.db.floor_z = 0
        self.assertEqual(get_room_floor_z(room), 0)

    def test_max_z_defaults_to_grid_size(self):
        self.assertEqual(get_room_max_z(MockRoom(room_size="small")), 3)
        self.assertEqual(get_room_max_z(MockRoom(room_size="large")), 11)

    def test_max_z_builder_override(self):
        room = MockRoom(room_size="large")
        room.db.max_z = 4
        self.assertEqual(get_room_max_z(room), 4)

class CombatSystemTest(SimpleTestCase):
    def test_grid_mapping(self):
        self.assertEqual(get_entry_coords(MockRoom(), "north"), (1, 2))
        self.assertEqual(get_room_grid_size(MockRoom()), (3, 3))

    def test_move_allowance_halving(self):
        self.assertEqual(get_move_allowance(0), 6)
        self.assertEqual(get_move_allowance(1), 3)
        self.assertEqual(get_move_allowance(2), 1)
        self.assertEqual(get_move_allowance(3), 0)

    def test_grid_occupancy(self):
        room = MockRoom()
        self.assertFalse(is_grid_occupied(room, 0, 0))

    def test_group_invite(self):
        char1 = MockChar()
        char2 = MockChar()
        GroupManager.invite(char1, char2)
        self.assertEqual(char1.db.group_invite, char2)

    def test_opposed_test(self):
        char1 = MockChar()
        char2 = MockChar()
        self.assertTrue(opposed_test(char1, char2, "ram", "resist"))

    def test_exit_direction(self):
        self.assertEqual(exit_direction(MockExit("north")), "north")
        self.assertEqual(exit_direction(MockExit("east")), "east")
        self.assertIsNone(exit_direction(MockExit("door")))

    def test_exit_coords(self):
        self.assertEqual(get_exit_coords(MockRoom(), MockExit("north")), (1, 2))
        self.assertIsNone(get_exit_coords(MockRoom(), MockExit("door")))


class NavTargetTest(SimpleTestCase):
    """describe_nav_target phrase selection for observer movement messages."""

    def setUp(self):
        self.room = MockRoom(room_size="large")
        self.room.contents = []

    def test_quadrant_northwest(self):
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1}
        self.assertEqual(
            describe_nav_target(self.room, nav),
            "the northwest portion of the area",
        )

    def test_quadrant_southeast(self):
        nav = {"dest_x": 10, "dest_y": 0, "dest_z": 1}
        self.assertEqual(
            describe_nav_target(self.room, nav),
            "the southeast portion of the area",
        )

    def test_quadrant_plain_north(self):
        nav = {"dest_x": 5, "dest_y": 10, "dest_z": 1}
        self.assertEqual(
            describe_nav_target(self.room, nav),
            "the northern portion of the area",
        )

    def test_center(self):
        nav = {"dest_x": 5, "dest_y": 5, "dest_z": 1}
        self.assertEqual(
            describe_nav_target(self.room, nav),
            "the center of the area",
        )

    def test_occupant_appearance(self):
        occupant = MockOccupant(2, 3, appearance_name="A tall Visarii")
        self.room.contents = [occupant]
        nav = {"dest_x": 2, "dest_y": 3, "dest_z": 1}
        self.assertEqual(describe_nav_target(self.room, nav), "A tall Visarii")

    def test_occupant_key_fallback(self):
        occupant = MockOccupant(2, 3, key="a stone")
        self.room.contents = [occupant]
        nav = {"dest_x": 2, "dest_y": 3, "dest_z": 1}
        self.assertEqual(describe_nav_target(self.room, nav), "a stone")

    def test_vertical_up_target(self):
        mover = type("M", (), {"db": type("db", (), {"pos_z": 1})()})()
        nav = {"dest_x": 0, "dest_y": 0, "dest_z": 2}
        self.assertEqual(
            describe_nav_target(self.room, nav, mover=mover), "the air above"
        )

    def test_vertical_down_target(self):
        mover = type("M", (), {"db": type("db", (), {"pos_z": 3})()})()
        nav = {"dest_x": 0, "dest_y": 0, "dest_z": 2}
        self.assertEqual(
            describe_nav_target(self.room, nav, mover=mover), "the area below"
        )

    def test_vertical_target_without_mover_falls_back_to_quadrant(self):
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 2}
        self.assertEqual(
            describe_nav_target(self.room, nav), "the northwest portion of the area"
        )


class AnnounceGridMoveTest(SimpleTestCase):
    """announce_grid_move realm-gating of in-room movement messages."""

    class _MsgChar(MockChar):
        is_creature = True

        def __init__(self, name, plane="physical"):
            super().__init__()
            self.name = name
            self._messages = []
            self._can_see = True

        def msg(self, text, from_obj=None, **kwargs):
            self._messages.append(text)

        def visible_to(self, looker):
            return looker._can_see

    def test_observers_get_message(self):
        mover = self._MsgChar("mover")
        seer = self._MsgChar("seer")
        mover.appearance_name = "A tall Visarii"
        mover.location = None
        seer.location = None
        room = MockRoom(room_size="large")
        room.contents = [mover, seer]
        mover.location = room
        seer.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        announce_grid_move(mover, nav)
        self.assertEqual(seer._messages, ["A tall Visarii moves toward the northwest portion of the area."])
        self.assertEqual(mover._messages, [])

    def test_blind_observer_gets_nothing(self):
        mover = self._MsgChar("mover")
        blind = self._MsgChar("blind")
        mover.appearance_name = "A tall Visarii"
        blind._can_see = False
        room = MockRoom(room_size="large")
        room.contents = [mover, blind]
        mover.location = room
        blind.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        announce_grid_move(mover, nav)
        self.assertEqual(blind._messages, [])


class MoverMessageTest(SimpleTestCase):
    """mover_start_message / mover_arrival_message / nav_eta mover feedback."""

    class _MsgChar(MockChar):
        def __init__(self, x, y):
            super().__init__()
            self.db.pos_x = x
            self.db.pos_y = y
            self.appearance_name = "A tall Visarii"

    def test_eta_single_round(self):
        nav = {"dest_x": 3, "dest_y": 4}
        self.assertEqual(nav_eta(nav, 0, 0), 4)

    def test_eta_full_round_pause(self):
        nav = {"dest_x": 6, "dest_y": 0}
        self.assertEqual(nav_eta(nav, 0, 0), 6)

    def test_eta_zero(self):
        nav = {"dest_x": 2, "dest_y": 2}
        self.assertEqual(nav_eta(nav, 2, 2), 0)

    def test_start_message_quadrant(self):
        mover = self._MsgChar(0, 0)
        room = MockRoom(room_size="large")
        room.contents = [mover]
        mover.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        self.assertEqual(
            mover_start_message(room, nav, mover),
            "You begin moving toward the northwest portion of the area. You should arrive in about 11 seconds.",
        )

    def test_start_message_beside_occupant(self):
        mover = self._MsgChar(0, 0)
        occupant = MockOccupant(0, 10, key="a stone")
        room = MockRoom(room_size="large")
        room.contents = [mover, occupant]
        mover.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        self.assertEqual(
            mover_start_message(room, nav, mover),
            "You begin moving toward a stone. You should arrive in about 11 seconds.",
        )

    def test_arrival_message_quadrant(self):
        mover = self._MsgChar(0, 10)
        room = MockRoom(room_size="large")
        room.contents = [mover]
        mover.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        self.assertEqual(
            mover_arrival_message(room, nav, mover),
            "You arrive in the northwest portion of the area.",
        )

    def test_arrival_message_beside_occupant(self):
        mover = self._MsgChar(0, 10)
        occupant = MockOccupant(0, 10, key="a stone")
        room = MockRoom(room_size="large")
        room.contents = [mover, occupant]
        mover.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        self.assertEqual(
            mover_arrival_message(room, nav, mover),
            "You arrive beside a stone.",
        )


class AnnounceGridArrivalTest(SimpleTestCase):
    """announce_grid_arrival arrival phrasing for observer movement messages."""

    class _MsgChar(MockChar):
        is_creature = True

        def __init__(self, name, plane="physical"):
            super().__init__()
            self.name = name
            self._messages = []
            self._can_see = True

        def msg(self, text, from_obj=None, **kwargs):
            self._messages.append(text)

        def visible_to(self, looker):
            return looker._can_see

    def test_arrival_in_quadrant(self):
        mover = self._MsgChar("mover")
        seer = self._MsgChar("seer")
        mover.appearance_name = "A tall Visarii"
        room = MockRoom(room_size="large")
        room.contents = [mover, seer]
        mover.location = room
        seer.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        announce_grid_arrival(mover, nav)
        self.assertEqual(seer._messages, ["A tall Visarii arrives in the northwest portion of the area."])

    def test_arrival_beside_observer(self):
        mover = self._MsgChar("mover")
        seer = self._MsgChar("seer")
        mover.appearance_name = "A tall Visarii"
        seer.appearance_name = "A short Visarii"
        seer.db.pos_x = 0
        seer.db.pos_y = 10
        mover.db.pos_x = 5
        mover.db.pos_y = 5
        room = MockRoom(room_size="large")
        room.contents = [mover, seer]
        mover.location = room
        seer.location = room
        nav = {"dest_x": 0, "dest_y": 10, "dest_z": 1, "exit_dbref": None}
        announce_grid_arrival(mover, nav)
        self.assertEqual(seer._messages, ["A tall Visarii arrives beside you."])
