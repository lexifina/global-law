"""tools/check_corpus.py's pin diff of data/acts.json (act_ends_lost), on small corpora built here, and on
spain-law's real history when a clone of it is named in $SPAIN_LAW_GIT.

  python -m unittest tests.test_check_corpus -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(HERE / 'tests'))
try:
    import check_corpus
    from test_law_fixtures import Corpus, run
finally:
    del sys.path[:2]

UNTIL = '2026-11-05'


def acts(*rows: dict) -> str:
    return json.dumps({'acts': list(rows)}, indent=1)


def row(path: str, **kw) -> dict:
    return {'path': path, 'status': 'in force', 'repealed': None, 'expired': None, **kw}


class PinDiff(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix='gl-pin-diff-'))
        self.addCleanup(self.close)
        c = self.c = Corpus(self.d / 'repo')
        (c.path / 'REPRODUCE.md').write_text('x', encoding='utf-8')
        (c.path / 'corpus.json').write_text(json.dumps({
            'corpus': 'xx/national/acts', 'name': 'XX', 'language': 'en', 'history_from': '2000-01-01',
            'record_to': '2026-11-01', 'in_force_trailer': 'In-force'}), encoding='utf-8')
        run('add', '-A', cwd=c.path)
        c.commit('Act 1 of 2000', {'a/s1.md': 'A\n', 'b/s1.md': 'B\n', 'c/s1.md': 'C\n'}, In_force='2000-01-01')
        self.rows = [row('a', status='expired'), row('b', status='repealed', repealed='2010-05-01'), row('c')]
        self.pin = c.commit('Lexifina', {'data/acts.json': acts(*self.rows)}, Kind='documentation')

    def close(self):
        def writable(func, path, _):  # git writes its objects read-only, which Windows will not delete
            os.chmod(path, 0o700)
            func(path)
        shutil.rmtree(self.d, onerror=writable)

    def fatal(self) -> list[str]:
        return check_corpus.act_ends_lost(self.c.path, self.pin)

    def write(self, *rows: dict, **trailers) -> str:
        return self.c.commit('Lexifina', {'data/acts.json': acts(*rows)}, Kind='documentation', **trailers)

    def test_pin_diff_fails_when_act_ends_are_lost(self):
        # spain-law d4839ce: "expired" (no day) became "as captured", a status readers do not know.
        self.write(row('a', status='as captured', vigencia_agotada='S'), *self.rows[1:])
        fatal = [f for f in check_corpus.problems(self.c.path, UNTIL, self.pin)[0] if 'data/acts.json' in f]
        self.assertEqual(len(fatal), 1, fatal)
        self.assertEqual(fatal, self.fatal())
        self.assertIn('1 act(s) that readers end at the pinned commit', fatal[0])
        self.assertIn('1 no longer ended; e.g. a)', fatal[0])
        self.assertIn('Act-ends-reviewed', fatal[0])
        # Not without a pin, and not at the pin itself.
        self.assertFalse([f for f in check_corpus.problems(self.c.path, UNTIL)[0] if 'data/acts.json' in f])

    def test_a_row_added_passes(self):
        self.write(*self.rows, row('d', status='repealed', repealed='2020-01-01'))
        self.assertEqual(self.fatal(), [])

    def test_a_restored_end_passes(self):
        self.write(row('a', status='as captured'), *self.rows[1:])
        self.write(*self.rows)  # spain-law 645ca52 / 57854db: the status set back
        self.assertEqual(self.fatal(), [])

    def test_a_lost_day_or_a_dropped_row_fails(self):
        self.write(self.rows[0], row('b', status='repealed', repealed=None), self.rows[2])
        fatal = self.fatal()
        self.assertTrue(fatal and '1 no longer from a day; e.g. b)' in fatal[0], fatal)
        self.write(self.rows[2])
        fatal = self.fatal()
        self.assertTrue(fatal and '2 no longer ended' in fatal[0], fatal)

    def test_a_later_end_day_is_not_a_loss(self):
        self.write(self.rows[0], row('b', status='repealed', repealed='2011-05-01'), self.rows[2])
        self.assertEqual(self.fatal(), [])

    def test_the_trailer_excuses_only_its_own_commit(self):
        self.write(row('a'), *self.rows[1:], Act_ends_reviewed='BOE lists act a as in force again (BOE-A-1)')
        self.assertEqual(self.fatal(), [])
        self.write(row('a'), row('b', status='as captured', repealed='2010-05-01'), self.rows[2])
        fatal = self.fatal()  # readers do not know the status, but end b by its day: still ended
        self.assertEqual(fatal, [])
        self.write(row('a'), row('b', status='in force', repealed='2010-05-01'), self.rows[2])
        fatal = self.fatal()  # an in-force status hides the day: b is no longer ended, and nothing says why
        self.assertTrue(fatal and '1 no longer ended; e.g. b)' in fatal[0], fatal)

    def test_the_trailer_must_be_in_the_trailer_block(self):
        self.c.commit('Lexifina', {'data/acts.json': acts(row('a'), *self.rows[1:])},
                      Kind='documentation\n\nAct-ends-reviewed: written in the body, not as a trailer\n\nMore text.')
        self.assertTrue(self.fatal())


SPAIN = os.environ.get('SPAIN_LAW_GIT')


class RecordStandard(unittest.TestCase):
    """The record standard's refusals (audit rows 77-80): what builders write their own way and readers would have to
    guess is refused ("refused (<code>): ...", exit 3), so the pointer loop does not move the pin. Commit checks look
    at the commits added since the pin; what is already pinned only warns, as the history cannot change."""

    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix='gl-standard-'))
        self.addCleanup(self.close)

    def close(self):
        def writable(func, path, _):
            os.chmod(path, 0o700)
            func(path)
        shutil.rmtree(self.d, onerror=writable)

    def corpus(self, corpus_json: dict | None = None, repo_json: dict | None = None) -> Corpus:
        c = Corpus(self.d / f'repo{len(list(self.d.iterdir()))}')
        files = {'REPRODUCE.md': 'x\n'}
        if corpus_json is not None:
            files['corpus.json'] = json.dumps({'corpus': 'xx/national/acts', 'name': 'XX', 'language': 'en',
                                               'history_from': '2000-01-01', 'record_to': '2026-11-01',
                                               'in_force_trailer': 'In-force', 'citation': {
                                                   'file': '([a-z0-9-]+)/s([0-9]+)\\.md', 'cites': 's {n}'},
                                               **corpus_json})
        if repo_json is not None:
            files['data/repo.json'] = json.dumps(repo_json)
            files['jurisdiction.json'] = json.dumps({'name': 'XX', 'code': 'XX'})
        c.commit('Lexifina', files, Kind='documentation')
        return c

    def refusals(self, c: Corpus, pin: str | None = None) -> tuple[list[str], list[str]]:
        fatal, warn = check_corpus.problems(c.path, UNTIL, pin)
        return [f for f in fatal if check_corpus.is_refusal(f)], warn

    # Row 77: an unknown Kind, and a law credited to the publisher, are refused when new; pinned ones only warn.
    def test_kind_and_publisher_refusals(self):
        c = self.corpus({'history': 'in-force', 'publisher': 'Register'})
        c.commit('Act 1 of 2000', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='law')
        pin = c.commit('Register', {'a/s1.md': 'two\n'}, In_force='2001-01-01', Kind='Wibble')
        refused, warn = self.refusals(c)
        self.assertTrue(any(f.startswith('refused (kind):') and "'wibble' (1)" in f for f in refused), refused)
        self.assertTrue(any(f.startswith('refused (publisher):') and "'Register'" in f for f in refused), refused)
        refused, warn = self.refusals(c, pin)  # already pinned: warnings
        self.assertEqual(refused, [])
        self.assertTrue(any('already pinned' in w and 'wibble' in w for w in warn), warn)
        c.commit('Register', {'a/s1.md': 'three\n'}, In_force='2002-01-01', Kind='Amend')
        refused, warn = self.refusals(c, pin)
        self.assertEqual([f.split(':')[0] for f in refused], ['refused (publisher)'], refused)
        self.assertIn(f'added since the pin {pin[:7]}', refused[0])
        # Kinds readers know, credited to laws, pass.
        ok = self.corpus({'history': 'in-force'})
        ok.commit('Act 1 of 2000', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='AsMade')
        ok.commit('Register', {'a/s1.md': 'two\n'}, In_force='2001-01-01', Kind='Unattributed')
        self.assertEqual(self.refusals(ok)[0], [])

    # Row 78: a corpus that says its versions were replayed, though each names the publisher's own compilation.
    def test_history_label_replayed_with_compilations(self):
        c = self.corpus({'history': 'replayed'})
        c.commit('Act 1 of 2000', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='law', Compilation_id='C2000')
        c.commit('Act 2 of 2001', {'a/s1.md': 'two\n'}, In_force='2001-01-01', Kind='law', Compilation_id='C2001')
        refused, _ = self.refusals(c)
        self.assertEqual(len(refused), 1, refused)
        self.assertTrue(refused[0].startswith('refused (history):'))
        self.assertIn("declare history 'in-force'", refused[0])
        c.commit('Act 3 of 2002', {'a/s1.md': 'three\n'}, In_force='2002-01-01', Kind='law')  # one replayed version
        self.assertEqual(self.refusals(c)[0], [])
        bad = self.corpus({'history': 'compiled'})
        bad.commit('Act 1 of 2000', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='law')
        self.assertTrue(any(f.startswith("refused (history): corpus.json history 'compiled'") for f in self.refusals(bad)[0]))

    # Row 79: data/repo.json may declare the history too; in an as-enacted record a law is not the publisher's
    # starting text.
    def test_as_enacted_declared_in_repo_json(self):
        c = self.corpus(repo_json={'name': 'XX', 'publisher': 'JDIH X', 'history': 'as-enacted'})
        pin = c.commit('JDIH X', {'perda-2016-012/pasal-001.md': 'Pasal 1\n'}, In_force='2016-12-05', Kind='publisher')
        refused, _ = self.refusals(c)
        self.assertTrue(any(f.startswith('refused (as-enacted):') and '(data/repo.json)' in f for f in refused), refused)
        self.assertEqual(self.refusals(c, pin)[0], [])
        c.commit('Perda Lamongan 4/2026', {'perda-2026-004/pasal-001.md': 'Pasal 1\n'}, In_force='2026-04-23', Kind='law')
        self.assertEqual(self.refusals(c, pin)[0], [])  # credited to the law itself
        odd = self.corpus(repo_json={'name': 'XX', 'history': 'publisher'})
        odd.commit('Act 1', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='law')
        self.assertTrue(any(f.startswith("refused (history): data/repo.json history 'publisher'")
                            for f in self.refusals(odd)[0]))

    # Row 80: a listing page's view and download counters, or its posting date, in an act folder's name.
    def test_path_furniture(self):
        c = self.corpus({'history': 'as-enacted'})
        c.commit('Perda 4/2021', {'perda-2021-004-kawasan-tanpa-rokok-18-april-2022-tahun-2021-137-views-105-downloads/'
                                  'pasal-001.md': 'one\n'}, In_force='2021-01-01', Kind='law')
        pin = c.commit('Perda 14/2015', {'perda-2015-014-pedagang-kaki-lima-6-november-2025-tahun/pasal-001.md': 'x\n'},
                       In_force='2016-03-15', Kind='law')
        for p in (None, pin):  # a folder at HEAD: refused until it is renamed
            refused, _ = self.refusals(c, p)
            self.assertEqual([f.split(':')[0] for f in refused], ['refused (path)'], refused)
            self.assertIn('2 folder(s)', refused[0])
        for name in ('perda-2019-008-badan-usaha-milik-desa-10-november-2020-tahun-2019-73-views-72',
                     'perda-2021-015-penanggulangan-bencana-21-november', 'x-lihat-unduh'):
            self.assertTrue(check_corpus.PATH_FURNITURE.search(name), name)
        for name in ('perda-2021-004-kawasan-tanpa-rokok', 'ley-de-1-de-enero-de-2000', 'act-1-of-may-2000',
                     'review-of-views-2020', 'BOE-A-1996-4718', 'perda-2026-002-infrastruktur-pasif-telekomunikasi-tahun'):
            self.assertFalse(check_corpus.PATH_FURNITURE.search(name), name)

    def test_exit_code_says_refused(self):
        c = self.corpus({'history': 'replayed'})
        c.commit('Act 1 of 2000', {'a/s1.md': 'one\n'}, In_force='2000-01-01', Kind='law', Compilation_id='C2000')
        done = subprocess.run([sys.executable, '-X', 'utf8', str(HERE / 'tools' / 'check_corpus.py'), str(c.path),
                               '--pin', c.commit('Lexifina', {'README.md': 'x\n'}, Kind='documentation'),
                               '--until', UNTIL], capture_output=True, encoding='utf-8')
        self.assertEqual(done.returncode, check_corpus.EXIT_REFUSED, done.stdout + done.stderr)
        self.assertIn('FAIL: refused (history):', done.stdout)


@unittest.skipUnless(SPAIN, 'set SPAIN_LAW_GIT to a clone of lexifina/spain-law (blob-less is enough)')
class SpainHistory(unittest.TestCase):
    """The regression that motivated the check, on the real commits: the gate must have held d4839ce."""

    def ends_lost(self, pin: str, head: str) -> list[str]:
        sha = lambda c: run('rev-parse', f'{c}^{{commit}}', cwd=SPAIN)
        return check_corpus.act_ends_lost(Path(SPAIN), sha(pin), sha(head))

    def test_d4839ce_fails(self):
        lost = self.ends_lost('ee54e80', 'd4839ce')
        self.assertTrue(lost and '834 act(s)' in lost[0], lost)

    def test_the_fixes_pass(self):
        self.assertEqual(self.ends_lost('d4839ce', '4d77ced'), [])
        self.assertEqual(self.ends_lost('4cc99eb', '57854db'), [])
        self.assertEqual(self.ends_lost('ee54e80', '57854db'), [])

    def test_the_live_pin_step_still_lost_418(self):
        lost = self.ends_lost('ee54e80', '4cc99eb')
        self.assertTrue(lost and '418 act(s)' in lost[0], lost)


if __name__ == '__main__':
    unittest.main()
