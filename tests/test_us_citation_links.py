"""How US case law links to legislation, and how the tools read US citations (cap-interplay-check and cap-deep-check,
2026-11-09). One test per defect found:

  D1  a PACER page stamp ("USCA4 Appeal ... Pg: 3", "13 USCA11") is not a US Code citation
  D2  a section number under an older numbering (before the title's recodification, before the section was added, an
      earlier edition, "former") is not today's section
  D3  "Pub. L. No.", "H.R. Rep. No.", "Dkt. No." and street numbers are not dockets; a shared docket is settled by the
      words around it, or named as ambiguous with a short list
  D4  "(a)(4)" is a subsection, not section 4
  D5  the same decision filed twice resolves once (decision-relations.tsv, and the same day and name)
  D6  a state statute is named as not held; a Puerto Rico "Código Civil" is not Spain's
  D7  lists, ranges, "U.S.C.S.", long forms and older reporter forms are read
  D9  check_precedent says "before the record starts" for a decision older than the record
  T1  a decision is "not yet decided" on a date before it; T2 law_details matches a decision's author whole; T6 a
      decision dated by month only says so; world_on_date takes a jurisdiction; git grep threads are capped

  python -m unittest tests.test_us_citation_links -v
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
sys.path.insert(0, str(ROOT / 'tools'))

import usc_cite  # noqa: E402

LAW = 'united-states/federal/usc'
CASES = 'united-states/alabama/caselaw'
COURT = 'Alabama Supreme Court'
F = 'decisions/alabama-supreme-court'
BARNHART = f'{F}/2018/275-So-3d-1112.md'
ALA9 = f'{F}/1840/1-Ala-9.md'
ALA98 = f'{F}/1840/1-Ala-98.md'
HUGHES1 = f'{F}/1978/362-So-2d-918.md'
HUGHES2 = f'{F}/1979/372-So-2d-845.md'
DUP_KEPT = f'{F}/1990/560-So-2d-1.md'
DUP_COPY = f'{F}/1990/560-So-2d-1--cap-99.md'
MONTH = f'{F}/1900/126-Ala-1.md'
OLD = f'{F}/2000/770-So-2d-1.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')


def sections(text, **kw):
    return [(c['title'], c['section'], c['role']) for c in usc_cite.cites(text, **kw)]


class UsCodeCitationReader(unittest.TestCase):
    """usc_cite.py: the reader the case-law builders and resolve_citations share."""

    def test_d1_page_stamps_are_not_citations(self):
        for stamp in ('USCA4 Appeal: 19-1234 Doc: 45 Filed: 03/02/2021 Pg: 3 of 47', 'Pg: 3 USCA4 Appeal', '13 USCA11 Case: 18-1',
                      'Filed: 1 Pg: 4 USCA4 Appeal: 20-1'):
            self.assertEqual(sections(stamp), [], stamp)
        # "U.S.C." needs a separator and a section: never a digit or letter straight after it
        self.assertEqual(sections('11 U.S.C.362'), [])
        self.assertEqual(sections('11 U.S.C.§362'), [(11, '362', 'cited')])
        self.assertEqual(sections('15 USC 78j(b)'), [(15, '78j', 'cited')])

    def test_d4_subsections_are_not_sections(self):
        self.assertEqual(sections('9 U.S.C. § 10(a)(4)'), [(9, '10', 'cited')])
        self.assertEqual(sections('11 U.S.C. § 523(a)(2)(A)'), [(11, '523', 'cited')])
        self.assertEqual(sections('11 U.S.C. § 503(b)(l)(B)(i)'), [(11, '503', 'cited')])

    def test_d7_lists_ranges_and_forms(self):
        self.assertEqual(sections('11 U.S.C. §§ 361, 363(e), and 364'), [(11, '361', 'cited'), (11, '363', 'cited'), (11, '364', 'cited')])
        self.assertEqual(sections('11 U.S.C. § 707(a), § 1112(b)(1), § 1307(b)'), [(11, '707', 'cited'), (11, '1112', 'cited'), (11, '1307', 'cited')])
        self.assertEqual(sections('9 U.S.C. §§ 1-16'), [(9, '1', 'range-start'), (9, '16', 'range-end')])
        self.assertEqual(sections('9 U.S.C. §§ 1 through 16'), [(9, '1', 'range-start'), (9, '16', 'range-end')])
        self.assertEqual(sections('11 U.S. C.A. § 701 to § 766'), [(11, '701', 'range-start'), (11, '766', 'range-end')])
        self.assertEqual(sections('42 U.S.C. § 2000e-2(a)', exists=lambda t, s: s == '2000e-2'), [(42, '2000e-2', 'cited')])
        for text, want in (('11 U.S.C, § 1126', '1126'), ('11 U.S.C., Sec. 104', '104'), ('11 U.S.C.S. § 523(a)(2)(A)', '523'),
                           ('11 U. S. C. A., § 351', '351'), ('4 USCA, § 7', '7'), ('11 U.S.C.A. §.544(a)', '544'),
                           ('11 U.S.C. Section 501(a)', '501')):
            self.assertEqual([s for _, s, _ in sections(text)], [want], text)
        self.assertEqual(sections('Title 11, United States Code, section 541', long_forms=True), [(11, '541', 'cited')])
        self.assertEqual(sections('section 1334 of title 28', long_forms=True), [(28, '1334', 'cited')])
        # a later number that is a reporter's volume, a Westlaw year or another title is not a further section
        self.assertEqual(sections('11 U.S.C. § 362, 365 F.3d 1'), [(11, '362', 'cited')])
        self.assertEqual(sections('11 U.S.C. § 101, 1997 WL 1234'), [(11, '101', 'cited')])
        self.assertEqual(sections('11 U.S.C. § 362(a), 28 U.S.C. § 157'), [(11, '362', 'cited'), (28, '157', 'cited')])

    def test_long_lists_that_are_no_citation_are_read_at_once(self):
        """A state opinion's "sections 1, 2, 3, ... of the act" that never says "of title N" was read by every split of
        its spaces: one Connecticut decision took minutes (the overlay rebuild, 2026-11-09)."""
        import time
        text = ('Under sections ' + ', '.join(str(i) for i in range(1, 60)) + '  and  61 of the act, ' + 'section 4 , 5 , 6 ' * 50) * 20
        t0 = time.time()
        usc_cite.cites(text, long_forms=True)
        self.assertLess(time.time() - t0, 2)

    def test_d2_older_numbering(self):
        one = lambda text: usc_cite.cites(text)[0]
        self.assertIn('Bankruptcy Reform Act', usc_cite.old_numbering(one('11 U.S.C. § 110(e)'), '1938-05-01'))
        self.assertIn('section was added (1994-10-22)', usc_cite.old_numbering(one('11 U.S.C. § 110(e)'), '1990-01-01'))
        self.assertIsNone(usc_cite.old_numbering(one('11 U.S.C. § 110(e)'), '2001-01-01'))
        self.assertIn('1976 edition', usc_cite.old_numbering(one('17 U.S.C. § 101 (1976 ed.)')))
        self.assertIn('1976 edition', usc_cite.old_numbering(one('11 U.S.C. (1976 ed.) § 103(a)')))
        self.assertIn('1976 edition', usc_cite.old_numbering(one('11 U.S.C. § 701 et seq. (1976)')))
        self.assertEqual(usc_cite.old_numbering(one('former 11 U.S.C. § 35')), 'cited as former')
        self.assertIsNone(usc_cite.old_numbering(one('35 U.S.C. § 101 (1976 ed.)'), '1980-01-01'))  # after the Patent Act of 1952
        self.assertIn('Patent Act', usc_cite.old_numbering(one('35 U.S.C. § 33'), '1950-01-01'))
        self.assertIn('first version in the record: 2020-02-19',
                      usc_cite.old_numbering(one('11 U.S.C. § 1182'), '2019-01-01', '2020-02-19', '2018-01-12'))


class ResolverForms(unittest.TestCase):
    """The resolver's own forms, read without a tree."""

    @classmethod
    def setUpClass(cls):
        import mcp_server
        cls.m = mcp_server

    def test_d7_reporter_variants(self):
        for text in ('22 Wn.2d 1', '100 F. (2d) 5', '50 Fed. 7', '20 South. 3', '30 Pac. 9', '410 U. S., 113', '8 Bush 587',
                     '1 Tyng 570', '3 Watts 12', '2004-NMCA-020', '2010-NMSC-001', '13 Wall. 335'):
            self.assertTrue(self.m.US_REPORTER.search(text), text)
        self.assertIsNone(self.m.US_REPORTER.search('11 U.S.C. § 1182'))

    def test_d3_not_dockets(self):
        for text in ('Pub. L. No. 95-521', 'H.R. Rep. No. 526', 'S. Rep. No. 989', 'Dkt. No. 355', 'ASBCA No. 4403',
                     'BCA No. 1551', 'Exec. Order No. 12', 'located at No. 516 North Clinton Street'):
            m = self.m.US_DOCKET.search(text)
            gone = m is None or self.m.NOT_DOCKET_BEFORE.search(text[max(0, m.start() - 40):m.start()]) \
                or self.m.STREET_AFTER.match(text, m.end())
            self.assertTrue(gone, text)
        m = self.m.US_DOCKET.search('Docket No. 77-440')
        self.assertTrue(m and not self.m.NOT_DOCKET_BEFORE.search('Docket '))
        self.assertEqual(self.m._dockets_of('Nos. 70-18, 70-40'), {'70-18', '70-40'})
        self.assertNotIn('701-8', self.m._dockets_of('No. 70-18'))  # the index key drops the hyphen; the check keeps it
        for q in ('1170253', 'No. 1389', '77-440', 'Docket No. 2:19-cv-01234', 'S219881'):
            self.assertTrue(self.m.DOCKET_QUERY.fullmatch(q), q)
        for q in ('1182', '11 U.S.C. § 1182', 'art. 415 k.c.', '4A_123/2024', 'II CSK 123/20'):
            self.assertIsNone(self.m.DOCKET_QUERY.fullmatch(q), q)

    def test_d6_state_statutes_are_named(self):
        got = {s['citation']: s['state'] for s in self.m.state_statutes(
            'Cal. Civ. Code § 1714(a); N.Y. Gen. Oblig. Law § 15-108; 735 ILCS 5/2-1001; O.C.G.A. § 9-3-33; '
            'Mass. Gen. Laws ch. 93A, § 9; Tex. Civ. Prac. & Rem. Code Ann. § 16.003(a); 42 Pa. C.S. § 5524.')}
        self.assertEqual(sorted(set(got.values())), ['California', 'Georgia', 'Illinois', 'Massachusetts', 'New York', 'Pennsylvania', 'Texas'])
        self.assertEqual(self.m.state_statutes('11 U.S.C. § 362 and 410 U.S. 113'), [])
        self.assertTrue(self.m.PUERTO_RICO.search('Tribunal Supremo de Puerto Rico'))
        self.assertTrue(self.m.PUERTO_RICO.search('31 L.P.R.A. sec. 5141'))

    def test_t7_git_grep_threads_are_capped(self):
        self.assertIn(f'--threads={self.m.GREP_THREADS}', self.m.grep_threads(['git', '-c', 'core.quotepath=off', 'grep', '-n', 'x']))
        self.assertEqual(self.m.grep_threads(['git', 'grep', '--threads=1', 'x']), ['git', 'grep', '--threads=1', 'x'])
        self.assertEqual(self.m.grep_threads(['git', 'log', '--grep=x']), ['git', 'log', '--grep=x'])
        self.assertLessEqual(self.m.GREP_THREADS, 8)

    def test_t5_case_law_has_a_time_budget(self):
        import time
        m = self.m
        try:
            m._call.deadline = 0.0
            self.assertFalse(m.caselaw_time_up())  # no deadline: no budget (the command line)
            m._call.deadline = time.monotonic() + m.GIT_TIMEOUT
            self.assertFalse(m.caselaw_time_up())
            m._call.deadline = time.monotonic() + (m.GIT_TIMEOUT - m.CASELAW_SECONDS) - 1
            self.assertTrue(m.caselaw_time_up())
            m._call.skipped = []
            m.carried(lambda: m.caselaw_skipped(2))()
            self.assertEqual(m._call.skipped, [2])
        finally:
            m._call.deadline = 0.0

    def test_t6_partial_dates_are_shown_as_such(self):
        self.assertEqual(self.m.date_precision({'decided': '1900-01'}), 'month')
        self.assertEqual(self.m.date_precision({'decided': '1900-01-01', 'decided_precision': 'year'}), 'year')
        self.assertIsNone(self.m.date_precision({'decided': '1900-01-05'}))
        self.assertIn('month only', self.m.day_shown('1900-01-01', 'month'))


def decision(name: str, text: str, **fm) -> str:
    head = ''.join(f'{k}: {json.dumps(v)}\n' for k, v in {'court': COURT, **fm}.items())
    return f'---\n{head}---\n\n# {name}\n\n## Opinion\n\n{text}\n'


class LinksOnATree(unittest.TestCase):
    """The tools over a small tree: a US Code record and one state's case law."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        (t.root / 'data').mkdir()
        (t.root / 'data' / 'us-reporters.json').write_text(json.dumps({'reporters': ['So. 2d', 'So. 3d', 'Ala.']}), encoding='utf-8')
        manifest = {'corpora': [
            {'path': LAW, 'name': 'United States Code', 'language': 'en', 'in_force_trailer': 'In-force', 'code': 'US'},
            {'path': CASES, 'name': 'Case law: Alabama', 'language': 'en', 'kind': 'judgments', 'in_force_trailer': 'In-force',
             'correction_trailer': 'Corrected', 'code': 'US'}]}
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        from tests.test_law_fixtures import run
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('2017 edition of the US Code', {'title-11/362.md': '(a) A petition operates as a stay.\n',
                                                   'title-11/110.md': '(a) In this section, petition preparers.\n',
                                                   'title-9/1.md': 'Maritime transactions.\n', 'title-9/10.md': 'Vacation.\n',
                                                   'title-9/16.md': 'Appeals.\n', 'title-9/4.md': 'Failure to arbitrate.\n'},
                   In_force='2018-01-12', Kind='baseline')
        law.commit('Pub. L. 116-54', {'title-11/1182.md': '(1) The term "debtor".\n'}, In_force='2020-02-19', Kind='law')
        c = t.corpus(CASES)

        def add(path, name, cite, day, text, **fm):
            c.commit(f'{COURT} {cite}', {path: decision(name, text, decided=fm.pop('decided', day), citations=[cite], **fm)},
                     Kind='court', In_force=day, Decided=day, Court=COURT, Citation=cite, **({'Docket': fm['docket']} if 'docket' in fm else {}))
        add(ALA9, 'Branch Bank v. Harrison', '1 Ala. 9', '1840-01-01', 'Affirmed.')
        add(ALA98, 'Other v. Party', '1 Ala. 98', '1840-01-01', 'Reversed.')
        add(MONTH, 'Month v. Only', '126 Ala. 1', '1900-01-01', 'Affirmed.', decided='1900-01', decided_precision='month')
        add(HUGHES1, 'Ex parte Hughes', '362 So. 2d 918', '1978-09-22', 'Writ granted.', docket='77-440')
        add(HUGHES2, 'Hughes v. Hughes', '372 So. 2d 845', '1979-06-08', 'Affirmed.', docket='77-440')
        add(DUP_KEPT, 'Same v. Decision', '560 So. 2d 1', '1990-02-02', 'Affirmed.')
        add(DUP_COPY, 'Same v. Decision', '560 So. 2d 1', '1990-02-02', 'Affirmed.')
        add(OLD, 'Old v. Record', '770 So. 2d 1', '2000-03-03', 'Under 11 U.S.C. § 362(a) the stay applies.')
        add(BARNHART, 'Barnhart v. Ingalls', '275 So. 3d 1112', '2018-11-21', 'Affirmed.', docket='1170253')
        rows = [{'decided': '2000-03-03', 'name': 'Old v. Record', 'court': COURT, 'citation': '770 So. 2d 1', 'url': 'u',
                 'how': '11 U.S.C. § 362(a)', 'mentions': 1, 'decision': OLD, 'law_record_from': '2018-01-12'}]
        index = 'reference\tpath\n' + ''.join(f'{r}\t{p}\n' for r, p in (
            ('1 Ala. 9', ALA9), ('1 Ala. 98', ALA98), ('126 Ala. 1', MONTH), ('362 So. 2d 918', HUGHES1), ('77-440', HUGHES1),
            ('372 So. 2d 845', HUGHES2), ('77-440', HUGHES2), ('560 So. 2d 1', DUP_KEPT), ('560 So. 2d 1', DUP_COPY),
            ('770 So. 2d 1', OLD), ('275 So. 3d 1112', BARNHART), ('1170253', BARNHART)))
        c.commit('Lexifina', {f'judgments/{LAW}/title-11/362.jsonl': ''.join(json.dumps(r) + '\n' for r in rows),
                              'decision-index.tsv': index,
                              'decision-relations.tsv': f'path\trelation\ttarget\tnote\n{DUP_COPY}\tsame-decision-as\t{DUP_KEPT}\tBankruptcy Reporter reprint\n',
                              'decision-dates.tsv': f'path\tdecided_as_given\tprecision\n{MONTH}\t1900-01\tmonth\n',
                              'corpus.json': json.dumps({'corpus': 'us/alabama/caselaw', 'kind': 'judgments', 'name': 'Case law: Alabama',
                                                         'in_force_trailer': 'In-force'})},
                 Kind='documentation')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def calls(self, *calls) -> list[dict]:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=json.dumps(calls),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout)
        for r in out:
            self.assertFalse(r['error'], r['text'])
        return out

    def test_us_code_citations_in_a_brief(self):
        (r,) = self.calls(('resolve_citations', {'text': 'USCA4 Appeal: 19-1 Pg: 3 of 4. 13 USCA11 Case. See 9 U.S.C. § 10(a)(4); '
                                                         '9 U.S.C. §§ 1-16; 11 U.S.C. § 110(e) (1976) (Act § 70e); 42 U.S.C. § 1983; '
                                                         'Cal. Civ. Code § 1714(a); Pub. L. No. 95-521; H.R. Rep. No. 526.'}))
        paths = [h['path'] for h in r['data']['citations']]
        self.assertEqual(paths, [f'{LAW}/title-9/10.md', f'{LAW}/title-9/1.md', f'{LAW}/title-42/1983.md'])
        self.assertNotIn(f'{LAW}/title-3/4.md', paths)  # D1
        self.assertNotIn(f'{LAW}/title-9/4.md', paths)  # D4
        self.assertIn('a range', r['data']['citations'][1]['note'])
        self.assertIn('no part of title 42', r['data']['citations'][2]['status'])
        (other,) = self.calls(('resolve_citations', {'text': 'Jurisdiction lies under 28 U.S.C. §§ 1331 and 1343(a)(3).'}))
        self.assertEqual([h['citation'] for h in other['data']['citations']], ['28 U.S.C. §§ 1331'])  # one answer per title not held
        self.assertIn('also cites § 1343 of title 28', other['data']['citations'][0]['note'])
        self.assertEqual([o['number_now_names'] for o in r['data']['old_numbering']], [f'{LAW}/title-11/110.md'])  # D2
        self.assertEqual([n['jurisdiction'] for n in r['data']['not_held']], ['California'])  # D6
        self.assertIn('global-law holds no California statutes', r['text'])
        self.assertNotIn('ambiguous', r['data'])  # D3: no docket read in a public law or a report

    def test_dockets_are_settled_by_the_words_around_them(self):
        near, bare, found = self.calls(('resolve_citations', {'text': 'Ex parte Hughes, Docket No. 77-440, 362 So. 2d 918 (Ala. 1978).'}),
                                       ('resolve_citations', {'text': 'It was argued as No. 77-440.'}),
                                       ('find_provision', {'query': '77-440'}))
        self.assertEqual({h['path'] for h in near['data']['citations']}, {f'{CASES}/{HUGHES1}'})
        self.assertEqual(bare['data']['citations'], [])
        self.assertEqual(bare['data']['ambiguous'][0]['count'], 2)
        self.assertIn('Give the court, the year or the reporter citation', bare['text'])
        self.assertIn(f'{CASES}/{HUGHES1}', found['text'])
        self.assertIn(f'{CASES}/{HUGHES2}', found['text'])
        # the decision cited elsewhere in the text by its reporter citation wins ("Roe v. Wade, 410 U.S. 113 ... argued as No. 70-18")
        (far,) = self.calls(('resolve_citations', {'text': 'Hughes v. Hughes, 372 So. 2d 845, settled it. ' + 'Much was said. ' * 20
                                                           + 'It had been argued as No. 77-440.'}))
        self.assertEqual({h['path'] for h in far['data']['citations']}, {f'{CASES}/{HUGHES2}'})

    def test_a_bare_docket_is_found_fast_and_never_by_heading(self):
        import time
        t0 = time.time()
        hit, miss = self.calls(('find_provision', {'query': '1170253'}), ('find_provision', {'query': '9999999'}))
        self.assertIn(f'{CASES}/{BARNHART}', hit['text'])
        self.assertIn('No decision', miss['text'])
        self.assertLess(time.time() - t0, 60)

    def test_t1_a_decision_is_not_yet_decided_before_its_day(self):
        before, after = self.calls(('resolve_citations', {'text': 'Barnhart v. Ingalls, No. 1170253 (Ala. 2018)', 'date': '2010-01-01'}),
                                   ('resolve_citations', {'text': 'Barnhart v. Ingalls, 275 So. 3d 1112 (Ala. 2018)', 'date': '2020-01-01'}))
        self.assertIn('not yet decided on 2010-01-01', before['data']['citations'][0]['status'])
        self.assertEqual(after['data']['citations'][0]['status'], 'court decision of 2018-11-21')

    def test_d5_the_same_decision_filed_twice_resolves_once(self):
        r, found = self.calls(('resolve_citations', {'text': 'Same v. Decision, 560 So. 2d 1 (Ala. 1990).'}),
                              ('find_provision', {'query': '560 So. 2d 1'}))
        self.assertEqual([h['path'] for h in r['data']['citations']], [f'{CASES}/{DUP_KEPT}'])
        self.assertNotIn(DUP_COPY, found['text'])

    def test_t2_law_details_reads_the_author_whole(self):
        a, b = self.calls(('law_details', {'law': f'{COURT} 1 Ala. 9', 'corpus': CASES, 'include_diffs': False}),
                          ('law_details', {'law': f'{COURT} 1 Ala. 9', 'include_diffs': False}))
        for r in (a, b):
            self.assertIn(ALA9, r['text'])
            self.assertNotIn(ALA98, r['text'])

    def test_t6_a_month_only_date_is_shown_as_such(self):
        read, cited = self.calls(('read_law', {'path': f'{CASES}/{MONTH}', 'include_text': False}),
                                 ('resolve_citations', {'text': '126 Ala. 1'}))
        self.assertIn('by its month only (1900-01)', read['text'])
        self.assertIn('1900-01 (month only', cited['data']['citations'][0]['status'])

    def test_d9_check_precedent_before_the_record(self):
        (r,) = self.calls(('check_precedent', {'path': f'{LAW}/title-11/362.md'}))
        self.assertIn('decided before the record starts for this provision (2018-01-12)', r['text'])
        self.assertNotIn('not in force in the record on that day', r['text'])

    def test_world_on_date_takes_a_jurisdiction(self):
        whole, cases = self.calls(('world_on_date', {'date': '2021-01-01', 'jurisdiction': LAW}),
                                  ('world_on_date', {'date': '2021-01-01', 'kind': 'judgments'}))
        self.assertIn(LAW, whole['text'])
        self.assertNotIn(CASES, whole['text'])
        self.assertIn(CASES, cases['text'])
        self.assertNotIn(f'{LAW}:', cases['text'])

    def test_present_sections_resolve_and_old_ones_say_why(self):
        r, gone = self.calls(('resolve_citations', {'text': '11 U.S.C. § 1182(1)', 'date': '2019-06-01'}),
                             ('resolve_citations', {'text': '11 U.S.C. § 1182(1)'}))
        self.assertIn('did not exist then', r['data']['citations'][0]['status'])
        self.assertEqual(gone['data']['citations'][0]['status'], 'in force')


if __name__ == '__main__':
    unittest.main()
