"""Austrian case law in the tree: a corpus of decision texts of the Verfassungsgerichtshof (lexifina/austria-
verfassungsgerichtshof-caselaw and the other Austrian courts' -caselaw repos), read with the same tools as law, on a
small tree built here: Austrian law (Art. 7 B-VG in two versions, § 4 DSG) and a case-law corpus (three decisions, a
correction, a decision index, the judgment overlay, and the CC BY 4.0 credit RIS asks for: "Datenquelle: RIS").

  python -m unittest tests.test_caselaw_at -v

One test per feature of the feature list, plus the Austrian forms: decisions by Geschäftszahl ("G 123/2024",
"1 Ob 123/20a", "Ra 2020/01/0123") and ECLI, articles "Art 7 B-VG", "§ 4 Abs 1 DSG", never read as German law.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True

LAW = 'austria/bund/acts'
CASES = 'austria/verfassungsgerichtshof/caselaw'
ART = f'{LAW}/b-vg/art-007.md'
DSG4 = f'{LAW}/dsg/art-002/par-0004.md'
D1 = 'decisions/verfassungsgerichtshof-vfgh/2010/JFT_20100505_09G00123_00.md'
D2 = 'decisions/verfassungsgerichtshof-vfgh/2016/JFT_20160601_15G00100_00.md'
D3 = 'decisions/verfassungsgerichtshof-vfgh/2024/JFT_20240303_24G00123_00.md'
CREDIT = 'Datenquelle: RIS - Rechtsinformationssystem des Bundes (www.ris.bka.gv.at), Bundeskanzleramt; CC BY 4.0'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return (f'---\ncourt: "Verfassungsgerichtshof (VfGH)"\nsource: "RIS - Rechtsinformationssystem des Bundes, Bundeskanzleramt"\n'
            f'licence: "CC BY 4.0"\n---\n\n# {title}\n\n{text}\n')


class AustrianCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'de-aliases.json'):
            shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Austrian federal law', 'language': 'de', 'in_force_trailer': 'In-force', 'code': 'AT'},
            {'path': CASES, 'name': 'Case law: Verfassungsgerichtshof', 'language': 'de', 'kind': 'judgments', 'credit': CREDIT,
             'licence': 'CC BY 4.0', 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'AT'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('BGBl. Nr. 1/1930', {'b-vg/art-007.md': '# Artikel 7\n\n(1) Alle Staatsbürger sind vor dem Gesetz gleich.\n',
                                        'dsg/art-002/par-0004.md': '# § 4\n\nPersonenbezogene Daten dürfen verarbeitet werden.\n'},
                   In_force='1930-01-03', Kind='law')
        cls.v2020 = law.commit('BGBl. I Nr. 24/2020', {'b-vg/art-007.md': '# Artikel 7\n\n(1) Alle Staatsbürger sind vor dem Gesetz '
                                                                          'gleich. Niemand darf benachteiligt werden.\n'},
                               In_force='2020-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Verfassungsgerichtshof (VfGH) G 123/09', {D1: decision('VfGH G 123/09', 'Die Bestimmung ist verfassungswidrig.\nSie wird aufgehoben.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Verfassungsgerichtshof (VfGH)', Docket='G 123/09',
                 ECLI='ECLI:AT:VFGH:2010:G123.2009', Cites=f'{ART} (Art 7 B-VG)')
        c.commit('Verfassungsgerichtshof (VfGH) G 123/09', {D1: decision('VfGH G 123/09', 'Die Bestimmung ist verfassungswidrig.\nSie wird als verfassungswidrig aufgehoben.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='G 123/09')
        c.commit('Verfassungsgerichtshof (VfGH) G 100/2015', {D2: decision('VfGH G 100/2015', 'Der Gleichheitsgrundsatz ist nicht verletzt.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Verfassungsgerichtshof (VfGH)', Docket='G 100/2015',
                 ECLI='ECLI:AT:VFGH:2016:G100.2015', Cites=f'{ART} (Art. 7 Abs. 1 B-VG)')
        c.commit('Verfassungsgerichtshof (VfGH) G 123/2024', {D3: decision('VfGH G 123/2024', 'Das Gesetz verletzt Art 7 B-VG.')},
                 Kind='court', In_force='2024-03-03', Decided='2024-03-03', Court='Verfassungsgerichtshof (VfGH)', Docket='G 123/2024',
                 ECLI='ECLI:AT:VFGH:2024:G123.2024', Cites=f'{ART} (Art 7 B-VG)')
        url = 'https://ogd.ris.bka.gv.at/Dokument.wxe?Abfrage=Vfgh&Dokumentnummer='
        rows = [{'decided': '2010-05-05', 'name': 'VfGH G 123/09', 'court': 'Verfassungsgerichtshof (VfGH)', 'citation': 'ECLI:AT:VFGH:2010:G123.2009',
                 'url': url + 'JFT_20100505_09G00123_00', 'how': 'Art 7 B-VG', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'VfGH G 100/2015', 'court': 'Verfassungsgerichtshof (VfGH)', 'citation': 'ECLI:AT:VFGH:2016:G100.2015',
                 'url': url + 'JFT_20160601_15G00100_00', 'how': 'Art. 7 Abs. 1 B-VG', 'mentions': 2, 'decision': D2},
                {'decided': '2024-03-03', 'name': 'VfGH G 123/2024', 'court': 'Verfassungsgerichtshof (VfGH)', 'citation': 'ECLI:AT:VFGH:2024:G123.2024',
                 'url': url + 'JFT_20240303_24G00123_00', 'how': 'Art 7 B-VG', 'mentions': 1, 'decision': D3, 'law_commit': cls.v2020}]
        index = 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in (('G 123/09', D1), ('ECLI:AT:VFGH:2010:G123.2009', D1),
                                                                              ('G 100/2015', D2), ('G 123/2024', D3), ('ECLI:AT:VFGH:2024:G123.2024', D3)))
        c.commit('Lexifina', {f'judgments/{LAW}/b-vg/art-007.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': index,
                              'corpus.json': json.dumps({'corpus': 'at/verfassungsgerichtshof/caselaw', 'kind': 'judgments', 'credit': CREDIT,
                                                         'licence': 'CC BY 4.0', 'name': 'Case law: Verfassungsgerichtshof',
                                                         'in_force_trailer': 'In-force'})},
                 Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def cli(self, *args) -> str:
        out, err, code = self.t.cli(*args)
        self.assertEqual(code, 0, err)
        return out + err

    def calls(self, *calls) -> list[dict]:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=json.dumps(calls),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def test_law_py_reads_a_decision(self):
        path = f'{CASES}/{D1}'
        self.assertIn('als verfassungswidrig aufgehoben', self.cli('show', '2012-01-01', path))
        self.assertIn('Sie wird aufgehoben', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Verfassungsgerichtshof (VfGH) G 123/09', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('(court ruling', blame)  # the column cuts "court ruling, not a law" after a long court name
        self.assertIn('correction', blame)
        self.assertIn('(court ruling', self.cli('words', '2012-01-01', path))
        self.assertIn('verfassungswidrig', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_world_and_countries(self):
        laws = self.cli('laws', '1990-01-01', '2030-01-01')
        self.assertIn('BGBl. I Nr. 24/2020', laws)
        self.assertNotIn('G 123/2024', laws)
        decisions = self.cli('laws', '1990-01-01', '2030-01-01', 'austria/caselaw')
        self.assertIn('G 123/2024 (court decision)', decisions)
        self.assertIn('(latest decision), given 2024-03-03', self.cli('world', '2025-01-01'))

        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        self.assertNotIn(CASES, add('austria'))
        self.assertIn(CASES, add('austria/caselaw'))

    def test_check_precedent_and_what_else_changes(self):
        prec, else_ = self.calls(('check_precedent', {'path': ART, 'date': '2025-01-01'}),
                                 ('what_else_changes', {'path': ART, 'date': '2025-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 3)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['ECLI:AT:VFGH:2010:G123.2009']['same_words'])  # before BGBl. I Nr. 24/2020
        self.assertTrue(by['ECLI:AT:VFGH:2024:G123.2024']['same_words'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist, lj = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2025-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}),
            ('list_jurisdictions', {}))
        for a in (read, cmp, who, listed, cases, hist, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('Gleichheitsgrundsatz', read['text'])
        self.assertIn('Datenquelle: RIS', read['text'])
        self.assertIn('verfassungswidrig', cmp['text'])
        self.assertIn('G 123/09', who['text'])
        self.assertIn('VfGH G 100/2015', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('2011-01-01', hist['text'])
        self.assertIn('Datenquelle: RIS', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        answers = self.calls(('search_law', {'query': 'gleich', 'date': '2025-01-01'}),
                             ('search_law', {'query': 'Gleichheitsgrundsatz', 'date': '2025-01-01', 'kind': 'judgments'}),
                             ('search_changes', {'query': 'VfGH'}),
                             ('phrase_history', {'query': 'verfassungswidrig'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, changes, phrase = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(f'{CASES}/', law_only['text'].split('Not read')[0])
        self.assertIn(f'{CASES}/{D2}', judgments['text'])
        self.assertEqual(changes['data']['changes'], [])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])

    def test_decisions_by_geschaeftszahl_and_austrian_citations(self):
        found, details, cites = self.calls(
            ('find_provision', {'query': 'G 123/2024'}),
            ('law_details', {'law': 'G 100/2015'}),
            ('resolve_citations', {'text': 'Art 7 B-VG und § 4 Abs 1 DSG (VfGH G 123/09); vgl. § 823 BGB.', 'date': '2025-01-01'}))
        for a in (found, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(ART, text)
        self.assertIn(DSG4, text)

    def test_austrian_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        self.assertEqual(m.AT_BVG.search('Art. 140 Abs. 1 B-VG').group('num'), '140')
        self.assertEqual(m.AT_DSG.search('§ 4 Abs 1 DSG').group('num'), '4')
        for ref in ('G 123/2024', '1 Ob 123/20a', '15 Os 12/21m', 'Ra 2020/01/0123'):
            self.assertTrue(m.AT_DOCKET.fullmatch(ref), ref)
        # German law is not read as Austrian, nor Austrian as German.
        for other in ('§ 823 Abs. 1 BGB', 'Art. 3 Abs. 1 GG', '1 BvR 123/20', 'VI ZR 123/20'):
            self.assertIsNone(m.AT_BVG.search(other), other)
            self.assertIsNone(m.AT_DSG.search(other), other)
            self.assertIsNone(m.AT_DOCKET.search(other), other)
        self.assertIsNone(m.DE_PARA.search('§ 4 Abs 1 DSG'))


if __name__ == '__main__':
    unittest.main()
