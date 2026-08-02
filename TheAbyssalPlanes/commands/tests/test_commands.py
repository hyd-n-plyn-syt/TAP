"""Integration tests for player commands using Evennia's in-DB test harness."""

from evennia.utils.test_resources import EvenniaCommandTest

from commands.player.skills import CmdSkills
from commands.player.train import CmdTrain


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