"""Dutch case law in the tree: a corpus of decisions of the Hoge Raad (lexifina/netherlands-hoge-raad-caselaw and the
other Dutch courts' -caselaw repos), read with the same tools as law, on a small tree built here: Dutch law (Burgerlijk
Wetboek Boek 6, art. 6:162 in two versions) and a case-law corpus (three decisions, a correction, and the judgment
overlay, one row with the version date the court applied: text_date, from the jci g= parameter).

  python -m unittest tests.test_caselaw_nl -v

One test per feature of the feature list (as tests/test_caselaw.py does for Switzerland), plus the Dutch forms:
decisions by ECLI, articles by abbreviation ("artikel 6:162 BW", "art. 8:69 Awb"), the ECHR left alone.
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

LAW = 'netherlands/national/acts'
CASES = 'netherlands/hoge-raad/caselaw'
ART = f'{LAW}/bw-boek-6/art-162.md'
D1 = 'decisions/hr/2010/ECLI_NL_HR_2010_BK1234.md'
D2 = 'decisions/hr/2016/ECLI_NL_HR_2016_100.md'
D3 = 'decisions/hr/2022/ECLI_NL_HR_2022_200.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return f'---\ncourt: "Hoge Raad"\n---\n\n# {title}\n\n## Text\n\n{text}\n'


class DutchCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'nl-aliases.json'):
            shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Dutch law', 'language': 'nl', 'in_force_trailer': 'In-force', 'code': 'NL'},
            {'path': CASES, 'name': 'Case law: Hoge Raad', 'language': 'nl', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'NL'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Stb. 1992, 422', {'bw-boek-6/art-162.md': '1 Hij die jegens een ander een onrechtmatige daad pleegt, '
                                                             'is verplicht de schade te vergoeden.\n',
                                      'awb/art-08-069.md': '1 De bestuursrechter doet uitspraak op de grondslag van het beroepschrift.\n',
                                      'bw-boek-6/README.md': '# Burgerlijk Wetboek Boek 6\n\n| Provision | File |\n| --- | --- |\n'
                                                             '| Art. 162 | [art-162.md](art-162.md) |\n',
                                      'awb/README.md': '# Algemene wet bestuursrecht\n\n# Not the title\n'},
                   In_force='1992-01-01', Kind='law')
        cls.v2020 = law.commit('Stb. 2020, 5', {'bw-boek-6/art-162.md': '1 Hij die jegens een ander een onrechtmatige daad '
                                                                        'pleegt, welke hem kan worden toegerekend, is verplicht '
                                                                        'de schade te vergoeden.\n'},
                               In_force='2020-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Hoge Raad 09/01234', {D1: decision('Onrechtmatige daad', 'De vordering wordt afgewezen.\nHet beroep is ongegrond.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Hoge Raad', Docket='09/01234',
                 ECLI='ECLI:NL:HR:2010:BK1234', Cites=f'{ART} (artikel 6:162 BW)')
        c.commit('Hoge Raad 09/01234', {D1: decision('Onrechtmatige daad', 'De vordering wordt afgewezen.\nHet beroep wordt verworpen.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='09/01234')
        c.commit('Hoge Raad 15/00100', {D2: decision('Toerekening', 'De schade wordt toegerekend aan de dader.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Hoge Raad', Docket='15/00100',
                 ECLI='ECLI:NL:HR:2016:100', Cites=f'{ART} (artikel 6:162 BW)')
        c.commit('Hoge Raad 21/00200', {D3: decision('Aansprakelijkheid', 'De werkgever is aansprakelijk.')},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court='Hoge Raad', Docket='21/00200',
                 ECLI='ECLI:NL:HR:2022:200', Cites=f'{ART} (artikel 6:162 BW)')
        url = 'https://uitspraken.rechtspraak.nl/details?id='
        rows = [{'decided': '2010-05-05', 'name': 'Hoge Raad 09/01234', 'court': 'Hoge Raad', 'citation': 'ECLI:NL:HR:2010:BK1234',
                 'url': url + 'ECLI:NL:HR:2010:BK1234', 'how': 'Burgerlijk Wetboek Boek 6 162', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Hoge Raad 15/00100', 'court': 'Hoge Raad', 'citation': 'ECLI:NL:HR:2016:100',
                 'url': url + 'ECLI:NL:HR:2016:100', 'how': 'Burgerlijk Wetboek Boek 6 162', 'mentions': 2, 'decision': D2},
                # Decided after the 2020 change, but applying the text of 2015 (the court's jci g= date): text_date.
                {'decided': '2022-03-03', 'text_date': '2015-07-01', 'name': 'Hoge Raad 21/00200', 'court': 'Hoge Raad',
                 'citation': 'ECLI:NL:HR:2022:200', 'url': url + 'ECLI:NL:HR:2022:200', 'how': 'Burgerlijk Wetboek Boek 6 162',
                 'mentions': 1, 'decision': D3, 'law_commit': cls.v2020}]
        c.commit('Lexifina', {f'judgments/{LAW}/bw-boek-6/art-162.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': f'reference\tpath\n09/01234\t{D1}\n15/00100\t{D2}\n21/00200\t{D3}\nBK1234\t{D1}\n',
                              'corpus.json': json.dumps({'corpus': 'nl/hoge-raad/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: Hoge Raad', 'in_force_trailer': 'In-force'})},
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
        self.assertIn('wordt verworpen', self.cli('show', '2012-01-01', path))
        self.assertIn('is ongegrond', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Hoge Raad 09/01234', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('verworpen', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '1990-01-01', '2030-01-01')
        self.assertIn('Stb. 2020, 5', laws)
        self.assertNotIn('21/00200', laws)
        dutch = self.cli('laws', '1990-01-01', '2030-01-01', 'netherlands')
        self.assertIn('Stb. 2020, 5', dutch)
        self.assertNotIn('(court decision)', dutch)
        decisions = self.cli('laws', '1990-01-01', '2030-01-01', 'netherlands/caselaw')
        self.assertIn('Hoge Raad 21/00200 (court decision)', decisions)
        self.assertNotIn('Stb. 2020, 5', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('Hoge Raad 21/00200 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_dutch_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        dutch = add('netherlands')
        self.assertIn(LAW, dutch)
        self.assertNotIn(CASES, dutch)
        self.assertIn(CASES, add('netherlands/caselaw'))
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
        self.assertFalse(by['ECLI:NL:HR:2010:BK1234']['same_words'])  # decided before Stb. 2020, 5
        # Decided in 2022, after the change, but the court applied the 2015 text (text_date): not today's words.
        self.assertEqual(by['ECLI:NL:HR:2022:200']['text_date'], '2015-07-01')
        self.assertFalse(by['ECLI:NL:HR:2022:200']['same_words'])
        self.assertIn('applying the text of 2015-07-01', prec['text'])
        self.assertEqual(by['ECLI:NL:HR:2016:100']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/hr'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}))
        for a in (read, cmp, who, listed, cases, hist):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('toegerekend aan de dader', read['text'])
        self.assertIn('verworpen', cmp['text'])
        self.assertIn('Hoge Raad 09/01234', who['text'])
        self.assertIn('Onrechtmatige daad', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])

    def test_list_jurisdictions_names_dutch_case_law(self):
        (lj,) = self.calls(('list_jurisdictions', {}))
        self.assertFalse(lj['error'], lj['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('2022-03-03', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'schade'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': 'netherlands/caselaw'}),
                             ('laws_between', {'start': '1990-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'Hoge Raad'}),
                             ('search_changes', {'query': 'Hoge Raad', 'jurisdiction': 'netherlands/caselaw'}),
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
        self.assertIn('Stb. 2020, 5', laws['text'])
        self.assertNotIn('21/00200', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_phrase_history_in_case_law(self):
        """phrase_history in case law: the decisions that hold the words, each dated the day decided, and what a
        correction added or removed (read from the files at the pin and the corrections alone, not a pickaxe search of
        every decision, which passed 120 s on the Hoge Raad)."""
        toe, gegrond, verworpen = self.calls(
            ('phrase_history', {'query': 'toegerekend', 'jurisdiction': 'netherlands/caselaw'}),
            ('phrase_history', {'query': 'is ongegrond', 'jurisdiction': CASES}),
            ('phrase_history', {'query': 'wordt verworpen', 'jurisdiction': 'netherlands/caselaw'}))
        for a in (toe, gegrond, verworpen):
            self.assertFalse(a['error'], a['text'])
        rows = lambda a: [(c['in_force'], c['effect'], c['path']) for c in a['data']['changes']]  # noqa: E731
        self.assertEqual(rows(toe), [('2016-06-01', 'added', f'{CASES}/{D2}')])
        self.assertEqual(rows(gegrond), [('2010-05-05', 'added', f'{CASES}/{D1}'), ('2011-01-01', 'removed', f'{CASES}/{D1}')])
        self.assertEqual(rows(verworpen), [('2011-01-01', 'added', f'{CASES}/{D1}')])

    def test_decisions_by_zaaknummer_and_ljn(self):
        """A Dutch decision by its zaaknummer or LJN (decision-index.tsv): find_provision and law_details find it at once;
        a zaaknummer not in the record is answered at once too, not by a heading search of every decision (over 8
        minutes with the Dutch courts served)."""
        docket, ljn, details, none = self.calls(
            ('find_provision', {'query': '09/01234'}), ('find_provision', {'query': 'LJN BK1234'}),
            ('law_details', {'law': '15/00100'}), ('find_provision', {'query': '99/09999'}))
        for a in (docket, ljn, details, none):
            self.assertFalse(a['error'], a['text'])
        self.assertTrue(docket['text'].startswith(f'{CASES}/{D1}'), docket['text'])
        self.assertTrue(ljn['text'].startswith(f'{CASES}/{D1}'), ljn['text'])
        self.assertIn('Hoge Raad 15/00100', details['text'])
        self.assertIn('No decision', none['text'])
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for ref in ('19/00135', '24/1067 PW', '201901234/1/A2', '200.123.456/01', '21-000854-26', 'C/13/785683',
                    'C/13/785683 / HA ZA 26-301', 'CUR2024H00259', 'LJN BK1234'):
            self.assertTrue(m.NL_DOCKET.fullmatch(ref), ref)
        for other in ('S.I. 2020/471', 'art. 6:162 BW', 'Stcrt. 2019, 70272', '1 BvR 123/20', 'II CSK 123/20'):
            self.assertIsNone(m.NL_DOCKET.fullmatch(other), other)

    def test_decisions_by_ecli_and_dutch_citations(self):
        found, details, cites = self.calls(
            ('find_provision', {'query': 'ECLI:NL:HR:2022:200'}),
            ('law_details', {'law': 'ECLI:NL:HR:2016:100'}),
            ('resolve_citations', {'text': 'Op grond van artikel 6:162 BW (ECLI:NL:HR:2010:BK1234) en art. 8:69 Awb, '
                                           'maar niet artikel 6 EVRM.', 'date': '2023-01-01'}))
        for a in (found, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(ART, text)
        self.assertIn(f'{LAW}/awb/art-08-069.md', text)
        self.assertIn(f'{CASES}/{D1}', text)
        self.assertNotIn('EVRM', json.dumps([h.get('path') for h in cites['data'].get('citations', [])]))

    def test_bare_citation_and_readme_titles_are_fast(self):
        """Speed gate on the real Dutch case law (2026-11-06): find_provision "6:162 BW" (no "artikel") fell through to
        the act-title search, which read all 35,466 act READMEs of the Dutch law in full: over 120 s in every process.
        Now the bare form is a citation, and act titles come from one git grep of each README's first heading, kept on
        disk per corpus commit."""
        (found,) = self.calls(('find_provision', {'query': '6:162 BW'}))
        self.assertFalse(found['error'], found['text'])
        self.assertTrue(found['text'].startswith(ART), found['text'])
        code = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server as m, law\n'
                f'c = "{LAW}"; sha = m.corpus_head(c)\n'
                'print(json.dumps([m.readme_titles(c, sha), sorted(p.name for p in law._store().glob("titles-*.json"))]))\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        titles, cached = json.loads(done.stdout)
        self.assertEqual(titles, {'bw-boek-6': 'Burgerlijk Wetboek Boek 6', 'awb': 'Algemene wet bestuursrecht'})
        self.assertTrue(cached, 'the titles are kept on disk')

    def test_dutch_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for text, abbr, num in (('artikel 6:162 BW', 'BW', '6:162'), ('art. 8:69 Awb', 'Awb', '8:69'),
                                ('artikel 310 Sr', 'Sr', '310'), ('art. 359a Sv', 'Sv', '359a'),
                                ('artikel 3:40 lid 2 BW', 'BW', '3:40'), ('art. 7:658 BW', 'BW', '7:658')):
            hit = m.NL_ARTICLE.search(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual((hit.group('abbr'), hit.group('num')), (abbr, num), text)
        for other in ('artikel 6 EVRM', 'art. 14 CE', 'Art. 336 OR', 'Art. 16a Abs. 1 GG', 'art. 1902 CC'):
            self.assertIsNone(m.NL_ARTICLE.search(other), other)
        # The bare form with a book or chapter is Dutch too; a bare number without one is not read.
        for text, abbr, num in (('6:162 BW', 'BW', '6:162'), ('zie 8:69 Awb', 'Awb', '8:69'), ('3:40 lid 2 BW', 'BW', '3:40')):
            hit = m.NL_ARTICLE.search(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual((hit.group('abbr'), hit.group('num')), (abbr, num), text)
        for other in ('162 BW', 'ECLI:NL:HR:2019:162 BW', '2019/6:162 BW', 'om 12:30 uur'):
            self.assertIsNone(m.NL_ARTICLE.search(other), other)
        t = m.nl_aliases()
        self.assertEqual(t['bw_books']['6'], 'bw-boek-6')
        for abbr, folder in (('AWB', 'awb'), ('SR', 'wetboek-van-strafrecht'), ('SV', 'wetboek-van-strafvordering'),
                             ('RV', 'wetboek-van-burgerlijke-rechtsvordering')):
            self.assertEqual(t['acts'][abbr], folder, abbr)
        self.assertNotIn('EVRM', t['acts'])
        self.assertEqual(m.nl_article_key('08-069a'), '8:69a')
        for ref in ('ECLI:NL:HR:2019:1234', 'ECLI:DE:BGH:2020:123456UVIZR1.19.0', 'ECLI:FR:CCASS:2021:C100123'):
            self.assertTrue(m.ECLI.fullmatch(ref), ref)
            self.assertTrue(m.DECISION_REF.search(ref), ref)


class NightlyAppends(unittest.TestCase):
    """Decisions a nightly run appends: dated the day decided (author date) but committed the day the run made them
    (committer date), after the corpus was built with both dates the day decided. `git log --before` reads the committer
    date, so world and world_on_date named the last decision of the build (2026-04-24 on every Dutch court) for any day
    before the run, and missed old decisions published late."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        manifest = {'corpora': [{'path': CASES, 'name': 'Case law: Hoge Raad', 'language': 'nl', 'kind': 'judgments',
                                 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'NL'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        c = t.corpus(CASES)

        def commit(name, path, decided, committed, author='Hoge Raad'):
            f = c.path / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(decision(name, 'Tekst.'), encoding='utf-8')
            run('add', path, cwd=c.path)
            env = {'GIT_AUTHOR_NAME': f'{author} {name}', 'GIT_AUTHOR_EMAIL': 'x@caselaw.invalid',
                   'GIT_AUTHOR_DATE': f'{decided}T12:00:00+01:00', 'GIT_COMMITTER_NAME': 'Lexifina',
                   'GIT_COMMITTER_EMAIL': 'corpus@lexifina.com', 'GIT_COMMITTER_DATE': f'{committed}T12:00:00+01:00'}
            run('commit', '-q', '-m', f'{author} {name}\n\nKind: court\nIn-force: {decided}\nDecided: {decided}\nECLI: {name}\n',
                cwd=c.path, env=env)

        # The build: committed the day decided.
        commit('ECLI:NL:HR:1995:1', 'decisions/hr/1995/ECLI_NL_HR_1995_1.md', '1995-06-01', '1995-06-01')
        commit('ECLI:NL:HR:2026:1', 'decisions/hr/2026/ECLI_NL_HR_2026_1.md', '2026-04-24', '2026-04-24')
        # The nightly run of 2026-11-06: decisions of May and October, and one of 1995 published late.
        commit('ECLI:NL:HR:2026:2', 'decisions/hr/2026/ECLI_NL_HR_2026_2.md', '2026-05-15', '2026-11-06')
        commit('ECLI:NL:HR:1995:2', 'decisions/hr/1995/ECLI_NL_HR_1995_2.md', '1995-12-20', '2026-11-06')
        commit('ECLI:NL:HR:2026:3', 'decisions/hr/2026/ECLI_NL_HR_2026_3.md', '2026-10-30', '2026-11-06')
        t.pin()
        cls.law = t.law()

    @classmethod
    def tearDownClass(cls):
        cls.law.close_readers()
        cls.t.close()

    def test_world_reads_decisions_committed_after_the_day(self):
        latest = lambda day: (self.law.latest_decision(CASES, day) or ('', ''))[:2]  # noqa: E731
        self.assertEqual(latest('2026-11-01'), ('Hoge Raad ECLI:NL:HR:2026:3', '2026-10-30'))
        self.assertEqual(latest('2026-06-01'), ('Hoge Raad ECLI:NL:HR:2026:2', '2026-05-15'))
        self.assertEqual(latest('2026-05-01'), ('Hoge Raad ECLI:NL:HR:2026:1', '2026-04-24'))
        self.assertEqual(latest('1996-01-01'), ('Hoge Raad ECLI:NL:HR:1995:2', '1995-12-20'))
        self.assertEqual(latest('1995-07-01'), ('Hoge Raad ECLI:NL:HR:1995:1', '1995-06-01'))
        self.assertEqual(latest('9999-12-31'), ('Hoge Raad ECLI:NL:HR:2026:3', '2026-10-30'))
        self.assertIsNone(self.law.latest_decision(CASES, '1990-01-01'))
        out, err, code = self.t.cli('world', '2026-11-01')
        self.assertEqual(code, 0, err)
        self.assertIn('ECLI:NL:HR:2026:3 (latest decision), given 2026-10-30', out)


if __name__ == '__main__':
    unittest.main()
