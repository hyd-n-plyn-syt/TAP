"""Tests for realm-aware `look` sections and per-seat plane occupancy."""

from unittest.mock import patch

from evennia import create_object
from evennia.utils.ansi import strip_ansi
from evennia.utils.test_resources import EvenniaCommandTest

from commands.player.poses import _get_furniture_seat_coord, CmdSit, CmdStand
from commands.player.manifest import CmdManifest
from combat.realm_contest import contest_roll

import re


def _plain(text):
    """Strip Evennia markup tags (truecolor and single-letter) from text."""
    return re.sub(r"\|(?:#[0-9a-fA-F]{6}|[A-Za-z0-9])", "", str(text))


class RealmLookTest(EvenniaCommandTest):
    def _furniture(self, key, nature, x, y):
        furn = create_object(
            "typeclasses.furniture.Furniture", key=key, location=self.room1
        )
        furn.db.dimension = "1x1"
        furn.db.facing = "north"
        furn.db.pos_x = x
        furn.db.pos_y = y
        furn.db.visarial_nature = nature
        furn.calculate_footprint()
        return furn

    def test_normal_looker_sees_only_physical_section(self):
        self._furniture("oak stool", "physical", 1, 1)
        self._furniture("moonstone table", "visarial", 3, 1)
        out = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertIn("In the (physical),", out)
        self.assertIn("oak stool", out)
        self.assertNotIn("moonstone table", out)

    def test_manifested_looker_sees_only_visarial_section(self):
        self._furniture("oak stool", "physical", 1, 1)
        self._furniture("moonstone table", "visarial", 3, 1)
        self.char1.set_state("manifested")
        out = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertIn("In the (visarial),", out)
        self.assertIn("moonstone table", out)
        self.assertNotIn("oak stool", out)

    def test_perceiving_looker_sees_combined_section(self):
        self._furniture("oak stool", "physical", 1, 1)
        self._furniture("moonstone table", "visarial", 3, 1)
        self.char1.set_state("perceiving")
        out = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertIn("In the (physical and visarial),", out)
        self.assertIn("oak stool", out)
        self.assertIn("moonstone table", out)

    def test_dual_furniture_appears_once(self):
        self._furniture("relic bench", "dual_natured", 1, 1)
        out = strip_ansi(self.room1.return_appearance(self.char1))
        self.assertEqual(out.count("relic bench"), 1)


class RealmSeatOccupancyTest(EvenniaCommandTest):
    def _sofa(self):
        furn = create_object(
            "typeclasses.furniture.Furniture", key="ghost couch", location=self.room1
        )
        furn.db.dimension = "1x2"
        furn.db.facing = "north"
        furn.db.pos_x = 2
        furn.db.pos_y = 2
        furn.calculate_footprint()
        return furn

    def test_cross_realm_occupants_share_a_seat(self):
        furn = self._sofa()
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.set_pose("sitting")
        self.char2.set_state("manifested")
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 2
        seat = _get_furniture_seat_coord(self.char2, furn)
        self.assertEqual(seat, (2, 2))
        self.char2.db.pos_x, self.char2.db.pos_y = seat
        self.char2.set_pose("sitting")
        occ = furn.occupied_seats_by_plane()
        self.assertEqual(occ[(2, 2)], frozenset({"physical", "visarial"}))
        self.assertEqual(occ[(2, 3)], frozenset())

    def test_same_realm_occupant_blocks_that_seat(self):
        furn = self._sofa()
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.set_pose("sitting")
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 2
        seat = _get_furniture_seat_coord(self.char2, furn)
        self.assertEqual(seat, (2, 3))


class ContestRollTest(EvenniaCommandTest):
    def test_fumble_subtracts_ten(self):
        with patch("combat.realm_contest.random.randint", return_value=1):
            self.assertEqual(contest_roll(5), -5)

    def test_exploding_tens_accumulate(self):
        with patch("combat.realm_contest.random.randint", side_effect=[10, 10, 3]):
            self.assertEqual(contest_roll(0), 23)

    def test_followup_one_claws_back_past_ten(self):
        with patch("combat.realm_contest.random.randint", side_effect=[10, 1]):
            self.assertEqual(contest_roll(6), 6)

    def test_plain_roll_adds_stat(self):
        with patch("combat.realm_contest.random.randint", return_value=4):
            self.assertEqual(contest_roll(8), 12)


class RealmManifestContestTest(EvenniaCommandTest):
    def _sitters(self):
        self.char1.apply_species("terran")
        self.char2.apply_species("terran")

    def _sofa(self):
        furn = create_object(
            "typeclasses.furniture.Furniture", key="ghost couch", location=self.room1
        )
        furn.db.dimension = "1x2"
        furn.db.facing = "north"
        furn.db.pos_x = 2
        furn.db.pos_y = 2
        furn.calculate_footprint()
        return furn

    def _manifest_into_occupied_tile(self, char_total, occ_total):
        """char1 (physical, standing) manifests into a tile already held in
        the visarial by char2. Returns char1's post-manifest pos."""
        self._sitters()
        self.char1.db.pos_x = 3
        self.char1.db.pos_y = 3
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 3
        self.char2.set_state("manifested")
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[char_total, occ_total],
        ):
            out = self.call(CmdManifest(), "")
        self.assertEqual(self.char1.state(), "manifested")
        self.assertEqual(self.char1.current_plane(), "visarial")
        self.assertIn("proves", out)
        return self.char1.db.pos_x, self.char1.db.pos_y

    def test_no_contest_when_free_spot(self):
        self._sitters()
        self.char1.db.pos_x = 3
        self.char1.db.pos_y = 3
        self.char2.db.pos_x = 4
        self.char2.db.pos_y = 4
        self.char2.set_state("manifested")
        out = self.call(CmdManifest(), "")
        self.assertEqual((self.char1.db.pos_x, self.char1.db.pos_y), (3, 3))
        self.assertNotIn("contest", out)

    def test_newcomer_wins_and_occupant_is_shoved_on_open_ground(self):
        pos = self._manifest_into_occupied_tile(10, 5)
        self.assertEqual(pos, (3, 3))
        self.assertNotEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (3, 3)
        )
        self.assertEqual(self.char2.pose, "standing")

    def test_newcomer_loses_and_is_shoved_on_open_ground(self):
        pos = self._manifest_into_occupied_tile(5, 10)
        self.assertNotEqual(pos, (3, 3))
        self.assertEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (3, 3)
        )

    def test_tie_favors_occupant(self):
        pos = self._manifest_into_occupied_tile(10, 10)
        self.assertNotEqual(pos, (3, 3))
        self.assertEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (3, 3)
        )

    def test_manifest_into_occupied_seat_newcomer_shoved_off(self):
        self._sitters()
        furn = self._sofa()
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.set_pose("sitting")
        self.char2.db.pos_x = 2
        self.char2.db.pos_y = 2
        self.char2.set_state("manifested")
        self.char2.set_pose("sitting")
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[5, 10],
        ):
            out = self.call(CmdManifest(), "")
        self.assertEqual(self.char1.state(), "manifested")
        self.assertIn("off the seat", out)
        self.assertEqual(self.char1.pose, "standing")
        self.assertNotEqual(
            (self.char1.db.pos_x, self.char1.db.pos_y), (2, 2)
        )
        self.assertEqual(self.char2.pose, "sitting")
        self.assertEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (2, 2)
        )
        self.assertTrue(furn.is_at_coord(2, 2))

    def test_manifest_into_occupied_seat_occupant_shoved_off(self):
        self._sitters()
        self._sofa()
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.set_pose("sitting")
        self.char2.db.pos_x = 2
        self.char2.db.pos_y = 2
        self.char2.set_state("manifested")
        self.char2.set_pose("sitting")
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[10, 5],
        ):
            out = self.call(CmdManifest(), "")
        self.assertEqual(self.char1.state(), "manifested")
        self.assertIn("off the seat", out)
        self.assertEqual(self.char1.pose, "sitting")
        self.assertEqual(
            (self.char1.db.pos_x, self.char1.db.pos_y), (2, 2)
        )
        self.assertEqual(self.char2.pose, "standing")
        self.assertNotEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (2, 2)
        )


class PoseRealmEchoTest(EvenniaCommandTest):
    """Pose changes only announce to creatures that can actually observe the
    caller - same realm, perceiving it, awake."""

    def _record(self, char):
        self.log = []
        def record(text, **kwargs):
            if text is not None:
                self.log.append(text)
        char.at_msg_receive = record
        return self.log

    def _chars(self):
        self.char1.apply_species("terran")
        self.char2.apply_species("terran")
        self.char1.db.pos_x = 3
        self.char1.db.pos_y = 3
        self.char2.db.pos_x = 4
        self.char2.db.pos_y = 4

    def test_cross_realm_observer_hears_no_sit(self):
        self._chars()
        self._record(self.char2)
        self.char2.set_state("manifested")
        self.call(CmdSit(), "")
        self.assertEqual(self.log, [])

    def test_perceiving_observer_hears_the_sit(self):
        self._chars()
        self._record(self.char2)
        self.char2.set_state("perceiving")
        self.call(CmdSit(), "")
        self.assertTrue(
            any("sits down" in str(t) for t in self.log),
            f"saw: {self.log}",
        )

    def test_asleep_observer_hears_no_stand(self):
        self._chars()
        self._record(self.char2)
        self.char1.set_pose("sitting")
        self.char2.set_pose("sleeping")
        self.call(CmdStand(), "")
        self.assertEqual(self.log, [])


class ManifestEchoTest(EvenniaCommandTest):
    def _record(self, char):
        self.log = []
        def record(text, **kwargs):
            if text is not None:
                self.log.append(text)
        char.at_msg_receive = record
        return self.log

    def _chars(self, x=3, y=3):
        self.char1.apply_species("terran")
        self.char2.apply_species("terran")
        self.char1.db.pos_x = x
        self.char1.db.pos_y = y
        self.char2.db.pos_x = x + 1
        self.char2.db.pos_y = y

    def test_physical_observer_sees_departure_not_arrival(self):
        self._chars()
        log = self._record(self.char2)
        self.call(CmdManifest(), "")
        combined = " ".join(str(t) for t in log)
        self.assertIn("blinks out of existence", combined)
        self.assertNotIn("blinks into existence", combined)

    def test_physical_observer_sees_arrival_on_unmanifest(self):
        self._chars()
        self.char1.set_state("manifested")
        log = self._record(self.char2)
        self.call(CmdManifest(), "")
        self.assertTrue(
            any("blinks into existence" in str(t) for t in log),
            f"saw: {log}",
        )

    def test_visarial_observer_sees_arrival(self):
        self._chars()
        log = self._record(self.char2)
        self.char2.set_state("manifested")
        self.call(CmdManifest(), "")
        self.assertTrue(
            any("blinks into existence" in str(t) for t in log),
            f"saw: {log}",
        )

    def test_manifested_observer_sees_departure(self):
        self._chars()
        self._record(self.char2)
        self.char2.set_state("manifested")
        self.char1.set_state("manifested")
        self.call(CmdManifest(), "")
        self.assertTrue(
            any("blinks out of existence" in str(t) for t in self.log),
            f"saw: {self.log}",
        )

    def test_contested_arrival_tells_occupant_as_you(self):
        self._chars()
        log = self._record(self.char2)
        self.char2.set_state("manifested")
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 3
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[10, 5],
        ):
            out = self.call(CmdManifest(), "")
        self.assertIn("manifesting into the same space as", _plain(out))
        self.assertIn("spirit proves to be stronger", _plain(out))
        combined = " ".join(str(t) for t in log)
        self.assertIn("appearing in the exact same space as you", _plain(combined))
        self.assertIn("spirit proves to be stronger", _plain(combined))

    def test_contested_departure_echoes_shove(self):
        self._chars()
        log = self._record(self.char2)
        self.char1.set_state("manifested")
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 3
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[5, 10],
        ):
            out = self.call(CmdManifest(), "")
        self.assertEqual(self.char1.state(), "normal")
        self.assertIn("attempting to manifest into the same space as", _plain(out))
        self.assertIn("body proves to be stronger", _plain(out))
        self.assertNotEqual(
            (self.char1.db.pos_x, self.char1.db.pos_y), (3, 3)
        )
        self.assertEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (3, 3)
        )

    def test_contested_unmanifest_collides_with_physical_occupant(self):
        self._chars()
        log = self._record(self.char2)
        self.char1.set_state("manifested")
        self.char2.db.pos_x = 3
        self.char2.db.pos_y = 3
        with patch(
            "combat.realm_contest.contest_roll",
            side_effect=[10, 5],
        ):
            out = self.call(CmdManifest(), "")
        self.assertEqual(self.char1.state(), "normal")
        self.assertIn("manifesting into the same space as", _plain(out))
        self.assertIn("body proves to be stronger", _plain(out))
        combined = " ".join(str(t) for t in log)
        self.assertIn("appearing in the exact same space as you", _plain(combined))
        self.assertIn("body proves to be stronger", _plain(combined))
        self.assertNotEqual(
            (self.char2.db.pos_x, self.char2.db.pos_y), (3, 3)
        )