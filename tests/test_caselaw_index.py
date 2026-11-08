"""The case-law index (law.caselaw_index): every case-law corpus served, read once per pin and joined into one index per
set of pins, so that a call's cost does not grow with the number of case-law corpora. On a small tree built here: the US
Code (11 U.S.C. §§ 362 and 1182) and two case-law corpora, one committed out of the order its decisions were given and
with a decision of 1960 (git cannot date it), each with decision-index.tsv and a judgment overlay.

  python -m unittest tests.test_caselaw_index -v

Checked: the index gives the answers the per-corpus reads give (world_on_date, law.py world, list_jurisdictions,
check_precedent, what_else_changes, find_provision and resolve_citations by docket and reporter citation); a call reads
it without a git process per corpus (one git process reads the overlays of every corpus that holds one); a pin that
moves forward is read from its earlier record (only the new commits); and a decision appended after the index was
built is found once the index is built again for the new pins.
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
SC, CA = 'united-states/supreme-court/caselaw', 'united-states/ca9/caselaw'
FR = 'france/conseil-constitutionnel/caselaw'  # a decision filed as 09-100, the key of a US docket: never a US citation's answer
ART, STAY = f'{LAW}/title-11/1182.md', f'{LAW}/title-11/362.md'
CALL = ('import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
        'out = []\n'
        'for name, args in json.loads(sys.stdin.read()):\n'
        '    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", '
        '"params": {"name": name, "arguments": args}})["result"]\n'
        '    out.append({"error": r["isError"], "text": r["content"][0]["text"], "data": r.get("structuredContent", {})})\n'
        'print(json.dumps(out))\n')
# Counts the git processes started while the index answers, in a fresh process with the index built.
PROBE = ('import json, subprocess, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import law\n'
         'law.manifest(); law.caselaw_index("no")\n'  # the tree's own reads, once, before counting
         'started = []\n'
         'popen = subprocess.Popen\n'
         'class P(popen):  # subprocess.run starts its process through Popen too\n'
         '    def __init__(self, cmd, *a, **k):\n'
         '        started.append(cmd[:3]); super().__init__(cmd, *a, **k)\n'
         'subprocess.Popen = P\n'
         'cases = [c["path"] for c in law.manifest()["corpora"] if law.is_caselaw(c)]\n'
         'latest = law.latest_decisions("2024-01-01", cases)\n'
         'cands = law.bloom_candidates(law.decision_key("560 U.S. 100"))\n'
         'rows = law.caselaw_overlay_rows(["united-states/federal/usc/title-11/362"])\n'
         'n_lookup = len(started)\n'
         'texts = law.read_blobs_of(rows)\n'
         'print(json.dumps({"lookup": n_lookup, "read": len(started) - n_lookup, "latest": latest, "cands": [c for c, _ in cands],\n'
         '                  "rows": rows, "texts": len(texts), "started": started}))\n')


def decision(court: str, title: str, text: str) -> str:
    return f'---\ncourt: "{court}"\n---\n\n# {title}\n\n## Majority\n\n{text}\n'


class CaseLawIndex(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT))
        from tests.test_law_fixtures import Tree, run
        cls.git = staticmethod(run)
        t = cls.t = Tree()
        for name in ('mcp_server.py', 'countries.py', 'freshness.py'):
            shutil.copy(ROOT / 'tools' / name, t.root / 'tools' / name)
        (t.root / 'data').mkdir()
        (t.root / 'jurisdiction.json').write_text('{"name": "fixture", "jurisdictions": []}', encoding='utf-8')
        cases = {'kind': 'judgments', 'language': 'en', 'in_force_trailer': 'In-force', 'correction_trailer': 'Corrected', 'code': 'US'}
        manifest = {'corpora': [
            {'path': LAW, 'name': 'United States Code', 'language': 'en', 'in_force_trailer': 'In-force', 'code': 'US'},
            {'path': SC, 'name': 'Case law: Supreme Court of the United States', **cases},
            {'path': CA, 'name': 'Case law: Court of Appeals for the Ninth Circuit', **cases}]}  # FR: pinned, not listed
        (t.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        run('add', 'jurisdiction.json', 'data', cwd=t.root)
        law = t.corpus(LAW)
        law.commit('Pub. L. 95-598', {'title-11/362.md': '(a) A petition operates as a stay.\n'}, In_force='1979-10-01', Kind='law')
        law.commit('Pub. L. 116-54', {'title-11/1182.md': '(1) The term "debtor" means a small business debtor.\n'},
                   In_force='2020-02-19', Kind='law')
        cls.v2022 = law.commit('Pub. L. 117-151', {'title-11/1182.md': '(1) The term "debtor" means a person engaged in '
                                                                      'commercial or business activities.\n'},
                               In_force='2022-06-21', Kind='law')
        sc, court = t.corpus(SC), 'Supreme Court of the United States'
        f = 'decisions/supreme-court-of-the-united-states'
        cls.sc_paths = [f'{f}/1960/361-U-S-1.md', f'{f}/2010/560-U-S-100.md', f'{f}/2022/596-U-S-300.md', f'{f}/2014/573-U-S-500.md']
        for path, (cite, day, title) in zip(cls.sc_paths, [('361 U.S. 1', '1960-01-11', 'Old v. Case'),
                                                           ('560 U.S. 100', '2010-05-05', 'Smith v. Jones'),
                                                           ('596 U.S. 300', '2022-03-03', 'In re Debtor'),
                                                           ('573 U.S. 500', '2014-05-05', 'Late v. Backfill')]):
            # the last is a backfill: an older decision committed after a newer one
            sc.commit(f'{court} {cite}', {path: decision(court, title, f'Decided {day}.')}, Kind='court', In_force=day,
                      Decided=day, Court=court, Citation=cite)
        sc.commit(f'{court} 560 U.S. 100', {cls.sc_paths[1]: decision(court, 'Smith v. Jones', 'Corrected.')},
                  Kind='correction', In_force='2023-01-01', Corrected='2023-01-01')
        url = 'https://static.case.law/'
        sc_rows = {f'judgments/{LAW}/title-11/1182.jsonl': [
            {'decided': '2010-05-05', 'name': 'Smith v. Jones', 'court': court, 'citation': '560 U.S. 100', 'url': url + '1',
             'decision': cls.sc_paths[1]},
            {'decided': '2022-03-03', 'name': 'In re Debtor', 'court': court, 'citation': '596 U.S. 300', 'url': url + '3',
             'decision': cls.sc_paths[2], 'law_commit': cls.v2022}],
            f'judgments/{LAW}/title-11/362.jsonl': [
            {'decided': '2010-05-05', 'name': 'Smith v. Jones', 'court': court, 'citation': '560 U.S. 100', 'url': url + '1',
             'decision': cls.sc_paths[1]}]}
        sc.commit('Lexifina', {**{p: ''.join(json.dumps(r) + '\n' for r in rows) for p, rows in sc_rows.items()},
                               'decision-index.tsv': 'reference\tpath\n560 U.S. 100\t' + cls.sc_paths[1] + '\n09-100\t'
                               + cls.sc_paths[1] + '\n596 U.S. 300\t' + cls.sc_paths[2] + '\n'}, Kind='documentation')
        ca, ccourt = t.corpus(CA), 'United States Court of Appeals for the Ninth Circuit'
        g = 'decisions/united-states-court-of-appeals-for-the-ninth-circuit'
        cls.ca_paths = [f'{g}/2018/900-F-3d-1.md', f'{g}/2019/920-F-3d-2.md']
        for path, (cite, day) in zip(cls.ca_paths, [('900 F.3d 1', '2018-07-01'), ('920 F.3d 2', '2019-03-04')]):
            ca.commit(f'{ccourt} {cite}', {path: decision(ccourt, 'In re Stay', 'The automatic stay applies.')}, Kind='court',
                      In_force=day, Decided=day, Court=ccourt, Citation=cite)
        # A long overlay file (2,500 rows, more than SUM_ROWS): the index keeps its summary, which check_precedent reads
        # when the rows are many (test_4).
        many = ''.join(json.dumps({'decided': f'{2000 + i % 20}-{1 + i % 12:02d}-{1 + i % 28:02d}', 'name': f'Case {i}', 'court': ccourt,
                                   'citation': f'{i} F.3d {i}', 'url': f'{url}m{i}'}) + '\n' for i in range(2500))
        ca.commit('Lexifina', {f'judgments/{LAW}/title-11/362.2018.jsonl': json.dumps(
            {'decided': '2018-07-01', 'name': 'In re Stay', 'court': ccourt, 'citation': '900 F.3d 1', 'url': url + '9',
             'decision': cls.ca_paths[0]}) + '\n', f'judgments/{LAW}/title-11/1182.2019.jsonl': many,
            'decision-index.tsv': 'reference\tpath\n900 F.3d 1\t' + cls.ca_paths[0] + '\n'},
            Kind='documentation')
        fr = t.corpus(FR)
        fr.commit('Conseil constitutionnel 09-100', {'decisions/cc/2009/09-100.md': decision('Conseil constitutionnel', 'Décision 09-100', 'Texte.')},
                  Kind='court', In_force='2009-12-29', Decided='2009-12-29', Court='Conseil constitutionnel')
        t.pin()

    @classmethod
    def tearDownClass(cls):
        cls.t.close()

    def calls(self, *calls) -> list[dict]:
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=json.dumps(calls),
                              capture_output=True, encoding='utf-8', timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return json.loads(done.stdout)

    def cli(self, *args) -> str:
        out, err, code = self.t.cli(*args)
        self.assertEqual(code, 0, err)
        return out

    def store(self) -> Path:
        return self.t.root / '.git' / 'global-law-cache'

    def drop_index(self) -> None:
        for p in self.store().glob('cl-*'):
            p.unlink()
        for p in self.store().glob('decisions-*'):
            p.unlink()

    CHECKS = [('world_on_date', {'date': '2024-01-01'}), ('world_on_date', {'date': '1965-01-01'}),
              ('world_on_date', {'date': '2015-01-01'}), ('list_jurisdictions', {}),
              ('check_precedent', {'path': ART, 'date': '2024-01-01'}), ('check_precedent', {'path': STAY, 'date': '2024-01-01'}),
              ('what_else_changes', {'path': STAY, 'date': '2024-01-01'}),
              ('find_provision', {'query': '560 U.S. 100'}), ('find_provision', {'query': 'No. 09-100'}),
              ('find_provision', {'query': '900 F.3d 1'}), ('find_provision', {'query': '999 U.S. 999'}),
              ('resolve_citations', {'text': 'See 560 U.S. 100 and 900 F.3d 1; 11 U.S.C. § 362(a).', 'date': '2024-01-01'})]

    def test_1_index_gives_the_answers_of_the_reads_it_replaces(self):
        self.drop_index()
        before = self.calls(*self.CHECKS)
        world_before = self.cli('world', '1965-01-01') + self.cli('world', '2024-01-01')
        self.assertFalse(list(self.store().glob('cl-set-*')), 'a call builds no index: the update step does')
        built = self.cli('caselaw-index')
        self.assertIn('case-law index: 3 corpora', built)
        self.assertEqual(len(list(self.store().glob('cl-set-v2-*.json'))), 1)
        after = self.calls(*self.CHECKS)
        for (name, args), b, a in zip(self.CHECKS, before, after):
            self.assertEqual(b['text'], a['text'], f'{name} {args}')
        self.assertEqual(world_before, self.cli('world', '1965-01-01') + self.cli('world', '2024-01-01'))
        texts = {f"{n} {json.dumps(a)}": r['text'] for (n, a), r in zip(self.CHECKS, after)}
        self.assertIn('361 U.S. 1 (latest decision), given 1960-01-11', texts['world_on_date {"date": "1965-01-01"}'])  # 1960: read from its trailer, not git's date
        self.assertIn('given 2022-03-03', texts['world_on_date {"date": "2024-01-01"}'])  # not the backfill committed later
        self.assertIn('573 U.S. 500 (latest decision), given 2014-05-05', texts['world_on_date {"date": "2015-01-01"}'])
        self.assertIn('In re Stay', texts[f'check_precedent {json.dumps({"path": STAY, "date": "2024-01-01"})}'])  # a .2018.jsonl file
        self.assertIn(self.sc_paths[1], texts['find_provision {"query": "No. 09-100"}'])
        self.assertNotIn(FR, texts['find_provision {"query": "No. 09-100"}'])  # a US docket names US decisions only
        self.assertIn('No decision', texts['find_provision {"query": "999 U.S. 999"}'])

    def test_2_a_call_starts_no_git_process_per_corpus(self):
        self.cli('caselaw-index')
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c', PROBE], cwd=self.t.root, capture_output=True, encoding='utf-8',
                              timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        got = json.loads(done.stdout)
        self.assertEqual(got['lookup'], 0, 'latest decisions, Bloom filter and overlay rows are read without git')
        self.assertEqual(got['read'], 1, f"one git process reads the overlays of both corpora: {got['started']}")
        self.assertEqual(sorted(c for c, _ in got['rows']), [CA, SC])
        self.assertEqual(got['texts'], 2)
        self.assertEqual(got['latest'][SC][1], '2022-03-03')
        self.assertEqual(got['latest'][CA][1], '2019-03-04')
        self.assertIn(SC, got['cands'])

    def test_3_a_moved_pin_reads_only_its_new_commits(self):
        self.cli('caselaw-index')
        ca = self.t.corpora[CA]
        old_pin = self.git('rev-parse', 'HEAD', cwd=ca.path)
        ccourt = 'United States Court of Appeals for the Ninth Circuit'
        new = 'decisions/united-states-court-of-appeals-for-the-ninth-circuit/2025/130-F-4th-7.md'
        ca.commit(f'{ccourt} 130 F.4th 7', {new: decision(ccourt, 'In re Newer', 'Stayed.')}, Kind='court',
                  In_force='2025-02-03', Decided='2025-02-03', Court=ccourt, Citation='130 F.4th 7')
        ca.commit('Lexifina', {f'judgments/{LAW}/title-11/362.2025.jsonl': json.dumps(
            {'decided': '2025-02-03', 'name': 'In re Newer', 'court': ccourt, 'citation': '130 F.4th 7', 'decision': new}) + '\n',
            'decision-index.tsv': 'reference\tpath\n900 F.3d 1\t' + self.ca_paths[0] + '\n24-777\t' + new + '\n'},
            Kind='documentation')
        self.t.pin()
        try:
            stale = self.calls(('find_provision', {'query': '130 F.4th 7'}))[0]['text']
            self.assertIn('In re Newer', stale)  # before the update step: each corpus read as before, at its new pin
            self.cli('caselaw-index')
            pin = self.git('rev-parse', 'HEAD', cwd=ca.path)
            rec = json.loads(next(self.store().glob(f'cl-v2-united-states~ca9~caselaw-{pin[:12]}.json')).read_text(encoding='utf-8'))
            self.assertEqual(rec.get('from'), old_pin, 'read from the record of the earlier pin')
            self.assertEqual(rec['files'], 3)
            full = self.store() / f'decisions-{pin}.tsv'
            self.assertIn(b'24777\t', full.read_bytes())
            got = self.calls(('find_provision', {'query': '130 F.4th 7'}), ('find_provision', {'query': 'No. 24-777'}),
                             ('world_on_date', {'date': '2025-12-31'}), ('check_precedent', {'path': STAY, 'date': '2026-01-01'}))
            self.assertIn(new, got[0]['text'])
            self.assertIn(new, got[1]['text'])
            self.assertIn('130 F.4th 7 (latest decision), given 2025-02-03', got[2]['text'])
            self.assertIn('In re Newer', got[3]['text'])
            self.assertIn('In re Stay', got[3]['text'])
            # the same answers as a full read of the new pin
            for p in self.store().glob('cl-v2-united-states~ca9~*'):
                p.unlink()
            for p in self.store().glob('cl-set-*'):
                p.unlink()
            full.unlink()
            self.cli('caselaw-index')
            again = self.calls(('find_provision', {'query': '130 F.4th 7'}), ('find_provision', {'query': 'No. 24-777'}),
                               ('world_on_date', {'date': '2025-12-31'}), ('check_precedent', {'path': STAY, 'date': '2026-01-01'}))
            self.assertEqual([r['text'] for r in got], [r['text'] for r in again])
        finally:
            pass

    def test_6_state_reporters_and_dockets(self):
        # The states' highest courts (CAP): official reports, West's regional reporters, a state docket number.
        sys.path.insert(0, str(ROOT / 'tools'))
        import mcp_server
        for cite in ('123 Nev. 105', '1 Cal. 5th 233', '57 Cal. 2d 1', '465 P.2d 133', '159 P.3d 1086', '30 N.Y.3d 1', '1 N.Y.2d 5',
                     '90 N.E.3d 1', '310 A.2d 1', '25 A.3d 1', '1 Del. 1', '470 Mass. 1',
                     '6 Dakota 494', '2 Am. Samoa 2d 100', '57 Ill. App. 3d 12', '12 So. 2d 3', '100 B.R. 1', '572 S.W.3d 461', '12 N.E.2d 4', '5 N.Y.S.2d 3'):  # every CAP reporter (data/us-reporters.json)
            self.assertTrue(mcp_server.US_REPORTER.fullmatch(cite), cite)
        for docket in ('No. 61308', 'No. S221852', 'No. 70-18', 'No. 389, 2008', 'No. 2019-775'):
            self.assertTrue(mcp_server.US_DOCKET.fullmatch(docket), docket)
        self.assertFalse(mcp_server.US_DOCKET.fullmatch('No. 12'))

    def test_5_list_jurisdictions_by_jurisdiction_and_the_whole_manifest(self):
        got = self.calls(('list_jurisdictions', {'jurisdiction': 'france'}), ('list_jurisdictions', {}))
        self.assertIn(FR, got[0]['text'])
        self.assertNotIn(SC, got[0]['text'])
        self.assertIn(SC, got[1]['text'])
        done = subprocess.run([sys.executable, '-X', 'utf8', '-c',
                               'import json, sys; sys.path.insert(0, "tools"); sys.dont_write_bytecode = True; import mcp_server\n'
                               'r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "resources/read", '
                               '"params": {"uri": "global-law://manifest.json"}})\n'
                               'print(r["result"]["contents"][0]["text"])'], cwd=self.t.root, capture_output=True, encoding='utf-8', timeout=300)
        self.assertIn(FR, done.stdout, 'a corpus pinned after manifest.json was written is in the manifest resource')

    def test_4_a_long_overlay_is_counted_from_its_summary(self):
        # With the rows counted rather than read (GLOBAL_LAW_JUDGMENTS_COUNTED below the 2,500 rows), check_precedent and
        # what_else_changes give the same answer from the index's summary of the long file as from the file itself.
        checks = [('check_precedent', {'path': ART, 'date': '2024-01-01'}), ('check_precedent', {'path': ART, 'date': '2010-06-01'}),
                  ('check_precedent', {'path': ART, 'date': '2024-01-01', 'max_results': 400}),
                  ('what_else_changes', {'path': ART, 'date': '2024-01-01'})]

        def run(*calls):
            import os
            done = subprocess.run([sys.executable, '-X', 'utf8', '-c', CALL], cwd=self.t.root, input=json.dumps(calls),
                                  capture_output=True, encoding='utf-8', timeout=300,
                                  env={**os.environ, 'GLOBAL_LAW_JUDGMENTS_COUNTED': '1000'})
            self.assertEqual(done.returncode, 0, done.stderr)
            return [r['text'] for r in json.loads(done.stdout)]
        self.drop_index()
        read = run(*checks)
        self.cli('caselaw-index')
        sums = ''.join(p.read_text(encoding='utf-8') for p in self.store().glob('cl-set-v2-*.sums.tsv'))
        self.assertIn('"rows": 2500', sums)
        self.assertEqual(read, run(*checks))
        self.assertIn('decisions are recorded; the latest 50 are checked', read[0])


if __name__ == '__main__':
    unittest.main()
