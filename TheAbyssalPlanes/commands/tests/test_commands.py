"""Integration tests for player commands using Evennia's in-DB test harness."""

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from commands.player.skills import CmdSkills
from commands.player.train import CmdTrain
from commands.building.setnature import CmdSetNature


class SkillsCommandTest(EvenniaCommandTest):
    def test_no_skills_plain_words(self):
        self.char1.skills = {}
        out = self.call(CmdSkills(), "")
        self.assertIn("You have not learned any skills yet", out)

    def test_known_skill_listing(self):
        self.char1.skills = {"attack": 100, "punch": 50}
        out = self.call(CmdSkills(), "")
        self.assertIn("Attack", out)
        self.assertIn("Punch", out)

    def test_unknown_skill_detail(self):
        out = self.call(CmdSkills(), "nonsense")
        self.assertTrue(out.startswith("You don't know how to do that."))

    def test_learned_skill_detail(self):
        self.char1.skills = {"attack": 300}
        out = self.call(CmdSkills(), "attack")
        self.assertIn("Attack", out)
        self.assertIn("Corpus Potestas", out)

    def test_skill_key_detail_shows_requirements(self):
        self.char1.skills = {"power_strike": 0, "attack": 300, "punch": 300}
        out = self.call(CmdSkills(), "power strike")
        self.assertIn("Power Strike", out)
        self.assertIn("Requires", out)


class TrainCommandTest(EvenniaCommandTest):
    def _make_trainer(self):
        trainer = self.char2
        trainer.attributes.add("trained_skills", ["punch", "kick", "power_strike"])
        return trainer

    def test_no_trainers_message(self):
        out = self.call(CmdTrain(), "")
        self.assertTrue(out.startswith("There's no one here who can train you."))

    def test_list_trainers(self):
        self._make_trainer()
        out = self.call(CmdTrain(), "")
        self.assertIn("trains in", out)
        self.assertIn("Punch", out)
        self.assertIn("Power Strike", out)

    def test_learn_simple_skill(self):
        self._make_trainer()
        self.call(CmdTrain(), "punch")
        self.assertIn("punch", self.char1.skills)
        self.assertEqual(self.char1.skills["punch"], 0)

    def test_learn_gated_by_prereqs(self):
        self._make_trainer()
        out = self.call(CmdTrain(), "power strike")
        self.assertIn("You need Attack 0% Adept", out)
        self.assertNotIn("power_strike", self.char1.skills)

    def test_learn_after_prereqs(self):
        self._make_trainer()
        self.char1.skills = {"attack": 300, "punch": 300}
        self.call(CmdTrain(), "power strike")
        self.assertIn("power_strike", self.char1.skills)

    def test_no_trainer_for_skill(self):
        self._make_trainer()
        out = self.call(CmdTrain(), "block")
        self.assertTrue(out.startswith("No one here can teach you that."))

    def test_unknown_skill(self):
        self._make_trainer()
        out = self.call(CmdTrain(), "nonsense")
        self.assertTrue(out.startswith("You don't know how to do that."))


class PlaneVisibilityTest(EvenniaCommandTest):
    def _make_obelisks(self):
        room = create_object("typeclasses.rooms.Room", key="VisTestRoom")
        phys = create_object(
            "typeclasses.objects.Object", key="black obelisk", location=room, home=room
        )
        phys.set_nature("physical")
        vis = create_object(
            "typeclasses.objects.Object", key="lapis obelisk", location=room, home=room
        )
        vis.set_nature("visarial")
        return room, phys, vis

    def test_vis_obelisk_lives_in_visarial_plane(self):
        _, phys, vis = self._make_obelisks()
        self.assertEqual(vis.current_plane(), "visarial")
        self.assertEqual(phys.current_plane(), "physical")

    def test_physical_looker_does_not_see_vis_obelisk(self):
        room, _, _ = self._make_obelisks()
        self.char1.attributes.add("visarial_state", "physical")
        out = room.return_appearance(self.char1)
        self.assertIn("black obelisk", out)
        self.assertNotIn("lapis obelisk", out)

    def test_perceiver_sees_vis_obelisk(self):
        room, _, _ = self._make_obelisks()
        self.char1.attributes.add("visarial_state", "perceiving")
        out = room.return_appearance(self.char1)
        self.assertIn("black obelisk", out)
        self.assertIn("lapis obelisk", out)

    def test_vis_object_aura_default(self):
        _, _, vis = self._make_obelisks()
        self.assertEqual(vis.visarial_desc_text(), "This object gives off an aura of Vim")
        self.assertEqual(vis.can_vis_touch, True)
        self.assertEqual(vis.can_phys_touch, False)

    def test_physical_object_disconnected_no_attr(self):
        _, phys, _ = self._make_obelisks()
        self.assertEqual(
            phys.visarial_desc_text(), "This object is absolutely disconnected from Vim."
        )
        self.assertIsNone(phys.db.visarial_desc)
        self.assertEqual(phys.can_phys_touch, True)
        self.assertEqual(phys.can_vis_touch, False)

    def test_physical_object_desc_hidden_from_plain_looker(self):
        room, phys, _ = self._make_obelisks()
        self.char1.attributes.add("visarial_state", "physical")
        out = phys.get_display_desc(self.char1)
        self.assertNotIn("disconnected", out)

    def test_physical_object_desc_shown_to_perceiver(self):
        _, phys, _ = self._make_obelisks()
        self.char1.attributes.add("visarial_state", "perceiving")
        out = phys.get_display_desc(self.char1)
        self.assertIn("absolutely disconnected from Vim", out)

    def test_dual_object_aura_default(self):
        _, phys, _ = self._make_obelisks()
        dual = create_object(
            "typeclasses.objects.Object", key="relic", location=phys.location, home=phys.location
        )
        self.assertEqual(dual.nature(), "dual_natured")
        self.assertEqual(dual.current_plane(), "physical")
        self.assertEqual(dual.visarial_desc_text(), "This object gives off an aura of Vim")

    def test_silex_character_disconnected_no_attr(self):
        silex = create_object("typeclasses.characters.Character", key="Grimstone")
        self.assertTrue(silex.apply_species("silex"))
        self.assertEqual(
            silex.visarial_desc_text(), "This entity is absolutely disconnected from Vim."
        )
        self.assertIsNone(silex.db.visarial_desc)
        self.assertEqual(silex.is_creature, True)
        self.assertEqual(silex.can_project, False)
        self.assertEqual(silex.can_phys_see, True)
        self.assertEqual(silex.can_vis_see, False)

    def test_vis_natured_character_aura_default(self):
        vis = create_object("typeclasses.characters.Character", key="Prism")
        vis.apply_species("visarii")
        self.assertEqual(vis.visarial_desc_text(), "This entity gives off an aura of Vim.")
        self.assertEqual(vis.can_project, True)
        self.assertEqual(vis.can_vis_see, True)

    def test_can_see_and_touch_flags(self):
        self.char1.attributes.add("visarial_state", "perceiving")
        self.assertEqual(self.char1.can_phys_see, True)
        self.assertEqual(self.char1.can_vis_see, True)
        self.assertEqual(self.char1.can_phys_touch, True)
        self.assertEqual(self.char1.can_vis_touch, False)


class SetNatureCommandTest(EvenniaCommandTest):
    def test_set_nature_on_object_in_room(self):
        self.assertEqual(self.obj1.nature(), "dual_natured")
        out = self.call(CmdSetNature(), "visarial = Obj")
        self.assertIn("visarial", out)
        self.assertEqual(self.obj1.nature(), "visarial")
        self.assertEqual(self.obj1.current_plane(), "visarial")

    def test_bad_nature_rejected(self):
        out = self.call(CmdSetNature(), "magic = Obj")
        self.assertIn("physical, visarial, dual_natured", out)
        self.assertEqual(self.obj1.nature(), "dual_natured")

    def test_unknown_target(self):
        out = self.call(CmdSetNature(), "visarial = ghost")
        self.assertIn("Could not find", out)

    def test_setnature_on_self(self):
        out = self.call(CmdSetNature(), "physical")
        self.assertIn("physical", out)
        self.assertEqual(self.char1.nature(), "physical")