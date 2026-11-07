"""German case law in the tree: a corpus of decisions of the Bundesverfassungsgericht (lexifina/germany-bverfg-caselaw
and the other federal courts' -caselaw repos), read with the same tools as law, on a small tree built here: German
federal law (BGB § 823 in two versions, the Grundgesetz's Art. 3) and a case-law corpus (three decisions, a correction,
decision-index.tsv by Aktenzeichen and ECLI, and the judgment overlay, one row with the version date the court applied).

  python -m unittest tests.test_caselaw_de -v

One test per feature of the feature list (as tests/test_caselaw_nl.py does for the Netherlands), plus the German forms:
decisions by Aktenzeichen and ECLI, § citations of any federal act by its official abbreviation.
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

LAW = 'germany/bund/acts'
CASES = 'germany/bverfg/caselaw'
ART = f'{LAW}/bgb/0823.md'
D1 = 'decisions/bverfg/2010/ECLI_DE_BVerfG_2010_rk20100505.1bvr012309.md'
D2 = 'decisions/bverfg/2016/ECLI_DE_BVerfG_2016_rs20160601.1bvr010015.md'
D3 = 'decisions/bverfg/2022/ECLI_DE_BVerfG_2022_rs20220303.1bvr020021.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return f'---\ncourt: "Bundesverfassungsgericht"\n---\n\n# {title}\n\n## Entscheidung\n\n{text}\n'


class GermanCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'nl-aliases.json', 'fr-aliases.json', 'de-aliases.json'):
            shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'German federal law', 'language': 'de', 'in_force_trailer': 'In-force', 'code': 'DE'},
            {'path': CASES, 'name': 'Case law: Bundesverfassungsgericht', 'language': 'de', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'DE'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('BGBl. I 2002, 42', {'bgb/0823.md': '(1) Wer vorsätzlich oder fahrlässig das Leben eines anderen widerrechtlich '
                                                       'verletzt, ist zum Ersatz des Schadens verpflichtet.\n',
                                        'grundgesetz/artikel/003.md': '(1) Alle Menschen sind vor dem Gesetz gleich.\n'},
                   In_force='2002-01-01', Kind='law')
        cls.v2020 = law.commit('BGBl. I 2020, 5', {'bgb/0823.md': '(1) Wer vorsätzlich oder fahrlässig das Leben, den Körper oder '
                                                                  'die Gesundheit eines anderen widerrechtlich verletzt, ist '
                                                                  'zum Ersatz des Schadens verpflichtet.\n'},
                               In_force='2020-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Bundesverfassungsgericht 1 BvR 123/09', {D1: decision('Schadensersatz', 'Die Verfassungsbeschwerde wird zurückgewiesen.\nSie ist unbegründet.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Bundesverfassungsgericht', Docket='1 BvR 123/09',
                 ECLI='ECLI:DE:BVerfG:2010:rk20100505.1bvr012309', Cites=f'{ART} (§ 823 Abs. 1 BGB)')
        c.commit('Bundesverfassungsgericht 1 BvR 123/09', {D1: decision('Schadensersatz', 'Die Verfassungsbeschwerde wird zurückgewiesen.\nSie ist offensichtlich unbegründet.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='1 BvR 123/09')
        c.commit('Bundesverfassungsgericht 1 BvR 100/15', {D2: decision('Gleichheit', 'Der Schaden ist nach § 823 BGB zu ersetzen.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Bundesverfassungsgericht', Docket='1 BvR 100/15',
                 ECLI='ECLI:DE:BVerfG:2016:rs20160601.1bvr010015', Cites=f'{ART} (§ 823 BGB)')
        c.commit('Bundesverfassungsgericht 1 BvR 200/21', {D3: decision('Haftung', 'Die Haftung folgt aus § 823 Abs. 1 BGB.')},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court='Bundesverfassungsgericht', Docket='1 BvR 200/21',
                 ECLI='ECLI:DE:BVerfG:2022:rs20220303.1bvr020021', Cites=f'{ART} (§ 823 Abs. 1 BGB)')
        url = 'https://www.bundesverfassungsgericht.de/e/'
        rows = [{'decided': '2010-05-05', 'name': 'Bundesverfassungsgericht 1 BvR 123/09', 'court': 'Bundesverfassungsgericht',
                 'citation': 'ECLI:DE:BVerfG:2010:rk20100505.1bvr012309', 'url': url + '1', 'how': '§ 823 Abs. 1 BGB', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Bundesverfassungsgericht 1 BvR 100/15', 'court': 'Bundesverfassungsgericht',
                 'citation': 'ECLI:DE:BVerfG:2016:rs20160601.1bvr010015', 'url': url + '2', 'how': '§ 823 BGB', 'mentions': 2, 'decision': D2},
                {'decided': '2022-03-03', 'text_date': '2015-07-01', 'name': 'Bundesverfassungsgericht 1 BvR 200/21',
                 'court': 'Bundesverfassungsgericht', 'citation': 'ECLI:DE:BVerfG:2022:rs20220303.1bvr020021', 'url': url + '3',
                 'how': '§ 823 Abs. 1 BGB', 'mentions': 1, 'decision': D3, 'law_commit': cls.v2020}]
        index = 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in (
            ('1 BvR 123/09', D1), ('ECLI:DE:BVerfG:2010:rk20100505.1bvr012309', D1), ('1 BvR 100/15', D2),
            ('ECLI:DE:BVerfG:2016:rs20160601.1bvr010015', D2), ('1 BvR 200/21', D3), ('ECLI:DE:BVerfG:2022:rs20220303.1bvr020021', D3)))
        c.commit('Lexifina', {f'judgments/{LAW}/bgb/0823.jsonl': ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows),
                              'decision-index.tsv': index,
                              'corpus.json': json.dumps({'corpus': 'de/bverfg/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: Bundesverfassungsgericht', 'in_force_trailer': 'In-force'})},
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
        self.assertIn('offensichtlich unbegründet', self.cli('show', '2012-01-01', path))
        self.assertNotIn('offensichtlich', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Bundesverfassungsgericht 1 BvR 123/09', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('(court ruling', blame)  # the column is cut to its width: a long court name shortens the label
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('offensichtlich', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '2000-01-01', '2030-01-01')
        self.assertIn('BGBl. I 2020, 5', laws)
        self.assertNotIn('1 BvR 200/21', laws)
        german = self.cli('laws', '2000-01-01', '2030-01-01', 'germany')
        self.assertIn('BGBl. I 2020, 5', german)
        self.assertNotIn('(court decision)', german)
        decisions = self.cli('laws', '2000-01-01', '2030-01-01', 'germany/caselaw')
        self.assertIn('Bundesverfassungsgericht 1 BvR 200/21 (court decision)', decisions)
        self.assertNotIn('BGBl. I 2020, 5', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('Bundesverfassungsgericht 1 BvR 200/21 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_german_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        german = add('germany')
        self.assertIn(LAW, german)
        self.assertNotIn(CASES, german)
        self.assertIn(CASES, add('germany/caselaw'))
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
        self.assertFalse(by['ECLI:DE:BVerfG:2010:rk20100505.1bvr012309']['same_words'])
        self.assertEqual(by['ECLI:DE:BVerfG:2022:rs20220303.1bvr020021']['text_date'], '2015-07-01')
        self.assertFalse(by['ECLI:DE:BVerfG:2022:rs20220303.1bvr020021']['same_words'])
        self.assertIn('applying the text of 2015-07-01', prec['text'])
        self.assertEqual(by['ECLI:DE:BVerfG:2016:rs20160601.1bvr010015']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/bverfg'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}))
        for a in (read, cmp, who, listed, cases, hist):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('nach § 823 BGB zu ersetzen', read['text'])
        self.assertIn('offensichtlich', cmp['text'])
        self.assertIn('Bundesverfassungsgericht 1 BvR 123/09', who['text'])
        self.assertIn('Schadensersatz', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])

    def test_list_jurisdictions_names_german_case_law(self):
        (lj,) = self.calls(('list_jurisdictions', {}))
        self.assertFalse(lj['error'], lj['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('2022-03-03', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'Schaden'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': 'germany/caselaw'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'Bundesverfassungsgericht'}),
                             ('search_changes', {'query': 'Bundesverfassungsgericht', 'jurisdiction': 'germany/caselaw'}),
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
        self.assertIn('BGBl. I 2020, 5', laws['text'])
        self.assertNotIn('1 BvR 200/21', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_decisions_by_aktenzeichen_and_ecli_and_german_citations(self):
        found, by_ecli, details, cites = self.calls(
            ('find_provision', {'query': '1 BvR 200/21'}),
            ('find_provision', {'query': 'ECLI:DE:BVerfG:2016:rs20160601.1bvr010015'}),
            ('law_details', {'law': '1 BvR 100/15'}),
            ('resolve_citations', {'text': 'Der Anspruch folgt aus § 823 Abs. 1 BGB und Art. 3 Abs. 1 GG '
                                           '(BVerfG, 1 BvR 123/09), nicht aus § 1295 ABGB.', 'date': '2023-01-01'}))
        for a in (found, by_ecli, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D2}', by_ecli['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(ART, text)
        self.assertIn(f'{CASES}/{D1}', text)
        self.assertNotIn('ABGB', json.dumps([h.get('path') for h in cites['data'].get('citations', [])]))

    def test_a_decision_reference_in_no_served_case_law_is_answered_at_once(self):
        """A heading search for "1 BvR 1547/19" read every corpus for over 120 s (speed gate, 2026-11-06): a query that is
        only a decision's reference and is in no case law served is answered without searching the law."""
        import time
        t0 = time.time()
        (miss,) = self.calls(('find_provision', {'query': '1 BvR 9999/99'}))
        self.assertFalse(miss['error'], miss['text'])
        self.assertIn('No decision', miss['text'])
        self.assertEqual(miss['data']['results'], [])
        self.assertLess(time.time() - t0, 30)

    def test_list_jurisdictions_gives_each_case_law_corpus_its_latest_decision(self):
        """git misread --before=9999-12-31 (the "latest ever" date), so list_jurisdictions gave every German court's last
        decision as 2012-12-30 or so (case-law audit, 2026-11-07); the fixture's last decision is 2022-03-03."""
        (lj,) = self.calls(('list_jurisdictions', {}))
        row = next(c for c in lj['data']['corpora'] if c['path'] == CASES)
        self.assertEqual(row['last_change_in_record'], '2022-03-03')
        # The shared fixture dates every commit 2001; the bug needs decisions committed on their own (later) days.
        from tests.test_law_fixtures import Tree, run
        t = Tree()
        try:
            c = t.corpus('germany/bag/caselaw')
            for i, day in enumerate(('2010-03-24', '2015-06-01', '2020-06-23')):
                (c.path / f'd{i}.md').write_text(f'# {day}\n', encoding='utf-8')
                run('add', f'd{i}.md', cwd=c.path)
                stamp = f'{day}T12:00:00+01:00'
                run('commit', '-q', '-m', f'Bundesarbeitsgericht {i} AZR {i}/{day[2:4]}\n\nKind: court\nIn-force: {day}\n',
                    cwd=c.path, env={'GIT_AUTHOR_NAME': f'Bundesarbeitsgericht {i} AZR', 'GIT_AUTHOR_EMAIL': 'c@x.invalid',
                                     'GIT_AUTHOR_DATE': stamp, 'GIT_COMMITTER_NAME': 'Lexifina',
                                     'GIT_COMMITTER_EMAIL': 'corpus@lexifina.com', 'GIT_COMMITTER_DATE': stamp})
            t.pin()
            got = t.law().latest_decision('germany/bag/caselaw', '9999-12-31')
            self.assertEqual(got[1] if got else None, '2020-06-23')
        finally:
            try:
                t.close()
            except OSError:  # Windows: a git reader the module started may still hold the folder
                pass

    def test_german_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for text, abbr, nums in (('§ 823 Abs. 1 BGB', 'BGB', '823 Abs. 1'), ('§§ 280, 281 BGB', 'BGB', '280, 281'),
                                 ('§ 15 Abs. 1 Satz 1 AsylG', 'AsylG', '15 Abs. 1 Satz 1'), ('§ 13 SGB V', 'SGB V', '13')):
            hit = m.DE_PARA.search(text)
            self.assertIsNotNone(hit, text)
            self.assertEqual((hit.group('abbr'), hit.group('nums')), (abbr, nums), text)
        for other in ('Art. 336 OR', '§ 1295 ABGB', 'artikel 6:162 BW', 'article 1240 du code civil'):
            self.assertIsNone(m.DE_PARA.search(other), other)
        t = m.de_aliases()
        for abbr, folder in (('bgb', 'bgb'), ('stgb', 'stgb'), ('asylg', 'asylvfg_1992'), ('sgb5', 'sgb_5')):
            self.assertEqual(t['acts'][abbr], folder, abbr)
        self.assertNotIn('gg', t['acts'])  # the Grundgesetz is read by its own form
        for ref in ('1 BvR 123/20', 'VI ZR 123/20', '2 C 12.19', 'IX R 12/19', '5 AZR 123/19', '35 W (pat) 12/19'):
            self.assertTrue(m.DE_DOCKET.search(ref), ref)
        for not_german in ('4A_123/2024', '09/01234', 'A-1234/2020'):
            self.assertIsNone(m.DE_DOCKET.search(not_german), not_german)
        long_run = '§ ' + ', '.join(str(i) for i in range(3000)) + ' foo'
        import time
        t0 = time.time()
        self.assertIsNone(m.DE_PARA.search(long_run))
        self.assertLess(time.time() - t0, 2.0)


if __name__ == '__main__':
    unittest.main()
