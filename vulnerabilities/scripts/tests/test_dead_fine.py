"""Offline tests for detectors/dead_fine.py: small acts in several languages, no corpus needed.
python -m unittest discover -s tests   (from vulnerabilities/scripts)"""
import sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ingest")); sys.path.insert(0, str(ROOT / "detectors"))
from dead_fine import scan_act, is_penal  # noqa: E402


def refs_of(flags):
    return sorted({(f["path"], f["ref"]) for f in flags})


class Germany(unittest.TestCase):
    ACT = {
        "awaffv/0012.md": "# § 12 (weggefallen)\n",
        "awaffv/0013.md": "# § 13 Schießstätten\n\n(1) Wer eine Schießstätte betreibt, hat sie zu prüfen.\n",
        "awaffv/0034.md": ("# § 34 Ordnungswidrigkeiten\n\nOrdnungswidrig im Sinne des § 53 Abs. 1 Nr. 23 des Waffengesetzes handelt, "
                           "wer vorsätzlich oder fahrlässig\n1. entgegen § 13 Abs. 1 eine Prüfung unterlässt,\n"
                           "11. entgegen § 12 Abs. 2 Satz 2 eine Schießstätte betreibt oder benutzt,\n"
                           "12. entgegen § 60 Abs. 1 des Lebensmittel- und Futtermittelgesetzbuches handelt.\n"),
    }

    def test_flags_dead_item_only(self):
        self.assertEqual(refs_of(scan_act(self.ACT)), [("awaffv/0034.md", "12")])

    def test_trigger_word_raises_score(self):
        f = scan_act(self.ACT)[0]
        self.assertTrue(f["trigger"]); self.assertEqual(f["target_status"], "repealed (placeholder)")

    def test_external_act_same_number_not_flagged(self):
        act = dict(self.ACT); act["awaffv/0060.md"] = "# § 60 (weggefallen)\n"
        self.assertNotIn(("awaffv/0034.md", "60"), refs_of(scan_act(act)))

    def test_deleted_provision(self):
        act = {k: v for k, v in self.ACT.items() if k != "awaffv/0012.md"}
        flags = scan_act(act, frozenset({"12"}))
        self.assertEqual([(f["ref"], f["target_status"]) for f in flags], [("12", "deleted")])

    def test_non_penal_provision_ignored(self):
        act = {"x/0001.md": "# § 1 Zweck\n\nDie Vorschrift des § 2 gilt entsprechend.\n", "x/0002.md": "# § 2 (weggefallen)\n"}
        self.assertEqual(scan_act(act), [])


class Regressions(unittest.TestCase):
    """false positives seen on the live corpora (FuttMV, Fiji VAT Act)."""

    def test_eu_regulation_article_is_not_own_paragraph(self):
        act = {"futtmv/0003.md": "# § 3 (weggefallen)\n",
               "futtmv/0041.md": "# § 41 Ordnungswidrigkeiten\n\n(1)\nOrdnungswidrig handelt, wer gegen die Verordnung (EG) "
                                 "Nr. 1831/2003 verstößt, indem er\n1. entgegen Artikel 3 Absatz 1 einen Zusatzstoff in Verkehr bringt.\n"}
        self.assertEqual(scan_act(act), [])

    def test_section_under_another_act(self):
        act = {"vat/S57.md": "# s 57 [s 57 repealed]\n",
               "vat/S70.md": "# s 70 Offences\n\n(b) Any tax officer who commits an offence under paragraph (a), shall be subject "
                             "to section 57 under the Tax Administration Act 2009.\n"}
        self.assertEqual(scan_act(act), [])

    def test_reference_to_old_version_is_deliberate(self):
        act = {"futtmv/0004.md": "# § 4 (weggefallen)\n",
               "futtmv/0050.md": "# § 50 Übergangsvorschrift\n\nAuf Sachverhalte, die vor dem 24. Dezember 2020 entstanden sind, "
                                 "ist § 4 in der bis zum 23. Dezember 2020 geltenden Fassung weiter anzuwenden; ordnungswidrig "
                                 "handelt, wer entgegen § 4 handelt.\n"}
        self.assertEqual(scan_act(act), [])


class Switzerland(unittest.TestCase):
    def test_busse(self):
        act = {"910.1/art-151.md": "# Art. 151\n\nAufgehoben\n",
               "910.1/art-173.md": "# Art. 173 Übertretungen\n\nMit Busse bis zu 40 000 Franken wird bestraft, wer vorsätzlich "
                                   "die Pflichten nach Artikel 151 verletzt.\n"}
        self.assertEqual(refs_of(scan_act(act)), [("910.1/art-173.md", "151")])


class Spain(unittest.TestCase):
    def test_infracciones(self):
        act = {"ley/a15.md": "## Artículo 15. (Derogado)\n",
               "ley/a40.md": "## Artículo 40. Infracciones graves\n\nConstituyen infracciones graves: a) el incumplimiento de lo "
                             "dispuesto en el artículo 15. b) el incumplimiento del artículo 15 de la Ley 30/1992.\n"}
        flags = scan_act(act)
        self.assertEqual(refs_of(flags), [("ley/a40.md", "15")])


class Brazil(unittest.TestCase):
    def test_multa(self):
        act = {"clt/art-325.md": "Art. 325. (Revogado pela Lei nº 2.800, de 1956)\n",
               "clt/art-347.md": "Art. 347 - Aqueles que exercerem a profissão de químico sem ter preenchido as condições do art. 325 "
                                 "incorrerão na multa de 200 a 5.000 cruzeiros.\n"}
        self.assertEqual(refs_of(scan_act(act)), [("clt/art-347.md", "325")])


class Common(unittest.TestCase):
    def test_offence_contravenes_section(self):
        act = {"boilers/s-047.md": "# 47 [Repealed]\n",
               "boilers/s-050.md": "# 50 Offences\n\nA person who contravenes section 47 commits an offence and is liable on "
                                   "summary conviction to a fine.\n"}
        self.assertEqual(refs_of(scan_act(act)), [("boilers/s-050.md", "47")])

    def test_other_act_section_not_flagged(self):
        act = {"boilers/s-047.md": "# 47 [Repealed]\n",
               "boilers/s-050.md": "# 50 Offences\n\nA person who contravenes section 47 of the Safety Act commits an offence.\n"}
        self.assertEqual(scan_act(act), [])

    def test_live_target_not_flagged(self):
        act = {"a/s-047.md": "# 47 Notice\n\nThe owner shall give notice.\n",
               "a/s-050.md": "# 50 Offences\n\nA person who contravenes section 47 commits an offence.\n"}
        self.assertEqual(scan_act(act), [])


class France(unittest.TestCase):
    def test_puni(self):
        act = {"code/12.md": "# Article 12\n\nAbrogé\n",
               "code/20.md": "# Article 20\n\nEst puni d'une amende de 3 750 euros le fait de méconnaître les dispositions de l'article 12.\n"}
        self.assertEqual(refs_of(scan_act(act)), [("code/20.md", "12")])


class PenalCue(unittest.TestCase):
    POS = ["Ordnungswidrig handelt, wer vorsätzlich", "commits an offence", "Constituyen infracciones leves",
           "incorrerão na multa de", "est puni de six mois", "è punito con la sanzione", "wordt gestraft met",
           "dömes till böter", "kažnjava se novčanom kaznom", "τιμωρείται με φυλάκιση", "para cezası verilir",
           "Mit Busse wird bestraft, wer", "is guilty of an offence"]
    NEG = ["Die Strafprozessordnung gilt entsprechend.", "The penalty rate for late payment is 5 per cent.",
           "La pena de prisión se cumplirá en", "Section 12 applies to this Part.", "El plazo de prescripción es de tres años."]

    def test_positive(self):
        for s in self.POS:
            self.assertTrue(is_penal(s), s)

    def test_negative(self):
        for s in self.NEG:
            self.assertFalse(is_penal(s), s)


class RefscanRegressions(unittest.TestCase):
    """bugs met on the full run of 732 corpora."""

    def test_thousands_dot_in_a_list(self):
        from refscan import refs
        ks = [k for k, _, _ in refs("# Art. 1\n\nNos termos dos arts. 1.048, 1.049 e 1.050 deste Código.\n")]
        self.assertTrue({"1048", "1049", "1050"} <= set(ks), ks)

    def test_thousands_dot_in_a_range(self):
        from refscan import refs
        ks = [k for k, _, _ in refs("# Art. 1\n\nAplica-se o disposto nos arts. 1.048 a 1.050.\n")]
        self.assertIn("1048", ks)

    def test_first_line_without_heading_is_read(self):
        from refscan import refs
        ks = [k for k, _, _ in refs("Art. 347 - Os químicos sem as condições do art. 325 incorrerão na multa.\n")]
        self.assertIn("325", ks)
        self.assertNotIn("347", ks)


if __name__ == "__main__":
    unittest.main()
