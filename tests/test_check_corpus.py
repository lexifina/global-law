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
