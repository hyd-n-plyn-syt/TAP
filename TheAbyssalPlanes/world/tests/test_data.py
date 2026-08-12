"""Tests for the pure-data modules in world/data (skills, species, rankings)."""

import os
import tempfile
import ast
from unittest import mock

from django.test import SimpleTestCase

from world.data import changes, rankings, skills, species

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
        self.assertIs(skills.get_skill("HAYMAKER"), skills.SKILLS["haymaker"])
        self.assertIsNone(skills.get_skill("power strike"))  # removed skill
        self.assertIsNone(skills.get_skill(None))
        self.assertIsNone(skills.get_skill("nope"))

    def test_skill_key_resolves(self):
        self.assertEqual(skills.skill_key("melee feint"), "melee_feint")
        self.assertEqual(skills.skill_key("Focused Meditation"), "focused_meditation")
        self.assertIsNone(skills.skill_key("not a skill"))

    def test_advanced_skills_have_prereqs(self):
        self.assertEqual(skills.SKILLS["haymaker"]["requires"], {"axehandle": 300})
        self.assertEqual(skills.SKILLS["focused_meditation"]["requires"], {"meditate": 400})

    def test_categories_present(self):
        cats = skills.categories()
        self.assertEqual(cats, ["animus", "corpus", "genius"])

    def test_skill_weight_rules(self):
        for key, skill in skills.SKILLS.items():
            stats = skill["stats"]
            self.assertTrue(stats)
            self.assertLessEqual(len(stats), 3)
            self.assertAlmostEqual(sum(stats.values()), 1.0)
            sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
            major_stat, major_weight = sorted_stats[0]
            if len(stats) == 1:
                self.assertEqual(major_weight, 1.0)
            elif len(stats) == 2:
                self.assertGreaterEqual(major_weight, 0.55)
            elif len(stats) == 3:
                self.assertGreaterEqual(major_weight, 0.40)
                self.assertGreater(major_weight, sorted_stats[1][1])
            expected_cat = major_stat.split("_")[0]
            self.assertEqual(skill["category"], expected_cat)


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


class ChangesCatalogTest(SimpleTestCase):
    def test_entries_are_numbered_and_sorted(self):
        self.assertGreaterEqual(len(changes.CHANGES), 1)
        numbers = [c["number"] for c in changes.CHANGES]
        self.assertEqual(numbers, sorted(numbers))
        self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_latest_number_matches_last_entry(self):
        self.assertEqual(changes.latest_number(), changes.CHANGES[-1]["number"])

    def test_get_change(self):
        first = changes.CHANGES[0]
        self.assertIs(changes.get_change(first["number"]), first)
        self.assertIsNone(changes.get_change(9999))

    def test_unread(self):
        latest = changes.latest_number()
        self.assertEqual(changes.unread(latest), [])
        self.assertEqual(len(changes.unread(0)), latest)

    def test_alert_text(self):
        latest = changes.latest_number()
        self.assertIsNone(changes.alert_text(latest))
        alert = changes.alert_text(latest - 1)
        self.assertIn(f"#{latest}", alert)
        self.assertIn("changes", alert)
        self.assertNotIn("more", alert)

    def test_date_formatting(self):
        self.assertEqual(changes.short_date("2026-08-03"), "Aug 3")
        self.assertEqual(changes.full_date("2026-08-03"), "August 3, 2026")

    def test_serialize_single_line_body(self):
        entry = {"number": 11, "date": "2026-08-03", "title": "Short title", "body": "A short body."}
        block = changes._serialize(entry)
        self.assertIn('"number": 11', block)
        self.assertIn('"body": "A short body."', block)

    def test_serialize_wraps_long_body(self):
        entry = {"number": 11, "date": "2026-08-03", "title": "T", "body": "word " * 30}
        block = changes._serialize(entry)
        self.assertIn('"body": (', block)

    def test_serialize_escapes_quotes(self):
        entry = {"number": 11, "date": "2026-08-03", "title": 'Say "hi"', "body": "it's fine"}
        block = changes._serialize(entry)
        self.assertIn('\\"hi\\"', block)
        self.assertIn("it's fine", block)

    def test_append_entry_writes_file_and_updates_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "changes.py")
            with open(changes.CHANGES_FILE, encoding="utf-8") as f:
                source = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            with mock.patch.object(changes, "CHANGES", list(changes.CHANGES)):
                entry = changes.append_entry("A brand new title", "Its body text.", filepath=path)
                self.assertEqual(entry["number"], changes.latest_number())
                self.assertIs(changes.get_change(entry["number"]), entry)
            with open(path, encoding="utf-8") as f:
                new_source = f.read()
            import ast

            ast.parse(new_source)
            self.assertIn("A brand new title", new_source)
            self.assertIn("Its body text.", new_source)

    def test_append_entry_requires_title_and_body(self):
        with self.assertRaises(ValueError):
            changes.append_entry("   ", "body")
        with self.assertRaises(ValueError):
            changes.append_entry("title", "   ")

    def test_remove_entry_renumbers_and_writes_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "changes.py")
            with open(changes.CHANGES_FILE, encoding="utf-8") as f:
                source = f.read()
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            fake_changes = [
                {"number": 1, "date": "2026-08-01", "title": "First", "body": "One"},
                {"number": 2, "date": "2026-08-02", "title": "Second", "body": "Two"},
                {"number": 3, "date": "2026-08-03", "title": "Third", "body": "Three"},
            ]
            with mock.patch.object(changes, "CHANGES", fake_changes), \
                    mock.patch.object(changes, "CHANGES_FILE", path):
                removed = changes.remove_entry(2, filepath=path)
                self.assertEqual(removed["title"], "Second")
                self.assertEqual(len(changes.CHANGES), 2)
                self.assertEqual(changes.CHANGES[0]["number"], 1)
                self.assertEqual(changes.CHANGES[0]["title"], "First")
                self.assertEqual(changes.CHANGES[1]["number"], 2)
                self.assertEqual(changes.CHANGES[1]["title"], "Third")
            with open(path, encoding="utf-8") as f:
                new_source = f.read()
            ast.parse(new_source)
            self.assertIn("First", new_source)
            self.assertIn("Third", new_source)
            self.assertNotIn("Second", new_source)

    def test_remove_entry_missing_raises_value_error(self):
        with mock.patch.object(changes, "CHANGES", [{"number": 1, "date": "2026-08-01", "title": "T", "body": "B"}]):
            with self.assertRaises(ValueError):
                changes.remove_entry(99)
