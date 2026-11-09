"""Structural tests of the taxonomy (taxonomy.py): complete, consistent, mutually exclusive on paper.
python -m unittest discover -s tests"""
import re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import taxonomy as T  # noqa: E402

REQUIRED = ("name", "definition", "rule", "include", "exclude", "effect", "confirm", "example", "detectors", "severity", "status")
RELEASED_DETECTORS = {"lapsed_limit", "repeal_gap", "dead_currency", "placeholder_ref", "same_day_conflict", "retroactive_date",
                      "dead_act_ref", "stale_amount", "dup_label", "late_extension", "missing_paragraph", "publisher_flag",
                      "dangling_ref", "authority_gap", "organic_reserve", "dead_fine"}


class Structure(unittest.TestCase):
    def test_every_category_complete(self):
        for code, c in T.C.items():
            for k in REQUIRED:
                self.assertTrue(c[k] not in (None, "", []) or k == "exclude" or (k == "detectors" and "no detector" in c["status"]), f"{code} lacks {k}")
            self.assertIn(c["family"], T.FAMILIES, code)
            self.assertIn(c["effect"], T.EFFECTS, code)
            self.assertTrue(1 <= c["severity"] <= 5, code)

    def test_codes_are_family_prefixed_and_unique(self):
        self.assertEqual(len(T.C), len(set(T.C)))
        for code in T.C:
            self.assertRegex(code, r"^[A-E]\d$")

    def test_every_released_detector_has_a_category(self):
        self.assertFalse(RELEASED_DETECTORS - set(T.DETECTORS), "detectors without a category")
        for d, code in T.DETECTORS.items():
            self.assertIn(code, T.C, d)

    def test_every_category_except_new_ones_is_fed_by_a_detector(self):
        fed = set(T.DETECTORS.values()) | {T.classify("publisher_flag", {"summary": "[sic]"})[0]}  # E5 via the conditional rule
        self.assertEqual(sorted(set(T.C) - fed), ["C3"], "only C3 (decree-laws) may lack a detector for now")

    def test_exclusions_point_somewhere_real(self):
        """an exclusion either names another category (-> X9) or says it is not a defect / cured / cosmetic."""
        for code, c in T.C.items():
            for e in c["exclude"]:
                targets = re.findall(r"->\s*([A-E]\d)", e)
                for t in targets:
                    self.assertIn(t, T.C, f"{code}: exclusion points at unknown {t}")
                    self.assertNotEqual(t, code, f"{code}: exclusion points at itself")
                self.assertTrue(targets or re.search(r"not a defect|not_a_defect|cured|corpus error|detector error|nothing", e), f"{code}: '{e}'")

    def test_boundaries_are_symmetric_where_it_matters(self):
        """if A says 'X -> B', B should mention A (in its exclusions or definition), so the pair is decided from both sides."""
        pairs = [("A1", "A2"), ("A1", "A3"), ("A1", "A4"), ("A2", "A4"), ("B1", "B2"), ("B2", "B3"), ("B2", "E4"), ("E1", "B2"), ("E2", "A3"), ("C1", "C4"), ("A3", "E5")]
        for a, b in pairs:
            text_a = " ".join(T.C[a]["exclude"]); text_b = " ".join(T.C[b]["exclude"]) + T.C[b]["definition"]
            self.assertIn(b, text_a + " ".join(T.C[a]["include"]), f"{a} does not point at {b}")
            self.assertTrue(a in text_b or b in text_a, f"{b} silent about {a}")


class Mapping(unittest.TestCase):
    def test_classify_conditional_rules(self):
        self.assertEqual(T.classify("placeholder_ref", {"summary": "Ordnungswidrig handelt, wer entgegen § 12"}), ("A2", "flagged"))
        self.assertEqual(T.classify("placeholder_ref", {"summary": "nach § 12 gilt"}), ("A1", "flagged"))
        self.assertEqual(T.classify("retroactive_date", {"summary": "in force 2022-01-01, published 2022-01-05"}), ("B1", "flagged"))
        self.assertEqual(T.classify("repeal_gap", {"review": "artefact"}), ("E1", "corpus_error"))
        self.assertEqual(T.classify("dead_act_ref", {"review": "cured_or_harmless"}), ("A4", "not_a_defect"))
        self.assertEqual(T.classify("publisher_flag", {"summary": "Chimie inorganique (SIC)"}), ("E5", "flagged"))
        self.assertEqual(T.classify("publisher_flag", {"summary": "Änderung ist nicht ausführbar, da § 50c nicht vorhanden ist"}),
                         ("A3", "flagged"))

    def test_every_verdict_known(self):
        for r in ("", "artefact", "lawful", "harmless", "cured_or_harmless", "candidate_defect", "candidate_defect, rebutted",
                  "candidate_gap", "no_gap, gap not real", "artefact, gap not real", "candidate_defect, survived rebuttal"):
            self.assertIn(T.verdict(r), T.VERDICTS, r)

    def test_confirmed_cases_sit_in_defect_families(self):
        self.assertTrue(all(c[0] in "ABCD" for c in T.CONFIRMED.values()))

if __name__ == "__main__":
    unittest.main()
