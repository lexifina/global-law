"""French case law in the tree: a corpus of decisions of the Cour de cassation (lexifina/france-cour-de-cassation-caselaw
and the other French courts' -caselaw repos, from DILA's open data under the Licence Ouverte 2.0), read with the same
tools as law, on a small tree built here: French law (Code civil, art. 1240 in two versions) and a case-law corpus
(three decisions, a correction, the judgment overlay with one row's text_date, and decision-index.tsv, as the files are
named by DILA id).

  python -m unittest tests.test_caselaw_fr -v

One test per feature of the feature list (as tests/test_caselaw_nl.py does for the Netherlands), plus the French forms:
decisions by pourvoi, DILA id and ECLI; articles by code name ("article 1240 du code civil"), abbreviation ("art.
L. 1235-3 C. trav.") and of the Constitution; the ECHR and other states' constitutions left alone; and the credit the
licence requires, shown wherever the corpus is read.
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

LAW = 'france/national/acts'
CASES = 'france/cour-de-cassation/caselaw'
ART = f'{LAW}/codes/code-civil/1240.md'
D1 = 'decisions/ccass/2010/JURITEXT000022222221.md'
D2 = 'decisions/ccass/2016/JURITEXT000033333332.md'
D3 = 'decisions/ccass/2022/JURITEXT000044444443.md'
CREDIT = ("Direction de l'information légale et administrative (DILA), Cour de cassation (CASS, INCA), "
          "updated 2026-11-05, Licence Ouverte / Open Licence 2.0 (Etalab)")
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return (f'---\njuridiction: "Cour de cassation"\nsource: "DILA, base CASS"\n'
            f'licence: "Licence Ouverte / Open Licence 2.0"\n---\n\n# {title}\n\n## Texte\n\n{text}\n')


class FrenchCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'nl-aliases.json', 'fr-aliases.json'):
            shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        source = {'publisher': "Direction de l'information légale et administrative (DILA)",
                  'dataset': 'Cour de cassation (CASS, INCA)', 'updated': '2026-11-05',
                  'url': 'https://echanges.dila.gouv.fr/OPENDATA/CASS/'}
        manifest = {'corpora': [
            {'path': LAW, 'name': 'French law', 'language': 'fr', 'in_force_trailer': 'In-force', 'code': 'FR'},
            {'path': CASES, 'name': 'Case law: Cour de cassation', 'language': 'fr', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'FR',
             'source': source, 'licence': 'Licence Ouverte / Open Licence 2.0 (Etalab)'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Code civil (1804)', {'codes/code-civil/1240.md': "# Article 1240\n\nTout fait quelconque de l'homme, "
                                                                      "qui cause à autrui un dommage, oblige à le réparer.\n",
                                         'constitution/constitution-1958/66.md': '# Article 66\n\nNul ne peut être arbitrairement détenu.\n'},
                   In_force='1990-01-01', Kind='law')
        cls.v2016 = law.commit('Ordonnance n° 2016-131 du 10 février 2016',
                               {'codes/code-civil/1240.md': "# Article 1240\n\nTout fait quelconque de l'homme, qui cause à "
                                                            "autrui un dommage, oblige celui par la faute duquel il est arrivé "
                                                            "à le réparer.\n"},
                               In_force='2016-10-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Cour de cassation 09-12.345', {D1: decision('Responsabilité délictuelle', 'Le pourvoi est rejeté.\nLa faute est établie.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Cour de cassation', Docket='09-12.345',
                 ECLI='ECLI:FR:CCASS:2010:C100123', Cites=f'{ART} (Code civil - art. 1382)')
        c.commit('Cour de cassation 09-12.345', {D1: decision('Responsabilité délictuelle', 'Le pourvoi est rejeté.\nLa faute est caractérisée.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='09-12.345')
        c.commit('Cour de cassation 15-10.100', {D2: decision('Faute et dommage', "Le dommage est réparé par l'auteur.")},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Cour de cassation', Docket='15-10.100',
                 ECLI='ECLI:FR:CCASS:2016:C200100', Cites=f'{ART} (Code civil - art. 1382)')
        c.commit('Cour de cassation 21-20.200', {D3: decision('Responsabilité du fait personnel', "L'arrêt est cassé.")},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court='Cour de cassation', Docket='21-20.200',
                 ECLI='ECLI:FR:CCASS:2022:C300200', Cites=f'{ART} (Code civil - art. 1240)')
        url = 'https://www.legifrance.gouv.fr/juri/id/'
        rows = [{'decided': '2010-05-05', 'name': 'Cour de cassation 09-12.345', 'court': 'Cour de cassation',
                 'citation': '09-12.345', 'url': url + 'JURITEXT000022222221', 'how': 'Code civil - art. 1382', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Cour de cassation 15-10.100', 'court': 'Cour de cassation',
                 'citation': '15-10.100', 'url': url + 'JURITEXT000033333332', 'how': 'Code civil - art. 1382', 'mentions': 2, 'decision': D2},
                # Decided after the 2016 reform, on facts of 2015: the court applied the earlier text (text_date).
                {'decided': '2022-03-03', 'text_date': '2015-07-01', 'name': 'Cour de cassation 21-20.200', 'court': 'Cour de cassation',
                 'citation': '21-20.200', 'url': url + 'JURITEXT000044444443', 'how': 'Code civil - art. 1240', 'mentions': 1,
                 'decision': D3, 'law_commit': cls.v2016}]
        index = ''.join(f'{ref}\t{p}\n' for ref, p in (('09-12.345', D1), ('ECLI:FR:CCASS:2010:C100123', D1), ('15-10.100', D2),
                                                         ('ECLI:FR:CCASS:2016:C200100', D2), ('21-20.200', D3),
                                                         ('ECLI:FR:CCASS:2022:C300200', D3)))
        c.commit('Lexifina', {f'judgments/{LAW}/codes/code-civil/1240.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': '# reference\tpath\n' + index,
                              'corpus.json': json.dumps({'corpus': 'fr/cour-de-cassation/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: Cour de cassation', 'in_force_trailer': 'In-force',
                                                         'source': source, 'licence': 'Licence Ouverte / Open Licence 2.0 (Etalab)'})},
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

    # --- law.py on a decision -------------------------------------------------------------------------------------

    def test_law_py_reads_a_decision(self):
        path = f'{CASES}/{D1}'
        shown = self.cli('show', '2012-01-01', path)
        self.assertIn('est caractérisée', shown)
        self.assertIn('Licence Ouverte', shown)  # the decision's own credit lines are part of what is shown
        self.assertIn('est établie', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Cour de cassation 09-12.345', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('caractérisée', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '1980-01-01', '2030-01-01')
        self.assertIn('Ordonnance n° 2016-131', laws)
        self.assertNotIn('21-20.200', laws)
        self.assertNotIn('(court decision)', self.cli('laws', '1980-01-01', '2030-01-01', 'france'))
        decisions = self.cli('laws', '1980-01-01', '2030-01-01', 'france/caselaw')
        self.assertIn('Cour de cassation 21-20.200 (court decision)', decisions)
        self.assertNotIn('Ordonnance n° 2016-131', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('Cour de cassation 21-20.200 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_french_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        french = add('france')
        self.assertIn(LAW, french)
        self.assertNotIn(CASES, french)
        self.assertIn(CASES, add('france/caselaw'))
        self.assertIn(CASES, add(CASES))
        listing = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py'], cwd=self.t.root,
                                 capture_output=True, encoding='utf-8', timeout=120).stdout
        self.assertTrue(any(CASES in l and 'court decisions' in l for l in listing.splitlines()), listing)

    # --- the server ---------------------------------------------------------------------------------------------

    def test_check_precedent_uses_the_version_date_the_court_applied(self):
        prec, else_ = self.calls(('check_precedent', {'path': ART, 'date': '2023-01-01'}),
                                 ('what_else_changes', {'path': ART, 'date': '2023-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 3)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['09-12.345']['same_words'])  # decided before the 2016 reform
        self.assertEqual(by['21-20.200']['text_date'], '2015-07-01')
        self.assertFalse(by['21-20.200']['same_words'])
        self.assertIn('applying the text of 2015-07-01', prec['text'])
        self.assertEqual(by['15-10.100']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/ccass'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}))
        for a in (read, cmp, who, listed, cases, hist):
            self.assertFalse(a['error'], a['text'])
        self.assertIn("réparé par l'auteur", read['text'])
        self.assertIn('caractérisée', cmp['text'])
        self.assertIn('Cour de cassation 09-12.345', who['text'])
        self.assertIn('Responsabilité délictuelle', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])

    def test_the_licence_credit_is_shown(self):
        """Licence Ouverte 2.0 requires naming the source and the date of its last update: read_law and
        list_jurisdictions give the corpus's credit, from its corpus.json."""
        read, lj = self.calls(('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}), ('list_jurisdictions', {}))
        for a in (read, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'Credit: {CREDIT}', read['text'])
        self.assertEqual(read['data']['credit'], CREDIT)
        self.assertIn(f'Credit: {CREDIT}.', lj['text'])
        self.assertIn('2022-03-03', lj['text'])
        row = next(r for r in lj['data']['corpora'] if r.get('path', r.get('corpus')) == CASES)
        self.assertEqual(row['credit'], CREDIT)
        law_read = self.calls(('read_law', {'path': ART, 'date': '2023-01-01'}))[0]
        self.assertNotIn('Credit:', law_read['text'])  # a corpus that states no duty gets no credit line

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'dommage'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': 'france/caselaw'}),
                             ('laws_between', {'start': '1980-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'Cour de cassation'}),
                             ('search_changes', {'query': 'Cour de cassation', 'jurisdiction': 'france/caselaw'}),
                             ('phrase_history', {'query': q}),
                             ('changes_between', {'date_a': '2009-01-01', 'date_b': '2023-01-01'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, named, laws, changes, changes_cl, phrase, between = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(CASES, law_only['text'].split('Not read')[0])
        self.assertIn(f'{CASES}/{D2}', judgments['text'])
        self.assertNotIn(ART, judgments['text'])
        self.assertIn(f'{CASES}/{D2}', named['text'])
        self.assertIn('Ordonnance n° 2016-131', laws['text'])
        self.assertNotIn('21-20.200', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_decisions_by_pourvoi_dila_id_and_ecli_and_french_citations(self):
        by_pourvoi, by_id, by_ecli, details, cites = self.calls(
            ('find_provision', {'query': 'pourvoi n° 21-20.200'}),
            ('find_provision', {'query': 'JURITEXT000033333332'}),
            ('find_provision', {'query': 'ECLI:FR:CCASS:2010:C100123'}),
            ('law_details', {'law': 'n° 15-10.100'}),
            ('resolve_citations', {'text': "Vu l'article 1240 du code civil, l'article 66 de la Constitution et "
                                           "l'arrêt n° 09-12.345, mais non l'article 6 de la Convention européenne "
                                           'ni l\'article 5 de la Constitution fédérale.', 'date': '2023-01-01'}))
        for a in (by_pourvoi, by_id, by_ecli, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', by_pourvoi['text'])
        self.assertIn(f'{CASES}/{D2}', by_id['text'])
        self.assertIn(f'{CASES}/{D1}', by_ecli['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        paths = [h.get('path') for h in cites['data'].get('citations', [])]
        self.assertIn(ART, paths)
        self.assertIn(f'{LAW}/constitution/constitution-1958/66.md', paths)
        self.assertIn(f'{CASES}/{D1}', paths)
        self.assertFalse([p for p in paths if p and p.endswith('/5.md')], paths)  # not the Swiss Constitution

    def test_french_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for text, want in (('article 1240 du code civil', ['codes/code-civil/1240.md']),
                           ('art. L. 1234-5 du code du travail', ['codes/code-du-travail/L1234-5.md']),
                           ("article R. 421-1 du code de l'urbanisme", ['codes/code-de-l-urbanisme/R421-1.md']),
                           ('articles 1240 et 1241 du code civil', ['codes/code-civil/1240.md', 'codes/code-civil/1241.md']),
                           ('article 39 du code général des impôts', ['codes/code-general-des-impots-cgi/39.md']),
                           ('article L. 4 du code du travail maritime', ['codes/code-du-travail-maritime/L4.md']),
                           ('art. L. 1235-3 C. trav.', ['codes/code-du-travail/L1235-3.md']),
                           ('art. L. 411-1 CJA', ['codes/code-de-justice-administrative/L411-1.md']),
                           ('article 66 de la Constitution', ['constitution/constitution-1958/66.md']),
                           # two citations in one sentence: the code's name stops where the next citation starts
                           ("Vu l'article 1240 du code civil et l'article L. 1234-5 du code du travail.",
                            ['codes/code-civil/1240.md', 'codes/code-du-travail/L1234-5.md']),
                           ('article 9 du code civil, article 700 du code de procédure civile',
                            ['codes/code-civil/9.md', 'codes/code-de-procedure-civile/700.md'])):
            got = [h['path'] for h in m.citations_in(text) if h['country'] == 'fr']
            self.assertEqual(got, [f'{LAW}/{w}' for w in want], text)
        for other in ('article 6 de la Convention européenne', 'article 5 de la Constitution fédérale', 'art. 106 CPC',
                      'art. 1357 C. civ.', 'artículo 1902 del Código Civil', 'art. 29 al. 2 Cst.'):
            self.assertFalse([h for h in m.citations_in(other) if h['country'] == 'fr'], other)
        self.assertEqual(m.fr_article_file('L. 1234-5'), 'L1234-5')
        self.assertEqual(m.fr_article_file('15 bis'), '15-bis')
        for ref in ('pourvoi n° 18-12.345', 'n° 2019-791 QPC', "CE, 10 juin 2020, n° 412345", 'JURITEXT000041234567'):
            self.assertTrue(m.FR_DECISION.search(ref), ref)
        self.assertIsNone(m.FR_DECISION.search('n° 412345'))  # a bare number without its court is not read

    def test_laws_between_lists_decisions_when_the_jurisdiction_names_case_law(self):
        """laws_between with a case-law jurisdiction ("france/caselaw", a court's corpus) lists the decisions given in the
        window, as law.py laws does and the tool's description says; it answered "No law took effect ... not listed: 22
        court rulings" (case-law audit 2026-11-07)."""
        named, court, law_only = self.calls(
            ('laws_between', {'start': '2016-01-01', 'end': '2022-12-31', 'jurisdiction': 'france/caselaw'}),
            ('laws_between', {'start': '2016-01-01', 'end': '2022-12-31', 'jurisdiction': CASES}),
            ('laws_between', {'start': '2016-01-01', 'end': '2022-12-31', 'jurisdiction': 'france'}))
        for a in (named, court, law_only):
            self.assertFalse(a['error'], a['text'])
        for a in (named, court):
            self.assertIn('Cour de cassation 15-10.100', a['text'])
            self.assertIn('Cour de cassation 21-20.200', a['text'])
            self.assertNotIn('Ordonnance n° 2016-131', a['text'])
        self.assertIn('Ordonnance n° 2016-131', law_only['text'])
        self.assertNotIn('21-20.200', law_only['text'].split('Not read')[0])

    def test_phrase_history_in_case_law_reads_each_year_and_dates_by_first_version(self):
        """phrase_history in case law greps the corpus by year folder, side by side, and dates each decision by its first
        version from the index (the Cour de cassation: 69 s -> 19 s for "préjudice d'anxiété"; case-law audit
        2026-11-07). Every year is read, and a corrected decision keeps its first version's day."""
        dommage, faute = self.calls(('phrase_history', {'query': 'dommage', 'kind': 'judgments'}),
                                    ('phrase_history', {'query': 'La faute est', 'jurisdiction': 'france/caselaw'}))
        for a in (dommage, faute):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'2016-06-01  added    {CASES}/{D2}  by Cour de cassation 15-10.100', dommage['text'])
        self.assertIn(f'2010-05-05  added    {CASES}/{D1}  by Cour de cassation 09-12.345', faute['text'])
        self.assertNotIn(ART, dommage['text'])

    def test_conseil_constitutionnel_decision_by_number_and_kind(self):
        """decision-index.tsv files a Conseil constitutionnel decision by its bare number ("2026-1225") and its ECLI, not
        by "2026-1225 QPC", so "n° 2026-1225 QPC" found nothing (case-law audit 2026-11-07). The ECLI picks the kind
        where two decisions of different kinds share a number (2010-28 QPC and 2010-28 AN)."""
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        index = {'2026-1225': ['cc/2026/CONSTEXT1.md'], 'ECLI:FR:CC:2026:2026.1225.QPC': ['cc/2026/CONSTEXT1.md'],
                 '2010-28': ['cc/2010/QPC.md', 'cc/2010/AN.md'], 'ECLI:FR:CC:2010:2010.28.QPC': ['cc/2010/QPC.md'],
                 'ECLI:FR:CC:2011:2010.28.AN': ['cc/2010/AN.md'], 'ECLI:FR:CC:1979:78.101.DC': ['cc/1979/DC.md'],
                 '99-1': ['cc/1999/bare.md']}
        keyed = {m._decision_key(k): v for k, v in index.items()}
        real = m.decision_paths
        m.decision_paths = lambda text: list(keyed.get(m._decision_key(text), []))
        try:
            def paths(text):
                return m.fr_decision_paths(m.FR_DECISION.search(text))
            self.assertEqual(paths('décision n° 2026-1225 QPC du 16 octobre 2026'), ['cc/2026/CONSTEXT1.md'])
            self.assertEqual(paths('n° 2010-28 QPC'), ['cc/2010/QPC.md'])
            self.assertEqual(paths('n° 2010-28 AN'), ['cc/2010/AN.md'])  # decided the year after its number's
            self.assertEqual(paths('n° 78-101 DC'), ['cc/1979/DC.md'])
            self.assertEqual(paths('n° 99-1 DC'), ['cc/1999/bare.md'])  # no ECLI recorded: the bare number
        finally:
            m.decision_paths = real

    # --- speed (FR speed gate, 2026-11-06) -------------------------------------------------------------------------

    def test_decision_lookups_use_a_sorted_index_file_per_pin(self):
        """A decision reference is looked up in a sorted file written once per corpus pin in the tree's cache, so a fresh
        process does not rebuild the map (12 s a lookup on the Cour de cassation's 2 million references); a reference
        the record lacks is answered at once, not by a heading search (29-39 s without French case law served)."""
        first, = self.calls(('find_provision', {'query': 'pourvoi n° 21-20.200'}))
        cache = Path(subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-path', 'global-law-cache'],
                                    cwd=self.t.root, capture_output=True, encoding='utf-8').stdout.strip())
        files = sorted(cache.glob('decisions-*.tsv'))
        self.assertTrue(files, 'no decisions-<pin>.tsv in the cache')
        lines = files[0].read_text(encoding='utf-8').splitlines()
        self.assertEqual(lines, sorted(lines))
        self.assertFalse([l for l in lines if l.startswith(('REFERENCE\t', '\t'))], 'the header was read as a reference')
        again, by_ecli, missing = self.calls(('find_provision', {'query': 'pourvoi n° 21-20.200'}),
                                             ('find_provision', {'query': 'ECLI:FR:CCASS:2016:C200100'}),
                                             ('find_provision', {'query': 'pourvoi n° 99-99.999'}))
        self.assertIn(f'{CASES}/{D3}', first['text'])
        self.assertEqual(first['text'], again['text'])
        self.assertIn(f'{CASES}/{D2}', by_ecli['text'])
        self.assertIn('No decision', missing['text'])

    def test_read_law_on_a_decision_skips_the_modifies_scan(self):
        """read_law on a decision does not grep the corpus for Modifies: effects (none names a decision; 4.6 s on the
        Cour de cassation's 530,000 commits), and still shows the decision and its credit."""
        code = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server as m\n'
                'def boom(*a, **k): raise AssertionError("modifies_in read for a decision")\n'
                'm.modifies_in = boom\n'
                f'r = m.handle({{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {{"name": "read_law", '
                f'"arguments": {{"path": "{CASES}/{D2}", "date": "2023-01-01"}}}}}})["result"]\n'
                'print(json.dumps({"error": r["isError"], "text": r["content"][0]["text"]}))\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True,
                              encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        got = json.loads(done.stdout)
        self.assertFalse(got['error'], got['text'])
        self.assertIn('Licence Ouverte', got['text'])


if __name__ == '__main__':
    unittest.main()
