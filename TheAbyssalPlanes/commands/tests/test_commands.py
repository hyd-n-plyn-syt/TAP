"""Integration tests for player commands using Evennia's in-DB test harness."""

import ast
import os
import tempfile
from unittest import mock

from evennia import create_object
from evennia.utils.test_resources import EvenniaCommandTest

from commands.player.emote import CmdEmote
from commands.player.skills import CmdSkills
from commands.player.train import CmdTrain
from commands.player.perceive import CmdPerceive
from commands.player.manifest import CmdManifest
from commands.player.changes import CmdChanges
from commands.building.setnature import CmdSetNature
from commands.building.force import CmdForce
from commands.building.addchange import CmdAddChange
from commands.player.appearance import (
    CmdSetEyes,
    CmdSetEyeColor,
    CmdSetHair,
    CmdSetHairColor,
    CmdSetSkin,
)
from world.data import changes


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


class ChangesCommandTest(EvenniaCommandTest):
    account_typeclass = "typeclasses.accounts.Account"

    def test_bare_lists_unread(self):
        out = self.call(CmdChanges(), "")
        self.assertIn("Changes", out)
        self.assertIn("#1", out)
        self.assertIn("changes <number>", out)
        self.assertEqual(self.account.changes_seen, 0)

    def test_all_lists_everything_and_marks_read(self):
        out = self.call(CmdChanges(), "all")
        self.assertIn("#1", out)
        self.assertIn(f"#{changes.latest_number()}", out)
        self.assertEqual(self.account.changes_seen, changes.latest_number())

    def test_read_single_shows_body_and_marks_read(self):
        out = self.call(CmdChanges(), "#5")
        self.assertIn("Change #5", out)
        self.assertIn(changes.get_change(5)["title"], out)
        self.assertEqual(self.account.changes_seen, 5)
        self.assertNotIn("more", out)

    def test_read_latest_marks_read(self):
        out = self.call(CmdChanges(), "latest")
        self.assertIn(f"#10", out)
        self.assertEqual(self.account.changes_seen, changes.latest_number())

    def test_caught_up_message(self):
        self.account.changes_seen = changes.latest_number()
        out = self.call(CmdChanges(), "")
        self.assertIn("all caught up", out)

    def test_bad_argument(self):
        out = self.call(CmdChanges(), "xyz")
        self.assertTrue(out.startswith("Usage"))

    def test_unknown_number(self):
        out = self.call(CmdChanges(), "#999")
        self.assertIn("There is no change #999", out)

    def test_login_alert_when_unread(self):
        self.account.changes_seen = changes.latest_number() - 1
        with mock.patch.object(self.account, "_send_to_connect_channel"), \
                mock.patch.object(self.account, "puppet_object"):
            with mock.patch.object(self.account, "msg", wraps=self.account.msg) as m:
                self.account.at_post_login(session=None)
        joined = "\n".join(
            str(c.args[0]) for c in m.call_args_list if c.args
        )
        self.assertIn("New change", joined)
        self.assertIn("changes", joined)

    def test_no_login_alert_when_read(self):
        self.account.changes_seen = changes.latest_number()
        with mock.patch.object(self.account, "_send_to_connect_channel"), \
                mock.patch.object(self.account, "puppet_object"):
            with mock.patch.object(self.account, "msg", wraps=self.account.msg) as m:
                self.account.at_post_login(session=None)
        joined = "\n".join(
            str(c.args[0]) for c in m.call_args_list if c.args
        )
        self.assertNotIn("New change", joined)


class AddChangeCommandTest(EvenniaCommandTest):
    def _fake_file(self):
        tmp = tempfile.TemporaryDirectory()
        path = os.path.join(tmp.name, "changes.py")
        with open(changes.CHANGES_FILE, encoding="utf-8") as f:
            source = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(source)
        self.addCleanup(tmp.cleanup)
        return path

    def test_missing_equals_shows_usage(self):
        out = self.call(CmdAddChange(), "Just a title")
        self.assertTrue(out.startswith("Usage"))

    def test_empty_body_shows_usage(self):
        out = self.call(CmdAddChange(), "Title =   ")
        self.assertTrue(out.startswith("Usage"))

    def test_appends_entry_and_announces(self):
        path = self._fake_file()
        with mock.patch.object(changes, "CHANGES", list(changes.CHANGES)) as fake, \
                mock.patch.object(changes, "CHANGES_FILE", path):
            before = changes.latest_number()
            out = self.call(
                CmdAddChange(), "A spiffy new feature = It does cool things now."
            )
            self.assertIn(f"Added change #{before + 1}", out)
            self.assertEqual(changes.latest_number(), before + 1)
            entry = changes.get_change(before + 1)
            self.assertEqual(entry["title"], "A spiffy new feature")
            self.assertEqual(entry["body"], "It does cool things now.")
        with open(path, encoding="utf-8") as f:
            new_source = f.read()
        ast.parse(new_source)
        self.assertIn("A spiffy new feature", new_source)


class EmoteCommandTest(EvenniaCommandTest):
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

    def _get_msg_text(self, mock_obj):
        call_args = mock_obj.msg.call_args
        return call_args[1]["text"][0]

    def test_emote_physical_seen_by_physical_only(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        vis_native = self._visarii()
        vis_native.location = self.room1
        vis_native.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at the wall")
        self.assertIn("waves at the wall", out)
        self.assertTrue(phys_listener.msg.called)
        self.assertFalse(vis_native.msg.called)

    def test_emote_visarial_seen_by_visarial_only(self):
        self.char1.apply_species("visarii")
        self.char1.set_state("normal")
        self.char1.location = self.room1
        vis_listener = self._visarii()
        vis_listener.location = self.room1
        vis_listener.msg = mock.Mock()
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        out = self.call(CmdEmote(), "glows in the dark")
        self.assertIn("glows in the dark", out)
        self.assertTrue(vis_listener.msg.called)
        self.assertFalse(phys_listener.msg.called)

    def test_emote_at_target_resolves(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @walker")
        self.assertIn("waves at a middling and average Terran", out)
        self.assertTrue(target.msg.called)

    def test_emote_at_target_seen_by_observer(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        observer = self._visarii()
        observer.set_state("perceiving")
        observer.location = self.room1
        observer.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @walker")
        self.assertTrue(observer.msg.called)
        msg_text = self._get_msg_text(observer)
        self.assertIn("waves at", msg_text)
        self.assertIn("middling and average Terran", msg_text)

    def test_emote_at_target_multiple_resolves(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        dup1 = create_object("typeclasses.characters.Character", key="Clone")
        dup1.apply_species("terran")
        dup1.location = self.room1
        dup1.msg = mock.Mock()
        dup2 = create_object("typeclasses.characters.Character", key="Clone")
        dup2.apply_species("terran")
        dup2.location = self.room1
        dup2.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @clone")
        self.assertIn("waves at", out)
        self.assertIn("Clone", out)
        self.assertTrue(dup1.msg.called)
        self.assertTrue(dup2.msg.called)

    def test_emote_at_target_not_found_errors(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        out = self.call(CmdEmote(), "waves at @nobody")
        self.assertIn("No one matching", out)

    def test_emote_at_target_in_quote_rejected(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        out = self.call(CmdEmote(), 'says "Hello @walker"')
        self.assertIn("can't apply a target", out)

    def test_emote_at_self_removes_prefix(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @self")
        self.assertIn("waves at a middling and average Terran", out)
        self.assertIn("(You)", out)
        self.assertTrue(target.msg.called)

    def test_emote_quoted_speech_heard_same_realm(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        out = self.call(CmdEmote(), 'yells "Hello!"')
        self.assertTrue(phys_listener.msg.called)
        msg_text = self._get_msg_text(phys_listener)
        self.assertIn('"Hello!"', msg_text)

    def test_emote_quoted_speech_heard_perceiving_other_realm(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        vis_perceiving = self._visarii()
        vis_perceiving.set_state("perceiving")
        vis_perceiving.location = self.room1
        vis_perceiving.msg = mock.Mock()
        out = self.call(CmdEmote(), 'yells "Hello!"')
        self.assertTrue(vis_perceiving.msg.called)
        msg_text = self._get_msg_text(vis_perceiving)
        self.assertIn('"Hello!"', msg_text)

    def test_emote_quoted_then_continuation_comma(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        out = self.call(CmdEmote(), 'says "Hello." then waves')
        self.assertTrue(phys_listener.msg.called)
        msg_text = self._get_msg_text(phys_listener)
        self.assertIn('"Hello,"', msg_text)

    def test_emote_display_name_no_prefix_same_realm(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves")
        self.assertTrue(target.msg.called)
        msg_text = self._get_msg_text(target)
        self.assertNotIn("|w(|", msg_text)

    def test_emote_display_name_prefix_diff_realm(self):
        self.char1.apply_species("visarii")
        self.char1.set_state("manifested")
        self.char1.location = self.room1
        perceiving_vis = self._visarii()
        perceiving_vis.set_state("perceiving")
        perceiving_vis.location = self.room1
        perceiving_vis.msg = mock.Mock()
        out = self.call(CmdEmote(), "glows")
        self.assertTrue(perceiving_vis.msg.called)
        msg_text = self._get_msg_text(perceiving_vis)
        self.assertIn("|w(|", msg_text)

    def test_emote_staff_sees_real_name(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        self.char1.locks.add("perm(Builder):id(%s)" % self.char1.dbref)
        out = self.call(CmdEmote(), "waves at @walker")
        self.assertIn("(Walker)", out)
        self.assertTrue(target.msg.called)

    def test_emote_multiple_quotes_independent(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        phys_listener = self._dual()
        phys_listener.location = self.room1
        phys_listener.msg = mock.Mock()
        out = self.call(CmdEmote(), 'says "Hello." and then "Goodbye."')
        self.assertTrue(phys_listener.msg.called)
        msg_text = self._get_msg_text(phys_listener)
        self.assertIn('"Hello,"', msg_text)
        self.assertIn('"Goodbye."', msg_text)

    def test_emote_empty_args(self):
        out = self.call(CmdEmote(), "")
        self.assertIn("What do you want to do?", out)

    def test_emote_multi_sentence_pronoun_reset(self):
        self.char1.apply_species("terran")
        self.char1.gender = "male"
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        self.call(CmdEmote(), '@me says, "Hello!" to @self. @me snorts at @walker.')
        msg_text = self._get_msg_text(target)
        self.assertIn("himself", msg_text)
        self.assertIn("|wHe|n", msg_text)

    def test_emote_multi_sentence_self_view(self):
        self.char1.apply_species("terran")
        self.char1.gender = "female"
        self.char1.location = self.room1
        out = self.call(CmdEmote(), '@me says, "Hello!" to @self. @me nods.')
        self.assertIn("yourself", out)
        self.assertIn("You", out)

    def test_emote_reflexive_pronouns_observer(self):
        self.char1.apply_species("terran")
        self.char1.gender = "male"
        self.char1.location = self.room1
        observer = self._dual()
        observer.location = self.room1
        observer.msg = mock.Mock()
        out = self.call(CmdEmote(), "@me waves at @self")
        self.assertTrue(observer.msg.called)
        msg_text = self._get_msg_text(observer)
        self.assertIn("himself", msg_text)

    def test_emote_reflexive_pronouns_self(self):
        self.char1.apply_species("terran")
        self.char1.gender = "female"
        self.char1.location = self.room1
        out = self.call(CmdEmote(), "@me waves at @self")
        self.assertIn("yourself", out)

    def test_emote_reflexive_neuter(self):
        self.char1.apply_species("terran")
        self.char1.gender = "neuter"
        self.char1.location = self.room1
        out = self.call(CmdEmote(), "@me waves at @self")
        self.assertIn("yourself", out)

    def test_emote_target_by_species(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @terran")
        self.assertTrue(target.msg.called)
        self.assertIn("waves at", out)

    def test_emote_target_by_adjective(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.appearance_adjective = "hardy"
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "stares at @hardy")
        self.assertTrue(target.msg.called)
        self.assertIn("stares at", out)

    def test_emote_target_by_height(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.appearance_height = "tall"
        target.msg = mock.Mock()
        out = self.call(CmdEmote(), "waves at @tall")
        self.assertTrue(target.msg.called)
        self.assertIn("waves at", out)

    def test_emote_target_pronoun_on_repeat(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.gender = "male"
        target.msg = mock.Mock()
        self.call(CmdEmote(), "waves at @walker. @walker waves back.")
        msg_text = self._get_msg_text(target)
        self.assertIn("middling and average Terran male", msg_text)
        self.assertIn("|wHe|n waves back", msg_text)

    def test_emote_target_pronoun_mid_sentence(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.gender = "male"
        target.msg = mock.Mock()
        self.call(CmdEmote(), "waves at @walker and nods at @walker.")
        msg_text = self._get_msg_text(target)
        self.assertIn("middling and average Terran male", msg_text)
        self.assertIn("|whim|n", msg_text)

    def test_emote_target_possessive_on_repeat(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.gender = "male"
        target.msg = mock.Mock()
        self.call(CmdEmote(), "looks at @walker and pats @walker's gear.")
        msg_text = self._get_msg_text(target)
        self.assertIn("middling and average Terran male", msg_text)
        self.assertIn("|whis|n gear", msg_text)

    def test_emote_target_possessive_sentence_start(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.gender = "female"
        target.msg = mock.Mock()
        self.call(CmdEmote(), "looks at @walker. @walker's blade gleams.")
        msg_text = self._get_msg_text(target)
        self.assertIn("|wHer|n blade gleams", msg_text)

    def test_emote_target_pronoun_sentence_start(self):
        self.char1.apply_species("terran")
        self.char1.location = self.room1
        target = self._dual()
        target.location = self.room1
        target.gender = "female"
        target.msg = mock.Mock()
        self.call(CmdEmote(), "waves at @walker. @walker waves back.")
        msg_text = self._get_msg_text(target)
        self.assertIn("|wShe|n", msg_text)


class AppearanceParagraphTest(EvenniaCommandTest):
    """Tests for the expanded appearance_paragraph shown on 'look'."""

    def _visarii(self):
        c = create_object("typeclasses.characters.Character", key="Prism")
        c.apply_species("visarii")
        return c

    def test_paragraph_basic_terran(self):
        self.char1.apply_species("terran")
        self.char1.appearance_height = "tall"
        self.char1.appearance_build = "lean"
        self.char1.gender = "male"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("male Terran", para)
        self.assertIn("lean of frame with little waste upon your form", para)
        self.assertIn("taller than average with a commanding presence", para)

    def test_paragraph_pose_opening(self):
        self.char1.apply_species("terran")
        self.char1.pose = "sitting"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Before you sits", para)

    def test_paragraph_adjective_sentence(self):
        self.char1.apply_species("visarii")
        self.char1.appearance_adjective = "translucent"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("translucent body", para)

    def test_paragraph_height_description(self):
        self.char1.apply_species("terran")
        self.char1.appearance_height = "towering"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("enormous, towering over most who stand nearby", para)

    def test_paragraph_build_description(self):
        self.char1.apply_species("terran")
        self.char1.appearance_build = "muscular"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("powerfully built with thick cords of muscle", para)

    def test_paragraph_eyes(self):
        self.char1.apply_species("visarii")
        self.char1.appearance_eyes = "faceted"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Faceted eyes catch the light", para)

    def test_paragraph_eye_color(self):
        self.char1.apply_species("visarii")
        self.char1.appearance_eyes = "luminous"
        self.char1.appearance_eye_color = "violet"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Luminous", para)
        self.assertIn("violet", para)
        self.assertIn("eyes glow", para)

    def test_paragraph_hair(self):
        self.char1.apply_species("terran")
        self.char1.appearance_hair = "braided"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Neat braids", para)

    def test_paragraph_hair_color(self):
        self.char1.apply_species("terran")
        self.char1.appearance_hair = "long"
        self.char1.appearance_hair_color = "black"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Long", para)
        self.assertIn("black", para)
        self.assertIn("hair", para)

    def test_paragraph_skin_tone(self):
        self.char1.apply_species("terran")
        self.char1.appearance_skin = "bronze"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("bronze", para)
        self.assertIn("hue", para)

    def test_paragraph_skin_hex_colored(self):
        self.char1.apply_species("terran")
        self.char1.appearance_skin = "bronze"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("|", para)
        self.assertIn("bronze", para)

    def test_paragraph_possessive_pronoun_male(self):
        self.char1.apply_species("visarii")
        self.char1.gender = "male"
        self.char1.appearance_adjective = "translucent"
        observer = self._visarii()
        para = self.char1.appearance_paragraph(observer)
        self.assertIn("His ", para)
        self.assertNotIn("Their ", para)

    def test_paragraph_possessive_pronoun_female(self):
        self.char1.apply_species("visarii")
        self.char1.gender = "female"
        self.char1.appearance_adjective = "translucent"
        observer = self._visarii()
        para = self.char1.appearance_paragraph(observer)
        self.assertIn("Her ", para)
        self.assertNotIn("Their ", para)

    def test_paragraph_possessive_pronoun_neuter(self):
        self.char1.apply_species("visarii")
        self.char1.gender = "neuter"
        self.char1.appearance_adjective = "translucent"
        observer = self._visarii()
        para = self.char1.appearance_paragraph(observer)
        self.assertIn("Its ", para)
        self.assertNotIn("Their ", para)

    def test_paragraph_self_view_uses_your(self):
        self.char1.apply_species("visarii")
        self.char1.gender = "male"
        self.char1.appearance_adjective = "translucent"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Your ", para)
        self.assertNotIn("Their ", para)
        self.assertNotIn("His ", para)

    def test_paragraph_observer_gets_pronouns(self):
        self.char1.apply_species("visarii")
        self.char1.gender = "female"
        self.char1.appearance_adjective = "translucent"
        observer = self._visarii()
        para = self.char1.appearance_paragraph(observer)
        self.assertIn("Her ", para)
        self.assertNotIn("Their ", para)

    def test_paragraph_visarii_skin_sentence(self):
        self.char1.apply_species("visarii")
        self.char1.appearance_skin = "violet"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("crystalline surface", para)

    def test_paragraph_silex_skin_sentence(self):
        self.char1.apply_species("silex")
        self.char1.appearance_skin = "obsidian"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("stone flesh", para)

    def test_paragraph_volucres_skin_sentence(self):
        self.char1.apply_species("volucres")
        self.char1.appearance_skin = "fair"
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("feathers", para)

    def test_paragraph_missing_optional_attrs(self):
        self.char1.apply_species("terran")
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("neuter Terran", para)

    def test_paragraph_species_name_in_output(self):
        self.char1.apply_species("visarii")
        para = self.char1.appearance_paragraph(self.char1)
        self.assertIn("Visarii", para)

    def test_paragraph_observer_sees_paragraph(self):
        self.char1.apply_species("terran")
        self.char1.appearance_height = "tall"
        observer = self._visarii()
        observer.location = self.room1
        self.char1.location = self.room1
        para = self.char1.appearance_paragraph(observer)
        self.assertIn("taller than average, with a commanding presence", para)

    def test_return_appearance_uses_paragraph(self):
        self.char1.apply_species("terran")
        self.char1.appearance_height = "tall"
        self.char1.gender = "male"
        self.char1.db.desc = "A custom description."
        out = self.char1.return_appearance(self.char1)
        self.assertIn("male Terran", out)
        self.assertIn("taller than average, with a commanding presence", out)
        self.assertIn("A custom description.", out)
        # Desc follows the paragraph with a space, not a newline
        idx = out.index("male Terran")
        desc_idx = out.index("A custom description.")
        between = out[idx:desc_idx]
        self.assertNotIn("\n", between.strip())


class BuilderAppearanceCommandsTest(EvenniaCommandTest):
    """Tests for the new builder appearance commands."""

    def _visarii(self):
        c = create_object("typeclasses.characters.Character", key="Prism")
        c.apply_species("visarii")
        return c

    def test_seteyes_valid(self):
        self.char1.apply_species("visarii")
        self.call(CmdSetEyes(), "faceted")
        self.assertEqual(self.char1.appearance_eyes, "faceted")

    def test_seteyes_invalid(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdSetEyes(), "square")
        self.assertIn("Invalid", out)

    def test_seteyes_no_species(self):
        out = self.call(CmdSetEyes(), "round")
        self.assertIn("no species", out)

    def test_seteyes_list_options(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdSetEyes(), "")
        self.assertIn("faceted", out)

    def test_seteyes_clear(self):
        self.char1.apply_species("visarii")
        self.call(CmdSetEyes(), "faceted")
        self.call(CmdSetEyes(), "none")
        self.assertIsNone(self.char1.appearance_eyes)

    def test_seteyecolor_valid(self):
        self.char1.apply_species("visarii")
        self.call(CmdSetEyeColor(), "violet")
        self.assertEqual(self.char1.appearance_eye_color, "violet")

    def test_seteyecolor_invalid(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdSetEyeColor(), "rainbow")
        self.assertIn("Invalid", out)

    def test_sethair_valid(self):
        self.char1.apply_species("terran")
        self.call(CmdSetHair(), "braided")
        self.assertEqual(self.char1.appearance_hair, "braided")

    def test_sethair_invalid(self):
        self.char1.apply_species("terran")
        out = self.call(CmdSetHair(), "mohawk")
        self.assertIn("Invalid", out)

    def test_sethaircolor_valid(self):
        self.char1.apply_species("terran")
        self.call(CmdSetHairColor(), "black")
        self.assertEqual(self.char1.appearance_hair_color, "black")

    def test_sethaircolor_invalid(self):
        self.char1.apply_species("terran")
        out = self.call(CmdSetHairColor(), "plaid")
        self.assertIn("Invalid", out)

    def test_seteyes_on_target(self):
        self.char1.apply_species("visarii")
        target = self._visarii()
        target.location = self.room1
        self.call(CmdSetEyes(), f"faceted = {target.name}")
        self.assertEqual(target.appearance_eyes, "faceted")

    def test_seteyecolor_list_shows_hex(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdSetEyeColor(), "")
        self.assertIn("(#b0a0f0)", out)
        self.assertIn("violet", out)

    def test_sethaircolor_list_shows_hex(self):
        self.char1.apply_species("terran")
        out = self.call(CmdSetHairColor(), "")
        self.assertIn("(#1a1a1a)", out)
        self.assertIn("black", out)

    def test_setskin_list_shows_hex(self):
        self.char1.apply_species("visarii")
        out = self.call(CmdSetSkin(), "")
        self.assertIn("(#a99ad4)", out)
        self.assertIn("ghost-violet", out)

    def test_color_list_with_hex_formatting(self):
        from world.data.appearance import color_list_with_hex
        result = color_list_with_hex(["violet", "silver"])
        self.assertIn("(#b0a0f0)", result)
        self.assertIn("(#dcdcdc)", result)
        self.assertIn("violet", result)
        self.assertIn("silver", result)