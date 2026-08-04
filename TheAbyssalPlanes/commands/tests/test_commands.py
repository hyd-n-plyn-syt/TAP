"""Integration tests for player commands using Evennia's in-DB test harness."""

from unittest import mock

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from commands.player.skills import CmdSkills
from commands.player.train import CmdTrain
from commands.player.perceive import CmdPerceive
from commands.player.manifest import CmdManifest
from commands.building.setnature import CmdSetNature
from commands.building.force import CmdForce


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
        self.char1.attributes.add("visarial_state", "normal")
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
        self.char1.attributes.add("visarial_state", "normal")
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
        self.assertEqual(silex.can_perceive, False)
        self.assertEqual(silex.can_manifest, False)
        self.assertEqual(silex.can_phys_see, True)
        self.assertEqual(silex.can_vis_see, False)

    def test_vis_natured_character_aura_default(self):
        vis = create_object("typeclasses.characters.Character", key="Prism")
        vis.apply_species("visarii")
        self.assertEqual(vis.visarial_desc_text(), "This entity gives off an aura of Vim.")
        self.assertEqual(vis.can_perceive, True)
        self.assertEqual(vis.can_manifest, True)
        self.assertEqual(vis.can_vis_see, True)

    def test_can_see_and_touch_flags(self):
        self.char1.attributes.add("visarial_state", "perceiving")
        self.assertEqual(self.char1.can_phys_see, True)
        self.assertEqual(self.char1.can_vis_see, True)
        self.assertEqual(self.char1.can_phys_touch, True)
        self.assertEqual(self.char1.can_vis_touch, False)


class VisariiPlaneTest(EvenniaCommandTest):
    def _make_visarii(self):
        vis = create_object("typeclasses.characters.Character", key="Prism")
        self.assertTrue(vis.apply_species("visarii"))
        return vis

    def test_native_visarii_lives_in_visarial(self):
        vis = self._make_visarii()
        self.assertEqual(vis.state(), "normal")
        self.assertEqual(vis.current_plane(), "visarial")
        self.assertTrue(vis.can_vis_touch)
        self.assertTrue(vis.can_vis_see)
        self.assertFalse(vis.can_phys_touch)
        self.assertFalse(vis.can_phys_see)

    def test_perceiving_visarii_sees_physical_in_place(self):
        vis = self._make_visarii()
        vis.set_state("perceiving")
        self.assertEqual(vis.current_plane(), "visarial")
        self.assertTrue(vis.can_vis_touch)
        self.assertTrue(vis.can_phys_see)
        self.assertFalse(vis.can_phys_touch)

    def test_manifested_visarii_touches_physical_only(self):
        vis = self._make_visarii()
        vis.set_state("manifested")
        self.assertEqual(vis.current_plane(), "physical")
        self.assertTrue(vis.can_phys_touch)
        self.assertTrue(vis.can_phys_see)
        self.assertFalse(vis.can_vis_touch)
        self.assertFalse(vis.can_vis_see)

    def test_silex_cannot_leave_physical(self):
        silex = create_object("typeclasses.characters.Character", key="Grimstone")
        self.assertTrue(silex.apply_species("silex"))
        self.assertFalse(silex.set_state("perceiving"))
        self.assertFalse(silex.set_state("manifested"))
        self.assertTrue(silex.set_state("normal"))
        self.assertFalse(silex.can_vis_touch)
        self.assertFalse(silex.can_vis_see)


class VisariiCommandsTest(EvenniaCommandTest):
    def test_visarii_native_cannot_manifest_into_physical_by_default(self):
        self.char1.apply_species("visarii")
        self.assertEqual(self.char1.state(), "normal")
        self.assertFalse(self.char1.can_phys_touch)

    def test_visarii_manifest_projects_into_physical(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdManifest(), "")
        self.assertIn("project your crystalline form", out)
        self.assertEqual(self.char1.state(), "manifested")
        self.assertEqual(self.char1.current_plane(), "physical")
        self.assertTrue(self.char1.can_phys_touch)

    def test_visarii_perceive_sees_physical_in_place(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdPerceive(), "")
        self.assertIn("perceive the physical plane", out)
        self.assertEqual(self.char1.state(), "perceiving")
        self.assertEqual(self.char1.current_plane(), "visarial")
        self.assertTrue(self.char1.can_phys_see)
        self.assertFalse(self.char1.can_phys_touch)

    def test_silex_cannot_manifest(self):
        self.char1.apply_species("silex")
        out = self.call(CmdManifest(), "")
        self.assertIn("cannot manifest", out)
        self.assertEqual(self.char1.state(), "normal")
        self.assertTrue(self.char1.can_phys_touch)
        self.assertFalse(self.char1.can_vis_touch)

    def test_silex_cannot_perceive(self):
        self.char1.apply_species("silex")
        out = self.call(CmdPerceive(), "")
        self.assertIn("cannot perceive", out)
        self.assertEqual(self.char1.state(), "normal")


class SpeakHearPlaneTest(EvenniaCommandTest):
    def _dual(self):
        c = create_object("typeclasses.characters.Character", key="Walker")
        c.apply_species("terran")
        return c

    def _visarii(self):
        c = create_object("typeclasses.characters.Character", key="Prism")
        c.apply_species("visarii")
        return c

    def _silex(self):
        c = create_object("typeclasses.characters.Character", key="Grimstone")
        c.apply_species("silex")
        return c

    def test_dual_normal_speaks_and_hears_physical(self):
        c = self._dual()
        self.assertTrue(c.can_speak_phys)
        self.assertFalse(c.can_speak_vis)
        self.assertTrue(c.can_hear_phys)
        self.assertFalse(c.can_hear_vis)

    def test_dual_perceiving_hears_visarial_but_speaks_physical(self):
        c = self._dual()
        c.set_state("perceiving")
        self.assertTrue(c.can_speak_phys)
        self.assertFalse(c.can_speak_vis)
        self.assertTrue(c.can_hear_phys)
        self.assertTrue(c.can_hear_vis)

    def test_dual_manifested_speaks_and_hears_visarial_only(self):
        c = self._dual()
        c.set_state("manifested")
        self.assertFalse(c.can_speak_phys)
        self.assertTrue(c.can_speak_vis)
        self.assertFalse(c.can_hear_phys)
        self.assertTrue(c.can_hear_vis)

    def test_visarii_normal_speaks_and_hears_visarial(self):
        c = self._visarii()
        self.assertFalse(c.can_speak_phys)
        self.assertTrue(c.can_speak_vis)
        self.assertFalse(c.can_hear_phys)
        self.assertTrue(c.can_hear_vis)

    def test_visarii_perceiving_hears_physical_but_speaks_visarial(self):
        c = self._visarii()
        c.set_state("perceiving")
        self.assertFalse(c.can_speak_phys)
        self.assertTrue(c.can_speak_vis)
        self.assertTrue(c.can_hear_phys)
        self.assertTrue(c.can_hear_vis)

    def test_visarii_manifested_speaks_and_hears_physical_only(self):
        c = self._visarii()
        c.set_state("manifested")
        self.assertTrue(c.can_speak_phys)
        self.assertFalse(c.can_speak_vis)
        self.assertTrue(c.can_hear_phys)
        self.assertFalse(c.can_hear_vis)

    def test_silex_physical_only(self):
        c = self._silex()
        self.assertTrue(c.can_speak_phys)
        self.assertFalse(c.can_speak_vis)
        self.assertTrue(c.can_hear_phys)
        self.assertFalse(c.can_hear_vis)

    def test_at_say_physical_reaches_physical_hearers(self):
        speaker = self._dual()
        speaker.location = self.room1
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        silex_listener = self._silex()
        silex_listener.location = self.room1
        silex_listener.msg = mock.Mock()
        vis_native = self._visarii()
        vis_native.location = self.room1
        vis_native.msg = mock.Mock()
        speaker.at_say("hello", msg_self=False)
        self.assertTrue(phys_listener.msg.called)
        self.assertTrue(silex_listener.msg.called)
        self.assertFalse(vis_native.msg.called)

    def test_at_say_visarial_reaches_visarial_hearers(self):
        speaker = self._dual()
        speaker.set_state("manifested")
        speaker.location = self.room1
        vis_listener = self._visarii()
        vis_listener.location = self.room1
        vis_listener.msg = mock.Mock()
        silex_listener = self._silex()
        silex_listener.location = self.room1
        silex_listener.msg = mock.Mock()
        speaker.at_say("Echo", msg_self=False)
        self.assertTrue(vis_listener.msg.called)
        self.assertFalse(silex_listener.msg.called)

    def test_whisper_bypasses_realm_gating(self):
        speaker = self._dual()
        speaker.location = self.room1
        silex_listener = self._silex()
        silex_listener.location = self.room1
        silex_listener.msg = mock.Mock()
        speaker.at_say(
            "psst",
            whisper=True,
            receivers=silex_listener,
            msg_receivers='{object} whispers: "{speech}"',
        )
        self.assertTrue(silex_listener.msg.called)

    def test_cmdsay_realm_gated_end_to_end(self):
        from evennia.commands.default.general import CmdSay

        self.char1.apply_species("terran")
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        vis_native = self._visarii()
        vis_native.location = self.room1
        vis_native.msg = mock.Mock()
        out = self.call(CmdSay(), "hello there")
        self.assertIn("You say", out)
        self.assertTrue(phys_listener.msg.called)
        self.assertFalse(vis_native.msg.called)


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


class SearchVisibilityTest(EvenniaCommandTest):
    def test_non_builder_cannot_search_other_plane(self):
        plain = create_object("typeclasses.characters.Character", key="Plain")
        plain.apply_species("terran")
        plain.location = self.room1
        vis_native = create_object("typeclasses.characters.Character", key="Prism")
        vis_native.apply_species("visarii")
        vis_native.location = self.room1
        result = plain.search("Prism", quiet=True)
        self.assertNotIn(vis_native, result)

    def test_builder_can_search_other_plane(self):
        vis_native = create_object("typeclasses.characters.Character", key="Prism")
        vis_native.apply_species("visarii")
        vis_native.location = self.room1
        result = self.char1.search("Prism", quiet=True)
        self.assertIn(vis_native, result)


class ForceCommandTest(EvenniaCommandTest):
    def _visarii(self):
        c = create_object("typeclasses.characters.Character", key="Prism")
        c.apply_species("visarii")
        return c

    def test_force_missing_args(self):
        out = self.call(CmdForce(), "")
        self.assertIn("target and a command string", out)

    def test_force_other_plane_same_room(self):
        vis_hearer = self._visarii()
        vis_hearer.location = self.room1
        vis_hearer.msg = mock.Mock()
        silex_listener = create_object("typeclasses.characters.Character", key="Grimstone")
        silex_listener.apply_species("silex")
        silex_listener.location = self.room1
        silex_listener.msg = mock.Mock()
        out = self.call(CmdForce(), "Prism = say hello")
        self.assertIn("You have forced Prism", out)
        self.assertTrue(vis_hearer.msg.called)
        self.assertFalse(silex_listener.msg.called)