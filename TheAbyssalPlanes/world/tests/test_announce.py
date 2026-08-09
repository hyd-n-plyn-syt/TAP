"""Integration tests for plane-gated movement announcements."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaTest

from typeclasses.exits import Exit


class MovementAnnounceTest(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.char1.location = self.room1
        self.char2.location = self.room1
        self.char1.db.pos_x = 0
        self.char1.db.pos_y = 0
        self.char2.db.pos_x = 1
        self.char2.db.pos_y = 1
        self.exit = create_object(
            Exit,
            key="north",
            location=self.room1,
            destination=self.room2,
        )
        self.return_exit = create_object(
            Exit,
            key="south",
            location=self.room2,
            destination=self.room1,
        )
        self.msg_log = []

        def record_msg(text, **kwargs):
            self.msg_log.append(text)

        self.char2.at_msg_receive = record_msg

    def test_announce_move_from_traverse(self):
        self.char1.announce_move_from(self.room2, move_type="traverse")
        self.assertTrue(
            any("walks away to the north" in line for line in self.msg_log),
            f"observer saw: {self.msg_log}",
        )

    def test_announce_move_from_move(self):
        self.char1.announce_move_from(self.room2, move_type="move")
        self.assertTrue(
            any("walks away to the north" in line for line in self.msg_log),
            f"observer saw: {self.msg_log}",
        )

    def test_announce_move_to(self):
        self.char1.location = self.room2
        self.char2.location = self.room2
        self.char1.announce_move_to(self.room1, move_type="traverse")
        self.assertTrue(
            any("walks in from the south" in line for line in self.msg_log),
            f"observer saw: {self.msg_log}",
        )

    def test_no_room_names(self):
        self.char1.announce_move_from(self.room2, move_type="traverse")
        for line in self.msg_log:
            self.assertNotIn("leaving", line)
            self.assertNotIn("heading for", line)
            self.assertNotIn(self.room1.key, line)
            self.assertNotIn(self.room2.key, line)

    def test_observer_cannot_perceive_gets_nothing(self):
        self.char1.db.visarial_state = "normal"
        self.char2.db.visarial_state = "manifested"
        self.char1.announce_move_from(self.room2, move_type="traverse")
        self.assertEqual(self.msg_log, [])
