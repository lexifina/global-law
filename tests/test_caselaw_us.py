"""United States case law in the tree: a corpus of decisions of the Supreme Court of the United States
(lexifina/united-states-supreme-court-caselaw and the courts of appeals' -caselaw repos), read with the same tools as law,
on a small tree built here: the US Code (11 U.S.C. § 1182 in two versions) and a case-law corpus (three decisions, a
correction, decision-index.tsv by reporter citation and docket number, and the judgment overlay).

  python -m unittest tests.test_caselaw_us -v

One test per feature of the feature list (as tests/test_caselaw_de.py does for Germany), plus the US forms: decisions by
reporter citation ("410 U.S. 113", "93 S. Ct. 705", "550 F.3d 1") and docket number ("No. 70-18").
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

LAW = 'united-states/federal/usc'
CASES = 'united-states/supreme-court/caselaw'
ART = f'{LAW}/title-11/1182.md'
COURT = 'Supreme Court of the United States'
FOLDER = 'decisions/supreme-court-of-the-united-states'
D1 = f'{FOLDER}/2010/560-U-S-100.md'
D2 = f'{FOLDER}/2016/578-U-S-200.md'
D3 = f'{FOLDER}/2022/596-U-S-300.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def decision(title: str, text: str) -> str:
    return f'---\ncourt: "{COURT}"\n---\n\n# {title}\n\n## Majority\n\n{text}\n'


class UnitedStatesCaseLaw(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        for name in ('swiss-aliases.json', 'nl-aliases.json', 'fr-aliases.json', 'de-aliases.json', 'pl-aliases.json'):
            if (ROOT / 'data' / name).exists():
                shutil.copy(ROOT / 'data' / name, t.root / 'data' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'United States Code', 'language': 'en', 'in_force_trailer': 'In-force', 'code': 'US'},
            {'path': CASES, 'name': 'Case law: Supreme Court of the United States', 'language': 'en', 'kind': 'judgments',
             'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'US'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Pub. L. 116-54', {'title-11/1182.md': '(1) The term "debtor" means a small business debtor.\n'},
                   In_force='2020-02-19', Kind='law')
        cls.v2022 = law.commit('Pub. L. 117-151', {'title-11/1182.md': '(1) The term "debtor" means a person engaged in commercial '
                                                                      'or business activities.\n'},
                               In_force='2022-06-21', Kind='law')
        c = t.corpus(CASES)
        c.commit(f'{COURT} 560 U.S. 100', {D1: decision('Smith v. Jones', 'The judgment is affirmed.\nIt is so ordered.')},
                 Kind='court', In_force='2010-05-05', Decided='2010-05-05', Court=COURT, Docket='08-1234',
                 Citation='560 U.S. 100', Cites=f'{ART} (11 U.S.C. § 1182)')
        c.commit(f'{COURT} 560 U.S. 100', {D1: decision('Smith v. Jones', 'The judgment is reversed.\nIt is so ordered.')},
                 Kind='correction', In_force='2011-01-01', Corrected='2011-01-01', Docket='08-1234')
        c.commit(f'{COURT} 578 U.S. 200', {D2: decision('Doe v. Roe', 'A small business debtor under 11 U.S.C. § 1182 may elect.')},
                 Kind='court', In_force='2016-06-01', Decided='2016-06-01', Court=COURT, Docket='15-100',
                 Citation='578 U.S. 200', Cites=f'{ART} (11 U.S.C. § 1182)')
        c.commit(f'{COURT} 596 U.S. 300', {D3: decision('In re Debtor', 'The definition in 11 U.S.C. § 1182(1) controls.')},
                 Kind='court', In_force='2022-03-03', Decided='2022-03-03', Court=COURT, Docket='21-200',
                 Citation='596 U.S. 300', Cites=f'{ART} (11 U.S.C. § 1182(1))')
        url = 'https://static.case.law/us/'
        rows = [{'decided': '2010-05-05', 'name': 'Smith v. Jones', 'court': COURT, 'citation': '560 U.S. 100', 'url': url + '1',
                 'how': '11 U.S.C. § 1182', 'mentions': 1, 'decision': D1},
                {'decided': '2016-06-01', 'name': 'Doe v. Roe', 'court': COURT, 'citation': '578 U.S. 200', 'url': url + '2',
                 'how': '11 U.S.C. § 1182', 'mentions': 2, 'decision': D2},
                {'decided': '2022-03-03', 'name': 'In re Debtor', 'court': COURT, 'citation': '596 U.S. 300', 'url': url + '3',
                 'how': '11 U.S.C. § 1182(1)', 'mentions': 1, 'decision': D3, 'law_commit': cls.v2022}]
        index = 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in (
            ('560 U.S. 100', D1), ('130 S. Ct. 1000', D1), ('08-1234', D1), ('578 U.S. 200', D2), ('15-100', D2),
            ('596 U.S. 300', D3), ('142 S. Ct. 3000', D3), ('21-200', D3)))
        c.commit('Lexifina', {f'judgments/{LAW}/title-11/1182.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': index,
                              'corpus.json': json.dumps({'corpus': 'us/supreme-court/caselaw', 'kind': 'judgments',
                                                         'name': 'Case law: Supreme Court of the United States',
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

    # --- law.py on a decision -------------------------------------------------------------------------------------

    def test_law_py_reads_a_decision(self):
        path = f'{CASES}/{D1}'
        self.assertIn('reversed', self.cli('show', '2012-01-01', path))
        self.assertIn('affirmed', self.cli('show', '2010-06-01', path))
        log = self.cli('log', path)
        self.assertIn('560 U.S. 100', log)
        self.assertIn('2011-01-01', log)
        blame = self.cli('blame', '2012-01-01', path)
        self.assertIn('560 U.S. 100 (cou', blame)  # the column is cut to its width: the label shortens
        self.assertIn('2011-01-01      Supreme Court of the United States 560 U.S. 100 (cor', blame)  # the correction's line
        self.assertIn('court ruling, not a law', self.cli('words', '2012-01-01', path))
        self.assertIn('reversed', self.cli('diff', '2010-06-01', '2012-01-01', path))
        self.assertNotIn('same', self.cli('today', '2010-06-01', path).split('\n')[0].lower())

    def test_laws_leaves_out_decisions_unless_named(self):
        laws = self.cli('laws', '2000-01-01', '2030-01-01')
        self.assertIn('Pub. L. 117-151', laws)
        self.assertNotIn('596 U.S. 300', laws)
        decisions = self.cli('laws', '2000-01-01', '2030-01-01', 'united-states/caselaw')
        self.assertIn('596 U.S. 300 (court decision)', decisions)
        self.assertNotIn('Pub. L. 117-151', decisions)

    def test_world_labels_the_latest_decision(self):
        self.assertIn('596 U.S. 300 (latest decision), given 2022-03-03', self.cli('world', '2023-01-01'))

    def test_countries_adds_us_case_law_only_by_name(self):
        def add(name):
            done = subprocess.run([sys.executable, '-X', 'utf8', 'tools/countries.py', 'add', name], cwd=self.t.root,
                                  capture_output=True, encoding='utf-8', timeout=120)
            return done.stdout + done.stderr
        us = add('united-states')
        self.assertIn(LAW, us)
        self.assertNotIn(CASES, us)
        self.assertIn(CASES, add('united-states/caselaw'))
        self.assertIn(CASES, add(CASES))
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
        self.assertFalse(by['578 U.S. 200']['same_words'])
        self.assertFalse(by['596 U.S. 300']['same_words'])  # decided 2022-03-03, before Pub. L. 117-151 took force
        self.assertEqual(by['578 U.S. 200']['decision'], f'{CASES}/{D2}')
        self.assertFalse(else_['error'], else_['text'])
        self.assertIn('court decision(s) cite it', else_['text'])

    def test_a_decision_is_read_like_a_provision(self):
        path = f'{CASES}/{D1}'
        read, cmp, who, listed, cases, hist = self.calls(
            ('read_law', {'path': f'{CASES}/{D2}', 'date': '2023-01-01'}),
            ('compare_dates', {'path': path, 'date_a': '2010-06-01', 'date_b': '2012-01-01'}),
            ('who_wrote', {'path': path, 'date': '2012-01-01'}),
            ('list_provisions', {'path': f'{CASES}/{FOLDER}'}),
            ('applies_to_case', {'path': path, 'commenced': '2010-01-01'}),
            ('provision_history', {'path': path}))
        for a in (read, cmp, who, listed, cases, hist):
            self.assertFalse(a['error'], a['text'])
        self.assertIn('small business debtor', read['text'])
        self.assertIn('reversed', cmp['text'])
        self.assertIn('560 U.S. 100', who['text'])
        self.assertIn('Smith v. Jones', listed['text'])
        self.assertTrue(cases['data']['court_decision'])
        self.assertIn('court decision, not a law', cases['text'])
        self.assertIn('2010-05-05', hist['text'])
        self.assertIn('2011-01-01', hist['text'])

    def test_list_jurisdictions_names_us_case_law(self):
        (lj,) = self.calls(('list_jurisdictions', {}))
        self.assertFalse(lj['error'], lj['text'])
        self.assertIn(CASES, lj['text'])
        self.assertIn('2022-03-03', lj['text'])

    def test_lists_and_searches_leave_case_law_out_unless_asked(self):
        q = 'debtor'
        answers = self.calls(('search_law', {'query': q, 'date': '2023-01-01'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'kind': 'judgments'}),
                             ('search_law', {'query': q, 'date': '2023-01-01', 'jurisdiction': 'united-states/caselaw'}),
                             ('laws_between', {'start': '2000-01-01', 'end': '2030-01-01'}),
                             ('search_changes', {'query': 'Supreme Court'}),
                             ('search_changes', {'query': 'Supreme Court', 'jurisdiction': 'united-states/caselaw'}),
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
        self.assertIn('Pub. L. 117-151', laws['text'])
        self.assertNotIn('596 U.S. 300', laws['text'].split('Not read')[0])
        self.assertEqual(changes['data']['changes'], [])
        self.assertTrue(changes_cl['data']['changes'])
        self.assertNotIn(f'{CASES}/', phrase['text'].split('Not read')[0])
        self.assertNotIn(f'{CASES}/', between['text'].split('Not read')[0])

    def test_decisions_by_reporter_citation_and_docket_and_us_citations(self):
        found, by_sct, by_docket, details, cites = self.calls(
            ('find_provision', {'query': '596 U.S. 300'}),
            ('find_provision', {'query': '130 S. Ct. 1000'}),
            ('find_provision', {'query': 'No. 15-100'}),
            ('law_details', {'law': '578 U.S. 200'}),
            ('resolve_citations', {'text': 'See Smith v. Jones, 560 U.S. 100 (2010), and 11 U.S.C. § 1182; '
                                           'cf. BGE 142 II 307.', 'date': '2023-01-01'}))
        for a in (found, by_sct, by_docket, details, cites):
            self.assertFalse(a['error'], a['text'])
        self.assertIn(f'{CASES}/{D3}', found['text'])
        self.assertIn(f'{CASES}/{D1}', by_sct['text'])
        self.assertIn(f'{CASES}/{D2}', by_docket['text'])
        self.assertIn(f'{CASES}/{D2}', details['text'])
        text = json.dumps(cites['data'], ensure_ascii=False)
        self.assertIn(f'{CASES}/{D1}', text)

    def test_a_reporter_citation_in_no_served_case_law_is_answered_at_once(self):
        import time
        t0 = time.time()
        (miss,) = self.calls(('find_provision', {'query': '999 U.S. 999'}))
        self.assertFalse(miss['error'], miss['text'])
        self.assertIn('No decision', miss['text'])
        self.assertEqual(miss['data']['results'], [])
        self.assertLess(time.time() - t0, 30)

    def test_heading_search_reads_case_law_only_when_named(self):
        """find_provision's heading search left case law out unless its scope names it: reading a million US decisions'
        headings for "automatic stay" took 110 s (US speed gate, 2026-11-07). A decision is still found by reference."""
        plain, scoped, ref = self.calls(('find_provision', {'query': 'small business debtor'}),
                                        ('find_provision', {'query': 'small business debtor', 'jurisdiction': 'united-states/caselaw'}),
                                        ('find_provision', {'query': '578 U.S. 200'}))
        for a in (plain, scoped, ref):
            self.assertFalse(a['error'], a['text'])
        self.assertNotIn(f'{CASES}/', plain['text'])
        self.assertIn(f'{CASES}/{D2}', ref['text'])

    def test_us_citation_forms(self):
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server as m
        for text in ('410 U.S. 113', '410 U. S. 113', '93 S. Ct. 705', '35 L. Ed. 2d 147', '550 F.3d 1', '123 F. Supp. 2d 45',
                     "200 F. App'x 3", '5 F. 123', '300 F.2d 10'):
            self.assertTrue(m.US_REPORTER.fullmatch(text), text)
        for not_a_case in ('11 U.S.C. § 1182', '11 U.S.C. 1182', '42 U.S.C. § 1983', 'BGE 142 II 307', 'Art. 336 OR',
                           '§ 823 Abs. 1 BGB', 'artikel 6:162 BW', 'art. 415 k.c.'):
            self.assertIsNone(m.US_REPORTER.search(not_a_case), not_a_case)
        self.assertEqual(m.US_DOCKET.search('No. 70-18').group(0), 'No. 70-18')
        self.assertIsNone(m.US_DOCKET.search('n° 18-12.345'))


if __name__ == '__main__':
    unittest.main()
