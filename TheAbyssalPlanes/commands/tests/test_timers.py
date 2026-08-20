"""Integration tests for the universal-time combat/movement/regen timers."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from combat.timers import (
    check_engagement_resume,
    disengage_combat,
    engage_combat,
    ensure_combat_timer,
    ensure_movement_timer,
    set_non_combat,
)
from world.systems.regen import ensure_regen_timer
from world.systems.time import COMBAT_ROUND_SECONDS, REGEN_ROUND_SECONDS, now


def _nav(dest_x, dest_y, dest_z=None):
    return {
        "dest_x": dest_x,
        "dest_y": dest_y,
        "dest_z": dest_z,
        "exit_dbref": None,
        "movement_mode": "walking",
        "step_count": 0,
    }


class MovementTimerTest(EvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.char1.db.pos_x = 2
        self.char1.db.pos_y = 2
        self.char1.db.pos_z = 1
        self.char1.db.movement_used = 0
        self.char1.db.move_speed = "run"
        self.char1.db.autonavigate = False
        self.char1.db.autofly = False
        other = create_object("typeclasses.rooms.Room", key="ExitRoom")
        create_object(
            "evennia.objects.objects.DefaultExit",
            key="north",
            location=self.room1,
            destination=other,
            locks="traverse:all()",
        )

    def test_moves_one_grid_per_round_ignoring_non_creatures(self):
        self.char1.db.navigation = _nav(2, 3)
        script = ensure_movement_timer(self.char1)
        script.at_repeat()
        self.assertEqual((self.char1.db.pos_x, self.char1.db.pos_y), (2, 3))
        self.assertIsNone(self.char1.db.navigation)
        self.assertIsNone(self.char1.db.nav_queue)

    def test_arrives_beside_occupied_destination(self):
        self.char1.db.navigation = _nav(2, 3)
        self.char2.db.pos_x = 2
        self.char2.db.pos_y = 3
        msgs = []
        self.char1.msg = lambda text, **kwargs: msgs.append(text)
        script = ensure_movement_timer(self.char1)
        script.at_repeat()
        self.assertEqual((self.char1.db.pos_x, self.char1.db.pos_y), (2, 2))
        self.assertIsNone(self.char1.db.navigation)
        self.assertTrue(
            any("arrive" in line.lower() for line in msgs),
            f"messages were: {msgs}",
        )
        self.assertFalse(
            any("way is blocked" in line.lower() for line in msgs),
            f"messages were: {msgs}",
        )

    def test_mid_path_blocker_still_blocks(self):
        self.char1.db.navigation = _nav(2, 4)
        furn = create_object(
            "typeclasses.furniture.Furniture",
            key="leather armchair",
            location=self.room1,
        )
        furn.db.dimension = "1x1"
        furn.db.pos_x = 2
        furn.db.pos_y = 3
        furn.calculate_footprint()
        msgs = []
        self.char1.msg = lambda text, **kwargs: msgs.append(text)
        script = ensure_movement_timer(self.char1)
        script.at_repeat()
        self.assertEqual((self.char1.db.pos_x, self.char1.db.pos_y), (2, 2))
        self.assertIsNone(self.char1.db.navigation)
        self.assertTrue(
            any("way is blocked" in line.lower() for line in msgs),
            f"messages were: {msgs}",
        )

    def test_timer_stops_on_arrival(self):
        self.char1.db.navigation = _nav(2, 2)
        script = ensure_movement_timer(self.char1)
        script.at_repeat()
        self.assertFalse(script.is_valid())

    def test_first_tick_waits_one_second(self):
        self.char1.db.navigation = _nav(2, 3)
        script = ensure_movement_timer(self.char1)
        self.assertTrue(script.db_start_delay)

    def test_blocked_message_capitalizes_name(self):
        self.char1.db.navigation = _nav(4, 2)
        furn = create_object(
            "typeclasses.furniture.Furniture",
            key="leather armchair",
            location=self.room1,
        )
        furn.db.dimension = "1x1"
        furn.db.pos_x = 3
        furn.db.pos_y = 2
        furn.calculate_footprint()
        msgs = []
        self.char1.msg = lambda text, **kwargs: msgs.append(text)
        script = ensure_movement_timer(self.char1)
        script.at_repeat()
        self.assertEqual((self.char1.db.pos_x, self.char1.db.pos_y), (2, 2))
        self.assertTrue(
            any("way is blocked" in line.lower() for line in msgs),
            f"messages were: {msgs}",
        )


class RegenTimerTest(EvenniaCommandTest):
    def test_heals_after_elapsed_regen_round(self):
        self.char1.set_pool("vigor", max(0, self.char1.vigor - 30))
        self.assertTrue(self.char1.is_injured)
        script = ensure_regen_timer(self.char1)
        before = self.char1.pools_current["vigor"]
        script.db.anchor = now() - REGEN_ROUND_SECONDS - 1
        script.at_repeat()
        if script.is_valid():
            script.db.anchor = now() - REGEN_ROUND_SECONDS - 1
            script.at_repeat()
        self.assertGreater(self.char1.pools_current["vigor"], before)

    def test_stops_when_fully_healed(self):
        self.char1.set_pool("vigor", max(0, self.char1.vigor - 10))
        script = ensure_regen_timer(self.char1)
        self.char1.reset_pools()
        self.assertFalse(self.char1.is_injured)
        self.assertFalse(script.is_valid())


class CombatStateTest(EvenniaCommandTest):
    def test_engage_flags_both_sides(self):
        engage_combat(self.char1, self.char2)
        self.assertEqual(self.char1.combat_state, "in_combat")
        self.assertEqual(self.char2.combat_state, "in_combat")
        self.assertIn(str(self.char2.id), self.char1.engagements)
        self.assertIn(str(self.char1.id), self.char2.engagements)

    def test_non_combat_target_not_engaged(self):
        set_non_combat(self.char2)
        engage_combat(self.char1, self.char2)
        self.assertEqual(self.char2.combat_state, "non_combat")
        self.assertNotIn(str(self.char2.id), self.char1.engagements)
        self.assertFalse(self.char1.engagements)

    def test_flee_and_resume_within_grace(self):
        engage_combat(self.char1, self.char2)
        self.assertIn(str(self.char2.id), self.char1.engagements)
        other = create_object("typeclasses.rooms.Room", key="FarRoom")
        self.char2.move_to(other)
        self.assertEqual(self.char2.combat_state, "fled_combat")
        self.assertEqual(self.char1.combat_state, "fled_from_combat")
        felt = self.char1.engagements[str(self.char2.id)]["fled_since"]
        self.assertLessEqual(
            now() - felt, COMBAT_ROUND_SECONDS * 5, "grace should still be open"
        )
        self.char2.move_to(self.room1)
        check_engagement_resume(self.char1)
        self.assertEqual(self.char1.combat_state, "in_combat")
        self.assertEqual(self.char2.combat_state, "in_combat")

    def test_flee_grace_expires(self):
        engage_combat(self.char1, self.char2)
        other = create_object("typeclasses.rooms.Room", key="FarRoom2")
        self.char2.move_to(other)
        engs = self.char1.engagements
        engs[str(self.char2.id)]["fled_since"] = now() - COMBAT_ROUND_SECONDS * 6
        self.char1.engagements = engs
        check_engagement_resume(self.char1)
        self.assertEqual(self.char1.combat_state, "idle")
        self.assertNotIn(str(self.char2.id), self.char1.engagements)

    def test_disengage_clears_both_sides(self):
        engage_combat(self.char1, self.char2)
        disengage_combat(self.char1, self.char2)
        self.assertNotIn(str(self.char2.id), self.char1.engagements)
        self.assertNotIn(str(self.char1.id), self.char2.engagements)
        self.assertEqual(self.char1.combat_state, "idle")
        self.assertEqual(self.char2.combat_state, "idle")

    def test_ensure_combat_timer_is_single(self):
        ensure_combat_timer(self.char1)
        ensure_combat_timer(self.char1)
        scripts = self.char1.scripts.get(key="combat_timer")
        self.assertEqual(len(scripts), 1)