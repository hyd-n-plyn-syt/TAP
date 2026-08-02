"""Unit tests for the world/systems modules (skills, growth, stats) using mocks."""

from django.test import SimpleTestCase

from world.systems import growth, skills, stats
from world.tests._mock import MockChar


class GrowthTest(SimpleTestCase):
    def test_threshold_rises_with_value(self):
        self.assertEqual(growth.threshold_for(0), 5.0)
        self.assertGreater(growth.threshold_for(2), growth.threshold_for(1))

    def test_add_stat_xp_raises_after_threshold(self):
        char = MockChar()
        # base is 1, so threshold is 5 + 3*1 = 8
        ok, gained, value = growth.add_stat_xp(char, "corpus", "potestas", 8.0)
        self.assertTrue(ok)
        self.assertEqual(gained, 1)
        self.assertEqual(value, 2)
        self.assertEqual(char.corpus_potestas, 2)

    def test_add_stat_xp_sub_threshold_accumulates(self):
        char = MockChar()
        ok, gained, value = growth.add_stat_xp(char, "genius", "reflexus", 3.0)
        self.assertTrue(ok)
        self.assertEqual(gained, 0)
        self.assertEqual(value, 1)
        self.assertAlmostEqual(char.stat_xp["genius_reflexus"], 3.0)

    def test_add_stat_xp_refuses_locked_column(self):
        char = MockChar(species_key="visarii")
        ok, gained, value = growth.add_stat_xp(char, "corpus", "potestas", 100.0)
        self.assertFalse(ok)
        self.assertEqual(gained, 0)
        self.assertIsNone(value)

    def test_stat_xp_to_next(self):
        char = MockChar()
        self.assertEqual(growth.stat_xp_to_next(char, "corpus", "potestas"), 8.0)
        growth.add_stat_xp(char, "corpus", "potestas", 2.0)
        self.assertEqual(growth.stat_xp_to_next(char, "corpus", "potestas"), 6.0)


class SkillGrowthTest(SimpleTestCase):
    def test_use_unknown_skill_returns_none(self):
        self.assertIsNone(skills.use_skill(MockChar(), "nope"))

    def test_use_not_learned_reports_unknown(self):
        result = skills.use_skill(MockChar(), "attack")
        self.assertIsNotNone(result)
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "unknown")

    def test_use_learned_skill_advances_skill_and_stats(self):
        char = MockChar()
        skills.learn_skill(char, "attack")
        result = skills.use_skill(char, "attack", difficulty="medium")
        self.assertTrue(result["success"])
        self.assertGreater(result["skill_xp"], 0)
        self.assertGreater(result["stat_xp"], 0)
        self.assertEqual(char.skills["attack"], 1)  # 15 xp buys one point (cost 10)
        self.assertGreater(char.stat_xp.get("corpus_potestas", 0), 0)

    def test_use_repeats_accumulate_to_point(self):
        char = MockChar()
        skills.learn_skill(char, "attack")
        for _ in range(5):
            skills.use_skill(char, "attack", difficulty="extreme")
        # each extreme use is 40 xp; point cost tier 1 is 10
        self.assertGreaterEqual(char.skills["attack"], 1)

    def test_diminishing_returns_high_tier(self):
        char = MockChar()
        skills.learn_skill(char, "attack", value=900)
        first = skills.use_skill(char, "attack", difficulty="medium")
        skills.learn_skill(char, "meditate")
        second = skills.use_skill(char, "meditate", difficulty="medium")
        self.assertGreater(second["skill_xp"], first["skill_xp"])

    def test_prereq_gating(self):
        char = MockChar()
        ok, _ = skills.learn_skill(char, "power_strike")
        self.assertFalse(ok)
        self.assertFalse(skills.prereqs_met(char, "power_strike"))
        self.assertIn("attack", skills.missing_prereqs(char, "power_strike"))

    def test_use_respects_prereqs(self):
        char = MockChar()
        char.skills = {"power_strike": 0}  # force-set past the learning gate
        result = skills.use_skill(char, "power_strike")
        self.assertFalse(result["success"])
        self.assertEqual(result["reason"], "prereq")

    def test_learn_enforces_value_cap(self):
        char = MockChar()
        ok, _ = skills.learn_skill(char, "punch", value=5000)
        self.assertTrue(ok)
        self.assertEqual(char.skills["punch"], skills.MAX_SKILL)

    def test_known_skills_sorted(self):
        char = MockChar()
        skills.learn_skill(char, "kick")
        skills.learn_skill(char, "attack")
        self.assertEqual([k for k, _ in skills.known_skills(char)], ["attack", "kick"])


class EffectiveStatsTest(SimpleTestCase):
    def test_default_species_uses_own_stats(self):
        char = MockChar()
        self.assertEqual(skills.effective_skill_stats(char, "feint"),
                         {"corpus_reflexus": 0.7, "genius_reflexus": 0.3})

    def test_visarii_remaps_corpus_to_animus(self):
        char = MockChar(species_key="visarii")
        stats_map = skills.effective_skill_stats(char, "punch")
        self.assertNotIn("corpus_potestas", stats_map)
        self.assertIn("animus_potestas", stats_map)
        self.assertIn("animus_reflexus", stats_map)
        self.assertEqual(stats_map["animus_potestas"] + stats_map["animus_reflexus"], 1.0)

    def test_unknown_skill_has_no_effective_stats(self):
        self.assertEqual(skills.effective_skill_stats(MockChar(), "nope"), {})


class StatsSchemaTest(SimpleTestCase):
    def test_main_stat_is_sum(self):
        char = MockChar()
        self.assertEqual(stats.main_stat(char, "corpus"), 3)

    def test_effective_sub_stat_applies_bonus(self):
        char = MockChar(species_key="terran")  # terran: genius_obsistis +1
        self.assertEqual(stats.effective_sub_stat(char, "genius", "obsistis"), 2)

    def test_locked_column_reads_zero(self):
        char = MockChar(species_key="visarii")
        self.assertEqual(stats.main_stat(char, "corpus"), 0)
        self.assertEqual(stats.effective_sub_stat(char, "corpus", "potestas"), 0)

    def test_zeroed_pool_pinned_to_zero(self):
        char = MockChar(species_key="visarii")
        pools = stats.derived_pools(char)
        self.assertEqual(pools["vigor"], 0)
        self.assertEqual(pools["vigor_regen"], 0)

    def test_derived_pools_positive_generic(self):
        char = MockChar()
        pools = stats.derived_pools(char)
        for pool in ("vigor", "vim", "mens"):
            self.assertGreater(pools[pool], 0, pool)
            self.assertGreater(pools[f"{pool}_regen"], 0, pool)