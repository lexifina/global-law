"""Finnish case law in the tree: a corpus of decisions of the Korkein oikeus (lexifina/finland-korkein-oikeus-caselaw
and the other Finnish courts' -caselaw repos), read with the same tools as law, on a small tree built here: Finnish law
(työsopimuslaki 7 luku 3 § in two versions, perustuslaki 21 §) and a case-law corpus (three decisions, a correction, a
decision index, the judgment overlay with one row's text_date, and the CC BY 4.0 credit Finlex's licence asks for).

  python -m unittest tests.test_caselaw_fi -v

One test per feature of the feature list, as tests/test_caselaw_nl.py does for the Netherlands, plus the Finnish forms:
decisions by identifier ("KKO:2023:8", Swedish "HD:2023:8") and ECLI, sections by abbreviation ("TSL 7 luku 3 §", "PL
21 §") or by the act's name in the genitive ("työsopimuslain 7 luvun 3 §").
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

LAW = 'finland/national/acts'
CASES = 'finland/korkein-oikeus/caselaw'
ART = f'{LAW}/tyosopimuslaki/luku-07-pykala-003.md'
PL21 = f'{LAW}/perustuslaki/pykala-021.md'
D1 = 'decisions/ennakkopaatokset/2010/KKO-2010-5.md'
D2 = 'decisions/ennakkopaatokset/2016/KKO-2016-40.md'
D3 = 'decisions/ennakkopaatokset/2023/KKO-2023-8.md'
CREDIT = 'Source: Finlex (www.finlex.fi), Ministry of Justice of Finland; CC BY 4.0; retrieved 2026-11-07'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return (f'---\ncourt: "Korkein oikeus"\nsource: "Finlex (www.finlex.fi), Ministry of Justice of Finland"\n'
            f'licence: "CC BY 4.0"\n---\n\n# {title}\n\n## Suomeksi\n\n{text}\n')


class FinnishCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'fi-aliases.json'):
            shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Finnish law', 'language': 'fi', 'in_force_trailer': 'In-force', 'code': 'FI'},
            {'path': CASES, 'name': 'Case law: Korkein oikeus', 'language': 'fi', 'kind': 'judgments', 'credit': CREDIT,
             'licence': 'CC BY 4.0', 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'FI'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('55/2001', {'tyosopimuslaki/luku-07-pykala-003.md': '# 3 § Taloudelliset ja tuotannolliset irtisanomisperusteet\n\n'
                                                                         'Työnantaja saa irtisanoa työsopimuksen, jos työ on vähentynyt.\n',
                               'perustuslaki/pykala-021.md': '# 21 § Oikeusturva\n\nJokaisella on oikeus saada asiansa käsitellyksi.\n'},
                   In_force='2001-06-01', Kind='law')
        cls.v2019 = law.commit('1032/2018', {'tyosopimuslaki/luku-07-pykala-003.md':
                                             '# 3 § Taloudelliset ja tuotannolliset irtisanomisperusteet\n\n'
                                             'Työnantaja saa irtisanoa työsopimuksen, jos työ on vähentynyt olennaisesti ja pysyvästi.\n'},
                               In_force='2019-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Korkein oikeus KKO:2010:5', {D1: decision('KKO:2010:5', 'Irtisanominen oli perusteeton.\nValitus hylätään.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Korkein oikeus', Docket='S2009/12',
                 ECLI='ECLI:FI:KKO:2010:5', Cites=f'{ART} (TSL 7 luku 3 §)')
        c.commit('Korkein oikeus KKO:2010:5', {D1: decision('KKO:2010:5', 'Irtisanominen oli perusteeton.\nValitus hyväksytään.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='S2009/12')
        c.commit('Korkein oikeus KKO:2016:40', {D2: decision('KKO:2016:40', 'Työ oli vähentynyt olennaisesti.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Korkein oikeus', Docket='S2015/100',
                 ECLI='ECLI:FI:KKO:2016:40', Cites=f'{ART} (työsopimuslain 7 luvun 3 §)')
        c.commit('Korkein oikeus KKO:2023:8', {D3: decision('KKO:2023:8', 'Työnantaja oli vastuussa.')},
                 Kind='court', In_force='2023-02-02', Decided='2023-02-02', Court='Korkein oikeus', Docket='S2020/111',
                 ECLI='ECLI:FI:KKO:2023:8', Cites=f'{ART} (TSL 7 luku 3 §)')
        url = 'https://www.finlex.fi/fi/oikeuskaytanto/korkein-oikeus/ennakkopaatokset/'
        rows = [{'decided': '2010-05-05', 'name': 'Korkein oikeus KKO:2010:5', 'court': 'Korkein oikeus', 'citation': 'ECLI:FI:KKO:2010:5',
                 'url': url + '2010/5', 'how': 'TSL 7 luku 3 §', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Korkein oikeus KKO:2016:40', 'court': 'Korkein oikeus', 'citation': 'ECLI:FI:KKO:2016:40',
                 'url': url + '2016/40', 'how': 'työsopimuslain 7 luvun 3 §', 'mentions': 2, 'decision': D2},
                {'decided': '2023-02-02', 'text_date': '2018-06-01', 'name': 'Korkein oikeus KKO:2023:8', 'court': 'Korkein oikeus',
                 'citation': 'ECLI:FI:KKO:2023:8', 'url': url + '2023/8', 'how': 'TSL 7 luku 3 §', 'mentions': 1, 'decision': D3,
                 'law_commit': cls.v2019}]
        index = 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in (('KKO:2010:5', D1), ('ECLI:FI:KKO:2010:5', D1), ('S2009/12', D1),
                                                                              ('KKO:2016:40', D2), ('KKO:2023:8', D3), ('S2020/111', D3)))
        c.commit('Lexifina', {f'judgments/{LAW}/tyosopimuslaki/luku-07-pykala-003.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': index,
                              'corpus.json': json.dumps({'corpus': 'fi/korkein-oikeus/caselaw', 'kind': 'judgments', 'credit': CREDIT,
                                                         'licence': 'CC BY 4.0', 'name': 'Case law: Korkein oikeus',
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
        self.assertIn('Valitus hyväksytään', self.cli('show', '2012-01-01', path))
        self.assertIn('Valitus hylätään', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Korkein oikeus KKO:2010:5', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('hyväksytään', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '1990-01-01', '2030-01-01')
        self.assertIn('1032/2018', laws)
        self.assertNotIn('KKO:2023:8', laws)
        decisions = self.cli('laws', '1990-01-01', '2030-01-01', 'finland/caselaw')
        self.assertIn('Korkein oikeus KKO:2023:8 (court decision)', decisions)
        self.assertNotIn('1032/2018', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('Korkein oikeus KKO:2023:8 (latest decision), given 2023-02-02', self.cli('world', '2024-01-01'))

    def test_countries_adds_finnish_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        finnish = add('finland')
        self.assertIn(LAW, finnish)
        self.assertNotIn(CASES, finnish)
        self.assertIn(CASES, add('finland/caselaw'))

    def test_check_precedent_and_what_else_changes(self):
        prec, else_ = self.calls(('check_precedent', {'path': ART, 'date': '2024-01-01'}),
                                 ('what_else_changes', {'path': ART, 'date': '2024-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 3)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['ECLI:FI:KKO:2010:5']['same_words'])
        self.assertEqual(by['ECLI:FI:KKO:2023:8']['text_date'], '2018-06-01')
        self.assertIn('applying the text of 2018-06-01', prec['text'])
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist, lj = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2024-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/ennakkopaatokset'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}),
            ('list_jurisdictions', {}))
        for a in (read, cmp, who, listed, cases, hist, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('vähentynyt olennaisesti', read['text'])
        self.assertIn('Finlex', read['text'])  # the CC BY 4.0 credit
        self.assertIn('hyväksytään', cmp['text'])
        self.assertIn('Korkein oikeus KKO:2010:5', who['text'])
        self.assertIn('KKO:2016:40', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('2011-01-01', hist['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('Finlex', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        answers = self.calls(('search_law', {'query': 'vähentynyt', 'date': '2024-01-01'}),
                             ('search_law', {'query': 'vähentynyt', 'date': '2024-01-01', 'kind': 'judgments'}),
                             ('laws_between', {'start': '1990-01-01', 'end': '2030-01-01'}),
                             ('changes_between', {'date_a': '2009-01-01', 'date_b': '2024-01-01'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, laws, between = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(f'{CASES}/', law_only['text'].split('Not read')[0])
        self.assertIn(f'{CASES}/{D2}', judgments['text'])
        self.assertNotIn('KKO:2023:8', laws['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_decisions_by_identifier_and_finnish_citations(self):
        found, found_sv, details, cites = self.calls(
            ('find_provision', {'query': 'KKO:2023:8'}),
            ('find_provision', {'query': 'HD:2016:40'}),
            ('law_details', {'law': 'KKO:2016:40'}),
            ('resolve_citations', {'text': 'TSL 7 luku 3 § ja PL 21 § (KKO:2010:5); työsopimuslain 7 luvun 3 §; RL 21 luku 1 §.',
                                   'date': '2024-01-01'}))
        for a in (found, found_sv, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D2}', found_sv['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(ART, text)
        self.assertIn(PL21, text)
        self.assertIn(f'{CASES}/{D1}', text)

    def test_finnish_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        hit = m.FI_ABBR.search('TSL 7 luku 3 §')
        self.assertEqual((hit.group('abbr'), hit.group('a'), hit.group('b')), ('TSL', '7', '3'))
        hit = m.FI_ABBR.search('PL 21 §')
        self.assertEqual((hit.group('abbr'), hit.group('a'), hit.group('b')), ('PL', '21', None))
        hit = m.FI_GENITIVE.search('työsopimuslain 7 luvun 3 §:n')
        self.assertEqual((hit.group('stem').lower(), hit.group('end'), hit.group('a'), hit.group('b')), ('työsopimus', 'lain', '7', '3'))
        self.assertEqual(m.fi_genitive_folder('työsopimus', 'lain'), 'tyosopimuslaki')
        self.assertIsNone(m.fi_aliases().get('aliases', {}).get('RL'))  # finland-law leaves the Criminal Code out
        for other in ('§ 823 Abs. 1 BGB', 'Art. 336 OR', 'artikel 6:162 BW', 'art. 415 k.c.'):
            self.assertIsNone(m.FI_ABBR.search(other), other)
            self.assertIsNone(m.FI_GENITIVE.search(other), other)


if __name__ == '__main__':
    unittest.main()
