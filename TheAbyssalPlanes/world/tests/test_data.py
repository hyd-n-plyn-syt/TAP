"""Tests for the pure-data modules in world/data (skills, species, rankings)."""

from django.test import SimpleTestCase

from world.data import rankings, skills, species

MAINS = ("corpus", "genius", "animus")
SUBS = ("potestas", "reflexus", "obsistis")


def _all_stat_keys():
    return {f"{m}_{s}" for m in MAINS for s in SUBS}


class SkillCatalogTest(SimpleTestCase):
    def test_tiers(self):
        self.assertEqual(len(skills.TIER_NAMES), 10)
        self.assertEqual(len(skills.TIER_COLORS), 10)
        self.assertEqual(skills.TIER_NAMES[0], "Novice")
        self.assertEqual(skills.TIER_NAMES[-1], "Grandmaster")

    def test_difficulty_xp_positive(self):
        for difficulty, xp in skills.DIFFICULTY_XP.items():
            self.assertGreater(xp, 0, difficulty)

    def test_every_skill_is_well_formed(self):
        valid = _all_stat_keys()
        keys = [s["key"] for s in skills.SKILLS.values()]
        self.assertEqual(len(keys), len(set(keys)), "skill keys must be unique")
        for skill in skills.SKILLS.values():
            self.assertEqual(skill["key"], skill["key"].lower())
            self.assertTrue(skill["name"])
            self.assertTrue(skill["category"])
            self.assertTrue(set(skill["stats"]).issubset(valid), skill["key"])
            self.assertAlmostEqual(sum(skill["stats"].values()), 1.0, places=6, msg=skill["key"])
            for prereq in skill["requires"]:
                self.assertIn(prereq, skills.SKILLS, skill["key"])

    def test_get_skill_normalizes(self):
        self.assertIs(skills.get_skill("POWER_STRIKE"), skills.SKILLS["power_strike"])
        self.assertIsNone(skills.get_skill("power strike"))  # a name, not a key
        self.assertIsNone(skills.get_skill(None))
        self.assertIsNone(skills.get_skill("nope"))

    def test_skill_key_resolves(self):
        self.assertEqual(skills.skill_key("feint"), "feint")
        self.assertEqual(skills.skill_key("Focused Meditation"), "focused_meditation")
        self.assertIsNone(skills.skill_key("not a skill"))

    def test_advanced_skills_have_prereqs(self):
        self.assertEqual(skills.SKILLS["power_strike"]["requires"], {"attack": 300, "punch": 300})
        self.assertEqual(skills.SKILLS["focused_meditation"]["requires"], {"meditate": 400})

    def test_categories_present(self):
        cats = skills.categories()
        self.assertIn("combat", cats)
        self.assertIn("meta", cats)


class SpeciesCatalogTest(SimpleTestCase):
    def test_species_count(self):
        self.assertEqual(len(species.species_keys()), 9)

    def test_every_species_is_well_formed(self):
        for spec in species.SPECIES.values():
            self.assertEqual(spec["key"], spec["key"].lower())
            self.assertIn(spec["visarial_nature"], {"dual_natured", "visarial", "physical"})
            self.assertEqual(spec["default_visarial_state"], "normal")
            self.assertIsInstance(spec["locked_main_stats"], tuple)
            self.assertLessEqual(set(spec["locked_main_stats"]), {"corpus", "animus"})

    def test_locked_alternates_match_locked_mains(self):
        for spec in species.SPECIES.values():
            for locked_, alt in spec.get("locked_alternates", {}).items():
                self.assertIn(locked_, spec["locked_main_stats"])
                self.assertNotEqual(locked_, alt)
                self.assertNotIn(alt, spec["locked_main_stats"])

    def test_zeroed_pools_are_valid(self):
        valid = {"vigor", "vim", "mens"}
        for spec in species.SPECIES.values():
            self.assertLessEqual(set(spec["zeroed_pools"]), valid, spec["key"])

    def test_visarii_and_silex_lock_opposite_columns(self):
        visarii = species.SPECIES["visarii"]
        silex = species.SPECIES["silex"]
        self.assertEqual(visarii["locked_main_stats"], ("corpus",))
        self.assertEqual(visarii["locked_alternates"], {"corpus": "animus"})
        self.assertEqual(silex["locked_main_stats"], ("animus",))
        self.assertEqual(silex["locked_alternates"], {"animus": "corpus"})

    def test_alternate_for(self):
        self.assertEqual(species.alternate_for("visarii", "corpus"), "animus")
        self.assertEqual(species.alternate_for("silex", "animus"), "corpus")
        self.assertIsNone(species.alternate_for("terran", "corpus"))
        self.assertIsNone(species.alternate_for(None, "corpus"))

    def test_helpers(self):
        self.assertTrue(species.is_locked("visarii", "corpus"))
        self.assertFalse(species.is_locked("visarii", "animus"))
        self.assertFalse(species.is_locked("terran", "animus"))
        self.assertEqual(species.stat_bonus("virentes", "genius_potestas"), 1)
        self.assertEqual(species.stat_bonus("visarii", "animus_potestas"), 1)


class RankingLadderTest(SimpleTestCase):
    def test_bounds(self):
        self.assertEqual(rankings.rank_name(0), "none")
        self.assertEqual(rankings.rank_name(-5), "none")
        self.assertEqual(rankings.rank_name(1_000_000), "ungodly")

    def test_thresholds_ascending_and_unique(self):
        minima = [rank[0] for rank in rankings.RANKS]
        self.assertEqual(minima, sorted(minima))
        names = [rank[1] for rank in rankings.RANKS]
        self.assertEqual(len(names), len(set(names)), "rank names must be unique")

    def test_rank_at_each_threshold(self):
        for minimum, name, _ in rankings.RANKS:
            self.assertEqual(rankings.rank_name(minimum), name)

    def test_helpers_agree(self):
        for total in range(0, 120):
            idx = rankings.rank_index(total)
            self.assertEqual(rankings.rank_name(total), rankings.RANKS[idx][1])
            self.assertEqual(rankings.rank_color(total), rankings.RANKS[idx][2])
            self.assertEqual(rankings.rank_threshold(idx), rankings.RANKS[idx][0])


class SkillEquationTest(SimpleTestCase):
    def test_tier_math(self):
        from world.systems import skills as sys

        self.assertEqual(sys.tier(-5), 1)
        self.assertEqual(sys.tier(0), 1)
        self.assertEqual(sys.tier(99), 1)
        self.assertEqual(sys.tier(100), 2)
        self.assertEqual(sys.tier(900), 10)
        self.assertEqual(sys.tier(1000), 10)

    def test_tier_name_and_within(self):
        from world.systems import skills as sys

        self.assertEqual(sys.tier_name(150), "Apprentice")
        self.assertEqual(sys.within_tier(150), 50)
        self.assertEqual(sys.within_tier(99), 99)

    def test_requirement_str(self):
        from world.systems import skills as sys

        self.assertEqual(sys.requirement_str(0), "0% Novice")
        self.assertEqual(sys.requirement_str(50), "50% Novice")
        self.assertEqual(sys.requirement_str(300), "0% Adept")
        self.assertEqual(sys.requirement_str(350), "50% Adept")

    def test_point_cost_rises_with_tier(self):
        from world.systems import skills as sys

        costs = [sys.point_cost(t) for t in range(1, 11)]
        self.assertEqual(costs, sorted(costs))
        self.assertEqual(costs[0], 10.0)

    def test_tapers_shrink(self):
        from world.systems import skills as sys

        self.assertEqual(sys.skill_taper(1), 1.0)
        self.assertLess(sys.skill_taper(10), sys.skill_taper(2))
        self.assertLess(sys.stat_taper(10), sys.stat_taper(2))