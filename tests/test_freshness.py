"""tools/freshness.py: corpus freshness rows, the status file and per-act lookups. Needs no corpus checked out.

  python -m unittest tests.test_freshness -v
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import describe  # noqa: E402
import freshness  # noqa: E402

D = dt.date(2026, 11, 6)
PIN = 'a' * 40


def entry(path='ro/national/acts', code='RO', **kw):
    return {'path': path, 'code': code, 'publisher': 'Official portal', **kw}


class CorpusRow(unittest.TestCase):
    def test_retrieval_within_threshold_is_current(self):
        r = freshness.corpus_row(entry(checked_on='2026-11-04', derived=['checked_on']), PIN, None, D)
        self.assertEqual((r['status'], r['method'], r['check_due']), ('current', 'source-retrieval', '2026-11-11'))

    def test_national_past_seven_days_is_stale(self):
        r = freshness.corpus_row(entry(checked_on='2026-10-28', derived=['checked_on']), PIN, None, D)
        self.assertEqual(r['status'], 'stale')

    def test_subnational_has_thirty_days(self):
        r = freshness.corpus_row(entry('br/ba/acts', 'BR-BA', checked_on='2026-10-28'), PIN, None, D)
        self.assertEqual((r['status'], r['method']), ('current', 'stated'))

    def test_corpus_threshold_overrides(self):
        r = freshness.corpus_row(entry(checked_on='2026-11-04', freshness_days=1), PIN, None, D)
        self.assertEqual(r['status'], 'stale')

    def test_never_checked_is_unverified(self):
        self.assertEqual(freshness.corpus_row(entry(), PIN, None, D)['status'], 'unverified')

    def test_newer_corpus_commit_is_pending(self):
        r = freshness.corpus_row(entry(checked_on='2026-11-05'), PIN, 'b' * 40, D)
        self.assertEqual(r['status'], 'pending-change')

    def test_own_freshness_wins_and_source_down_shows(self):
        own = {'checked_against_official_source': '2026-10-20', 'totals': {'acts': 10, 'by_status': {'current': 7}},
               'sources': [{'source': 'portal', 'unavailable_since': '2026-10-21'}]}
        r = freshness.corpus_row(entry(checked_on='2026-11-05', freshness=own), PIN, None, D)
        self.assertEqual((r['status'], r['method'], r['acts'], r['acts_current'], r['per_act']),
                         ('source-unavailable', 'act-checks', 10, 7, 'yes'))

    def test_acts_list_is_counted(self):
        self.assertEqual(freshness.corpus_row(entry(acts=['A', 'B']), PIN, None, D)['acts'], 2)

    def test_due_check_turns_stale_when_read_later(self):
        row = {'status': 'current', 'check_due': '2026-11-11'}
        self.assertEqual(freshness.status_on(row, dt.date(2026, 11, 12)), 'stale')
        self.assertEqual(freshness.status_on(row, dt.date(2026, 11, 11)), 'current')


class OwnFreshness(unittest.TestCase):
    """describe.own_freshness keeps only the summary of a corpus's own data/freshness.json (Romania's shape)."""

    def test_romania_shape(self):
        f = {'schema': 'ro-freshness/1', 'as_of': '2026-11-06', 'checked_against_official_source': '2026-11-06',
             'totals': {'acts': 214694, 'by_status': {'current': 171316, 'pending-change': 27637}},
             'sources': [{'source': 'Portalul legislativ', 'kinds': ['lege'], 'acts': 1,
                          'last_successful_check': '2026-11-06', 'unavailable_since': '2026-11-06'}]}
        got = describe.own_freshness(f)
        self.assertEqual(got['checked_against_official_source'], '2026-11-06')
        self.assertEqual(got['totals']['acts'], 214694)
        self.assertEqual(got['sources'], [{'source': 'Portalul legislativ', 'last_successful_check': '2026-11-06',
                                           'unavailable_since': '2026-11-06'}])

    def test_none(self):
        self.assertEqual(describe.own_freshness({}), {})
        self.assertEqual(describe.own_freshness({'as_of': '2026-11-06'}), {})


class OnDisk(unittest.TestCase):
    """write(), note(), act_row() and write_status() on a small repository with one corpus that publishes per-act
    freshness the way romania/national/acts does."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        git = lambda *a: subprocess.run(['git', '-C', str(self.root), *a], check=True, capture_output=True)  # noqa: E731
        git('init', '-q')
        git('config', 'user.email', 't@example.invalid')
        git('config', 'user.name', 't')
        corpus = 'ro/national/acts'
        own = {'checked_against_official_source': '2026-11-06', 'totals': {'acts': 1, 'by_status': {'pending-change': 1}},
               'sources': [{'source': 'portal', 'state': 'unavailable', 'unavailable_since': '2026-11-06T12:00:00Z'}]}
        manifest = {'corpora': [entry(corpus, freshness=own), entry('br/ba/acts', 'BR-BA', checked_on='2026-11-01')]}
        (self.root / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
        git('add', 'manifest.json')
        git('update-index', '--add', '--cacheinfo', f'160000,{PIN},{corpus}')
        git('commit', '-q', '-m', 'Add 2 corpora as submodules; point 0 at their current commits')
        # the corpus's own files, as a checkout would hold them
        c = self.root / corpus
        (c / 'data' / 'freshness' / 'lege').mkdir(parents=True)
        (c / 'data' / 'paths.json').write_text(json.dumps({'paths': {'codul-civil': 'lege/2009/287'}}), encoding='utf-8')
        (c / 'data' / 'freshness' / 'index.json').write_text(json.dumps(
            {'shards': [{'shard': 'lege/2009', 'kind': 'lege', 'file': 'data/freshness/lege/2009.csv'}]}),
            encoding='utf-8')
        with open(c / 'data' / 'freshness' / 'lege' / '2009.csv', 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['act', 'status', 'last_verified', 'check_due', 'method', 'newest_change',
                        'newest_change_date', 'change_in_repo', 'official_url'])
            w.writerow(['codul-civil', 'pending-change', '2026-11-05', '2026-11-12', 'amendment-search',
                        'legea-1-2026', '2026-11-01', 'no', 'https://example.invalid/109884'])

    def tearDown(self):
        self.tmp.cleanup()

    def test_write_and_read(self):
        s = freshness.write(self.root, today=D)
        self.assertEqual(s['totals']['corpora'], 2)
        rows = {r['path']: r for r in freshness.read_rows(self.root)}
        self.assertEqual(rows['ro/national/acts']['pinned'], PIN)
        self.assertEqual(rows['ro/national/acts']['per_act'], 'yes')
        self.assertEqual(rows['br/ba/acts']['pinned'], '')

    def test_act_row_and_note(self):
        freshness.write(self.root, today=D)
        a = freshness.act_row(self.root / 'ro/national/acts', 'lege/2009/287/art-1112.md')
        self.assertEqual((a['act'], a['folder']), ('codul-civil', 'lege/2009/287'))
        n = freshness.note('ro/national/acts/lege/2009/287/art-1112.md', D, self.root)
        self.assertIn('codul-civil: pending-change', n)
        self.assertIn('legea-1-2026', n)
        self.assertIn('https://example.invalid/109884', n)

    def test_note_without_act_falls_back_to_corpus(self):
        freshness.write(self.root, today=D)
        n = freshness.note('br/ba/acts/lei/1.md', D, self.root)
        self.assertTrue(n.startswith('br/ba/acts: current, last checked against Official portal on 2026-11-01'), n)

    def test_status(self):
        freshness.write(self.root, today=D)
        now = dt.datetime(2026, 11, 6, 14, 30, tzinfo=dt.timezone.utc)
        hb = {'at': '2026-11-06T14:20:38Z', 'result': 'pushed', 'last_push_at': '2026-11-06T14:20:38Z',
              'gate_held': {'x/national/acts': 'reason'}}
        st = freshness.write_status(hb, self.root, now)
        self.assertEqual(st['updates'], 'running')
        self.assertEqual(st['held_back'], ['x/national/acts'])
        self.assertEqual(st['published_last_24h']['corpora_added'], 2)
        self.assertEqual(st['official_sources_unavailable'][0]['corpus'], 'ro/national/acts')
        late = freshness.write_status(hb, self.root, now + dt.timedelta(hours=2))
        self.assertEqual(late['updates'], 'stalled')
        self.assertTrue((self.root / 'data' / 'status.json').exists())

    def test_one_failed_pass_is_still_running(self):
        freshness.write(self.root, today=D)
        now = dt.datetime(2026, 11, 6, 15, 20, tzinfo=dt.timezone.utc)
        hb = {'at': '2026-11-06T15:16:26Z', 'result': 'error', 'last_success_at': '2026-11-06T15:15:48Z'}
        st = freshness.write_status(hb, self.root, now)
        self.assertEqual((st['updates'], st['last_pass_ok']), ('running', False))

    def test_readme_lines_rewritten(self):
        (self.root / 'MONITORING.md').write_text('top\n<!-- status-summary -->\nold\n<!-- /status-summary -->\n',
                                                 encoding='utf-8')
        (self.root / 'monitoring').mkdir()
        (self.root / 'monitoring' / 'README.md').write_text(
            'top\n<!-- status-summary -->\nold\n<!-- /status-summary -->\n', encoding='utf-8')
        (self.root / 'FRESHNESS.md').write_text('<!-- freshness-summary -->\nold\n<!-- /freshness-summary -->\n',
                                                encoding='utf-8')
        freshness.write(self.root, today=D)
        now = dt.datetime(2026, 11, 6, 14, 30, tzinfo=dt.timezone.utc)
        freshness.write_status({'at': '2026-11-06T14:20:00Z', 'result': 'pushed', 'last_success_at':
                                '2026-11-06T14:20:00Z', 'last_push_at': '2026-11-06T14:20:00Z'}, self.root, now,
                               subjects=['Point submodules at the current country commits (7 corpora)'])
        mon = (self.root / 'MONITORING.md').read_text(encoding='utf-8')
        fre = (self.root / 'FRESHNESS.md').read_text(encoding='utf-8')
        self.assertIn('**Updates: running**: last published 2026-11-06 14:20 UTC', mon)
        self.assertIn('1 commit: 7 corpus updates', mon)
        self.assertIn('Official sources not answering | portal (`ro/national/acts`, since 2026-11-06)', mon)
        self.assertIn('corpora current** on 2026-11-06', fre)
        self.assertIn('| Subnational | 1 | 1 |', fre)
        page = (self.root / 'monitoring' / 'README.md').read_text(encoding='utf-8')
        self.assertIn('**Updates: running**: last published 2026-11-06 14:20 UTC', page)
        self.assertIn('([FRESHNESS.md](../FRESHNESS.md))', page)
        self.assertIn('([FRESHNESS.md](FRESHNESS.md))', mon)
        self.assertNotIn('old', mon + fre + page)

    def test_health(self):
        freshness.write(self.root, today=D)
        t = dt.datetime(2026, 11, 6, 14, 30, tzinfo=dt.timezone.utc)
        freshness.write_status({'at': '2026-11-06T14:20:00Z', 'result': 'pushed',
                                'last_success_at': '2026-11-06T14:20:00Z'}, self.root, t)
        problems = freshness.health(self.root, t + dt.timedelta(minutes=30))
        self.assertTrue(all(p.startswith('official source') for p in problems), problems)  # Romania's source is down
        late = freshness.health(self.root, t + dt.timedelta(hours=3))
        self.assertTrue(any('not publishing' in p for p in late), late)


if __name__ == '__main__':
    unittest.main()
