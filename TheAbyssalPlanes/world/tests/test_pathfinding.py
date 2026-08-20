"""Unit tests for BFS pathfinding and movement echo helpers."""

from django.test import SimpleTestCase
from combat.movement import (
    SPEED_FLY_OVER,
    SPEED_FLY_VERBS,
    SPEED_GROUND_VERBS,
    SPEED_TICKS,
    direction_from_delta,
    find_path,
    _toward_or_away,
    _format_next_to,
    _adjacent_entities,
)
from combat.grid import get_room_grid_size


class MockRoom:
    def __init__(self, room_size="small"):
        self.db = type("db", (), {"room_size": room_size})()
        self.contents = []


class MockOccupant:
    def __init__(self, x, y, key="thing", planes=("physical",), pos_z=1):
        self.key = key
        self.appearance_name = key
        self.occupies_space = True
        self.planes_occupied = planes
        self.destination = None
        self.is_creature = False
        self.db = type("db", (), {"pos_x": x, "pos_y": y, "pos_z": pos_z})()


class MockMover:
    def __init__(self, planes):
        self.planes_occupied = planes


class SpeedConstantsTest(SimpleTestCase):
    def test_speed_ticks(self):
        self.assertEqual(SPEED_TICKS["walk"], 3)
        self.assertEqual(SPEED_TICKS["jog"], 2)
        self.assertEqual(SPEED_TICKS["run"], 1)

    def test_ground_verbs(self):
        self.assertEqual(SPEED_GROUND_VERBS["walk"], "walks")
        self.assertEqual(SPEED_GROUND_VERBS["jog"], "jogs")
        self.assertEqual(SPEED_GROUND_VERBS["run"], "runs")

    def test_fly_verbs(self):
        self.assertEqual(SPEED_FLY_VERBS["walk"], "flies slowly")
        self.assertEqual(SPEED_FLY_VERBS["jog"], "flies briskly")
        self.assertEqual(SPEED_FLY_VERBS["run"], "flies recklessly")

    def test_fly_over(self):
        self.assertEqual(SPEED_FLY_OVER["walk"], "flies slowly over")
        self.assertEqual(SPEED_FLY_OVER["jog"], "flies briskly over")
        self.assertEqual(SPEED_FLY_OVER["run"], "flies recklessly over")


class DirectionFromDeltaTest(SimpleTestCase):
    def test_cardinals(self):
        self.assertEqual(direction_from_delta(0, 1), "north")
        self.assertEqual(direction_from_delta(0, -1), "south")
        self.assertEqual(direction_from_delta(1, 0), "east")
        self.assertEqual(direction_from_delta(-1, 0), "west")

    def test_ordinals(self):
        self.assertEqual(direction_from_delta(1, 1), "northeast")
        self.assertEqual(direction_from_delta(-1, 1), "northwest")
        self.assertEqual(direction_from_delta(1, -1), "southeast")
        self.assertEqual(direction_from_delta(-1, -1), "southwest")

    def test_zero(self):
        self.assertIsNone(direction_from_delta(0, 0))

    def test_large_delta(self):
        self.assertIsNone(direction_from_delta(0, 2))


class FindPathTest(SimpleTestCase):
    def test_straight_line(self):
        room = MockRoom(room_size="small")
        path, blockers = find_path(room, 0, 0, 2, 2)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))
        self.assertEqual(blockers, [])

    def test_same_start_end(self):
        room = MockRoom(room_size="small")
        path, blockers = find_path(room, 1, 1, 1, 1)
        self.assertEqual(path, [(1, 1)])
        self.assertEqual(blockers, [])

    def test_path_around_obstacle(self):
        room = MockRoom(room_size="small")
        room.contents = [MockOccupant(1, 1, key="wall")]
        path, blockers = find_path(room, 0, 0, 2, 2)
        self.assertGreater(len(path), 0)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))
        for px, py in path:
            self.assertFalse(px == 1 and py == 1, f"path goes through obstacle at {px},{py}")

    def test_fully_blocked_returns_empty(self):
        room = MockRoom(room_size="small")
        room.contents = [
            MockOccupant(0, 1, key="a"),
            MockOccupant(1, 0, key="b"),
            MockOccupant(1, 1, key="c"),
            MockOccupant(2, 2, key="d"),
        ]
        path, blockers = find_path(room, 0, 0, 2, 2)
        self.assertEqual(path, [])
        self.assertTrue(len(blockers) > 0)

    def test_out_of_bounds(self):
        room = MockRoom(room_size="small")
        path, blockers = find_path(room, 0, 0, 10, 10)
        self.assertEqual(path, [])
        self.assertEqual(blockers, [])

    def test_realm_aware(self):
        room = MockRoom(room_size="small")
        room.contents = [MockOccupant(1, 1, key="ghost", planes=("visarial",))]
        path, blockers = find_path(
            room, 0, 0, 2, 2,
            mover=MockMover(("physical",)),
        )
        self.assertGreater(len(path), 0)
        self.assertEqual(path[-1], (2, 2))


class TowardOrAwayTest(SimpleTestCase):
    def _make(self, cx, cy, ox, oy):
        char = type("C", (), {"db": type("db", (), {"pos_x": cx, "pos_y": cy})()})()
        obs = type("O", (), {"db": type("db", (), {"pos_x": ox, "pos_y": oy})()})()
        return char, obs

    def test_north_toward(self):
        char, obs = self._make(5, 5, 5, 8)
        self.assertEqual(_toward_or_away(obs, char, 0, 1), "toward you")

    def test_north_away(self):
        char, obs = self._make(5, 5, 5, 2)
        self.assertEqual(_toward_or_away(obs, char, 0, 1), "away from you")

    def test_east_toward(self):
        char, obs = self._make(5, 5, 8, 5)
        self.assertEqual(_toward_or_away(obs, char, 1, 0), "toward you")

    def test_east_away(self):
        char, obs = self._make(5, 5, 2, 5)
        self.assertEqual(_toward_or_away(obs, char, 1, 0), "away from you")

    def test_perpendicular(self):
        char, obs = self._make(5, 5, 5, 8)
        result = _toward_or_away(obs, char, 1, 0)
        self.assertIsNone(result)

    def test_no_position(self):
        char = type("C", (), {"db": type("db", (), {"pos_x": None, "pos_y": None})()})()
        obs = type("O", (), {"db": type("db", (), {"pos_x": 5, "pos_y": 5})()})()
        self.assertIsNone(_toward_or_away(obs, char, 0, 1))


class FormatNextToTest(SimpleTestCase):
    def test_empty(self):
        self.assertEqual(_format_next_to([]), "")

    def test_one(self):
        self.assertEqual(_format_next_to(["a chair"]), "a chair")

    def test_two(self):
        self.assertEqual(_format_next_to(["a chair", "a table"]), "a chair, and a table")

    def test_three(self):
        result = _format_next_to(["a", "b", "c"])
        self.assertEqual(result, "a, b, and c")
