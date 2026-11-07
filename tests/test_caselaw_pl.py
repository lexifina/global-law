"""Polish case law in the tree: corpora of judgments (lexifina/poland-<court group>-caselaw, from SAOS, the courts'
judgments being official documents outside copyright under Art. 4 of the Polish Copyright Act), read with the same tools
as law, on a small tree built here: Polish law (Kodeks cywilny art. 415 in two versions, Kodeks pracy art. 22¹ and the
Constitution) and a case-law corpus of the Sąd Najwyższy (three judgments, a correction, the judgment overlay with one
row's law_record_from, and decision-index.tsv, as the files are named by case number and SAOS id).

  python -m unittest tests.test_caselaw_pl -v

One test per feature of the feature list (as tests/test_caselaw_fr.py does for France), plus the Polish forms: judgments
by case number (sygnatura); articles by code abbreviation ("art. 415 k.c.", "art. 22¹ § 1 k.p.", "art. 32 ust. 1
Konstytucji RP"); codes poland-law does not hold and other countries' forms left alone.
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

LAW = 'poland/national/acts'
CASES = 'poland/sad-najwyzszy/caselaw'
TK = 'poland/trybunal-konstytucyjny/caselaw'
TK1 = 'decisions/trybunal-konstytucyjny/2016/K-1-16-2001.md'
KIO = 'poland/krajowa-izba-odwolawcza/caselaw'
K1 = 'decisions/krajowa-izba-odwolawcza/2018/KIO-1711-18-354890.md'  # SAOS's last (2018-09-06)
K2 = 'decisions/krajowa-izba-odwolawcza/2025/KIO-100-25-uzp-30001.md'  # from orzeczenia.uzp.gov.pl, appended after SAOS's
K3 = 'decisions/krajowa-izba-odwolawcza/2024/KIO-900-24-uzp-29001.md'  # a late upload, appended after K2: out of order
ART = f'{LAW}/kodeks-cywilny/art-415.md'
# words that left art. 416 in 2018 and are law in art. 417 after: check_precedent says where they went
MOVED = 'Osoba prawna jest obowiązana do naprawienia szkody wyrządzonej z winy jej organu.'
D1 = 'decisions/sad-najwyzszy/2010/II-CSK-100-10-1001.md'
D2 = 'decisions/sad-najwyzszy/2016/IV-CSK-200-16-1002.md'
D3 = 'decisions/sad-najwyzszy/2022/I-CSKP-300-21-1003.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def judgment(title: str, text: str) -> str:
    return f'---\ncourt: "Sąd Najwyższy"\nsource_url: "https://www.sn.pl/"\n---\n\n# {title}\n\n## Treść\n\n{text}\n'


class PolishCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        globals()['run'] = run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for p in (ROOT / 'data').glob('*-aliases.json'):
            shutil.copy(p, t.root / 'data' / p.name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'Polish law', 'language': 'pl', 'in_force_trailer': 'In-force', 'code': 'PL'},
            {'path': CASES, 'name': 'Case law: Sąd Najwyższy', 'language': 'pl', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'PL'},
            {'path': TK, 'name': 'Case law: Trybunał Konstytucyjny', 'language': 'pl', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'PL', 'history_from': '2016-06-01'},
            {'path': KIO, 'name': 'Case law: Krajowa Izba Odwoławcza', 'language': 'pl', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'PL', 'history_from': '2018-09-06'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Dz.U. 1964 nr 16 poz. 93', {'kodeks-cywilny/art-415.md': '# Art. 415\n\nKto z winy swej wyrządził drugiemu szkodę, '
                                                                            'obowiązany jest do jej naprawienia.\n',
                                                'kodeks-pracy/art-022-1.md': '# Art. 22¹\n\nPracodawca żąda danych osobowych.\n',
                                                'konstytucja/art-032.md': '# Art. 32\n\nWszyscy są wobec prawa równi.\n',
                                                'kodeks-cywilny/art-416.md': f'# Art. 416\n\n{MOVED}\n',
                                                'kodeks-cywilny/art-417.md': '# Art. 417\n\nSkarb Państwa odpowiada za szkodę.\n'},
                   In_force='2009-01-01', Kind='law')
        cls.v2018 = law.commit('Dz.U. 2018 poz. 1', {'kodeks-cywilny/art-415.md': '# Art. 415\n\nKto z winy swej wyrządził drugiemu '
                                                                                 'szkodę, obowiązany jest do jej naprawienia w całości.\n',
                                                     'kodeks-cywilny/art-416.md': '# Art. 416\n\n(uchylony)\n',
                                                     'kodeks-cywilny/art-417.md': f'# Art. 417\n\nSkarb Państwa odpowiada za szkodę. {MOVED}\n'},
                               In_force='2018-01-01', Kind='law')
        c = t.corpus(CASES)
        c.commit('Sąd Najwyższy II CSK 100/10', {D1: judgment('Odpowiedzialność deliktowa', 'Skarga kasacyjna zostaje oddalona.\nWina jest wykazana.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court='Sąd Najwyższy', Docket='II CSK 100/10',
                 Cites=f'{ART} (art. 415 k.c.)')
        c.commit('Sąd Najwyższy II CSK 100/10', {D1: judgment('Odpowiedzialność deliktowa', 'Skarga kasacyjna zostaje oddalona.\nWina jest udowodniona.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='II CSK 100/10')
        c.commit('Sąd Najwyższy IV CSK 200/16', {D2: judgment('Szkoda i wina', 'Sprawca naprawia szkodę.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Sąd Najwyższy', Docket='IV CSK 200/16',
                 Cites=f'{ART} (art. 415 k.c.)')
        c.commit('Sąd Najwyższy I CSKP 300/21', {D3: judgment('Naprawienie szkody', 'Wyrok zostaje uchylony.')},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court='Sąd Najwyższy', Docket='I CSKP 300/21',
                 Cites=f'{ART} (art. 415 k.c.)')
        rows = [{'decided': '2010-05-05', 'name': 'Sąd Najwyższy II CSK 100/10', 'court': 'Sąd Najwyższy', 'citation': 'II CSK 100/10',
                 'url': 'https://www.sn.pl/1', 'how': 'art. 415 k.c.', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Sąd Najwyższy IV CSK 200/16', 'court': 'Sąd Najwyższy', 'citation': 'IV CSK 200/16',
                 'url': 'https://www.sn.pl/2', 'how': 'art. 415 k.c.', 'mentions': 2, 'decision': D2},
                {'decided': '2022-03-03', 'name': 'Sąd Najwyższy I CSKP 300/21', 'court': 'Sąd Najwyższy', 'citation': 'I CSKP 300/21',
                 'url': 'https://www.sn.pl/3', 'how': 'art. 415 k.c.', 'mentions': 1, 'decision': D3, 'law_commit': cls.v2018}]
        index = ''.join(f'{ref}\t{p}\n' for ref, p in (('II CSK 100/10', D1), ('SAOS 1001', D1), ('IV CSK 200/16', D2),
                                                         ('SAOS 1002', D2), ('I CSKP 300/21', D3), ('SAOS 1003', D3)))
        moved = {'decided': '2012-02-02', 'name': 'Sąd Najwyższy II CSK 100/10', 'court': 'Sąd Najwyższy', 'citation': 'II CSK 100/10',
                 'url': 'https://www.sn.pl/1', 'how': 'art. 416 k.c.', 'mentions': 1, 'decision': D1}
        c.commit('Lexifina', {f'judgments/{LAW}/kodeks-cywilny/art-415.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              f'judgments/{LAW}/kodeks-cywilny/art-416.jsonl': json.dumps(moved) + '\n',
                              'decision-index.tsv': 'reference\tpath\n' + index,
                              'corpus.json': json.dumps({'corpus': 'pl/sad-najwyzszy/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: Sąd Najwyższy', 'in_force_trailer': 'In-force'})},
                 Kind='documentation')
        # The Trybunał Konstytucyjny: a one-letter repertory ("K 1/16") and a commit dated the day given, after 2012, as
        # the real corpora are (list_jurisdictions read "--before=9999-12-31" as 2012-12-28 and missed it).
        tk = t.corpus(TK)
        tk.commit('Trybunał Konstytucyjny K 1/16', {TK1: judgment('Wyrok Trybunału', 'Przepis jest zgodny z Konstytucją.')},
                  Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court='Trybunał Konstytucyjny', Docket='K 1/16')
        run('commit', '-q', '--amend', '--no-edit', '--date=2016-06-01T12:00:00+0200', cwd=tk.path)
        tk.commit('Lexifina', {'decision-index.tsv': f'reference\tpath\nK 1/16\t{TK1}\nSAOS 2001\t{TK1}\n'}, Kind='documentation')
        # The KIO: SAOS's decisions to 2018-09-06, then the UZP portal's appended after them (UZP: <portal id>), and a late
        # upload of 2024 appended after one of 2025, as the nightly run appends them.
        kio = t.corpus(KIO)
        for path, day, docket, extra in ((K1, '2018-09-06', 'KIO 1711/18', {'SAOS': '354890'}),
                                         (K2, '2025-01-15', 'KIO 100/25', {'UZP': '30001'}),
                                         (K3, '2024-06-03', 'KIO 900/24', {'UZP': '29001'})):
            kio.commit(f'Krajowa Izba Odwoławcza {docket}', {path: judgment(f'Krajowa Izba Odwoławcza, Wyrok, {day}, {docket}',
                                                                                 'Izba oddala odwołanie.')},
                       Kind='court', In_force=day, Decided=day, Court='Krajowa Izba Odwoławcza', Docket=docket, **extra)
            run('commit', '-q', '--amend', '--no-edit', f'--date={day}T12:00:00+0100', cwd=kio.path)
        kio.commit('Lexifina', {'decision-index.tsv': f'reference\tpath\nKIO 1711/18\t{K1}\nSAOS 354890\t{K1}\n'
                                                      f'KIO 100/25\t{K2}\nUZP 30001\t{K2}\nKIO 900/24\t{K3}\nUZP 29001\t{K3}\n'},
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

    # --- law.py on a judgment -------------------------------------------------------------------------------------

    def test_law_py_reads_a_judgment(self):
        path = f'{CASES}/{D1}'
        self.assertIn('udowodniona', self.cli('show', '2012-01-01', path))
        self.assertIn('wykazana', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('Sąd Najwyższy II CSK 100/10', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('court ruling, not a law', blame)
        self.assertIn('correction', blame)
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('udowodniona', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_judgments_unless_named(self):
        laws = self.cli('laws', '2000-01-01', '2030-01-01')
        self.assertIn('Dz.U. 2018 poz. 1', laws)
        self.assertNotIn('I CSKP 300/21', laws)
        judgments = self.cli('laws', '2000-01-01', '2030-01-01', 'poland/caselaw')
        self.assertIn('Sąd Najwyższy I CSKP 300/21 (court decision)', judgments)
        self.assertNotIn('Dz.U. 2018 poz. 1', judgments)

    def test_world_labels_the_latest_judgment(self):
        self.assertIn('Sąd Najwyższy I CSKP 300/21 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_polish_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        polish = add('poland')
        self.assertIn(LAW, polish)
        self.assertNotIn(CASES, polish)
        self.assertIn(CASES, add('poland/caselaw'))
        listing = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py'], cwd=self.t.root,
                                 capture_output=True, encoding='utf-8', timeout=120).stdout
        self.assertTrue(any(CASES in l and 'court decisions' in l for l in listing.splitlines()), listing)

    # --- the server ---------------------------------------------------------------------------------------------

    def test_check_precedent_and_what_else_changes_read_the_overlay(self):
        prec, else_ = self.calls(('check_precedent', {'path': ART, 'date': '2023-01-01'}),
                                 ('what_else_changes', {'path': ART, 'date': '2023-01-01'}))
        self.assertFalse(prec['error'], prec['text'])
        self.assertEqual(prec['data']['judgments_recorded'], 3)
        by = {c['citation']: c for c in prec['data']['checks']}
        self.assertFalse(by['II CSK 100/10']['same_words'])  # given before the 2018 change
        self.assertTrue(by['I CSKP 300/21']['same_words'])
        self.assertEqual(by['IV CSK 200/16']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_check_precedent_finds_where_the_applied_words_went(self):
        prec = self.calls(('check_precedent', {'path': f'{LAW}/kodeks-cywilny/art-416.md', 'date': '2023-01-01'}))[0]
        self.assertFalse(prec['error'], prec['text'])
        check = prec['data']['checks'][0]
        self.assertFalse(check['same_words'])
        self.assertEqual([m['now_in'] for m in check['removed_words_now_elsewhere']][:1], [[f'{LAW}/kodeks-cywilny/art-417.md']])

    def test_a_judgment_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist, lj = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/decisions/sad-najwyzszy'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}),
            ('list_jurisdictions', {}))
        for a in (read, cmp, who, listed, cases, hist, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('naprawia szkodę', read['text'])
        self.assertIn('udowodniona', cmp['text'])
        self.assertIn('Sąd Najwyższy II CSK 100/10', who['text'])
        self.assertIn('Odpowiedzialność deliktowa', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('2022-03-03', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'szkod'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': 'poland/caselaw'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'Sąd Najwyższy'}),
                             ('search_changes', {'query': 'Sąd Najwyższy', 'jurisdiction': 'poland/caselaw'}),
                             ('phrase_history', {'query': q}),
                             ('changes_between', {'date_a': '2009-06-01', 'date_b': '2023-01-01'}))
        for a in answers:
            self.assertFalse(a['error'], a['text'])
        law_only, judgments, named, laws, changes, changes_cl, phrase, between = answers
        self.assertIn(ART, law_only['text'])
        self.assertNotIn(CASES, law_only['text'].split('Not read')[0])
        self.assertIn(f'{CASES}/{D2}', judgments['text'])
        self.assertNotIn(ART, judgments['text'])
        self.assertIn(f'{CASES}/{D2}', named['text'])
        self.assertIn('Dz.U. 2018 poz. 1', laws['text'])
        self.assertNotIn('I CSKP 300/21', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_judgments_by_case_number_and_polish_citations(self):
        by_docket, details, cites = self.calls(
            ('find_provision', {'query': 'I CSKP 300/21'}),
            ('law_details', {'law': 'IV CSK 200/16'}),
            ('resolve_citations', {'text': 'Zgodnie z art. 415 k.c., art. 22¹ § 1 k.p. i art. 32 ust. 1 Konstytucji RP oraz '
                                           'wyrokiem II CSK 100/10, lecz nie art. 6 k.p.a. ani § 823 Abs. 1 BGB.',
                                   'date': '2023-01-01'}))
        for a in (by_docket, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', by_docket['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        paths = [h.get('path') for h in cites['data'].get('citations', [])]
        self.assertIn(ART, paths)
        self.assertIn(f'{LAW}/kodeks-pracy/art-022-1.md', paths)
        self.assertIn(f'{LAW}/konstytucja/art-032.md', paths)
        self.assertIn(f'{CASES}/{D1}', paths)
        self.assertFalse([p for p in paths if p and 'kodeks-postepowania-administracyjnego' in p], paths)  # not held

    def test_polish_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for text, want in (('art. 415 k.c.', 'kodeks-cywilny/art-415.md'), ('art. 22¹ § 1 k.p.', 'kodeks-pracy/art-022-1.md'),
                           ('art. 77[1] k.p.', 'kodeks-pracy/art-077-1.md'), ('art. 58 § 1 i 2 k.c.', 'kodeks-cywilny/art-058.md'),
                           ('art. 189 k.p.c.', 'kodeks-postepowania-cywilnego/art-189.md'),
                           ('art. 32 ust. 1 Konstytucji RP', 'konstytucja/art-032.md'), ('art. 148 § 1 k.k.', 'kodeks-karny/art-148.md')):
            got = [h['path'] for h in m.citations_in(text) if h['country'] == 'pl' and h.get('path')]
            self.assertEqual(got, [f'{LAW}/{want}'], text)
        for other in ('art. 6 k.p.a.', '§ 823 Abs. 1 BGB', 'art. 1240 du code civil', 'Art. 336 OR', 'artikel 6:162 BW',
                      'VI ZR 123/20', '2 C 12.19'):
            self.assertFalse([h for h in m.citations_in(other) if h['country'] == 'pl'], other)
        for ref in ('II CSK 123/20', 'I ACa 456/19', 'II OSK 123/20', 'III SA/Wa 1234/19', 'SK 12/20', 'KIO 1234/20'):
            self.assertTrue(m.PL_DOCKET.search(ref), ref)
            self.assertFalse(m.DE_DOCKET.search(ref), ref)

    def test_constitutional_tribunal_numbers_saos_ids_and_the_latest_decision(self):
        by_k, by_saos, details, lj = self.calls(('find_provision', {'query': 'K 1/16'}), ('find_provision', {'query': 'SAOS 2001'}),
                                                ('law_details', {'law': 'K 1/16'}), ('list_jurisdictions', {}))
        for a in (by_k, by_saos, details, lj):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{TK}/{TK1}', by_k['text'])
        self.assertIn(f'{TK}/{TK1}', by_saos['text'])
        self.assertIn('Trybunał Konstytucyjny K 1/16', details['text'])
        rows = {c['path']: c for c in lj['data']['corpora']}
        self.assertEqual(rows[TK]['last_change_in_record'], '2016-06-01')
        self.assertEqual(rows[CASES]['last_change_in_record'], '2022-03-03')
        self.assertIn(f'{TK}: Case law: Trybunał Konstytucyjny (pl; 1 decision files)', lj['text'])
        self.assertFalse(PL_REF_IN_TEXT(), 'a one-letter repertory is never read as a citation in running text')

    def test_kio_decisions_from_the_uzp_portal_appended_out_of_order(self):
        """The KIO after SAOS (orzeczenia.uzp.gov.pl): found by docket and by portal id, and a late upload appended after
        a newer decision is not the latest decision (the latest day given is)."""
        by_docket, by_uzp, lj, world = self.calls(('find_provision', {'query': 'KIO 100/25'}), ('find_provision', {'query': 'UZP 29001'}),
                                                  ('list_jurisdictions', {}), ('world_on_date', {'date': '2024-12-31'}))
        for a in (by_docket, by_uzp, lj, world):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{KIO}/{K2}', by_docket['text'])
        self.assertIn(f'{KIO}/{K3}', by_uzp['text'])
        rows = {c['path']: c for c in lj['data']['corpora']}
        self.assertEqual(rows[KIO]['last_change_in_record'], '2025-01-15')
        self.assertIn('KIO 900/24 (latest decision), given 2024-06-03', world['text'])
        self.assertIn('KIO 100/25 (latest decision), given 2025-01-15', self.cli('world', '2026-01-01'))
        self.assertIn('KIO 1711/18 (latest decision), given 2018-09-06', self.cli('world', '2019-01-01'))

    def test_served_note_with_case_law_chosen_by_path(self):
        """Corpora chosen by their own paths (as countries.py only writes them) are not matched against every corpus
        (1.0 s of world_on_date with 14 Polish case-law corpora), and a misspelt choice is still named."""
        code = ('import os, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True\n'
                'import mcp_server as m\n'
                f'os.environ["GLOBAL_LAW_JURISDICTIONS"] = "{LAW},{CASES},{KIO}"\n'
                'a = m.served_note()\n'
                f'os.environ["GLOBAL_LAW_JURISDICTIONS"] = "{LAW},polandd/caselaw"\n'
                'b = m.served_note()\n'
                'print(repr(a)); print(repr(b))\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True, encoding='utf-8',
                              timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        a, b = done.stdout.splitlines()[:2]
        self.assertNotIn('name nothing', a)
        self.assertIn("'polandd/caselaw'", b)
        self.assertIn('name nothing', b)

    def test_a_search_of_case_law_stops_at_its_line_cap_and_says_so(self):
        code = CALL.replace('import mcp_server\n', 'import mcp_server; mcp_server.CASELAW_LINES = 1\n')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', code], cwd=self.t.root, capture_output=True, encoding='utf-8',
                              input=json.dumps([('search_law', {'query': 'a', 'date': '2023-01-01', 'kind': 'judgments'}),
                                                ('search_law', {'query': 'szkod', 'date': '2023-01-01'})]), timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        capped, law_only = json.loads(done.stdout)
        self.assertFalse(capped['error'], capped['text'])
        self.assertTrue(capped['text'].startswith('At least '), capped['text'])
        self.assertTrue(capped['data']['case_law_read_in_part'])
        self.assertFalse(law_only['data']['case_law_read_in_part'])
        self.assertIn(ART, law_only['text'])


def PL_REF_IN_TEXT():
    sys.path.insert(0, str(ROOT / 'tools'))
    import mcp_server as m
    return [h for h in m.citations_in('Wyrok TK K 1/16 oraz 2 K 123/20 und S 1/20.') if h['country'] == 'pl']


if __name__ == '__main__':
    unittest.main()
